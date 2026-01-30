-- Migration: Create Disaster Management Tables
-- جداول إدارة الكوارث
-- Required by disaster-assessment service

-- ============================================================================
-- Disaster Reports Table
-- جدول تقارير الكوارث
-- ============================================================================
CREATE TABLE IF NOT EXISTS disaster_reports (
    -- Identity
    id VARCHAR(50) PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,

    -- Classification
    type VARCHAR(50) NOT NULL,  -- flood, drought, pest, disease, fire, storm, earthquake
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',  -- low, medium, high, critical
    status VARCHAR(20) NOT NULL DEFAULT 'reported',  -- reported, verified, active, resolved, closed

    -- Title (bilingual)
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),

    -- Description (bilingual)
    description TEXT,
    description_ar TEXT,

    -- Location information
    governorate VARCHAR(100),
    district VARCHAR(100),
    location GEOGRAPHY(POINT, 4326),
    affected_radius_km NUMERIC(10, 2),
    affected_area GEOGRAPHY(POLYGON, 4326),

    -- Impact assessment
    affected_fields_count INTEGER DEFAULT 0,
    total_affected_area_hectares NUMERIC(12, 2) DEFAULT 0,
    total_estimated_loss_yer NUMERIC(15, 2) DEFAULT 0,  -- Yemeni Rial

    -- Reporting
    reported_by VARCHAR(100),

    -- Timeline
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,

    -- Media
    images JSONB DEFAULT '[]'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for disaster_reports
CREATE INDEX IF NOT EXISTS ix_disaster_reports_tenant ON disaster_reports(tenant_id);
CREATE INDEX IF NOT EXISTS ix_disaster_reports_type ON disaster_reports(type);
CREATE INDEX IF NOT EXISTS ix_disaster_reports_severity ON disaster_reports(severity);
CREATE INDEX IF NOT EXISTS ix_disaster_reports_status ON disaster_reports(status);
CREATE INDEX IF NOT EXISTS ix_disaster_reports_governorate ON disaster_reports(governorate);
CREATE INDEX IF NOT EXISTS ix_disaster_reports_dates ON disaster_reports(start_date, end_date);
CREATE INDEX IF NOT EXISTS ix_disaster_reports_location ON disaster_reports USING GIST(location);

-- ============================================================================
-- Disaster Alerts Table
-- جدول تنبيهات الكوارث
-- ============================================================================
CREATE TABLE IF NOT EXISTS disaster_alerts (
    -- Identity
    id VARCHAR(50) PRIMARY KEY,
    disaster_report_id VARCHAR(50) REFERENCES disaster_reports(id) ON DELETE CASCADE,
    tenant_id VARCHAR(100) NOT NULL,

    -- Alert details
    alert_type VARCHAR(50) NOT NULL,  -- warning, evacuation, advisory, update, all_clear
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',

    -- Message (bilingual)
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    message TEXT NOT NULL,
    message_ar TEXT,

    -- Target audience
    target_governorates VARCHAR[],
    target_districts VARCHAR[],
    target_user_ids VARCHAR[],

    -- Alert boundaries
    alert_area GEOGRAPHY(POLYGON, 4326),

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Delivery tracking
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    read_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for disaster_alerts
CREATE INDEX IF NOT EXISTS ix_disaster_alerts_tenant ON disaster_alerts(tenant_id);
CREATE INDEX IF NOT EXISTS ix_disaster_alerts_report ON disaster_alerts(disaster_report_id);
CREATE INDEX IF NOT EXISTS ix_disaster_alerts_type ON disaster_alerts(alert_type);
CREATE INDEX IF NOT EXISTS ix_disaster_alerts_active ON disaster_alerts(is_active, expires_at);
CREATE INDEX IF NOT EXISTS ix_disaster_alerts_area ON disaster_alerts USING GIST(alert_area);

-- ============================================================================
-- Disaster Affected Fields Table (Junction)
-- جدول الحقول المتأثرة
-- ============================================================================
CREATE TABLE IF NOT EXISTS disaster_affected_fields (
    id VARCHAR(50) PRIMARY KEY,
    disaster_report_id VARCHAR(50) REFERENCES disaster_reports(id) ON DELETE CASCADE,
    field_id VARCHAR(100) NOT NULL,

    -- Impact assessment
    damage_percent NUMERIC(5, 2) DEFAULT 0,
    estimated_loss_yer NUMERIC(15, 2) DEFAULT 0,
    crop_type VARCHAR(100),
    crop_stage VARCHAR(50),

    -- Status
    status VARCHAR(20) DEFAULT 'affected',  -- affected, recovering, recovered

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_affected_fields_disaster ON disaster_affected_fields(disaster_report_id);
CREATE INDEX IF NOT EXISTS ix_affected_fields_field ON disaster_affected_fields(field_id);

-- ============================================================================
-- Triggers for updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_disaster_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_disaster_reports_updated_at ON disaster_reports;
CREATE TRIGGER update_disaster_reports_updated_at
    BEFORE UPDATE ON disaster_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_disaster_updated_at_column();

DROP TRIGGER IF EXISTS update_disaster_alerts_updated_at ON disaster_alerts;
CREATE TRIGGER update_disaster_alerts_updated_at
    BEFORE UPDATE ON disaster_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_disaster_updated_at_column();

DROP TRIGGER IF EXISTS update_disaster_affected_fields_updated_at ON disaster_affected_fields;
CREATE TRIGGER update_disaster_affected_fields_updated_at
    BEFORE UPDATE ON disaster_affected_fields
    FOR EACH ROW
    EXECUTE FUNCTION update_disaster_updated_at_column();

-- ============================================================================
-- Verification
-- ============================================================================
SELECT 'Disaster management tables created successfully!' AS status;
