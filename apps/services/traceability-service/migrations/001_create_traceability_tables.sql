-- Migration: 001_create_traceability_tables
-- Description: Create supply chain traceability tables - إنشاء جداول تتبع سلسلة التوريد
-- Service: traceability-service
-- Date: 2026-02-14

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- Produce Batches - دفعات المنتجات
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS produce_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    farm_id VARCHAR(100) NOT NULL,
    field_id VARCHAR(100) NOT NULL,

    -- Product Details - تفاصيل المنتج
    batch_code VARCHAR(50) NOT NULL,
    product_name_en VARCHAR(200) NOT NULL,
    product_name_ar VARCHAR(200) NOT NULL,
    variety VARCHAR(100),
    quantity DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',

    -- Quality - الجودة
    quality_grade VARCHAR(20) DEFAULT 'A',

    -- Status - الحالة
    status VARCHAR(30) NOT NULL DEFAULT 'created',

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_batch_status CHECK (status IN (
        'created', 'harvested', 'in_processing', 'in_storage',
        'in_transit', 'at_retail', 'sold', 'expired', 'recalled'
    )),
    CONSTRAINT valid_quality_grade CHECK (quality_grade IN ('premium', 'A', 'B', 'C', 'rejected')),
    CONSTRAINT valid_quantity CHECK (quantity > 0),
    CONSTRAINT unique_batch_code UNIQUE (batch_code)
);

COMMENT ON TABLE produce_batches IS 'Produce batch records for supply chain tracking - سجلات الدفعات لتتبع سلسلة التوريد';

CREATE INDEX IF NOT EXISTS idx_batches_tenant_id ON produce_batches(tenant_id);
CREATE INDEX IF NOT EXISTS idx_batches_farm_id ON produce_batches(farm_id);
CREATE INDEX IF NOT EXISTS idx_batches_field_id ON produce_batches(field_id);
CREATE INDEX IF NOT EXISTS idx_batches_batch_code ON produce_batches(batch_code);
CREATE INDEX IF NOT EXISTS idx_batches_status ON produce_batches(status);
CREATE INDEX IF NOT EXISTS idx_batches_tenant_status ON produce_batches(tenant_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_batches_product ON produce_batches(product_name_en);

-- ─────────────────────────────────────────────────────────────────────────────
-- Supply Chain Events - أحداث سلسلة التوريد
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS supply_chain_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID NOT NULL REFERENCES produce_batches(id) ON DELETE CASCADE,

    -- Event Details - تفاصيل الحدث
    event_type VARCHAR(30) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Location - الموقع
    location VARCHAR(200),
    location_ar VARCHAR(200),

    -- Event-Specific Data - بيانات خاصة بالحدث
    -- Harvest
    crop_type VARCHAR(100),
    harvest_method VARCHAR(100),
    quality_grade VARCHAR(20),

    -- Processing
    facility_name VARCHAR(200),
    process_type VARCHAR(100),

    -- Storage
    temperature_c DECIMAL(5, 1),
    humidity_percent DECIMAL(5, 1),

    -- Transport
    origin VARCHAR(200),
    destination VARCHAR(200),
    transport_mode VARCHAR(30),
    vehicle_id VARCHAR(100),

    -- Notes
    notes TEXT,
    notes_ar TEXT,

    -- Metadata - البيانات الوصفية
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'harvest', 'processing', 'storage', 'transport',
        'retail', 'consumer_scan', 'quality_check', 'certification'
    )),
    CONSTRAINT valid_transport_mode CHECK (
        transport_mode IS NULL OR transport_mode IN (
            'truck_refrigerated', 'truck_ambient', 'air', 'sea',
            'rail', 'local_delivery', 'truck'
        )
    )
);

COMMENT ON TABLE supply_chain_events IS 'Supply chain event log - سجل أحداث سلسلة التوريد';

CREATE INDEX IF NOT EXISTS idx_events_batch_id ON supply_chain_events(batch_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON supply_chain_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON supply_chain_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_batch_type ON supply_chain_events(batch_id, event_type, timestamp DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- Certifications - الشهادات
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS batch_certifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID NOT NULL REFERENCES produce_batches(id) ON DELETE CASCADE,

    -- Certification Details - تفاصيل الشهادة
    certification_type VARCHAR(30) NOT NULL,
    certificate_number VARCHAR(100),
    issuing_body VARCHAR(200),
    valid_from DATE,
    valid_until DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- Timestamps - الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_cert_type CHECK (certification_type IN (
        'globalgap', 'organic', 'halal', 'saso', 'sfda',
        'iso22000', 'haccp', 'fair_trade'
    )),
    CONSTRAINT valid_cert_status CHECK (status IN ('active', 'expired', 'revoked', 'pending'))
);

COMMENT ON TABLE batch_certifications IS 'Batch certification records - سجلات شهادات الدفعات';

CREATE INDEX IF NOT EXISTS idx_certs_batch_id ON batch_certifications(batch_id);
CREATE INDEX IF NOT EXISTS idx_certs_type ON batch_certifications(certification_type);
CREATE INDEX IF NOT EXISTS idx_certs_status ON batch_certifications(status);

-- Updated_at Triggers - مشغلات تحديث التاريخ
CREATE OR REPLACE FUNCTION update_traceability_tables_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_batches_updated_at
    BEFORE UPDATE ON produce_batches
    FOR EACH ROW
    EXECUTE FUNCTION update_traceability_tables_updated_at();

-- Migration tracking
INSERT INTO public._migrations (name) VALUES ('001_create_traceability_tables')
ON CONFLICT (name) DO NOTHING;
