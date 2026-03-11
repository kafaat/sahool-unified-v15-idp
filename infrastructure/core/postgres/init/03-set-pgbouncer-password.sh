#!/bin/sh
# ═══════════════════════════════════════════════════════════════════════════════
# Set pgbouncer user password to match POSTGRES_PASSWORD
# This script runs after SQL init scripts to update the password
#
# SECURITY: Uses psql -v variable binding to prevent SQL injection.
# The quoted heredoc (<<'EOSQL') prevents shell expansion inside the SQL block.
# The :'password_val' syntax makes psql safely quote the value as a SQL literal.
# ═══════════════════════════════════════════════════════════════════════════════

set -e

POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "WARNING: POSTGRES_PASSWORD not set, skipping pgbouncer password update"
    exit 0
fi

# Pass password via psql's -v flag; :'password_val' is safely quoted by psql
# \if requires psql 10+ (PostgreSQL 16 ships psql 16)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    -v password_val="$POSTGRES_PASSWORD" <<'EOSQL'
SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') AS pgbouncer_exists \gset
\if :pgbouncer_exists
ALTER USER pgbouncer WITH PASSWORD :'password_val';
\echo 'Updated pgbouncer user password'
\else
\echo 'pgbouncer user does not exist, skipping password update'
\endif
EOSQL

echo "pgbouncer password init script completed"
