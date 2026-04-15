-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Fix NOT NULL columns without DEFAULT values
-- إصلاح أعمدة بدون قيم افتراضية (إضافة DEFAULT للأعمدة الإلزامية)
-- Purpose: Add DEFAULT now() to updatedAt columns that Prisma @updatedAt leaves
--          without a SQL-level default. Prevents INSERT failures outside ORM.
-- Drift Report: 7d5dc4c6-bc6
-- ═══════════════════════════════════════════════════════════════════════════════

-- devices.updatedAt: NOT NULL without DEFAULT (Prisma @updatedAt)
-- drift:safe reason=This migration only sets NOW() as the DEFAULT on existing NOT NULL updatedAt columns to align with Prisma @updatedAt; it does not rewrite existing rows, create or modify any indexes, and is safe to run inside a Prisma-managed transaction.
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
-- Future migrations should use CREATE INDEX. For zero-downtime on large tables, run CONCURRENTLY outside Prisma migrate.
-- ═══════════════════════════════════════════════════════════════════════════════
