#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Database Migration Runner
# Script to apply all pending migrations to PostgreSQL database
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database connection details
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-sahool}"
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

# Migration directory
MIGRATION_DIR="./infrastructure/core/postgres/migrations"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  SAHOOL Database Migration Runner${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if PostgreSQL is accessible
echo -e "${YELLOW}→ Checking database connection...${NC}"
if docker exec sahool-postgres pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is accessible${NC}"
else
    echo -e "${RED}✗ Cannot connect to database${NC}"
    echo -e "${YELLOW}  Make sure PostgreSQL container is running: docker-compose up -d postgres${NC}"
    exit 1
fi

# Create migrations tracking table if it doesn't exist
echo -e "${YELLOW}→ Creating migrations tracking table...${NC}"
docker exec -i sahool-postgres psql -U "$DB_USER" -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(255) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    checksum VARCHAR(64)
);
EOF
echo -e "${GREEN}✓ Migrations tracking table ready${NC}"

# Get list of applied migrations
echo -e "${YELLOW}→ Checking applied migrations...${NC}"
APPLIED_MIGRATIONS=$(docker exec sahool-postgres psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT filename FROM schema_migrations ORDER BY applied_at;")
echo -e "${GREEN}✓ Found $(echo "$APPLIED_MIGRATIONS" | grep -c .) applied migrations${NC}"

# Apply pending migrations
echo -e "${YELLOW}→ Applying pending migrations...${NC}"
MIGRATION_COUNT=0

# Sort migration files
for migration_file in $(ls -1 "$MIGRATION_DIR"/*.sql 2>/dev/null | sort); do
    filename=$(basename "$migration_file")
    
    # Check if migration already applied
    if echo "$APPLIED_MIGRATIONS" | grep -q "$filename"; then
        echo -e "${BLUE}  ⊙ Skipping $filename (already applied)${NC}"
        continue
    fi
    
    # Apply migration
    echo -e "${YELLOW}  → Applying $filename...${NC}"
    
    if docker exec -i sahool-postgres psql -U "$DB_USER" -d "$DB_NAME" < "$migration_file"; then
        # Record migration
        docker exec -i sahool-postgres psql -U "$DB_USER" -d "$DB_NAME" <<EOF
INSERT INTO schema_migrations (filename, version) 
VALUES ('$filename', '$(echo $filename | grep -oP '^\d+|V\d+' || echo 'manual')');
EOF
        echo -e "${GREEN}  ✓ Applied $filename${NC}"
        ((MIGRATION_COUNT++))
    else
        echo -e "${RED}  ✗ Failed to apply $filename${NC}"
        exit 1
    fi
done

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
if [ $MIGRATION_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All migrations are up to date!${NC}"
else
    echo -e "${GREEN}✓ Successfully applied $MIGRATION_COUNT migration(s)${NC}"
fi
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Show current schema version
echo ""
echo -e "${YELLOW}Current schema migrations:${NC}"
docker exec sahool-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    id,
    filename,
    version,
    applied_at 
FROM schema_migrations 
ORDER BY applied_at DESC 
LIMIT 10;
"

echo ""
echo -e "${GREEN}✓ Migration complete!${NC}"
