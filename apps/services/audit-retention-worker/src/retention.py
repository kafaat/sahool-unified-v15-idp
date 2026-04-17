"""
SAHOOL Audit Retention — Core deletion logic.

One-shot retention sweep:

  1. For each (tenant, policy) pair, find the rows whose
     ``created_at < NOW() - retention_days``.
  2. Capture the ``(seq_num, entry_hash)`` of the newest row being
     deleted — this is the anchor a future chain-validation upgrade
     will use to treat the gap as expected rather than as tampering.
  3. Run a single DELETE under
     ``SET LOCAL sahool.audit_retention_job = 'on'`` so the
     append-only trigger lets the row out.
  4. Insert a matching row into ``audit_retention_events``.

Everything runs inside a single transaction per (tenant, policy). If
the INSERT into the event log fails, the DELETE rolls back with it —
we refuse to delete audit rows we cannot account for.

Dry-run mode (``dry_run=True``) runs the SELECT side of the logic so
the operator can see exactly what would be deleted, but skips both
the DELETE and the event insert.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from .policies import RetentionPolicy

logger = logging.getLogger(__name__)


@dataclass
class RetentionRunResult:
    """Outcome of a single (tenant, policy) retention invocation."""

    tenant_id: str
    category: str
    retention_days: int
    cutoff: datetime
    rows_deleted: int
    last_retained_seq_num: int | None
    last_retained_entry_hash: str | None
    dry_run: bool

    @property
    def was_noop(self) -> bool:
        return self.rows_deleted == 0


@dataclass
class SweepSummary:
    """Aggregated result across every tenant × policy."""

    runs: list[RetentionRunResult]
    started_at: datetime
    finished_at: datetime

    @property
    def total_deleted(self) -> int:
        return sum(r.rows_deleted for r in self.runs)

    @property
    def tenants_touched(self) -> int:
        return len({r.tenant_id for r in self.runs if r.rows_deleted > 0})


# ═══════════════════════════════════════════════════════════════════════════
# SQL — hard-coded, no user input ever flows into the statement text.
# ═══════════════════════════════════════════════════════════════════════════

# Two-step preview+delete. We pick the last row that will be retained
# (= highest seq_num among rows being deleted) up front so we can record
# its entry_hash even after the DELETE has run.
_FIND_LAST_RETAINED_SQL = """
SELECT seq_num, entry_hash
FROM audit_log
WHERE tenant_id = $1
  AND category = $2
  AND created_at < $3
ORDER BY seq_num DESC
LIMIT 1
"""

_COUNT_EXPIRED_SQL = """
SELECT COUNT(*) AS n
FROM audit_log
WHERE tenant_id = $1
  AND category = $2
  AND created_at < $3
"""

_DELETE_EXPIRED_SQL = """
DELETE FROM audit_log
WHERE tenant_id = $1
  AND category = $2
  AND created_at < $3
