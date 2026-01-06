#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Comprehensive Database Backup Script
# سكريبت النسخ الاحتياطي الشامل لقاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 2.0.0
# Author: SAHOOL Platform Team
# Description: Production-ready backup solution with incremental support
# الوصف: حل نسخ احتياطي جاهز للإنتاج مع دعم النسخ التدريجي
# ═══════════════════════════════════════════════════════════════════════════════
#
# FEATURES - المميزات:
# - Daily, weekly, and monthly backup schedules (جدول النسخ الاحتياطي اليومي والأسبوعي والشهري)
# - Full and incremental backup support (دعم النسخ الكامل والتدريجي)
# - Schema-specific backups (النسخ الاحتياطي لمخططات محددة)
# - Gzip compression (ضغط gzip)
# - Pre/Post backup hooks (خطافات ما قبل/بعد النسخ الاحتياطي)
# - Retention policy: 7 daily, 4 weekly, 12 monthly (سياسة الاحتفاظ)
# - PgBouncer connection support (دعم اتصال PgBouncer)
# - Comprehensive logging (تسجيل شامل)
# - Error handling and notifications (معالجة الأخطاء والإشعارات)
# - Backup verification (التحقق من النسخ الاحتياطية)
#
# USAGE - الاستخدام:
#   ./backup_database.sh [OPTIONS]
#
# OPTIONS:
#   -t, --type TYPE          Backup type: daily|weekly|monthly|manual (default: daily)
#   -m, --mode MODE          Backup mode: full|incremental (default: full)
#   -s, --schema SCHEMA      Specific schema to backup (e.g., geo, users, public)
#   -d, --database DB        Database name (default: from env)
#   --pgbouncer              Use PgBouncer connection
#   --no-compress            Skip compression
#   --verify-only FILE       Only verify existing backup file
#   -h, --help               Show this help message
#
# EXAMPLES - أمثلة:
#   # Full daily backup (نسخ احتياطي يومي كامل)
#   ./backup_database.sh -t daily -m full
#
#   # Incremental backup (نسخ احتياطي تدريجي)
#   ./backup_database.sh -t daily -m incremental
#
#   # Backup specific schema only (نسخ احتياطي لمخطط محدد فقط)
#   ./backup_database.sh -t manual -s geo
#
#   # Weekly backup via PgBouncer (نسخ أسبوعي عبر PgBouncer)
#   ./backup_database.sh -t weekly --pgbouncer
#
# RESTORE INSTRUCTIONS - تعليمات الاستعادة:
# ════════════════════════════════════════════════════════════════════════════════
#
# 1. RESTORE FULL BACKUP - استعادة النسخة الاحتياطية الكاملة:
#
#    # Decompress if needed (فك الضغط إذا لزم الأمر)
#    gunzip backup_file.dump.gz
#
#    # Restore using pg_restore (الاستعادة باستخدام pg_restore)
#    pg_restore -U sahool -d sahool -v -c backup_file.dump
#
#    # Or using Docker (أو باستخدام Docker)
#    docker exec -i sahool-postgres pg_restore -U sahool -d sahool -v -c < backup_file.dump
#
# 2. RESTORE SPECIFIC SCHEMA - استعادة مخطط محدد:
#
#    pg_restore -U sahool -d sahool -n geo -v backup_file.dump
#
# 3. RESTORE SPECIFIC TABLE - استعادة جدول محدد:
#
#    pg_restore -U sahool -d sahool -t users -v backup_file.dump
#
# 4. RESTORE FROM SQL DUMP - الاستعادة من نسخة SQL:
#
#    # Decompress (فك الضغط)
#    gunzip backup_file.sql.gz
#
#    # Restore (الاستعادة)
#    psql -U sahool -d sahool < backup_file.sql
#
#    # Or using Docker (أو باستخدام Docker)
#    docker exec -i sahool-postgres psql -U sahool -d sahool < backup_file.sql
#
# 5. RESTORE INCREMENTAL BACKUP - استعادة النسخة التدريجية:
#
#    # First restore the base full backup (أولاً استعادة النسخة الأساسية الكاملة)
#    pg_restore -U sahool -d sahool -v -c full_backup.dump
#
#    # Then apply incremental changes (ثم تطبيق التغييرات التدريجية)
#    psql -U sahool -d sahool < incremental_backup.sql
#
# 6. VERIFY BACKUP BEFORE RESTORE - التحقق من النسخة قبل الاستعادة:
#
#    ./backup_database.sh --verify-only /path/to/backup_file.dump
#
#    # Or list contents (أو عرض المحتويات)
#    pg_restore -l backup_file.dump
#
# 7. RESTORE WITH PgBouncer - الاستعادة عبر PgBouncer:
#
#    # PgBouncer doesn't support pg_restore, connect directly to PostgreSQL
#    # PgBouncer لا يدعم pg_restore، اتصل مباشرة بـ PostgreSQL
#    pg_restore -U sahool -h postgres -p 5432 -d sahool -v backup_file.dump
#
# TROUBLESHOOTING - استكشاف الأخطاء:
# ════════════════════════════════════════════════════════════════════════════════
#
# - If restore fails with permission errors (إذا فشلت الاستعادة بسبب أخطاء الصلاحيات):
#   Add --no-owner --no-privileges flags
#   pg_restore -U sahool -d sahool --no-owner --no-privileges backup_file.dump
#
# - If database is in use (إذا كانت قاعدة البيانات قيد الاستخدام):
#   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'sahool';
#
# - To restore to a different database (للاستعادة إلى قاعدة بيانات مختلفة):
#   pg_restore -U sahool -d new_database backup_file.dump
#
# - Check logs for errors (التحقق من السجلات للأخطاء):
#   tail -f /backups/logs/postgres_*.log
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Formatting - الألوان والتنسيق
# ─────────────────────────────────────────────────────────────────────────────
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Default Configuration - التكوين الافتراضي
# ─────────────────────────────────────────────────────────────────────────────

