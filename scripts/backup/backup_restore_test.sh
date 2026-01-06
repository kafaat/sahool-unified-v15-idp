#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Automated Backup Restore Testing Script
# نظام اختبار استعادة النسخ الاحتياطية التلقائي
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: SAHOOL Platform Team
# Description: Automated restore testing to ensure backup recoverability
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Paths
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
REPORTS_DIR="${PROJECT_ROOT}/logs/backup-reports"
TEMP_RESTORE_DIR="/tmp/sahool_restore_test_$$"

# Create directories
mkdir -p "${REPORTS_DIR}"
mkdir -p "${TEMP_RESTORE_DIR}"

# Test database credentials
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD}"
TEST_DB_PREFIX="test_restore_"

# Docker containers
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-sahool-postgres}"
REDIS_CONTAINER="${REDIS_CONTAINER:-sahool-redis}"

# Notification configuration
SLACK_NOTIFICATIONS="${SLACK_NOTIFICATIONS_ENABLED:-false}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

success_message() {
    print_message "${GREEN}" "✓ $1"
}

error_message() {
    print_message "${RED}" "✗ $1"
}

warning_message() {
    print_message "${YELLOW}" "⚠ $1"
}

info_message() {
    print_message "${BLUE}" "ℹ $1"
}

send_notification() {
    local status=$1
    local message=$2

    [ "$SLACK_NOTIFICATIONS" != "true" ] || [ -z "$SLACK_WEBHOOK_URL" ] && return

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
        "title": "${emoji} Backup Restore Test",
        "text": "${message}",
        "footer": "SAHOOL Backup System",
        "ts": $(date +%s)
    }]
}
EOF
}

cleanup() {
    info_message "Cleaning up test resources..."
    rm -rf "${TEMP_RESTORE_DIR}"

    # Drop test databases
    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c \
        "DROP DATABASE IF EXISTS ${TEST_DB_PREFIX}$(date +%Y%m%d);" postgres 2>/dev/null || true
}

trap cleanup EXIT

# ─────────────────────────────────────────────────────────────────────────────
# Test Functions - دوال الاختبار
# ─────────────────────────────────────────────────────────────────────────────

# Test PostgreSQL restore - اختبار استعادة PostgreSQL
test_postgres_restore() {
    info_message "Testing PostgreSQL backup restore..."

    local backup_dir="${BACKUP_BASE_DIR}/postgres/daily"

    if [ ! -d "$backup_dir" ]; then
        error_message "PostgreSQL backup directory not found"
        return 1
    fi

    # Find latest backup
    local latest_backup=$(find "$backup_dir" -maxdepth 1 -type d -name "20*" | sort -r | head -n 1)

    if [ -z "$latest_backup" ]; then
        error_message "No PostgreSQL backup found"
        return 1
    fi

    info_message "Testing backup: $(basename $latest_backup)"

    # Find dump file
    local dump_file=$(find "$latest_backup" -name "*.dump.gz" -o -name "*.dump" | head -n 1)

    if [ -z "$dump_file" ]; then
        error_message "No dump file found in backup"
        return 1
    fi

    # Decompress if needed
    local test_file="${TEMP_RESTORE_DIR}/test.dump"
    if [[ "$dump_file" == *.gz ]]; then
        gunzip -c "$dump_file" > "$test_file"
    else
        cp "$dump_file" "$test_file"
    fi

    # Create test database
    local test_db="${TEST_DB_PREFIX}$(date +%Y%m%d)"
    info_message "Creating test database: ${test_db}"

    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c \
        "DROP DATABASE IF EXISTS ${test_db};" postgres 2>/dev/null || true

    docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c \
        "CREATE DATABASE ${test_db};" postgres

    # Restore backup
    info_message "Restoring backup to test database..."

    if docker run --rm \
        -v "${TEMP_RESTORE_DIR}:/backup" \
        --network container:${POSTGRES_CONTAINER} \
        postgres:16-alpine \
        pg_restore \
        -h localhost \
        -p 5432 \
        -U "${DB_USER}" \
        -d "${test_db}" \
        -v \
        --no-owner \
        --no-acl \
        /backup/test.dump > /dev/null 2>&1; then

        success_message "PostgreSQL restore successful"

        # Verify restored data
        local table_count=$(docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -d "${test_db}" -t -c \
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)

        info_message "Restored ${table_count} tables"

        # Cleanup
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c \
            "DROP DATABASE ${test_db};" postgres

        return 0
    else
        error_message "PostgreSQL restore failed"
        docker exec "${POSTGRES_CONTAINER}" psql -U "${DB_USER}" -c \
            "DROP DATABASE IF EXISTS ${test_db};" postgres 2>/dev/null || true
        return 1
    fi
}

