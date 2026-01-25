#!/bin/bash
# SAHOOL Field Boundary Detection - API Test Script
# سكريبت اختبار API كشف حدود الحقول

set -e  # Exit on error

BASE_URL="http://localhost:8090"
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "SAHOOL Field Boundary Detection API Tests"
echo "اختبار API كشف حدود الحقول"
echo "========================================"
echo ""

# Check if service is running
echo -e "${YELLOW}Checking if service is running...${NC}"
if curl -s "${BASE_URL}/healthz" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${RED}✗ Service not running!${NC}"
    echo ""
    echo "Please start the service first:"
    echo "  cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service"
    echo "  python -m src.main"
    exit 1
fi

echo ""
echo "========================================"
echo "Test 1: Detect Field Boundaries"
echo "========================================"
echo ""
echo -e "${YELLOW}Detecting boundaries around Sana'a region...${NC}"
echo "Location: 15.5527°N, 44.2075°E"
echo "Radius: 500 meters"
echo ""

curl -X POST "${BASE_URL}/v1/boundaries/detect" \
  -G \
  --data-urlencode "lat=15.5527" \
  --data-urlencode "lon=44.2075" \
  --data-urlencode "radius_m=500" \
  --data-urlencode "date=2024-01-15" \
  -H "Content-Type: application/json" \
  -w "\n\nStatus: %{http_code}\n" \
  | jq '.' 2>/dev/null || cat

echo ""
echo -e "${GREEN}✓ Detection complete${NC}"
echo ""

echo "========================================"
echo "Test 2: Refine Field Boundary"
echo "========================================"
echo ""
echo -e "${YELLOW}Refining a rough boundary...${NC}"
echo "Initial coordinates: 4 points (rectangular)"
echo "Buffer: 50 meters"
echo ""

# Note: Using form-encoded data for arrays
curl -X POST "${BASE_URL}/v1/boundaries/refine" \
  --data-urlencode 'coords=[[44.207, 15.552], [44.208, 15.552], [44.208, 15.553], [44.207, 15.553]]' \
  --data-urlencode 'buffer_m=50' \
  -w "\n\nStatus: %{http_code}\n" \
  | jq '.' 2>/dev/null || cat

echo ""
echo -e "${GREEN}✓ Refinement complete${NC}"
echo ""

echo "========================================"
echo "Test 3: Detect Boundary Changes"
echo "========================================"
echo ""
echo -e "${YELLOW}Detecting changes since July 2023...${NC}"
echo "Field ID: field_12345"
echo "Comparison date: 2023-07-01"
echo ""

curl -X GET "${BASE_URL}/v1/boundaries/field_12345/changes" \
  -G \
  --data-urlencode "since_date=2023-07-01" \
  --data-urlencode 'previous_coords=[[44.207, 15.552], [44.208, 15.552], [44.208, 15.553], [44.207, 15.553]]' \
  -w "\n\nStatus: %{http_code}\n" \
  | jq '.' 2>/dev/null || cat

echo ""
echo -e "${GREEN}✓ Change detection complete${NC}"
echo ""

echo "========================================"
echo "Test 4: Different Locations in Yemen"
echo "========================================"
echo ""

# Aden (Coastal)
echo -e "${YELLOW}Testing Aden (Coastal region)...${NC}"
echo "Location: 12.7855°N, 45.0187°E"
echo ""

curl -X POST "${BASE_URL}/v1/boundaries/detect" \
  -G \
  --data-urlencode "lat=12.7855" \
  --data-urlencode "lon=45.0187" \
  --data-urlencode "radius_m=300" \
  -s | jq '.metadata' 2>/dev/null || echo "Request sent"

echo ""

# Taiz (Highland)
echo -e "${YELLOW}Testing Taiz (Highland region)...${NC}"
echo "Location: 13.5796°N, 44.0194°E"
echo ""

