#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - MinIO/S3 Backup Script
# نظام النسخ الاحتياطي لـ MinIO/S3
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Complete backup solution for MinIO/S3 object storage
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
BACKUP_DIR="${BACKUP_BASE_DIR}/minio/${BACKUP_TYPE}/${BACKUP_DATE}"

# Retention policy (days) - سياسة الاحتفاظ بالنسخ
declare -A RETENTION_DAYS=(
    ["daily"]=30
    ["weekly"]=90
    ["monthly"]=365
    ["manual"]=30
)

# MinIO configuration - إعدادات MinIO
MINIO_ALIAS="${MINIO_ALIAS:-primary}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://minio:9000}"
MINIO_ACCESS_KEY="${MINIO_ROOT_USER:-${MINIO_ACCESS_KEY}}"
MINIO_SECRET_KEY="${MINIO_ROOT_PASSWORD:-${MINIO_SECRET_KEY}}"

# Backup destination - وجهة النسخ الاحتياطي
BACKUP_MINIO_ALIAS="${BACKUP_MINIO_ALIAS:-backup}"
BACKUP_MINIO_ENDPOINT="${BACKUP_MINIO_ENDPOINT:-}"
BACKUP_MINIO_ACCESS_KEY="${BACKUP_MINIO_ACCESS_KEY:-}"
BACKUP_MINIO_SECRET_KEY="${BACKUP_MINIO_SECRET_KEY:-}"

# AWS S3 configuration (optional) - إعدادات AWS S3 (اختياري)
AWS_S3_ENABLED="${AWS_S3_BACKUP_ENABLED:-false}"
AWS_S3_BUCKET="${AWS_S3_BUCKET:-sahool-backups}"
AWS_S3_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"

# Buckets to backup - الحاويات المراد نسخها احتياطيًا
BUCKETS_TO_BACKUP="${MINIO_BUCKETS:-uploads,documents,images,backups}"

# Backup options - خيارات النسخ الاحتياطي
BACKUP_METHOD="${BACKUP_METHOD:-mirror}"  # mirror, snapshot, incremental
VERIFY_BACKUP="${VERIFY_BACKUP:-true}"
CREATE_ARCHIVE="${CREATE_ARCHIVE:-false}"
COMPRESSION="${BACKUP_COMPRESSION:-gzip}"
ENCRYPTION_ENABLED="${BACKUP_ENCRYPTION_ENABLED:-false}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# Notification configuration - إعدادات الإشعارات
SLACK_NOTIFICATIONS="${SLACK_NOTIFICATIONS_ENABLED:-false}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# Logging - السجلات
LOG_DIR="${BACKUP_BASE_DIR}/logs"
LOG_FILE="${LOG_DIR}/minio_${BACKUP_TYPE}_$(date +%Y%m%d).log"

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
    send_notification "failure" "MinIO backup failed: $1"
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

# Check if mc command is available - التحقق من توفر أمر mc
check_mc_command() {
    if ! command_exists mc; then
        error_exit "MinIO client (mc) is not installed. Please install it first."
    fi
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
        printf "%.2f GB" "$(echo "scale=2; $bytes / 1073741824" | bc)"
    fi
}

# Send notification - إرسال إشعار
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
        "title": "${emoji} MinIO Backup - ${BACKUP_TYPE}",
        "text": "${message}",
        "footer": "SAHOOL Backup System",
        "ts": $(date +%s)
    }]
}
EOF
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# MinIO Functions - دوال MinIO
# ─────────────────────────────────────────────────────────────────────────────

# Configure MinIO aliases - إعداد أسماء مستعارة لـ MinIO
configure_minio_aliases() {
    info_message "Configuring MinIO aliases..."

    # Configure primary MinIO
    if ! mc alias set "${MINIO_ALIAS}" "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" >> "${LOG_FILE}" 2>&1; then
        error_exit "Failed to configure primary MinIO alias"
    fi

    # Configure backup MinIO (if different)
    if [ -n "$BACKUP_MINIO_ENDPOINT" ]; then
        if ! mc alias set "${BACKUP_MINIO_ALIAS}" "${BACKUP_MINIO_ENDPOINT}" "${BACKUP_MINIO_ACCESS_KEY}" "${BACKUP_MINIO_SECRET_KEY}" >> "${LOG_FILE}" 2>&1; then
            warning_message "Failed to configure backup MinIO alias"
        fi
    fi

    success_message "MinIO aliases configured"
}

