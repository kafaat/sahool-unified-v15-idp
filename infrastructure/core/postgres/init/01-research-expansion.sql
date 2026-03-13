-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Research Expansion Pack - Additional Tables
-- حزمة التوسع البحثي - جداول إضافية
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- FIX (2026-03-13): Removed all REFERENCES users(id) foreign key constraints.
-- The users table is managed by Prisma ORM (user-service) and does NOT exist
-- during Docker init. FK constraints will be added by a post-startup migration
-- after user-service runs `prisma migrate deploy`.
--
-- FIX (2026-03-13): Added missing enums (sample_type, experiment_status) that
-- are normally created by Prisma but are needed here for column definitions.
--
-- FIX (2026-03-13): Removed REFERENCES experiments(id), research_plots(id),
-- treatments(id) as those tables are also Prisma-managed (research-core).
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

-- FIX: Create sample_type enum (normally created by Prisma in research-core)
-- Required by analysis_types.sample_types column and demo data INSERT casts
DO $$ BEGIN
    CREATE TYPE sample_type AS ENUM ('soil', 'plant_tissue', 'water', 'grain', 'fruit', 'leaf', 'root', 'seed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- FIX: Create experiment_status enum (normally created by Prisma in research-core)
-- Required by experiment_locks.previous_status column
DO $$ BEGIN
    CREATE TYPE experiment_status AS ENUM ('draft', 'planning', 'active', 'paused', 'completed', 'cancelled', 'archived');
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
    contact_person UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    created_by UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    experiment_id UUID,  -- FK to experiments(id) added post-startup after Prisma migration
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
    created_by UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    analyzed_by UUID,  -- FK to users(id) added post-startup after Prisma migration
    analyzed_at TIMESTAMPTZ,
    verified_by UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    experiment_id UUID NOT NULL,  -- FK to experiments(id) added post-startup after Prisma migration
    plot_id UUID,  -- FK to research_plots(id) added post-startup after Prisma migration
    treatment_id UUID,  -- FK to treatments(id) added post-startup after Prisma migration
    measurement_date DATE NOT NULL,
    measurement_time TIME,
    parameter_name VARCHAR(255) NOT NULL,
    parameter_code VARCHAR(50),
    value DECIMAL(20,6),
    value_text VARCHAR(500),
    unit VARCHAR(50),
    measurement_method VARCHAR(255),
    equipment_id VARCHAR(100),
    recorded_by UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    experiment_id UUID NOT NULL,  -- FK to experiments(id) added post-startup after Prisma migration
    action VARCHAR(50) NOT NULL, -- 'lock', 'unlock', 'extend'
    reason TEXT,
    locked_by UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    experiment_id UUID,  -- FK to experiments(id) added post-startup after Prisma migration
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500),
    abstract TEXT,
    abstract_ar TEXT,
    content JSONB DEFAULT '{}',
    authors UUID[],
    status VARCHAR(50) DEFAULT 'draft',
    submitted_at TIMESTAMPTZ,
    reviewed_by UUID,  -- FK to users(id) added post-startup after Prisma migration
    reviewed_at TIMESTAMPTZ,
    approved_by UUID,  -- FK to users(id) added post-startup after Prisma migration
    approved_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    file_url VARCHAR(500),
    doi VARCHAR(255),
    citation TEXT,
    keywords TEXT[],
    created_by UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    experiment_id UUID NOT NULL,  -- FK to experiments(id) added post-startup after Prisma migration
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
    performed_by UUID,  -- FK to users(id) added post-startup after Prisma migration
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
    'a5000000-0000-0000-0000-000000000001',
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
    '1ab00000-0000-0000-0000-000000000001',
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
    'a6000000-0000-0000-0000-000000000001',
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
    ('a7000000-0000-0000-0000-000000000001', 'SOIL-NPK', 'Soil NPK Analysis', 'تحليل NPK للتربة', 'soil', ARRAY['soil']::sample_type[], 'mg/kg'),
    ('a7000000-0000-0000-0000-000000000002', 'SOIL-PH', 'Soil pH Test', 'اختبار حموضة التربة', 'soil', ARRAY['soil']::sample_type[], 'pH'),
    ('a7000000-0000-0000-0000-000000000003', 'LEAF-CHLOROPHYLL', 'Leaf Chlorophyll Content', 'محتوى الكلوروفيل في الأوراق', 'plant', ARRAY['plant_tissue']::sample_type[], 'SPAD'),
    ('a7000000-0000-0000-0000-000000000004', 'WATER-EC', 'Water Electrical Conductivity', 'التوصيل الكهربائي للماء', 'water', ARRAY['water']::sample_type[], 'dS/m')
ON CONFLICT (code) DO NOTHING;

-- FIX: Demo data referencing Prisma-managed tables (experiments, lab_samples)
-- is wrapped in a DO block with exception handling to avoid errors when those
-- tables don't exist yet. The data will be inserted if tables exist (e.g. on restart).

-- Insert demo sample batch (experiment_id is just a UUID reference, no FK enforced)
INSERT INTO sample_batches (id, tenant_id, experiment_id, batch_code, laboratory_id, status, sample_count, collection_date)
VALUES (
    '5b000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'ae000000-0000-0000-0000-000000000001',
    'BATCH-2025-001',
    '1ab00000-0000-0000-0000-000000000001',
    'received',
    10,
    CURRENT_DATE - 3
) ON CONFLICT (batch_code) DO NOTHING;

-- Update existing lab samples with batch info (safe: skips if lab_samples doesn't exist yet)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lab_samples') THEN
        EXECUTE '
            WITH numbered_samples AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as row_num
                FROM lab_samples
                WHERE batch_id IS NULL
            )
            UPDATE lab_samples
            SET batch_id = ''5b000000-0000-0000-0000-000000000001'',
                barcode = ''SOIL-'' || LPAD(numbered_samples.row_num::TEXT, 4, ''0000'')
            FROM numbered_samples
            WHERE lab_samples.id = numbered_samples.id';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Skipping lab_samples update: %', SQLERRM;
END $$;

-- Insert demo research data points (experiment_id is just a UUID, no FK enforced)
INSERT INTO research_data_points (id, experiment_id, measurement_date, parameter_name, parameter_code, value, unit)
VALUES
    ('ad000000-0000-0000-0000-000000000001', 'ae000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Plant Height', 'PLANT_HEIGHT', 45.5, 'cm'),
    ('ad000000-0000-0000-0000-000000000002', 'ae000000-0000-0000-0000-000000000001', CURRENT_DATE - 7, 'Leaf Count', 'LEAF_COUNT', 12, 'count'),
    ('ad000000-0000-0000-0000-000000000003', 'ae000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'Plant Height', 'PLANT_HEIGHT', 52.3, 'cm'),
    ('ad000000-0000-0000-0000-000000000004', 'ae000000-0000-0000-0000-000000000001', CURRENT_DATE - 5, 'Chlorophyll Index', 'SPAD', 42.8, 'SPAD')
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
