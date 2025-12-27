#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - PostgreSQL Backup Script
# نظام النسخ الاحتياطي لقاعدة بيانات PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Complete backup solution for PostgreSQL with compression and S3
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Formatting - الألوان والتنسيق
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Backup configuration - إعدادات النسخ الاحتياطي
BACKUP_TYPE="${1:-daily}"  # daily, weekly, monthly, manual
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
BACKUP_DIR="${BACKUP_BASE_DIR}/postgres/${BACKUP_TYPE}/${BACKUP_DATE}"

# Retention policy (days) - سياسة الاحتفاظ بالنسخ
declare -A RETENTION_DAYS=(
    ["daily"]=7
    ["weekly"]=28
    ["monthly"]=365
    ["manual"]=90
)

# Database configuration - إعدادات قاعدة البيانات
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
DB_NAME="${POSTGRES_DB:-sahool}"

# Backup options - خيارات النسخ الاحتياطي
COMPRESSION="${BACKUP_COMPRESSION:-gzip}"  # gzip, zstd, none
ENCRYPTION_ENABLED="${BACKUP_ENCRYPTION_ENABLED:-false}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# S3/MinIO configuration - إعدادات S3/MinIO
S3_ENABLED="${S3_BACKUP_ENABLED:-false}"
S3_ENDPOINT="${S3_ENDPOINT:-http://minio:9000}"
S3_BUCKET="${S3_BUCKET:-sahool-backups}"
S3_ACCESS_KEY="${S3_ACCESS_KEY:-${MINIO_ROOT_USER}}"
S3_SECRET_KEY="${S3_SECRET_KEY:-${MINIO_ROOT_PASSWORD}}"

# Notification configuration - إعدادات الإشعارات
EMAIL_NOTIFICATIONS="${EMAIL_NOTIFICATIONS_ENABLED:-false}"
SLACK_NOTIFICATIONS="${SLACK_NOTIFICATIONS_ENABLED:-false}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# Logging - السجلات
LOG_DIR="${BACKUP_BASE_DIR}/logs"
LOG_FILE="${LOG_DIR}/postgres_${BACKUP_TYPE}_$(date +%Y%m%d).log"

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
    send_notification "failure" "PostgreSQL backup failed: $1"
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

# Get database size - الحصول على حجم قاعدة البيانات
get_db_size() {
    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -t -c \
        "SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));" | xargs
}

# Format bytes - تنسيق البايتات
format_bytes() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes} B"
    elif [ "$bytes" -lt 1048576 ]; then
        echo "$(( bytes / 1024 )) KB"
    elif [ "$bytes" -lt 1073741824 ]; then
        echo "$(( bytes / 1048576 )) MB"
    else
        echo "$(( bytes / 1073741824 )) GB"
    fi
}

