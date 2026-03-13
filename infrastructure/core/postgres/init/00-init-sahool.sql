-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform v15.3 - Complete Database Initialization
-- منصة سهول - تهيئة قاعدة البيانات الكاملة
-- ═══════════════════════════════════════════════════════════════════════════════
-- Generated: 2025
-- Admin User: n@admin.com / admin
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 1: EXTENSIONS
-- ─────────────────────────────────────────────────────────────────────────────

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "postgis_topology";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 2: CUSTOM TYPES (ENUMS)
-- ─────────────────────────────────────────────────────────────────────────────

-- User & Auth Enums
-- UserRole enum matching Prisma schema
DO $$ BEGIN
    CREATE TYPE "UserRole" AS ENUM ('ADMIN', 'MANAGER', 'FARMER', 'WORKER', 'VIEWER');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- UserStatus enum matching Prisma schema
DO $$ BEGIN
    CREATE TYPE "UserStatus" AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Legacy user_role enum for backward compatibility with other tables
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'manager', 'agronomist', 'field_worker', 'researcher', 'viewer');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE subscription_tier AS ENUM ('free', 'basic', 'professional', 'enterprise');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE subscription_status AS ENUM ('active', 'trial', 'suspended', 'cancelled', 'expired');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Field & Crop Enums
DO $$ BEGIN
    CREATE TYPE field_status AS ENUM ('active', 'fallow', 'preparing', 'harvested', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE irrigation_type AS ENUM ('drip', 'sprinkler', 'flood', 'center_pivot', 'manual', 'none');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE soil_type AS ENUM ('clay', 'sandy', 'loam', 'silt', 'peat', 'chalk', 'mixed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE crop_status AS ENUM ('planned', 'planted', 'growing', 'flowering', 'fruiting', 'harvesting', 'harvested', 'failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE growth_stage AS ENUM ('germination', 'seedling', 'vegetative', 'flowering', 'fruiting', 'maturity', 'senescence');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Task Enums
DO $$ BEGIN
    CREATE TYPE task_type AS ENUM ('irrigation', 'fertilization', 'pesticide', 'harvest', 'planting', 'soil_prep', 'pruning', 'inspection', 'maintenance', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_status AS ENUM ('pending', 'scheduled', 'in_progress', 'completed', 'cancelled', 'overdue');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Alert Enums
DO $$ BEGIN
    CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical', 'emergency');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved', 'expired', 'dismissed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE alert_category AS ENUM ('weather', 'pest', 'disease', 'irrigation', 'harvest', 'equipment', 'market', 'system');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- IoT Enums
DO $$ BEGIN
    CREATE TYPE device_type AS ENUM ('soil_sensor', 'weather_station', 'water_meter', 'camera', 'drone', 'actuator', 'gateway');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE device_status AS ENUM ('online', 'offline', 'maintenance', 'error', 'inactive');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Sync Enums
DO $$ BEGIN
    CREATE TYPE sync_state AS ENUM ('idle', 'syncing', 'error', 'conflict');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE change_source AS ENUM ('user', 'system', 'import', 'satellite', 'survey');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Marketplace Enums - REMOVED: Now managed by Prisma ORM (marketplace-service)
-- The marketplace-service runs `prisma migrate deploy` on startup which creates
-- its own enums (ProductCategory, ProductStatus, etc.) with different naming conventions.
-- See: apps/services/marketplace-service/prisma/schema.prisma

-- Research Enums
DO $$ BEGIN
    CREATE TYPE experiment_status AS ENUM ('draft', 'active', 'paused', 'completed', 'cancelled', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE treatment_type AS ENUM ('fertilizer', 'pesticide', 'irrigation', 'seed_variety', 'soil_amendment', 'biological', 'control');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE sample_type AS ENUM ('soil', 'plant_tissue', 'water', 'fruit', 'seed', 'pest', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE log_category AS ENUM ('observation', 'measurement', 'treatment', 'harvest', 'weather', 'pest', 'disease', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Chat Enums
DO $$ BEGIN
    CREATE TYPE scope_type AS ENUM ('field', 'task', 'incident', 'general');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE message_type AS ENUM ('text', 'image', 'file', 'voice', 'location', 'system');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- NDVI Enums
DO $$ BEGIN
    CREATE TYPE ndvi_classification AS ENUM ('excellent', 'good', 'moderate', 'poor', 'critical', 'bare_soil', 'water');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE ndvi_trend AS ENUM ('improving', 'stable', 'declining', 'unknown');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 3: CORE TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Tenants (المستأجرين/المنظمات)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    slug VARCHAR(100) UNIQUE NOT NULL,
    subscription_tier subscription_tier DEFAULT 'free',
    subscription_status subscription_status DEFAULT 'trial',
    settings JSONB DEFAULT '{}',
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    logo_url VARCHAR(500),
    max_users INTEGER DEFAULT 5,
    max_fields INTEGER DEFAULT 10,
    trial_ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users (المستخدمين)
-- Updated to match Prisma schema with first_name/last_name and UserRole/UserStatus enums
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    role "UserRole" DEFAULT 'VIEWER',
    status "UserStatus" DEFAULT 'PENDING',
    email_verified BOOLEAN DEFAULT false,
    phone_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Account lockout fields for security
    failed_login_attempts INTEGER DEFAULT 0,
    lockout_until TIMESTAMPTZ,
    last_failed_login_at TIMESTAMPTZ,
    
    -- Password reset fields
    password_reset_token VARCHAR(255),
    password_reset_expiry TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- User Profiles (ملفات المستخدمين)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    national_id VARCHAR(50),
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    region VARCHAR(100),
    country VARCHAR(3) DEFAULT 'SA',
    avatar_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_national_id ON user_profiles(national_id);

-- User Roles (الأدوار المخصصة)
-- For custom roles and permissions (separate from UserRole enum)
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    permissions JSONB NOT NULL,
    is_system BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Sessions (جلسات المستخدمين)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_session_user_expiry ON user_sessions(user_id, expires_at);

-- Refresh Tokens (رموز التحديث)
-- For JWT refresh token rotation and security
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jti VARCHAR(255) UNIQUE NOT NULL,
    family VARCHAR(255) NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT false,
    used BOOLEAN DEFAULT false,
    used_at TIMESTAMPTZ,
    replaced_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_jti ON refresh_tokens(jti);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_family ON refresh_tokens(family);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_token_cleanup ON refresh_tokens(user_id, revoked, expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_token_revoked_expiry ON refresh_tokens(revoked, expires_at);


-- Crops Master Data (المحاصيل)
CREATE TABLE IF NOT EXISTS crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255),
    category VARCHAR(100),
    min_temp_celsius DECIMAL(5,2),
    max_temp_celsius DECIMAL(5,2),
    water_needs VARCHAR(50),
    soil_types TEXT[],
    growth_duration_days INTEGER,
    traditional_name VARCHAR(255),
    suitable_anwa TEXT[],
    common_in_regions TEXT[],
    icon_url VARCHAR(500),
    description TEXT,
    description_ar TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fields (الحقول)
CREATE TABLE IF NOT EXISTS fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description TEXT,
    boundary GEOMETRY(POLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    area_hectares DECIMAL(12,4),
    elevation_meters DECIMAL(8,2),
    governorate VARCHAR(100),
    district VARCHAR(100),
    village VARCHAR(100),
    soil_type soil_type,
    soil_ph DECIMAL(4,2),
    terrain_type VARCHAR(50),
    irrigation_type irrigation_type DEFAULT 'none',
    current_crop_id UUID REFERENCES crops(id),
    status field_status DEFAULT 'active',
    health_score DECIMAL(5,2),
    ndvi_value DECIMAL(5,4),
    planting_date DATE,
    expected_harvest DATE,
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    version INTEGER DEFAULT 1,
    etag VARCHAR(64),
    server_updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fields_tenant ON fields(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fields_boundary ON fields USING GIST(boundary);
CREATE INDEX IF NOT EXISTS idx_fields_center ON fields USING GIST(center_point);
CREATE INDEX IF NOT EXISTS idx_fields_status ON fields(status);
CREATE INDEX IF NOT EXISTS idx_fields_owner ON fields(owner_id);

-- Field Boundary History (تاريخ حدود الحقول)
CREATE TABLE IF NOT EXISTS field_boundary_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    version_at_change INTEGER NOT NULL,
    previous_boundary GEOMETRY(POLYGON, 4326),
    new_boundary GEOMETRY(POLYGON, 4326),
    area_change_hectares DECIMAL(12,4),
    changed_by UUID REFERENCES users(id),
    change_reason TEXT,
    change_source change_source DEFAULT 'user',
    device_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_boundary_history_field ON field_boundary_history(field_id);

-- Field Crops (زراعة المحاصيل)
CREATE TABLE IF NOT EXISTS field_crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    crop_id UUID NOT NULL REFERENCES crops(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    planting_date DATE,
    expected_harvest_date DATE,
    actual_harvest_date DATE,
    planted_area_hectares DECIMAL(12,4),
    status crop_status DEFAULT 'planned',
    growth_stage growth_stage,
    expected_yield_kg DECIMAL(12,2),
    actual_yield_kg DECIMAL(12,2),
    yield_quality VARCHAR(50),
    total_cost DECIMAL(12,2),
    total_revenue DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'SAR',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_field_crops_field ON field_crops(field_id);
CREATE INDEX IF NOT EXISTS idx_field_crops_tenant ON field_crops(tenant_id);
CREATE INDEX IF NOT EXISTS idx_field_crops_status ON field_crops(status);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 4: NDVI & SATELLITE TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- NDVI Records (سجلات NDVI)
CREATE TABLE IF NOT EXISTS ndvi_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    capture_date DATE NOT NULL,
    satellite VARCHAR(50),
    cloud_coverage_percent DECIMAL(5,2),
    ndvi_mean DECIMAL(6,4),
    ndvi_min DECIMAL(6,4),
    ndvi_max DECIMAL(6,4),
    ndvi_std_dev DECIMAL(6,4),
    classification ndvi_classification,
    health_score DECIMAL(5,2),
    change_from_previous DECIMAL(6,4),
    trend ndvi_trend DEFAULT 'unknown',
    raw_image_url VARCHAR(500),
    processed_image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    zones JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ndvi_field ON ndvi_records(field_id);
CREATE INDEX IF NOT EXISTS idx_ndvi_tenant ON ndvi_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ndvi_date ON ndvi_records(capture_date);
CREATE INDEX IF NOT EXISTS idx_ndvi_classification ON ndvi_records(classification);

-- NDVI Readings (قراءات NDVI التفصيلية)
CREATE TABLE IF NOT EXISTS ndvi_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    value DECIMAL(6,4) NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    source VARCHAR(100),
    cloud_cover DECIMAL(5,2),
    quality VARCHAR(50),
    satellite_name VARCHAR(100),
    band_info JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ndvi_readings_field_date ON ndvi_readings(field_id, captured_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 5: WEATHER TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Weather Records (سجلات الطقس)
CREATE TABLE IF NOT EXISTS weather_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    location_id VARCHAR(100),
    coordinates GEOMETRY(POINT, 4326),
    location_name VARCHAR(255),
    recorded_at TIMESTAMPTZ NOT NULL,
    temperature_celsius DECIMAL(5,2),
    feels_like_celsius DECIMAL(5,2),
    humidity_percent DECIMAL(5,2),
    pressure_hpa DECIMAL(7,2),
    wind_speed_ms DECIMAL(6,2),
    wind_direction_degrees INTEGER,
    wind_gust_ms DECIMAL(6,2),
    precipitation_mm DECIMAL(8,2),
    precipitation_probability DECIMAL(5,2),
    conditions VARCHAR(100),
    conditions_ar VARCHAR(100),
    icon_code VARCHAR(20),
    uv_index DECIMAL(4,2),
    visibility_km DECIMAL(6,2),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weather_tenant ON weather_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_weather_location ON weather_records(location_id);
CREATE INDEX IF NOT EXISTS idx_weather_recorded ON weather_records(recorded_at);

-- Weather Forecasts (توقعات الطقس)
CREATE TABLE IF NOT EXISTS weather_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    location_id VARCHAR(100),
    coordinates GEOMETRY(POINT, 4326),
    forecast_date DATE NOT NULL,
    forecast_time TIME,
    temperature_min DECIMAL(5,2),
    temperature_max DECIMAL(5,2),
    humidity_percent DECIMAL(5,2),
    precipitation_probability DECIMAL(5,2),
    precipitation_mm DECIMAL(8,2),
    wind_speed_ms DECIMAL(6,2),
    conditions VARCHAR(100),
    conditions_ar VARCHAR(100),
    icon_code VARCHAR(20),
    source VARCHAR(50),
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecast_date ON weather_forecasts(forecast_date);
CREATE INDEX IF NOT EXISTS idx_forecast_location ON weather_forecasts(location_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 6: TASKS & ACTIVITIES
-- ─────────────────────────────────────────────────────────────────────────────

-- Tasks (المهام)
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id VARCHAR(100),
    zone_id VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    task_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    assigned_to VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,
    due_date TIMESTAMPTZ,
    scheduled_time VARCHAR(10),
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    completed_at TIMESTAMPTZ,
    completion_notes TEXT,
    task_metadata JSONB DEFAULT '{}',
    astronomical_score INTEGER,
    moon_phase_at_due_date VARCHAR(100),
    lunar_mansion_at_due_date VARCHAR(100),
    optimal_time_of_day VARCHAR(50),
    suggested_by_calendar BOOLEAN DEFAULT false,
    astronomical_recommendation JSONB,
    astronomical_warnings TEXT[],
    parent_task_id VARCHAR(50) REFERENCES tasks(task_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_field ON tasks(field_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 7: ALERTS & NOTIFICATIONS
-- ─────────────────────────────────────────────────────────────────────────────

-- Alerts (التنبيهات)
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    message TEXT NOT NULL,
    message_ar TEXT,
    category alert_category NOT NULL,
    severity alert_severity DEFAULT 'info',
    source_service VARCHAR(100),
    source_event_id VARCHAR(255),
    channels TEXT[] DEFAULT ARRAY['push', 'in_app'],
    sent_at TIMESTAMPTZ,
    status alert_status DEFAULT 'active',
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    action_required BOOLEAN DEFAULT false,
    action_url VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_tenant ON alerts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_alerts_field ON alerts(field_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at);

-- Notification Log (سجل الإشعارات)
CREATE TABLE IF NOT EXISTS notification_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    alert_id UUID REFERENCES alerts(id),
    channel VARCHAR(50) NOT NULL,
    destination VARCHAR(255),
    title VARCHAR(255),
    body TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notification_user ON notification_log(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_status ON notification_log(status);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 8: IOT DEVICES & READINGS
-- ─────────────────────────────────────────────────────────────────────────────

-- IoT Devices (أجهزة إنترنت الأشياء)
CREATE TABLE IF NOT EXISTS iot_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    device_type device_type NOT NULL,
    name VARCHAR(255),
    name_ar VARCHAR(255),
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    location GEOMETRY(POINT, 4326),
    status device_status DEFAULT 'offline',
    last_seen_at TIMESTAMPTZ,
    battery_level DECIMAL(5,2),
    signal_strength INTEGER,
    firmware_version VARCHAR(50),
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_iot_devices_tenant ON iot_devices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_iot_devices_field ON iot_devices(field_id);
CREATE INDEX IF NOT EXISTS idx_iot_devices_device_id ON iot_devices(device_id);
CREATE INDEX IF NOT EXISTS idx_iot_devices_type ON iot_devices(device_type);

-- IoT Readings (قراءات المستشعرات)
CREATE TABLE IF NOT EXISTS iot_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES iot_devices(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    recorded_at TIMESTAMPTZ NOT NULL,
    readings JSONB NOT NULL,
    soil_moisture DECIMAL(6,2),
    soil_temperature DECIMAL(6,2),
    air_temperature DECIMAL(6,2),
    humidity DECIMAL(6,2),
    light_intensity DECIMAL(10,2),
    ec_value DECIMAL(8,4),
    ph_value DECIMAL(4,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_iot_readings_device ON iot_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_iot_readings_tenant ON iot_readings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_iot_readings_recorded ON iot_readings(recorded_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 9: SYNC & OFFLINE SUPPORT
-- ─────────────────────────────────────────────────────────────────────────────

-- Sync Status (حالة المزامنة)
CREATE TABLE IF NOT EXISTS sync_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    last_sync_at TIMESTAMPTZ,
    last_sync_version BIGINT DEFAULT 0,
    status sync_state DEFAULT 'idle',
    pending_uploads INTEGER DEFAULT 0,
    pending_downloads INTEGER DEFAULT 0,
    conflicts_count INTEGER DEFAULT 0,
    last_error TEXT,
    device_info JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(device_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_sync_status_user ON sync_status(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_status_device ON sync_status(device_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 10: MARKETPLACE TABLES - REMOVED
-- Now managed by Prisma ORM (marketplace-service runs `prisma migrate deploy` on startup)
-- Tables: products, orders, order_items, wallets, transactions, loans,
--         credit_scores, shipping_zones, delivery_estimates, escrows,
--         scheduled_payments, recurring_payments, reviews, payments
-- See: apps/services/marketplace-service/prisma/schema.prisma
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 11: RESEARCH TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Experiments (التجارب البحثية)
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    hypothesis TEXT,
    hypothesis_ar TEXT,
    start_date DATE,
    end_date DATE,
    status experiment_status DEFAULT 'draft',
    locked_at TIMESTAMPTZ,
    locked_by UUID REFERENCES users(id),
    principal_researcher_id UUID REFERENCES users(id),
    organization_id UUID,
    farm_id UUID,
    location GEOGRAPHY(POINT, 4326),
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_experiments_tenant ON experiments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiments_researcher ON experiments(principal_researcher_id);

-- Research Protocols (بروتوكولات البحث)
CREATE TABLE IF NOT EXISTS research_protocols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    methodology TEXT,
    methodology_ar TEXT,
    variables JSONB DEFAULT '{}',
    measurement_schedule JSONB DEFAULT '{}',
    equipment_required TEXT[],
    safety_guidelines TEXT,
    version INTEGER DEFAULT 1,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_protocols_experiment ON research_protocols(experiment_id);

-- Research Plots (قطع التجارب)
CREATE TABLE IF NOT EXISTS research_plots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_code VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    name_ar VARCHAR(255),
    area_sqm DECIMAL(12,4),
    boundary GEOGRAPHY(POLYGON, 4326),
    centroid GEOGRAPHY(POINT, 4326),
    soil_type VARCHAR(100),
    soil_ph DECIMAL(4,2),
    previous_crop VARCHAR(100),
    replicate_number INTEGER,
    block_number INTEGER,
    row_number INTEGER,
    column_number INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(experiment_id, plot_code)
);

CREATE INDEX IF NOT EXISTS idx_plots_experiment ON research_plots(experiment_id);

-- Treatments (المعاملات التجريبية)
CREATE TABLE IF NOT EXISTS treatments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_id UUID REFERENCES research_plots(id) ON DELETE SET NULL,
    treatment_code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    type treatment_type NOT NULL,
    description TEXT,
    description_ar TEXT,
    dosage VARCHAR(100),
    dosage_unit VARCHAR(50),
    application_method VARCHAR(100),
    application_frequency VARCHAR(100),
    start_date DATE,
    end_date DATE,
    is_control BOOLEAN DEFAULT false,
    parameters JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_treatments_experiment ON treatments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_treatments_plot ON treatments(plot_id);

-- Research Daily Logs (السجلات اليومية للبحث)
CREATE TABLE IF NOT EXISTS research_daily_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_id UUID REFERENCES research_plots(id) ON DELETE SET NULL,
    treatment_id UUID REFERENCES treatments(id) ON DELETE SET NULL,
    log_date DATE NOT NULL,
    log_time TIME,
    category log_category DEFAULT 'observation',
    title VARCHAR(255),
    title_ar VARCHAR(255),
    notes TEXT,
    notes_ar TEXT,
    measurements JSONB DEFAULT '{}',
    weather_conditions JSONB DEFAULT '{}',
    photos TEXT[],
    attachments TEXT[],
    recorded_by UUID REFERENCES users(id),
    device_id VARCHAR(255),
    offline_id VARCHAR(255) UNIQUE,
    hash VARCHAR(64),
    synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_experiment ON research_daily_logs(experiment_id);
CREATE INDEX IF NOT EXISTS idx_logs_date ON research_daily_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_logs_plot ON research_daily_logs(plot_id);

-- Lab Samples (عينات المختبر)
CREATE TABLE IF NOT EXISTS lab_samples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_id UUID REFERENCES research_plots(id) ON DELETE SET NULL,
    log_id UUID REFERENCES research_daily_logs(id) ON DELETE SET NULL,
    sample_code VARCHAR(100) UNIQUE NOT NULL,
    type sample_type NOT NULL,
    description TEXT,
    description_ar TEXT,
    collection_date DATE NOT NULL,
    collection_time TIME,
    collection_location GEOGRAPHY(POINT, 4326),
    collected_by UUID REFERENCES users(id),
    storage_location VARCHAR(255),
    storage_conditions VARCHAR(255),
    quantity DECIMAL(10,4),
    quantity_unit VARCHAR(50),
    analysis_status VARCHAR(50) DEFAULT 'pending',
    analysis_results JSONB DEFAULT '{}',
    analyzed_by UUID REFERENCES users(id),
    analyzed_at TIMESTAMPTZ,
    photos TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_samples_experiment ON lab_samples(experiment_id);
CREATE INDEX IF NOT EXISTS idx_samples_code ON lab_samples(sample_code);

-- Digital Signatures (التوقيعات الرقمية)
CREATE TABLE IF NOT EXISTS digital_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    signer_id UUID NOT NULL REFERENCES users(id),
    signature_hash VARCHAR(512) NOT NULL,
    algorithm VARCHAR(50) DEFAULT 'SHA256',
    payload_hash VARCHAR(512),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    device_info JSONB DEFAULT '{}',
    purpose VARCHAR(100),
    is_valid BOOLEAN DEFAULT true,
    invalidated_at TIMESTAMPTZ,
    invalidated_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signatures_entity ON digital_signatures(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_signatures_signer ON digital_signatures(signer_id);

-- Experiment Collaborators (المتعاونون في التجارب)
CREATE TABLE IF NOT EXISTS experiment_collaborators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100) NOT NULL,
    permissions JSONB DEFAULT '{}',
    invited_by UUID REFERENCES users(id),
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(experiment_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_collaborators_experiment ON experiment_collaborators(experiment_id);

-- Experiment Audit Log (سجل تدقيق التجارب)
CREATE TABLE IF NOT EXISTS experiment_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID REFERENCES experiments(id) ON DELETE SET NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_exp_audit_experiment ON experiment_audit_log(experiment_id);
CREATE INDEX IF NOT EXISTS idx_exp_audit_entity ON experiment_audit_log(entity_type, entity_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 12: CHAT TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Chat Threads (محادثات)
CREATE TABLE IF NOT EXISTS chat_threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    scope_type scope_type NOT NULL,
    scope_id UUID,
    created_by UUID REFERENCES users(id),
    title VARCHAR(255),
    is_archived BOOLEAN DEFAULT false,
    last_message_at TIMESTAMPTZ,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, scope_type, scope_id)
);

CREATE INDEX IF NOT EXISTS idx_threads_tenant ON chat_threads(tenant_id);
CREATE INDEX IF NOT EXISTS idx_threads_scope ON chat_threads(scope_type, scope_id);

-- Chat Messages (الرسائل)
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id),
    text TEXT,
    attachments JSONB DEFAULT '[]',
    reply_to_id UUID REFERENCES chat_messages(id),
    message_type message_type DEFAULT 'text',
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_thread ON chat_messages(thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON chat_messages(tenant_id, sender_id);

-- Chat Participants (المشاركون)
CREATE TABLE IF NOT EXISTS chat_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_read_at TIMESTAMPTZ,
    last_read_message_id UUID REFERENCES chat_messages(id),
    unread_count INTEGER DEFAULT 0,
    is_muted BOOLEAN DEFAULT false,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(thread_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_participants_thread ON chat_participants(thread_id);
CREATE INDEX IF NOT EXISTS idx_participants_user ON chat_participants(user_id);

-- Chat Attachments (المرفقات)
CREATE TABLE IF NOT EXISTS chat_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size BIGINT,
    file_url VARCHAR(500) NOT NULL,
    width INTEGER,
    height INTEGER,
    thumbnail_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_attachments_message ON chat_attachments(message_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 13: ASTRONOMICAL CALENDAR (أنواء)
-- ─────────────────────────────────────────────────────────────────────────────

-- Anwa Events (أحداث الأنواء)
CREATE TABLE IF NOT EXISTS anwa_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    naw_id INTEGER NOT NULL,
    naw_name_ar VARCHAR(100) NOT NULL,
    naw_name_en VARCHAR(100),
    star_name VARCHAR(100),
    year INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    season VARCHAR(50),
    season_ar VARCHAR(50),
    suitable_crops JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '{}',
    traditional_weather JSONB DEFAULT '{}',
    proverbs JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anwa_dates ON anwa_events(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_anwa_year ON anwa_events(year);
CREATE INDEX IF NOT EXISTS idx_anwa_naw ON anwa_events(naw_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 14: AUDIT & SYSTEM TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Audit Logs (سجلات التدقيق)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);

-- AI Consultations (استشارات الذكاء الاصطناعي)
CREATE TABLE IF NOT EXISTS ai_consultations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    field_id UUID REFERENCES fields(id),
    agent_type VARCHAR(100) NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    context JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '[]',
    confidence_score DECIMAL(5,4),
    tokens_used INTEGER,
    response_time_ms INTEGER,
    rating INTEGER,
    feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_tenant ON ai_consultations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ai_user ON ai_consultations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_agent ON ai_consultations(agent_type);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 15: EQUIPMENT TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Equipment (المعدات)
CREATE TABLE IF NOT EXISTS equipment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    type VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    serial_number VARCHAR(100),
    purchase_date DATE,
    purchase_price DECIMAL(14,2),
    currency VARCHAR(3) DEFAULT 'SAR',
    status VARCHAR(50) DEFAULT 'available',
    current_location VARCHAR(255),
    assigned_to UUID REFERENCES users(id),
    assigned_field_id UUID REFERENCES fields(id),
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    operating_hours DECIMAL(10,2),
    fuel_type VARCHAR(50),
    notes TEXT,
    image_url VARCHAR(500),
    documents JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_equipment_tenant ON equipment(tenant_id);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(type);

-- Equipment Maintenance (صيانة المعدات)
CREATE TABLE IF NOT EXISTS equipment_maintenance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_id UUID NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMPTZ,
    cost DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'SAR',
    parts_replaced JSONB DEFAULT '[]',
    next_due_date DATE,
    notes TEXT,
    documents JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_maintenance_equipment ON equipment_maintenance(equipment_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_date ON equipment_maintenance(performed_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 16: FUNCTIONS & TRIGGERS
-- ─────────────────────────────────────────────────────────────────────────────

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to tables
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%s_updated_at ON %s', t, t);
        EXECUTE format('CREATE TRIGGER update_%s_updated_at BEFORE UPDATE ON %s FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
    END LOOP;
END;
$$;

-- Generate order number function
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.order_number IS NULL THEN
        NEW.order_number := 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' ||
                           LPAD(NEXTVAL('order_number_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create sequence for order numbers
CREATE SEQUENCE IF NOT EXISTS order_number_seq START 1;

-- Apply order number trigger
DROP TRIGGER IF EXISTS generate_order_number_trigger ON orders;
CREATE TRIGGER generate_order_number_trigger
    BEFORE INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION generate_order_number();

-- Calculate field area from boundary
CREATE OR REPLACE FUNCTION calculate_field_area()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.boundary IS NOT NULL THEN
        NEW.area_hectares := ST_Area(NEW.boundary::geography) / 10000;
        NEW.center_point := ST_Centroid(NEW.boundary);
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS calculate_field_area_trigger ON fields;
CREATE TRIGGER calculate_field_area_trigger
    BEFORE INSERT OR UPDATE OF boundary ON fields
    FOR EACH ROW
    EXECUTE FUNCTION calculate_field_area();

-- ═══════════════════════════════════════════════════════════════════════════════
-- SECTION 17: DEMO DATA - MOVED TO SEPARATE FILE
-- ═══════════════════════════════════════════════════════════════════════════════
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║  ⚠️  SECURITY WARNING - FOR DEVELOPMENT/TESTING ONLY ⚠️                      ║
-- ║                                                                               ║
-- ║  The following demo data contains HARDCODED PASSWORDS that must NEVER be     ║
-- ║  used in production environments. Before deploying to production:            ║
-- ║                                                                               ║
-- ║  1. DELETE all demo users or change their passwords                          ║
-- ║  2. Use environment variables for admin credentials                          ║
-- ║  3. Generate strong, unique passwords (min 16 chars, mixed case, symbols)    ║
-- ║  4. Enable password policies in your application                             ║
-- ║                                                                               ║
-- ║  Run in production: DELETE FROM users WHERE email LIKE '%@sahool.io';        ║
-- ║  Or disable this section by setting SKIP_DEMO_DATA=true                      ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝

-- Insert default tenant
INSERT INTO tenants (id, name, name_ar, slug, subscription_tier, subscription_status, max_users, max_fields, contact_email)
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'Sahool Demo Farm',
    'مزرعة سهول التجريبية',
    'sahool-demo',
    'enterprise',
    'active',
    100,
    1000,
    'admin@sahool.io'
) ON CONFLICT (slug) DO NOTHING;

-- Insert admin user (password: admin)
-- Using pgcrypto for bcrypt hash
INSERT INTO users (id, tenant_id, email, password_hash, first_name, last_name, role, status, email_verified)
VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'n@admin.com',
    crypt('admin', gen_salt('bf', 12)),
    'Admin',
    'User',
    'ADMIN',
    'ACTIVE',
    true
) ON CONFLICT (email) DO UPDATE SET
    password_hash = crypt('admin', gen_salt('bf', 12)),
    role = 'ADMIN',
    status = 'ACTIVE';

-- Insert demo users
INSERT INTO users (id, tenant_id, email, password_hash, first_name, last_name, role, status, email_verified)
VALUES
    ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'manager@sahool.io', crypt('manager123', gen_salt('bf', 12)), 'Farm', 'Manager', 'MANAGER', 'ACTIVE', true),
    ('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'agronomist@sahool.io', crypt('agro123', gen_salt('bf', 12)), 'Ahmed', 'Al-Rashid', 'FARMER', 'ACTIVE', true),
    ('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 'worker@sahool.io', crypt('worker123', gen_salt('bf', 12)), 'Mohammed', 'Ali', 'WORKER', 'ACTIVE', true),
    ('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000001', 'researcher@sahool.io', crypt('research123', gen_salt('bf', 12)), 'Fatima', 'Hassan', 'VIEWER', 'ACTIVE', true)
ON CONFLICT (email) DO NOTHING;

-- Insert crops master data
INSERT INTO crops (id, name_en, name_ar, scientific_name, category, min_temp_celsius, max_temp_celsius, water_needs, growth_duration_days, is_active)
VALUES
    ('c0000000-0000-0000-0000-000000000001', 'Wheat', 'القمح', 'Triticum aestivum', 'grains', 5, 35, 'medium', 120, true),
    ('c0000000-0000-0000-0000-000000000002', 'Barley', 'الشعير', 'Hordeum vulgare', 'grains', 5, 30, 'low', 90, true),
    ('c0000000-0000-0000-0000-000000000003', 'Date Palm', 'النخيل', 'Phoenix dactylifera', 'fruits', 10, 50, 'low', 365, true),
    ('c0000000-0000-0000-0000-000000000004', 'Tomato', 'الطماطم', 'Solanum lycopersicum', 'vegetables', 15, 35, 'high', 90, true),
    ('c0000000-0000-0000-0000-000000000005', 'Alfalfa', 'البرسيم', 'Medicago sativa', 'fodder', 10, 40, 'high', 60, true),
    ('c0000000-0000-0000-0000-000000000006', 'Cucumber', 'الخيار', 'Cucumis sativus', 'vegetables', 18, 35, 'high', 60, true),
    ('c0000000-0000-0000-0000-000000000007', 'Olive', 'الزيتون', 'Olea europaea', 'fruits', 5, 40, 'low', 365, true),
    ('c0000000-0000-0000-0000-000000000008', 'Grape', 'العنب', 'Vitis vinifera', 'fruits', 10, 40, 'medium', 180, true),
    ('c0000000-0000-0000-0000-000000000009', 'Citrus', 'الحمضيات', 'Citrus spp.', 'fruits', 10, 38, 'medium', 365, true),
    ('c0000000-0000-0000-0000-000000000010', 'Onion', 'البصل', 'Allium cepa', 'vegetables', 10, 30, 'medium', 120, true)
ON CONFLICT DO NOTHING;

-- Insert demo fields with PostGIS geometry
INSERT INTO fields (id, tenant_id, owner_id, name, name_ar, governorate, district, soil_type, irrigation_type, current_crop_id, status, health_score, boundary, area_hectares)
VALUES
    (
        'd0000000-0000-0000-0000-000000000001',
        'a0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000002',
        'North Field',
        'الحقل الشمالي',
        'Riyadh',
        'Al-Kharj',
        'loam',
        'drip',
        'c0000000-0000-0000-0000-000000000001',
        'active',
        85.5,
        ST_GeomFromText('POLYGON((46.7 24.1, 46.71 24.1, 46.71 24.11, 46.7 24.11, 46.7 24.1))', 4326),
        120.5
    ),
    (
        'd0000000-0000-0000-0000-000000000002',
        'a0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000002',
        'South Field',
        'الحقل الجنوبي',
        'Riyadh',
        'Al-Kharj',
        'sandy',
        'center_pivot',
        'c0000000-0000-0000-0000-000000000003',
        'active',
        78.2,
        ST_GeomFromText('POLYGON((46.72 24.08, 46.73 24.08, 46.73 24.09, 46.72 24.09, 46.72 24.08))', 4326),
        85.0
    ),
    (
        'd0000000-0000-0000-0000-000000000003',
        'a0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000003',
        'East Greenhouse',
        'البيت المحمي الشرقي',
        'Riyadh',
        'Al-Kharj',
        'mixed',
        'drip',
        'c0000000-0000-0000-0000-000000000004',
        'active',
        92.0,
        ST_GeomFromText('POLYGON((46.74 24.1, 46.745 24.1, 46.745 24.105, 46.74 24.105, 46.74 24.1))', 4326),
        2.5
    )
ON CONFLICT DO NOTHING;

-- Insert field crops
INSERT INTO field_crops (id, field_id, crop_id, tenant_id, planting_date, expected_harvest_date, status, growth_stage, planted_area_hectares)
VALUES
    ('e0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', '2025-01-15', '2025-05-15', 'growing', 'vegetative', 120.5),
    ('e0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', '2020-03-01', '2025-09-01', 'growing', 'fruiting', 85.0),
    ('e0000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', '2025-02-01', '2025-05-01', 'growing', 'flowering', 2.5)
ON CONFLICT DO NOTHING;

-- Insert demo tasks
INSERT INTO tasks (task_id, tenant_id, field_id, title, title_ar, task_type, status, priority, assigned_to, created_by, due_date)
VALUES
    ('f0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Apply fertilizer', 'تطبيق السماد', 'fertilization', 'pending', 'high', 'b0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000002', CURRENT_DATE + INTERVAL '2 days'),
    ('f0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'Irrigation check', 'فحص الري', 'irrigation', 'pending', 'medium', 'b0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000002', CURRENT_DATE + INTERVAL '1 day'),
    ('f0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'Pest inspection', 'فحص الآفات', 'inspection', 'pending', 'high', 'b0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000002', CURRENT_DATE + INTERVAL '3 days'),
    ('f0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Soil sampling', 'أخذ عينات التربة', 'soil_prep', 'completed', 'low', 'b0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000002', CURRENT_DATE - INTERVAL '2 days')
ON CONFLICT DO NOTHING;

-- Insert demo NDVI records
INSERT INTO ndvi_records (id, field_id, tenant_id, capture_date, satellite, cloud_coverage_percent, ndvi_mean, ndvi_min, ndvi_max, classification, health_score, trend)
VALUES
    ('00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Sentinel-2', 5.2, 0.72, 0.45, 0.89, 'good', 85.5, 'improving'),
    ('00000000-0000-0000-0001-000000000002', 'd0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 14, 'Sentinel-2', 8.1, 0.68, 0.42, 0.85, 'good', 82.0, 'stable'),
    ('00000000-0000-0000-0001-000000000003', 'd0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Landsat-8', 3.5, 0.65, 0.38, 0.82, 'moderate', 78.2, 'stable'),
    ('00000000-0000-0000-0001-000000000004', 'd0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'Sentinel-2', 2.0, 0.85, 0.72, 0.95, 'excellent', 92.0, 'improving')
ON CONFLICT DO NOTHING;

-- Insert demo IoT devices
INSERT INTO iot_devices (id, tenant_id, field_id, device_id, device_type, name, name_ar, status, battery_level)
VALUES
    ('00000000-0000-0000-0002-000000000001', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'SOIL-001', 'soil_sensor', 'Soil Sensor North-1', 'مستشعر التربة شمال-1', 'online', 85.0),
    ('00000000-0000-0000-0002-000000000002', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'WEATHER-001', 'weather_station', 'Weather Station Main', 'محطة الطقس الرئيسية', 'online', 92.0),
    ('00000000-0000-0000-0002-000000000003', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'WATER-001', 'water_meter', 'Water Meter South', 'عداد المياه الجنوبي', 'online', 78.0),
    ('00000000-0000-0000-0002-000000000004', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'CAM-001', 'camera', 'Greenhouse Camera', 'كاميرا البيت المحمي', 'online', 100.0)
ON CONFLICT DO NOTHING;

-- Insert demo IoT readings
INSERT INTO iot_readings (id, device_id, tenant_id, recorded_at, readings, soil_moisture, soil_temperature, air_temperature, humidity)
VALUES
    ('00000000-0000-0000-0003-000000000001', '00000000-0000-0000-0002-000000000001', 'a0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '1 hour', '{"moisture": 45.2, "temperature": 22.5, "ec": 1.2}', 45.2, 22.5, 28.0, 55.0),
    ('00000000-0000-0000-0003-000000000002', '00000000-0000-0000-0002-000000000001', 'a0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '2 hours', '{"moisture": 44.8, "temperature": 23.0, "ec": 1.1}', 44.8, 23.0, 29.0, 52.0),
    ('00000000-0000-0000-0003-000000000003', '00000000-0000-0000-0002-000000000002', 'a0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '1 hour', '{"temperature": 28.5, "humidity": 45, "pressure": 1013}', NULL, NULL, 28.5, 45.0)
ON CONFLICT DO NOTHING;

-- Insert demo alerts
INSERT INTO alerts (id, tenant_id, field_id, title, title_ar, message, message_ar, category, severity, status)
VALUES
    ('00000000-0000-0000-0004-000000000001', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Low Soil Moisture', 'انخفاض رطوبة التربة', 'Soil moisture in North Field has dropped below 40%', 'انخفضت رطوبة التربة في الحقل الشمالي إلى أقل من 40%', 'irrigation', 'warning', 'active'),
    ('00000000-0000-0000-0004-000000000002', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'High Temperature Alert', 'تنبيه درجة حرارة مرتفعة', 'Greenhouse temperature exceeds 38°C', 'درجة حرارة البيت المحمي تتجاوز 38 درجة مئوية', 'weather', 'critical', 'active'),
    ('00000000-0000-0000-0004-000000000003', 'a0000000-0000-0000-0000-000000000001', NULL, 'Harvest Season Reminder', 'تذكير موسم الحصاد', 'Wheat harvest season approaching in 30 days', 'يقترب موسم حصاد القمح خلال 30 يوماً', 'harvest', 'info', 'active')
ON CONFLICT DO NOTHING;

-- Demo marketplace data REMOVED: Tables now managed by Prisma (marketplace-service)
-- Marketplace seed data should be added via marketplace-service's own seed mechanism

-- Insert demo experiment
INSERT INTO experiments (id, tenant_id, title, title_ar, description, hypothesis, start_date, status, principal_researcher_id)
VALUES
    ('00000000-0000-0000-0007-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Drought-Resistant Wheat Varieties Trial', 'تجربة أصناف القمح المقاومة للجفاف', 'Testing 5 wheat varieties for drought resistance in Al-Kharj region', 'Variety X-15 will show 20% higher yield under water stress conditions', '2025-01-01', 'active', 'b0000000-0000-0000-0000-000000000005')
ON CONFLICT DO NOTHING;

-- Insert demo Anwa events
INSERT INTO anwa_events (id, naw_id, naw_name_ar, naw_name_en, year, start_date, end_date, season, season_ar, suitable_crops, recommendations)
VALUES
    ('00000000-0000-0000-0008-000000000001', 1, 'الثريا', 'Al-Thurayya', 2025, '2025-06-07', '2025-06-19', 'summer', 'الصيف', '["dates", "grapes"]', '{"irrigation": "increase", "activities": ["harvest_dates"]}'),
    ('00000000-0000-0000-0008-000000000002', 2, 'الدبران', 'Al-Dabaran', 2025, '2025-06-20', '2025-07-02', 'summer', 'الصيف', '["dates", "melons"]', '{"irrigation": "maintain", "activities": ["protect_from_heat"]}'),
    ('00000000-0000-0000-0008-000000000003', 15, 'سعد الذابح', 'Saad Al-Thabeh', 2025, '2025-01-29', '2025-02-10', 'winter', 'الشتاء', '["wheat", "barley", "vegetables"]', '{"irrigation": "reduce", "activities": ["planting_grains"]}')
ON CONFLICT DO NOTHING;

-- Insert demo weather records
INSERT INTO weather_records (id, tenant_id, location_id, location_name, recorded_at, temperature_celsius, humidity_percent, wind_speed_ms, conditions, conditions_ar, source)
VALUES
    ('00000000-0000-0000-0009-000000000001', 'a0000000-0000-0000-0000-000000000001', 'al-kharj', 'Al-Kharj', NOW(), 32.5, 35.0, 4.2, 'Clear', 'صافي', 'openweather'),
    ('00000000-0000-0000-0009-000000000002', 'a0000000-0000-0000-0000-000000000001', 'al-kharj', 'Al-Kharj', NOW() - INTERVAL '1 day', 30.2, 40.0, 3.8, 'Partly Cloudy', 'غائم جزئياً', 'openweather')
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- SECTION 18: GRANT PERMISSIONS
-- ═══════════════════════════════════════════════════════════════════════════════

-- Grant all privileges on all tables to sahool user
DO $$
BEGIN
    EXECUTE format('GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO %I', current_user);
    EXECUTE format('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO %I', current_user);
    EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO %I', current_user);

    -- Grant pg_monitor role for PgBouncer auth_query access to pg_shadow
    -- This is required for PgBouncer to authenticate users via SCRAM-SHA-256
    IF current_user != 'postgres' THEN
        EXECUTE format('GRANT pg_monitor TO %I', current_user);
        RAISE NOTICE 'Granted pg_monitor to % for PgBouncer auth_query support', current_user;
    END IF;
END;
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA VERIFICATION
-- ═══════════════════════════════════════════════════════════════════════════════

-- Summary of schema creation (no demo data verification - moved to 03-demo-data.sql)
DO $$
DECLARE
    table_count INTEGER;
    index_count INTEGER;
    function_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    SELECT COUNT(*) INTO index_count FROM pg_indexes WHERE schemaname = 'public';
    SELECT COUNT(*) INTO function_count FROM information_schema.routines WHERE routine_schema = 'public';

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  SAHOOL DATABASE SCHEMA INITIALIZATION COMPLETE';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  Tables created: %', table_count;
    RAISE NOTICE '  Indexes created: %', index_count;
    RAISE NOTICE '  Functions created: %', function_count;
    RAISE NOTICE '';
    RAISE NOTICE '  Note: Demo data is loaded separately from 03-demo-data.sql';
    RAISE NOTICE '  For production: Remove or rename 03-demo-data.sql';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
