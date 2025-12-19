-- SAHOOL Field Core - Initial Migration
-- Database: PostgreSQL with PostGIS
-- Created: 2025

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. Enable PostGIS Extension
-- ═══════════════════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. Create Enums
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TYPE field_status AS ENUM ('active', 'fallow', 'harvested', 'preparing', 'inactive');
CREATE TYPE change_source AS ENUM ('mobile', 'web', 'api', 'system');
CREATE TYPE sync_state AS ENUM ('idle', 'syncing', 'error', 'conflict');
CREATE TYPE task_type AS ENUM ('irrigation', 'fertilization', 'spraying', 'scouting', 'maintenance', 'sampling', 'harvest', 'planting', 'other');
CREATE TYPE priority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE task_state AS ENUM ('pending', 'in_progress', 'completed', 'cancelled', 'overdue');

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. Create Fields Table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version INTEGER NOT NULL DEFAULT 1,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    crop_type VARCHAR(100) NOT NULL,
    owner_id UUID,

    -- Geospatial (PostGIS)
    boundary geometry(Polygon, 4326),
    centroid geometry(Point, 4326),

    -- Calculated Fields
    area_hectares DECIMAL(10, 4),

    -- Health & Analysis
    health_score DECIMAL(3, 2) CHECK (health_score >= 0 AND health_score <= 1),
    ndvi_value DECIMAL(4, 3) CHECK (ndvi_value >= -1 AND ndvi_value <= 1),

    -- Status & Dates
    status field_status NOT NULL DEFAULT 'active',
    planting_date DATE,
    expected_harvest DATE,

    -- Agricultural Info
    irrigation_type VARCHAR(50),
    soil_type VARCHAR(100),

    -- Flexible Metadata
    metadata JSONB,

    -- Sync Metadata
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    server_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    etag VARCHAR(64) DEFAULT uuid_generate_v4()::text,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for Fields
CREATE INDEX idx_field_tenant ON fields(tenant_id);
CREATE INDEX idx_field_sync ON fields(server_updated_at);
CREATE INDEX idx_field_status ON fields(status);
CREATE INDEX idx_field_crop ON fields(crop_type);
CREATE INDEX idx_field_boundary ON fields USING GIST(boundary);
CREATE INDEX idx_field_centroid ON fields USING GIST(centroid);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. Create Field Boundary History Table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE field_boundary_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Field Reference
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    version_at_change INTEGER NOT NULL,

    -- Boundary Snapshots (PostGIS)
    previous_boundary geometry(Polygon, 4326),
    new_boundary geometry(Polygon, 4326),

    -- Change Metrics
    area_change_hectares DECIMAL(10, 4),

    -- Change Metadata
    changed_by VARCHAR(255),
    change_reason VARCHAR(500),
    change_source change_source NOT NULL DEFAULT 'api',
    device_id VARCHAR(100),

    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for Boundary History
CREATE INDEX idx_history_field ON field_boundary_history(field_id);
CREATE INDEX idx_history_date ON field_boundary_history(created_at);

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. Create Sync Status Table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE sync_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Device Identification
    device_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,

    -- Sync State
    last_sync_at TIMESTAMPTZ,
    last_sync_version BIGINT NOT NULL DEFAULT 0,
    status sync_state NOT NULL DEFAULT 'idle',

    -- Pending Operations
    pending_uploads INTEGER NOT NULL DEFAULT 0,
    pending_downloads INTEGER NOT NULL DEFAULT 0,
    conflicts_count INTEGER NOT NULL DEFAULT 0,

    -- Error Tracking
    last_error TEXT,

    -- Device Info
    device_info JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint
    CONSTRAINT idx_sync_device_user UNIQUE (device_id, user_id)
);

