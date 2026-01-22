-- SAHOOL CRM Service - Initial Database Schema
-- Migration: 001_initial_schema
-- Created: 2026-01-22
-- Description: Create farmers, harvest_deals, and interactions tables

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- FARMERS TABLE
-- =============================================================================
-- Stores farmer (customer) information for CRM
-- جدول المزارعين (العملاء) لإدارة العلاقات

CREATE TABLE IF NOT EXISTS farmers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,

    -- Basic Information
    name VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    national_id VARCHAR(50),

    -- Farm Details
    farm_size_hectares DECIMAL(10, 2),
    location VARCHAR(255),
    location_ar VARCHAR(255),
    crops JSONB DEFAULT '[]'::jsonb,

    -- CRM Fields
    status VARCHAR(50) NOT NULL DEFAULT 'lead',
    engagement_score DECIMAL(5, 2) DEFAULT 0.0,
    tags JSONB DEFAULT '[]'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_interaction_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_farmer_status CHECK (
        status IN ('lead', 'registered', 'active', 'premium', 'churned')
    ),
    CONSTRAINT chk_engagement_score CHECK (
        engagement_score >= 0 AND engagement_score <= 100
    )
);

-- Indexes for farmers table
CREATE INDEX IF NOT EXISTS idx_farmers_tenant_id ON farmers(tenant_id);
CREATE INDEX IF NOT EXISTS idx_farmers_status ON farmers(status);
CREATE INDEX IF NOT EXISTS idx_farmers_phone ON farmers(phone);
CREATE INDEX IF NOT EXISTS idx_farmers_email ON farmers(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_farmers_created_at ON farmers(created_at);
CREATE INDEX IF NOT EXISTS idx_farmers_tenant_status ON farmers(tenant_id, status);


-- =============================================================================
-- HARVEST DEALS TABLE
-- =============================================================================
-- Stores harvest/supply deals (opportunities) for CRM pipeline
-- جدول صفقات الحصاد/التوريد (الفرص) لخط أنابيب إدارة العلاقات

CREATE TABLE IF NOT EXISTS harvest_deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,

    -- Deal Details
    crop_type VARCHAR(100) NOT NULL,
    crop_type_ar VARCHAR(100),
    quantity_tons DECIMAL(10, 2) NOT NULL,
    price_per_ton DECIMAL(12, 2),
    total_value DECIMAL(14, 2) GENERATED ALWAYS AS (
        COALESCE(quantity_tons * price_per_ton, 0)
    ) STORED,

    -- Actual Values (after delivery)
    actual_quantity_tons DECIMAL(10, 2),
    actual_harvest_date DATE,

    -- Timing
    expected_harvest_date DATE,

    -- Pipeline Stage
    stage VARCHAR(50) NOT NULL DEFAULT 'prospecting',
    probability DECIMAL(3, 2) DEFAULT 0.1,

    -- Notes
    notes TEXT,
    notes_ar TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT chk_deal_stage CHECK (
        stage IN ('prospecting', 'qualification', 'negotiation', 'contracted', 'delivered', 'paid', 'closed_lost')
    ),
    CONSTRAINT chk_quantity_positive CHECK (quantity_tons > 0),
    CONSTRAINT chk_price_positive CHECK (price_per_ton IS NULL OR price_per_ton > 0),
    CONSTRAINT chk_probability CHECK (probability >= 0 AND probability <= 1)
);

-- Indexes for harvest_deals table
CREATE INDEX IF NOT EXISTS idx_harvest_deals_tenant_id ON harvest_deals(tenant_id);
CREATE INDEX IF NOT EXISTS idx_harvest_deals_farmer_id ON harvest_deals(farmer_id);
CREATE INDEX IF NOT EXISTS idx_harvest_deals_stage ON harvest_deals(stage);
CREATE INDEX IF NOT EXISTS idx_harvest_deals_crop_type ON harvest_deals(crop_type);
CREATE INDEX IF NOT EXISTS idx_harvest_deals_created_at ON harvest_deals(created_at);
CREATE INDEX IF NOT EXISTS idx_harvest_deals_tenant_stage ON harvest_deals(tenant_id, stage);
CREATE INDEX IF NOT EXISTS idx_harvest_deals_tenant_farmer ON harvest_deals(tenant_id, farmer_id);


