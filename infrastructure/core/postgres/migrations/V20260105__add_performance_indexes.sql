-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Performance Optimization Migration
-- تحسينات الأداء
-- Version: V20260105
-- Description: Add missing indexes for performance optimization
-- Based on: GAPS_AND_RECOMMENDATIONS.md - Phase 1 (High Priority)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- 1. Single Column Indexes (High Priority)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Add index on fields.current_crop_id
-- Improves query performance when filtering or joining on current_crop
-- Partial index: Only index non-null values to save space
CREATE INDEX IF NOT EXISTS idx_fields_current_crop 
ON geo.fields(current_crop_id) 
WHERE current_crop_id IS NOT NULL;

COMMENT ON INDEX idx_fields_current_crop IS 'Performance index for fields by current crop (non-null only)';

-- ═══════════════════════════════════════════════════════════════════════════════
-- 2. GIN Indexes for JSONB Columns (Medium Priority)
-- ═══════════════════════════════════════════════════════════════════════════════
-- GIN indexes improve query performance on JSONB columns
-- Useful for queries like: WHERE metadata @> '{"key": "value"}'
-- ═══════════════════════════════════════════════════════════════════════════════

-- Tenants metadata
CREATE INDEX IF NOT EXISTS idx_tenants_metadata_gin 
ON tenants.tenants USING GIN (settings);

COMMENT ON INDEX idx_tenants_metadata_gin IS 'GIN index for JSONB settings queries';

-- Users metadata (if metadata column exists in users table)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'users' 
        AND table_name = 'users' 
        AND column_name = 'metadata'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_users_metadata_gin 
        ON users.users USING GIN (metadata);
    END IF;
END $$;

-- Fields metadata
CREATE INDEX IF NOT EXISTS idx_fields_metadata_gin 
ON geo.fields USING GIN (metadata);

COMMENT ON INDEX idx_fields_metadata_gin IS 'GIN index for fields metadata JSONB queries';

-- Crops metadata (if crops table and metadata column exist)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'crops'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'crops' 
        AND column_name = 'metadata'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_crops_metadata_gin 
        ON crops USING GIN (metadata);
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- 3. Log Migration Completion
-- ═══════════════════════════════════════════════════════════════════════════════

DO $$
BEGIN
    -- Record migration if _migrations table exists
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = '_migrations'
    ) THEN
        INSERT INTO public._migrations (name, applied_at) 
        VALUES ('V20260105__add_performance_indexes', CURRENT_TIMESTAMP)
        ON CONFLICT (name) DO NOTHING;
    END IF;
    
    RAISE NOTICE '✅ Migration V20260105__add_performance_indexes completed successfully';
    RAISE NOTICE '   - Added index on fields.current_crop_id';
    RAISE NOTICE '   - Added GIN indexes for JSONB metadata columns';
END $$;
