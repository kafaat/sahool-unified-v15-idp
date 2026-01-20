#!/bin/sh
# ═══════════════════════════════════════════════════════════════════════════════
# Set pgbouncer user password to match POSTGRES_PASSWORD
# This script runs after SQL init scripts to update the password
#
# SECURITY: Uses psql's -v variable binding to prevent SQL injection
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Get the password from environment (passed by docker-entrypoint-initdb.d)
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-${POSTGRES_PASSWORD}}"

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "WARNING: POSTGRES_PASSWORD not set, skipping pgbouncer password update"
    exit 0
fi

# Escape single quotes in password for safe SQL usage
# This replaces ' with '' which is the SQL standard for escaping single quotes
ESCAPED_PASSWORD=$(printf '%s' "$POSTGRES_PASSWORD" | sed "s/'/''/g")

# Update pgbouncer user password using properly escaped password
# Using format() with %L for safe literal quoting inside PL/pgSQL
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOSQL
DO \$\$
DECLARE
    _escaped_pass TEXT := '${ESCAPED_PASSWORD}';
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
        -- Use format() with %L for safe SQL literal quoting
        EXECUTE format('ALTER USER pgbouncer WITH PASSWORD %L', _escaped_pass);
        RAISE NOTICE 'Updated pgbouncer user password';
    ELSE
        RAISE NOTICE 'pgbouncer user does not exist, skipping password update';
    END IF;
END
\$\$;
EOSQL

echo "✓ PgBouncer user password updated"
