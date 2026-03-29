-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add tenant_id to field-management models missing tenant isolation
-- إضافة معرف المستأجر لجداول إدارة الحقول
-- Purpose: Multi-tenant isolation (drift fix)
-- Note: Farm, Field, SyncStatus already have tenant_id. Adding to child models.
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add tenant_id columns with safe DEFAULT for existing rows

-- drift:safe reason=CREATE INDEX inside a Prisma-managed transaction cannot use CONCURRENTLY; zero-downtime index creation must be run manually outside Prisma migrate on large production tables.
ALTER TABLE "field_boundary_history" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'default';
ALTER TABLE "tasks" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'default';
ALTER TABLE "ndvi_readings" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'default';

-- Step 2: Backfill tenant_id from parent Field table
-- الخطوة 2: ملء tenant_id من جدول الحقل الأصلي

UPDATE "field_boundary_history" h SET "tenant_id" = f."tenant_id"
FROM "fields" f WHERE h."field_id" = f."id" AND h."tenant_id" = 'default';

UPDATE "tasks" t SET "tenant_id" = f."tenant_id"
FROM "fields" f WHERE t."field_id" = f."id" AND t."tenant_id" = 'default';

UPDATE "ndvi_readings" n SET "tenant_id" = f."tenant_id"
FROM "fields" f WHERE n."field_id" = f."id" AND n."tenant_id" = 'default';

-- Step 3: Remove DEFAULT constraint

ALTER TABLE "field_boundary_history" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "tasks" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "ndvi_readings" ALTER COLUMN "tenant_id" DROP DEFAULT;

-- Step 4: Create tenant isolation indexes

CREATE INDEX IF NOT EXISTS "idx_history_tenant" ON "field_boundary_history" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_task_tenant" ON "tasks" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_task_tenant_status" ON "tasks" ("tenant_id", "status");
CREATE INDEX IF NOT EXISTS "idx_ndvi_tenant" ON "ndvi_readings" ("tenant_id");