# Send notification - إرسال إشعار
send_notification() {
    local status=$1
    local message=$2

    # Slack notification
    if [ "$SLACK_NOTIFICATIONS" = "true" ] && [ -n "$SLACK_WEBHOOK_URL" ]; then
        local color="good"
        local emoji=":white_check_mark:"

        if [ "$status" = "failure" ]; then
            color="danger"
            emoji=":x:"
        fi

        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H 'Content-Type: application/json' \
            -d @- > /dev/null 2>&1 <<EOF
{
    "attachments": [{
        "color": "${color}",
        "title": "${emoji} PostgreSQL Backup - ${BACKUP_TYPE}",
        "text": "${message}",
        "footer": "SAHOOL Backup System",
        "ts": $(date +%s)
    }]
}
EOF
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup Functions - دوال النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

# Initialize backup - تهيئة النسخ الاحتياطي
init_backup() {
    info_message "Initializing PostgreSQL backup..."
    info_message "Backup type: ${BACKUP_TYPE}"
    info_message "Database: ${DB_NAME}"

    # Create backup directories - إنشاء مجلدات النسخ الاحتياطي
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"

    # Check prerequisites - التحقق من المتطلبات
    check_container

    # Get database info - الحصول على معلومات قاعدة البيانات
    local db_size=$(get_db_size)
    info_message "Database size: ${db_size}"
}

# Perform pg_dump backup - تنفيذ النسخ الاحتياطي باستخدام pg_dump
perform_dump() {
    info_message "Starting pg_dump backup..."

    local dump_file="${BACKUP_DIR}/sahool_${BACKUP_DATE}.dump"
    local start_time=$(date +%s)

    # Perform backup - تنفيذ النسخ الاحتياطي
    if docker exec "${POSTGRES_CONTAINER}" pg_dump \
        -U "${DB_USER}" \
        -F c \
        -b \
        -v \
        -f "/tmp/backup.dump" \
        "${DB_NAME}" >> "${LOG_FILE}" 2>&1; then

        # Copy from container - نسخ من الحاوية
        docker cp "${POSTGRES_CONTAINER}:/tmp/backup.dump" "${dump_file}"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/backup.dump

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local dump_size=$(stat -f%z "${dump_file}" 2>/dev/null || stat -c%s "${dump_file}")

        success_message "Dump completed in ${duration} seconds"
        info_message "Dump size: $(format_bytes ${dump_size})"

        echo "${dump_file}"
    else
        error_exit "pg_dump failed"
    fi
}

# Perform SQL backup - تنفيذ النسخ الاحتياطي بصيغة SQL
perform_sql_dump() {
    info_message "Creating SQL dump for portability..."

    local sql_file="${BACKUP_DIR}/sahool_${BACKUP_DATE}.sql"

    if docker exec "${POSTGRES_CONTAINER}" pg_dump \
        -U "${DB_USER}" \
        --no-owner \
        --no-privileges \
        -f "/tmp/backup.sql" \
        "${DB_NAME}" >> "${LOG_FILE}" 2>&1; then

        docker cp "${POSTGRES_CONTAINER}:/tmp/backup.sql" "${sql_file}"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/backup.sql

        success_message "SQL dump created"
        echo "${sql_file}"
    else
        warning_message "SQL dump failed (non-critical)"
        echo ""
    fi
}

# Backup database schema - النسخ الاحتياطي لمخطط قاعدة البيانات
backup_schema() {
    info_message "Backing up database schema..."

    local schema_file="${BACKUP_DIR}/schema_${BACKUP_DATE}.sql"

    if docker exec "${POSTGRES_CONTAINER}" pg_dump \
        -U "${DB_USER}" \
        --schema-only \
        --no-owner \
        -f "/tmp/schema.sql" \
        "${DB_NAME}" >> "${LOG_FILE}" 2>&1; then

        docker cp "${POSTGRES_CONTAINER}:/tmp/schema.sql" "${schema_file}"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/schema.sql

        success_message "Schema backup completed"
    else
        warning_message "Schema backup failed (non-critical)"
    fi
}

# Backup globals - النسخ الاحتياطي للإعدادات العامة
backup_globals() {
    info_message "Backing up PostgreSQL globals (roles, tablespaces)..."

    local globals_file="${BACKUP_DIR}/globals_${BACKUP_DATE}.sql"

    if docker exec "${POSTGRES_CONTAINER}" pg_dumpall \
        -U "${DB_USER}" \
        --globals-only \
        -f "/tmp/globals.sql" >> "${LOG_FILE}" 2>&1; then

        docker cp "${POSTGRES_CONTAINER}:/tmp/globals.sql" "${globals_file}"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/globals.sql

        success_message "Globals backup completed"
    else
        warning_message "Globals backup failed (non-critical)"
    fi
}

# Compress backup - ضغط النسخة الاحتياطية
compress_backup() {
    local file=$1

    if [ "$COMPRESSION" = "none" ]; then
        echo "${file}"
        return
    fi

    info_message "Compressing backup with ${COMPRESSION}..."
    local start_time=$(date +%s)

    case "$COMPRESSION" in
        gzip)
            gzip -9 "${file}"
            local compressed_file="${file}.gz"
            ;;
        zstd)
            if command_exists zstd; then
                zstd -19 --rm "${file}"
                local compressed_file="${file}.zst"
            else
                warning_message "zstd not found, using gzip instead"
                gzip -9 "${file}"
                local compressed_file="${file}.gz"
            fi
            ;;
        *)
            warning_message "Unknown compression type, skipping compression"
            local compressed_file="${file}"
            ;;
    esac

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [ -f "${compressed_file}" ]; then
        local compressed_size=$(stat -f%z "${compressed_file}" 2>/dev/null || stat -c%s "${compressed_file}")
        success_message "Compression completed in ${duration} seconds"
        info_message "Compressed size: $(format_bytes ${compressed_size})"
        echo "${compressed_file}"
    else
        error_exit "Compression failed"
    fi
}

# Encrypt backup - تشفير النسخة الاحتياطية
encrypt_backup() {
    local file=$1

    if [ "$ENCRYPTION_ENABLED" != "true" ]; then
        echo "${file}"
        return
    fi

    if [ -z "$ENCRYPTION_KEY" ]; then
        warning_message "Encryption enabled but no key provided, skipping"
        echo "${file}"
        return
    fi

    info_message "Encrypting backup..."

    local encrypted_file="${file}.enc"

    if openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in "${file}" \
        -out "${encrypted_file}" \
        -k "${ENCRYPTION_KEY}"; then

        rm -f "${file}"
        success_message "Encryption completed"
        echo "${encrypted_file}"
    else
        error_exit "Encryption failed"
    fi
}

