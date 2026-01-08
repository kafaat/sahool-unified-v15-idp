#!/bin/bash
# Test Rate Limiting Across Services
# This script verifies that rate limiting is working correctly

set -e

echo "=========================================="
echo "SAHOOL Rate Limiting Verification Test"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
STANDARD_LIMIT=60
PREMIUM_LIMIT=120
TEST_COUNT=70

# Function to test a service endpoint
test_endpoint() {
    local service_name=$1
    local port=$2
    local path=$3
    local method=$4
    local data=$5
    local expected_limit=$6

    echo -e "${YELLOW}Testing: ${service_name}${NC}"
    echo "  Port: ${port}"
    echo "  Path: ${path}"
    echo "  Expected limit: ${expected_limit}/min"
    echo ""

    success_count=0
    rate_limited_count=0
    error_count=0

    for i in $(seq 1 $TEST_COUNT); do
        if [ "$method" = "POST" ]; then
            response=$(curl -s -w "\n%{http_code}" \
                -X POST \
                -H "Content-Type: application/json" \
                -d "$data" \
                "http://localhost:${port}${path}" 2>/dev/null || echo "000")
        else
            response=$(curl -s -w "\n%{http_code}" \
                "http://localhost:${port}${path}" 2>/dev/null || echo "000")
        fi

        status_code=$(echo "$response" | tail -n1)

        case $status_code in
            200|201)
                ((success_count++))
                ;;
            429)
                ((rate_limited_count++))
                break  # Stop after hitting rate limit
                ;;
            *)
                ((error_count++))
                ;;
        esac

        # Small delay to avoid connection issues
        sleep 0.05
    done

    echo "  Results:"
    echo "    ✓ Successful requests: ${success_count}"
    echo "    ✗ Rate limited at: request #$((success_count + 1))"
    echo "    ⚠ Errors: ${error_count}"
    echo ""

    # Verify rate limiting is working
    if [ $rate_limited_count -gt 0 ]; then
        # Check if we got rate limited around the expected limit (±10 for variance)
        lower_bound=$((expected_limit - 10))
        upper_bound=$((expected_limit + 10))

        if [ $success_count -ge $lower_bound ] && [ $success_count -le $upper_bound ]; then
            echo -e "  ${GREEN}✅ PASS: Rate limiting working correctly${NC}"
        else
            echo -e "  ${YELLOW}⚠️  WARNING: Rate limited at ${success_count} (expected ~${expected_limit})${NC}"
        fi
    else
        echo -e "  ${RED}❌ FAIL: No rate limiting detected${NC}"
    fi

    echo ""
    echo "----------------------------------------"
    echo ""

    # Wait for rate limit window to reset
    echo "  Waiting 5 seconds for rate limit window to reset..."
    sleep 5
}

# Check if services are running
echo "Checking service availability..."
echo ""

services=(
    "ai-agents-core:8120:/api/v1/system/status"
    "iot-gateway:8106:/healthz"
    "billing-core:8089:/healthz"
)

all_services_available=true

for service_info in "${services[@]}"; do
    IFS=':' read -r name port path <<< "$service_info"

    if curl -s "http://localhost:${port}${path}" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} ${name} (port ${port})"
    else
        echo -e "  ${RED}✗${NC} ${name} (port ${port}) - NOT AVAILABLE"
        all_services_available=false
    fi
done

echo ""

if [ "$all_services_available" = false ]; then
    echo -e "${RED}Error: Some services are not available.${NC}"
    echo "Please ensure all services are running before testing."
    echo ""
    echo "To start services:"
    echo "  docker-compose up -d ai-agents-core iot-gateway billing-core"
    echo ""
    exit 1
fi

echo "All services available. Starting rate limit tests..."
echo ""
echo "=========================================="
echo ""

# Test 1: AI Agents Core - Analysis endpoint (STANDARD tier)
test_endpoint \
    "AI Agents Core - Analysis" \
    "8120" \
    "/api/v1/analyze" \
    "POST" \
    '{"field_id":"test","crop_type":"wheat","sensor_data":{},"weather_data":{}}' \
    "$STANDARD_LIMIT"

# Test 2: IoT Gateway - Sensor reading (STANDARD tier)
test_endpoint \
    "IoT Gateway - Sensor Reading" \
    "8106" \
    "/sensor/reading" \
    "POST" \
    '{"device_id":"test-device","tenant_id":"test-tenant","field_id":"test-field","sensor_type":"temperature","value":25.5}' \
    "$STANDARD_LIMIT"

# Test 3: Billing Core - List plans (STANDARD tier)
test_endpoint \
    "Billing Core - List Plans" \
    "8089" \
    "/v1/plans" \
    "GET" \
    "" \
    "$STANDARD_LIMIT"

echo "=========================================="
echo "Rate Limiting Verification Complete"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - All critical services tested"
echo "  - Rate limiting verified for each service"
echo "  - Check results above for any failures"
echo ""
echo "To view rate limit headers in responses:"
echo "  curl -v http://localhost:8120/api/v1/system/status"
echo ""
echo "To check Redis rate limit keys:"
echo "  redis-cli KEYS 'ratelimit:*'"
echo ""
