#!/bin/bash

################################################################################
# Docker Smoke Test Script
# Description: Start containers and check health endpoints
# Usage: ./smoke-test.sh [--services SERVICE1,SERVICE2] [--timeout SECONDS]
################################################################################

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Configuration
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
TIMEOUT=120
MAX_RETRIES=30
RETRY_INTERVAL=5
SELECTED_SERVICES=()
TEST_NETWORK="sahool-test-network"
CLEANUP_ON_EXIT=true
EXIT_CODE=0

# Test tracking
declare -a STARTED_SERVICES=()
declare -a HEALTHY_SERVICES=()
declare -a UNHEALTHY_SERVICES=()
declare -a FAILED_SERVICES=()

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $*${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

################################################################################
# Cleanup function
################################################################################

cleanup() {
    if [[ "${CLEANUP_ON_EXIT}" == "true" ]]; then
        log_info "Cleaning up test containers..."
        docker-compose -f "${COMPOSE_FILE}" down --remove-orphans 2>/dev/null || true
        log_success "Cleanup completed"
    else
        log_warning "Skipping cleanup. Containers are still running."
        log_info "Run './cleanup.sh' to clean up manually"
    fi
}

# Trap to ensure cleanup on exit
trap cleanup EXIT INT TERM

################################################################################
# Check prerequisites
################################################################################

check_prerequisites() {
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    # Check if compose file exists
    if [[ ! -f "${COMPOSE_FILE}" ]]; then
        log_error "Docker Compose file not found: ${COMPOSE_FILE}"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

################################################################################
# Get services from docker-compose
################################################################################

get_services() {
    local services=()

    # Try docker compose (v2)
    if docker compose version &> /dev/null; then
        mapfile -t services < <(docker compose -f "${COMPOSE_FILE}" config --services 2>/dev/null)
    else
        # Fallback to docker-compose (v1)
        mapfile -t services < <(docker-compose -f "${COMPOSE_FILE}" config --services 2>/dev/null)
    fi

    printf '%s\n' "${services[@]}"
}

################################################################################
# Start services
################################################################################

start_services() {
    local services_to_start=("$@")

    if [[ ${#services_to_start[@]} -eq 0 ]]; then
        log_info "Starting all services..."
        docker-compose -f "${COMPOSE_FILE}" up -d
    else
        log_info "Starting selected services: ${services_to_start[*]}"
        docker-compose -f "${COMPOSE_FILE}" up -d "${services_to_start[@]}"
    fi

    # Get list of started containers
    mapfile -t STARTED_SERVICES < <(docker-compose -f "${COMPOSE_FILE}" ps --services --filter "status=running")

    if [[ ${#STARTED_SERVICES[@]} -eq 0 ]]; then
        log_error "No services started"
        return 1
    fi

    log_success "Started ${#STARTED_SERVICES[@]} service(s)"
    return 0
}

################################################################################
# Wait for container to be healthy
################################################################################

wait_for_container() {
    local service="$1"
    local container_id

    # Get container ID
    container_id=$(docker-compose -f "${COMPOSE_FILE}" ps -q "${service}" 2>/dev/null | head -n1)

    if [[ -z "${container_id}" ]]; then
        log_error "Container for service '${service}' not found"
        return 1
    fi

    log_info "Waiting for ${CYAN}${service}${NC} to be healthy..."

    local retries=0
    local status

    while [[ ${retries} -lt ${MAX_RETRIES} ]]; do
        # Get container status
        status=$(docker inspect --format='{{.State.Status}}' "${container_id}" 2>/dev/null || echo "unknown")

        # Check if container has health check
        local health_status
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "${container_id}" 2>/dev/null || echo "none")

        if [[ "${health_status}" == "healthy" ]]; then
            log_success "✓ ${service} is healthy"
            return 0
        elif [[ "${health_status}" == "none" ]]; then
            # No health check defined, check if running
            if [[ "${status}" == "running" ]]; then
                log_success "✓ ${service} is running (no health check defined)"
                return 0
            fi
        elif [[ "${health_status}" == "unhealthy" ]]; then
            log_error "✗ ${service} is unhealthy"
            docker logs "${container_id}" --tail 50 2>&1 | sed 's/^/  /'
            return 1
        fi

        # Check if container exited
        if [[ "${status}" == "exited" ]]; then
            log_error "✗ ${service} exited unexpectedly"
            docker logs "${container_id}" --tail 50 2>&1 | sed 's/^/  /'
            return 1
        fi

        ((retries++))
        sleep "${RETRY_INTERVAL}"
    done

    log_error "✗ ${service} failed to become healthy (timeout)"
    docker logs "${container_id}" --tail 50 2>&1 | sed 's/^/  /'
    return 1
}

################################################################################
# Check HTTP endpoint
################################################################################

check_http_endpoint() {
    local service="$1"
    local endpoint="${2:-/health}"
    local port="${3:-3000}"

    log_info "Checking HTTP endpoint for ${CYAN}${service}${NC}: http://localhost:${port}${endpoint}"

    local retries=0

    while [[ ${retries} -lt ${MAX_RETRIES} ]]; do
        if curl -sf -m 5 "http://localhost:${port}${endpoint}" > /dev/null 2>&1; then
            log_success "✓ ${service} HTTP endpoint is responding"
            return 0
        fi

        ((retries++))
        sleep "${RETRY_INTERVAL}"
    done

    log_warning "✗ ${service} HTTP endpoint not responding (may not be exposed)"
    return 1
}

################################################################################
# Check container logs for errors
################################################################################

check_logs_for_errors() {
    local service="$1"
    local container_id

    container_id=$(docker-compose -f "${COMPOSE_FILE}" ps -q "${service}" 2>/dev/null | head -n1)

    if [[ -z "${container_id}" ]]; then
        return 1
    fi

    log_info "Checking logs for ${CYAN}${service}${NC} for errors..."

    # Check for common error patterns
    local error_count
    error_count=$(docker logs "${container_id}" 2>&1 | grep -iE "error|fatal|exception|failed" | grep -v "0 error" | wc -l)

    if [[ ${error_count} -gt 0 ]]; then
        log_warning "Found ${error_count} error-like message(s) in logs"
        docker logs "${container_id}" 2>&1 | grep -iE "error|fatal|exception|failed" | head -n 10 | sed 's/^/  /'
        return 1
    else
        log_success "✓ No errors found in logs"
        return 0
    fi
}

################################################################################
# Test a single service
################################################################################

test_service() {
    local service="$1"
    local test_passed=true

    log_info "Testing service: ${CYAN}${service}${NC}"
    echo ""

    # Wait for container to be healthy
    if ! wait_for_container "${service}"; then
        test_passed=false
    fi

    # Check logs for errors
    if ! check_logs_for_errors "${service}"; then
        test_passed=false
    fi

    # Record result
    if [[ "${test_passed}" == "true" ]]; then
        HEALTHY_SERVICES+=("${service}")
        log_success "✓ ${service} passed all checks"
    else
        UNHEALTHY_SERVICES+=("${service}")
        log_error "✗ ${service} failed health checks"
        EXIT_CODE=1
    fi

    echo ""
}

################################################################################
# Run smoke tests
################################################################################

run_smoke_tests() {
    if [[ ${#STARTED_SERVICES[@]} -eq 0 ]]; then
        log_error "No services to test"
        return 1
    fi

    log_info "Running smoke tests on ${#STARTED_SERVICES[@]} service(s)..."
    echo ""

    for service in "${STARTED_SERVICES[@]}"; do
        test_service "${service}"
    done
}

################################################################################
# Display test summary
################################################################################

show_summary() {
    print_header "Smoke Test Summary"

    echo "Total Services:    ${#STARTED_SERVICES[@]}"
    echo -e "Healthy:           ${GREEN}${#HEALTHY_SERVICES[@]}${NC}"
    echo -e "Unhealthy:         ${RED}${#UNHEALTHY_SERVICES[@]}${NC}"
    echo ""

    if [[ ${#HEALTHY_SERVICES[@]} -gt 0 ]]; then
        echo -e "${GREEN}Healthy Services:${NC}"
        for service in "${HEALTHY_SERVICES[@]}"; do
            echo "  ✓ ${service}"
        done
        echo ""
    fi

    if [[ ${#UNHEALTHY_SERVICES[@]} -gt 0 ]]; then
        echo -e "${RED}Unhealthy Services:${NC}"
        for service in "${UNHEALTHY_SERVICES[@]}"; do
            echo "  ✗ ${service}"
        done
        echo ""
    fi

    # Show running containers
    log_info "Running containers:"
    docker-compose -f "${COMPOSE_FILE}" ps
}

################################################################################
# Quick health check
################################################################################

quick_health_check() {
    print_header "Quick Health Check"

    log_info "Checking all running containers..."
    echo ""

    mapfile -t running_services < <(docker-compose -f "${COMPOSE_FILE}" ps --services --filter "status=running")

    for service in "${running_services[@]}"; do
        local container_id
        container_id=$(docker-compose -f "${COMPOSE_FILE}" ps -q "${service}" 2>/dev/null | head -n1)

        if [[ -n "${container_id}" ]]; then
            local status
            status=$(docker inspect --format='{{.State.Status}}' "${container_id}" 2>/dev/null)
            local health
            health=$(docker inspect --format='{{.State.Health.Status}}' "${container_id}" 2>/dev/null || echo "none")

            if [[ "${health}" == "healthy" ]] || [[ "${health}" == "none" && "${status}" == "running" ]]; then
                log_success "✓ ${service}: ${status} (${health})"
            else
                log_error "✗ ${service}: ${status} (${health})"
            fi
        fi
    done
}

################################################################################
# Usage
################################################################################

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Start containers and run smoke tests to verify they're healthy.

OPTIONS:
    -h, --help                  Show this help message
    -f, --file FILE             Docker Compose file (default: docker-compose.yml)
    -s, --services SERVICES     Comma-separated list of services to test
    -t, --timeout SECONDS       Health check timeout (default: 120)
    -n, --no-cleanup            Don't cleanup containers on exit
    -q, --quick                 Quick health check only (no full test)

EXAMPLES:
    $(basename "$0")                                # Test all services
    $(basename "$0") -s api,web                     # Test specific services
    $(basename "$0") -t 300                         # Wait up to 5 minutes
    $(basename "$0") -n                             # Keep containers running
    $(basename "$0") -q                             # Quick health check

EOF
    exit 0
}

################################################################################
# Parse Arguments
################################################################################

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                ;;
            -f|--file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -s|--services)
                IFS=',' read -ra SELECTED_SERVICES <<< "$2"
                shift 2
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                MAX_RETRIES=$((TIMEOUT / RETRY_INTERVAL))
                shift 2
                ;;
            -n|--no-cleanup)
                CLEANUP_ON_EXIT=false
                shift
                ;;
            -q|--quick)
                quick_health_check
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
}

################################################################################
# Main
################################################################################

main() {
    print_header "Docker Smoke Tests"

    # Parse arguments
    parse_args "$@"

    # Check prerequisites
    check_prerequisites

    # Change to project root
    cd "${PROJECT_ROOT}"

    # Start services
    if ! start_services "${SELECTED_SERVICES[@]}"; then
        log_error "Failed to start services"
        exit 1
    fi

    # Wait a bit for services to initialize
    log_info "Waiting for services to initialize..."
    sleep 10

    # Run smoke tests
    run_smoke_tests

    # Show summary
    show_summary

    # Exit with appropriate code
    if [[ ${EXIT_CODE} -eq 0 ]]; then
        log_success "All smoke tests passed!"
        exit 0
    else
        log_error "Some smoke tests failed!"
        exit 1
    fi
}

# Run main function
main "$@"
