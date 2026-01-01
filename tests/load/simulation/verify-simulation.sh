#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL IDP - Simulation Environment Verification Script
# سكريبت التحقق من بيئة المحاكاة لمنصة سهول
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script verifies that all simulation files are present and valid,
# then attempts to build and run the simulation environment.
#
# Usage:
#   ./verify-simulation.sh          # Full verification and build
#   ./verify-simulation.sh --check  # Only check files (no build)
#   ./verify-simulation.sh --build  # Skip checks, just build
#
# ═══════════════════════════════════════════════════════════════════════════════

# Don't exit on errors - we want to collect all results
# set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

print_banner() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  SAHOOL IDP - Simulation Verification Script"
    echo "  سكريبت التحقق من بيئة المحاكاة"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
    echo "  Project Root: $PROJECT_ROOT"
    echo "  Script Dir: $SCRIPT_DIR"
    echo ""
}

check_pass() {
    echo -e "  ${GREEN}[✓ PASS]${NC} $1"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
}

check_fail() {
    echo -e "  ${RED}[✗ FAIL]${NC} $1"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
}

check_warn() {
    echo -e "  ${YELLOW}[⚠ WARN]${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

section_header() {
    echo ""
    echo -e "${BLUE}───────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────────────────────${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

verify_core_files() {
    section_header "1. Core Simulation Files - الملفات الأساسية"

    # docker-compose-sim.yml
    if [ -f "$SCRIPT_DIR/docker-compose-sim.yml" ]; then
        check_pass "docker-compose-sim.yml exists"

        # Verify it contains key services
        if grep -q "sahool-db:" "$SCRIPT_DIR/docker-compose-sim.yml"; then
            check_pass "docker-compose-sim.yml contains sahool-db service"
        else
            check_fail "docker-compose-sim.yml missing sahool-db service"
        fi

        if grep -q "sahool-app-1:" "$SCRIPT_DIR/docker-compose-sim.yml"; then
            check_pass "docker-compose-sim.yml contains app instances"
        else
            check_fail "docker-compose-sim.yml missing app instances"
        fi

        if grep -q "sahool-nginx:" "$SCRIPT_DIR/docker-compose-sim.yml"; then
            check_pass "docker-compose-sim.yml contains nginx load balancer"
        else
            check_fail "docker-compose-sim.yml missing nginx load balancer"
        fi

        if grep -q "sahool-k6:" "$SCRIPT_DIR/docker-compose-sim.yml"; then
            check_pass "docker-compose-sim.yml contains k6 testing service"
        else
            check_fail "docker-compose-sim.yml missing k6 testing service"
        fi
    else
        check_fail "docker-compose-sim.yml NOT FOUND"
    fi

    # README.md
    if [ -f "$SCRIPT_DIR/README.md" ]; then
        check_pass "README.md documentation exists"
    else
        check_warn "README.md documentation missing"
    fi

    # run-simulation.sh
    if [ -f "$SCRIPT_DIR/run-simulation.sh" ]; then
        check_pass "run-simulation.sh runner script exists"
        if [ -x "$SCRIPT_DIR/run-simulation.sh" ]; then
            check_pass "run-simulation.sh is executable"
        else
            check_warn "run-simulation.sh is not executable (chmod +x needed)"
        fi
    else
        check_fail "run-simulation.sh NOT FOUND"
    fi

    # .env.example
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        check_pass ".env.example environment template exists"
    else
        check_warn ".env.example template missing"
    fi
}

verify_nginx_config() {
    section_header "2. Nginx Configuration - إعدادات موازن الحمل"

    # nginx.conf
    if [ -f "$SCRIPT_DIR/config/nginx.conf" ]; then
        check_pass "config/nginx.conf exists"

        # Check for load balancing config
        if grep -q "upstream sahool_backend" "$SCRIPT_DIR/config/nginx.conf"; then
            check_pass "nginx.conf contains upstream backend definition"
        else
            check_fail "nginx.conf missing upstream backend definition"
        fi

        if grep -q "least_conn" "$SCRIPT_DIR/config/nginx.conf"; then
            check_pass "nginx.conf uses least_conn load balancing"
        else
            check_warn "nginx.conf may not have optimal load balancing"
        fi

        if grep -q "sahool-app-1:8080" "$SCRIPT_DIR/config/nginx.conf"; then
            check_pass "nginx.conf references app instances correctly"
        else
            check_fail "nginx.conf missing app instance references"
        fi
    else
        check_fail "config/nginx.conf NOT FOUND"
    fi

    # nginx-upstream.conf
    if [ -f "$SCRIPT_DIR/config/nginx-upstream.conf" ]; then
        check_pass "config/nginx-upstream.conf exists"
    else
        check_warn "config/nginx-upstream.conf missing (optional)"
    fi

    # proxy-params.conf
    if [ -f "$SCRIPT_DIR/config/proxy-params.conf" ]; then
        check_pass "config/proxy-params.conf exists"
    else
        check_warn "config/proxy-params.conf missing (optional)"
    fi
}

verify_k6_scripts() {
    section_header "3. K6 Load Testing Scripts - سكريبتات اختبار الحمل"

    # agent-simulation.js
    if [ -f "$SCRIPT_DIR/scripts/agent-simulation.js" ]; then
        check_pass "scripts/agent-simulation.js exists"

        # Check for key test components
        if grep -q "export default function" "$SCRIPT_DIR/scripts/agent-simulation.js"; then
            check_pass "agent-simulation.js has main test function"
        else
            check_fail "agent-simulation.js missing main test function"
        fi

        if grep -q "loginSuccessRate" "$SCRIPT_DIR/scripts/agent-simulation.js"; then
            check_pass "agent-simulation.js has custom metrics"
        else
            check_warn "agent-simulation.js missing custom metrics"
        fi

        if grep -q "connection_pool_errors" "$SCRIPT_DIR/scripts/agent-simulation.js"; then
            check_pass "agent-simulation.js tracks connection pool errors"
        else
            check_warn "agent-simulation.js may not track connection pool errors"
        fi

        if grep -q "session_loss_errors" "$SCRIPT_DIR/scripts/agent-simulation.js"; then
            check_pass "agent-simulation.js tracks session loss errors"
        else
            check_warn "agent-simulation.js may not track session loss errors"
        fi
    else
        check_fail "scripts/agent-simulation.js NOT FOUND"
    fi
}

verify_grafana_config() {
    section_header "4. Grafana Dashboards - لوحات المراقبة"

    # Dashboard JSON
    if [ -f "$SCRIPT_DIR/grafana/dashboards/k6-dashboard.json" ]; then
        check_pass "grafana/dashboards/k6-dashboard.json exists"
    else
        check_warn "grafana/dashboards/k6-dashboard.json missing"
    fi

    # Dashboards config
    if [ -f "$SCRIPT_DIR/grafana/dashboards/dashboards.yml" ]; then
        check_pass "grafana/dashboards/dashboards.yml exists"
    else
        check_warn "grafana/dashboards/dashboards.yml missing"
    fi

    # Datasources
    if [ -f "$SCRIPT_DIR/grafana/datasources/influxdb.yml" ]; then
        check_pass "grafana/datasources/influxdb.yml exists"
    else
        check_warn "grafana/datasources/influxdb.yml missing"
    fi
}

verify_dockerfile() {
    section_header "5. Application Dockerfile - ملف بناء التطبيق"

    # Check the Dockerfile referenced in docker-compose
    DOCKERFILE_PATH="$PROJECT_ROOT/apps/services/field-ops/Dockerfile"

    if [ -f "$DOCKERFILE_PATH" ]; then
        check_pass "apps/services/field-ops/Dockerfile exists"

        # Check Dockerfile contents
        if grep -q "FROM python" "$DOCKERFILE_PATH"; then
            check_pass "Dockerfile uses Python base image"
        elif grep -q "FROM node" "$DOCKERFILE_PATH"; then
            check_pass "Dockerfile uses Node.js base image"
        else
            check_warn "Dockerfile base image unclear"
        fi

        if grep -q "HEALTHCHECK" "$DOCKERFILE_PATH"; then
            check_pass "Dockerfile includes HEALTHCHECK"
        else
            check_warn "Dockerfile missing HEALTHCHECK instruction"
        fi

        if grep -q "8080" "$DOCKERFILE_PATH"; then
            check_pass "Dockerfile exposes port 8080"
        else
            check_warn "Dockerfile may not expose correct port"
        fi
    else
        check_fail "apps/services/field-ops/Dockerfile NOT FOUND"
        echo -e "    ${YELLOW}→ The docker-compose-sim.yml references this Dockerfile${NC}"
    fi
}

verify_docker_requirements() {
    section_header "6. Docker Environment - بيئة Docker"

    # Check if Docker is installed
    if command -v docker &> /dev/null; then
        check_pass "Docker is installed"
        DOCKER_VERSION=$(docker --version)
        echo -e "    ${CYAN}Version: $DOCKER_VERSION${NC}"
    else
        check_fail "Docker is NOT installed"
    fi

    # Check if Docker Compose is available
    if command -v docker-compose &> /dev/null; then
        check_pass "Docker Compose is installed (standalone)"
        COMPOSE_VERSION=$(docker-compose --version)
        echo -e "    ${CYAN}Version: $COMPOSE_VERSION${NC}"
    elif docker compose version &> /dev/null; then
        check_pass "Docker Compose is installed (plugin)"
        COMPOSE_VERSION=$(docker compose version)
        echo -e "    ${CYAN}Version: $COMPOSE_VERSION${NC}"
    else
        check_fail "Docker Compose is NOT installed"
    fi

    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        check_pass "Docker daemon is running"
    else
        check_warn "Docker daemon is not running (start Docker to build)"
    fi
}

verify_directories() {
    section_header "7. Required Directories - المجلدات المطلوبة"

    # Results directory
    if [ -d "$SCRIPT_DIR/results" ]; then
        check_pass "results/ directory exists"
    else
        check_warn "results/ directory missing (will be created)"
        mkdir -p "$SCRIPT_DIR/results"
        check_pass "results/ directory created"
    fi

    # Init scripts directory
    if [ -d "$SCRIPT_DIR/init-scripts" ]; then
        check_pass "init-scripts/ directory exists"
    else
        check_warn "init-scripts/ directory missing (will be created)"
        mkdir -p "$SCRIPT_DIR/init-scripts"
        check_pass "init-scripts/ directory created"
    fi

    # Config directory
    if [ -d "$SCRIPT_DIR/config" ]; then
        check_pass "config/ directory exists"
    else
        check_fail "config/ directory NOT FOUND"
    fi

    # Scripts directory
    if [ -d "$SCRIPT_DIR/scripts" ]; then
        check_pass "scripts/ directory exists"
    else
        check_fail "scripts/ directory NOT FOUND"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD & TEST FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

try_build() {
    section_header "8. Build Test - اختبار البناء"

    if ! docker info &> /dev/null; then
        check_warn "Skipping build test - Docker daemon not running"
        return
    fi

    echo "  Attempting to validate docker-compose configuration..."

    cd "$SCRIPT_DIR"
    if docker-compose -f docker-compose-sim.yml config --quiet 2>/dev/null; then
        check_pass "docker-compose-sim.yml is valid YAML"
    else
        check_fail "docker-compose-sim.yml has syntax errors"
        echo -e "    ${YELLOW}Run: docker-compose -f docker-compose-sim.yml config${NC}"
    fi

    echo ""
    echo "  To build and run the simulation:"
    echo -e "    ${CYAN}cd $SCRIPT_DIR${NC}"
    echo -e "    ${CYAN}./run-simulation.sh start${NC}"
    echo -e "    ${CYAN}./run-simulation.sh test${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

print_summary() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  VERIFICATION SUMMARY - ملخص التحقق${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}Passed:${NC}   $CHECKS_PASSED checks"
    echo -e "  ${RED}Failed:${NC}   $CHECKS_FAILED checks"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS checks"
    echo ""

    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "  ${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
        echo -e "  ${GREEN}  ✓ ALL CRITICAL CHECKS PASSED - SIMULATION READY${NC}"
        echo -e "  ${GREEN}  ✓ جميع الفحوصات الحرجة نجحت - المحاكاة جاهزة${NC}"
        echo -e "  ${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo "  Next steps:"
        echo "    1. cd tests/load/simulation"
        echo "    2. ./run-simulation.sh start"
        echo "    3. ./run-simulation.sh test"
        echo ""
        return 0
    else
        echo -e "  ${RED}═══════════════════════════════════════════════════════════════════════════════${NC}"
        echo -e "  ${RED}  ✗ SOME CHECKS FAILED - REVIEW REQUIRED${NC}"
        echo -e "  ${RED}  ✗ بعض الفحوصات فشلت - مراجعة مطلوبة${NC}"
        echo -e "  ${RED}═══════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    print_banner

    case "${1:-full}" in
        --check|-c)
            echo "Running file checks only..."
            verify_core_files
            verify_nginx_config
            verify_k6_scripts
            verify_grafana_config
            verify_dockerfile
            verify_directories
            ;;
        --build|-b)
            echo "Running build only..."
            verify_docker_requirements
            try_build
            ;;
        full|*)
            verify_core_files
            verify_nginx_config
            verify_k6_scripts
            verify_grafana_config
            verify_dockerfile
            verify_directories
            verify_docker_requirements
            try_build
            ;;
    esac

    print_summary
}

main "$@"
