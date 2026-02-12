#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Docker Configuration Validation Script
# Validates all Docker services, configurations, and dependencies
# ═══════════════════════════════════════════════════════════════════════════════

set +e  # Don't exit on errors - collect all issues

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Output functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_check() {
    ((TOTAL_CHECKS++))
    echo -ne "  [CHECK] $1..."
}

print_pass() {
    ((PASSED_CHECKS++))
    echo -e " ${GREEN}✓ PASS${NC}"
}

print_fail() {
    ((FAILED_CHECKS++))
    echo -e " ${RED}✗ FAIL${NC}"
    if [ -n "$1" ]; then
        echo -e "    ${RED}Error: $1${NC}"
    fi
}

print_warn() {
    ((WARNING_CHECKS++))
    echo -e " ${YELLOW}⚠ WARNING${NC}"
    if [ -n "$1" ]; then
        echo -e "    ${YELLOW}$1${NC}"
    fi
}

# Change to project root
cd "$PROJECT_ROOT"

print_header "SAHOOL Docker Configuration Validation"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Environment File Validation
# ─────────────────────────────────────────────────────────────────────────────
print_header "1. Environment File Validation"

print_check "Checking .env file exists"
if [ -f ".env" ]; then
    print_pass
else
    print_fail ".env file not found"
    exit 1
fi

