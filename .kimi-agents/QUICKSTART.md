# 🚀 Kimi Repair Agent - Quick Start Guide

## التشغيل السريع - Quick Start

This guide will help you get started with Kimi Repair Agent in under 5 minutes.

سيساعدك هذا الدليل على بدء استخدام وكيل كيمي في أقل من 5 دقائق.

---

## ⚡ Installation - التثبيت

### 1. Install Dependencies (One Time)

```bash
# Python tools
pip install ruff bandit pytest

# Node.js tools (if you have frontend work)
npm install -g eslint
```

### 2. Verify Installation

```bash
make kimi-help
```

You should see Kimi commands listed.

---

## 🔍 Basic Usage - الاستخدام الأساسي

### Scan Your Code

```bash
# Run comprehensive scan
make kimi-scan
```

**Output Example:**
```
🤖 وكيل إصلاح Kimi v16.0 - Kimi Repair Agent v16.0
📊 Total Issues: 30
   - Frontend: 12
   - Backend: 10
   - Infrastructure: 3
   - Mobile: 5
```

### Apply Auto-Fixes

```bash
# Apply automatic fixes
make kimi-fix
```

**⚠️ Important:** Always review changes before committing!

### Quick Scan (Modified Files Only)

```bash
# Fast scan of changed files
make kimi-quick-scan
```

---

## 🪝 Enable Pre-Commit Hook

```bash
# Install pre-commit hook (optional but recommended)
make kimi-install-hook
```

This will check your code **before every commit**.

---

## 📊 Generate Reports

```bash
# Generate JSON report
make kimi-report
```

The report will be saved to `/tmp/kimi-report.json`.

---

## 🎯 Common Workflows - سير العمل الشائع

### Workflow 1: Before Committing

```bash
# 1. Check what changed
git status

# 2. Quick scan
make kimi-quick-scan

# 3. Fix issues if any
make kimi-fix

# 4. Review changes
git diff

# 5. Commit
git add .
git commit -m "Your message"
```

### Workflow 2: Daily Code Quality Check

```bash
# Run comprehensive scan
make kimi-scan

# Review the report
# Fix critical issues manually
# Let Kimi auto-fix the rest
make kimi-fix
```

### Workflow 3: Before Pull Request

```bash
# 1. Comprehensive scan
make kimi-scan

# 2. Generate report
make kimi-report

# 3. Review JSON report
cat /tmp/kimi-report.json | jq .

# 4. Fix all issues
make kimi-fix

# 5. Verify
make kimi-scan

# 6. Create PR
git push
```

---

## 📖 Key Commands Reference

| Command | Purpose | Arabic |
|---------|---------|--------|
| `make kimi-scan` | Full scan | فحص شامل |
| `make kimi-fix` | Auto-fix | إصلاح تلقائي |
| `make kimi-quick-scan` | Quick scan | فحص سريع |
| `make kimi-report` | Generate report | إنشاء تقرير |
| `make kimi-install-hook` | Install pre-commit | تثبيت pre-commit |
| `make kimi-help` | Show help | عرض المساعدة |

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `.kimi-agents/sahool-repair-config.yaml` | Main configuration |
| `.kimi-agents/eslint-kimi-config.yaml` | Frontend rules |
| `.kimi-agents/pylint-kimi-config.ini` | Backend rules |
| `scripts/kimi-sahool-repair.sh` | Main scan script |
| `.github/workflows/kimi-quality-check.yml` | CI/CD workflow |

---

## 🚨 Troubleshooting - حل المشكلات

### Problem: "Command not found"

```bash
# Install missing tools
pip install ruff bandit
npm install -g eslint
```

### Problem: "Permission denied"

```bash
# Make script executable
chmod +x scripts/kimi-sahool-repair.sh
```

### Problem: "No issues found but I know there are some"

```bash
# Check if tools are installed
which ruff
which eslint
which bandit

# Run script directly with verbose output
./scripts/kimi-sahool-repair.sh --scan-only
```

---

## 📞 Getting Help

- **Full Documentation:** `.kimi-agents/README.md`
- **Configuration:** `.kimi-agents/sahool-repair-config.yaml`
- **Support:** dev@kafaat.io

---

## ✅ Next Steps

1. ✅ Run your first scan: `make kimi-scan`
2. ✅ Install pre-commit hook: `make kimi-install-hook`
3. ✅ Read full documentation: `.kimi-agents/README.md`
4. ✅ Customize rules in: `.kimi-agents/sahool-repair-config.yaml`

---

**Happy Coding! 🎉**

*Kimi Repair Agent v16.0.0 - Part of SAHOOL Unified Platform*
