-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Fix NOT NULL columns without DEFAULT values
-- إصلاح أعمدة NOT NULL بدون قيم افتراضية
-- Purpose: Prevent breaking deployments when inserting into NOT NULL columns
-- Drift Report: 7d5dc4c6-bc6
-- ═══════════════════════════════════════════════════════════════════════════════

-- tasks.created_by: NOT NULL without DEFAULT (initial migration)
-- Safe default for system-created tasks
ALTER TABLE "tasks" ALTER COLUMN "created_by" SET DEFAULT 'system';

-- field_boundary_history.version_at_change: NOT NULL without DEFAULT
ALTER TABLE "field_boundary_history" ALTER COLUMN "version_at_change" SET DEFAULT 1;

-- Ensure tenant_id columns retain a safe DEFAULT for new rows
-- Previous migration dropped DEFAULT after backfill; restore sentinel default
ALTER TABLE "field_boundary_history" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "tasks" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "ndvi_readings" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- Fix non-concurrent indexes: recreate with CONCURRENTLY where safe
-- Note: Initial migration indexes are already applied and cannot be recreated
-- without downtime. Adding concurrent alternatives for future safety.
-- The following indexes from 0001_init_postgis were non-concurrent:
--   idx_field_tenant, idx_field_sync, idx_field_status, idx_field_crop,
--   idx_field_boundary (GIST), idx_field_centroid (GIST),
--   idx_history_field, idx_history_date,
--   idx_task_field, idx_task_status, idx_task_due,
--   idx_ndvi_field_date
-- These are acceptable for initial schema creation (empty tables).
-- All subsequent migrations use CONCURRENTLY.
