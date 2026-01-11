#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Database Migration Script
# سكريبت ترحيل قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Configuration
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_USER="${POSTGRES_USER:-sahool}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
POSTGRES_DB="${POSTGRES_DB:-sahool}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-/migrations}"

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║       SAHOOL Database Migration Script                               ║"
echo "║       سكريبت ترحيل قاعدة بيانات سهول                                  ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER"; do
    echo "PostgreSQL not ready yet... waiting"
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# Run migrations
echo "Running migrations from $MIGRATIONS_DIR..."

if [ -d "$MIGRATIONS_DIR" ]; then
    for f in "$MIGRATIONS_DIR"/*.sql; do
        if [ -f "$f" ]; then
            echo "Executing: $(basename "$f")..."
            PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$f" || {
                echo "⚠️ Warning: Migration $(basename "$f") had issues (may already exist)"
            }
        fi
    done
    echo "✅ Migrations complete!"
else
    echo "⚠️ Migrations directory not found: $MIGRATIONS_DIR"
fi

echo "Done!"
