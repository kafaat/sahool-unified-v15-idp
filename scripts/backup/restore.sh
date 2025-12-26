#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Restore Script - نظام الاستعادة لمنصة سهول
# Restore from backup for PostgreSQL, Redis, NATS, and file uploads
# استعادة من النسخ الاحتياطي لقاعدة البيانات، Redis، NATS، والملفات
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration - التكوين
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment variables - تحميل متغيرات البيئة
if [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
fi

# Backup configuration - إعدادات النسخ الاحتياطي
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"

# Docker containers - حاويات Docker
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
REDIS_CONTAINER="${REDIS_CONTAINER:-sahool-redis}"
NATS_CONTAINER="${NATS_CONTAINER:-sahool-nats}"

# Database credentials - بيانات الاعتماد
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD}"
DB_NAME="${POSTGRES_DB:-sahool}"

# Colors - ألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# List available backups - عرض النسخ الاحتياطية المتاحة
list_backups() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  Available Backups - النسخ الاحتياطية المتاحة"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    if [ ! -d "${BACKUP_BASE_DIR}" ]; then
        log_error "No backup directory found - لم يتم العثور على مجلد النسخ الاحتياطي"
        exit 1
    fi

    local backups=($(find "${BACKUP_BASE_DIR}" -maxdepth 1 -type f -name "sahool_backup_*.tar.gz" | sort -r))

    if [ ${#backups[@]} -eq 0 ]; then
        log_error "No backups found - لم يتم العثور على نسخ احتياطية"
        exit 1
    fi

    local index=1
    for backup in "${backups[@]}"; do
        local basename=$(basename "$backup")
        local size=$(du -h "$backup" | cut -f1)
        local date=$(stat -c %y "$backup" | cut -d' ' -f1,2)
        echo "  [$index] $basename"
        echo "      Size: $size | Date: $date"
        echo ""
        index=$((index + 1))
    done

    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
}

# Select backup file - اختيار ملف النسخ الاحتياطي
select_backup() {
    local backup_file="$1"

    # If backup file provided as argument - إذا تم توفير الملف كمعامل
    if [ -n "${backup_file}" ]; then
        if [ -f "${backup_file}" ]; then
            echo "${backup_file}"
            return 0
        else
            log_error "Backup file not found: ${backup_file} - ملف النسخ الاحتياطي غير موجود"
            exit 1
        fi
    fi

    # Interactive selection - اختيار تفاعلي
    list_backups

    local backups=($(find "${BACKUP_BASE_DIR}" -maxdepth 1 -type f -name "sahool_backup_*.tar.gz" | sort -r))

    echo -n "Select backup number to restore (1-${#backups[@]}): "
    read -r selection

    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#backups[@]} ]; then
        log_error "Invalid selection - اختيار غير صحيح"
        exit 1
    fi

    echo "${backups[$((selection - 1))]}"
}

# Verify backup integrity - التحقق من سلامة النسخ الاحتياطي
verify_backup() {
    local backup_file="$1"

    log_info "Verifying backup integrity - التحقق من سلامة النسخة الاحتياطية"

    if ! tar -tzf "${backup_file}" > /dev/null 2>&1; then
        log_error "Backup archive is corrupted - الأرشيف تالف"
        return 1
    fi

    log_success "Backup verification successful - التحقق من السلامة نجح"
    return 0
}

# Stop services - إيقاف الخدمات
stop_services() {
    log_warning "Stopping services - إيقاف الخدمات"

    cd "${PROJECT_ROOT}"
    docker compose down || true

    log_success "Services stopped - تم إيقاف الخدمات"
}

# Start services - تشغيل الخدمات
start_services() {
    log_info "Starting services - تشغيل الخدمات"

    cd "${PROJECT_ROOT}"
    docker compose up -d postgres redis nats

    # Wait for services to be ready - انتظار جاهزية الخدمات
    log_info "Waiting for services to be ready - انتظار جاهزية الخدمات"
    sleep 10

    # Check PostgreSQL - فحص PostgreSQL
    local max_attempts=30
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker exec "${POSTGRES_CONTAINER}" pg_isready -U "${DB_USER}" > /dev/null 2>&1; then
            break
        fi
        sleep 2
        attempt=$((attempt + 1))
    done

    if [ $attempt -eq $max_attempts ]; then
        log_error "PostgreSQL failed to start - فشل بدء PostgreSQL"
        return 1
    fi

    log_success "Services started - تم تشغيل الخدمات"
}

# Restore PostgreSQL - استعادة PostgreSQL
restore_postgres() {
    local restore_dir="$1"

    log_info "Restoring PostgreSQL database - استعادة قاعدة البيانات"

    local sql_file=$(find "${restore_dir}/postgres" -name "*.sql.gz" | head -n 1)

    if [ -z "$sql_file" ]; then
        log_error "PostgreSQL backup file not found - ملف النسخ الاحتياطي غير موجود"
        return 1
    fi

    # Decompress - فك الضغط
    gunzip -k "${sql_file}"
    local decompressed_file="${sql_file%.gz}"

    # Drop and recreate database - حذف وإعادة إنشاء قاعدة البيانات
    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${DB_NAME};" postgres
    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};" postgres

    # Restore from dump - استعادة من النسخة
    cat "${decompressed_file}" | docker exec -i "${POSTGRES_CONTAINER}" pg_restore \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --verbose \
        --clean \
        --if-exists

    # Cleanup - تنظيف
    rm -f "${decompressed_file}"

    if [ $? -eq 0 ]; then
        log_success "PostgreSQL restore completed - اكتملت استعادة PostgreSQL"
    else
        log_error "PostgreSQL restore failed - فشلت استعادة PostgreSQL"
        return 1
    fi
}

