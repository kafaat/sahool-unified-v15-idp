#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Disaster Recovery Failover Test Script
# سكريبت اختبار التبديل التلقائي للتعافي من الكوارث
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Automated DR testing for PostgreSQL cluster
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

# Test configuration
TEST_TYPE="${1:-full}"  # full, basic, comprehensive
DRY_RUN="${DRY_RUN:-false}"

# Logging
LOG_DIR="${PROJECT_ROOT}/logs/dr-tests"
LOG_FILE="${LOG_DIR}/dr_test_$(date +%Y%m%d_%H%M%S).log"
RESULTS_FILE="${LOG_DIR}/dr_test_results_$(date +%Y%m%d_%H%M%S).json"
mkdir -p "${LOG_DIR}"

# Test results tracking
declare -A TEST_RESULTS
TEST_START_TIME=$(date +%s)

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

# Record test result
record_test_result() {
    local test_name="$1"
    local status="$2"  # PASS, FAIL, SKIP
    local duration="$3"
    local message="${4:-}"

    TEST_RESULTS["${test_name}"]="${status}|${duration}|${message}"

    if [ "$status" = "PASS" ]; then
        success_message "${test_name}: PASSED (${duration}s)"
    elif [ "$status" = "FAIL" ]; then
        error_message "${test_name}: FAILED - ${message}"
    else
        warning_message "${test_name}: SKIPPED - ${message}"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Test Functions
# ─────────────────────────────────────────────────────────────────────────────

# Test 1: Cluster Status Check
test_cluster_status() {
    local test_name="cluster_status_check"
    local start_time=$(date +%s)

    info_message "Test 1: Checking cluster status..."

    if ${SCRIPT_DIR}/failover-postgres.sh status > /dev/null 2>&1; then
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "PASS" "$duration"
        return 0
    else
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "FAIL" "$duration" "Unable to get cluster status"
        return 1
    fi
}

# Test 2: Primary Health Check
test_primary_health() {
    local test_name="primary_health_check"
    local start_time=$(date +%s)

    info_message "Test 2: Checking primary node health..."

    if ${SCRIPT_DIR}/failover-postgres.sh check; then
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "PASS" "$duration"
        return 0
    else
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "FAIL" "$duration" "Primary node is unhealthy"
        return 1
    fi
}

# Test 3: Replication Lag Check
test_replication_lag() {
    local test_name="replication_lag_check"
    local start_time=$(date +%s)

    info_message "Test 3: Checking replication lag..."

    # Get cluster status and check lag
    local status=$(${SCRIPT_DIR}/failover-postgres.sh status 2>/dev/null)
    local max_lag=$(echo "$status" | jq -r '.members[] | select(.role == "replica") | .lag' | sort -n | tail -1)

    if [ -z "$max_lag" ]; then
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "SKIP" "$duration" "No replicas found"
        return 0
    fi

    # Check if lag is acceptable (< 10MB)
    local lag_bytes=$(echo "$max_lag" | sed 's/[^0-9]//g')
    if [ "$lag_bytes" -lt 10485760 ]; then
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "PASS" "$duration" "Max lag: ${max_lag}"
        return 0
    else
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "FAIL" "$duration" "Excessive lag: ${max_lag}"
        return 1
    fi
}

# Test 4: Database Connectivity
test_database_connectivity() {
    local test_name="database_connectivity"
    local start_time=$(date +%s)

    info_message "Test 4: Testing database connectivity..."

    # Test connection via HAProxy
    if docker exec sahool-postgres-haproxy nc -z localhost 5432 > /dev/null 2>&1; then
        # Try a simple query
        if docker exec sahool-postgres-primary psql -U postgres -c "SELECT 1" > /dev/null 2>&1; then
            local duration=$(($(date +%s) - start_time))
            record_test_result "$test_name" "PASS" "$duration"
            return 0
        fi
    fi

    local duration=$(($(date +%s) - start_time))
    record_test_result "$test_name" "FAIL" "$duration" "Cannot connect to database"
    return 1
}

# Test 5: Write Test
test_write_operations() {
    local test_name="write_operations"
    local start_time=$(date +%s)

    info_message "Test 5: Testing write operations..."

    local test_table="dr_test_$(date +%s)"

    # Create test table and insert data
    if docker exec sahool-postgres-primary psql -U postgres -c "
        CREATE TABLE IF NOT EXISTS ${test_table} (id SERIAL PRIMARY KEY, data TEXT, created_at TIMESTAMP DEFAULT NOW());
        INSERT INTO ${test_table} (data) VALUES ('test_data_1'), ('test_data_2'), ('test_data_3');
        SELECT COUNT(*) FROM ${test_table};
    " > /dev/null 2>&1; then
        # Clean up
        docker exec sahool-postgres-primary psql -U postgres -c "DROP TABLE ${test_table};" > /dev/null 2>&1

        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "PASS" "$duration"
        return 0
    else
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "FAIL" "$duration" "Write operations failed"
        return 1
    fi
}

# Test 6: Simulated Failover Test
test_simulated_failover() {
    local test_name="simulated_failover"
    local start_time=$(date +%s)

    if [ "$DRY_RUN" = "true" ]; then
        record_test_result "$test_name" "SKIP" "0" "Dry run mode"
        return 0
    fi

    info_message "Test 6: Testing failover mechanism..."
    warning_message "This will perform an actual switchover!"

    # Get current primary
    local old_primary=$(${SCRIPT_DIR}/failover-postgres.sh status 2>/dev/null | jq -r '.members[] | select(.role == "leader") | .name')
    info_message "Current primary: ${old_primary}"

    # Perform switchover
    if ${SCRIPT_DIR}/failover-postgres.sh switchover > /dev/null 2>&1; then
        sleep 10  # Wait for switchover to complete

        # Verify new primary
        local new_primary=$(${SCRIPT_DIR}/failover-postgres.sh status 2>/dev/null | jq -r '.members[] | select(.role == "leader") | .name')

        if [ "$new_primary" != "$old_primary" ]; then
            info_message "New primary: ${new_primary}"

            # Switchback to original primary
            info_message "Switching back to original primary..."
            ${SCRIPT_DIR}/failover-postgres.sh switchover "$old_primary" > /dev/null 2>&1
            sleep 10

            local duration=$(($(date +%s) - start_time))
            record_test_result "$test_name" "PASS" "$duration" "Failover completed in ${duration}s"
            return 0
        fi
    fi

    local duration=$(($(date +%s) - start_time))
    record_test_result "$test_name" "FAIL" "$duration" "Failover mechanism failed"
    return 1
}

# Test 7: WAL Archive Check
test_wal_archive() {
    local test_name="wal_archive_check"
    local start_time=$(date +%s)

    info_message "Test 7: Checking WAL archiving..."

    # Check if WAL archive directory exists and has files
    local wal_count=$(docker exec sahool-postgres-primary sh -c 'ls -1 /var/lib/postgresql/wal-archive 2>/dev/null | wc -l' || echo "0")

    if [ "$wal_count" -gt 0 ]; then
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "PASS" "$duration" "Found ${wal_count} WAL files"
        return 0
    else
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "FAIL" "$duration" "No WAL files found in archive"
        return 1
    fi
}

# Test 8: Backup Recovery Test
test_backup_recovery() {
    local test_name="backup_recovery_test"
    local start_time=$(date +%s)

    info_message "Test 8: Testing backup recovery capability..."

    # Check if recent backups exist
    local backup_dir="${PROJECT_ROOT}/backups/postgres/daily"
    if [ ! -d "$backup_dir" ]; then
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "SKIP" "$duration" "No backup directory found"
        return 0
    fi

    local recent_backup=$(find "$backup_dir" -type d -mtime -1 | head -1)
    if [ -n "$recent_backup" ]; then
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "PASS" "$duration" "Recent backup found"
        return 0
    else
        local duration=$(($(date +%s) - start_time))
        record_test_result "$test_name" "FAIL" "$duration" "No recent backup found (< 24h)"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Report Generation
# ─────────────────────────────────────────────────────────────────────────────

generate_report() {
    local end_time=$(date +%s)
    local total_duration=$((end_time - TEST_START_TIME))

    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  DR Test Results Summary"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local skipped_tests=0

    # Generate JSON report
    cat > "${RESULTS_FILE}" <<EOF
{
    "test_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "test_type": "${TEST_TYPE}",
    "total_duration_seconds": ${total_duration},
    "results": {
EOF

    local first=true
    for test_name in "${!TEST_RESULTS[@]}"; do
        IFS='|' read -r status duration message <<< "${TEST_RESULTS[$test_name]}"

        ((total_tests++))

        case "$status" in
            PASS) ((passed_tests++)) ;;
            FAIL) ((failed_tests++)) ;;
            SKIP) ((skipped_tests++)) ;;
        esac

        if [ "$first" = false ]; then
            echo "," >> "${RESULTS_FILE}"
        fi
        first=false

        cat >> "${RESULTS_FILE}" <<EOF
        "${test_name}": {
            "status": "${status}",
            "duration_seconds": ${duration},
            "message": "${message}"
        }
EOF
    done

    cat >> "${RESULTS_FILE}" <<EOF

    },
    "summary": {
        "total": ${total_tests},
        "passed": ${passed_tests},
        "failed": ${failed_tests},
        "skipped": ${skipped_tests},
        "success_rate": $(awk "BEGIN {printf \"%.2f\", (${passed_tests}/${total_tests})*100}")
    }
}
EOF

    # Print summary
    echo ""
    info_message "Total Tests: ${total_tests}"
    success_message "Passed: ${passed_tests}"
    error_message "Failed: ${failed_tests}"
    warning_message "Skipped: ${skipped_tests}"
    echo ""
    info_message "Success Rate: $(awk "BEGIN {printf \"%.2f\", (${passed_tests}/${total_tests})*100}")%"
    info_message "Total Duration: ${total_duration}s"
    echo ""
    info_message "Results saved to: ${RESULTS_FILE}"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    if [ "$failed_tests" -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

main() {
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  SAHOOL Platform - DR Failover Test Suite"
    print_message "${BLUE}" "  مجموعة اختبارات التعافي من الكوارث"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    info_message "Test Type: ${TEST_TYPE}"
    if [ "$DRY_RUN" = "true" ]; then
        warning_message "Running in DRY RUN mode (no actual failover)"
    fi
    echo ""

    # Run tests based on test type
    case "$TEST_TYPE" in
        basic)
            test_cluster_status
            test_primary_health
            test_database_connectivity
            ;;

        full|*)
            test_cluster_status
            test_primary_health
            test_replication_lag
            test_database_connectivity
            test_write_operations
            test_wal_archive
            test_backup_recovery
            ;;

        comprehensive)
            test_cluster_status
            test_primary_health
            test_replication_lag
            test_database_connectivity
            test_write_operations
            test_simulated_failover
            test_wal_archive
            test_backup_recovery
            ;;
    esac

    echo ""
    generate_report
}

main "$@"
