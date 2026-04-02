-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Multi-Tenant Row-Level Security (RLS)
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- Enables tenant isolation at the database level. Each query automatically
-- filters rows by the current tenant set via SET app.current_tenant.
--
-- Prerequisites:
--   - Tables must have a tenant_id TEXT column
--   - Application must call SET app.current_tenant before queries
--   - Use TenantContext from packages/platform-bootstrap/src/tenant/
--
-- ═══════════════════════════════════════════════════════════════════════════════

-- Helper function to retrieve current tenant from session variable
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS TEXT AS $$
DECLARE
    tid TEXT;
BEGIN
    tid := current_setting('app.current_tenant', true);
    IF tid IS NULL OR tid = '' THEN
        RAISE EXCEPTION 'Tenant context not set. Use SET app.current_tenant = ''tenant_id''';
    END IF;
    RETURN tid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create tenant isolation policies (before enabling RLS)
CREATE POLICY tenant_isolation_fields ON fields
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_sensors ON sensors
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_irrigation ON irrigation_schedules
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_ndvi ON ndvi_data
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_weather ON weather_data
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_marketplace ON marketplace_listings
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_chat ON chat_messages
    USING (tenant_id = get_current_tenant_id());

-- Enable RLS on all tenant-scoped tables (after policies are in place)
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensors ENABLE ROW LEVEL SECURITY;
ALTER TABLE irrigation_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE ndvi_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Bypass RLS for admin users (use carefully)
CREATE ROLE sahool_admin BYPASSRLS;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sahool_admin;

-- Grant standard permissions for application user
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sahool_app;
