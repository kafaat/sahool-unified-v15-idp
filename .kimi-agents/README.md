# 🤖 Kimi Repair Agent for SAHOOL Platform

## نظام الإصلاح التلقائي للكود - Automated Code Quality System

This directory contains the configuration and documentation for the Kimi Repair Agent, an automated code quality and security scanning system integrated into the SAHOOL Unified Platform.

هذا المجلد يحتوي على إعدادات ووثائق وكيل الإصلاح التلقائي كيمي، نظام فحص تلقائي لجودة الكود والأمان المدمج في منصة سهول الموحدة.

---

## 📋 Table of Contents - جدول المحتويات

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [CI/CD Integration](#cicd-integration)
- [Supported Tools](#supported-tools)
- [Custom Rules](#custom-rules)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Kimi Repair Agent is a multi-layer code quality system that automatically scans and fixes issues across all layers of the SAHOOL platform:

- **Frontend** (React/TypeScript)
- **Backend** (Python/FastAPI)
- **Infrastructure** (Docker/Terraform)
- **Mobile** (Flutter/Dart)

وكيل كيمي هو نظام متعدد الطبقات لجودة الكود يفحص ويصلح المشكلات تلقائياً عبر جميع طبقات منصة سهول.

---

## ✨ Features - المميزات

### Automated Scanning - الفحص التلقائي
- ✅ ESLint for JavaScript/TypeScript
- ✅ Ruff for Python linting
- ✅ Bandit for security scanning
- ✅ Hadolint for Dockerfile validation
- ✅ Flutter Analyze for mobile code

### Auto-Fix Capabilities - الإصلاح التلقائي
- 🔧 Automatic code style fixes
- 🔧 Import organization
- 🔧 Formatting corrections
- 🔧 Simple refactoring

### CI/CD Integration - التكامل مع CI/CD
- 🚀 GitHub Actions workflow
- 🚀 Pre-commit hooks
- 🚀 Automated PR comments
- 🚀 Quality gates

### Custom Rules - قواعد مخصصة
- 🎯 Agricultural domain validation
- 🎯 EC (Electrical Conductivity) consistency
- 🎯 Security pattern detection
- 🎯 Type safety enforcement

---

## 📦 Installation - التثبيت

### Prerequisites - المتطلبات

```bash
# Python tools
pip install ruff bandit pytest

# Node.js tools
npm install -g eslint

# Docker (for infrastructure scanning)
docker --version

# Flutter (for mobile scanning)
flutter --version
```

### Setup - الإعداد

1. **Clone the repository**
   ```bash
   git clone https://github.com/kafaat/sahool-unified-v15-idp.git
   cd sahool-unified-v15-idp
   ```

2. **Install pre-commit hook** (optional)
   ```bash
   make kimi-install-hook
   ```

3. **Verify installation**
   ```bash
   make kimi-scan
   ```

---

## ⚙️ Configuration - الإعداد

### Main Configuration File

**File:** `.kimi-agents/sahool-repair-config.yaml`

```yaml
project_name: "SAHOOL Unified v16.0"
version: "16.0.0"

scan_tools:
  eslint:
    enabled: true
    paths: ["apps/web", "apps/admin", "packages"]
    auto_fix: true
  
  ruff:
    enabled: true
    paths: ["apps/kernel", "apps/services", "shared"]
    auto_fix: true
  
  bandit:
    enabled: true
    severity_threshold: "MEDIUM"
```

### ESLint Configuration

**File:** `.kimi-agents/eslint-kimi-config.yaml`

Custom ESLint rules for frontend code quality.

### Pylint Configuration

**File:** `.kimi-agents/pylint-kimi-config.ini`

Custom Ruff/Pylint rules for backend code quality.

---

## 🚀 Usage - الاستخدام

### Command Line - سطر الأوامر

```bash
# Run comprehensive scan
# تشغيل فحص شامل
make kimi-scan

# Apply automatic fixes
# تطبيق الإصلاحات التلقائية
make kimi-fix

# Generate detailed report
# إنشاء تقرير مفصل
make kimi-report

# Quick scan of modified files only
# فحص سريع للملفات المعدلة فقط
make kimi-quick-scan

# Show Kimi help
# عرض مساعدة Kimi
make kimi-help
```

### Direct Script Usage

```bash
# Scan only (no fixes)
./scripts/kimi-sahool-repair.sh --scan-only

# Scan and apply fixes
./scripts/kimi-sahool-repair.sh --apply-fixes

# Generate JSON report
./scripts/kimi-sahool-repair.sh --scan-only --output-json report.json
```

---

## 🔄 CI/CD Integration - التكامل مع CI/CD

### GitHub Actions Workflow

**File:** `.github/workflows/kimi-quality-check.yml`

Automatically runs on:
- Push to `main`, `develop`, `feature/*`, `copilot/*` branches
- Pull request creation/updates
- Daily at 2 AM UTC

#### Workflow Features:
- ✅ Multi-layer scanning
- ✅ PR comments with results
- ✅ Automatic labeling
- ✅ Quality gates (fails if >50 issues)

### Pre-Commit Hook

**File:** `.git/hooks/pre-commit`

Installed via: `make kimi-install-hook`

Validates code before allowing commits:
- ESLint for JS/TS files
- Ruff for Python files
- Bandit for security
- Secret detection

---

## 🛠️ Supported Tools - الأدوات المدعومة

| Tool | Language | Purpose | Auto-Fix |
|------|----------|---------|----------|
| **ESLint** | JavaScript/TypeScript | Code quality & style | ✅ |
| **Ruff** | Python | Linting & formatting | ✅ |
| **Bandit** | Python | Security scanning | ❌ |
| **Hadolint** | Dockerfile | Docker best practices | ❌ |
| **Flutter Analyze** | Dart | Mobile code quality | ✅ |
| **Terraform Validate** | HCL | Infrastructure validation | ❌ |

---

## 🎯 Custom Rules - القواعد المخصصة

### Agricultural Domain Rules

#### 1. Inconsistent EC Usage
**Pattern:** `ec_value.*fertilizer`

**Severity:** MEDIUM

**Description:** Ensures EC (Electrical Conductivity) values are not confused with nutrient/fertilizer values.

```python
# ❌ Bad
ec_value = fertilizer_amount * 2

# ✅ Good
ec_value = soil_ec_measurement
fertilizer_rate = calculate_fertilizer(ec_value)
```

#### 2. Missing Type Hints
**Pattern:** `def\s+\w+\([^)]*\)\s*:`

**Severity:** LOW

**Description:** Python functions should have type hints for better code clarity.

```python
# ❌ Bad
def calculate_irrigation(field_size):
    return field_size * 2.5

# ✅ Good
def calculate_irrigation(field_size: float) -> float:
    return field_size * 2.5
```

#### 3. Hardcoded Passwords
**Pattern:** `password\s*=\s*['"][^'"]+['"]`

**Severity:** CRITICAL

**Description:** No hardcoded passwords or secrets in code.

```python
# ❌ Bad
password = "mypassword123"

# ✅ Good
password = os.getenv("DATABASE_PASSWORD")
```

#### 4. Empty Except Blocks
**Pattern:** `except.*:\s*pass`

**Severity:** MEDIUM

**Description:** Avoid empty except blocks that hide errors.

```python
# ❌ Bad
try:
    result = api_call()
except:
    pass

# ✅ Good
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    raise
```

---

## 📊 Example Output - مثال النتائج

### Console Output

```
════════════════════════════════════════════════════════════
  🤖 وكيل إصلاح Kimi v16.0 - Kimi Repair Agent v16.0
  منصة سهول الزراعية الموحدة - SAHOOL Unified Platform
════════════════════════════════════════════════════════════

📊 المرحلة 1: فحص جميع الطبقات - Phase 1: Scanning All Layers...

   🔍 فحص Frontend - Scanning Frontend...
      ✅ ESLint scan completed: 12 issues found

   🔍 فحص Backend - Scanning Backend...
      ✅ Ruff scan completed: 8 issues found
      ✅ Bandit scan completed: 2 security issues found

   🔍 فحص Infrastructure - Scanning Infrastructure...
      ✅ Dockerfile lint completed: 3 issues found

   🔍 فحص Mobile - Scanning Mobile...
      ✅ Flutter analyze completed: 5 issues found

✅ فحص اكتمل - Scan completed!
   📊 Total Issues: 30
   - Frontend: 12
   - Backend: 10
   - Infrastructure: 3
   - Mobile: 5
```

### JSON Report

```json
{
  "total_issues": 30,
  "frontend": {
    "issues": 12,
    "tools": ["eslint"]
  },
  "backend": {
    "issues": 10,
    "tools": ["ruff", "bandit"]
  },
  "infrastructure": {
    "issues": 3,
    "tools": ["hadolint"]
  },
  "mobile": {
    "issues": 5,
    "tools": ["flutter_analyze"]
  },
  "timestamp": "2026-01-28T16:00:00Z",
  "version": "16.0.0"
}
```

---

## 🔧 Troubleshooting - حل المشكلات

### Common Issues

#### Issue 1: Tools Not Found
```bash
# Error: npx: command not found
# Solution: Install Node.js and npm
npm install -g npm
```

#### Issue 2: Permission Denied
```bash
# Error: Permission denied: ./scripts/kimi-sahool-repair.sh
# Solution: Make script executable
chmod +x scripts/kimi-sahool-repair.sh
```

#### Issue 3: No Python Tools
```bash
# Error: ruff: command not found
# Solution: Install Python dependencies
pip install ruff bandit pytest
```

#### Issue 4: Pre-commit Hook Not Working
```bash
# Solution: Reinstall the hook
make kimi-install-hook
chmod +x .git/hooks/pre-commit
```

---

## 📚 Additional Resources - موارد إضافية

- **Configuration:** `.kimi-agents/sahool-repair-config.yaml`
- **Script:** `scripts/kimi-sahool-repair.sh`
- **Workflow:** `.github/workflows/kimi-quality-check.yml`
- **PR Template:** `.kimi-agents/pr-template.md`

---

## 🤝 Contributing - المساهمة

To add new Kimi rules:

1. Edit `.kimi-agents/sahool-repair-config.yaml`
2. Add rule definition under `rules:` section
3. Test with `make kimi-scan`
4. Commit and create PR

---

## 📄 License - الترخيص

Proprietary - KAFAAT © 2026

Part of SAHOOL Unified Platform v16.0.0

---

## 📞 Support - الدعم

For issues or questions:
- Email: dev@kafaat.io
- GitHub Issues: https://github.com/kafaat/sahool-unified-v15-idp/issues

---

**Generated by Kimi Repair Agent v16.0.0**  
**Last Updated:** 2026-01-28
