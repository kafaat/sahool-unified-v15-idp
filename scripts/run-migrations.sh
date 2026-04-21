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
MIGRATIONS_TABLE="${MIGRATIONS_TABLE:-schema_migrations}"
MIGRATIONS_STRICT="${MIGRATIONS_STRICT:-false}"

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
    # Create migration tracking table (idempotent)
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c \
      "CREATE TABLE IF NOT EXISTS ${MIGRATIONS_TABLE} (
          migration_name TEXT PRIMARY KEY,
          applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
       );"

    APPLIED_COUNT=0
    SKIPPED_COUNT=0
    FAILED_COUNT=0

    for f in $(find "$MIGRATIONS_DIR" -maxdepth 1 -type f -name "*.sql" | sort); do
        if [ -f "$f" ]; then
            MIGRATION_NAME="$(basename "$f")"
            EXISTS=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c \
              "SELECT 1 FROM ${MIGRATIONS_TABLE} WHERE migration_name = '${MIGRATION_NAME}' LIMIT 1;")

            if [ "$EXISTS" = "1" ]; then
                echo "Skipping (already applied): ${MIGRATION_NAME}"
                SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
                continue
            fi

            echo "Executing: ${MIGRATION_NAME}..."
            if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -f "$f"; then
                PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c \
                  "INSERT INTO ${MIGRATIONS_TABLE} (migration_name) VALUES ('${MIGRATION_NAME}') ON CONFLICT DO NOTHING;"
                APPLIED_COUNT=$((APPLIED_COUNT + 1))
            else
                echo "⚠️ Warning: Migration ${MIGRATION_NAME} failed"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
        fi
    done
    echo "✅ Migrations complete! applied=${APPLIED_COUNT}, skipped=${SKIPPED_COUNT}, failed=${FAILED_COUNT}"
    if [ "$MIGRATIONS_STRICT" = "true" ] && [ "$FAILED_COUNT" -gt 0 ]; then
        echo "❌ Strict mode enabled and one or more migrations failed"
        exit 1
    fi
else
    echo "⚠️ Migrations directory not found: $MIGRATIONS_DIR"
fi

echo "Done!"