print_check "Checking required variables in .env"
REQUIRED_VARS=(
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "POSTGRES_DB"
    "REDIS_PASSWORD"
    "NATS_USER"
    "NATS_PASSWORD"
    "NATS_ADMIN_USER"
    "NATS_ADMIN_PASSWORD"
    "NATS_MONITOR_USER"
    "NATS_MONITOR_PASSWORD"
    "NATS_CLUSTER_USER"
    "NATS_CLUSTER_PASSWORD"
    "NATS_SYSTEM_USER"
    "NATS_SYSTEM_PASSWORD"
    "NATS_JETSTREAM_KEY"
    "JWT_SECRET_KEY"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" .env 2>/dev/null; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    print_pass
else
    print_fail "Missing variables: ${MISSING_VARS[*]}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. Docker Compose Configuration Validation
# ─────────────────────────────────────────────────────────────────────────────
print_header "2. Docker Compose Configuration Validation"

print_check "Validating docker-compose.yml syntax"
if docker compose config > /dev/null 2>&1; then
    print_pass
else
    print_fail "docker-compose.yml has syntax errors"
    exit 1
fi

print_check "Counting services in docker-compose.yml"
SERVICE_COUNT=$(docker compose config --services | wc -l)
if [ "$SERVICE_COUNT" -gt 0 ]; then
    print_pass
    echo "    Found $SERVICE_COUNT services"
else
    print_fail "No services found"
fi

print_check "Checking for port conflicts"
DUPLICATE_PORTS=$(docker compose config | grep -E '^\s+- "(127\.0\.0\.1:)?[0-9]+:[0-9]+"' | sed 's/.*"\([0-9.]*:\)\?\([0-9]*\):.*/\2/' | sort -n | uniq -d)
if [ -z "$DUPLICATE_PORTS" ]; then
    print_pass
else
    print_fail "Duplicate ports found: $DUPLICATE_PORTS"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. Required Configuration Files
# ─────────────────────────────────────────────────────────────────────────────
print_header "3. Required Configuration Files"

CONFIG_FILES=(
    "infrastructure/core/pgbouncer/entrypoint.sh"
    "infrastructure/core/pgbouncer/pgbouncer.ini"
    "infrastructure/redis/redis-secure.conf"
    "config/nats/nats.conf"
    "config/nats/nats-secure.conf"
)

for file in "${CONFIG_FILES[@]}"; do
    print_check "Checking $file"
    if [ -f "$file" ]; then
        print_pass
    else
        print_fail "File not found"
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# 4. Dockerfile Validation
# ─────────────────────────────────────────────────────────────────────────────
print_header "4. Dockerfile Validation"

print_check "Counting Dockerfiles in apps/services"
DOCKERFILE_COUNT=$(find apps/services -name "Dockerfile" | wc -l)
echo "    Found $DOCKERFILE_COUNT Dockerfiles"
print_pass

print_check "Checking for services without Dockerfiles"
SERVICES_WITHOUT_DOCKERFILE=()
for service_dir in apps/services/*/; do
    service_name=$(basename "$service_dir")
    if [ ! -f "${service_dir}Dockerfile" ]; then
        SERVICES_WITHOUT_DOCKERFILE+=("$service_name")
    fi
done

if [ ${#SERVICES_WITHOUT_DOCKERFILE[@]} -eq 0 ]; then
    print_pass
else
    print_warn "Services without Dockerfile: ${SERVICES_WITHOUT_DOCKERFILE[*]}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. Network Configuration
# ─────────────────────────────────────────────────────────────────────────────
print_header "5. Network Configuration"

print_check "Checking network definition in docker-compose.yml"
if docker compose config | grep -q "sahool-network"; then
    print_pass
else
    print_fail "sahool-network not found"
fi

print_check "Checking all services are on sahool-network"
TOTAL_SERVICES=$(docker compose config --services | wc -l)
SERVICES_ON_NETWORK=$(docker compose config | grep -c "sahool-network" || echo 0)
if [ "$SERVICES_ON_NETWORK" -ge "$TOTAL_SERVICES" ]; then
    print_pass
    echo "    $SERVICES_ON_NETWORK services connected"
else
    print_warn "Some services may not be on sahool-network"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 6. Volume Configuration
# ─────────────────────────────────────────────────────────────────────────────
print_header "6. Volume Configuration"

print_check "Checking named volumes"
VOLUME_COUNT=$(docker compose config --volumes 2>/dev/null | wc -l)
if [ "$VOLUME_COUNT" -gt 0 ]; then
    print_pass
    echo "    Found $VOLUME_COUNT named volumes"
else
    print_warn "No named volumes found (using bind mounts only)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 7. Service Dependencies
# ─────────────────────────────────────────────────────────────────────────────
print_header "7. Service Dependencies"

print_check "Validating service dependencies"
if docker compose config > /tmp/docker-compose-check.yml 2>&1; then
    INVALID_DEPS=$(grep -i "service.*not found" /tmp/docker-compose-check.yml || echo "")
    if [ -z "$INVALID_DEPS" ]; then
        print_pass
    else
        print_fail "Invalid dependencies found"
        echo "$INVALID_DEPS"
    fi
    rm -f /tmp/docker-compose-check.yml
else
    print_fail "Could not validate dependencies"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 8. Health Check Configuration
# ─────────────────────────────────────────────────────────────────────────────
print_header "8. Health Check Configuration"

print_check "Checking health checks in docker-compose.yml"
HEALTHCHECK_COUNT=$(docker compose config | grep -c "healthcheck:" || echo 0)
if [ "$HEALTHCHECK_COUNT" -gt 0 ]; then
    print_pass
    echo "    Found $HEALTHCHECK_COUNT health checks"
else
    print_warn "No health checks found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 9. Resource Limits
# ─────────────────────────────────────────────────────────────────────────────
print_header "9. Resource Limits"

print_check "Checking resource limits"
RESOURCE_LIMITS=$(docker compose config | grep -c "limits:" || echo 0)
if [ "$RESOURCE_LIMITS" -gt 0 ]; then
    print_pass
    echo "    Found $RESOURCE_LIMITS resource limit configurations"
else
    print_warn "No resource limits configured"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 10. Security Configuration
# ─────────────────────────────────────────────────────────────────────────────
print_header "10. Security Configuration"

print_check "Checking for localhost-only port bindings"
LOCALHOST_BINDINGS=$(docker compose config | grep -c "127.0.0.1:" || echo 0)
if [ "$LOCALHOST_BINDINGS" -gt 0 ]; then
    print_pass
    echo "    Found $LOCALHOST_BINDINGS localhost-only bindings"
else
    print_warn "No localhost-only bindings found"
fi

print_check "Checking for security_opt configurations"
SECURITY_OPT=$(docker compose config | grep -c "security_opt:" || echo 0)
if [ "$SECURITY_OPT" -gt 0 ]; then
    print_pass
    echo "    Found $SECURITY_OPT security option configurations"
else
    print_warn "No security options configured"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print_header "Validation Summary"

echo -e "Total Checks:   ${BLUE}$TOTAL_CHECKS${NC}"
echo -e "Passed:         ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed:         ${RED}$FAILED_CHECKS${NC}"
echo -e "Warnings:       ${YELLOW}$WARNING_CHECKS${NC}"

if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo -e "\n${GREEN}✓ All critical checks passed!${NC}\n"
    exit 0
else
    echo -e "\n${RED}✗ Some checks failed. Please review the errors above.${NC}\n"
    exit 1
fi
