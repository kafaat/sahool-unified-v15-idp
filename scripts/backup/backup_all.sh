#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Complete Backup Orchestration Script
# نظام النسخ الاحتياطي الشامل لجميع المكونات
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Orchestrates backup of all platform components
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Formatting - الألوان والتنسيق
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
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

# Backup configuration - إعدادات النسخ الاحتياطي
BACKUP_TYPE="${1:-daily}"  # daily, weekly, monthly, manual
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
BACKUP_DIR="${BACKUP_BASE_DIR}/complete/${BACKUP_TYPE}/${BACKUP_DATE}"

# Components to backup - المكونات المراد نسخها احتياطيًا
BACKUP_POSTGRES="${BACKUP_POSTGRES:-true}"
BACKUP_REDIS="${BACKUP_REDIS:-true}"
BACKUP_MINIO="${BACKUP_MINIO:-true}"
BACKUP_NATS="${BACKUP_NATS:-false}"
BACKUP_CONFIGS="${BACKUP_CONFIGS:-true}"

# Backup scripts - نصوص النسخ الاحتياطي
POSTGRES_BACKUP_SCRIPT="${SCRIPT_DIR}/backup_postgres.sh"
REDIS_BACKUP_SCRIPT="${SCRIPT_DIR}/backup_redis.sh"
MINIO_BACKUP_SCRIPT="${SCRIPT_DIR}/backup_minio.sh"

# Notification configuration - إعدادات الإشعارات
EMAIL_NOTIFICATIONS="${EMAIL_NOTIFICATIONS_ENABLED:-false}"
SLACK_NOTIFICATIONS="${SLACK_NOTIFICATIONS_ENABLED:-false}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
BACKUP_EMAIL_TO="${BACKUP_EMAIL_TO:-admin@sahool.com}"

# Logging - السجلات
LOG_DIR="${BACKUP_BASE_DIR}/logs"
LOG_FILE="${LOG_DIR}/backup_all_${BACKUP_TYPE}_$(date +%Y%m%d).log"

# Status tracking
declare -A COMPONENT_STATUS
declare -A COMPONENT_DURATION
declare -A COMPONENT_SIZE

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

# Error handler - معالج الأخطاء
error_message() {
    print_message "${RED}" "✗ $1"
}

