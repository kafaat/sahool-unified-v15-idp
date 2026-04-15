"""
Tests for shared/db module — Database utilities
اختبارات وحدة قاعدة البيانات المشتركة

Covers:
- Migration dataclass (frozen, defaults)
- MigrationResult dataclass (mutable, defaults)
- SimpleMigrationRunner (run, rollback, status, get_current_version)
- tenant_connection context manager (RLS, cleanup, error handling)
- tenant_transaction context manager
- TenantPool wrapper
- verify_tenant_isolation helper
- setup_tenant_rls helper
- Module __init__ exports
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Migration dataclass
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMigrationDataclass:
    """Tests for the Migration frozen dataclass."""

    def test_create_migration_with_all_fields(self):
        """Should create a Migration with version, description, up, and down."""
        from shared.db.simple_migrations import Migration

        m = Migration(
            version=1,
            description="Create fields table",
            up="CREATE TABLE fields (id SERIAL PRIMARY KEY)",
            down="DROP TABLE IF EXISTS fields",
        )
        assert m.version == 1
        assert m.description == "Create fields table"
        assert m.up == "CREATE TABLE fields (id SERIAL PRIMARY KEY)"
        assert m.down == "DROP TABLE IF EXISTS fields"

    def test_migration_down_defaults_to_none(self):
        """down should default to None when not provided."""
        from shared.db.simple_migrations import Migration

        m = Migration(version=2, description="Add index", up="CREATE INDEX idx ON t(col)")
        assert m.down is None

    def test_migration_is_frozen(self):
        """Migration should be immutable (frozen dataclass)."""
        from shared.db.simple_migrations import Migration

        m = Migration(version=1, description="test", up="SELECT 1")
        with pytest.raises(AttributeError):
            m.version = 99  # type: ignore[misc]

    def test_migration_equality(self):
        """Two Migrations with same fields should be equal."""
        from shared.db.simple_migrations import Migration

        m1 = Migration(version=1, description="d", up="u", down="d")
        m2 = Migration(version=1, description="d", up="u", down="d")
        assert m1 == m2

    def test_migration_inequality(self):
        """Migrations with different versions should not be equal."""
        from shared.db.simple_migrations import Migration

        m1 = Migration(version=1, description="d", up="u")
        m2 = Migration(version=2, description="d", up="u")
        assert m1 != m2

    def test_migration_arabic_description(self):
        """Migration should accept Arabic descriptions (bilingual support)."""
        from shared.db.simple_migrations import Migration

        m = Migration(
            version=1,
            description="إنشاء جدول الحقول - Create fields table",
            up="CREATE TABLE fields (id SERIAL PRIMARY KEY)",
        )
        assert "إنشاء" in m.description
        assert "Create" in m.description


# ──────────────────────────────────────────────────────────────────────────────
# MigrationResult dataclass
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMigrationResult:
    """Tests for the MigrationResult dataclass."""

    def test_default_values(self):
        """MigrationResult should have sensible defaults."""
        from shared.db.simple_migrations import MigrationResult

        r = MigrationResult()
        assert r.applied == []
        assert r.skipped == []
        assert r.failed is None
        assert r.error is None
        assert r.dry_run is False

    def test_dry_run_flag(self):
        """dry_run flag should be settable."""
        from shared.db.simple_migrations import MigrationResult

        r = MigrationResult(dry_run=True)
        assert r.dry_run is True

    def test_mutable_lists(self):
        """applied and skipped lists should be mutable."""
        from shared.db.simple_migrations import MigrationResult

        r = MigrationResult()
        r.applied.append(1)
        r.skipped.append(2)
        assert r.applied == [1]
        assert r.skipped == [2]

    def test_error_tracking(self):
        """Should track failed version and error message."""
        from shared.db.simple_migrations import MigrationResult

        r = MigrationResult()
        r.failed = 3
        r.error = "column already exists"
        assert r.failed == 3
        assert r.error == "column already exists"


# ──────────────────────────────────────────────────────────────────────────────
# SimpleMigrationRunner.run()
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSimpleMigrationRunnerRun:
    """Tests for SimpleMigrationRunner.run() method."""

    def _make_runner(self, mock_pool):
        from shared.db.simple_migrations import SimpleMigrationRunner

        return SimpleMigrationRunner(mock_pool, service_name="test-service")

    def _make_migrations(self):
        from shared.db.simple_migrations import Migration

        return [
            Migration(version=1, description="Create table A", up="CREATE TABLE a (id INT)", down="DROP TABLE a"),
            Migration(version=2, description="Create table B", up="CREATE TABLE b (id INT)", down="DROP TABLE b"),
        ]

    def _mock_pool_and_conn(self, applied_versions=None):
        """Create a mock pool and connection with applied versions."""
        if applied_versions is None:
            applied_versions = set()

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[{"version": v} for v in applied_versions]
        )

        # Support async context manager for transaction
        mock_tx = AsyncMock()
        mock_tx.__aenter__ = AsyncMock(return_value=mock_tx)
        mock_tx.__aexit__ = AsyncMock(return_value=False)
        mock_conn.transaction = MagicMock(return_value=mock_tx)

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_pool.release = AsyncMock()

        # Support async context manager for acquire
        mock_pool.acquire.return_value = mock_conn
        mock_pool.acquire = AsyncMock(return_value=mock_conn)

        # Make pool.acquire() work as async context manager
        class _AcquireCM:
            async def __aenter__(self_inner):
                return mock_conn

            async def __aexit__(self_inner, *args):
                pass

        mock_pool.acquire = MagicMock(return_value=_AcquireCM())

        return mock_pool, mock_conn

    @pytest.mark.asyncio
    async def test_run_applies_all_pending_migrations(self):
        """Should apply all migrations when none have been applied yet."""
        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions=set())
        runner = self._make_runner(mock_pool)
        migrations = self._make_migrations()

        result = await runner.run(migrations)

        assert result.applied == [1, 2]
        assert result.skipped == []
        assert result.failed is None
        assert result.error is None

    @pytest.mark.asyncio
    async def test_run_skips_already_applied(self):
        """Should skip migrations that have already been applied."""
        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions={1})
        runner = self._make_runner(mock_pool)
        migrations = self._make_migrations()

        result = await runner.run(migrations)

        assert result.skipped == [1]
        assert result.applied == [2]

    @pytest.mark.asyncio
    async def test_run_skips_all_when_up_to_date(self):
        """Should skip all migrations when all are already applied."""
        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions={1, 2})
        runner = self._make_runner(mock_pool)
        migrations = self._make_migrations()

        result = await runner.run(migrations)

        assert result.skipped == [1, 2]
        assert result.applied == []

    @pytest.mark.asyncio
    async def test_run_duplicate_versions_raises(self):
        """Should raise ValueError for duplicate migration versions."""
        from shared.db.simple_migrations import Migration

        mock_pool, _ = self._mock_pool_and_conn()
        runner = self._make_runner(mock_pool)
        migrations = [
            Migration(version=1, description="First", up="SELECT 1"),
            Migration(version=1, description="Duplicate", up="SELECT 2"),
        ]

        with pytest.raises(ValueError, match="Duplicate migration versions"):
            await runner.run(migrations)

    @pytest.mark.asyncio
    async def test_run_applies_in_version_order(self):
        """Should apply migrations in ascending version order regardless of input order."""
        from shared.db.simple_migrations import Migration

        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions=set())
        runner = self._make_runner(mock_pool)

        # Intentionally out of order
        migrations = [
            Migration(version=3, description="Third", up="SELECT 3"),
            Migration(version=1, description="First", up="SELECT 1"),
            Migration(version=2, description="Second", up="SELECT 2"),
        ]

        result = await runner.run(migrations)
        assert result.applied == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_run_dry_run_does_not_execute(self):
        """dry_run=True should report pending migrations without executing."""
        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions=set())
        runner = self._make_runner(mock_pool)
        migrations = self._make_migrations()

        result = await runner.run(migrations, dry_run=True)

        assert result.applied == [1, 2]
        assert result.dry_run is True
        # In dry_run, CREATE TRACKING TABLE should not be called
        mock_conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_stops_on_failure(self):
        """Should stop applying subsequent migrations after a failure."""
        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions=set())

        # Track call count so we only fail during migration execution (not tracking table creation)
        execute_call_count = 0

        async def selective_execute_side_effect(*args, **kwargs):
            nonlocal execute_call_count
            execute_call_count += 1
            # Call 1: CREATE TRACKING TABLE - allow
            # Call 2+: migration SQL - fail
            if execute_call_count > 1:
                raise Exception("SQL error")

        mock_conn.execute = AsyncMock(side_effect=selective_execute_side_effect)

        # Override transaction to not swallow the exception
        class _TxCM:
            async def __aenter__(self_inner):
                return self_inner

            async def __aexit__(self_inner, exc_type, exc_val, exc_tb):
                return False

        mock_conn.transaction = MagicMock(return_value=_TxCM())

        runner = self._make_runner(mock_pool)
        migrations = self._make_migrations()

        result = await runner.run(migrations)

        assert result.failed == 1
        assert result.error == "SQL error"
        # Version 2 should NOT be in applied
        assert 2 not in result.applied


# ──────────────────────────────────────────────────────────────────────────────
# SimpleMigrationRunner.rollback()
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSimpleMigrationRunnerRollback:
    """Tests for SimpleMigrationRunner.rollback() method."""

    def _make_runner(self, mock_pool):
        from shared.db.simple_migrations import SimpleMigrationRunner

        return SimpleMigrationRunner(mock_pool, service_name="test-service")

    def _mock_pool_and_conn(self, applied_versions=None):
        if applied_versions is None:
            applied_versions = set()

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[{"version": v} for v in sorted(applied_versions)]
        )

        mock_tx = AsyncMock()
        mock_tx.__aenter__ = AsyncMock(return_value=mock_tx)
        mock_tx.__aexit__ = AsyncMock(return_value=False)
        mock_conn.transaction = MagicMock(return_value=mock_tx)

        mock_pool = AsyncMock()

        class _AcquireCM:
            async def __aenter__(self_inner):
                return mock_conn

            async def __aexit__(self_inner, *args):
                pass

        mock_pool.acquire = MagicMock(return_value=_AcquireCM())
        return mock_pool, mock_conn

    @pytest.mark.asyncio
    async def test_rollback_reverts_applied_migrations(self):
        """Should revert applied migrations in reverse order."""
        from shared.db.simple_migrations import Migration

        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions={1, 2})
        runner = self._make_runner(mock_pool)

        migrations = [
            Migration(version=1, description="A", up="CREATE TABLE a", down="DROP TABLE a"),
            Migration(version=2, description="B", up="CREATE TABLE b", down="DROP TABLE b"),
        ]

        result = await runner.rollback(migrations, target_version=0)
        assert 2 in result.applied
        assert 1 in result.applied

    @pytest.mark.asyncio
    async def test_rollback_to_target_version(self):
        """Should only revert versions above target_version."""
        from shared.db.simple_migrations import Migration

        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions={1, 2, 3})
        runner = self._make_runner(mock_pool)

        migrations = [
            Migration(version=1, description="A", up="u1", down="d1"),
            Migration(version=2, description="B", up="u2", down="d2"),
            Migration(version=3, description="C", up="u3", down="d3"),
        ]

        result = await runner.rollback(migrations, target_version=1)
        # Versions 2 and 3 should be reverted, version 1 should remain
        assert 3 in result.applied
        assert 2 in result.applied
        assert 1 not in result.applied

    @pytest.mark.asyncio
    async def test_rollback_raises_without_down_sql(self):
        """Should raise ValueError if a migration to revert has no down SQL."""
        from shared.db.simple_migrations import Migration

        mock_pool, _ = self._mock_pool_and_conn(applied_versions={1})
        runner = self._make_runner(mock_pool)

        migrations = [
            Migration(version=1, description="No rollback", up="CREATE TABLE x"),
        ]

        with pytest.raises(ValueError, match="has no rollback SQL"):
            await runner.rollback(migrations)

    @pytest.mark.asyncio
    async def test_rollback_dry_run(self):
        """dry_run should report pending rollbacks without executing."""
        from shared.db.simple_migrations import Migration

        mock_pool, mock_conn = self._mock_pool_and_conn(applied_versions={1, 2})
        runner = self._make_runner(mock_pool)

        migrations = [
            Migration(version=1, description="A", up="u1", down="d1"),
            Migration(version=2, description="B", up="u2", down="d2"),
        ]

        result = await runner.rollback(migrations, dry_run=True)
        assert result.dry_run is True
        assert 2 in result.applied
        assert 1 in result.applied
        # No execute calls for actual SQL
        mock_conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_rollback_skips_unapplied_migrations(self):
        """Should skip migrations that are not in the applied set."""
        from shared.db.simple_migrations import Migration

        mock_pool, _ = self._mock_pool_and_conn(applied_versions={2})
        runner = self._make_runner(mock_pool)

        migrations = [
            Migration(version=1, description="A", up="u1", down="d1"),
            Migration(version=2, description="B", up="u2", down="d2"),
        ]

        result = await runner.rollback(migrations, target_version=0)
        assert 1 in result.skipped
        assert 2 in result.applied


# ──────────────────────────────────────────────────────────────────────────────
# SimpleMigrationRunner.get_current_version() / get_status()
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSimpleMigrationRunnerStatus:
    """Tests for get_current_version() and get_status()."""

    def _mock_pool_and_conn(self, applied_versions=None):
        if applied_versions is None:
            applied_versions = set()

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[{"version": v} for v in sorted(applied_versions)]
        )

        mock_pool = AsyncMock()

        class _AcquireCM:
            async def __aenter__(self_inner):
                return mock_conn

            async def __aexit__(self_inner, *args):
                pass

        mock_pool.acquire = MagicMock(return_value=_AcquireCM())
        return mock_pool, mock_conn

    @pytest.mark.asyncio
    async def test_get_current_version_returns_max(self):
        """Should return the highest applied version."""
        from shared.db.simple_migrations import SimpleMigrationRunner

        mock_pool, _ = self._mock_pool_and_conn(applied_versions={1, 2, 3})
        runner = SimpleMigrationRunner(mock_pool)

        version = await runner.get_current_version()
        assert version == 3

    @pytest.mark.asyncio
    async def test_get_current_version_returns_none_when_empty(self):
        """Should return None when no migrations are applied."""
        from shared.db.simple_migrations import SimpleMigrationRunner

        mock_pool, _ = self._mock_pool_and_conn(applied_versions=set())
        runner = SimpleMigrationRunner(mock_pool)

        version = await runner.get_current_version()
        assert version is None

    @pytest.mark.asyncio
    async def test_get_status_up_to_date(self):
        """Should report up_to_date=True when all migrations applied."""
        from shared.db.simple_migrations import Migration, SimpleMigrationRunner

        mock_pool, _ = self._mock_pool_and_conn(applied_versions={1, 2})
        runner = SimpleMigrationRunner(mock_pool)

        migrations = [
            Migration(version=1, description="A", up="u1"),
            Migration(version=2, description="B", up="u2"),
        ]

        status = await runner.get_status(migrations)
        assert status["current_version"] == 2
        assert status["applied"] == [1, 2]
        assert status["pending"] == []
        assert status["up_to_date"] is True

    @pytest.mark.asyncio
    async def test_get_status_with_pending(self):
        """Should report pending versions when not all applied."""
        from shared.db.simple_migrations import Migration, SimpleMigrationRunner

        mock_pool, _ = self._mock_pool_and_conn(applied_versions={1})
        runner = SimpleMigrationRunner(mock_pool)

        migrations = [
            Migration(version=1, description="A", up="u1"),
            Migration(version=2, description="B", up="u2"),
            Migration(version=3, description="C", up="u3"),
        ]

        status = await runner.get_status(migrations)
        assert status["current_version"] == 1
        assert status["applied"] == [1]
        assert status["pending"] == [2, 3]
        assert status["up_to_date"] is False

    @pytest.mark.asyncio
    async def test_get_status_no_migrations_applied(self):
        """Should handle the case where no migrations are applied."""
        from shared.db.simple_migrations import Migration, SimpleMigrationRunner

        mock_pool, _ = self._mock_pool_and_conn(applied_versions=set())
        runner = SimpleMigrationRunner(mock_pool)

        migrations = [
            Migration(version=1, description="A", up="u1"),
        ]

        status = await runner.get_status(migrations)
        assert status["current_version"] is None
        assert status["applied"] == []
        assert status["pending"] == [1]
        assert status["up_to_date"] is False


# ──────────────────────────────────────────────────────────────────────────────
# tenant_connection context manager
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTenantConnectionContextManager:
    """Tests for tenant_connection() context manager."""

    def _mock_pool(self):
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_pool.release = AsyncMock()

        return mock_pool, mock_conn

    @pytest.mark.asyncio
    async def test_sets_tenant_session_variable(self):
        """Should call set_config with tenant_id."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool, mock_conn = self._mock_pool()

        async with tenant_connection(mock_pool, tenant_id="tenant-abc") as conn:
            assert conn is mock_conn

        calls = mock_conn.execute.call_args_list
        assert calls[0].args == (
            "SELECT set_config('app.current_tenant', $1, true)",
            "tenant-abc",
        )

    @pytest.mark.asyncio
    async def test_sets_non_admin_by_default(self):
        """Should set is_super_admin to false by default."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool, mock_conn = self._mock_pool()

        async with tenant_connection(mock_pool, tenant_id="t-1") as conn:
            pass

        calls = mock_conn.execute.call_args_list
        assert calls[1].args == (
            "SELECT set_config('app.is_super_admin', $1, true)",
            "false",
        )

    @pytest.mark.asyncio
    async def test_sets_admin_flag_when_requested(self):
        """Should set is_super_admin to true when is_admin=True."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool, mock_conn = self._mock_pool()

        async with tenant_connection(mock_pool, tenant_id="t-1", is_admin=True) as conn:
            pass

        calls = mock_conn.execute.call_args_list
        assert calls[1].args == (
            "SELECT set_config('app.is_super_admin', $1, true)",
            "true",
        )

    @pytest.mark.asyncio
    async def test_resets_session_variables_on_exit(self):
        """Should reset tenant and admin session variables on exit."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool, mock_conn = self._mock_pool()

        async with tenant_connection(mock_pool, tenant_id="t-1") as conn:
            pass

        calls = mock_conn.execute.call_args_list
        # Cleanup calls are the last two
        assert calls[-2].args == ("SELECT set_config('app.current_tenant', '', true)",)
        assert calls[-1].args == ("SELECT set_config('app.is_super_admin', 'false', true)",)

    @pytest.mark.asyncio
    async def test_releases_connection_to_pool(self):
        """Should release the connection back to the pool."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool, mock_conn = self._mock_pool()

        async with tenant_connection(mock_pool, tenant_id="t-1") as conn:
            pass

        mock_pool.release.assert_called_once_with(mock_conn)

    @pytest.mark.asyncio
    async def test_releases_connection_on_exception(self):
        """Should release connection even if user code raises."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool, mock_conn = self._mock_pool()

        with pytest.raises(ValueError, match="user error"):
            async with tenant_connection(mock_pool, tenant_id="t-1") as conn:
                raise ValueError("user error")

        mock_pool.release.assert_called_once_with(mock_conn)

    @pytest.mark.asyncio
    async def test_raises_runtime_error_for_empty_tenant(self):
        """Should raise RuntimeError when tenant_id is empty string."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool = AsyncMock()

        with pytest.raises(RuntimeError, match="tenant_id cannot be empty"):
            async with tenant_connection(mock_pool, tenant_id="") as conn:
                pass

    @pytest.mark.asyncio
    async def test_raises_runtime_error_without_tenant_or_context(self):
        """Should raise when no tenant_id and no middleware context.

        When tenant_id is not provided, tenant_connection tries to import
        get_current_tenant from shared.middleware.tenant_context. If that
        raises RuntimeError (no context set), tenant_connection should
        raise RuntimeError with 'tenant_id is required'.
        """
        from shared.db.tenant_connection import tenant_connection

        mock_pool = AsyncMock()

        # Mock the entire import path so we don't need fastapi installed
        mock_tenant_ctx = MagicMock()
        mock_tenant_ctx.get_current_tenant = MagicMock(
            side_effect=RuntimeError("No context"),
        )

        with patch.dict("sys.modules", {"shared.middleware.tenant_context": mock_tenant_ctx}):
            with pytest.raises(RuntimeError, match="tenant_id is required"):
                async with tenant_connection(mock_pool) as conn:
                    pass

    @pytest.mark.asyncio
    async def test_handles_cleanup_failure_gracefully(self):
        """Should not raise if cleanup set_config fails."""
        from shared.db.tenant_connection import tenant_connection

        mock_conn = AsyncMock()
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Fail on the third call (first cleanup call)
            if call_count >= 3:
                raise Exception("connection lost")

        mock_conn.execute = AsyncMock(side_effect=side_effect)

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_pool.release = AsyncMock()

        # Should not raise
        async with tenant_connection(mock_pool, tenant_id="t-1") as conn:
            pass

        # Connection should still be released
        mock_pool.release.assert_called_once_with(mock_conn)


