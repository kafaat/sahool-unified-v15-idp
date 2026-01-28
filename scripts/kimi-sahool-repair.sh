#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Kimi SAHOOL Repair Agent - وكيل إصلاح كيمي لمنصة سهول
# Automated code quality and security scanning with auto-fix capabilities
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 16.0.0
# Usage: ./scripts/kimi-sahool-repair.sh [--scan-only] [--apply-fixes]
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
CONFIG_FILE=".kimi-agents/sahool-repair-config.yaml"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCAN_ONLY=false
APPLY_FIXES=false
OUTPUT_JSON=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --scan-only)
      SCAN_ONLY=true
      shift
      ;;
    --apply-fixes)
      APPLY_FIXES=true
      shift
      ;;
    --output-json)
      OUTPUT_JSON="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--scan-only] [--apply-fixes] [--output-json FILE]"
      exit 1
      ;;
  esac
done

cd "$REPO_ROOT"

echo -e "${PURPLE}════════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}  🤖 وكيل إصلاح Kimi v16.0 - Kimi Repair Agent v16.0${NC}"
echo -e "${PURPLE}  منصة سهول الزراعية الموحدة - SAHOOL Unified Platform${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# المرحلة 1: فحص كل طبقة - Phase 1: Scan All Layers
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${CYAN}📊 المرحلة 1: فحص جميع الطبقات - Phase 1: Scanning All Layers...${NC}"
echo ""

# Create temp directory for scan results
TEMP_DIR="/tmp/kimi-scan-$$"
mkdir -p "$TEMP_DIR"

# Track statistics
TOTAL_ISSUES=0
FRONTEND_ISSUES=0
BACKEND_ISSUES=0
INFRA_ISSUES=0
MOBILE_ISSUES=0

# ─────────────────────────────────────────────────────────────────────────────
# Frontend Scanning
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}   🔍 فحص Frontend - Scanning Frontend...${NC}"

if command -v npx &> /dev/null; then
  if [ -f "$REPO_ROOT/package.json" ]; then
    # ESLint scan
    npx eslint apps/web apps/admin packages --format json --output-file "$TEMP_DIR/eslint-frontend.json" 2>/dev/null || true
    
    if [ -f "$TEMP_DIR/eslint-frontend.json" ]; then
      FRONTEND_ISSUES=$(jq 'reduce .[] as $item (0; . + ($item.errorCount + $item.warningCount))' "$TEMP_DIR/eslint-frontend.json" 2>/dev/null || echo "0")
      echo -e "${GREEN}      ✅ ESLint scan completed: $FRONTEND_ISSUES issues found${NC}"
    fi
  fi
else
  echo -e "${YELLOW}      ⚠️ npm/npx not found, skipping frontend scan${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Backend Scanning
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}   🔍 فحص Backend - Scanning Backend...${NC}"

# Ruff check
if command -v ruff &> /dev/null; then
  ruff check apps/kernel apps/services shared --output-format json > "$TEMP_DIR/ruff-backend.json" 2>/dev/null || true
  
  if [ -f "$TEMP_DIR/ruff-backend.json" ]; then
    RUFF_ISSUES=$(jq 'length' "$TEMP_DIR/ruff-backend.json" 2>/dev/null || echo "0")
    echo -e "${GREEN}      ✅ Ruff scan completed: $RUFF_ISSUES issues found${NC}"
    BACKEND_ISSUES=$((BACKEND_ISSUES + RUFF_ISSUES))
  fi
else
  echo -e "${YELLOW}      ⚠️ Ruff not found, skipping Ruff scan${NC}"
fi

# Bandit security scan
if command -v bandit &> /dev/null; then
  bandit -r apps/kernel apps/services shared -f json -o "$TEMP_DIR/bandit-backend.json" -ll 2>/dev/null || true
  
  if [ -f "$TEMP_DIR/bandit-backend.json" ]; then
    BANDIT_ISSUES=$(jq '.results | length' "$TEMP_DIR/bandit-backend.json" 2>/dev/null || echo "0")
    echo -e "${GREEN}      ✅ Bandit scan completed: $BANDIT_ISSUES security issues found${NC}"
    BACKEND_ISSUES=$((BACKEND_ISSUES + BANDIT_ISSUES))
  fi
else
  echo -e "${YELLOW}      ⚠️ Bandit not found, skipping security scan${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Infrastructure Scanning
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}   🔍 فحص Infrastructure - Scanning Infrastructure...${NC}"

