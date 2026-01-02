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
        -- Grant necessary permissions for auth_query to read pg_shadow
        GRANT pg_monitor TO pgbouncer;
    END IF;
END
$$;

-- Note: PgBouncer auth_query uses pg_shadow directly
-- The pgbouncer user has pg_monitor role which allows reading pg_shadow
-- auth_query in pgbouncer.ini: SELECT usename, passwd FROM pg_shadow WHERE usename=$1