# Restore Redis - استعادة Redis
restore_redis() {
    local restore_dir="$1"

    log_info "Restoring Redis data - استعادة بيانات Redis"

    local rdb_file=$(find "${restore_dir}/redis" -name "dump_*.rdb.gz" | head -n 1)

    if [ -z "$rdb_file" ]; then
        log_warning "Redis backup file not found - ملف النسخ الاحتياطي غير موجود"
        return 0
    fi

    # Decompress - فك الضغط
    gunzip -k "${rdb_file}"
    local decompressed_file="${rdb_file%.gz}"

    # Stop Redis - إيقاف Redis
    docker compose stop redis

    # Copy RDB file - نسخ ملف RDB
    docker cp "${decompressed_file}" "${REDIS_CONTAINER}:/data/dump.rdb"

    # Copy AOF file if exists - نسخ ملف AOF إن وُجد
    local aof_file=$(find "${restore_dir}/redis" -name "appendonly_*.aof.gz" | head -n 1)
    if [ -n "$aof_file" ]; then
        gunzip -k "${aof_file}"
        docker cp "${aof_file%.gz}" "${REDIS_CONTAINER}:/data/appendonly.aof"
        rm -f "${aof_file%.gz}"
    fi

    # Start Redis - تشغيل Redis
    docker compose start redis

    # Cleanup - تنظيف
    rm -f "${decompressed_file}"

    log_success "Redis restore completed - اكتملت استعادة Redis"
}

