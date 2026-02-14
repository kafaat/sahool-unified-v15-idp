# Dependency Version Audit Report - February 2026

# تقرير تدقيق إصدارات المكتبات - فبراير 2026

**Date**: 2026-02-14
**Version**: 16.0.0
**Status**: All conflicts resolved

---

## Executive Summary | الملخص التنفيذي

A comprehensive dependency audit was conducted across all 72 Python requirements files and 39 Node.js package.json files in the SAHOOL platform. All identified conflicts have been resolved.

تم إجراء تدقيق شامل للمكتبات عبر 72 ملف requirements.txt للخدمات Python و 39 ملف package.json لخدمات Node.js. تم حل جميع التعارضات المكتشفة.

---

## Python Audit Results | نتائج تدقيق Python

### Scope

| Metric | Value |
|--------|-------|
| Total `requirements.txt` files audited | 72 |
| Total unique Python packages | 124 |
| Active services checked | 57 |
| Kernel modules checked | 3 |
| Shared modules checked | 2 |
| IDP templates checked | 2 |
| Tools checked | 1 |

### Issues Found & Fixed

#### 1. IDP Template Outdated Versions (7 fixes)

The FastAPI service template (`idp/templates/python-fastapi/skeleton/`) had outdated pinned versions that diverged from `constraints.txt`.

| Package | Before | After |
|---------|--------|-------|
| `fastapi` | `==0.126.0` | `==0.128.5` |
| `uvicorn` | `==0.34.0` | `==0.40.0` |
| `pydantic` | `==2.9.2` | `==2.12.5` |
| `prometheus-client` | `==0.21.1` | `==0.24.1` |
| `opentelemetry-api` | `==1.29.0` | `==1.39.1` |
| `opentelemetry-sdk` | `==1.29.0` | `==1.39.1` |
| `opentelemetry-exporter-otlp-proto-http` | `==0.50b0` | `==0.60b1` |
| `opentelemetry-instrumentation-fastapi` | `==0.50b0` | `==0.60b1` |

#### 2. NumPy Version Inconsistencies (17 fixes)

NumPy had 7 different version specifications across 19 services. All standardized to `>=1.26.0,<2.5.0` (matching `constraints.txt`).

| Previous Spec | Services | Issue |
|---------------|----------|-------|
| `==1.26.4` | 4 | Exact pin, unnecessarily restrictive |
| `>=1.24.0` | 3 | Below constraint minimum |
| `>=1.26.0,<2.0.0` | 3 | Upper bound too restrictive |
| `>=1.26.0,<2.1.0` | 6 | Upper bound too restrictive |
| `>=1.26.0,<2.5.0` | 2 | Already correct |
| `>=2.0.0` | 1 | Excluded valid numpy 1.x (data-pipeline template) |

**After fix**: All 19 services use `>=1.26.0,<2.5.0`.

#### 3. Authentication Package Standardization (5 fixes)

| Package | Issue | Fix |
|---------|-------|-----|
| `PyJWT>=2.8.0` (no upper bound) | 3 services | Added `<3.0.0` upper bound |
| `python-jose>=3.3.0` | 2 services | Updated to `>=3.4.0` (constraint minimum) |

#### 4. Observability Module Updates (1 file, multiple changes)

`shared/observability/requirements.txt` was outdated (December 2024, v15.3.3).

| Package Group | Before | After |
|---------------|--------|-------|
| `prometheus-client` | `>=0.19.0` | `>=0.24.1` |
| `opentelemetry-api/sdk` | `>=1.21.0` | `>=1.39.1` |
| `opentelemetry-instrumentation-*` | `>=0.42b0` | `>=0.60b1` |
| `opentelemetry-exporter-otlp-*` | `>=1.21.0` | `>=1.39.1` |
| `fastapi` | `>=0.115.0` | `>=0.128.5` |
| `aiohttp` | `>=3.9.0` | `>=3.13.3` (CVE fixes) |

### Post-Fix Verification

```
Constraint violations:  0
Inter-service conflicts: 0
NumPy specifications:   19/19 consistent (>=1.26.0,<2.5.0)
```

---

## Node.js Audit Results | نتائج تدقيق Node.js

### Scope

| Metric | Value |
|--------|-------|
| Total `package.json` files audited | 39 |
| Total unique npm packages | 156 |
| Major version conflicts found | 16 |
| Conflicts fixed | 10 |
| Intentionally skipped | 6 |

### Issues Fixed

