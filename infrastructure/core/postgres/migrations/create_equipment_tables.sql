-- Equipment Service Schema Creation
-- Creates equipment, equipment_maintenance, and equipment_alerts tables with correct schema

-- ============================================================================
-- Equipment Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment (
    -- Identity
    equipment_id VARCHAR(50) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,

    -- Basic information (bilingual)
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),

    -- Equipment classification
    equipment_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'operational',

    -- Equipment details
    brand VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    year INTEGER,

    -- Purchase information
    purchase_date TIMESTAMP WITH TIME ZONE,
    purchase_price NUMERIC(12, 2),

    -- Location information
    field_id VARCHAR(100),
    location_name VARCHAR(200),

    -- Specifications
    horsepower INTEGER,
    fuel_capacity_liters NUMERIC(8, 2),

    -- Telemetry data
    current_fuel_percent NUMERIC(5, 2),
    current_hours NUMERIC(10, 2),
    current_lat NUMERIC(10, 7),
    current_lon NUMERIC(10, 7),

    -- Maintenance scheduling
    last_maintenance_at TIMESTAMP WITH TIME ZONE,
    next_maintenance_at TIMESTAMP WITH TIME ZONE,
    next_maintenance_hours NUMERIC(10, 2),

    -- QR code for easy identification
    qr_code VARCHAR(100) UNIQUE,

    -- Additional metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for equipment table
CREATE INDEX IF NOT EXISTS ix_equipment_tenant_status ON equipment (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_equipment_type_status ON equipment (equipment_type, status);
CREATE INDEX IF NOT EXISTS ix_equipment_field_status ON equipment (field_id, status);
CREATE INDEX IF NOT EXISTS ix_equipment_next_maintenance ON equipment (next_maintenance_at);
CREATE INDEX IF NOT EXISTS ix_equipment_tenant_id ON equipment (tenant_id);
CREATE INDEX IF NOT EXISTS ix_equipment_equipment_type ON equipment (equipment_type);

-- ============================================================================
-- Equipment Maintenance Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment_maintenance (
    -- Identity
    record_id VARCHAR(50) PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,

    -- Maintenance details
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    description_ar TEXT,

    -- Who and when
    performed_by VARCHAR(100),
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Cost tracking
    cost NUMERIC(10, 2),

    -- Additional details
    notes TEXT,
    parts_replaced VARCHAR []
);

-- Indexes for equipment_maintenance table
CREATE INDEX IF NOT EXISTS ix_maintenance_equipment_date ON equipment_maintenance (equipment_id, performed_at);
CREATE INDEX IF NOT EXISTS ix_maintenance_type ON equipment_maintenance (maintenance_type, performed_at);

-- ============================================================================
-- Equipment Alerts Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS equipment_alerts (
    -- Identity
    alert_id VARCHAR(50) PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,
    equipment_name VARCHAR(200) NOT NULL,

    -- Alert details
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    description_ar TEXT,

    -- Priority
    priority VARCHAR(20) NOT NULL,

    -- Due dates
    due_at TIMESTAMP WITH TIME ZONE,
    due_hours NUMERIC(10, 2),

    -- Status
    is_overdue BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for equipment_alerts table
CREATE INDEX IF NOT EXISTS ix_alerts_overdue ON equipment_alerts (is_overdue, priority);
CREATE INDEX IF NOT EXISTS ix_alerts_equipment_due ON equipment_alerts (equipment_id, due_at);

-- ============================================================================
-- Triggers for updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION UPDATE_EQUIPMENT_UPDATED_AT_COLUMN()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_equipment_updated_at ON equipment;
CREATE TRIGGER update_equipment_updated_at
BEFORE UPDATE ON equipment
FOR EACH ROW
EXECUTE FUNCTION UPDATE_EQUIPMENT_UPDATED_AT_COLUMN();

-- Verification
SELECT 'Equipment tables created successfully!' AS status;
SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name IN ('equipment', 'equipment_maintenance', 'equipment_alerts')
ORDER BY table_name, ordinal_position;
