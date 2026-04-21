-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Schema-only hardening. weather-service src/ has no Prisma call
-- sites yet, but the composite unique ensures any future reader/writer gets
-- the tenant-bound `id_tenantId` accessor exposed by Prisma Client.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_weather_observation_id_tenant" ON "weather_observations" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_weather_forecast_id_tenant" ON "weather_forecasts" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_weather_alert_id_tenant" ON "weather_alerts" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_location_config_id_tenant" ON "location_configs" ("id", "tenant_id");
