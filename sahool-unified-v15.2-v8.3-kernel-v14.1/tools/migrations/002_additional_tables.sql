-- ============================================
-- SAHOOL Platform - Additional Tables Migration
-- الجداول الإضافية للخدمات الجديدة
-- ============================================

-- ============================================
-- WEATHER RECORDS
-- سجلات الطقس
-- ============================================

CREATE TABLE IF NOT EXISTS weather_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    location_id VARCHAR(100) NOT NULL,
    coordinates GEOMETRY(POINT, 4326),
    location_name VARCHAR(255),
    
    -- Weather Data
    temperature_celsius DECIMAL(5, 2),
    feels_like_celsius DECIMAL(5, 2),
    humidity_percent INTEGER,
    pressure_hpa INTEGER,
    wind_speed_ms DECIMAL(5, 2),
    wind_direction_degrees INTEGER,
    precipitation_mm DECIMAL(6, 2),
    precipitation_probability INTEGER,
    uv_index INTEGER,
    visibility_km DECIMAL(5, 2),
    cloud_coverage_percent INTEGER,
    
    -- Conditions
    conditions VARCHAR(100),
    conditions_ar VARCHAR(100),
    icon VARCHAR(20),
    
    -- Metadata
    recorded_at TIMESTAMP NOT NULL,
    source VARCHAR(50) DEFAULT 'weather-signal',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weather_tenant_location ON weather_records(tenant_id, location_id);
