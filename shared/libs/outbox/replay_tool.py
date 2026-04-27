"""
SAHOOL Outbox Replay Tool
=========================
أداة إعادة تشغيل الصندوق الصادر

Resets dead-lettered outbox rows so the relay picks them up again.

A row is dead-lettered when its ``retry_count`` reaches ``_MAX_RETRIES``.
Operators can inspect dead-lettered rows with:

    SELECT id, subject, tenant_id, retry_count, dead_lettered_at
    FROM outbox_messages
    WHERE dead_lettered_at IS NOT NULL
    ORDER BY dead_lettered_at;

Then replay all, a subset by subject, or individual rows by ID:

    # Python API
    from shared.libs.outbox.replay_tool import OutboxReplay

    # Dry-run inspection (no rows modified)
    info = await OutboxReplay.inspect_dead_lettered(pool)
    # → {"total": 5, "by_subject": {"sahool.ndvi.computed": 3}, "oldest_age_seconds": 7200}

    # Reset and record who triggered the replay (forensic audit)
    replayed = await OutboxReplay.reset_dead_lettered(pool, replayed_by="ops-team")
    replayed = await OutboxReplay.reset_dead_lettered(pool, subject="sahool.satellite.ndvi.computed", replayed_by="admin")
    replayed = await OutboxReplay.reset_dead_lettered(pool, ids=["<uuid>", "<uuid>"], replayed_by="automated-recovery")

    # CLI (run from repo root)
    python -m shared.libs.outbox.replay_tool --dsn postgresql://... --dry-run
    python -m shared.libs.outbox.replay_tool --dsn postgresql://... --list
    python -m shared.libs.outbox.replay_tool --dsn postgresql://... --replayed-by ops --subject sahool.satellite.ndvi.computed

After reset the relay will attempt to re-publish on the next poll tick.

⚠️  Replay safety
==================
The consumer's idempotency guard (``processed_events``) prevents duplicate
side-effects if the original message was already successfully processed before
the DLQ was triggered.

For complete write-side idempotency, side-effect tables MUST have:

    ALTER TABLE <side_effect_table>
    ADD CONSTRAINT uq_<table>_event_id UNIQUE (event_id);

This ensures that even if both the ``processed_events`` guard is missed *and*
the relay re-delivers, the DB write is physically idempotent.  See
``migration_idempotency.sql`` in this package for the pattern.

Replay does NOT guarantee delivery to the same consumer instance — it
re-enters the normal relay flow.  Ensure downstream consumers are idempotent
before replaying.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from shared.libs.outbox.metrics import OUTBOX_METRICS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQL
# ---------------------------------------------------------------------------

_RESET_ALL_SQL = """
UPDATE outbox_messages
SET dead_lettered_at = NULL,
    retry_count      = 0,
    claimed_at       = NULL,
    claimed_by       = NULL
WHERE dead_lettered_at IS NOT NULL
"""

_RESET_BY_SUBJECT_SQL = """
UPDATE outbox_messages
SET dead_lettered_at = NULL,
    retry_count      = 0,
    claimed_at       = NULL,
    claimed_by       = NULL
WHERE dead_lettered_at IS NOT NULL
  AND subject = $1
"""

_RESET_BY_IDS_SQL = """
UPDATE outbox_messages
SET dead_lettered_at = NULL,
    retry_count      = 0,
    claimed_at       = NULL,
    claimed_by       = NULL
WHERE dead_lettered_at IS NOT NULL
  AND id = ANY($1::uuid[])
"""

_COUNT_DLQ_SQL = """
SELECT COUNT(*) AS n
FROM outbox_messages
WHERE dead_lettered_at IS NOT NULL
"""

# Transaction-level advisory lock — automatically released on commit/rollback.
# Two-argument form uses (int4, int4): namespace=1 (SAHOOL outbox advisory-lock
# namespace), key=_ADVISORY_LOCK_KEY.
#
# A pre-computed literal integer is used instead of hashtext('outbox-replay')
# to avoid any dependency on the hashtext() function and to make the lock
# identity fully transparent in code review without requiring a DB query.
# The value 20290 was chosen as a stable, unique identifier for the outbox
# replay operation (hex 0x4F42 = "OB" for OutBox).
_ADVISORY_LOCK_KEY: int = 20290  # stable int4 key for "outbox-replay" within namespace 1
_ADVISORY_LOCK_SQL = f"SELECT pg_advisory_xact_lock(1, {_ADVISORY_LOCK_KEY})"

_LIST_DLQ_SQL = """
SELECT id, subject, tenant_id, retry_count, dead_lettered_at
FROM outbox_messages
WHERE dead_lettered_at IS NOT NULL
ORDER BY dead_lettered_at
"""

# Count by subject + oldest dead_lettered_at for dry-run inspection.
_INSPECT_DLQ_SQL = """
SELECT
    subject,
    COUNT(*) AS n,
    MIN(dead_lettered_at) AS oldest_dead_lettered_at
