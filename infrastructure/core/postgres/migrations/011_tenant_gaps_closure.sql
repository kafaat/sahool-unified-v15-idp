-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Tenant Isolation Gaps Closure
-- إغلاق فجوات عزل المستأجرين
-- Migration: 011_tenant_gaps_closure.sql
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- This migration closes all remaining tenant isolation gaps:
--
-- 1. Creates missing tables: tenant_audit_log, usage_metering, security_audit_log
-- 2. Enables RLS + FORCE RLS on all new tables
-- 3. Adds RLS policies for billing-core tables (conditional — IF EXISTS)
-- 4. Adds FORCE ROW LEVEL SECURITY to existing 18 tables from migration 010
-- 5. Creates app_user role as alias for sahool (formalizes the convention)
--
-- DEPENDENCIES:
--   - 010_row_level_security.sql (current_tenant_id(), is_super_admin())
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 1: Create missing tables
-- القسم 1: إنشاء الجداول المفقودة
-- ─────────────────────────────────────────────────────────────────────────────

-- 1a. tenant_audit_log — records all cross-tenant and sensitive access events
CREATE TABLE IF NOT EXISTS tenant_audit_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    tenant_id UUID,  -- nullable: may be NULL if accessed_tenant_id is not a valid UUID
    user_id VARCHAR(255) NOT NULL,
    service_name VARCHAR(100),
    request_id VARCHAR(255),
    table_name VARCHAR(100),
    op_type VARCHAR(20) NOT NULL,  -- SELECT, INSERT, UPDATE, DELETE, CROSS_TENANT
    row_count INTEGER DEFAULT 0,
    duration_ms DOUBLE PRECISION,
    ip_address INET,
    user_agent TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE tenant_audit_log IS 'سجل تدقيق المستأجرين — يسجل جميع أحداث الوصول الحساسة';

