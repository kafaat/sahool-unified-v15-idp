# PostGIS Performance Optimization

## تحسين أداء PostGIS

**Version:** 15.5.0
**Last Updated:** 2024-12-22

---

## Overview | نظرة عامة

This document describes the PostGIS optimization strategy for SAHOOL, including:

- **GIST indexes** for spatial queries
- **Table partitioning** for time-series data
- **Materialized views** for analytics
- **Query optimization** patterns

---

## Performance Targets | أهداف الأداء

| Metric                     | Before | After | Improvement |
| -------------------------- | ------ | ----- | ----------- |
| Spatial query (5km radius) | 800ms  | 20ms  | **97.5%**   |
| NDVI trend query           | 1200ms | 5ms   | **99.6%**   |
| Daily analytics            | 3000ms | 50ms  | **98.3%**   |
| Memory usage               | 8GB    | 2GB   | **75%**     |

---

## Index Strategy | استراتيجية الفهارس

### GIST Indexes (Spatial)

```sql
-- Main geometry index
CREATE INDEX CONCURRENTLY idx_fields_geom_gist
ON fields USING GIST(geom);

-- Centroid for point queries
CREATE INDEX CONCURRENTLY idx_fields_centroid_gist
ON fields USING GIST(ST_Centroid(geom));

-- Geography for distance queries (meters)
CREATE INDEX CONCURRENTLY idx_fields_geog_gist
ON fields USING GIST(geom::geography);
```

### BRIN Indexes (Time-Series)

```sql
-- Efficient for large time-series tables
CREATE INDEX CONCURRENTLY idx_ndvi_readings_timestamp_brin
ON ndvi_readings USING BRIN(timestamp)
WITH (pages_per_range = 128);
```

### When to Use

| Index Type | Use Case                                         | Storage    |
| ---------- | ------------------------------------------------ | ---------- |
| GIST       | Spatial queries (contains, intersects, distance) | Medium     |
| BRIN       | Time-series with natural ordering                | Very small |
| B-tree     | Exact matches, range queries                     | Medium     |
| GIN        | Full-text search, JSONB                          | Large      |

---

## Table Partitioning | تقسيم الجداول

### NDVI Readings (By Month)

```sql
CREATE TABLE ndvi_readings (
    id SERIAL,
    field_id INTEGER NOT NULL,
    value DECIMAL(5,4),
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Monthly partitions
CREATE TABLE ndvi_readings_2024_01
PARTITION OF ndvi_readings
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### Benefits

- **Query performance**: Only scans relevant partitions
- **Maintenance**: Easy to drop old partitions
- **Parallel queries**: Can scan partitions in parallel
- **Vacuum efficiency**: Per-partition vacuum

### Partition Management

```sql
-- Create new partition (run monthly)
CREATE TABLE ndvi_readings_2025_02
PARTITION OF ndvi_readings
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Drop old partition (data retention)
DROP TABLE ndvi_readings_2023_01;

-- Detach without dropping (for archiving)
ALTER TABLE ndvi_readings
DETACH PARTITION ndvi_readings_2023_01;
```

---

## Materialized Views | العروض المحققة

### Daily Field Summary

```sql
CREATE MATERIALIZED VIEW mv_daily_field_summary AS
SELECT
    f.id as field_id,
    f.name as field_name,
    DATE(r.timestamp) as reading_date,
    AVG(r.value) as avg_ndvi,
    MIN(r.value) as min_ndvi,
    MAX(r.value) as max_ndvi
FROM fields f
LEFT JOIN ndvi_readings r ON f.id = r.field_id
WHERE r.timestamp > NOW() - INTERVAL '90 days'
GROUP BY f.id, f.name, DATE(r.timestamp)
WITH DATA;

-- Create unique index for CONCURRENTLY refresh
CREATE UNIQUE INDEX idx_mv_daily_pk
ON mv_daily_field_summary(field_id, reading_date);
```

### Weekly Crop Health

```sql
CREATE MATERIALIZED VIEW mv_weekly_crop_health AS
SELECT
    f.id as field_id,
    f.crop_type,
    DATE_TRUNC('week', r.timestamp) as week_start,
    AVG(r.value) as avg_ndvi,
    CASE
        WHEN AVG(r.value) >= 0.6 THEN 'healthy'
        WHEN AVG(r.value) >= 0.4 THEN 'moderate'
        WHEN AVG(r.value) >= 0.2 THEN 'stressed'
        ELSE 'critical'
    END as health_status
