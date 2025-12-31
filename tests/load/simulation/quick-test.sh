#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL IDP - Quick Test Script (No Docker Required)
# سكريبت الاختبار السريع بدون Docker
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script validates all simulation files without requiring Docker
# Useful for CI/CD pipelines and quick local validation
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════════"
echo "  SAHOOL IDP - Quick Validation Test"
echo "  اختبار التحقق السريع"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# Test Functions
# ═══════════════════════════════════════════════════════════════════════════════

test_pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    echo -e "  ${RED}✗${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

test_file_exists() {
    local file="$1"
    local desc="$2"
    if [ -f "$file" ]; then
        test_pass "$desc"
        return 0
    else
        test_fail "$desc (not found: $file)"
        return 1
    fi
}

test_yaml_valid() {
    local file="$1"
    local desc="$2"
    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        test_pass "$desc"
        return 0
    else
        test_fail "$desc (invalid YAML)"
        return 1
    fi
}

test_json_valid() {
    local file="$1"
    local desc="$2"
    if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        test_pass "$desc"
        return 0
    else
        test_fail "$desc (invalid JSON)"
        return 1
    fi
}

test_js_syntax() {
    local file="$1"
    local desc="$2"
    # Basic syntax check - look for K6 export patterns
    # K6 supports both "export default function" and scenario-based "export function"
    if grep -qE "export (default )?function" "$file" 2>/dev/null; then
        test_pass "$desc"
        return 0
    else
        test_fail "$desc (missing export)"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}[1] Docker Compose Files${NC}"
test_file_exists "$SCRIPT_DIR/docker-compose-sim.yml" "docker-compose-sim.yml exists"
test_file_exists "$SCRIPT_DIR/docker-compose-advanced.yml" "docker-compose-advanced.yml exists"
test_yaml_valid "$SCRIPT_DIR/docker-compose-sim.yml" "docker-compose-sim.yml is valid YAML"
test_yaml_valid "$SCRIPT_DIR/docker-compose-advanced.yml" "docker-compose-advanced.yml is valid YAML"

echo ""
echo -e "${BLUE}[2] Nginx Configuration${NC}"
test_file_exists "$SCRIPT_DIR/config/nginx.conf" "nginx.conf exists"
test_file_exists "$SCRIPT_DIR/config/nginx-advanced.conf" "nginx-advanced.conf exists"
test_file_exists "$SCRIPT_DIR/config/proxy-params.conf" "proxy-params.conf exists"

echo ""
echo -e "${BLUE}[3] K6 Test Scripts${NC}"
test_file_exists "$SCRIPT_DIR/scripts/agent-simulation.js" "agent-simulation.js exists"
test_file_exists "$SCRIPT_DIR/scripts/advanced-scenarios.js" "advanced-scenarios.js exists"
test_file_exists "$SCRIPT_DIR/scripts/chaos-testing.js" "chaos-testing.js exists"
test_file_exists "$SCRIPT_DIR/scripts/mobile-app-simulation.js" "mobile-app-simulation.js exists"
test_file_exists "$SCRIPT_DIR/scripts/web-dashboard-simulation.js" "web-dashboard-simulation.js exists"
test_file_exists "$SCRIPT_DIR/scripts/multi-client-simulation.js" "multi-client-simulation.js exists"
test_js_syntax "$SCRIPT_DIR/scripts/agent-simulation.js" "agent-simulation.js has valid structure"
test_js_syntax "$SCRIPT_DIR/scripts/advanced-scenarios.js" "advanced-scenarios.js has valid structure"
test_js_syntax "$SCRIPT_DIR/scripts/chaos-testing.js" "chaos-testing.js has valid structure"
test_js_syntax "$SCRIPT_DIR/scripts/mobile-app-simulation.js" "mobile-app-simulation.js has valid structure"
test_js_syntax "$SCRIPT_DIR/scripts/web-dashboard-simulation.js" "web-dashboard-simulation.js has valid structure"
test_js_syntax "$SCRIPT_DIR/scripts/multi-client-simulation.js" "multi-client-simulation.js has valid structure"

echo ""
echo -e "${BLUE}[4] Monitoring Configuration${NC}"
test_file_exists "$SCRIPT_DIR/monitoring/prometheus.yml" "prometheus.yml exists"
test_file_exists "$SCRIPT_DIR/monitoring/alertmanager.yml" "alertmanager.yml exists"
test_file_exists "$SCRIPT_DIR/monitoring/alert-rules.yml" "alert-rules.yml exists"
test_yaml_valid "$SCRIPT_DIR/monitoring/prometheus.yml" "prometheus.yml is valid YAML"
test_yaml_valid "$SCRIPT_DIR/monitoring/alertmanager.yml" "alertmanager.yml is valid YAML"
test_yaml_valid "$SCRIPT_DIR/monitoring/alert-rules.yml" "alert-rules.yml is valid YAML"

echo ""
echo -e "${BLUE}[5] Grafana Dashboards${NC}"
test_file_exists "$SCRIPT_DIR/grafana/dashboards/k6-dashboard.json" "k6-dashboard.json exists"
test_file_exists "$SCRIPT_DIR/grafana/dashboards/advanced-dashboard.json" "advanced-dashboard.json exists"
test_file_exists "$SCRIPT_DIR/grafana/dashboards/multi-client-dashboard.json" "multi-client-dashboard.json exists"
test_json_valid "$SCRIPT_DIR/grafana/dashboards/k6-dashboard.json" "k6-dashboard.json is valid JSON"
test_json_valid "$SCRIPT_DIR/grafana/dashboards/advanced-dashboard.json" "advanced-dashboard.json is valid JSON"
test_json_valid "$SCRIPT_DIR/grafana/dashboards/multi-client-dashboard.json" "multi-client-dashboard.json is valid JSON"

echo ""
echo -e "${BLUE}[6] Runner Scripts${NC}"
test_file_exists "$SCRIPT_DIR/run-simulation.sh" "run-simulation.sh exists"
test_file_exists "$SCRIPT_DIR/run-simulation.ps1" "run-simulation.ps1 exists"
test_file_exists "$SCRIPT_DIR/run-advanced.sh" "run-advanced.sh exists"
test_file_exists "$SCRIPT_DIR/run-advanced.ps1" "run-advanced.ps1 exists"
test_file_exists "$SCRIPT_DIR/run-multiclient.ps1" "run-multiclient.ps1 exists"
test_file_exists "$SCRIPT_DIR/verify-simulation.sh" "verify-simulation.sh exists"
test_file_exists "$SCRIPT_DIR/verify-simulation.ps1" "verify-simulation.ps1 exists"

# Check executability
if [ -x "$SCRIPT_DIR/run-simulation.sh" ]; then
    test_pass "run-simulation.sh is executable"
else
    test_fail "run-simulation.sh is not executable"
fi

if [ -x "$SCRIPT_DIR/run-advanced.sh" ]; then
    test_pass "run-advanced.sh is executable"
else
    test_fail "run-advanced.sh is not executable"
fi

echo ""
echo -e "${BLUE}[7] Application Dockerfile${NC}"
test_file_exists "$PROJECT_ROOT/apps/services/field-ops/Dockerfile" "field-ops Dockerfile exists"

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  TEST SUMMARY - ملخص الاختبارات${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC} $TESTS_PASSED"
echo -e "  ${RED}Failed:${NC} $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}  ✓ جميع الاختبارات نجحت${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}  ✗ بعض الاختبارات فشلت${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
