"""
SAHOOL Tenant-Aware Database Connection
========================================
اتصال قاعدة البيانات مع عزل المستأجرين

Provides a context manager that automatically sets PostgreSQL session
variables (app.current_tenant, app.is_super_admin) before executing
queries, activating Row-Level Security (RLS) at the database level.

This creates defense-in-depth: even if application-layer filtering
is bypassed, PostgreSQL RLS policies will prevent cross-tenant data access.

Usage:
    from shared.db.tenant_connection import tenant_connection, create_tenant_pool

    # Option 1: Explicit tenant_id
    async with tenant_connection(pool, tenant_id="org-123") as conn:
        rows = await conn.fetch("SELECT * FROM fields")  # RLS filters automatically

    # Option 2: Auto-detect from middleware context
    async with tenant_connection(pool) as conn:
        rows = await conn.fetch("SELECT * FROM fields")

    # Option 3: Admin access (bypasses RLS)
    async with tenant_connection(pool, tenant_id="org-123", is_admin=True) as conn:
        rows = await conn.fetch("SELECT * FROM fields")  # Sees all rows
"""

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    import asyncpg

logger = logging.getLogger(__name__)


@asynccontextmanager
async def tenant_connection(
    pool: asyncpg.Pool,
    tenant_id: str | None = None,
    is_admin: bool = False,
) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Acquire a database connection with tenant RLS session variables set.

    Sets PostgreSQL session variables that RLS policies read:
      - app.current_tenant = '<tenant_id>'
      - app.is_super_admin = 'true'|'false'

    Args:
        pool: asyncpg connection pool
        tenant_id: Explicit tenant ID. If None, reads from TenantContextMiddleware.
        is_admin: If True, sets app.is_super_admin = 'true' to bypass RLS.

    Yields:
        asyncpg.Connection with RLS session variables configured.

    Raises:
        RuntimeError: If tenant_id is not provided and not available from context.

    Example:
        async with tenant_connection(pool) as conn:
            # RLS enforces: only rows where tenant_id = current_tenant_id()
            fields = await conn.fetch("SELECT * FROM fields")
    """
    # Auto-detect tenant from middleware context if not provided
    if tenant_id is None:
        try:
            from shared.middleware.tenant_context import get_current_tenant

            ctx = get_current_tenant()
            tenant_id = ctx.id
            if ctx.roles and ("admin" in ctx.roles or "super_admin" in ctx.roles):
                is_admin = True
        except (RuntimeError, ImportError):
            raise RuntimeError(
                "tenant_id is required: either pass it explicitly or "
                "ensure TenantContextMiddleware is active."
            )

    if not tenant_id:
        raise RuntimeError("tenant_id cannot be empty")

    # Validate tenant_id format to prevent injection into session variables.
    # Allows UUIDs, alphanumeric with hyphens/underscores, max 128 chars.
    if not re.fullmatch(r"[a-zA-Z0-9_\-]{1,128}", tenant_id):
        raise RuntimeError(
            f"tenant_id contains invalid characters or exceeds length limit: "
            f"{tenant_id!r:.40}"
        )

    conn: asyncpg.Connection = await pool.acquire()
    try:
        # Set RLS session variables using parameterized SET
        # Use set_config() which is SQL-injection safe (takes text parameters)
        await conn.execute(
            "SELECT set_config('app.current_tenant', $1, true)",
            tenant_id,
        )
        await conn.execute(
            "SELECT set_config('app.is_super_admin', $1, true)",
            "true" if is_admin else "false",
        )

        logger.debug(
            "RLS session configured: tenant=%s, admin=%s",
            tenant_id,
            is_admin,
        )

        yield conn
    finally:
        # Reset session variables before returning connection to pool
        try:
            await conn.execute(
                "SELECT set_config('app.current_tenant', '', true)"
            )
            await conn.execute(
                "SELECT set_config('app.is_super_admin', 'false', true)"
            )
        except Exception as cleanup_err:
            logger.warning(
                "Failed to reset RLS session variables: %s", cleanup_err
            )
        await pool.release(conn)


@asynccontextmanager
async def tenant_transaction(
    pool: asyncpg.Pool,
    tenant_id: str | None = None,
    is_admin: bool = False,
) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Same as tenant_connection but wraps in a database transaction.

    Usage:
        async with tenant_transaction(pool) as conn:
            await conn.execute("INSERT INTO fields ...")
            await conn.execute("UPDATE crop_seasons ...")
            # Auto-commits on success, auto-rollbacks on exception
    """
    async with tenant_connection(pool, tenant_id=tenant_id, is_admin=is_admin) as conn:
        async with conn.transaction():
            yield conn


class TenantPool:
    """
    Wrapper around asyncpg.Pool that provides tenant-aware connections.

    Usage:
        pool = TenantPool(asyncpg_pool)

        # In request handler (auto-detects tenant from middleware):
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM fields")

        # Explicit tenant:
        async with pool.acquire(tenant_id="org-123") as conn:
            rows = await conn.fetch("SELECT * FROM fields")
    """

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    @asynccontextmanager
    async def acquire(
        self,
        tenant_id: str | None = None,
        is_admin: bool = False,
    ) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire a tenant-scoped connection."""
        async with tenant_connection(self._pool, tenant_id=tenant_id, is_admin=is_admin) as conn:
            yield conn

    @asynccontextmanager
    async def transaction(
        self,
        tenant_id: str | None = None,
        is_admin: bool = False,
    ) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire a tenant-scoped connection with transaction."""
        async with tenant_transaction(self._pool, tenant_id=tenant_id, is_admin=is_admin) as conn:
            yield conn

    @property
    def raw_pool(self) -> asyncpg.Pool:
        """Access the raw asyncpg pool (for health checks, migrations, etc.)."""
        return self._pool

    async def close(self):
        """Close the underlying pool."""
        await self._pool.close()