# ──────────────────────────────────────────────────────────────────────────────
# TenantPool wrapper
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTenantPool:
    """Tests for TenantPool wrapper class."""

    def test_raw_pool_property(self):
        """Should expose the underlying asyncpg pool."""
        from shared.db.tenant_connection import TenantPool

        mock_pool = MagicMock()
        tp = TenantPool(mock_pool)
        assert tp.raw_pool is mock_pool

    @pytest.mark.asyncio
    async def test_acquire_delegates_to_tenant_connection(self):
        """acquire() should set RLS session variables."""
        from shared.db.tenant_connection import TenantPool

        mock_conn = AsyncMock()
        mock_raw_pool = AsyncMock()
        mock_raw_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_raw_pool.release = AsyncMock()

        tp = TenantPool(mock_raw_pool)

        async with tp.acquire(tenant_id="org-42") as conn:
            assert conn is mock_conn

        # Verify RLS was configured
        calls = mock_conn.execute.call_args_list
        assert calls[0].args[1] == "org-42"

    @pytest.mark.asyncio
    async def test_close_delegates_to_pool(self):
        """close() should close the underlying pool."""
        from shared.db.tenant_connection import TenantPool

        mock_raw_pool = AsyncMock()
        tp = TenantPool(mock_raw_pool)

        await tp.close()
        mock_raw_pool.close.assert_called_once()


