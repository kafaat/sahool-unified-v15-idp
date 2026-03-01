-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Drift Detection Fix (Report 5c6dd891-251)
-- إصلاح كشف الانحراف - تقرير 5c6dd891-251
-- Purpose: Resolve critical NOT NULL without DEFAULT pattern
-- Service: weather-service
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix: Ensure tenant_id columns have safe DEFAULT before NOT NULL
-- Migration 20260301000000 set DEFAULT then NOT NULL, which is safe but
-- the scanner flags the SET NOT NULL statement. Re-affirm defaults here.
-- ─────────────────────────────────────────────────────────────────────────────

-- weather_observations.tenant_id
ALTER TABLE "weather_observations" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- weather_forecasts.tenant_id
ALTER TABLE "weather_forecasts" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- weather_alerts.tenant_id
ALTER TABLE "weather_alerts" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- Ensure updatedAt columns have DEFAULT now()
ALTER TABLE "weather_forecasts" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "weather_alerts" ALTER COLUMN "updated_at" SET DEFAULT now();

-- ─────────────────────────────────────────────────────────────────────────────
-- location_configs.tenant_id: Ensure DEFAULT for direct SQL inserts
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE "location_configs" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "location_configs" ALTER COLUMN "updated_at" SET DEFAULT now();

-- ═══════════════════════════════════════════════════════════════════════════════
-- Note: weather_observations has no updated_at column (append-only table).
-- This is by design - observations are immutable once recorded.
-- ═══════════════════════════════════════════════════════════════════════════════
