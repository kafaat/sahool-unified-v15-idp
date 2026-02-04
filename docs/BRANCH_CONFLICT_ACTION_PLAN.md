# حل التعارضات في الفروع المفتوحة - خطة العمل
# Branch Conflicts Resolution - Action Plan

## الملخص التنفيذي | Executive Summary

تم تحديد تعارضات في فرعين من الفروع المفتوحة نتيجة تحديثات في الفرع الرئيسي (main).
Two open branches have been identified with conflicts due to updates in the main branch.

---

## الحالة الحالية | Current Status

### ✅ الفروع النظيفة | Clean Branches
- **PR #813**: `copilot/resolve-merge-conflicts-again` - No conflicts

### ❌ الفروع المتعارضة | Conflicting Branches  
- **PR #810**: `copilot/fix-ci-workflow-issues` - Has conflicts
- **PR #809**: `copilot/final-project-review` - Has conflicts

---

## خطة الحل | Resolution Plan

### المرحلة 1: PR #810 - توحيد Python 3.12 | Phase 1: PR #810 - Python 3.12 Standardization

**السبب | Reason**: تعارض بسبب تحديثات في main بعد إنشاء الفرع

**الحل | Solution**: 
1. إعادة التأسيس (Rebase) على main
2. حل أي تعارضات بإختيار Python 3.12
3. إعادة الدفع بـ force-with-lease

**الملفات المتوقع تعارضها | Expected Conflict Files**:
```
- pyproject.toml (Python version)
- .github/workflows/*.yml (CI Python version)
- apps/services/*/Dockerfile (Base image)
- README files (Python version mentions)
```

**الأوامر | Commands**:
```bash
# 1. Checkout branch
git fetch origin copilot/fix-ci-workflow-issues
git checkout copilot/fix-ci-workflow-issues

# 2. Fetch latest main
git fetch origin main

# 3. Rebase (creates clean history)
git rebase origin/main

# 4. If conflicts appear:
#    - Edit conflicting files
#    - Choose Python 3.12 over Python 3.11
#    - Stage: git add <file>
#    - Continue: git rebase --continue

# 5. Force push with safety check
git push origin copilot/fix-ci-workflow-issues --force-with-lease
```

**قواعد حل التعارضات | Conflict Resolution Rules**:
- ✅ Keep: `python:3.12-slim-bookworm` 
- ❌ Reject: `python:3.11-slim-bookworm`
- ✅ Keep: `requires-python = ">=3.12"`
- ❌ Reject: `requires-python = ">=3.11"`
- ✅ Keep: `python-version: '3.12'`
- ❌ Reject: `python-version: '3.11'`

---

### المرحلة 2: PR #809 - مراجعة المشروع النهائية | Phase 2: PR #809 - Final Project Review

**السبب | Reason**: إضافة ملفات توثيق جديدة قد تتعارض مع تحديثات في main

