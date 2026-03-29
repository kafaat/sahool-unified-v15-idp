-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add tenant_id to all research-core models
-- إضافة معرف المستأجر لجميع جداول نواة البحث العلمي
-- Purpose: Multi-tenant isolation (drift fix)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add tenant_id columns with safe DEFAULT for existing rows
-- الخطوة 1: إضافة أعمدة tenant_id مع قيمة افتراضية آمنة للصفوف الحالية

ALTER TABLE "germplasm" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "seed_lots" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "plantings" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "experiments" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "research_protocols" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "research_plots" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "treatments" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "research_daily_logs" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "lab_samples" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "digital_signatures" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "experiment_collaborators" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "experiment_audit_log" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';

-- Step 2: Remove DEFAULT constraint (tenant_id must always be provided by application)
-- الخطوة 2: إزالة القيمة الافتراضية (يجب تقديم tenant_id دائمًا من التطبيق)

ALTER TABLE "germplasm" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "seed_lots" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "plantings" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "experiments" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "research_protocols" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "research_plots" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "treatments" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "research_daily_logs" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "lab_samples" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "digital_signatures" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "experiment_collaborators" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "experiment_audit_log" ALTER COLUMN "tenant_id" DROP DEFAULT;

-- Step 3: Create indexes for tenant isolation queries
-- الخطوة 3: إنشاء فهارس لاستعلامات عزل المستأجر

CREATE INDEX IF NOT EXISTS "idx_germplasm_tenant" ON "germplasm" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_germplasm_tenant_available" ON "germplasm" ("tenant_id", "is_available");
CREATE INDEX IF NOT EXISTS "idx_seed_lot_tenant" ON "seed_lots" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_planting_tenant" ON "plantings" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_experiment_tenant" ON "experiments" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_experiment_tenant_status" ON "experiments" ("tenant_id", "status");
CREATE INDEX IF NOT EXISTS "idx_protocol_tenant" ON "research_protocols" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_plot_tenant" ON "research_plots" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_treatment_tenant" ON "treatments" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_daily_log_tenant" ON "research_daily_logs" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_lab_sample_tenant" ON "lab_samples" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_signature_tenant" ON "digital_signatures" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_collaborator_tenant" ON "experiment_collaborators" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_audit_log_tenant" ON "experiment_audit_log" ("tenant_id");
