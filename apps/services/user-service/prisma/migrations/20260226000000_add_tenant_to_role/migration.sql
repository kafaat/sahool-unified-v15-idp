-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add tenant_id to Role model for multi-tenant isolation
-- إضافة معرف المستأجر لجدول الأدوار لعزل المستأجرين
-- Purpose: Prevent cross-tenant role name collisions
-- Note: Replaces global @unique(name) with @@unique([tenantId, name])
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add tenant_id column (nullable first for safe backfill)

ALTER TABLE "user_roles" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';

-- Step 2: Backfill tenant_id from the first user assigned to each role
-- If a role has no users, it keeps 'default' (system roles)

UPDATE "user_roles" r SET "tenant_id" = sub."tenant_id"
FROM (
    SELECT DISTINCT ON (ur."B") ur."B" AS role_id, u."tenant_id"
    FROM "_UserAssignedRoles" ur
    JOIN "users" u ON ur."A" = u."id"
    ORDER BY ur."B", u."created_at" ASC
) sub
WHERE r."id" = sub.role_id AND r."tenant_id" = 'default';

-- Step 3: Remove DEFAULT constraint

ALTER TABLE "user_roles" ALTER COLUMN "tenant_id" DROP DEFAULT;

-- Step 4: Drop the old global unique constraint on name

DROP INDEX IF EXISTS "user_roles_name_key";

-- Step 5: Create tenant-scoped unique constraint and index

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "uq_role_tenant_name" ON "user_roles" ("tenant_id", "name");
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_role_tenant" ON "user_roles" ("tenant_id");
