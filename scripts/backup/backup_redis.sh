#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Redis Backup Script
# نظام النسخ الاحتياطي لـ Redis
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Complete backup solution for Redis (RDB + AOF)
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
BACKUP_DIR="${BACKUP_BASE_DIR}/redis/${BACKUP_TYPE}/${BACKUP_DATE}"

# Retention policy (days) - سياسة الاحتفاظ بالنسخ
declare -A RETENTION_DAYS=(
    ["daily"]=7
    ["weekly"]=28
    ["monthly"]=90
    ["manual"]=30
)

# Redis configuration - إعدادات Redis
REDIS_CONTAINER="${REDIS_CONTAINER:-sahool-redis}"
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:?REDIS_PASSWORD is required}"

# Backup options - خيارات النسخ الاحتياطي
BACKUP_RDB="${BACKUP_RDB:-true}"
BACKUP_AOF="${BACKUP_AOF:-true}"
COMPRESSION="${BACKUP_COMPRESSION:-gzip}"
ENCRYPTION_ENABLED="${BACKUP_ENCRYPTION_ENABLED:-false}"
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
LOG_FILE="${LOG_DIR}/redis_${BACKUP_TYPE}_$(date +%Y%m%d).log"

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
    send_notification "failure" "Redis backup failed: $1"
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
    if ! docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        error_exit "Redis container '${REDIS_CONTAINER}' is not running"
    fi
}

# Execute Redis command - تنفيذ أمر Redis
redis_cli() {
    docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" "$@" 2>/dev/null
}

# Get Redis info - الحصول على معلومات Redis
get_redis_info() {
    local key=$1
    redis_cli INFO | grep "^${key}:" | cut -d: -f2 | tr -d '\r'
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
        "title": "${emoji} Redis Backup - ${BACKUP_TYPE}",
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
    info_message "Initializing Redis backup..."
    info_message "Backup type: ${BACKUP_TYPE}"

    # Create backup directories - إنشاء مجلدات النسخ الاحتياطي
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"

    # Check prerequisites - التحقق من المتطلبات
    check_container

    # Get Redis info - الحصول على معلومات Redis
    local redis_version=$(get_redis_info "redis_version")
    local used_memory=$(get_redis_info "used_memory_human")
    local db_keys=$(redis_cli DBSIZE)

    info_message "Redis version: ${redis_version}"
    info_message "Used memory: ${used_memory}"
    info_message "Total keys: ${db_keys}"

    # Check if AOF is enabled
    local aof_enabled=$(get_redis_info "aof_enabled")
    if [ "$aof_enabled" = "0" ] && [ "$BACKUP_AOF" = "true" ]; then
        warning_message "AOF is not enabled in Redis configuration"
        BACKUP_AOF="false"
    fi
}

# Backup RDB file - النسخ الاحتياطي لملف RDB
backup_rdb() {
    if [ "$BACKUP_RDB" != "true" ]; then
        return
    fi

    info_message "Starting RDB backup..."

    local start_time=$(date +%s)

    # Trigger BGSAVE - تشغيل BGSAVE
    if redis_cli BGSAVE | grep -q "Background saving started"; then
        info_message "Background save initiated..."

        # Wait for BGSAVE to complete - انتظار اكتمال BGSAVE
        local max_wait=300  # 5 minutes
        local waited=0

        while [ $waited -lt $max_wait ]; do
            local save_in_progress=$(get_redis_info "rdb_bgsave_in_progress")

            if [ "$save_in_progress" = "0" ]; then
                break
            fi

            sleep 2
            waited=$((waited + 2))
        done

        if [ $waited -ge $max_wait ]; then
            error_exit "BGSAVE timeout"
        fi

        # Check for errors - التحقق من الأخطاء
        local last_save_status=$(get_redis_info "rdb_last_bgsave_status")
        if [ "$last_save_status" != "ok" ]; then
            error_exit "BGSAVE failed with status: ${last_save_status}"
        fi

        # Copy RDB file - نسخ ملف RDB
        local rdb_file="${BACKUP_DIR}/dump_${BACKUP_DATE}.rdb"

        if docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${rdb_file}" >> "${LOG_FILE}" 2>&1; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            local file_size=$(stat -f%z "${rdb_file}" 2>/dev/null || stat -c%s "${rdb_file}")

            success_message "RDB backup completed in ${duration} seconds"
            info_message "RDB file size: $(format_bytes ${file_size})"

            echo "${rdb_file}"
        else
            error_exit "Failed to copy RDB file"
        fi
    else
        error_exit "Failed to initiate BGSAVE"
    fi
}

