#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - PostgreSQL WAL Archiving Script (PITR)
# نظام أرشفة سجلات WAL لقاعدة بيانات PostgreSQL (الاستعادة للنقطة الزمنية)
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Point-in-Time Recovery (PITR) via WAL archiving and base backups
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
BACKUP_TYPE="${1:-wal-archive}"  # wal-archive, base-backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
WAL_ARCHIVE_DIR="${BACKUP_BASE_DIR}/postgres/wal_archive"
BASE_BACKUP_DIR="${BACKUP_BASE_DIR}/postgres/base_backups"

# Retention policy (days) - سياسة الاحتفاظ بالنسخ
WAL_RETENTION_DAYS="${WAL_RETENTION_DAYS:-7}"
BASE_BACKUP_RETENTION_DAYS="${BASE_BACKUP_RETENTION_DAYS:-30}"

# Database configuration - إعدادات قاعدة البيانات
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
DB_NAME="${POSTGRES_DB:-sahool}"

# WAL archiving configuration - إعدادات أرشفة WAL
WAL_ARCHIVE_ENABLED="${WAL_ARCHIVE_ENABLED:-true}"
WAL_ARCHIVE_MODE="${WAL_ARCHIVE_MODE:-always}"  # on, always, off
WAL_LEVEL="${WAL_LEVEL:-replica}"  # minimal, replica, logical
MAX_WAL_SENDERS="${MAX_WAL_SENDERS:-3}"

# Backup options - خيارات النسخ الاحتياطي
COMPRESSION="${BACKUP_COMPRESSION:-gzip}"
ENCRYPTION_ENABLED="${BACKUP_ENCRYPTION_ENABLED:-true}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# S3/MinIO configuration - إعدادات S3/MinIO
S3_ENABLED="${S3_BACKUP_ENABLED:-false}"
S3_ENDPOINT="${S3_ENDPOINT:-http://minio:9000}"
S3_BUCKET="${S3_BUCKET:-sahool-backups}"
S3_ACCESS_KEY="${S3_ACCESS_KEY:-${MINIO_ROOT_USER}}"
S3_SECRET_KEY="${S3_SECRET_KEY:-${MINIO_ROOT_PASSWORD}}"

# Notification configuration - إعدادات الإشعارات
SLACK_NOTIFICATIONS="${SLACK_NOTIFICATIONS_ENABLED:-false}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# Logging - السجلات
LOG_DIR="${BACKUP_BASE_DIR}/logs"
LOG_FILE="${LOG_DIR}/postgres_pitr_$(date +%Y%m%d).log"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────

# Print colored message - طباعة رسالة ملونة
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "${LOG_FILE}"
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_FILE}"
}

error_exit() {
    print_message "${RED}" "ERROR: $1"
    send_notification "failure" "PostgreSQL PITR backup failed: $1"
    exit 1
}

success_message() {
    print_message "${GREEN}" "✓ $1"
}

warning_message() {
    print_message "${YELLOW}" "⚠ $1"
}

info_message() {
    print_message "${BLUE}" "ℹ $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
        error_exit "PostgreSQL container '${POSTGRES_CONTAINER}' is not running"
    fi
}

send_notification() {
    local status=$1
    local message=$2

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
        "title": "${emoji} PostgreSQL PITR Backup",
        "text": "${message}",
        "footer": "SAHOOL Backup System",
        "ts": $(date +%s)
    }]
}
EOF
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# PITR Functions - دوال الاستعادة للنقطة الزمنية
# ─────────────────────────────────────────────────────────────────────────────

# Configure PostgreSQL for WAL archiving - إعداد PostgreSQL لأرشفة WAL
configure_wal_archiving() {
    info_message "Configuring PostgreSQL for WAL archiving..."

    # Check current configuration
    local current_wal_level=$(docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -t -c "SHOW wal_level;" | xargs)
    local current_archive_mode=$(docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -t -c "SHOW archive_mode;" | xargs)

    info_message "Current wal_level: ${current_wal_level}"
    info_message "Current archive_mode: ${current_archive_mode}"

    if [ "${current_wal_level}" != "replica" ] || [ "${current_archive_mode}" = "off" ]; then
        warning_message "WAL archiving not properly configured, updating settings..."

        # Update postgresql.conf settings
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "ALTER SYSTEM SET wal_level = '${WAL_LEVEL}';" || true
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "ALTER SYSTEM SET archive_mode = '${WAL_ARCHIVE_MODE}';" || true
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "ALTER SYSTEM SET archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f';" || true
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "ALTER SYSTEM SET max_wal_senders = ${MAX_WAL_SENDERS};" || true
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "ALTER SYSTEM SET wal_keep_size = '1GB';" || true

        warning_message "Configuration updated. PostgreSQL restart required for changes to take effect."
        warning_message "Run: docker restart ${POSTGRES_CONTAINER}"
    else
        success_message "WAL archiving already configured"
    fi

    # Create WAL archive directory in container
    docker exec "${POSTGRES_CONTAINER}" mkdir -p /var/lib/postgresql/wal_archive
    docker exec "${POSTGRES_CONTAINER}" chown postgres:postgres /var/lib/postgresql/wal_archive
}

