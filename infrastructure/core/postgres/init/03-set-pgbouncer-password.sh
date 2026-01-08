#!/bin/bash
# Set pgbouncer user password to match POSTGRES_PASSWORD
# This script runs after SQL init scripts to update the password

set -e

# Get the password from environment (passed by docker-entrypoint-initdb.d)
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-${POSTGRES_PASSWORD}}"

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "WARNING: POSTGRES_PASSWORD not set, skipping pgbouncer password update"
    exit 0
fi

# Update pgbouncer user password
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
            ALTER USER pgbouncer WITH PASSWORD '$POSTGRES_PASSWORD';
            RAISE NOTICE 'Updated pgbouncer user password';
        ELSE
            RAISE NOTICE 'pgbouncer user does not exist, skipping password update';
        END IF;
    END
    \$\$;
EOSQL

echo "✓ PgBouncer user password updated"

