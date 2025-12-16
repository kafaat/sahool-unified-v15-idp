-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Research Core Database Schema v15.3
-- نواة البحث العلمي - قاعدة البيانات
-- ═══════════════════════════════════════════════════════════════════════════════

-- Enable PostGIS extension for geospatial data
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ─────────────────────────────────────────────────────────────────────────────
-- ENUM Types
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TYPE experiment_status AS ENUM ('draft', 'active', 'locked', 'completed', 'archived');
CREATE TYPE sample_type AS ENUM ('soil', 'plant', 'water', 'pest', 'other');
CREATE TYPE treatment_type AS ENUM ('fertilizer', 'pesticide', 'irrigation', 'seed_variety', 'other');
CREATE TYPE log_category AS ENUM ('observation', 'measurement', 'treatment', 'harvest', 'weather', 'pest', 'other');

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: experiments (التجارب البحثية)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    hypothesis TEXT,
    hypothesis_ar TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    status experiment_status DEFAULT 'draft',
    locked_at TIMESTAMP WITH TIME ZONE,
    locked_by UUID,
    principal_researcher_id UUID NOT NULL,
    organization_id UUID,
    farm_id UUID,
    location GEOGRAPHY(POINT, 4326),
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,

    CONSTRAINT valid_date_range CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Indexes for experiments
CREATE INDEX idx_experiments_status ON experiments(status);
CREATE INDEX idx_experiments_researcher ON experiments(principal_researcher_id);
CREATE INDEX idx_experiments_dates ON experiments(start_date, end_date);
CREATE INDEX idx_experiments_location ON experiments USING GIST(location);
CREATE INDEX idx_experiments_tags ON experiments USING GIN(tags);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: research_protocols (بروتوكولات البحث)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE research_protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description TEXT,
    description_ar TEXT,
    methodology TEXT NOT NULL,
    methodology_ar TEXT,
    variables JSONB DEFAULT '{}',
    measurement_schedule JSONB DEFAULT '{}',
    equipment_required TEXT[],
    safety_guidelines TEXT,
    version INTEGER DEFAULT 1,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_protocols_experiment ON research_protocols(experiment_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: research_plots (قطع البحث)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE research_plots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_code VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    name_ar VARCHAR(255),
    area_sqm DECIMAL(10, 2),
    boundary GEOGRAPHY(POLYGON, 4326),
    centroid GEOGRAPHY(POINT, 4326),
    soil_type VARCHAR(100),
    soil_ph DECIMAL(4, 2),
    previous_crop VARCHAR(100),
    replicate_number INTEGER DEFAULT 1,
    block_number INTEGER,
    row_number INTEGER,
    column_number INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_plot_code_per_experiment UNIQUE(experiment_id, plot_code)
);

CREATE INDEX idx_plots_experiment ON research_plots(experiment_id);
CREATE INDEX idx_plots_boundary ON research_plots USING GIST(boundary);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: treatments (المعاملات)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_id UUID REFERENCES research_plots(id) ON DELETE SET NULL,
    treatment_code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    type treatment_type NOT NULL,
    description TEXT,
    description_ar TEXT,
    dosage VARCHAR(100),
    dosage_unit VARCHAR(50),
    application_method VARCHAR(100),
    application_frequency VARCHAR(100),
    start_date DATE,
    end_date DATE,
    is_control BOOLEAN DEFAULT FALSE,
    parameters JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_treatments_experiment ON treatments(experiment_id);
CREATE INDEX idx_treatments_plot ON treatments(plot_id);
CREATE INDEX idx_treatments_type ON treatments(type);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: research_daily_logs (السجلات اليومية)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE research_daily_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_id UUID REFERENCES research_plots(id) ON DELETE SET NULL,
    treatment_id UUID REFERENCES treatments(id) ON DELETE SET NULL,
    log_date DATE NOT NULL,
    log_time TIME,
    category log_category NOT NULL,
    title VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    notes TEXT,
    notes_ar TEXT,
    measurements JSONB DEFAULT '{}',
    weather_conditions JSONB DEFAULT '{}',
    photos TEXT[] DEFAULT '{}',
    attachments TEXT[] DEFAULT '{}',
    recorded_by UUID NOT NULL,
    device_id VARCHAR(100),
    location GEOGRAPHY(POINT, 4326),
    synced_at TIMESTAMP WITH TIME ZONE,
    offline_id VARCHAR(100),
    hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_offline_id UNIQUE(offline_id)
);