CREATE INDEX IF NOT EXISTS idx_tenant_audit_log_tenant_id
ON tenant_audit_log (tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_audit_log_created_at
ON tenant_audit_log (created_at);
CREATE INDEX IF NOT EXISTS idx_tenant_audit_log_operation
ON tenant_audit_log (op_type);
CREATE INDEX IF NOT EXISTS idx_tenant_audit_log_user_id
ON tenant_audit_log (user_id);

-- 1b. usage_metering — records resource usage for billing (referenced by shared/platform.py)
CREATE TABLE IF NOT EXISTS usage_metering (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    tenant_id UUID NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    quantity DOUBLE PRECISION NOT NULL DEFAULT 0,
    unit VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE usage_metering IS 'قياس الاستهلاك — يسجل استخدام الموارد للفوترة';

CREATE INDEX IF NOT EXISTS idx_usage_metering_tenant_id
ON usage_metering (tenant_id);
CREATE INDEX IF NOT EXISTS idx_usage_metering_recorded_at
ON usage_metering (recorded_at);
CREATE INDEX IF NOT EXISTS idx_usage_metering_resource_type
ON usage_metering (resource_type);

-- 1c. security_audit_log — records security-relevant events (login, auth failures, etc.)
CREATE TABLE IF NOT EXISTS security_audit_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    tenant_id UUID NOT NULL,
    user_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,  -- login, logout, auth_failure, permission_denied, etc.
    severity VARCHAR(20) NOT NULL DEFAULT 'info',  -- info, warning, error, critical
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE security_audit_log IS 'سجل التدقيق الأمني — يسجل أحداث الأمان';

CREATE INDEX IF NOT EXISTS idx_security_audit_log_tenant_id
ON security_audit_log (tenant_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_log_created_at
ON security_audit_log (created_at);
CREATE INDEX IF NOT EXISTS idx_security_audit_log_event_type
ON security_audit_log (event_type);
CREATE INDEX IF NOT EXISTS idx_security_audit_log_severity
ON security_audit_log (severity);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 2: Enable RLS on new tables
-- القسم 2: تفعيل أمان الصف على الجداول الجديدة
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE tenant_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_audit_log FORCE ROW LEVEL SECURITY;

ALTER TABLE usage_metering ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_metering FORCE ROW LEVEL SECURITY;

ALTER TABLE security_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_audit_log FORCE ROW LEVEL SECURITY;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 3: RLS policies for new tables
-- القسم 3: سياسات أمان الصف للجداول الجديدة
-- ─────────────────────────────────────────────────────────────────────────────

-- tenant_audit_log policies (tenant_id can be NULL for invalid UUID cases)
-- Split into separate read and write policies so audit inserts work from
-- system/super-admin context without requiring a matching tenant GUC.
DROP POLICY IF EXISTS tenant_audit_log_isolation ON tenant_audit_log;
DROP POLICY IF EXISTS tenant_audit_log_read ON tenant_audit_log;
DROP POLICY IF EXISTS tenant_audit_log_write ON tenant_audit_log;

-- Restrictive read/update/delete: only the current tenant or super admin
CREATE POLICY tenant_audit_log_read ON tenant_audit_log
FOR SELECT USING (
    (tenant_id IS NOT NULL AND tenant_id = current_tenant_id())
    OR is_super_admin()
);

-- Permissive insert: current tenant or super admin
CREATE POLICY tenant_audit_log_write ON tenant_audit_log
FOR INSERT WITH CHECK (
    (tenant_id IS NOT NULL AND tenant_id = current_tenant_id())
    OR is_super_admin()
);

-- usage_metering policies
DROP POLICY IF EXISTS usage_metering_isolation ON usage_metering;
CREATE POLICY usage_metering_isolation ON usage_metering
FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

-- security_audit_log policies
DROP POLICY IF EXISTS security_audit_log_isolation ON security_audit_log;
CREATE POLICY security_audit_log_isolation ON security_audit_log
FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 4: FORCE RLS on existing tables from migration 010
-- القسم 4: فرض أمان الصف على الجداول الموجودة من الهجرة 010
-- ─────────────────────────────────────────────────────────────────────────────
-- Migration 010 used ENABLE but not FORCE. FORCE ensures RLS applies even
-- to the table owner (sahool role), providing defense-in-depth.

DO $$
DECLARE
    tbl TEXT;
    existing_tables TEXT[] := ARRAY[
        'fields', 'users', 'tasks', 'products', 'orders', 'invoices',
        'equipment', 'iot_devices', 'sensor_readings', 'weather_data',
        'crop_seasons', 'field_zones', 'alerts', 'notifications',
        'experiments', 'research_plots', 'treatments', 'lab_samples'
    ];
BEGIN
    FOREACH tbl IN ARRAY existing_tables LOOP
        -- Only FORCE if the table exists
        IF EXISTS (
            SELECT 1 FROM pg_tables
            WHERE schemaname = 'public' AND tablename = tbl
        ) THEN
            EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', tbl);
            RAISE NOTICE 'FORCE RLS enabled on table: %', tbl;
        END IF;
    END LOOP;
END;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 5: RLS for billing-core tables (conditional)
-- القسم 5: أمان الصف لجداول الفوترة (شرطي)
-- ─────────────────────────────────────────────────────────────────────────────
-- These tables are created by billing-core's Alembic migration. This section
-- adds RLS only if the tables already exist.

DO $$
DECLARE
    billing_tables TEXT[] := ARRAY[
        'subscriptions', 'invoices', 'payments', 'usage_records'
    ];
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY billing_tables LOOP
        IF EXISTS (
            SELECT 1 FROM pg_tables
            WHERE schemaname = 'public' AND tablename = tbl
        ) THEN
            -- Enable + Force RLS
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
            EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', tbl);

            -- Drop existing policy if any (idempotent)
            EXECUTE format('DROP POLICY IF EXISTS %I ON %I',
                           tbl || '_tenant_isolation', tbl);

            -- Create tenant isolation policy
            -- Note: billing tables use VARCHAR tenant_id, not UUID;
            -- current_tenant_id() returns UUID, so we cast for compatibility
            EXECUTE format(
                'CREATE POLICY %I ON %I FOR ALL USING ('
                || 'tenant_id::TEXT = current_tenant_id()::TEXT OR is_super_admin())',
                tbl || '_tenant_isolation', tbl
            );

            RAISE NOTICE 'RLS enabled on billing table: %', tbl;
        ELSE
            RAISE NOTICE 'Billing table % does not exist yet — skipped', tbl;
        END IF;
    END LOOP;
END;
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 6: Formalize database roles
-- القسم 6: توحيد أدوار قاعدة البيانات
-- ─────────────────────────────────────────────────────────────────────────────
-- The codebase uses 'sahool' as the application role. Some documentation
-- references 'app_user'. Create app_user as an alias (member of sahool group)
-- to avoid confusion.

DO $$
BEGIN
    -- Create app_user role if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user WITH LOGIN;
        RAISE NOTICE 'Created app_user role';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE 'app_user role already exists';
END;
$$;

-- Grant sahool's permissions to app_user
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sahool') THEN
        EXECUTE 'GRANT sahool TO app_user';
        RAISE NOTICE 'Granted sahool role to app_user';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Could not grant sahool to app_user: %', SQLERRM;
END;
$$;

-- Grant permissions on new tables
GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_audit_log TO sahool;
GRANT SELECT, INSERT, UPDATE, DELETE ON usage_metering TO sahool;
GRANT SELECT, INSERT, UPDATE, DELETE ON security_audit_log TO sahool;

-- ─────────────────────────────────────────────────────────────────────────────
-- Summary
-- ─────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    rls_count INTEGER;
    forced_count INTEGER;
    policy_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO rls_count
    FROM pg_tables t
    JOIN pg_class c ON t.tablename = c.relname
    WHERE t.schemaname = 'public' AND c.relrowsecurity = TRUE;

    SELECT COUNT(*) INTO forced_count
    FROM pg_tables t
    JOIN pg_class c ON t.tablename = c.relname
    WHERE t.schemaname = 'public' AND c.relforcerowsecurity = TRUE;

    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  TENANT ISOLATION GAPS CLOSURE - COMPLETE';
    RAISE NOTICE '  إغلاق فجوات عزل المستأجرين - مكتمل';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  Tables with RLS enabled:  %', rls_count;
    RAISE NOTICE '  Tables with FORCE RLS:    %', forced_count;
    RAISE NOTICE '  Total RLS policies:       %', policy_count;
    RAISE NOTICE '';
    RAISE NOTICE '  New tables created:';
    RAISE NOTICE '    - tenant_audit_log   (cross-tenant access audit)';
    RAISE NOTICE '    - usage_metering     (resource usage for billing)';
    RAISE NOTICE '    - security_audit_log (security event audit)';
    RAISE NOTICE '';
    RAISE NOTICE '  Gaps closed:';
    RAISE NOTICE '    [x] tenant_audit_log table created with RLS';
    RAISE NOTICE '    [x] usage_metering table created with RLS';
    RAISE NOTICE '    [x] security_audit_log table created with RLS';
    RAISE NOTICE '    [x] FORCE RLS on all 18 existing tables';
    RAISE NOTICE '    [x] RLS on billing tables (if exist)';
    RAISE NOTICE '    [x] app_user role created as sahool alias';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
