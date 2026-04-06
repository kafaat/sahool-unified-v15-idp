-- ═══════════════════════════════════════════════════════════════════════════════
-- Create PgBouncer user for auth_query
-- This user is used by PgBouncer to query PostgreSQL for password verification
-- Supports SCRAM-SHA-256 authentication (PostgreSQL 16 default)
--
-- AUTHENTICATION METHOD: SCRAM-SHA-256
-- - PostgreSQL password_encryption = scram-sha-256 (postgresql.conf line 133)
-- - pg_hba.conf uses scram-sha-256 for all authentication methods
-- - PgBouncer auth_type = scram-sha-256 (upgraded from md5)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Create pgbouncer user if it doesn't exist
-- Note: This user is NOT used for auth_query in the current configuration.
-- The auth_user (POSTGRES_USER, defaults to 'sahool') is used instead.
-- This pgbouncer user is kept for backwards compatibility and future use.
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
        -- Create user with a temporary password
        -- Note: This user is not actively used in the current PgBouncer configuration
        -- Password will be set by 03-set-pgbouncer-password.sh from env var
        CREATE USER pgbouncer WITH PASSWORD 'init_' || md5(random()::text || clock_timestamp()::text);
        -- Grant necessary permissions (for potential future use)
        GRANT pg_monitor TO pgbouncer;
        -- pg_read_all_auth needed for reading pg_shadow in PostgreSQL 16+
        GRANT pg_read_all_auth TO pgbouncer;
        RAISE NOTICE 'Created pgbouncer user (not actively used - auth_user is sahool)';
    ELSE
        -- If user exists, ensure it has the correct permissions
        GRANT pg_monitor TO pgbouncer;
        -- pg_read_all_auth needed for reading pg_shadow in PostgreSQL 16+
        GRANT pg_read_all_auth TO pgbouncer;
        RAISE NOTICE 'Pgbouncer user already exists (not actively used - auth_user is sahool)';
    END IF;
END
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Grant pg_monitor to main database user for auth_query support
-- The main DB user (POSTGRES_USER, defaults to 'sahool') is used as auth_user
-- by PgBouncer to run auth_query against pg_shadow
-- ═══════════════════════════════════════════════════════════════════════════════
DO $$
DECLARE
    main_user TEXT;
BEGIN
    -- Get the main database user (the user running this script)
    main_user := current_user;

    -- Grant pg_monitor role for monitoring + pg_read_all_auth for auth_query access to pg_shadow
    -- This allows PgBouncer to authenticate users via auth_query
    IF main_user IS NOT NULL AND main_user != 'postgres' THEN
        EXECUTE format('GRANT pg_monitor TO %I', main_user);
        RAISE NOTICE 'Granted pg_monitor to main database user: %', main_user;
    END IF;

    -- Also grant to 'sahool' user explicitly (default POSTGRES_USER)
    -- This ensures compatibility even when script runs as a different user
    IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'sahool') THEN
        GRANT pg_monitor TO sahool;
        RAISE NOTICE 'Granted pg_monitor to sahool user';
    END IF;
END
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Create the pgbouncer schema (needed for function creation)
-- Note: Schema is created first, then authorization is granted after user exists
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE SCHEMA IF NOT EXISTS pgbouncer;

-- Grant schema ownership to pgbouncer user (user was created above)
ALTER SCHEMA pgbouncer OWNER TO pgbouncer;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Create a SECURITY DEFINER function for auth_query
-- This is the recommended approach for PostgreSQL 14+ with SCRAM authentication
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION pgbouncer.get_auth(p_usename TEXT)
RETURNS TABLE(usename NAME, passwd TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.usename::NAME,
        u.passwd::TEXT
    FROM pg_catalog.pg_shadow u
    WHERE u.usename = p_usename;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Set the search path for security
ALTER FUNCTION pgbouncer.get_auth(TEXT) SET search_path = pg_catalog;

-- Grant execute permission to pgbouncer user
GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(TEXT) TO pgbouncer;

-- Grant execute permission to sahool user (used as auth_user in PgBouncer config)
-- Also grant USAGE on schema so sahool can access the function
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'sahool') THEN
        -- CRITICAL: Grant USAGE on schema first - required to call functions in the schema
        GRANT USAGE ON SCHEMA pgbouncer TO sahool;
        RAISE NOTICE 'Granted USAGE on pgbouncer schema to sahool user';

        -- Grant execute permission on the auth function
        GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(TEXT) TO sahool;
        RAISE NOTICE 'Granted EXECUTE on pgbouncer.get_auth() to sahool user';
    END IF;
END
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Note for pgbouncer.ini auth_query:
-- Use: auth_query = SELECT usename, passwd FROM pgbouncer.get_auth($1)
-- This function returns SCRAM-SHA-256 password hashes from pg_shadow
-- ═══════════════════════════════════════════════════════════════════════════════