CREATE INDEX idx_logs_experiment ON research_daily_logs(experiment_id);
CREATE INDEX idx_logs_plot ON research_daily_logs(plot_id);
CREATE INDEX idx_logs_date ON research_daily_logs(log_date);
CREATE INDEX idx_logs_category ON research_daily_logs(category);
CREATE INDEX idx_logs_recorded_by ON research_daily_logs(recorded_by);
CREATE INDEX idx_logs_offline ON research_daily_logs(offline_id) WHERE offline_id IS NOT NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: lab_samples (عينات المختبر)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE lab_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    plot_id UUID REFERENCES research_plots(id) ON DELETE SET NULL,
    log_id UUID REFERENCES research_daily_logs(id) ON DELETE SET NULL,
    sample_code VARCHAR(100) NOT NULL UNIQUE,
    type sample_type NOT NULL,
    description TEXT,
    description_ar TEXT,
    collection_date DATE NOT NULL,
    collection_time TIME,
    collection_location GEOGRAPHY(POINT, 4326),
    collected_by UUID NOT NULL,
    storage_location VARCHAR(255),
    storage_conditions VARCHAR(255),
    quantity DECIMAL(10, 3),
    quantity_unit VARCHAR(50),
    analysis_status VARCHAR(50) DEFAULT 'pending',
    analysis_results JSONB DEFAULT '{}',
    analyzed_by UUID,
    analyzed_at TIMESTAMP WITH TIME ZONE,
    photos TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_experiment ON lab_samples(experiment_id);
CREATE INDEX idx_samples_plot ON lab_samples(plot_id);
CREATE INDEX idx_samples_type ON lab_samples(type);
CREATE INDEX idx_samples_date ON lab_samples(collection_date);
CREATE INDEX idx_samples_status ON lab_samples(analysis_status);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: digital_signatures (التوقيعات الرقمية)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE digital_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    signer_id UUID NOT NULL,
    signature_hash VARCHAR(128) NOT NULL,
    algorithm VARCHAR(50) DEFAULT 'HMAC-SHA256',
    payload_hash VARCHAR(128) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    device_info JSONB DEFAULT '{}',
    purpose VARCHAR(100),
    is_valid BOOLEAN DEFAULT TRUE,
    invalidated_at TIMESTAMP WITH TIME ZONE,
    invalidated_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_entity_signature UNIQUE(entity_type, entity_id, signer_id, purpose)
);

CREATE INDEX idx_signatures_entity ON digital_signatures(entity_type, entity_id);
CREATE INDEX idx_signatures_signer ON digital_signatures(signer_id);
CREATE INDEX idx_signatures_timestamp ON digital_signatures(timestamp);
CREATE INDEX idx_signatures_valid ON digital_signatures(is_valid) WHERE is_valid = TRUE;

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: experiment_collaborators (المتعاونون في التجربة)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE experiment_collaborators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,
    permissions JSONB DEFAULT '{"read": true, "write": false, "admin": false}',
    invited_by UUID,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_collaborator UNIQUE(experiment_id, user_id)
);