# Archive WAL files - أرشفة ملفات WAL
archive_wal_files() {
    info_message "Archiving WAL files..."

    # Create WAL archive directory
    mkdir -p "${WAL_ARCHIVE_DIR}"

    # Copy WAL files from container to host
    local wal_count=0

    # Get list of WAL files from container
    local wal_files=$(docker exec "${POSTGRES_CONTAINER}" ls -1 /var/lib/postgresql/wal_archive/ 2>/dev/null || echo "")

    if [ -z "$wal_files" ]; then
        info_message "No WAL files to archive"
        return 0
    fi

    # Copy each WAL file
    while IFS= read -r wal_file; do
        [ -z "$wal_file" ] && continue

        local dest_file="${WAL_ARCHIVE_DIR}/${wal_file}"

        # Skip if already archived
        if [ -f "$dest_file" ]; then
            continue
        fi

        # Copy WAL file
        if docker cp "${POSTGRES_CONTAINER}:/var/lib/postgresql/wal_archive/${wal_file}" "${dest_file}" >> "${LOG_FILE}" 2>&1; then
            ((wal_count++))

            # Compress WAL file
            if [ "$COMPRESSION" = "gzip" ]; then
                gzip -9 "${dest_file}"
            fi

            # Remove from container after successful copy
            docker exec "${POSTGRES_CONTAINER}" rm -f "/var/lib/postgresql/wal_archive/${wal_file}"
        fi
    done <<< "$wal_files"

    if [ $wal_count -gt 0 ]; then
        success_message "Archived ${wal_count} WAL file(s)"
    else
        info_message "No new WAL files to archive"
    fi
}

# Perform base backup using pg_basebackup - إجراء نسخة احتياطية أساسية
perform_base_backup() {
    info_message "Performing base backup with pg_basebackup..."

    local backup_dir="${BASE_BACKUP_DIR}/${BACKUP_DATE}"
    mkdir -p "${backup_dir}"

    local start_time=$(date +%s)

    # Perform pg_basebackup
    if docker exec "${POSTGRES_CONTAINER}" pg_basebackup \
        -U "${DB_USER}" \
        -D "/tmp/base_backup" \
        -Ft \
        -z \
        -Xs \
        -P \
        -v >> "${LOG_FILE}" 2>&1; then

        # Copy base backup from container
        docker cp "${POSTGRES_CONTAINER}:/tmp/base_backup/base.tar.gz" "${backup_dir}/base.tar.gz"
        docker cp "${POSTGRES_CONTAINER}:/tmp/base_backup/pg_wal.tar.gz" "${backup_dir}/pg_wal.tar.gz" 2>/dev/null || true

        # Cleanup container
        docker exec "${POSTGRES_CONTAINER}" rm -rf /tmp/base_backup

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        success_message "Base backup completed in ${duration} seconds"

        # Create metadata
        create_base_backup_metadata "${backup_dir}"

        # Encrypt if enabled
        if [ "$ENCRYPTION_ENABLED" = "true" ] && [ -n "$ENCRYPTION_KEY" ]; then
            encrypt_base_backup "${backup_dir}"
        fi

        # Upload to S3
        if [ "$S3_ENABLED" = "true" ]; then
            upload_base_backup_to_s3 "${backup_dir}"
        fi

        echo "${backup_dir}"
    else
        error_exit "pg_basebackup failed"
    fi
}

