#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Pre-commit Secret Check
# Run before commits to prevent accidental secret exposure
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

echo "🔍 Checking for secrets in staged files..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [[ -z "$STAGED_FILES" ]]; then
    echo -e "${GREEN}✅ No staged files to check${NC}"
    exit 0
fi

# Patterns to check
check_pattern() {
    local pattern="$1"
    local description="$2"

    if echo "$STAGED_FILES" | xargs grep -lE "$pattern" 2>/dev/null | head -1 | grep -q .; then
        echo -e "${RED}❌ Found: $description${NC}"
        echo "$STAGED_FILES" | xargs grep -lE "$pattern" 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi
}

# Check for common secret patterns
check_pattern "password\s*=\s*['\"][^'\"]{8,}['\"]" "Hardcoded passwords"
check_pattern "secret\s*=\s*['\"][^'\"]{8,}['\"]" "Hardcoded secrets"
check_pattern "api_key\s*=\s*['\"][^'\"]{16,}['\"]" "Hardcoded API keys"
check_pattern "-----BEGIN RSA PRIVATE KEY-----" "RSA private keys"
check_pattern "-----BEGIN PRIVATE KEY-----" "Private keys"
check_pattern "-----BEGIN EC PRIVATE KEY-----" "EC private keys"
check_pattern "AKIA[0-9A-Z]{16}" "AWS Access Key IDs"
check_pattern "ghp_[a-zA-Z0-9]{36}" "GitHub Personal Access Tokens"

# Check for sensitive file types
for file in $STAGED_FILES; do
    case "$file" in
        *.pem|*.key|*.p12|*.pfx)
            echo -e "${RED}❌ Sensitive file type: $file${NC}"
            ERRORS=$((ERRORS + 1))
            ;;
        .env|.env.local|.env.*.local)
            echo -e "${RED}❌ Environment file: $file${NC}"
            ERRORS=$((ERRORS + 1))
            ;;
        *credentials*|*secrets*)
            echo -e "${YELLOW}⚠️ Potentially sensitive: $file${NC}"
            ;;
    esac
done

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ❌ SECRET CHECK FAILED - $ERRORS issue(s) found${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Please remove secrets from your commit or add them to .gitignore"
    echo "If this is a false positive, you can skip with: git commit --no-verify"
    exit 1
fi

echo -e "${GREEN}✅ No secrets detected in staged files${NC}"
exit 0
