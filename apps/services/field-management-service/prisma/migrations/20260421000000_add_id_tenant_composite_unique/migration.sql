-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Expose Prisma `id_tenantId` accessor so the ~42 findUnique / update
-- / delete call sites in field-management-service (fields, farms, tasks,
-- crop-seasons, field-operations, ndvi, field-reports, sync, erp-sync) bind
-- tenantId atomically with id, eliminating TOCTOU gaps between the
-- `findFirst({id, tenantId})` pre-check and the subsequent `update({id})`.
--
-- CarbonEventDedup is intentionally NOT included — its PK is already the
-- composite (tenant_id, operation_id), so findUnique({id}) is impossible.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_farm_id_tenant" ON "farms" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_id_tenant" ON "fields" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_boundary_history_id_tenant" ON "field_boundary_history" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_sync_status_id_tenant" ON "sync_status" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_task_id_tenant" ON "tasks" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_ndvi_reading_id_tenant" ON "ndvi_readings" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_kpi_snapshot_id_tenant" ON "field_kpi_snapshots" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_crop_season_id_tenant" ON "crop_seasons" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_operation_id_tenant" ON "field_operations" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_outbox_event_id_tenant" ON "outbox_events" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_idempotency_key_id_tenant" ON "idempotency_keys" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_operation_audit_id_tenant" ON "field_operation_audit" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_sub_zone_id_tenant" ON "field_sub_zones" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_report_id_tenant" ON "field_reports" ("id", "tenant_id");