CREATE INDEX idx_collaborators_experiment ON experiment_collaborators(experiment_id);
CREATE INDEX idx_collaborators_user ON experiment_collaborators(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Table: experiment_audit_log (سجل التدقيق)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE experiment_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES experiments(id) ON DELETE SET NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_audit_experiment ON experiment_audit_log(experiment_id);
CREATE INDEX idx_audit_entity ON experiment_audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_action ON experiment_audit_log(action);
CREATE INDEX idx_audit_changed_at ON experiment_audit_log(changed_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- Functions and Triggers
-- ─────────────────────────────────────────────────────────────────────────────

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_experiments_updated_at BEFORE UPDATE ON experiments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_protocols_updated_at BEFORE UPDATE ON research_protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plots_updated_at BEFORE UPDATE ON research_plots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_treatments_updated_at BEFORE UPDATE ON treatments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_logs_updated_at BEFORE UPDATE ON research_daily_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_samples_updated_at BEFORE UPDATE ON lab_samples
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to prevent modification of locked experiments
CREATE OR REPLACE FUNCTION prevent_locked_experiment_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT status FROM experiments WHERE id = COALESCE(NEW.experiment_id, OLD.experiment_id)) = 'locked' THEN
        RAISE EXCEPTION 'Cannot modify data for a locked experiment';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply lock protection to related tables
CREATE TRIGGER check_experiment_lock_protocols BEFORE INSERT OR UPDATE OR DELETE ON research_protocols
    FOR EACH ROW EXECUTE FUNCTION prevent_locked_experiment_modification();

CREATE TRIGGER check_experiment_lock_plots BEFORE INSERT OR UPDATE OR DELETE ON research_plots
    FOR EACH ROW EXECUTE FUNCTION prevent_locked_experiment_modification();

CREATE TRIGGER check_experiment_lock_treatments BEFORE INSERT OR UPDATE OR DELETE ON treatments
    FOR EACH ROW EXECUTE FUNCTION prevent_locked_experiment_modification();

-- Function to generate log hash
CREATE OR REPLACE FUNCTION generate_log_hash()
RETURNS TRIGGER AS $$
BEGIN
    NEW.hash = encode(
        digest(
            COALESCE(NEW.experiment_id::text, '') ||
            COALESCE(NEW.plot_id::text, '') ||
            COALESCE(NEW.log_date::text, '') ||
            COALESCE(NEW.category::text, '') ||
            COALESCE(NEW.notes, '') ||
            COALESCE(NEW.measurements::text, '{}') ||
            COALESCE(NEW.recorded_by::text, ''),
            'sha256'
        ),
        'hex'
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER generate_log_hash_trigger BEFORE INSERT OR UPDATE ON research_daily_logs
    FOR EACH ROW EXECUTE FUNCTION generate_log_hash();

-- ─────────────────────────────────────────────────────────────────────────────
-- Views
-- ─────────────────────────────────────────────────────────────────────────────

-- View: Experiment summary with statistics
CREATE OR REPLACE VIEW experiment_summary AS
SELECT
    e.id,
    e.title,
    e.title_ar,
    e.status,
    e.start_date,
    e.end_date,
    e.principal_researcher_id,
    COUNT(DISTINCT rp.id) as plot_count,
    COUNT(DISTINCT t.id) as treatment_count,
    COUNT(DISTINCT rdl.id) as log_count,
    COUNT(DISTINCT ls.id) as sample_count,
    MAX(rdl.log_date) as last_log_date
FROM experiments e
LEFT JOIN research_plots rp ON e.id = rp.experiment_id
LEFT JOIN treatments t ON e.id = t.experiment_id
LEFT JOIN research_daily_logs rdl ON e.id = rdl.experiment_id
LEFT JOIN lab_samples ls ON e.id = ls.experiment_id
GROUP BY e.id;

-- View: Daily log with related info
CREATE OR REPLACE VIEW daily_log_details AS
SELECT
    rdl.*,
    e.title as experiment_title,
    e.status as experiment_status,
    rp.plot_code,
    rp.name as plot_name,
    t.treatment_code,
    t.name as treatment_name
FROM research_daily_logs rdl
JOIN experiments e ON rdl.experiment_id = e.id
LEFT JOIN research_plots rp ON rdl.plot_id = rp.id
LEFT JOIN treatments t ON rdl.treatment_id = t.id;

-- ─────────────────────────────────────────────────────────────────────────────
-- Initial Data / Seed Data
-- ─────────────────────────────────────────────────────────────────────────────

-- Insert default measurement templates
-- These can be customized per experiment
COMMENT ON TABLE experiments IS 'التجارب البحثية الزراعية - Agricultural Research Experiments';
COMMENT ON TABLE research_protocols IS 'بروتوكولات البحث - Research Protocols';
COMMENT ON TABLE research_plots IS 'قطع الأرض البحثية - Research Plots';
COMMENT ON TABLE treatments IS 'المعاملات الزراعية - Agricultural Treatments';
COMMENT ON TABLE research_daily_logs IS 'السجلات اليومية للبحث - Daily Research Logs';
COMMENT ON TABLE lab_samples IS 'عينات المختبر - Laboratory Samples';
COMMENT ON TABLE digital_signatures IS 'التوقيعات الرقمية للتحقق - Digital Verification Signatures';

-- Grant permissions (adjust based on your user setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sahool;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sahool;
