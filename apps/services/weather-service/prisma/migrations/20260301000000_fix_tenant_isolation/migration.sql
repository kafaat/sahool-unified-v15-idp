-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Fix multi-tenant isolation for weather models
-- إصلاح عزل المستأجر لنماذج الطقس
-- Purpose: Make tenant_id required (NOT NULL) on weather_observations,
--          weather_forecasts, and weather_alerts to enforce multi-tenant isolation.
-- Drift Report: CI multi-tenant violation (HIGH severity)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Backfill NULL tenant_id values with 'unassigned' sentinel
-- الخطوة 1: ملء القيم الفارغة بقيمة 'unassigned'

UPDATE "weather_observations" SET "tenant_id" = 'unassigned' WHERE "tenant_id" IS NULL;
UPDATE "weather_forecasts" SET "tenant_id" = 'unassigned' WHERE "tenant_id" IS NULL;
UPDATE "weather_alerts" SET "tenant_id" = 'unassigned' WHERE "tenant_id" IS NULL;

-- Step 2: Set DEFAULT for tenant_id columns
-- الخطوة 2: تعيين القيمة الافتراضية

ALTER TABLE "weather_observations" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "weather_forecasts" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "weather_alerts" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- Step 3: Set NOT NULL constraint
-- الخطوة 3: تعيين قيد NOT NULL

ALTER TABLE "weather_observations" ALTER COLUMN "tenant_id" SET NOT NULL;
ALTER TABLE "weather_forecasts" ALTER COLUMN "tenant_id" SET NOT NULL;
ALTER TABLE "weather_alerts" ALTER COLUMN "tenant_id" SET NOT NULL;

-- Step 4: Set column type to VARCHAR(50) for consistency
-- الخطوة 4: تعيين نوع العمود

ALTER TABLE "weather_observations" ALTER COLUMN "tenant_id" TYPE VARCHAR(50);
ALTER TABLE "weather_forecasts" ALTER COLUMN "tenant_id" TYPE VARCHAR(50);
ALTER TABLE "weather_alerts" ALTER COLUMN "tenant_id" TYPE VARCHAR(50);

-- Step 5: Add updatedAt DEFAULT for weather_forecasts and weather_alerts
-- الخطوة 5: إضافة DEFAULT لأعمدة updated_at

ALTER TABLE "weather_forecasts" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "weather_alerts" ALTER COLUMN "updated_at" SET DEFAULT now();
