# Tenant Isolation & Row-Level Security (RLS)

**Date**: 2026-03-24
**Status**: Incrementally rolling out
**Related PR**: #1316

---

## Overview

SAHOOL enforces tenant isolation at two layers:

1. **Application Layer**: `WHERE tenant_id = $1` in all SQL queries
2. **Database Layer**: PostgreSQL Row-Level Security (RLS) policies

RLS provides defense-in-depth: even if application-layer filtering is bypassed,
PostgreSQL will prevent cross-tenant data access.

---

## Architecture

```
Request → Auth Middleware → TenantContextMiddleware
                                    ↓
                          tenant_connection(pool)
                                    ↓
                          SET app.current_tenant = '<uuid>'
                          SET app.is_super_admin = 'true'|'false'
                                    ↓
                          PostgreSQL RLS Policies
                          ├── tenant_isolation_*: tenant_id = current_setting('app.current_tenant')
                          └── superadmin_bypass_*: app.is_super_admin = 'true'
```

## Session Variables

Set by `shared/db/tenant_connection.py`:

| Variable | Value | Purpose |
|----------|-------|---------|
| `app.current_tenant` | UUID string | Current tenant ID for RLS filtering |
| `app.is_super_admin` | `'true'` / `'false'` | Bypass RLS for admin operations |

**Important**: On connection release, variables are reset to `''` and `'false'`.
RLS policies on UUID columns must use `nullif(..., '')::uuid` to handle the empty
string reset safely.

## RLS-Protected Tables

### Digital Twin Module (`shared/digital_twin/migrations/002_rls_policies.sql`)

| Table | Tenant Column Type | Policy |
|-------|-------------------|--------|
| `field_daily_state` | UUID | `nullif(current_setting('app.current_tenant', true), '')::uuid` |
| `field_observation` | UUID | `nullif(current_setting('app.current_tenant', true), '')::uuid` |
| `irrigation_recommendation` | UUID | `nullif(current_setting('app.current_tenant', true), '')::uuid` |

### Calibration Module (`shared/calibration/migrations/s16_011_rls_policies.sql`)

| Table | Tenant Column Type | Policy |
|-------|-------------------|--------|
| `calibration_run` | VARCHAR | `current_setting('app.current_tenant', true)` |
| `parameter_set` | VARCHAR | `current_setting('app.current_tenant', true)` |
| `parameter_change_log` | VARCHAR | `current_setting('app.current_tenant', true)` |

## Usage

### Enabling RLS in a Service

```python
from shared.db.tenant_connection import tenant_connection, setup_tenant_rls

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    app.state.db_pool = db_pool

    # Enable RLS
    setup_tenant_rls(app, db_pool)
    await verify_tenant_isolation(app)

    yield
    await db_pool.close()
```

### Using Tenant-Scoped Connections

```python
async with tenant_connection(pool, tenant_id=tenant_id) as conn:
    # RLS automatically filters rows by tenant
    rows = await conn.fetch("SELECT * FROM fields")
```

### Admin Bypass

```python
async with tenant_connection(pool, tenant_id=tenant_id, is_admin=True) as conn:
    # Sees all rows across tenants
    rows = await conn.fetch("SELECT * FROM fields")
```

## Writing New RLS Migrations

When adding RLS to a new table:

1. **UUID tenant_id columns** — use `nullif()` to handle empty string resets:
   ```sql
   CREATE POLICY tenant_isolation ON my_table
       USING (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid)
       WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid);
   ```

2. **VARCHAR tenant_id columns** — direct comparison:
   ```sql
   CREATE POLICY tenant_isolation ON my_table
       USING (tenant_id = current_setting('app.current_tenant', true))
       WITH CHECK (tenant_id = current_setting('app.current_tenant', true));
   ```

3. **Super-admin bypass** — always add:
   ```sql
   CREATE POLICY superadmin_bypass ON my_table
       USING (current_setting('app.is_super_admin', true) = 'true');
   ```

## Rollout Status

> **WARNING**: Most services still use raw asyncpg pools WITHOUT setting RLS
> session variables. Until all 72 services adopt `tenant_connection()` or call
> `setup_tenant_rls()`, cross-tenant data leaks are possible at the DB layer.

### Services with Application-Layer Tenant Isolation (PR #1316)

| Service | Methods Fixed |
|---------|--------------|
| lowcode-engine | UPDATE/DELETE/SELECT queries |
| ground-vision-service | UPDATE/DELETE/SELECT queries |
| copilot-api | Session UUID seed + queries |
| traceability-service | UPDATE/DELETE/SELECT queries |
| cooperative-service | UPDATE/DELETE/SELECT queries |
| billing-core | 5 repository methods |
| provider-config | get_config_version + rollback |
| inventory-service | Tenant scoping |
| globalgap-compliance | get_by_id methods |

---

_Last Updated: 2026-03-24_
