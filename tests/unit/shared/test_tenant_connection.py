"""
Tests for SAHOOL Tenant-Aware Database Connection
اختبارات اتصال قاعدة البيانات مع عزل المستأجرين

Tests that:
- RLS session variables are set correctly via set_config()
- Session variables are reset on connection release
- TenantPool wrapper works correctly
- Auto-detection from TenantContextMiddleware works
- Error handling for missing tenant_id
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.unit
class TestTenantConnection:
    """Tests for tenant_connection context manager."""

    @pytest.mark.asyncio
    async def test_sets_rls_session_variables(self):
        """Should set app.current_tenant and app.is_super_admin via set_config."""
        from shared.db.tenant_connection import tenant_connection

        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_pool.release = AsyncMock()

        async with tenant_connection(mock_pool, tenant_id="org-123") as conn:
            assert conn is mock_conn

        # Verify set_config calls (SQL-injection safe)
        calls = mock_conn.execute.call_args_list
        assert len(calls) >= 4  # 2 setup + 2 cleanup

        # Setup calls
        assert calls[0].args == (
            "SELECT set_config('app.current_tenant', $1, true)",
            "org-123",
        )
        assert calls[1].args == (
            "SELECT set_config('app.is_super_admin', $1, true)",
            "false",
        )

    @pytest.mark.asyncio
    async def test_sets_admin_flag(self):
        """Should set is_super_admin=true when is_admin=True."""
        from shared.db.tenant_connection import tenant_connection

        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_pool.release = AsyncMock()

        async with tenant_connection(
            mock_pool, tenant_id="org-123", is_admin=True
        ) as conn:
            pass

        calls = mock_conn.execute.call_args_list
        assert calls[1].args == (
            "SELECT set_config('app.is_super_admin', $1, true)",
            "true",
        )

    @pytest.mark.asyncio
    async def test_resets_session_on_release(self):
        """Should reset RLS session variables before returning connection to pool."""
        from shared.db.tenant_connection import tenant_connection

        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_pool.release = AsyncMock()

        async with tenant_connection(mock_pool, tenant_id="org-123") as conn:
            pass

        # Last calls should be the cleanup
        calls = mock_conn.execute.call_args_list
        assert calls[-2].args == (
            "SELECT set_config('app.current_tenant', '', true)",
        )
        assert calls[-1].args == (
            "SELECT set_config('app.is_super_admin', 'false', true)",
        )

        # Pool release should be called
        mock_pool.release.assert_called_once_with(mock_conn)

    @pytest.mark.asyncio
    async def test_raises_without_tenant_id(self):
        """Should raise RuntimeError when no tenant_id and no middleware context."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool = AsyncMock()

        with patch(
            "shared.middleware.tenant_context.get_current_tenant",
            side_effect=RuntimeError("No context"),
        ):
            with pytest.raises(RuntimeError, match="tenant_id is required"):
                async with tenant_connection(mock_pool) as conn:
                    pass

    @pytest.mark.asyncio
    async def test_raises_with_empty_tenant_id(self):
        """Should raise RuntimeError when tenant_id is empty string."""
        from shared.db.tenant_connection import tenant_connection

        mock_pool = AsyncMock()

        with pytest.raises(RuntimeError, match="tenant_id cannot be empty"):
            async with tenant_connection(mock_pool, tenant_id="") as conn:
                pass

    @pytest.mark.asyncio
    async def test_auto_detects_from_middleware(self):
        """Should auto-detect tenant_id from TenantContextMiddleware."""
        from shared.db.tenant_connection import tenant_connection
        from shared.middleware.tenant_context import TenantContext

        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_pool.release = AsyncMock()

        mock_ctx = TenantContext(
            id="auto-org-456", user_id="user-1", roles=["viewer"]
        )

        with patch(
            "shared.middleware.tenant_context.get_current_tenant",
            return_value=mock_ctx,
        ):
            async with tenant_connection(mock_pool) as conn:
                pass

        calls = mock_conn.execute.call_args_list
        assert calls[0].args == (
            "SELECT set_config('app.current_tenant', $1, true)",
            "auto-org-456",
        )
        # Non-admin user
        assert calls[1].args == (
            "SELECT set_config('app.is_super_admin', $1, true)",
            "false",
        )

    @pytest.mark.asyncio
    async def test_auto_detects_admin_from_middleware(self):
        """Should auto-detect admin role from middleware context."""
        from shared.db.tenant_connection import tenant_connection
        from shared.middleware.tenant_context import TenantContext

        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_pool.release = AsyncMock()

        mock_ctx = TenantContext(
            id="org-789", user_id="admin-1", roles=["admin"]
        )

        with patch(
            "shared.middleware.tenant_context.get_current_tenant",
            return_value=mock_ctx,
        ):
            async with tenant_connection(mock_pool) as conn:
                pass

        calls = mock_conn.execute.call_args_list
        assert calls[1].args == (
            "SELECT set_config('app.is_super_admin', $1, true)",
            "true",
        )

    @pytest.mark.asyncio
    async def test_cleanup_on_exception(self):
        """Should still reset session and release connection on exception."""
        from shared.db.tenant_connection import tenant_connection

        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn
        mock_pool.release = AsyncMock()

        with pytest.raises(ValueError):
            async with tenant_connection(mock_pool, tenant_id="org-123") as conn:
                raise ValueError("test error")

        # Cleanup should still happen
        mock_pool.release.assert_called_once_with(mock_conn)


