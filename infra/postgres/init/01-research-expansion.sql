-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Research Expansion Pack - Additional Tables
-- حزمة التوسع البحثي - جداول إضافية
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Additional Research Enums
-- ─────────────────────────────────────────────────────────────────────────────

DO $$ BEGIN
    CREATE TYPE sample_status AS ENUM ('pending', 'in_transit', 'received', 'processing', 'analyzed', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE protocol_status AS ENUM ('draft', 'review', 'approved', 'active', 'completed', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE governance_level AS ENUM ('standard', 'strict', 'regulatory', 'gmp');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Research Sites (مواقع البحث)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS research_sites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    code VARCHAR(50) UNIQUE,
    location GEOGRAPHY(POINT, 4326),
    boundary GEOGRAPHY(POLYGON, 4326),
    area_hectares DECIMAL(12,4),
    climate_zone VARCHAR(100),
    soil_classification VARCHAR(100),
    elevation_meters DECIMAL(8,2),
    infrastructure JSONB DEFAULT '{}',
    contact_person UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_research_sites_tenant ON research_sites(tenant_id);
CREATE INDEX IF NOT EXISTS idx_research_sites_code ON research_sites(code);

-- ─────────────────────────────────────────────────────────────────────────────
-- Protocol Templates (قوالب البروتوكولات)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS protocol_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    code VARCHAR(50) UNIQUE,
    category VARCHAR(100),
    description TEXT,
    description_ar TEXT,
    methodology_template JSONB DEFAULT '{}',
    measurement_template JSONB DEFAULT '{}',
    required_equipment TEXT[],
    governance_level governance_level DEFAULT 'standard',
    governance_rules JSONB DEFAULT '{}',
    is_certified BOOLEAN DEFAULT false,
    certified_by VARCHAR(255),
    certified_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_protocol_templates_code ON protocol_templates(code);

-- ─────────────────────────────────────────────────────────────────────────────
-- Laboratory Information (معلومات المختبر)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS laboratories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    code VARCHAR(50) UNIQUE,
    lab_type VARCHAR(100),
    accreditation VARCHAR(255),
    accreditation_expiry DATE,
    address TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    capabilities TEXT[],
    turnaround_days INTEGER DEFAULT 7,
    is_internal BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_laboratories_code ON laboratories(code);

-- ─────────────────────────────────────────────────────────────────────────────
-- Sample Batches (دفعات العينات)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sample_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    experiment_id UUID REFERENCES experiments(id) ON DELETE CASCADE,
    batch_code VARCHAR(100) UNIQUE NOT NULL,
    laboratory_id UUID REFERENCES laboratories(id),
    status sample_status DEFAULT 'pending',
    sample_count INTEGER DEFAULT 0,
    collection_date DATE,
    shipped_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(255),
    storage_conditions VARCHAR(255),
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sample_batches_experiment ON sample_batches(experiment_id);
CREATE INDEX IF NOT EXISTS idx_sample_batches_status ON sample_batches(status);
CREATE INDEX IF NOT EXISTS idx_sample_batches_code ON sample_batches(batch_code);

-- ─────────────────────────────────────────────────────────────────────────────
-- Extended Lab Samples (تفاصيل العينات الموسعة)
-- ─────────────────────────────────────────────────────────────────────────────

-- Add batch_id to existing lab_samples if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'lab_samples' AND column_name = 'batch_id') THEN
        ALTER TABLE lab_samples ADD COLUMN batch_id UUID REFERENCES sample_batches(id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'lab_samples' AND column_name = 'barcode') THEN
        ALTER TABLE lab_samples ADD COLUMN barcode VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'lab_samples' AND column_name = 'chain_of_custody') THEN
        ALTER TABLE lab_samples ADD COLUMN chain_of_custody JSONB DEFAULT '[]';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_lab_samples_batch ON lab_samples(batch_id);
CREATE INDEX IF NOT EXISTS idx_lab_samples_barcode ON lab_samples(barcode);

-- ─────────────────────────────────────────────────────────────────────────────
-- Analysis Types (أنواع التحليل)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS analysis_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    category VARCHAR(100),
    description TEXT,
    sample_types sample_type[],
    parameters JSONB DEFAULT '[]',
    unit VARCHAR(50),
    method VARCHAR(255),
    turnaround_hours INTEGER,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'SAR',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_types_code ON analysis_types(code);

