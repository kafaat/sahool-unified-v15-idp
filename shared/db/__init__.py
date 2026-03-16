"""
SAHOOL Database Utilities
=========================

Provides tenant-aware database connections with Row-Level Security (RLS).

Usage:
    from shared.db import tenant_connection, tenant_transaction, TenantPool

    # Context manager (auto-detects tenant from middleware):
    async with tenant_connection(pool) as conn:
        rows = await conn.fetch("SELECT * FROM fields")

    # Pool wrapper:
    tenant_pool = TenantPool(asyncpg_pool)
    async with tenant_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM fields")
"""

from shared.db.tenant_connection import (
    TenantPool,
    tenant_connection,
    tenant_transaction,
)

__all__ = [
    "TenantPool",
    "tenant_connection",
    "tenant_transaction",
]
