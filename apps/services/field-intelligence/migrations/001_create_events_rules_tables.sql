-- Field Intelligence Service - Database Migration
-- خدمة ذكاء الحقول - ترحيل قاعدة البيانات
-- Migration: 001_create_events_rules_tables
-- Description: Create tables for field intelligence events and automation rules
-- الوصف: إنشاء جداول لأحداث ذكاء الحقول وقواعد الأتمتة

-- =============================================================================
-- Events Table
-- جدول الأحداث
-- =============================================================================

CREATE TABLE IF NOT EXISTS field_intelligence_events (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Event identification
    event_id VARCHAR(100) UNIQUE NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    field_id VARCHAR(100) NOT NULL,

    -- Event classification
    event_type VARCHAR(50) NOT NULL,
    -- Possible values: ndvi_drop, ndvi_anomaly, weather_alert, soil_moisture_low,
    --                  soil_moisture_high, temperature_extreme, pest_detection,
    --                  disease_detection, irrigation_needed, harvest_ready,
    --                  astronomical_event, custom

    severity VARCHAR(20) NOT NULL,
    -- Possible values: low, medium, high, critical

    status VARCHAR(20) NOT NULL DEFAULT 'active',
    -- Possible values: active, acknowledged, resolved, ignored

    -- Event content
    title VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500),
    description TEXT NOT NULL,
    description_ar TEXT,
    source_service VARCHAR(100) NOT NULL,

    -- Additional data
    metadata JSONB DEFAULT '{}',
    location JSONB,
    correlation_id VARCHAR(100),

    -- Processing results
    triggered_rules TEXT[] DEFAULT '{}',
    created_tasks TEXT[] DEFAULT '{}',
    notifications_sent INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

-- Comments for events table
COMMENT ON TABLE field_intelligence_events IS 'Field intelligence events for SAHOOL platform - أحداث ذكاء الحقول لمنصة ساحول';
COMMENT ON COLUMN field_intelligence_events.event_id IS 'Unique event identifier - معرف الحدث الفريد';
COMMENT ON COLUMN field_intelligence_events.tenant_id IS 'Tenant/organization identifier - معرف المستأجر/المنظمة';
COMMENT ON COLUMN field_intelligence_events.field_id IS 'Field identifier - معرف الحقل';
COMMENT ON COLUMN field_intelligence_events.event_type IS 'Type of event (ndvi_drop, weather_alert, etc.) - نوع الحدث';
COMMENT ON COLUMN field_intelligence_events.severity IS 'Event severity (low, medium, high, critical) - خطورة الحدث';
COMMENT ON COLUMN field_intelligence_events.status IS 'Event status (active, acknowledged, resolved, ignored) - حالة الحدث';
COMMENT ON COLUMN field_intelligence_events.metadata IS 'Additional event-specific data as JSON - بيانات إضافية خاصة بالحدث';
COMMENT ON COLUMN field_intelligence_events.location IS 'Geographic location {lat, lon} - الموقع الجغرافي';
COMMENT ON COLUMN field_intelligence_events.triggered_rules IS 'List of rule IDs that were triggered - قائمة معرفات القواعد التي تم تفعيلها';
COMMENT ON COLUMN field_intelligence_events.created_tasks IS 'List of task IDs created by rules - قائمة معرفات المهام التي تم إنشاؤها';

-- =============================================================================
-- Rules Table
-- جدول القواعد
-- =============================================================================

