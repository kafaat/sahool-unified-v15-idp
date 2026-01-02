#!/bin/bash
# SAHOOL PostGIS Test Suite Runner
# مشغل مجموعة اختبارات PostGIS لسهول

set -e

echo "=========================================="
echo "SAHOOL PostGIS Validation Test Suite"
echo "مجموعة اختبارات التحقق من PostGIS"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "tests/test_postgis_validation.py" ]; then
    echo -e "${RED}Error: Must be run from field-ops service root directory${NC}"
    echo "Run: cd /home/user/sahool-unified-v15-idp/apps/services/field-ops"
    exit 1
fi

# Step 1: Check Python version
echo -e "${YELLOW}[1/5] Checking Python version...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}[2/5] Installing test dependencies...${NC}"
if ! pip list | grep -q pytest; then
    echo "Installing pytest and dependencies..."
    pip install pytest pytest-asyncio pytest-cov shapely geojson pyproj
else
    echo -e "${GREEN}Dependencies already installed${NC}"
fi
echo ""

# Step 3: Verify imports
echo -e "${YELLOW}[3/5] Verifying imports...${NC}"
python -c "import pytest; import shapely; import pyproj; print('All imports successful')" || {
    echo -e "${RED}Import verification failed. Installing missing dependencies...${NC}"
    pip install -r requirements.txt
}
echo ""

# Step 4: Collect tests
echo -e "${YELLOW}[4/5] Collecting tests...${NC}"
test_count=$(python -m pytest tests/test_postgis_validation.py --collect-only -q 2>&1 | tail -1 | awk '{print $1}')
echo "Total tests discovered: $test_count"
echo ""

# Step 5: Run tests
echo -e "${YELLOW}[5/5] Running PostGIS validation tests...${NC}"
echo ""

# Default: run all tests
TEST_FILTER=${1:-""}

if [ -z "$TEST_FILTER" ]; then
    # Run all tests
    python -m pytest tests/test_postgis_validation.py \
        -v \
        --tb=short \
        --asyncio-mode=auto \
        --color=yes
else
    # Run specific test class or function
    python -m pytest "tests/test_postgis_validation.py::$TEST_FILTER" \
        -v \
        --tb=short \
        --asyncio-mode=auto \
        --color=yes
fi

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}✓ جميع الاختبارات نجحت!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo -e "${RED}✗ بعض الاختبارات فشلت${NC}"
fi

exit $exit_code
