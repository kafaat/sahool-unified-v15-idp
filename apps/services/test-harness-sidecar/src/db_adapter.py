"""Adapter shim around ``shared.db.tenant_connection``.

The sidecar's introspection endpoints want a simple two-method API:

    async with admin_connection() as conn: ...
    async with tenant_connection(tenant_id) as conn: ...

The shared module's actual signature takes the pool as its first
argument and a kwarg flag for admin-mode:

    @asynccontextmanager
    async def tenant_connection(pool, tenant_id=None, is_admin=False): ...

This file holds the singleton pool and exposes the simpler signatures.
By delegating to the SAME ``shared.db.tenant_connection`` function that
production services use, any RLS-context bug in production is also
visible to the introspection probe — which is the whole point.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

import asyncpg

from shared.db.tenant_connection import tenant_connection as _shared_tenant_connection


_pool: asyncpg.Pool | None = None


async def init_pool(dsn: str) -> None:
    """Create the asyncpg pool. Called once from FastAPI lifespan."""
    global _pool
    if _pool is not None:
        return
    _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=4)


async def close_pool() -> None:
    """Close the pool on shutdown."""
    global _pool
    if _pool is None:
        return
    await _pool.close()
    _pool = None


async def check_connection() -> bool:
    """Used by /readyz — returns True if a SELECT 1 succeeds."""
    if _pool is None:
        return False
    try:
        async with _pool.acquire() as conn:
            return await conn.fetchval("SELECT 1") == 1
    except Exception:
        return False


def _require_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized — call init_pool() first")
    return _pool


@asynccontextmanager
async def admin_connection() -> AsyncIterator[asyncpg.Connection]:
    """Yields an admin (RLS-bypassing) connection.

    Used for meta queries (pg_indexes, pg_policies) that need to see
    the platform from outside any tenant scope.
    """
    async with _shared_tenant_connection(_require_pool(), is_admin=True) as conn:
        yield conn


@asynccontextmanager
async def tenant_connection(tenant_id: str) -> AsyncIterator[asyncpg.Connection]:
    """Yields a connection with ``app.current_tenant`` SET to ``tenant_id``.

    Delegates to ``shared.db.tenant_connection`` — the SAME function
    production services use. If RLS context handling in production has
    a bug, the probe inherits it (and reports truthfully).
    """
    async with _shared_tenant_connection(_require_pool(), tenant_id=tenant_id) as conn:
        yield conn
