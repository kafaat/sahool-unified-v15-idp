#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - InfluxDB Backup Script
# سكريبت النسخ الاحتياطي لقاعدة بيانات InfluxDB
# ═══════════════════════════════════════════════════════════════════════════════
#
# Features:
# - Automated backups with date-based naming
# - Compression for storage efficiency
# - Retention policy (cleanup old backups)
# - Optional S3/MinIO upload
# - Validation and logging
#
# Usage:
#   ./backup-influxdb.sh [environment]
#
# Environment: load, sim, advanced (default: load)
#
# Schedule with cron:
#   0 2 * * * /path/to/backup-influxdb.sh load >> /var/log/influxdb-backup.log 2>&1
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-load}"
BACKUP_ROOT_DIR="${BACKUP_DIR:-/var/backups/influxdb}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_DIR=$(date +%Y%m%d)

# InfluxDB Configuration based on environment
case "$ENVIRONMENT" in
    load)
        INFLUXDB_CONTAINER="sahool-loadtest-influxdb"
        INFLUXDB_URL="http://localhost:8086"
        INFLUXDB_PORT="8086"
        ;;
    sim)
        INFLUXDB_CONTAINER="sahool_influxdb_sim"
        INFLUXDB_URL="http://localhost:8087"
        INFLUXDB_PORT="8087"
        ;;
    advanced)
        INFLUXDB_CONTAINER="sahool_influxdb_advanced"
        INFLUXDB_URL="http://localhost:8088"
        INFLUXDB_PORT="8088"
        ;;
    *)
        echo -e "${RED}ERROR: Invalid environment. Use: load, sim, or advanced${NC}"
        exit 1
        ;;
esac

# Backup directory structure
BACKUP_DIR="${BACKUP_ROOT_DIR}/${ENVIRONMENT}/${DATE_DIR}"
BACKUP_NAME="influxdb_${ENVIRONMENT}_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# S3/MinIO Configuration (optional)
S3_ENABLED="${S3_ENABLED:-false}"
S3_BUCKET="${S3_BUCKET:-sahool-influxdb-backups}"
S3_ENDPOINT="${S3_ENDPOINT:-}"
S3_ACCESS_KEY="${S3_ACCESS_KEY:-}"
S3_SECRET_KEY="${S3_SECRET_KEY:-}"

# Logging
LOG_FILE="${BACKUP_ROOT_DIR}/${ENVIRONMENT}/backup.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to log with color
log_color() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "$LOG_FILE"
}

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}SAHOOL InfluxDB Backup Script${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if InfluxDB container is running
log_color "$YELLOW" "Checking InfluxDB container status..."
if ! docker ps --format '{{.Names}}' | grep -q "^${INFLUXDB_CONTAINER}$"; then
    log_color "$RED" "ERROR: InfluxDB container '$INFLUXDB_CONTAINER' is not running"
    exit 1
fi
log_color "$GREEN" "✓ InfluxDB container is running"
echo ""

# Check if admin token is set
if [ -z "$INFLUXDB_ADMIN_TOKEN" ]; then
    log_color "$RED" "ERROR: INFLUXDB_ADMIN_TOKEN environment variable is not set"
    echo "Load from .env file: source .env.influxdb.secret"
    exit 1
fi

# Create backup directory
log_color "$YELLOW" "Creating backup directory..."
mkdir -p "$BACKUP_DIR"
log_color "$GREEN" "✓ Backup directory: $BACKUP_DIR"
echo ""

# Perform backup
log_color "$YELLOW" "Starting InfluxDB backup..."
log "Container: $INFLUXDB_CONTAINER"
log "Organization: ${INFLUXDB_ORG:-sahool}"
log "Backup path: $BACKUP_PATH"

# Create backup inside container
docker exec "$INFLUXDB_CONTAINER" influx backup \
    --host "$INFLUXDB_URL" \
    --token "$INFLUXDB_ADMIN_TOKEN" \
    "/tmp/${BACKUP_NAME}" 2>&1 | tee -a "$LOG_FILE"

# Copy backup from container to host
docker cp "${INFLUXDB_CONTAINER}:/tmp/${BACKUP_NAME}" "$BACKUP_PATH"

# Clean up backup inside container
docker exec "$INFLUXDB_CONTAINER" rm -rf "/tmp/${BACKUP_NAME}"

log_color "$GREEN" "✓ Backup completed successfully"
echo ""

# Verify backup
log_color "$YELLOW" "Verifying backup..."
if [ -d "$BACKUP_PATH" ]; then
    BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)
    FILE_COUNT=$(find "$BACKUP_PATH" -type f | wc -l)
    log_color "$GREEN" "✓ Backup verified"
    log "  Size: $BACKUP_SIZE"
    log "  Files: $FILE_COUNT"
