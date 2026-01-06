-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Provider Configuration Database Schema
-- نموذج قاعدة بيانات تكوين المزودين
-- ═══════════════════════════════════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- Provider Configurations Table
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS provider_configs (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Tenant Information
    tenant_id VARCHAR(255) NOT NULL,

    -- Provider Information
    provider_type VARCHAR(50) NOT NULL,  -- map, weather, satellite, payment, sms, notification
    provider_name VARCHAR(100) NOT NULL, -- openstreetmap, google_maps, stripe, etc.

    -- Configuration
    api_key TEXT,                        -- Encrypted in production
    api_secret TEXT,                     -- Encrypted in production
    priority VARCHAR(20) NOT NULL DEFAULT 'primary',  -- primary, secondary, tertiary
    enabled BOOLEAN NOT NULL DEFAULT true,

    -- Additional Settings
    config_data JSONB,                   -- Additional provider-specific settings

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,

    -- Constraints
    CONSTRAINT unique_tenant_provider UNIQUE (tenant_id, provider_type, provider_name)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_provider_configs_tenant ON provider_configs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_provider_configs_type ON provider_configs(provider_type);
CREATE INDEX IF NOT EXISTS idx_provider_configs_tenant_type ON provider_configs(tenant_id, provider_type);
CREATE INDEX IF NOT EXISTS idx_provider_configs_tenant_name ON provider_configs(tenant_id, provider_name);
CREATE INDEX IF NOT EXISTS idx_provider_configs_tenant_type_enabled ON provider_configs(tenant_id, provider_type, enabled);
CREATE INDEX IF NOT EXISTS idx_provider_configs_tenant_type_priority ON provider_configs(tenant_id, provider_type, priority);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_provider_configs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_provider_configs_updated_at
    BEFORE UPDATE ON provider_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_provider_configs_updated_at();

-- ─────────────────────────────────────────────────────────────────────────────
-- Configuration Version History Table
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS config_versions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Reference to ProviderConfig
    config_id UUID NOT NULL,

    -- Tenant Information (denormalized)
    tenant_id VARCHAR(255) NOT NULL,

    -- Snapshot of configuration
    provider_type VARCHAR(50) NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    api_key TEXT,
    api_secret TEXT,
    priority VARCHAR(20) NOT NULL,
    enabled BOOLEAN NOT NULL,
    config_data JSONB,

    -- Version Information
    version INTEGER NOT NULL,
    change_type VARCHAR(20) NOT NULL,  -- created, updated, deleted, enabled, disabled

    -- Change Metadata
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    changed_by VARCHAR(255),
    change_reason TEXT
);

-- Indexes for version history
CREATE INDEX IF NOT EXISTS idx_config_versions_config ON config_versions(config_id);
CREATE INDEX IF NOT EXISTS idx_config_versions_tenant ON config_versions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_config_versions_config_version ON config_versions(config_id, version);
CREATE INDEX IF NOT EXISTS idx_config_versions_tenant_changed ON config_versions(tenant_id, changed_at);
CREATE INDEX IF NOT EXISTS idx_config_versions_tenant_provider ON config_versions(tenant_id, provider_type, changed_at);

-- Function to create version history on insert/update/delete
CREATE OR REPLACE FUNCTION create_config_version()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO config_versions (
            config_id, tenant_id, provider_type, provider_name,
            api_key, api_secret, priority, enabled, config_data,
            version, change_type, changed_by
        ) VALUES (
            OLD.id, OLD.tenant_id, OLD.provider_type, OLD.provider_name,
            OLD.api_key, OLD.api_secret, OLD.priority, OLD.enabled, OLD.config_data,
            OLD.version, 'deleted', OLD.updated_by
        );
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO config_versions (
            config_id, tenant_id, provider_type, provider_name,
            api_key, api_secret, priority, enabled, config_data,
            version, change_type, changed_by
        ) VALUES (
            NEW.id, NEW.tenant_id, NEW.provider_type, NEW.provider_name,
            NEW.api_key, NEW.api_secret, NEW.priority, NEW.enabled, NEW.config_data,
            NEW.version,
            CASE
                WHEN OLD.enabled != NEW.enabled AND NEW.enabled = true THEN 'enabled'
                WHEN OLD.enabled != NEW.enabled AND NEW.enabled = false THEN 'disabled'
                ELSE 'updated'
            END,
            NEW.updated_by
        );
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO config_versions (
            config_id, tenant_id, provider_type, provider_name,
            api_key, api_secret, priority, enabled, config_data,
            version, change_type, changed_by
        ) VALUES (
            NEW.id, NEW.tenant_id, NEW.provider_type, NEW.provider_name,
            NEW.api_key, NEW.api_secret, NEW.priority, NEW.enabled, NEW.config_data,
            NEW.version, 'created', NEW.created_by
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Triggers for version history
CREATE TRIGGER trigger_config_version_insert
    AFTER INSERT ON provider_configs
    FOR EACH ROW
    EXECUTE FUNCTION create_config_version();

CREATE TRIGGER trigger_config_version_update
    AFTER UPDATE ON provider_configs
    FOR EACH ROW
    EXECUTE FUNCTION create_config_version();

CREATE TRIGGER trigger_config_version_delete
    AFTER DELETE ON provider_configs
    FOR EACH ROW
    EXECUTE FUNCTION create_config_version();

-- ─────────────────────────────────────────────────────────────────────────────
-- Comments for documentation
-- ─────────────────────────────────────────────────────────────────────────────

COMMENT ON TABLE provider_configs IS 'Provider configurations for each tenant (maps, weather, satellite, payment, etc.)';
COMMENT ON TABLE config_versions IS 'Version history of provider configurations for audit and rollback';

COMMENT ON COLUMN provider_configs.tenant_id IS 'Tenant identifier (organization/customer)';
COMMENT ON COLUMN provider_configs.provider_type IS 'Type of provider: map, weather, satellite, payment, sms, notification';
COMMENT ON COLUMN provider_configs.provider_name IS 'Specific provider name: openstreetmap, google_maps, stripe, etc.';
COMMENT ON COLUMN provider_configs.priority IS 'Provider priority for failover: primary, secondary, tertiary';
COMMENT ON COLUMN provider_configs.enabled IS 'Whether this provider is currently enabled';
COMMENT ON COLUMN provider_configs.config_data IS 'Additional provider-specific configuration (JSON)';
COMMENT ON COLUMN provider_configs.version IS 'Configuration version number (auto-incremented on update)';

-- ─────────────────────────────────────────────────────────────────────────────
-- Sample Data (Optional - for testing)
-- ─────────────────────────────────────────────────────────────────────────────

-- Insert default configuration for demo tenant
-- Uncomment for testing:
-- INSERT INTO provider_configs (tenant_id, provider_type, provider_name, priority, enabled, created_by)
-- VALUES
--     ('demo-tenant', 'map', 'openstreetmap', 'primary', true, 'system'),
--     ('demo-tenant', 'map', 'esri_satellite', 'secondary', true, 'system'),
--     ('demo-tenant', 'weather', 'open_meteo', 'primary', true, 'system'),
--     ('demo-tenant', 'satellite', 'sentinel_hub', 'primary', false, 'system')
-- ON CONFLICT (tenant_id, provider_type, provider_name) DO NOTHING;
