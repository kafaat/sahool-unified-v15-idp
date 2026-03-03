-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Schema Isolation - Phase 1: Schema-per-Service Domain
-- عزل المخططات - المرحلة 1: مخطط لكل نطاق خدمة
-- Migration: V20260303__schema_isolation_phase1.sql
--
-- Strategy: Move from monolithic public schema to domain-isolated schemas.
-- This gives 80% of database-per-service benefit at 20% of the cost.
--
-- Schemas created:
--   field_ops     - Field management, boundaries, NDVI, sync
--   auth          - Users, sessions, tokens, roles
--   marketplace   - Products, orders, wallets, transactions
--   iot           - Devices, sensors, readings, actuators
--   weather       - Observations, forecasts, alerts, locations
--   research      - Experiments, plots, treatments, samples
--   inventory     - Items, movements, warehouses, transfers
--   disaster      - Reports, alerts, assessments, subscriptions
--   tasks         - Task management
--   notifications - Notifications, templates, preferences
--   alerts        - Alert management
--   equipment     - Equipment tracking and maintenance
--   billing       - Billing and invoicing
--   chat          - Conversations, messages, participants
--   geospatial_metadata - ISO 19115 metadata records
--   shared_types  - Shared enums and reference data (cross-service)
--
-- IMPORTANT: Phase 1 creates schemas and views. Actual table migration
-- (ALTER TABLE SET SCHEMA) should be done in Phase 2 after service code
-- is updated to use schema-qualified names.
--
-- DEPENDENCIES:
--   - 001_init_extensions.sql (PostGIS, uuid-ossp, pg_trgm, btree_gist)
--   - 010_row_level_security.sql (current_tenant_id(), is_super_admin())
--     NOTE: Fallback definitions are included if 010 hasn't run yet.
--
-- KNOWN PRE-EXISTING ISSUES:
--   - 'iot' schema is also created in 001_init_extensions.sql (safe: IF NOT EXISTS)
--   - Disaster tables have duplicate definitions in 005 and V20260130 migrations
--     (not related to this migration - tracked separately)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 1: Create domain schemas
-- القسم 1: إنشاء مخططات النطاقات
-- ─────────────────────────────────────────────────────────────────────────────

CREATE SCHEMA IF NOT EXISTS shared_types;
COMMENT ON SCHEMA shared_types IS 'Shared enums, reference data, and cross-service types | أنواع مشتركة وبيانات مرجعية';

CREATE SCHEMA IF NOT EXISTS field_ops;
COMMENT ON SCHEMA field_ops IS 'Field management: farms, fields, boundaries, NDVI, sync | إدارة الحقول';

CREATE SCHEMA IF NOT EXISTS auth;
COMMENT ON SCHEMA auth IS 'Authentication: users, sessions, tokens, roles | المصادقة والمستخدمين';

CREATE SCHEMA IF NOT EXISTS marketplace;
COMMENT ON SCHEMA marketplace IS 'Marketplace: products, orders, wallets, transactions | السوق الإلكتروني';

CREATE SCHEMA IF NOT EXISTS iot;
COMMENT ON SCHEMA iot IS 'IoT: devices, sensors, readings, actuators | إنترنت الأشياء';

CREATE SCHEMA IF NOT EXISTS weather;
COMMENT ON SCHEMA weather IS 'Weather: observations, forecasts, alerts | الطقس';

CREATE SCHEMA IF NOT EXISTS research;
COMMENT ON SCHEMA research IS 'Research: experiments, plots, treatments, samples | البحث العلمي';

CREATE SCHEMA IF NOT EXISTS inventory;
COMMENT ON SCHEMA inventory IS 'Inventory: items, movements, warehouses | المخزون';

CREATE SCHEMA IF NOT EXISTS disaster;
COMMENT ON SCHEMA disaster IS 'Disaster: reports, alerts, assessments | الكوارث';

CREATE SCHEMA IF NOT EXISTS tasks;
COMMENT ON SCHEMA tasks IS 'Task management | إدارة المهام';

CREATE SCHEMA IF NOT EXISTS notifications;
COMMENT ON SCHEMA notifications IS 'Notifications: alerts, templates, preferences | الإشعارات';

CREATE SCHEMA IF NOT EXISTS alerts;
COMMENT ON SCHEMA alerts IS 'Alert management | إدارة التنبيهات';

CREATE SCHEMA IF NOT EXISTS equipment;
COMMENT ON SCHEMA equipment IS 'Equipment tracking and maintenance | تتبع المعدات';

