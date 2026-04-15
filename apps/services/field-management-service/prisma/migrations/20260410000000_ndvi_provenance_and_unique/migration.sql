-- ─────────────────────────────────────────────────────────────────────────────
-- NDVI provenance, provider lineage, idempotency guard, and soft-delete flag
-- Satellite flow audit fixes: H12 (no provenance) + H17 (duplicate imports)
-- ─────────────────────────────────────────────────────────────────────────────
-- drift:safe reason=ndvi-provenance-additive-and-commented-dedup-snippet
--
-- Adds:
--   * provider           : which upstream client produced the reading
--                          (e.g. 'sentinel_hub_s2l2a', 'planet_labs',
--                          'copernicus_stac', 'simulated')
--   * scene_id           : provider's scene / tile / order identifier
--                          (used for re-fetch + audit)
--   * request_id         : correlation id of the HTTP request that
--                          produced the reading
--   * is_deleted         : soft-delete flag mirroring Field.is_deleted
--
-- Indexes & constraints:
--   * idx_ndvi_provider_scene : fast reverse lookup by provider+scene
--   * uq_ndvi_field_source_date : idempotent upsert key; replaying the same
--                                 scene into the same field MUST NOT create
--                                 duplicate rows. Uses
--                                 (field_id, captured_at, satellite_name)
--                                 because (provider, scene_id) is nullable
--                                 and older rows pre-fix may not have them.
--
-- Backfill strategy:
--   * No backfill is required for provider/scene_id/request_id — existing
--     rows keep NULL and new writes populate them going forward.
--   * is_deleted defaults to FALSE so existing rows are unaffected.
--   * The unique constraint is added as a DEFERRABLE INITIALLY IMMEDIATE
--     b-tree index to surface duplicates at INSERT time, not at commit.
--     If duplicates already exist in production, the CREATE UNIQUE INDEX
--     will fail and operators should run the dedup CTE below first.

ALTER TABLE "ndvi_readings"
  ADD COLUMN IF NOT EXISTS "provider"    VARCHAR(64),
  ADD COLUMN IF NOT EXISTS "scene_id"    VARCHAR(255),
  ADD COLUMN IF NOT EXISTS "request_id"  UUID,
  ADD COLUMN IF NOT EXISTS "is_deleted"  BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS "idx_ndvi_provider_scene"
  ON "ndvi_readings" ("provider", "scene_id");

-- Idempotent import guard (H17). This matches the Prisma model's
-- `@@unique([fieldId, capturedAt, satelliteName])`. We use a NULLS NOT
-- DISTINCT index so two rows with a NULL `satellite_name` still conflict.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_ndvi_field_source_date"
  ON "ndvi_readings" ("field_id", "captured_at", "satellite_name")
  NULLS NOT DISTINCT;

-- ─────────────────────────────────────────────────────────────────────────────
-- Dedup CTE (OPERATORS: run manually BEFORE applying this migration if
-- CREATE UNIQUE INDEX fails because duplicates already exist).
-- ─────────────────────────────────────────────────────────────────────────────
--
--   WITH ranked AS (
--     SELECT id,
--            ROW_NUMBER() OVER (
--              PARTITION BY field_id, captured_at, satellite_name
--              ORDER BY created_at DESC, id
--            ) AS rn
--     FROM ndvi_readings
--   )
--   DELETE FROM ndvi_readings
--   WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