# ──────────────────────────────────────────────────────────────────────────────
# verify_tenant_isolation
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestVerifyTenantIsolation:
    """Tests for verify_tenant_isolation() helper."""

    @pytest.mark.asyncio
    async def test_returns_false_when_no_pool(self):
        """Should return False and warn if app has no db_pool."""
        from shared.db.tenant_connection import verify_tenant_isolation

        mock_app = MagicMock()
        mock_app.state = MagicMock(spec=[])  # No db_pool attr

        result = await verify_tenant_isolation(mock_app)
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_true_when_all_tables_have_rls(self):
        """Should return True when all critical tables have RLS enabled and forced."""
        from shared.db.tenant_connection import verify_tenant_isolation

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={"relrowsecurity": True, "relforcerowsecurity": True}
        )

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_pool.release = AsyncMock()

        mock_app = MagicMock()
        mock_app.state.db_pool = mock_pool

        result = await verify_tenant_isolation(mock_app)
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_rls_not_enabled(self):
        """Should return False when relrowsecurity is False."""
        from shared.db.tenant_connection import verify_tenant_isolation

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={"relrowsecurity": False, "relforcerowsecurity": False}
        )

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_pool.release = AsyncMock()

        mock_app = MagicMock()
        mock_app.state.db_pool = mock_pool

        result = await verify_tenant_isolation(mock_app)
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_when_rls_not_forced(self):
        """Should return False when relforcerowsecurity is False."""
        from shared.db.tenant_connection import verify_tenant_isolation

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={"relrowsecurity": True, "relforcerowsecurity": False}
        )

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_pool.release = AsyncMock()

        mock_app = MagicMock()
        mock_app.state.db_pool = mock_pool

        result = await verify_tenant_isolation(mock_app)
        assert result is False

    @pytest.mark.asyncio
    async def test_skips_nonexistent_tables(self):
        """Should skip tables that do not exist (fetchrow returns None)."""
        from shared.db.tenant_connection import verify_tenant_isolation

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(return_value=mock_conn)
        mock_pool.release = AsyncMock()

        mock_app = MagicMock()
        mock_app.state.db_pool = mock_pool

        result = await verify_tenant_isolation(mock_app)
        assert result is True  # No tables to check => all OK

    @pytest.mark.asyncio
    async def test_returns_false_on_connection_error(self):
        """Should return False if DB connection fails."""
        from shared.db.tenant_connection import verify_tenant_isolation

        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock(side_effect=Exception("connection refused"))

        mock_app = MagicMock()
        mock_app.state.db_pool = mock_pool

        result = await verify_tenant_isolation(mock_app)
        assert result is False