CREATE SCHEMA IF NOT EXISTS billing;
COMMENT ON SCHEMA billing IS 'Billing and invoicing | الفوترة';

CREATE SCHEMA IF NOT EXISTS chat;
COMMENT ON SCHEMA chat IS 'Chat: conversations, messages, participants | المحادثات';

CREATE SCHEMA IF NOT EXISTS geospatial_metadata;
COMMENT ON SCHEMA geospatial_metadata IS 'ISO 19115 geospatial metadata records | بيانات وصفية جغرافية ISO 19115';

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 2: Grant schema access to application role
-- القسم 2: منح صلاحيات الوصول للمخططات
-- ─────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    schema_name TEXT;
    schemas TEXT[] := ARRAY[
        'shared_types', 'field_ops', 'auth', 'marketplace', 'iot',
        'weather', 'research', 'inventory', 'disaster', 'tasks',
        'notifications', 'alerts', 'equipment', 'billing', 'chat',
        'geospatial_metadata'
    ];
BEGIN
    FOREACH schema_name IN ARRAY schemas LOOP
        EXECUTE format('GRANT USAGE ON SCHEMA %I TO sahool', schema_name);
        EXECUTE format('GRANT CREATE ON SCHEMA %I TO sahool', schema_name);
        EXECUTE format(
            'ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sahool',
            schema_name
        );
        EXECUTE format(
            'ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT USAGE, SELECT ON SEQUENCES TO sahool',
            schema_name
        );
    END LOOP;
END;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 3: Set search_path to include all schemas
-- القسم 3: ضبط مسار البحث ليشمل جميع المخططات
-- ─────────────────────────────────────────────────────────────────────────────

-- Update default search_path for the sahool role
ALTER ROLE sahool SET search_path TO
    public, shared_types, field_ops, auth, marketplace, iot,
    weather, research, inventory, disaster, tasks,
    notifications, alerts, equipment, billing, chat,
    geospatial_metadata;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 4: Create ISO 19115 Geospatial Metadata table
-- القسم 4: إنشاء جدول البيانات الوصفية الجغرافية ISO 19115
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS geospatial_metadata.metadata_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    domain VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,

    -- ISO 19115 MD_Metadata root
    metadata_identifier VARCHAR(255) NOT NULL UNIQUE,
    metadata_standard VARCHAR(50) NOT NULL DEFAULT 'ISO 19115-1:2014',
    metadata_standard_version VARCHAR(10) NOT NULL DEFAULT '2014',
    hierarchy_level VARCHAR(50) NOT NULL DEFAULT 'dataset',

    -- ISO 19115 MD_DataIdentification
    title VARCHAR(500) NOT NULL,
    title_ar VARCHAR(500),
    abstract TEXT NOT NULL,
    abstract_ar TEXT,
    purpose TEXT,
    purpose_ar TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'onGoing',

    -- Topic categories (ISO 19115 MD_TopicCategory)
    topic_categories TEXT[] NOT NULL DEFAULT ARRAY['farming'],

    -- Keywords
    keywords TEXT[] NOT NULL DEFAULT '{}',
    keywords_ar TEXT[] DEFAULT '{}',

    -- Spatial info
    spatial_representation_type VARCHAR(50) DEFAULT 'vector',
    spatial_resolution_m DOUBLE PRECISION,
    crs_code VARCHAR(50) NOT NULL DEFAULT 'EPSG:4326',
    crs_description VARCHAR(255) DEFAULT 'WGS 84',

    -- Geographic extent (EX_GeographicBoundingBox)
    bbox_west DOUBLE PRECISION,
    bbox_east DOUBLE PRECISION,
    bbox_south DOUBLE PRECISION,
    bbox_north DOUBLE PRECISION,
    bbox_geometry geometry(Polygon, 4326),

    -- Temporal extent
    temporal_begin TIMESTAMPTZ,
    temporal_end TIMESTAMPTZ,

    -- Vertical extent
    vertical_min_m DOUBLE PRECISION,
    vertical_max_m DOUBLE PRECISION,

    -- Responsible party (CI_ResponsibleParty)
    contact_org VARCHAR(255) DEFAULT 'KAFAAT - SAHOOL Platform',
    contact_org_ar VARCHAR(255) DEFAULT 'كفاءات - منصة سهول',
    contact_role VARCHAR(50) DEFAULT 'pointOfContact',
    contact_email VARCHAR(255),

    -- Constraints (MD_LegalConstraints)
    access_constraints TEXT[] DEFAULT ARRAY['restricted'],
    use_constraints TEXT[] DEFAULT ARRAY['intellectualPropertyRights'],

    -- Maintenance (MD_MaintenanceInformation)
    maintenance_frequency VARCHAR(50) DEFAULT 'asNeeded',

    -- Distribution (MD_Distribution)
    distribution_formats JSONB DEFAULT '[]',

    -- Data Quality (ISO 19157)
    data_quality JSONB DEFAULT '{}',

    -- Lineage (LI_Lineage)
    lineage_statement TEXT,
    lineage_statement_ar TEXT,
    lineage_sources JSONB DEFAULT '[]',
    lineage_process_steps JSONB DEFAULT '[]',

    -- Full ISO 19115 metadata as JSON (complete record)
    metadata_json JSONB NOT NULL DEFAULT '{}',

    -- Browse graphic
    thumbnail_url VARCHAR(500),

    -- SAHOOL management fields
    tags TEXT[] DEFAULT '{}',
    is_published BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT chk_domain CHECK (domain IN ('field', 'satellite', 'terrain', 'iot', 'weather', 'ndvi')),
    CONSTRAINT chk_resource_type CHECK (resource_type IN (
        'field_boundary', 'ndvi_reading', 'dem_analysis', 'satellite_image',
        'sensor_data', 'weather_observation', 'weather_forecast'
    )),
    CONSTRAINT chk_hierarchy_level CHECK (hierarchy_level IN (
        'dataset', 'series', 'service', 'feature', 'featureType', 'fieldSession',
        'software', 'model', 'tile', 'collectionHardware'
    )),
    CONSTRAINT chk_bbox_valid CHECK (
        bbox_west IS NULL OR (
            bbox_west >= -180 AND bbox_west <= 180 AND
            bbox_east >= -180 AND bbox_east <= 180 AND
            bbox_south >= -90 AND bbox_south <= 90 AND
            bbox_north >= -90 AND bbox_north <= 90 AND
            bbox_east >= bbox_west AND bbox_north >= bbox_south
        )
    )
);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 5: Indexes for metadata_records
-- القسم 5: فهارس جدول البيانات الوصفية
-- ─────────────────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_metadata_tenant_id
    ON geospatial_metadata.metadata_records (tenant_id);

