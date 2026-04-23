-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Expose the Prisma `id_tenantId` accessor so the admin-facing
-- UsersService.{findOne,update,remove,hardDelete} can bind tenantId atomically
-- with id. Combined with the controller-layer SUPER_ADMIN bypass this closes
-- the cross-tenant admin-read/admin-write IDOR where a tenant-scoped ADMIN
-- role was effectively granted platform-wide access.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_user_id_tenant" ON "users" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_user_profile_id_tenant" ON "user_profiles" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_role_id_tenant" ON "user_roles" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_user_session_id_tenant" ON "user_sessions" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_refresh_token_id_tenant" ON "refresh_tokens" ("id", "tenant_id");
