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
BEGIN
    RETURN current_setting('app.current_tenant', true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create tenant isolation policies before enabling RLS
CREATE POLICY tenant_isolation_fields ON fields
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_sensors ON sensors
    USING (tenant_id = get_current_tenant_id());

CREATE POLICY tenant_isolation_irrigation ON irrigation_schedules
    USING (tenant_id = get_current_tenant_id());

-- Enable RLS on core tables (after policies are in place)
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensors ENABLE ROW LEVEL SECURITY;
ALTER TABLE irrigation_schedules ENABLE ROW LEVEL SECURITY;
