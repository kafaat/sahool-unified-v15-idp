-- Low-Code Engine Service - Database Migration
-- خدمة محرك التطوير منخفض الكود - ترحيل قاعدة البيانات
-- Migration: 001_create_data_models_pages_tables
-- Description: Create tables for low-code data models and page definitions
-- الوصف: إنشاء جداول لنماذج البيانات وتعريفات الصفحات

-- =============================================================================
-- Data Models Table
-- جدول نماذج البيانات
-- =============================================================================

CREATE TABLE IF NOT EXISTS lowcode_data_models (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,

    -- Model identification
    name VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100),

    -- Description
    description TEXT,
    description_ar TEXT,

    -- Field definitions (stored as JSONB array)
    -- Each field: {name, name_ar, field_type, required, default_value, options, validation}
    fields JSONB NOT NULL DEFAULT '[]',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint for name within tenant
    CONSTRAINT uq_lowcode_data_models_tenant_name UNIQUE (tenant_id, name)
);

-- Comments for data_models table
COMMENT ON TABLE lowcode_data_models IS 'Low-code data model definitions for SAHOOL platform - تعريفات نماذج البيانات منخفضة الكود لمنصة ساحول';
COMMENT ON COLUMN lowcode_data_models.id IS 'Unique data model identifier - معرف نموذج البيانات الفريد';
COMMENT ON COLUMN lowcode_data_models.tenant_id IS 'Tenant/organization identifier - معرف المستأجر/المنظمة';
COMMENT ON COLUMN lowcode_data_models.name IS 'Model name in English - اسم النموذج بالإنجليزية';
COMMENT ON COLUMN lowcode_data_models.name_ar IS 'Model name in Arabic - اسم النموذج بالعربية';
COMMENT ON COLUMN lowcode_data_models.description IS 'Model description in English - وصف النموذج بالإنجليزية';
COMMENT ON COLUMN lowcode_data_models.description_ar IS 'Model description in Arabic - وصف النموذج بالعربية';
COMMENT ON COLUMN lowcode_data_models.fields IS 'Field definitions as JSONB array - تعريفات الحقول كمصفوفة JSON';

-- =============================================================================
-- Pages Table
-- جدول الصفحات
-- =============================================================================

CREATE TABLE IF NOT EXISTS lowcode_pages (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,

    -- Page identification
    name VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100),

    -- Description
    description TEXT,
    description_ar TEXT,

    -- Routing
    route VARCHAR(255) NOT NULL,

    -- Layout configuration
    layout VARCHAR(50) DEFAULT 'default',
    -- Possible values: default, full-width, sidebar, dashboard

    -- Block definitions (stored as JSONB array)
    -- Each block: {id, component_name, props, children, conditions, loop}
    blocks JSONB NOT NULL DEFAULT '[]',

    -- Data model reference
    data_model_id UUID,

    -- Publishing state
    is_published BOOLEAN NOT NULL DEFAULT FALSE,

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint for route within tenant
    CONSTRAINT uq_lowcode_pages_tenant_route UNIQUE (tenant_id, route),

    -- Foreign key to data models (optional)
    CONSTRAINT fk_lowcode_pages_data_model
        FOREIGN KEY (data_model_id)
        REFERENCES lowcode_data_models(id)
        ON DELETE SET NULL
);

-- Comments for pages table
COMMENT ON TABLE lowcode_pages IS 'Low-code page definitions for SAHOOL platform - تعريفات الصفحات منخفضة الكود لمنصة ساحول';
COMMENT ON COLUMN lowcode_pages.id IS 'Unique page identifier - معرف الصفحة الفريد';
COMMENT ON COLUMN lowcode_pages.tenant_id IS 'Tenant/organization identifier - معرف المستأجر/المنظمة';
COMMENT ON COLUMN lowcode_pages.name IS 'Page name in English - اسم الصفحة بالإنجليزية';
COMMENT ON COLUMN lowcode_pages.name_ar IS 'Page name in Arabic - اسم الصفحة بالعربية';
COMMENT ON COLUMN lowcode_pages.route IS 'URL route for the page - مسار URL للصفحة';
COMMENT ON COLUMN lowcode_pages.layout IS 'Page layout type - نوع تخطيط الصفحة';
COMMENT ON COLUMN lowcode_pages.blocks IS 'Block configurations as JSONB array - تكوينات الكتل كمصفوفة JSON';
COMMENT ON COLUMN lowcode_pages.data_model_id IS 'Reference to data model (optional) - مرجع لنموذج البيانات (اختياري)';
COMMENT ON COLUMN lowcode_pages.is_published IS 'Whether the page is published - هل الصفحة منشورة';
COMMENT ON COLUMN lowcode_pages.version IS 'Page version number - رقم إصدار الصفحة';

