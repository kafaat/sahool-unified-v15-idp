#!/bin/bash
# ============================================================================
# SAHOOL Quality Belt - حزام الجودة الموحد
# ============================================================================
# Unified quality checks for all platforms:
# - Python (Ruff, Mypy, Pytest)
# - TypeScript (ESLint, TypeScript, Vitest)
# - Flutter (Analyze, Format, Test)
#
# Usage:
#   ./scripts/quality-belt.sh           # Run all checks
#   ./scripts/quality-belt.sh python    # Python only
#   ./scripts/quality-belt.sh typescript # TypeScript only
#   ./scripts/quality-belt.sh flutter   # Flutter only
#   ./scripts/quality-belt.sh quick     # Quick checks only
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Print header
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

# Print status
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $1${NC}"
        ((FAILED++))
    fi
}

# Print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARNINGS++))
}

# ============================================================================
# PYTHON CHECKS
# ============================================================================
check_python() {
    print_header "🐍 Python Quality Checks"

    # Ruff lint
    echo "Running Ruff linter..."
    if ruff check apps/ shared/ --fix --quiet 2>/dev/null; then
        print_status "Ruff lint" 0
    else
        print_status "Ruff lint" 1
    fi

    # Ruff format check
    echo "Checking Ruff formatting..."
    if ruff format --check apps/ shared/ --quiet 2>/dev/null; then
        print_status "Ruff format" 0
    else
        print_warning "Some files need formatting (run: ruff format .)"
    fi

    # Mypy type check (optional, slower)
    if [ "$QUICK" != "true" ]; then
        echo "Running Mypy type checker..."
        if mypy shared/ --ignore-missing-imports --no-error-summary --quiet 2>/dev/null; then
            print_status "Mypy type check" 0
        else
            print_warning "Mypy found type issues"
        fi
    fi

    # Pytest smoke tests
    echo "Running smoke tests..."
    if python -m pytest tests/smoke/ -x -q --no-header 2>/dev/null; then
        print_status "Smoke tests" 0
    else
        print_status "Smoke tests" 1
    fi

    # Bandit security check
    if [ "$QUICK" != "true" ]; then
        echo "Running Bandit security check..."
        if bandit -r shared/ -q -ll 2>/dev/null; then
            print_status "Bandit security" 0
        else
            print_warning "Bandit found security issues"
        fi
    fi
}

# ============================================================================
# TYPESCRIPT CHECKS
# ============================================================================
check_typescript() {
    print_header "📘 TypeScript Quality Checks"

    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_warning "npm not found, skipping TypeScript checks"
        return
    fi

    # TypeScript type check - Web
    echo "Checking TypeScript (web)..."
    if cd apps/web && npx tsc --noEmit --skipLibCheck 2>/dev/null; then
        print_status "TypeScript (web)" 0
    else
        print_status "TypeScript (web)" 1
    fi
    cd - > /dev/null

    # TypeScript type check - Admin
    echo "Checking TypeScript (admin)..."
    if cd apps/admin && npx tsc --noEmit --skipLibCheck 2>/dev/null; then
        print_status "TypeScript (admin)" 0
    else
        print_status "TypeScript (admin)" 1
    fi
    cd - > /dev/null

    # ESLint
    echo "Running ESLint..."
    if cd apps/web && npx eslint src/ --max-warnings=50 --quiet 2>/dev/null; then
        print_status "ESLint (web)" 0
    else
        print_warning "ESLint found issues"
    fi
    cd - > /dev/null

    # Vitest tests
    if [ "$QUICK" != "true" ]; then
        echo "Running Vitest tests..."
        if cd apps/web && npm run test -- --run --reporter=dot 2>/dev/null; then
            print_status "Vitest tests" 0
        else
            print_status "Vitest tests" 1
        fi
        cd - > /dev/null
    fi
}

# ============================================================================
# FLUTTER CHECKS
# ============================================================================
check_flutter() {
    print_header "🦋 Flutter Quality Checks"

    # Check if flutter is available
    if ! command -v flutter &> /dev/null; then
        print_warning "Flutter not found, skipping Flutter checks"
        return
    fi

    # Flutter analyze
    echo "Running Flutter analyze..."
    if cd apps/mobile && flutter analyze --no-fatal-infos 2>/dev/null; then
        print_status "Flutter analyze" 0
    else
        print_warning "Flutter analyze found issues"
    fi
    cd - > /dev/null

    # Dart format check
    echo "Checking Dart formatting..."
    if cd apps/mobile && dart format --set-exit-if-changed --output=none lib/ 2>/dev/null; then
        print_status "Dart format" 0
    else
        print_warning "Some Dart files need formatting (run: dart format .)"
    fi
    cd - > /dev/null

    # Flutter tests
    if [ "$QUICK" != "true" ]; then
        echo "Running Flutter tests..."
        if cd apps/mobile && flutter test --reporter=compact 2>/dev/null; then
            print_status "Flutter tests" 0
        else
            print_status "Flutter tests" 1
        fi
        cd - > /dev/null
    fi
}

# ============================================================================
# SECURITY CHECKS
# ============================================================================
check_security() {
    print_header "🔒 Security Checks"

    # Detect secrets
    echo "Checking for secrets..."
    if detect-secrets scan --baseline .secrets.baseline > /dev/null 2>&1; then
        print_status "Secret detection" 0
    else
        print_warning "New secrets may have been detected"
    fi

    # Check for .env files
    echo "Checking for .env files..."
    if ! find . -name ".env" -not -name "*.example" -type f 2>/dev/null | grep -q .; then
        print_status "No .env files" 0
    else
        print_warning ".env files found in repository"
    fi

    # Gitleaks (if available)
    if command -v gitleaks &> /dev/null; then
        echo "Running Gitleaks..."
        if gitleaks detect --no-git --quiet 2>/dev/null; then
            print_status "Gitleaks" 0
        else
            print_warning "Gitleaks found potential secrets"
        fi
    fi
}

# ============================================================================
# SUMMARY
# ============================================================================
print_summary() {
    print_header "📊 Quality Belt Summary"

    echo -e "Passed:   ${GREEN}$PASSED${NC}"
    echo -e "Failed:   ${RED}$FAILED${NC}"
    echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"

    if [ $FAILED -gt 0 ]; then
        echo -e "\n${RED}❌ Quality checks failed!${NC}"
        exit 1
    elif [ $WARNINGS -gt 0 ]; then
        echo -e "\n${YELLOW}⚠️ Quality checks passed with warnings${NC}"
        exit 0
    else
        echo -e "\n${GREEN}✅ All quality checks passed!${NC}"
        exit 0
    fi
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    print_header "🎯 SAHOOL Quality Belt - حزام الجودة الموحد"
    echo "Starting quality checks at $(date)"

    case "${1:-all}" in
        python)
            check_python
            ;;
        typescript|ts)
            check_typescript
            ;;
        flutter|dart)
            check_flutter
            ;;
        security)
            check_security
            ;;
        quick)
            QUICK=true
            check_python
            check_typescript
            check_flutter
            ;;
        all)
            check_python
            check_typescript
            check_flutter
            check_security
            ;;
        *)
            echo "Usage: $0 {python|typescript|flutter|security|quick|all}"
            exit 1
            ;;
    esac

    print_summary
}

# Run main
main "$@"