CREATE INDEX IF NOT EXISTS idx_weather_recorded_at ON weather_records(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_weather_coordinates ON weather_records USING GIST(coordinates);

-- ============================================
-- WEATHER FORECASTS
-- توقعات الطقس
-- ============================================

CREATE TABLE IF NOT EXISTS weather_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    location_id VARCHAR(100) NOT NULL,
    
    forecast_date DATE NOT NULL,
    temp_min_celsius DECIMAL(5, 2),
    temp_max_celsius DECIMAL(5, 2),
    humidity_percent INTEGER,
    precipitation_mm DECIMAL(6, 2),
    precipitation_probability INTEGER,
    conditions VARCHAR(100),
    conditions_ar VARCHAR(100),
    icon VARCHAR(20),
    
    fetched_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecast_location_date ON weather_forecasts(location_id, forecast_date);

-- ============================================
-- NDVI ANALYSES
-- تحليلات صور الأقمار الصناعية
-- ============================================

CREATE TABLE IF NOT EXISTS ndvi_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    
    -- Capture Info
    capture_date TIMESTAMP NOT NULL,
    satellite_source VARCHAR(50) DEFAULT 'sentinel-2',
    cloud_coverage INTEGER DEFAULT 0,
    
    -- NDVI Values
    ndvi_mean DECIMAL(5, 4),
    ndvi_min DECIMAL(5, 4),
    ndvi_max DECIMAL(5, 4),
    ndvi_std_dev DECIMAL(5, 4),
    
    -- Classification
    classification VARCHAR(20), -- poor, moderate, good, excellent
    change_from_previous DECIMAL(5, 4),
    change_trend VARCHAR(20), -- improving, stable, declining
    
    -- Images
    image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    raw_data_url VARCHAR(500),
    
    -- Zones (JSON array of health zones)
    health_zones JSONB DEFAULT '[]',
    
    -- Recommendations
    recommendations TEXT[],
    recommendations_ar TEXT[],
    
    -- Metadata
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ndvi_field ON ndvi_analyses(field_id);
CREATE INDEX IF NOT EXISTS idx_ndvi_tenant ON ndvi_analyses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ndvi_capture_date ON ndvi_analyses(capture_date DESC);
CREATE INDEX IF NOT EXISTS idx_ndvi_classification ON ndvi_analyses(classification);

-- ============================================
-- TASKS
-- المهام الزراعية
-- ============================================

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    field_crop_id UUID,
    
    -- Task Info
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    
    -- Type & Category
    type VARCHAR(50) NOT NULL, -- irrigation, fertilizing, spraying, harvesting, planting, maintenance, other
    category VARCHAR(100),
    
    -- Assignment
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Scheduling
    scheduled_date DATE,
    scheduled_time TIME,
    due_date TIMESTAMP,
    estimated_duration_minutes INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, assigned, in_progress, completed, cancelled, overdue
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    
    -- Completion
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    completion_notes TEXT,
    completion_photos TEXT[],
    
    -- AI Generated
    is_ai_generated BOOLEAN DEFAULT false,
    source_event_id VARCHAR(100),
    source_agent VARCHAR(100),
    
    -- Recurrence
    is_recurring BOOLEAN DEFAULT false,
    recurrence_rule VARCHAR(255),
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_field ON tasks(field_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON tasks(scheduled_date);

-- ============================================
-- ALERTS
-- التنبيهات
-- ============================================

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Alert Content
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    message_ar TEXT NOT NULL,
    
    -- Classification
    category VARCHAR(50) NOT NULL, -- weather, pest, irrigation, harvest, market, system, task, calendar
    severity VARCHAR(20) NOT NULL, -- info, warning, error, critical
    
    -- Delivery
    channels VARCHAR(20)[] DEFAULT ARRAY['in_app'], -- push, sms, email, in_app
    
    -- Source
    source_service VARCHAR(100),
    source_event_id VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, acknowledged, resolved, expired
    action_required BOOLEAN DEFAULT false,
    action_url VARCHAR(500),
    
    -- Timestamps
    sent_at TIMESTAMP,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_tenant ON alerts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_alerts_field ON alerts(field_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_category ON alerts(category);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);

-- ============================================
-- NOTIFICATION LOG
-- سجل الإشعارات
-- ============================================

CREATE TABLE IF NOT EXISTS notification_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    channel VARCHAR(20) NOT NULL, -- push, sms, email
    status VARCHAR(20) NOT NULL, -- pending, sent, delivered, failed
    
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    error_message TEXT,
    
    -- Channel-specific data
    channel_response JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notification_alert ON notification_log(alert_id);
CREATE INDEX IF NOT EXISTS idx_notification_user ON notification_log(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_status ON notification_log(status);

-- ============================================
-- ASTRONOMICAL CALENDAR EVENTS
-- أحداث التقويم الفلكي
-- ============================================

CREATE TABLE IF NOT EXISTS astronomical_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Naw Information
    naw_id VARCHAR(50) NOT NULL,
    naw_name_ar VARCHAR(100) NOT NULL,
    naw_name_en VARCHAR(100) NOT NULL,
    star_name VARCHAR(100),
    star_name_ar VARCHAR(100),
    
    -- Dates
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    season VARCHAR(20),
    
    -- Agricultural Data
    characteristics TEXT[],
    agricultural_guidance JSONB,
    suitable_crops JSONB,
    traditional_weather JSONB,
    proverbs JSONB,
    
    -- Metadata
    year INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_astro_naw ON astronomical_events(naw_id);
CREATE INDEX IF NOT EXISTS idx_astro_dates ON astronomical_events(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_astro_year ON astronomical_events(year);

-- ============================================
-- AI AGENT CONSULTATIONS
-- استشارات وكلاء الذكاء الاصطناعي
-- ============================================

CREATE TABLE IF NOT EXISTS ai_consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    field_id UUID REFERENCES fields(id),
    
    -- Request
    query TEXT NOT NULL,
    query_type VARCHAR(50), -- crop_advice, pest_identification, irrigation, market, general
    context JSONB,
    
    -- Processing
    agents_consulted VARCHAR(100)[],
    primary_agent VARCHAR(100),
    
    -- Response
    response TEXT NOT NULL,
    response_ar TEXT,
    confidence DECIMAL(3, 2),
    recommendations JSONB,
    
    -- Feedback
    user_rating INTEGER, -- 1-5
    user_feedback TEXT,
    was_helpful BOOLEAN,
    
    -- Performance
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_tenant ON ai_consultations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ai_user ON ai_consultations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_type ON ai_consultations(query_type);
CREATE INDEX IF NOT EXISTS idx_ai_created ON ai_consultations(created_at DESC);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tasks table
DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR REPORTING
-- عروض للتقارير
-- ============================================

-- Field Health Overview
CREATE OR REPLACE VIEW field_health_overview AS
SELECT 
    f.id as field_id,
    f.name as field_name,
    f.tenant_id,
    na.ndvi_mean as latest_ndvi,
    na.classification as health_status,
    na.capture_date as last_analysis,
    na.change_trend,
    (SELECT COUNT(*) FROM tasks t WHERE t.field_id = f.id AND t.status = 'pending') as pending_tasks,
    (SELECT COUNT(*) FROM alerts a WHERE a.field_id = f.id AND a.status = 'active') as active_alerts
FROM fields f
LEFT JOIN LATERAL (
    SELECT * FROM ndvi_analyses 
    WHERE field_id = f.id 
    ORDER BY capture_date DESC 
    LIMIT 1
) na ON true
WHERE f.is_active = true;

-- Task Summary by Tenant
CREATE OR REPLACE VIEW task_summary AS
SELECT 
    tenant_id,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
    COUNT(*) FILTER (WHERE status = 'completed' AND completed_at > NOW() - INTERVAL '7 days') as completed_this_week,
    COUNT(*) FILTER (WHERE status = 'overdue') as overdue,
    COUNT(*) as total
FROM tasks
GROUP BY tenant_id;

-- ============================================
-- SAMPLE DATA FOR TESTING
-- بيانات تجريبية للاختبار
-- ============================================

-- Insert default tenant for testing
INSERT INTO tenants (id, name, slug, subscription_tier)
VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Farm', 'demo-farm', 'pro')
ON CONFLICT (id) DO NOTHING;

COMMENT ON TABLE weather_records IS 'سجلات الطقس من خدمة Weather Signal';
COMMENT ON TABLE ndvi_analyses IS 'تحليلات NDVI من صور الأقمار الصناعية';
COMMENT ON TABLE tasks IS 'المهام الزراعية';
COMMENT ON TABLE alerts IS 'التنبيهات والإشعارات';
COMMENT ON TABLE astronomical_events IS 'أحداث التقويم الفلكي اليمني';
COMMENT ON TABLE ai_consultations IS 'استشارات وكلاء الذكاء الاصطناعي';
