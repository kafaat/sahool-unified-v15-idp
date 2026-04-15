-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform v15.3 - Complete Database Initialization
-- منصة سهول - تهيئة قاعدة البيانات الكاملة
-- ═══════════════════════════════════════════════════════════════════════════════
-- Generated: 2025
-- Admin User: n@admin.com / admin
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- NOTE: The following tables are managed by Prisma ORM and are NOT created here.
-- Each NestJS service runs `prisma migrate deploy` on startup to create its own tables:
--   - user-service: users, user_profiles, user_roles, user_sessions, refresh_tokens, etc.
--   - field-management-service: fields, farms, field_boundary_history, tasks, ndvi_readings, sync_status, etc.
--   - marketplace-service: products, orders, wallets, transactions, loans, etc.
--   - disaster-assessment: disaster_alerts, disaster_zones, damage_assessments, etc.
--   - research-core: experiments, research_protocols, research_plots, treatments, etc.
--   - chat-service: conversations, messages, participants, etc.
--   - iot-service: devices, sensors, actuators, sensor_readings, etc.
--   - weather-service: weather_observations, weather_forecasts, weather_alerts, location_configs
--
-- Tables in THIS file are used by Python services (FastAPI/SQLAlchemy/Tortoise) which
-- use Base.metadata.create_all() or generate_schemas() and need tables pre-created.
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
-- Only enums used by Python services and non-Prisma tables.
-- Prisma-managed enums (UserRole, UserStatus, field_status, irrigation_type,
-- soil_type, crop_status, growth_stage, task_type, task_status, task_priority,
-- device_type, device_status, sync_state, change_source, experiment_status,
-- treatment_type, sample_type, log_category, scope_type, message_type,
-- ndvi_classification, ndvi_trend, and all marketplace enums) are created
-- by their respective services via `prisma migrate deploy`.
-- ─────────────────────────────────────────────────────────────────────────────

