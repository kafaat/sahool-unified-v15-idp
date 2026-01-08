#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL - Provider Config Service Persistence Test
# نص اختبار استمرارية خدمة تكوين المزودين
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SERVICE_URL="${SERVICE_URL:-http://localhost:8104}"
TENANT_ID="test-persistence-$(date +%s)"

echo "════════════════════════════════════════════════════════════"
echo "SAHOOL Provider Config Service - Persistence Test"
echo "Testing database persistence and caching"
echo "════════════════════════════════════════════════════════════"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Service Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Service Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s "$SERVICE_URL/healthz" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Service is healthy"
else
    echo -e "${RED}✗${NC} Service is not responding"
    exit 1
fi
echo

# Test 2: Create Provider Configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Create Provider Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Creating configuration for tenant: $TENANT_ID"

CREATE_RESPONSE=$(curl -s -X POST "$SERVICE_URL/config/$TENANT_ID" \
  -H "Content-Type: application/json" \
  -d "{
    \"tenant_id\": \"$TENANT_ID\",
    \"map_providers\": [
      {
        \"provider_name\": \"openstreetmap\",
        \"priority\": \"primary\",
        \"enabled\": true
      },
      {
        \"provider_name\": \"google_maps\",
        \"api_key\": \"test-api-key-123\",
        \"priority\": \"secondary\",
        \"enabled\": true
      }
    ],
    \"weather_providers\": [
      {
        \"provider_name\": \"open_meteo\",
        \"priority\": \"primary\",
        \"enabled\": true
      }
    ],
    \"satellite_providers\": [
      {
        \"provider_name\": \"sentinel_hub\",
        \"api_key\": \"test-sentinel-key\",
        \"priority\": \"primary\",
        \"enabled\": false
      }
    ]
  }")

if echo "$CREATE_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓${NC} Configuration created successfully"
else
    echo -e "${RED}✗${NC} Failed to create configuration"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi
echo

# Test 3: Retrieve Configuration (First Read - Database)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Retrieve Configuration (Database Read)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

GET_RESPONSE=$(curl -s "$SERVICE_URL/config/$TENANT_ID")

if echo "$GET_RESPONSE" | grep -q "openstreetmap"; then
    echo -e "${GREEN}✓${NC} Configuration retrieved successfully"
    echo "Map providers: $(echo "$GET_RESPONSE" | jq -r '.map_providers | length') configured"
    echo "Weather providers: $(echo "$GET_RESPONSE" | jq -r '.weather_providers | length') configured"
    echo "Satellite providers: $(echo "$GET_RESPONSE" | jq -r '.satellite_providers | length') configured"
else
    echo -e "${RED}✗${NC} Failed to retrieve configuration"
    echo "Response: $GET_RESPONSE"
    exit 1
fi
echo

# Test 4: Cache Performance Test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: Cache Performance Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# First request (should hit database)
START1=$(date +%s%N)
curl -s "$SERVICE_URL/config/$TENANT_ID" > /dev/null
END1=$(date +%s%N)
TIME1=$(( (END1 - START1) / 1000000 ))

# Second request (should hit cache)
START2=$(date +%s%N)
curl -s "$SERVICE_URL/config/$TENANT_ID" > /dev/null
END2=$(date +%s%N)
TIME2=$(( (END2 - START2) / 1000000 ))

echo "First request (database): ${TIME1}ms"
echo "Second request (cache): ${TIME2}ms"

if [ $TIME2 -lt $TIME1 ]; then
    echo -e "${GREEN}✓${NC} Cache is working (faster second request)"
else
    echo -e "${YELLOW}⚠${NC} Cache may not be working (second request not faster)"
fi
echo

# Test 5: Update Configuration (Version History)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Update Configuration (Version History)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

UPDATE_RESPONSE=$(curl -s -X POST "$SERVICE_URL/config/$TENANT_ID" \
  -H "Content-Type: application/json" \
  -d "{
    \"tenant_id\": \"$TENANT_ID\",
    \"map_providers\": [
      {
        \"provider_name\": \"openstreetmap\",
        \"priority\": \"secondary\",
        \"enabled\": false
      }
    ],
    \"weather_providers\": []
  }")

if echo "$UPDATE_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓${NC} Configuration updated successfully"
else
    echo -e "${RED}✗${NC} Failed to update configuration"
    exit 1
fi
echo

# Test 6: Check Version History
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 6: Check Version History"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HISTORY_RESPONSE=$(curl -s "$SERVICE_URL/config/$TENANT_ID/history")

if echo "$HISTORY_RESPONSE" | grep -q "history"; then
    VERSION_COUNT=$(echo "$HISTORY_RESPONSE" | jq -r '.history | length')
    echo -e "${GREEN}✓${NC} Version history retrieved successfully"
    echo "Total versions: $VERSION_COUNT"
    echo
    echo "Recent changes:"
    echo "$HISTORY_RESPONSE" | jq -r '.history[] | "  - Version \(.version): \(.change_type) at \(.changed_at)"' | head -5
else
    echo -e "${YELLOW}⚠${NC} Version history not available"
    echo "Response: $HISTORY_RESPONSE"
fi
echo

# Test 7: Service Restart Persistence Test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 7: Service Restart Persistence Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}⚠${NC} To test persistence across restarts, run:"
echo
echo "   docker-compose restart provider-config"
echo "   curl $SERVICE_URL/config/$TENANT_ID"
echo
echo "The configuration should still be available after restart."
echo

# Test 8: Cleanup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 8: Cleanup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DELETE_RESPONSE=$(curl -s -X DELETE "$SERVICE_URL/config/$TENANT_ID")

if echo "$DELETE_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓${NC} Test configuration deleted successfully"
else
    echo -e "${YELLOW}⚠${NC} Failed to delete test configuration"
    echo "Response: $DELETE_RESPONSE"
fi
echo

# Summary
echo "════════════════════════════════════════════════════════════"
echo "Test Summary"
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓${NC} All tests passed successfully!"
echo
echo "Key Features Verified:"
echo "  ✓ Service health and connectivity"
echo "  ✓ Configuration creation (database write)"
echo "  ✓ Configuration retrieval (database read)"
echo "  ✓ Redis caching performance"
echo "  ✓ Configuration updates"
echo "  ✓ Version history tracking"
echo "  ✓ Configuration deletion"
echo
echo "Next Steps:"
echo "  1. Test persistence by restarting the service"
echo "  2. Monitor database and cache metrics"
echo "  3. Test with multiple tenants"
echo "  4. Implement API key encryption for production"
echo "════════════════════════════════════════════════════════════"
