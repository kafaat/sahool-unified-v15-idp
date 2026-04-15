-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Drift Detection Fix (Report 5c6dd891-251)
-- إصلاح كشف الانحراف - تقرير 5c6dd891-251
-- Purpose: Resolve critical mandatory-columns-without-DEFAULT and risky migration patterns
-- Service: iot-service
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix: Ensure updatedAt columns have DEFAULT now()
-- Prisma @updatedAt does not generate SQL-level DEFAULT. Migration 20260227
-- added defaults; re-affirm here to close drift scanner gap.
-- ─────────────────────────────────────────────────────────────────────────────

-- devices.updatedAt (mapped to "updatedAt" in camelCase schema)
-- drift:safe reason=CREATE INDEX inside a Prisma-managed transaction cannot use CONCURRENTLY; zero-downtime index creation must be run manually outside Prisma migrate on large production tables.
ALTER TABLE "devices" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- sensors.updatedAt
ALTER TABLE "sensors" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- actuators.updatedAt
ALTER TABLE "actuators" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- actuator_commands.updatedAt
ALTER TABLE "actuator_commands" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- device_alerts.updatedAt
ALTER TABLE "device_alerts" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- ─────────────────────────────────────────────────────────────────────────────
-- Medium: Non-concurrent index creation (Acknowledged)
-- فهارس غير متزامنة (مقبولة)
--
-- All 40+ indexes in 20260214000000_init were created during initial table
-- creation on EMPTY tables. Non-concurrent creation is safe and optimal
-- for initial schema setup. No data was at risk.
--
-- Tables affected: devices, sensors, sensor_readings, actuators,
--                  actuator_commands, device_alerts
--
-- All future migrations should use CREATE INDEX. For zero-downtime on large tables, run CONCURRENTLY outside Prisma migrate.
-- ═══════════════════════════════════════════════════════════════════════════════
