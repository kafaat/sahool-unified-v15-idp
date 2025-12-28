-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Row-Level Security (RLS) Implementation
-- أمان مستوى الصف - عزل المستأجرين
-- Migration: 010_row_level_security.sql
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Enable RLS on all multi-tenant tables
-- تفعيل أمان الصف على جميع الجداول متعددة المستأجرين
-- ─────────────────────────────────────────────────────────────────────────────

-- Core tables
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE iot_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE crop_seasons ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_zones ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Research tables
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE treatments ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab_samples ENABLE ROW LEVEL SECURITY;

-- ─────────────────────────────────────────────────────────────────────────────
-- Create helper function to get current tenant from session
-- إنشاء دالة مساعدة للحصول على المستأجر الحالي من الجلسة
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION current_tenant_id()
RETURNS UUID AS $$
BEGIN
    -- Get tenant_id from current session variable
    -- Set via: SET app.current_tenant = 'tenant-uuid';
    RETURN NULLIF(current_setting('app.current_tenant', true), '')::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION is_super_admin()
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if current user has super_admin role
    -- Set via: SET app.is_super_admin = 'true';
    RETURN COALESCE(current_setting('app.is_super_admin', true), 'false')::BOOLEAN;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for FIELDS table
-- سياسات أمان الصف لجدول الحقول
-- ─────────────────────────────────────────────────────────────────────────────

-- Drop existing policies if any
DROP POLICY IF EXISTS fields_tenant_isolation ON fields;
DROP POLICY IF EXISTS fields_insert_policy ON fields;
DROP POLICY IF EXISTS fields_update_policy ON fields;
DROP POLICY IF EXISTS fields_delete_policy ON fields;

-- SELECT: Users can only see fields from their tenant
CREATE POLICY fields_tenant_isolation ON fields
    FOR SELECT
    USING (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    );

-- INSERT: Users can only create fields in their tenant
CREATE POLICY fields_insert_policy ON fields
    FOR INSERT
    WITH CHECK (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    );

-- UPDATE: Users can only update fields in their tenant
CREATE POLICY fields_update_policy ON fields
    FOR UPDATE
    USING (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    )
    WITH CHECK (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    );