**الحل | Solution**:
1. إعادة التأسيس (Rebase) على main (بعد حل PR #810)
2. دمج أي تحديثات توثيقية من main
3. الحفاظ على الملفات الجديدة المضافة

**الملفات المتوقع تعارضها | Expected Conflict Files**:
```
- docs/AUDIT_REPORTS_INDEX.md
- docs/*.md (any updated docs in main)
```

**الأوامر | Commands**:
```bash
# Wait until PR #810 is merged, then:

# 1. Checkout branch
git fetch origin copilot/final-project-review
git checkout copilot/final-project-review

# 2. Fetch latest main (after #810 merged)
git fetch origin main

# 3. Rebase
git rebase origin/main

# 4. If conflicts:
#    - Keep new documentation files from this PR
#    - Merge any updates from main
#    - Stage: git add <file>
#    - Continue: git rebase --continue

# 5. Force push
git push origin copilot/final-project-review --force-with-lease
```

**قواعد حل التعارضات | Conflict Resolution Rules**:
- ✅ Keep all new documentation files from PR #809
- ✅ Merge doc updates from main if any
- ✅ Update cross-references as needed
- ❌ Don't delete existing documentation

---

## الأدوات المتاحة | Available Tools

### 1. دليل تفصيلي | Detailed Guide
📖 **File**: `docs/BRANCH_CONFLICT_RESOLUTION_GUIDE.md`
- Full bilingual documentation
- Step-by-step instructions
- Troubleshooting tips

### 2. سكريبت مساعد | Helper Script
🔧 **File**: `scripts/resolve-pr-conflicts.sh`
- Automated conflict detection
- Guided resolution process
- Safety checks

**الاستخدام | Usage**:
```bash
# Check conflicts
./scripts/resolve-pr-conflicts.sh check

# Resolve PR #810
./scripts/resolve-pr-conflicts.sh 810

# Resolve PR #809  
./scripts/resolve-pr-conflicts.sh 809
```

### 3. دليل سريع | Quick Reference
📋 **File**: `CONFLICT_RESOLUTION_README.md`
- Quick commands
- Expected conflict points
- Checklists

---

## الترتيب الموصى به للتنفيذ | Recommended Execution Order

### الأولوية 1: PR #810 (بنية تحتية حرجة)
```
1. ✅ Resolve conflicts with main
2. ✅ Verify all Python 3.12 references
3. ✅ Run tests and linting
4. ✅ Merge to main
```

### الأولوية 2: PR #809 (توثيق)
```
1. ✅ Wait for PR #810 to be merged
2. ✅ Rebase on updated main
3. ✅ Resolve any documentation conflicts
4. ✅ Verify documentation integrity
5. ✅ Merge to main
```

### الأولوية 3: PR #813 (سيكون نظيف تلقائياً)
```
1. ✅ After PR #810 merged, this becomes clean
2. ✅ Ready to merge without conflicts
```

---

## التحقق بعد الحل | Post-Resolution Verification

### For PR #810
```bash
# Check Python versions
grep -r "python:3\.11" apps/services/*/Dockerfile
# Should return nothing

grep -r "3\.11" .github/workflows/*.yml
# Should return nothing

grep "3\.11" pyproject.toml
# Should return nothing

# Run linting
ruff check .

# Run tests
pytest tests/smoke/ -v
```

### For PR #809
```bash
# Check documentation integrity
find docs -name "*.md" -exec grep -l "TODO\|FIXME\|XXX" {} \;

# Verify no broken links
grep -r "](.*\.md)" docs/ | grep -v "http" | while read line; do
    file=$(echo "$line" | cut -d: -f1)
    link=$(echo "$line" | grep -o "](.*\.md)" | sed 's/](\|)//g')
    if [ ! -f "docs/$link" ]; then
        echo "Broken link in $file: $link"
    fi
done
```

---

## الملاحظات الهامة | Important Notes

### ⚠️ تحذيرات | Warnings

1. **Force Push**: After rebase, force push is required
   - Use `--force-with-lease` for safety
   - This rewrites commit history

2. **Grafted History**: This repository has grafted history
   - Some git commands may behave differently
   - Always use origin/ prefix for remote branches

3. **Coordination**: If multiple people working on same branch
   - Coordinate before force pushing
   - Consider merge instead of rebase

### ✅ أفضل الممارسات | Best Practices

1. **Backup**: Create backup branch before resolving
   ```bash
   git checkout copilot/fix-ci-workflow-issues
   git checkout -b backup-810
   git push origin backup-810
   ```

2. **Test Locally**: After resolving, test before pushing
   ```bash
   make lint
   make test
   ```

3. **Document**: Update PR description with resolution notes

---

## الدعم والمساعدة | Support and Help

### إذا واجهت مشاكل | If You Encounter Issues

1. **Abort and Ask**:
   ```bash
   git rebase --abort  # or git merge --abort
   ```

2. **Check Documentation**:
   - `docs/BRANCH_CONFLICT_RESOLUTION_GUIDE.md`
   - `CONFLICT_RESOLUTION_README.md`

3. **Git Tools**:
   ```bash
   git status          # Current state
   git diff            # See changes
   git log --merge     # See conflicting commits
   ```

4. **Ask Team**: 
   - Document specific conflict
   - Share error messages
   - Request review

---

## ملخص الملفات المضافة | Summary of Added Files

```
✅ docs/BRANCH_CONFLICT_RESOLUTION_GUIDE.md
   - Full bilingual guide
   - Detailed instructions
   - Troubleshooting

✅ scripts/resolve-pr-conflicts.sh (executable)
   - Automated helper script
   - Conflict detection
   - Guided resolution

✅ CONFLICT_RESOLUTION_README.md
   - Quick reference
   - Essential commands
   - Checklist

✅ docs/BRANCH_CONFLICT_ACTION_PLAN.md (this file)
   - Action plan
   - Priority order
   - Verification steps
```

---

## الخطوات التالية | Next Steps

1. **Review Documentation**: Read the detailed guide
2. **Test Helper Script**: Try `./scripts/resolve-pr-conflicts.sh check`
3. **Start with PR #810**: Follow the resolution plan
4. **Then PR #809**: After #810 is merged
5. **Verify PR #813**: Should be clean after #810

---

**تاريخ الإنشاء | Created**: 2026-02-04
**الإصدار | Version**: 1.0.0
**الحالة | Status**: Ready for Implementation
