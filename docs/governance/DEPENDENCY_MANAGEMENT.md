# SAHOOL Dependency Management

# إدارة المكتبات والتبعيات

## Overview | نظرة عامة

This document describes the dependency management practices for the SAHOOL platform,
ensuring consistency, stability, and security across all services.

---

## 📋 Central Version Control

### Python Dependencies

All Python services MUST use versions defined in:

1. **`pyproject.toml`** - Central version definitions
2. **`constraints.txt`** - Pip constraints for consistency

#### Usage

```bash
# Install with constraints
pip install -c constraints.txt -r requirements.txt

# Or use pip-sync (recommended)
pip-compile requirements.in -c constraints.txt
pip-sync requirements.txt
```

### Node.js Dependencies

Frontend applications use npm workspaces for version consistency:

```
package.json (root)
├── workspaces: packages/*, apps/*
├── engines: node>=20, npm>=10
└── devDependencies: typescript, @types/node (shared)
```

### Flutter Dependencies

Mobile app uses `pubspec.yaml` with `dependency_overrides` for compatibility:

```yaml
# Fix compatibility issues
dependency_overrides:
  analyzer: ^6.7.0 # For mockito compatibility
```

---

## 🔄 Automatic Updates (Dependabot)

Dependabot is configured in `.github/dependabot.yml`:

| Ecosystem      | Schedule | Day       | Groups               |
| -------------- | -------- | --------- | -------------------- |
| Python (pip)   | Weekly   | Monday    | Minor/Patch together |
| Node.js (npm)  | Weekly   | Tuesday   | React, Next, Testing |
| Flutter (pub)  | Weekly   | Wednesday | Core, UI packages    |
| GitHub Actions | Weekly   | Thursday  | All actions          |
| Docker         | Monthly  | -         | Base images          |

### Review Process

1. Dependabot creates PR with version bump
2. CI runs tests automatically
3. Review breaking changes in CHANGELOG
4. Merge if tests pass
5. Monitor production for issues

---

## 📌 Version Pinning Strategy

### Pinned Versions (==)

Use for **critical dependencies** that affect API contracts:

```txt
fastapi==0.126.0      # API framework
pydantic==2.10.3      # Validation
tensorflow-cpu==2.18.0 # ML models
```

### Range Constraints (>=, <)

Use for **compatibility requirements**:

```txt
numpy>=1.26.0,<2.1.0  # TensorFlow compatibility
aiohttp>=3.11.12      # Security minimum
```

### Caret Constraints (^)

Use in **Flutter/Dart** for minor updates:

```yaml
flutter_riverpod: ^2.6.1 # Allows 2.6.x, not 3.x
```

---

## 🚨 Known Constraints

### NumPy < 2.1.0

**Reason:** TensorFlow 2.18.0 requires `numpy<2.1.0`

**Affected services:**

- `crop-health-ai`
- `yield-engine`
- `virtual-sensors`

**Resolution:** Upgrade to TensorFlow 2.19.x when available

### Analyzer ^6.7.0 (Flutter)

**Reason:** mockito 5.4.5 incompatible with analyzer 7.x

**Resolution:** Fixed with `dependency_overrides` in `pubspec.yaml`

---

## 📊 Version Matrix

### Python Services (Active)

| Package  | Version | Updated  |
| -------- | ------- | -------- |
| fastapi  | 0.126.0 | Dec 2025 |
| uvicorn  | 0.34.0  | Dec 2025 |
| pydantic | 2.10.3  | Dec 2025 |
| httpx    | 0.28.1  | Dec 2025 |
| asyncpg  | 0.30.0  | Dec 2025 |
| redis    | 5.2.1   | Dec 2025 |
| nats-py  | 2.9.0   | Dec 2025 |

### Frontend (Node.js)

| Package     | Version | Updated  |
| ----------- | ------- | -------- |
| next        | 15.1.2  | Dec 2025 |
| react       | 19.0.0  | Dec 2025 |
| typescript  | 5.7.2   | Dec 2025 |
| tailwindcss | 3.4.17  | Dec 2025 |

### Mobile (Flutter)

| Package  | Version | Updated  |
| -------- | ------- | -------- |
| flutter  | 3.27.1  | Dec 2025 |
| dart     | 3.6.0   | Dec 2025 |
| drift    | 2.22.1  | Dec 2025 |
| riverpod | 2.6.1   | Dec 2025 |

---

## 🔐 Security Updates

### Priority Handling

1. **Critical (CVE):** Update within 24 hours
2. **High:** Update within 1 week
3. **Medium:** Include in next release
4. **Low:** Batch with regular updates

### Security Scanning

```yaml
# CI Security Checks
- Bandit (Python security linter)
- Trivy (vulnerability scanner)
- detect-secrets (credential leaks)
```

---

## 📝 Adding New Dependencies

### Checklist

- [ ] Check license compatibility (avoid GPL in proprietary code)
- [ ] Verify security status (no known CVEs)
- [ ] Check maintenance status (active maintainer)
- [ ] Add to `constraints.txt` with pinned version
- [ ] Update `pyproject.toml` if platform-wide
- [ ] Document in this file if significant

### Example PR

```markdown
## Add `new-package` dependency

- **Package:** new-package==1.2.3
- **Purpose:** Handle X feature
- **License:** MIT ✅
- **CVEs:** None ✅
- **Last commit:** 2 weeks ago ✅
```

---

## 🔄 Upgrade Workflow

### Monthly Upgrade Cycle

1. **Week 1:** Review Dependabot PRs
2. **Week 2:** Test upgrades in staging
3. **Week 3:** Deploy to production
4. **Week 4:** Monitor and document

### Breaking Change Handling

1. Create upgrade branch
2. Update code for compatibility
3. Run full test suite
4. Document migration steps
5. Update ADR if architectural impact

---

## 📚 References

- [constraints.txt](/constraints.txt) - Central version constraints
- [pyproject.toml](/pyproject.toml) - Python project configuration
- [Dependabot Config](/.github/dependabot.yml) - Auto-update settings
- [ADR-004: Kong Gateway](/docs/adr/ADR-004-kong-api-gateway.md)
- [ADR-005: NATS Event Bus](/docs/adr/ADR-005-nats-event-bus.md)