# Docker Lint
if command -v docker &> /dev/null; then
  for dockerfile in $(find . -name "Dockerfile*" -not -path "*/node_modules/*" -not -path "*/.next/*" | head -5); do
    docker run --rm -i hadolint/hadolint < "$dockerfile" >> "$TEMP_DIR/docker-lint.txt" 2>/dev/null || true
  done
  
  if [ -f "$TEMP_DIR/docker-lint.txt" ]; then
    DOCKER_ISSUES=$(wc -l < "$TEMP_DIR/docker-lint.txt" | tr -d ' ')
    echo -e "${GREEN}      ✅ Dockerfile lint completed: $DOCKER_ISSUES issues found${NC}"
    INFRA_ISSUES=$((INFRA_ISSUES + DOCKER_ISSUES))
  fi
else
  echo -e "${YELLOW}      ⚠️ Docker not found, skipping Dockerfile lint${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Mobile Scanning (Flutter)
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}   🔍 فحص Mobile - Scanning Mobile...${NC}"

if [ -d "apps/mobile" ]; then
  if command -v flutter &> /dev/null; then
    cd apps/mobile
    flutter analyze > "$TEMP_DIR/flutter-analyze.txt" 2>/dev/null || true
    cd "$REPO_ROOT"
    
    if [ -f "$TEMP_DIR/flutter-analyze.txt" ]; then
      MOBILE_ISSUES=$(grep -c "•" "$TEMP_DIR/flutter-analyze.txt" 2>/dev/null || echo "0")
      echo -e "${GREEN}      ✅ Flutter analyze completed: $MOBILE_ISSUES issues found${NC}"
    fi
  else
    echo -e "${YELLOW}      ⚠️ Flutter not found, skipping mobile scan${NC}"
  fi
fi

# Calculate total issues
TOTAL_ISSUES=$((FRONTEND_ISSUES + BACKEND_ISSUES + INFRA_ISSUES + MOBILE_ISSUES))

echo ""
echo -e "${GREEN}✅ فحص اكتمل - Scan completed!${NC}"
echo -e "${CYAN}   📊 Total Issues: $TOTAL_ISSUES${NC}"
echo -e "${CYAN}   - Frontend: $FRONTEND_ISSUES${NC}"
echo -e "${CYAN}   - Backend: $BACKEND_ISSUES${NC}"
echo -e "${CYAN}   - Infrastructure: $INFRA_ISSUES${NC}"
echo -e "${CYAN}   - Mobile: $MOBILE_ISSUES${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Output JSON if requested
# ═══════════════════════════════════════════════════════════════════════════════

if [ -n "$OUTPUT_JSON" ]; then
  cat > "$OUTPUT_JSON" <<EOF
{
  "total_issues": $TOTAL_ISSUES,
  "frontend": {
    "issues": $FRONTEND_ISSUES,
    "tools": ["eslint"]
  },
  "backend": {
    "issues": $BACKEND_ISSUES,
    "tools": ["ruff", "bandit"]
  },
  "infrastructure": {
    "issues": $INFRA_ISSUES,
    "tools": ["hadolint"]
  },
  "mobile": {
    "issues": $MOBILE_ISSUES,
    "tools": ["flutter_analyze"]
  },
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "16.0.0"
}
EOF
  echo -e "${GREEN}📄 Results saved to: $OUTPUT_JSON${NC}"
fi

# If scan-only mode, exit here
if [ "$SCAN_ONLY" = true ]; then
  echo -e "${YELLOW}📋 Scan-only mode - exiting without applying fixes${NC}"
  rm -rf "$TEMP_DIR"
  exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# المرحلة 2: توليد الإصلاحات - Phase 2: Generate Fixes
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$APPLY_FIXES" = true ] && [ $TOTAL_ISSUES -gt 0 ]; then
  echo ""
  echo -e "${CYAN}🔧 المرحلة 2: تطبيق الإصلاحات - Phase 2: Applying Fixes...${NC}"
  echo ""
  
  # Apply ESLint fixes
  if [ $FRONTEND_ISSUES -gt 0 ] && command -v npx &> /dev/null; then
    echo -e "${BLUE}   🔧 Applying ESLint fixes...${NC}"
    npx eslint apps/web apps/admin packages --fix 2>/dev/null || true
    echo -e "${GREEN}      ✅ ESLint fixes applied${NC}"
  fi
  
  # Apply Ruff fixes
  if [ $BACKEND_ISSUES -gt 0 ] && command -v ruff &> /dev/null; then
    echo -e "${BLUE}   🔧 Applying Ruff fixes...${NC}"
    ruff check apps/kernel apps/services shared --fix 2>/dev/null || true
    echo -e "${GREEN}      ✅ Ruff fixes applied${NC}"
  fi
  
  echo ""
  echo -e "${GREEN}✅ الإصلاحات اكتملت - Fixes completed!${NC}"
  echo -e "${YELLOW}📝 Please review the changes and commit them${NC}"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}  🏁 اكتمل وكيل الإصلاح - Repair Agent Completed${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════${NC}"
echo ""