-- =============================================================================
-- Indexes for Data Models Table
-- فهارس جدول نماذج البيانات
-- =============================================================================

-- Index for tenant filtering (most common filter)
CREATE INDEX IF NOT EXISTS idx_lowcode_dm_tenant_id
    ON lowcode_data_models(tenant_id);

-- Index for name search
CREATE INDEX IF NOT EXISTS idx_lowcode_dm_name
    ON lowcode_data_models(name);

-- Index for time-based queries (most recent first)
CREATE INDEX IF NOT EXISTS idx_lowcode_dm_created_at
    ON lowcode_data_models(created_at DESC);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_lowcode_dm_tenant_created
    ON lowcode_data_models(tenant_id, created_at DESC);

-- =============================================================================
-- Indexes for Pages Table
-- فهارس جدول الصفحات
-- =============================================================================

-- Index for tenant filtering (most common filter)
CREATE INDEX IF NOT EXISTS idx_lowcode_pages_tenant_id
    ON lowcode_pages(tenant_id);

-- Index for route lookup
CREATE INDEX IF NOT EXISTS idx_lowcode_pages_route
    ON lowcode_pages(route);

-- Index for published pages
CREATE INDEX IF NOT EXISTS idx_lowcode_pages_is_published
    ON lowcode_pages(is_published);

-- Index for data model reference
CREATE INDEX IF NOT EXISTS idx_lowcode_pages_data_model_id
    ON lowcode_pages(data_model_id);

-- Index for time-based queries (most recent first)
CREATE INDEX IF NOT EXISTS idx_lowcode_pages_created_at
    ON lowcode_pages(created_at DESC);

-- Composite index for tenant + published filter
CREATE INDEX IF NOT EXISTS idx_lowcode_pages_tenant_published
    ON lowcode_pages(tenant_id, is_published);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_lowcode_pages_tenant_created
    ON lowcode_pages(tenant_id, created_at DESC);

-- =============================================================================
-- Functions and Triggers
-- الدوال والمحفزات
-- =============================================================================

-- Function to update updated_at timestamp for data models
CREATE OR REPLACE FUNCTION update_lowcode_data_models_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp for pages
CREATE OR REPLACE FUNCTION update_lowcode_pages_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on data models table
DROP TRIGGER IF EXISTS trigger_update_lowcode_dm_updated_at ON lowcode_data_models;
CREATE TRIGGER trigger_update_lowcode_dm_updated_at
    BEFORE UPDATE ON lowcode_data_models
    FOR EACH ROW
    EXECUTE FUNCTION update_lowcode_data_models_updated_at();

-- Trigger to auto-update updated_at on pages table
DROP TRIGGER IF EXISTS trigger_update_lowcode_pages_updated_at ON lowcode_pages;
CREATE TRIGGER trigger_update_lowcode_pages_updated_at
    BEFORE UPDATE ON lowcode_pages
    FOR EACH ROW
    EXECUTE FUNCTION update_lowcode_pages_updated_at();

-- =============================================================================
-- Row Level Security (RLS) - Optional for multi-tenant security
-- أمان مستوى الصف - اختياري للأمان متعدد المستأجرين
-- =============================================================================

-- Enable RLS on data models table (uncomment to enable)
-- ALTER TABLE lowcode_data_models ENABLE ROW LEVEL SECURITY;

-- Enable RLS on pages table (uncomment to enable)
-- ALTER TABLE lowcode_pages ENABLE ROW LEVEL SECURITY;

-- Policy for data models (example - uncomment and customize as needed)
-- CREATE POLICY data_models_tenant_isolation ON lowcode_data_models
--     USING (tenant_id = current_setting('app.tenant_id', true));

-- Policy for pages (example - uncomment and customize as needed)
-- CREATE POLICY pages_tenant_isolation ON lowcode_pages
--     USING (tenant_id = current_setting('app.tenant_id', true));

-- =============================================================================
-- Grants (adjust roles as needed for your environment)
-- الصلاحيات
-- =============================================================================

-- Grant permissions to application user (uncomment and adjust role name)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON lowcode_data_models TO sahool_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON lowcode_pages TO sahool_app;

-- =============================================================================
-- Migration Complete
-- اكتمل الترحيل
-- =============================================================================
