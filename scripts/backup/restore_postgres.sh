#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - PostgreSQL Restore Script
# نظام استعادة قاعدة بيانات PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Complete restore solution for PostgreSQL with safety checks
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Formatting - الألوان والتنسيق
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Configuration - التكوين
# ─────────────────────────────────────────────────────────────────────────────

# Script paths - مسارات السكريبت
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment variables - تحميل متغيرات البيئة
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Backup file - ملف النسخة الاحتياطية
BACKUP_FILE="${1:-}"
RESTORE_MODE="${2:-full}"  # full, schema-only, data-only, partial

# Database configuration - إعدادات قاعدة البيانات
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
DB_NAME="${POSTGRES_DB:-sahool}"
DB_NAME_TEMP="${DB_NAME}_restore_temp"

# Restore options - خيارات الاستعادة
FORCE_RESTORE="${FORCE_RESTORE:-false}"
CREATE_BACKUP_BEFORE_RESTORE="${CREATE_BACKUP_BEFORE_RESTORE:-true}"
STOP_SERVICES="${STOP_SERVICES:-true}"
VERIFY_RESTORE="${VERIFY_RESTORE:-true}"

# Services to stop/start - الخدمات التي يجب إيقافها/تشغيلها
SERVICES_TO_STOP="${SERVICES_TO_STOP:-api-gateway auth-service user-service}"

# Logging - السجلات
LOG_DIR="${PROJECT_ROOT}/backups/logs"
LOG_FILE="${LOG_DIR}/restore_$(date +%Y%m%d_%H%M%S).log"

# Backup directory
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────

# Print colored message - طباعة رسالة ملونة
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "${LOG_FILE}"
}

# Log function - دالة التسجيل
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_FILE}"
}

# Error handler - معالج الأخطاء
error_exit() {
    print_message "${RED}" "ERROR: $1"
    print_message "${RED}" "Restore failed! Check logs: ${LOG_FILE}"
    exit 1
}

# Success handler - معالج النجاح
success_message() {
    print_message "${GREEN}" "✓ $1"
}

# Warning handler - معالج التحذير
warning_message() {
    print_message "${YELLOW}" "⚠ $1"
}

# Info handler - معالج المعلومات
info_message() {
    print_message "${BLUE}" "ℹ $1"
}

# Question handler - معالج الأسئلة
question_message() {
    print_message "${CYAN}" "? $1"
}

# Check if command exists - التحقق من وجود أمر
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker container status - التحقق من حالة حاوية Docker
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
        error_exit "PostgreSQL container '${POSTGRES_CONTAINER}' is not running"
    fi
}

# Execute PostgreSQL command - تنفيذ أمر PostgreSQL
psql_exec() {
    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" "$@"
}

# Check if database exists - التحقق من وجود قاعدة البيانات
database_exists() {
    local db_name=$1
    psql_exec -lqt | cut -d \| -f 1 | grep -qw "$db_name"
}

# Get database size - الحصول على حجم قاعدة البيانات
get_db_size() {
    local db_name=$1
    psql_exec -t -c "SELECT pg_size_pretty(pg_database_size('${db_name}'));" 2>/dev/null | xargs || echo "N/A"
}

# Get database table count - الحصول على عدد الجداول
get_table_count() {
    local db_name=$1
    psql_exec -d "$db_name" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | xargs || echo "0"
}

# Confirm action - تأكيد الإجراء
confirm_action() {
    local message=$1

    if [ "$FORCE_RESTORE" = "true" ]; then
        return 0
    fi

    question_message "$message"
    read -p "Type 'yes' to continue: " -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_message "${YELLOW}" "Restore cancelled by user"
        exit 0
    fi
}

# Show usage - عرض الاستخدام
show_usage() {
    cat <<EOF
${BOLD}SAHOOL Platform - PostgreSQL Restore Script${NC}
نظام استعادة قاعدة بيانات PostgreSQL

${BOLD}Usage:${NC}
  $0 <backup_file> [restore_mode]

${BOLD}Parameters:${NC}
  backup_file    - Path to backup file (.dump, .sql, .sql.gz, etc.)
  restore_mode   - Restore mode (default: full)
                   • full         - Full database restore
                   • schema-only  - Restore schema only
                   • data-only    - Restore data only
                   • partial      - Partial restore (interactive)

${BOLD}Environment Variables:${NC}
  FORCE_RESTORE                 - Skip confirmations (default: false)
  CREATE_BACKUP_BEFORE_RESTORE  - Create backup before restore (default: true)
  STOP_SERVICES                 - Stop dependent services (default: true)
  VERIFY_RESTORE                - Verify restore integrity (default: true)

${BOLD}Examples:${NC}
  # Restore from latest backup
  $0 --latest

  # Restore specific backup file
  $0 /backups/postgres/daily/20250127_020000/sahool_20250127_020000.dump

  # Restore schema only
  $0 backup.dump schema-only

  # Force restore without confirmation
  FORCE_RESTORE=true $0 backup.dump

EOF
    exit 0
}