CREATE TABLE IF NOT EXISTS field_intelligence_rules (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Rule identification
    rule_id VARCHAR(100) UNIQUE NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,

    -- Rule definition
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    description TEXT,
    description_ar TEXT,

    -- Rule status
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    -- Possible values: active, inactive, paused

    -- Rule scope
    field_ids TEXT[] DEFAULT '{}',
    -- Empty array means applies to all fields

    event_types TEXT[] DEFAULT '{}',
    -- Event types that trigger this rule

    -- Rule logic
    conditions JSONB NOT NULL,
    -- JSON structure: {logic: "AND"|"OR", conditions: [{field, operator, value, value_type}]}

    actions JSONB NOT NULL,
    -- JSON array of action configurations

    -- Execution settings
    cooldown_minutes INTEGER DEFAULT 60,
    priority INTEGER DEFAULT 100,
    -- Lower priority number = higher priority

    -- Statistics
    trigger_count INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMPTZ,

    -- Additional data
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Comments for rules table
COMMENT ON TABLE field_intelligence_rules IS 'Automation rules for field intelligence - قواعد الأتمتة لذكاء الحقول';
COMMENT ON COLUMN field_intelligence_rules.rule_id IS 'Unique rule identifier - معرف القاعدة الفريد';
COMMENT ON COLUMN field_intelligence_rules.tenant_id IS 'Tenant/organization identifier - معرف المستأجر/المنظمة';
COMMENT ON COLUMN field_intelligence_rules.field_ids IS 'Field IDs this rule applies to (empty = all fields) - معرفات الحقول التي تنطبق عليها القاعدة';
COMMENT ON COLUMN field_intelligence_rules.event_types IS 'Event types that trigger this rule - أنواع الأحداث التي تفعل هذه القاعدة';
COMMENT ON COLUMN field_intelligence_rules.conditions IS 'Rule conditions as JSON - شروط القاعدة';
COMMENT ON COLUMN field_intelligence_rules.actions IS 'Actions to execute when rule triggers - الإجراءات المنفذة عند تفعيل القاعدة';
COMMENT ON COLUMN field_intelligence_rules.cooldown_minutes IS 'Minimum time between triggers - الحد الأدنى للوقت بين التفعيلات';
COMMENT ON COLUMN field_intelligence_rules.priority IS 'Rule priority (lower = higher priority) - أولوية القاعدة';
COMMENT ON COLUMN field_intelligence_rules.trigger_count IS 'Number of times this rule has been triggered - عدد مرات تفعيل القاعدة';

-- =============================================================================
-- Indexes for Events Table
-- فهارس جدول الأحداث
-- =============================================================================

-- Index for tenant filtering (most common filter)
CREATE INDEX IF NOT EXISTS idx_fie_tenant_id
    ON field_intelligence_events(tenant_id);

-- Index for field filtering
CREATE INDEX IF NOT EXISTS idx_fie_field_id
    ON field_intelligence_events(field_id);

-- Index for event type filtering
CREATE INDEX IF NOT EXISTS idx_fie_event_type
    ON field_intelligence_events(event_type);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_fie_status
    ON field_intelligence_events(status);

-- Index for time-based queries (most recent first)
CREATE INDEX IF NOT EXISTS idx_fie_created_at
    ON field_intelligence_events(created_at DESC);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_fie_tenant_field_created
    ON field_intelligence_events(tenant_id, field_id, created_at DESC);

-- Composite index for status filtering with tenant
CREATE INDEX IF NOT EXISTS idx_fie_tenant_status
    ON field_intelligence_events(tenant_id, status);

-- =============================================================================
-- Indexes for Rules Table
-- فهارس جدول القواعد
-- =============================================================================

-- Index for tenant filtering
CREATE INDEX IF NOT EXISTS idx_fir_tenant_id
    ON field_intelligence_rules(tenant_id);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_fir_status
    ON field_intelligence_rules(status);

-- Index for priority ordering
CREATE INDEX IF NOT EXISTS idx_fir_priority
    ON field_intelligence_rules(priority);

-- Composite index for active rules query
CREATE INDEX IF NOT EXISTS idx_fir_tenant_status_priority
    ON field_intelligence_rules(tenant_id, status, priority);

-- =============================================================================
-- Functions and Triggers
-- الدوال والمحفزات
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_field_intelligence_rules_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on rules table
DROP TRIGGER IF EXISTS trigger_update_fir_updated_at ON field_intelligence_rules;
CREATE TRIGGER trigger_update_fir_updated_at
    BEFORE UPDATE ON field_intelligence_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_field_intelligence_rules_updated_at();

-- =============================================================================
-- Row Level Security (RLS) - Optional for multi-tenant security
-- أمان مستوى الصف - اختياري للأمان متعدد المستأجرين
-- =============================================================================

-- Enable RLS on events table (uncomment to enable)
-- ALTER TABLE field_intelligence_events ENABLE ROW LEVEL SECURITY;

-- Enable RLS on rules table (uncomment to enable)
-- ALTER TABLE field_intelligence_rules ENABLE ROW LEVEL SECURITY;

-- Policy for events (example - uncomment and customize as needed)
-- CREATE POLICY events_tenant_isolation ON field_intelligence_events
--     USING (tenant_id = current_setting('app.tenant_id', true));

-- Policy for rules (example - uncomment and customize as needed)
-- CREATE POLICY rules_tenant_isolation ON field_intelligence_rules
--     USING (tenant_id = current_setting('app.tenant_id', true));

-- =============================================================================
-- Grants (adjust roles as needed for your environment)
-- الصلاحيات
-- =============================================================================

-- Grant permissions to application user (uncomment and adjust role name)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON field_intelligence_events TO sahool_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON field_intelligence_rules TO sahool_app;
-- GRANT USAGE, SELECT ON SEQUENCE field_intelligence_events_id_seq TO sahool_app;
-- GRANT USAGE, SELECT ON SEQUENCE field_intelligence_rules_id_seq TO sahool_app;

-- =============================================================================
-- Migration Complete
-- اكتمل الترحيل
-- =============================================================================