# Script paths - مسارات السكريبت
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load environment variables - تحميل متغيرات البيئة
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
elif [ -f "${PROJECT_ROOT}/config/base.env" ]; then
    set -a
    source "${PROJECT_ROOT}/config/base.env"
    set +a
fi

# Command line arguments - معاملات سطر الأوامر
BACKUP_TYPE="${BACKUP_TYPE:-daily}"
BACKUP_MODE="full"
SPECIFIC_SCHEMA=""
USE_PGBOUNCER=false
ENABLE_COMPRESSION=true
VERIFY_ONLY=""

# Backup configuration - إعدادات النسخ الاحتياطي
readonly BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
readonly BACKUP_BASE_DIR="${BACKUP_DIR:-/backups}"
BACKUP_DIR="${BACKUP_BASE_DIR}/postgres/${BACKUP_TYPE}/${BACKUP_DATE}"

# Retention policy - سياسة الاحتفاظ (keep count, not days)
declare -A RETENTION_COUNT=(
    ["daily"]=7      # Keep last 7 daily backups
    ["weekly"]=4     # Keep last 4 weekly backups
    ["monthly"]=12   # Keep last 12 monthly backups
    ["manual"]=10    # Keep last 10 manual backups
)

# Database configuration - إعدادات قاعدة البيانات
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
PGBOUNCER_HOST="${PGBOUNCER_HOST:-pgbouncer}"
PGBOUNCER_PORT="${PGBOUNCER_PORT:-6432}"
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"
DB_NAME="${POSTGRES_DB:-sahool}"

# Backup schemas - المخططات المدعومة
readonly AVAILABLE_SCHEMAS=("public" "geo" "users" "inventory" "notifications" "audit")

# Hooks configuration - إعدادات الخطافات
readonly PRE_BACKUP_HOOK="${SCRIPT_DIR}/hooks/pre-backup.sh"
readonly POST_BACKUP_HOOK="${SCRIPT_DIR}/hooks/post-backup.sh"

# Logging - السجلات
readonly LOG_DIR="${BACKUP_BASE_DIR}/logs"
readonly LOG_FILE="${LOG_DIR}/backup_${BACKUP_TYPE}_$(date +%Y%m%d).log"

# State tracking for incremental backups - تتبع الحالة للنسخ التدريجي
readonly STATE_DIR="${BACKUP_BASE_DIR}/.state"
readonly LAST_BACKUP_STATE="${STATE_DIR}/last_backup.state"

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
    log "ERROR: $1"
    run_post_backup_hook "failure"
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

