"""
Tests for shared/middleware/tenant_context — RLS session helpers.

set_app_tenant() and acquire_tenant_conn() are mocked so no real DB is needed.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock, MagicMock, call

import pytest

# ---------------------------------------------------------------------------
# Tests for set_app_tenant()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_set_app_tenant_calls_set_config():
    """set_app_tenant must call SET LOCAL via set_config with the tenant_id."""
    from shared.middleware.tenant_context import set_app_tenant

    conn = AsyncMock()
    await set_app_tenant(conn, "tenant-abc")

    conn.execute.assert_awaited_once()
    sql, tenant_arg = conn.execute.call_args[0]
    assert "set_config" in sql
    assert "app.current_tenant" in sql
    assert tenant_arg == "tenant-abc"


@pytest.mark.asyncio
async def test_set_app_tenant_empty_tenant_id_is_noop():
    """set_app_tenant with an empty tenant_id must not call execute."""
    from shared.middleware.tenant_context import set_app_tenant

    conn = AsyncMock()
    await set_app_tenant(conn, "")
    conn.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_set_app_tenant_none_tenant_id_is_noop():
    """set_app_tenant with None is also a no-op (empty string check)."""
    from shared.middleware.tenant_context import set_app_tenant

    conn = AsyncMock()
    await set_app_tenant(conn, None)  # type: ignore[arg-type]
    conn.execute.assert_not_awaited()


# ---------------------------------------------------------------------------
# Tests for acquire_tenant_conn()
# ---------------------------------------------------------------------------


def _make_pool_with_conn(execute_side_effect=None):
    """
    Build a mock asyncpg pool whose acquire() yields a mock connection.
    The mock connection also supports async-context-manager transaction().
    """
    conn = AsyncMock()
    if execute_side_effect:
        conn.execute.side_effect = execute_side_effect

    # asyncpg's transaction() is a SYNC call that returns an object with
    # async __aenter__ / __aexit__.  Use a plain MagicMock so the call
    # returns synchronously, and attach async enter/exit to its return value.
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=None)
    tx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=tx)

    pool = MagicMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

    return pool, conn


@pytest.mark.asyncio
async def test_acquire_tenant_conn_sets_tenant_and_yields_conn():
    """acquire_tenant_conn must set the tenant and yield the connection."""
    from shared.middleware.tenant_context import acquire_tenant_conn

    pool, conn = _make_pool_with_conn()

    async with acquire_tenant_conn(pool, "tenant-xyz") as c:
        assert c is conn
        # The SET LOCAL call must have happened before yield
        conn.execute.assert_awaited()
        sql, tid = conn.execute.call_args[0]
        assert "app.current_tenant" in sql
        assert tid == "tenant-xyz"


@pytest.mark.asyncio
async def test_acquire_tenant_conn_transaction_scoped():
    """The connection's transaction() must be entered (SET LOCAL is tx-scoped)."""
    from shared.middleware.tenant_context import acquire_tenant_conn

    pool, conn = _make_pool_with_conn()

    async with acquire_tenant_conn(pool, "t1"):
        conn.transaction.assert_called_once()


@pytest.mark.asyncio
async def test_acquire_tenant_conn_propagates_query_errors():
    """Errors raised inside the `async with` block must propagate normally."""
    from shared.middleware.tenant_context import acquire_tenant_conn

    pool, conn = _make_pool_with_conn()

    with pytest.raises(RuntimeError, match="boom"):
        async with acquire_tenant_conn(pool, "t2"):
            raise RuntimeError("boom")
