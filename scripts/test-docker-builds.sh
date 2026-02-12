#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Docker Build Test Script
# Tests building a sample of services to verify Dockerfiles work correctly
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
TOTAL_BUILDS=0
SUCCESS_BUILDS=0
FAILED_BUILDS=0

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_build() {
    ((TOTAL_BUILDS++))
    echo -ne "  [BUILD] $1..."
}

print_success() {
    ((SUCCESS_BUILDS++))
    echo -e " ${GREEN}✓ SUCCESS${NC}"
}

print_fail() {
    ((FAILED_BUILDS++))
    echo -e " ${RED}✗ FAILED${NC}"
    if [ -n "$1" ]; then
        echo -e "    ${RED}Error: $1${NC}"
    fi
}

cd "$PROJECT_ROOT"

print_header "SAHOOL Docker Build Test"

echo "Testing representative services from each category..."
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Infrastructure Services (pre-built images - skip)
# ─────────────────────────────────────────────────────────────────────────────
print_header "Infrastructure Services (using pre-built images)"
echo "  ℹ️  postgres, redis, nats, vault, kong - using official images (skipped)"

# ─────────────────────────────────────────────────────────────────────────────
# Node.js Services
# ─────────────────────────────────────────────────────────────────────────────
print_header "Node.js Services (5 representative samples)"

NODEJS_SERVICES=(
    "field-management-service"
    "marketplace-service"
    "crop-growth-model"
    "lai-estimation"
    "disaster-assessment"
)

for service in "${NODEJS_SERVICES[@]}"; do
    print_build "$service (Node.js)"
    if docker compose build "$service" --quiet > /tmp/build-${service}.log 2>&1; then
        print_success
    else
        print_fail "Check /tmp/build-${service}.log for details"
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# Python Services
# ─────────────────────────────────────────────────────────────────────────────
print_header "Python Services (10 representative samples)"

PYTHON_SERVICES=(
    "advisory-service"
    "vegetation-analysis-service"
    "indicators-service"
    "weather-service"
    "irrigation-smart"
    "crop-intelligence-service"
    "billing-core"
    "notification-service"
    "task-service"
    "equipment-service"
)

for service in "${PYTHON_SERVICES[@]}"; do
    print_build "$service (Python)"
    if docker compose build "$service" --quiet > /tmp/build-${service}.log 2>&1; then
        print_success
    else
        print_fail "Check /tmp/build-${service}.log for details"
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# AI/Vision Services (GPU-aware)
# ─────────────────────────────────────────────────────────────────────────────
print_header "AI/Vision Services (3 samples)"

AI_SERVICES=(
    "ai-agents-service"
    "llm-orchestrator-service"
    "yolo26-vision-service"
)

for service in "${AI_SERVICES[@]}"; do
    print_build "$service (AI/Vision)"
    if docker compose build "$service" --quiet > /tmp/build-${service}.log 2>&1; then
        print_success
    else
        print_fail "Check /tmp/build-${service}.log for details"
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# Terrain & Edge Services (New)
# ─────────────────────────────────────────────────────────────────────────────
print_header "Terrain & Edge Services (3 samples)"

TERRAIN_SERVICES=(
    "terrain-core-service"
    "hydrology-service"
    "edge-orchestrator-service"
)

for service in "${TERRAIN_SERVICES[@]}"; do
    print_build "$service (Terrain/Edge)"
    if docker compose build "$service" --quiet > /tmp/build-${service}.log 2>&1; then
        print_success
    else
        print_fail "Check /tmp/build-${service}.log for details"
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print_header "Build Test Summary"

echo -e "Total Builds:   ${BLUE}$TOTAL_BUILDS${NC}"
echo -e "Successful:     ${GREEN}$SUCCESS_BUILDS${NC}"
echo -e "Failed:         ${RED}$FAILED_BUILDS${NC}"

if [ "$FAILED_BUILDS" -eq 0 ]; then
    echo -e "\n${GREEN}✓ All builds successful!${NC}\n"
    echo "The platform is ready to be deployed."
    exit 0
else
    echo -e "\n${RED}✗ Some builds failed.${NC}\n"
    echo "Check /tmp/build-*.log files for details."
    exit 1
fi
