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
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    import asyncpg
    from fastapi import FastAPI

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# WARNING: Row-Level Security (RLS) gap
# ──────────────────────────────────────────────────────────────────────────────
# This module provides tenant_connection() for RLS-enforced DB access, but
# most services still use raw asyncpg pools WITHOUT setting RLS session
# variables.  Until all 72 services adopt tenant_connection() or call
# setup_tenant_rls(), cross-tenant data leaks are possible at the DB layer.
#
# To close the gap incrementally, call setup_tenant_rls(app, db_pool) in your
# service's lifespan function.  See docstring below for details.
# ──────────────────────────────────────────────────────────────────────────────
logger.warning(
    "shared.db.tenant_connection loaded but RLS is NOT enforced by default. "
    "Services must explicitly call setup_tenant_rls(app, db_pool) in their "
    "lifespan to enable Row-Level Security.  Without this, cross-tenant data "
    "access is only prevented by application-layer filtering."
)


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
                "tenant_id is required: either pass it explicitly or ensure TenantContextMiddleware is active."
            )

    if not tenant_id:
        raise RuntimeError("tenant_id cannot be empty")

    conn: asyncpg.Connection = await pool.acquire(timeout=10.0)
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
            await conn.execute("SELECT set_config('app.current_tenant', '', true)")
            await conn.execute("SELECT set_config('app.is_super_admin', 'false', true)")
        except Exception as exc:
            logger.warning("Failed to reset RLS session variables: %s", exc)
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


# ──────────────────────────────────────────────────────────────────────────────
# Adoption helpers - make it easy for services to enable RLS
# ──────────────────────────────────────────────────────────────────────────────


async def verify_tenant_isolation(app: FastAPI) -> bool:
    """
    Verify that RLS policies are active on critical tables.

    Call this in your service's lifespan (after DB pool is created) to confirm
    that PostgreSQL RLS policies exist and are enabled.  Logs warnings for any
    tables missing RLS.

    Args:
        app: FastAPI application instance (expects app.state.db_pool).

    Returns:
        True if all critical tables have RLS enabled, False otherwise.

    Example:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
            await verify_tenant_isolation(app)
            yield
    """
    pool: asyncpg.Pool | None = getattr(app.state, "db_pool", None)
    if pool is None:
        logger.warning("verify_tenant_isolation: no db_pool on app.state, skipping RLS check")
        return False

    critical_tables = ["fields", "tasks", "farms", "ndvi_readings", "sync_status"]
    all_ok = True

    try:
        conn = await pool.acquire(timeout=10.0)
        try:
            for table in critical_tables:
                row = await conn.fetchrow(
                    "SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname = $1",
                    table,
                )
                if row is None:
                    # Table may not exist in this service's DB
                    continue
                if not row["relrowsecurity"]:
                    logger.warning(
                        "RLS is NOT enabled on table '%s'. Run: ALTER TABLE %s ENABLE ROW LEVEL SECURITY;",
                        table,
                        table,
                    )
                    all_ok = False
                elif not row["relforcerowsecurity"]:
                    logger.warning(
                        "RLS on table '%s' does not apply to table owner. Run: "
                        "ALTER TABLE %s FORCE ROW LEVEL SECURITY;",
                        table,
                        table,
                    )
                    all_ok = False
                else:
                    logger.info("RLS verified for table '%s'", table)
        finally:
            await pool.release(conn)
    except Exception as exc:
        logger.error("verify_tenant_isolation failed: %s", exc)
        return False

    if all_ok:
        logger.info("All critical tables have RLS enabled and enforced.")
    return all_ok


def setup_tenant_rls(app: FastAPI, db_pool: asyncpg.Pool) -> None:
    """
    Register a TenantPool on the app and wrap the raw pool for RLS enforcement.

    Call this in your service's lifespan to enable tenant-scoped DB access.
    After calling this, use ``app.state.tenant_pool`` instead of the raw pool
    for all tenant-scoped queries.

    Args:
        app: FastAPI application instance.
        db_pool: asyncpg connection pool (already created).

    Usage:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
            app.state.db_pool = db_pool

            # Enable RLS - creates app.state.tenant_pool
            setup_tenant_rls(app, db_pool)

            # Optionally verify RLS policies exist in the DB
            await verify_tenant_isolation(app)

            yield
            await db_pool.close()

        # In route handlers, use the tenant pool:
        async def get_fields(request: Request):
            tenant_id = request.state.tenant_id  # from auth middleware
            async with request.app.state.tenant_pool.acquire(tenant_id=tenant_id) as conn:
                return await conn.fetch("SELECT * FROM fields")
    """
    tenant_pool = TenantPool(db_pool)
    app.state.tenant_pool = tenant_pool
    logger.info(
        "Tenant RLS pool registered on app.state.tenant_pool. "
        "Use tenant_pool.acquire(tenant_id=...) for RLS-enforced queries."
    )
