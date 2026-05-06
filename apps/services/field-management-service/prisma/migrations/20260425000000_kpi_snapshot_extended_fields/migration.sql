-- drift:safe reason=Additive migration only. All new columns are nullable with no defaults,
-- no existing column renames or drops, precision widening via ALTER COLUMN TYPE is safe
-- on PostgreSQL (no table rewrite required for Decimal precision increases).

-- Migration: Expand FieldKpiSnapshot with extended vegetation, water, soil, fire, urban,
--            snow, atmosphere, air quality, and solar irradiance columns
-- الهجرة: توسيع جدول لقطات KPI — مؤشرات نباتية إضافية، جودة الهواء، الإشعاع الشمسي
-- Created: 2026-04-25

-- ── Widen existing precision columns (Decimal(5,4) → Decimal(6,4), lai Decimal(6,4) → Decimal(7,4)) ──
ALTER TABLE "field_kpi_snapshots"
    ALTER COLUMN "ndvi"  TYPE DECIMAL(6,4),
    ALTER COLUMN "evi"   TYPE DECIMAL(6,4),
    ALTER COLUMN "savi"  TYPE DECIMAL(6,4),
    ALTER COLUMN "ndmi"  TYPE DECIMAL(6,4),
    ALTER COLUMN "ndwi"  TYPE DECIMAL(6,4),
    ALTER COLUMN "lai"   TYPE DECIMAL(7,4);

-- ── Sentinel Hub: Extra vegetation indices ────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "gndvi"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "ndre"   DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "msavi"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "osavi"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "evi2"   DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "cvi"    DECIMAL(7,4),
    ADD COLUMN IF NOT EXISTS "mcari"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "tcari"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "wdrvi"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "vari"   DECIMAL(6,4);

-- ── Sentinel Hub: Water indices ───────────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "mndwi"        DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "turbidity"    DECIMAL(8,4),
    ADD COLUMN IF NOT EXISTS "chlorophyll_a" DECIMAL(8,4),
    ADD COLUMN IF NOT EXISTS "phycocyanin"  DECIMAL(8,4);

-- ── Sentinel Hub: Soil / Bare land ───────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "bsi"   DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "nbsi"  DECIMAL(6,4);

-- ── Sentinel Hub: Fire / Burn ─────────────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "nbr"   DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "nbr2"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "bais2" DECIMAL(6,4);

-- ── Sentinel Hub: Urban / Built-up ───────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "ndbi"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "ibi"   DECIMAL(6,4);

-- ── Sentinel Hub: Snow / Ice ──────────────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "ndsi"  DECIMAL(6,4),
    ADD COLUMN IF NOT EXISTS "ndgi"  DECIMAL(6,4);

-- ── Sentinel Hub: Atmosphere ─────────────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "lst"               DECIMAL(6,2),
    ADD COLUMN IF NOT EXISTS "cloud_probability" DECIMAL(5,2),
    ADD COLUMN IF NOT EXISTS "arvi"              DECIMAL(6,4);

-- ── OpenWeather: Extra weather columns ───────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "wind_direction_deg" DECIMAL(5,1),
    ADD COLUMN IF NOT EXISTS "pressure_hpa"       DECIMAL(7,2),
    ADD COLUMN IF NOT EXISTS "cloud_cover_pct"    DECIMAL(5,2),
    ADD COLUMN IF NOT EXISTS "visibility_m"       DECIMAL(8,1);

-- ── OpenWeather: Air pollution ────────────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "aqi"   INTEGER,
    ADD COLUMN IF NOT EXISTS "co"    DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "no"    DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "no2"   DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "o3"    DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "so2"   DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "nh3"   DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "pm2_5" DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "pm10"  DECIMAL(8,2);

-- ── Solar irradiance (Open-Meteo) ─────────────────────────────────────────
ALTER TABLE "field_kpi_snapshots"
    ADD COLUMN IF NOT EXISTS "ghi_clear_sky_wm2" DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "dni_clear_sky_wm2" DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "dhi_clear_sky_wm2" DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "ghi_cloudy_wm2"    DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "dni_cloudy_wm2"    DECIMAL(8,2),
    ADD COLUMN IF NOT EXISTS "dhi_cloudy_wm2"    DECIMAL(8,2);
