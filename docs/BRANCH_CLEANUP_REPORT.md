# Branch Cleanup Report | تقرير تنظيف الفروع

**Generated**: 2026-01-29
**Repository**: kafaat/sahool-unified-v15-idp
**Total Unmerged Branches**: 262

---

## Executive Summary | الملخص التنفيذي

| Category | Count | Status | Action Required |
|----------|-------|--------|-----------------|
| **Dependabot** | 14 | Active | Review & Merge |
| **Claude (Recent)** | 76 | Mixed | Review |
| **Claude (Stale)** | 37 | Stale | Delete |
| **Copilot (Recent)** | 78 | Mixed | Review |
| **Copilot (Stale)** | 48 | Stale | Delete |
| **Other** | 9 | Mixed | Review |

**Recommendation**: Delete 91 stale branches (older than 30 days)

---

## 1. Dependabot Branches (Priority: HIGH)

These branches contain important security and dependency updates. Review and merge as appropriate.

### Python Dependencies
| Branch | Package | Version |
|--------|---------|---------|
| `dependabot/pip/apps/services/alembic-1.18.2` | Alembic | 1.18.2 |
| `dependabot/pip/apps/services/celery-5.6.2` | Celery | 5.6.2 |
| `dependabot/pip/apps/services/pydantic-settings-2.12.0` | Pydantic Settings | 2.12.0 |
| `dependabot/pip/apps/services/redis-hiredis--7.1.0` | Redis/Hiredis | 7.1.0 |
| `dependabot/pip/apps/services/services-deps-645679f8b1` | Multiple deps | - |
| `dependabot/pip/python-minor-4983c66365` | Python minor | - |
| `dependabot/pip/scipy-gte-1.11.0-and-lt-1.18.0` | SciPy | 1.11-1.18 |

### JavaScript/Node.js Dependencies
| Branch | Package | Notes |
|--------|---------|-------|
| `dependabot/npm_and_yarn/next-ecosystem-640d0739f8` | Next.js ecosystem | Framework update |
| `dependabot/npm_and_yarn/react-ecosystem-540e38fa3a` | React ecosystem | UI library |
| `dependabot/npm_and_yarn/tanstack/react-query-5.90.20` | React Query | 5.90.20 |
| `dependabot/npm_and_yarn/testing-660ccf895f` | Testing libs | Vitest/Jest |
| `dependabot/npm_and_yarn/typescript-f6074de692` | TypeScript | Type system |

### Infrastructure
| Branch | Update |
|--------|--------|
| `dependabot/docker/apps/services/vegetation-analysis-service/python-3.14-slim-bookworm` | Python 3.14 Docker image |
| `dependabot/github_actions/actions-feabcb4e6f` | GitHub Actions |

---

## 2. Stale Branches to Delete (91 branches)

### Claude Stale Branches (37)
Branches older than 30 days that should be deleted:

```
claude/fix-apk-simple-gOHKo
claude/fix-apk-workflow-gOHKo
claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL
claude/frontend-improvements-1QAAM
claude/mobile-fix-JfDP3
claude/review-branches-gOHKo
claude/review-project-JfDP3
claude/security-enhancements-1QAAM
claude/v16-features-JfDP3
... (and 28 more)
```

### Copilot Stale Branches (48)
```
copilot/consolidate-improvements-pr
copilot/consolidate-subprojects-blocks
copilot/comprehensive-review-project
copilot/fix-build-gradle-kts-alignment
copilot/fix-ci-pipeline-errors
copilot/fix-ci-workflow-file
copilot/fix-flake8-lint-errors
copilot/fix-flutter-apk-build-errors
copilot/fix-flutter-apk-build-issues
copilot/fix-flutter-build-dexing-issue
copilot/fix-iot-rules-tests
copilot/fix-issue-in-action-step
copilot/fix-issue-with-user-authentication
copilot/fix-it-issue
copilot/fix-six-failed-tests
copilot/fix-website-header-issue
copilot/refactor-after-evaluate-setup
copilot/resolve-merge-conflict
copilot/review-full-stack-blueprint
copilot/review-project-comprehensively
copilot/review-project-jfdp3
copilot/sub-pr-105
copilot/sub-pr-107
copilot/sub-pr-107-again
copilot/sub-pr-115
copilot/sub-pr-115-again
copilot/sub-pr-115-another-one
copilot/sub-pr-115-one-more-time
copilot/sub-pr-115-please-work
copilot/sub-pr-115-yet-again
copilot/sub-pr-71
copilot/update-backend-system
copilot/update-build-deployment-config
copilot/update-dockerfile-dependency-install
copilot/update-dockerfile-dependency-installation
copilot/update-dockerfile-npm-commands
... (and 12 more)
```

### Other Stale Branches (6)
```
fix-integration-tests
fix-websocket-hook-error
revert-179-claude/recover-deleted-kernel-xw3xR
revert-2-claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL
revert-3-revert-2-claude/fix-sahool-kernel-script-01XqF6bcNNVtFpmgJR2gmNXL
تحديث-sahool
```

---

## 3. Active Branches to Review

### Recent Claude Branches (Last 7 days)
| Date | Branch | Purpose |
|------|--------|---------|
| 01-29 | `claude/implement-todo-item-346bI` | Task implementation |
| 01-26 | `claude/analyze-microservices-architecture-qLtJo` | Architecture analysis |
| 01-25 | `claude/fix-postgres-window-function-WgO5P` | PostgreSQL fix |
| 01-25 | `claude/analyze-kong-services-E8TJ8` | Kong analysis |
| 01-24 | `claude/fix-frontend-tests-workflow-Zkfad` | Test fixes |

### Recent Copilot Branches (Last 7 days)
| Date | Branch | Purpose |
|------|--------|---------|
| 01-28 | `copilot/add-kimi-repair-agent-integration` | Agent integration |
| 01-28 | `copilot/resolve-merge-conflicts` | Conflict resolution |
| 01-28 | `copilot/comprehensive-project-review` | Project review |
| 01-28 | `copilot/integrate-kimi-repair-agent` | Agent integration |
| 01-26 | `copilot/add-user-registration-feature` | User feature |

---

## 4. Recommended Actions

### Immediate (This Week)
1. **Review Dependabot PRs** - Merge security updates
2. **Delete stale sub-pr-* branches** - These are temporary
3. **Delete revert-* branches** - Already processed

### Short Term (This Month)
1. **Clean up 91 stale branches** - Use cleanup script
2. **Review recent Claude/Copilot branches** for useful changes
3. **Establish branch cleanup policy** - Auto-delete after 30 days

### Long Term
1. **Enable branch protection rules**
2. **Set up automatic stale branch notifications**
3. **Create PR templates requiring branch cleanup**

---

## 5. Cleanup Commands

### Delete Single Branch
```bash
git push origin --delete <branch-name>
```

### Delete All Stale Branches (use with caution)
```bash
# See scripts/cleanup-stale-branches.sh
./scripts/cleanup-stale-branches.sh --dry-run  # Preview
./scripts/cleanup-stale-branches.sh            # Execute
```

---

## Statistics Summary

| Metric | Value |
|--------|-------|
| Total branches | 263 (including main) |
| Unmerged branches | 262 |
| Stale branches (>30 days) | 91 (35%) |
| Claude branches | 113 |
| Copilot branches | 126 |
| Dependabot branches | 14 |
| Other branches | 9 |

---

*Report generated by Claude Code*
*https://claude.ai/code*
