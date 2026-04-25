-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Schema-only hardening. partner-auth call sites are already safe
-- (all lookups are by cryptographically unguessable keys: codeHash,
-- tokenHash, jti). Adding the composite unique exposes tenant-bound
-- accessors for future code paths and satisfies the platform-wide IDOR
-- policy. Note: access_tokens uses jti as primary key, so its composite
-- is (jti, tenant_id).
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique primary key — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_auth_code_id_tenant" ON "auth_codes" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_access_token_jti_tenant" ON "access_tokens" ("jti", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_refresh_token_id_tenant" ON "refresh_tokens" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_consent_grant_id_tenant" ON "consent_grants" ("id", "tenant_id");