CREATE INDEX IF NOT EXISTS idx_metadata_domain
    ON geospatial_metadata.metadata_records (domain);

CREATE INDEX IF NOT EXISTS idx_metadata_resource
    ON geospatial_metadata.metadata_records (resource_id, resource_type);

CREATE INDEX IF NOT EXISTS idx_metadata_tenant_domain
    ON geospatial_metadata.metadata_records (tenant_id, domain);

CREATE INDEX IF NOT EXISTS idx_metadata_crs
    ON geospatial_metadata.metadata_records (crs_code);

CREATE INDEX IF NOT EXISTS idx_metadata_created_at
    ON geospatial_metadata.metadata_records (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_metadata_tags
    ON geospatial_metadata.metadata_records USING GIN (tags);

CREATE INDEX IF NOT EXISTS idx_metadata_keywords
    ON geospatial_metadata.metadata_records USING GIN (keywords);

CREATE INDEX IF NOT EXISTS idx_metadata_bbox
    ON geospatial_metadata.metadata_records USING GIST (bbox_geometry);

CREATE INDEX IF NOT EXISTS idx_metadata_temporal
    ON geospatial_metadata.metadata_records (temporal_begin, temporal_end);

CREATE INDEX IF NOT EXISTS idx_metadata_quality
    ON geospatial_metadata.metadata_records USING GIN (data_quality);

CREATE INDEX IF NOT EXISTS idx_metadata_json
    ON geospatial_metadata.metadata_records USING GIN (metadata_json);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 6: Lineage tracking table
-- القسم 6: جدول تتبع النسب
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS geospatial_metadata.lineage_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metadata_record_id UUID NOT NULL REFERENCES geospatial_metadata.metadata_records(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,

    -- Source info
    source_description TEXT NOT NULL,
    source_description_ar TEXT,
    source_citation JSONB DEFAULT '{}',
    source_crs VARCHAR(50),
    source_resolution_m DOUBLE PRECISION,
    source_extent JSONB DEFAULT '{}',

    -- Process step
    step_order INTEGER NOT NULL DEFAULT 0,
    step_description TEXT NOT NULL,
    step_description_ar TEXT,
    step_rationale TEXT,
    step_datetime TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    step_processor VARCHAR(255),
    step_software VARCHAR(255),
    step_algorithm VARCHAR(255),
    step_parameters JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lineage_metadata_id
    ON geospatial_metadata.lineage_records (metadata_record_id);

CREATE INDEX IF NOT EXISTS idx_lineage_tenant_id
    ON geospatial_metadata.lineage_records (tenant_id);

CREATE INDEX IF NOT EXISTS idx_lineage_step_order
    ON geospatial_metadata.lineage_records (metadata_record_id, step_order);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 7: Data quality assessment table
-- القسم 7: جدول تقييم جودة البيانات
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS geospatial_metadata.quality_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metadata_record_id UUID NOT NULL REFERENCES geospatial_metadata.metadata_records(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,

    -- ISO 19157 DQ_Element
    quality_type VARCHAR(50) NOT NULL,
    quality_type_ar VARCHAR(100),
    element_name VARCHAR(255) NOT NULL,
    element_name_ar VARCHAR(255),
    measure_description TEXT,
    measure_description_ar TEXT,
    evaluation_method VARCHAR(255),

    -- Quantitative result
    result_value DOUBLE PRECISION,
    result_unit VARCHAR(20),
    result_type VARCHAR(20) DEFAULT 'measure',

    -- Conformance result
    conformance_specification VARCHAR(255),
    conformance_explanation TEXT,
    is_conformant BOOLEAN,

    assessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_quality_type CHECK (quality_type IN (
        'completeness', 'logicalConsistency', 'positionalAccuracy',
        'temporalQuality', 'thematicAccuracy'
    ))
);

CREATE INDEX IF NOT EXISTS idx_quality_metadata_id
    ON geospatial_metadata.quality_assessments (metadata_record_id);

CREATE INDEX IF NOT EXISTS idx_quality_tenant_id
    ON geospatial_metadata.quality_assessments (tenant_id);

CREATE INDEX IF NOT EXISTS idx_quality_type
    ON geospatial_metadata.quality_assessments (quality_type);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 8: Enable RLS on new tables
-- القسم 8: تفعيل أمان مستوى الصف على الجداول الجديدة
--
-- DEPENDENCY: Requires current_tenant_id() and is_super_admin() from
-- 010_row_level_security.sql. If those functions don't exist, we create
-- fallback versions to ensure this migration can run independently.
-- ─────────────────────────────────────────────────────────────────────────────

-- Ensure RLS helper functions exist (idempotent - won't overwrite 010's versions)
DO $$
BEGIN
    -- Create current_tenant_id() if not exists (defined in 010_row_level_security.sql)
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc WHERE proname = 'current_tenant_id'
    ) THEN
        EXECUTE $func$
            CREATE FUNCTION current_tenant_id() RETURNS UUID AS $body$
            BEGIN
                RETURN NULLIF(current_setting('app.current_tenant', true), '')::UUID;
            EXCEPTION WHEN OTHERS THEN RETURN NULL;
            END;
            $body$ LANGUAGE plpgsql SECURITY DEFINER STABLE;
        $func$;
        RAISE NOTICE 'Created fallback current_tenant_id() function';
    END IF;

    -- Create is_super_admin() if not exists (defined in 010_row_level_security.sql)
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc WHERE proname = 'is_super_admin'
    ) THEN
        EXECUTE $func$
            CREATE FUNCTION is_super_admin() RETURNS BOOLEAN AS $body$
            BEGIN
                RETURN COALESCE(current_setting('app.is_super_admin', true), 'false')::BOOLEAN;
            EXCEPTION WHEN OTHERS THEN RETURN FALSE;
            END;
            $body$ LANGUAGE plpgsql SECURITY DEFINER STABLE;
        $func$;
        RAISE NOTICE 'Created fallback is_super_admin() function';
    END IF;
