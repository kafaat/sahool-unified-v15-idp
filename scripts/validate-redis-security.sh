#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Redis Security Validation Script
# التحقق من أمان Redis - منصة سهول الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Validates that Redis security measures are properly implemented
# التحقق من تطبيق تدابير الأمان بشكل صحيح
#
# Usage: ./validate-redis-security.sh
#
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REDIS_CONTAINER="sahool-redis"
PASSED=0
FAILED=0
WARNINGS=0

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep REDIS_PASSWORD | xargs)
fi

# Helper functions
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ INFO${NC}: $1"
}

# Test functions
test_container_running() {
    echo ""
    info "Testing: Container Status"
    if docker ps --filter "name=$REDIS_CONTAINER" --format "{{.Names}}" | grep -q "$REDIS_CONTAINER"; then
        pass "Redis container is running"
    else
        fail "Redis container is not running"
        return 1
    fi
}

test_authentication() {
    echo ""
    info "Testing: Authentication"

    # Test with correct password
    if [ -n "${REDIS_PASSWORD:-}" ]; then
        if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" PING 2>/dev/null | grep -q "PONG"; then
            pass "Authentication with correct password works"
        else
            fail "Authentication with correct password failed"
        fi
    else
        fail "REDIS_PASSWORD not set in environment"
        return 1
    fi

    # Test without password (should fail)
    if docker exec "$REDIS_CONTAINER" redis-cli PING 2>&1 | grep -q "NOAUTH"; then
        pass "Access without password is blocked"
    else
        warn "Could not verify password protection"
    fi
}

test_dangerous_commands() {
    echo ""
    info "Testing: Dangerous Command Protection"

    # Test FLUSHDB (should be renamed)
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" FLUSHDB 2>&1 | grep -q "unknown command"; then
        pass "FLUSHDB command is renamed/disabled"
    else
        fail "FLUSHDB command is still accessible"
    fi

    # Test CONFIG (should be renamed)
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" CONFIG GET maxmemory 2>&1 | grep -q "unknown command"; then
        pass "CONFIG command is renamed/disabled"
    else
        fail "CONFIG command is still accessible"
    fi

    # Test DEBUG (should be disabled)
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" DEBUG OBJECT test 2>&1 | grep -q "unknown command"; then
        pass "DEBUG command is disabled"
    else
        fail "DEBUG command is still accessible"
    fi
}

test_renamed_commands() {
    echo ""
    info "Testing: Renamed Command Access"

    # Test renamed CONFIG command
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET maxmemory 2>/dev/null | grep -q "512"; then
        pass "Renamed CONFIG command works"
    else
        warn "Could not verify renamed CONFIG command"
    fi
}

test_persistence() {
    echo ""
    info "Testing: Data Persistence"

    # Check AOF enabled
    if docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET appendonly 2>/dev/null | grep -q "yes"; then
        pass "AOF persistence is enabled"
    else
        fail "AOF persistence is not enabled"
    fi

    # Check AOF file exists
    if docker exec "$REDIS_CONTAINER" sh -c "[ -f /data/sahool-appendonly.aof ]" 2>/dev/null; then
        pass "AOF file exists"
    else
        warn "AOF file not found (may not be created yet)"
    fi
}

test_memory_limits() {
    echo ""
    info "Testing: Memory Management"

    # Check maxmemory setting
    memory=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET maxmemory 2>/dev/null | grep -v "maxmemory" || echo "0")
    if [ "$memory" != "0" ]; then
        pass "Memory limit is configured: $memory bytes"
    else
        warn "Memory limit may not be set properly"
    fi

    # Check eviction policy
    policy=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET maxmemory-policy 2>/dev/null | tail -1)
    if [ "$policy" = "allkeys-lru" ]; then
        pass "Eviction policy is set to: $policy"
    else
        warn "Eviction policy is: $policy (expected: allkeys-lru)"
    fi
}

test_network_security() {
    echo ""
    info "Testing: Network Security"

    # Check if port is bound to localhost
    if docker ps --filter "name=$REDIS_CONTAINER" --format "{{.Ports}}" | grep -q "127.0.0.1:6379"; then
        pass "Port 6379 is bound to localhost only"
    else
        fail "Port 6379 is not properly bound to localhost"
    fi

    # Check protected mode
    protected=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET protected-mode 2>/dev/null | tail -1)
    if [ "$protected" = "yes" ]; then
        pass "Protected mode is enabled"
    else
        fail "Protected mode is not enabled"
    fi
}

test_config_file() {
    echo ""
    info "Testing: Configuration File"

    # Check if config file exists in container
    if docker exec "$REDIS_CONTAINER" sh -c "[ -f /usr/local/etc/redis/redis.conf ]" 2>/dev/null; then
        pass "Redis configuration file is mounted"
    else
        fail "Redis configuration file is not found"
    fi

    # Check if config file is being used
    if docker inspect "$REDIS_CONTAINER" 2>/dev/null | grep -q "redis.conf"; then
        pass "Redis is using configuration file"
    else
        warn "Could not verify config file usage"
    fi
}

