-- ============================================================================
-- pgTAP: tenant isolation via RLS on ``fields``.
-- ============================================================================
-- Verifies the production pattern:
--   1. Without a session tenant, an app role sees zero rows.
--   2. Tenant A sees only A's fields; tenant B only B's.
--   3. Cross-tenant INSERT is rejected by WITH CHECK.
--   4. Super-admin bypass surfaces every row.
--   5. A downgrade from super-admin back to a normal tenant is enforced.
-- ============================================================================

\set ON_ERROR_STOP on
\pset pager off

BEGIN;
SET search_path TO sahool_rls_test, public;

CREATE EXTENSION IF NOT EXISTS pgtap;

-- 14 assertions total; keep this in sync when adding cases.
SELECT plan(14);

-- ── 1. Bootstrap sanity checks ────────────────────────────────────────────
SELECT has_table('sahool_rls_test', 'fields', 'fields table exists');
SELECT ok(
    (SELECT relrowsecurity FROM pg_class WHERE oid = 'sahool_rls_test.fields'::regclass),
    'fields has ROW LEVEL SECURITY enabled'
);
SELECT ok(
    (SELECT relforcerowsecurity FROM pg_class WHERE oid = 'sahool_rls_test.fields'::regclass),
    'fields has FORCE ROW LEVEL SECURITY (owner is not exempt)'
);
SELECT is(
    (SELECT count(*)::int FROM pg_policies
      WHERE schemaname = 'sahool_rls_test' AND tablename = 'fields'),
    2,
    'fields has exactly two policies (tenant + super-admin)'
);

-- ── 2. Act as the unprivileged application role. ─────────────────────────
SET LOCAL ROLE sahool_app;

-- No tenant set ⇒ RLS filters everything out.
RESET app.current_tenant;
RESET app.is_super_admin;
SELECT is(
    (SELECT count(*)::int FROM fields),
    0,
    'no rows visible without app.current_tenant'
);

-- ── 3. Tenant A visibility ───────────────────────────────────────────────
SET LOCAL app.current_tenant = '00000000-0000-0000-0000-000000000001';
SELECT is(
    (SELECT count(*)::int FROM fields),
    2,
    'tenant A sees exactly 2 rows'
);
SELECT is(
    (SELECT count(*)::int FROM fields WHERE tenant_id <> '00000000-0000-0000-0000-000000000001'::uuid),
    0,
    'tenant A sees no other tenant''s rows'
);

-- ── 4. Tenant B visibility ───────────────────────────────────────────────
SET LOCAL app.current_tenant = '00000000-0000-0000-0000-000000000002';
SELECT is(
    (SELECT count(*)::int FROM fields),
    1,
    'tenant B sees exactly 1 row'
);
SELECT is(
    (SELECT (SELECT name FROM fields LIMIT 1)),
    'b-east',
    'tenant B sees the expected row name'
);

-- ── 5. Cross-tenant INSERT is rejected by WITH CHECK. ────────────────────
SET LOCAL app.current_tenant = '00000000-0000-0000-0000-000000000001';
SELECT throws_ok(
    $$INSERT INTO sahool_rls_test.fields (tenant_id, name, area_ha)
          VALUES ('00000000-0000-0000-0000-000000000002', 'forged', 1.0)$$,
    '42501',  -- insufficient_privilege (RLS violation)
    NULL,
    'cross-tenant INSERT rejected by RLS WITH CHECK'
);

-- ── 6. Same-tenant INSERT succeeds. ──────────────────────────────────────
SELECT lives_ok(
    $$INSERT INTO sahool_rls_test.fields (tenant_id, name, area_ha)
          VALUES ('00000000-0000-0000-0000-000000000001', 'a-extra', 2.0)$$,
    'same-tenant INSERT succeeds'
);
SELECT is(
    (SELECT count(*)::int FROM fields),
    3,
    'tenant A now sees 3 rows after insert'
);

-- ── 7. Super-admin bypass sees everything. ───────────────────────────────
RESET app.current_tenant;
SET LOCAL app.is_super_admin = 'true';
SELECT is(
    (SELECT count(*)::int FROM fields),
    4,
    'super-admin sees all 4 rows (2 original A + 1 B + 1 inserted)'
);

-- ── 8. Dropping super-admin re-engages tenant scoping. ────────────────────
RESET app.is_super_admin;
SET LOCAL app.current_tenant = '00000000-0000-0000-0000-000000000002';
SELECT is(
    (SELECT count(*)::int FROM fields),
    1,
    'tenant B still only sees 1 row after dropping super-admin'
);

-- ── 9. Finish ────────────────────────────────────────────────────────────
SELECT finish();

ROLLBACK;
