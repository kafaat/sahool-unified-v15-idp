-- ═══════════════════════════════════════════════════════════════════════════════
-- Create PgBouncer user for auth_query
-- This user is used by PgBouncer to query PostgreSQL for password verification
-- Supports SCRAM-SHA-256 authentication (PostgreSQL 16 default)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Create pgbouncer user if it doesn't exist
-- Password will be set to match POSTGRES_PASSWORD for compatibility with edoburu/pgbouncer image
DO $$
DECLARE
    postgres_password TEXT;
BEGIN
    -- Get POSTGRES_PASSWORD from environment (set via ALTER USER after creation)
    -- For now, create with a placeholder that will be updated
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
        -- Create user - password will be set to POSTGRES_PASSWORD via ALTER USER
        -- This allows edoburu/pgbouncer image to use DB_PASSWORD for auth_user connection
        CREATE USER pgbouncer WITH PASSWORD 'temp_password_will_be_updated';
        -- Grant necessary permissions for auth_query to read pg_shadow
        GRANT pg_monitor TO pgbouncer;
    END IF;
END
$$;

-- Note: PgBouncer auth_query uses pg_shadow directly
-- The pgbouncer user has pg_monitor role which allows reading pg_shadow
-- auth_query in pgbouncer.ini: SELECT usename, passwd FROM pg_shadow WHERE usename=$1
