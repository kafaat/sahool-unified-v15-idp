#!/bin/bash
# Test Runner Script for AI Agents Core
# سكريبت تشغيل الاختبارات

set -e

echo "🧪 AI Agents Core Test Suite"
echo "============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install -r requirements-test.txt"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-yes}"

echo "Test Type: $TEST_TYPE"
echo "Coverage: $COVERAGE"
echo ""

# Base pytest command
PYTEST_CMD="pytest"

# Add coverage if requested
if [ "$COVERAGE" = "yes" ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml"
fi

# Run tests based on type
case $TEST_TYPE in
    "all")
        echo -e "${GREEN}Running all tests...${NC}"
        $PYTEST_CMD tests/
        ;;
    "unit")
        echo -e "${GREEN}Running unit tests...${NC}"
        $PYTEST_CMD -m unit tests/unit/
        ;;
    "integration")
        echo -e "${GREEN}Running integration tests...${NC}"
        $PYTEST_CMD -m integration tests/integration/
        ;;
    "agent")
        echo -e "${GREEN}Running agent tests...${NC}"
        $PYTEST_CMD -m agent tests/
        ;;
    "api")
        echo -e "${GREEN}Running API tests...${NC}"
        $PYTEST_CMD -m api tests/
        ;;
    "fast")
        echo -e "${GREEN}Running fast tests only...${NC}"
        $PYTEST_CMD -m "not slow" tests/
        ;;
    "slow")
        echo -e "${GREEN}Running slow tests...${NC}"
        $PYTEST_CMD -m slow tests/
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo "Usage: $0 [all|unit|integration|agent|api|fast|slow] [yes|no]"
        echo ""
        echo "Examples:"
        echo "  $0 all yes          # Run all tests with coverage"
        echo "  $0 unit no          # Run unit tests without coverage"
        echo "  $0 fast yes         # Run fast tests with coverage"
        exit 1
        ;;
esac

# Check test results
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"

    if [ "$COVERAGE" = "yes" ]; then
        echo ""
        echo "📊 Coverage report generated:"
        echo "  - Terminal: See above"
        echo "  - HTML: htmlcov/index.html"
        echo "  - XML: coverage.xml"
    fi
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $TEST_EXIT_CODE
