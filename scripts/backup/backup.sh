#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Backup Script - نظام النسخ الاحتياطي لمنصة سهول
# Complete backup for PostgreSQL, Redis, NATS, and file uploads
# نسخ احتياطي كامل لقاعدة البيانات، Redis، NATS، والملفات المرفوعة
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration - التكوين
# ─────────────────────────────────────────────────────────────────────────────

# Script directory - مجلد السكريبت
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment variables - تحميل متغيرات البيئة
if [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
fi

# Backup configuration - إعدادات النسخ الاحتياطي
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_DATE}"
BACKUP_TYPE="${1:-daily}"  # daily, weekly, monthly

# Retention policy (days) - سياسة الاحتفاظ بالنسخ
DAILY_RETENTION=7
WEEKLY_RETENTION=28    # 4 weeks
MONTHLY_RETENTION=365  # 12 months

# Docker containers - حاويات Docker
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
REDIS_CONTAINER="${REDIS_CONTAINER:-sahool-redis}"
NATS_CONTAINER="${NATS_CONTAINER:-sahool-nats}"

# Database credentials - بيانات الاعتماد لقاعدة البيانات
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD}"
DB_NAME="${POSTGRES_DB:-sahool}"

# S3/MinIO configuration (optional) - إعدادات S3/MinIO (اختياري)
S3_ENABLED="${S3_BACKUP_ENABLED:-false}"
S3_ENDPOINT="${S3_ENDPOINT:-}"
S3_BUCKET="${S3_BUCKET:-sahool-backups}"
S3_ACCESS_KEY="${S3_ACCESS_KEY:-}"
S3_SECRET_KEY="${S3_SECRET_KEY:-}"

# Notification settings - إعدادات الإشعارات
EMAIL_ENABLED="${EMAIL_NOTIFICATIONS_ENABLED:-false}"
EMAIL_TO="${BACKUP_EMAIL_TO:-admin@sahool.com}"
SLACK_ENABLED="${SLACK_NOTIFICATIONS_ENABLED:-false}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

# Colors for output - ألوان للطباعة
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if docker container is running - التحقق من تشغيل الحاوية
check_container() {
    local container=$1
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        log_error "Container ${container} is not running - الحاوية ${container} غير قيد التشغيل"
        return 1
    fi
    return 0
}

# Send email notification - إرسال إشعار بالبريد الإلكتروني
send_email() {
    local subject="$1"
    local body="$2"

    if [ "${EMAIL_ENABLED}" = "true" ] && [ -n "${SMTP_HOST:-}" ]; then
        log_info "Sending email notification - إرسال إشعار بالبريد"

        # Using swaks if available, otherwise python
        if command -v swaks &> /dev/null; then
            echo "$body" | swaks \
                --to "${EMAIL_TO}" \
                --from "${SMTP_FROM_EMAIL:-backup@sahool.com}" \
                --server "${SMTP_HOST}" \
                --port "${SMTP_PORT:-587}" \
                --auth LOGIN \
                --auth-user "${SMTP_USER}" \
                --auth-password "${SMTP_PASSWORD}" \
                --subject "$subject" \
                --body - \
                --tls
        else
            python3 - <<EOF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart()
msg['From'] = '${SMTP_FROM_EMAIL:-backup@sahool.com}'
msg['To'] = '${EMAIL_TO}'
msg['Subject'] = '${subject}'
msg.attach(MIMEText('''${body}''', 'plain'))

server = smtplib.SMTP('${SMTP_HOST}', ${SMTP_PORT:-587})
server.starttls()
server.login('${SMTP_USER}', '${SMTP_PASSWORD}')
server.send_message(msg)
server.quit()
EOF
        fi
    fi
}

