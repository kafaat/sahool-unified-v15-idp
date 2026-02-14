-- Migration: 001_create_soil_tests
-- Description: Create soil analysis tables - إنشاء جداول تحليل التربة
-- Service: soil-analysis-service
-- Date: 2026-02-14

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- Soil Tests - فحوصات التربة
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS soil_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    farm_id VARCHAR(100),
    field_id VARCHAR(100) NOT NULL,

    -- Sample Information - معلومات العينة
    sample_id VARCHAR(50),
    sample_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    sample_depth_cm DECIMAL(5, 1) DEFAULT 30.0,
    lab_name VARCHAR(200),
    lab_name_ar VARCHAR(200),

    -- Macronutrients (ppm) - العناصر الكبرى
    nitrogen_ppm DECIMAL(8, 2),
    phosphorus_ppm DECIMAL(8, 2),
    potassium_ppm DECIMAL(8, 2),
    calcium_ppm DECIMAL(8, 2),
    magnesium_ppm DECIMAL(8, 2),
    sulfur_ppm DECIMAL(8, 2),

    -- Micronutrients (ppm) - العناصر الصغرى
    iron_ppm DECIMAL(8, 3),
    zinc_ppm DECIMAL(8, 3),
    manganese_ppm DECIMAL(8, 3),
    copper_ppm DECIMAL(8, 3),
    boron_ppm DECIMAL(8, 3),
    molybdenum_ppm DECIMAL(8, 4),

    -- Soil Properties - خصائص التربة
    ph DECIMAL(4, 2),
    ec_dsm DECIMAL(6, 3),
    organic_matter_percent DECIMAL(5, 2),
    cec DECIMAL(6, 2),
    carbonate_percent DECIMAL(5, 2),

    -- Soil Texture - قوام التربة
    sand_percent DECIMAL(5, 2),
    silt_percent DECIMAL(5, 2),
    clay_percent DECIMAL(5, 2),
    texture_class VARCHAR(50),
    texture_class_ar VARCHAR(50),

    -- Heavy Metals (ppm) - المعادن الثقيلة
    lead_ppm DECIMAL(8, 4),
    cadmium_ppm DECIMAL(8, 4),
    chromium_ppm DECIMAL(8, 4),
    nickel_ppm DECIMAL(8, 4),
    arsenic_ppm DECIMAL(8, 4),
    mercury_ppm DECIMAL(8, 5),

    -- Interpretation Results - نتائج التفسير
    interpretation JSONB,
    amendment_plan JSONB,

    -- Status - الحالة
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_soil_test_status CHECK (status IN ('pending', 'analyzed', 'interpreted', 'archived')),
    CONSTRAINT valid_ph CHECK (ph IS NULL OR (ph >= 0 AND ph <= 14)),
    CONSTRAINT valid_texture CHECK (
        (sand_percent IS NULL AND silt_percent IS NULL AND clay_percent IS NULL) OR
        (ABS(COALESCE(sand_percent, 0) + COALESCE(silt_percent, 0) + COALESCE(clay_percent, 0) - 100) < 1)
    )
);

COMMENT ON TABLE soil_tests IS 'Soil test records with nutrient analysis - سجلات فحص التربة مع تحليل العناصر';

-- Indexes - الفهارس
CREATE INDEX IF NOT EXISTS idx_soil_tests_tenant_id ON soil_tests(tenant_id);
CREATE INDEX IF NOT EXISTS idx_soil_tests_field_id ON soil_tests(field_id);
CREATE INDEX IF NOT EXISTS idx_soil_tests_tenant_field ON soil_tests(tenant_id, field_id);
CREATE INDEX IF NOT EXISTS idx_soil_tests_sample_date ON soil_tests(sample_date DESC);
CREATE INDEX IF NOT EXISTS idx_soil_tests_status ON soil_tests(status);
CREATE INDEX IF NOT EXISTS idx_soil_tests_tenant_status ON soil_tests(tenant_id, status, created_at DESC);

-- Updated_at Trigger - مشغل تحديث التاريخ
CREATE OR REPLACE FUNCTION update_soil_tests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_soil_tests_updated_at
    BEFORE UPDATE ON soil_tests
    FOR EACH ROW
    EXECUTE FUNCTION update_soil_tests_updated_at();

-- Migration tracking - تتبع الترحيل
INSERT INTO public._migrations (name) VALUES ('001_create_soil_tests')
ON CONFLICT (name) DO NOTHING;
