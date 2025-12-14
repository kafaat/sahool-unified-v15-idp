#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Smoke Test Suite
# Validates all services are running and responding correctly
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL="${BASE_URL:-http://localhost}"

SERVICES=(
    "field_ops:8080:/healthz"
    "ndvi_engine:8097:/healthz"
    "weather_core:8098:/healthz"
    "field_chat:8099:/healthz"
    "iot_gateway:8094:/healthz"
    "agro_advisor:8095:/healthz"
    "ws_gateway:8090:/healthz"
)

INFRA=(
    "postgres:5432"
    "nats:4222"
    "redis:6379"
    "mqtt:1883"
)

PASSED=0
FAILED=0
WARNINGS=0

# ─────────────────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────────────────

log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; ((PASSED++)); }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; ((FAILED++)); }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; ((WARNINGS++)); }

check_http_health() {
    local name="$1"
    local port="$2"
    local path="$3"
    local url="${BASE_URL}:${port}${path}"

    local response
    local http_code

    response=$(curl -sf -w "%{http_code}" "$url" -o /tmp/health_response.json 2>/dev/null) || response="000"

    if [[ "$response" == "200" ]]; then
        log_pass "$name health check ($url)"
        return 0
    else
        log_fail "$name health check ($url) - HTTP $response"
        return 1
    fi
}

check_tcp_port() {
    local name="$1"
    local port="$2"

    if nc -z localhost "$port" 2>/dev/null; then
        log_pass "$name port $port is open"
        return 0
    else
        log_fail "$name port $port is closed"
        return 1
    fi
}

test_api_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local expected_code="$4"

    local http_code
    http_code=$(curl -sf -X "$method" -w "%{http_code}" "$url" -o /dev/null 2>/dev/null) || http_code="000"

    if [[ "$http_code" == "$expected_code" ]]; then
        log_pass "$name - $method $url (HTTP $http_code)"
        return 0
    else
        log_fail "$name - $method $url (expected $expected_code, got $http_code)"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Test Suites
# ─────────────────────────────────────────────────────────────────────────────

test_infrastructure() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Infrastructure Tests"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    for infra in "${INFRA[@]}"; do
        local name="${infra%%:*}"
        local port="${infra##*:}"
        check_tcp_port "$name" "$port" || true
    done
}

test_services() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Service Health Tests"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name port path <<< "$service"
        check_http_health "$name" "$port" "$path" || true
    done
}

test_api_functionality() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  API Functionality Tests"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    # FieldOps
    test_api_endpoint "FieldOps root" "GET" "${BASE_URL}:8080/" "200" || true

    # NDVI Engine
    test_api_endpoint "NDVI root" "GET" "${BASE_URL}:8097/" "200" || true

    # Weather Core
    test_api_endpoint "Weather root" "GET" "${BASE_URL}:8098/" "200" || true

    # Field Chat
    test_api_endpoint "Chat root" "GET" "${BASE_URL}:8099/" "200" || true

    # IoT Gateway
    test_api_endpoint "IoT root" "GET" "${BASE_URL}:8094/" "200" || true
}

test_event_system() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Event System Tests"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    # Check NATS monitoring endpoint
    if curl -sf "http://localhost:8222/varz" > /dev/null 2>&1; then
        log_pass "NATS monitoring endpoint responding"
    else
        log_warn "NATS monitoring endpoint not available (optional)"
    fi
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Smoke Test Summary"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo -e "  ${GREEN}Passed:${NC}   $PASSED"
    echo -e "  ${RED}Failed:${NC}   $FAILED"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
    echo ""

    if [[ $FAILED -eq 0 ]]; then
        echo -e "${GREEN}All critical tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed. Please check the services.${NC}"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "           SAHOOL v15.3.2 Smoke Test Suite"
    echo "═══════════════════════════════════════════════════════════════"

    test_infrastructure
    test_services
    test_api_functionality
    test_event_system
    print_summary
}

main "$@"
