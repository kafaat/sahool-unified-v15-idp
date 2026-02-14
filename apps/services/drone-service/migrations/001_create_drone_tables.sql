-- Migration: 001_create_drone_tables
-- Description: Create drone management tables - إنشاء جداول إدارة الطائرات المسيرة
-- Service: drone-service
-- Date: 2026-02-14

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- Drones - الطائرات المسيرة
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS drones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,

    -- Identification - التعريف
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    model VARCHAR(200) NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    drone_type VARCHAR(50) NOT NULL DEFAULT 'custom',

    -- Specifications - المواصفات
    max_payload_kg DECIMAL(6, 2),
    tank_capacity_l DECIMAL(6, 2),
    max_flight_time_min DECIMAL(6, 1),

    -- Status - الحالة
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    battery_percent DECIMAL(5, 2) DEFAULT 100.0,
    total_flight_hours DECIMAL(10, 2) DEFAULT 0.0,

    -- Timestamps - الطوابع الزمنية
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_maintenance_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_drone_status CHECK (status IN ('active', 'maintenance', 'grounded', 'retired')),
    CONSTRAINT valid_drone_type CHECK (drone_type IN ('custom', 'dji', 'xag', 'hylio', 'spray', 'mapping', 'survey')),
    CONSTRAINT valid_battery CHECK (battery_percent >= 0 AND battery_percent <= 100),
    CONSTRAINT unique_serial_number UNIQUE (serial_number)
);

COMMENT ON TABLE drones IS 'Registered drone fleet - أسطول الطائرات المسجلة';

CREATE INDEX IF NOT EXISTS idx_drones_tenant_id ON drones(tenant_id);
CREATE INDEX IF NOT EXISTS idx_drones_status ON drones(status);
CREATE INDEX IF NOT EXISTS idx_drones_tenant_status ON drones(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_drones_serial ON drones(serial_number);

-- ─────────────────────────────────────────────────────────────────────────────
-- Flight Plans - خطط الرحلات
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS flight_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    field_id VARCHAR(100),

    -- Plan Details - تفاصيل الخطة
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    plan_type VARCHAR(20) NOT NULL DEFAULT 'spray',
    success BOOLEAN DEFAULT TRUE,

    -- Flight Parameters - معلمات الرحلة
    altitude_m DECIMAL(6, 1),
    swath_width_m DECIMAL(5, 1),
    spray_rate_l_ha DECIMAL(6, 2),
    overlap_percent DECIMAL(5, 2),
    sidelap_percent DECIMAL(5, 2),

    -- Results - النتائج
    total_distance_m DECIMAL(10, 2),
    estimated_duration_min DECIMAL(8, 2),
    waypoints_count INTEGER DEFAULT 0,
    total_spray_volume_l DECIMAL(10, 2),
    area_ha DECIMAL(10, 4),

    -- Waypoints Data - بيانات نقاط المسار
    waypoints JSONB DEFAULT '[]'::jsonb,
    boundary JSONB,

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_plan_type CHECK (plan_type IN ('spray', 'mapping', 'survey', 'inspection'))
);

COMMENT ON TABLE flight_plans IS 'Flight plans for drone operations - خطط الرحلات لعمليات الطائرات';

CREATE INDEX IF NOT EXISTS idx_flight_plans_tenant_id ON flight_plans(tenant_id);
CREATE INDEX IF NOT EXISTS idx_flight_plans_field_id ON flight_plans(field_id);
CREATE INDEX IF NOT EXISTS idx_flight_plans_type ON flight_plans(plan_type);
CREATE INDEX IF NOT EXISTS idx_flight_plans_created ON flight_plans(created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- Missions - المهام
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS missions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    drone_id UUID REFERENCES drones(id) ON DELETE SET NULL,
    flight_plan_id UUID REFERENCES flight_plans(id) ON DELETE SET NULL,

    -- Mission Details - تفاصيل المهمة
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    mission_type VARCHAR(30) NOT NULL DEFAULT 'spray',
    field_id VARCHAR(100),

    -- Status & Progress - الحالة والتقدم
    status VARCHAR(20) NOT NULL DEFAULT 'planned',
    progress_percent DECIMAL(5, 2) DEFAULT 0.0,

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT valid_mission_status CHECK (status IN ('planned', 'active', 'paused', 'completed', 'aborted')),
    CONSTRAINT valid_mission_type CHECK (mission_type IN ('spray', 'mapping', 'survey', 'inspection', 'monitoring')),
    CONSTRAINT valid_progress CHECK (progress_percent >= 0 AND progress_percent <= 100)
);

COMMENT ON TABLE missions IS 'Drone mission records - سجلات مهام الطائرات';

CREATE INDEX IF NOT EXISTS idx_missions_tenant_id ON missions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_missions_drone_id ON missions(drone_id);
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_tenant_status ON missions(tenant_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_missions_field_id ON missions(field_id);

-- Updated_at Triggers - مشغلات تحديث التاريخ
CREATE OR REPLACE FUNCTION update_drone_tables_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_drones_updated_at
    BEFORE UPDATE ON drones
    FOR EACH ROW
    EXECUTE FUNCTION update_drone_tables_updated_at();

CREATE TRIGGER trigger_flight_plans_updated_at
    BEFORE UPDATE ON flight_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_drone_tables_updated_at();

CREATE TRIGGER trigger_missions_updated_at
    BEFORE UPDATE ON missions
    FOR EACH ROW
    EXECUTE FUNCTION update_drone_tables_updated_at();

-- Migration tracking
INSERT INTO public._migrations (name) VALUES ('001_create_drone_tables')
ON CONFLICT (name) DO NOTHING;