# List buckets - عرض الحاويات
list_buckets() {
    local alias=$1
    mc ls "${alias}" 2>/dev/null | awk '{print $NF}' | sed 's|/$||'
}

# Get bucket size - الحصول على حجم الحاوية
get_bucket_size() {
    local alias=$1
    local bucket=$2
    mc du "${alias}/${bucket}" 2>/dev/null | awk '{print $1}'
}

# Get bucket object count - الحصول على عدد الكائنات في الحاوية
get_bucket_object_count() {
    local alias=$1
    local bucket=$2
    mc ls "${alias}/${bucket}" --recursive 2>/dev/null | wc -l
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup Functions - دوال النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

# Initialize backup - تهيئة النسخ الاحتياطي
init_backup() {
    info_message "Initializing MinIO backup..."
    info_message "Backup type: ${BACKUP_TYPE}"
    info_message "Backup method: ${BACKUP_METHOD}"

    # Create backup directories - إنشاء مجلدات النسخ الاحتياطي
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"

    # Check prerequisites - التحقق من المتطلبات
    check_mc_command

    # Configure aliases - إعداد الأسماء المستعارة
    configure_minio_aliases

    # Get MinIO info - الحصول على معلومات MinIO
    local total_buckets=$(list_buckets "${MINIO_ALIAS}" | wc -l)
    info_message "Total buckets: ${total_buckets}"
}

# Backup bucket - النسخ الاحتياطي للحاوية
backup_bucket() {
    local bucket=$1
    local start_time=$(date +%s)

    info_message "Backing up bucket: ${bucket}"

    # Get bucket info - الحصول على معلومات الحاوية
    local object_count=$(get_bucket_object_count "${MINIO_ALIAS}" "${bucket}")
    local bucket_size=$(get_bucket_size "${MINIO_ALIAS}" "${bucket}")

    info_message "  Objects: ${object_count}"
    info_message "  Size: $(format_bytes ${bucket_size})"

    local success=false

    case "$BACKUP_METHOD" in
        mirror)
            # Mirror backup - نسخ متطابق
            if backup_bucket_mirror "${bucket}"; then
                success=true
            fi
            ;;
        snapshot)
            # Snapshot backup - نسخة لقطة
            if backup_bucket_snapshot "${bucket}"; then
                success=true
            fi
            ;;
        incremental)
            # Incremental backup - نسخ متزايد
            if backup_bucket_incremental "${bucket}"; then
                success=true
            fi
            ;;
        *)
            error_exit "Unknown backup method: ${BACKUP_METHOD}"
            ;;
    esac

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [ "$success" = true ]; then
        success_message "Bucket ${bucket} backed up in ${duration} seconds"
    else
        warning_message "Bucket ${bucket} backup had issues"
    fi
}

# Backup bucket using mirror - النسخ الاحتياطي باستخدام النسخ المتطابق
backup_bucket_mirror() {
    local bucket=$1
    local dest_path="${BACKUP_DIR}/${bucket}"

    mkdir -p "${dest_path}"

    # Use mc mirror for exact copy
    if mc mirror --overwrite \
        "${MINIO_ALIAS}/${bucket}" \
        "${dest_path}" >> "${LOG_FILE}" 2>&1; then
        return 0
    else
        return 1
    fi
}

# Backup bucket using snapshot - النسخ الاحتياطي باستخدام لقطة
backup_bucket_snapshot() {
    local bucket=$1
    local snapshot_name="${bucket}_${BACKUP_DATE}"
    local dest_path="${BACKUP_DIR}/${snapshot_name}"

    mkdir -p "${dest_path}"

    # Copy all objects to snapshot directory
    if mc mirror \
        "${MINIO_ALIAS}/${bucket}" \
        "${dest_path}" >> "${LOG_FILE}" 2>&1; then

        # Create snapshot metadata
        cat > "${dest_path}/.snapshot.json" <<EOF
{
    "bucket": "${bucket}",
    "snapshot_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_type": "${BACKUP_TYPE}",
    "object_count": $(get_bucket_object_count "${MINIO_ALIAS}" "${bucket}"),
    "size_bytes": $(get_bucket_size "${MINIO_ALIAS}" "${bucket}")
}
EOF
        return 0
    else
        return 1
    fi
}

# Backup bucket using incremental - النسخ الاحتياطي المتزايد
backup_bucket_incremental() {
    local bucket=$1
    local dest_path="${BACKUP_DIR}/${bucket}"

    mkdir -p "${dest_path}"

    # Mirror only files newer than last backup
    if mc mirror --newer-than 24h \
        "${MINIO_ALIAS}/${bucket}" \
        "${dest_path}" >> "${LOG_FILE}" 2>&1; then
        return 0
    else
        return 1
    fi
}