# ──────────────────────────────────────────────────────────────────────────────
# setup_tenant_rls
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSetupTenantRls:
    """Tests for setup_tenant_rls() helper function."""

    def test_registers_tenant_pool_on_app_state(self):
        """Should create a TenantPool and set it on app.state.tenant_pool."""
        from shared.db.tenant_connection import TenantPool, setup_tenant_rls

        mock_pool = MagicMock()
        mock_app = MagicMock()

        setup_tenant_rls(mock_app, mock_pool)

        assert hasattr(mock_app.state, "tenant_pool")
        tenant_pool = mock_app.state.tenant_pool
        assert isinstance(tenant_pool, TenantPool)
        assert tenant_pool.raw_pool is mock_pool


# ──────────────────────────────────────────────────────────────────────────────
# Module __init__ exports
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestModuleExports:
    """Tests for shared.db module __init__.py exports."""

    def test_exports_migration(self):
        """Should export Migration from the package."""
        from shared.db import Migration

        assert Migration is not None

    def test_exports_simple_migration_runner(self):
        """Should export SimpleMigrationRunner from the package."""
        from shared.db import SimpleMigrationRunner

        assert SimpleMigrationRunner is not None

    def test_exports_tenant_pool(self):
        """Should export TenantPool from the package."""
        from shared.db import TenantPool

        assert TenantPool is not None

    def test_exports_tenant_connection(self):
        """Should export tenant_connection from the package."""
        from shared.db import tenant_connection

        assert callable(tenant_connection)

    def test_exports_tenant_transaction(self):
        """Should export tenant_transaction from the package."""
        from shared.db import tenant_transaction

        assert callable(tenant_transaction)

    def test_all_list_completeness(self):
        """__all__ should list all public exports."""
        import shared.db as db_module

        expected = {
            "Migration",
            "SimpleMigrationRunner",
            "TenantPool",
            "tenant_connection",
            "tenant_transaction",
        }
        assert set(db_module.__all__) == expected


