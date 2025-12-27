#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Test Runner Script
# سكريبت تشغيل اختبارات منصة سهول
#
# This script runs the comprehensive test suite for SAHOOL platform
# Supports unit, integration, and E2E tests
#
# Usage:
#   ./scripts/run-tests.sh [options]
#
# Options:
#   --unit           Run unit tests only
#   --integration    Run integration tests only
#   --e2e            Run E2E tests only
#   --health         Run health check tests only
#   --all            Run all tests (default)
#   --fast           Skip slow tests
#   --verbose        Verbose output
#   --coverage       Generate coverage report
#   --docker         Run tests in Docker containers
#   --clean          Clean test environment before running
#   --help           Show this help message
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

# Default options
TEST_TYPE="all"
VERBOSE=""
COVERAGE=""
FAST=""
DOCKER_MODE=false
CLEAN=false

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ───────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────────────────────────────────────

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    cat << EOF
SAHOOL Test Runner - سكريبت تشغيل اختبارات سهول

Usage: $0 [options]

Options:
  --unit           Run unit tests only
  --integration    Run integration tests only
  --e2e            Run E2E workflow tests only
  --health         Run health check tests only
  --all            Run all tests (default)
  --fast           Skip slow tests
  --verbose        Verbose output
  --coverage       Generate coverage report
  --docker         Run tests in Docker containers
  --clean          Clean test environment before running
  --help           Show this help message

Examples:
  $0 --unit                    # Run unit tests
  $0 --integration --coverage  # Run integration tests with coverage
  $0 --e2e --docker            # Run E2E tests in Docker
  $0 --health --fast           # Run health checks, skip slow tests
  $0 --all --verbose           # Run all tests with verbose output

EOF
    exit 0
}

# ───────────────────────────────────────────────────────────────────────────────
# Parse Command Line Arguments
# ───────────────────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --e2e)
            TEST_TYPE="e2e"
            shift
            ;;
        --health)
            TEST_TYPE="health"
            shift
            ;;
        --all)
            TEST_TYPE="all"
            shift
            ;;
        --fast)
            FAST="-m 'not slow'"
            shift
            ;;
        --verbose)
            VERBOSE="-vv"
            shift
            ;;
        --coverage)
            COVERAGE="--cov=apps --cov=packages --cov-report=html --cov-report=term"
            shift
            ;;
        --docker)
            DOCKER_MODE=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# ───────────────────────────────────────────────────────────────────────────────
# Main Script
# ───────────────────────────────────────────────────────────────────────────────

print_header "SAHOOL Automated Test Suite"
print_info "Test Type: $TEST_TYPE"
print_info "Project Root: $PROJECT_ROOT"

# Navigate to project root
cd "$PROJECT_ROOT"

# ───────────────────────────────────────────────────────────────────────────────
# Clean Test Environment
# ───────────────────────────────────────────────────────────────────────────────