# Restore NATS JetStream - استعادة NATS JetStream
restore_nats() {
    local restore_dir="$1"

    log_info "Restoring NATS JetStream data - استعادة بيانات NATS"

    local nats_file=$(find "${restore_dir}/nats" -name "jetstream_*.tar.gz" | head -n 1)

    if [ -z "$nats_file" ]; then
        log_warning "NATS backup file not found - ملف النسخ الاحتياطي غير موجود"
        return 0
    fi

    # Stop NATS - إيقاف NATS
    docker compose stop nats

    # Clear existing data - مسح البيانات الموجودة
    docker exec "${NATS_CONTAINER}" rm -rf /data/* || true

    # Restore from backup - استعادة من النسخة
    docker cp "${nats_file}" "${NATS_CONTAINER}:/tmp/jetstream_backup.tar.gz"
    docker exec "${NATS_CONTAINER}" tar xzf /tmp/jetstream_backup.tar.gz -C /data
    docker exec "${NATS_CONTAINER}" rm /tmp/jetstream_backup.tar.gz

    # Start NATS - تشغيل NATS
    docker compose start nats

    log_success "NATS restore completed - اكتملت استعادة NATS"
}

# Restore uploaded files - استعادة الملفات المرفوعة
restore_uploads() {
    local restore_dir="$1"

    log_info "Restoring uploaded files - استعادة الملفات المرفوعة"

    local uploads_file=$(find "${restore_dir}/uploads" -name "files_*.tar.gz" | head -n 1)

    if [ -z "$uploads_file" ]; then
        log_warning "Uploads backup file not found - ملف النسخ الاحتياطي غير موجود"
        return 0
    fi

    # Extract to uploads directory - فك الضغط إلى مجلد الملفات
    local target_dir="${PROJECT_ROOT}/uploads"
    mkdir -p "${target_dir}"

    tar xzf "${uploads_file}" -C "${PROJECT_ROOT}"

    log_success "Uploads restore completed - اكتملت استعادة الملفات"
}

# Restore configuration files - استعادة ملفات التكوين
restore_config() {
    local restore_dir="$1"

    log_info "Restoring configuration files - استعادة ملفات التكوين"

    local config_file=$(find "${restore_dir}/config" -name "config_*.tar.gz" | head -n 1)

    if [ -z "$config_file" ]; then
        log_warning "Config backup file not found - ملف النسخ الاحتياطي غير موجود"
        return 0
    fi

    # Create backup of current config - نسخ احتياطي للتكوين الحالي
    local config_backup_dir="${PROJECT_ROOT}/.config_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${config_backup_dir}"
    cp -r "${PROJECT_ROOT}/infra" "${config_backup_dir}/" 2>/dev/null || true
    cp -r "${PROJECT_ROOT}/config" "${config_backup_dir}/" 2>/dev/null || true

    log_warning "Current config backed up to: ${config_backup_dir}"

    # Extract configuration - فك الضغط
    tar xzf "${config_file}" -C "${PROJECT_ROOT}"

    log_success "Configuration restore completed - اكتملت استعادة التكوين"
}

# Verify restoration - التحقق من الاستعادة
verify_restoration() {
    log_info "Verifying restoration - التحقق من الاستعادة"

    # Check PostgreSQL - فحص PostgreSQL
    if docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT COUNT(*) FROM information_schema.tables;" > /dev/null 2>&1; then
        log_success "PostgreSQL verification passed - نجح فحص PostgreSQL"
    else
        log_error "PostgreSQL verification failed - فشل فحص PostgreSQL"
        return 1
    fi

    # Check Redis - فحص Redis
    if docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" PING | grep -q "PONG"; then
        log_success "Redis verification passed - نجح فحص Redis"
    else
        log_error "Redis verification failed - فشل فحص Redis"
        return 1
    fi

    # Check NATS - فحص NATS
    if docker exec "${NATS_CONTAINER}" nats-server --signal=reload 2>/dev/null; then
        log_success "NATS verification passed - نجح فحص NATS"
    else
        log_warning "NATS verification skipped - تم تخطي فحص NATS"
    fi

    log_success "Restoration verification completed - اكتمل التحقق من الاستعادة"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Restore Process - عملية الاستعادة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local backup_file="${1:-}"
    local start_time=$(date +%s)

    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  SAHOOL Platform Restore - استعادة منصة سهول"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # Warning message - رسالة تحذير
    echo -e "${RED}⚠️  WARNING - تحذير:${NC}"
    echo "This will restore from backup and OVERWRITE current data!"
    echo "سيتم استعادة البيانات من النسخة الاحتياطية والكتابة فوق البيانات الحالية!"
    echo ""
    echo -n "Are you sure you want to continue? (yes/no): "
    read -r confirmation

    if [ "$confirmation" != "yes" ]; then
        log_info "Restore cancelled - تم إلغاء الاستعادة"
        exit 0
    fi

    # Select backup - اختيار النسخة الاحتياطية
    backup_file=$(select_backup "$backup_file")
    log_info "Selected backup: $(basename "$backup_file")"

    # Verify backup integrity - التحقق من سلامة النسخة
    if ! verify_backup "$backup_file"; then
        exit 1
    fi

    # Extract backup archive - فك ضغط الأرشيف
    local temp_dir=$(mktemp -d)
    log_info "Extracting backup to temporary directory - فك الضغط إلى مجلد مؤقت"
    tar xzf "$backup_file" -C "$temp_dir"

    local restore_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "20*" | head -n 1)

    if [ -z "$restore_dir" ]; then
        log_error "Invalid backup archive - أرشيف غير صحيح"
        rm -rf "$temp_dir"
        exit 1
    fi

    # Stop services - إيقاف الخدمات
    stop_services

    # Start infrastructure services - تشغيل خدمات البنية التحتية
    start_services

    # Perform restoration - تنفيذ الاستعادة
    local restore_failed=false

    if ! restore_postgres "$restore_dir"; then
        restore_failed=true
    fi

    if ! restore_redis "$restore_dir"; then
        restore_failed=true
    fi

    if ! restore_nats "$restore_dir"; then
        restore_failed=true
    fi

    restore_uploads "$restore_dir" || true
    restore_config "$restore_dir" || true

    # Verify restoration - التحقق من الاستعادة
    if ! verify_restoration; then
        restore_failed=true
    fi

    # Cleanup temporary directory - تنظيف المجلد المؤقت
    rm -rf "$temp_dir"

    # Calculate duration - حساب المدة
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo ""
    echo "═══════════════════════════════════════════════════════════════════"

    if [ "$restore_failed" = false ]; then
        log_success "Restore completed successfully in ${duration}s - اكتملت الاستعادة بنجاح"
        echo ""
        echo "Next steps:"
        echo "1. Start all services: cd ${PROJECT_ROOT} && docker compose up -d"
        echo "2. Verify services: make health"
        echo "3. Check application functionality"
    else
        log_error "Restore completed with errors - اكتملت الاستعادة مع أخطاء"
        echo ""
        echo "Please check the logs and verify the services manually."
    fi

    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
}

# Run main function - تشغيل الدالة الرئيسية
main "$@"
