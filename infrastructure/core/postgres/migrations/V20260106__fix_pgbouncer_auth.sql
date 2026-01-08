-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Fix PgBouncer Authentication
-- Date: 2026-01-06
-- Issue: PgBouncer auth_query fails with "password authentication failed for user sahool"
--
-- Root Cause:
--   PgBouncer uses auth_user=sahool to run auth_query against pg_shadow.
--   The sahool user needs pg_monitor role to read pg_shadow for SCRAM-SHA-256 auth.
--
-- Fix:
--   Grant pg_monitor role to the main database user (sahool)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Grant pg_monitor to sahool user for PgBouncer auth_query support
DO $$
BEGIN
    -- Grant to sahool user (default POSTGRES_USER)
    IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'sahool') THEN
        GRANT pg_monitor TO sahool;
        RAISE NOTICE 'Granted pg_monitor to sahool user for PgBouncer auth_query support';
    END IF;

    -- Also grant to current user in case it's different
    IF current_user != 'postgres' AND current_user != 'sahool' THEN
        EXECUTE format('GRANT pg_monitor TO %I', current_user);
        RAISE NOTICE 'Granted pg_monitor to % for PgBouncer auth_query support', current_user;
    END IF;
END
$$;

-- Verify the grant was successful
DO $$
DECLARE
    has_pg_monitor BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM pg_auth_members
        WHERE roleid = (SELECT oid FROM pg_roles WHERE rolname = 'pg_monitor')
        AND member = (SELECT oid FROM pg_roles WHERE rolname = 'sahool')
    ) INTO has_pg_monitor;

    IF has_pg_monitor THEN
        RAISE NOTICE '✓ Migration successful: sahool user now has pg_monitor role';
    ELSE
        RAISE WARNING 'Migration may have failed: sahool user does not have pg_monitor role';
    END IF;
END
$$;
