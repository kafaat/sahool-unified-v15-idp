-- drift:safe reason=Additive migration only. CREATE TABLE IF NOT EXISTS on new tables
-- with zero rows and ALTER TABLE ADD COLUMN IF NOT EXISTS (all nullable) on
-- existing tables. No mutations to existing rows, no locks observable to
-- production traffic. Partial indexes on empty / mostly-empty predicates.
-- Migration: Phase 1 — FieldSubZone + FieldReport + Carbon columns
-- الهجرة: المرحلة الأولى — مناطق فرعية + تقارير + انبعاثات الكربون
-- Created: 2026-04-11
--
-- Scope (per Phase 1 gap analysis):
--   A4. Multi-polygon sub-zones (terraced Yemeni farms)
--   A5. Async HTML/PDF report generation (Arabic RTL)
--   A6. Carbon footprint per operation (IPCC Tier 1 compatible)
--   A1. Hook for carbon-service (column schema — service lives separately)

-- ---------------------------------------------------------------------------
-- Table: field_sub_zones
-- Represents sub-polygons within a single Field record. Crucial for terraced
-- Yemeni agriculture where a logical "field" is actually 10-30 small terraces
-- each with different elevation, slope, aspect, and crop performance. A
-- single NDVI reading on the whole field would mask this variability.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "field_sub_zones" (
    "id"              UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"       VARCHAR(100) NOT NULL,
    "field_id"        UUID NOT NULL,

    "name"            VARCHAR(255) NOT NULL,
    "name_ar"         VARCHAR(255),
    "description"     TEXT,

    -- PostGIS polygon for the sub-zone (MUST be inside the parent field)
    "boundary"        geometry(Polygon, 4326),
    "area_hectares"   DECIMAL(10, 4),

    -- Topography (populated from terrain-core-service via DEM lookup)
    "elevation_m"     DECIMAL(8, 2),
    "slope_degrees"   DECIMAL(5, 2),
    "aspect"          VARCHAR(20),    -- N | NE | E | SE | S | SW | W | NW | flat
    "is_terrace"      BOOLEAN NOT NULL DEFAULT FALSE,
    "terrace_level"   INTEGER,        -- 1 = lowest, N = highest

    -- Ordering for stable UI display
    "display_order"   INTEGER NOT NULL DEFAULT 0,

    -- Soft delete (SOX audit)
    "deleted_at"      TIMESTAMPTZ,
    "deleted_by"      VARCHAR(100),

    -- Audit
    "created_by"      VARCHAR(100),
    "created_at"      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "updated_at"      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT "field_sub_zones_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "field_sub_zones_field_fk"
        FOREIGN KEY ("field_id") REFERENCES "fields"("id") ON DELETE CASCADE,
    CONSTRAINT "field_sub_zones_aspect_check"
        CHECK ("aspect" IS NULL OR "aspect" IN
            ('N','NE','E','SE','S','SW','W','NW','flat'))
);

CREATE INDEX IF NOT EXISTS "idx_field_sub_zone_tenant"
    ON "field_sub_zones" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_field_sub_zone_field"
    ON "field_sub_zones" ("field_id", "display_order");
CREATE INDEX IF NOT EXISTS "idx_field_sub_zone_terrace"
    ON "field_sub_zones" ("field_id", "terrace_level")
    WHERE "is_terrace" = TRUE;
CREATE INDEX IF NOT EXISTS "idx_field_sub_zone_not_deleted"
    ON "field_sub_zones" ("tenant_id", "field_id")
    WHERE "deleted_at" IS NULL;

-- Spatial index on the boundary (GiST) — used by ST_Contains /
-- ST_Intersects when assigning NDVI readings to sub-zones.
CREATE INDEX IF NOT EXISTS "idx_field_sub_zone_boundary_gist"
    ON "field_sub_zones" USING GIST ("boundary");

-- ---------------------------------------------------------------------------
-- Table: field_reports
-- Async-generated per-field reports. Caller POSTs a "generate report"
-- request; a background worker renders HTML (Arabic RTL) + charts, uploads
-- to object storage (MinIO / S3), and stamps the resulting URL back on the
-- row. Mirrors the Farmonaut pattern of returning a URL instead of bytes.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "field_reports" (
    "id"              UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"       VARCHAR(100) NOT NULL,
    "field_id"        UUID NOT NULL,
    "crop_season_id"  UUID,

    -- Report metadata
    "report_type"     VARCHAR(50) NOT NULL DEFAULT 'field_summary',
    "language"        VARCHAR(8) NOT NULL DEFAULT 'ar',
    "period_from"     DATE,
    "period_to"       DATE,

    -- Rendering status
    "status"          VARCHAR(20) NOT NULL DEFAULT 'pending',
    "rendered_at"     TIMESTAMPTZ,
    "error_message"   TEXT,
    "render_attempts" INTEGER NOT NULL DEFAULT 0,

    -- Output
    "content_html"    TEXT,
    "content_url"     VARCHAR(1000),      -- signed URL to MinIO/S3
    "content_size_bytes" BIGINT,
    "content_type"    VARCHAR(50),         -- text/html or application/pdf
    "expires_at"      TIMESTAMPTZ,         -- signed URL expiry

    -- Snapshot of what was rendered (for audit / debugging)
    "input_snapshot"  JSONB,

    -- Audit
    "requested_by"    VARCHAR(100),
    "created_at"      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "updated_at"      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT "field_reports_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "field_reports_field_fk"
        FOREIGN KEY ("field_id") REFERENCES "fields"("id") ON DELETE CASCADE,
    CONSTRAINT "field_reports_crop_season_fk"
        FOREIGN KEY ("crop_season_id") REFERENCES "crop_seasons"("id") ON DELETE SET NULL,
    CONSTRAINT "field_reports_status_check"
        CHECK ("status" IN ('pending','rendering','ready','failed','expired')),
    CONSTRAINT "field_reports_type_check"
        CHECK ("report_type" IN
            ('field_summary','crop_season','weather_history',
             'ndvi_timeseries','operation_log','carbon_footprint',
             'financial_summary'))
);