else
    log_color "$RED" "✗ Backup verification failed - directory not found"
    exit 1
fi
echo ""

# Compress backup
log_color "$YELLOW" "Compressing backup..."
ARCHIVE_PATH="${BACKUP_PATH}.tar.gz"
tar -czf "$ARCHIVE_PATH" -C "$BACKUP_DIR" "$BACKUP_NAME"
log_color "$GREEN" "✓ Backup compressed: $(basename $ARCHIVE_PATH)"

# Remove uncompressed backup
rm -rf "$BACKUP_PATH"

# Get compressed size
COMPRESSED_SIZE=$(du -sh "$ARCHIVE_PATH" | cut -f1)
log "  Compressed size: $COMPRESSED_SIZE"
echo ""

# Upload to S3/MinIO (if enabled)
if [ "$S3_ENABLED" = "true" ]; then
    log_color "$YELLOW" "Uploading backup to S3/MinIO..."

    if command -v aws &> /dev/null; then
        S3_KEY="${ENVIRONMENT}/${DATE_DIR}/$(basename $ARCHIVE_PATH)"

        if [ -n "$S3_ENDPOINT" ]; then
            aws s3 cp "$ARCHIVE_PATH" "s3://${S3_BUCKET}/${S3_KEY}" \
                --endpoint-url "$S3_ENDPOINT" 2>&1 | tee -a "$LOG_FILE"
        else
            aws s3 cp "$ARCHIVE_PATH" "s3://${S3_BUCKET}/${S3_KEY}" 2>&1 | tee -a "$LOG_FILE"
        fi

        log_color "$GREEN" "✓ Backup uploaded to S3"
        log "  Bucket: $S3_BUCKET"
        log "  Key: $S3_KEY"
    else
        log_color "$YELLOW" "⚠ AWS CLI not found - skipping S3 upload"
    fi
    echo ""
fi

# Cleanup old backups
log_color "$YELLOW" "Cleaning up old backups (retention: ${RETENTION_DAYS} days)..."
DELETED_COUNT=0

find "$BACKUP_ROOT_DIR/$ENVIRONMENT" -type f -name "*.tar.gz" -mtime +$RETENTION_DAYS | while read old_backup; do
    log "  Deleting: $(basename $old_backup)"
    rm -f "$old_backup"
    DELETED_COUNT=$((DELETED_COUNT + 1))
done

# Clean up empty directories
find "$BACKUP_ROOT_DIR/$ENVIRONMENT" -type d -empty -delete

log_color "$GREEN" "✓ Cleanup completed"
echo ""

# Backup summary
log_color "$GREEN" "═══════════════════════════════════════════════════════════════════════════════"
log_color "$GREEN" "Backup Summary"
log_color "$GREEN" "═══════════════════════════════════════════════════════════════════════════════"
log "Environment: $ENVIRONMENT"
log "Timestamp: $TIMESTAMP"
log "Archive: $(basename $ARCHIVE_PATH)"
log "Size: $COMPRESSED_SIZE"
log "Location: $ARCHIVE_PATH"

if [ "$S3_ENABLED" = "true" ]; then
    log "S3 Upload: Enabled"
fi

log "Retention: $RETENTION_DAYS days"
log_color "$GREEN" "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Test restore capability (optional)
if [ "${TEST_RESTORE:-false}" = "true" ]; then
    log_color "$YELLOW" "Testing restore capability..."
    TEST_RESTORE_DIR="/tmp/influxdb-restore-test-${TIMESTAMP}"

    mkdir -p "$TEST_RESTORE_DIR"
    tar -xzf "$ARCHIVE_PATH" -C "$TEST_RESTORE_DIR"

    if [ -d "$TEST_RESTORE_DIR/$BACKUP_NAME" ]; then
        log_color "$GREEN" "✓ Restore test successful"
        rm -rf "$TEST_RESTORE_DIR"
    else
        log_color "$RED" "✗ Restore test failed"
    fi
    echo ""
fi

log_color "$GREEN" "Backup completed successfully!"
echo ""

# Exit with success
exit 0
