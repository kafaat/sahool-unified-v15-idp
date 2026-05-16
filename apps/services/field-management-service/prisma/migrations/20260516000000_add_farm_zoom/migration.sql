-- SAHOOL Field Management - Add zoom column to farms
-- Stores the map zoom level at the time the farm boundary was drawn.
-- drift:safe reason=additive-column-addition

ALTER TABLE "farms"
    ADD COLUMN IF NOT EXISTS "zoom" INTEGER;

COMMENT ON COLUMN "farms"."zoom" IS 'Map zoom level at the time the farm boundary was drawn';
