"""
Retention logic tests.

We test against an in-process fake that speaks enough of asyncpg's surface
to exercise run_policy_for_tenant's transaction + SQL flow. This keeps the
suite fast and deterministic — correctness of the SQL itself is covered by
an integration test in tests/integration/test_audit_retention.py (out of
scope for this module; runs only when ``SAHOOL_TEST_DB_URL`` is set).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from src.policies import RetentionPolicy
from src.retention import run_policy_for_tenant, run_sweep

# ═════════════════════════════════════════════════════════════════════════
# Minimal asyncpg fake — enough surface for the worker to run against.
# ═════════════════════════════════════════════════════════════════════════


@dataclass
class _Row:
    """Mimics asyncpg.Record's __getitem__ interface."""

    data: dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.data[key]


@dataclass
class FakeRow:
    id: str
    tenant_id: str
    seq_num: int
    category: str
    created_at: datetime
    entry_hash: str


class FakeTransaction:
    def __init__(self, conn: FakeConn) -> None:
        self._conn = conn

    async def __aenter__(self) -> FakeTransaction:
        self._conn.tx_depth += 1
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self._conn.tx_depth -= 1
        if exc_type is not None:
            self._conn.rolled_back = True


class FakeConn:
    """In-memory stand-in for an asyncpg connection.

    Supports only the queries the worker actually issues — deliberately
    narrow so the fake can't drift silently into permitting queries the
    real DB would reject.
    """

    def __init__(self, rows: list[FakeRow], bypassrls: bool | None = True) -> None:
        self.rows = rows
        self.events: list[dict[str, Any]] = []
        self.archived: list[FakeRow] = []
        self.executed: list[str] = []
        self.tx_depth = 0
        self.rolled_back = False
        self.session_vars: dict[str, Any] = {}
        self._bypassrls = bypassrls

    def transaction(self) -> FakeTransaction:
        return FakeTransaction(self)

    async def execute(self, query: str, *args: Any) -> str:
        self.executed.append(query)
        normalised = " ".join(query.split())

        if normalised.startswith("SET LOCAL sahool.audit_retention_job"):
            self.session_vars["sahool.audit_retention_job"] = "on"
            return "SET"

        if normalised.startswith("SELECT set_config"):
            self.session_vars["app.current_tenant_id"] = args[0]
            return "SELECT 1"

        if normalised.startswith("INSERT INTO audit_retention_events"):
            (
                tenant_id,
                last_seq_num,
                last_hash,
                rows_deleted,
                deleted_hashes,
                category,
                retention_days,
                cutoff,
                archive_location,
                dry_run,
            ) = args
            self.events.append(
                {
                    "tenant_id": tenant_id,
                    "last_deleted_seq_num": last_seq_num,
                    "last_deleted_entry_hash": last_hash,
                    "rows_deleted": rows_deleted,
                    "deleted_entry_hashes": list(deleted_hashes),
                    "category_filter": category,
                    "retention_days": retention_days,
                    "cutoff_timestamp": cutoff,
                    "archive_location": archive_location,
                    "dry_run": dry_run,
                }
            )
            return "INSERT 0 1"

        raise AssertionError(f"Unexpected execute(): {normalised!r}")

    async def fetchrow(self, query: str, *args: Any) -> _Row | None:
        self.executed.append(query)
        normalised = " ".join(query.split())

        if normalised.startswith("SELECT set_config"):
            return _Row({"set_config": str(args[0])})

        if normalised.startswith("SELECT COUNT(*) AS n FROM audit_log"):
            tenant_id, category, cutoff = args
            n = sum(
                1 for r in self.rows if r.tenant_id == tenant_id and r.category == category and r.created_at < cutoff
            )
            return _Row({"n": n})

        if normalised.startswith("SELECT rolbypassrls"):
            if self._bypassrls is None:
                return None
            return _Row({"rolbypassrls": self._bypassrls})

        raise AssertionError(f"Unexpected fetchrow(): {normalised!r}")

    async def fetch(self, query: str, *args: Any) -> list[_Row]:
        self.executed.append(query)
        normalised = " ".join(query.split())

        if normalised == "SELECT DISTINCT tenant_id FROM audit_log":
            uniq = sorted({r.tenant_id for r in self.rows})
            return [_Row({"tenant_id": t}) for t in uniq]

        if normalised.startswith("INSERT INTO audit_log_archive"):
            # INSERT ... SELECT ... FROM audit_log WHERE ... RETURNING seq_num
            # Emulate by finding the matching rows and appending them to
            # `self.archived`. ON CONFLICT DO NOTHING means rows already
            # in archive (by (tenant_id, seq_num)) don't get duplicated.
            tenant_id, category, cutoff = args
            matches = [
                r for r in self.rows
                if r.tenant_id == tenant_id and r.category == category and r.created_at < cutoff
            ]
            archived_keys = {(a.tenant_id, a.seq_num) for a in self.archived}
            inserted: list[FakeRow] = []
            for r in matches:
                if (r.tenant_id, r.seq_num) in archived_keys:
                    continue
                self.archived.append(r)
                inserted.append(r)
            return [_Row({"seq_num": r.seq_num}) for r in inserted]

        if normalised.startswith("DELETE FROM audit_log"):
            # DELETE ... RETURNING seq_num, entry_hash — emulate by
            # partitioning out the matching rows and returning them.
            tenant_id, category, cutoff = args
            kept: list[FakeRow] = []
            deleted: list[FakeRow] = []
            for r in self.rows:
                if r.tenant_id == tenant_id and r.category == category and r.created_at < cutoff:
                    deleted.append(r)
                else:
                    kept.append(r)
            self.rows = kept
            # Real Postgres returns rows in the order they were deleted —
            # for our purposes any order works since the worker sorts
            # them by seq_num. Keep it stable for test assertions.
            deleted.sort(key=lambda r: r.seq_num)
            return [_Row({"seq_num": r.seq_num, "entry_hash": r.entry_hash}) for r in deleted]

        raise AssertionError(f"Unexpected fetch(): {normalised!r}")


