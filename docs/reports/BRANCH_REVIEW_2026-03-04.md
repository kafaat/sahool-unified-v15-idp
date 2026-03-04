# GitHub Branch Review Report

**Date**: 2026-03-04
**Repository**: kafaat/sahool-unified-v15-idp
**Total Remote Branches**: 400

---

## Summary

| Category | Count | Percentage |
|----------|-------|------------|
| `claude/` branches | 161 | 40.3% |
| `copilot/` branches | 223 | 55.8% |
| `dependabot/` branches | 5 | 1.3% |
| `fix/` branches | 3 | 0.8% |
| Other (main, gh-pages, etc.) | 8 | 2.0% |
| **Total** | **400** | **100%** |

### Activity Status

| Status | Count |
|--------|-------|
| Active (last 7 days) | ~15 |
| Recent (last 30 days) | ~148 |
| Stale (older than 30 days) | ~252 |
| Oldest branch date | 2025-12-14 |

---

## Recently Active Branches (Last 7 days)

| Branch | Last Updated | Last Commit |
|--------|-------------|-------------|
| `gh-pages` | 2026-03-04 | deploy: ac27f40 |
| `main` | 2026-03-04 | feat: AI + Smart Agriculture knowledge base |
| `claude/agriculture-ai-knowledge-base-3XrgZ` | 2026-03-04 | fix: Mobile CI APK build |
| `claude/review-and-fix-issues-LGatW` | 2026-03-04 | fix: update drift baseline |
| `claude/fix-docker-build-errors-jAq0J` | 2026-03-03 | fix: add tsconfig.base.json for nestjs-auth |
| `dependabot/npm_and_yarn/eslint/js-9.39.3` | 2026-03-03 | chore(deps): bump @eslint/js 9.39.3 |
| `dependabot/npm_and_yarn/pg-8.19.0` | 2026-03-03 | chore(deps): bump pg 8.19.0 |
| `dependabot/npm_and_yarn/autoprefixer-10.4.27` | 2026-03-03 | chore(deps): bump autoprefixer 10.4.27 |
| `dependabot/npm_and_yarn/typescript-eslint/eslint-plugin-8.56.1` | 2026-03-03 | chore(deps): bump @typescript-eslint/eslint-plugin 8.56.1 |
| `dependabot/npm_and_yarn/typescript-5aec3daba0` | 2026-03-03 | chore(deps): bump @types/node |
| `claude/setup-vllm-deepseek-u5Bps` | 2026-03-02 | merge: resolve drift baseline conflict |
| `claude/setup-trivy-scanning-al341` | 2026-03-02 | merge: resolve conflict in drift baseline |
| `claude/fix-admin-dashboard-performance-vMj0q` | 2026-03-02 | Merge branch 'main' |
| `claude/add-claude-documentation-48GdK` | 2026-03-02 | Fix topologySpreadConstraints |

---

## Duplicate & Redundant Branch Groups

These groups contain multiple branches for the same purpose, indicating failed attempts or retry patterns. **Recommended for cleanup.**

### 1. Merge Conflicts (15 branches)

All related to resolving merge conflicts - should be deleted after resolution:

- `copilot/fix-merge-conflicts` (+ again, and-issues, and-review, another-one)
- `copilot/resolve-merge-conflict` (+ conflicts, -390, -again, -another-one, -pr-394, -pr-882, -pr-882-again, -pr390)
- `claude/resolve-merge-conflicts-4hyVO`

### 2. Sub-PR Retries (14 branches)

Multiple retry attempts for the same PRs:

- `copilot/sub-pr-115` (6 variants: original, -again, -another-one, -one-more-time, -please-work, -yet-again)
- `copilot/sub-pr-1045` (3 variants: original, -again, -another-one)
- `copilot/sub-pr-107` (2 variants: original, -again)
- `copilot/sub-pr-227`, `copilot/sub-pr-71`, `copilot/sub-pr-105`

### 3. Action/Workflow Updates (25 branches)

Excessive retry branches for CI/CD fixes:

- `copilot/update-action-run-logs` (3 variants)
- `copilot/update-action-run-reference` (4 variants)
- `copilot/fix-github-actions-workflow` (+ failure variant)
- `copilot/fix-ci-workflow-*` (3 variants)
- And 12 more related branches

### 4. Build Fix Retries (7 branches)

- `copilot/fix-build-errors` (+ again, and-warnings, and-run-errors, docker-image-errors, issues, gradle)

