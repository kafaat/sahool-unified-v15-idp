#!/bin/bash
# SAHOOL MCP Integration Validation Script
# Validates that all MCP components are properly installed

set -e

echo "======================================"
echo "SAHOOL MCP Integration Validator"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Test function
test_file() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (missing: $file)"
        ((FAILED++))
    fi
}

test_dir() {
    local dir=$1
    local description=$2

    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (missing: $dir)"
        ((FAILED++))
    fi
}

echo "1. Checking Core MCP Module (shared/mcp/)"
echo "-------------------------------------------"
test_dir "shared/mcp" "MCP module directory exists"
test_file "shared/mcp/__init__.py" "Package initialization"
test_file "shared/mcp/server.py" "MCP server implementation"
test_file "shared/mcp/client.py" "MCP client implementation"
test_file "shared/mcp/tools.py" "Agricultural tools"
test_file "shared/mcp/resources.py" "Resource providers"
test_file "shared/mcp/examples.py" "Usage examples"
test_file "shared/mcp/README.md" "Module documentation"
echo ""

echo "2. Checking MCP Server Service (apps/services/mcp-server/)"
echo "-----------------------------------------------------------"
test_dir "apps/services/mcp-server" "MCP server service directory"
test_dir "apps/services/mcp-server/src" "Source directory"
test_file "apps/services/mcp-server/src/main.py" "FastAPI application"
test_file "apps/services/mcp-server/src/__init__.py" "Package init"
test_file "apps/services/mcp-server/Dockerfile" "Docker configuration"
test_file "apps/services/mcp-server/requirements.txt" "Python dependencies"
test_file "apps/services/mcp-server/run.sh" "Startup script"
test_file "apps/services/mcp-server/README.md" "Service documentation"
test_dir "apps/services/mcp-server/tests" "Tests directory"
test_file "apps/services/mcp-server/tests/test_mcp_server.py" "Test suite"
echo ""

echo "3. Checking Configuration Files"
echo "--------------------------------"
test_file "mcp.json" "MCP configuration"
test_file "requirements/mcp.txt" "MCP requirements"
echo ""

echo "4. Checking Documentation"
echo "-------------------------"
test_file "docs/MCP_INTEGRATION.md" "Integration guide"
test_file "MCP_QUICK_START.md" "Quick start guide"
test_file "MCP_IMPLEMENTATION_SUMMARY.md" "Implementation summary"
echo ""

echo "5. Checking Docker Integration"
echo "-------------------------------"
if grep -q "mcp-server:" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} MCP server in docker-compose.yml"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} MCP server not in docker-compose.yml"
    ((FAILED++))
fi
echo ""

echo "6. Validating Python Syntax"
echo "----------------------------"
if command -v python3 &> /dev/null; then
    for file in shared/mcp/*.py apps/services/mcp-server/src/*.py; do
        if [ -f "$file" ]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} $(basename $file) - syntax valid"
                ((PASSED++))
            else
                echo -e "${RED}✗${NC} $(basename $file) - syntax error"
                ((FAILED++))
            fi
        fi
    done
else
    echo -e "${YELLOW}⚠${NC} Python3 not found, skipping syntax validation"
fi
echo ""

echo "7. Checking Executable Permissions"
echo "-----------------------------------"
if [ -x "apps/services/mcp-server/run.sh" ]; then
    echo -e "${GREEN}✓${NC} run.sh is executable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} run.sh is not executable"
    ((FAILED++))
fi
echo ""

# Summary
echo "======================================"
echo "Validation Summary"
echo "======================================"
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validation checks passed!${NC}"
    echo ""
    echo "MCP Integration is ready to use."
    echo ""
    echo "Next steps:"
    echo "  1. Start services: docker-compose up -d"
    echo "  2. Check health: curl http://localhost:8200/health"
    echo "  3. View docs: open http://localhost:8200/docs"
    echo "  4. Read guide: cat MCP_QUICK_START.md"
    exit 0
else
    echo -e "${RED}✗ Some validation checks failed!${NC}"
    echo "Please review the errors above."
    exit 1
fi