FROM fields f
JOIN ndvi_readings r ON f.id = r.field_id
GROUP BY f.id, f.crop_type, DATE_TRUNC('week', r.timestamp)
WITH DATA;
```

### Scheduled Refresh (pg_cron)

```sql
-- Refresh daily summary every hour
SELECT cron.schedule(
    'refresh-daily-summary',
    '0 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_field_summary'
);

-- Refresh weekly health every 6 hours
SELECT cron.schedule(
    'refresh-weekly-health',
    '0 */6 * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_crop_health'
);
```

---

## Query Patterns | أنماط الاستعلامات

### Fast Spatial Query (Using Geography Index)

```sql
-- Find fields within 5km (uses geography index)
SELECT id, name, ST_AsGeoJSON(geom) as geojson
FROM fields
WHERE ST_DWithin(
    geom::geography,
    ST_MakePoint(46.7, 24.7)::geography,
    5000  -- meters
);
```

### NDVI Trend (From Materialized View)

```sql
-- Instant response from pre-computed view
SELECT reading_date, avg_ndvi
FROM mv_daily_field_summary
WHERE field_id = 123
ORDER BY reading_date DESC
LIMIT 30;
```

### Fields Needing Attention

```sql
-- From weekly health view
SELECT field_id, crop_type, avg_ndvi, health_status
FROM mv_weekly_crop_health
WHERE week_start = DATE_TRUNC('week', NOW())
  AND health_status IN ('stressed', 'critical')
ORDER BY avg_ndvi ASC;
```

---

## Query Anti-Patterns | أنماط يجب تجنبها

### Bad: Geometry Cast in WHERE

```sql
-- SLOW: casts to geometry, can't use geography index
SELECT * FROM fields
WHERE ST_DWithin(geom::geometry, point::geometry, 0.05);
```

### Good: Use Geography

```sql
-- FAST: uses geography index
SELECT * FROM fields
WHERE ST_DWithin(geom::geography, point::geography, 5000);
```

### Bad: SELECT \*

```sql
-- SLOW: fetches all columns including large geometry
SELECT * FROM fields WHERE user_id = 123;
```

### Good: Select Needed Columns

```sql
-- FAST: only fetches needed data
SELECT id, name, area_hectares FROM fields WHERE user_id = 123;
```

---

## Monitoring | المراقبة

### Check Index Usage

```sql
SELECT
    schemaname,
    relname as table,
    indexrelname as index,
    idx_scan as scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Check Slow Queries

```sql
SELECT
    query,
    calls,
    mean_time::numeric(10,2) as avg_ms,
    total_time::numeric(10,2) as total_ms
FROM pg_stat_statements
WHERE mean_time > 100  -- > 100ms
ORDER BY mean_time DESC
LIMIT 20;
```

### Check Partition Sizes

```sql
SELECT
    child.relname AS partition,
    pg_size_pretty(pg_relation_size(child.oid)) as size
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'ndvi_readings'
ORDER BY child.relname;
```

---

## Migration | الترحيل

### Running the Migration

```bash
# Connect to database
psql -h localhost -U sahool_admin -d sahool_db

# Run migration
\i migrations/20241222_postgis_optimization.sql

# Verify indexes
\di+ idx_fields_*
```

### Rollback (if needed)

```sql
-- Drop indexes
DROP INDEX IF EXISTS idx_fields_geom_gist;
DROP INDEX IF EXISTS idx_fields_centroid_gist;
DROP INDEX IF EXISTS idx_fields_geog_gist;

-- Drop materialized views
DROP MATERIALIZED VIEW IF EXISTS mv_daily_field_summary;
DROP MATERIALIZED VIEW IF EXISTS mv_weekly_crop_health;
```

---

## Maintenance | الصيانة

### Daily Tasks (Automated)

- Materialized view refresh (pg_cron)
- Partition check

### Weekly Tasks

```sql
-- Update statistics
ANALYZE fields;
ANALYZE ndvi_readings;
ANALYZE mv_daily_field_summary;

-- Check for bloat
SELECT * FROM pgstattuple('fields');
```

### Monthly Tasks

- Create new partitions for next month
- Archive/drop old partitions (>1 year)
- Review slow query log

---

**Related Documents:**

- [Engineering Recovery Plan](../engineering/ENGINEERING_RECOVERY_PLAN.md)
- [Database Architecture](../architecture/DATABASE.md)
