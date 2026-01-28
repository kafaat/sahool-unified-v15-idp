#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Kimi Repair Agent - Scan Script
# سكريبت فحص وكيل إصلاح Kimi لسهول
#
# Integrates Kimi AI with existing linting and analysis tools
# تكامل Kimi AI مع أدوات الفحص والتحليل الموجودة
#
# Usage:
#   ./scripts/kimi-repair-scan.sh [--auto-apply] [--dry-run]
#
# Environment Variables:
#   KIMI_API_KEY         - Kimi AI API key (optional)
#   AUTO_APPLY_FIXES     - Auto-apply fixes (default: false)
#   KIMI_CONFIG          - Path to config file (default: .kimi-agents/repair-agent-config.yaml)
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
KIMI_CONFIG="${KIMI_CONFIG:-${PROJECT_ROOT}/.kimi-agents/repair-agent-config.yaml}"
AUTO_APPLY_FIXES="${AUTO_APPLY_FIXES:-false}"
DRY_RUN="${DRY_RUN:-false}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Parse command-line arguments
# ─────────────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --auto-apply)
      AUTO_APPLY_FIXES=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --config)
      KIMI_CONFIG="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --auto-apply    Automatically apply fixes (requires review disabled)"
      echo "  --dry-run       Run scan without applying fixes"
      echo "  --config PATH   Path to Kimi config file"
      echo "  --help          Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}❌ Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────
log_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "   🤖 Kimi Repair Agent - SAHOOL Platform"
echo "   وكيل إصلاح Kimi - منصة سهول"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Verify Configuration
# ─────────────────────────────────────────────────────────────────────────────
log_info "Verifying configuration..."

if [[ ! -f "${KIMI_CONFIG}" ]]; then
  log_error "Configuration file not found: ${KIMI_CONFIG}"
  exit 1
fi

log_success "Configuration loaded: ${KIMI_CONFIG}"

# ─────────────────────────────────────────────────────────────────────────────
# Check Prerequisites
# ─────────────────────────────────────────────────────────────────────────────
log_info "Checking prerequisites..."

MISSING_TOOLS=()

# Check for Python tools
command -v python3 >/dev/null 2>&1 || MISSING_TOOLS+=("python3")
command -v ruff >/dev/null 2>&1 || log_warning "ruff not found (Python linter)"
command -v mypy >/dev/null 2>&1 || log_warning "mypy not found (Python type checker)"
command -v bandit >/dev/null 2>&1 || log_warning "bandit not found (Python security scanner)"
command -v pytest >/dev/null 2>&1 || log_warning "pytest not found (Python test runner)"

# Check for Node.js tools
command -v node >/dev/null 2>&1 || log_warning "node not found (JavaScript runtime)"
command -v npm >/dev/null 2>&1 || log_warning "npm not found (Node package manager)"

