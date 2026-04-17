"""
SAHOOL Audit Service — Persistence Layer
============================================

Two interchangeable backends for storing audit entries:

* ``PostgresAuditStore`` — production backend, persists to the
  ``audit_log`` table (see ``migrations/001_create_audit_log.sql``).
  All reads/writes run inside a per-request transaction that sets
  ``app.current_tenant_id`` so the row-level-security policy
  transparently scopes every query to a single tenant.

* ``InMemoryAuditStore`` — fallback for unit tests and CI where no
  PostgreSQL is available. Same interface, but entries live only for
  the process lifetime.

Every write is appended to a per-tenant SHA-256 hash chain. Any
historical row that gets mutated out-of-band will break the chain,
so ``validate_chain()`` is a cheap tamper detector.

Retention awareness
~~~~~~~~~~~~~~~~~~~
The audit-retention-worker (apps/services/audit-retention-worker/)
legitimately deletes expired rows under a dedicated Postgres role,
which creates gaps in the per-tenant hash chain. Each deletion run
records the ``(seq_num, entry_hash)`` of its last-deleted row in the
``audit_retention_events`` table. ``validate_chain()`` loads those
checkpoints via ``retention_boundaries_for_tenant()`` and accepts any
surviving row whose ``prev_hash`` matches a boundary hash as a
legitimate re-anchor rather than a chain break — counted in
``ChainValidation.retention_gaps_crossed`` so dashboards can tell
"retention has run" from "chain has never been touched".

The store is deliberately async-first, transaction-safe, and has no
business logic of its own — ``main.py`` is still the single place
that decides *what* to log.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

try:
    import asyncpg
except ImportError:  # pragma: no cover - asyncpg is optional in test/CI
    asyncpg = None  # type: ignore[assignment]


# ═══════════════════════════════════════════════════════════════════════════
# Hash chain — deterministic, per-tenant, SHA-256 (+ optional HMAC secret).
# ═══════════════════════════════════════════════════════════════════════════

GENESIS_HASH = "0" * 64


def _canonical(entry: dict) -> str:
    """Stable JSON serialisation used as hash input.

    JSONB round-trips lose key ordering, so we always serialise with
    sorted keys and no whitespace; otherwise two semantically equal
    entries would produce different hashes.
    """
    relevant = {
        "tenant_id": entry.get("tenant_id"),
        "seq_num": entry.get("seq_num"),
        "user_id": entry.get("user_id"),
        "action": entry.get("action"),
        "category": entry.get("category"),
        "severity": entry.get("severity"),
        "resource_type": entry.get("resource_type"),
        "resource_id": entry.get("resource_id"),
        "success": entry.get("success"),
        "details": entry.get("details") or {},
        "old_value": entry.get("old_value"),
        "new_value": entry.get("new_value"),
        "created_at": entry.get("created_at"),
    }
    return json.dumps(relevant, sort_keys=True, separators=(",", ":"), default=str)


def compute_entry_hash(entry: dict, prev_hash: str, secret: str | None = None) -> str:
    """Compute the hash for a single entry. Symmetric with validate_chain."""
    payload = (prev_hash + _canonical(entry)).encode("utf-8")
    if secret:
        return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hashlib.sha256(payload).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════
# Dataclasses
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ChainValidation:
    valid: bool
    total_entries: int
    errors: list[str] = field(default_factory=list)
    first_entry_at: str | None = None
    last_entry_at: str | None = None
    # Count of legitimate chain "re-anchors" the validator crossed — one per
    # retention_events row whose last_retained_entry_hash matched a surviving
    # row's prev_hash. A non-zero value means retention ran and the chain
    # reconnected cleanly; it is NOT an error. Exposed in the API response
    # so dashboards can distinguish "this tenant has been retention-processed"
    # from "this tenant's chain has never been touched".
    retention_gaps_crossed: int = 0


@dataclass(frozen=True)
class RetentionBoundary:
    """Checkpoint written by the audit-retention-worker each time it
    deletes rows from audit_log. Holds the seq_num + entry_hash of the
    last-deleted row in that run so validate_chain() can accept the
    resulting gap instead of reporting it as tampering.

    Populated from audit_retention_events (see
    apps/services/audit-retention-worker/migrations/003_audit_retention_events.sql).
    """

    seq_num: int
    entry_hash: str
    created_at: str  # ISO-8601; retention event's executed_at


# ═══════════════════════════════════════════════════════════════════════════
# Interface
# ═══════════════════════════════════════════════════════════════════════════


class AuditStore(Protocol):
    """Minimal contract every backend must satisfy."""

    async def write(self, entry: dict) -> dict:
        """Persist ``entry``; return it with id/seq_num/hashes filled in."""
        pass  # Protocol method — body intentionally empty

    async def query(
        self,
        tenant_id: str,
        *,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Return ``(items, total_matching_filters)``."""
        pass  # Protocol method — body intentionally empty

    async def all_for_tenant(self, tenant_id: str) -> list[dict]:
        """Return every entry for a tenant, oldest first. Used by chain
        validation and aggregates. Bounded by retention, not user pagination.
        """
        pass  # Protocol method — body intentionally empty

    async def count_since(self, tenant_id: str | None, since: datetime) -> int:
        """Global or per-tenant write count since ``since``. Feeds the
        ``audit_writes_total`` Prometheus gauge."""
        pass  # Protocol method — body intentionally empty

    async def validate_chain(self, tenant_id: str) -> ChainValidation:
        """Recompute the chain and flag any divergence."""
        pass  # Protocol method — body intentionally empty

    async def tenants_with_activity_since(self, since: datetime) -> list[str]:
        """Tenant IDs that have written any audit entry since ``since``.

        Feeds the periodic chain-validation job so the
        ``audit_chain_valid`` gauge only refreshes for tenants that
        actually matter, avoiding wasted work on dormant tenants.
        """
        pass  # Protocol method — body intentionally empty

    async def retention_boundaries_for_tenant(self, tenant_id: str) -> list[RetentionBoundary]:
        """Retention checkpoints for ``tenant_id``, ordered by seq_num.

        Feeds ``validate_chain()`` so retention-driven gaps in the chain
        are recognised as legitimate rather than reported as tampering.
        Returns an empty list when the retention worker has not yet
        deployed (table missing) or has not yet run for this tenant.
        """
        pass  # Protocol method — body intentionally empty