END;
$$;

ALTER TABLE geospatial_metadata.metadata_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE geospatial_metadata.lineage_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE geospatial_metadata.quality_assessments ENABLE ROW LEVEL SECURITY;

-- RLS Policies (idempotent with DROP IF EXISTS)
DROP POLICY IF EXISTS metadata_records_tenant_isolation ON geospatial_metadata.metadata_records;
CREATE POLICY metadata_records_tenant_isolation
    ON geospatial_metadata.metadata_records
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

DROP POLICY IF EXISTS lineage_records_tenant_isolation ON geospatial_metadata.lineage_records;
CREATE POLICY lineage_records_tenant_isolation
    ON geospatial_metadata.lineage_records
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

DROP POLICY IF EXISTS quality_assessments_tenant_isolation ON geospatial_metadata.quality_assessments;
CREATE POLICY quality_assessments_tenant_isolation
    ON geospatial_metadata.quality_assessments
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 9: Auto-generate bbox_geometry trigger
-- القسم 9: مشغّل لإنشاء هندسة الحدود تلقائياً
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION geospatial_metadata.update_bbox_geometry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.bbox_west IS NOT NULL AND NEW.bbox_east IS NOT NULL
       AND NEW.bbox_south IS NOT NULL AND NEW.bbox_north IS NOT NULL THEN
        NEW.bbox_geometry := ST_SetSRID(ST_MakeEnvelope(
            NEW.bbox_west, NEW.bbox_south,
            NEW.bbox_east, NEW.bbox_north
        ), 4326);
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_metadata_bbox_geometry
    BEFORE INSERT OR UPDATE ON geospatial_metadata.metadata_records
    FOR EACH ROW
    EXECUTE FUNCTION geospatial_metadata.update_bbox_geometry();

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 10: Schema mapping reference table
-- القسم 10: جدول مرجعي لخريطة المخططات
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS shared_types.schema_service_mapping (
    id SERIAL PRIMARY KEY,
    schema_name VARCHAR(63) NOT NULL UNIQUE,
    service_name VARCHAR(255) NOT NULL,
    service_type VARCHAR(20) NOT NULL DEFAULT 'python',
    description TEXT,
    description_ar TEXT,
    tables_count INTEGER DEFAULT 0,
    migration_status VARCHAR(50) NOT NULL DEFAULT 'phase1_schema_created',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_service_type CHECK (service_type IN ('python', 'nodejs')),
    CONSTRAINT chk_migration_status CHECK (migration_status IN (
        'phase1_schema_created',
        'phase2_views_created',
        'phase3_tables_migrated',
        'phase4_fk_updated',
        'completed'
    ))
);

