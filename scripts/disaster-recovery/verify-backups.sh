#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Comprehensive Backup Verification Script
# سكريبت التحقق الشامل من النسخ الاحتياطية
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Automated verification of all backup types and disaster recovery readiness
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# Backup configuration
BACKUP_BASE_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
VERIFICATION_DIR="/tmp/sahool-backup-verification-$(date +%s)"
LOG_DIR="${PROJECT_ROOT}/logs/backup-verification"
LOG_FILE="${LOG_DIR}/verify_$(date +%Y%m%d_%H%M%S).log"

# Create directories
mkdir -p "${VERIFICATION_DIR}"
mkdir -p "${LOG_DIR}"

# Verification results
declare -A VERIFICATION_RESULTS
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "${LOG_FILE}"
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_FILE}"
}

info_message() {
    print_message "${BLUE}" "ℹ $1"
}

success_message() {
    print_message "${GREEN}" "✓ $1"
}

warning_message() {
    print_message "${YELLOW}" "⚠ $1"
}

error_message() {
    print_message "${RED}" "✗ $1"
}

# Record verification result
record_result() {
    local check_name="$1"
    local status="$2"  # PASS, FAIL, WARN
    local message="${3:-}"

    ((TOTAL_CHECKS++))
    VERIFICATION_RESULTS["$check_name"]="${status}:${message}"

    case "$status" in
        PASS)
            ((PASSED_CHECKS++))
            success_message "${check_name}: ${message}"
            ;;
        FAIL)
            ((FAILED_CHECKS++))
            error_message "${check_name}: ${message}"
            ;;
        WARN)
            warning_message "${check_name}: ${message}"
            ;;
    esac
}

# ─────────────────────────────────────────────────────────────────────────────
# PostgreSQL Backup Verification
# ─────────────────────────────────────────────────────────────────────────────

