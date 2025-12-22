-- ============================================================================
-- SAHOOL PostGIS Performance Optimization Migration
-- Date: 2024-12-22
-- Purpose: Create indexes, partitions, and materialized views for performance
-- ============================================================================

-- Step 1: Enable required extensions
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Step 2: Create GIST Indexes for spatial queries
-- ============================================================================
-- Note: CONCURRENTLY allows queries to continue during index creation

-- Main fields geometry index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_geom_gist
ON fields USING GIST(geom);

-- Centroid index for point-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_centroid_gist
ON fields USING GIST(ST_Centroid(geom));

-- Geography index for distance queries (uses meters, not degrees)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_geog_gist
ON fields USING GIST(geom::geography);

-- Compound index for common query patterns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_user_geom
ON fields USING GIST(geom)
WHERE deleted_at IS NULL;

-- BRIN index for time-series data (very space efficient)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_readings_timestamp_brin
ON ndvi_readings USING BRIN(timestamp)
WITH (pages_per_range = 128);

-- Step 3: Table Partitioning for NDVI readings (time-series data)
-- ============================================================================
-- Create partitioned table structure

-- First, rename existing table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ndvi_readings' AND table_type = 'BASE TABLE') THEN
        ALTER TABLE ndvi_readings RENAME TO ndvi_readings_old;
    END IF;
END $$;

-- Create new partitioned table
CREATE TABLE IF NOT EXISTS ndvi_readings (
    id SERIAL,
    field_id INTEGER NOT NULL,
    value DECIMAL(5,4),
    quality_score DECIMAL(3,2),
    cloud_cover DECIMAL(5,2),
    source VARCHAR(50) DEFAULT 'sentinel2',
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create partitions for each month (2024-2025)
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_01 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_02 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_03 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_04 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_05 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_06 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_07 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_08 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_09 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_10 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_11 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2024_12 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- 2025 partitions
CREATE TABLE IF NOT EXISTS ndvi_readings_2025_01 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2025_02 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2025_03 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2025_q2 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2025_q3 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE IF NOT EXISTS ndvi_readings_2025_q4 PARTITION OF ndvi_readings
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

-- Create indexes on partitions
CREATE INDEX IF NOT EXISTS idx_ndvi_field_id ON ndvi_readings(field_id);

-- Step 4: Materialized Views for analytics (pre-computed aggregations)
-- ============================================================================

-- Daily field summary view
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_field_summary AS
SELECT
    f.id as field_id,
    f.name as field_name,
    f.user_id,
    DATE(r.timestamp) as reading_date,
    COUNT(r.id) as reading_count,
    AVG(r.value) as avg_ndvi,
    MIN(r.value) as min_ndvi,
    MAX(r.value) as max_ndvi,
    AVG(r.quality_score) as avg_quality,
    AVG(r.cloud_cover) as avg_cloud_cover
FROM fields f
LEFT JOIN ndvi_readings r ON f.id = r.field_id
WHERE r.timestamp > NOW() - INTERVAL '90 days'
GROUP BY f.id, f.name, f.user_id, DATE(r.timestamp)
WITH DATA;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_field_summary_pk
ON mv_daily_field_summary(field_id, reading_date);

CREATE INDEX IF NOT EXISTS idx_mv_daily_field_summary_user
ON mv_daily_field_summary(user_id, reading_date);

-- Weekly crop health summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_weekly_crop_health AS
SELECT
    f.id as field_id,
    f.crop_type,
    DATE_TRUNC('week', r.timestamp) as week_start,
    AVG(r.value) as avg_ndvi,
    STDDEV(r.value) as ndvi_stddev,
    CASE
        WHEN AVG(r.value) >= 0.6 THEN 'healthy'
        WHEN AVG(r.value) >= 0.4 THEN 'moderate'
        WHEN AVG(r.value) >= 0.2 THEN 'stressed'
        ELSE 'critical'
    END as health_status
FROM fields f
JOIN ndvi_readings r ON f.id = r.field_id
WHERE r.timestamp > NOW() - INTERVAL '1 year'
GROUP BY f.id, f.crop_type, DATE_TRUNC('week', r.timestamp)
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_weekly_crop_health_pk
ON mv_weekly_crop_health(field_id, week_start);

-- Step 5: Refresh functions for materialized views
-- ============================================================================

-- Function to refresh daily summary
CREATE OR REPLACE FUNCTION refresh_daily_field_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_field_summary;
    RAISE NOTICE 'Daily field summary refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to refresh weekly health
CREATE OR REPLACE FUNCTION refresh_weekly_crop_health()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_crop_health;
    RAISE NOTICE 'Weekly crop health refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- Step 6: Schedule refresh jobs (using pg_cron)
-- ============================================================================

-- Refresh daily summary every hour
SELECT cron.schedule('refresh-daily-summary', '0 * * * *', 'SELECT refresh_daily_field_summary()');

-- Refresh weekly health every 6 hours
SELECT cron.schedule('refresh-weekly-health', '0 */6 * * *', 'SELECT refresh_weekly_crop_health()');

-- Step 7: Optimized query examples
-- ============================================================================

-- Example 1: Get fields within 5km (fast with geography index)
-- EXPLAIN ANALYZE
-- SELECT id, name, ST_AsGeoJSON(geom) as geojson
-- FROM fields
-- WHERE ST_DWithin(
--     geom::geography,
--     ST_MakePoint(46.7, 24.7)::geography,
--     5000  -- 5km in meters
-- );

-- Example 2: Get NDVI trend (instant from materialized view)
-- SELECT reading_date, avg_ndvi, reading_count
-- FROM mv_daily_field_summary
-- WHERE field_id = 123
-- ORDER BY reading_date DESC
-- LIMIT 30;

-- Example 3: Get fields with health issues this week
-- SELECT field_id, crop_type, avg_ndvi, health_status
-- FROM mv_weekly_crop_health
-- WHERE week_start = DATE_TRUNC('week', NOW())
--   AND health_status IN ('stressed', 'critical')
-- ORDER BY avg_ndvi ASC;

-- Step 8: Statistics and maintenance
-- ============================================================================

-- Update statistics for query planner
ANALYZE fields;
ANALYZE ndvi_readings;
ANALYZE mv_daily_field_summary;
ANALYZE mv_weekly_crop_health;

-- ============================================================================
-- Post-migration verification queries
-- ============================================================================

-- Verify indexes exist
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_indexes
WHERE tablename IN ('fields', 'ndvi_readings')
ORDER BY tablename, indexname;

-- Verify materialized views
SELECT
    schemaname,
    matviewname,
    pg_size_pretty(pg_total_relation_size(matviewname::regclass)) as total_size
FROM pg_matviews
WHERE schemaname = 'public';

-- Check partition info
SELECT
    parent.relname AS parent_table,
    child.relname AS partition_name,
    pg_size_pretty(pg_relation_size(child.oid)) as size
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'ndvi_readings'
ORDER BY child.relname;
