-- ============================================
-- SAHOOL Platform - Database Schema
-- PostgreSQL with PostGIS Extension
-- ============================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================
-- TENANTS (Multi-tenancy)
-- ============================================

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, basic, pro, enterprise
    subscription_status VARCHAR(50) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    logo_url VARCHAR(500),
    max_users INTEGER DEFAULT 5,
    max_fields INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tenants_slug ON tenants(slug);

-- ============================================
-- USERS
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    full_name_ar VARCHAR(255),
    phone VARCHAR(50),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer', -- owner, manager, worker, viewer, admin
    avatar_url VARCHAR(500),
    language VARCHAR(10) DEFAULT 'ar',
    timezone VARCHAR(50) DEFAULT 'Asia/Aden',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    phone_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    fcm_token VARCHAR(500),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- FIELDS (Agricultural Plots)
-- ============================================

CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description TEXT,
    
    -- Location (PostGIS)
    location GEOMETRY(POLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    area_hectares DECIMAL(10, 4),
    elevation_meters INTEGER,
    
    -- Address
    governorate VARCHAR(100), -- محافظة
    district VARCHAR(100),    -- مديرية
    village VARCHAR(100),     -- قرية
    
    -- Soil & Terrain
    soil_type VARCHAR(100),
    soil_ph DECIMAL(3, 1),
    terrain_type VARCHAR(50), -- flat, terraced, sloped
    irrigation_type VARCHAR(50), -- drip, sprinkler, flood, rain-fed
    
    -- Current Status
    current_crop_id UUID,
    status VARCHAR(50) DEFAULT 'active', -- active, fallow, preparing
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fields_tenant ON fields(tenant_id);
CREATE INDEX idx_fields_location ON fields USING GIST(location);
CREATE INDEX idx_fields_center ON fields USING GIST(center_point);
CREATE INDEX idx_fields_status ON fields(status);

-- ============================================
-- CROPS
-- ============================================

CREATE TABLE crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255),
    category VARCHAR(100), -- vegetables, fruits, grains, legumes, etc.
    
    -- Growing Requirements
    min_temp_celsius INTEGER,
    max_temp_celsius INTEGER,
    water_needs VARCHAR(50), -- low, medium, high
    soil_types TEXT[], -- array of suitable soil types
    growth_duration_days INTEGER,
    
    -- Yemeni Context
    traditional_name VARCHAR(255),
    suitable_anwa TEXT[], -- suitable naw periods
    common_in_regions TEXT[],
    
    -- Metadata
    icon_url VARCHAR(500),
    description TEXT,
    description_ar TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_crops_category ON crops(category);
CREATE INDEX idx_crops_name ON crops USING GIN(name_ar gin_trgm_ops);

-- ============================================
-- FIELD CROPS (Planting Records)
-- ============================================

