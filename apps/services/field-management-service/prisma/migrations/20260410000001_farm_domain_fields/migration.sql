-- SAHOOL Field Management - Farm domain fields (Wave 2)
--
-- Adds farmer-facing display columns required by the Admin Portal and
-- Mobile UIs: bilingual name/region/water source, workers count, status,
-- cultivated area, label location, and owner display name.
--
-- NOTE: Does NOT drop the existing PostGIS `location` geometry column.
--       The new `location_label` column is a human-readable display
--       string (e.g. "Riyadh Province, Sector 5"). Prisma maps the
--       geometry column to `Farm.locationGeom` and the string to
--       `Farm.location`.
--
-- drift:safe reason=additive-column-addition

ALTER TABLE "farms"
    ADD COLUMN IF NOT EXISTS "name_ar"                 VARCHAR(255),
    ADD COLUMN IF NOT EXISTS "region"                  VARCHAR(255),
    ADD COLUMN IF NOT EXISTS "region_ar"               VARCHAR(255),
    ADD COLUMN IF NOT EXISTS "water_source"            VARCHAR(255),
    ADD COLUMN IF NOT EXISTS "water_source_ar"         VARCHAR(255),
    ADD COLUMN IF NOT EXISTS "workers_count"           INTEGER       NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS "status"                  VARCHAR(32)   NOT NULL DEFAULT 'active',
    ADD COLUMN IF NOT EXISTS "cultivated_area_hectares" DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS "location_label"          VARCHAR(500),
    ADD COLUMN IF NOT EXISTS "location_label_ar"       VARCHAR(500),
    ADD COLUMN IF NOT EXISTS "owner_name"              VARCHAR(255);

-- Composite index for status-filtered farm listings
-- NOTE: CONCURRENTLY is not allowed inside a Prisma transaction block (P3018).
CREATE INDEX IF NOT EXISTS "idx_farm_tenant_status"
    ON "farms" ("tenant_id", "status");

COMMENT ON COLUMN "farms"."name_ar"                 IS 'Arabic farm name';
COMMENT ON COLUMN "farms"."region"                  IS 'Region / province (EN)';
COMMENT ON COLUMN "farms"."region_ar"               IS 'Region / province (AR)';
COMMENT ON COLUMN "farms"."water_source"            IS 'Primary water source (EN)';
COMMENT ON COLUMN "farms"."water_source_ar"         IS 'Primary water source (AR)';
COMMENT ON COLUMN "farms"."workers_count"           IS 'Number of workers currently employed';
COMMENT ON COLUMN "farms"."status"                  IS 'Farm status: active|inactive|archived';
COMMENT ON COLUMN "farms"."cultivated_area_hectares" IS 'Actively cultivated area (ha), subset of total_area_hectares';
COMMENT ON COLUMN "farms"."location_label"          IS 'Human-readable location label (EN)';
COMMENT ON COLUMN "farms"."location_label_ar"       IS 'Human-readable location label (AR)';
COMMENT ON COLUMN "farms"."owner_name"              IS 'Farm owner display name (denormalised from users)';
