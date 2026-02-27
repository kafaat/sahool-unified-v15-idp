-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Fix NOT NULL columns without DEFAULT values
-- إصلاح أعمدة NOT NULL بدون قيم افتراضية
-- Purpose: Add DEFAULT now() to updatedAt columns that Prisma @updatedAt leaves
--          without a SQL-level default. Prevents INSERT failures outside ORM.
-- Drift Report: 7d5dc4c6-bc6
-- ═══════════════════════════════════════════════════════════════════════════════

-- devices.updatedAt: NOT NULL without DEFAULT (Prisma @updatedAt)
ALTER TABLE "devices" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- sensors.updatedAt: NOT NULL without DEFAULT
ALTER TABLE "sensors" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- actuators.updatedAt: NOT NULL without DEFAULT
ALTER TABLE "actuators" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- actuator_commands.updatedAt: NOT NULL without DEFAULT
ALTER TABLE "actuator_commands" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- device_alerts.updatedAt: NOT NULL without DEFAULT
ALTER TABLE "device_alerts" ALTER COLUMN "updatedAt" SET DEFAULT now();

-- ═══════════════════════════════════════════════════════════════════════════════
-- Note on non-concurrent indexes from initial migration (20260214000000_init):
-- All indexes were created in the initial schema on empty tables, which is safe.
-- Future migrations MUST use CREATE INDEX CONCURRENTLY for online index creation.
-- ═══════════════════════════════════════════════════════════════════════════════