CREATE TABLE field_crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    crop_id UUID NOT NULL REFERENCES crops(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Timeline
    planting_date DATE NOT NULL,
    expected_harvest_date DATE,
    actual_harvest_date DATE,
    
    -- Area
    planted_area_hectares DECIMAL(10, 4),
    
    -- Status
    status VARCHAR(50) DEFAULT 'planted', -- planned, planted, growing, harvesting, harvested, failed
    growth_stage VARCHAR(50),
    
    -- Yield
    expected_yield_kg DECIMAL(12, 2),
    actual_yield_kg DECIMAL(12, 2),
    yield_quality VARCHAR(50), -- excellent, good, average, poor
    
    -- Costs & Revenue
    total_cost DECIMAL(12, 2),
    total_revenue DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'YER',
    
    -- Notes
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_field_crops_field ON field_crops(field_id);
CREATE INDEX idx_field_crops_tenant ON field_crops(tenant_id);
CREATE INDEX idx_field_crops_status ON field_crops(status);
CREATE INDEX idx_field_crops_dates ON field_crops(planting_date, expected_harvest_date);

-- ============================================
-- NDVI RECORDS (Satellite Imagery)
-- ============================================

CREATE TABLE ndvi_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Capture Info
    capture_date DATE NOT NULL,
    satellite VARCHAR(50), -- Sentinel-2, Landsat-8
    cloud_coverage_percent DECIMAL(5, 2),
    
    -- NDVI Values
    ndvi_mean DECIMAL(4, 3),
    ndvi_min DECIMAL(4, 3),
    ndvi_max DECIMAL(4, 3),
    ndvi_std_dev DECIMAL(4, 3),
    
    -- Classification
    classification VARCHAR(50), -- excellent, good, moderate, poor, bare
    health_score INTEGER, -- 0-100
    
    -- Change Detection
    change_from_previous DECIMAL(4, 3),
    trend VARCHAR(20), -- improving, stable, declining
    
    -- Storage
    raw_image_url VARCHAR(500),
    processed_image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    
    -- Zones (for large fields)
    zones JSONB, -- [{zone_id, ndvi, area, recommendation}]
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ndvi_field ON ndvi_records(field_id);
CREATE INDEX idx_ndvi_tenant ON ndvi_records(tenant_id);
CREATE INDEX idx_ndvi_date ON ndvi_records(capture_date DESC);
CREATE INDEX idx_ndvi_classification ON ndvi_records(classification);

-- ============================================
-- WEATHER RECORDS
-- ============================================

CREATE TABLE weather_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    location_id VARCHAR(100) NOT NULL,
    
    -- Location
    coordinates GEOMETRY(POINT, 4326),
    location_name VARCHAR(255),
    
    -- Timestamp
    recorded_at TIMESTAMP NOT NULL,
    
    -- Current Conditions
    temperature_celsius DECIMAL(4, 1),
    feels_like_celsius DECIMAL(4, 1),
    humidity_percent INTEGER,
    pressure_hpa INTEGER,
    
    -- Wind
    wind_speed_ms DECIMAL(5, 2),
    wind_direction_degrees INTEGER,
    wind_gust_ms DECIMAL(5, 2),
    
    -- Precipitation
    precipitation_mm DECIMAL(6, 2),
    precipitation_probability INTEGER,
    
    -- Conditions
    conditions VARCHAR(100),
    conditions_ar VARCHAR(100),
    icon_code VARCHAR(20),
    
    -- UV & Visibility
    uv_index DECIMAL(3, 1),
    visibility_km DECIMAL(5, 2),
    
    -- Source
    source VARCHAR(50), -- openweathermap, local_station
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_weather_location ON weather_records(location_id);
CREATE INDEX idx_weather_tenant ON weather_records(tenant_id);
CREATE INDEX idx_weather_time ON weather_records(recorded_at DESC);
CREATE INDEX idx_weather_geo ON weather_records USING GIST(coordinates);

-- ============================================
-- TASKS
-- ============================================

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    field_crop_id UUID REFERENCES field_crops(id) ON DELETE SET NULL,
    
    -- Task Info
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    
    -- Type & Category
    type VARCHAR(50) NOT NULL, -- irrigation, fertilizing, spraying, harvesting, planting, maintenance
    category VARCHAR(50),
    
    -- Assignment
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Schedule
    scheduled_date DATE,
    scheduled_time TIME,
    due_date TIMESTAMP,
    estimated_duration_minutes INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, assigned, in_progress, completed, cancelled, overdue
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    
    -- Completion
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    completion_notes TEXT,
    completion_photos TEXT[], -- array of URLs
    
    -- AI Generated
    is_ai_generated BOOLEAN DEFAULT false,
    source_event_id VARCHAR(100),
    source_agent VARCHAR(50),
    
    -- Recurring
    is_recurring BOOLEAN DEFAULT false,
    recurrence_rule VARCHAR(255), -- RRULE format
    parent_task_id UUID REFERENCES tasks(id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX idx_tasks_field ON tasks(field_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due ON tasks(due_date);
CREATE INDEX idx_tasks_scheduled ON tasks(scheduled_date);

-- ============================================
-- ALERTS
-- ============================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    
    -- Alert Info
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    message TEXT NOT NULL,
    message_ar TEXT,
    
    -- Classification
    category VARCHAR(50) NOT NULL, -- weather, pest, irrigation, harvest, market, system
    severity VARCHAR(20) NOT NULL, -- info, warning, error, critical
    
    -- Source
    source_service VARCHAR(50),
    source_event_id VARCHAR(100),
    
    -- Delivery
    channels TEXT[], -- push, sms, email, in_app
    sent_at TIMESTAMP,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, acknowledged, resolved, expired
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- Action
    action_required BOOLEAN DEFAULT false,
    action_url VARCHAR(500),
    
    -- Expiry
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_tenant ON alerts(tenant_id);
CREATE INDEX idx_alerts_field ON alerts(field_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

-- ============================================
-- ASTRONOMICAL CALENDAR (Yemeni Anwa)
-- ============================================

CREATE TABLE anwa_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Naw Info
    naw_id VARCHAR(50) NOT NULL,
    naw_name_ar VARCHAR(100) NOT NULL,
    naw_name_en VARCHAR(100) NOT NULL,
    star_name VARCHAR(100),
    
    -- Dates
    year INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Season
    season VARCHAR(20),
    season_ar VARCHAR(50),
    
    -- Agricultural Data (cached from signal service)
    suitable_crops JSONB,
    recommendations JSONB,
    traditional_weather JSONB,
    proverbs JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_anwa_dates ON anwa_events(start_date, end_date);
CREATE INDEX idx_anwa_year ON anwa_events(year);
CREATE INDEX idx_anwa_naw ON anwa_events(naw_id);

-- ============================================
-- IOT DEVICES
-- ============================================

CREATE TABLE iot_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    
    -- Device Info
    device_id VARCHAR(100) UNIQUE NOT NULL,
    device_type VARCHAR(50) NOT NULL, -- soil_sensor, weather_station, water_meter, camera
    name VARCHAR(255),
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    
    -- Location
    location GEOMETRY(POINT, 4326),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, maintenance, offline
    last_seen_at TIMESTAMP,
    battery_level INTEGER,
    signal_strength INTEGER,
    
    -- Configuration
    config JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_iot_tenant ON iot_devices(tenant_id);
CREATE INDEX idx_iot_field ON iot_devices(field_id);
CREATE INDEX idx_iot_device_id ON iot_devices(device_id);
CREATE INDEX idx_iot_type ON iot_devices(device_type);

-- ============================================
-- IOT READINGS
-- ============================================

CREATE TABLE iot_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES iot_devices(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Timestamp
    recorded_at TIMESTAMP NOT NULL,
    
    -- Readings (flexible structure)
    readings JSONB NOT NULL, -- {metric: {value, unit}}
    
    -- Common metrics (extracted for indexing)
    soil_moisture DECIMAL(5, 2),
    soil_temperature DECIMAL(4, 1),
    air_temperature DECIMAL(4, 1),
    humidity DECIMAL(5, 2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_iot_readings_device ON iot_readings(device_id);
CREATE INDEX idx_iot_readings_tenant ON iot_readings(tenant_id);
CREATE INDEX idx_iot_readings_time ON iot_readings(recorded_at DESC);

-- Partitioning for high volume (optional)
-- CREATE TABLE iot_readings_y2024m01 PARTITION OF iot_readings
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ============================================
-- AUDIT LOG
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Action
    action VARCHAR(50) NOT NULL, -- create, update, delete, login, logout
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    
    -- Details
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_fields_updated_at
    BEFORE UPDATE ON fields
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_field_crops_updated_at
    BEFORE UPDATE ON field_crops
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_iot_devices_updated_at
    BEFORE UPDATE ON iot_devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Calculate field area from geometry
CREATE OR REPLACE FUNCTION calculate_field_area()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.location IS NOT NULL THEN
        NEW.area_hectares = ST_Area(NEW.location::geography) / 10000;
        NEW.center_point = ST_Centroid(NEW.location);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_field_area_trigger
    BEFORE INSERT OR UPDATE OF location ON fields
    FOR EACH ROW EXECUTE FUNCTION calculate_field_area();

-- ============================================
-- SEED DATA
-- ============================================

-- Insert default crops
INSERT INTO crops (name_en, name_ar, category, traditional_name, suitable_anwa, growth_duration_days) VALUES
('Wheat', 'قمح', 'grains', 'برّ', ARRAY['sharatan', 'butain', 'jabha'], 120),
('Barley', 'شعير', 'grains', 'شعير', ARRAY['sharatan', 'butain', 'jabha'], 90),
('Sorghum', 'ذرة رفيعة', 'grains', 'ذرة', ARRAY['sharatan', 'thurayya'], 120),
('Coffee', 'بن', 'beverages', 'قهوة', ARRAY['thurayya', 'dabaran'], 365),
('Qat', 'قات', 'stimulants', 'قات', ARRAY['thurayya', 'dabaran', 'haqaa'], 365),
('Mango', 'مانجو', 'fruits', 'منقا', ARRAY['dabaran', 'haqaa'], 365),
('Banana', 'موز', 'fruits', 'موز', ARRAY['hanaa', 'dhiraa'], 365),
('Date Palm', 'نخيل', 'fruits', 'تمر', ARRAY['haqaa', 'hanaa', 'dhiraa'], 365),
('Tomato', 'طماطم', 'vegetables', 'بندورة', ARRAY['sharatan', 'butain', 'tarf'], 90),
('Onion', 'بصل', 'vegetables', 'بصل', ARRAY['tarf', 'jabha', 'zubra'], 120),
('Garlic', 'ثوم', 'vegetables', 'ثوم', ARRAY['zubra', 'sarfa'], 150),
('Potato', 'بطاطس', 'vegetables', 'بطاطا', ARRAY['sharatan', 'tarf'], 100),
('Watermelon', 'بطيخ', 'fruits', 'حبحب', ARRAY['butain', 'thurayya'], 90),
('Grapes', 'عنب', 'fruits', 'عنب', ARRAY['dabaran', 'haqaa'], 365),
('Pomegranate', 'رمان', 'fruits', 'رمان', ARRAY['nathra', 'tarf'], 365);

-- Insert sample tenant
INSERT INTO tenants (id, name, slug, subscription_tier) VALUES
('00000000-0000-0000-0000-000000000001', 'مزرعة تجريبية', 'demo-farm', 'pro');

COMMIT;
