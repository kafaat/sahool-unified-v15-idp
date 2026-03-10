-- SAHOOL Field Core - Add Farms Table and farm_id FK
-- Fixes missing farms table from initial migration

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. Create Farms Table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    owner_id UUID,

    -- Geospatial (PostGIS)
    location geometry(Point, 4326),
    boundary geometry(Polygon, 4326),

    -- Farm Details
    total_area_hectares DECIMAL(10, 4),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),

    -- Status
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for Farms
CREATE INDEX IF NOT EXISTS idx_farm_tenant ON farms(tenant_id);
CREATE INDEX IF NOT EXISTS idx_farm_tenant_active ON farms(tenant_id, is_deleted);
CREATE INDEX IF NOT EXISTS idx_farm_owner ON farms(owner_id);
CREATE INDEX IF NOT EXISTS idx_farm_created ON farms(created_at);

-- Triggers for Farms
CREATE TRIGGER update_farms_updated_at
    BEFORE UPDATE ON farms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE farms IS 'Farms that contain multiple agricultural fields';

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. Add farm_id column to fields table
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE fields ADD COLUMN IF NOT EXISTS farm_id UUID;

-- Add FK constraint (NOT VALID to avoid full table scan, validated in 20260303 remediation)
-- drift:safe reason=not-valid-pattern remediated_by=20260303000000_safe_index_remediation
ALTER TABLE fields ADD CONSTRAINT fk_fields_farm_id
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE SET NULL NOT VALID;

-- Add index (on existing table; remediated with CONCURRENTLY in 20260303)
-- drift:safe reason=remediated remediated_by=20260303000000_safe_index_remediation
CREATE INDEX IF NOT EXISTS idx_field_farm ON fields(farm_id);

-- Composite indexes for common queries (on existing table; remediated with CONCURRENTLY in 20260303)
-- drift:safe reason=remediated remediated_by=20260303000000_safe_index_remediation
CREATE INDEX IF NOT EXISTS idx_field_tenant_status ON fields(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_field_tenant_crop ON fields(tenant_id, crop_type);
CREATE INDEX IF NOT EXISTS idx_field_tenant_active ON fields(tenant_id, is_deleted);
CREATE INDEX IF NOT EXISTS idx_field_owner ON fields(owner_id);
CREATE INDEX IF NOT EXISTS idx_field_planting ON fields(planting_date);
CREATE INDEX IF NOT EXISTS idx_field_harvest ON fields(expected_harvest);
