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

-- Marketplace Enums
DO $$ BEGIN
    CREATE TYPE product_category AS ENUM ('seeds', 'fertilizers', 'pesticides', 'equipment', 'crops', 'livestock', 'services');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE product_status AS ENUM ('draft', 'active', 'sold', 'expired', 'suspended');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE seller_type AS ENUM ('farmer', 'supplier', 'cooperative', 'company');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE transaction_type AS ENUM ('deposit', 'withdrawal', 'purchase', 'sale', 'refund', 'loan', 'repayment', 'fee');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'reversed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE loan_status AS ENUM ('pending', 'approved', 'active', 'paid', 'defaulted', 'rejected');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE loan_purpose AS ENUM ('seeds', 'equipment', 'fertilizer', 'irrigation', 'labor', 'general');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE credit_tier AS ENUM ('bronze', 'silver', 'gold', 'platinum');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

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
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    field_crop_id UUID REFERENCES field_crops(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    type task_type DEFAULT 'other',
    category VARCHAR(100),
    assigned_to UUID REFERENCES users(id),
    assigned_by UUID REFERENCES users(id),
    scheduled_date DATE,
    scheduled_time TIME,
    due_date DATE,
    estimated_duration_minutes INTEGER,
    status task_status DEFAULT 'pending',
    priority task_priority DEFAULT 'medium',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    completion_notes TEXT,
    completion_photos TEXT[],
    evidence JSONB,
    is_ai_generated BOOLEAN DEFAULT false,
    source_event_id VARCHAR(255),
    source_agent VARCHAR(100),
    is_recurring BOOLEAN DEFAULT false,
    recurrence_rule VARCHAR(255),
    parent_task_id UUID REFERENCES tasks(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_field ON tasks(field_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_date);

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
-- SECTION 10: MARKETPLACE TABLES
-- ─────────────────────────────────────────────────────────────────────────────

-- Products (المنتجات)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    seller_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    category product_category NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'SAR',
    stock INTEGER DEFAULT 0,
    unit VARCHAR(50),
    image_url VARCHAR(500),
    images TEXT[],
    seller_type seller_type DEFAULT 'farmer',
    seller_name VARCHAR(255),
    governorate VARCHAR(100),
    district VARCHAR(100),
    crop_type VARCHAR(100),
    harvest_date DATE,
    quality_grade VARCHAR(50),
    status product_status DEFAULT 'draft',
    featured BOOLEAN DEFAULT false,
    views_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_tenant ON products(tenant_id);
CREATE INDEX IF NOT EXISTS idx_products_seller ON products(seller_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);

-- Orders (الطلبات)
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    buyer_id UUID REFERENCES users(id),
    buyer_name VARCHAR(255),
    buyer_phone VARCHAR(50),
    buyer_email VARCHAR(255),
    subtotal DECIMAL(12,2) NOT NULL,
    delivery_fee DECIMAL(12,2) DEFAULT 0,
    service_fee DECIMAL(12,2) DEFAULT 0,
    discount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'SAR',
    status order_status DEFAULT 'pending',
    payment_status payment_status DEFAULT 'pending',
    payment_method VARCHAR(50),
    delivery_address TEXT,
    delivery_governorate VARCHAR(100),
    delivery_district VARCHAR(100),
    delivery_date DATE,
    delivery_notes TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number);

-- Order Items (عناصر الطلب)
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    seller_id UUID REFERENCES users(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

-- Wallets (المحافظ)
CREATE TABLE IF NOT EXISTS wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_type VARCHAR(50) DEFAULT 'farmer',
    balance DECIMAL(14,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'SAR',
    credit_score INTEGER DEFAULT 500,
    credit_tier credit_tier DEFAULT 'bronze',
    loan_limit DECIMAL(14,2) DEFAULT 0,
    current_loan DECIMAL(14,2) DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    kyc_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wallets_user ON wallets(user_id);

-- Transactions (المعاملات المالية)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id),
    type transaction_type NOT NULL,
    amount DECIMAL(14,2) NOT NULL,
    balance_after DECIMAL(14,2),
    currency VARCHAR(3) DEFAULT 'SAR',
    reference_id VARCHAR(255),
    reference_type VARCHAR(100),
    description VARCHAR(500),
    description_ar VARCHAR(500),
    status transaction_status DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_wallet ON transactions(wallet_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);

-- Loans (القروض)
CREATE TABLE IF NOT EXISTS loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    amount DECIMAL(14,2) NOT NULL,
    interest_rate DECIMAL(5,4) DEFAULT 0,
    total_due DECIMAL(14,2) NOT NULL,
    paid_amount DECIMAL(14,2) DEFAULT 0,
    term_months INTEGER DEFAULT 12,
    start_date DATE,
    due_date DATE,
    purpose loan_purpose,
    purpose_details TEXT,
    collateral_type VARCHAR(100),
    collateral_value DECIMAL(14,2),
    status loan_status DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_loans_wallet ON loans(wallet_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);

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
-- Demo data has been moved to: 03-demo-data.sql
--
-- This separation allows:
-- - Clean schema-only deployments for production
-- - Easy removal of demo data by deleting/renaming the file
-- - Better security practices (no hardcoded passwords in production)
--
-- For development: Keep 03-demo-data.sql as-is
-- For production:  Rename 03-demo-data.sql to 03-demo-data.sql.bak or delete it

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
