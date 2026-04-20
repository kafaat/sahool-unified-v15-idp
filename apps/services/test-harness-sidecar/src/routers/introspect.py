"""Behavioral introspection — never returns schema details, only invariants.

Two endpoints in PR 1:

  GET /test-introspect/v1/invariants/fields/{field_id}
      → {exists, tenant_isolation_enforced, geometry_valid, has_spatial_index}

  GET /test-introspect/v1/invariants/rls/{tenant_id}
      → {cross_tenant_leakage_detected, row_count_for_tenant, rls_policy_active}

CRITICAL DESIGN: the RLS probe routes through the SAME
``shared.db.tenant_connection`` function production services use
(via ``src/db_adapter.py``). If RLS context handling has a bug in
production, this probe inherits the bug — which is the whole point.

A migration that renames a column does NOT break these tests; only a
behavioral regression does.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.db_adapter import admin_connection, tenant_connection

router = APIRouter()


class FieldInvariants(BaseModel):
    exists: bool
    tenant_isolation_enforced: bool
    geometry_valid: bool
    has_spatial_index: bool
    created_within_last_seconds: float | None = None


class RlsInvariants(BaseModel):
    cross_tenant_leakage_detected: bool
    row_count_for_tenant: int
    rls_policy_active: bool


@router.get("/invariants/fields/{field_id}", response_model=FieldInvariants)
async def field_invariants(field_id: str) -> FieldInvariants:
    # ---------- Meta queries: admin connection (RLS-bypassing) ----------
    async with admin_connection() as conn:
        meta = await conn.fetchrow(
            """
            SELECT
              EXISTS(SELECT 1 FROM fields WHERE id = $1::uuid) AS exists,
              (SELECT ST_IsValid(geometry) FROM fields WHERE id = $1::uuid) AS geometry_valid,
              (SELECT tenant_id FROM fields WHERE id = $1::uuid) AS tenant_id,
              (SELECT EXTRACT(EPOCH FROM (NOW() - created_at))
                 FROM fields WHERE id = $1::uuid) AS age
            """,
            field_id,
        )
        spatial_idx = await conn.fetchval(
            """
            SELECT EXISTS(
              SELECT 1 FROM pg_indexes
              WHERE tablename = 'fields' AND indexdef ILIKE '%using gist%geometry%'
            )
            """
        )

    if not meta or not meta["exists"]:
        return FieldInvariants(
            exists=False,
            tenant_isolation_enforced=True,  # vacuously true
            geometry_valid=False,
            has_spatial_index=bool(spatial_idx),
        )

    # ---------- Isolation probe: tenant connection with WRONG tenant ----------
    # Use the SAME RLS-context module production uses. If RLS is enforced
    # correctly, the WRONG tenant cannot see this field → returns False.
    real_tenant = str(meta["tenant_id"])
    probe_tenant = (
        f"tenant_e2e_probe_{real_tenant[:8]}"
        if real_tenant
        else "tenant_e2e_probe_unknown"
    )
    async with tenant_connection(probe_tenant) as conn:
        leaked = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM fields WHERE id = $1::uuid)", field_id
        )
    isolation_enforced = not leaked

    return FieldInvariants(
        exists=True,
        tenant_isolation_enforced=isolation_enforced,
        geometry_valid=bool(meta["geometry_valid"]),
        has_spatial_index=bool(spatial_idx),
        created_within_last_seconds=float(meta["age"]) if meta["age"] is not None else None,
    )


@router.get("/invariants/rls/{tenant_id}", response_model=RlsInvariants)
async def rls_invariants(tenant_id: str) -> RlsInvariants:
    # In a tenant-scoped session: RLS should filter rows server-side.
    # If the policy is active, an unfiltered COUNT returns the same as a
    # filtered COUNT for THIS tenant, and a COUNT of "tenant_id != current"
    # MUST return 0.
    async with tenant_connection(tenant_id) as conn:
        row_count = await conn.fetchval(
            "SELECT COUNT(*) FROM fields WHERE tenant_id = $1",
            tenant_id,
        )
        leakage_count = await conn.fetchval(
            "SELECT COUNT(*) FROM fields WHERE tenant_id <> $1",
            tenant_id,
        )

    # Policy presence (admin view — RLS bypassed)
    async with admin_connection() as conn:
        policy_active = await conn.fetchval(
            """
            SELECT EXISTS(
              SELECT 1 FROM pg_policies
              WHERE tablename = 'fields' AND cmd IN ('ALL', 'SELECT')
            )
            """
        )

    return RlsInvariants(
        cross_tenant_leakage_detected=(leakage_count or 0) > 0,
        row_count_for_tenant=row_count or 0,
        rls_policy_active=bool(policy_active),
    )