# ─────────────────────────────────────────────────────────────────────────────
# Restore Functions - دوال الاستعادة
# ─────────────────────────────────────────────────────────────────────────────

# Find latest backup - البحث عن أحدث نسخة احتياطية
find_latest_backup() {
    info_message "Searching for latest backup..."

    local latest_backup=""

    # Search in daily backups first
    if [ -d "${BACKUP_BASE_DIR}/postgres/daily" ]; then
        latest_backup=$(find "${BACKUP_BASE_DIR}/postgres/daily" -name "*.dump" -o -name "*.dump.gz" | sort -r | head -1)
    fi

    # If not found, search in weekly
    if [ -z "$latest_backup" ] && [ -d "${BACKUP_BASE_DIR}/postgres/weekly" ]; then
        latest_backup=$(find "${BACKUP_BASE_DIR}/postgres/weekly" -name "*.dump" -o -name "*.dump.gz" | sort -r | head -1)
    fi

    if [ -z "$latest_backup" ]; then
        error_exit "No backup found in ${BACKUP_BASE_DIR}/postgres/"
    fi

    echo "$latest_backup"
}

# Decompress backup if needed - فك ضغط النسخة الاحتياطية إذا لزم الأمر
decompress_backup() {
    local file=$1

    # Check if file is compressed
    if [[ "$file" == *.gz ]]; then
        info_message "Decompressing backup file..."
        local decompressed="${file%.gz}"

        if gunzip -c "$file" > "$decompressed"; then
            success_message "Decompression completed"
            echo "$decompressed"
        else
            error_exit "Failed to decompress backup file"
        fi
    elif [[ "$file" == *.zst ]]; then
        info_message "Decompressing backup file (zstd)..."
        local decompressed="${file%.zst}"

        if zstd -d "$file" -o "$decompressed"; then
            success_message "Decompression completed"
            echo "$decompressed"
        else
            error_exit "Failed to decompress backup file"
        fi
    elif [[ "$file" == *.enc ]]; then
        error_exit "Encrypted backup detected. Please decrypt manually first."
    else
        echo "$file"
    fi
}

# Validate backup file - التحقق من صحة ملف النسخة الاحتياطية
validate_backup() {
    local file=$1

    info_message "Validating backup file..."

    # Check file exists
    if [ ! -f "$file" ]; then
        error_exit "Backup file not found: $file"
    fi

    # Check file size
    local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    if [ "$file_size" -eq 0 ]; then
        error_exit "Backup file is empty"
    fi

    # For .dump files, validate with pg_restore --list
    if [[ "$file" == *.dump ]]; then
        if docker run --rm -v "$(dirname $file):/backup" postgres:16-alpine \
            pg_restore --list "/backup/$(basename $file)" > /dev/null 2>&1; then
            success_message "Backup file validation passed"
        else
            error_exit "Backup file validation failed - file may be corrupted"
        fi
    else
        success_message "Basic file validation passed"
    fi
}

# Create safety backup - إنشاء نسخة احتياطية للأمان
create_safety_backup() {
    if [ "$CREATE_BACKUP_BEFORE_RESTORE" != "true" ]; then
        return
    fi

    if ! database_exists "$DB_NAME"; then
        info_message "Database doesn't exist, skipping safety backup"
        return
    fi

    info_message "Creating safety backup before restore..."

    local safety_backup_dir="${BACKUP_BASE_DIR}/postgres/pre-restore"
    local safety_backup_file="${safety_backup_dir}/pre_restore_$(date +%Y%m%d_%H%M%S).dump"

    mkdir -p "$safety_backup_dir"

    if docker exec "${POSTGRES_CONTAINER}" pg_dump \
        -U "${DB_USER}" \
        -F c \
        -f "/tmp/safety_backup.dump" \
        "${DB_NAME}" >> "${LOG_FILE}" 2>&1; then

        docker cp "${POSTGRES_CONTAINER}:/tmp/safety_backup.dump" "$safety_backup_file"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/safety_backup.dump

        success_message "Safety backup created: $safety_backup_file"
    else
        warning_message "Failed to create safety backup (continuing anyway)"
    fi
}

# Stop dependent services - إيقاف الخدمات المعتمدة
stop_dependent_services() {
    if [ "$STOP_SERVICES" != "true" ]; then
        return
    fi

    info_message "Stopping dependent services..."

    for service in $SERVICES_TO_STOP; do
        if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
            info_message "  Stopping ${service}..."
            docker stop "$service" >> "${LOG_FILE}" 2>&1 || true
        fi
    done

    success_message "Services stopped"
}

