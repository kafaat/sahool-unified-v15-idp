-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Disaster Management Tables
-- جداول إدارة الكوارث
-- ═══════════════════════════════════════════════════════════════════════════════

-- Disaster Reports Table
CREATE TABLE IF NOT EXISTS public.disaster_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    
    -- Classification
    type VARCHAR(50) NOT NULL, -- drought, flood, pest, disease, frost, hail, fire
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    status VARCHAR(20) NOT NULL DEFAULT 'reported', -- reported, verified, active, resolved
    
    -- Bilingual information
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    
    -- Location
    governorate VARCHAR(100),
    district VARCHAR(100),
    location GEOMETRY(Point, 4326),
    
    -- Impact assessment
    affected_radius_km NUMERIC(10, 2),
    affected_area GEOMETRY(MultiPolygon, 4326),
    affected_fields_count INTEGER DEFAULT 0,
    total_affected_area_hectares NUMERIC(12, 2),
    total_estimated_loss_yer NUMERIC(15, 2),
    
    -- Reporting
    reported_by UUID, -- user_id
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Media
    images TEXT[], -- Array of image URLs
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Disaster Alerts Table
CREATE TABLE IF NOT EXISTS public.disaster_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disaster_report_id UUID REFERENCES public.disaster_reports(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    
    -- Alert details
    alert_type VARCHAR(50) NOT NULL, -- warning, critical, advisory
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    message TEXT NOT NULL,
    message_ar TEXT,
    
    -- Target audience
    target_governorates VARCHAR(100)[],
    target_districts VARCHAR(100)[],
    target_user_ids UUID[],
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, expired, cancelled
    priority VARCHAR(20) NOT NULL DEFAULT 'medium', -- low, medium, high, critical
    
    -- Timing
    expires_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Delivery tracking
    total_recipients INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    read_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for disaster_reports
CREATE INDEX IF NOT EXISTS idx_disaster_reports_tenant ON public.disaster_reports(tenant_id);
CREATE INDEX IF NOT EXISTS idx_disaster_reports_type_status ON public.disaster_reports(type, status);
CREATE INDEX IF NOT EXISTS idx_disaster_reports_severity ON public.disaster_reports(severity);
CREATE INDEX IF NOT EXISTS idx_disaster_reports_location ON public.disaster_reports USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_disaster_reports_affected_area ON public.disaster_reports USING GIST(affected_area);
CREATE INDEX IF NOT EXISTS idx_disaster_reports_created_at ON public.disaster_reports(created_at DESC);

-- Indexes for disaster_alerts
CREATE INDEX IF NOT EXISTS idx_disaster_alerts_tenant ON public.disaster_alerts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_disaster_alerts_report ON public.disaster_alerts(disaster_report_id);
CREATE INDEX IF NOT EXISTS idx_disaster_alerts_status_priority ON public.disaster_alerts(status, priority);
CREATE INDEX IF NOT EXISTS idx_disaster_alerts_expires_at ON public.disaster_alerts(expires_at);
CREATE INDEX IF NOT EXISTS idx_disaster_alerts_created_at ON public.disaster_alerts(created_at DESC);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_disaster_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_disaster_reports_updated_at ON public.disaster_reports;
CREATE TRIGGER update_disaster_reports_updated_at
    BEFORE UPDATE ON public.disaster_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_disaster_updated_at();

DROP TRIGGER IF EXISTS update_disaster_alerts_updated_at ON public.disaster_alerts;
CREATE TRIGGER update_disaster_alerts_updated_at
    BEFORE UPDATE ON public.disaster_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_disaster_updated_at();

-- Verification
SELECT 'Disaster management tables created successfully!' AS status;
