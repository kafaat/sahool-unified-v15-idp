#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Qdrant Vector Database Backup Script
# نظام النسخ الاحتياطي لقاعدة بيانات Qdrant
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Complete backup solution for Qdrant vector database
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
BACKUP_DIR="${BACKUP_BASE_DIR}/qdrant/${BACKUP_TYPE}/${BACKUP_DATE}"

# Retention policy (days) - سياسة الاحتفاظ بالنسخ
declare -A RETENTION_DAYS=(
    ["daily"]=7
    ["weekly"]=28
    ["monthly"]=90
    ["manual"]=30
)

# Qdrant configuration - إعدادات Qdrant
QDRANT_CONTAINER="${QDRANT_CONTAINER:-sahool-qdrant}"
QDRANT_HOST="${QDRANT_HOST:-qdrant}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_GRPC_PORT="${QDRANT_GRPC_PORT:-6334}"
QDRANT_API_KEY="${QDRANT_API_KEY:-}"

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
LOG_FILE="${LOG_DIR}/qdrant_${BACKUP_TYPE}_$(date +%Y%m%d).log"

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
    send_notification "failure" "Qdrant backup failed: $1"
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
    if ! docker ps --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
        error_exit "Qdrant container '${QDRANT_CONTAINER}' is not running"
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
        "title": "${emoji} Qdrant Backup - ${BACKUP_TYPE}",
        "text": "${message}",
        "footer": "SAHOOL Backup System",
        "ts": $(date +%s)
    }]
}
EOF
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Qdrant API Functions - دوال Qdrant API
# ─────────────────────────────────────────────────────────────────────────────

qdrant_api_call() {
    local endpoint=$1
    local method=${2:-GET}

    local url="http://${QDRANT_HOST}:${QDRANT_PORT}${endpoint}"
    local curl_cmd="curl -s -X ${method}"

    if [ -n "$QDRANT_API_KEY" ]; then
        curl_cmd="${curl_cmd} -H 'api-key: ${QDRANT_API_KEY}'"
    fi

    eval "${curl_cmd} ${url}"
}

get_qdrant_info() {
    qdrant_api_call "/"
}

get_collections() {
    qdrant_api_call "/collections"
}

