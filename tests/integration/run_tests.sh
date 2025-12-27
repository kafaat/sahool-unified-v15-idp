#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Integration Test Runner
# سكريبت تشغيل اختبارات التكامل لمنصة سهول
#
# This script runs integration tests for the SAHOOL platform
# يقوم هذا السكريبت بتشغيل اختبارات التكامل لمنصة سهول
#
# Usage:
#   ./run_tests.sh                    # Run all integration tests
#   ./run_tests.sh starter            # Run starter package tests only
#   ./run_tests.sh professional       # Run professional package tests only
#   ./run_tests.sh enterprise         # Run enterprise package tests only
#   ./run_tests.sh events             # Run event flow tests only
#
# Author: SAHOOL Platform Team
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_PACKAGE=${1:-"all"}
VERBOSE=${VERBOSE:-0}
FAIL_FAST=${FAIL_FAST:-0}

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEST_RESULTS_DIR="${PROJECT_ROOT}/test-results"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          SAHOOL Integration Test Runner                     ║${NC}"
echo -e "${BLUE}║          مشغل اختبارات التكامل لمنصة سهول                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create test results directory
mkdir -p "${TEST_RESULTS_DIR}"

# Function to print status
print_status() {
    local status=$1
    local message=$2

    if [ "${status}" = "success" ]; then
        echo -e "${GREEN}✓${NC} ${message}"
    elif [ "${status}" = "error" ]; then
        echo -e "${RED}✗${NC} ${message}"
    elif [ "${status}" = "info" ]; then
        echo -e "${BLUE}ℹ${NC} ${message}"
    elif [ "${status}" = "warning" ]; then
        echo -e "${YELLOW}⚠${NC} ${message}"
    fi
}

# Function to check if Docker Compose is running
check_docker_compose() {
    print_status "info" "Checking Docker Compose services..."

    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        print_status "error" "Docker Compose not found. Please install Docker."
        exit 1
    fi

    # Check if test services are running
    if docker ps | grep -q "sahool.*test"; then
        print_status "success" "Docker Compose test services are running"
        return 0
    else
        print_status "warning" "Docker Compose test services not detected"
        print_status "info" "Starting Docker Compose test environment..."

        cd "${PROJECT_ROOT}"
        docker-compose -f docker-compose.test.yml up -d

        print_status "info" "Waiting for services to be ready (60 seconds)..."
        sleep 60

        print_status "success" "Docker Compose test services started"
    fi
}

# Function to check Python dependencies
check_dependencies() {
    print_status "info" "Checking Python dependencies..."

    if ! command -v python3 &> /dev/null; then
        print_status "error" "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi

    if ! command -v pytest &> /dev/null; then
        print_status "warning" "pytest not found. Installing dependencies..."
        pip install -r "${PROJECT_ROOT}/requirements-test.txt" || {
            print_status "error" "Failed to install dependencies"
            exit 1
        }
    fi

    print_status "success" "Python dependencies OK"
}

# Function to run tests
run_tests() {
    local test_file=$1
    local test_name=$2

    print_status "info" "Running ${test_name} tests..."

    local pytest_args="-v --tb=short --color=yes"

    # Add markers
    pytest_args="${pytest_args} -m integration"

    # Add verbosity
    if [ "${VERBOSE}" = "1" ]; then
        pytest_args="${pytest_args} -vv"
    fi

    # Add fail fast
    if [ "${FAIL_FAST}" = "1" ]; then
        pytest_args="${pytest_args} -x"
    fi

    # Add coverage
    pytest_args="${pytest_args} --cov=. --cov-report=html:${TEST_RESULTS_DIR}/coverage"

    # Add test results
    pytest_args="${pytest_args} --junit-xml=${TEST_RESULTS_DIR}/junit-${test_name}.xml"
    pytest_args="${pytest_args} --html=${TEST_RESULTS_DIR}/report-${test_name}.html --self-contained-html"

    # Run pytest
    cd "${PROJECT_ROOT}"

    if pytest ${pytest_args} "${test_file}"; then
        print_status "success" "${test_name} tests passed"
        return 0
    else
        print_status "error" "${test_name} tests failed"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    print_status "info" "Test Package: ${TEST_PACKAGE}"
    print_status "info" "Project Root: ${PROJECT_ROOT}"
    echo ""

    # Check dependencies
    check_dependencies

    # Check Docker Compose
    check_docker_compose

    echo ""
    print_status "info" "═══════════════════════════════════════════════════════════"
    print_status "info" "Starting Test Execution"
    print_status "info" "═══════════════════════════════════════════════════════════"
    echo ""

    local exit_code=0

    case "${TEST_PACKAGE}" in
        "all")
            print_status "info" "Running ALL integration tests"
            echo ""

            run_tests "tests/integration/test_starter_package.py" "Starter Package" || exit_code=1
            echo ""

            run_tests "tests/integration/test_professional_package.py" "Professional Package" || exit_code=1
            echo ""

            run_tests "tests/integration/test_enterprise_package.py" "Enterprise Package" || exit_code=1
            echo ""

            run_tests "tests/integration/test_event_flow.py" "Event Flow" || exit_code=1
            ;;

        "starter")
            run_tests "tests/integration/test_starter_package.py" "Starter Package" || exit_code=1
            ;;

        "professional")
            run_tests "tests/integration/test_professional_package.py" "Professional Package" || exit_code=1
            ;;

        "enterprise")
            run_tests "tests/integration/test_enterprise_package.py" "Enterprise Package" || exit_code=1
            ;;

        "events")
            run_tests "tests/integration/test_event_flow.py" "Event Flow" || exit_code=1
            ;;

        *)
            print_status "error" "Unknown test package: ${TEST_PACKAGE}"
            echo ""
            echo "Usage: $0 [all|starter|professional|enterprise|events]"
            exit 1
            ;;
    esac

    echo ""
    print_status "info" "═══════════════════════════════════════════════════════════"
    print_status "info" "Test Execution Complete"
    print_status "info" "═══════════════════════════════════════════════════════════"
    echo ""

    if [ ${exit_code} -eq 0 ]; then
        print_status "success" "All tests passed! ✨"
        print_status "info" "Test results: ${TEST_RESULTS_DIR}"
    else
        print_status "error" "Some tests failed. Check the reports for details."
        print_status "info" "Test results: ${TEST_RESULTS_DIR}"
    fi

    echo ""

    exit ${exit_code}
}

# Run main
main
