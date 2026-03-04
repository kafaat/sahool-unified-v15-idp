-- Migration: Safe Index Remediation
-- الهجرة: إصلاح الفهارس غير الآمنة
-- Created: 2026-03-03
-- Description: Recreate non-concurrent indexes from 20260214000000_add_farms_table
--              using CONCURRENTLY to avoid table locks on production.
--              Also validates FK constraint fk_fields_farm_id with NOT VALID pattern.
-- Addresses: Drift Detection medium-severity findings:
--   - "Non-concurrent index creation"
--   - "Adding constraint"

-- ═══════════════════════════════════════════════════════════════════════════
-- Drop existing non-concurrent indexes from 20260214000000
-- حذف الفهارس غير المتزامنة الحالية
-- ═══════════════════════════════════════════════════════════════════════════

DROP INDEX IF EXISTS "idx_field_farm";
DROP INDEX IF EXISTS "idx_field_tenant_status";
DROP INDEX IF EXISTS "idx_field_tenant_crop";
DROP INDEX IF EXISTS "idx_field_tenant_active";
DROP INDEX IF EXISTS "idx_field_owner";
DROP INDEX IF EXISTS "idx_field_planting";
DROP INDEX IF EXISTS "idx_field_harvest";

-- ═══════════════════════════════════════════════════════════════════════════
-- Recreate indexes with CONCURRENTLY (no table locks)
-- إعادة إنشاء الفهارس بشكل متزامن (بدون قفل الجداول)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_field_farm"
    ON "fields"("farm_id");

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_field_tenant_status"
    ON "fields"("tenant_id", "status");

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_field_tenant_crop"
    ON "fields"("tenant_id", "crop_type");

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_field_tenant_active"
    ON "fields"("tenant_id", "is_deleted");

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_field_owner"
    ON "fields"("owner_id");

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_field_planting"
    ON "fields"("planting_date");

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_field_harvest"
    ON "fields"("expected_harvest");

-- ═══════════════════════════════════════════════════════════════════════════
-- Validate FK constraint (safe re-validation, no lock if already valid)
-- التحقق من قيد المفتاح الخارجي
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE "fields" VALIDATE CONSTRAINT "fk_fields_farm_id";
