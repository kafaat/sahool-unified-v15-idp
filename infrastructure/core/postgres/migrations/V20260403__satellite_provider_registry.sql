-- Ensure pgcrypto is available for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform — Satellite & Weather Provider Registry Tables
-- جداول تسجيل مزودي الأقمار الصناعية والطقس
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: V20260403__satellite_provider_registry.sql
-- Author: SAHOOL Platform Team
-- Description: Track external satellite/weather provider configurations,
--              API usage quotas, health status, and failover chains.

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Provider Registry — مسجل المزودين
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS satellite_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    name_ar VARCHAR(100) NOT NULL,
    provider_type VARCHAR(50) NOT NULL,  -- 'satellite', 'weather', 'map_tiles'
    priority INT NOT NULL DEFAULT 100,  -- Lower = higher priority
    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    -- Connection details
    base_url TEXT NOT NULL,
    auth_type VARCHAR(30) NOT NULL DEFAULT 'none',  -- 'none', 'api_key', 'oauth2', 'basic'
    auth_url TEXT,  -- OAuth2 token endpoint

    -- Capabilities
    resolution_m INT,  -- Spatial resolution in meters (NULL for weather)
    revisit_days FLOAT,  -- Revisit frequency in days
    satellites TEXT [],  -- Array of satellite names
    indices TEXT [],  -- Supported indices: NDVI, EVI, SAVI, etc.

    -- Quota / Rate limits
    free_tier BOOLEAN NOT NULL DEFAULT FALSE,
    quota_monthly INT,  -- Monthly API call limit (NULL = unlimited)
    quota_daily INT,  -- Daily limit
    processing_units_monthly INT,  -- For Sentinel Hub style quotas

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, degraded, offline, maintenance
    last_health_check TIMESTAMPTZ,
    last_error TEXT,
    uptime_pct FLOAT DEFAULT 100.0,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Provider Usage Tracking — تتبع استخدام المزودين
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS satellite_provider_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES satellite_providers (id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,

    -- Usage counters
    period_start DATE NOT NULL,  -- First day of period (month or day)
    period_type VARCHAR(10) NOT NULL DEFAULT 'monthly',  -- 'daily', 'monthly'
    api_calls INT NOT NULL DEFAULT 0,
    processing_units INT NOT NULL DEFAULT 0,
    bytes_downloaded BIGINT NOT NULL DEFAULT 0,
    scenes_fetched INT NOT NULL DEFAULT 0,
    ndvi_requests INT NOT NULL DEFAULT 0,

    -- Cost tracking
    estimated_cost_usd FLOAT DEFAULT 0.0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (provider_id, tenant_id, period_start, period_type)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Provider Health Log — سجل صحة المزودين
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS satellite_provider_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES satellite_providers (id) ON DELETE CASCADE,

    checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status VARCHAR(20) NOT NULL,  -- healthy, degraded, offline, timeout
    response_ms INT,  -- Response time in milliseconds
    error_message TEXT,

    -- Indexed for cleanup (keep 30 days)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Indexes — الفهارس
-- ─────────────────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_providers_type_priority
ON satellite_providers (provider_type, priority) WHERE enabled = TRUE;

CREATE INDEX IF NOT EXISTS idx_provider_usage_tenant_period
ON satellite_provider_usage (tenant_id, period_start);

CREATE INDEX IF NOT EXISTS idx_provider_usage_provider_period
ON satellite_provider_usage (provider_id, period_start);

CREATE INDEX IF NOT EXISTS idx_provider_health_provider_time
ON satellite_provider_health (provider_id, checked_at DESC);

-- Auto-cleanup old health records (keep 30 days)
CREATE INDEX IF NOT EXISTS idx_provider_health_cleanup
ON satellite_provider_health (created_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Seed Default Providers — بذر المزودين الافتراضيين
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO satellite_providers (
    name,
    name_ar,
    provider_type,
    priority,
    base_url,
    auth_type,
    resolution_m,
    revisit_days,
    satellites,
    indices,
    free_tier,
    quota_monthly,
    processing_units_monthly
)
VALUES
(
    'sentinel_hub', 'سنتينل هب', 'satellite', 10, 'https://services.sentinel-hub.com/api/v1', 'oauth2', 10, 5,
    ARRAY['Sentinel-2A', 'Sentinel-2B', 'Sentinel-1', 'Landsat-8', 'Landsat-9'],
    ARRAY['NDVI', 'EVI', 'SAVI', 'NDWI', 'NDRE', 'LAI', 'MSAVI', 'GNDVI'],
    TRUE, NULL, 30000
),

(
    'agromonitoring', 'أجرو مونيتورينج', 'satellite', 20, 'https://api.agromonitoring.com/agro/1.0', 'api_key', 10, 3,
    ARRAY['Sentinel-2', 'Landsat-8'],
    ARRAY['NDVI', 'EVI'],
    TRUE, 25000, NULL
),

(
    'planet_labs', 'بلانيت لابز', 'satellite', 30, 'https://api.planet.com/data/v1', 'api_key', 3, 1,
    ARRAY['PlanetScope', 'SkySat'],
    ARRAY['NDVI', 'EVI', 'SAVI'],
    FALSE, NULL, 30000
),

(
    'copernicus_stac', 'كوبرنيكوس', 'satellite', 40, 'https://catalogue.dataspace.copernicus.eu/stac', 'none', 10, 5,
    ARRAY['Sentinel-2'],
    ARRAY['NDVI'],
    TRUE, NULL, NULL
),

(
    'nasa_earthdata', 'ناسا إيرث داتا', 'satellite', 50, 'https://cmr.earthdata.nasa.gov/search', 'basic', 250, 1,
    ARRAY['MODIS-Terra', 'MODIS-Aqua', 'VIIRS'],
    ARRAY['NDVI', 'EVI'],
    TRUE, NULL, NULL
),

(
    'usgs_landsat_archive',
    'أرشيف لاندسات',
    'satellite',
    60,
    'https://m2m.cr.usgs.gov/api/api/json/stable',
    'basic',
    30,
    16,
    ARRAY['Landsat-1', 'Landsat-2', 'Landsat-3', 'Landsat-4', 'Landsat-5', 'Landsat-7', 'Landsat-8', 'Landsat-9'],
    ARRAY['NDVI', 'EVI', 'SAVI', 'NDWI'],
    TRUE, NULL, NULL
),

(
    'open_meteo', 'أوبن ميتيو', 'weather', 10, 'https://api.open-meteo.com/v1/forecast', 'none', NULL, NULL,
    NULL, NULL, TRUE, 10000, NULL
),

(
    'openweathermap', 'أوبن ويذر ماب', 'weather', 20, 'https://api.openweathermap.org/data/2.5', 'api_key', NULL, NULL,
    NULL, NULL, TRUE, 30000, NULL
),

(
    'openstreetmap', 'أوبن ستريت ماب', 'map_tiles', 10, 'https://tile.openstreetmap.org', 'none', NULL, NULL,
    NULL, NULL, TRUE, NULL, NULL
),

(
    'esri_satellite',
    'إسري',
    'map_tiles',
    20,
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer',
    'none',
    NULL,
    NULL,
    NULL, NULL, TRUE, NULL, NULL
)

ON CONFLICT (name) DO UPDATE SET
    updated_at = now(),
    base_url = excluded.base_url,
    priority = excluded.priority;

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. Auto-update updated_at trigger — تحديث تلقائي لوقت التعديل
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION update_satellite_providers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_satellite_providers_updated_at
BEFORE UPDATE ON satellite_providers
FOR EACH ROW
EXECUTE FUNCTION update_satellite_providers_updated_at();

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. Row Level Security — أمان مستوى الصف
-- ─────────────────────────────────────────────────────────────────────────────

-- Providers table is global (no RLS needed — read by all tenants)
-- Usage table is tenant-scoped
ALTER TABLE satellite_provider_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE satellite_provider_usage FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS satellite_provider_usage_tenant_policy ON satellite_provider_usage;
CREATE POLICY satellite_provider_usage_tenant_policy ON satellite_provider_usage
FOR ALL
USING (tenant_id = current_tenant_id() OR is_super_admin())
WITH CHECK (tenant_id = current_tenant_id() OR is_super_admin());
