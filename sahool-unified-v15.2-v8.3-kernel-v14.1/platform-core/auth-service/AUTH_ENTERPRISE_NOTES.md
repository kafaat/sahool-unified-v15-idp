# Auth Service Enterprise Notes

What changed:
- True SaaS multi-tenancy: require `X-Tenant-Id` (UUID)
- DB schema upgraded: tenants table + FK, unique (tenant_id,email), composite indexes
- Added RBAC tables, sessions, API keys, audit logs, password history, oauth providers
- Login is now tenant-aware and enforces tenant match.

Minimum env:
- DATABASE_URL=postgresql://...
- REQUIRE_TENANT_HEADER=true

Important:
- This is a greenfield-friendly upgrade. If you have an old `users` table (tenant_id TEXT + email UNIQUE),
  migrate data before enabling the new schema in production.