# Send Slack notification - إرسال إشعار على Slack
send_slack() {
    local message="$1"
    local status="${2:-info}"  # success, error, info

    if [ "${SLACK_ENABLED}" = "true" ] && [ -n "${SLACK_WEBHOOK}" ]; then
        local color="good"
        [ "$status" = "error" ] && color="danger"
        [ "$status" = "info" ] && color="#36a64f"

        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"${color}\",\"text\":\"${message}\"}]}" \
            "${SLACK_WEBHOOK}" &>/dev/null || true
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup Functions - دوال النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

# Backup PostgreSQL database - نسخ احتياطي لقاعدة البيانات
backup_postgres() {
    log_info "Starting PostgreSQL backup - بدء النسخ الاحتياطي لـ PostgreSQL"

    if ! check_container "${POSTGRES_CONTAINER}"; then
        return 1
    fi

    local backup_file="${BACKUP_DIR}/postgres/sahool_${BACKUP_DATE}.sql"
    mkdir -p "${BACKUP_DIR}/postgres"

    # Create database dump - إنشاء نسخة من قاعدة البيانات
    docker exec "${POSTGRES_CONTAINER}" pg_dump \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --format=custom \
        --compress=9 \
        --verbose \
        > "${backup_file}" 2>&1

    if [ $? -eq 0 ]; then
        # Compress with gzip - ضغط الملف
        gzip -9 "${backup_file}"
        local backup_size=$(du -h "${backup_file}.gz" | cut -f1)
        log_success "PostgreSQL backup completed: ${backup_size} - اكتمل النسخ الاحتياطي"
        echo "${backup_file}.gz"
    else
        log_error "PostgreSQL backup failed - فشل النسخ الاحتياطي"
        return 1
    fi
}

# Backup Redis data - نسخ احتياطي لبيانات Redis
backup_redis() {
    log_info "Starting Redis backup - بدء النسخ الاحتياطي لـ Redis"

    if ! check_container "${REDIS_CONTAINER}"; then
        return 1
    fi

    local backup_file="${BACKUP_DIR}/redis/dump_${BACKUP_DATE}.rdb"
    mkdir -p "${BACKUP_DIR}/redis"

    # Trigger Redis BGSAVE - تفعيل BGSAVE في Redis
    docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" BGSAVE

    # Wait for save to complete - انتظار اكتمال الحفظ
    local max_wait=60
    local count=0
    while [ $count -lt $max_wait ]; do
        local status=$(docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" LASTSAVE)
        sleep 1
        local new_status=$(docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" LASTSAVE)
        if [ "$new_status" != "$status" ]; then
            break
        fi
        count=$((count + 1))
    done

    # Copy RDB file - نسخ ملف RDB
    docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${backup_file}"

    # Copy AOF file if exists - نسخ ملف AOF إن وُجد
    if docker exec "${REDIS_CONTAINER}" test -f /data/appendonly.aof; then
        docker cp "${REDIS_CONTAINER}:/data/appendonly.aof" "${BACKUP_DIR}/redis/appendonly_${BACKUP_DATE}.aof"
    fi

    # Compress - ضغط
    gzip -9 "${backup_file}"
    [ -f "${BACKUP_DIR}/redis/appendonly_${BACKUP_DATE}.aof" ] && \
        gzip -9 "${BACKUP_DIR}/redis/appendonly_${BACKUP_DATE}.aof"

    local backup_size=$(du -h "${backup_file}.gz" | cut -f1)
    log_success "Redis backup completed: ${backup_size} - اكتمل النسخ الاحتياطي"
    echo "${backup_file}.gz"
}

# Backup NATS JetStream data - نسخ احتياطي لبيانات NATS JetStream
backup_nats() {
    log_info "Starting NATS JetStream backup - بدء النسخ الاحتياطي لـ NATS"

    if ! check_container "${NATS_CONTAINER}"; then
        return 1
    fi

    local backup_file="${BACKUP_DIR}/nats/jetstream_${BACKUP_DATE}.tar"
    mkdir -p "${BACKUP_DIR}/nats"

    # Copy JetStream data directory - نسخ مجلد بيانات JetStream
    docker exec "${NATS_CONTAINER}" tar czf /tmp/jetstream_backup.tar.gz -C /data .
    docker cp "${NATS_CONTAINER}:/tmp/jetstream_backup.tar.gz" "${backup_file}.gz"
    docker exec "${NATS_CONTAINER}" rm /tmp/jetstream_backup.tar.gz

    local backup_size=$(du -h "${backup_file}.gz" | cut -f1)
    log_success "NATS backup completed: ${backup_size} - اكتمل النسخ الاحتياطي"
    echo "${backup_file}.gz"
}

# Backup uploaded files - نسخ احتياطي للملفات المرفوعة
backup_uploads() {
    log_info "Starting uploads backup - بدء النسخ الاحتياطي للملفات المرفوعة"

    local backup_file="${BACKUP_DIR}/uploads/files_${BACKUP_DATE}.tar"
    mkdir -p "${BACKUP_DIR}/uploads"

    # Backup uploads directory (satellite images, photos, etc.)
    # نسخ مجلد الملفات المرفوعة (صور الأقمار الصناعية، الصور، إلخ)
    local upload_dirs=(
        "${PROJECT_ROOT}/uploads"
        "${PROJECT_ROOT}/data/uploads"
        "${PROJECT_ROOT}/storage/uploads"
    )

    local found_uploads=false
    for upload_dir in "${upload_dirs[@]}"; do
        if [ -d "$upload_dir" ]; then
            tar czf "${backup_file}.gz" -C "$(dirname "$upload_dir")" "$(basename "$upload_dir")" 2>/dev/null
            found_uploads=true
            break
        fi
    done

    if [ "$found_uploads" = true ]; then
        local backup_size=$(du -h "${backup_file}.gz" | cut -f1)
        log_success "Uploads backup completed: ${backup_size} - اكتمل النسخ الاحتياطي"
        echo "${backup_file}.gz"
    else
        log_warning "No uploads directory found - لم يتم العثور على مجلد الملفات المرفوعة"
    fi
}

# Backup configuration files - نسخ احتياطي لملفات التكوين
backup_config() {
    log_info "Starting configuration backup - بدء النسخ الاحتياطي للتكوينات"

    local backup_file="${BACKUP_DIR}/config/config_${BACKUP_DATE}.tar"
    mkdir -p "${BACKUP_DIR}/config"

    # Backup important configuration files - نسخ ملفات التكوين المهمة
    tar czf "${backup_file}.gz" \
        -C "${PROJECT_ROOT}" \
        --exclude='.env' \
        docker-compose.yml \
        Makefile \
        .env.example \
        infra/ \
        config/ \
        2>/dev/null || true

    local backup_size=$(du -h "${backup_file}.gz" | cut -f1)
    log_success "Configuration backup completed: ${backup_size} - اكتمل النسخ الاحتياطي"
    echo "${backup_file}.gz"
}

# Upload to S3/MinIO - رفع إلى S3/MinIO
upload_to_s3() {
    local backup_archive="$1"

    if [ "${S3_ENABLED}" != "true" ] || [ -z "${S3_ENDPOINT}" ]; then
        return 0
    fi

    log_info "Uploading to S3/MinIO - رفع إلى S3/MinIO"

    # Check if aws CLI is available - التحقق من توفر aws CLI
    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI not found, skipping S3 upload - لم يتم العثور على AWS CLI"
        return 1
    fi

    # Configure AWS credentials - تكوين بيانات AWS
    export AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY}"
    export AWS_SECRET_ACCESS_KEY="${S3_SECRET_KEY}"

    local s3_path="s3://${S3_BUCKET}/${BACKUP_DATE}/$(basename "${backup_archive}")"

    aws s3 cp \
        "${backup_archive}" \
        "${s3_path}" \
        --endpoint-url="${S3_ENDPOINT}" \
        --region="${AWS_REGION:-us-east-1}" \
        --no-progress

    if [ $? -eq 0 ]; then
        log_success "Uploaded to S3: ${s3_path} - تم الرفع إلى S3"
    else
        log_error "Failed to upload to S3 - فشل الرفع إلى S3"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Retention Management - إدارة الاحتفاظ بالنسخ
# ─────────────────────────────────────────────────────────────────────────────

cleanup_old_backups() {
    log_info "Cleaning up old backups - تنظيف النسخ القديمة"

    local retention_days
    case "${BACKUP_TYPE}" in
        daily)
            retention_days=${DAILY_RETENTION}
            ;;
        weekly)
            retention_days=${WEEKLY_RETENTION}
            ;;
        monthly)
            retention_days=${MONTHLY_RETENTION}
            ;;
        *)
            retention_days=${DAILY_RETENTION}
            ;;
    esac

    # Remove backups older than retention period - حذف النسخ الأقدم من فترة الاحتفاظ
    find "${BACKUP_BASE_DIR}" -type d -name "20*" -mtime +${retention_days} -exec rm -rf {} + 2>/dev/null || true

    log_success "Cleanup completed (retention: ${retention_days} days) - اكتمل التنظيف"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Backup Process - عملية النسخ الاحتياطي الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local start_time=$(date +%s)

    echo "═══════════════════════════════════════════════════════════════════"
    echo "  SAHOOL Platform Backup - النسخ الاحتياطي لمنصة سهول"
    echo "  Type: ${BACKUP_TYPE}"
    echo "  Date: ${BACKUP_DATE}"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # Create backup directory - إنشاء مجلد النسخ الاحتياطي
    mkdir -p "${BACKUP_DIR}"

    # Array to track successful backups - مصفوفة لتتبع النسخ الناجحة
    declare -a backup_files
    local backup_failed=false

    # Perform backups - تنفيذ النسخ الاحتياطي
    if postgres_backup=$(backup_postgres); then
        backup_files+=("$postgres_backup")
    else
        backup_failed=true
    fi

    if redis_backup=$(backup_redis); then
        backup_files+=("$redis_backup")
    else
        backup_failed=true
    fi

    if nats_backup=$(backup_nats); then
        backup_files+=("$nats_backup")
    else
        backup_failed=true
    fi

    if uploads_backup=$(backup_uploads); then
        [ -n "$uploads_backup" ] && backup_files+=("$uploads_backup")
    fi

    if config_backup=$(backup_config); then
        backup_files+=("$config_backup")
    fi

    # Create consolidated archive - إنشاء أرشيف موحد
    log_info "Creating consolidated backup archive - إنشاء أرشيف موحد"
    local archive_file="${BACKUP_BASE_DIR}/sahool_backup_${BACKUP_TYPE}_${BACKUP_DATE}.tar.gz"
    tar czf "${archive_file}" -C "${BACKUP_BASE_DIR}" "$(basename "${BACKUP_DIR}")"

    local archive_size=$(du -h "${archive_file}" | cut -f1)
    log_success "Consolidated archive created: ${archive_size} - تم إنشاء الأرشيف"

    # Upload to S3 if enabled - رفع إلى S3 إذا كان مفعلاً
    upload_to_s3 "${archive_file}"

    # Create backup metadata - إنشاء بيانات وصفية للنسخ الاحتياطي
    cat > "${BACKUP_DIR}/backup_metadata.json" <<EOF
{
    "backup_date": "${BACKUP_DATE}",
    "backup_type": "${BACKUP_TYPE}",
    "platform_version": "16.0.0",
    "files": [
        $(printf '%s\n' "${backup_files[@]}" | sed 's/.*/"&"/' | paste -sd,)
    ],
    "archive_file": "${archive_file}",
    "archive_size": "${archive_size}",
    "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

    # Cleanup old backups - تنظيف النسخ القديمة
    cleanup_old_backups

    # Calculate duration - حساب المدة
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo ""
    echo "═══════════════════════════════════════════════════════════════════"

    # Send notifications - إرسال الإشعارات
    if [ "$backup_failed" = false ]; then
        log_success "Backup completed successfully in ${duration}s - اكتمل النسخ بنجاح"
        echo "Archive: ${archive_file}"
        echo "Size: ${archive_size}"

        local message="✅ SAHOOL Backup Successful\nType: ${BACKUP_TYPE}\nSize: ${archive_size}\nDuration: ${duration}s"
        send_email "SAHOOL Backup Success" "$message"
        send_slack "$message" "success"
    else
        log_error "Backup completed with errors - اكتمل النسخ مع أخطاء"

        local message="⚠️ SAHOOL Backup Completed with Errors\nType: ${BACKUP_TYPE}\nCheck logs for details"
        send_email "SAHOOL Backup Warning" "$message"
        send_slack "$message" "error"
    fi

    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
}

# Run main function - تشغيل الدالة الرئيسية
main "$@"
