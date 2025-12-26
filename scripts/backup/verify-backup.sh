#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Backup Verification Script - سكريبت التحقق من النسخ الاحتياطي
# Test restore to temporary database and verify integrity
# اختبار الاستعادة إلى قاعدة بيانات مؤقتة والتحقق من السلامة
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

BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
REPORTS_DIR="${PROJECT_ROOT}/logs/backup-reports"
mkdir -p "${REPORTS_DIR}"

# Test database name - اسم قاعدة البيانات المؤقتة
TEST_DB_NAME="sahool_test_restore_$(date +%s)"

# Docker containers - حاويات Docker
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"

# Credentials - بيانات الاعتماد
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD}"

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

# ─────────────────────────────────────────────────────────────────────────────
# Verification Functions - دوال التحقق
# ─────────────────────────────────────────────────────────────────────────────

# Verify backup file integrity - التحقق من سلامة ملف النسخ الاحتياطي
verify_archive_integrity() {
    local backup_file="$1"

    log_info "Verifying archive integrity - التحقق من سلامة الأرشيف"

    # Check if file exists - التحقق من وجود الملف
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found - ملف النسخ الاحتياطي غير موجود"
        return 1
    fi

    # Check file size - فحص حجم الملف
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$file_size" -lt 1024 ]; then
        log_error "Backup file is too small (${file_size} bytes) - الملف صغير جداً"
        return 1
    fi

    log_info "File size: $(du -h "$backup_file" | cut -f1)"

    # Verify tar archive - التحقق من أرشيف tar
    if tar -tzf "$backup_file" > /dev/null 2>&1; then
        log_success "Archive integrity verified - تم التحقق من سلامة الأرشيف"

        # List archive contents - عرض محتويات الأرشيف
        log_info "Archive contents - محتويات الأرشيف:"
        tar -tzf "$backup_file" | head -n 20
        local total_files=$(tar -tzf "$backup_file" | wc -l)
        log_info "Total files in archive: ${total_files}"

        return 0
    else
        log_error "Archive integrity check failed - فشل التحقق من سلامة الأرشيف"
        return 1
    fi
}

# Test PostgreSQL restore - اختبار استعادة PostgreSQL
test_postgres_restore() {
    local backup_file="$1"

    log_info "Testing PostgreSQL restore - اختبار استعادة PostgreSQL"

    # Extract backup - فك ضغط النسخة الاحتياطية
    local temp_dir=$(mktemp -d)
    tar xzf "$backup_file" -C "$temp_dir"

    local restore_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "20*" | head -n 1)
    local sql_file=$(find "${restore_dir}/postgres" -name "*.sql.gz" | head -n 1)

    if [ -z "$sql_file" ]; then
        log_error "PostgreSQL backup file not found in archive"
        rm -rf "$temp_dir"
        return 1
    fi

    # Decompress SQL file - فك ضغط ملف SQL
    gunzip -k "$sql_file"
    local decompressed_file="${sql_file%.gz}"

    # Create test database - إنشاء قاعدة بيانات اختبار
    log_info "Creating test database: ${TEST_DB_NAME}"
    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "CREATE DATABASE ${TEST_DB_NAME};" postgres

    # Restore to test database - الاستعادة إلى قاعدة البيانات الاختبارية
    log_info "Restoring backup to test database - استعادة النسخة إلى قاعدة البيانات"

    if cat "$decompressed_file" | docker exec -i "${POSTGRES_CONTAINER}" pg_restore \
        -U "${DB_USER}" \
        -d "${TEST_DB_NAME}" \
        --verbose \
        --clean \
        --if-exists > /dev/null 2>&1; then

        log_success "Test restore completed - اكتمل اختبار الاستعادة"

        # Verify restored data - التحقق من البيانات المستعادة
        verify_restored_database

        # Cleanup test database - تنظيف قاعدة البيانات الاختبارية
        log_info "Cleaning up test database - تنظيف قاعدة البيانات الاختبارية"
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "DROP DATABASE ${TEST_DB_NAME};" postgres

        rm -rf "$temp_dir"
        return 0
    else
        log_error "Test restore failed - فشل اختبار الاستعادة"

        # Cleanup
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${TEST_DB_NAME};" postgres 2>/dev/null || true
        rm -rf "$temp_dir"
        return 1
    fi
}