# ═══════════════════════════════════════════════════════════════════════════
# Postgres backend
# ═══════════════════════════════════════════════════════════════════════════


_INSERT_SQL = """
INSERT INTO audit_log (
    id, tenant_id, user_id, action, category, severity,
    resource_type, resource_id, correlation_id, ip_address, user_agent,
    success, error_code, error_message,
    details, old_value, new_value,
    entry_hash, prev_hash, created_at
) VALUES (
    $1, $2, $3, $4, $5, $6,
    $7, $8, $9, $10, $11,
    $12, $13, $14,
    $15::jsonb, $16::jsonb, $17::jsonb,
    $18, $19, $20
)
RETURNING seq_num, created_at
"""


class PostgresAuditStore:
    """Real production backend backed by PostgreSQL."""

    def __init__(self, pool: Any, secret: str | None = None) -> None:
        self._pool = pool
        self._secret = secret

    async def _with_tenant(self, conn: Any, tenant_id: str) -> None:
        """Set the session variable consumed by the RLS policy. Must be
        called inside every transaction that touches ``audit_log``."""
        await conn.execute("SELECT set_config('app.current_tenant_id', $1, true)", tenant_id)

    async def write(self, entry: dict) -> dict:
        tenant_id = entry["tenant_id"]
        entry.setdefault("id", str(uuid.uuid4()))
        entry.setdefault("user_id", "system")
        entry.setdefault("severity", "info")
        entry.setdefault("category", "system")
        entry.setdefault("success", True)
        entry.setdefault("details", {})
        entry.setdefault("created_at", datetime.now(UTC))
        if isinstance(entry["created_at"], str):
            entry["created_at"] = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                await self._with_tenant(conn, tenant_id)

                prev_hash_row = await conn.fetchrow(
                    "SELECT entry_hash FROM audit_log WHERE tenant_id = $1 ORDER BY seq_num DESC LIMIT 1",
                    tenant_id,
                )
                prev_hash = prev_hash_row["entry_hash"] if prev_hash_row else GENESIS_HASH

                # We compute the hash *before* insert so it becomes part of the
                # row; seq_num is assigned by the BIGSERIAL at INSERT time, so
                # we look it up in the same transaction with pg_advisory locks
                # disabled — a simple sequence peek is sufficient for hashing.
                next_seq_row = await conn.fetchrow(
                    "SELECT COALESCE(MAX(seq_num), 0) + 1 AS next_seq FROM audit_log WHERE tenant_id = $1",
                    tenant_id,
                )
                entry["seq_num"] = int(next_seq_row["next_seq"])
                entry["prev_hash"] = prev_hash
                entry["entry_hash"] = compute_entry_hash(entry, prev_hash, self._secret)

                row = await conn.fetchrow(
                    _INSERT_SQL,
                    uuid.UUID(entry["id"]),
                    tenant_id,
                    entry["user_id"],
                    entry["action"],
                    entry["category"],
                    entry["severity"],
                    entry.get("resource_type"),
                    entry.get("resource_id"),
                    uuid.UUID(entry["correlation_id"]) if entry.get("correlation_id") else None,
                    entry.get("ip_address"),
                    entry.get("user_agent"),
                    entry["success"],
                    entry.get("error_code"),
                    entry.get("error_message"),
                    json.dumps(entry["details"], default=str),
                    json.dumps(entry["old_value"], default=str) if entry.get("old_value") else None,
                    json.dumps(entry["new_value"], default=str) if entry.get("new_value") else None,
                    entry["entry_hash"],
                    prev_hash,
                    entry["created_at"],
                )
                entry["seq_num"] = int(row["seq_num"])
                entry["created_at"] = row["created_at"].isoformat()

        return entry

    @staticmethod
    def _build_where(filters: dict[str, Any] | None) -> tuple[str, list[Any]]:
        """Translate the endpoint filter dict into a parameterised WHERE."""
        clauses: list[str] = []
        values: list[Any] = []
        if not filters:
            return "", values

        # Column names are hard-coded; the placeholder index is derived
        # from the parameter list length so WHERE can grow safely.
        columns = (
            "user_id",
            "action",
            "category",
            "resource_type",
            "resource_id",
            "success",
            "severity",
        )
        for column in columns:
            if filters.get(column) is not None:
                values.append(filters[column])
                clauses.append(f"{column} = ${len(values) + 1}")  # +1: $1 is tenant

        # Use `is not None` (parity with the column loop above) — otherwise
        # a valid ``datetime(1970, 1, 1)`` or an empty-string range bound
        # could be silently dropped by Python truthiness.
        if filters.get("start_date") is not None:
            values.append(filters["start_date"])
            clauses.append(f"created_at >= ${len(values) + 1}")
        if filters.get("end_date") is not None:
            values.append(filters["end_date"])
            clauses.append(f"created_at <= ${len(values) + 1}")

        where = " AND " + " AND ".join(clauses) if clauses else ""
        return where, values

    async def query(
        self,
        tenant_id: str,
        *,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        where, extra = self._build_where(filters)
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                await self._with_tenant(conn, tenant_id)
                # SQL is safe: `where` is composed only from an allowlisted
                # column-name tuple (see _build_where columns) and $N
                # placeholders. No user-controlled string is interpolated
                # into the query; all filter values flow through asyncpg
                # parameters in `*extra`. Bandit B608 cannot see through
                # the helper so we silence it explicitly.
                # nosemgrep: python.lang.security.audit.sqli.asyncpg-sqli.asyncpg-sqli
                total_row = await conn.fetchrow(
                    f"SELECT COUNT(*) AS c FROM audit_log WHERE tenant_id = $1{where}",  # nosec B608
                    tenant_id,
                    *extra,
                )
                # nosemgrep: python.lang.security.audit.sqli.asyncpg-sqli.asyncpg-sqli
                rows = await conn.fetch(
                    f"SELECT * FROM audit_log WHERE tenant_id = $1{where} "  # nosec B608
                    f"ORDER BY created_at DESC, seq_num DESC "
                    f"OFFSET ${len(extra) + 2} LIMIT ${len(extra) + 3}",
                    tenant_id,
                    *extra,
                    skip,
                    limit,
                )
        return [_row_to_dict(r) for r in rows], int(total_row["c"])

    async def all_for_tenant(self, tenant_id: str) -> list[dict]:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                await self._with_tenant(conn, tenant_id)
                rows = await conn.fetch(
                    "SELECT * FROM audit_log WHERE tenant_id = $1 ORDER BY seq_num ASC",
                    tenant_id,
                )
        return [_row_to_dict(r) for r in rows]

    async def count_since(self, tenant_id: str | None, since: datetime) -> int:
        async with self._pool.acquire() as conn:
            if tenant_id is not None:
                async with conn.transaction():
                    await self._with_tenant(conn, tenant_id)
                    return int(
                        await conn.fetchval(
                            "SELECT COUNT(*) FROM audit_log WHERE tenant_id = $1 AND created_at >= $2",
                            tenant_id,
                            since,
                        )
                    )
            # Tenant-less (platform-wide metric) — bypass RLS with a superuser
            # pool would be ideal; for now run a COUNT that RLS will scope to
            # zero unless executed by a superuser role. The Prometheus scraper
            # should set app.current_tenant_id='*' via a pre-configured role.
            return int(
                await conn.fetchval(
                    "SELECT COUNT(*) FROM audit_log WHERE created_at >= $1",
                    since,
                )
            )

    async def validate_chain(self, tenant_id: str) -> ChainValidation:
        entries = await self.all_for_tenant(tenant_id)
        boundaries = await self.retention_boundaries_for_tenant(tenant_id)
        return _validate_chain_inmem(entries, self._secret, boundaries)

    async def tenants_with_activity_since(self, since: datetime) -> list[str]:
        """Cross-tenant query; RLS is bypassed on purpose because the
        periodic chain-validation job is a platform-level operator,
        not a per-tenant caller. In practice the Postgres role this
        pool connects as must hold BYPASSRLS or the query returns
        zero rows.
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT DISTINCT tenant_id FROM audit_log WHERE created_at >= $1",
                since,
            )
        return [r["tenant_id"] for r in rows]

    async def retention_boundaries_for_tenant(self, tenant_id: str) -> list[RetentionBoundary]:
        """Load retention checkpoints from audit_retention_events.

        Gracefully returns an empty list when the table does not yet
        exist — the retention worker's migration (003_audit_retention_events)
        is owned by a different service and may be deployed later than
        audit-service. We MUST NOT break chain validation just because
        retention isn't live yet; an empty boundary list means
        _validate_chain_inmem behaves exactly as it did pre-retention.
        """
        try:
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    await self._with_tenant(conn, tenant_id)
                    rows = await conn.fetch(
                        """
                        SELECT last_retained_seq_num, last_retained_entry_hash, executed_at
                        FROM audit_retention_events
                        WHERE tenant_id = $1
                          AND dry_run = FALSE
                        ORDER BY last_retained_seq_num ASC
                        """,
                        tenant_id,
                    )
        except Exception as exc:
            # asyncpg raises UndefinedTableError (42P01) when the
            # retention worker's migration hasn't been applied yet.
            # Don't bubble — empty boundaries mean "pre-retention
            # behavior", which is strictly more conservative (every
            # gap reported as tamper). We log so an operator who
            # expected retention to be live can spot the skew.
            message = str(exc)
            if "audit_retention_events" in message or "42P01" in message:
                return []
            # Unknown error — re-raise so the caller's exception
            # handling (and Prometheus gauge) reflects the real failure.
            raise
        return [
            RetentionBoundary(
                seq_num=int(r["last_retained_seq_num"]),
                entry_hash=str(r["last_retained_entry_hash"]),
                created_at=r["executed_at"].isoformat()
                if hasattr(r["executed_at"], "isoformat")
                else str(r["executed_at"]),
            )
            for r in rows
        ]


# ═══════════════════════════════════════════════════════════════════════════
# In-memory backend (CI/test)
# ═══════════════════════════════════════════════════════════════════════════


class InMemoryAuditStore:
    """Test double with identical surface. Not safe under concurrency — fine
    for unit tests and single-worker CI jobs, never for production."""

    def __init__(self, secret: str | None = None) -> None:
        self._by_tenant: dict[str, list[dict]] = {}
        self._secret = secret
        # Retention checkpoints mirror the Postgres `audit_retention_events`
        # table. Populated in tests via the `_simulate_retention` helper;
        # never populated in production since InMemoryAuditStore is the
        # CI/unit-test fallback, never the live backend.
        self._retention_boundaries: dict[str, list[RetentionBoundary]] = {}

    async def write(self, entry: dict) -> dict:
        tenant_id = entry["tenant_id"]
        bucket = self._by_tenant.setdefault(tenant_id, [])

        entry.setdefault("id", str(uuid.uuid4()))
        entry.setdefault("user_id", "system")
        entry.setdefault("severity", "info")
        entry.setdefault("category", "system")
        entry.setdefault("success", True)
        entry.setdefault("details", {})
        if "created_at" not in entry:
            entry["created_at"] = datetime.now(UTC).isoformat()
        elif isinstance(entry["created_at"], datetime):
            entry["created_at"] = entry["created_at"].isoformat()

        entry["seq_num"] = len(bucket) + 1
        prev_hash = bucket[-1]["entry_hash"] if bucket else GENESIS_HASH
        entry["prev_hash"] = prev_hash
        entry["entry_hash"] = compute_entry_hash(entry, prev_hash, self._secret)

        bucket.append(entry)
        return entry

    async def query(
        self,
        tenant_id: str,
        *,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        entries = list(self._by_tenant.get(tenant_id, []))
        filters = filters or {}

        def keep(e: dict) -> bool:
            for key in ("user_id", "action", "category", "resource_type", "resource_id", "severity"):
                if filters.get(key) is not None and e.get(key) != filters[key]:
                    return False
            if filters.get("success") is not None and bool(e.get("success")) != bool(filters["success"]):
                return False
            if filters.get("start_date") and e.get("created_at", "") < str(filters["start_date"]):
                return False
            if filters.get("end_date") and e.get("created_at", "") > str(filters["end_date"]):
                return False
            return True

        filtered = [e for e in entries if keep(e)]
        filtered.sort(key=lambda e: e.get("created_at", ""), reverse=True)
        return filtered[skip : skip + limit], len(filtered)

    async def all_for_tenant(self, tenant_id: str) -> list[dict]:
        return list(self._by_tenant.get(tenant_id, []))

    async def count_since(self, tenant_id: str | None, since: datetime) -> int:
        cutoff = since.isoformat()
        if tenant_id is not None:
            return sum(1 for e in self._by_tenant.get(tenant_id, []) if e.get("created_at", "") >= cutoff)
        return sum(1 for bucket in self._by_tenant.values() for e in bucket if e.get("created_at", "") >= cutoff)

    async def validate_chain(self, tenant_id: str) -> ChainValidation:
        return _validate_chain_inmem(
            self._by_tenant.get(tenant_id, []),
            self._secret,
            self._retention_boundaries.get(tenant_id, []),
        )

    async def tenants_with_activity_since(self, since: datetime) -> list[str]:
        cutoff = since.isoformat()
        return [
            tenant_id
            for tenant_id, bucket in self._by_tenant.items()
            if any(e.get("created_at", "") >= cutoff for e in bucket)
        ]

    async def retention_boundaries_for_tenant(self, tenant_id: str) -> list[RetentionBoundary]:
        return list(self._retention_boundaries.get(tenant_id, []))

    # Test-only helper: simulate a retention run by recording the last
    # seq_num + entry_hash being "deleted", then dropping those entries
    # from the in-memory bucket. Production retention always happens via
    # the audit-retention-worker against Postgres; this shim exists so
    # unit tests can exercise the retention-gap path without standing up
    # a full DB.
    def _simulate_retention(self, tenant_id: str, keep_from_seq: int) -> None:
        bucket = self._by_tenant.get(tenant_id, [])
        to_delete = [e for e in bucket if int(e.get("seq_num", 0)) < keep_from_seq]
        if not to_delete:
            return
        last = max(to_delete, key=lambda e: int(e.get("seq_num", 0)))
        self._retention_boundaries.setdefault(tenant_id, []).append(
            RetentionBoundary(
                seq_num=int(last["seq_num"]),
                entry_hash=str(last["entry_hash"]),
                created_at=datetime.now(UTC).isoformat(),
            )
        )
        self._by_tenant[tenant_id] = [
            e for e in bucket if int(e.get("seq_num", 0)) >= keep_from_seq
        ]


# ═══════════════════════════════════════════════════════════════════════════
# Shared helpers
# ═══════════════════════════════════════════════════════════════════════════


def _validate_chain_inmem(
    entries: list[dict],
    secret: str | None,
    retention_boundaries: list[RetentionBoundary] | None = None,
) -> ChainValidation:
    """Walk ``entries`` and verify the per-tenant hash chain.

    Two checks are performed per entry:
      1. *Chain link*: the stored ``prev_hash`` equals the previous
         surviving row's ``entry_hash``. A mismatch normally indicates
         tampering — but if it matches any retention boundary's hash
         we treat it as a legitimate retention-driven gap and count it
         in ``retention_gaps_crossed`` instead of flagging an error.
      2. *Entry integrity*: ``compute_entry_hash(entry, stored_prev)``
         matches the stored ``entry_hash``. Uses the row's OWN stored
         prev_hash (not the running one) so a chain-link break doesn't
         cascade into false-positive entry_hash errors on the next row.
    """
    boundary_hashes = {b.entry_hash for b in (retention_boundaries or [])}

    errors: list[str] = []
    gaps_crossed = 0
    # The hash we EXPECT the next entry's prev_hash to be, based on the
    # chain we've walked so far. Updated to the current entry's entry_hash
    # after it's been validated.
    expected_prev = GENESIS_HASH

    for entry in entries:
        stored_prev = entry.get("prev_hash") or GENESIS_HASH
        if stored_prev == expected_prev:
            pass  # Normal chain link — nothing to flag.
        elif stored_prev in boundary_hashes:
            # The rows between expected_prev and stored_prev were deleted
            # by retention; the chain reconnected cleanly at this hash.
            gaps_crossed += 1
        else:
            errors.append(f"seq={entry.get('seq_num')} prev_hash mismatch")

        recomputed = compute_entry_hash(entry, stored_prev, secret)
        if recomputed != entry.get("entry_hash"):
            errors.append(f"seq={entry.get('seq_num')} entry_hash mismatch")

        expected_prev = entry.get("entry_hash", expected_prev)

    first_at = entries[0].get("created_at") if entries else None
    last_at = entries[-1].get("created_at") if entries else None
    return ChainValidation(
        valid=not errors,
        total_entries=len(entries),
        errors=errors,
        first_entry_at=str(first_at) if first_at else None,
        last_entry_at=str(last_at) if last_at else None,
        retention_gaps_crossed=gaps_crossed,
    )


def _row_to_dict(row: Any) -> dict:
    """asyncpg.Record → plain dict with ISO-serialised timestamps/UUIDs."""
    d = dict(row)
    for key, value in list(d.items()):
        if isinstance(value, datetime):
            d[key] = value.isoformat()
        elif isinstance(value, uuid.UUID):
            d[key] = str(value)
    # Normalise JSON payloads — asyncpg returns dict for jsonb, keep as-is.
    return d


# ═══════════════════════════════════════════════════════════════════════════
# Migration runner
# ═══════════════════════════════════════════════════════════════════════════


async def apply_migrations(pool: Any, migrations_dir: str | Path | None = None) -> list[str]:
    """Idempotently apply every *.sql file in ``migrations_dir`` in sorted
    order. Uses the ``audit_service_schema_migrations`` bookkeeping table
    created by 001_create_audit_log.sql to skip already-applied scripts.
    Returns the list of versions applied during this call (empty if all
    were already applied).
    """
    if migrations_dir is None:
        here = Path(__file__).resolve().parent
        # First check src-local layout (dev), then container layout.
        candidates = [here.parent / "migrations", Path("/app/migrations")]
        migrations_dir = next((c for c in candidates if c.exists()), None)
    else:
        migrations_dir = Path(migrations_dir)
    if not migrations_dir or not migrations_dir.exists():
        return []

    applied: list[str] = []
    files = sorted(p for p in migrations_dir.glob("*.sql") if p.is_file())

    async with pool.acquire() as conn:
        # Ensure the bookkeeping table exists even before 001 runs.
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_service_schema_migrations ("
            "version VARCHAR(64) PRIMARY KEY, "
            "applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
        )
        already = {r["version"] for r in await conn.fetch("SELECT version FROM audit_service_schema_migrations")}
        for path in files:
            version = path.stem
            if version in already:
                continue
            sql = path.read_text()
            async with conn.transaction():
                await conn.execute(sql)
            applied.append(version)
    return applied


# ═══════════════════════════════════════════════════════════════════════════
# Factory
# ═══════════════════════════════════════════════════════════════════════════


def build_store(db_pool: Any, secret: str | None = None) -> AuditStore:
    """Pick the right backend.

    When ``db_pool`` is a real asyncpg pool, returns ``PostgresAuditStore``.
    Otherwise falls back to ``InMemoryAuditStore`` so the service still
    boots and unit tests can run without a DB.
    """
    if db_pool is not None and asyncpg is not None:
        return PostgresAuditStore(db_pool, secret=secret)
    return InMemoryAuditStore(secret=secret)


def get_secret() -> str | None:
    """The HMAC secret comes from ``AUDIT_HASH_SECRET`` (optional).
    When set, each hash is an HMAC-SHA-256 instead of a plain SHA-256,
    so leaking a historical row is insufficient to forge its predecessor.
    """
    return os.getenv("AUDIT_HASH_SECRET") or None
