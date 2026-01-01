#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Rate Limiting Test Script
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script tests the rate limiting implementation across the platform.
#
# Usage:
#   bash scripts/test_rate_limits.sh
#
# Tests:
#   1. Login endpoint (5 req/min limit)
#   2. Password reset endpoint (3 req/min limit)
#   3. Registration endpoint (10 req/min limit)
#   4. Token refresh endpoint (10 req/min limit)
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
KONG_URL="${KONG_URL:-http://localhost:8000}"
API_PREFIX="/api/v1"

# Test data
TEST_EMAIL="test@example.com"
TEST_PASSWORD="password123"
TEST_NAME="Test User"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       SAHOOL Platform - Rate Limiting Test Suite              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to extract rate limit headers
extract_headers() {
    local response="$1"
    echo "$response" | grep -i "X-RateLimit" || echo "No rate limit headers found"
}

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local data="$3"
    local limit="$4"
    local test_count="$5"

    echo -e "\n${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Testing: $name${NC}"
    echo -e "${YELLOW}Endpoint: $endpoint${NC}"
    echo -e "${YELLOW}Expected Limit: $limit requests/minute${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

    local success_count=0
    local rate_limited_count=0

    for i in $(seq 1 $test_count); do
        echo -e "${BLUE}Request $i/$test_count...${NC}"

        response=$(curl -s -w "\n%{http_code}" -X POST \
            "${KONG_URL}${API_PREFIX}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -i 2>&1)

        http_code=$(echo "$response" | tail -n 1)
        headers=$(echo "$response" | grep -i "X-RateLimit" || echo "")

        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            success_count=$((success_count + 1))
            echo -e "${GREEN}✓ Request $i succeeded (HTTP $http_code)${NC}"
            if [ -n "$headers" ]; then
                echo -e "${GREEN}  Headers: $(echo $headers | tr '\r\n' ' ')${NC}"
            fi
        elif [ "$http_code" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -e "${RED}✗ Request $i rate limited (HTTP 429)${NC}"
            if [ -n "$headers" ]; then
                echo -e "${RED}  Headers: $(echo $headers | tr '\r\n' ' ')${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ Request $i returned HTTP $http_code${NC}"
        fi

        # Small delay between requests
        sleep 0.5
    done

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Results for $name:${NC}"
    echo -e "${GREEN}  Successful requests: $success_count${NC}"
    echo -e "${RED}  Rate limited requests: $rate_limited_count${NC}"

    if [ $success_count -le $limit ] && [ $rate_limited_count -gt 0 ]; then
        echo -e "${GREEN}  ✓ Rate limiting is working correctly!${NC}"
    elif [ $rate_limited_count -eq 0 ]; then
        echo -e "${YELLOW}  ⚠ Warning: No rate limiting detected. Check configuration.${NC}"
    else
        echo -e "${YELLOW}  ⚠ Unexpected behavior. Review results above.${NC}"
    fi
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check if services are running
check_services() {
    echo -e "\n${BLUE}Checking if services are running...${NC}\n"

    # Check Kong
    if curl -s "${KONG_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Kong Gateway is running at $KONG_URL${NC}"
    else
        echo -e "${RED}✗ Kong Gateway is not accessible at $KONG_URL${NC}"
        echo -e "${YELLOW}  Start services with: docker-compose up -d${NC}"
        exit 1
    fi

    # Check Redis
    if docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD:-sahool}" ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠ Could not verify Redis connection${NC}"
    fi

    echo ""
}

# Main test execution
main() {
    check_services

    echo -e "${BLUE}Starting rate limit tests...${NC}"
    echo -e "${BLUE}This will take approximately 1-2 minutes.${NC}\n"

    # Test 1: Login endpoint (5 req/min)
    test_endpoint \
        "Login Endpoint" \
        "/auth/login" \
        "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
        5 \
        8

    sleep 2

    # Test 2: Password Reset endpoint (3 req/min)
    test_endpoint \
        "Password Reset Endpoint" \
        "/auth/forgot-password" \
        "{\"email\":\"$TEST_EMAIL\"}" \
        3 \
        6

    sleep 2

    # Test 3: Registration endpoint (10 req/min)
    test_endpoint \
        "Registration Endpoint" \
        "/auth/register" \
        "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"fullName\":\"$TEST_NAME\"}" \
        10 \
        13

    sleep 2

    # Test 4: Token Refresh endpoint (10 req/min)
    test_endpoint \
        "Token Refresh Endpoint" \
        "/auth/refresh" \
        "{\"refreshToken\":\"dummy_refresh_token\"}" \
        10 \
        13

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║             Rate Limiting Tests Completed                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Summary:${NC}"
    echo -e "  - Login: Tested with 8 requests (limit: 5/min)"
    echo -e "  - Password Reset: Tested with 6 requests (limit: 3/min)"
    echo -e "  - Registration: Tested with 13 requests (limit: 10/min)"
    echo -e "  - Token Refresh: Tested with 13 requests (limit: 10/min)"
    echo ""
    echo -e "${BLUE}Expected Behavior:${NC}"
    echo -e "  - First N requests should succeed (200/201)"
    echo -e "  - Remaining requests should be rate limited (429)"
    echo -e "  - Rate limit headers should be present in responses"
    echo ""
    echo -e "${YELLOW}Note:${NC}"
    echo -e "  If no rate limiting is observed, check:"
    echo -e "  1. Kong configuration: infrastructure/gateway/kong/kong.yml"
    echo -e "  2. Kong logs: docker-compose logs kong"
    echo -e "  3. Redis connection: docker-compose logs redis"
    echo ""
    echo -e "${BLUE}For detailed documentation, see:${NC}"
    echo -e "  RATE_LIMITING_IMPLEMENTATION.md"
    echo ""
}

# Run main function
main
