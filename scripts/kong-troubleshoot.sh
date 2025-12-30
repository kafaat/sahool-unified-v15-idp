#!/bin/bash
# ============================================================================
# Kong Troubleshooting Script / سكريبت تصحيح أخطاء Kong
# SAHOOL Platform
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "============================================================"
echo "Kong Troubleshooting Script / سكريبت تصحيح أخطاء Kong"
echo "============================================================"
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📁 Project Root: $PROJECT_ROOT${NC}"
echo ""

# ============================================================================
# Step 1: Check if kong.yml file exists
# ============================================================================
echo "============================================================"
echo "Step 1: Checking kong.yml file existence"
echo "============================================================"

KONG_CONFIG="infrastructure/gateway/kong/kong.yml"
if [ -f "$KONG_CONFIG" ]; then
    echo -e "${GREEN}✅ File exists: $KONG_CONFIG${NC}"
    echo "   Size: $(ls -lh "$KONG_CONFIG" | awk '{print $5}')"
    echo "   Type: $(file "$KONG_CONFIG" | cut -d: -f2)"
else
    echo -e "${RED}❌ File NOT found: $KONG_CONFIG${NC}"
    echo "   This will cause Kong to fail!"
    exit 1
fi
echo ""

# ============================================================================
# Step 2: Validate YAML syntax
# ============================================================================
echo "============================================================"
echo "Step 2: Validating YAML syntax"
echo "============================================================"

if command -v python3 &> /dev/null; then
    if python3 -c "import yaml; yaml.safe_load(open('$KONG_CONFIG'))" 2>/dev/null; then
        echo -e "${GREEN}✅ YAML syntax is valid${NC}"
    else
        echo -e "${RED}❌ YAML syntax error${NC}"
        python3 -c "import yaml; yaml.safe_load(open('$KONG_CONFIG'))"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Python3 not available, skipping YAML validation${NC}"
fi
echo ""

# ============================================================================
# Step 3: Check for existing Kong volumes/containers
# ============================================================================
echo "============================================================"
echo "Step 3: Checking existing Kong state"
echo "============================================================"

if command -v docker &> /dev/null; then
    # Check for existing container
    if docker ps -a --format '{{.Names}}' | grep -q "sahool-kong"; then
        echo -e "${YELLOW}⚠️  Existing Kong container found${NC}"
        docker ps -a --filter "name=sahool-kong" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

        echo ""
        echo "Removing existing container..."
        docker rm -f sahool-kong 2>/dev/null || true
        echo -e "${GREEN}✅ Container removed${NC}"
    else
        echo -e "${GREEN}✅ No existing Kong container${NC}"
    fi

    # Check for volumes that might have wrong mounts
    echo ""
    echo "Checking for stale volume mounts..."

    # Check if there's a directory where file should be mounted
    CONTAINER_CHECK=$(docker run --rm -v "$PROJECT_ROOT/infrastructure/gateway/kong/kong.yml:/kong/declarative/kong.yml:ro" kong:3.4 ls -la /kong/declarative/kong.yml 2>&1 || true)

    if echo "$CONTAINER_CHECK" | grep -q "Is a directory"; then
        echo -e "${RED}❌ Volume mount is creating a directory instead of file${NC}"
        echo "   This is the root cause of the issue!"
        echo ""
        echo "Solution: Running cleanup..."
        docker volume prune -f 2>/dev/null || true
        echo -e "${GREEN}✅ Cleanup completed${NC}"
    elif echo "$CONTAINER_CHECK" | grep -q "kong.yml"; then
        echo -e "${GREEN}✅ Volume mount working correctly${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker not available, skipping container checks${NC}"
fi
echo ""

# ============================================================================
# Step 4: Verify Kong configuration compatibility
# ============================================================================
echo "============================================================"
echo "Step 4: Verifying Kong config compatibility"
echo "============================================================"

FORMAT_VERSION=$(grep "_format_version" "$KONG_CONFIG" | head -1 | cut -d'"' -f2)
echo "Format version in config: $FORMAT_VERSION"

if [[ "$FORMAT_VERSION" == "3.0" || "$FORMAT_VERSION" == "2.1" ]]; then
    echo -e "${GREEN}✅ Format version compatible with Kong 3.4${NC}"
else
    echo -e "${YELLOW}⚠️  Format version might not be compatible${NC}"
fi
echo ""

# ============================================================================
# Step 5: Test Kong with declarative config
# ============================================================================
echo "============================================================"
echo "Step 5: Testing Kong startup (dry run)"
echo "============================================================"

if command -v docker &> /dev/null; then
    echo "Running Kong config validation..."

    docker run --rm \
        -v "$PROJECT_ROOT/infrastructure/gateway/kong/kong.yml:/kong/declarative/kong.yml:ro" \
        -e "KONG_DATABASE=off" \
        -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml" \
        kong:3.4 kong config parse /kong/declarative/kong.yml 2>&1 && \
        echo -e "${GREEN}✅ Kong configuration is valid${NC}" || \
        echo -e "${RED}❌ Kong configuration has errors${NC}"
else
    echo -e "${YELLOW}⚠️  Docker not available${NC}"
fi
echo ""

# ============================================================================
# Summary and Fix Command
# ============================================================================
echo "============================================================"
echo "Summary and Fix / الملخص والإصلاح"
echo "============================================================"
echo ""
echo "To fix and restart Kong, run these commands:"
echo ""
echo -e "${BLUE}# 1. Stop all services${NC}"
echo "docker-compose down"
echo ""
echo -e "${BLUE}# 2. Remove any cached volumes${NC}"
echo "docker volume prune -f"
echo ""
echo -e "${BLUE}# 3. Verify the file exists${NC}"
echo "ls -la infrastructure/gateway/kong/kong.yml"
echo ""
echo -e "${BLUE}# 4. Start Kong alone first${NC}"
echo "docker-compose up -d kong"
echo ""
echo -e "${BLUE}# 5. Check Kong logs${NC}"
echo "docker logs sahool-kong"
echo ""
echo -e "${BLUE}# 6. Check Kong health${NC}"
echo "docker inspect sahool-kong --format='{{.State.Health.Status}}'"
echo ""
echo "============================================================"
echo "End of Troubleshooting Script"
echo "============================================================"
