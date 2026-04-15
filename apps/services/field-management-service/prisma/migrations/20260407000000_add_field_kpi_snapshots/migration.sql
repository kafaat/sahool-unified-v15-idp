-- drift:safe reason=Indexes target the field_kpi_snapshots table that is CREATED in the
-- same migration above. At CREATE INDEX time the table has zero rows, so the non-
-- CONCURRENTLY index build is instantaneous and cannot lock any existing data.
-- Prisma wraps migrations in a transaction, which makes CREATE INDEX CONCURRENTLY
-- unusable; the standard CREATE INDEX form is the correct choice for new empty tables.
-- Migration: Add FieldKpiSnapshot table
-- الهجرة: إضافة جدول لقطات KPI للحقول (Sentinel Hub + OpenWeather)
-- Created: 2026-04-07

CREATE TABLE "field_kpi_snapshots" (
    "id"                    UUID NOT NULL DEFAULT gen_random_uuid(),
    "field_id"              UUID NOT NULL,
    "tenant_id"             VARCHAR(100) NOT NULL,
    "fetched_at"            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Sentinel Hub vegetation indices
    "ndvi"                  DECIMAL(5,4),
    "evi"                   DECIMAL(5,4),
    "ndwi"                  DECIMAL(5,4),
    "savi"                  DECIMAL(5,4),
    "lai"                   DECIMAL(6,4),
    "ndmi"                  DECIMAL(5,4),

    -- OpenWeather / weather data
    "temperature_c"         DECIMAL(5,2),
    "humidity_pct"          DECIMAL(5,2),
    "wind_speed_kmh"        DECIMAL(6,2),
    "precipitation_mm"      DECIMAL(6,2),
    "uv_index"              DECIMAL(4,2),
    "weather_condition"     VARCHAR(100),
    "weather_condition_ar"  VARCHAR(100),

    -- Source metadata
    "satellite_source"      VARCHAR(50),
    "weather_source"        VARCHAR(50),

    CONSTRAINT "field_kpi_snapshots_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "field_kpi_snapshots_field_fk"
        FOREIGN KEY ("field_id") REFERENCES "fields"("id") ON DELETE CASCADE
);

CREATE INDEX "idx_kpi_field_date" ON "field_kpi_snapshots" ("field_id", "fetched_at" DESC);
CREATE INDEX "idx_kpi_tenant"     ON "field_kpi_snapshots" ("tenant_id");
