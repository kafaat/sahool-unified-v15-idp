#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Backup Cron Wrapper - مجدول النسخ الاحتياطي لمنصة سهول
# Cron job wrapper for automated backups
# غلاف مجدولة للنسخ الاحتياطي الآلي
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# ═══════════════════════════════════════════════════════════════════════════════
#
# Crontab configuration (add to crontab -e):
# إعدادات Crontab (أضف إلى crontab -e):
#
# Daily backup at 2 AM - نسخ احتياطي يومي في الساعة 2 صباحاً
# 0 2 * * * /path/to/sahool/scripts/backup/backup-cron.sh daily
#
# Weekly backup on Sunday at 3 AM - نسخ احتياطي أسبوعي الأحد في الساعة 3 صباحاً
# 0 3 * * 0 /path/to/sahool/scripts/backup/backup-cron.sh weekly
#
# Monthly backup on 1st at 4 AM - نسخ احتياطي شهري في الأول من كل شهر الساعة 4 صباحاً
# 0 4 1 * * /path/to/sahool/scripts/backup/backup-cron.sh monthly
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration - التكوين
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Backup type: daily, weekly, monthly - نوع النسخ الاحتياطي
BACKUP_TYPE="${1:-daily}"

# Log directory - مجلد السجلات
LOG_DIR="${PROJECT_ROOT}/logs/backup"
mkdir -p "${LOG_DIR}"

# Log file - ملف السجل
LOG_FILE="${LOG_DIR}/backup_${BACKUP_TYPE}_$(date +%Y%m%d_%H%M%S).log"

# Lock file to prevent concurrent backups - ملف قفل لمنع النسخ المتزامنة
LOCK_FILE="/tmp/sahool_backup_${BACKUP_TYPE}.lock"

# Maximum log age in days - أقصى عمر للسجلات بالأيام
MAX_LOG_AGE=30

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo "[ERROR] [$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}" >&2
}

# Acquire lock - الحصول على القفل
acquire_lock() {
    if [ -e "${LOCK_FILE}" ]; then
        local lock_pid=$(cat "${LOCK_FILE}")
        if ps -p "${lock_pid}" > /dev/null 2>&1; then
            log_error "Another backup is already running (PID: ${lock_pid})"
            log_error "نسخة احتياطية أخرى قيد التشغيل بالفعل"
            exit 1
        else
            log "Removing stale lock file - إزالة ملف قفل قديم"
            rm -f "${LOCK_FILE}"
        fi
    fi

    echo $$ > "${LOCK_FILE}"
}

# Release lock - تحرير القفل
release_lock() {
    rm -f "${LOCK_FILE}"
}

# Cleanup old logs - تنظيف السجلات القديمة
cleanup_logs() {
    log "Cleaning up old log files - تنظيف ملفات السجلات القديمة"
    find "${LOG_DIR}" -name "backup_*.log" -mtime +${MAX_LOG_AGE} -delete 2>/dev/null || true
}

# Check system resources - فحص موارد النظام
check_resources() {
    log "Checking system resources - فحص موارد النظام"

    # Check disk space - فحص مساحة القرص
    local backup_dir="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
    local available_space=$(df -BG "${backup_dir}" | awk 'NR==2 {print $4}' | sed 's/G//')

    # Require at least 5GB free space - يتطلب 5 جيجابايت على الأقل
    if [ "${available_space}" -lt 5 ]; then
        log_error "Insufficient disk space: ${available_space}GB available"
        log_error "مساحة القرص غير كافية: ${available_space} جيجابايت متاحة"
        return 1
    fi

    log "Available disk space: ${available_space}GB - المساحة المتاحة: ${available_space} جيجابايت"

    # Check system load - فحص حمل النظام
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    log "System load average: ${load_avg} - متوسط حمل النظام: ${load_avg}"

    # Check if Docker is running - التحقق من تشغيل Docker
    if ! docker ps > /dev/null 2>&1; then
        log_error "Docker is not running - Docker غير قيد التشغيل"
        return 1
    fi

    log "System resource check passed - نجح فحص موارد النظام"
    return 0
}

# Run pre-backup checks - تشغيل فحوصات ما قبل النسخ الاحتياطي
pre_backup_checks() {
    log "Running pre-backup checks - تشغيل فحوصات ما قبل النسخ الاحتياطي"

    # Check if backup script exists - التحقق من وجود سكريبت النسخ الاحتياطي
    if [ ! -f "${SCRIPT_DIR}/backup.sh" ]; then
        log_error "Backup script not found - سكريبت النسخ الاحتياطي غير موجود"
        return 1
    fi

    # Check if backup script is executable - التحقق من قابلية تنفيذ السكريبت
    if [ ! -x "${SCRIPT_DIR}/backup.sh" ]; then
        log "Making backup script executable - جعل السكريبت قابلاً للتنفيذ"
        chmod +x "${SCRIPT_DIR}/backup.sh"
    fi

    # Check environment file - فحص ملف البيئة
    if [ ! -f "${PROJECT_ROOT}/.env" ]; then
        log_error "Environment file (.env) not found - ملف البيئة غير موجود"
        return 1
    fi

    # Verify required environment variables - التحقق من متغيرات البيئة المطلوبة
    source "${PROJECT_ROOT}/.env"
    local required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required environment variable ${var} is not set"
            log_error "متغير البيئة المطلوب ${var} غير معرف"
            return 1
        fi
    done

    log "Pre-backup checks passed - نجحت فحوصات ما قبل النسخ الاحتياطي"
    return 0
}