# Backup all buckets - النسخ الاحتياطي لجميع الحاويات
backup_all_buckets() {
    info_message "Starting backup of all buckets..."

    # Convert comma-separated list to array
    IFS=',' read -ra BUCKETS <<< "$BUCKETS_TO_BACKUP"

    local total_buckets=${#BUCKETS[@]}
    local current=0
    local successful=0
    local failed=0

    for bucket in "${BUCKETS[@]}"; do
        bucket=$(echo "$bucket" | xargs)  # Trim whitespace
        ((current++))

        info_message "Processing bucket ${current}/${total_buckets}: ${bucket}"

        # Check if bucket exists
        if ! mc ls "${MINIO_ALIAS}/${bucket}" > /dev/null 2>&1; then
            warning_message "Bucket '${bucket}' does not exist, skipping"
            ((failed++))
            continue
        fi

        # Backup bucket
        if backup_bucket "${bucket}"; then
            ((successful++))
        else
            ((failed++))
        fi
    done

    info_message "Backup summary: ${successful} successful, ${failed} failed out of ${total_buckets} total"

    if [ $failed -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

# Create tar archive - إنشاء أرشيف tar
create_tar_archive() {
    if [ "$CREATE_ARCHIVE" != "true" ]; then
        return
    fi

    info_message "Creating tar archive..."

    local archive_file="${BACKUP_DIR}.tar.gz"

    if tar -czf "${archive_file}" -C "$(dirname ${BACKUP_DIR})" "$(basename ${BACKUP_DIR})" >> "${LOG_FILE}" 2>&1; then
        local archive_size=$(stat -f%z "${archive_file}" 2>/dev/null || stat -c%s "${archive_file}")
        success_message "Archive created: $(basename ${archive_file}) ($(format_bytes ${archive_size}))"

        # Optionally remove uncompressed backup
        if [ "${REMOVE_UNCOMPRESSED:-false}" = "true" ]; then
            rm -rf "${BACKUP_DIR}"
            info_message "Removed uncompressed backup directory"
        fi
    else
        warning_message "Failed to create tar archive"
    fi
}

# Encrypt backup archive - تشفير أرشيف النسخة الاحتياطية
encrypt_backup_archive() {
    if [ "$ENCRYPTION_ENABLED" != "true" ]; then
        return
    fi

    if [ -z "$ENCRYPTION_KEY" ]; then
        warning_message "Encryption enabled but no key provided, skipping"
        return
    fi

    # Find archive file
    local archive_file="${BACKUP_DIR}.tar.gz"
    if [ ! -f "$archive_file" ]; then
        warning_message "No archive file found to encrypt"
        return
    fi

    info_message "Encrypting backup archive with AES-256..."

    local encrypted_file="${archive_file}.enc"

    if openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in "${archive_file}" \
        -out "${encrypted_file}" \
        -k "${ENCRYPTION_KEY}"; then

        # Remove unencrypted archive
        rm -f "${archive_file}"

        local encrypted_size=$(stat -f%z "${encrypted_file}" 2>/dev/null || stat -c%s "${encrypted_file}")
        success_message "Encryption completed ($(format_bytes ${encrypted_size}))"
    else
        error_exit "Encryption failed"
    fi
}

# Upload to AWS S3 - رفع إلى AWS S3
upload_to_aws_s3() {
    if [ "$AWS_S3_ENABLED" != "true" ]; then
        return
    fi

    info_message "Uploading to AWS S3..."

    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_DEFAULT_REGION="${AWS_S3_REGION}"

    local s3_path="s3://${AWS_S3_BUCKET}/minio/${BACKUP_TYPE}/${BACKUP_DATE}/"

    if command_exists aws; then
        if aws s3 sync "${BACKUP_DIR}" "${s3_path}" >> "${LOG_FILE}" 2>&1; then
            success_message "Uploaded to AWS S3: ${s3_path}"
        else
            warning_message "AWS S3 upload failed (non-critical)"
        fi
    else
        warning_message "AWS CLI not found, skipping S3 upload"
    fi
}

# Upload to backup MinIO - رفع إلى MinIO الاحتياطي
upload_to_backup_minio() {
    if [ -z "$BACKUP_MINIO_ENDPOINT" ]; then
        return
    fi

    info_message "Uploading to backup MinIO..."

    # Upload each bucket to backup MinIO
    IFS=',' read -ra BUCKETS <<< "$BUCKETS_TO_BACKUP"

    for bucket in "${BUCKETS[@]}"; do
        bucket=$(echo "$bucket" | xargs)

        local source_path="${BACKUP_DIR}/${bucket}"
        if [ ! -d "$source_path" ]; then
            continue
        fi

        local dest_bucket="${bucket}-backup-${BACKUP_DATE}"

        # Create bucket in backup MinIO
        mc mb "${BACKUP_MINIO_ALIAS}/${dest_bucket}" >> "${LOG_FILE}" 2>&1 || true

        # Mirror to backup MinIO
        if mc mirror "${source_path}" "${BACKUP_MINIO_ALIAS}/${dest_bucket}" >> "${LOG_FILE}" 2>&1; then
            success_message "Uploaded ${bucket} to backup MinIO"
        else
            warning_message "Failed to upload ${bucket} to backup MinIO"
        fi
    done
}

# Verify backup - التحقق من النسخة الاحتياطية
verify_backup() {
    if [ "$VERIFY_BACKUP" != "true" ]; then
        return
    fi

    info_message "Verifying backup integrity..."

    local verified=0
    local failed=0

    IFS=',' read -ra BUCKETS <<< "$BUCKETS_TO_BACKUP"

    for bucket in "${BUCKETS[@]}"; do
        bucket=$(echo "$bucket" | xargs)

        local backup_path="${BACKUP_DIR}/${bucket}"
        if [ ! -d "$backup_path" ]; then
            continue
        fi

        # Count objects in backup
        local backup_object_count=$(find "$backup_path" -type f | wc -l)

        # Count objects in source (allow some margin for active writes)
        local source_object_count=$(get_bucket_object_count "${MINIO_ALIAS}" "${bucket}")

        if [ $backup_object_count -ge $((source_object_count - 10)) ]; then
            ((verified++))
        else
            warning_message "Bucket ${bucket} verification failed: expected ~${source_object_count}, got ${backup_object_count}"
            ((failed++))
        fi
    done

    if [ $failed -eq 0 ]; then
        success_message "All backups verified successfully"
    else
        warning_message "Some backups failed verification"
    fi
}

# Create backup metadata - إنشاء البيانات الوصفية
create_metadata() {
    info_message "Creating backup metadata..."

    local metadata_file="${BACKUP_DIR}/metadata.json"
    local total_size=0

    # Calculate total size
    if [ -d "${BACKUP_DIR}" ]; then
        total_size=$(du -sb "${BACKUP_DIR}" 2>/dev/null | awk '{print $1}')
    fi

    cat > "${metadata_file}" <<EOF
{
    "backup_type": "${BACKUP_TYPE}",
    "backup_date": "${BACKUP_DATE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "minio": {
        "endpoint": "${MINIO_ENDPOINT}",
        "buckets": "${BUCKETS_TO_BACKUP}"
    },
    "backup": {
        "method": "${BACKUP_METHOD}",
        "total_size_bytes": ${total_size},
        "total_size_human": "$(format_bytes ${total_size})"
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

# Cleanup old backups - تنظيف النسخ القديمة
cleanup_old_backups() {
    info_message "Cleaning up old backups..."

    local retention_days=${RETENTION_DAYS[$BACKUP_TYPE]}
    local backup_type_dir="${BACKUP_BASE_DIR}/minio/${BACKUP_TYPE}"

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
    print_message "${BLUE}" "  SAHOOL Platform - MinIO/S3 Backup"
    print_message "${BLUE}" "  نظام النسخ الاحتياطي لـ MinIO/S3"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Initialize
    init_backup

    # Backup all buckets
    if ! backup_all_buckets; then
        warning_message "Some bucket backups failed"
    fi

    # Create archive
    create_tar_archive

    # Encrypt archive
    encrypt_backup_archive

    # Verify backup
    verify_backup

    # Create metadata
    create_metadata

    # Upload to external storage
    upload_to_aws_s3
    upload_to_backup_minio

    # Cleanup old backups
    cleanup_old_backups

    # Calculate total time
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    # Calculate total backup size
    local total_size=$(du -sb "${BACKUP_DIR}" 2>/dev/null | awk '{print $1}')

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "MinIO backup completed successfully!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "Total size: $(format_bytes ${total_size})"
    info_message "Backup location: ${BACKUP_DIR}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    # Send success notification
    send_notification "success" "MinIO backup completed in ${minutes}m ${seconds}s ($(format_bytes ${total_size}))"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