# Backup AOF file - النسخ الاحتياطي لملف AOF
backup_aof() {
    if [ "$BACKUP_AOF" != "true" ]; then
        return
    fi

    info_message "Starting AOF backup..."

    local start_time=$(date +%s)

    # Trigger BGREWRITEAOF - تشغيل BGREWRITEAOF
    if redis_cli BGREWRITEAOF | grep -q "rewriting"; then
        info_message "AOF rewrite initiated..."

        # Wait for rewrite to complete - انتظار اكتمال إعادة الكتابة
        local max_wait=300  # 5 minutes
        local waited=0

        while [ $waited -lt $max_wait ]; do
            local rewrite_in_progress=$(get_redis_info "aof_rewrite_in_progress")

            if [ "$rewrite_in_progress" = "0" ]; then
                break
            fi

            sleep 2
            waited=$((waited + 2))
        done

        if [ $waited -ge $max_wait ]; then
            warning_message "AOF rewrite timeout (non-critical)"
            return
        fi

        # Copy AOF file - نسخ ملف AOF
        local aof_file="${BACKUP_DIR}/appendonly_${BACKUP_DATE}.aof"

        if docker cp "${REDIS_CONTAINER}:/data/appendonly.aof" "${aof_file}" >> "${LOG_FILE}" 2>&1; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            local file_size=$(stat -f%z "${aof_file}" 2>/dev/null || stat -c%s "${aof_file}")

            success_message "AOF backup completed in ${duration} seconds"
            info_message "AOF file size: $(format_bytes ${file_size})"

            echo "${aof_file}"
        else
            warning_message "Failed to copy AOF file (non-critical)"
        fi
    else
        warning_message "Failed to initiate BGREWRITEAOF (non-critical)"
    fi
}