# Check if command exists - التحقق من وجود أمر
command_exists() {
    command -v "$1" >/dev/null 2>&1
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

# Format duration - تنسيق المدة
format_duration() {
    local seconds=$1
    local minutes=$((seconds / 60))
    local remaining_seconds=$((seconds % 60))
    echo "${minutes}m ${remaining_seconds}s"
}

# Get directory size - الحصول على حجم المجلد
get_dir_size() {
    local dir=$1
    if [ -d "$dir" ]; then
        du -sb "$dir" 2>/dev/null | awk '{print $1}' || echo "0"
    else
        echo "0"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Notification Functions - دوال الإشعارات
# ─────────────────────────────────────────────────────────────────────────────

# Send Slack notification - إرسال إشعار Slack
send_slack_notification() {
    local status=$1
    local message=$2

    if [ "$SLACK_NOTIFICATIONS" != "true" ] || [ -z "$SLACK_WEBHOOK_URL" ]; then
        return
    fi

    local color="good"
    local emoji=":white_check_mark:"

    if [ "$status" = "failure" ]; then
        color="danger"
        emoji=":x:"
    elif [ "$status" = "warning" ]; then
        color="warning"
        emoji=":warning:"
    fi

    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d @- > /dev/null 2>&1 <<EOF
{
    "attachments": [{
        "color": "${color}",
        "title": "${emoji} SAHOOL Complete Backup - ${BACKUP_TYPE}",
        "text": "${message}",
        "footer": "SAHOOL Backup System",
        "ts": $(date +%s)
    }]
}
EOF
}

# Send email notification - إرسال إشعار بريد إلكتروني
send_email_notification() {
    local subject=$1
    local body=$2

    if [ "$EMAIL_NOTIFICATIONS" != "true" ]; then
        return
    fi

    if command_exists mail; then
        echo "$body" | mail -s "$subject" "$BACKUP_EMAIL_TO"
    elif command_exists sendmail; then
        cat > /tmp/backup_email.txt <<EOF
To: ${BACKUP_EMAIL_TO}
Subject: ${subject}

${body}
EOF
        sendmail -t < /tmp/backup_email.txt
        rm -f /tmp/backup_email.txt
    else
        warning_message "No email command found, skipping email notification"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup Functions - دوال النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

# Initialize backup - تهيئة النسخ الاحتياطي
init_backup() {
    info_message "Initializing complete backup..."
    info_message "Backup type: ${BACKUP_TYPE}"
    info_message "Backup date: ${BACKUP_DATE}"

    # Create directories
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"

    # Check if backup scripts exist
    local missing_scripts=0

    if [ "$BACKUP_POSTGRES" = "true" ] && [ ! -f "$POSTGRES_BACKUP_SCRIPT" ]; then
        error_message "PostgreSQL backup script not found: $POSTGRES_BACKUP_SCRIPT"
        ((missing_scripts++))
    fi

    if [ "$BACKUP_REDIS" = "true" ] && [ ! -f "$REDIS_BACKUP_SCRIPT" ]; then
        error_message "Redis backup script not found: $REDIS_BACKUP_SCRIPT"
        ((missing_scripts++))
    fi

    if [ "$BACKUP_MINIO" = "true" ] && [ ! -f "$MINIO_BACKUP_SCRIPT" ]; then
        error_message "MinIO backup script not found: $MINIO_BACKUP_SCRIPT"
        ((missing_scripts++))
    fi

    if [ $missing_scripts -gt 0 ]; then
        error_message "Missing ${missing_scripts} backup script(s)"
        exit 1
    fi

    success_message "Initialization completed"
}

# Backup component - النسخ الاحتياطي لمكون
backup_component() {
    local component_name=$1
    local backup_script=$2

    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"
    info_message "Starting ${component_name} backup..."
    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"

    local start_time=$(date +%s)

    if bash "$backup_script" "$BACKUP_TYPE" >> "${LOG_FILE}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        COMPONENT_STATUS[$component_name]="success"
        COMPONENT_DURATION[$component_name]=$duration

        # Get backup size
        local backup_dir="${BACKUP_BASE_DIR}/${component_name,,}/${BACKUP_TYPE}"
        local size=$(get_dir_size "$backup_dir")
        COMPONENT_SIZE[$component_name]=$size

        success_message "${component_name} backup completed in $(format_duration $duration)"
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        COMPONENT_STATUS[$component_name]="failed"
        COMPONENT_DURATION[$component_name]=$duration
        COMPONENT_SIZE[$component_name]=0

        error_message "${component_name} backup failed after $(format_duration $duration)"
    fi
}

# Backup PostgreSQL - النسخ الاحتياطي لـ PostgreSQL
backup_postgresql() {
    if [ "$BACKUP_POSTGRES" != "true" ]; then
        info_message "PostgreSQL backup disabled, skipping"
        COMPONENT_STATUS["PostgreSQL"]="skipped"
        return
    fi

    backup_component "PostgreSQL" "$POSTGRES_BACKUP_SCRIPT"
}

# Backup Redis - النسخ الاحتياطي لـ Redis
backup_redis() {
    if [ "$BACKUP_REDIS" != "true" ]; then
        info_message "Redis backup disabled, skipping"
        COMPONENT_STATUS["Redis"]="skipped"
        return
    fi

    backup_component "Redis" "$REDIS_BACKUP_SCRIPT"
}

# Backup MinIO - النسخ الاحتياطي لـ MinIO
backup_minio() {
    if [ "$BACKUP_MINIO" != "true" ]; then
        info_message "MinIO backup disabled, skipping"
        COMPONENT_STATUS["MinIO"]="skipped"
        return
    fi

    backup_component "MinIO" "$MINIO_BACKUP_SCRIPT"
}

# Backup NATS - النسخ الاحتياطي لـ NATS
backup_nats() {
    if [ "$BACKUP_NATS" != "true" ]; then
        COMPONENT_STATUS["NATS"]="skipped"
        return
    fi

    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"
    info_message "Starting NATS backup..."
    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"

    local start_time=$(date +%s)
    local nats_backup_dir="${BACKUP_DIR}/nats"

    mkdir -p "$nats_backup_dir"

    # Backup NATS JetStream data
    if docker cp sahool-nats:/data "$nats_backup_dir/" >> "${LOG_FILE}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local size=$(get_dir_size "$nats_backup_dir")

        COMPONENT_STATUS["NATS"]="success"
        COMPONENT_DURATION["NATS"]=$duration
        COMPONENT_SIZE["NATS"]=$size

        success_message "NATS backup completed in $(format_duration $duration)"
    else
        COMPONENT_STATUS["NATS"]="failed"
        error_message "NATS backup failed"
    fi
}

# Backup configurations - النسخ الاحتياطي للإعدادات
backup_configs() {
    if [ "$BACKUP_CONFIGS" != "true" ]; then
        COMPONENT_STATUS["Configs"]="skipped"
        return
    fi

    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"
    info_message "Starting configuration backup..."
    print_message "${CYAN}" "───────────────────────────────────────────────────────────────"

    local start_time=$(date +%s)
    local config_backup_dir="${BACKUP_DIR}/configs"

    mkdir -p "$config_backup_dir"

    # Backup docker-compose files
    cp "${PROJECT_ROOT}"/docker-compose*.yml "$config_backup_dir/" 2>/dev/null || true

    # Backup .env.example (not .env for security)
    cp "${PROJECT_ROOT}/.env.example" "$config_backup_dir/" 2>/dev/null || true

    # Backup configuration directories
    for config_dir in config infra/*/config; do
        if [ -d "${PROJECT_ROOT}/${config_dir}" ]; then
            mkdir -p "${config_backup_dir}/${config_dir}"
            cp -r "${PROJECT_ROOT}/${config_dir}"/* "${config_backup_dir}/${config_dir}/" 2>/dev/null || true
        fi
    done

    # Create backup info
    cat > "${config_backup_dir}/backup_info.txt" <<EOF
SAHOOL Platform Configuration Backup
Backup Date: $(date)
Backup Type: ${BACKUP_TYPE}
Git Commit: $(cd "$PROJECT_ROOT" && git rev-parse HEAD 2>/dev/null || echo "N/A")
Git Branch: $(cd "$PROJECT_ROOT" && git branch --show-current 2>/dev/null || echo "N/A")
EOF

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local size=$(get_dir_size "$config_backup_dir")

    COMPONENT_STATUS["Configs"]="success"
    COMPONENT_DURATION["Configs"]=$duration
    COMPONENT_SIZE["Configs"]=$size

    success_message "Configuration backup completed in $(format_duration $duration)"
}

# Create backup summary - إنشاء ملخص النسخة الاحتياطية
create_backup_summary() {
    info_message "Creating backup summary..."

    local summary_file="${BACKUP_DIR}/BACKUP_SUMMARY.txt"
    local total_duration=0
    local total_size=0
    local successful_count=0
    local failed_count=0
    local skipped_count=0

    # Calculate totals
    for component in "${!COMPONENT_STATUS[@]}"; do
        local status="${COMPONENT_STATUS[$component]}"
        local duration="${COMPONENT_DURATION[$component]:-0}"
        local size="${COMPONENT_SIZE[$component]:-0}"

        total_duration=$((total_duration + duration))
        total_size=$((total_size + size))

        case "$status" in
            success) ((successful_count++)) ;;
            failed) ((failed_count++)) ;;
            skipped) ((skipped_count++)) ;;
        esac
    done

    # Create summary
    cat > "$summary_file" <<EOF
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform - Complete Backup Summary
ملخص النسخة الاحتياطية الشاملة لمنصة سهول
═══════════════════════════════════════════════════════════════════════════════

Backup Information:
  Type:           ${BACKUP_TYPE}
  Date:           ${BACKUP_DATE}
  Started:        $(date -d "@${OVERALL_START_TIME}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date '+%Y-%m-%d %H:%M:%S')
  Completed:      $(date '+%Y-%m-%d %H:%M:%S')
  Total Duration: $(format_duration $total_duration)
  Total Size:     $(format_bytes $total_size)

Component Status:
  ✓ Successful:   ${successful_count}
  ✗ Failed:       ${failed_count}
  ○ Skipped:      ${skipped_count}

Detailed Results:
───────────────────────────────────────────────────────────────────────────────
EOF

    # Add component details
    for component in "${!COMPONENT_STATUS[@]}"; do
        local status="${COMPONENT_STATUS[$component]}"
        local duration="${COMPONENT_DURATION[$component]:-0}"
        local size="${COMPONENT_SIZE[$component]:-0}"

        local status_icon="○"
        case "$status" in
            success) status_icon="✓" ;;
            failed) status_icon="✗" ;;
            skipped) status_icon="○" ;;
        esac

        printf "  %-15s %s %-10s | Duration: %-10s | Size: %-15s\n" \
            "$component" \
            "$status_icon" \
            "$status" \
            "$(format_duration $duration)" \
            "$(format_bytes $size)" >> "$summary_file"
    done

    cat >> "$summary_file" <<EOF

Backup Location:
  ${BACKUP_DIR}

Log File:
  ${LOG_FILE}

═══════════════════════════════════════════════════════════════════════════════
EOF

    success_message "Backup summary created: $summary_file"

    # Display summary
    cat "$summary_file"
}

# Create backup metadata - إنشاء البيانات الوصفية
create_metadata() {
    info_message "Creating backup metadata..."

    local metadata_file="${BACKUP_DIR}/metadata.json"
    local total_size=0

    for component in "${!COMPONENT_SIZE[@]}"; do
        total_size=$((total_size + ${COMPONENT_SIZE[$component]}))
    done

    # Build components JSON
    local components_json="{"
    local first=true

    for component in "${!COMPONENT_STATUS[@]}"; do
        if [ "$first" = false ]; then
            components_json+=","
        fi
        first=false

        components_json+="
    \"${component}\": {
      \"status\": \"${COMPONENT_STATUS[$component]}\",
      \"duration_seconds\": ${COMPONENT_DURATION[$component]:-0},
      \"size_bytes\": ${COMPONENT_SIZE[$component]:-0}
    }"
    done

    components_json+="
  }"

    cat > "$metadata_file" <<EOF
{
  "backup_type": "${BACKUP_TYPE}",
  "backup_date": "${BACKUP_DATE}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "components": ${components_json},
  "summary": {
    "total_size_bytes": ${total_size},
    "total_size_human": "$(format_bytes ${total_size})",
    "successful": $(echo "${!COMPONENT_STATUS[@]}" | tr ' ' '\n' | while read c; do echo "${COMPONENT_STATUS[$c]}"; done | grep -c "success" || echo "0"),
    "failed": $(echo "${!COMPONENT_STATUS[@]}" | tr ' ' '\n' | while read c; do echo "${COMPONENT_STATUS[$c]}"; done | grep -c "failed" || echo "0"),
    "skipped": $(echo "${!COMPONENT_STATUS[@]}" | tr ' ' '\n' | while read c; do echo "${COMPONENT_STATUS[$c]}"; done | grep -c "skipped" || echo "0")
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

# ─────────────────────────────────────────────────────────────────────────────
# Main Function - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    OVERALL_START_TIME=$(date +%s)

    print_message "${MAGENTA}" "═══════════════════════════════════════════════════════════════"
    print_message "${MAGENTA}" "  SAHOOL Platform - Complete Backup System"
    print_message "${MAGENTA}" "  نظام النسخ الاحتياطي الشامل لمنصة سهول"
    print_message "${MAGENTA}" "═══════════════════════════════════════════════════════════════"

    # Initialize
    init_backup

    # Backup all components
    backup_postgresql
    backup_redis
    backup_minio
    backup_nats
    backup_configs

    # Create summary and metadata
    create_backup_summary
    create_metadata

    # Calculate final stats
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - OVERALL_START_TIME))

    # Determine overall status
    local overall_status="success"
    local failed_count=0

    for component in "${!COMPONENT_STATUS[@]}"; do
        if [ "${COMPONENT_STATUS[$component]}" = "failed" ]; then
            ((failed_count++))
            overall_status="failure"
        fi
    done

    # Send notifications
    if [ "$overall_status" = "success" ]; then
        print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
        success_message "Complete backup finished successfully!"
        info_message "Total duration: $(format_duration $total_duration)"
        info_message "Backup location: ${BACKUP_DIR}"
        print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

        send_slack_notification "success" "Complete backup completed in $(format_duration $total_duration)"
        send_email_notification "✓ SAHOOL Backup Success - ${BACKUP_TYPE}" "Complete backup completed successfully in $(format_duration $total_duration).\n\nBackup location: ${BACKUP_DIR}"
    else
        print_message "${RED}" "═══════════════════════════════════════════════════════════════"
        warning_message "Complete backup finished with ${failed_count} failure(s)"
        info_message "Total duration: $(format_duration $total_duration)"
        info_message "Check log file: ${LOG_FILE}"
        print_message "${RED}" "═══════════════════════════════════════════════════════════════"

        send_slack_notification "failure" "Complete backup completed with ${failed_count} failure(s). Check logs for details."
        send_email_notification "⚠ SAHOOL Backup Warning - ${BACKUP_TYPE}" "Complete backup completed with ${failed_count} failure(s).\n\nCheck log file: ${LOG_FILE}"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
