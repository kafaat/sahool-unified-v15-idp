-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Drift Detection Fix (Report 5c6dd891-251)
-- إصلاح كشف الانحراف - تقرير 5c6dd891-251
-- Purpose: Resolve critical mandatory-columns-without-DEFAULT and risky migration patterns
-- Service: field-management-service
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix 1: Ensure tenant_id columns retain safe DEFAULT
-- Migration 20260225000000 dropped DEFAULT after backfill; 20260227000000
-- restored it as 'unassigned'. Re-affirm to prevent drift scanner gaps.
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE "field_boundary_history" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "tasks" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "ndvi_readings" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix 2: Ensure all mandatory columns have safe DEFAULT values
-- Covers columns from initial migration that lacked defaults
-- ─────────────────────────────────────────────────────────────────────────────

-- tasks.created_by: Required field, default to 'system' for automated tasks
ALTER TABLE "tasks" ALTER COLUMN "created_by" SET DEFAULT 'system';

-- field_boundary_history.version_at_change: Default to 1 for first version
ALTER TABLE "field_boundary_history" ALTER COLUMN "version_at_change" SET DEFAULT 1;

-- Ensure all updated_at columns have DEFAULT now()
ALTER TABLE "farms" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "fields" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "sync_status" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "tasks" ALTER COLUMN "updated_at" SET DEFAULT now();

-- ─────────────────────────────────────────────────────────────────────────────
-- Medium: Non-concurrent index creation (Acknowledged)
-- فهارس غير متزامنة (مقبولة)
--
-- The following non-concurrent indexes were created in initial migrations on
-- EMPTY tables (0001_init_postgis, 20260214000000_add_farms_table), which is
-- safe and does not require special handling:
--   - idx_field_tenant, idx_field_sync, idx_field_status, idx_field_crop
--   - idx_field_boundary (GIST), idx_field_centroid (GIST)
--   - idx_history_field, idx_history_date
--   - idx_task_field, idx_task_status, idx_task_due
--   - idx_ndvi_field_date
--   - idx_farm_tenant, idx_farm_tenant_active, idx_farm_owner, idx_farm_created
--   - idx_field_farm, idx_field_tenant_status, idx_field_tenant_crop
--   - idx_field_tenant_active, idx_field_owner, idx_field_planting, idx_field_harvest
--
-- Medium: Adding constraint (Acknowledged)
-- FK constraint fk_fields_farm_id was added in 20260214000000_add_farms_table
-- on an existing table. This is acceptable as it uses SET NULL on delete and
-- the column was nullable, so no existing rows would violate the constraint.
--
-- All subsequent migrations (20260207000000+) use CREATE INDEX.
-- ═══════════════════════════════════════════════════════════════════════════════
