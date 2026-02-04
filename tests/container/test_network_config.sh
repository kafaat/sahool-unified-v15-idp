#!/usr/bin/env bash
#
# Test Docker Network Configuration
# Validates that sahool-network is properly configured as external
#
# Usage:
#   ./test_network_config.sh
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper functions
test_start() {
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test $TESTS_RUN: $1 ... "
}

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}PASS${NC}"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}FAIL${NC}"
    echo -e "${RED}  Error: $1${NC}"
}

echo "=========================================="
echo "Docker Network Configuration Tests"
echo "=========================================="
echo ""

# Determine repository root (2 levels up from tests/container/)
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

echo "Repository root: $REPO_ROOT"
echo ""

# Test 1: Verify main docker-compose.yml has external network
test_start "Main docker-compose.yml has external network"
if grep -q "external: true" "$REPO_ROOT/docker-compose.yml" && grep -q "name: sahool-network" "$REPO_ROOT/docker-compose.yml"; then
    test_pass
else
    test_fail "docker-compose.yml missing 'external: true' for sahool-network"
fi

# Test 2: Verify infra docker-compose has external network
test_start "Infrastructure docker-compose has external network"
if grep -q "external: true" "$REPO_ROOT/docker/docker-compose.infra.yml" && grep -q "name: sahool-network" "$REPO_ROOT/docker/docker-compose.infra.yml"; then
    test_pass
else
    test_fail "docker/docker-compose.infra.yml missing 'external: true' for sahool-network"
fi

# Test 3: Verify telemetry docker-compose has external network
test_start "Telemetry docker-compose has external network"
if grep -q "external: true" "$REPO_ROOT/docker-compose.telemetry.yml" && grep -q "name: sahool-network" "$REPO_ROOT/docker-compose.telemetry.yml"; then
    test_pass
else
    test_fail "docker-compose.telemetry.yml missing 'external: true' for sahool-network"
fi

# Test 4: Verify IoT docker-compose has external network
test_start "IoT docker-compose has external network"
if grep -q "external: true" "$REPO_ROOT/docker/docker-compose.iot.yml" && grep -q "name: sahool-network" "$REPO_ROOT/docker/docker-compose.iot.yml"; then
    test_pass
else
    test_fail "docker/docker-compose.iot.yml missing 'external: true' for sahool-network"
fi

# Test 5: Verify network-create target exists in Makefile
test_start "Makefile has network-create target"
if grep -q "^network-create:" "$REPO_ROOT/Makefile"; then
    test_pass
else
    test_fail "Makefile missing 'network-create' target"
fi

# Test 6: Verify infra-up depends on network-create
test_start "infra-up target depends on network-create"
if grep -q "^infra-up: network-create" "$REPO_ROOT/Makefile"; then
    test_pass
else
    test_fail "infra-up doesn't depend on network-create"
fi

# Test 7: Verify dev target depends on network-create
test_start "dev target depends on network-create"
if grep -q "^dev: network-create" "$REPO_ROOT/Makefile"; then
    test_pass
else
    test_fail "dev doesn't depend on network-create"
fi

# Test 8: Verify dev-terrain depends on network-create
test_start "dev-terrain target depends on network-create"
if grep -q "^dev-terrain: network-create" "$REPO_ROOT/Makefile"; then
    test_pass
else
    test_fail "dev-terrain doesn't depend on network-create"
fi

# Test 9: Verify docker compose config works without errors
test_start "Docker Compose config validates successfully"
if docker compose config > /dev/null 2>&1; then
    test_pass
else
    test_fail "docker compose config failed - check .env file and compose syntax"
fi

# Test 10: Verify network shows as external in compose config
test_start "Network configured as external in compose config"
if docker compose config 2>&1 | grep -A 5 "^networks:" | grep -q "external: true"; then
    test_pass
else
    test_fail "Network not marked as external in parsed config"
fi

# Test 11: Create network if it doesn't exist (for testing)
test_start "Can create sahool-network"
if docker network create sahool-network 2>/dev/null || docker network inspect sahool-network >/dev/null 2>&1; then
    test_pass
else
    test_fail "Failed to create or inspect sahool-network"
fi

# Test 12: Verify no warnings when using docker compose (quick check)
test_start "No warnings in compose validation"
OUTPUT=$(docker compose config 2>&1 || true)
if echo "$OUTPUT" | grep -qi "not created for project"; then
    test_fail "Still getting 'not created for project' warning"
else
    test_pass
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Tests Run:    ${TESTS_RUN}"
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed.${NC}"
    exit 1
fi
