-- SPDX-License-Identifier: Proprietary
-- Copyright (c) 2026 KAFAAT - SAHOOL Platform
-- ============================================================
-- Digital Twin RLS Policies - سياسات أمان صف البيانات
-- Migration: 002_rls_policies.sql
-- ============================================================
-- Enable Row Level Security on all digital twin tables
-- to enforce tenant isolation at the database level.
-- ============================================================

-- 1. field_daily_state
ALTER TABLE field_daily_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_fds ON field_daily_state
    USING (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid);

-- 2. field_observation
ALTER TABLE field_observation ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_obs ON field_observation
    USING (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid);

-- 3. irrigation_recommendation
ALTER TABLE irrigation_recommendation ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_irec ON irrigation_recommendation
    USING (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid);

-- Super-admin bypass: allow service accounts to access all tenants
CREATE POLICY superadmin_bypass_fds ON field_daily_state
    USING (current_setting('app.is_super_admin', true) = 'true');

CREATE POLICY superadmin_bypass_obs ON field_observation
    USING (current_setting('app.is_super_admin', true) = 'true');

CREATE POLICY superadmin_bypass_irec ON irrigation_recommendation
    USING (current_setting('app.is_super_admin', true) = 'true');