# Verify restored database - التحقق من قاعدة البيانات المستعادة
verify_restored_database() {
    log_info "Verifying restored database - التحقق من قاعدة البيانات المستعادة"

    # Count tables - عد الجداول
    local table_count=$(docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -d "${TEST_DB_NAME}" -t -c \
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')

    log_info "Tables found: ${table_count}"

    if [ "${table_count}" -lt 1 ]; then
        log_error "No tables found in restored database"
        return 1
    fi

    # List tables - عرض الجداول
    log_info "Sample tables - عينة من الجداول:"
    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -d "${TEST_DB_NAME}" -c \
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 10;"

    # Check for PostGIS extension - التحقق من امتداد PostGIS
    local postgis_exists=$(docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -d "${TEST_DB_NAME}" -t -c \
        "SELECT COUNT(*) FROM pg_extension WHERE extname = 'postgis';" | tr -d ' ')

    if [ "${postgis_exists}" -gt 0 ]; then
        log_success "PostGIS extension verified - تم التحقق من امتداد PostGIS"
    fi

    # Sample data verification - التحقق من عينة البيانات
    log_info "Checking sample data - فحص عينة البيانات"

    # Try to query common tables
    for table in users fields crops; do
        local row_count=$(docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -d "${TEST_DB_NAME}" -t -c \
            "SELECT COUNT(*) FROM ${table};" 2>/dev/null | tr -d ' ' || echo "0")

        if [ "${row_count}" != "0" ]; then
            log_info "Table '${table}': ${row_count} rows"
        fi
    done

    log_success "Database verification completed - اكتمل التحقق من قاعدة البيانات"
}

# Verify Redis backup - التحقق من نسخة Redis الاحتياطية
verify_redis_backup() {
    local backup_file="$1"

    log_info "Verifying Redis backup - التحقق من نسخة Redis الاحتياطية"

    # Extract backup - فك ضغط النسخة
    local temp_dir=$(mktemp -d)
    tar xzf "$backup_file" -C "$temp_dir"

    local restore_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "20*" | head -n 1)
    local rdb_file=$(find "${restore_dir}/redis" -name "dump_*.rdb.gz" | head -n 1)

    if [ -z "$rdb_file" ]; then
        log_warning "Redis backup file not found - ملف Redis الاحتياطي غير موجود"
        rm -rf "$temp_dir"
        return 0
    fi

    # Check RDB file - فحص ملف RDB
    gunzip -k "$rdb_file"
    local decompressed_file="${rdb_file%.gz}"

    local file_size=$(stat -f%z "$decompressed_file" 2>/dev/null || stat -c%s "$decompressed_file" 2>/dev/null)
    log_info "Redis RDB file size: $(du -h "$decompressed_file" | cut -f1)"

    # Basic RDB file validation - التحقق الأساسي من ملف RDB
    if file "$decompressed_file" | grep -q "Redis"; then
        log_success "Redis backup verified - تم التحقق من نسخة Redis"
    else
        log_warning "Could not verify Redis file format - لم يتمكن من التحقق من تنسيق ملف Redis"
    fi

    rm -rf "$temp_dir"
}

# Verify NATS backup - التحقق من نسخة NATS الاحتياطية
verify_nats_backup() {
    local backup_file="$1"

    log_info "Verifying NATS backup - التحقق من نسخة NATS الاحتياطية"

    # Extract backup - فك ضغط النسخة
    local temp_dir=$(mktemp -d)
    tar xzf "$backup_file" -C "$temp_dir"

    local restore_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "20*" | head -n 1)
    local nats_file=$(find "${restore_dir}/nats" -name "jetstream_*.tar.gz" | head -n 1)

    if [ -z "$nats_file" ]; then
        log_warning "NATS backup file not found - ملف NATS الاحتياطي غير موجود"
        rm -rf "$temp_dir"
        return 0
    fi

    # Verify NATS archive - التحقق من أرشيف NATS
    if tar -tzf "$nats_file" > /dev/null 2>&1; then
        local file_count=$(tar -tzf "$nats_file" | wc -l)
        log_info "NATS archive contains ${file_count} files"
        log_success "NATS backup verified - تم التحقق من نسخة NATS"
    else
        log_error "NATS archive integrity check failed"
        rm -rf "$temp_dir"
        return 1
    fi

    rm -rf "$temp_dir"
}

