#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Pre-Backup Hook
# خطاف ما قبل النسخ الاحتياطي
# ═══════════════════════════════════════════════════════════════════════════════
# Description: This script runs before the backup process starts
# الوصف: يتم تشغيل هذا السكريبت قبل بدء عملية النسخ الاحتياطي
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Parameters - المعاملات
BACKUP_TYPE="${1:-}"
BACKUP_MODE="${2:-}"
DB_NAME="${3:-}"

# Colors - الألوان
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# Helper functions - دوال مساعدة
info_message() {
    echo -e "${BLUE}[PRE-BACKUP] $1${NC}"
}

success_message() {
    echo -e "${GREEN}[PRE-BACKUP] ✓ $1${NC}"
}

warning_message() {
    echo -e "${YELLOW}[PRE-BACKUP] ⚠ $1${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Pre-Backup Tasks - مهام ما قبل النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

info_message "Starting pre-backup tasks..."
info_message "Backup type: ${BACKUP_TYPE}"
info_message "Backup mode: ${BACKUP_MODE}"
info_message "Database: ${DB_NAME}"

# Example 1: Check disk space - فحص مساحة القرص
info_message "Checking available disk space..."
AVAILABLE_SPACE=$(df /backups 2>/dev/null | awk 'NR==2 {print $4}' || echo "0")
REQUIRED_SPACE=1048576  # 1GB in KB
if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    warning_message "Low disk space: ${AVAILABLE_SPACE}KB available"
else
    success_message "Sufficient disk space available: ${AVAILABLE_SPACE}KB"
fi

# Example 2: Check database connections - فحص اتصالات قاعدة البيانات
info_message "Checking active database connections..."
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
if docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
    ACTIVE_CONNECTIONS=$(docker exec "${POSTGRES_CONTAINER}" psql -U sahool -t -c \
        "SELECT count(*) FROM pg_stat_activity WHERE datname='${DB_NAME}';" 2>/dev/null | xargs || echo "0")
    info_message "Active connections: ${ACTIVE_CONNECTIONS}"
else
    warning_message "PostgreSQL container not running"
fi

# Example 3: Perform VACUUM ANALYZE for better backup performance
# تنفيذ VACUUM ANALYZE لأداء أفضل للنسخ الاحتياطي
if [ "$BACKUP_TYPE" = "weekly" ] || [ "$BACKUP_TYPE" = "monthly" ]; then
    info_message "Running VACUUM ANALYZE for optimal backup performance..."
    if docker exec "${POSTGRES_CONTAINER}" psql -U sahool -d "${DB_NAME}" -c "VACUUM ANALYZE;" >> /dev/null 2>&1; then
        success_message "VACUUM ANALYZE completed"
    else
        warning_message "VACUUM ANALYZE failed (non-critical)"
    fi
fi

# Example 4: Create checkpoint for consistent backup
# إنشاء نقطة تفتيش للنسخ الاحتياطي المتسق
info_message "Creating database checkpoint..."
if docker exec "${POSTGRES_CONTAINER}" psql -U sahool -d "${DB_NAME}" -c "CHECKPOINT;" >> /dev/null 2>&1; then
    success_message "Checkpoint created"
else
    warning_message "Checkpoint creation failed (non-critical)"
fi

# Example 5: Log backup start to monitoring system
# تسجيل بدء النسخ الاحتياطي في نظام المراقبة
info_message "Logging backup start to monitoring system..."
# Add your monitoring/logging integration here
# أضف تكامل المراقبة/التسجيل هنا
# curl -X POST http://monitoring-system/api/backup-started -d "{\"database\":\"${DB_NAME}\",\"type\":\"${BACKUP_TYPE}\"}"

# Example 6: Optional - Pause non-critical background jobs
# اختياري - إيقاف الوظائف الخلفية غير الحرجة مؤقتاً
if [ "$BACKUP_TYPE" = "monthly" ]; then
    info_message "Considering pausing background jobs for monthly backup..."
    # Add logic to pause jobs if needed
    # أضف منطق إيقاف الوظائف إذا لزم الأمر
fi

success_message "Pre-backup tasks completed successfully"
exit 0
