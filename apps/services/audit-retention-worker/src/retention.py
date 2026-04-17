"""
SAHOOL Audit Retention — Core deletion logic.

One-shot retention sweep:

  1. For each (tenant, policy) pair, find the rows whose
     ``created_at < NOW() - retention_days``.
  2. DELETE those rows under ``SET LOCAL sahool.audit_retention_job = 'on'``
     with a RETURNING clause so we capture every deleted row's
     (seq_num, entry_hash).
  3. Insert a matching row into ``audit_retention_events``:
       * last_deleted_seq_num / last_deleted_entry_hash = newest deleted row
       * deleted_entry_hashes  = every deleted hash (so the consumer's
         chain validator can accept ANY surviving prev_hash that matches
         one of them as a legitimate retention-driven gap).

Why ``deleted_entry_hashes`` is an array, not just the newest hash:
  The per-tenant hash chain is shared across ALL categories. Per-category
  retention with different cutoffs (the realistic config — auth 90d,
  billing 1825d) produces non-contiguous deletions interleaved inside
  the chain. One surviving row might point at a deleted predecessor at
  seq_num 12 while another points at seq_num 8. Recording only the
  newest deleted hash would leave validate_chain() flagging all earlier
  gap points as tampering. The array captures every gap boundary.

Everything runs inside a single transaction per (tenant, policy). If
the INSERT into the event log fails, the DELETE rolls back with it —
we refuse to delete audit rows we cannot account for.

Dry-run mode (``dry_run=True``) runs the SELECT side of the logic so
the operator can see exactly what would be deleted, but skips both
the DELETE and the event insert.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
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
    # The newest deleted row's (seq_num, entry_hash) — used by
    # validate_chain() when reconstructing the chain boundary. None for
    # no-op runs (nothing matched the cutoff).
    last_deleted_seq_num: int | None
    last_deleted_entry_hash: str | None
    # Every deleted row's entry_hash, seq_num-ascending. Empty for no-op.
    deleted_entry_hashes: list[str] = field(default_factory=list)
    dry_run: bool = False

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

_COUNT_EXPIRED_SQL = """
SELECT COUNT(*) AS n
FROM audit_log
WHERE tenant_id = $1
  AND category = $2
  AND created_at < $3
"""

# DELETE ... RETURNING captures every deleted row's identifying columns in
# one round-trip. On a realistic retention run this is bounded by the
# configured retention window's daily volume (typically under 100k rows);
# streaming that back is cheap relative to the cost of missing a gap
# boundary. Ordered by seq_num so the caller can record the newest
# deterministically.
_DELETE_EXPIRED_SQL = """
DELETE FROM audit_log
WHERE tenant_id = $1
  AND category = $2
  AND created_at < $3
