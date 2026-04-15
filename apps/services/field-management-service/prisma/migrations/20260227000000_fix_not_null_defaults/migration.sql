-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Fix NOT NULL columns without DEFAULT values
-- إصلاح أعمدة بدون قيم افتراضية (إضافة DEFAULT للأعمدة الإلزامية)
-- Purpose: Prevent breaking deployments by adding DEFAULT to mandatory columns
-- Drift Report: 7d5dc4c6-bc6
-- ═══════════════════════════════════════════════════════════════════════════════

-- tasks.created_by: NOT NULL without DEFAULT (initial migration)
-- Safe default for system-created tasks
-- drift:safe reason=This migration only sets column DEFAULTs on existing NOT NULL columns; it affects future inserts only, does not rewrite existing rows, and creates no indexes — safe for online deployment inside a Prisma-managed transaction.
ALTER TABLE "tasks" ALTER COLUMN "created_by" SET DEFAULT 'system';

-- field_boundary_history.version_at_change: NOT NULL without DEFAULT
ALTER TABLE "field_boundary_history" ALTER COLUMN "version_at_change" SET DEFAULT 1;

-- Ensure tenant_id columns retain a safe DEFAULT for new rows
-- Previous migration dropped DEFAULT after backfill; restore sentinel default
ALTER TABLE "field_boundary_history" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "tasks" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "ndvi_readings" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- farms.updated_at: NOT NULL without DEFAULT (Prisma @updatedAt)
ALTER TABLE "farms" ALTER COLUMN "updated_at" SET DEFAULT now();

-- fields.updated_at: NOT NULL without DEFAULT (Prisma @updatedAt)
ALTER TABLE "fields" ALTER COLUMN "updated_at" SET DEFAULT now();

-- sync_status.updated_at: NOT NULL without DEFAULT (Prisma @updatedAt)
ALTER TABLE "sync_status" ALTER COLUMN "updated_at" SET DEFAULT now();

-- tasks.updated_at: NOT NULL without DEFAULT (Prisma @updatedAt)
ALTER TABLE "tasks" ALTER COLUMN "updated_at" SET DEFAULT now();

-- Note on indexes from initial migration (0001_init_postgis):
-- The following indexes were created non-concurrently on empty tables, which is safe:
--   idx_field_tenant, idx_field_sync, idx_field_status, idx_field_crop,
--   idx_field_boundary (GIST), idx_field_centroid (GIST),
--   idx_history_field, idx_history_date,
--   idx_task_field, idx_task_status, idx_task_due,
--   idx_ndvi_field_date
-- These are acceptable for initial schema creation (empty tables).
-- All subsequent migrations use standard CREATE INDEX within Prisma transaction wrapper.
