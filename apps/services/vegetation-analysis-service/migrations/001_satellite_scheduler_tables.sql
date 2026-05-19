-- Migration 001: Satellite Scheduler Tables
-- جداول مجدول الأقمار الصناعية
-- Created: 2026-05-19

-- Per-field per-day satellite index values and asset URLs
CREATE TABLE IF NOT EXISTS satellite_field_data (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL,
    field_id            UUID NOT NULL,
    acquisition_date    DATE NOT NULL,
    satellite           TEXT NOT NULL DEFAULT 'sentinel-2-l2a',
    cloud_cover_percent FLOAT,
    -- NDVI stats
    ndvi_mean FLOAT, ndvi_min FLOAT, ndvi_max FLOAT, ndvi_std FLOAT,
    -- EVI stats
    evi_mean  FLOAT, evi_min  FLOAT, evi_max  FLOAT, evi_std  FLOAT,
    -- LAI stats
    lai_mean  FLOAT, lai_min  FLOAT, lai_max  FLOAT, lai_std  FLOAT,
    -- NDWI stats
    ndwi_mean FLOAT, ndwi_min FLOAT, ndwi_max FLOAT, ndwi_std FLOAT,
    -- Asset URLs (stored in MinIO)
    geotiff_url         TEXT,
    png_url             TEXT,
    -- Raw STAC feature JSON for future flexibility
    stac_metadata       JSONB,
    processing_status   TEXT NOT NULL DEFAULT 'completed',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, field_id, acquisition_date)
);

CREATE INDEX IF NOT EXISTS idx_sfd_tenant_field
    ON satellite_field_data(tenant_id, field_id);
CREATE INDEX IF NOT EXISTS idx_sfd_acquisition_date
    ON satellite_field_data(acquisition_date);
CREATE INDEX IF NOT EXISTS idx_sfd_processing_status
    ON satellite_field_data(processing_status);

-- Planned / completed / missed overfly dates per field
CREATE TABLE IF NOT EXISTS satellite_acquisition_plan (
    tenant_id       UUID NOT NULL,
    field_id        UUID NOT NULL,
    planned_date    DATE NOT NULL,
    plan_fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- planned | completed | missed | skipped
    status          TEXT NOT NULL DEFAULT 'planned',
    PRIMARY KEY (tenant_id, field_id, planned_date)
);

CREATE INDEX IF NOT EXISTS idx_sap_planned_date
    ON satellite_acquisition_plan(planned_date);
CREATE INDEX IF NOT EXISTS idx_sap_status
    ON satellite_acquisition_plan(status);
CREATE INDEX IF NOT EXISTS idx_sap_tenant_field_status
    ON satellite_acquisition_plan(tenant_id, field_id, status);