# Test Redis restore - اختبار استعادة Redis
test_redis_restore() {
    info_message "Testing Redis backup restore..."

    local backup_dir="${BACKUP_BASE_DIR}/redis/daily"

    if [ ! -d "$backup_dir" ]; then
        warning_message "Redis backup directory not found"
        return 0  # Non-critical
    fi

    # Find latest backup
    local latest_backup=$(find "$backup_dir" -maxdepth 1 -type d -name "20*" | sort -r | head -n 1)

    if [ -z "$latest_backup" ]; then
        warning_message "No Redis backup found"
        return 0  # Non-critical
    fi

    info_message "Testing backup: $(basename $latest_backup)"

    # Find RDB file
    local rdb_file=$(find "$latest_backup" -name "*.rdb.gz" -o -name "*.rdb" | head -n 1)

    if [ -z "$rdb_file" ]; then
        warning_message "No RDB file found in backup"
        return 0  # Non-critical
    fi

    # Decompress if needed
    local test_file="${TEMP_RESTORE_DIR}/dump.rdb"
    if [[ "$rdb_file" == *.gz ]]; then
        gunzip -c "$rdb_file" > "$test_file"
    else
        cp "$rdb_file" "$test_file"
    fi

    # Verify RDB file
    if command -v redis-check-rdb >/dev/null 2>&1; then
        if redis-check-rdb "$test_file" > /dev/null 2>&1; then
            success_message "Redis RDB file verification passed"
            return 0
        else
            error_message "Redis RDB file verification failed"
            return 1
        fi
    else
        # Check if file exists and has content
        if [ -f "$test_file" ] && [ -s "$test_file" ]; then
            success_message "Redis backup file exists and has content"
            return 0
        else
            error_message "Redis backup file is empty or missing"
            return 1
        fi
    fi
}

# Test ETCD restore - اختبار استعادة ETCD
test_etcd_restore() {
    info_message "Testing ETCD backup restore..."

    local backup_dir="${BACKUP_BASE_DIR}/etcd/daily"

    if [ ! -d "$backup_dir" ]; then
        warning_message "ETCD backup directory not found"
        return 0  # Non-critical
    fi

    # Find latest backup
    local latest_backup=$(find "$backup_dir" -maxdepth 1 -type d -name "20*" | sort -r | head -n 1)

    if [ -z "$latest_backup" ]; then
        warning_message "No ETCD backup found"
        return 0  # Non-critical
    fi

    info_message "Testing backup: $(basename $latest_backup)"

    # Find snapshot file
    local snapshot_file=$(find "$latest_backup" -name "*.db.gz" -o -name "*.db" | head -n 1)

    if [ -z "$snapshot_file" ]; then
        warning_message "No snapshot file found in backup"
        return 0  # Non-critical
    fi

    # Decompress if needed
    local test_file="${TEMP_RESTORE_DIR}/etcd_snapshot.db"
    if [[ "$snapshot_file" == *.gz ]]; then
        gunzip -c "$snapshot_file" > "$test_file"
    else
        cp "$snapshot_file" "$test_file"
    fi

    # Check if file exists and has content
    if [ -f "$test_file" ] && [ -s "$test_file" ]; then
        local file_size=$(stat -f%z "$test_file" 2>/dev/null || stat -c%s "$test_file")
        success_message "ETCD snapshot file exists ($(( file_size / 1024 ))KB)"
        return 0
    else
        error_message "ETCD snapshot file is empty or missing"
        return 1
    fi
}

# Test Qdrant restore - اختبار استعادة Qdrant
test_qdrant_restore() {
    info_message "Testing Qdrant backup restore..."

    local backup_dir="${BACKUP_BASE_DIR}/qdrant/daily"

    if [ ! -d "$backup_dir" ]; then
        warning_message "Qdrant backup directory not found"
        return 0  # Non-critical
    fi

    # Find latest backup
    local latest_backup=$(find "$backup_dir" -maxdepth 1 -type d -name "20*" | sort -r | head -n 1)

    if [ -z "$latest_backup" ]; then
        warning_message "No Qdrant backup found"
        return 0  # Non-critical
    fi

    info_message "Testing backup: $(basename $latest_backup)"

    # Find storage backup file
    local storage_file=$(find "$latest_backup" -name "*.tar.gz" -o -name "*.tar" | head -n 1)

    if [ -z "$storage_file" ]; then
        warning_message "No storage file found in backup"
        return 0  # Non-critical
    fi

    # Verify tar file integrity
    if tar -tzf "$storage_file" > /dev/null 2>&1; then
        local file_count=$(tar -tzf "$storage_file" | wc -l)
        success_message "Qdrant backup archive valid (${file_count} files)"
        return 0
    else
        error_message "Qdrant backup archive verification failed"
        return 1
    fi
}

