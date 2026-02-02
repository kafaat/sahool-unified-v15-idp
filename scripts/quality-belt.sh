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

    cd "$PROJECT_ROOT"

    # TypeScript type check - Admin
    echo "Checking TypeScript (admin)..."
    if cd apps/admin && npx tsc --noEmit --skipLibCheck 2>/dev/null; then
        print_status "TypeScript (admin)" 0
    else
        print_status "TypeScript (admin)" 1
    fi
    cd "$PROJECT_ROOT"

    # ESLint
    echo "Running ESLint..."
    if cd apps/web && npx eslint src/ --max-warnings=50 --quiet 2>/dev/null; then
        print_status "ESLint (web)" 0
    else
        print_warning "ESLint found issues"
    fi
    cd "$PROJECT_ROOT"

    # Vitest tests
    if [ "$QUICK" != "true" ]; then
        echo "Running Vitest tests..."
        if cd apps/web && npm run test -- --run --reporter=dot 2>/dev/null; then
            print_status "Vitest tests" 0
        else
            print_status "Vitest tests" 1
        fi
        cd "$PROJECT_ROOT"
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

    # Check if we should use Melos
    USE_MELOS=false
    if command -v melos &> /dev/null && [ -f "apps/mobile/melos.yaml" ]; then
        USE_MELOS=true
        echo "Using Melos for monorepo management..."
    fi

    # Flutter analyze
    echo "Running Flutter analyze..."
    if [ "$USE_MELOS" = true ]; then
        if cd apps/mobile && melos run analyze 2>/dev/null; then
            print_status "Flutter analyze (Melos)" 0
        else
            print_warning "Flutter analyze found issues"
        fi
        cd "$PROJECT_ROOT"
    else
        if cd apps/mobile && flutter analyze --no-fatal-infos 2>/dev/null; then
            print_status "Flutter analyze" 0
        else
            print_warning "Flutter analyze found issues"
        fi
        cd "$PROJECT_ROOT"
    fi

    # Dart format check
    echo "Checking Dart formatting..."
    if cd apps/mobile && dart format --set-exit-if-changed --output=none lib/ 2>/dev/null; then
        print_status "Dart format" 0
    else
        print_warning "Some Dart files need formatting (run: dart format .)"
    fi
    cd "$PROJECT_ROOT"

    # Import sorting check (if import_sorter is available)
    if [ -f "apps/mobile/import_sorter.yaml" ]; then
        echo "Checking import sorting..."
        if cd apps/mobile && dart run import_sorter:main --exit-if-changed 2>/dev/null; then
            print_status "Import sorting" 0
        else
            print_warning "Some imports need sorting (run: dart run import_sorter:main)"
        fi
        cd "$PROJECT_ROOT"
    fi

    # Flutter tests
    if [ "$QUICK" != "true" ]; then
        echo "Running Flutter tests..."
        if [ "$USE_MELOS" = true ]; then
            if cd apps/mobile && melos run test 2>/dev/null; then
                print_status "Flutter tests (Melos)" 0
            else
                print_status "Flutter tests" 1
            fi
            cd "$PROJECT_ROOT"
        else
            if cd apps/mobile && flutter test --reporter=compact 2>/dev/null; then
                print_status "Flutter tests" 0
            else
                print_status "Flutter tests" 1
            fi
            cd "$PROJECT_ROOT"
        fi
    fi

    # Code generation check (build_runner)
    if [ "$QUICK" != "true" ]; then
        echo "Checking code generation..."
        if cd apps/mobile && dart run build_runner build --delete-conflicting-outputs 2>/dev/null; then
            print_status "Code generation" 0
        else
            print_warning "Code generation needs update (run: dart run build_runner build)"
        fi
        cd "$PROJECT_ROOT"
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