if [ "$CLEAN" = true ]; then
    print_info "Cleaning test environment..."

    # Remove test databases and caches
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf test-results/*

    if [ "$DOCKER_MODE" = true ]; then
        print_info "Stopping and removing test containers..."
        docker-compose -f docker-compose.test.yml down -v
    fi

    print_success "Test environment cleaned"
fi

# ───────────────────────────────────────────────────────────────────────────────
# Docker Mode
# ───────────────────────────────────────────────────────────────────────────────

if [ "$DOCKER_MODE" = true ]; then
    print_header "Running Tests in Docker Environment"

    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found. Please install docker-compose."
        exit 1
    fi

    # Build and start test environment
    print_info "Starting test environment..."
    docker-compose -f docker-compose.test.yml up -d --build

    # Wait for services to be ready
    print_info "Waiting for services to be ready (30 seconds)..."
    sleep 30

    # Run tests in container
    print_info "Running tests in container..."
    docker-compose -f docker-compose.test.yml exec -T test_runner \
        pytest tests/ $VERBOSE $COVERAGE $FAST \
        --junit-xml=test-results/junit.xml \
        --html=test-results/report.html

    TEST_EXIT_CODE=$?

    # Cleanup
    print_info "Stopping test environment..."
    docker-compose -f docker-compose.test.yml down

    if [ $TEST_EXIT_CODE -eq 0 ]; then
        print_success "All tests passed!"
        exit 0
    else
        print_error "Some tests failed. Check test-results/ for details."
        exit $TEST_EXIT_CODE
    fi
fi

# ───────────────────────────────────────────────────────────────────────────────
# Local Mode
# ───────────────────────────────────────────────────────────────────────────────

print_header "Running Tests Locally"

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    print_error "pytest not found. Installing test dependencies..."
    pip install -r requirements/test-requirements.txt
fi

# Check if services are running
print_info "Checking if services are running..."

# Check PostgreSQL
if ! nc -z localhost 5432 2>/dev/null; then
    print_warning "PostgreSQL not running on localhost:5432"
    print_info "Some tests may be skipped. Start services with: docker-compose up -d"
fi

# Check Redis
if ! nc -z localhost 6379 2>/dev/null; then
    print_warning "Redis not running on localhost:6379"
fi

# Check NATS
if ! nc -z localhost 4222 2>/dev/null; then
    print_warning "NATS not running on localhost:4222"
fi

# ───────────────────────────────────────────────────────────────────────────────
# Run Tests Based on Type
# ───────────────────────────────────────────────────────────────────────────────

case $TEST_TYPE in
    unit)
        print_header "Running Unit Tests"
        pytest tests/unit/ $VERBOSE $COVERAGE $FAST \
            --junit-xml=test-results/unit-junit.xml \
            --html=test-results/unit-report.html
        ;;

    integration)
        print_header "Running Integration Tests"
        pytest tests/integration/ $VERBOSE $COVERAGE $FAST \
            -m integration \
            --junit-xml=test-results/integration-junit.xml \
            --html=test-results/integration-report.html
        ;;

    e2e)
        print_header "Running E2E Workflow Tests"
        pytest tests/e2e/ $VERBOSE $COVERAGE $FAST \
            -m e2e \
            --junit-xml=test-results/e2e-junit.xml \
            --html=test-results/e2e-report.html
        ;;

    health)
        print_header "Running Health Check Tests"
        pytest tests/integration/test_service_health.py $VERBOSE $FAST \
            -m health \
            --junit-xml=test-results/health-junit.xml \
            --html=test-results/health-report.html
        ;;

    all)
        print_header "Running All Tests"
        pytest tests/ $VERBOSE $COVERAGE $FAST \
            --junit-xml=test-results/all-junit.xml \
            --html=test-results/all-report.html
        ;;
esac

TEST_EXIT_CODE=$?

# ───────────────────────────────────────────────────────────────────────────────
# Report Results
# ───────────────────────────────────────────────────────────────────────────────

echo ""
print_header "Test Results"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed! ✓"
    echo ""
    print_info "Test reports available in: test-results/"

    if [ -n "$COVERAGE" ]; then
        print_info "Coverage report available at: htmlcov/index.html"
    fi
else
    print_error "Some tests failed. Please check the output above."
    echo ""
    print_info "Detailed reports available in: test-results/"
fi

# ───────────────────────────────────────────────────────────────────────────────
# Test Summary
# ───────────────────────────────────────────────────────────────────────────────

echo ""
print_info "Test suite components:"
echo "  • Unit Tests:        tests/unit/"
echo "  • Integration Tests: tests/integration/"
echo "  • E2E Tests:         tests/e2e/"
echo ""
print_info "Quick commands:"
echo "  • Health checks:  $0 --health"
echo "  • Fast tests:     $0 --fast"
echo "  • With coverage:  $0 --coverage"
echo "  • In Docker:      $0 --docker"
echo ""

exit $TEST_EXIT_CODE