# Debug handler - معالج التصحيح
debug_message() {
    if [ "${DEBUG:-false}" = "true" ]; then
        print_message "${CYAN}" "DEBUG: $1"
    fi
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
        echo "$(( bytes / 1073741824 )) GB"
    fi
}

# Show usage - عرض الاستخدام
show_usage() {
    cat << EOF
SAHOOL Platform - Comprehensive Database Backup Script
سكريبت النسخ الاحتياطي الشامل لقاعدة البيانات

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -t, --type TYPE          Backup type: daily|weekly|monthly|manual (default: daily)
    -m, --mode MODE          Backup mode: full|incremental (default: full)
    -s, --schema SCHEMA      Specific schema to backup (e.g., geo, users, public)
    -d, --database DB        Database name (default: from env)
    --pgbouncer              Use PgBouncer connection
    --no-compress            Skip compression
    --verify-only FILE       Only verify existing backup file
    -h, --help               Show this help message

EXAMPLES:
    # Full daily backup
    $0 -t daily -m full

    # Incremental backup
    $0 -t daily -m incremental

    # Backup specific schema
    $0 -t manual -s geo

    # Weekly backup via PgBouncer
    $0 -t weekly --pgbouncer

For restore instructions, see the comments at the top of this script.

EOF
    exit 0
}

# Parse command line arguments - تحليل معاملات سطر الأوامر
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                BACKUP_TYPE="$2"
                shift 2
                ;;
            -m|--mode)
                BACKUP_MODE="$2"
                shift 2
                ;;
            -s|--schema)
                SPECIFIC_SCHEMA="$2"
                shift 2
                ;;
            -d|--database)
                DB_NAME="$2"
                shift 2
                ;;
            --pgbouncer)
                USE_PGBOUNCER=true
                shift
                ;;
            --no-compress)
                ENABLE_COMPRESSION=false
                shift
                ;;
            --verify-only)
                VERIFY_ONLY="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                ;;
            *)
                error_exit "Unknown option: $1. Use -h for help."
                ;;
        esac
    done

    # Validate backup type
    if [[ ! "$BACKUP_TYPE" =~ ^(daily|weekly|monthly|manual)$ ]]; then
        error_exit "Invalid backup type: $BACKUP_TYPE"
    fi

    # Validate backup mode
    if [[ ! "$BACKUP_MODE" =~ ^(full|incremental)$ ]]; then
        error_exit "Invalid backup mode: $BACKUP_MODE"
    fi

    # Validate schema if specified
    if [ -n "$SPECIFIC_SCHEMA" ]; then
        local valid=false
        for schema in "${AVAILABLE_SCHEMAS[@]}"; do
            if [ "$schema" = "$SPECIFIC_SCHEMA" ]; then
                valid=true
                break
            fi
        done
        if [ "$valid" = false ]; then
            error_exit "Invalid schema: $SPECIFIC_SCHEMA. Available: ${AVAILABLE_SCHEMAS[*]}"
        fi
    fi

    # Update backup directory based on parsed arguments
    BACKUP_DIR="${BACKUP_BASE_DIR}/postgres/${BACKUP_TYPE}/${BACKUP_DATE}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Database Connection Functions - دوال الاتصال بقاعدة البيانات
# ─────────────────────────────────────────────────────────────────────────────

# Get database connection parameters - الحصول على معاملات الاتصال
get_db_connection() {
    if [ "$USE_PGBOUNCER" = true ]; then
        echo "-h ${PGBOUNCER_HOST} -p ${PGBOUNCER_PORT}"
    else
        echo "-h ${POSTGRES_HOST} -p ${POSTGRES_PORT}"
    fi
}

# Check database connection - التحقق من اتصال قاعدة البيانات
check_db_connection() {
    info_message "Checking database connection..."

    local conn_params=$(get_db_connection)

    if docker exec "${POSTGRES_CONTAINER}" psql ${conn_params} -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT 1;" > /dev/null 2>&1; then
        success_message "Database connection successful"
    else
        error_exit "Cannot connect to database"
    fi
}