-- Seed the mapping table
INSERT INTO shared_types.schema_service_mapping
    (schema_name, service_name, service_type, description, description_ar, tables_count, migration_status)
VALUES
    ('field_ops', 'field-management-service', 'nodejs',
     'Field management: farms, fields, boundaries, NDVI, sync', 'إدارة الحقول والحدود', 6, 'phase1_schema_created'),
    ('auth', 'user-service', 'nodejs',
     'Authentication: users, sessions, tokens, roles', 'المصادقة والمستخدمين', 5, 'phase1_schema_created'),
    ('marketplace', 'marketplace-service', 'nodejs',
     'Marketplace: products, orders, wallets, transactions', 'السوق الإلكتروني', 11, 'phase1_schema_created'),
    ('iot', 'iot-service', 'nodejs',
     'IoT: devices, sensors, readings, actuators', 'إنترنت الأشياء', 6, 'phase1_schema_created'),
    ('weather', 'weather-service', 'nodejs',
     'Weather: observations, forecasts, alerts', 'الطقس', 4, 'phase1_schema_created'),
    ('research', 'research-core', 'nodejs',
     'Research: experiments, plots, treatments', 'البحث العلمي', 12, 'phase1_schema_created'),
    ('inventory', 'inventory-service', 'nodejs',
     'Inventory: items, movements, warehouses', 'المخزون', 8, 'phase1_schema_created'),
    ('disaster', 'disaster-assessment', 'nodejs',
     'Disaster: reports, alerts, assessments', 'الكوارث', 5, 'phase1_schema_created'),
    ('tasks', 'task-service', 'python',
     'Task management', 'إدارة المهام', 1, 'phase1_schema_created'),
    ('notifications', 'notification-service', 'python',
     'Notifications and preferences', 'الإشعارات', 3, 'phase1_schema_created'),
    ('alerts', 'alert-service', 'python',
     'Alert management', 'إدارة التنبيهات', 3, 'phase1_schema_created'),
    ('equipment', 'equipment-service', 'python',
     'Equipment tracking', 'تتبع المعدات', 2, 'phase1_schema_created'),
    ('billing', 'billing-core', 'python',
     'Billing and invoicing', 'الفوترة', 2, 'phase1_schema_created'),
    ('chat', 'chat-service', 'nodejs',
     'Chat: conversations, messages, participants', 'المحادثات', 3, 'phase1_schema_created'),
    ('geospatial_metadata', 'geospatial-metadata', 'python',
     'ISO 19115 geospatial metadata', 'بيانات وصفية ISO 19115', 3, 'completed')