# Upload to S3/MinIO - رفع إلى S3/MinIO
upload_to_s3() {
    local file=$1

    if [ "$S3_ENABLED" != "true" ]; then
        return
    fi

    info_message "Uploading to S3/MinIO..."

    # Configure AWS CLI
    export AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY}"
    export AWS_SECRET_ACCESS_KEY="${S3_SECRET_KEY}"
    export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

    local s3_path="s3://${S3_BUCKET}/postgres/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

    if command_exists aws; then
        if aws s3 cp "${file}" "${s3_path}" --endpoint-url "${S3_ENDPOINT}" >> "${LOG_FILE}" 2>&1; then
            success_message "Uploaded to S3: ${s3_path}"
        else
            warning_message "S3 upload failed (non-critical)"
        fi
    elif command_exists mc; then
        # Configure MinIO client
        mc alias set backup "${S3_ENDPOINT}" "${S3_ACCESS_KEY}" "${S3_SECRET_KEY}" > /dev/null 2>&1

        local mc_path="backup/${S3_BUCKET}/postgres/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

        if mc cp "${file}" "${mc_path}" >> "${LOG_FILE}" 2>&1; then
            success_message "Uploaded to MinIO: ${mc_path}"
        else
            warning_message "MinIO upload failed (non-critical)"
        fi
    else
        warning_message "Neither aws nor mc command found, skipping S3 upload"
    fi
}

# Create backup metadata - إنشاء البيانات الوصفية
create_metadata() {
    local backup_file=$1

    info_message "Creating backup metadata..."

    local metadata_file="${BACKUP_DIR}/metadata.json"
    local file_size=$(stat -f%z "${backup_file}" 2>/dev/null || stat -c%s "${backup_file}")
    local file_hash=$(sha256sum "${backup_file}" | awk '{print $1}')

    cat > "${metadata_file}" <<EOF
{
    "backup_type": "${BACKUP_TYPE}",
    "backup_date": "${BACKUP_DATE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "database": {
        "name": "${DB_NAME}",
        "user": "${DB_USER}",
        "host": "${POSTGRES_HOST}",
        "port": ${POSTGRES_PORT},
        "version": "$(docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -t -c 'SELECT version();' | xargs)"
    },
    "backup_file": {
        "name": "$(basename ${backup_file})",
        "size": ${file_size},
        "size_human": "$(format_bytes ${file_size})",
        "sha256": "${file_hash}",
        "compression": "${COMPRESSION}",
        "encrypted": ${ENCRYPTION_ENABLED}
    },
    "system": {
        "hostname": "$(hostname)",
        "platform": "$(uname -s)",
        "script_version": "1.0.0"
    }
}
EOF

    success_message "Metadata created"
}

# Verify backup - التحقق من النسخة الاحتياطية
verify_backup() {
    local backup_file=$1

    info_message "Verifying backup integrity..."

    # Check file exists and is not empty
    if [ ! -f "${backup_file}" ]; then
        error_exit "Backup file not found: ${backup_file}"
    fi

    local file_size=$(stat -f%z "${backup_file}" 2>/dev/null || stat -c%s "${backup_file}")
    if [ "$file_size" -eq 0 ]; then
        error_exit "Backup file is empty"
    fi

    # For .dump files, verify with pg_restore --list
    if [[ "${backup_file}" == *.dump ]]; then
        if docker run --rm -v "$(dirname ${backup_file}):/backup" postgres:16-alpine \
            pg_restore --list "/backup/$(basename ${backup_file})" > /dev/null 2>&1; then
            success_message "Backup verification passed"
        else
            error_exit "Backup verification failed"
        fi
    else
        success_message "Basic file checks passed"
    fi
}

# Cleanup old backups - تنظيف النسخ القديمة
cleanup_old_backups() {
    info_message "Cleaning up old backups..."

    local retention_days=${RETENTION_DAYS[$BACKUP_TYPE]}
    local backup_type_dir="${BACKUP_BASE_DIR}/postgres/${BACKUP_TYPE}"

    if [ -d "${backup_type_dir}" ]; then
        local deleted_count=0
        while IFS= read -r old_backup; do
            rm -rf "${old_backup}"
            ((deleted_count++))
        done < <(find "${backup_type_dir}" -maxdepth 1 -type d -mtime +${retention_days} -not -path "${backup_type_dir}")

        if [ $deleted_count -gt 0 ]; then
            success_message "Deleted ${deleted_count} old backup(s)"
        else
            info_message "No old backups to delete"
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local overall_start_time=$(date +%s)

    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  SAHOOL Platform - PostgreSQL Backup"
    print_message "${BLUE}" "  نظام النسخ الاحتياطي لقاعدة بيانات PostgreSQL"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Initialize
    init_backup

    # Perform backups
    local dump_file=$(perform_dump)

    # Additional backups for weekly/monthly
    if [ "$BACKUP_TYPE" = "weekly" ] || [ "$BACKUP_TYPE" = "monthly" ]; then
        perform_sql_dump
        backup_schema
        backup_globals
    fi

    # Compress
    dump_file=$(compress_backup "${dump_file}")

    # Encrypt
    dump_file=$(encrypt_backup "${dump_file}")

    # Verify
    verify_backup "${dump_file}"

    # Create metadata
    create_metadata "${dump_file}"

    # Upload to S3
    upload_to_s3 "${dump_file}"

    # Cleanup old backups
    cleanup_old_backups

    # Calculate total time
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "PostgreSQL backup completed successfully!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "Backup location: ${BACKUP_DIR}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    # Send success notification
    send_notification "success" "PostgreSQL backup completed in ${minutes}m ${seconds}s"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
