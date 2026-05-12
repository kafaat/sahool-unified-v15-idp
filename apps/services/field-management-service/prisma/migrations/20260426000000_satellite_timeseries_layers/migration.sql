-- drift:safe reason=Additive migration only. New table with no existing table modifications.
-- All indexes on new empty table, no locks on existing data.

-- Migration: Add satellite_timeseries_layers table
-- Phase 3 of Geospatial Audit — Time-Series Imagery Persistence
-- Stores per-field, per-index, per-date Sentinel Hub imagery metadata and cache URLs
-- Created: 2026-04-26

CREATE TABLE IF NOT EXISTS "satellite_timeseries_layers" (
  "id"           UUID        NOT NULL DEFAULT gen_random_uuid(),
  "field_id"     UUID        NOT NULL,
  "tenant_id"    VARCHAR(100) NOT NULL,
  "index_type"   VARCHAR(20)  NOT NULL,   -- NDVI, EVI, NDWI, LST, etc.
  "scene_date"   DATE         NOT NULL,   -- Sentinel-2 nominal acquisition date
  "from_ts"      TIMESTAMPTZ  NOT NULL,   -- Start of time window used for query
  "to_ts"        TIMESTAMPTZ  NOT NULL,   -- End of time window used for query
  "image_url"    TEXT,                    -- MinIO/S3 cached PNG path (null = not cached yet)
  "data_url"     TEXT,                    -- base64 data URL snapshot (for offline fallback)
  "stats"        JSONB,                   -- { min, max, mean, std, valid_pixels_pct }
  "cloud_cover"  DECIMAL(5,2),            -- Cloud cover percentage at acquisition (0-100)
  "available"    BOOLEAN      NOT NULL DEFAULT TRUE,  -- FALSE if Sentinel returned empty/cloudy
  "width_px"     SMALLINT     NOT NULL DEFAULT 512,
  "height_px"    SMALLINT     NOT NULL DEFAULT 512,
  "bbox_west"    DECIMAL(12,8),
  "bbox_south"   DECIMAL(12,8),
  "bbox_east"    DECIMAL(12,8),
  "bbox_north"   DECIMAL(12,8),
  "created_at"   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  "updated_at"   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

  CONSTRAINT "satellite_timeseries_layers_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "satellite_timeseries_field_fk"
      FOREIGN KEY ("field_id") REFERENCES "fields"("id") ON DELETE CASCADE
);

-- Idempotency: one row per (field, index, scene_date)
CREATE UNIQUE INDEX IF NOT EXISTS "uq_sat_tl_field_index_date"
  ON "satellite_timeseries_layers" ("field_id", "index_type", "scene_date");

-- Fast range queries: "give me NDVI imagery for this field in the last 30 days"
CREATE INDEX IF NOT EXISTS "idx_sat_tl_field_index_date"
  ON "satellite_timeseries_layers" ("field_id", "index_type", "scene_date" DESC);

-- Tenant-scoped queries for admin / billing
CREATE INDEX IF NOT EXISTS "idx_sat_tl_tenant"
  ON "satellite_timeseries_layers" ("tenant_id", "scene_date" DESC);

-- Change-detection queries: scan fields with new imagery since a given timestamp
CREATE INDEX IF NOT EXISTS "idx_sat_tl_created"
  ON "satellite_timeseries_layers" ("created_at" DESC);

COMMENT ON TABLE  "satellite_timeseries_layers" IS
  'Cached Sentinel-2 imagery metadata per field/index/date — one row per acquisition window. '
  'image_url points to MinIO, data_url holds the base64 PNG for offline fallback.';
