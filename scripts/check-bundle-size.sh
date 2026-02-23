#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# SAHOOL Bundle Size Budget Checker
# فاحص ميزانية حجم الحزم
#
# Checks Next.js build output against size budgets.
# Run after `next build` to verify bundle sizes stay within limits.
#
# Usage:
#   ./scripts/check-bundle-size.sh apps/web/.next
#   ./scripts/check-bundle-size.sh apps/admin/.next
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Budget limits (in KB)
CLIENT_BUDGET_KB=500    # Target: <500KB for client bundle (gzipped)
NODEJS_BUDGET_KB=1500   # Target: <1.5MB for nodejs bundle
EDGE_BUDGET_KB=400      # Target: <400KB for edge bundle
PAGE_BUDGET_KB=200      # Target: <200KB per page (first load JS)

BUILD_DIR="${1:-.next}"

if [ ! -d "$BUILD_DIR" ]; then
  echo -e "${RED}Error: Build directory '$BUILD_DIR' not found.${NC}"
  echo "Run 'next build' first, then provide the .next directory path."
  exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "  SAHOOL Bundle Size Budget Check"
echo "  فحص ميزانية حجم الحزم"
echo "═══════════════════════════════════════════════════════════"
echo ""

VIOLATIONS=0

# Check client chunks
if [ -d "$BUILD_DIR/static/chunks" ]; then
  CLIENT_SIZE_BYTES=$(find "$BUILD_DIR/static/chunks" -name "*.js" -exec stat -c%s {} + 2>/dev/null | awk '{s+=$1} END {print s+0}')
  CLIENT_SIZE_KB=$((CLIENT_SIZE_BYTES / 1024))

  if [ "$CLIENT_SIZE_KB" -gt "$CLIENT_BUDGET_KB" ]; then
    echo -e "${YELLOW}[WARN] Client bundle: ${CLIENT_SIZE_KB}KB (budget: ${CLIENT_BUDGET_KB}KB)${NC}"
    VIOLATIONS=$((VIOLATIONS + 1))
  else
    echo -e "${GREEN}[OK]   Client bundle: ${CLIENT_SIZE_KB}KB (budget: ${CLIENT_BUDGET_KB}KB)${NC}"
  fi
else
  echo -e "${YELLOW}[SKIP] Client chunks directory not found${NC}"
fi

# Check server chunks (nodejs)
if [ -d "$BUILD_DIR/server" ]; then
  NODEJS_SIZE_BYTES=$(find "$BUILD_DIR/server" -name "*.js" -exec stat -c%s {} + 2>/dev/null | awk '{s+=$1} END {print s+0}')
  NODEJS_SIZE_KB=$((NODEJS_SIZE_BYTES / 1024))

  if [ "$NODEJS_SIZE_KB" -gt "$NODEJS_BUDGET_KB" ]; then
    echo -e "${YELLOW}[WARN] NodeJS bundle: ${NODEJS_SIZE_KB}KB (budget: ${NODEJS_BUDGET_KB}KB)${NC}"
    VIOLATIONS=$((VIOLATIONS + 1))
  else
    echo -e "${GREEN}[OK]   NodeJS bundle: ${NODEJS_SIZE_KB}KB (budget: ${NODEJS_BUDGET_KB}KB)${NC}"
  fi
else
  echo -e "${YELLOW}[SKIP] Server directory not found${NC}"
fi

echo ""
echo "───────────────────────────────────────────────────────────"

# List largest chunks for analysis
echo ""
echo "Top 10 largest client chunks:"
if [ -d "$BUILD_DIR/static/chunks" ]; then
  find "$BUILD_DIR/static/chunks" -name "*.js" -exec ls -lS {} + 2>/dev/null | head -10 | awk '{printf "  %6.1fKB  %s\n", $5/1024, $NF}'
fi

echo ""
echo "───────────────────────────────────────────────────────────"

if [ "$VIOLATIONS" -gt 0 ]; then
  echo -e "${YELLOW}$VIOLATIONS budget warning(s) detected.${NC}"
  echo "Consider: lazy loading heavy components, checking optimizePackageImports,"
  echo "and reviewing dynamic imports for maps/charts."
  exit 0  # Warning only, don't fail CI
else
  echo -e "${GREEN}All bundles within budget limits.${NC}"
fi