# Check for critical tools
if [[ ${#MISSING_TOOLS[@]} -gt 0 ]]; then
  log_error "Missing required tools: ${MISSING_TOOLS[*]}"
  exit 1
fi

log_success "Prerequisites check passed"

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Run Linting Tools
# المرحلة 1: تشغيل أدوات الفحص
# ─────────────────────────────────────────────────────────────────────────────
echo ""
log_info "═══ Phase 1: Running Linting Tools ═══"
log_info "═══ المرحلة 1: تشغيل أدوات الفحص ═══"
echo ""

# Python - Ruff
if command -v ruff >/dev/null 2>&1; then
  log_info "Running Ruff (Python linter)..."
  ruff check ${PROJECT_ROOT}/apps/services --output-format=json > "${OUTPUT_DIR}/eslint-results.json" 2>&1 || true
  ruff check ${PROJECT_ROOT}/shared --output-format=json >> "${OUTPUT_DIR}/eslint-results.json" 2>&1 || true
  log_success "Ruff scan completed"
else
  log_warning "Skipping Ruff (not installed)"
fi

# Python - Bandit (Security)
if command -v bandit >/dev/null 2>&1; then
  log_info "Running Bandit (Python security scanner)..."
  bandit -r ${PROJECT_ROOT}/apps/services -f json -o "${OUTPUT_DIR}/bandit-results.json" 2>/dev/null || true
  bandit -r ${PROJECT_ROOT}/shared -f json >> "${OUTPUT_DIR}/bandit-results.json" 2>/dev/null || true
  log_success "Bandit scan completed"
else
  log_warning "Skipping Bandit (not installed)"
fi

# Python - Mypy (Type Checking)
if command -v mypy >/dev/null 2>&1; then
  log_info "Running Mypy (Python type checker)..."
  # Note: Mypy might be slow, run on key directories only
  mypy ${PROJECT_ROOT}/shared/ai --show-error-codes --no-error-summary 2>&1 | tee "${OUTPUT_DIR}/mypy-results.txt" || true
  log_success "Mypy scan completed"
else
  log_warning "Skipping Mypy (not installed)"
fi

# Python - Pytest (Test Discovery)
if command -v pytest >/dev/null 2>&1; then
  log_info "Running Pytest (test discovery)..."
  pytest ${PROJECT_ROOT}/tests --collect-only --quiet > "${OUTPUT_DIR}/pytest-collect.txt" 2>&1 || true
  log_success "Test discovery completed"
else
  log_warning "Skipping Pytest (not installed)"
fi

# TypeScript/JavaScript - ESLint
if [[ -f "${PROJECT_ROOT}/package.json" ]] && command -v npm >/dev/null 2>&1; then
  log_info "Running ESLint (TypeScript/JavaScript linter)..."
  cd ${PROJECT_ROOT}
  npm run lint --if-present -- --format=json --output-file="${OUTPUT_DIR}/eslint-results.json" 2>/dev/null || true
  log_success "ESLint scan completed"
else
  log_warning "Skipping ESLint (npm not available or no package.json)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Integrate with Existing Auto-Fix
# المرحلة 2: التكامل مع الإصلاح التلقائي الموجود
# ─────────────────────────────────────────────────────────────────────────────
echo ""
log_info "═══ Phase 2: Running Auto-Fix Engine ═══"
log_info "═══ المرحلة 2: تشغيل محرك الإصلاح التلقائي ═══"
echo ""

if [[ -f "${PROJECT_ROOT}/shared/ai/auto_fix/diagnostic_cli.py" ]]; then
  log_info "Running existing auto-fix diagnostic..."
  cd ${PROJECT_ROOT}
  
  # Run auto-fix diagnostic
  python -m shared.ai.auto_fix.diagnostic_cli \
    --all \
    --output-json "${OUTPUT_DIR}/auto-fix-report.json" \
    2>&1 | tee "${OUTPUT_DIR}/auto-fix-output.txt" || true
  
  log_success "Auto-fix diagnostic completed"
else
  log_warning "Auto-fix engine not found, skipping..."
fi

# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Kimi AI Integration (Optional)
# المرحلة 3: تكامل Kimi AI (اختياري)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
log_info "═══ Phase 3: Kimi AI Integration ═══"
log_info "═══ المرحلة 3: تكامل Kimi AI ═══"
echo ""

if [[ -n "${KIMI_API_KEY}" ]]; then
  log_info "Kimi API key detected, attempting Kimi integration..."
  log_warning "Note: Kimi CLI integration is placeholder (requires Kimi SDK installation)"
  
  # Placeholder for Kimi CLI integration
  # This would require the actual Kimi SDK/CLI to be installed
  # kimi repair-agent --input "${OUTPUT_DIR}/*-results.*" --config "${KIMI_CONFIG}"
  
  log_warning "Kimi integration skipped (SDK not installed)"
else
  log_info "KIMI_API_KEY not set, skipping Kimi AI integration"
  log_info "Using existing auto-fix infrastructure only"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Phase 4: Generate Reports
# المرحلة 4: إنشاء التقارير
# ─────────────────────────────────────────────────────────────────────────────
echo ""
log_info "═══ Phase 4: Generating Reports ═══"
log_info "═══ المرحلة 4: إنشاء التقارير ═══"
echo ""

# Create a summary report
REPORT_FILE="${OUTPUT_DIR}/kimi-report.md"
REPORT_HTML="${OUTPUT_DIR}/kimi-report.html"

log_info "Generating summary report..."

cat > "${REPORT_FILE}" <<EOF
# Kimi Repair Agent - Scan Report
# تقرير فحص وكيل إصلاح Kimi

**Date | التاريخ**: $(date '+%Y-%m-%d %H:%M:%S')  
**Project | المشروع**: SAHOOL Platform  
**Version | الإصدار**: 16.0.0

---

## Summary | ملخص

This report summarizes the automated code analysis performed by the Kimi Repair Agent.

هذا التقرير يلخص تحليل الكود التلقائي الذي قام به وكيل إصلاح Kimi.

## Tools Executed | الأدوات المنفذة

EOF

# List executed tools
if [[ -f "${OUTPUT_DIR}/ruff-results.json" ]]; then
  echo "- ✅ **Ruff**: Python linting" >> "${REPORT_FILE}"
fi

if [[ -f "${OUTPUT_DIR}/bandit-results.json" ]]; then
  echo "- ✅ **Bandit**: Python security scanning" >> "${REPORT_FILE}"
fi

if [[ -f "${OUTPUT_DIR}/mypy-results.txt" ]]; then
  echo "- ✅ **Mypy**: Python type checking" >> "${REPORT_FILE}"
fi

if [[ -f "${OUTPUT_DIR}/eslint-results.json" ]]; then
  echo "- ✅ **ESLint**: JavaScript/TypeScript linting" >> "${REPORT_FILE}"
fi

if [[ -f "${OUTPUT_DIR}/auto-fix-report.json" ]]; then
  echo "- ✅ **Auto-Fix Engine**: SAHOOL auto-fix diagnostics" >> "${REPORT_FILE}"
fi

cat >> "${REPORT_FILE}" <<EOF

## Output Files | ملفات الإخراج

EOF

# List output files
for file in ${OUTPUT_DIR}/*-results.*; do
  if [[ -f "$file" ]]; then
    filename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    echo "- \`$filename\` ($size)" >> "${REPORT_FILE}"
  fi
done

cat >> "${REPORT_FILE}" <<EOF

## Next Steps | الخطوات التالية

1. Review the generated reports in \`${OUTPUT_DIR}/\`
2. Check the auto-fix suggestions
3. Apply fixes manually or with \`--auto-apply\` flag (requires review)
4. Create a pull request if fixes are applied

---

**Configuration Used | الإعدادات المستخدمة**: \`${KIMI_CONFIG}\`
EOF

log_success "Report generated: ${REPORT_FILE}"

# Optional: Generate HTML report (simple conversion)
if command -v markdown >/dev/null 2>&1 || command -v pandoc >/dev/null 2>&1; then
  log_info "Converting to HTML..."
  if command -v pandoc >/dev/null 2>&1; then
    pandoc "${REPORT_FILE}" -o "${REPORT_HTML}" --standalone 2>/dev/null || true
  fi
  log_success "HTML report: ${REPORT_HTML}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Phase 5: Apply Fixes (if enabled)
# المرحلة 5: تطبيق الإصلاحات (إذا كانت مفعلة)
# ─────────────────────────────────────────────────────────────────────────────
if [[ "${AUTO_APPLY_FIXES}" == "true" ]] && [[ "${DRY_RUN}" == "false" ]]; then
  echo ""
  log_warning "═══ Phase 5: Applying Fixes ═══"
  log_warning "═══ المرحلة 5: تطبيق الإصلاحات ═══"
  echo ""
  
  log_warning "AUTO_APPLY_FIXES is enabled!"
  log_info "Applying safe auto-fixes..."
  
  # Apply Ruff fixes
  if command -v ruff >/dev/null 2>&1; then
    log_info "Applying Ruff fixes..."
    ruff check ${PROJECT_ROOT}/apps/services --fix || true
    ruff check ${PROJECT_ROOT}/shared --fix || true
    ruff format ${PROJECT_ROOT}/apps/services || true
    ruff format ${PROJECT_ROOT}/shared || true
    log_success "Ruff fixes applied"
  fi
  
  # Git operations
  if command -v git >/dev/null 2>&1; then
    cd ${PROJECT_ROOT}
    
    # Check for changes
    if git diff --quiet; then
      log_info "No changes to commit"
    else
      log_info "Creating commit..."
      
      BRANCH_NAME="kimi-auto/fixes-$(date +%Y%m%d-%H%M%S)"
      
      # Create new branch
      git checkout -b "${BRANCH_NAME}" 2>/dev/null || true
      
      # Stage changes
      git add .
      
      # Commit
      git commit -m "🤖 Kimi Repair Agent: Auto-fixes $(date +%Y-%m-%d)" \
                 -m "Automated fixes applied by Kimi Repair Agent" \
                 -m "- Ruff formatting" \
                 -m "- Code style fixes" \
                 -m "" \
                 -m "Config: ${KIMI_CONFIG}" || true
      
      log_success "Commit created on branch: ${BRANCH_NAME}"
      log_info "To push: git push origin ${BRANCH_NAME}"
    fi
  fi
else
  log_info "Auto-apply is disabled. Review reports and apply fixes manually."
  log_info "تطبيق الإصلاحات معطل. راجع التقارير وطبق الإصلاحات يدوياً."
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
log_success "✅ Kimi Repair Agent scan completed!"
log_success "✅ اكتمل فحص وكيل إصلاح Kimi!"
echo ""
log_info "Reports available at | التقارير متاحة في:"
log_info "  - Markdown: ${REPORT_FILE}"
if [[ -f "${REPORT_HTML}" ]]; then
  log_info "  - HTML: ${REPORT_HTML}"
fi
log_info "  - Output directory | مجلد الإخراج: ${OUTPUT_DIR}/"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

exit 0
