#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - PostgreSQL Post-Bootstrap Script
# سكريبت ما بعد التهيئة الأولية لقاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Configures PostgreSQL after initial cluster bootstrap
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Wait for PostgreSQL to be ready
until pg_isready -U postgres; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 2
done

# Install extensions
psql -U postgres -d postgres <<-EOSQL
    -- Create extensions for SAHOOL platform
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    CREATE EXTENSION IF NOT EXISTS btree_gist;
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    -- Create replication user if not exists
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'replicator') THEN
            CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '${REPLICATION_PASSWORD}';
        END IF;
    END
    \$\$;

    -- Create application database if not exists
    SELECT 'CREATE DATABASE sahool'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sahool')\gexec

    -- Grant permissions
    GRANT CONNECT ON DATABASE sahool TO replicator;
EOSQL

# Install PostGIS extensions in sahool database
psql -U postgres -d sahool <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    CREATE EXTENSION IF NOT EXISTS btree_gist;
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
EOSQL

echo "Post-bootstrap completed successfully"
