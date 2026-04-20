-- ============================================================
-- pgTAP truthfulness tests for the introspection probe.
--
-- The CRITICAL property: the probe MUST report the truth.
--   * When RLS is genuinely enforced, the leakage probe → false.
--   * When RLS is DISABLED (test scenario), the same probe → true.
--
-- If both scenarios produce the same answer, the probe is a yes-man
-- and our entire E2E confidence is fake.
--
-- Self-contained: creates a sandbox schema, runs the probe queries
-- against it, asserts both directions, and rolls back on exit.
--
-- Run:
--   PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d postgres \
--     -f apps/services/test-harness-sidecar/tests/pgtap/test_introspection_truthfulness.sql
-- ============================================================

\set ON_ERROR_STOP on
\pset pager off

BEGIN;

-- Self-contained sandbox so we don't poison the real schema
DROP SCHEMA IF EXISTS th_introspect_test CASCADE;
CREATE SCHEMA th_introspect_test;
SET search_path TO th_introspect_test, public;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pgtap;

-- Mirror production fields table shape (the relevant subset)
CREATE TABLE fields (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   text        NOT NULL,
    name        text        NOT NULL
);

INSERT INTO fields (id, tenant_id, name) VALUES
    ('11111111-1111-1111-1111-111111111111', 'tenant_e2e_a', 'a-field'),
    ('22222222-2222-2222-2222-222222222222', 'tenant_e2e_b', 'b-field');

ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE fields FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON fields
    USING      (tenant_id = nullif(current_setting('app.current_tenant', true), ''))
    WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant', true), ''));

-- Production services connect as non-superuser; superusers bypass RLS by
-- default which would invalidate the test. Create a sandbox role that
-- mirrors production's privileges.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'th_app') THEN
        CREATE ROLE th_app NOLOGIN;
    END IF;
END$$;
GRANT USAGE  ON SCHEMA th_introspect_test TO th_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA th_introspect_test TO th_app;

SELECT plan(4);

SET LOCAL ROLE th_app;

-- ── Test 1: WHEN RLS active, leakage query for tenant A returns 0 ──
SET LOCAL app.current_tenant = 'tenant_e2e_a';
SELECT is(
    (SELECT COUNT(*)::int FROM fields WHERE tenant_id <> 'tenant_e2e_a'),
    0,
    'leakage probe correctly reports 0 when RLS is enforced for tenant A'
);

-- ── Test 2: tenant A's legitimate row count is 1 ──
SET LOCAL app.current_tenant = 'tenant_e2e_a';
SELECT is(
    (SELECT COUNT(*)::int FROM fields WHERE tenant_id = 'tenant_e2e_a'),
    1,
    'tenant A sees exactly 1 row when RLS is enforced'
);

-- ── Test 3 (CRITICAL): WHEN RLS is DISABLED, leakage probe reports >0 ──
RESET ROLE;
ALTER TABLE fields DISABLE ROW LEVEL SECURITY;
SET LOCAL ROLE th_app;
SET LOCAL app.current_tenant = 'tenant_e2e_a';
SELECT cmp_ok(
    (SELECT COUNT(*)::int FROM fields WHERE tenant_id <> 'tenant_e2e_a'),
    '>', 0,
    'leakage probe correctly reports >0 when RLS is DISABLED (probe does not lie)'
);

-- ── Test 4: pg_policies query the introspect router uses ──
RESET ROLE;
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
SELECT ok(
    EXISTS(SELECT 1 FROM pg_policies WHERE tablename = 'fields' AND cmd = 'ALL'),
    'pg_policies query returns true when policy is defined'
);

SELECT * FROM finish();

ROLLBACK;
