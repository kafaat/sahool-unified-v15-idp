-- SAHOOL Field Management - Add bbox column to farms
-- Stores the geographic bounding box [minLng, minLat, maxLng, maxLat]
-- selected by the user on the farm creation/edit map.
-- drift:safe reason=additive-column-addition

ALTER TABLE "farms"
    ADD COLUMN IF NOT EXISTS "bbox" JSONB;

COMMENT ON COLUMN "farms"."bbox" IS 'Geographic bounding box [minLng, minLat, maxLng, maxLat] from map selection';
