-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Initial Weather Service Schema
-- الترحيل: المخطط الأولي لخدمة الطقس
-- Service: weather-service
-- Created: 2026-02-25
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- ENUMS
-- ─────────────────────────────────────────────────────────────────────────────

-- Alert Type - نوع التنبيه
CREATE TYPE "AlertType" AS ENUM (
    'HEAT_STRESS',
    'FROST',
    'HEAVY_RAIN',
    'DROUGHT',
    'STRONG_WIND',
    'STORM',
    'DISEASE_RISK',
    'OTHER'
);

-- Alert Severity - شدة التنبيه
CREATE TYPE "AlertSeverity" AS ENUM (
    'INFO',
    'MINOR',
    'MODERATE',
    'SEVERE',
    'EXTREME'
);

-- ─────────────────────────────────────────────────────────────────────────────
-- TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. Weather Observations - الأرصاد الجوية
CREATE TABLE "weather_observations" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid()::TEXT,
    "location_id" TEXT NOT NULL,
    "tenant_id" VARCHAR(50) NOT NULL DEFAULT 'unassigned',
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "temperature" DOUBLE PRECISION NOT NULL,
    "humidity" DOUBLE PRECISION NOT NULL,
    "pressure" DOUBLE PRECISION NOT NULL,
    "windSpeed" DOUBLE PRECISION NOT NULL,
    "windDirection" DOUBLE PRECISION NOT NULL,
    "rainfall" DOUBLE PRECISION,
    "uvIndex" DOUBLE PRECISION,
    "cloudCover" DOUBLE PRECISION,
    "visibility" DOUBLE PRECISION,
    "source" TEXT NOT NULL,
    "raw_data" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "weather_observations_pkey" PRIMARY KEY ("id")
);

-- 2. Weather Forecasts - التنبؤات الجوية
CREATE TABLE "weather_forecasts" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid()::TEXT,
    "location_id" TEXT NOT NULL,
    "tenant_id" VARCHAR(50) NOT NULL DEFAULT 'unassigned',
    "forecast_for" TIMESTAMP(3) NOT NULL,
    "fetched_at" TIMESTAMP(3) NOT NULL,
    "provider" TEXT NOT NULL,
    "hourly_data" JSONB NOT NULL,
    "daily_data" JSONB NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "weather_forecasts_pkey" PRIMARY KEY ("id")
);

-- 3. Weather Alerts - التنبيهات الجوية
CREATE TABLE "weather_alerts" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid()::TEXT,
    "location_id" TEXT NOT NULL,
    "tenant_id" VARCHAR(50) NOT NULL DEFAULT 'unassigned',
    "alert_type" "AlertType" NOT NULL,
    "severity" "AlertSeverity" NOT NULL,
    "headline" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "start_time" TIMESTAMP(3) NOT NULL,
    "end_time" TIMESTAMP(3) NOT NULL,
    "source" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "weather_alerts_pkey" PRIMARY KEY ("id")
);

-- 4. Location Configs - إعدادات المواقع
CREATE TABLE "location_configs" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid()::TEXT,
    "tenant_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "timezone" TEXT NOT NULL DEFAULT 'Asia/Aden',
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "fetch_interval" INTEGER NOT NULL DEFAULT 3600,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "location_configs_pkey" PRIMARY KEY ("id")
);

-- ─────────────────────────────────────────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────────────────────────────────────────

-- Weather Observations indexes
CREATE INDEX "weather_observations_location_id_timestamp_idx" ON "weather_observations"("location_id", "timestamp" DESC);
CREATE INDEX "weather_observations_tenant_id_timestamp_idx" ON "weather_observations"("tenant_id", "timestamp" DESC);
CREATE INDEX "weather_observations_timestamp_idx" ON "weather_observations"("timestamp" DESC);
CREATE INDEX "weather_observations_latitude_longitude_timestamp_idx" ON "weather_observations"("latitude", "longitude", "timestamp");

-- Weather Forecasts indexes
CREATE INDEX "weather_forecasts_location_id_forecast_for_idx" ON "weather_forecasts"("location_id", "forecast_for" DESC);
CREATE INDEX "weather_forecasts_tenant_id_forecast_for_idx" ON "weather_forecasts"("tenant_id", "forecast_for" DESC);
CREATE INDEX "weather_forecasts_forecast_for_idx" ON "weather_forecasts"("forecast_for" DESC);
CREATE INDEX "weather_forecasts_fetched_at_idx" ON "weather_forecasts"("fetched_at" DESC);
CREATE UNIQUE INDEX "weather_forecasts_location_id_forecast_for_provider_key" ON "weather_forecasts"("location_id", "forecast_for", "provider");

-- Weather Alerts indexes
CREATE INDEX "weather_alerts_location_id_start_time_idx" ON "weather_alerts"("location_id", "start_time" DESC);
CREATE INDEX "weather_alerts_tenant_id_start_time_idx" ON "weather_alerts"("tenant_id", "start_time" DESC);
CREATE INDEX "weather_alerts_alert_type_severity_idx" ON "weather_alerts"("alert_type", "severity");
CREATE INDEX "weather_alerts_start_time_end_time_idx" ON "weather_alerts"("start_time", "end_time");
CREATE INDEX "weather_alerts_end_time_idx" ON "weather_alerts"("end_time" DESC);

-- Location Configs indexes
CREATE INDEX "location_configs_tenant_id_is_active_idx" ON "location_configs"("tenant_id", "is_active");
CREATE INDEX "location_configs_is_active_idx" ON "location_configs"("is_active");
CREATE UNIQUE INDEX "location_configs_tenant_id_latitude_longitude_key" ON "location_configs"("tenant_id", "latitude", "longitude");