test_slow_log() {
    echo ""
    info "Testing: Monitoring Features"

    # Check slow log configuration
    slowlog_threshold=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET slowlog-log-slower-than 2>/dev/null | tail -1)
    if [ "$slowlog_threshold" != "0" ]; then
        pass "Slow log is configured: $slowlog_threshold microseconds"
    else
        warn "Slow log threshold is 0 (disabled)"
    fi

    # Check latency monitoring
    latency_threshold=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET latency-monitor-threshold 2>/dev/null | tail -1)
    if [ "$latency_threshold" != "0" ]; then
        pass "Latency monitoring is enabled: $latency_threshold ms"
    else
        warn "Latency monitoring is disabled"
    fi
}

test_health_check() {
    echo ""
    info "Testing: Health Check"

    # Check Docker health status
    health=$(docker inspect "$REDIS_CONTAINER" --format='{{.State.Health.Status}}' 2>/dev/null || echo "none")
    if [ "$health" = "healthy" ]; then
        pass "Docker health check is passing"
    elif [ "$health" = "none" ]; then
        warn "Health check not configured"
    else
        fail "Health check status: $health"
    fi
}

test_connection_limits() {
    echo ""
    info "Testing: Connection Limits"

    # Check maxclients
    maxclients=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET maxclients 2>/dev/null | tail -1)
    if [ "$maxclients" -gt "0" ]; then
        pass "Max clients configured: $maxclients"
    else
        warn "Max clients limit may not be set"
    fi

    # Check timeout
    timeout=$(docker exec "$REDIS_CONTAINER" redis-cli -a "$REDIS_PASSWORD" SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET timeout 2>/dev/null | tail -1)
    if [ "$timeout" -gt "0" ]; then
        pass "Connection timeout configured: $timeout seconds"
    else
        warn "Connection timeout is disabled (0)"
    fi
}

test_documentation() {
    echo ""
    info "Testing: Documentation"

    # Check if documentation exists
    if [ -f "infrastructure/redis/REDIS_SECURITY.md" ]; then
        pass "Security documentation exists"
    else
        fail "Security documentation not found"
    fi

    if [ -f "infrastructure/redis/REDIS_SECURITY_SUMMARY.md" ]; then
        pass "Security summary exists"
    else
        fail "Security summary not found"
    fi

    if [ -f "infrastructure/redis/redis-docker.conf" ]; then
        pass "Configuration file exists"
    else
        fail "Configuration file not found"
    fi

    if [ -f "scripts/redis-management.sh" ]; then
        pass "Management script exists"
    else
        fail "Management script not found"
    fi
}

test_service_connections() {
    echo ""
    info "Testing: Service Configuration"

    # Count services with Redis URLs
    redis_services=$(grep -r "REDIS_URL=redis://:" docker-compose.yml 2>/dev/null | wc -l || echo "0")
    if [ "$redis_services" -gt "15" ]; then
        pass "Found $redis_services services configured with Redis authentication"
    else
        warn "Only $redis_services services configured with Redis"
    fi

    # Check Kong Redis configuration
    if grep -q "redis_password: \${REDIS_PASSWORD}" infrastructure/gateway/kong/kong.yml 2>/dev/null; then
        pass "Kong rate limiting uses Redis with authentication"
    else
        warn "Could not verify Kong Redis configuration"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}SAHOOL Platform - Redis Security Validation${NC}"
    echo -e "${BLUE}التحقق من أمان Redis - منصة سهول الزراعية${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"

    # Run all tests
    test_container_running || exit 1
    test_authentication
    test_dangerous_commands
    test_renamed_commands
    test_persistence
    test_memory_limits
    test_network_security
    test_config_file
    test_slow_log
    test_health_check
    test_connection_limits
    test_documentation
    test_service_connections

    # Summary
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Validation Summary${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Passed:${NC}   $PASSED tests"
    echo -e "${RED}Failed:${NC}   $FAILED tests"
    echo -e "${YELLOW}Warnings:${NC} $WARNINGS tests"
    echo ""

    if [ "$FAILED" -eq 0 ]; then
        echo -e "${GREEN}✓ All critical tests passed!${NC}"
        echo -e "${GREEN}Redis security is properly configured.${NC}"
        if [ "$WARNINGS" -gt 0 ]; then
            echo -e "${YELLOW}⚠ Please review warnings above.${NC}"
        fi
        exit 0
    else
        echo -e "${RED}✗ Some tests failed!${NC}"
        echo -e "${RED}Please review and fix the issues above.${NC}"
        exit 1
    fi
}

# Run main function
main
