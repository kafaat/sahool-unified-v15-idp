#!/bin/bash
# ============================================================================
# Branch Cleanup Script for SAHOOL Platform
# ============================================================================
# This script identifies and optionally deletes stale branches that haven't
# been updated in the specified number of days.
#
# Usage:
#   ./cleanup-stale-branches.sh [OPTIONS]
#
# Options:
#   --dry-run       Preview branches without deleting (default)
#   --execute       Actually delete the branches
#   --days N        Consider branches older than N days as stale (default: 30)
#   --category CAT  Filter by category: claude, copilot, dependabot, all
#   --help          Show this help message
#
# Examples:
#   ./cleanup-stale-branches.sh --dry-run
#   ./cleanup-stale-branches.sh --execute --days 60
#   ./cleanup-stale-branches.sh --execute --category copilot
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DRY_RUN=true
STALE_DAYS=30
CATEGORY="all"
PROTECTED_BRANCHES="main master develop release gh-pages"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --execute)
            DRY_RUN=false
            shift
            ;;
        --days)
            STALE_DAYS="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --help)
            head -30 "$0" | tail -25
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Calculate cutoff date
if [[ "$OSTYPE" == "darwin"* ]]; then
    CUTOFF_DATE=$(date -v-${STALE_DAYS}d +%Y-%m-%d)
else
    CUTOFF_DATE=$(date -d "${STALE_DAYS} days ago" +%Y-%m-%d)
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   SAHOOL Branch Cleanup Script${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Mode: ${YELLOW}$([ "$DRY_RUN" = true ] && echo "DRY RUN (preview only)" || echo "EXECUTE (will delete branches)")${NC}"
echo -e "Stale threshold: ${YELLOW}${STALE_DAYS} days${NC}"
echo -e "Cutoff date: ${YELLOW}${CUTOFF_DATE}${NC}"
echo -e "Category filter: ${YELLOW}${CATEGORY}${NC}"
echo ""

# Fetch latest remote info
echo -e "${BLUE}Fetching latest branch information...${NC}"
git fetch --prune origin 2>/dev/null

# Get stale branches
echo -e "${BLUE}Analyzing branches...${NC}"
echo ""

STALE_COUNT=0
DELETED_COUNT=0

# Build grep pattern for category
case $CATEGORY in
    claude)
        GREP_PATTERN="^claude/"
        ;;
    copilot)
        GREP_PATTERN="^copilot/"
        ;;
    dependabot)
        GREP_PATTERN="^dependabot/"
        ;;
    all)
        GREP_PATTERN="."
        ;;
    *)
        echo -e "${RED}Invalid category: ${CATEGORY}${NC}"
        exit 1
        ;;
esac

# Process branches
echo -e "${YELLOW}Stale branches found:${NC}"
echo ""

git for-each-ref --sort=committerdate --format='%(committerdate:short) %(refname:short)' refs/remotes/origin 2>/dev/null | \
while read line; do
    BRANCH_DATE=$(echo "$line" | cut -d' ' -f1)
    BRANCH_FULL=$(echo "$line" | cut -d' ' -f2)
    BRANCH_NAME=$(echo "$BRANCH_FULL" | sed 's|origin/||')

    # Skip main branch
    if [[ "$BRANCH_NAME" == "main" ]] || [[ "$BRANCH_NAME" == "HEAD" ]]; then
        continue
    fi

    # Check if protected
    IS_PROTECTED=false
    for protected in $PROTECTED_BRANCHES; do
        if [[ "$BRANCH_NAME" == "$protected" ]]; then
            IS_PROTECTED=true
            break
        fi
    done

    if [[ "$IS_PROTECTED" == "true" ]]; then
        continue
    fi

    # Check if stale
    if [[ "$BRANCH_DATE" < "$CUTOFF_DATE" ]]; then
        # Check category filter
        if echo "$BRANCH_NAME" | grep -qE "$GREP_PATTERN"; then
            STALE_COUNT=$((STALE_COUNT + 1))

            if [[ "$DRY_RUN" == "true" ]]; then
                echo -e "  ${RED}[STALE]${NC} ${BRANCH_DATE} | ${BRANCH_NAME}"
            else
                echo -e "  ${RED}[DELETING]${NC} ${BRANCH_DATE} | ${BRANCH_NAME}"
                if git push origin --delete "$BRANCH_NAME" 2>/dev/null; then
                    DELETED_COUNT=$((DELETED_COUNT + 1))
                    echo -e "    ${GREEN}Deleted successfully${NC}"
                else
                    echo -e "    ${RED}Failed to delete${NC}"
                fi
            fi
        fi
    fi
done

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Summary${NC}"
echo -e "${BLUE}============================================${NC}"

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "Stale branches found: ${YELLOW}${STALE_COUNT}${NC}"
    echo ""
    echo -e "${YELLOW}To delete these branches, run:${NC}"
    echo -e "  $0 --execute --days ${STALE_DAYS} --category ${CATEGORY}"
else
    echo -e "Branches deleted: ${GREEN}${DELETED_COUNT}${NC}"
fi

echo ""
