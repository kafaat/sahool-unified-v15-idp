-- Migration: Add center_lat and center_lng to farms table
-- These columns store the pre-computed map center so the field form
-- can fly directly to the farm location without deriving it at runtime.

ALTER TABLE "farms"
  ADD COLUMN IF NOT EXISTS "center_lat" DECIMAL(12, 8),
  ADD COLUMN IF NOT EXISTS "center_lng" DECIMAL(12, 8);