create_snapshot() {
    local collection=$1
    qdrant_api_call "/collections/${collection}/snapshots" "POST"
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup Functions - دوال النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

init_backup() {
    info_message "Initializing Qdrant backup..."
    info_message "Backup type: ${BACKUP_TYPE}"

    # Create backup directories
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"

    # Check prerequisites
    check_container

    # Get Qdrant info
    local qdrant_info=$(get_qdrant_info 2>/dev/null || echo "{}")
    local qdrant_version=$(echo "$qdrant_info" | jq -r '.version // "unknown"' 2>/dev/null || echo "unknown")

    info_message "Qdrant version: ${qdrant_version}"
}

# Backup Qdrant storage directory - نسخ احتياطي لمجلد التخزين
backup_storage_directory() {
    info_message "Backing up Qdrant storage directory..."

    local storage_backup="${BACKUP_DIR}/qdrant_storage_${BACKUP_DATE}.tar"
    local start_time=$(date +%s)

    # Create tar archive of Qdrant storage
    if docker exec "${QDRANT_CONTAINER}" tar -cf /tmp/storage_backup.tar -C /qdrant/storage . >> "${LOG_FILE}" 2>&1; then

        # Copy from container
        docker cp "${QDRANT_CONTAINER}:/tmp/storage_backup.tar" "${storage_backup}"
        docker exec "${QDRANT_CONTAINER}" rm -f /tmp/storage_backup.tar

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local file_size=$(stat -f%z "${storage_backup}" 2>/dev/null || stat -c%s "${storage_backup}")

        success_message "Storage backup completed in ${duration} seconds"
        info_message "Backup size: $(format_bytes ${file_size})"

        echo "${storage_backup}"
    else
        error_exit "Storage directory backup failed"
    fi
}

# Create collection snapshots - إنشاء لقطات للمجموعات
backup_collection_snapshots() {
    info_message "Creating collection snapshots..."

    local snapshots_dir="${BACKUP_DIR}/snapshots"
    mkdir -p "${snapshots_dir}"

    # Get list of collections
    local collections=$(get_collections 2>/dev/null)

    if [ -z "$collections" ]; then
        warning_message "Could not retrieve collections list"
        return
    fi

    local collection_names=$(echo "$collections" | jq -r '.result.collections[].name' 2>/dev/null || echo "")

    if [ -z "$collection_names" ]; then
        info_message "No collections found"
        return
    fi

    local snapshot_count=0

    # Create snapshot for each collection
    while IFS= read -r collection; do
        [ -z "$collection" ] && continue

        info_message "Creating snapshot for collection: ${collection}"

        # Create snapshot via API
        local snapshot_response=$(create_snapshot "$collection" 2>/dev/null || echo "{}")
        local snapshot_name=$(echo "$snapshot_response" | jq -r '.result.name' 2>/dev/null || echo "")

        if [ -n "$snapshot_name" ]; then
            # Wait a moment for snapshot to be created
            sleep 2

            # Copy snapshot from container
            local snapshot_path="/qdrant/storage/collections/${collection}/snapshots/${snapshot_name}"
            local dest_file="${snapshots_dir}/${collection}_${snapshot_name}"

            if docker cp "${QDRANT_CONTAINER}:${snapshot_path}" "${dest_file}" >> "${LOG_FILE}" 2>&1; then
                success_message "Snapshot created for ${collection}"
                ((snapshot_count++))
            else
                warning_message "Failed to copy snapshot for ${collection}"
            fi
        else
            warning_message "Failed to create snapshot for ${collection}"
        fi
    done <<< "$collection_names"

    info_message "Created ${snapshot_count} collection snapshot(s)"

    if [ $snapshot_count -gt 0 ]; then
        # Create tar archive of all snapshots
        local snapshots_tar="${BACKUP_DIR}/qdrant_snapshots_${BACKUP_DATE}.tar"
        tar -cf "${snapshots_tar}" -C "${snapshots_dir}" . >> "${LOG_FILE}" 2>&1

        # Remove individual snapshot files
        rm -rf "${snapshots_dir}"

        echo "${snapshots_tar}"
    else
        echo ""
    fi
}

# Export collection metadata - تصدير البيانات الوصفية للمجموعات
export_collections_metadata() {
    info_message "Exporting collections metadata..."

    local metadata_file="${BACKUP_DIR}/collections_metadata_${BACKUP_DATE}.json"

    # Get collections info
    local collections=$(get_collections 2>/dev/null || echo "{}")

    if [ -n "$collections" ]; then
        echo "$collections" | jq '.' > "${metadata_file}" 2>/dev/null || echo "$collections" > "${metadata_file}"

        success_message "Metadata exported"
        echo "${metadata_file}"
    else
        warning_message "Could not export metadata"
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

    local s3_path="s3://${S3_BUCKET}/qdrant/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

    if command_exists mc; then
        mc alias set backup "${S3_ENDPOINT}" "${S3_ACCESS_KEY}" "${S3_SECRET_KEY}" > /dev/null 2>&1
        local mc_path="backup/${S3_BUCKET}/qdrant/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

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
    local qdrant_info=$(get_qdrant_info 2>/dev/null || echo "{}")

    cat > "${metadata_file}" <<EOF
{
    "backup_type": "${BACKUP_TYPE}",
    "backup_date": "${BACKUP_DATE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "qdrant": {
        "version": "$(echo "$qdrant_info" | jq -r '.version // "unknown"' 2>/dev/null || echo 'unknown')",
        "host": "${QDRANT_HOST}",
        "port": ${QDRANT_PORT},
        "info": ${qdrant_info}
    },
    "files": {
        "storage_backup": $([ -f "${BACKUP_DIR}"/qdrant_storage*.tar* ] && echo "true" || echo "false"),
        "snapshots": $([ -f "${BACKUP_DIR}"/qdrant_snapshots*.tar* ] && echo "true" || echo "false"),
        "metadata": $([ -f "${BACKUP_DIR}"/collections_metadata*.json* ] && echo "true" || echo "false")
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
    local backup_type_dir="${BACKUP_BASE_DIR}/qdrant/${BACKUP_TYPE}"

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
    print_message "${BLUE}" "  SAHOOL Platform - Qdrant Vector Database Backup"
    print_message "${BLUE}" "  نظام النسخ الاحتياطي لقاعدة بيانات Qdrant"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Initialize
    init_backup

    # Backup storage directory
    local storage_file=$(backup_storage_directory)
    [ -n "$storage_file" ] && storage_file=$(compress_backup "$storage_file")
    [ -n "$storage_file" ] && storage_file=$(encrypt_backup "$storage_file")
    [ -n "$storage_file" ] && upload_to_s3 "$storage_file"

    # Create collection snapshots (weekly/monthly only)
    if [ "$BACKUP_TYPE" = "weekly" ] || [ "$BACKUP_TYPE" = "monthly" ]; then
        local snapshots_file=$(backup_collection_snapshots)
        [ -n "$snapshots_file" ] && snapshots_file=$(compress_backup "$snapshots_file")
        [ -n "$snapshots_file" ] && snapshots_file=$(encrypt_backup "$snapshots_file")
        [ -n "$snapshots_file" ] && upload_to_s3 "$snapshots_file"

        # Export metadata
        local metadata_json=$(export_collections_metadata)
        [ -n "$metadata_json" ] && metadata_json=$(compress_backup "$metadata_json")
        [ -n "$metadata_json" ] && upload_to_s3 "$metadata_json"
    fi

    # Create backup metadata
    create_metadata

    # Cleanup old backups
    cleanup_old_backups

    # Calculate total time
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "Qdrant backup completed successfully!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "Backup location: ${BACKUP_DIR}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    send_notification "success" "Qdrant backup completed in ${minutes}m ${seconds}s"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
