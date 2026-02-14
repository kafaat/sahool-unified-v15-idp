-- Migration: 001_create_cooperative_tables
-- Description: Create cooperative management tables - إنشاء جداول إدارة التعاونيات
-- Service: cooperative-service
-- Date: 2026-02-14

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- Cooperatives - التعاونيات
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cooperatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,

    -- Details - التفاصيل
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    description TEXT,
    description_ar TEXT,
    type VARCHAR(30) NOT NULL DEFAULT 'multi_purpose',
    region VARCHAR(100),

    -- Status - الحالة
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    member_count INTEGER DEFAULT 0,

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_coop_type CHECK (type IN ('multi_purpose', 'marketing', 'production', 'service', 'supply', 'credit')),
    CONSTRAINT valid_coop_status CHECK (status IN ('active', 'suspended', 'dissolved'))
);

COMMENT ON TABLE cooperatives IS 'Agricultural cooperatives - التعاونيات الزراعية';

CREATE INDEX IF NOT EXISTS idx_cooperatives_tenant_id ON cooperatives(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cooperatives_status ON cooperatives(status);
CREATE INDEX IF NOT EXISTS idx_cooperatives_tenant_status ON cooperatives(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_cooperatives_region ON cooperatives(region);

-- ─────────────────────────────────────────────────────────────────────────────
-- Cooperative Members - أعضاء التعاونية
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cooperative_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID NOT NULL REFERENCES cooperatives(id) ON DELETE CASCADE,
    farmer_id VARCHAR(100) NOT NULL,

    -- Member Details - تفاصيل العضو
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    phone VARCHAR(30),
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    share_count INTEGER DEFAULT 1,
    land_area_ha DECIMAL(10, 4) DEFAULT 0.0,

    -- Status - الحالة
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- Timestamps - الطوابع الزمنية
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_member_role CHECK (role IN ('chairman', 'treasurer', 'secretary', 'board', 'member', 'observer')),
    CONSTRAINT valid_member_status CHECK (status IN ('active', 'suspended', 'withdrawn', 'expelled')),
    CONSTRAINT valid_share_count CHECK (share_count >= 0),
    CONSTRAINT unique_coop_farmer UNIQUE (cooperative_id, farmer_id)
);

COMMENT ON TABLE cooperative_members IS 'Cooperative membership records - سجلات عضوية التعاونية';

CREATE INDEX IF NOT EXISTS idx_coop_members_cooperative ON cooperative_members(cooperative_id);
CREATE INDEX IF NOT EXISTS idx_coop_members_farmer ON cooperative_members(farmer_id);
CREATE INDEX IF NOT EXISTS idx_coop_members_status ON cooperative_members(status);

-- ─────────────────────────────────────────────────────────────────────────────
-- Shared Resources - الموارد المشتركة
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shared_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID NOT NULL REFERENCES cooperatives(id) ON DELETE CASCADE,

    -- Resource Details - تفاصيل المورد
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    type VARCHAR(30) NOT NULL DEFAULT 'equipment',
    model VARCHAR(200),
    capacity DECIMAL(10, 2),
    capacity_unit VARCHAR(30),
    hourly_rate DECIMAL(10, 2) DEFAULT 0.0,

    -- Status - الحالة
    status VARCHAR(20) NOT NULL DEFAULT 'available',

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_resource_type CHECK (type IN ('equipment', 'storage', 'transport', 'processing', 'irrigation', 'land', 'seeds', 'fertilizer', 'pesticide')),
    CONSTRAINT valid_resource_status CHECK (status IN ('available', 'in_use', 'maintenance', 'retired'))
);

COMMENT ON TABLE shared_resources IS 'Cooperative shared resources - الموارد المشتركة للتعاونية';

CREATE INDEX IF NOT EXISTS idx_shared_resources_cooperative ON shared_resources(cooperative_id);
CREATE INDEX IF NOT EXISTS idx_shared_resources_status ON shared_resources(status);
CREATE INDEX IF NOT EXISTS idx_shared_resources_type ON shared_resources(type);

-- ─────────────────────────────────────────────────────────────────────────────
-- Resource Bookings - حجوزات الموارد
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resource_bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_id UUID NOT NULL REFERENCES shared_resources(id) ON DELETE CASCADE,
    member_id UUID NOT NULL REFERENCES cooperative_members(id) ON DELETE CASCADE,

    -- Booking Details - تفاصيل الحجز
    purpose TEXT NOT NULL,
    purpose_ar TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_hours DECIMAL(6, 2) DEFAULT 4.0,
    cost DECIMAL(10, 2) DEFAULT 0.0,

    -- Status - الحالة
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_booking_status CHECK (status IN ('pending', 'confirmed', 'in_use', 'completed', 'cancelled'))
);

COMMENT ON TABLE resource_bookings IS 'Resource booking records - سجلات حجز الموارد';

CREATE INDEX IF NOT EXISTS idx_bookings_resource ON resource_bookings(resource_id);
CREATE INDEX IF NOT EXISTS idx_bookings_member ON resource_bookings(member_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON resource_bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_start_time ON resource_bookings(start_time);

-- Updated_at Triggers - مشغلات تحديث التاريخ
CREATE OR REPLACE FUNCTION update_cooperative_tables_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_cooperatives_updated_at
    BEFORE UPDATE ON cooperatives
    FOR EACH ROW
    EXECUTE FUNCTION update_cooperative_tables_updated_at();

CREATE TRIGGER trigger_coop_members_updated_at
    BEFORE UPDATE ON cooperative_members
    FOR EACH ROW
    EXECUTE FUNCTION update_cooperative_tables_updated_at();

CREATE TRIGGER trigger_shared_resources_updated_at
    BEFORE UPDATE ON shared_resources
    FOR EACH ROW
    EXECUTE FUNCTION update_cooperative_tables_updated_at();

CREATE TRIGGER trigger_bookings_updated_at
    BEFORE UPDATE ON resource_bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_cooperative_tables_updated_at();

-- Migration tracking
INSERT INTO public._migrations (name) VALUES ('001_create_cooperative_tables')
ON CONFLICT (name) DO NOTHING;