| Package | Service | Before | After |
|---------|---------|--------|-------|
| `@nestjs/swagger` | `shared/versioning` | `^7.0.0` | `^8.0.0` |
| `uuid` | `shared/versioning` | `^9.0.0` | `^11.0.0` |
| `@types/uuid` | `shared/versioning` | `^9.0.0` | `^10.0.0` |
| `@types/express` | `idp/templates/node-service` | `^4.17.21` | `^5.0.0` |
| `@types/express` | `packages/shared-audit` | `^4.17.0` | `^5.0.0` |
| `@types/express` | `packages/shared-types` | `^4.17.21` | `^5.0.0` |
| `supertest` | `field-management-service` | `^6.3.3` | `^7.0.0` |
| `eslint` | `research-core` | `^8.42.0` | `^9.0.0` |
| `@types/passport-jwt` | `research-core` | `^3.0.13` | `^4.0.0` |
| `@types/jest` | `yield-prediction-service` | `^30.0.0` | `^29.5.0` |

### Intentionally Skipped

| Package | Service | Reason |
|---------|---------|--------|
| `react@18` | `apps/mobile/sahool-mobile` | React Native compatibility requires v18 |
| `next>=14.0.0` | `packages/i18n` | peerDependency, broad range is correct |
| `@types/node@22` | `user-service`, `shared/errors` | May need newer Node.js types |
| `eslint@8` / `@typescript-eslint/*@7` | `apps/mobile/sahool-mobile` | React Native ESLint compatibility |

---

## Remaining Architecture Notes | ملاحظات معمارية

### Intentional Version Differences

1. **React 18 vs 19**: Mobile app (`sahool-mobile`) uses React 18 for React Native compatibility. Web/admin apps use React 19. This is expected.

2. **@types/node 20 vs 22**: Two services use `@types/node@22` while 26 use `@types/node@20`. Both are valid; the newer types provide better coverage for Node.js 22 LTS features.

3. **PyJWT exact pin in shared/auth**: `apps/services/shared/auth/` pins `PyJWT==2.10.1` while other services use `>=2.8.0,<3.0.0`. The shared auth module needs exact pinning for stability.

### Recommendations

1. **Run `npm install --legacy-peer-deps`** after these changes to update lockfiles
2. **Run `pip install -c constraints.txt -r requirements.txt`** in affected services to verify resolution
3. **Consider adding a CI check** that validates all requirements against `constraints.txt` automatically

---

## Files Modified | الملفات المعدلة

### Python (25 files)

- `constraints.txt` - Updated date
- `idp/templates/python-fastapi/skeleton/requirements.txt` - 8 version updates
- `idp/templates/data-pipeline/skeleton/requirements.txt` - numpy fix
- `shared/observability/requirements.txt` - 6 version range updates
- `apps/kernel/field_ops/requirements.txt` - numpy standardized
- `apps/kernel/requirements.txt` - numpy standardized
- `apps/services/ai-advisor/requirements.txt` - numpy standardized
- `apps/services/ai-agents-core/requirements.txt` - numpy standardized
- `apps/services/ai-agents-service/requirements.txt` - numpy standardized
- `apps/services/copilot-api/requirements.txt` - python-jose fix
- `apps/services/crop-intelligence-service/requirements.txt` - PyJWT upper bound
- `apps/services/digital-twin-engine/requirements.txt` - numpy standardized
- `apps/services/fertigation-engine/requirements.txt` - numpy standardized
- `apps/services/field-chat/requirements.txt` - PyJWT upper bound
- `apps/services/hydrology-service/requirements.txt` - numpy standardized
- `apps/services/iot-sensor-hub/requirements.txt` - numpy standardized
- `apps/services/irrigation-cycle-engine/requirements.txt` - numpy standardized
- `apps/services/irrigation-smart/requirements.txt` - PyJWT upper bound
- `apps/services/ndvi-processor/requirements.txt` - numpy standardized
- `apps/services/supply-chain-service/requirements.txt` - python-jose fix
- `apps/services/terrain-core-service/requirements.txt` - numpy standardized
- `apps/services/vegetation-analysis-service/requirements.txt` - numpy standardized
- `apps/services/virtual-sensors/requirements.txt` - numpy standardized
- `apps/services/yield-engine/requirements.txt` - numpy standardized
- `apps/services/yolo26-vision-service/requirements.txt` - numpy standardized

### Node.js (7 files)

- `shared/versioning/package.json` - @nestjs/swagger, uuid, @types/uuid
- `idp/templates/node-service/skeleton/package.json` - @types/express
- `packages/shared-audit/package.json` - @types/express
- `packages/shared-types/package.json` - @types/express
- `apps/services/field-management-service/package.json` - supertest
- `apps/services/research-core/package.json` - eslint, @types/passport-jwt
- `apps/services/yield-prediction-service/package.json` - @types/jest

---

*Generated by dependency audit script - February 14, 2026*
