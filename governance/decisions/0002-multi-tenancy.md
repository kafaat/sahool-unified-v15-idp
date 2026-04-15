# ADR-0002: Multi-Tenancy Strategy

- **Status**: Accepted
- **Date**: 2026-04-02
- **Deciders**: Platform Architecture Team

## Context

> السياق | Context

SAHOOL is a multi-tenant agricultural platform serving multiple farm operators (tenants) from a shared infrastructure. The platform must ensure strict data isolation while maintaining cost efficiency and operational simplicity.

Key requirements:
1. **Data isolation** — No tenant can access another tenant's data
2. **Performance** — Tenant queries must not degrade as tenant count grows
3. **Cost efficiency** — Shared infrastructure, not per-tenant databases
4. **Compliance** — Audit trail for cross-tenant access
5. **Flexibility** — Super-admin access for platform operations

Options considered:
- **A) Database-per-tenant** — Full isolation but high operational cost
- **B) Schema-per-tenant** — Good isolation, moderate operational cost
- **C) Row-Level Security (RLS)** — Shared tables, PostgreSQL-enforced isolation
- **D) Application-layer only** — No DB enforcement, relies on code correctness

## Decision

> القرار | Decision

We adopt **Option C: PostgreSQL Row-Level Security (RLS)** as the primary tenant isolation mechanism, supplemented by application-layer middleware:

### Database Layer

1. **Every tenant-scoped table** has a `tenant_id UUID NOT NULL` column
2. **RLS policies** enforce `tenant_id = current_setting('app.current_tenant')` on SELECT, INSERT, UPDATE, DELETE
3. **`FORCE ROW LEVEL SECURITY`** is applied to prevent superuser bypass
4. **`current_tenant_id()`** SQL function reads the session variable `app.current_tenant`
5. **`is_super_admin()`** SQL function reads `app.is_super_admin` for administrative override

### Application Layer

1. **`shared.db.tenant_connection`** — Sets PostgreSQL session variables (`app.current_tenant`, `app.is_super_admin`) via injection-safe `set_config()`
2. **`shared.middleware.tenant_context`** — Extracts tenant from JWT `tid` claim, sets `ContextVar` for async safety
3. **`shared.middleware.tenant_audit`** — Logs all cross-tenant admin access
4. **Kong API Gateway** — Strips `X-Tenant-ID` header from external requests to prevent spoofing; re-derives from JWT

### JWT Claims

- `tid` — Canonical tenant claim (preferred)
- `tenant_id` — Fallback for backward compatibility
- Backend and frontend apps prefer `tid` first

### Migration Path

- Migration `010_row_level_security.sql` — Enables RLS on 14 core tables
- Migration `011_tenant_gaps_closure.sql` — Adds FORCE RLS, creates audit tables, covers billing tables
- Phase 1 schema isolation migration — 644 lines for advanced schema-level partitioning

## Consequences

> النتائج | Consequences

### Positive

- **Database-enforced isolation** — Even application bugs cannot leak cross-tenant data
- **Shared infrastructure** — Cost-efficient with single database cluster
- **Transparent to queries** — ORM queries work normally; RLS is invisible to application code
- **Audit trail** — Cross-tenant admin access is logged with full context
- **Compliance** — Meets GDPR and ISO 27001 requirements for data segregation

### Negative

- **Performance overhead** — RLS adds ~2-5% query overhead for policy evaluation
- **Migration complexity** — Retrofitting RLS on existing tables requires careful migration
- **Testing complexity** — Tests must set session variables or use service-level fixtures
- **Adoption gap** — Not all 72 services currently call `setup_tenant_rls()`; enforcement is ongoing

### Mitigations

- **Performance**: Index on `tenant_id` column on all tables; composite indexes for common queries
- **Adoption**: CI guard to be added that validates `setup_tenant_rls()` in service lifespans
- **Testing**: Shared test fixtures in `tests/utils/` that configure tenant context

## Enforcement

- [Tenant Isolation Policy](../policies/tenant-isolation.md) — Defines mandatory requirements
- Database migrations enforce RLS at the schema level
- `governance-validation.yml` CI workflow validates compliance

## Related

- [ADR-0001: Backend Services Root](./0001-backend-root.md)
- [Tenant Connection](../../shared/db/tenant_connection.py)
- [Tenant Context Middleware](../../shared/middleware/tenant_context.py)
- [RLS Migration](../../infrastructure/core/postgres/migrations/010_row_level_security.sql)
