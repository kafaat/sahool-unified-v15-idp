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

# Use printf-compatible escape codes for color (works across sh/bash/dash)
RED=$(printf '\033[0;31m')
GREEN=$(printf '\033[0;32m')
YELLOW=$(printf '\033[1;33m')
BLUE=$(printf '\033[0;34m')
CYAN=$(printf '\033[0;36m')
NC=$(printf '\033[0m')

# Determine script directory (works in both bash and POSIX sh)
if [ -n "${BASH_SOURCE:-}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

TESTS_PASSED=0
TESTS_FAILED=0

printf "%s\n" "${CYAN}"
echo "═══════════════════════════════════════════════════════════════"
echo "  SAHOOL IDP - Quick Validation Test"
echo "  اختبار التحقق السريع"
echo "═══════════════════════════════════════════════════════════════"
printf "%s\n" "${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# Test Functions
# ═══════════════════════════════════════════════════════════════════════════════

test_pass() {
    printf "  %s✓%s %s\n" "${GREEN}" "${NC}" "$1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    printf "  %s✗%s %s\n" "${RED}" "${NC}" "$1"
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

printf "%s[1] Docker Compose Files%s\n" "${BLUE}" "${NC}"
test_file_exists "$SCRIPT_DIR/docker-compose-sim.yml" "docker-compose-sim.yml exists"
test_file_exists "$SCRIPT_DIR/docker-compose-advanced.yml" "docker-compose-advanced.yml exists"
test_yaml_valid "$SCRIPT_DIR/docker-compose-sim.yml" "docker-compose-sim.yml is valid YAML"
test_yaml_valid "$SCRIPT_DIR/docker-compose-advanced.yml" "docker-compose-advanced.yml is valid YAML"
echo ""
printf "%s[2] Nginx Configuration%s\n" "${BLUE}" "${NC}"
test_file_exists "$SCRIPT_DIR/config/nginx.conf" "nginx.conf exists"
test_file_exists "$SCRIPT_DIR/config/nginx-advanced.conf" "nginx-advanced.conf exists"
test_file_exists "$SCRIPT_DIR/config/proxy-params.conf" "proxy-params.conf exists"
echo ""
printf "%s[3] K6 Test Scripts%s\n" "${BLUE}" "${NC}"
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
printf "%s[4] Monitoring Configuration%s\n" "${BLUE}" "${NC}"
test_file_exists "$SCRIPT_DIR/monitoring/prometheus.yml" "prometheus.yml exists"
test_file_exists "$SCRIPT_DIR/monitoring/alertmanager.yml" "alertmanager.yml exists"
test_file_exists "$SCRIPT_DIR/monitoring/alert-rules.yml" "alert-rules.yml exists"
test_yaml_valid "$SCRIPT_DIR/monitoring/prometheus.yml" "prometheus.yml is valid YAML"
test_yaml_valid "$SCRIPT_DIR/monitoring/alertmanager.yml" "alertmanager.yml is valid YAML"
test_yaml_valid "$SCRIPT_DIR/monitoring/alert-rules.yml" "alert-rules.yml is valid YAML"
echo ""
printf "%s[5] Grafana Dashboards%s\n" "${BLUE}" "${NC}"
test_file_exists "$SCRIPT_DIR/grafana/dashboards/k6-dashboard.json" "k6-dashboard.json exists"
test_file_exists "$SCRIPT_DIR/grafana/dashboards/advanced-dashboard.json" "advanced-dashboard.json exists"
test_file_exists "$SCRIPT_DIR/grafana/dashboards/multi-client-dashboard.json" "multi-client-dashboard.json exists"
test_json_valid "$SCRIPT_DIR/grafana/dashboards/k6-dashboard.json" "k6-dashboard.json is valid JSON"
test_json_valid "$SCRIPT_DIR/grafana/dashboards/advanced-dashboard.json" "advanced-dashboard.json is valid JSON"
test_json_valid "$SCRIPT_DIR/grafana/dashboards/multi-client-dashboard.json" "multi-client-dashboard.json is valid JSON"
echo ""
printf "%s[6] Runner Scripts%s\n" "${BLUE}" "${NC}"
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
printf "%s[7] Application Dockerfile%s\n" "${BLUE}" "${NC}"
test_file_exists "$PROJECT_ROOT/apps/services/field-ops/Dockerfile" "field-ops Dockerfile exists"

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
printf "%s═══════════════════════════════════════════════════════════════%s\n" "${CYAN}" "${NC}"
printf "%s  TEST SUMMARY - ملخص الاختبارات%s\n" "${CYAN}" "${NC}"
printf "%s═══════════════════════════════════════════════════════════════%s\n" "${CYAN}" "${NC}"
echo ""
printf "  %sPassed:%s %s\n" "${GREEN}" "${NC}" "$TESTS_PASSED"
printf "  %sFailed:%s %s\n" "${RED}" "${NC}" "$TESTS_FAILED"
echo ""
if [ $TESTS_FAILED -eq 0 ]; then
    printf "%s═══════════════════════════════════════════════════════════════%s\n" "${GREEN}" "${NC}"
    printf "%s  ✓ ALL TESTS PASSED%s\n" "${GREEN}" "${NC}"
    printf "%s  ✓ جميع الاختبارات نجحت%s\n" "${GREEN}" "${NC}"
    printf "%s═══════════════════════════════════════════════════════════════%s\n" "${GREEN}" "${NC}"
    exit 0
else
    printf "%s═══════════════════════════════════════════════════════════════%s\n" "${RED}" "${NC}"
    printf "%s  ✗ SOME TESTS FAILED%s\n" "${RED}" "${NC}"
    printf "%s  ✗ بعض الاختبارات فشلت%s\n" "${RED}" "${NC}"
    printf "%s═══════════════════════════════════════════════════════════════%s\n" "${RED}" "${NC}"
    exit 1
fi