# Start dependent services - تشغيل الخدمات المعتمدة
start_dependent_services() {
    if [ "$STOP_SERVICES" != "true" ]; then
        return
    fi

    info_message "Starting dependent services..."

    for service in $SERVICES_TO_STOP; do
        if docker ps -a --format '{{.Names}}' | grep -q "^${service}$"; then
            info_message "  Starting ${service}..."
            docker start "$service" >> "${LOG_FILE}" 2>&1 || true
        fi
    done

    success_message "Services started"
}

# Terminate database connections - إنهاء اتصالات قاعدة البيانات
terminate_connections() {
    local db_name=$1

    info_message "Terminating active connections to ${db_name}..."

    psql_exec -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${db_name}' AND pid <> pg_backend_pid();" >> "${LOG_FILE}" 2>&1 || true

    success_message "Connections terminated"
}

# Restore full database - استعادة كاملة لقاعدة البيانات
restore_full() {
    local backup_file=$1

    info_message "Starting full database restore..."

    # Terminate connections
    if database_exists "$DB_NAME"; then
        terminate_connections "$DB_NAME"

        # Drop existing database
        info_message "Dropping existing database..."
        if psql_exec -c "DROP DATABASE IF EXISTS ${DB_NAME};" >> "${LOG_FILE}" 2>&1; then
            success_message "Existing database dropped"
        else
            error_exit "Failed to drop existing database"
        fi
    fi

    # Create new database
    info_message "Creating new database..."
    if psql_exec -c "CREATE DATABASE ${DB_NAME};" >> "${LOG_FILE}" 2>&1; then
        success_message "New database created"
    else
        error_exit "Failed to create new database"
    fi

    # Enable PostGIS extension
    info_message "Enabling PostGIS extension..."
    psql_exec -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS postgis;" >> "${LOG_FILE}" 2>&1 || true
    psql_exec -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;" >> "${LOG_FILE}" 2>&1 || true

    # Restore data
    info_message "Restoring data from backup..."

    if [[ "$backup_file" == *.dump ]]; then
        # Copy to container
        docker cp "$backup_file" "${POSTGRES_CONTAINER}:/tmp/restore.dump"

        # Restore
        if docker exec "${POSTGRES_CONTAINER}" pg_restore \
            -U "${DB_USER}" \
            -d "${DB_NAME}" \
            -v \
            --no-owner \
            --no-privileges \
            /tmp/restore.dump >> "${LOG_FILE}" 2>&1; then

            docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/restore.dump
            success_message "Data restoration completed"
        else
            docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/restore.dump
            error_exit "Data restoration failed"
        fi
    elif [[ "$backup_file" == *.sql ]]; then
        # Copy to container
        docker cp "$backup_file" "${POSTGRES_CONTAINER}:/tmp/restore.sql"

        # Restore
        if docker exec "${POSTGRES_CONTAINER}" psql \
            -U "${DB_USER}" \
            -d "${DB_NAME}" \
            -f /tmp/restore.sql >> "${LOG_FILE}" 2>&1; then

            docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/restore.sql
            success_message "Data restoration completed"
        else
            docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/restore.sql
            error_exit "Data restoration failed"
        fi
    else
        error_exit "Unsupported backup file format"
    fi

    # Post-restore tasks
    post_restore_tasks
}

# Restore schema only - استعادة المخطط فقط
restore_schema_only() {
    local backup_file=$1

    info_message "Starting schema-only restore..."

    if [[ "$backup_file" != *.dump ]]; then
        error_exit "Schema-only restore requires .dump file format"
    fi

    # Create temp database
    psql_exec -c "DROP DATABASE IF EXISTS ${DB_NAME_TEMP};" >> "${LOG_FILE}" 2>&1 || true
    psql_exec -c "CREATE DATABASE ${DB_NAME_TEMP};" >> "${LOG_FILE}" 2>&1

    # Copy to container
    docker cp "$backup_file" "${POSTGRES_CONTAINER}:/tmp/restore.dump"

    # Restore schema only
    if docker exec "${POSTGRES_CONTAINER}" pg_restore \
        -U "${DB_USER}" \
        -d "${DB_NAME_TEMP}" \
        --schema-only \
        --no-owner \
        /tmp/restore.dump >> "${LOG_FILE}" 2>&1; then

        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/restore.dump
        success_message "Schema restoration completed to ${DB_NAME_TEMP}"
        info_message "Review the schema in ${DB_NAME_TEMP} before applying to ${DB_NAME}"
    else
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/restore.dump
        error_exit "Schema restoration failed"
    fi
}