### 5. Docker Fix Branches (7 branches)

- `claude/fix-docker-*` (6 branches)
- `copilot/fix-docker-builds-and-dependencies`

### 6. Review Branches (35 branches)

Many one-time review branches that served their purpose:

- 19 `claude/review-*` branches
- 16 `copilot/review-*` branches

---

## Dependabot Branches (5 - Pending Merge)

| Branch | Package | Update |
|--------|---------|--------|
| `dependabot/npm_and_yarn/eslint/js-9.39.3` | @eslint/js | → 9.39.3 |
| `dependabot/npm_and_yarn/pg-8.19.0` | pg | → 8.19.0 |
| `dependabot/npm_and_yarn/autoprefixer-10.4.27` | autoprefixer | → 10.4.27 |
| `dependabot/npm_and_yarn/typescript-5aec3daba0` | @types/node | TypeScript group |
| `dependabot/npm_and_yarn/typescript-eslint/eslint-plugin-8.56.1` | @typescript-eslint/eslint-plugin | → 8.56.1 |

**Action**: Review and merge these dependency updates.

---

## Oldest/Abandoned Branches (Pre-2026)

All branches from December 2025 that should be considered for deletion:

| Branch | Date | Purpose |
|--------|------|---------|
| `revert-2-claude/fix-sahool-kernel-script-*` | 2025-12-14 | Revert branch |
| `revert-3-revert-2-claude/fix-sahool-kernel-script-*` | 2025-12-14 | Double revert |
| `copilot/fix-flake8-lint-errors` | 2025-12-14 | Lint fixes |
| `claude/fix-sahool-kernel-script-*` | 2025-12-14 | Kernel script fix |
| `copilot/update-dockerfile-dependency-install` | 2025-12-14 | Dockerfile update |
| `copilot/update-dockerfile-dependency-installation` | 2025-12-14 | Duplicate |
| `copilot/update-dockerfile-npm-commands` | 2025-12-14 | Dockerfile update |
| `fix-integration-tests` | 2025-12-15 | Test fix |
| `copilot/fix-ci-workflow-file` | 2025-12-15 | CI fix |
| `copilot/fix-website-header-issue` | 2025-12-15 | Frontend fix |

---

## Recommendations

### 1. Immediate Cleanup (~200 branches)

Delete the following categories of stale branches:

- **Merged/completed `copilot/fix-*` branches** (~100 branches) - Most are one-time fixes
- **Retry branches** (sub-pr-*, -again, -another-one variants) (~30 branches)
- **Old `copilot/resolve-merge-conflicts-*`** (~15 branches)
- **Revert branches** (3 branches)
- **Old review branches** that have served their purpose (~30 branches)
- **Duplicate Dockerfile/workflow update branches** (~20 branches)

### 2. Merge Pending Work (~10 branches)

- **5 Dependabot PRs** - Review and merge dependency updates
- `claude/fix-docker-build-errors-jAq0J` - Active fix (Mar 3)
- `claude/setup-vllm-deepseek-u5Bps` - vLLM/DeepSeek setup
- `claude/setup-trivy-scanning-al341` - Security scanning setup
- `claude/fix-admin-dashboard-performance-vMj0q` - Dashboard performance

### 3. Branch Naming Convention Enforcement

- Enforce consistent naming: `{type}/{description}` (e.g., `fix/docker-build`, `feat/trivy-scanning`)
- Avoid retry suffixes (-again, -another-one, -yet-again, -please-work)
- Limit branch lifetime to 30 days with automated stale branch warnings

### 4. Process Improvements

- Enable automatic branch deletion on PR merge
- Set up stale branch detection in CI (warn after 14 days, auto-close after 30)
- Limit concurrent branches per contributor
- The `copilot/` prefix has 223 branches (55.8%) - many are redundant retry attempts, suggesting the Copilot agent needs better error handling before creating new branches

---

## Branch Count by Prefix

```
claude/    161 branches (40.3%)
copilot/   223 branches (55.8%)
dependabot/  5 branches  (1.3%)
fix/         3 branches  (0.8%)
other        8 branches  (2.0%)
```

### Priority Actions

1. **HIGH**: Delete ~200 stale/duplicate branches to reduce clutter
2. **HIGH**: Merge 5 Dependabot dependency updates
3. **MEDIUM**: Merge active feature branches (vLLM, Trivy, dashboard perf)
4. **LOW**: Implement branch lifecycle policies