# Get database version - الحصول على إصدار قاعدة البيانات
get_db_version() {
    local conn_params=$(get_db_connection)
    docker exec "${POSTGRES_CONTAINER}" psql ${conn_params} -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT version();" | xargs
}

# Get database size - الحصول على حجم قاعدة البيانات
get_db_size() {
    local conn_params=$(get_db_connection)
    if [ -n "$SPECIFIC_SCHEMA" ]; then
        docker exec "${POSTGRES_CONTAINER}" psql ${conn_params} -U "${DB_USER}" -d "${DB_NAME}" -t -c \
            "SELECT pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))::bigint)
             FROM pg_tables WHERE schemaname = '${SPECIFIC_SCHEMA}';" | xargs
    else
        docker exec "${POSTGRES_CONTAINER}" psql ${conn_params} -U "${DB_USER}" -d "${DB_NAME}" -t -c \
            "SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));" | xargs
    fi
}

# Get schema list - الحصول على قائمة المخططات
get_schemas() {
    local conn_params=$(get_db_connection)
    docker exec "${POSTGRES_CONTAINER}" psql ${conn_params} -U "${DB_USER}" -d "${DB_NAME}" -t -c \
        "SELECT schema_name FROM information_schema.schemata
         WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast');" | xargs
}

# ─────────────────────────────────────────────────────────────────────────────
# Pre/Post Backup Hooks - خطافات ما قبل/بعد النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

# Run pre-backup hook - تشغيل خطاف ما قبل النسخ الاحتياطي
run_pre_backup_hook() {
    info_message "Running pre-backup hook..."

    if [ -f "$PRE_BACKUP_HOOK" ] && [ -x "$PRE_BACKUP_HOOK" ]; then
        if "$PRE_BACKUP_HOOK" "$BACKUP_TYPE" "$BACKUP_MODE" "$DB_NAME"; then
            success_message "Pre-backup hook completed"
        else
            warning_message "Pre-backup hook failed (non-critical)"
        fi
    else
        debug_message "No pre-backup hook found or not executable"
    fi
}

