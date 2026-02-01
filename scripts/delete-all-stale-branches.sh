#!/bin/bash
# ============================================================================
# Delete All Stale and Obsolete Branches
# Generated: 2026-01-29
# ============================================================================
# This script deletes all stale branches (>30 days) and obsolete Dependabot
# branches that have been superseded by newer updates.
#
# Usage:
#   ./delete-all-stale-branches.sh          # Preview mode (dry run)
#   ./delete-all-stale-branches.sh --execute # Actually delete branches
# ============================================================================

set -e

DRY_RUN=true
if [[ "$1" == "--execute" ]]; then
    DRY_RUN=false
    echo "⚠️  EXECUTE MODE - Branches will be deleted!"
else
    echo "📋 DRY RUN MODE - No branches will be deleted"
    echo "   Run with --execute to actually delete branches"
fi

echo ""
echo "============================================"
echo "  Branch Deletion Script"
echo "============================================"
echo ""

DELETED=0
FAILED=0

delete_branch() {
    local branch=$1
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  [DRY RUN] Would delete: $branch"
    else
        echo -n "  Deleting: $branch ... "
        if git push origin --delete "$branch" 2>/dev/null; then
            echo "✅"
            ((DELETED++))
        else
            echo "❌ (may already be deleted)"
            ((FAILED++))
        fi
    fi
}

echo "=== PRIORITY 1: Temporary sub-pr branches (11) ==="
delete_branch "copilot/sub-pr-105"
delete_branch "copilot/sub-pr-107"
delete_branch "copilot/sub-pr-107-again"
delete_branch "copilot/sub-pr-115"
delete_branch "copilot/sub-pr-115-again"
delete_branch "copilot/sub-pr-115-another-one"
delete_branch "copilot/sub-pr-115-one-more-time"
delete_branch "copilot/sub-pr-115-please-work"
delete_branch "copilot/sub-pr-115-yet-again"
delete_branch "copilot/sub-pr-227"
delete_branch "copilot/sub-pr-71"

echo ""
echo "=== PRIORITY 2: Revert branches (3) ==="
delete_branch "revert-179-claude/recover-deleted-kernel-xw3xR"
delete_branch "revert-2-claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL"
delete_branch "revert-3-revert-2-claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL"

echo ""
echo "=== PRIORITY 3: Obsolete Dependabot branches (14) ==="
delete_branch "dependabot/docker/apps/services/vegetation-analysis-service/python-3.14-slim-bookworm"
delete_branch "dependabot/github_actions/actions-feabcb4e6f"
delete_branch "dependabot/npm_and_yarn/next-ecosystem-640d0739f8"
delete_branch "dependabot/npm_and_yarn/react-ecosystem-540e38fa3a"
delete_branch "dependabot/npm_and_yarn/tanstack/react-query-5.90.20"
delete_branch "dependabot/npm_and_yarn/testing-660ccf895f"
delete_branch "dependabot/npm_and_yarn/typescript-f6074de692"
delete_branch "dependabot/pip/apps/services/alembic-1.18.2"
delete_branch "dependabot/pip/apps/services/celery-5.6.2"
delete_branch "dependabot/pip/apps/services/pydantic-settings-2.12.0"
delete_branch "dependabot/pip/apps/services/redis-hiredis--7.1.0"
delete_branch "dependabot/pip/apps/services/services-deps-645679f8b1"
delete_branch "dependabot/pip/python-minor-4983c66365"
delete_branch "dependabot/pip/scipy-gte-1.11.0-and-lt-1.18.0"