FROM outbox_messages
WHERE dead_lettered_at IS NOT NULL
GROUP BY subject
ORDER BY n DESC
"""


class OutboxReplay:
    """
    Async helpers for replaying dead-lettered outbox rows.

    All methods accept an asyncpg pool (or connection) and return the
    number of rows reset.
    """

    @staticmethod
    async def count_dead_lettered(db_pool) -> int:
        """Return the current number of dead-lettered rows."""
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(_COUNT_DLQ_SQL)
            return int(row["n"]) if row else 0

    @staticmethod
    async def list_dead_lettered(db_pool) -> list[dict]:
        """Return all dead-lettered rows as a list of dicts (for inspection)."""
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(_LIST_DLQ_SQL)
        return [dict(r) for r in rows]

    @staticmethod
    async def inspect_dead_lettered(db_pool) -> dict:
        """Return a dry-run summary of dead-lettered rows.

        Returns a dict with:
        ``total``              — total DLQ row count
        ``by_subject``         — dict mapping subject → row count
        ``oldest_age_seconds`` — age in seconds of the oldest DLQ row
                                 (``None`` when there are no DLQ rows)

        This is safe to call without modifying any rows.  Use it to
        understand the impact of a replay before triggering one.

        Example::

            info = await OutboxReplay.inspect_dead_lettered(pool)
            # {
            #   "total": 12,
            #   "by_subject": {
            #     "sahool.satellite.ndvi.computed": 9,
            #     "sahool.weather.updated": 3,
            #   },
            #   "oldest_age_seconds": 7200,
            # }
        """
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(_INSPECT_DLQ_SQL)

        if not rows:
            return {"total": 0, "by_subject": {}, "oldest_age_seconds": None}

        by_subject: dict[str, int] = {}
        total = 0
        oldest: datetime | None = None

        for r in rows:
            count = int(r["n"])
            by_subject[r["subject"]] = count
            total += count
            dlq_ts = r["oldest_dead_lettered_at"]
            if dlq_ts is not None:
                if oldest is None or dlq_ts < oldest:
                    oldest = dlq_ts

        oldest_age: float | None = None
        if oldest is not None:
            now = datetime.now(tz=timezone.utc)
            # asyncpg returns timezone-aware datetimes for TIMESTAMPTZ columns
            # and naive datetimes for plain TIMESTAMP columns.  Both cases are
            # handled: timezone-aware values are compared directly; naive
            # values are assumed UTC and converted before computing the age.
            if oldest.tzinfo is None:
                oldest = oldest.replace(tzinfo=timezone.utc)
            oldest_age = (now - oldest).total_seconds()

        return {
            "total": total,
            "by_subject": by_subject,
            "oldest_age_seconds": oldest_age,
        }

    @staticmethod
    async def reset_dead_lettered(
        db_pool,
        *,
        subject: str | None = None,
        ids: Sequence[str | UUID] | None = None,
        replayed_by: str = "system",
    ) -> int:
        """
        Reset dead-lettered rows so the relay retries them.

        Args:
            db_pool: asyncpg pool.
            subject: If given, reset only rows matching this NATS subject.
            ids: If given, reset only the listed row UUIDs.
                 ``subject`` and ``ids`` are mutually exclusive.
            replayed_by: Human-readable identifier of who/what triggered the
                replay.  Stored in the structured audit log record for forensic
                tracing.  Examples: ``"ops-team"``, ``"admin-ui"``,
                ``"automated-recovery"``.

        Returns:
            Number of rows reset.

        Raises:
            ValueError: if both *subject* and *ids* are provided.
        """
        if subject is not None and ids is not None:
            raise ValueError("Provide either 'subject' or 'ids', not both.")

        # Determine metric labels before touching the DB.
        if ids is not None:
            reason = "by_ids"
            metric_subject = "(ids)"
        elif subject is not None:
            reason = "by_subject"
            metric_subject = subject
        else:
            reason = "all"
            metric_subject = "*"

        # Acquire a transaction-level advisory lock before mutating rows.
        # This serializes concurrent replay callers (two ops-team members,
        # automated-recovery + CLI) so they cannot reset the same DLQ rows
        # simultaneously — which would produce wasted relay load and
        # misleading audit log entries.  The lock is released automatically
        # when the transaction commits or rolls back.
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(_ADVISORY_LOCK_SQL)
                if ids is not None:
                    str_ids = [str(i) for i in ids]
                    status = await conn.execute(_RESET_BY_IDS_SQL, str_ids)
                elif subject is not None:
                    status = await conn.execute(_RESET_BY_SUBJECT_SQL, subject)
                else:
                    status = await conn.execute(_RESET_ALL_SQL)

        # asyncpg returns a status string like "UPDATE 5"
        try:
            count = int(status.split()[-1])
        except (IndexError, ValueError):
            count = 0

        # Record replay volume in Prometheus so it can be tracked alongside
        # the DLQ rate (outbox_dead_lettered_total) in dashboards and SLOs.
        if count > 0:
            OUTBOX_METRICS.record_replay(subject=metric_subject, reason=reason, count=count)

        # Forensic audit log — every replay is permanently traceable.
        logger.info(
            "outbox_replay_reset",
            extra={
                "rows_reset": count,
                "replayed_by": replayed_by,
                "replayed_at": datetime.now(tz=timezone.utc).isoformat(),
                "filter_subject": subject,
                "filter_ids": [str(i) for i in ids] if ids else None,
            },
        )
        return count


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m shared.libs.outbox.replay_tool",
        description="Reset dead-lettered outbox rows so the relay retries them.",
    )
    p.add_argument(
        "--dsn",
        required=True,
        help="asyncpg-compatible PostgreSQL DSN, e.g. postgresql://user:pass@host/db",
    )
    p.add_argument(
        "--subject",
        default=None,
        help="Reset only rows matching this NATS subject.",
    )
    p.add_argument(
        "--id",
        dest="ids",
        nargs="*",
        default=None,
        help="Reset only these row UUIDs (space-separated).",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="List all dead-lettered rows (id, subject, retries, age) and exit.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show a summary (total, by-subject count, oldest age) without "
            "modifying any rows.  Use this to assess impact before replaying."
        ),
    )
    p.add_argument(
        "--replayed-by",
        dest="replayed_by",
        default="cli",
        help="Identifier stored in the audit log for this replay operation (default: cli).",
    )
    return p


async def _main(args: argparse.Namespace) -> None:
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg is required. Install it with: pip install asyncpg")
        raise SystemExit(1)

    pool = await asyncpg.create_pool(args.dsn, min_size=1, max_size=2)
    try:
        if args.dry_run:
            info = await OutboxReplay.inspect_dead_lettered(pool)
            if info["total"] == 0:
                print("No dead-lettered rows.")
                return
            print(f"Dead-lettered rows: {info['total']}")
            if info["oldest_age_seconds"] is not None:
                hours = info["oldest_age_seconds"] / 3600
                print(f"Oldest row age:     {hours:.1f} hours")
            print("\nBy subject:")
            for subj, n in sorted(info["by_subject"].items(), key=lambda kv: -kv[1]):
                print(f"  {n:>6}  {subj}")
            print("\n(dry-run — no rows modified)")
            return

        if args.list:
            rows = await OutboxReplay.list_dead_lettered(pool)
            if not rows:
                print("No dead-lettered rows.")
                return
            now = datetime.now(tz=timezone.utc)
            print(f"{'ID':<38}  {'SUBJECT':<45}  {'RETRIES':>7}  {'AGE':>10}  DEAD_LETTERED_AT")
            print("-" * 120)
            for r in rows:
                dlq_ts = r["dead_lettered_at"]
                if dlq_ts is not None:
                    if dlq_ts.tzinfo is None:
                        dlq_ts = dlq_ts.replace(tzinfo=timezone.utc)
                    age_h = f"{(now - dlq_ts).total_seconds() / 3600:.1f}h"
                else:
                    age_h = "?"
                print(
                    f"{str(r['id']):<38}  {r['subject']:<45}  {r['retry_count']:>7}  {age_h:>10}  {r['dead_lettered_at']}"
                )
            return

        count = await OutboxReplay.reset_dead_lettered(
            pool,
            subject=args.subject,
            ids=args.ids,
            replayed_by=args.replayed_by,
        )
        print(f"Reset {count} dead-lettered row(s).  (replayed_by={args.replayed_by!r})")
    finally:
        await pool.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _args = _build_parser().parse_args()
    asyncio.run(_main(_args))