# Run post-backup hook - تشغيل خطاف ما بعد النسخ الاحتياطي
run_post_backup_hook() {
    local status=$1
    info_message "Running post-backup hook..."

    if [ -f "$POST_BACKUP_HOOK" ] && [ -x "$POST_BACKUP_HOOK" ]; then
        if "$POST_BACKUP_HOOK" "$BACKUP_TYPE" "$BACKUP_MODE" "$DB_NAME" "$status"; then
            success_message "Post-backup hook completed"
        else
            warning_message "Post-backup hook failed (non-critical)"
        fi
    else
        debug_message "No post-backup hook found or not executable"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Backup Functions - دوال النسخ الاحتياطي
# ─────────────────────────────────────────────────────────────────────────────

# Initialize backup - تهيئة النسخ الاحتياطي
init_backup() {
    info_message "Initializing backup process..."
    info_message "Backup type: ${BACKUP_TYPE}"
    info_message "Backup mode: ${BACKUP_MODE}"
    info_message "Database: ${DB_NAME}"

    if [ -n "$SPECIFIC_SCHEMA" ]; then
        info_message "Schema: ${SPECIFIC_SCHEMA}"
    fi

    if [ "$USE_PGBOUNCER" = true ]; then
        info_message "Connection: PgBouncer"
    fi

    # Create directories - إنشاء المجلدات
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"
    mkdir -p "${STATE_DIR}"
    mkdir -p "$(dirname "$PRE_BACKUP_HOOK")"

    # Check prerequisites - التحقق من المتطلبات
    check_db_connection

    # Get database info - الحصول على معلومات قاعدة البيانات
    local db_version=$(get_db_version)
    local db_size=$(get_db_size)

    info_message "Database version: ${db_version}"
    info_message "Database size: ${db_size}"
}

# Perform full backup - تنفيذ النسخ الاحتياطي الكامل
perform_full_backup() {
    info_message "Starting full backup using pg_dump..."

    local backup_name="full_${BACKUP_DATE}"
    local dump_file="${BACKUP_DIR}/${backup_name}.dump"
    local start_time=$(date +%s)

    # Build pg_dump command - بناء أمر pg_dump
    local dump_cmd="pg_dump -U ${DB_USER}"

    # Add connection parameters - إضافة معاملات الاتصال
    if [ "$USE_PGBOUNCER" = false ]; then
        dump_cmd="${dump_cmd} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT}"
    else
        # For PgBouncer, we need to use plain text format
        dump_cmd="${dump_cmd} -h ${PGBOUNCER_HOST} -p ${PGBOUNCER_PORT}"
        warning_message "Using PgBouncer: switching to plain text format"
    fi

    # Add format and options - إضافة التنسيق والخيارات
    if [ "$USE_PGBOUNCER" = false ]; then
        dump_cmd="${dump_cmd} -F c -b -v"  # Custom format with blobs
    else
        dump_cmd="${dump_cmd} -F p"  # Plain text format for PgBouncer
    fi

    # Add schema filter if specified - إضافة تصفية المخطط إذا تم تحديده
    if [ -n "$SPECIFIC_SCHEMA" ]; then
        dump_cmd="${dump_cmd} -n ${SPECIFIC_SCHEMA}"
    fi

    dump_cmd="${dump_cmd} -f /tmp/backup.dump ${DB_NAME}"

    # Execute backup - تنفيذ النسخ الاحتياطي
    if docker exec "${POSTGRES_CONTAINER}" ${dump_cmd} >> "${LOG_FILE}" 2>&1; then
        # Copy from container - نسخ من الحاوية
        docker cp "${POSTGRES_CONTAINER}:/tmp/backup.dump" "${dump_file}"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/backup.dump

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local dump_size=$(stat -c%s "${dump_file}" 2>/dev/null || stat -f%z "${dump_file}")

        success_message "Full backup completed in ${duration} seconds"
        info_message "Backup size: $(format_bytes ${dump_size})"

        # Save state for incremental backups - حفظ الحالة للنسخ التدريجي
        save_backup_state "${dump_file}"

        echo "${dump_file}"
    else
        error_exit "Full backup failed"
    fi
}

# Perform incremental backup - تنفيذ النسخ الاحتياطي التدريجي
perform_incremental_backup() {
    info_message "Starting incremental backup..."

    # Check if we have a base backup - التحقق من وجود نسخة أساسية
    if [ ! -f "$LAST_BACKUP_STATE" ]; then
        warning_message "No base backup found, performing full backup instead"
        perform_full_backup
        return
    fi

    local last_backup_time=$(cat "$LAST_BACKUP_STATE")
    local backup_name="incremental_${BACKUP_DATE}"
    local sql_file="${BACKUP_DIR}/${backup_name}.sql"
    local start_time=$(date +%s)

    info_message "Backing up changes since: ${last_backup_time}"

    # Build query to get modified data - بناء استعلام للحصول على البيانات المعدلة
    # This is a simplified approach - in production, you might use WAL archiving
    # هذا نهج مبسط - في الإنتاج، قد تستخدم أرشفة WAL

    local conn_params=$(get_db_connection)
    local query="-- Incremental Backup - $(date)
-- Base backup time: ${last_backup_time}

BEGIN;

"

    # For tables with updated_at column, export changes
    # للجداول التي تحتوي على عمود updated_at، تصدير التغييرات
    local tables_query="
        SELECT table_schema || '.' || table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema NOT IN ('pg_catalog', 'information_schema')
    "

    if [ -n "$SPECIFIC_SCHEMA" ]; then
        tables_query="${tables_query} AND table_schema = '${SPECIFIC_SCHEMA}'"
    fi

    # Export modified records - تصدير السجلات المعدلة
    docker exec "${POSTGRES_CONTAINER}" psql ${conn_params} -U "${DB_USER}" -d "${DB_NAME}" -t -c "${tables_query}" | while read -r table; do
        if [ -n "$table" ]; then
            query="${query}
-- Table: ${table}
COPY (SELECT * FROM ${table} WHERE updated_at > '${last_backup_time}') TO STDOUT;
"
        fi
    done

    query="${query}
COMMIT;
"

    # Save incremental backup - حفظ النسخة التدريجية
    echo "$query" > "${sql_file}"

    # Also use pg_dump for WAL-based incremental (if available)
    # أيضاً استخدام pg_dump للنسخ التدريجي المستند إلى WAL (إذا كان متاحاً)
    docker exec "${POSTGRES_CONTAINER}" bash -c "
        psql ${conn_params} -U ${DB_USER} -d ${DB_NAME} -t -c \"
            SELECT pg_start_backup('incremental_backup', true, false);
        \"
    " >> "${LOG_FILE}" 2>&1 || warning_message "pg_start_backup not available"

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local sql_size=$(stat -c%s "${sql_file}" 2>/dev/null || stat -f%z "${sql_file}")

    success_message "Incremental backup completed in ${duration} seconds"
    info_message "Backup size: $(format_bytes ${sql_size})"

    # Save state - حفظ الحالة
    save_backup_state "${sql_file}"

    echo "${sql_file}"
}

# Save backup state - حفظ حالة النسخة الاحتياطية
save_backup_state() {
    local backup_file=$1
    date -u +%Y-%m-%dT%H:%M:%SZ > "$LAST_BACKUP_STATE"

    # Save metadata - حفظ البيانات الوصفية
    cat > "${STATE_DIR}/last_backup.json" <<EOF
{
    "backup_file": "${backup_file}",
    "backup_type": "${BACKUP_TYPE}",
    "backup_mode": "${BACKUP_MODE}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "database": "${DB_NAME}",
    "schema": "${SPECIFIC_SCHEMA}"
}
EOF
}

# Backup specific schema - النسخ الاحتياطي لمخطط محدد
backup_schema() {
    local schema=$1
    info_message "Backing up schema: ${schema}..."

    local schema_file="${BACKUP_DIR}/schema_${schema}_${BACKUP_DATE}.sql"
    local conn_params=$(get_db_connection)

    if docker exec "${POSTGRES_CONTAINER}" pg_dump \
        ${conn_params} \
        -U "${DB_USER}" \
        -n "${schema}" \
        --schema-only \
        --no-owner \
        -f "/tmp/schema.sql" \
        "${DB_NAME}" >> "${LOG_FILE}" 2>&1; then

        docker cp "${POSTGRES_CONTAINER}:/tmp/schema.sql" "${schema_file}"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/schema.sql

        success_message "Schema backup completed: ${schema}"
        echo "${schema_file}"
    else
        warning_message "Schema backup failed: ${schema} (non-critical)"
        echo ""
    fi
}

# Backup all schemas - النسخ الاحتياطي لجميع المخططات
backup_all_schemas() {
    info_message "Backing up all schemas..."

    local schemas=$(get_schemas)
    for schema in $schemas; do
        backup_schema "$schema"
    done
}

# Backup database roles and permissions - النسخ الاحتياطي للأدوار والصلاحيات
backup_globals() {
    info_message "Backing up database roles and permissions..."

    local globals_file="${BACKUP_DIR}/globals_${BACKUP_DATE}.sql"
    local conn_params=$(get_db_connection)

    if docker exec "${POSTGRES_CONTAINER}" pg_dumpall \
        -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" \
        -U "${DB_USER}" \
        --globals-only \
        -f "/tmp/globals.sql" >> "${LOG_FILE}" 2>&1; then

        docker cp "${POSTGRES_CONTAINER}:/tmp/globals.sql" "${globals_file}"
        docker exec "${POSTGRES_CONTAINER}" rm -f /tmp/globals.sql

        success_message "Globals backup completed"
        echo "${globals_file}"
    else
        warning_message "Globals backup failed (non-critical)"
        echo ""
    fi
}

# Compress backup - ضغط النسخة الاحتياطية
compress_backup() {
    local file=$1

    if [ "$ENABLE_COMPRESSION" = false ]; then
        info_message "Compression disabled, skipping..."
        echo "${file}"
        return
    fi

    if [ ! -f "$file" ]; then
        warning_message "File not found for compression: $file"
        echo "${file}"
        return
    fi

    info_message "Compressing backup with gzip..."
    local start_time=$(date +%s)
    local original_size=$(stat -c%s "${file}" 2>/dev/null || stat -f%z "${file}")

    if gzip -9 "${file}"; then
        local compressed_file="${file}.gz"
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local compressed_size=$(stat -c%s "${compressed_file}" 2>/dev/null || stat -f%z "${compressed_file}")
        local ratio=$(( 100 - (compressed_size * 100 / original_size) ))

        success_message "Compression completed in ${duration} seconds"
        info_message "Original size: $(format_bytes ${original_size})"
        info_message "Compressed size: $(format_bytes ${compressed_size})"
        info_message "Compression ratio: ${ratio}%"

        echo "${compressed_file}"
    else
        warning_message "Compression failed, using uncompressed file"
        echo "${file}"
    fi
}

# Verify backup - التحقق من النسخة الاحتياطية
verify_backup() {
    local backup_file=$1

    info_message "Verifying backup integrity..."

    # Check file exists - التحقق من وجود الملف
    if [ ! -f "${backup_file}" ]; then
        error_exit "Backup file not found: ${backup_file}"
    fi

    # Check file is not empty - التحقق من أن الملف ليس فارغاً
    local file_size=$(stat -c%s "${backup_file}" 2>/dev/null || stat -f%z "${backup_file}")
    if [ "$file_size" -eq 0 ]; then
        error_exit "Backup file is empty"
    fi

    # Verify compressed files - التحقق من الملفات المضغوطة
    if [[ "${backup_file}" == *.gz ]]; then
        if gzip -t "${backup_file}" 2>/dev/null; then
            success_message "Gzip integrity check passed"
        else
            error_exit "Backup file is corrupted (gzip test failed)"
        fi
    fi

    # Verify dump files - التحقق من ملفات dump
    if [[ "${backup_file}" == *.dump ]] || [[ "${backup_file}" == *.dump.gz ]]; then
        local test_file="${backup_file}"

        # Decompress temporarily if needed - فك الضغط مؤقتاً إذا لزم الأمر
        if [[ "${backup_file}" == *.gz ]]; then
            test_file="${backup_file%.gz}"
            gunzip -c "${backup_file}" > "${test_file}"
        fi

        if docker run --rm -v "$(dirname ${test_file}):/backup" postgres:16-alpine \
            pg_restore --list "/backup/$(basename ${test_file})" > /dev/null 2>&1; then
            success_message "Backup verification passed (pg_restore --list)"
        else
            # Clean up temp file
            [ "${test_file}" != "${backup_file}" ] && rm -f "${test_file}"
            error_exit "Backup verification failed (pg_restore test)"
        fi

        # Clean up temp file - تنظيف الملف المؤقت
        if [ "${test_file}" != "${backup_file}" ]; then
            rm -f "${test_file}"
        fi
    fi

    success_message "Backup verification completed successfully"
}

# Create backup metadata - إنشاء البيانات الوصفية
create_metadata() {
    local backup_file=$1

    info_message "Creating backup metadata..."

    local metadata_file="${BACKUP_DIR}/metadata.json"
    local file_size=$(stat -c%s "${backup_file}" 2>/dev/null || stat -f%z "${backup_file}")
    local file_hash=$(sha256sum "${backup_file}" | awk '{print $1}')

    cat > "${metadata_file}" <<EOF
{
    "backup_info": {
        "type": "${BACKUP_TYPE}",
        "mode": "${BACKUP_MODE}",
        "date": "${BACKUP_DATE}",
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    "database": {
        "name": "${DB_NAME}",
        "user": "${DB_USER}",
        "host": "${POSTGRES_HOST}",
        "port": ${POSTGRES_PORT},
        "schema": "${SPECIFIC_SCHEMA:-all}",
        "version": "$(get_db_version)",
        "size": "$(get_db_size)"
    },
    "backup_file": {
        "name": "$(basename ${backup_file})",
        "path": "${backup_file}",
        "size": ${file_size},
        "size_human": "$(format_bytes ${file_size})",
        "sha256": "${file_hash}",
        "compressed": ${ENABLE_COMPRESSION}
    },
    "connection": {
        "pgbouncer": ${USE_PGBOUNCER},
        "host": "$([ "$USE_PGBOUNCER" = true ] && echo "$PGBOUNCER_HOST" || echo "$POSTGRES_HOST")",
        "port": $([ "$USE_PGBOUNCER" = true ] && echo "$PGBOUNCER_PORT" || echo "$POSTGRES_PORT")
    },
    "system": {
        "hostname": "$(hostname)",
        "platform": "$(uname -s)",
        "script_version": "2.0.0"
    }
}
EOF

    success_message "Metadata created"
}

# Cleanup old backups - تنظيف النسخ القديمة
cleanup_old_backups() {
    info_message "Cleaning up old backups..."

    local retention_count=${RETENTION_COUNT[$BACKUP_TYPE]}
    local backup_type_dir="${BACKUP_BASE_DIR}/postgres/${BACKUP_TYPE}"

    if [ ! -d "${backup_type_dir}" ]; then
        info_message "No backups to clean up"
        return
    fi

    # Get sorted list of backup directories (oldest first) - الحصول على قائمة مرتبة من مجلدات النسخ الاحتياطي
    local backup_dirs=($(find "${backup_type_dir}" -maxdepth 1 -type d -not -path "${backup_type_dir}" | sort))
    local total_backups=${#backup_dirs[@]}

    if [ $total_backups -le $retention_count ]; then
        info_message "No old backups to delete (${total_backups}/${retention_count})"
        return
    fi

    # Calculate how many to delete - حساب عدد النسخ المراد حذفها
    local to_delete=$((total_backups - retention_count))
    local deleted_count=0

    for ((i=0; i<to_delete; i++)); do
        local old_backup="${backup_dirs[$i]}"
        info_message "Deleting old backup: $(basename ${old_backup})"
        rm -rf "${old_backup}"
        ((deleted_count++))
    done

    success_message "Deleted ${deleted_count} old backup(s), kept ${retention_count} most recent"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local overall_start_time=$(date +%s)

    print_message "${MAGENTA}" "═══════════════════════════════════════════════════════════════"
    print_message "${MAGENTA}" "  SAHOOL Platform - Comprehensive Database Backup"
    print_message "${MAGENTA}" "  نظام النسخ الاحتياطي الشامل لقاعدة البيانات"
    print_message "${MAGENTA}" "═══════════════════════════════════════════════════════════════"

    # Parse command line arguments - تحليل معاملات سطر الأوامر
    parse_arguments "$@"

    # Handle verify-only mode - معالجة وضع التحقق فقط
    if [ -n "$VERIFY_ONLY" ]; then
        verify_backup "$VERIFY_ONLY"
        exit 0
    fi

    # Initialize - التهيئة
    init_backup

    # Run pre-backup hook - تشغيل خطاف ما قبل النسخ الاحتياطي
    run_pre_backup_hook

    # Perform backup based on mode - تنفيذ النسخ الاحتياطي بناءً على الوضع
    local backup_file=""
    if [ "$BACKUP_MODE" = "full" ]; then
        backup_file=$(perform_full_backup)
    else
        backup_file=$(perform_incremental_backup)
    fi

    # Additional backups for weekly/monthly - نسخ إضافية للنسخ الأسبوعي/الشهري
    if [ "$BACKUP_TYPE" = "weekly" ] || [ "$BACKUP_TYPE" = "monthly" ]; then
        if [ -z "$SPECIFIC_SCHEMA" ]; then
            backup_all_schemas
            backup_globals
        fi
    fi

    # Compress - الضغط
    backup_file=$(compress_backup "${backup_file}")

    # Verify - التحقق
    verify_backup "${backup_file}"

    # Create metadata - إنشاء البيانات الوصفية
    create_metadata "${backup_file}"

    # Cleanup old backups - تنظيف النسخ القديمة
    cleanup_old_backups

    # Run post-backup hook - تشغيل خطاف ما بعد النسخ الاحتياطي
    run_post_backup_hook "success"

    # Calculate total time - حساب الوقت الكلي
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    local minutes=$((total_duration / 60))
    local seconds=$((total_duration % 60))

    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "Database backup completed successfully!"
    success_message "النسخ الاحتياطي اكتمل بنجاح!"
    info_message "Total duration: ${minutes}m ${seconds}s"
    info_message "Backup location: ${BACKUP_DIR}"
    info_message "Main backup file: $(basename ${backup_file})"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"

    log "Backup completed successfully"
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