# Post-restore tasks - مهام ما بعد الاستعادة
post_restore_tasks() {
    info_message "Running post-restore tasks..."

    # Reindex database
    info_message "  Reindexing database..."
    psql_exec -d "${DB_NAME}" -c "REINDEX DATABASE ${DB_NAME};" >> "${LOG_FILE}" 2>&1 || warning_message "Reindex failed"

    # Analyze database
    info_message "  Analyzing database..."
    psql_exec -d "${DB_NAME}" -c "ANALYZE;" >> "${LOG_FILE}" 2>&1 || warning_message "Analyze failed"

    # Vacuum database
    info_message "  Vacuuming database..."
    psql_exec -d "${DB_NAME}" -c "VACUUM ANALYZE;" >> "${LOG_FILE}" 2>&1 || warning_message "Vacuum failed"

    success_message "Post-restore tasks completed"
}

# Verify restore - التحقق من الاستعادة
verify_restore() {
    if [ "$VERIFY_RESTORE" != "true" ]; then
        return
    fi

    info_message "Verifying restored database..."

    # Check if database exists
    if ! database_exists "$DB_NAME"; then
        error_exit "Restored database not found"
    fi

    # Get database stats
    local db_size=$(get_db_size "$DB_NAME")
    local table_count=$(get_table_count "$DB_NAME")

    info_message "  Database size: $db_size"
    info_message "  Table count: $table_count"

    # Basic connectivity test
    if psql_exec -d "${DB_NAME}" -c "SELECT 1;" >> "${LOG_FILE}" 2>&1; then
        success_message "Database connectivity verified"
    else
        error_exit "Database connectivity test failed"
    fi

    # Check critical tables (customize as needed)
    local critical_tables="users farms fields"
    for table in $critical_tables; do
        if psql_exec -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM $table;" >> "${LOG_FILE}" 2>&1; then
            local count=$(psql_exec -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM $table;" | xargs)
            info_message "  Table '$table': $count rows"
        else
            warning_message "  Table '$table' not found or empty"
        fi
    done

    success_message "Restore verification completed"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local overall_start_time=$(date +%s)

    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  SAHOOL Platform - PostgreSQL Restore"
    print_message "${BLUE}" "  نظام استعادة قاعدة بيانات PostgreSQL"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Check for help
    if [ "$#" -eq 0 ] || [ "$BACKUP_FILE" = "--help" ] || [ "$BACKUP_FILE" = "-h" ]; then
        show_usage
    fi

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Check prerequisites
    check_container

    # Find latest backup if requested
    if [ "$BACKUP_FILE" = "--latest" ]; then
        BACKUP_FILE=$(find_latest_backup)
        info_message "Using latest backup: $BACKUP_FILE"
    fi

    # Validate backup file
    validate_backup "$BACKUP_FILE"

    # Decompress if needed
    BACKUP_FILE=$(decompress_backup "$BACKUP_FILE")

    # Show restore information
    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"
    info_message "Restore Information:"
    info_message "  Backup file: $BACKUP_FILE"
    info_message "  Restore mode: $RESTORE_MODE"
    info_message "  Target database: $DB_NAME"
    info_message "  Container: $POSTGRES_CONTAINER"

    if database_exists "$DB_NAME"; then
        info_message "  Current database size: $(get_db_size $DB_NAME)"
        info_message "  Current table count: $(get_table_count $DB_NAME)"
    else
        info_message "  Database does not exist (will be created)"
    fi
    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"

    # Confirm restore
    confirm_action "⚠️  This will REPLACE the current database. Are you sure?"

    # Create safety backup
    create_safety_backup

    # Stop dependent services
    stop_dependent_services

    # Perform restore based on mode
    case "$RESTORE_MODE" in
        full)
            restore_full "$BACKUP_FILE"
            ;;
        schema-only)
            restore_schema_only "$BACKUP_FILE"
            ;;
        data-only)
            error_exit "data-only mode not yet implemented"
            ;;
        partial)
            error_exit "partial mode not yet implemented"
            ;;
        *)
            error_exit "Unknown restore mode: $RESTORE_MODE"
            ;;
    esac

    # Verify restore
    verify_restore

    # Start dependent services
    start_dependent_services

    # Calculate total time
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "PostgreSQL restore completed successfully!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "Restored database: ${DB_NAME}"
    info_message "Database size: $(get_db_size $DB_NAME)"
    info_message "Log file: ${LOG_FILE}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    # Cleanup temporary files
    if [[ "$BACKUP_FILE" == *"/tmp/"* ]]; then
        rm -f "$BACKUP_FILE"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
