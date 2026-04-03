-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Multi-Tenant Row-Level Security (RLS)
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- Enables tenant isolation at the database level. Each query automatically
-- filters rows by the current tenant set via set_config('app.current_tenant', ...).
--
-- Prerequisites:
--   - Tables must have a tenant_id TEXT column
--   - Application must call set_config('app.current_tenant', '<id>', false) before queries
--   - Use TenantContext from packages/platform-bootstrap/src/tenant/
--
-- ═══════════════════════════════════════════════════════════════════════════════

-- Helper function to retrieve current tenant from session variable.
-- Uses SECURITY INVOKER so it runs with the caller's privileges, not the
-- function creator's.  search_path is pinned to prevent object-hijacking.
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS TEXT AS $$
DECLARE
    tid TEXT;
BEGIN
    tid := current_setting('app.current_tenant', true);
    IF tid IS NULL OR tid = '' THEN
        RAISE EXCEPTION 'Tenant context not set. Use set_config(''app.current_tenant'', ''<tenant_id>'', false)';
    END IF;
    RETURN tid;
END;
$$ LANGUAGE plpgsql
   SET search_path = pg_catalog, public
   SECURITY INVOKER;

-- Create tenant isolation policies and enable RLS only on tables that exist.
-- This allows the script to be applied safely across different environments.
-- Uses DROP + CREATE instead of IF NOT EXISTS (not valid for CREATE POLICY).
-- WITH CHECK clause prevents cross-tenant INSERT/UPDATE.
-- FORCE ROW LEVEL SECURITY ensures table owners cannot bypass RLS.
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
            EXECUTE format('DROP POLICY IF EXISTS tenant_isolation_%I ON %I', tbl, tbl);
            EXECUTE format(
                'CREATE POLICY tenant_isolation_%I ON %I '
                'USING (tenant_id = get_current_tenant_id()) '
                'WITH CHECK (tenant_id = get_current_tenant_id())',
                tbl, tbl
            );
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
            EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', tbl);
        ELSE
            RAISE NOTICE 'Skipping RLS for missing table: %', tbl;
        END IF;
    END LOOP;
END;
$$;

-- Bypass RLS for admin users (use carefully)
-- NOLOGIN prevents direct authentication; access is via SET ROLE only (audit-logged).
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sahool_admin') THEN
        CREATE ROLE sahool_admin NOLOGIN BYPASSRLS;
    END IF;
END;
$$;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sahool_admin;

-- Grant standard permissions for application user
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sahool_app;