-- =============================================================================
-- INTERACTIONS TABLE
-- =============================================================================
-- Stores farmer interaction records (activities) for CRM
-- جدول سجلات تفاعل المزارعين (الأنشطة) لإدارة العلاقات

CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,

    -- Interaction Details
    interaction_type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) DEFAULT 'app',

    -- Content
    subject VARCHAR(255) NOT NULL,
    subject_ar VARCHAR(255),
    notes TEXT,
    notes_ar TEXT,

    -- Outcome
    outcome VARCHAR(255),
    sentiment_score DECIMAL(3, 2),

    -- Follow-up
    follow_up_date DATE,
    follow_up_completed BOOLEAN DEFAULT FALSE,

    -- User who created
    created_by VARCHAR(100),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_interaction_type CHECK (
        interaction_type IN ('advisory', 'support', 'sales', 'training', 'inspection', 'call', 'visit', 'whatsapp', 'sms', 'email')
    ),
    CONSTRAINT chk_channel CHECK (
        channel IN ('app', 'phone', 'whatsapp', 'sms', 'email', 'in_person', 'web')
    ),
    CONSTRAINT chk_sentiment_score CHECK (
        sentiment_score IS NULL OR (sentiment_score >= -1 AND sentiment_score <= 1)
    )
);

-- Indexes for interactions table
CREATE INDEX IF NOT EXISTS idx_interactions_tenant_id ON interactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_interactions_farmer_id ON interactions(farmer_id);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_interactions_created_at ON interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_interactions_tenant_farmer ON interactions(tenant_id, farmer_id);
CREATE INDEX IF NOT EXISTS idx_interactions_follow_up ON interactions(follow_up_date)
    WHERE follow_up_date IS NOT NULL AND follow_up_completed = FALSE;


-- =============================================================================
-- TRIGGER FUNCTIONS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for farmers table
DROP TRIGGER IF EXISTS trigger_farmers_updated_at ON farmers;
CREATE TRIGGER trigger_farmers_updated_at
    BEFORE UPDATE ON farmers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for harvest_deals table
DROP TRIGGER IF EXISTS trigger_harvest_deals_updated_at ON harvest_deals;
CREATE TRIGGER trigger_harvest_deals_updated_at
    BEFORE UPDATE ON harvest_deals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Function to update farmer's last_interaction_at when a new interaction is created
CREATE OR REPLACE FUNCTION update_farmer_last_interaction()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE farmers
    SET last_interaction_at = NEW.created_at,
        updated_at = NOW()
    WHERE id = NEW.farmer_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for interactions table
DROP TRIGGER IF EXISTS trigger_update_farmer_interaction ON interactions;
CREATE TRIGGER trigger_update_farmer_interaction
    AFTER INSERT ON interactions
    FOR EACH ROW
    EXECUTE FUNCTION update_farmer_last_interaction();


-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE farmers IS 'Farmer (customer) records for CRM - سجلات المزارعين (العملاء) لإدارة العلاقات';
COMMENT ON TABLE harvest_deals IS 'Harvest/supply deal pipeline - خط أنابيب صفقات الحصاد/التوريد';
COMMENT ON TABLE interactions IS 'Farmer interaction history - سجل تفاعلات المزارعين';

COMMENT ON COLUMN farmers.status IS 'Farmer engagement status: lead, registered, active, premium, churned';
COMMENT ON COLUMN farmers.engagement_score IS 'Calculated engagement score 0-100';
COMMENT ON COLUMN harvest_deals.stage IS 'Deal pipeline stage: prospecting, qualification, negotiation, contracted, delivered, paid, closed_lost';
COMMENT ON COLUMN harvest_deals.probability IS 'Win probability 0.0-1.0 based on stage';
COMMENT ON COLUMN interactions.sentiment_score IS 'Sentiment analysis score -1.0 (negative) to 1.0 (positive)';