-- ─────────────────────────────────────────────────────────────────────────────
-- Sample Analysis Results (نتائج تحليل العينات)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sample_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id UUID NOT NULL REFERENCES lab_samples(id) ON DELETE CASCADE,
    analysis_type_id UUID REFERENCES analysis_types(id),
    parameter_name VARCHAR(255) NOT NULL,
    value DECIMAL(20,6),
    value_text VARCHAR(500),
    unit VARCHAR(50),
    min_range DECIMAL(20,6),
    max_range DECIMAL(20,6),
    status VARCHAR(50),
    is_within_range BOOLEAN,
    method_used VARCHAR(255),
    equipment_used VARCHAR(255),
    analyzed_by UUID REFERENCES users(id),
    analyzed_at TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_sample ON sample_analysis_results(sample_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON sample_analysis_results(analysis_type_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Research Data Points (نقاط البيانات البحثية)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS research_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_id UUID REFERENCES research_plots(id),
    treatment_id UUID REFERENCES treatments(id),
    measurement_date DATE NOT NULL,
    measurement_time TIME,
    parameter_name VARCHAR(255) NOT NULL,
    parameter_code VARCHAR(50),
    value DECIMAL(20,6),
    value_text VARCHAR(500),
    unit VARCHAR(50),
    measurement_method VARCHAR(255),
    equipment_id VARCHAR(100),
    recorded_by UUID REFERENCES users(id),
    location GEOGRAPHY(POINT, 4326),
    environmental_conditions JSONB DEFAULT '{}',
    quality_flag VARCHAR(50) DEFAULT 'valid',
    notes TEXT,
    offline_id VARCHAR(255) UNIQUE,
    synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_points_experiment ON research_data_points(experiment_id);
CREATE INDEX IF NOT EXISTS idx_data_points_plot ON research_data_points(plot_id);
CREATE INDEX IF NOT EXISTS idx_data_points_date ON research_data_points(measurement_date);
CREATE INDEX IF NOT EXISTS idx_data_points_parameter ON research_data_points(parameter_code);

-- ─────────────────────────────────────────────────────────────────────────────
-- Experiment Lock History (سجل قفل التجارب)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS experiment_locks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- 'lock', 'unlock', 'extend'
    reason TEXT,
    locked_by UUID REFERENCES users(id),
    lock_level VARCHAR(50) DEFAULT 'full', -- 'full', 'partial', 'data_only'
    expires_at TIMESTAMPTZ,
    previous_status experiment_status,
    signature_hash VARCHAR(512),
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_experiment_locks_experiment ON experiment_locks(experiment_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Research Reports (تقارير البحث)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS research_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    experiment_id UUID REFERENCES experiments(id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500),
    abstract TEXT,
    abstract_ar TEXT,
    content JSONB DEFAULT '{}',
    authors UUID[],
    status VARCHAR(50) DEFAULT 'draft',
    submitted_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    file_url VARCHAR(500),
    doi VARCHAR(255),
    citation TEXT,
    keywords TEXT[],
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_experiment ON research_reports(experiment_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON research_reports(status);

-- ─────────────────────────────────────────────────────────────────────────────
-- Statistical Analysis Results (نتائج التحليل الإحصائي)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS statistical_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    analysis_name VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(100), -- 'anova', 't_test', 'regression', 'correlation', etc.
    dependent_variable VARCHAR(255),
    independent_variables TEXT[],
    model_formula TEXT,
    results JSONB NOT NULL,
    p_value DECIMAL(10,8),
    r_squared DECIMAL(10,8),
    confidence_level DECIMAL(5,4) DEFAULT 0.95,
    sample_size INTEGER,
    degrees_of_freedom INTEGER,
    interpretation TEXT,
    interpretation_ar TEXT,
    software_used VARCHAR(100),
    script_used TEXT,
    performed_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stats_experiment ON statistical_analyses(experiment_id);
CREATE INDEX IF NOT EXISTS idx_stats_type ON statistical_analyses(analysis_type);

-- ═══════════════════════════════════════════════════════════════════════════════
-- DEMO DATA FOR RESEARCH EXPANSION
-- ═══════════════════════════════════════════════════════════════════════════════

-- Insert demo research site
INSERT INTO research_sites (id, tenant_id, name, name_ar, code, climate_zone, is_active)
VALUES (
    'rs000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'Al-Kharj Research Station',
    'محطة الخرج البحثية',
    'KHARJ-RS-01',
    'Arid',
    true
) ON CONFLICT (code) DO NOTHING;

-- Insert demo laboratory
INSERT INTO laboratories (id, tenant_id, name, name_ar, code, lab_type, capabilities, is_internal, is_active)
VALUES (
    'lab00000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'Sahool Central Laboratory',
    'مختبر سهول المركزي',
    'SAHOOL-LAB-01',
    'agricultural',
    ARRAY['soil_analysis', 'plant_tissue', 'water_quality', 'pest_identification'],
    true,
    true
) ON CONFLICT (code) DO NOTHING;

-- Insert demo protocol template
INSERT INTO protocol_templates (id, tenant_id, name, name_ar, code, category, governance_level)
VALUES (
    'pt000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'Standard Crop Yield Trial Protocol',
    'بروتوكول تجربة إنتاجية المحاصيل القياسي',
    'YIELD-TRIAL-STD',
    'yield_trials',
    'standard'
) ON CONFLICT (code) DO NOTHING;

-- Insert demo analysis types
INSERT INTO analysis_types (id, code, name, name_ar, category, sample_types, unit)
VALUES
    ('at000000-0000-0000-0000-000000000001', 'SOIL-NPK', 'Soil NPK Analysis', 'تحليل NPK للتربة', 'soil', ARRAY['soil']::sample_type[], 'mg/kg'),
    ('at000000-0000-0000-0000-000000000002', 'SOIL-PH', 'Soil pH Test', 'اختبار حموضة التربة', 'soil', ARRAY['soil']::sample_type[], 'pH'),
    ('at000000-0000-0000-0000-000000000003', 'LEAF-CHLOROPHYLL', 'Leaf Chlorophyll Content', 'محتوى الكلوروفيل في الأوراق', 'plant', ARRAY['plant_tissue']::sample_type[], 'SPAD'),
    ('at000000-0000-0000-0000-000000000004', 'WATER-EC', 'Water Electrical Conductivity', 'التوصيل الكهربائي للماء', 'water', ARRAY['water']::sample_type[], 'dS/m')
ON CONFLICT (code) DO NOTHING;

-- Insert demo sample batch
INSERT INTO sample_batches (id, tenant_id, experiment_id, batch_code, laboratory_id, status, sample_count, collection_date)
VALUES (
    'sb000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'm0000000-0000-0000-0000-000000000001',
    'BATCH-2025-001',
    'lab00000-0000-0000-0000-000000000001',
    'received',
    10,
    CURRENT_DATE - 3
) ON CONFLICT (batch_code) DO NOTHING;

-- Update existing lab samples with batch info
UPDATE lab_samples
SET batch_id = 'sb000000-0000-0000-0000-000000000001',
    barcode = 'SOIL-' || LPAD((ROW_NUMBER() OVER())::TEXT, 4, '0')
WHERE batch_id IS NULL;

-- Insert demo research data points
INSERT INTO research_data_points (id, experiment_id, measurement_date, parameter_name, parameter_code, value, unit, recorded_by)
VALUES
    ('rdp00000-0000-0000-0000-000000000001', 'm0000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Plant Height', 'PLANT_HEIGHT', 45.5, 'cm', 'b0000000-0000-0000-0000-000000000005'),
    ('rdp00000-0000-0000-0000-000000000002', 'm0000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Leaf Count', 'LEAF_COUNT', 12, 'count', 'b0000000-0000-0000-0000-000000000005'),
    ('rdp00000-0000-0000-0000-000000000003', 'm0000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'Plant Height', 'PLANT_HEIGHT', 52.3, 'cm', 'b0000000-0000-0000-0000-000000000005'),
    ('rdp00000-0000-0000-0000-000000000004', 'm0000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'Chlorophyll Index', 'SPAD', 42.8, 'SPAD', 'b0000000-0000-0000-0000-000000000005')
ON CONFLICT DO NOTHING;

-- Summary
DO $$
DECLARE
    new_tables INTEGER;
BEGIN
    SELECT COUNT(*) INTO new_tables
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('research_sites', 'protocol_templates', 'laboratories', 'sample_batches',
                       'analysis_types', 'sample_analysis_results', 'research_data_points',
                       'experiment_locks', 'research_reports', 'statistical_analyses');

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  RESEARCH EXPANSION PACK INSTALLED';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  New research tables: %', new_tables;
    RAISE NOTICE '  Demo data: Research site, Laboratory, Protocol template, Analysis types';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