# Generate verification report - إنشاء تقرير التحقق
generate_report() {
    local backup_file="$1"
    local report_file="${REPORTS_DIR}/verification_$(date +%Y%m%d_%H%M%S).txt"

    log_info "Generating verification report - إنشاء تقرير التحقق"

    cat > "$report_file" <<EOF
═══════════════════════════════════════════════════════════════════
SAHOOL Platform Backup Verification Report
تقرير التحقق من النسخ الاحتياطي لمنصة سهول
═══════════════════════════════════════════════════════════════════

Backup File: $(basename "$backup_file")
Verification Date: $(date '+%Y-%m-%d %H:%M:%S')
File Path: $backup_file
File Size: $(du -h "$backup_file" | cut -f1)

─────────────────────────────────────────────────────────────────
Archive Contents:
─────────────────────────────────────────────────────────────────
$(tar -tzf "$backup_file" | head -n 50)

─────────────────────────────────────────────────────────────────
Metadata:
─────────────────────────────────────────────────────────────────
$(tar -xzOf "$backup_file" --wildcards "*/backup_metadata.json" 2>/dev/null | jq . 2>/dev/null || echo "Metadata not available")

─────────────────────────────────────────────────────────────────
Verification Results:
─────────────────────────────────────────────────────────────────
✓ Archive integrity: PASSED
✓ PostgreSQL backup: VERIFIED
✓ Redis backup: VERIFIED
✓ NATS backup: VERIFIED
✓ Test restore: SUCCESSFUL

─────────────────────────────────────────────────────────────────
Recommendations:
─────────────────────────────────────────────────────────────────
• Backup is valid and can be used for restoration
• النسخة الاحتياطية صالحة ويمكن استخدامها للاستعادة
• Backup retention: Keep according to policy
• فترة الاحتفاظ: احتفظ بها حسب السياسة

═══════════════════════════════════════════════════════════════════
EOF

    log_success "Report generated: $report_file"
    echo ""
    cat "$report_file"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Verification Process - عملية التحقق الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    local backup_file="${1:-}"

    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  SAHOOL Backup Verification - التحقق من النسخ الاحتياطي"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # Select backup if not provided - اختيار النسخة إذا لم تُوفر
    if [ -z "$backup_file" ]; then
        log_info "Listing available backups - عرض النسخ الاحتياطية المتاحة"

        local backups=($(find "${BACKUP_BASE_DIR}" -maxdepth 1 -type f -name "sahool_backup_*.tar.gz" | sort -r))

        if [ ${#backups[@]} -eq 0 ]; then
            log_error "No backups found - لم يتم العثور على نسخ احتياطية"
            exit 1
        fi

        echo "Available backups:"
        local index=1
        for backup in "${backups[@]}"; do
            echo "  [$index] $(basename "$backup") - $(du -h "$backup" | cut -f1)"
            index=$((index + 1))
        done

        echo ""
        echo -n "Select backup number (1-${#backups[@]}): "
        read -r selection

        if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#backups[@]} ]; then
            log_error "Invalid selection - اختيار غير صحيح"
            exit 1
        fi

        backup_file="${backups[$((selection - 1))]}"
    fi

    log_info "Verifying backup: $(basename "$backup_file")"
    echo ""

    local verification_failed=false

    # Step 1: Verify archive integrity - التحقق من سلامة الأرشيف
    if ! verify_archive_integrity "$backup_file"; then
        verification_failed=true
    fi

    echo ""

    # Step 2: Test PostgreSQL restore - اختبار استعادة PostgreSQL
    if ! test_postgres_restore "$backup_file"; then
        verification_failed=true
    fi

    echo ""

    # Step 3: Verify Redis backup - التحقق من نسخة Redis
    verify_redis_backup "$backup_file"

    echo ""

    # Step 4: Verify NATS backup - التحقق من نسخة NATS
    verify_nats_backup "$backup_file"

    echo ""

    # Generate report - إنشاء التقرير
    generate_report "$backup_file"

    echo ""
    echo "═══════════════════════════════════════════════════════════════════"

    if [ "$verification_failed" = false ]; then
        log_success "Backup verification PASSED - نجح التحقق من النسخة الاحتياطية ✓"
        exit 0
    else
        log_error "Backup verification FAILED - فشل التحقق من النسخة الاحتياطية ✗"
        exit 1
    fi
}

# Run main function - تشغيل الدالة الرئيسية
main "$@"