# Create base backup metadata - إنشاء البيانات الوصفية للنسخة الأساسية
create_base_backup_metadata() {
    local backup_dir=$1

    info_message "Creating base backup metadata..."

    local metadata_file="${backup_dir}/metadata.json"

    cat > "${metadata_file}" <<EOF
{
    "backup_type": "base_backup",
    "backup_date": "${BACKUP_DATE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "database": {
        "name": "${DB_NAME}",
        "user": "${DB_USER}",
        "host": "${POSTGRES_HOST}",
        "port": ${POSTGRES_PORT},
        "version": "$(docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -t -c 'SELECT version();' | xargs)"
    },
    "pitr": {
        "wal_level": "$(docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -t -c 'SHOW wal_level;' | xargs)",
        "archive_mode": "$(docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -t -c 'SHOW archive_mode;' | xargs)",
        "current_wal_lsn": "$(docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -t -c 'SELECT pg_current_wal_lsn();' | xargs)"
    },
    "backup_files": {
        "base_tar": "$(ls -lh ${backup_dir}/base.tar.gz 2>/dev/null | awk '{print $5}' || echo 'N/A')",
        "wal_tar": "$(ls -lh ${backup_dir}/pg_wal.tar.gz 2>/dev/null | awk '{print $5}' || echo 'N/A')"
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

# Encrypt base backup - تشفير النسخة الأساسية
encrypt_base_backup() {
    local backup_dir=$1

    info_message "Encrypting base backup..."

    for file in "${backup_dir}"/*.tar.gz; do
        [ ! -f "$file" ] && continue

        local encrypted_file="${file}.enc"

        if openssl enc -aes-256-cbc -salt -pbkdf2 \
            -in "${file}" \
            -out "${encrypted_file}" \
            -k "${ENCRYPTION_KEY}"; then

            rm -f "${file}"
            success_message "Encrypted $(basename ${file})"
        else
            warning_message "Failed to encrypt $(basename ${file})"
        fi
    done
}

# Upload base backup to S3 - رفع النسخة الأساسية إلى S3
upload_base_backup_to_s3() {
    local backup_dir=$1

    info_message "Uploading base backup to S3/MinIO..."

    export AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY}"
    export AWS_SECRET_ACCESS_KEY="${S3_SECRET_KEY}"
    export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

    for file in "${backup_dir}"/*; do
        [ ! -f "$file" ] && continue

        local s3_path="s3://${S3_BUCKET}/postgres/base_backups/${BACKUP_DATE}/$(basename ${file})"

        if command_exists mc; then
            mc alias set backup "${S3_ENDPOINT}" "${S3_ACCESS_KEY}" "${S3_SECRET_KEY}" > /dev/null 2>&1
            local mc_path="backup/${S3_BUCKET}/postgres/base_backups/${BACKUP_DATE}/$(basename ${file})"

            if mc cp "${file}" "${mc_path}" >> "${LOG_FILE}" 2>&1; then
                success_message "Uploaded $(basename ${file}) to MinIO"
            else
                warning_message "Failed to upload $(basename ${file})"
            fi
        fi
    done
}

# Cleanup old WAL archives - تنظيف أرشيفات WAL القديمة
cleanup_old_wal_archives() {
    info_message "Cleaning up old WAL archives..."

    if [ -d "${WAL_ARCHIVE_DIR}" ]; then
        local deleted_count=0
        while IFS= read -r old_wal; do
            rm -f "${old_wal}"
            ((deleted_count++))
        done < <(find "${WAL_ARCHIVE_DIR}" -type f -mtime +${WAL_RETENTION_DAYS})

        if [ $deleted_count -gt 0 ]; then
            success_message "Deleted ${deleted_count} old WAL file(s)"
        else
            info_message "No old WAL files to delete"
        fi
    fi
}

# Cleanup old base backups - تنظيف النسخ الأساسية القديمة
cleanup_old_base_backups() {
    info_message "Cleaning up old base backups..."

    if [ -d "${BASE_BACKUP_DIR}" ]; then
        local deleted_count=0
        while IFS= read -r old_backup; do
            rm -rf "${old_backup}"
            ((deleted_count++))
        done < <(find "${BASE_BACKUP_DIR}" -maxdepth 1 -type d -mtime +${BASE_BACKUP_RETENTION_DAYS} -not -path "${BASE_BACKUP_DIR}")

        if [ $deleted_count -gt 0 ]; then
            success_message "Deleted ${deleted_count} old base backup(s)"
        else
            info_message "No old base backups to delete"
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local overall_start_time=$(date +%s)

    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  SAHOOL Platform - PostgreSQL PITR Backup"
    print_message "${BLUE}" "  نظام النسخ الاحتياطي PITR لقاعدة بيانات PostgreSQL"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Create directories
    mkdir -p "${WAL_ARCHIVE_DIR}"
    mkdir -p "${BASE_BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"

    # Check prerequisites
    check_container

    case "$BACKUP_TYPE" in
        wal-archive)
            info_message "Mode: WAL Archive"
            configure_wal_archiving
            archive_wal_files
            cleanup_old_wal_archives
            ;;

        base-backup)
            info_message "Mode: Base Backup"
            configure_wal_archiving
            perform_base_backup
            cleanup_old_base_backups
            ;;

        *)
            error_exit "Invalid backup type: ${BACKUP_TYPE}. Use 'wal-archive' or 'base-backup'"
            ;;
    esac

    # Calculate total time
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "PostgreSQL PITR backup completed successfully!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "WAL Archive: ${WAL_ARCHIVE_DIR}"
    info_message "Base Backups: ${BASE_BACKUP_DIR}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    send_notification "success" "PostgreSQL PITR backup completed in ${minutes}m ${seconds}s"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