ON CONFLICT (schema_name) DO UPDATE SET
    updated_at = NOW(),
    migration_status = EXCLUDED.migration_status;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 11: Cross-schema reference tracking
-- القسم 11: تتبع المراجع بين المخططات
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS shared_types.cross_schema_references (
    id SERIAL PRIMARY KEY,
    source_schema VARCHAR(63) NOT NULL,
    source_table VARCHAR(63) NOT NULL,
    source_column VARCHAR(63) NOT NULL,
    target_schema VARCHAR(63) NOT NULL,
    target_table VARCHAR(63) NOT NULL,
    target_column VARCHAR(63) NOT NULL DEFAULT 'id',
    reference_type VARCHAR(20) NOT NULL DEFAULT 'soft',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_reference_type CHECK (reference_type IN ('hard_fk', 'soft', 'event_driven')),
    CONSTRAINT uq_cross_ref UNIQUE (source_schema, source_table, source_column, target_schema, target_table)
);

-- Document known cross-service references
INSERT INTO shared_types.cross_schema_references
    (source_schema, source_table, source_column, target_schema, target_table, target_column, reference_type, description)
VALUES
    ('field_ops', 'fields', 'owner_id', 'auth', 'users', 'id', 'soft',
     'Field owner reference to user'),
    ('field_ops', 'farms', 'owner_id', 'auth', 'users', 'id', 'soft',
     'Farm owner reference to user'),
    ('disaster', 'field_assessments', 'field_id', 'field_ops', 'fields', 'id', 'soft',
     'Disaster assessment linked to field'),
    ('tasks', 'tasks', 'field_id', 'field_ops', 'fields', 'id', 'soft',
     'Task assigned to field'),
    ('tasks', 'tasks', 'assigned_to', 'auth', 'users', 'id', 'soft',
     'Task assigned to user'),
    ('marketplace', 'orders', 'buyer_id', 'auth', 'users', 'id', 'soft',
     'Order buyer reference'),
    ('marketplace', 'products', 'seller_id', 'auth', 'users', 'id', 'soft',
     'Product seller reference'),
    ('iot', 'devices', 'field_id', 'field_ops', 'fields', 'id', 'soft',
     'IoT device deployed in field'),
    ('geospatial_metadata', 'metadata_records', 'resource_id', 'field_ops', 'fields', 'id', 'soft',
     'Metadata linked to field')
ON CONFLICT (source_schema, source_table, source_column, target_schema, target_table)
DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 12: Helper function for schema-qualified table access
-- القسم 12: دالة مساعدة للوصول المؤهل بالمخطط
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION shared_types.get_schema_for_service(p_service_name VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_schema VARCHAR;
BEGIN
    SELECT schema_name INTO v_schema
    FROM shared_types.schema_service_mapping
    WHERE service_name = p_service_name;

    IF v_schema IS NULL THEN
        RETURN 'public';
    END IF;

    RETURN v_schema;
END;
$$ LANGUAGE plpgsql STABLE;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 13: Migration status summary
-- القسم 13: ملخص حالة الترحيل
-- ─────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    schema_count INTEGER;
    table_count INTEGER;
    ref_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO schema_count
    FROM information_schema.schemata
    WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public', 'topology');

    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'geospatial_metadata' AND table_type = 'BASE TABLE';

    SELECT COUNT(*) INTO ref_count
    FROM shared_types.cross_schema_references;

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  SCHEMA ISOLATION - Phase 1 COMPLETE';
    RAISE NOTICE '  عزل المخططات - المرحلة 1 مكتملة';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  Domain schemas created:     %', schema_count;
    RAISE NOTICE '  Metadata tables created:    %', table_count;
    RAISE NOTICE '  Cross-schema refs tracked:  %', ref_count;
    RAISE NOTICE '';
    RAISE NOTICE '  Phase 1: ✅ Schemas created + metadata tables';
    RAISE NOTICE '  Phase 2: ⏳ Create views in new schemas pointing to public';
    RAISE NOTICE '  Phase 3: ⏳ Move tables from public to domain schemas';
    RAISE NOTICE '  Phase 4: ⏳ Update cross-schema FKs to soft references';
    RAISE NOTICE '';
    RAISE NOTICE '  New ISO 19115 tables (geospatial_metadata schema):';
    RAISE NOTICE '    - metadata_records (with PostGIS spatial index)';
    RAISE NOTICE '    - lineage_records (ISO 19115 LI_Lineage)';
    RAISE NOTICE '    - quality_assessments (ISO 19157 DQ_Element)';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
