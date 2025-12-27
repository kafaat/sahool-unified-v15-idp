"""
SAHOOL Field Service - Initial Migration
Creates all database tables for field service

Revision: 0_20251227000000_init
Created: 2025-12-27
"""

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    """Create initial schema"""
    return """
        -- ===================================================================
        -- FIELDS Table
        -- ===================================================================
        CREATE TABLE IF NOT EXISTS "fields" (
            "id" UUID NOT NULL PRIMARY KEY,
            "tenant_id" VARCHAR(64) NOT NULL,
            "user_id" VARCHAR(64) NOT NULL,
            "name" VARCHAR(200) NOT NULL,
            "name_en" VARCHAR(200),
            "status" VARCHAR(20) NOT NULL DEFAULT 'active',
            "location" JSONB NOT NULL,
            "boundary" JSONB,
            "area_hectares" DOUBLE PRECISION NOT NULL,
            "soil_type" VARCHAR(30) NOT NULL DEFAULT 'unknown',
            "irrigation_source" VARCHAR(30) NOT NULL DEFAULT 'none',
            "current_crop" VARCHAR(100),
            "metadata" JSONB,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT "fields_tenant_name_unique" UNIQUE ("tenant_id", "name")
        );

        -- Indexes for fields table
        CREATE INDEX IF NOT EXISTS "idx_fields_tenant_id" ON "fields" ("tenant_id");
        CREATE INDEX IF NOT EXISTS "idx_fields_user_id" ON "fields" ("user_id");
        CREATE INDEX IF NOT EXISTS "idx_fields_tenant_user" ON "fields" ("tenant_id", "user_id");
        CREATE INDEX IF NOT EXISTS "idx_fields_tenant_status" ON "fields" ("tenant_id", "status");
        CREATE INDEX IF NOT EXISTS "idx_fields_user_status" ON "fields" ("user_id", "status");

        COMMENT ON TABLE "fields" IS 'حقول زراعية - Agricultural fields';
        COMMENT ON COLUMN "fields"."id" IS 'معرف الحقل';
        COMMENT ON COLUMN "fields"."tenant_id" IS 'معرف المستأجر';
        COMMENT ON COLUMN "fields"."user_id" IS 'معرف المزارع';
        COMMENT ON COLUMN "fields"."name" IS 'اسم الحقل';
        COMMENT ON COLUMN "fields"."location" IS 'موقع الحقل (JSON)';
        COMMENT ON COLUMN "fields"."boundary" IS 'حدود الحقل (GeoJSON Polygon)';
        COMMENT ON COLUMN "fields"."area_hectares" IS 'المساحة بالهكتار';

        -- ===================================================================
        -- CROP SEASONS Table
        -- ===================================================================
        CREATE TABLE IF NOT EXISTS "crop_seasons" (
            "id" UUID NOT NULL PRIMARY KEY,
            "field_id" UUID NOT NULL,
            "tenant_id" VARCHAR(64) NOT NULL,
            "crop_type" VARCHAR(100) NOT NULL,
            "variety" VARCHAR(100),
            "planting_date" DATE NOT NULL,
            "expected_harvest" DATE,
            "harvest_date" DATE,
            "status" VARCHAR(20) NOT NULL DEFAULT 'planning',
            "expected_yield_kg" DOUBLE PRECISION,
            "actual_yield_kg" DOUBLE PRECISION,
            "quality_grade" VARCHAR(50),
            "seed_source" VARCHAR(200),
            "notes" TEXT,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes for crop_seasons table
        CREATE INDEX IF NOT EXISTS "idx_crop_seasons_field_id" ON "crop_seasons" ("field_id");
        CREATE INDEX IF NOT EXISTS "idx_crop_seasons_tenant_id" ON "crop_seasons" ("tenant_id");
        CREATE INDEX IF NOT EXISTS "idx_crop_seasons_field_status" ON "crop_seasons" ("field_id", "status");
        CREATE INDEX IF NOT EXISTS "idx_crop_seasons_tenant_crop" ON "crop_seasons" ("tenant_id", "crop_type");
        CREATE INDEX IF NOT EXISTS "idx_crop_seasons_planting_date" ON "crop_seasons" ("planting_date");

        COMMENT ON TABLE "crop_seasons" IS 'مواسم المحاصيل - Crop growing seasons';
        COMMENT ON COLUMN "crop_seasons"."crop_type" IS 'نوع المحصول';
        COMMENT ON COLUMN "crop_seasons"."planting_date" IS 'تاريخ الزراعة';
        COMMENT ON COLUMN "crop_seasons"."harvest_date" IS 'تاريخ الحصاد';

        -- ===================================================================
        -- ZONES Table
        -- ===================================================================
        CREATE TABLE IF NOT EXISTS "zones" (
            "id" UUID NOT NULL PRIMARY KEY,
            "field_id" UUID NOT NULL,
            "tenant_id" VARCHAR(64) NOT NULL,
            "name" VARCHAR(100) NOT NULL,
            "name_ar" VARCHAR(100),
            "boundary" JSONB NOT NULL,
            "area_hectares" DOUBLE PRECISION NOT NULL,
            "purpose" VARCHAR(50) NOT NULL,
            "notes" TEXT,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes for zones table
        CREATE INDEX IF NOT EXISTS "idx_zones_field_id" ON "zones" ("field_id");
        CREATE INDEX IF NOT EXISTS "idx_zones_tenant_id" ON "zones" ("tenant_id");

        COMMENT ON TABLE "zones" IS 'مناطق داخل الحقول - Sub-zones within fields';
        COMMENT ON COLUMN "zones"."purpose" IS 'غرض التقسيم - Purpose of zone division';

        -- ===================================================================
        -- NDVI RECORDS Table
        -- ===================================================================
        CREATE TABLE IF NOT EXISTS "ndvi_records" (
            "id" UUID NOT NULL PRIMARY KEY,
            "field_id" UUID NOT NULL,
            "tenant_id" VARCHAR(64) NOT NULL,
            "date" DATE NOT NULL,
            "mean" DOUBLE PRECISION NOT NULL,
            "min" DOUBLE PRECISION NOT NULL,
            "max" DOUBLE PRECISION NOT NULL,
            "std" DOUBLE PRECISION,
            "cloud_cover_pct" DOUBLE PRECISION,
            "source" VARCHAR(50),
            "metadata" JSONB,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT "ndvi_field_date_source_unique" UNIQUE ("field_id", "date", "source")
        );

        -- Indexes for ndvi_records table
        CREATE INDEX IF NOT EXISTS "idx_ndvi_records_field_id" ON "ndvi_records" ("field_id");
        CREATE INDEX IF NOT EXISTS "idx_ndvi_records_tenant_id" ON "ndvi_records" ("tenant_id");
        CREATE INDEX IF NOT EXISTS "idx_ndvi_records_field_date" ON "ndvi_records" ("field_id", "date");
        CREATE INDEX IF NOT EXISTS "idx_ndvi_records_tenant_date" ON "ndvi_records" ("tenant_id", "date");

        COMMENT ON TABLE "ndvi_records" IS 'سجلات NDVI - NDVI measurement records';
        COMMENT ON COLUMN "ndvi_records"."date" IS 'تاريخ القياس';
        COMMENT ON COLUMN "ndvi_records"."mean" IS 'متوسط NDVI';
        COMMENT ON COLUMN "ndvi_records"."source" IS 'مصدر البيانات (sentinel2, landsat, etc)';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    """Drop all tables"""
    return """
        DROP TABLE IF EXISTS "ndvi_records";
        DROP TABLE IF EXISTS "zones";
        DROP TABLE IF EXISTS "crop_seasons";
        DROP TABLE IF EXISTS "fields";
    """
