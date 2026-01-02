-- ═══════════════════════════════════════════════════════════════════════════════
-- Create PgBouncer user for auth_query
-- This user is used by PgBouncer to query PostgreSQL for password verification
-- Supports SCRAM-SHA-256 authentication (PostgreSQL 16 default)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Create pgbouncer user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
        CREATE USER pgbouncer WITH PASSWORD 'pgbouncer_auth_query';
    END IF;
END
$$;

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

-- Grant execute permission to pgbouncer user
GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(TEXT) TO pgbouncer;

-- Create the pgbouncer schema if not exists
CREATE SCHEMA IF NOT EXISTS pgbouncer AUTHORIZATION pgbouncer;

-- Move function to pgbouncer schema
ALTER FUNCTION pgbouncer.get_auth(TEXT) SET search_path = pg_catalog;

-- Alternative: Direct GRANT for pg_shadow access (simpler but requires superuser)
-- This grants the pgbouncer user permission to read pg_authid
-- GRANT pg_read_all_data TO pgbouncer;

-- Note for pgbouncer.ini auth_query:
-- Use: auth_query = SELECT usename, passwd FROM pgbouncer.get_auth($1)
-- Or if using GRANT: auth_query = SELECT usename, passwd FROM pg_shadow WHERE usename=$1
