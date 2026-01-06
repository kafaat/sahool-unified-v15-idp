#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Post-Backup Hook
# خطاف ما بعد النسخ الاحتياطي
# ═══════════════════════════════════════════════════════════════════════════════
# Description: This script runs after the backup process completes
# الوصف: يتم تشغيل هذا السكريبت بعد اكتمال عملية النسخ الاحتياطي
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Parameters - المعاملات
BACKUP_TYPE="${1:-}"
BACKUP_MODE="${2:-}"
DB_NAME="${3:-}"
STATUS="${4:-success}"  # success or failure

# Colors - الألوان
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# Helper functions - دوال مساعدة
info_message() {
    echo -e "${BLUE}[POST-BACKUP] $1${NC}"
}

success_message() {
    echo -e "${GREEN}[POST-BACKUP] ✓ $1${NC}"
}

error_message() {
    echo -e "${RED}[POST-BACKUP] ✗ $1${NC}"
}

warning_message() {
    echo -e "${YELLOW}[POST-BACKUP] ⚠ $1${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Post-Backup Tasks - مهام ما بعد النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

info_message "Starting post-backup tasks..."
info_message "Backup type: ${BACKUP_TYPE}"
info_message "Backup mode: ${BACKUP_MODE}"
info_message "Database: ${DB_NAME}"
info_message "Status: ${STATUS}"

# Example 1: Send notification based on status - إرسال إشعار بناءً على الحالة
info_message "Sending backup notification..."
if [ "$STATUS" = "success" ]; then
    success_message "Backup completed successfully!"
    # Send success notification
    # إرسال إشعار النجاح
    # Examples:
    # - Email: echo "Backup successful" | mail -s "SAHOOL Backup Success" admin@example.com
    # - Slack: curl -X POST -H 'Content-type: application/json' --data '{"text":"Backup successful"}' $SLACK_WEBHOOK
    # - SMS: curl -X POST https://api.twilio.com/...
else
    error_message "Backup failed!"
    # Send failure alert
    # إرسال تنبيه الفشل
    # High priority notifications for failures
fi

# Example 2: Update backup status in database or monitoring system
# تحديث حالة النسخ الاحتياطي في قاعدة البيانات أو نظام المراقبة
info_message "Updating backup status in monitoring system..."
# Add your monitoring integration here
# أضف تكامل المراقبة هنا
# curl -X POST http://monitoring-system/api/backup-completed \
#   -d "{\"database\":\"${DB_NAME}\",\"type\":\"${BACKUP_TYPE}\",\"status\":\"${STATUS}\"}"

# Example 3: Sync backups to remote storage (S3, NFS, etc.)
# مزامنة النسخ الاحتياطية إلى التخزين البعيد
if [ "$STATUS" = "success" ]; then
    info_message "Syncing backups to remote storage..."

    BACKUP_BASE_DIR="${BACKUP_DIR:-/backups}"

    # Example: Sync to S3
    # مثال: المزامنة إلى S3
    # aws s3 sync "${BACKUP_BASE_DIR}/postgres/${BACKUP_TYPE}" \
    #   s3://my-backup-bucket/postgres/${BACKUP_TYPE}/ \
    #   --exclude "*.log"

    # Example: Sync to remote NFS/CIFS
    # مثال: المزامنة إلى NFS/CIFS البعيد
    # rsync -avz "${BACKUP_BASE_DIR}/postgres/${BACKUP_TYPE}" \
    #   remote-server:/backups/postgres/${BACKUP_TYPE}/

    success_message "Remote sync completed (if configured)"
fi

# Example 4: Generate backup report - إنشاء تقرير النسخ الاحتياطي
if [ "$STATUS" = "success" ]; then
    info_message "Generating backup report..."

    BACKUP_BASE_DIR="${BACKUP_DIR:-/backups}"
    REPORT_FILE="${BACKUP_BASE_DIR}/reports/backup_report_$(date +%Y%m%d).txt"
    mkdir -p "${BACKUP_BASE_DIR}/reports"

    cat > "$REPORT_FILE" <<EOF
═══════════════════════════════════════════════════════════════
SAHOOL Platform - Backup Report
تقرير النسخ الاحتياطي
═══════════════════════════════════════════════════════════════

Date: $(date '+%Y-%m-%d %H:%M:%S')
Backup Type: ${BACKUP_TYPE}
Backup Mode: ${BACKUP_MODE}
Database: ${DB_NAME}
Status: ${STATUS}

Backup Statistics:
- Daily backups: $(find ${BACKUP_BASE_DIR}/postgres/daily -type d -maxdepth 1 2>/dev/null | wc -l)
- Weekly backups: $(find ${BACKUP_BASE_DIR}/postgres/weekly -type d -maxdepth 1 2>/dev/null | wc -l)
- Monthly backups: $(find ${BACKUP_BASE_DIR}/postgres/monthly -type d -maxdepth 1 2>/dev/null | wc -l)

Total Backup Size: $(du -sh ${BACKUP_BASE_DIR}/postgres 2>/dev/null | cut -f1)

═══════════════════════════════════════════════════════════════
EOF

    success_message "Backup report generated: ${REPORT_FILE}"
fi

# Example 5: Clean up temporary files - تنظيف الملفات المؤقتة
info_message "Cleaning up temporary files..."
# Add cleanup logic here
# أضف منطق التنظيف هنا

# Example 6: Resume background jobs if paused - استئناف الوظائف الخلفية إذا تم إيقافها
if [ "$BACKUP_TYPE" = "monthly" ]; then
    info_message "Resuming background jobs..."
    # Add logic to resume jobs
    # أضف منطق استئناف الوظائف
fi

# Example 7: Health check - فحص الصحة
info_message "Performing post-backup health check..."
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
if docker exec "${POSTGRES_CONTAINER}" psql -U sahool -d "${DB_NAME}" -c "SELECT 1;" > /dev/null 2>&1; then
    success_message "Database health check passed"
else
    error_message "Database health check failed"
fi

# Example 8: Log to syslog - التسجيل في syslog
if command -v logger >/dev/null 2>&1; then
    logger -t sahool-backup "Backup ${STATUS}: ${BACKUP_TYPE} ${BACKUP_MODE} for ${DB_NAME}"
fi

if [ "$STATUS" = "success" ]; then
    success_message "Post-backup tasks completed successfully"
    exit 0
else
    error_message "Backup failed - check logs for details"
    exit 1
fi