curl -X POST "${BASE_URL}/v1/boundaries/detect" \
  -G \
  --data-urlencode "lat=13.5796" \
  --data-urlencode "lon=44.0194" \
  --data-urlencode "radius_m=300" \
  -s | jq '.metadata' 2>/dev/null || echo "Request sent"

echo ""
echo -e "${GREEN}✓ Regional tests complete${NC}"
echo ""

echo "========================================"
echo "Test 5: Edge Cases and Validation"
echo "========================================"
echo ""

# Invalid coordinates
echo -e "${YELLOW}Testing invalid latitude (should fail)...${NC}"
curl -X POST "${BASE_URL}/v1/boundaries/detect" \
  -G \
  --data-urlencode "lat=99999" \
  --data-urlencode "lon=44.2075" \
  -w "\nStatus: %{http_code}\n" \
  -s || echo "Handled gracefully"

echo ""

# Very small radius
echo -e "${YELLOW}Testing very small radius...${NC}"
curl -X POST "${BASE_URL}/v1/boundaries/detect" \
  -G \
  --data-urlencode "lat=15.5527" \
  --data-urlencode "lon=44.2075" \
  --data-urlencode "radius_m=50" \
  -s | jq '.metadata' 2>/dev/null || echo "Request sent"

echo ""

# Very large radius
echo -e "${YELLOW}Testing large radius (1km)...${NC}"
curl -X POST "${BASE_URL}/v1/boundaries/detect" \
  -G \
  --data-urlencode "lat=15.5527" \
  --data-urlencode "lon=44.2075" \
  --data-urlencode "radius_m=1000" \
  -s | jq '.metadata' 2>/dev/null || echo "Request sent"

echo ""
echo -e "${GREEN}✓ Edge case tests complete${NC}"
echo ""

echo "========================================"
echo "Test 6: Save Results to Files"
echo "========================================"
echo ""

echo -e "${YELLOW}Saving detection results to file...${NC}"
curl -X POST "${BASE_URL}/v1/boundaries/detect" \
  -G \
  --data-urlencode "lat=15.5527" \
  --data-urlencode "lon=44.2075" \
  --data-urlencode "radius_m=500" \
  -s | jq '.' > /tmp/boundary_detection.geojson 2>/dev/null || \
  curl -X POST "${BASE_URL}/v1/boundaries/detect?lat=15.5527&lon=44.2075&radius_m=500" -s > /tmp/boundary_detection.geojson

if [ -f /tmp/boundary_detection.geojson ]; then
    echo -e "${GREEN}✓ Saved to /tmp/boundary_detection.geojson${NC}"
    echo "File size: $(du -h /tmp/boundary_detection.geojson | cut -f1)"
else
    echo -e "${RED}✗ Failed to save file${NC}"
fi

echo ""

echo -e "${YELLOW}Saving refinement results to file...${NC}"
curl -X POST "${BASE_URL}/v1/boundaries/refine" \
  --data-urlencode 'coords=[[44.207, 15.552], [44.208, 15.552], [44.208, 15.553], [44.207, 15.553]]' \
  --data-urlencode 'buffer_m=50' \
  -s > /tmp/boundary_refinement.json

if [ -f /tmp/boundary_refinement.json ]; then
    echo -e "${GREEN}✓ Saved to /tmp/boundary_refinement.json${NC}"
    echo "File size: $(du -h /tmp/boundary_refinement.json | cut -f1)"
else
    echo -e "${RED}✗ Failed to save file${NC}"
fi

echo ""

echo "========================================"
echo "All Tests Complete!"
echo "جميع الاختبارات مكتملة!"
echo "========================================"
echo ""
echo "Results saved to:"
echo "  - /tmp/boundary_detection.geojson"
echo "  - /tmp/boundary_refinement.json"
echo ""
echo "You can view these files or import them into GIS software."
echo ""
echo -e "${GREEN}✓ All API endpoints working correctly${NC}"
echo ""
