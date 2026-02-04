#!/bin/bash
# resolve-pr-conflicts.sh
# Helper script to resolve conflicts in open pull requests
# Usage: ./scripts/resolve-pr-conflicts.sh [pr-number|branch-name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if we're in the repository root
check_repo_root() {
    if [ ! -d ".git" ]; then
        error "Must be run from repository root"
        exit 1
    fi
}

# Function to fetch latest from origin
fetch_latest() {
    info "Fetching latest from origin..."
    git fetch --all
    success "Fetch complete"
}

# Function to check for uncommitted changes
check_clean_working_tree() {
    if ! git diff-index --quiet HEAD --; then
        error "Working tree has uncommitted changes. Please commit or stash them first."
        exit 1
    fi
}

# Function to resolve PR #810 (Python 3.12)
resolve_pr_810() {
    local branch="copilot/fix-ci-workflow-issues"
    
    info "Resolving PR #810: Python 3.12 Standardization"
    echo "Branch: $branch"
    echo ""
    
    # Checkout the branch
    info "Checking out branch: $branch"
    git checkout "$branch"
    
    # Rebase on main
    info "Rebasing on main..."
    if git rebase origin/main; then
        success "Rebase successful - no conflicts!"
        
        warning "Review the changes before force pushing:"
        git log --oneline origin/$branch..HEAD
        echo ""
        
        read -p "Force push to origin? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin "$branch" --force-with-lease
            success "Branch pushed successfully"
        else
            warning "Skipped push. You can push later with:"
            echo "  git push origin $branch --force-with-lease"
        fi
    else
        warning "Conflicts detected during rebase"
        echo ""
        echo "Conflicting files:"
        git status | grep "both modified" || echo "  Check 'git status' for details"
        echo ""
        echo "To resolve:"
        echo "  1. Edit the conflicting files"
        echo "  2. For Python version conflicts, choose Python 3.12"
        echo "  3. Mark resolved: git add <file>"
        echo "  4. Continue: git rebase --continue"
        echo "  5. Push: git push origin $branch --force-with-lease"
        echo ""
        echo "To abort: git rebase --abort"
        exit 1
    fi
}

# Function to resolve PR #809 (Documentation)
resolve_pr_809() {
    local branch="copilot/final-project-review"
    
    info "Resolving PR #809: Final Project Review Documentation"
    echo "Branch: $branch"
    echo ""
    
    # Checkout the branch
    info "Checking out branch: $branch"
    git checkout "$branch"
    
    # Rebase on main
    info "Rebasing on main..."
    if git rebase origin/main; then
        success "Rebase successful - no conflicts!"
        
        warning "Review the changes before force pushing:"
        git log --oneline origin/$branch..HEAD
        echo ""
        
        read -p "Force push to origin? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin "$branch" --force-with-lease
            success "Branch pushed successfully"
        else
            warning "Skipped push. You can push later with:"
            echo "  git push origin $branch --force-with-lease"
        fi
    else
        warning "Conflicts detected during rebase"
        echo ""
        echo "Conflicting files:"
        git status | grep "both modified" || echo "  Check 'git status' for details"
        echo ""
        echo "To resolve:"
        echo "  1. Edit the conflicting files (likely documentation)"
        echo "  2. Keep new documentation from this branch"
        echo "  3. Merge any new docs from main"
        echo "  4. Mark resolved: git add <file>"
        echo "  5. Continue: git rebase --continue"
        echo "  6. Push: git push origin $branch --force-with-lease"
        echo ""
        echo "To abort: git rebase --abort"
        exit 1
    fi
}

# Function to check conflict status for all PRs
check_all_conflicts() {
    info "Checking conflict status for all open PRs..."
    echo ""
    
    local branches=("copilot/fix-ci-workflow-issues" "copilot/final-project-review")
    
    for branch in "${branches[@]}"; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        info "Checking: $branch"
        
        # Create a temporary branch for testing
        git checkout main -q
        git checkout -b temp-merge-test-$$ -q
        
        # Try to merge
        if git merge --no-commit --no-ff origin/$branch &>/dev/null; then
            success "No conflicts with main"
            git merge --abort 2>/dev/null
        else
            warning "Has conflicts with main"
            echo ""
            echo "Conflicting files:"
            git status -s | grep "^UU" | awk '{print "  - " $2}' || echo "  (check git status)"
            git merge --abort 2>/dev/null
        fi
        
        # Cleanup
        git checkout main -q
        git branch -D temp-merge-test-$$ -q
        echo ""
    done
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [command]

Commands:
  810, pr-810      Resolve PR #810 (Python 3.12 standardization)
  809, pr-809      Resolve PR #809 (Final project review docs)
  check, status    Check conflict status for all PRs
  help             Show this help message

Examples:
  $0 810           # Resolve PR #810
  $0 check         # Check all PRs for conflicts
  $0 help          # Show help

EOF
}

# Main script
main() {
    check_repo_root
    
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    case "$1" in
        810|pr-810)
            check_clean_working_tree
            fetch_latest
            resolve_pr_810
            ;;
        809|pr-809)
            check_clean_working_tree
            fetch_latest
            resolve_pr_809
            ;;
        check|status)
            fetch_latest
            check_all_conflicts
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
