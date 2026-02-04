# حل التعارضات - دليل سريع
# Conflict Resolution - Quick Guide

## نظرة سريعة | Quick Overview

هذا المستند يوفر تعليمات سريعة لحل التعارضات في الفروع المفتوحة.
This document provides quick instructions for resolving conflicts in open branches.

---

## الفروع المتأثرة | Affected Branches

### PR #810: Python 3.12 Standardization
- **الحالة | Status**: ❌ Has conflicts with main
- **الملفات | Files**: 83 files (workflows, Dockerfiles, config)
- **الأولوية | Priority**: 🔴 High (Infrastructure)

### PR #809: Final Project Review  
- **الحالة | Status**: ❌ Has conflicts with main
- **الملفات | Files**: 25 files (documentation)
- **الأولوية | Priority**: 🟡 Medium (Documentation)

### PR #813: Resolve merge conflicts
- **الحالة | Status**: ✅ Clean (no conflicts)
- **الأولوية | Priority**: Depends on PR #810

---

## الحل السريع | Quick Resolution

### الخيار 1: استخدام السكريبت المساعد | Option 1: Use Helper Script

```bash
# Check conflict status
./scripts/resolve-pr-conflicts.sh check

# Resolve PR #810
./scripts/resolve-pr-conflicts.sh 810

# Resolve PR #809
./scripts/resolve-pr-conflicts.sh 809
```

### الخيار 2: يدوياً | Option 2: Manual Resolution

#### PR #810 (Python 3.12)

```bash
git checkout copilot/fix-ci-workflow-issues
git fetch origin main
git rebase origin/main

# If conflicts:
# 1. Edit files to keep Python 3.12 versions
# 2. git add <resolved-files>
# 3. git rebase --continue
# 4. git push origin copilot/fix-ci-workflow-issues --force-with-lease
```

#### PR #809 (Documentation)

```bash
git checkout copilot/final-project-review
git fetch origin main
git rebase origin/main

# If conflicts:
# 1. Edit files to keep new documentation
# 2. git add <resolved-files>
# 3. git rebase --continue
# 4. git push origin copilot/final-project-review --force-with-lease
```

---

## نقاط التعارض المتوقعة | Expected Conflict Points

### PR #810
- `pyproject.toml` - Python version requirements
- `.github/workflows/*.yml` - Python version in CI
- `apps/services/*/Dockerfile` - Python base images
- Documentation files referencing Python version

**الحل | Resolution**: Always choose Python 3.12 over 3.11

### PR #809
- `docs/AUDIT_REPORTS_INDEX.md` - Audit report index
- New documentation files vs. updates in main
- Cross-references in documentation

**الحل | Resolution**: Keep new docs, merge any updates from main

---

## قائمة التحقق بعد الحل | Post-Resolution Checklist

### ✅ For PR #810
- [ ] All Python references are 3.12 (not 3.11)
- [ ] CI workflows pass
- [ ] Linting passes (`ruff check .`)
- [ ] Docker builds succeed

### ✅ For PR #809
- [ ] All new documentation files present
- [ ] No broken links
- [ ] Markdown syntax correct
- [ ] Arabic/English synchronized

---

## المساعدة | Help

للحصول على دليل تفصيلي، راجع:
For detailed guide, see:

📖 **[BRANCH_CONFLICT_RESOLUTION_GUIDE.md](./BRANCH_CONFLICT_RESOLUTION_GUIDE.md)**

---

## الترتيب الموصى به | Recommended Order

1. **أولاً | First**: Resolve PR #810 (Infrastructure)
2. **ثانياً | Second**: Resolve PR #809 (Documentation)  
3. **أخيراً | Finally**: PR #813 will be clean after #810

---

**آخر تحديث | Last Updated**: 2026-02-04