# ──────────────────────────────────────────────────────────────────────────────
# _get_applied_versions internal helper
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestGetAppliedVersionsInternal:
    """Tests for the _get_applied_versions internal helper."""

    @pytest.mark.asyncio
    async def test_returns_set_from_tracking_table(self):
        """Should parse version rows into a set of ints."""
        from shared.db.simple_migrations import SimpleMigrationRunner

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[{"version": 1}, {"version": 3}, {"version": 5}]
        )

        mock_pool = MagicMock()
        runner = SimpleMigrationRunner(mock_pool)

        result = await runner._get_applied_versions(mock_conn)
        assert result == {1, 3, 5}

    @pytest.mark.asyncio
    async def test_returns_empty_set_on_error_in_dry_run(self):
        """Should return empty set if tracking table does not exist during dry_run."""
        from shared.db.simple_migrations import SimpleMigrationRunner

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            side_effect=Exception("relation _schema_migrations does not exist")
        )

        mock_pool = MagicMock()
        runner = SimpleMigrationRunner(mock_pool)

        result = await runner._get_applied_versions(mock_conn, dry_run=True)
        assert result == set()

    @pytest.mark.asyncio
    async def test_raises_on_error_outside_dry_run(self):
        """Should re-raise if tracking table does not exist outside dry_run."""
        from shared.db.simple_migrations import SimpleMigrationRunner

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            side_effect=Exception("relation does not exist")
        )

        mock_pool = MagicMock()
        runner = SimpleMigrationRunner(mock_pool)

        with pytest.raises(Exception, match="relation does not exist"):
            await runner._get_applied_versions(mock_conn, dry_run=False)


