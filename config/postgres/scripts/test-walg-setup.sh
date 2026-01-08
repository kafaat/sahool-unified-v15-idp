#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - WAL-G Setup Test Script
# سكريبت اختبار إعداد WAL-G
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Comprehensive testing of WAL-G backup and recovery setup
# Usage: ./test-walg-setup.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_test() {
    echo -e "${YELLOW}[TEST $((TESTS_TOTAL + 1))]${NC} $1"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_failure() {
    echo -e "${RED}✗${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Test Functions
# ═══════════════════════════════════════════════════════════════════════════════

test_postgres_running() {
    print_test "Checking if PostgreSQL is running"

    if docker-compose ps postgres | grep -q "Up"; then
        print_success "PostgreSQL is running"
        return 0
    else
        print_failure "PostgreSQL is not running"
        return 1
    fi
}

test_walg_installed() {
    print_test "Checking if WAL-G is installed"

    if docker-compose exec -T postgres which wal-g >/dev/null 2>&1; then
        VERSION=$(docker-compose exec -T postgres wal-g --version 2>&1 || echo "unknown")
        print_success "WAL-G is installed (version: $VERSION)"
        return 0
    else
        print_failure "WAL-G is not installed"
        return 1
    fi
}

test_archive_mode() {
    print_test "Checking PostgreSQL archive mode"

    ARCHIVE_MODE=$(docker-compose exec -T postgres psql -U sahool -t -c "SHOW archive_mode;" 2>/dev/null | tr -d ' ')

    if [ "$ARCHIVE_MODE" = "on" ]; then
        print_success "Archive mode is enabled"
        return 0
    else
        print_failure "Archive mode is not enabled (current: $ARCHIVE_MODE)"
        return 1
    fi
}

test_archive_command() {
    print_test "Checking PostgreSQL archive command"

    ARCHIVE_CMD=$(docker-compose exec -T postgres psql -U sahool -t -c "SHOW archive_command;" 2>/dev/null)

    if echo "$ARCHIVE_CMD" | grep -q "wal-archive.sh"; then
        print_success "Archive command is configured correctly"
        print_info "Command: $ARCHIVE_CMD"
        return 0
    else
        print_failure "Archive command is not configured correctly"
        print_info "Current: $ARCHIVE_CMD"
        return 1
    fi
}

test_wal_level() {
    print_test "Checking PostgreSQL WAL level"

    WAL_LEVEL=$(docker-compose exec -T postgres psql -U sahool -t -c "SHOW wal_level;" 2>/dev/null | tr -d ' ')

    if [ "$WAL_LEVEL" = "replica" ] || [ "$WAL_LEVEL" = "logical" ]; then
        print_success "WAL level is correct ($WAL_LEVEL)"
        return 0
    else
        print_failure "WAL level is incorrect (current: $WAL_LEVEL, need: replica or logical)"
        return 1
    fi
}

test_s3_connectivity() {
    print_test "Testing S3/MinIO connectivity"

    if docker-compose exec -T postgres wal-g backup-list >/dev/null 2>&1; then
        print_success "Successfully connected to S3/MinIO"
        return 0
    else
        print_failure "Cannot connect to S3/MinIO"
        return 1
    fi
}

test_environment_variables() {
    print_test "Checking required environment variables"

    REQUIRED_VARS=(
        "WALG_S3_PREFIX"
        "AWS_ACCESS_KEY_ID"
        "AWS_SECRET_ACCESS_KEY"
        "AWS_ENDPOINT"
    )

    ALL_SET=true
    for VAR in "${REQUIRED_VARS[@]}"; do
        VALUE=$(docker-compose exec -T postgres printenv "$VAR" 2>/dev/null || echo "")
        if [ -z "$VALUE" ]; then
            print_failure "$VAR is not set"
            ALL_SET=false
        else
            print_info "$VAR is set"
        fi
    done

    if [ "$ALL_SET" = true ]; then
        print_success "All required environment variables are set"
        return 0
    else
        print_failure "Some environment variables are missing"
        return 1
    fi
}

test_wal_archiving_status() {
    print_test "Checking WAL archiving status"

    STATS=$(docker-compose exec -T postgres psql -U sahool -t -c "
        SELECT
            archived_count,
            COALESCE(failed_count, 0) as failed_count,
            last_archived_time
        FROM pg_stat_archiver;
    " 2>/dev/null)

    ARCHIVED=$(echo "$STATS" | awk '{print $1}')
    FAILED=$(echo "$STATS" | awk '{print $3}')

    if [ "$ARCHIVED" -gt 0 ]; then
        print_success "WAL archiving is active ($ARCHIVED archived, $FAILED failed)"
        return 0
    else
        print_failure "No WAL files have been archived yet"
        return 1
    fi
}

test_backup_exists() {
    print_test "Checking if base backups exist"

    BACKUP_COUNT=$(docker-compose exec -T postgres wal-g backup-list 2>/dev/null | grep -c "^base_" || echo "0")

    if [ "$BACKUP_COUNT" -gt 0 ]; then
        print_success "$BACKUP_COUNT base backup(s) found"
        docker-compose exec -T postgres wal-g backup-list 2>/dev/null | head -5
        return 0
    else
        print_failure "No base backups found"
        print_info "Create a backup with: docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data"
        return 1
    fi
}

test_local_archive_directory() {
    print_test "Checking local WAL archive directory"

    if docker-compose exec -T postgres test -d /var/lib/postgresql/wal_archive; then
        FILE_COUNT=$(docker-compose exec -T postgres find /var/lib/postgresql/wal_archive -type f 2>/dev/null | wc -l)
        print_success "Local WAL archive directory exists ($FILE_COUNT files)"
        return 0
    else
        print_failure "Local WAL archive directory does not exist"
        return 1
    fi
}

test_scripts_executable() {
    print_test "Checking if WAL scripts are executable"

    ALL_EXECUTABLE=true

    for SCRIPT in "wal-archive.sh" "wal-restore.sh"; do
        if docker-compose exec -T postgres test -x "/usr/local/bin/$SCRIPT"; then
            print_info "$SCRIPT is executable"
        else
            print_failure "$SCRIPT is not executable"
            ALL_EXECUTABLE=false
        fi
    done

    if [ "$ALL_EXECUTABLE" = true ]; then
        print_success "All WAL scripts are executable"
        return 0
    else
        return 1
    fi
}

test_wal_push() {
    print_test "Testing WAL file push to S3"

    # Force a WAL switch to generate a new WAL file
    docker-compose exec -T postgres psql -U sahool -c "SELECT pg_switch_wal();" >/dev/null 2>&1

    # Wait a moment for archiving
    sleep 5

    # Check if new WAL was archived
    LAST_ARCHIVED=$(docker-compose exec -T postgres psql -U sahool -t -c "
        SELECT last_archived_wal FROM pg_stat_archiver;
    " 2>/dev/null | tr -d ' ')

    if [ -n "$LAST_ARCHIVED" ] && [ "$LAST_ARCHIVED" != "" ]; then
        print_success "WAL push test successful (last archived: $LAST_ARCHIVED)"
        return 0
    else
        print_failure "WAL push test failed"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Test Execution
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    print_header "SAHOOL WAL-G Setup Test Suite"

    echo "Testing WAL-G configuration and setup..."
    echo "Date: $(date)"
    echo ""

    # Run all tests
    test_postgres_running || true
    test_walg_installed || true
    test_environment_variables || true
    test_archive_mode || true
    test_archive_command || true
    test_wal_level || true
    test_scripts_executable || true
    test_local_archive_directory || true
    test_s3_connectivity || true
    test_wal_archiving_status || true
    test_backup_exists || true
    test_wal_push || true

    # Print summary
    print_header "Test Summary"

    echo "Total tests: $TESTS_TOTAL"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo ""
        print_success "All tests passed! WAL-G is configured correctly."
        echo ""
        echo "Next steps:"
        echo "1. Monitor WAL archiving: docker-compose exec postgres tail -f /var/log/postgresql/wal-archive.log"
        echo "2. Create regular backups: docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data"
        echo "3. Set up automated backup schedule (see documentation)"
        exit 0
    else
        echo ""
        print_failure "Some tests failed. Please review the output and fix issues."
        echo ""
        echo "Common fixes:"
        echo "1. Ensure PostgreSQL is running: docker-compose up -d postgres"
        echo "2. Check environment variables in .env file"
        echo "3. Verify S3/MinIO credentials and connectivity"
        echo "4. Review logs: docker-compose logs postgres"
        exit 1
    fi
}

# Run main function
main