class FakePool:
    """Minimal asyncpg.Pool surface — only ``acquire()``."""

    def __init__(self, conn: FakeConn) -> None:
        self._conn = conn

    def acquire(self) -> FakePoolAcquire:
        return FakePoolAcquire(self._conn)


@dataclass
class FakePoolAcquire:
    conn: FakeConn

    async def __aenter__(self) -> FakeConn:
        return self.conn

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


# ═════════════════════════════════════════════════════════════════════════
# Fixtures
# ═════════════════════════════════════════════════════════════════════════


NOW = datetime(2026, 4, 17, 12, 0, 0, tzinfo=UTC)


def _rows_for(tenant: str, category: str, ages_days: list[int], *, start_seq: int = 1) -> list[FakeRow]:
    """Build a set of rows whose age spans ``ages_days``.

    ``entry_hash`` is a deterministic value keyed to seq_num so assertions
    can predict what hash gets recorded in the retention event.
    """
    return [
        FakeRow(
            id=f"{tenant}-{start_seq + i}",
            tenant_id=tenant,
            seq_num=start_seq + i,
            category=category,
            created_at=NOW - timedelta(days=age),
            entry_hash=f"hash-{tenant}-{start_seq + i:04d}".ljust(64, "0"),
        )
        for i, age in enumerate(ages_days)
    ]


# ═════════════════════════════════════════════════════════════════════════
# Tests
# ═════════════════════════════════════════════════════════════════════════


