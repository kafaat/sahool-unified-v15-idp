-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Multi-Tenant Row-Level Security (RLS)
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- Enables tenant isolation at the database level. Each query automatically
-- filters rows by the current tenant set via set_config('app.current_tenant', ...).
--
-- Prerequisites:
--   - Tables must have a tenant_id TEXT column
--   - Application must call set_config('app.current_tenant', '<id>', true) before queries
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
        RAISE EXCEPTION 'Tenant context not set. Use set_config(''app.current_tenant'', ''<tenant_id>'', true)';
    END IF;
    RETURN tid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create tenant isolation policies and enable RLS only on tables that exist.
-- This allows the script to be applied safely across different environments.
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT unnest(ARRAY[
            'fields', 'sensors', 'irrigation_schedules', 'ndvi_data',
            'weather_data', 'marketplace_listings', 'chat_messages'
        ])
    LOOP
        IF to_regclass(tbl) IS NOT NULL THEN
            EXECUTE format(
                'CREATE POLICY IF NOT EXISTS tenant_isolation_%I ON %I USING (tenant_id = get_current_tenant_id())',
                tbl, tbl
            );
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
        ELSE
            RAISE NOTICE 'Skipping RLS for missing table: %', tbl;
        END IF;
    END LOOP;
END;
$$;

-- Bypass RLS for admin users (use carefully)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sahool_admin') THEN
        CREATE ROLE sahool_admin BYPASSRLS;
    END IF;
END;
$$;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sahool_admin;

-- Grant standard permissions for application user
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sahool_app;
