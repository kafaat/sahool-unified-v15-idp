#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# PostgreSQL Replica Setup Script
# Runs on REPLICA server during initialization
# Initializes replica from primary using pg_basebackup
# Last Updated: 2026-01-06
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PostgreSQL Replica Initialization"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Environment variables (set by docker-compose)
PRIMARY_HOST="${POSTGRES_PRIMARY_HOST:-postgres-primary}"
PRIMARY_PORT="${POSTGRES_PRIMARY_PORT:-5432}"
REPLICATION_USER="${POSTGRES_REPLICATION_USER:-replicator}"
REPLICATION_PASSWORD="${POSTGRES_REPLICATION_PASSWORD}"

echo "📋 Configuration:"
echo "   - Primary host: ${PRIMARY_HOST}:${PRIMARY_PORT}"
echo "   - Replication user: ${REPLICATION_USER}"
echo "   - Data directory: /var/lib/postgresql/data"
echo ""

# Check if already initialized
if [ -f "/var/lib/postgresql/data/PG_VERSION" ]; then
    echo "ℹ️  Database already initialized, skipping setup"
    exit 0
fi

# Check if replication password is set
if [ -z "$REPLICATION_PASSWORD" ]; then
    echo "❌ ERROR: POSTGRES_REPLICATION_PASSWORD not set!"
    exit 1
fi

# Wait for primary to be ready
echo "⏳ Waiting for primary database at ${PRIMARY_HOST}:${PRIMARY_PORT}..."
MAX_RETRIES=60
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if pg_isready -h "${PRIMARY_HOST}" -p "${PRIMARY_PORT}" -U "${REPLICATION_USER}" -q; then
        echo "✅ Primary database is ready"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Attempt ${RETRY_COUNT}/${MAX_RETRIES}..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ ERROR: Primary database not ready after ${MAX_RETRIES} attempts"
    exit 1
fi

echo ""

# Create .pgpass file for authentication
echo "🔐 Configuring authentication..."
cat > ~/.pgpass <<EOF
${PRIMARY_HOST}:${PRIMARY_PORT}:replication:${REPLICATION_USER}:${REPLICATION_PASSWORD}
${PRIMARY_HOST}:${PRIMARY_PORT}:*:${REPLICATION_USER}:${REPLICATION_PASSWORD}
EOF
chmod 0600 ~/.pgpass
echo "✅ Authentication configured"
echo ""

# Perform base backup from primary
echo "📥 Starting base backup from primary..."
echo "   This may take several minutes depending on database size..."
pg_basebackup \
    -h "${PRIMARY_HOST}" \
    -p "${PRIMARY_PORT}" \
    -U "${REPLICATION_USER}" \
    -D /var/lib/postgresql/data \
    -Fp \
    -Xs \
    -P \
    -R \
    --checkpoint=fast

echo "✅ Base backup completed"
echo ""

# Create standby.signal file (marks this as a replica)
echo "🔌 Configuring as standby server..."
touch /var/lib/postgresql/data/standby.signal
echo "✅ Standby signal created"
echo ""

# Configure primary connection info
echo "⚙️  Configuring replication connection..."
cat >> /var/lib/postgresql/data/postgresql.auto.conf <<EOF
# Replication configuration (auto-generated)
primary_conninfo = 'host=${PRIMARY_HOST} port=${PRIMARY_PORT} user=${REPLICATION_USER} password=${REPLICATION_PASSWORD} application_name=postgres-replica'
primary_slot_name = 'replica_slot'
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
EOF
echo "✅ Replication connection configured"
echo ""

# Set proper permissions
echo "🔒 Setting permissions..."
chown -R postgres:postgres /var/lib/postgresql/data
chmod 0700 /var/lib/postgresql/data
echo "✅ Permissions set"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Replica initialization completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Replica is ready to start streaming replication from primary"
echo ""