# ──────────────────────────────────────────────────────────────────────────────
# Tracking table constant
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTrackingTableConstant:
    """Tests for module-level tracking table constants."""

    def test_tracking_table_name(self):
        """Tracking table should be named _schema_migrations."""
        from shared.db.simple_migrations import _TRACKING_TABLE

        assert _TRACKING_TABLE == "_schema_migrations"

    def test_create_tracking_table_sql_contains_version_column(self):
        """CREATE TABLE SQL should define a version INTEGER PRIMARY KEY column."""
        from shared.db.simple_migrations import _CREATE_TRACKING_TABLE

        assert "version" in _CREATE_TRACKING_TABLE
        assert "INTEGER" in _CREATE_TRACKING_TABLE
        assert "PRIMARY KEY" in _CREATE_TRACKING_TABLE

    def test_create_tracking_table_sql_contains_description(self):
        """CREATE TABLE SQL should include a description column."""
        from shared.db.simple_migrations import _CREATE_TRACKING_TABLE

        assert "description" in _CREATE_TRACKING_TABLE
        assert "TEXT" in _CREATE_TRACKING_TABLE

    def test_create_tracking_table_sql_contains_applied_at(self):
        """CREATE TABLE SQL should include applied_at with default NOW()."""
        from shared.db.simple_migrations import _CREATE_TRACKING_TABLE

        assert "applied_at" in _CREATE_TRACKING_TABLE
        assert "TIMESTAMPTZ" in _CREATE_TRACKING_TABLE
        assert "NOW()" in _CREATE_TRACKING_TABLE

    def test_create_tracking_table_sql_is_idempotent(self):
        """CREATE TABLE SQL should use IF NOT EXISTS for idempotency."""
        from shared.db.simple_migrations import _CREATE_TRACKING_TABLE

        assert "IF NOT EXISTS" in _CREATE_TRACKING_TABLE