verify_postgres_backups() {
    info_message "Verifying PostgreSQL backups..."

    local backup_dir="${BACKUP_BASE_DIR}/postgres/daily"

    # Check 1: Backup directory exists
    if [ ! -d "$backup_dir" ]; then
        record_result "postgres_backup_directory" "FAIL" "Backup directory not found"
        return 1
    fi
    record_result "postgres_backup_directory" "PASS" "Directory exists"

    # Check 2: Find most recent backup
    local recent_backup=$(find "$backup_dir" -type d -name "2*" | sort -r | head -1)
    if [ -z "$recent_backup" ]; then
        record_result "postgres_recent_backup" "FAIL" "No recent backups found"
        return 1
    fi
    record_result "postgres_recent_backup" "PASS" "Found: $(basename $recent_backup)"

    # Check 3: Verify backup age (should be < 25 hours for daily)
    local backup_age_hours=$(( ($(date +%s) - $(stat -c %Y "$recent_backup")) / 3600 ))
    if [ "$backup_age_hours" -gt 25 ]; then
        record_result "postgres_backup_age" "WARN" "${backup_age_hours}h old (expected <25h)"
    else
        record_result "postgres_backup_age" "PASS" "${backup_age_hours}h old"
    fi

    # Check 4: Verify dump file exists
    local dump_file=$(find "$recent_backup" -name "*.dump*" | head -1)
    if [ -z "$dump_file" ]; then
        record_result "postgres_dump_file" "FAIL" "No dump file found"
        return 1
    fi
    record_result "postgres_dump_file" "PASS" "Found: $(basename $dump_file)"

    # Check 5: Verify file size (should be > 1MB for non-empty database)
    local file_size=$(stat -c %s "$dump_file" 2>/dev/null || echo 0)
    if [ "$file_size" -lt 1048576 ]; then
        record_result "postgres_dump_size" "WARN" "File size is ${file_size} bytes (<1MB)"
    else
        local size_mb=$((file_size / 1048576))
        record_result "postgres_dump_size" "PASS" "${size_mb} MB"
    fi

    # Check 6: Verify metadata file exists
    if [ -f "${recent_backup}/metadata.json" ]; then
        record_result "postgres_metadata" "PASS" "Metadata exists"

        # Verify metadata integrity
        if jq . "${recent_backup}/metadata.json" >/dev/null 2>&1; then
            record_result "postgres_metadata_valid" "PASS" "Valid JSON"
        else
            record_result "postgres_metadata_valid" "FAIL" "Invalid JSON"
        fi
    else
        record_result "postgres_metadata" "FAIL" "Metadata not found"
    fi

    # Check 7: Test restore capability (if not in production)
    if [ "${ENABLE_RESTORE_TEST:-false}" = "true" ]; then
        info_message "Testing PostgreSQL restore capability..."

        # Create temporary database for restore test
        local test_db="sahool_restore_test_$(date +%s)"

        if docker exec postgres-primary createdb -U postgres "$test_db" 2>/dev/null; then
            # Extract dump file if compressed
            local test_dump="$dump_file"
            if [[ "$dump_file" == *.gz ]]; then
                gunzip -c "$dump_file" > "${VERIFICATION_DIR}/test.dump"
                test_dump="${VERIFICATION_DIR}/test.dump"
            elif [[ "$dump_file" == *.zst ]]; then
                zstd -d "$dump_file" -o "${VERIFICATION_DIR}/test.dump"
                test_dump="${VERIFICATION_DIR}/test.dump"
            fi

            # Copy dump to container
            docker cp "$test_dump" postgres-primary:/tmp/restore_test.dump

            # Attempt restore
            if docker exec postgres-primary pg_restore \
                -U postgres -d "$test_db" \
                -F c /tmp/restore_test.dump \
                --no-owner --no-privileges \
                >/dev/null 2>&1; then

                # Verify restore
                local table_count=$(docker exec postgres-primary psql -U postgres -d "$test_db" -t -c \
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | xargs)

                record_result "postgres_restore_test" "PASS" "Restored ${table_count} tables"
            else
                record_result "postgres_restore_test" "FAIL" "Restore failed"
            fi

            # Cleanup
            docker exec postgres-primary dropdb -U postgres "$test_db" 2>/dev/null || true
            docker exec postgres-primary rm -f /tmp/restore_test.dump 2>/dev/null || true
        else
            record_result "postgres_restore_test" "WARN" "Could not create test database"
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# WAL Archive Verification
# ─────────────────────────────────────────────────────────────────────────────

verify_wal_archive() {
    info_message "Verifying WAL archive..."

    # Check 1: WAL archive directory exists
    local wal_dir="/var/lib/postgresql/wal-archive"
    if docker exec postgres-primary test -d "$wal_dir" 2>/dev/null; then
        record_result "wal_archive_directory" "PASS" "Directory exists"
    else
        record_result "wal_archive_directory" "WARN" "WAL archive directory not found"
        return 0
    fi

    # Check 2: WAL files present
    local wal_count=$(docker exec postgres-primary sh -c "ls -1 $wal_dir 2>/dev/null | wc -l" || echo 0)
    if [ "$wal_count" -gt 0 ]; then
        record_result "wal_files_present" "PASS" "${wal_count} WAL files"
    else
        record_result "wal_files_present" "WARN" "No WAL files found"
    fi

    # Check 3: Recent WAL activity (files modified in last hour)
    local recent_wal=$(docker exec postgres-primary sh -c \
        "find $wal_dir -type f -mmin -60 2>/dev/null | wc -l" || echo 0)
    if [ "$recent_wal" -gt 0 ]; then
        record_result "wal_recent_activity" "PASS" "${recent_wal} files in last hour"
    else
        record_result "wal_recent_activity" "WARN" "No recent WAL activity"
    fi

    # Check 4: S3/MinIO WAL backup
    if [ "${S3_BACKUP_ENABLED:-false}" = "true" ]; then
        if command -v aws >/dev/null 2>&1; then
            local s3_wal_count=$(aws s3 ls "s3://${S3_BUCKET:-sahool-backups}/wal-archive/" \
                --endpoint-url "${S3_ENDPOINT:-}" --recursive 2>/dev/null | wc -l || echo 0)
            if [ "$s3_wal_count" -gt 0 ]; then
                record_result "wal_s3_backup" "PASS" "${s3_wal_count} files in S3"
            else
                record_result "wal_s3_backup" "WARN" "No WAL files in S3"
            fi
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Redis Backup Verification
# ─────────────────────────────────────────────────────────────────────────────

verify_redis_backups() {
    info_message "Verifying Redis backups..."

    local backup_dir="${BACKUP_BASE_DIR}/redis/daily"

    # Check 1: Backup directory exists
    if [ ! -d "$backup_dir" ]; then
        record_result "redis_backup_directory" "FAIL" "Backup directory not found"
        return 1
    fi
    record_result "redis_backup_directory" "PASS" "Directory exists"

    # Check 2: Find most recent backup
    local recent_backup=$(find "$backup_dir" -type d -name "2*" | sort -r | head -1)
    if [ -z "$recent_backup" ]; then
        record_result "redis_recent_backup" "FAIL" "No recent backups found"
        return 1
    fi

    local backup_age_hours=$(( ($(date +%s) - $(stat -c %Y "$recent_backup")) / 3600 ))
    record_result "redis_recent_backup" "PASS" "Found: $(basename $recent_backup) (${backup_age_hours}h old)"

    # Check 3: Verify RDB file
    if [ -f "${recent_backup}/dump.rdb" ]; then
        local rdb_size=$(stat -c %s "${recent_backup}/dump.rdb")
        record_result "redis_rdb_file" "PASS" "RDB size: $((rdb_size/1024)) KB"
    else
        record_result "redis_rdb_file" "WARN" "No RDB file found"
    fi

    # Check 4: Verify AOF file
    if [ -f "${recent_backup}/appendonly.aof" ]; then
        local aof_size=$(stat -c %s "${recent_backup}/appendonly.aof")
        record_result "redis_aof_file" "PASS" "AOF size: $((aof_size/1024)) KB"
    else
        record_result "redis_aof_file" "WARN" "No AOF file found"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# MinIO Backup Verification
# ─────────────────────────────────────────────────────────────────────────────

verify_minio_backups() {
    info_message "Verifying MinIO backups..."

    local backup_dir="${BACKUP_BASE_DIR}/minio/daily"

    if [ ! -d "$backup_dir" ]; then
        record_result "minio_backup_directory" "WARN" "Backup directory not found"
        return 0
    fi
    record_result "minio_backup_directory" "PASS" "Directory exists"

    # Find most recent backup
    local recent_backup=$(find "$backup_dir" -type d -name "2*" | sort -r | head -1)
    if [ -n "$recent_backup" ]; then
        local backup_age_hours=$(( ($(date +%s) - $(stat -c %Y "$recent_backup")) / 3600 ))
        record_result "minio_recent_backup" "PASS" "Found: $(basename $recent_backup) (${backup_age_hours}h old)"

        # Check backup size
        local backup_size=$(du -sb "$recent_backup" | awk '{print $1}')
        record_result "minio_backup_size" "PASS" "$((backup_size/1048576)) MB"
    else
        record_result "minio_recent_backup" "WARN" "No recent backups found"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Cross-Region Replication Verification
# ─────────────────────────────────────────────────────────────────────────────

verify_cross_region_replication() {
    info_message "Verifying cross-region replication..."

    if [ "${S3_BACKUP_ENABLED:-false}" != "true" ]; then
        record_result "cross_region_config" "WARN" "S3 backup not enabled"
        return 0
    fi

    # Check primary bucket replication configuration
    if command -v aws >/dev/null 2>&1; then
        local primary_bucket="${S3_BUCKET:-sahool-backups}"

        if aws s3api get-bucket-replication --bucket "$primary_bucket" \
            --endpoint-url "${S3_ENDPOINT:-}" >/dev/null 2>&1; then
            record_result "s3_replication_config" "PASS" "Replication configured"
        else
            record_result "s3_replication_config" "WARN" "No replication configuration"
        fi

        # Verify secondary region bucket exists
        local secondary_bucket="${S3_SECONDARY_BUCKET:-sahool-backups-replica}"
        if aws s3 ls "s3://${secondary_bucket}" \
            --endpoint-url "${S3_SECONDARY_ENDPOINT:-}" >/dev/null 2>&1; then
            record_result "s3_secondary_bucket" "PASS" "Secondary bucket exists"
        else
            record_result "s3_secondary_bucket" "WARN" "Secondary bucket not accessible"
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# RTO/RPO Compliance Check
# ─────────────────────────────────────────────────────────────────────────────

verify_rto_rpo_compliance() {
    info_message "Verifying RTO/RPO compliance..."

    # RPO Check: Backup freshness
    local postgres_backup_dir="${BACKUP_BASE_DIR}/postgres/daily"
    if [ -d "$postgres_backup_dir" ]; then
        local recent_backup=$(find "$postgres_backup_dir" -type d -name "2*" | sort -r | head -1)
        if [ -n "$recent_backup" ]; then
            local backup_age_hours=$(( ($(date +%s) - $(stat -c %Y "$recent_backup")) / 3600 ))

            # RPO target: 1 hour (but daily backups give 24h RPO without PITR)
            if [ "$backup_age_hours" -le 24 ]; then
                record_result "rpo_compliance" "PASS" "Last backup ${backup_age_hours}h ago (within 24h)"
            else
                record_result "rpo_compliance" "FAIL" "Last backup ${backup_age_hours}h ago (exceeds 24h)"
            fi
        fi
    fi

    # RTO Check: Verify restore scripts exist
    local restore_script="${PROJECT_ROOT}/scripts/backup/restore_postgres.sh"
    if [ -x "$restore_script" ]; then
        record_result "rto_restore_script" "PASS" "Restore script available"
    else
        record_result "rto_restore_script" "FAIL" "Restore script not found or not executable"
    fi

    # HA Check: Verify replication is active
    if docker exec postgres-primary psql -U postgres -t -c \
        "SELECT COUNT(*) FROM pg_stat_replication;" 2>/dev/null | grep -q "[1-9]"; then
        record_result "ha_replication_active" "PASS" "Replication active"
    else
        record_result "ha_replication_active" "WARN" "No active replication (higher RPO)"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Generate Report
# ─────────────────────────────────────────────────────────────────────────────

generate_report() {
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  Backup Verification Report"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Create JSON report
    local report_file="${LOG_DIR}/verification_report_$(date +%Y%m%d_%H%M%S).json"

    cat > "$report_file" <<EOF
{
    "verification_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "total_checks": ${TOTAL_CHECKS},
    "passed_checks": ${PASSED_CHECKS},
    "failed_checks": ${FAILED_CHECKS},
    "success_rate": $(awk "BEGIN {printf \"%.2f\", (${PASSED_CHECKS}/${TOTAL_CHECKS})*100}"),
    "results": {
EOF

    local first=true
    for check in "${!VERIFICATION_RESULTS[@]}"; do
        IFS=':' read -r status message <<< "${VERIFICATION_RESULTS[$check]}"

        if [ "$first" = false ]; then
            echo "," >> "$report_file"
        fi
        first=false

        cat >> "$report_file" <<EOF
        "${check}": {
            "status": "${status}",
            "message": "${message}"
        }
EOF
    done

    cat >> "$report_file" <<EOF

    }
}
EOF

    echo ""
    info_message "Total Checks: ${TOTAL_CHECKS}"
    success_message "Passed: ${PASSED_CHECKS}"
    error_message "Failed: ${FAILED_CHECKS}"
    echo ""
    info_message "Success Rate: $(awk "BEGIN {printf \"%.2f\", (${PASSED_CHECKS}/${TOTAL_CHECKS})*100}")%"
    info_message "Report saved to: ${report_file}"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Cleanup
    rm -rf "${VERIFICATION_DIR}"

    if [ "$FAILED_CHECKS" -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

main() {
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  SAHOOL Platform - Backup Verification Suite"
    print_message "${BLUE}" "  مجموعة التحقق من النسخ الاحتياطية"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    # Run all verification checks
    verify_postgres_backups
    verify_wal_archive
    verify_redis_backups
    verify_minio_backups
    verify_cross_region_replication
    verify_rto_rpo_compliance

    # Generate report
    echo ""
    generate_report
}

main "$@"