CREATE INDEX IF NOT EXISTS "idx_field_report_tenant"
    ON "field_reports" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_field_report_field"
    ON "field_reports" ("field_id", "created_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_field_report_crop_season"
    ON "field_reports" ("crop_season_id");
CREATE INDEX IF NOT EXISTS "idx_field_report_pending"
    ON "field_reports" ("status", "created_at")
    WHERE "status" IN ('pending','rendering');
CREATE INDEX IF NOT EXISTS "idx_field_report_expired_cleanup"
    ON "field_reports" ("expires_at")
    WHERE "status" = 'ready' AND "expires_at" IS NOT NULL;

-- ---------------------------------------------------------------------------
-- ALTER: field_operations — carbon footprint columns
-- Follows IPCC Guidelines for National Greenhouse Gas Inventories, Tier 1.
-- Emissions are computed per operation based on fuel consumption, fertilizer
-- N application, machinery type, and operation-specific emission factors.
-- Sequestration applies to operations like cover cropping, no-till, and
-- biochar application that lock carbon into the soil.
-- ---------------------------------------------------------------------------

ALTER TABLE "field_operations"
    -- Direct CO2 equivalent emissions from this operation (kg CO2e).
    ADD COLUMN IF NOT EXISTS "co2_emissions_kg"     DECIMAL(12, 2),
    -- Estimated CO2 sequestered by this operation (kg CO2e, negative emissions).
    ADD COLUMN IF NOT EXISTS "co2_sequestration_kg" DECIMAL(12, 2),
    -- Net CO2 impact = emissions - sequestration.
    ADD COLUMN IF NOT EXISTS "co2_net_kg"           DECIMAL(12, 2),
    -- Whether this operation is eligible for carbon-credit claims.
    ADD COLUMN IF NOT EXISTS "carbon_credit_eligible" BOOLEAN NOT NULL DEFAULT FALSE,
    -- IPCC methodology tier: '1' (default factors), '2' (region-specific),
    -- '3' (model-based). Default to Tier 1 until region-specific factors
    -- are calibrated for Yemen / Saudi Arabia.
    ADD COLUMN IF NOT EXISTS "carbon_methodology"   VARCHAR(50),
    -- Primary emission source so dashboards can slice by category.
    -- Canonical values: fuel | fertilizer_n | fertilizer_other | machinery |
    -- pesticide | land_prep | residue_burning | sequestration | mixed
    ADD COLUMN IF NOT EXISTS "emission_source_type" VARCHAR(50),
    -- When carbon-service last computed these values (null = not computed).
    ADD COLUMN IF NOT EXISTS "carbon_computed_at"   TIMESTAMPTZ;

-- Index for the carbon-service worker that polls operations needing
-- CO2 calculation (those with cost data but no carbon data yet).
CREATE INDEX IF NOT EXISTS "idx_field_op_carbon_pending"
    ON "field_operations" ("tenant_id", "created_at")
    WHERE "carbon_computed_at" IS NULL
      AND "deleted_at" IS NULL;

-- Index for "eligible for carbon credits" queries — usually small subset.
CREATE INDEX IF NOT EXISTS "idx_field_op_carbon_eligible"
    ON "field_operations" ("tenant_id", "performed_at" DESC)
    WHERE "carbon_credit_eligible" = TRUE AND "deleted_at" IS NULL;

-- ---------------------------------------------------------------------------
-- ALTER: crop_seasons — cached carbon totals
-- Mirrors the cached cost rollup pattern so dashboards can list 100 seasons
-- without joining field_operations for aggregation.
-- ---------------------------------------------------------------------------

ALTER TABLE "crop_seasons"
    ADD COLUMN IF NOT EXISTS "total_co2_emissions_kg"     DECIMAL(14, 2),
    ADD COLUMN IF NOT EXISTS "total_co2_sequestration_kg" DECIMAL(14, 2),
    ADD COLUMN IF NOT EXISTS "total_co2_net_kg"           DECIMAL(14, 2),
    ADD COLUMN IF NOT EXISTS "carbon_totals_updated_at"   TIMESTAMPTZ;

-- ---------------------------------------------------------------------------
-- Trigger: keep field_sub_zones.updated_at + field_reports.updated_at fresh.
-- Reuses the shared set_updated_at() function defined in the Phase 0 migration.
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS "set_field_sub_zones_updated_at" ON "field_sub_zones";
CREATE TRIGGER "set_field_sub_zones_updated_at"
    BEFORE UPDATE ON "field_sub_zones"
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS "set_field_reports_updated_at" ON "field_reports";
CREATE TRIGGER "set_field_reports_updated_at"
    BEFORE UPDATE ON "field_reports"
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();