"""

_INSERT_EVENT_SQL = """
INSERT INTO audit_retention_events (
    tenant_id,
    last_retained_seq_num,
    last_retained_entry_hash,
    rows_deleted,
    category_filter,
    retention_days,
    cutoff_timestamp,
    dry_run
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
"""

_LIST_TENANTS_SQL = """
SELECT DISTINCT tenant_id
FROM audit_log
"""


async def list_tenants(conn: Any) -> list[str]:
    """Return every tenant that has any row in audit_log.

    The worker ALWAYS runs across every tenant — there is no per-tenant
    opt-in for retention. A tenant with no policy-matching rows still
    shows up here; the (tenant, policy) loop will just produce zero-row
    runs for them, which is the expected behaviour.
    """
    rows = await conn.fetch(_LIST_TENANTS_SQL)
    return [r["tenant_id"] for r in rows]


async def run_policy_for_tenant(
    conn: Any,
    *,
    tenant_id: str,
    policy: RetentionPolicy,
    now: datetime,
    dry_run: bool,
) -> RetentionRunResult:
    """Apply a single policy to a single tenant.

    The whole operation runs inside an explicit transaction on ``conn``
    so the session-local settings (retention trigger bypass + tenant
    context) can't leak into subsequent queries on the same connection.
    """
    cutoff = now - timedelta(days=policy.retention_days)

    async with conn.transaction():
        # 1. Session setup. Two statements; asyncpg treats them atomically
        #    inside this transaction.
        await conn.execute("SET LOCAL sahool.audit_retention_job = 'on'")
        await conn.execute("SELECT set_config('app.current_tenant_id', $1, true)", tenant_id)

        # 2. Find the "last retained" anchor before we delete anything.
        anchor = await conn.fetchrow(_FIND_LAST_RETAINED_SQL, tenant_id, policy.category, cutoff)

        if anchor is None:
            # Nothing to delete — still a legitimate no-op outcome, worth
            # surfacing in the metrics so an operator can distinguish
            # "policy ran cleanly and found nothing" from "policy skipped".
            # We do NOT write an event row for a no-op; events record
            # actual deletions, not attempts.
            logger.info(
                "retention.noop",
                extra={
                    "tenant_id": tenant_id,
                    "category": policy.category,
                    "cutoff": cutoff.isoformat(),
                },
            )
            return RetentionRunResult(
                tenant_id=tenant_id,
                category=policy.category,
                retention_days=policy.retention_days,
                cutoff=cutoff,
                rows_deleted=0,
                last_retained_seq_num=None,
                last_retained_entry_hash=None,
                dry_run=dry_run,
            )

        last_seq_num = int(anchor["seq_num"])
        last_hash = str(anchor["entry_hash"])

        # 3. Count rows (used for the event record + the returned summary).
        #    We avoid RETURNING * on the DELETE because that would stream
        #    potentially-millions of rows back to the client for no reason.
        count_row = await conn.fetchrow(_COUNT_EXPIRED_SQL, tenant_id, policy.category, cutoff)
        rows_to_delete = int(count_row["n"])

        if dry_run:
            logger.info(
                "retention.dry_run",
                extra={
                    "tenant_id": tenant_id,
                    "category": policy.category,
                    "would_delete": rows_to_delete,
                    "cutoff": cutoff.isoformat(),
                },
            )
            return RetentionRunResult(
                tenant_id=tenant_id,
                category=policy.category,
                retention_days=policy.retention_days,
                cutoff=cutoff,
                rows_deleted=rows_to_delete,
                last_retained_seq_num=last_seq_num,
                last_retained_entry_hash=last_hash,
                dry_run=True,
            )

        # 4. DELETE — the real thing. If this or the subsequent INSERT
        #    fails, the whole transaction rolls back and we're back to a
        #    consistent state.
        result = await conn.execute(_DELETE_EXPIRED_SQL, tenant_id, policy.category, cutoff)
        # asyncpg returns "DELETE N" as the tag; parse the count so we can
        # cross-check against our earlier COUNT(*). A mismatch here would
        # indicate a concurrent writer which shouldn't happen during a
        # retention window but is worth surfacing.
        deleted = _parse_delete_tag(result)
        if deleted != rows_to_delete:
            logger.warning(
                "retention.count_mismatch",
                extra={
                    "tenant_id": tenant_id,
                    "category": policy.category,
                    "expected": rows_to_delete,
                    "actual": deleted,
                },
            )

        # 5. Record the event so future chain-validation can treat the gap
        #    as expected. Same transaction — if this INSERT fails the
        #    DELETE above rolls back.
        await conn.execute(
            _INSERT_EVENT_SQL,
            tenant_id,
            last_seq_num,
            last_hash,
            deleted,
            policy.category,
            policy.retention_days,
            cutoff,
            False,  # dry_run column
        )

        logger.info(
            "retention.deleted",
            extra={
                "tenant_id": tenant_id,
                "category": policy.category,
                "rows_deleted": deleted,
                "last_retained_seq_num": last_seq_num,
            },
        )

        return RetentionRunResult(
            tenant_id=tenant_id,
            category=policy.category,
            retention_days=policy.retention_days,
            cutoff=cutoff,
            rows_deleted=deleted,
            last_retained_seq_num=last_seq_num,
            last_retained_entry_hash=last_hash,
            dry_run=False,
        )


async def run_sweep(
    pool: Any,
    policies: list[RetentionPolicy],
    *,
    dry_run: bool = False,
    now: datetime | None = None,
) -> SweepSummary:
    """Run every configured policy against every tenant.

    ``now`` is injectable so tests can pin time to a deterministic value.
    """
    started_at = datetime.now(UTC)
    effective_now = now or started_at
    runs: list[RetentionRunResult] = []

    async with pool.acquire() as conn:
        tenants = await list_tenants(conn)

        for tenant_id in tenants:
            for policy in policies:
                run = await run_policy_for_tenant(
                    conn,
                    tenant_id=tenant_id,
                    policy=policy,
                    now=effective_now,
                    dry_run=dry_run,
                )
                runs.append(run)

    return SweepSummary(runs=runs, started_at=started_at, finished_at=datetime.now(UTC))


def _parse_delete_tag(tag: str) -> int:
    """Turn asyncpg's ``'DELETE 42'`` tag into ``42``.

    Returns 0 on unrecognised input rather than raising — the tag format
    is stable across every supported Postgres version but we'd rather
    under-report than crash the worker on an oddity.
    """
    parts = tag.split()
    if len(parts) == 2 and parts[0] == "DELETE" and parts[1].isdigit():
        return int(parts[1])
    return 0
