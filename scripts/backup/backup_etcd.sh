#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - ETCD Backup Script
# نظام النسخ الاحتياطي لـ ETCD
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Complete backup solution for ETCD configuration storage
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
BACKUP_DIR="${BACKUP_BASE_DIR}/etcd/${BACKUP_TYPE}/${BACKUP_DATE}"

# Retention policy (days) - سياسة الاحتفاظ بالنسخ
declare -A RETENTION_DAYS=(
    ["daily"]=7
    ["weekly"]=28
    ["monthly"]=90
    ["manual"]=30
)

# ETCD configuration - إعدادات ETCD
ETCD_CONTAINER="${ETCD_CONTAINER:-sahool-etcd}"
ETCD_ENDPOINTS="${ETCD_ENDPOINTS:-127.0.0.1:2379}"
ETCD_USER="${ETCD_USER:-root}"
ETCD_PASSWORD="${ETCD_PASSWORD:-}"

# TLS configuration (if enabled) - إعدادات TLS
ETCD_TLS_ENABLED="${ETCD_TLS_ENABLED:-false}"
ETCD_CACERT="${ETCD_CACERT:-}"
ETCD_CERT="${ETCD_CERT:-}"
ETCD_KEY="${ETCD_KEY:-}"

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
LOG_FILE="${LOG_DIR}/etcd_${BACKUP_TYPE}_$(date +%Y%m%d).log"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────

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
    send_notification "failure" "ETCD backup failed: $1"
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
    if ! docker ps --format '{{.Names}}' | grep -q "^${ETCD_CONTAINER}$"; then
        error_exit "ETCD container '${ETCD_CONTAINER}' is not running"
    fi
}

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
        "title": "${emoji} ETCD Backup - ${BACKUP_TYPE}",
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

init_backup() {
    info_message "Initializing ETCD backup..."
    info_message "Backup type: ${BACKUP_TYPE}"

    # Create backup directories
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"

    # Check prerequisites
    check_container

    # Get ETCD info
    local etcd_version=$(docker exec "${ETCD_CONTAINER}" etcdctl version 2>&1 | grep 'etcdctl version' | awk '{print $3}' || echo "unknown")
    info_message "ETCD version: ${etcd_version}"
}

# Perform ETCD snapshot backup - إجراء نسخة احتياطية من ETCD
perform_etcd_snapshot() {
    info_message "Creating ETCD snapshot..."

    local snapshot_file="${BACKUP_DIR}/etcd_snapshot_${BACKUP_DATE}.db"
    local start_time=$(date +%s)

    # Build etcdctl command
    local etcd_cmd="etcdctl"

    # Add authentication if provided
    if [ -n "$ETCD_USER" ] && [ -n "$ETCD_PASSWORD" ]; then
        etcd_cmd="$etcd_cmd --user=${ETCD_USER}:${ETCD_PASSWORD}"
    fi

    # Add TLS options if enabled
    if [ "$ETCD_TLS_ENABLED" = "true" ]; then
        if [ -n "$ETCD_CACERT" ] && [ -n "$ETCD_CERT" ] && [ -n "$ETCD_KEY" ]; then
            etcd_cmd="$etcd_cmd --cacert=${ETCD_CACERT} --cert=${ETCD_CERT} --key=${ETCD_KEY}"
        fi
    fi

    # Add endpoints
    etcd_cmd="$etcd_cmd --endpoints=${ETCD_ENDPOINTS}"

    # Create snapshot
    if docker exec "${ETCD_CONTAINER}" ${etcd_cmd} snapshot save /tmp/etcd_snapshot.db >> "${LOG_FILE}" 2>&1; then

        # Copy snapshot from container
        docker cp "${ETCD_CONTAINER}:/tmp/etcd_snapshot.db" "${snapshot_file}"
        docker exec "${ETCD_CONTAINER}" rm -f /tmp/etcd_snapshot.db

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local file_size=$(stat -f%z "${snapshot_file}" 2>/dev/null || stat -c%s "${snapshot_file}")

        success_message "ETCD snapshot completed in ${duration} seconds"
        info_message "Snapshot size: $(format_bytes ${file_size})"

        echo "${snapshot_file}"
    else
        error_exit "ETCD snapshot creation failed"
    fi
}

