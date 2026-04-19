-- ============================================================================
-- pgTAP fixtures: SAHOOL tenant-isolation schema.
-- ============================================================================
-- A minimal, self-contained schema that mirrors the real production RLS
-- pattern (see shared/digital_twin/migrations/002_rls_policies.sql):
--   * every tenanted row carries a ``tenant_id uuid``
--   * the session GUC ``app.current_tenant`` scopes visibility
--   * the session GUC ``app.is_super_admin`` grants bypass
--
-- Running this file before the pgTAP scripts provides deterministic,
-- repeatable state without requiring the full platform migration history.
-- ============================================================================

BEGIN;

DROP SCHEMA IF EXISTS sahool_rls_test CASCADE;
CREATE SCHEMA sahool_rls_test;
SET search_path TO sahool_rls_test, public;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE tenants (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        text        NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE fields (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   uuid        NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name        text        NOT NULL,
    area_ha     numeric(10,2) NOT NULL CHECK (area_ha > 0),
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX fields_tenant_idx ON fields(tenant_id);

-- Seed two tenants with disjoint field sets.
INSERT INTO tenants (id, name) VALUES
    ('00000000-0000-0000-0000-000000000001', 'tenant-a'),
    ('00000000-0000-0000-0000-000000000002', 'tenant-b');

INSERT INTO fields (tenant_id, name, area_ha) VALUES
    ('00000000-0000-0000-0000-000000000001', 'a-north', 12.5),
    ('00000000-0000-0000-0000-000000000001', 'a-south',  7.0),
    ('00000000-0000-0000-0000-000000000002', 'b-east',   9.3);

-- Row-level security matches production: USING + WITH CHECK on current tenant,
-- super-admin bypass via separate policy.
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE fields FORCE ROW LEVEL SECURITY;

CREATE POLICY fields_tenant_isolation ON fields
    USING      (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid);

CREATE POLICY fields_superadmin_bypass ON fields
    USING      (current_setting('app.is_super_admin', true) = 'true')
    WITH CHECK (current_setting('app.is_super_admin', true) = 'true');

-- An unprivileged role that must play by the RLS rules.
-- Use a stable name so re-running the script is idempotent even without a DROP.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sahool_app') THEN
        CREATE ROLE sahool_app LOGIN;
    END IF;
END$$;

GRANT USAGE  ON SCHEMA sahool_rls_test TO sahool_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sahool_rls_test TO sahool_app;

COMMIT;
