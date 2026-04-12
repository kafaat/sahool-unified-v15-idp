#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Version Bump Script
# سكربت ترقية إصدار منصة سهول
# ═══════════════════════════════════════════════════════════════════════════════
#
# Bumps version across all platform files:
#   - pyproject.toml (Python root)
#   - package.json (Node.js root + workspaces)
#   - docker-compose.yml (labels)
#   - governance/services.yaml
#   - apps/mobile/pubspec.yaml (Flutter)
#
# Usage:
#   ./scripts/bump-version.sh <new_version>
#   ./scripts/bump-version.sh 16.1.0
#   ./scripts/bump-version.sh 17.0.0 --dry-run
#
# Exit codes:
#   0 - Version bumped successfully
#   1 - Error (invalid version, file not found)
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

DRY_RUN=false
NEW_VERSION=""

# ─────────────────────────────────────────────────────────────────────────────
# Parse arguments
# ─────────────────────────────────────────────────────────────────────────────
usage() {
    echo "Usage: $0 <new_version> [--dry-run]"
    echo ""
    echo "Examples:"
    echo "  $0 16.1.0          # Bump to 16.1.0"
    echo "  $0 17.0.0 --dry-run  # Preview changes"
    echo ""
    echo "Affected files:"
    echo "  - pyproject.toml"
    echo "  - package.json (root)"
    echo "  - governance/services.yaml"
    echo "  - apps/mobile/pubspec.yaml"
    echo "  - apps/mobile/sahool_field_app/pubspec.yaml"
    exit 1
}

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --help|-h) usage ;;
        *) NEW_VERSION="$arg" ;;
    esac
done

if [ -z "$NEW_VERSION" ]; then
    echo -e "${RED}Error: Version number required${NC}"
    usage
fi

# Validate semver format
if ! echo "$NEW_VERSION" | grep -qP '^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'; then
    echo -e "${RED}Error: Invalid version format. Use semver (e.g., 16.1.0)${NC}"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Detect current version
# ─────────────────────────────────────────────────────────────────────────────
CURRENT_VERSION=$(grep -oP '^version\s*=\s*"\K[^"]+' "$PROJECT_ROOT/pyproject.toml" 2>/dev/null || echo "unknown")

echo -e "\n${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}${BOLD}  SAHOOL Platform - Version Bump${NC}"
echo -e "${BLUE}${BOLD}  ترقية إصدار منصة سهول${NC}"
echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}\n"
echo -e "  Current version: ${YELLOW}${CURRENT_VERSION}${NC}"
echo -e "  New version:     ${GREEN}${NEW_VERSION}${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "  Mode:            ${YELLOW}DRY RUN (no changes)${NC}"
fi
echo ""

if [ "$CURRENT_VERSION" = "$NEW_VERSION" ]; then
    echo -e "${YELLOW}Version is already ${NEW_VERSION}. Nothing to do.${NC}"
    exit 0
fi

CHANGES=0

# ─────────────────────────────────────────────────────────────────────────────
# Bump functions
# ─────────────────────────────────────────────────────────────────────────────
bump_file() {
    local file="$1"
    local pattern="$2"
    local replacement="$3"
    local description="$4"

    local rel_path="${file#$PROJECT_ROOT/}"

    if [ ! -f "$file" ]; then
        echo -e "  ${YELLOW}⚠${NC} $rel_path (not found, skipping)"
        return
    fi

    if grep -qP "$pattern" "$file"; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "  ${BLUE}○${NC} $rel_path - $description"
            grep -nP "$pattern" "$file" | head -3 | while read -r line; do
                echo -e "    ${YELLOW}${line}${NC}"
            done
        else
            sed -i -E "s/$pattern/$replacement/g" "$file"
            echo -e "  ${GREEN}✓${NC} $rel_path - $description"
        fi
        CHANGES=$((CHANGES + 1))
    else
        echo -e "  ${YELLOW}─${NC} $rel_path (no match)"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Execute bumps
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BOLD}Updating files:${NC}\n"

# 1. pyproject.toml
bump_file \
    "$PROJECT_ROOT/pyproject.toml" \
    "^version = \"$CURRENT_VERSION\"" \
    "version = \"$NEW_VERSION\"" \
    "Python project version"

# 2. VERSION file
bump_file \
    "$PROJECT_ROOT/VERSION" \
    "^$CURRENT_VERSION" \
    "$NEW_VERSION" \
    "VERSION file"

# 3. Root package.json
bump_file \
    "$PROJECT_ROOT/package.json" \
    "\"version\": \"$CURRENT_VERSION\"" \
    "\"version\": \"$NEW_VERSION\"" \
    "Node.js root version"

# 3. governance/services.yaml
bump_file \
    "$PROJECT_ROOT/governance/services.yaml" \
    "version: \"?${CURRENT_VERSION}\"?" \
    "version: \"$NEW_VERSION\"" \
    "Service registry version"

# 4. Flutter pubspec.yaml files
for pubspec in \
    "$PROJECT_ROOT/apps/mobile/pubspec.yaml" \
    "$PROJECT_ROOT/apps/mobile/sahool_field_app/pubspec.yaml"; do
    if [ -f "$pubspec" ]; then
        bump_file \
            "$pubspec" \
            "^version: ${CURRENT_VERSION}" \
            "version: ${NEW_VERSION}" \
            "Flutter app version"
    fi
done

# 5. Makefile version reference (if any)
if grep -q "Version: $CURRENT_VERSION" "$PROJECT_ROOT/Makefile" 2>/dev/null; then
    bump_file \
        "$PROJECT_ROOT/Makefile" \
        "Version: $CURRENT_VERSION" \
        "Version: $NEW_VERSION" \
        "Makefile version reference"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}${BOLD}DRY RUN: $CHANGES files would be updated${NC}"
    echo -e "${YELLOW}Run without --dry-run to apply changes${NC}"
else
    echo -e "${GREEN}${BOLD}Version bumped: $CURRENT_VERSION → $NEW_VERSION ($CHANGES files updated)${NC}"
    echo -e "${GREEN}تم ترقية الإصدار بنجاح${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Review changes: git diff"
    echo "  2. Run tests: make test"
    echo "  3. Commit: git commit -am 'chore: bump version to $NEW_VERSION'"
fi
echo ""