-- DELETE: Users can only delete fields in their tenant
CREATE POLICY fields_delete_policy ON fields
    FOR DELETE
    USING (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for USERS table
-- سياسات أمان الصف لجدول المستخدمين
-- ─────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS users_tenant_isolation ON users;
DROP POLICY IF EXISTS users_insert_policy ON users;
DROP POLICY IF EXISTS users_update_policy ON users;

CREATE POLICY users_tenant_isolation ON users
    FOR SELECT
    USING (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    );

CREATE POLICY users_insert_policy ON users
    FOR INSERT
    WITH CHECK (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    );

CREATE POLICY users_update_policy ON users
    FOR UPDATE
    USING (
        tenant_id = current_tenant_id()
        OR is_super_admin()
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for TASKS table
-- ─────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS tasks_tenant_isolation ON tasks;
DROP POLICY IF EXISTS tasks_insert_policy ON tasks;
DROP POLICY IF EXISTS tasks_update_policy ON tasks;
DROP POLICY IF EXISTS tasks_delete_policy ON tasks;

CREATE POLICY tasks_tenant_isolation ON tasks
    FOR SELECT
    USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY tasks_insert_policy ON tasks
    FOR INSERT
    WITH CHECK (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY tasks_update_policy ON tasks
    FOR UPDATE
    USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY tasks_delete_policy ON tasks
    FOR DELETE
    USING (tenant_id = current_tenant_id() OR is_super_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for ORDERS table
-- ─────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS orders_tenant_isolation ON orders;
DROP POLICY IF EXISTS orders_insert_policy ON orders;

CREATE POLICY orders_tenant_isolation ON orders
    FOR SELECT
    USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY orders_insert_policy ON orders
    FOR INSERT
    WITH CHECK (tenant_id = current_tenant_id() OR is_super_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for IoT tables
-- ─────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS iot_devices_tenant_isolation ON iot_devices;
DROP POLICY IF EXISTS sensor_readings_tenant_isolation ON sensor_readings;

CREATE POLICY iot_devices_tenant_isolation ON iot_devices
    FOR ALL
    USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY sensor_readings_tenant_isolation ON sensor_readings
    FOR ALL
    USING (tenant_id = current_tenant_id() OR is_super_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for Research tables
-- ─────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS experiments_tenant_isolation ON experiments;
DROP POLICY IF EXISTS research_plots_tenant_isolation ON research_plots;
DROP POLICY IF EXISTS treatments_tenant_isolation ON treatments;
DROP POLICY IF EXISTS lab_samples_tenant_isolation ON lab_samples;

CREATE POLICY experiments_tenant_isolation ON experiments
    FOR ALL
    USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY research_plots_tenant_isolation ON research_plots
    FOR ALL
    USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY treatments_tenant_isolation ON treatments
    FOR ALL
    USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY lab_samples_tenant_isolation ON lab_samples
    FOR ALL
    USING (tenant_id = current_tenant_id() OR is_super_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for remaining tables
-- ─────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS products_tenant_isolation ON products;
DROP POLICY IF EXISTS invoices_tenant_isolation ON invoices;
DROP POLICY IF EXISTS equipment_tenant_isolation ON equipment;
DROP POLICY IF EXISTS weather_data_tenant_isolation ON weather_data;
DROP POLICY IF EXISTS crop_seasons_tenant_isolation ON crop_seasons;
DROP POLICY IF EXISTS field_zones_tenant_isolation ON field_zones;
DROP POLICY IF EXISTS alerts_tenant_isolation ON alerts;
DROP POLICY IF EXISTS notifications_tenant_isolation ON notifications;

CREATE POLICY products_tenant_isolation ON products
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY invoices_tenant_isolation ON invoices
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY equipment_tenant_isolation ON equipment
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY weather_data_tenant_isolation ON weather_data
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY crop_seasons_tenant_isolation ON crop_seasons
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY field_zones_tenant_isolation ON field_zones
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY alerts_tenant_isolation ON alerts
    FOR ALL USING (tenant_id = current_tenant_id() OR is_super_admin());

CREATE POLICY notifications_tenant_isolation ON notifications
    FOR ALL USING (user_id IN (
        SELECT id FROM users WHERE tenant_id = current_tenant_id()
    ) OR is_super_admin());

-- ─────────────────────────────────────────────────────────────────────────────
-- Grant necessary permissions to application role
-- ─────────────────────────────────────────────────────────────────────────────

-- The sahool role should use RLS but still have CRUD permissions
-- RLS policies will filter what they can actually access

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sahool;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sahool;

-- ─────────────────────────────────────────────────────────────────────────────
-- Summary
-- ─────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    rls_enabled_count INTEGER;
    policy_count INTEGER;
BEGIN
    -- Count tables with RLS enabled
    SELECT COUNT(*) INTO rls_enabled_count
    FROM pg_tables t
    JOIN pg_class c ON t.tablename = c.relname
    WHERE t.schemaname = 'public' AND c.relrowsecurity = true;

    -- Count RLS policies
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  ROW-LEVEL SECURITY (RLS) ENABLED';
    RAISE NOTICE '  أمان مستوى الصف مُفعّل';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '  Tables with RLS: %', rls_enabled_count;
    RAISE NOTICE '  Total Policies: %', policy_count;
    RAISE NOTICE '';
    RAISE NOTICE '  Usage in application:';
    RAISE NOTICE '    SET app.current_tenant = ''tenant-uuid'';';
    RAISE NOTICE '    SET app.is_super_admin = ''true'';  -- for admin access';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
END;
$$;