echo ""
echo "=== PRIORITY 4: Stale Copilot branches ==="
delete_branch "copilot/add-package-lock-json-file"
delete_branch "copilot/analyze-build-errors"
delete_branch "copilot/comprehensive-review-project"
delete_branch "copilot/consolidate-improvements-pr"
delete_branch "copilot/consolidate-subprojects-blocks"
delete_branch "copilot/fix-build-gradle-kts-alignment"
delete_branch "copilot/fix-ci-pipeline-errors"
delete_branch "copilot/fix-ci-workflow-file"
delete_branch "copilot/fix-field-card-property-names"
delete_branch "copilot/fix-flake8-lint-errors"
delete_branch "copilot/fix-flutter-apk-build-errors"
delete_branch "copilot/fix-flutter-apk-build-issues"
delete_branch "copilot/fix-flutter-build-dexing-issue"
delete_branch "copilot/fix-iot-rules-tests"
delete_branch "copilot/fix-issue-in-action-step"
delete_branch "copilot/fix-issue-with-user-authentication"
delete_branch "copilot/fix-issues-and-make-needed-changes"
delete_branch "copilot/fix-it-issue"
delete_branch "copilot/fix-missing-api-client-module"
delete_branch "copilot/fix-missing-package-lock-file"
delete_branch "copilot/fix-pending-issues"
delete_branch "copilot/fix-six-failed-tests"
delete_branch "copilot/fix-sys-path-integration-test"
delete_branch "copilot/fix-test-failures"
delete_branch "copilot/fix-website-header-issue"
delete_branch "copilot/refactor-after-evaluate-setup"
delete_branch "copilot/resolve-merge-conflict"
delete_branch "copilot/review-ai-llm-errors"
delete_branch "copilot/review-connection-ports"
delete_branch "copilot/review-full-stack-blueprint"
delete_branch "copilot/review-project-comprehensively"
delete_branch "copilot/review-project-jfdp3"
delete_branch "copilot/sub-pr-105"
delete_branch "copilot/sub-pr-107"
delete_branch "copilot/sub-pr-107-again"
delete_branch "copilot/sub-pr-115"
delete_branch "copilot/sub-pr-115-again"
delete_branch "copilot/sub-pr-115-another-one"
delete_branch "copilot/sub-pr-115-one-more-time"
delete_branch "copilot/sub-pr-115-please-work"
delete_branch "copilot/sub-pr-115-yet-again"
delete_branch "copilot/sub-pr-227"
delete_branch "copilot/sub-pr-71"
delete_branch "copilot/update-backend-system"
delete_branch "copilot/update-build-deployment-config"
delete_branch "copilot/update-dockerfile-dependency-install"
delete_branch "copilot/update-dockerfile-dependency-installation"
delete_branch "copilot/update-dockerfile-npm-commands"

echo ""
echo "=== PRIORITY 5: Stale Claude branches ==="
delete_branch "claude/add-idp-integration-zu3aA"
delete_branch "claude/analyze-library-conflicts-woInl"
delete_branch "claude/api-gateway-merge-zu3aA"
delete_branch "claude/api-gateway-security-zcpSG"
delete_branch "claude/codeql-permissions-fix-zcpSG"
delete_branch "claude/comprehensive-improvements-v2-UU3x3"
delete_branch "claude/docker-compose-build-test-KW14j"
delete_branch "claude/docker-fixes-KEIJS"
delete_branch "claude/docker-merge-zu3aA"
delete_branch "claude/fix-apk-simple-gOHKo"
delete_branch "claude/fix-apk-workflow-gOHKo"
delete_branch "claude/fix-docker-package-lock-UU3x3"
delete_branch "claude/fix-package-lock-UU3x3"
delete_branch "claude/fix-pr169-9T3E9"
delete_branch "claude/fix-react-types-UU3x3"
delete_branch "claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL"
delete_branch "claude/frontend-improvements-1QAAM"
delete_branch "claude/implement-todo-item-1QAAM"
delete_branch "claude/merge-all-fixes-KEIJS"
delete_branch "claude/merge-dashboard-fixes-zu3aA"
delete_branch "claude/merge-versions-zu3aA"
delete_branch "claude/mobile-app-improvement-zcpSG"
delete_branch "claude/mobile-fix-JfDP3"
delete_branch "claude/mobile-merge-zu3aA"
delete_branch "claude/mobile-permission-system-zcpSG"
delete_branch "claude/recover-deleted-kernel-xw3xR"
delete_branch "claude/review-branches-gOHKo"
delete_branch "claude/review-dashboard-multiple-KEIJS"
delete_branch "claude/review-kernel-services-9T3E9"
delete_branch "claude/review-project-JfDP3"
delete_branch "claude/security-enhancements-1QAAM"
delete_branch "claude/security-hotfix-zcpSG"
delete_branch "claude/typescript-fixes-UU3x3"
delete_branch "claude/unified-package-upgrade-zcpSG"
delete_branch "claude/unified-upgrade-zcpSG"
delete_branch "claude/unify-versions-zu3aA"
delete_branch "claude/v16-features-JfDP3"
delete_branch "revert-179-claude/recover-deleted-kernel-xw3xR"
delete_branch "revert-2-claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL"
delete_branch "revert-3-revert-2-claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL"

echo ""
echo "=== PRIORITY 6: Other stale branches ==="
delete_branch "fix-integration-tests"
delete_branch "fix-websocket-hook-error"
delete_branch "fix/prisma-docker-build"
delete_branch "تحديث-sahool"
delete_branch "alert-autofix-7394"

echo ""
echo "============================================"
echo "  Summary"
echo "============================================"
if [[ "$DRY_RUN" == "true" ]]; then
    echo "Dry run complete. Run with --execute to delete branches."
else
    echo "Deleted: $DELETED branches"
    echo "Failed: $FAILED branches"
fi