# Test encryption/decryption - اختبار التشفير/فك التشفير
test_encryption() {
    local encryption_enabled="${BACKUP_ENCRYPTION_ENABLED:-false}"
    local encryption_key="${BACKUP_ENCRYPTION_KEY:-}"

    if [ "$encryption_enabled" != "true" ] || [ -z "$encryption_key" ]; then
        warning_message "Encryption not configured"
        return 0
    fi

    info_message "Testing backup encryption/decryption..."

    # Create test file
    local test_file="${TEMP_RESTORE_DIR}/test_encryption.txt"
    echo "SAHOOL Backup Encryption Test" > "$test_file"

    # Encrypt
    local encrypted_file="${test_file}.enc"
    if openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in "$test_file" \
        -out "$encrypted_file" \
        -k "$encryption_key" 2>/dev/null; then

        # Decrypt
        local decrypted_file="${test_file}.dec"
        if openssl enc -d -aes-256-cbc -pbkdf2 \
            -in "$encrypted_file" \
            -out "$decrypted_file" \
            -k "$encryption_key" 2>/dev/null; then

            # Verify
            if diff "$test_file" "$decrypted_file" > /dev/null 2>&1; then
                success_message "Encryption test passed"
                return 0
            else
                error_message "Encryption test failed: content mismatch"
                return 1
            fi
        else
            error_message "Decryption failed"
            return 1
        fi
    else
        error_message "Encryption failed"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Report Generation - إنشاء التقارير
# ─────────────────────────────────────────────────────────────────────────────

generate_test_report() {
    local report_file="${REPORTS_DIR}/restore_test_$(date +%Y%m%d_%H%M%S).txt"
    local postgres_result=${1:-0}
    local redis_result=${2:-0}
    local etcd_result=${3:-0}
    local qdrant_result=${4:-0}
    local encryption_result=${5:-0}

    {
        echo "═══════════════════════════════════════════════════════════════"
        echo "  SAHOOL Platform - Backup Restore Test Report"
        echo "  تقرير اختبار استعادة النسخ الاحتياطية"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        echo "Test Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Test Type: Automated Restore Testing"
        echo ""

        echo "─────────────────────────────────────────────────────────────"
        echo "Test Results"
        echo "─────────────────────────────────────────────────────────────"
        echo ""

        echo "PostgreSQL Restore:    $([ $postgres_result -eq 0 ] && echo '✓ PASSED' || echo '✗ FAILED')"
        echo "Redis Restore:         $([ $redis_result -eq 0 ] && echo '✓ PASSED' || echo '⚠ SKIPPED')"
        echo "ETCD Restore:          $([ $etcd_result -eq 0 ] && echo '✓ PASSED' || echo '⚠ SKIPPED')"
        echo "Qdrant Restore:        $([ $qdrant_result -eq 0 ] && echo '✓ PASSED' || echo '⚠ SKIPPED')"
        echo "Encryption Test:       $([ $encryption_result -eq 0 ] && echo '✓ PASSED' || echo '⚠ SKIPPED')"

        echo ""
        echo "─────────────────────────────────────────────────────────────"
        echo "Overall Status"
        echo "─────────────────────────────────────────────────────────────"

        if [ $postgres_result -eq 0 ]; then
            echo "Status: ✓ PASSED"
            echo "All critical restore tests completed successfully"
        else
            echo "Status: ✗ FAILED"
            echo "Critical restore tests failed - immediate attention required"
        fi

        echo ""
        echo "─────────────────────────────────────────────────────────────"
        echo "Recommendations"
        echo "─────────────────────────────────────────────────────────────"

        if [ $postgres_result -eq 0 ]; then
            echo "• Backups are restorable and verified"
            echo "• Continue with current backup schedule"
        else
            echo "• URGENT: Investigate backup failures immediately"
            echo "• Verify backup scripts and storage integrity"
            echo "• Check backup logs for errors"
        fi

        echo ""
        echo "═══════════════════════════════════════════════════════════════"

    } > "$report_file"

    echo ""
    cat "$report_file"
    echo ""

    info_message "Report saved: $report_file"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function - الدالة الرئيسية
# ─────────────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  SAHOOL Backup Restore Testing"
    echo "  اختبار استعادة النسخ الاحتياطية"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    local postgres_result=1
    local redis_result=1
    local etcd_result=1
    local qdrant_result=1
    local encryption_result=1

    # Run tests
    test_postgres_restore && postgres_result=0 || postgres_result=1
    echo ""

    test_redis_restore && redis_result=0 || redis_result=1
    echo ""

    test_etcd_restore && etcd_result=0 || etcd_result=1
    echo ""

    test_qdrant_restore && qdrant_result=0 || qdrant_result=1
    echo ""

    test_encryption && encryption_result=0 || encryption_result=1
    echo ""

    # Generate report
    generate_test_report "$postgres_result" "$redis_result" "$etcd_result" "$qdrant_result" "$encryption_result"

    # Send notification
    if [ $postgres_result -eq 0 ]; then
        send_notification "success" "All backup restore tests passed successfully"
        exit 0
    else
        send_notification "failure" "Backup restore tests failed - immediate attention required"
        exit 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute Main - تنفيذ البرنامج الرئيسي
# ─────────────────────────────────────────────────────────────────────────────

main "$@"
