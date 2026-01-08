-- SAHOOL Notification Service - Farmer Profile Tables Migration
-- Migration: Add farmer_profiles, farmer_crops, and farmer_fields tables
-- Date: 2026-01-08
-- Purpose: Migrate farmer data from in-memory storage to PostgreSQL

-- ============================================================================
-- Table: farmer_profiles
-- Description: Stores main farmer information for personalized notifications
-- ============================================================================
CREATE TABLE IF NOT EXISTS farmer_profiles (
    id UUID PRIMARY KEY,
    tenant_id VARCHAR(100),
    farmer_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    governorate VARCHAR(50) NOT NULL,
    district VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    fcm_token VARCHAR(500),
    language VARCHAR(5) DEFAULT 'ar',
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for farmer_profiles
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_tenant_id ON farmer_profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_farmer_id ON farmer_profiles(farmer_id);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_governorate ON farmer_profiles(governorate);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_is_active ON farmer_profiles(is_active);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_tenant_farmer ON farmer_profiles(tenant_id, farmer_id);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_gov_active ON farmer_profiles(governorate, is_active);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_created_at ON farmer_profiles(created_at);

-- ============================================================================
-- Table: farmer_crops
-- Description: Junction table linking farmers to their crops
-- ============================================================================
CREATE TABLE IF NOT EXISTS farmer_crops (
    id UUID PRIMARY KEY,
    farmer_id UUID NOT NULL REFERENCES farmer_profiles(id) ON DELETE CASCADE,
    crop_type VARCHAR(50) NOT NULL,
    area_hectares FLOAT,
    planting_date DATE,
    harvest_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(farmer_id, crop_type)
);

-- Indexes for farmer_crops
CREATE INDEX IF NOT EXISTS idx_farmer_crops_farmer_id ON farmer_crops(farmer_id);
CREATE INDEX IF NOT EXISTS idx_farmer_crops_crop_type ON farmer_crops(crop_type);
CREATE INDEX IF NOT EXISTS idx_farmer_crops_is_active ON farmer_crops(is_active);
CREATE INDEX IF NOT EXISTS idx_farmer_crops_crop_active ON farmer_crops(crop_type, is_active);

-- ============================================================================
-- Table: farmer_fields
-- Description: Junction table linking farmers to their field IDs
-- ============================================================================
CREATE TABLE IF NOT EXISTS farmer_fields (
    id UUID PRIMARY KEY,
    farmer_id UUID NOT NULL REFERENCES farmer_profiles(id) ON DELETE CASCADE,
    field_id VARCHAR(100) NOT NULL,
    field_name VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(farmer_id, field_id)
);

-- Indexes for farmer_fields
CREATE INDEX IF NOT EXISTS idx_farmer_fields_farmer_id ON farmer_fields(farmer_id);
CREATE INDEX IF NOT EXISTS idx_farmer_fields_field_id ON farmer_fields(field_id);
CREATE INDEX IF NOT EXISTS idx_farmer_fields_is_active ON farmer_fields(is_active);
CREATE INDEX IF NOT EXISTS idx_farmer_fields_field_active ON farmer_fields(field_id, is_active);

-- ============================================================================
-- Triggers for updated_at timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for farmer_profiles
DROP TRIGGER IF EXISTS update_farmer_profiles_updated_at ON farmer_profiles;
CREATE TRIGGER update_farmer_profiles_updated_at
    BEFORE UPDATE ON farmer_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for farmer_crops
DROP TRIGGER IF EXISTS update_farmer_crops_updated_at ON farmer_crops;
CREATE TRIGGER update_farmer_crops_updated_at
    BEFORE UPDATE ON farmer_crops
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for farmer_fields
DROP TRIGGER IF EXISTS update_farmer_fields_updated_at ON farmer_fields;
CREATE TRIGGER update_farmer_fields_updated_at
    BEFORE UPDATE ON farmer_fields
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample data:
-- INSERT INTO farmer_profiles (id, farmer_id, name, name_ar, governorate, district, phone, email, language)
-- VALUES
--     (gen_random_uuid(), 'test-farmer-1', 'Ahmed Ali', 'أحمد علي', 'sanaa', 'Bani Harith', '+967771234567', 'ahmed.ali@example.com', 'ar'),
--     (gen_random_uuid(), 'test-farmer-2', 'Mohammed Hassan', 'محمد حسن', 'ibb', 'Ibb City', '+967772345678', 'mohammed.hassan@example.com', 'ar');

-- ============================================================================
-- Rollback Script
-- ============================================================================
-- To rollback this migration, run:
-- DROP TABLE IF EXISTS farmer_fields CASCADE;
-- DROP TABLE IF EXISTS farmer_crops CASCADE;
-- DROP TABLE IF EXISTS farmer_profiles CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column();

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- After running this migration, verify with:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'farmer_%';
-- SELECT COUNT(*) FROM farmer_profiles;
-- SELECT COUNT(*) FROM farmer_crops;
-- SELECT COUNT(*) FROM farmer_fields;