-- Legacy user_role enum for backward compatibility with Python services
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'manager', 'agronomist', 'field_worker', 'researcher', 'viewer');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE subscription_tier AS ENUM ('free', 'basic', 'professional', 'enterprise');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE subscription_status AS ENUM ('active', 'trial', 'suspended', 'cancelled', 'expired');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Alert Enums (used by Python alert-service)
DO $$ BEGIN
    CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'critical', 'emergency');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE alert_status AS ENUM ('active', 'acknowledged', 'resolved', 'expired', 'dismissed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE alert_category AS ENUM ('weather', 'pest', 'disease', 'irrigation', 'harvest', 'equipment', 'market', 'system');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 3: CORE TABLES (Non-Prisma only)
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

-- Users, user_profiles, user_roles, user_sessions, refresh_tokens:
-- REMOVED - Now managed by Prisma ORM (user-service runs `prisma migrate deploy` on startup)
-- See: apps/services/user-service/prisma/schema.prisma

-- Crops Master Data (المحاصيل)
-- Kept here as shared reference data used by multiple Python services
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

-- Fields, field_boundary_history, field_crops:
-- REMOVED - Now managed by Prisma ORM (field-management-service runs `prisma migrate deploy` on startup)
-- See: apps/services/field-management-service/prisma/schema.prisma

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 4: NDVI & SATELLITE TABLES - REMOVED
-- Now managed by Prisma ORM (field-management-service or vegetation-analysis-service)
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 5: WEATHER TABLES - REMOVED
-- Now managed by Prisma ORM (weather-service runs `prisma migrate deploy` on startup)
-- See: apps/services/weather-service/prisma/schema.prisma
--
-- This init script previously created weather_records and weather_forecasts tables
-- with a different schema (UUID tenant_id, DATE/TIME columns, flat structure)
-- which conflicted with the Prisma-managed schema (VARCHAR tenant_id, DATETIME,
-- JSON forecast data, weather_observations table name).
--
-- Prisma migrations are the single source of truth for:
--   - weather_observations (replaces weather_records)
--   - weather_forecasts (with forecastFor, hourlyData, dailyData columns)
--   - weather_alerts
--   - location_configs
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 6: TASKS & ACTIVITIES - REMOVED
-- Now managed by Prisma ORM (field-management-service runs `prisma migrate deploy` on startup)
-- See: apps/services/field-management-service/prisma/schema.prisma
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 7: ALERTS & NOTIFICATIONS
-- Kept: alert-service and notification-service are Python/FastAPI services
-- NOTE: FK references to users and fields tables have been removed because
-- those tables are now managed by Prisma (user-service, field-management-service)
-- and may not exist when this init script runs.
-- ─────────────────────────────────────────────────────────────────────────────

-- Alerts (التنبيهات)
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID,
    user_id UUID,
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
    acknowledged_by UUID,
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
    user_id UUID,
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
-- SECTION 8: IOT DEVICES & READINGS - REMOVED
-- Now managed by Prisma ORM (iot-service runs `prisma migrate deploy` on startup)
-- See: apps/services/iot-service/prisma/schema.prisma
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 9: SYNC & OFFLINE SUPPORT - REMOVED
-- Now managed by Prisma ORM (field-management-service runs `prisma migrate deploy` on startup)
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 10: MARKETPLACE TABLES - REMOVED
-- Now managed by Prisma ORM (marketplace-service runs `prisma migrate deploy` on startup)
-- See: apps/services/marketplace-service/prisma/schema.prisma
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 11: RESEARCH TABLES - REMOVED
-- Now managed by Prisma ORM (research-core runs `prisma migrate deploy` on startup)
-- See: apps/services/research-core/prisma/schema.prisma
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 12: CHAT TABLES - REMOVED
-- Now managed by Prisma ORM (chat-service runs `prisma migrate deploy` on startup)
-- See: apps/services/chat-service/prisma/schema.prisma
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 13: ASTRONOMICAL CALENDAR (أنواء)
-- Kept: astronomical-calendar is a Python/FastAPI service
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
-- Kept: audit-service and ai-advisor are Python/FastAPI services
-- NOTE: FK references to users and fields tables have been removed because
-- those tables are now managed by Prisma and may not exist at init time.
-- ─────────────────────────────────────────────────────────────────────────────

-- Audit Logs (سجلات التدقيق)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID,
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
    user_id UUID,
    field_id UUID,
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
-- Kept: equipment-service is a Python/FastAPI service
-- NOTE: FK references to users and fields tables have been removed because
-- those tables are now managed by Prisma and may not exist at init time.
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
    assigned_to UUID,
    assigned_field_id UUID,
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
    performed_by UUID,
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

-- Order number generation function (kept for future use by marketplace-service)
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

-- NOTE: Order number trigger is NOT applied here because the orders table
-- is now managed by Prisma (marketplace-service). The function is kept
-- for reference but the trigger must be created by the service if needed.

-- NOTE: calculate_field_area trigger is NOT applied here because the fields
-- table is now managed by Prisma (field-management-service).

-- ═══════════════════════════════════════════════════════════════════════════════
-- SECTION 17: DEMO DATA
-- ═══════════════════════════════════════════════════════════════════════════════
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║  SECURITY WARNING - FOR DEVELOPMENT/TESTING ONLY                            ║
-- ║                                                                               ║
-- ║  Demo data for Prisma-managed tables (users, fields, tasks, IoT devices,    ║
-- ║  experiments, etc.) should be inserted via each service's own seed mechanism ║
-- ║  or via `prisma db seed` after the services have run their migrations.      ║
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

-- Demo users: REMOVED - Now managed by Prisma ORM (user-service)
-- Demo fields: REMOVED - Now managed by Prisma ORM (field-management-service)
-- Demo field crops: REMOVED - Now managed by Prisma ORM (field-management-service)
-- Demo tasks: REMOVED - Now managed by Prisma ORM (field-management-service)
-- Demo NDVI records: REMOVED - Now managed by Prisma ORM (field-management-service)
-- Demo IoT devices: REMOVED - Now managed by Prisma ORM (iot-service)
-- Demo IoT readings: REMOVED - Now managed by Prisma ORM (iot-service)

-- Insert crops master data (shared reference data)
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

-- Insert demo alerts (field_id references are stored as UUIDs without FK constraint)
INSERT INTO alerts (id, tenant_id, field_id, title, title_ar, message, message_ar, category, severity, status)
VALUES
    ('00000000-0000-0000-0004-000000000001', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'Low Soil Moisture', 'انخفاض رطوبة التربة', 'Soil moisture in North Field has dropped below 40%', 'انخفضت رطوبة التربة في الحقل الشمالي إلى أقل من 40%', 'irrigation', 'warning', 'active'),
    ('00000000-0000-0000-0004-000000000002', 'a0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'High Temperature Alert', 'تنبيه درجة حرارة مرتفعة', 'Greenhouse temperature exceeds 38°C', 'درجة حرارة البيت المحمي تتجاوز 38 درجة مئوية', 'weather', 'critical', 'active'),
    ('00000000-0000-0000-0004-000000000003', 'a0000000-0000-0000-0000-000000000001', NULL, 'Harvest Season Reminder', 'تذكير موسم الحصاد', 'Wheat harvest season approaching in 30 days', 'يقترب موسم حصاد القمح خلال 30 يوماً', 'harvest', 'info', 'active')
ON CONFLICT DO NOTHING;

-- Demo marketplace data REMOVED: Tables now managed by Prisma (marketplace-service)
-- Demo experiments data REMOVED: Tables now managed by Prisma (research-core)

-- Insert demo Anwa events
INSERT INTO anwa_events (id, naw_id, naw_name_ar, naw_name_en, year, start_date, end_date, season, season_ar, suitable_crops, recommendations)
VALUES
    ('00000000-0000-0000-0008-000000000001', 1, 'الثريا', 'Al-Thurayya', 2025, '2025-06-07', '2025-06-19', 'summer', 'الصيف', '["dates", "grapes"]', '{"irrigation": "increase", "activities": ["harvest_dates"]}'),
    ('00000000-0000-0000-0008-000000000002', 2, 'الدبران', 'Al-Dabaran', 2025, '2025-06-20', '2025-07-02', 'summer', 'الصيف', '["dates", "melons"]', '{"irrigation": "maintain", "activities": ["protect_from_heat"]}'),
    ('00000000-0000-0000-0008-000000000003', 15, 'سعد الذابح', 'Saad Al-Thabeh', 2025, '2025-01-29', '2025-02-10', 'winter', 'الشتاء', '["wheat", "barley", "vegetables"]', '{"irrigation": "reduce", "activities": ["planting_grains"]}')
ON CONFLICT DO NOTHING;

-- Demo weather records: REMOVED - Tables now managed by Prisma ORM (weather-service)
-- Use weather-service seed mechanism for demo data.

-- ═══════════════════════════════════════════════════════════════════════════════
-- SECTION 18: GRANT PERMISSIONS
-- ═══════════════════════════════════════════════════════════════════════════════

-- Grant all privileges on all tables to sahool user
DO $$
BEGIN
    EXECUTE format('GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO %I', current_user);
    EXECUTE format('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO %I', current_user);
    EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO %I', current_user);

    -- Grant pg_monitor role for monitoring + pg_read_all_auth for auth_query access to pg_shadow
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
    RAISE NOTICE '  Tables created (init script): %', table_count;
    RAISE NOTICE '  Indexes created: %', index_count;
    RAISE NOTICE '  Functions created: %', function_count;
    RAISE NOTICE '';
    RAISE NOTICE '  NOTE: Additional tables will be created by NestJS services';
    RAISE NOTICE '  running `prisma migrate deploy` on startup (user-service,';
    RAISE NOTICE '  field-management-service, marketplace-service, iot-service,';
    RAISE NOTICE '  research-core, chat-service, disaster-assessment, weather-service).';
    RAISE NOTICE '';
    RAISE NOTICE '  Demo data is loaded separately from 03-demo-data.sql';
    RAISE NOTICE '  For production: Remove or rename 03-demo-data.sql';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