# Export Redis data as JSON - تصدير بيانات Redis بصيغة JSON
export_redis_data() {
    info_message "Exporting Redis keys to JSON..."

    local json_file="${BACKUP_DIR}/redis_data_${BACKUP_DATE}.json"

    # Get all keys and export - الحصول على جميع المفاتيح والتصدير
    local keys=$(redis_cli KEYS '*' | tr '\r' '\n')
    local key_count=$(echo "$keys" | wc -l)

    if [ $key_count -gt 0 ]; then
        {
            echo "{"
            echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
            echo "  \"total_keys\": ${key_count},"
            echo "  \"data\": {"

            local first=true
            while IFS= read -r key; do
                [ -z "$key" ] && continue

                if [ "$first" = false ]; then
                    echo ","
                fi
                first=false

                local key_type=$(redis_cli TYPE "$key" | tr -d '\r')
                local value=""

                case "$key_type" in
                    string)
                        value=$(redis_cli GET "$key" | sed 's/"/\\"/g')
                        echo -n "    \"${key}\": {\"type\": \"string\", \"value\": \"${value}\"}"
                        ;;
                    list)
                        value=$(redis_cli LRANGE "$key" 0 -1 | jq -Rs '.')
                        echo -n "    \"${key}\": {\"type\": \"list\", \"value\": ${value}}"
                        ;;
                    set)
                        value=$(redis_cli SMEMBERS "$key" | jq -Rs '.')
                        echo -n "    \"${key}\": {\"type\": \"set\", \"value\": ${value}}"
                        ;;
                    hash)
                        value=$(redis_cli HGETALL "$key" | jq -Rs '.')
                        echo -n "    \"${key}\": {\"type\": \"hash\", \"value\": ${value}\"}"
                        ;;
                    *)
                        echo -n "    \"${key}\": {\"type\": \"${key_type}\", \"value\": null}"
                        ;;
                esac
            done <<< "$keys"

            echo ""
            echo "  }"
            echo "}"
        } > "${json_file}"

        success_message "Exported ${key_count} keys to JSON"
        echo "${json_file}"
    else
        info_message "No keys to export"
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

    local s3_path="s3://${S3_BUCKET}/redis/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

    if command_exists mc; then
        mc alias set backup "${S3_ENDPOINT}" "${S3_ACCESS_KEY}" "${S3_SECRET_KEY}" > /dev/null 2>&1
        local mc_path="backup/${S3_BUCKET}/redis/${BACKUP_TYPE}/${BACKUP_DATE}/$(basename ${file})"

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

    cat > "${metadata_file}" <<EOF
{
    "backup_type": "${BACKUP_TYPE}",
    "backup_date": "${BACKUP_DATE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "redis": {
        "version": "$(get_redis_info 'redis_version')",
        "host": "${REDIS_HOST}",
        "port": ${REDIS_PORT},
        "used_memory": "$(get_redis_info 'used_memory_human')",
        "total_keys": $(redis_cli DBSIZE),
        "aof_enabled": $(get_redis_info 'aof_enabled')
    },
    "files": {
        "rdb": $([ -f "${BACKUP_DIR}"/dump*.rdb* ] && echo "true" || echo "false"),
        "aof": $([ -f "${BACKUP_DIR}"/appendonly*.aof* ] && echo "true" || echo "false"),
        "json": $([ -f "${BACKUP_DIR}"/redis_data*.json* ] && echo "true" || echo "false")
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
    info_message "Verifying backup integrity..."

    local rdb_file=$(ls "${BACKUP_DIR}"/dump*.rdb 2>/dev/null | head -1)

    if [ -f "$rdb_file" ]; then
        if command_exists redis-check-rdb; then
            if redis-check-rdb "$rdb_file" >> "${LOG_FILE}" 2>&1; then
                success_message "RDB verification passed"
            else
                warning_message "RDB verification failed"
            fi
        else
            info_message "redis-check-rdb not available, skipping RDB verification"
        fi
    fi

    success_message "Backup verification completed"
}

# Cleanup old backups - تنظيف النسخ القديمة
cleanup_old_backups() {
    info_message "Cleaning up old backups..."

    local retention_days=${RETENTION_DAYS[$BACKUP_TYPE]}
    local backup_type_dir="${BACKUP_BASE_DIR}/redis/${BACKUP_TYPE}"

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
    print_message "${BLUE}" "  SAHOOL Platform - Redis Backup"
    print_message "${BLUE}" "  نظام النسخ الاحتياطي لـ Redis"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Initialize
    init_backup

    # Backup RDB
    local rdb_file=$(backup_rdb)
    [ -n "$rdb_file" ] && rdb_file=$(compress_backup "$rdb_file")
    [ -n "$rdb_file" ] && rdb_file=$(encrypt_backup "$rdb_file")
    [ -n "$rdb_file" ] && upload_to_s3 "$rdb_file"

    # Backup AOF (weekly/monthly only)
    if [ "$BACKUP_TYPE" = "weekly" ] || [ "$BACKUP_TYPE" = "monthly" ]; then
        local aof_file=$(backup_aof)
        [ -n "$aof_file" ] && aof_file=$(compress_backup "$aof_file")
        [ -n "$aof_file" ] && aof_file=$(encrypt_backup "$aof_file")
        [ -n "$aof_file" ] && upload_to_s3 "$aof_file"

        # Export JSON
        local json_file=$(export_redis_data)
        [ -n "$json_file" ] && json_file=$(compress_backup "$json_file")
        [ -n "$json_file" ] && upload_to_s3 "$json_file"
    fi

    # Create metadata
    create_metadata

    # Verify backup
    verify_backup

    # Cleanup old backups
    cleanup_old_backups

    # Calculate total time
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "Redis backup completed successfully!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "Backup location: ${BACKUP_DIR}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    # Send success notification
    send_notification "success" "Redis backup completed in ${minutes}m ${seconds}s"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