# Verify ETCD snapshot - التحقق من نسخة ETCD
verify_snapshot() {
    local snapshot_file=$1

    info_message "Verifying ETCD snapshot..."

    # Copy snapshot to container for verification
    docker cp "${snapshot_file}" "${ETCD_CONTAINER}:/tmp/verify_snapshot.db"

    # Build etcdctl command
    local etcd_cmd="etcdctl"

    if [ -n "$ETCD_USER" ] && [ -n "$ETCD_PASSWORD" ]; then
        etcd_cmd="$etcd_cmd --user=${ETCD_USER}:${ETCD_PASSWORD}"
    fi

    if [ "$ETCD_TLS_ENABLED" = "true" ]; then
        if [ -n "$ETCD_CACERT" ] && [ -n "$ETCD_CERT" ] && [ -n "$ETCD_KEY" ]; then
            etcd_cmd="$etcd_cmd --cacert=${ETCD_CACERT} --cert=${ETCD_CERT} --key=${ETCD_KEY}"
        fi
    fi

    # Verify snapshot status
    if docker exec "${ETCD_CONTAINER}" ${etcd_cmd} snapshot status /tmp/verify_snapshot.db -w table >> "${LOG_FILE}" 2>&1; then
        success_message "ETCD snapshot verification passed"
        docker exec "${ETCD_CONTAINER}" rm -f /tmp/verify_snapshot.db
        return 0
    else
        error_exit "ETCD snapshot verification failed"
    fi
}

# Export ETCD keys as JSON - تصدير مفاتيح ETCD بصيغة JSON
export_etcd_keys() {
    info_message "Exporting ETCD keys to JSON..."

    local json_file="${BACKUP_DIR}/etcd_keys_${BACKUP_DATE}.json"

    # Build etcdctl command
    local etcd_cmd="etcdctl"

    if [ -n "$ETCD_USER" ] && [ -n "$ETCD_PASSWORD" ]; then
        etcd_cmd="$etcd_cmd --user=${ETCD_USER}:${ETCD_PASSWORD}"
    fi

    if [ "$ETCD_TLS_ENABLED" = "true" ]; then
        if [ -n "$ETCD_CACERT" ] && [ -n "$ETCD_CERT" ] && [ -n "$ETCD_KEY" ]; then
            etcd_cmd="$etcd_cmd --cacert=${ETCD_CACERT} --cert=${ETCD_CERT} --key=${ETCD_KEY}"
        fi
    fi

    etcd_cmd="$etcd_cmd --endpoints=${ETCD_ENDPOINTS}"

    # Get all keys
    local keys=$(docker exec "${ETCD_CONTAINER}" ${etcd_cmd} get "" --prefix --keys-only 2>/dev/null || echo "")

    if [ -n "$keys" ]; then
        {
            echo "{"
            echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
            echo "  \"etcd_endpoints\": \"${ETCD_ENDPOINTS}\","
            echo "  \"data\": {"

            local first=true
            while IFS= read -r key; do
                [ -z "$key" ] && continue

                if [ "$first" = false ]; then
                    echo ","
                fi
                first=false

                local value=$(docker exec "${ETCD_CONTAINER}" ${etcd_cmd} get "$key" --print-value-only 2>/dev/null | sed 's/"/\\"/g')
                echo -n "    \"${key}\": \"${value}\""
            done <<< "$keys"

            echo ""
            echo "  }"
            echo "}"
        } > "${json_file}"

        success_message "Exported ETCD keys to JSON"
        echo "${json_file}"
    else
        info_message "No ETCD keys to export"
        echo ""
    fi
}

# Compress backup - ضغط النسخة الاحتياطية
compress_backup() {
    local file=$1

    [ ! -f "$file" ] && return

    if [ "$COMPRESSION" = "none" ]; then
        echo "${file}"
        return
    fi

    info_message "Compressing $(basename ${file})..."

    case "$COMPRESSION" in
        gzip)
            gzip -9 "${file}"
            echo "${file}.gz"
            ;;
        zstd)
            if command_exists zstd; then
                zstd -19 --rm "${file}"
                echo "${file}.zst"
            else
                gzip -9 "${file}"
                echo "${file}.gz"
            fi
            ;;
        *)
            echo "${file}"
            ;;
    esac
}

