-- ============================================================================
-- s16_011_rls_policies.sql
-- Calibration Engine RLS Policies - سياسات أمان صف البيانات للمعايرة
--
-- Enable Row Level Security on all calibration tables
-- to enforce tenant isolation at the database level.
-- ============================================================================

-- 1. calibration_run
ALTER TABLE calibration_run ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_calrun ON calibration_run
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- 2. parameter_set
ALTER TABLE parameter_set ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_paramset ON parameter_set
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- 3. parameter_change_log
ALTER TABLE parameter_change_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_paramlog ON parameter_change_log
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- Super-admin bypass
CREATE POLICY superadmin_bypass_calrun ON calibration_run
    USING (current_setting('app.is_superadmin', true) = 'true');

CREATE POLICY superadmin_bypass_paramset ON parameter_set
    USING (current_setting('app.is_superadmin', true) = 'true');

CREATE POLICY superadmin_bypass_paramlog ON parameter_change_log
    USING (current_setting('app.is_superadmin', true) = 'true');
