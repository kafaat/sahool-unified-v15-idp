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

    replayed = await OutboxReplay.reset_dead_lettered(pool)
    replayed = await OutboxReplay.reset_dead_lettered(pool, subject="sahool.satellite.ndvi.computed")
    replayed = await OutboxReplay.reset_dead_lettered(pool, ids=["<uuid>", "<uuid>"])

    # CLI (run from repo root)
    python -m shared.libs.outbox.replay_tool --dsn postgresql://... [--subject SUBJECT] [--id ID ...]

After reset the relay will attempt to re-publish on the next poll tick.
The consumer's idempotency guard (``processed_events``) prevents duplicate
side-effects if the original message was already successfully processed before
the DLQ was triggered.

⚠️  Replay does NOT guarantee delivery to the same consumer — it re-enters
the normal relay flow.  Ensure downstream consumers are idempotent before
replaying.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from typing import Sequence
from uuid import UUID

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

_LIST_DLQ_SQL = """
SELECT id, subject, tenant_id, retry_count, dead_lettered_at
FROM outbox_messages
WHERE dead_lettered_at IS NOT NULL
ORDER BY dead_lettered_at
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
    async def reset_dead_lettered(
        db_pool,
        *,
        subject: str | None = None,
        ids: Sequence[str | UUID] | None = None,
    ) -> int:
        """
        Reset dead-lettered rows so the relay retries them.

        Args:
            db_pool: asyncpg pool.
            subject: If given, reset only rows matching this NATS subject.
            ids: If given, reset only the listed row UUIDs.
                 ``subject`` and ``ids`` are mutually exclusive; ``ids``
                 takes precedence.

        Returns:
            Number of rows reset.

        Raises:
            ValueError: if both *subject* and *ids* are provided.
        """
        if subject is not None and ids is not None:
            raise ValueError("Provide either 'subject' or 'ids', not both.")

        async with db_pool.acquire() as conn:
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

        logger.info(
            "outbox_replay_reset",
            extra={
                "rows_reset": count,
                "subject": subject,
                "ids": [str(i) for i in ids] if ids else None,
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
        help="List dead-lettered rows and exit without resetting.",
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
        if args.list:
            rows = await OutboxReplay.list_dead_lettered(pool)
            if not rows:
                print("No dead-lettered rows.")
                return
            print(f"{'ID':<38}  {'SUBJECT':<45}  {'RETRIES':>7}  DEAD_LETTERED_AT")
            print("-" * 110)
            for r in rows:
                print(
                    f"{str(r['id']):<38}  {r['subject']:<45}  {r['retry_count']:>7}  {r['dead_lettered_at']}"
                )
            return

        count = await OutboxReplay.reset_dead_lettered(
            pool,
            subject=args.subject,
            ids=args.ids,
        )
        print(f"Reset {count} dead-lettered row(s).")
    finally:
        await pool.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _args = _build_parser().parse_args()
    asyncio.run(_main(_args))