# Encrypt backup - تشفير النسخة الاحتياطية
encrypt_backup() {
    local file=$1

    [ ! -f "$file" ] && return

    if [ "$ENCRYPTION_ENABLED" != "true" ] || [ -z "$ENCRYPTION_KEY" ]; then
        echo "${file}"
        return
    fi

    info_message "Encrypting $(basename ${file})..."

    local encrypted_file="${file}.enc"

    if openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in "${file}" \
        -out "${encrypted_file}" \
        -k "${ENCRYPTION_KEY}"; then

        rm -f "${file}"
        echo "${encrypted_file}"
    else
        warning_message "Encryption failed for $(basename ${file})"
        echo "${file}"
    fi
}

# Upload to S3/MinIO - رفع إلى S3/MinIO
upload_to_s3() {
    local file=$1

    [ ! -f "$file" ] || [ "$S3_ENABLED" != "true" ] && return

    info_message "Uploading $(basename ${file}) to S3/MinIO..."

    export AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY}"
    export AWS_SECRET_ACCESS_KEY="${S3_SECRET_KEY}"
    export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

    local s3_path="s3://${S3_BUCKET}/etcd/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

    if command_exists mc; then
        mc alias set backup "${S3_ENDPOINT}" "${S3_ACCESS_KEY}" "${S3_SECRET_KEY}" > /dev/null 2>&1
        local mc_path="backup/${S3_BUCKET}/etcd/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

        if mc cp "${file}" "${mc_path}" >> "${LOG_FILE}" 2>&1; then
            success_message "Uploaded to MinIO"
        else
            warning_message "Upload failed (non-critical)"
        fi
    fi
}

# Create backup metadata - إنشاء البيانات الوصفية
create_metadata() {
    info_message "Creating backup metadata..."

    local metadata_file="${BACKUP_DIR}/metadata.json"

    # Build etcdctl command for cluster info
    local etcd_cmd="etcdctl --endpoints=${ETCD_ENDPOINTS}"

    if [ -n "$ETCD_USER" ] && [ -n "$ETCD_PASSWORD" ]; then
        etcd_cmd="$etcd_cmd --user=${ETCD_USER}:${ETCD_PASSWORD}"
    fi

    local member_list=$(docker exec "${ETCD_CONTAINER}" ${etcd_cmd} member list -w json 2>/dev/null || echo "{}")

    cat > "${metadata_file}" <<EOF
{
    "backup_type": "${BACKUP_TYPE}",
    "backup_date": "${BACKUP_DATE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "etcd": {
        "version": "$(docker exec ${ETCD_CONTAINER} etcdctl version 2>&1 | grep 'etcdctl version' | awk '{print $3}' || echo 'unknown')",
        "endpoints": "${ETCD_ENDPOINTS}",
        "tls_enabled": ${ETCD_TLS_ENABLED},
        "members": ${member_list}
    },
    "files": {
        "snapshot": $([ -f "${BACKUP_DIR}"/etcd_snapshot*.db* ] && echo "true" || echo "false"),
        "json_export": $([ -f "${BACKUP_DIR}"/etcd_keys*.json* ] && echo "true" || echo "false")
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
    local backup_type_dir="${BACKUP_BASE_DIR}/etcd/${BACKUP_TYPE}"

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
    print_message "${BLUE}" "  SAHOOL Platform - ETCD Backup"
    print_message "${BLUE}" "  نظام النسخ الاحتياطي لـ ETCD"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Initialize
    init_backup

    # Create ETCD snapshot
    local snapshot_file=$(perform_etcd_snapshot)

    # Verify snapshot
    verify_snapshot "${snapshot_file}"

    # Compress
    [ -n "$snapshot_file" ] && snapshot_file=$(compress_backup "$snapshot_file")

    # Encrypt
    [ -n "$snapshot_file" ] && snapshot_file=$(encrypt_backup "$snapshot_file")

    # Upload to S3
    [ -n "$snapshot_file" ] && upload_to_s3 "$snapshot_file"

    # Export keys to JSON (weekly/monthly only)
    if [ "$BACKUP_TYPE" = "weekly" ] || [ "$BACKUP_TYPE" = "monthly" ]; then
        local json_file=$(export_etcd_keys)
        [ -n "$json_file" ] && json_file=$(compress_backup "$json_file")
        [ -n "$json_file" ] && upload_to_s3 "$json_file"
    fi

    # Create metadata
    create_metadata

    # Cleanup old backups
    cleanup_old_backups

    # Calculate total time
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "ETCD backup completed successfully!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "Backup location: ${BACKUP_DIR}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    send_notification "success" "ETCD backup completed in ${minutes}m ${seconds}s"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
