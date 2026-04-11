-- drift:safe reason=New empty tables (crop_seasons + field_operations) and their
-- indexes cannot lock any existing rows — at CREATE TABLE + CREATE INDEX time the
-- tables hold zero rows so non-CONCURRENTLY index builds are instantaneous. Prisma
-- wraps migrations in a transaction, which makes CREATE INDEX CONCURRENTLY unusable;
-- the standard CREATE INDEX form is the correct choice for new empty tables.
-- Foreign keys to existing "fields" table use ON DELETE CASCADE because a deleted
-- field must take its crop history + operation records with it (no dangling audits).
-- Migration: Add CropSeason + FieldOperation tables
-- الهجرة: إضافة جداول مواسم المحاصيل وعمليات الحقل
-- Created: 2026-04-11

-- ---------------------------------------------------------------------------
-- Table: crop_seasons
-- First-class archive of per-field crop rotations. Replaces the interim
-- field.metadata.cropHistory[] JSON shim with a relational table indexed on
-- (field_id, sowing_date DESC) so downstream services (NDVI pipeline,
-- yield-prediction, irrigation-smart, advisory-service) can query planted
-- crops by date range with proper indexes instead of JSON probes.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "crop_seasons" (
    "id"                      UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"               VARCHAR(100) NOT NULL,
    "field_id"                UUID NOT NULL,

    "crop_type"               VARCHAR(100) NOT NULL,
    "crop_type_ar"            VARCHAR(100),
    "season"                  VARCHAR(32),

    "sowing_date"             DATE NOT NULL,
    "expected_harvest_date"   DATE,
    "actual_harvest_date"     DATE,
    "ended_at"                TIMESTAMPTZ,
    "end_reason"              VARCHAR(255),

    "is_current"              BOOLEAN NOT NULL DEFAULT FALSE,

    "seed_variety"            VARCHAR(255),
    "seed_variety_ar"         VARCHAR(255),
    "planting_density_kg_ha"  DECIMAL(10, 2),
    "irrigation_type"         VARCHAR(50),

    "yield_kg_ha"             DECIMAL(10, 2),

    "notes"                   TEXT,
    "metadata"                JSONB,

    "created_at"              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "updated_at"              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT "crop_seasons_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "crop_seasons_field_fk"
        FOREIGN KEY ("field_id") REFERENCES "fields"("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_crop_season_tenant"
    ON "crop_seasons" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_crop_season_field"
    ON "crop_seasons" ("field_id");
CREATE INDEX IF NOT EXISTS "idx_crop_season_field_sown"
    ON "crop_seasons" ("field_id", "sowing_date" DESC);
CREATE INDEX IF NOT EXISTS "idx_crop_season_tenant_crop"
    ON "crop_seasons" ("tenant_id", "crop_type");
CREATE INDEX IF NOT EXISTS "idx_crop_season_tenant_sown"
    ON "crop_seasons" ("tenant_id", "sowing_date");

-- Partial unique index: at most one "current" season per field. This is the
-- DB-level enforcement of the denormalized is_current flag — the service
-- layer flips the old current to false inside the same transaction before
-- inserting the new current row, and this index guards against races.
CREATE UNIQUE INDEX IF NOT EXISTS "idx_crop_season_field_single_current"
    ON "crop_seasons" ("field_id")
    WHERE "is_current" = TRUE;

-- ---------------------------------------------------------------------------
-- Table: field_operations
-- Per-field operation log (plowing, land preparation, fertilization, spraying,
-- irrigation, harvesting, ...). Each row optionally links to:
--   * a CropSeason (so operations can be rolled up per season for cost/hours)
--   * an Equipment record in equipment-service (soft cross-service link via
--     UUID — equipment-service owns the canonical data, we cache the display
--     name here so the timeline keeps working when equipment-service is down).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "field_operations" (
    "id"                  UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"           VARCHAR(100) NOT NULL,
    "field_id"            UUID NOT NULL,
    "crop_season_id"      UUID,

    "operation_type"      VARCHAR(50) NOT NULL,

    "performed_at"        DATE NOT NULL,
    "ended_at"            TIMESTAMPTZ,
    "duration_hours"      DECIMAL(8, 2),

    "cost_amount"         DECIMAL(12, 2),
    "cost_currency"       VARCHAR(8) NOT NULL DEFAULT 'SAR',

    "equipment_id"        UUID,
    "equipment_name"      VARCHAR(255),
    "equipment_name_ar"   VARCHAR(255),

    "metadata"            JSONB,
    "notes"               TEXT,

    "created_by"          VARCHAR(100),
    "created_at"          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "updated_at"          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT "field_operations_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "field_operations_field_fk"
        FOREIGN KEY ("field_id") REFERENCES "fields"("id") ON DELETE CASCADE,
    CONSTRAINT "field_operations_crop_season_fk"
        FOREIGN KEY ("crop_season_id") REFERENCES "crop_seasons"("id") ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS "idx_field_op_tenant"
    ON "field_operations" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_field_op_field"
    ON "field_operations" ("field_id");
CREATE INDEX IF NOT EXISTS "idx_field_op_field_date"
    ON "field_operations" ("field_id", "performed_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_field_op_crop_season"
    ON "field_operations" ("crop_season_id");
CREATE INDEX IF NOT EXISTS "idx_field_op_equipment"
    ON "field_operations" ("equipment_id");
CREATE INDEX IF NOT EXISTS "idx_field_op_tenant_type"
    ON "field_operations" ("tenant_id", "operation_type");
CREATE INDEX IF NOT EXISTS "idx_field_op_tenant_date"
    ON "field_operations" ("tenant_id", "performed_at");

-- ---------------------------------------------------------------------------
-- Validation: operation_type must be one of the canonical values. Kept as a
-- CHECK constraint rather than an enum so new operation types can be added
-- from the application layer without forcing another migration.
-- ---------------------------------------------------------------------------

ALTER TABLE "field_operations"
    ADD CONSTRAINT "field_op_type_check"
    CHECK ("operation_type" IN (
        'plowing',
        'land_preparation',
        'fertilization',
        'spraying',
        'irrigation',
        'harvesting',
        'scouting',
        'sowing',
        'other'
    ));

-- ---------------------------------------------------------------------------
-- Trigger: keep updated_at fresh on UPDATE for both tables. We rely on the
-- existing public.set_updated_at() function created in the very first
-- migration (0001_init_postgis); if it doesn't exist yet, create it here
-- defensively so this migration can run in a clean database.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS "set_crop_seasons_updated_at" ON "crop_seasons";
CREATE TRIGGER "set_crop_seasons_updated_at"
    BEFORE UPDATE ON "crop_seasons"
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS "set_field_operations_updated_at" ON "field_operations";
CREATE TRIGGER "set_field_operations_updated_at"
    BEFORE UPDATE ON "field_operations"
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();
