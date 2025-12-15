-- ============================================
-- SAHOOL Platform - Performance Indexes
-- Additional indexes for query optimization
-- ============================================

-- ============================================
-- COMPOSITE INDEXES for common query patterns
-- ============================================

-- Fields: tenant + status (frequent filter combination)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_tenant_status
    ON fields(tenant_id, status)
    WHERE is_active = true;

-- Fields: tenant + crop for dashboard queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_tenant_crop
    ON fields(tenant_id, current_crop_id)
    WHERE is_active = true;

-- Users: tenant + role + active (for permissions queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_tenant_role_active
    ON users(tenant_id, role)
    WHERE is_active = true;

-- Tasks: assigned user + status (worker dashboard)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_assigned_status
    ON tasks(assigned_to, status)
    WHERE status NOT IN ('completed', 'cancelled');

-- Tasks: tenant + field + status (field task list)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_tenant_field_status
    ON tasks(tenant_id, field_id, status);

-- Tasks: due date for overdue queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_overdue
    ON tasks(due_date, status)
    WHERE status NOT IN ('completed', 'cancelled') AND due_date IS NOT NULL;

-- ============================================
-- COVERING INDEXES (include columns for index-only scans)
-- ============================================

-- Fields list with common columns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_list_covering
    ON fields(tenant_id, status, created_at DESC)
    INCLUDE (name, name_ar, current_crop_id, area_hectares);

-- NDVI latest readings (commonly accessed together)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_latest_covering
    ON ndvi_records(field_id, capture_date DESC)
    INCLUDE (ndvi_mean, classification, health_score);

-- Tasks list covering index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_list_covering
    ON tasks(tenant_id, scheduled_date, status)
    INCLUDE (title, title_ar, type, priority, assigned_to);

-- ============================================
-- PARTIAL INDEXES for filtered queries
-- ============================================

-- Active fields only (most queries filter on is_active)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_active
    ON fields(tenant_id, name)
    WHERE is_active = true;

-- Pending/in-progress tasks (dashboard queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_pending
    ON tasks(tenant_id, scheduled_date)
    WHERE status IN ('pending', 'assigned', 'in_progress');

-- Critical/high priority tasks
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_high_priority
    ON tasks(tenant_id, due_date)
    WHERE priority IN ('high', 'critical') AND status NOT IN ('completed', 'cancelled');

-- Active alerts
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_active_only
    ON alerts(tenant_id, severity, created_at DESC)
    WHERE status = 'active';

-- Unacknowledged alerts (for notification badge)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_unacknowledged
    ON alerts(tenant_id, created_at DESC)
    WHERE status = 'active' AND acknowledged_at IS NULL;

-- Active IoT devices
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_devices_active
    ON iot_devices(tenant_id, device_type)
    WHERE status = 'active';

-- ============================================
-- BRIN INDEXES for time-series data
-- ============================================

-- IoT readings time-series (efficient for large tables with sequential inserts)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_readings_brin
    ON iot_readings USING BRIN(recorded_at)
    WITH (pages_per_range = 128);

-- Weather records time-series
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_weather_records_brin
    ON weather_records USING BRIN(recorded_at)
    WITH (pages_per_range = 128);

-- Audit logs time-series
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_brin
    ON audit_logs USING BRIN(created_at)
    WITH (pages_per_range = 128);

-- ============================================
-- GIN INDEXES for JSONB queries
-- ============================================

-- Field settings/metadata queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenants_settings_gin
    ON tenants USING GIN(settings);

-- User settings queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_settings_gin
    ON users USING GIN(settings);

-- IoT device config queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_devices_config_gin
    ON iot_devices USING GIN(config);

-- IoT readings for specific metrics
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_readings_data_gin
    ON iot_readings USING GIN(readings);

-- NDVI zones queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_zones_gin
    ON ndvi_records USING GIN(zones);

-- ============================================
-- EXPRESSION INDEXES
-- ============================================

-- Lower case email search (case-insensitive)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_lower
    ON users(LOWER(email));

-- Date extraction for grouping queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_year_month
    ON tasks(tenant_id, DATE_TRUNC('month', scheduled_date));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_year_month
    ON ndvi_records(field_id, DATE_TRUNC('month', capture_date));

-- ============================================
-- SYNC SUPPORT INDEXES (for mobile offline sync)
-- ============================================

-- Fields updated since (sync delta queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_sync
    ON fields(tenant_id, updated_at)
    WHERE is_active = true;

-- Tasks updated since (sync delta queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_sync
    ON tasks(tenant_id, updated_at);

-- NDVI records updated since
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_sync
    ON ndvi_records(tenant_id, created_at);

-- ============================================
-- UNIQUE CONSTRAINTS (also serve as indexes)
-- ============================================

-- Prevent duplicate NDVI records for same field/date
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_field_date_unique
    ON ndvi_records(field_id, capture_date, satellite);

-- Prevent duplicate weather records
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_weather_location_time_unique
    ON weather_records(location_id, recorded_at);

-- ============================================
-- STATISTICS for query planner
-- ============================================

-- Increase statistics target for frequently queried columns
ALTER TABLE fields ALTER COLUMN status SET STATISTICS 200;
ALTER TABLE fields ALTER COLUMN tenant_id SET STATISTICS 200;
ALTER TABLE tasks ALTER COLUMN status SET STATISTICS 200;
ALTER TABLE tasks ALTER COLUMN tenant_id SET STATISTICS 200;
ALTER TABLE tasks ALTER COLUMN assigned_to SET STATISTICS 200;
ALTER TABLE ndvi_records ALTER COLUMN field_id SET STATISTICS 200;
ALTER TABLE ndvi_records ALTER COLUMN classification SET STATISTICS 200;

-- ============================================
-- ANALYZE tables to update statistics
-- ============================================

ANALYZE tenants;
ANALYZE users;
ANALYZE fields;
ANALYZE field_crops;
ANALYZE crops;
ANALYZE ndvi_records;
ANALYZE weather_records;
ANALYZE tasks;
ANALYZE alerts;
ANALYZE iot_devices;
ANALYZE iot_readings;
ANALYZE audit_logs;
ANALYZE anwa_events;

-- ============================================
-- COMMENTS for documentation
-- ============================================

COMMENT ON INDEX idx_fields_tenant_status IS 'Composite index for filtering active fields by tenant and status';
COMMENT ON INDEX idx_tasks_overdue IS 'Partial index for finding overdue tasks efficiently';
COMMENT ON INDEX idx_iot_readings_brin IS 'BRIN index for time-series IoT data - efficient for range queries';
COMMENT ON INDEX idx_fields_sync IS 'Index supporting mobile app sync delta queries';
