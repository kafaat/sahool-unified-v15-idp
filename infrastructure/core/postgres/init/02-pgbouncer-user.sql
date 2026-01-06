-- ═══════════════════════════════════════════════════════════════════════════════
-- Create PgBouncer user for auth_query
-- This user is used by PgBouncer to query PostgreSQL for password verification
-- Supports SCRAM-SHA-256 authentication (PostgreSQL 16 default)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Create pgbouncer user if it doesn't exist
-- Password will be set to match POSTGRES_PASSWORD for compatibility with edoburu/pgbouncer image
-- Note: The password must be set manually after creation using the same password as POSTGRES_PASSWORD
-- This is done via the shell script 03-set-pgbouncer-password.sh
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
        -- Create user with a temporary password
        -- The password will be updated by 03-set-pgbouncer-password.sh to match POSTGRES_PASSWORD
        CREATE USER pgbouncer WITH PASSWORD 'temp_password_will_be_updated';
        -- Grant necessary permissions for auth_query to read pg_shadow
        GRANT pg_monitor TO pgbouncer;
    ELSE
        -- If user exists, ensure it has the correct permissions
        GRANT pg_monitor TO pgbouncer;
    END IF;
END
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Create the pgbouncer schema first (needed for function creation)
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE SCHEMA IF NOT EXISTS pgbouncer AUTHORIZATION pgbouncer;

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

-- ═══════════════════════════════════════════════════════════════════════════════
-- Note for pgbouncer.ini auth_query:
-- Use: auth_query = SELECT usename, passwd FROM pgbouncer.get_auth($1)
-- ═══════════════════════════════════════════════════════════════════════════════