-- Indexes for Sync Status
CREATE INDEX idx_sync_tenant ON sync_status(tenant_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- 6. Create Tasks Table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Task Info
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    task_type task_type NOT NULL DEFAULT 'other',
    priority priority NOT NULL DEFAULT 'medium',
    status task_state NOT NULL DEFAULT 'pending',

    -- Scheduling
    due_date TIMESTAMPTZ,
    scheduled_time VARCHAR(10),
    completed_at TIMESTAMPTZ,

    -- Assignment
    assigned_to VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,

    -- Field Reference
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,

    -- Duration
    estimated_minutes INTEGER,
    actual_minutes INTEGER,

    -- Completion Evidence
    completion_notes TEXT,
    evidence JSONB,

    -- Sync
    server_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for Tasks
CREATE INDEX idx_task_field ON tasks(field_id);
CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_due ON tasks(due_date);

-- ═══════════════════════════════════════════════════════════════════════════
-- 7. Create NDVI Readings Table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE ndvi_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Field Reference
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,

    -- NDVI Data
    value DECIMAL(4, 3) NOT NULL CHECK (value >= -1 AND value <= 1),
    captured_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'satellite',
    cloud_cover DECIMAL(5, 2) CHECK (cloud_cover >= 0 AND cloud_cover <= 100),
    quality VARCHAR(20),

    -- Satellite Info
    satellite_name VARCHAR(50),
    band_info JSONB,

    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for NDVI Readings
CREATE INDEX idx_ndvi_field_date ON ndvi_readings(field_id, captured_at);

-- ═══════════════════════════════════════════════════════════════════════════
-- 8. Create Helper Functions
-- ═══════════════════════════════════════════════════════════════════════════

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to auto-update server_updated_at for sync
CREATE OR REPLACE FUNCTION update_server_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.server_updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to auto-increment version for optimistic locking
CREATE OR REPLACE FUNCTION increment_version_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version = OLD.version + 1;
    NEW.etag = uuid_generate_v4()::text;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to auto-calculate area from boundary
CREATE OR REPLACE FUNCTION calculate_field_area()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.boundary IS NOT NULL THEN
        -- Calculate area in hectares using ST_Area with geography cast
        NEW.area_hectares = ST_Area(NEW.boundary::geography) / 10000;
        -- Calculate centroid
        NEW.centroid = ST_Centroid(NEW.boundary);
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ═══════════════════════════════════════════════════════════════════════════
-- 9. Create Triggers
-- ═══════════════════════════════════════════════════════════════════════════

-- Fields triggers
CREATE TRIGGER update_fields_updated_at
    BEFORE UPDATE ON fields
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fields_server_updated_at
    BEFORE UPDATE ON fields
    FOR EACH ROW
    EXECUTE FUNCTION update_server_updated_at_column();

CREATE TRIGGER increment_fields_version
    BEFORE UPDATE ON fields
    FOR EACH ROW
    EXECUTE FUNCTION increment_version_column();

CREATE TRIGGER calculate_fields_area
    BEFORE INSERT OR UPDATE OF boundary ON fields
    FOR EACH ROW
    EXECUTE FUNCTION calculate_field_area();

-- Sync Status triggers
CREATE TRIGGER update_sync_status_updated_at
    BEFORE UPDATE ON sync_status
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Tasks triggers
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_server_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_server_updated_at_column();

-- ═══════════════════════════════════════════════════════════════════════════
-- 10. Create Views for Common Queries
-- ═══════════════════════════════════════════════════════════════════════════

-- View for fields with GeoJSON boundary
CREATE VIEW fields_geojson AS
SELECT
    id,
    version,
    name,
    tenant_id,
    crop_type,
    owner_id,
    ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,
    ST_AsGeoJSON(centroid)::jsonb as centroid_geojson,
    area_hectares,
    health_score,
    ndvi_value,
    status,
    planting_date,
    expected_harvest,
    irrigation_type,
    soil_type,
    metadata,
    is_deleted,
    server_updated_at,
    etag,
    created_at,
    updated_at
FROM fields
WHERE is_deleted = FALSE;

-- View for field health summary by tenant
CREATE VIEW tenant_field_health AS
SELECT
    tenant_id,
    COUNT(*) as total_fields,
    SUM(area_hectares) as total_area_hectares,
    AVG(ndvi_value) as avg_ndvi,
    AVG(health_score) as avg_health_score,
    COUNT(*) FILTER (WHERE status = 'active') as active_fields,
    COUNT(*) FILTER (WHERE ndvi_value < 0.3) as low_health_fields
FROM fields
WHERE is_deleted = FALSE
GROUP BY tenant_id;

-- ═══════════════════════════════════════════════════════════════════════════
-- 11. Grant Permissions (adjust as needed)
-- ═══════════════════════════════════════════════════════════════════════════

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sahool;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sahool;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO sahool;

COMMENT ON TABLE fields IS 'Agricultural fields with geospatial boundaries (PostGIS Polygon)';
COMMENT ON TABLE field_boundary_history IS 'Audit trail for field boundary changes';
COMMENT ON TABLE sync_status IS 'Mobile device synchronization status tracking';
COMMENT ON TABLE tasks IS 'Agricultural tasks linked to fields';
COMMENT ON TABLE ndvi_readings IS 'Historical NDVI values for vegetation health analysis';
