# دليل حل التعارضات مع Main

# Merge Conflict Resolution Guide

**الفرع**: `copilot/resolve-dependency-and-workflow-issues` → `main`  
**التاريخ**: 7 يناير 2026

---

## 📋 التعارضات المكتشفة

| الملف                                   | الحل                          |
| --------------------------------------- | ----------------------------- |
| `.github/workflows/container-tests.yml` | **PR version** ✅             |
| `.gitleaks.toml`                        | **PR version** ✅ (30+ قاعدة) |
| `.hadolint.yaml`                        | **PR version** ✅             |

---

## 🛠️ الحل السريع

### GitHub UI:

1. افتح PR → "Resolve conflicts"
2. احتفظ بـ PR version لكل ملف
3. "Commit merge" → "Merge PR"

### Git CLI:

```bash
git checkout main && git pull
git merge copilot/resolve-dependency-and-workflow-issues
git checkout --ours .github/workflows/container-tests.yml
git checkout --ours .gitleaks.toml
git checkout --ours .hadolint.yaml
git add . && git commit -m "Merge: keep PR improvements"
git push origin main
```

---

**التوصية**: استخدم PR version (أشمل وأفضل) ✅