class TestRunPolicyForTenant:
    @pytest.mark.asyncio
    async def test_deletes_rows_older_than_cutoff(self) -> None:
        rows = _rows_for("t1", "authentication", ages_days=[120, 100, 80, 30, 5])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="authentication", retention_days=90)

        result = await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=False)

        # Rows older than 90 days: 120, 100 → 2 deletions.
        assert result.rows_deleted == 2
        assert len(conn.rows) == 3
        remaining_ages = sorted(int((NOW - r.created_at).days) for r in conn.rows)
        assert remaining_ages == [5, 30, 80]

    @pytest.mark.asyncio
    async def test_records_event_with_all_deleted_hashes(self) -> None:
        rows = _rows_for("t1", "billing", ages_days=[2000, 1900, 500])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="billing", retention_days=1825)

        result = await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=False)

        assert len(conn.events) == 1
        event = conn.events[0]
        # Rows aged 2000 and 1900 deleted (seq 1 and 2).
        assert event["last_deleted_seq_num"] == 2
        assert event["last_deleted_entry_hash"].startswith("hash-t1-0002")
        assert event["rows_deleted"] == 2
        # The critical invariant for retention-aware chain validation:
        # every deleted hash must appear in deleted_entry_hashes so
        # validate_chain() can recognise any prev_hash match as legitimate.
        assert len(event["deleted_entry_hashes"]) == 2
        assert all(h.startswith("hash-t1-") for h in event["deleted_entry_hashes"])
        # Order matches the DELETE ... RETURNING sort (seq_num ascending).
        assert event["deleted_entry_hashes"][0].startswith("hash-t1-0001")
        assert event["deleted_entry_hashes"][1].startswith("hash-t1-0002")
        assert event["category_filter"] == "billing"
        assert event["retention_days"] == 1825
        assert event["dry_run"] is False
        # Result surfaces the full hash list too.
        assert result.deleted_entry_hashes == event["deleted_entry_hashes"]

    @pytest.mark.asyncio
    async def test_category_filter_leaves_other_categories_untouched(self) -> None:
        rows = [
            *_rows_for("t1", "authentication", ages_days=[120, 5], start_seq=1),
            *_rows_for("t1", "billing", ages_days=[120, 5], start_seq=10),
        ]
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="authentication", retention_days=90)

        await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=False)

        # Billing row aged 120 should still be there.
        billing = [r for r in conn.rows if r.category == "billing"]
        assert len(billing) == 2

    @pytest.mark.asyncio
    async def test_noop_when_nothing_expired(self) -> None:
        rows = _rows_for("t1", "authentication", ages_days=[30, 5])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="authentication", retention_days=90)

        result = await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=False)

        assert result.rows_deleted == 0
        assert result.was_noop is True
        # No-ops must NOT create retention_events rows.
        assert conn.events == []
        assert result.last_deleted_seq_num is None
        assert result.deleted_entry_hashes == []

    @pytest.mark.asyncio
    async def test_dry_run_deletes_nothing_but_reports_what_would_be_deleted(
        self,
    ) -> None:
        rows = _rows_for("t1", "system", ages_days=[200, 100, 10])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="system", retention_days=90)

        result = await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=True)

        assert result.dry_run is True
        assert result.rows_deleted == 2
        # Crucially: rows + events unchanged, no hashes recorded.
        assert len(conn.rows) == 3
        assert conn.events == []
        assert result.deleted_entry_hashes == []

    @pytest.mark.asyncio
    async def test_sets_retention_session_variable(self) -> None:
        """Without this session variable the append-only trigger rejects
        the DELETE — regressing this silently would make the worker a
        permanent no-op in production."""
        rows = _rows_for("t1", "authentication", ages_days=[120])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="authentication", retention_days=90)

        await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=False)

        assert conn.session_vars.get("sahool.audit_retention_job") == "on"

    @pytest.mark.asyncio
    async def test_archives_every_expired_row_before_delete(self) -> None:
        """Every deleted row must be present in audit_log_archive. Without
        this, the replay endpoint (/api/v1/audit/logs/archived) returns
        404 for compliance queries spanning the retention boundary — the
        exact gap this migration was introduced to close."""
        rows = _rows_for("t1", "authentication", ages_days=[200, 150, 120, 5])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="authentication", retention_days=90)

        await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=False)

        # Three rows older than 90 days (200, 150, 120) should have been
        # archived AND deleted. Archive retains them; audit_log does not.
        assert len(conn.archived) == 3
        archived_seq_nums = sorted(a.seq_num for a in conn.archived)
        assert archived_seq_nums == [1, 2, 3]
        # Audit log has just the surviving row (age 5, seq 4).
        assert len(conn.rows) == 1
        assert conn.rows[0].seq_num == 4

    @pytest.mark.asyncio
    async def test_records_archive_location_uri(self) -> None:
        """The retention_events row must carry the archive URI so
        compliance tooling can locate where the content went. Without
        this, auditors know rows were deleted but can't find them."""
        rows = _rows_for("t1", "billing", ages_days=[2000])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="billing", retention_days=1825)

        await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=False)

        assert len(conn.events) == 1
        assert conn.events[0]["archive_location"] == "pg://audit_log_archive"

    @pytest.mark.asyncio
    async def test_dry_run_does_not_archive(self) -> None:
        """Dry-run must leave both audit_log AND audit_log_archive
        untouched. An archive write during dry-run would turn "preview"
        into "irreversible side-effect"."""
        rows = _rows_for("t1", "system", ages_days=[200, 100])
        conn = FakeConn(rows)
        policy = RetentionPolicy(category="system", retention_days=90)

        await run_policy_for_tenant(conn, tenant_id="t1", policy=policy, now=NOW, dry_run=True)

        assert len(conn.rows) == 2  # nothing deleted
        assert conn.archived == []  # nothing archived


class TestRunSweep:
    @pytest.mark.asyncio
    async def test_covers_every_tenant_and_policy(self) -> None:
        rows = [
            *_rows_for("tenant-a", "authentication", ages_days=[120], start_seq=1),
            *_rows_for("tenant-b", "authentication", ages_days=[120], start_seq=10),
        ]
        conn = FakeConn(rows)
        pool = FakePool(conn)
        policies = [RetentionPolicy(category="authentication", retention_days=90)]

        summary = await run_sweep(pool, policies, now=NOW)

        assert summary.total_deleted == 2
        assert summary.tenants_touched == 2
        # Each (tenant × policy) produces one RetentionRunResult.
        assert len(summary.runs) == 2

    @pytest.mark.asyncio
    async def test_raises_on_zero_tenants_without_bypassrls(self) -> None:
        """If policies are configured but list_tenants returns empty AND
        the current role lacks BYPASSRLS, we've almost certainly got an
        RLS misconfiguration and the sweep would silently delete nothing.
        Fail loud instead."""
        conn = FakeConn(rows=[], bypassrls=False)
        pool = FakePool(conn)
        policies = [RetentionPolicy(category="authentication", retention_days=90)]

        with pytest.raises(RuntimeError, match="BYPASSRLS"):
            await run_sweep(pool, policies, now=NOW)

    @pytest.mark.asyncio
    async def test_empty_tenants_with_bypassrls_is_ok(self) -> None:
        """Legitimate empty audit_log — BYPASSRLS is set, no rows exist.
        Logs a warning but doesn't raise."""
        conn = FakeConn(rows=[], bypassrls=True)
        pool = FakePool(conn)
        policies = [RetentionPolicy(category="authentication", retention_days=90)]

        summary = await run_sweep(pool, policies, now=NOW)
        assert summary.total_deleted == 0
        assert summary.runs == []


# pytest-asyncio hook: treat all coroutine tests as asyncio-driven without
# needing per-test `@pytest.mark.asyncio` in strict mode.
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
