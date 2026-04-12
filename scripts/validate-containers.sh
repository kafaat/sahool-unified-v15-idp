#!/bin/bash
# Container Configuration Validation Script
# Validates Kong, postgres, pgbouncer, redis, nats, and user-service configurations

# Don't exit on first error
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  SAHOOL Container Configuration Validation"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNING_CHECKS++))
    ((TOTAL_CHECKS++))
}

echo "1. Checking docker-compose.yml..."
echo "-----------------------------------"

# Check Kong Admin API binding
if grep -q "KONG_ADMIN_LISTEN: 127.0.0.1:8001" docker-compose.yml; then
    check_pass "Kong Admin API bound to localhost only (127.0.0.1:8001)"
else
    check_fail "Kong Admin API should be bound to localhost (127.0.0.1:8001)"
fi

# Check Kong DNS no-sync
if grep -q 'KONG_DNS_NO_SYNC: "on"' docker-compose.yml; then
    check_pass "Kong DNS no-sync enabled for resilience"
else
    check_fail "Kong DNS no-sync should be 'on' for better resilience"
fi

# Check PgBouncer volume persistence
if grep -q "pgbouncer-userlist:/etc/pgbouncer/runtime" docker-compose.yml; then
    check_pass "PgBouncer using persistent volume for userlist.txt"
else
    check_fail "PgBouncer should use persistent volume instead of tmpfs"
fi

# Check Redis health check
if grep -q -- '--no-auth-warning' docker-compose.yml && grep -q 'REDIS_PASSWORD.*ping' docker-compose.yml; then
    check_pass "Redis health check has proper password handling"
else
    check_warn "Redis health check may have password interpolation issues"
fi

# Check NATS environment variables
if grep -q "NATS_SYSTEM_USER:.*:?" docker-compose.yml && \
   grep -q "NATS_SYSTEM_PASSWORD:.*:?" docker-compose.yml && \
   grep -q "NATS_JETSTREAM_KEY:.*:?" docker-compose.yml; then
    check_pass "NATS security variables are marked as required"
else
    check_fail "NATS security variables (SYSTEM_USER, SYSTEM_PASSWORD, JETSTREAM_KEY) should be required"
fi

# Check user-service localhost binding
if grep -q '"127.0.0.1:3025:3025"' docker-compose.yml; then
    check_pass "user-service bound to localhost only"
else
    check_fail "user-service should be bound to localhost (127.0.0.1:3025)"
fi

echo ""
echo "2. Checking .env.example..."
echo "-----------------------------------"

# Check NATS variables in .env.example
if grep -q "NATS_SYSTEM_USER=" .env.example && \
   grep -q "NATS_SYSTEM_PASSWORD=" .env.example && \
   grep -q "NATS_JETSTREAM_KEY=" .env.example; then
    check_pass ".env.example contains all required NATS variables"
else
    check_fail ".env.example missing NATS_SYSTEM_USER, NATS_SYSTEM_PASSWORD, or NATS_JETSTREAM_KEY"
fi

echo ""
echo "3. Checking .env.development..."
echo "-----------------------------------"

# Check development environment
if grep -q "NATS_JETSTREAM_KEY=" .env.development; then
    check_pass ".env.development has NATS_JETSTREAM_KEY"
else
    check_fail ".env.development missing NATS_JETSTREAM_KEY"
fi

echo ""
echo "4. Checking application configurations..."
echo "-----------------------------------"

# Check mobile Android NDK version
if grep -q 'ndkVersion = "27\.2\.12479018"' apps/mobile/android/app/build.gradle.kts; then
    check_pass "Mobile Android NDK version set to 27.2.12479018 (r27c LTS)"
else
    check_fail "Mobile Android NDK should be 27.2.12479018 for AGP 8.13 compatibility"
fi

# Check admin Dockerfile documentation
if grep -q "TODO.*legacy-peer-deps.*React 19" apps/admin/Dockerfile; then
    check_pass "Admin Dockerfile has --legacy-peer-deps documentation"
else
    check_warn "Admin Dockerfile should document --legacy-peer-deps usage"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Validation Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "Total Checks:    $TOTAL_CHECKS"
echo -e "${GREEN}Passed:          $PASSED_CHECKS${NC}"
echo -e "${RED}Failed:          $FAILED_CHECKS${NC}"
echo -e "${YELLOW}Warnings:        $WARNING_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the issues above.${NC}"
    exit 1
fi
