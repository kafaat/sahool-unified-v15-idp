-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add tenant_id to Role model for multi-tenant isolation
-- إضافة معرف المستأجر لنموذج الأدوار لعزل المستأجرين
-- Purpose: Fix tenant isolation drift - Role was globally shared
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add tenant_id with safe DEFAULT for existing rows
ALTER TABLE "user_roles" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'default';

-- Step 2: Backfill tenant_id from users who have the role assigned
-- (existing roles get 'default' tenant, which is acceptable for system roles)

-- Step 3: Drop the global unique constraint on name
DROP INDEX IF EXISTS "user_roles_name_key";

-- Step 4: Remove DEFAULT constraint
ALTER TABLE "user_roles" ALTER COLUMN "tenant_id" DROP DEFAULT;

-- Step 5: Create tenant-scoped unique constraint (name unique per tenant)
CREATE UNIQUE INDEX IF NOT EXISTS "idx_role_tenant_name" ON "user_roles" ("tenant_id", "name");

-- Step 6: Create tenant isolation index
CREATE INDEX IF NOT EXISTS "idx_role_tenant" ON "user_roles" ("tenant_id");
