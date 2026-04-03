-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Multi-Tenant Row-Level Security (RLS)
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- Enables tenant isolation at the database level. Each query automatically
-- filters rows by the current tenant set via set_config('app.current_tenant', ...).
--
-- ── Relationship with migration 011 ────────────────────────────────────────
-- Migration 010/011 (infrastructure/core/postgres/migrations/) already
-- enables + FORCE-RLS on 18 core tables using current_tenant_id() and policy
-- names of the form <table>_tenant_isolation.
--
-- THIS script is supplementary:
--   • It defines get_current_tenant_id() as a stable alias that delegates to
--     current_tenant_id() (from migration 010).  New services should use this
--     alias so they are not tightly coupled to the migration naming.
--   • It applies tenant isolation to the 5 tables NOT covered by migration 011:
--       sensors, irrigation_schedules, ndvi_data,
--       marketplace_listings, chat_messages
--   • Tables already covered by migration 011 (fields, weather_data, …) are
--     intentionally excluded to avoid duplicate policies.
--
-- Prerequisites:
--   - Migrations 010 + 011 must have been applied first
--   - Tables must have a tenant_id TEXT column
--   - Application must call set_config('app.current_tenant', '<id>', false)
--   - Use TenantContext from packages/platform-bootstrap/src/tenant/
--
-- ═══════════════════════════════════════════════════════════════════════════════

-- Stable alias for current_tenant_id() (defined in migration 010).
-- Provides a consistent name so services do not import migration internals.
-- Falls back to reading the session variable directly in test/dev environments
-- where migration 010 may not have run.
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS TEXT AS $$
DECLARE
    tid TEXT;
BEGIN
    -- Prefer the canonical implementation from migration 010 when available.
    BEGIN
        tid := current_tenant_id();
        RETURN tid;
    EXCEPTION
        WHEN undefined_function THEN
            -- Standalone fallback (dev/test environments without migration 010).
            NULL;
    END;

    tid := current_setting('app.current_tenant', true);
    IF tid IS NULL OR tid = '' THEN
        RAISE EXCEPTION 'Tenant context not set. Use set_config(''app.current_tenant'', ''<tenant_id>'', false)';
    END IF;
    RETURN tid;
END;
$$ LANGUAGE plpgsql
   SET search_path = pg_catalog, public
   SECURITY INVOKER;

-- Apply tenant isolation policies to tables NOT already covered by migration 011.
-- Migration 011 already handles: fields, users, tasks, products, orders,
-- invoices, equipment, iot_devices, sensor_readings, weather_data,
-- crop_seasons, field_zones, alerts, notifications, experiments,
-- research_plots, treatments, lab_samples.
--
-- This script handles the remaining application-specific tables.
-- Uses DROP + CREATE instead of IF NOT EXISTS (not valid for CREATE POLICY).
-- WITH CHECK clause prevents cross-tenant INSERT/UPDATE.
-- FORCE ROW LEVEL SECURITY ensures table owners cannot bypass RLS.
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT unnest(ARRAY[
            'sensors', 'irrigation_schedules', 'ndvi_data',
            'marketplace_listings', 'chat_messages'
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

-- ── sahool_admin role ───────────────────────────────────────────────────────
-- BYPASSRLS lets administrators inspect/repair cross-tenant data during
-- support incidents.  To prevent silent privilege escalation:
--   • NOLOGIN: the role cannot authenticate directly; access is only via
--     SET ROLE sahool_admin within an already-authenticated session.
--   • Every SET ROLE transition is audit-logged by PostgreSQL's pg_audit
--     extension (log_level = LOG, log = 'all').
--   • Application code must NEVER use this role for normal operations.
--   • Incident usage must be documented in the security_audit_log table
--     (see migration 011_tenant_gaps_closure.sql).
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
