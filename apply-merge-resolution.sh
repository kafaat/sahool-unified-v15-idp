#!/bin/bash
# Script to apply the merge conflict resolution for PR #699
# Usage: ./apply-merge-resolution.sh

set -e

echo "==================================="
echo "PR #699 Merge Conflict Resolution"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PR_BRANCH="claude/implement-todo-item-346bI"
BASE_BRANCH="main"

echo -e "${YELLOW}This script will resolve the merge conflict in PR #699${NC}"
echo -e "PR Branch: ${GREEN}${PR_BRANCH}${NC}"
echo -e "Base Branch: ${GREEN}${BASE_BRANCH}${NC}"
echo ""

# Check git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Fetch latest changes
echo "Fetching latest changes..."
git fetch origin

# Checkout PR branch
echo "Checking out ${PR_BRANCH}..."
if ! git checkout "${PR_BRANCH}"; then
    echo -e "${RED}Error: Could not checkout ${PR_BRANCH}${NC}"
    exit 1
fi

# Show what will happen
echo ""
echo "The following merge will be performed:"
echo "  git merge -X theirs main --allow-unrelated-histories"
echo ""
echo "This will:"
echo "  - Accept all changes from main for conflicts"
echo "  - Allow merging unrelated histories"
echo "  - Resolve all 519 conflicts automatically"
echo ""

# Confirm
read -p "Continue? (yes/no): " -r
echo ""
if [[ ! $REPLY =~ ^[Yy](es)?$ ]]; then
    echo "Aborted"
    exit 0
fi

# Perform merge
echo "Merging ${BASE_BRANCH} into ${PR_BRANCH}..."
if git merge -X theirs main --allow-unrelated-histories \
    -m "Merge main resolving conflicts"; then
    echo -e "${GREEN}✓${NC} Merge completed successfully!"
else
    echo -e "${RED}✗${NC} Merge failed"
    echo "You may need to resolve conflicts manually"
    exit 1
fi

# Push
echo ""
echo "Pushing to origin/${PR_BRANCH}..."
if git push origin "${PR_BRANCH}"; then
    echo -e "${GREEN}✓${NC} Successfully pushed!"
    echo ""
    echo "PR #699 is now ready to merge"
    echo "View at: https://github.com/kafaat/sahool-unified-v15-idp/pull/699"
else
    echo -e "${YELLOW}⚠${NC} Push failed"
    echo "If the branch is protected, you may need to:"
    echo "  1. Temporarily disable branch protection"
    echo "  2. Push the changes"
    echo "  3. Re-enable protection"
    echo ""
    echo "Or, merge the PR directly on GitHub once conflicts are resolved"
    exit 1
fi

echo ""
echo -e "${GREEN}Done!${NC}"