RETURNING seq_num, entry_hash
"""

_INSERT_EVENT_SQL = """
INSERT INTO audit_retention_events (
    tenant_id,
    last_deleted_seq_num,
    last_deleted_entry_hash,
    rows_deleted,
    deleted_entry_hashes,
    category_filter,
    retention_days,
    cutoff_timestamp,
    dry_run
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
"""

_LIST_TENANTS_SQL = """
SELECT DISTINCT tenant_id
FROM audit_log
"""

# Detect whether the connected role has BYPASSRLS. audit_retention is
# supposed to hold it (see migration 002) but that ALTER ROLE only runs
# under a superuser. On managed-Postgres deployments operators may miss
# the post-provision step; without BYPASSRLS, list_tenants() silently
# returns zero tenants and the sweep looks successful while deleting
# nothing. A startup probe makes the misconfiguration loud.
_CHECK_BYPASSRLS_SQL = """
SELECT rolbypassrls
FROM pg_roles
WHERE rolname = current_user
"""


async def list_tenants(conn: Any) -> list[str]:
    """Return every tenant that has any row in audit_log.

    The worker ALWAYS runs across every tenant — there is no per-tenant
    opt-in for retention. A tenant with no policy-matching rows still
    shows up here; the (tenant, policy) loop will just produce zero-row
    runs for them, which is the expected behaviour.

    No RLS context is set on this query on purpose — the retention worker
    operates platform-wide, not per-tenant, so it relies on the connecting
    role's BYPASSRLS attribute. If that attribute is missing, the query
    returns an empty list and the caller logs a hard error (see
    ``run_sweep``'s configuration guard).
    """
    rows = await conn.fetch(_LIST_TENANTS_SQL)
    return [r["tenant_id"] for r in rows]


async def probe_bypassrls(conn: Any) -> bool | None:
    """Return True if the current DB role has BYPASSRLS, False if not,
    None if the probe itself fails (role hidden, pg_roles not queryable).

    Surfaced so the caller can raise a loud configuration error instead
    of silently sweeping zero rows on a misconfigured deployment.
    """
    try:
        row = await conn.fetchrow(_CHECK_BYPASSRLS_SQL)
    except Exception as exc:  # noqa: BLE001 — diagnostic only
        logger.warning("retention.bypassrls_probe_failed", extra={"error": str(exc)})
        return None
    return bool(row["rolbypassrls"]) if row else None


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

        # 2. Count rows up-front to distinguish "nothing matched" from
        #    "matched but DELETE RETURNING gave back a different number"
        #    (would indicate a concurrent writer — shouldn't happen but
        #    worth surfacing).
        count_row = await conn.fetchrow(_COUNT_EXPIRED_SQL, tenant_id, policy.category, cutoff)
        rows_to_delete = int(count_row["n"])

        if rows_to_delete == 0:
            # Nothing to delete — no event row (we log actual deletions,
            # not attempts), but the result still surfaces in metrics so
            # operators can tell "policy ran cleanly and found nothing"
            # from "policy skipped".
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
                last_deleted_seq_num=None,
                last_deleted_entry_hash=None,
                deleted_entry_hashes=[],
                dry_run=dry_run,
            )

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
                last_deleted_seq_num=None,
                last_deleted_entry_hash=None,
                deleted_entry_hashes=[],
                dry_run=True,
            )

        # 3. DELETE ... RETURNING — the real thing. If this or the
        #    subsequent INSERT fails, the whole transaction rolls back
        #    and we're back to a consistent state.
        deleted_rows = await conn.fetch(_DELETE_EXPIRED_SQL, tenant_id, policy.category, cutoff)
        deleted = len(deleted_rows)
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

        # Sort by seq_num ascending so `deleted_entry_hashes[-1]` is always
        # the newest — deterministic for the event row.
        sorted_rows = sorted(deleted_rows, key=lambda r: int(r["seq_num"]))
        all_hashes = [str(r["entry_hash"]) for r in sorted_rows]
        last_seq_num = int(sorted_rows[-1]["seq_num"])
        last_hash = all_hashes[-1]

        # 4. Record the event so future chain-validation can treat the gap
        #    as expected. Same transaction — if this INSERT fails the
        #    DELETE above rolls back.
        await conn.execute(
            _INSERT_EVENT_SQL,
            tenant_id,
            last_seq_num,
            last_hash,
            deleted,
            all_hashes,
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
                "last_deleted_seq_num": last_seq_num,
                "hashes_recorded": len(all_hashes),
            },
        )

        return RetentionRunResult(
            tenant_id=tenant_id,
            category=policy.category,
            retention_days=policy.retention_days,
            cutoff=cutoff,
            rows_deleted=deleted,
            last_deleted_seq_num=last_seq_num,
            last_deleted_entry_hash=last_hash,
            deleted_entry_hashes=all_hashes,
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

    Raises ``RuntimeError`` if the connecting role lacks BYPASSRLS AND
    policies are configured AND list_tenants() returns empty — that
    combination always means the worker will silently do nothing. Better
    to fail loud than to mask a production misconfig.
    """
    started_at = datetime.now(UTC)
    effective_now = now or started_at
    runs: list[RetentionRunResult] = []

    async with pool.acquire() as conn:
        # Startup probe: if policies are configured but list_tenants
        # returns nothing, inspect BYPASSRLS and raise with a pointer
        # at the likely misconfiguration.
        tenants = await list_tenants(conn)
        if policies and not tenants:
            bypass = await probe_bypassrls(conn)
            if bypass is False:
                raise RuntimeError(
                    "retention worker sees zero tenants AND the connecting "
                    "role lacks BYPASSRLS. RLS is hiding audit_log rows. "
                    "Run `ALTER ROLE audit_retention BYPASSRLS;` as a "
                    "superuser — see migration 002 header for the full "
                    "provisioning notes."
                )
            logger.warning(
                "retention.zero_tenants",
                extra={
                    "bypassrls": bypass,
                    "hint": "policies configured but list_tenants returned empty — "
                    "either audit_log is genuinely empty or BYPASSRLS probe "
                    "could not verify the role privilege",
                },
            )

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
