-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Schema-only hardening. iot-service call sites are already safe
-- (upserts bind tenant via tenantId_deviceId composite or deterministic
-- sensor keys), but exposing the Prisma `id_tenantId` accessor lets future
-- code paths opt into tenant-bound lookups without a schema change.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_device_id_tenant" ON "devices" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_sensor_id_tenant" ON "sensors" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_sensor_reading_id_tenant" ON "sensor_readings" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_actuator_id_tenant" ON "actuators" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_actuator_command_id_tenant" ON "actuator_commands" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_device_alert_id_tenant" ON "device_alerts" ("id", "tenant_id");
