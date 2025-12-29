-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Ecological Agriculture Tables Migration
-- جداول الزراعة الإيكولوجية
-- ═══════════════════════════════════════════════════════════════════════════════
-- Version: 1.0.0
-- Based on: Ecological Agriculture Article Series 2025
-- ═══════════════════════════════════════════════════════════════════════════════

-- Skip if already applied
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM public._migrations WHERE name = '012_ecological_assessments') THEN
        RAISE NOTICE 'Migration 012_ecological_assessments already applied, skipping...';
        RETURN;
    END IF;

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Create eco schema if not exists
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE SCHEMA IF NOT EXISTS eco;

    COMMENT ON SCHEMA eco IS 'Ecological agriculture and sustainability data | بيانات الزراعة الإيكولوجية والاستدامة';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Ecological Assessments Table
    -- جدول التقييمات الإيكولوجية
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.ecological_assessments (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        tenant_id UUID REFERENCES tenants.tenants(id),
        assessment_date DATE NOT NULL DEFAULT CURRENT_DATE,

        -- Sustainability Scores | درجات الاستدامة
        overall_score DECIMAL(5, 2) CHECK (overall_score >= 0 AND overall_score <= 100),
        biodiversity_score DECIMAL(5, 2) CHECK (biodiversity_score >= 0 AND biodiversity_score <= 100),
        soil_health_score DECIMAL(5, 2) CHECK (soil_health_score >= 0 AND soil_health_score <= 100),
        water_efficiency_score DECIMAL(5, 2) CHECK (water_efficiency_score >= 0 AND water_efficiency_score <= 100),
        pest_management_score DECIMAL(5, 2) CHECK (pest_management_score >= 0 AND pest_management_score <= 100),
        resource_cycling_score DECIMAL(5, 2) CHECK (resource_cycling_score >= 0 AND resource_cycling_score <= 100),

        -- Detailed Data | البيانات التفصيلية
        strengths JSONB DEFAULT '[]',
        weaknesses JSONB DEFAULT '[]',
        opportunities JSONB DEFAULT '[]',
        recommendations JSONB DEFAULT '[]',

        -- Metadata | البيانات الوصفية
        assessor_notes TEXT,
        assessor_notes_ar TEXT,
        assessed_by UUID REFERENCES users.users(id),

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.ecological_assessments IS 'Farm ecological sustainability assessments | تقييمات الاستدامة الإيكولوجية للمزارع';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Ecological Practices Table
    -- جدول الممارسات الإيكولوجية المطبقة
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.farm_practices (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        field_id UUID REFERENCES geo.fields(id) ON DELETE SET NULL,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Practice Details | تفاصيل الممارسة
        practice_id VARCHAR(100) NOT NULL,
        practice_name VARCHAR(255) NOT NULL,
        practice_name_ar VARCHAR(255),
        category VARCHAR(50) NOT NULL,

        -- Implementation | التنفيذ
        status VARCHAR(20) DEFAULT 'planned' CHECK (status IN ('planned', 'in_progress', 'implemented', 'paused', 'abandoned')),
        start_date DATE,
        implementation_date DATE,

        -- Details | التفاصيل
        implementation_notes TEXT,
        implementation_notes_ar TEXT,
        materials_used JSONB DEFAULT '[]',
        labor_hours DECIMAL(10, 2),
        cost_estimate DECIMAL(12, 2),

        -- Results | النتائج
        observed_benefits JSONB DEFAULT '[]',
        challenges JSONB DEFAULT '[]',
        effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 5),

        -- GlobalGAP Mapping | ربط GlobalGAP
        globalgap_control_points VARCHAR(50)[] DEFAULT '{}',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.farm_practices IS 'Implemented ecological practices per farm | الممارسات الإيكولوجية المطبقة لكل مزرعة';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Transition Plans Table
    -- جدول خطط التحول الإيكولوجي
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.transition_plans (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Plan Info | معلومات الخطة
        name VARCHAR(255) NOT NULL,
        name_ar VARCHAR(255),
        description TEXT,
        description_ar TEXT,

        -- Timeline | الجدول الزمني
        start_date DATE NOT NULL,
        target_completion_date DATE,
        actual_completion_date DATE,

        -- Status | الحالة
        status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'paused', 'cancelled')),
        current_phase INTEGER DEFAULT 1,
        total_phases INTEGER DEFAULT 1,

        -- Goals | الأهداف
        target_practices VARCHAR(100)[] DEFAULT '{}',
        target_scores JSONB DEFAULT '{}',

        -- Progress | التقدم
        completion_percentage DECIMAL(5, 2) DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
        milestones_completed INTEGER DEFAULT 0,
        milestones_total INTEGER DEFAULT 0,

        created_by UUID REFERENCES users.users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.transition_plans IS 'Ecological transition plans for farms | خطط التحول الإيكولوجي للمزارع';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Transition Milestones Table
    -- جدول المعالم في خطط التحول
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.transition_milestones (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        plan_id UUID REFERENCES eco.transition_plans(id) ON DELETE CASCADE,

        -- Milestone Info | معلومات المعلم
        phase INTEGER NOT NULL,
        sequence_order INTEGER NOT NULL,
        title VARCHAR(255) NOT NULL,
        title_ar VARCHAR(255),
        description TEXT,
        description_ar TEXT,

        -- Practice Reference | مرجع الممارسة
        practice_id VARCHAR(100),

        -- Timeline | الجدول الزمني
        planned_date DATE,
        completed_date DATE,

        -- Status | الحالة
        status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'skipped')),

        -- Evidence | الأدلة
        evidence_required JSONB DEFAULT '[]',
        evidence_provided JSONB DEFAULT '[]',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.transition_milestones IS 'Milestones within transition plans | المعالم ضمن خطط التحول';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Pitfall Diagnoses Table
    -- جدول تشخيصات المزالق
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.pitfall_diagnoses (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        field_id UUID REFERENCES geo.fields(id) ON DELETE SET NULL,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Diagnosis | التشخيص
        diagnosis_date DATE NOT NULL DEFAULT CURRENT_DATE,
        pitfall_id VARCHAR(100) NOT NULL,
        pitfall_name VARCHAR(255) NOT NULL,
        pitfall_name_ar VARCHAR(255),
        category VARCHAR(50) NOT NULL,
        severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),

        -- Analysis | التحليل
        observed_symptoms JSONB DEFAULT '[]',
        root_causes JSONB DEFAULT '[]',
        match_confidence DECIMAL(5, 2) CHECK (match_confidence >= 0 AND match_confidence <= 1),

        -- Resolution | الحل
        status VARCHAR(20) DEFAULT 'identified' CHECK (status IN ('identified', 'in_remediation', 'resolved', 'monitoring')),
        recommended_actions JSONB DEFAULT '[]',
        actions_taken JSONB DEFAULT '[]',
        resolution_date DATE,

        -- Impact | التأثير
        estimated_recovery_months INTEGER,
        economic_impact_estimate DECIMAL(12, 2),

        diagnosed_by UUID REFERENCES users.users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.pitfall_diagnoses IS 'Agricultural pitfall diagnoses and tracking | تشخيص وتتبع المزالق الزراعية';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Companion Planting Records Table
    -- جدول سجلات الزراعة التصاحبية
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.companion_plantings (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        field_id UUID REFERENCES geo.fields(id) ON DELETE CASCADE,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Planting Info | معلومات الزراعة
        season VARCHAR(20) NOT NULL,
        planting_year INTEGER NOT NULL,

        -- Crops | المحاصيل
        main_crop VARCHAR(100) NOT NULL,
        companion_crops VARCHAR(100)[] NOT NULL DEFAULT '{}',

        -- Layout | التخطيط
        layout_design JSONB DEFAULT '{}',
        spacing_notes TEXT,

        -- Results | النتائج
        observed_benefits JSONB DEFAULT '[]',
        observed_issues JSONB DEFAULT '[]',
        pest_reduction_observed BOOLEAN,
        yield_impact VARCHAR(20) CHECK (yield_impact IN ('positive', 'neutral', 'negative', 'unknown')),

        -- Rating | التقييم
        success_rating INTEGER CHECK (success_rating >= 1 AND success_rating <= 5),
        would_repeat BOOLEAN,
        notes TEXT,
        notes_ar TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.companion_plantings IS 'Companion planting records and outcomes | سجلات الزراعة التصاحبية ونتائجها';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Biodiversity Records Table
    -- جدول سجلات التنوع البيولوجي
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.biodiversity_records (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Survey Info | معلومات المسح
        survey_date DATE NOT NULL,
        survey_type VARCHAR(50) NOT NULL CHECK (survey_type IN ('species_count', 'habitat_assessment', 'beneficial_insects', 'soil_organisms', 'general')),

        -- Counts | الأعداد
        species_observed JSONB DEFAULT '[]',
        species_count INTEGER,
        beneficial_insect_count INTEGER,
        pollinator_count INTEGER,

        -- Habitat | الموئل
        habitat_features JSONB DEFAULT '[]',
        cover_crop_species VARCHAR(100)[] DEFAULT '{}',
        hedgerow_length_meters DECIMAL(10, 2),

        -- Assessment | التقييم
        diversity_index DECIMAL(5, 3),
        habitat_quality_score DECIMAL(5, 2) CHECK (habitat_quality_score >= 0 AND habitat_quality_score <= 100),

        notes TEXT,
        notes_ar TEXT,
        surveyed_by UUID REFERENCES users.users(id),

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.biodiversity_records IS 'Biodiversity survey records | سجلات مسح التنوع البيولوجي';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Soil Health Records Table
    -- جدول سجلات صحة التربة
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.soil_health_records (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        field_id UUID REFERENCES geo.fields(id) ON DELETE CASCADE,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Sample Info | معلومات العينة
        sample_date DATE NOT NULL,
        sample_depth_cm INTEGER,
        sample_location GEOMETRY(Point, 4326),

        -- Physical Properties | الخصائص الفيزيائية
        organic_matter_percent DECIMAL(5, 2),
        soil_texture VARCHAR(50),
        bulk_density DECIMAL(4, 2),
        water_infiltration_rate DECIMAL(6, 2),
        aggregate_stability DECIMAL(5, 2),

        -- Biological Indicators | المؤشرات البيولوجية
        earthworm_count INTEGER,
        microbial_biomass DECIMAL(10, 2),
        respiration_rate DECIMAL(6, 2),

        -- Chemical Properties | الخصائص الكيميائية
        ph_level DECIMAL(4, 2),
        ec_level DECIMAL(6, 2),
        cec_level DECIMAL(6, 2),

        -- Overall Assessment | التقييم العام
        health_score DECIMAL(5, 2) CHECK (health_score >= 0 AND health_score <= 100),
        status VARCHAR(20) CHECK (status IN ('poor', 'fair', 'good', 'excellent')),

        lab_report_url TEXT,
        notes TEXT,
        notes_ar TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.soil_health_records IS 'Soil health monitoring records | سجلات مراقبة صحة التربة';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Water Conservation Records Table
    -- جدول سجلات الحفاظ على المياه
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.water_conservation_records (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        field_id UUID REFERENCES geo.fields(id) ON DELETE SET NULL,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Period | الفترة
        record_date DATE NOT NULL,
        period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'seasonal')),

        -- Water Usage | استخدام المياه
        water_used_liters DECIMAL(12, 2),
        water_source VARCHAR(50),
        irrigation_method VARCHAR(50),

        -- Efficiency Metrics | مقاييس الكفاءة
        water_per_hectare DECIMAL(10, 2),
        efficiency_percentage DECIMAL(5, 2),
        comparison_to_baseline DECIMAL(5, 2),

        -- Conservation Practices | ممارسات الحفاظ
        mulching_applied BOOLEAN DEFAULT false,
        drip_irrigation_used BOOLEAN DEFAULT false,
        rainwater_harvested_liters DECIMAL(12, 2),

        notes TEXT,
        notes_ar TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    COMMENT ON TABLE eco.water_conservation_records IS 'Water usage and conservation tracking | تتبع استخدام المياه والحفاظ عليها';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- GlobalGAP Ecological Compliance Table
    -- جدول امتثال GlobalGAP الإيكولوجي
    -- ═══════════════════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS eco.globalgap_ecological_compliance (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        tenant_id UUID REFERENCES tenants.tenants(id),

        -- Control Point | نقطة التحكم
        control_point VARCHAR(20) NOT NULL,
        control_point_description TEXT,
        control_point_description_ar TEXT,

        -- Status | الحالة
        compliance_status VARCHAR(20) DEFAULT 'not_assessed' CHECK (compliance_status IN ('not_assessed', 'non_compliant', 'partially_compliant', 'compliant')),
        assessment_date DATE,

        -- Evidence | الأدلة
        ecological_practices_used VARCHAR(100)[] DEFAULT '{}',
        evidence_documents JSONB DEFAULT '[]',
        evidence_photos JSONB DEFAULT '[]',

        -- Audit Info | معلومات التدقيق
        last_audit_date DATE,
        audit_findings TEXT,
        corrective_actions JSONB DEFAULT '[]',

        notes TEXT,
        notes_ar TEXT,
        assessed_by UUID REFERENCES users.users(id),

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        UNIQUE(farm_id, control_point)
    );

    COMMENT ON TABLE eco.globalgap_ecological_compliance IS 'GlobalGAP sustainability control points compliance via ecological practices | امتثال نقاط التحكم في الاستدامة لـ GlobalGAP عبر الممارسات الإيكولوجية';

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Create Indexes
    -- إنشاء الفهارس
    -- ═══════════════════════════════════════════════════════════════════════════

    -- Ecological Assessments indexes
    CREATE INDEX IF NOT EXISTS idx_eco_assessments_farm ON eco.ecological_assessments (farm_id);
    CREATE INDEX IF NOT EXISTS idx_eco_assessments_tenant ON eco.ecological_assessments (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_assessments_date ON eco.ecological_assessments (assessment_date DESC);

    -- Farm Practices indexes
    CREATE INDEX IF NOT EXISTS idx_eco_practices_farm ON eco.farm_practices (farm_id);
    CREATE INDEX IF NOT EXISTS idx_eco_practices_field ON eco.farm_practices (field_id);
    CREATE INDEX IF NOT EXISTS idx_eco_practices_tenant ON eco.farm_practices (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_practices_status ON eco.farm_practices (status);
    CREATE INDEX IF NOT EXISTS idx_eco_practices_category ON eco.farm_practices (category);
    CREATE INDEX IF NOT EXISTS idx_eco_practices_globalgap ON eco.farm_practices USING GIN (globalgap_control_points);

    -- Transition Plans indexes
    CREATE INDEX IF NOT EXISTS idx_eco_plans_farm ON eco.transition_plans (farm_id);
    CREATE INDEX IF NOT EXISTS idx_eco_plans_tenant ON eco.transition_plans (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_plans_status ON eco.transition_plans (status);

    -- Transition Milestones indexes
    CREATE INDEX IF NOT EXISTS idx_eco_milestones_plan ON eco.transition_milestones (plan_id);
    CREATE INDEX IF NOT EXISTS idx_eco_milestones_status ON eco.transition_milestones (status);

    -- Pitfall Diagnoses indexes
    CREATE INDEX IF NOT EXISTS idx_eco_pitfalls_farm ON eco.pitfall_diagnoses (farm_id);
    CREATE INDEX IF NOT EXISTS idx_eco_pitfalls_field ON eco.pitfall_diagnoses (field_id);
    CREATE INDEX IF NOT EXISTS idx_eco_pitfalls_tenant ON eco.pitfall_diagnoses (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_pitfalls_severity ON eco.pitfall_diagnoses (severity);
    CREATE INDEX IF NOT EXISTS idx_eco_pitfalls_status ON eco.pitfall_diagnoses (status);

    -- Companion Plantings indexes
    CREATE INDEX IF NOT EXISTS idx_eco_companion_field ON eco.companion_plantings (field_id);
    CREATE INDEX IF NOT EXISTS idx_eco_companion_tenant ON eco.companion_plantings (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_companion_year ON eco.companion_plantings (planting_year);

    -- Biodiversity Records indexes
    CREATE INDEX IF NOT EXISTS idx_eco_biodiversity_farm ON eco.biodiversity_records (farm_id);
    CREATE INDEX IF NOT EXISTS idx_eco_biodiversity_tenant ON eco.biodiversity_records (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_biodiversity_date ON eco.biodiversity_records (survey_date DESC);

    -- Soil Health Records indexes
    CREATE INDEX IF NOT EXISTS idx_eco_soil_field ON eco.soil_health_records (field_id);
    CREATE INDEX IF NOT EXISTS idx_eco_soil_tenant ON eco.soil_health_records (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_soil_date ON eco.soil_health_records (sample_date DESC);
    CREATE INDEX IF NOT EXISTS idx_eco_soil_location ON eco.soil_health_records USING GIST (sample_location);

    -- Water Conservation Records indexes
    CREATE INDEX IF NOT EXISTS idx_eco_water_farm ON eco.water_conservation_records (farm_id);
    CREATE INDEX IF NOT EXISTS idx_eco_water_field ON eco.water_conservation_records (field_id);
    CREATE INDEX IF NOT EXISTS idx_eco_water_tenant ON eco.water_conservation_records (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_water_date ON eco.water_conservation_records (record_date DESC);

    -- GlobalGAP Compliance indexes
    CREATE INDEX IF NOT EXISTS idx_eco_globalgap_farm ON eco.globalgap_ecological_compliance (farm_id);
    CREATE INDEX IF NOT EXISTS idx_eco_globalgap_tenant ON eco.globalgap_ecological_compliance (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_eco_globalgap_cp ON eco.globalgap_ecological_compliance (control_point);
    CREATE INDEX IF NOT EXISTS idx_eco_globalgap_status ON eco.globalgap_ecological_compliance (compliance_status);

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Create Updated Trigger Function
    -- إنشاء دالة التحديث التلقائي
    -- ═══════════════════════════════════════════════════════════════════════════

    -- Apply updated_at trigger to all eco tables
    CREATE OR REPLACE FUNCTION eco.update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    -- Create triggers for each table
    CREATE TRIGGER update_eco_assessments_updated_at
        BEFORE UPDATE ON eco.ecological_assessments
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_practices_updated_at
        BEFORE UPDATE ON eco.farm_practices
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_plans_updated_at
        BEFORE UPDATE ON eco.transition_plans
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_milestones_updated_at
        BEFORE UPDATE ON eco.transition_milestones
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_pitfalls_updated_at
        BEFORE UPDATE ON eco.pitfall_diagnoses
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_companion_updated_at
        BEFORE UPDATE ON eco.companion_plantings
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_biodiversity_updated_at
        BEFORE UPDATE ON eco.biodiversity_records
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_soil_updated_at
        BEFORE UPDATE ON eco.soil_health_records
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_water_updated_at
        BEFORE UPDATE ON eco.water_conservation_records
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    CREATE TRIGGER update_eco_globalgap_updated_at
        BEFORE UPDATE ON eco.globalgap_ecological_compliance
        FOR EACH ROW EXECUTE FUNCTION eco.update_updated_at_column();

    -- ═══════════════════════════════════════════════════════════════════════════
    -- Record Migration
    -- تسجيل الهجرة
    -- ═══════════════════════════════════════════════════════════════════════════
    INSERT INTO public._migrations (name) VALUES ('012_ecological_assessments');

    RAISE NOTICE 'Migration 012_ecological_assessments completed successfully';
    RAISE NOTICE '  - Created schema: eco';
    RAISE NOTICE '  - Created 10 tables for ecological agriculture tracking';
    RAISE NOTICE '  - Created indexes for performance optimization';
    RAISE NOTICE '  - Created triggers for updated_at automation';

END $$;