@pytest.mark.unit
class TestTenantPool:
    """Tests for TenantPool wrapper."""

    @pytest.mark.asyncio
    async def test_acquire_sets_rls(self):
        """TenantPool.acquire should set RLS session variables."""
        from shared.db.tenant_connection import TenantPool

        mock_conn = AsyncMock()
        mock_raw_pool = AsyncMock()
        mock_raw_pool.acquire.return_value = mock_conn
        mock_raw_pool.release = AsyncMock()

        pool = TenantPool(mock_raw_pool)

        async with pool.acquire(tenant_id="org-100") as conn:
            assert conn is mock_conn

        calls = mock_conn.execute.call_args_list
        assert calls[0].args[1] == "org-100"

    def test_raw_pool_access(self):
        """Should expose raw_pool for health checks."""
        from shared.db.tenant_connection import TenantPool

        mock_raw_pool = MagicMock()
        pool = TenantPool(mock_raw_pool)
        assert pool.raw_pool is mock_raw_pool


@pytest.mark.unit
class TestTenantContextHelpers:
    """Tests for is_current_user_admin helper."""

    def test_is_admin_with_admin_role(self):
        """Should return True for admin role."""
        from shared.middleware.tenant_context import (
            TenantContext,
            _tenant_context,
            is_current_user_admin,
        )

        ctx = TenantContext(id="org-1", roles=["admin"])
        token = _tenant_context.set(ctx)
        try:
            assert is_current_user_admin() is True
        finally:
            _tenant_context.reset(token)

    def test_is_admin_with_super_admin_role(self):
        """Should return True for super_admin role."""
        from shared.middleware.tenant_context import (
            TenantContext,
            _tenant_context,
            is_current_user_admin,
        )

        ctx = TenantContext(id="org-1", roles=["super_admin"])
        token = _tenant_context.set(ctx)
        try:
            assert is_current_user_admin() is True
        finally:
            _tenant_context.reset(token)

    def test_is_not_admin_with_viewer_role(self):
        """Should return False for non-admin roles."""
        from shared.middleware.tenant_context import (
            TenantContext,
            _tenant_context,
            is_current_user_admin,
        )

        ctx = TenantContext(id="org-1", roles=["viewer"])
        token = _tenant_context.set(ctx)
        try:
            assert is_current_user_admin() is False
        finally:
            _tenant_context.reset(token)

    def test_is_not_admin_without_context(self):
        """Should return False when no tenant context."""
        from shared.middleware.tenant_context import is_current_user_admin

        assert is_current_user_admin() is False
