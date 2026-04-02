# Tenant Isolation Policy

> سياسة عزل المستأجرين | Tenant Isolation Policy

**Version**: 1.0.0
**Status**: Approved
**Last Updated**: 2026-04-02

## Purpose | الهدف

This policy defines the mandatory requirements for tenant data isolation across all SAHOOL platform services to prevent cross-tenant data leakage and ensure regulatory compliance.

تحدد هذه السياسة المتطلبات الإلزامية لعزل بيانات المستأجرين عبر جميع خدمات منصة سهول لمنع تسريب البيانات بين المستأجرين وضمان الامتثال التنظيمي.

---

## Scope | النطاق

This policy applies to **all 72 microservices** in `apps/services/` and all shared modules in `shared/`.

---

## Requirements | المتطلبات

### 1. Database-Level Isolation (Mandatory)

| Requirement | Description | Status |
|-------------|-------------|--------|
| **RLS Enabled** | PostgreSQL Row-Level Security MUST be enabled on ALL tables containing tenant data | Enforced on 14+ tables |
| **FORCE RLS** | `ALTER TABLE ... FORCE ROW LEVEL SECURITY` MUST be applied to prevent superuser bypass | Enforced |
| **Tenant Column** | Every tenant-scoped table MUST have a `tenant_id UUID NOT NULL` column | Required |
| **Session Variable** | `current_tenant_id()` SQL function reads from `app.current_tenant` session variable | Implemented |

### 2. Application-Level Isolation (Mandatory)

| Requirement | Description |
|-------------|-------------|
| **`setup_tenant_rls()`** | All services MUST call `setup_tenant_rls()` from `shared.db.tenant_connection` during lifespan startup |
| **TenantContextMiddleware** | All HTTP services MUST include `TenantContextMiddleware` from `shared.middleware.tenant_context` |
| **JWT `tid` Claim** | Tenant ID MUST be derived from JWT `tid` claim (canonical) with `tenant_id` as fallback |
| **No Header Trust** | `X-Tenant-ID` header MUST NOT be trusted from external requests — Kong strips it via `request-transformer` |

### 3. Cross-Tenant Access Control

| Scenario | Policy |
|----------|--------|
| **Normal user access** | Users can ONLY access data within their own tenant |
| **Admin cross-tenant access** | Requires `SUPER_ADMIN` or `TENANT_ADMIN` role with explicit audit logging |
| **Cross-tenant audit** | `TenantAuditMiddleware` MUST log all cross-tenant admin access with: user_id, source tenant, target tenant, path, IP |
| **API responses** | MUST NOT include tenant IDs or data from other tenants in error messages |

### 4. Event Isolation

| Requirement | Description |
|-------------|-------------|
| **Tenant-scoped subjects** | NATS events MUST use tenant-scoped subjects: `sahool.tenant.{tenant_id}.{domain}.{action}` |
| **Event payload** | All events MUST include `tenant_id` in payload for downstream filtering |
| **Consumer filtering** | Event consumers MUST validate `tenant_id` matches their processing context |

### 5. Caching Isolation

| Requirement | Description |
|-------------|-------------|
| **Redis key prefix** | Cache keys MUST include tenant ID: `sahool:{tenant_id}:{resource}:{id}` |
| **No shared cache** | Tenant-specific data MUST NOT be stored in shared (non-prefixed) cache keys |

---

## Enforcement | التنفيذ

### CI/CD Enforcement

1. **`governance-validation.yml`** — Validates service metadata includes tenant isolation markers
2. **Database migrations** — `010_row_level_security.sql` and `011_tenant_gaps_closure.sql` enforce RLS
3. **Code review** — PR reviews MUST verify tenant isolation for new endpoints

### Service Adoption Tracking

Services MUST declare RLS adoption in their service configuration. Non-compliant services will be flagged in governance dashboards.

---

## Violations | المخالفات

| Severity | Violation | Action |
|----------|-----------|--------|
| **Critical** | Missing RLS on tenant-scoped table | Block deployment |
| **High** | Missing `setup_tenant_rls()` in service lifespan | Require remediation within 7 days |
| **Medium** | Missing tenant audit logging | Require remediation within 30 days |
| **Low** | Cache keys without tenant prefix | Track for next sprint |

---

## Related | مراجع ذات صلة

- [ADR-0002: Multi-Tenancy Strategy](../decisions/0002-multi-tenancy.md)
- [Database Migrations](../../infrastructure/core/postgres/migrations/)
- [Tenant Connection Module](../../shared/db/tenant_connection.py)
- [Tenant Context Middleware](../../shared/middleware/tenant_context.py)
- [Security Policies](../../infrastructure/security/security-policies.yaml)