# Send notification on failure - إرسال إشعار عند الفشل
notify_failure() {
    local exit_code=$1

    log_error "Backup failed with exit code: ${exit_code}"
    log_error "فشل النسخ الاحتياطي برمز الخطأ: ${exit_code}"

    # Send email if configured - إرسال بريد إلكتروني إذا كان مكوناً
    if [ -n "${BACKUP_EMAIL_TO:-}" ] && [ -n "${SMTP_HOST:-}" ]; then
        local subject="❌ SAHOOL Backup Failed - ${BACKUP_TYPE}"
        local body="Backup job failed at $(date)\nType: ${BACKUP_TYPE}\nExit code: ${exit_code}\n\nCheck log: ${LOG_FILE}"

        echo "$body" | mail -s "$subject" "${BACKUP_EMAIL_TO}" 2>/dev/null || true
    fi

    # Send Slack notification if configured - إرسال إشعار Slack إذا كان مكوناً
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"❌ SAHOOL Backup Failed\",\"attachments\":[{\"color\":\"danger\",\"fields\":[{\"title\":\"Type\",\"value\":\"${BACKUP_TYPE}\",\"short\":true},{\"title\":\"Exit Code\",\"value\":\"${exit_code}\",\"short\":true},{\"title\":\"Time\",\"value\":\"$(date)\",\"short\":false}]}]}" \
            "${SLACK_WEBHOOK_URL}" &>/dev/null || true
    fi
}

# Rotate log files - تدوير ملفات السجلات
rotate_logs() {
    log "Rotating log files - تدوير ملفات السجلات"

    # Keep only last 50 log files - الاحتفاظ بآخر 50 ملف سجل فقط
    local log_count=$(find "${LOG_DIR}" -name "backup_*.log" | wc -l)

    if [ "${log_count}" -gt 50 ]; then
        log "Removing old log files (keeping last 50) - إزالة ملفات السجلات القديمة"
        find "${LOG_DIR}" -name "backup_*.log" -type f -printf '%T@ %p\n' | \
            sort -n | \
            head -n -50 | \
            awk '{print $2}' | \
            xargs rm -f 2>/dev/null || true
    fi

    # Compress logs older than 7 days - ضغط السجلات الأقدم من 7 أيام
    find "${LOG_DIR}" -name "backup_*.log" -mtime +7 ! -name "*.gz" -exec gzip {} \; 2>/dev/null || true
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Process - العملية الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local start_time=$(date +%s)

    log "═══════════════════════════════════════════════════════════════════"
    log "SAHOOL Backup Cron Job - مجدولة النسخ الاحتياطي لسهول"
    log "Type: ${BACKUP_TYPE}"
    log "Started at: $(date)"
    log "═══════════════════════════════════════════════════════════════════"

    # Set trap to release lock on exit - تعيين trap لتحرير القفل عند الخروج
    trap release_lock EXIT

    # Acquire lock - الحصول على القفل
    acquire_lock

    # Run pre-backup checks - تشغيل فحوصات ما قبل النسخ الاحتياطي
    if ! pre_backup_checks; then
        log_error "Pre-backup checks failed - فشلت فحوصات ما قبل النسخ الاحتياطي"
        notify_failure 1
        exit 1
    fi

    # Check system resources - فحص موارد النظام
    if ! check_resources; then
        log_error "Resource check failed - فشل فحص الموارد"
        notify_failure 2
        exit 2
    fi

    # Run backup script - تشغيل سكريبت النسخ الاحتياطي
    log "Starting backup process - بدء عملية النسخ الاحتياطي"

    if "${SCRIPT_DIR}/backup.sh" "${BACKUP_TYPE}" >> "${LOG_FILE}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        log "═══════════════════════════════════════════════════════════════════"
        log "Backup completed successfully - اكتمل النسخ الاحتياطي بنجاح"
        log "Duration: ${duration}s - المدة: ${duration} ثانية"
        log "═══════════════════════════════════════════════════════════════════"

        # Cleanup old logs - تنظيف السجلات القديمة
        cleanup_logs
        rotate_logs

        exit 0
    else
        local exit_code=$?
        log_error "Backup failed - فشل النسخ الاحتياطي"
        notify_failure ${exit_code}
        exit ${exit_code}
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Validate backup type - التحقق من نوع النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

if [[ ! "${BACKUP_TYPE}" =~ ^(daily|weekly|monthly)$ ]]; then
    echo "Error: Invalid backup type '${BACKUP_TYPE}'"
    echo "Usage: $0 {daily|weekly|monthly}"
    echo ""
    echo "خطأ: نوع نسخ احتياطي غير صحيح '${BACKUP_TYPE}'"
    echo "الاستخدام: $0 {daily|weekly|monthly}"
    exit 1
fi

# Run main function - تشغيل الدالة الرئيسية
main "$@"
