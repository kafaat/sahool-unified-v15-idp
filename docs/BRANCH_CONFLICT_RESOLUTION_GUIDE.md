# دليل حل التعارضات في الفروع المفتوحة
# Branch Conflict Resolution Guide

## نظرة عامة | Overview

This guide provides step-by-step instructions for resolving merge conflicts in open pull requests for the SAHOOL platform.

### الفروع المتأثرة | Affected Branches

Based on the current repository status, the following PRs have merge conflicts:

1. **PR #810**: Standardize Python version to 3.12 across all environments
   - Branch: `copilot/fix-ci-workflow-issues`
   - Base: `main`
   - Status: `mergeable: false`, `mergeable_state: "dirty"`
   - Files changed: 83 files
   - Changes: +108 insertions, -108 deletions

2. **PR #809**: Add comprehensive final project review with bilingual documentation
   - Branch: `copilot/final-project-review`
   - Base: `main`
   - Status: `mergeable: false`, `mergeable_state: "dirty"`
   - Files changed: 25 files
   - Changes: +2810 insertions, -60 deletions

3. **PR #813**: Resolve merge conflicts in pull request (already clean)
   - Branch: `copilot/resolve-merge-conflicts-again`
   - Base: `copilot/fix-ci-workflow-issues`
   - Status: `mergeable: true`, `mergeable_state: "clean"` ✅

---

## السبب الجذري | Root Cause

The conflicts occur because:
1. The base branch `main` has received new commits (PR #811 was merged)
2. The feature branches were created from an earlier state of `main`
3. Changes in `main` overlap with changes in the feature branches

---

## حل التعارضات | Conflict Resolution

### الطريقة 1: إعادة التأسيس (Rebase) - الموصى بها | Method 1: Rebase (Recommended)

This method creates a clean, linear history by replaying the feature branch commits on top of the latest `main`.

#### PR #810: Python 3.12 Standardization

```bash
# Step 1: Checkout the branch
git checkout copilot/fix-ci-workflow-issues
git fetch origin main

# Step 2: Rebase on main
git rebase origin/main

# Step 3: Resolve conflicts if any
# For each conflicting file:
# - Edit the file to resolve conflicts
# - Mark as resolved: git add <file>
# - Continue: git rebase --continue

# Step 4: Force push (required after rebase)
git push origin copilot/fix-ci-workflow-issues --force-with-lease
```

**Expected Conflicts**:
- Configuration files (pyproject.toml, GitHub workflows, Dockerfiles)
- Likely due to Python version changes vs. other dependency updates in main

**Resolution Strategy**:
- Keep Python 3.12 changes from PR #810
- Integrate any new services or workflows from main
- Ensure all Python version references are 3.12 (not 3.11)

#### PR #809: Final Project Review

```bash
# Step 1: Checkout the branch
git checkout copilot/final-project-review
git fetch origin main

# Step 2: Rebase on main
git rebase origin/main

# Step 3: Resolve conflicts if any
# Documentation files may conflict if new docs were added to main

# Step 4: Force push
git push origin copilot/final-project-review --force-with-lease
```

**Expected Conflicts**:
- Documentation files in `docs/` directory
- Audit report index files

**Resolution Strategy**:
- Keep new documentation from PR #809
- Merge any new documentation added to main
- Update references to include latest changes

---

### الطريقة 2: الدمج (Merge) - بديلة | Method 2: Merge (Alternative)

This method preserves the full history by creating a merge commit.

#### PR #810

```bash
# Step 1: Checkout the branch
git checkout copilot/fix-ci-workflow-issues
git fetch origin main

# Step 2: Merge main into feature branch
git merge origin/main

# Step 3: Resolve conflicts
# Edit conflicting files
# git add <resolved-files>
# git commit -m "Merge main into copilot/fix-ci-workflow-issues"

# Step 4: Push
git push origin copilot/fix-ci-workflow-issues
```

#### PR #809

```bash
# Step 1: Checkout the branch
git checkout copilot/final-project-review
git fetch origin main

# Step 2: Merge main into feature branch
git merge origin/main

# Step 3: Resolve conflicts and commit
# git add <resolved-files>
# git commit -m "Merge main into copilot/final-project-review"

# Step 4: Push
git push origin copilot/final-project-review
```

---

## أدوات المساعدة | Helper Tools

### Automated Conflict Detection Script

```bash
#!/bin/bash
# check-conflicts.sh

BRANCHES=("copilot/fix-ci-workflow-issues" "copilot/final-project-review")

for branch in "${BRANCHES[@]}"; do
    echo "Checking $branch..."
    git fetch origin $branch
    git fetch origin main
    
    # Try merge simulation
    git checkout main
    git merge --no-commit --no-ff origin/$branch 2>&1 | grep -i "conflict" || echo "No conflicts"
    git merge --abort 2>/dev/null
    echo "---"
done
```

### Conflict File Identifier

```bash
#!/bin/bash
# find-conflict-markers.sh

echo "Searching for conflict markers in repository..."
grep -r "<<<<<<< HEAD" --include="*.py" --include="*.js" --include="*.ts" \
    --include="*.yaml" --include="*.yml" --include="*.json" --include="*.md" \
    --include="Dockerfile" . 2>/dev/null
```

---

## قائمة التحقق | Verification Checklist

After resolving conflicts, verify:

### PR #810 (Python 3.12)
- [ ] All Dockerfiles use `python:3.12-slim-bookworm`
- [ ] pyproject.toml has `requires-python = ">=3.12"`
- [ ] GitHub workflows use `python-version: '3.12'`
- [ ] Ruff target is `py312`
- [ ] Mypy python_version is `"3.12"`
- [ ] No Python 3.11 references remain
- [ ] Smoke tests pass
- [ ] Linting passes (`make lint`)

### PR #809 (Documentation)
- [ ] All new documentation files are present
- [ ] No markdown syntax errors
- [ ] Cross-references are valid
- [ ] Audit reports index is updated
- [ ] Arabic and English content is synchronized

---

## الخطوات التالية | Next Steps

1. **Prioritize PR #810** (Python 3.12 standardization)
   - This is a critical infrastructure change
   - Should be merged before other PRs

2. **Then resolve PR #809** (Documentation)
   - Can be rebased after #810 is merged
   - Minimal code conflicts expected

3. **PR #813 is already clean**
   - No action needed
   - Can be merged once its base branch (#810) is resolved

---

## الأوامر السريعة | Quick Commands

### Check current conflict status
```bash
# For PR #810
git checkout copilot/fix-ci-workflow-issues
git fetch origin main
git merge-base origin/main HEAD
git log --oneline origin/main..HEAD

# For PR #809
git checkout copilot/final-project-review
git fetch origin main
git log --oneline origin/main..HEAD
```

### View file differences
```bash
# Compare branch with main
git diff origin/main...copilot/fix-ci-workflow-issues
git diff origin/main...copilot/final-project-review
```

---

## اتصل بنا للمساعدة | Contact for Help

If you encounter issues during conflict resolution:

1. **Document the conflict**: Note which files and what type of conflict
2. **Check this guide**: Ensure you followed the recommended steps
3. **Use Git tools**: `git status`, `git diff`, `git log --merge`
4. **Ask for review**: Request help from team members familiar with the changes

---

## المراجع | References

- [Git Rebase Documentation](https://git-scm.com/docs/git-rebase)
- [Git Merge Documentation](https://git-scm.com/docs/git-merge)
- [GitHub Conflict Resolution](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line)
- SAHOOL Contribution Guidelines: `docs/CONTRIBUTING.md`

---

**Last Updated**: 2026-02-04
**Version**: 1.0.0
