#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# PostgreSQL Replication Setup Script
# Runs on PRIMARY server during initialization
# Creates replication user and replication slot
# Last Updated: 2026-01-06
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setting up PostgreSQL Streaming Replication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Environment variables (set by docker-compose)
REPLICATION_USER="${POSTGRES_REPLICATION_USER:-replicator}"
REPLICATION_PASSWORD="${POSTGRES_REPLICATION_PASSWORD}"

# Check if replication password is set
if [ -z "$REPLICATION_PASSWORD" ]; then
    echo "⚠️  WARNING: POSTGRES_REPLICATION_PASSWORD not set!"
    echo "Skipping replication setup. Set this variable to enable replication."
    exit 0
fi

echo "📋 Configuration:"
echo "   - Replication user: ${REPLICATION_USER}"
echo "   - Database: ${POSTGRES_DB:-sahool}"
echo ""

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -U "${POSTGRES_USER:-sahool}" -q; do
    sleep 1
done
echo "✅ PostgreSQL is ready"
echo ""

# Create replication user
echo "👤 Creating replication user '${REPLICATION_USER}'..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-sahool}" --dbname "${POSTGRES_DB:-sahool}" <<-EOSQL
    -- Check if replication user already exists
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${REPLICATION_USER}') THEN
            -- Create replication user with REPLICATION privilege
            CREATE ROLE ${REPLICATION_USER} WITH REPLICATION LOGIN PASSWORD '${REPLICATION_PASSWORD}';
            RAISE NOTICE 'Created replication user: ${REPLICATION_USER}';
        ELSE
            -- Update password for existing user
            ALTER ROLE ${REPLICATION_USER} WITH REPLICATION LOGIN PASSWORD '${REPLICATION_PASSWORD}';
            RAISE NOTICE 'Updated existing replication user: ${REPLICATION_USER}';
        END IF;
    END
    \$\$;

    -- Grant necessary permissions
    GRANT pg_monitor TO ${REPLICATION_USER};
    GRANT CONNECT ON DATABASE ${POSTGRES_DB:-sahool} TO ${REPLICATION_USER};
EOSQL
echo "✅ Replication user created/updated"
echo ""

# Create replication slot
echo "🔌 Creating replication slot 'replica_slot'..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-sahool}" --dbname "${POSTGRES_DB:-sahool}" <<-EOSQL
    -- Check if replication slot already exists
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replica_slot') THEN
            -- Create physical replication slot
            SELECT pg_create_physical_replication_slot('replica_slot');
            RAISE NOTICE 'Created replication slot: replica_slot';
        ELSE
            RAISE NOTICE 'Replication slot already exists: replica_slot';
        END IF;
    END
    \$\$;
EOSQL
echo "✅ Replication slot created"
echo ""

# Enable pg_stat_statements extension
echo "📊 Enabling performance monitoring extensions..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-sahool}" --dbname "${POSTGRES_DB:-sahool}" <<-EOSQL
    -- Enable pg_stat_statements for query performance tracking
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

    -- Verify extension is loaded
    SELECT extname, extversion FROM pg_extension WHERE extname = 'pg_stat_statements';
EOSQL
echo "✅ Extensions enabled"
echo ""

# Display replication status
echo "📊 Replication Status:"
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-sahool}" --dbname "${POSTGRES_DB:-sahool}" <<-EOSQL
    -- Show replication slots
    SELECT slot_name, slot_type, active, restart_lsn
    FROM pg_replication_slots;

    -- Show replication configuration
    SELECT name, setting, unit, category
    FROM pg_settings
    WHERE name IN ('wal_level', 'max_wal_senders', 'max_replication_slots', 'archive_mode')
    ORDER BY name;
EOSQL
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Replication setup completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "   1. Start the replica container"
echo "   2. Monitor replication status with:"
echo "      docker exec -it sahool-postgres-primary psql -U sahool -c 'SELECT * FROM pg_stat_replication;'"
echo ""
