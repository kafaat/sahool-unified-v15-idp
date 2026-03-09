# Dependency Version Conflict Analysis Report

**Date**: 2026-03-09
**Platform**: SAHOOL v16.0.0
**Analysis Method**: 17 parallel agents covering all dependency layers
**Scope**: 72 active services, 24 npm packages, 3 Flutter apps, 32 Helm charts, 53 CI workflows

---

## Executive Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 6 | Major version mismatches, dev/prod divergence, floating tags |
| **HIGH** | 5 | Version drift from central constraints affecting 50+ services |
| **MEDIUM** | 15 | Patch-level mismatches, module system conflicts, wildcard deps |
| **LOW** | 15 | Minor inconsistencies, duplicates, non-blocking |
| **INFO** | 6 | Observations and recommendations |

**Total conflicts found: 47 across 17 analysis categories**

---

## 1. Python Constraints vs Service Requirements

### CRITICAL: tortoise-orm Major Version Mismatch

| Location | Version | Status |
|----------|---------|--------|
| `constraints.txt` | `==0.25.4` | **Stale** |
| 6 active services | `==1.1.6` | **Production** |
| Archived services | `==0.21.7` / `==0.25.4` | Deprecated |

**Affected services**: field-management-service, knowledge-graph, ndvi-processor, notification-service, ws-gateway, apps/services/requirements.txt

**Risk**: Services using `-c constraints.txt` will install 0.25.4 instead of 1.1.6, causing import failures (API breaking changes between 0.x and 1.x).

**Fix**: Update `constraints.txt` to `tortoise-orm==1.1.6`

---

### HIGH: nats-py Version Drift (50 services)

| Location | Version |
|----------|---------|
| `constraints.txt` | `==2.14.0` |
| All 50 active services | `==2.13.1` |
| IDP template | `==2.13.1` |

**Risk**: Services not using `-c constraints.txt` install 2.13.1. Version 2.14.0 includes JetStream consumer bugfixes.

**Fix**: Update all 50 service requirements.txt from `==2.13.1` to `==2.14.0`

---

### HIGH: python-dotenv Version Drift (40 services)

| Location | Version |
|----------|---------|
| `constraints.txt` | `==1.2.2` |
| 40 active services | `==1.2.1` |

**Fix**: Update all 40 services from `==1.2.1` to `==1.2.2`

---

### MEDIUM: pydantic-settings (9 services)

| Location | Version |
|----------|---------|
| `constraints.txt` | `==2.13.1` |
| 9 services | `==2.12.0` |

**Affected**: agent-registry, ai-advisor, ai-chat-assistant, code-review-service, globalgap-compliance, leveling-optimizer-service, ndvi-processor, terrain-core-service, virtual-sensors

---

### MEDIUM: uvicorn (8 services)

| Location | Version |
|----------|---------|
| `constraints.txt` | `==0.41.0` |
| 8 services | `==0.40.0` |

**Affected**: code-review-service, cooperative-service, drone-service, inventory-service, mcp-server, soil-analysis-service, traceability-service, yolo26-vision-service

---

### MEDIUM: alembic (6 services)

| Location | Version |
|----------|---------|
| `constraints.txt` | `==1.18.4` |
| 6 services | `==1.18.3` |

**Affected**: alert-service, audit-service, billing-core, equipment-service, field-intelligence, provider-config

---

### MEDIUM: psycopg2-binary (6 services)

| Location | Version |
|----------|---------|
| `constraints.txt` | `==2.9.11` |
| 6 services | `==2.9.9` |

**Affected**: alert-service, audit-service, equipment-service, field-intelligence, logistics-service, provider-config

---

### MEDIUM: Geospatial Libraries (2 services)

| Package | Constraint | Service Version | Affected |
|---------|-----------|----------------|----------|
| rasterio | `==1.4.4` | `==1.4.3` | ndvi-processor, terrain-core-service |
| shapely | `==2.1.2` | `==2.0.6` | ndvi-processor, terrain-core-service |
| pyproj | `==3.7.2` | `==3.7.0` | ndvi-processor, terrain-core-service |

---

### LOW: Dev Tool Versions

| Package | Constraint | Service Version | Affected |
|---------|-----------|----------------|----------|
| ruff | `==0.15.5` | `==0.15.0` | ai-chat-assistant, leveling-optimizer-service |
| mypy | `==1.19.1` | `==1.14.1` | ai-chat-assistant |

---

## 2. Security Library Conflicts

### HIGH: PyJWT Lower Bound Allows Vulnerable Versions

| Location | Version | Issue |
|----------|---------|-------|
| `constraints.txt` | `>=2.10.1,<3.0.0` | Correct (CVE-2024-53861 fixed) |
| `docker/constraints-ai.txt` | `>=2.9.0,<3.0.0` | **Allows vulnerable 2.9.x** |
| `apps/services/requirements.txt` | `>=2.8.0,<3.0.0` | **Allows vulnerable 2.8.x** |

**Fix**: Raise lower bounds to `>=2.10.1` in both files.

### MEDIUM: Dual Database Drivers

3 services use both `asyncpg` AND `psycopg2-binary`:
- yolo26-vision-service
- logistics-service
- field-intelligence

**Risk**: Connection pool confusion, memory overhead.

### LOW: bcrypt Not in Central Constraints

`bcrypt==5.0.0` is used in `shared/auth/` and `shared/requirements.txt` but has no constraint in `constraints.txt`.

---

## 3. Node.js Workspace Dependencies

### LOW: ioredis Version Spread

| Package | Version | Count |
|---------|---------|-------|
| nestjs-auth, crop-growth-model, lai-estimation, marketplace-service, yield-prediction-service | `^5.0.0` | 5 |
| shared/cache | `^5.3.0` | 1 |
| apps/web | `^5.4.1` | 1 |
| iot-service | `^5.4.2` | 1 |

Ranges overlap but inconsistent floors.

### LOW: node-redis Version Spread

| Package | Version |
|---------|---------|
| Most services | `^4.6.0` |
| user-service | `^4.7.0` |

### MEDIUM: Module System Split (CommonJS vs ESNext)

17 TypeScript configs use `module: "commonjs"` (all NestJS services), 10 use `module: "ESNext"` (frontend/packages), 1 uses `NodeNext`. Shared packages (`field-shared`, `shared-events`, `shared-db`) emit CommonJS but may be consumed by ESNext consumers, risking runtime failures.

### MEDIUM: `esModuleInterop` Missing (5 NestJS services)

chat-service, iot-service, research-core, user-service, yield-prediction-service set `allowSyntheticDefaultImports: true` but omit `esModuleInterop`, risking subtle runtime import failures with CJS default exports.

### LOW: `@sahool/code-review-agent` Version Outlier

Versioned at `1.0.0` while every other package in the monorepo is at `16.0.0`.

### LOW: `file:` vs Workspace Resolution

`nestjs-auth` and `field-shared` use `file:` protocol references while other `@sahool/*` packages use `^16.0.0` semver workspace resolution.

### LOW: Prisma CLI as Dependency

`user-service` lists `prisma` CLI in `dependencies` instead of `devDependencies` (unlike all other services).

### LOW: ESLint Dead Root Config

25 of 29 TypeScript workspaces have no ESLint config. Root `.eslintrc.base.json` (legacy format) is not referenced by any flat config workspace.

### INFO: TypeScript Consistent

All workspaces use TypeScript `^5.9.3` or `5.9.3`. No conflicts.

### INFO: React Versions

| Location | Version |
|----------|---------|
| apps/web, apps/admin | `^19.2.4` or `^19.0.0` |
| packages (peerDeps) | `>=18.0.0` |

Compatible - peer deps allow React 19.

---

## 4. Flutter/Dart Dependencies

### INFO: No Version Conflicts

All 3 Flutter pubspec.yaml files use identical version constraints for all shared packages. The `dependency_overrides` (record_platform_interface: 1.2.0) is identical and documented.

### LOW: Duplicate pubspec.yaml

`apps/mobile/pubspec.yaml` and `apps/mobile/sahool_field_app/pubspec.yaml` both declare `name: sahool_field_app`. Minor drift:
- `crypto`: root `^3.0.3` vs sahool_field_app `^3.0.6`
- `sentry_flutter`: present in root, absent from sahool_field_app
- `timezone`: absent from root, present in sahool_field_app

---

## 5. Docker Base Images

### INFO: Consistent Base Images

All Python services use `python:${PYTHON_VERSION}-slim-bookworm` (default 3.11). Exception:
- yolo26-vision-service: `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` (expected)
- 2 services use `-slim` instead of `-slim-bookworm` (minor)

All Node.js services use `node:${NODE_VERSION}-bookworm-slim` (20.x).

---

## 6. GitHub Actions CI Workflows

### MEDIUM: Python Version Inconsistency

| Version | Count | Workflows |
|---------|-------|-----------|
| `${{ env.PYTHON_VERSION }}` | 47 | Most workflows (good) |
| `'3.11'` (hardcoded) | 37 | Various |
| `'3.12'` (hardcoded) | 5 | Some workflows |

**Risk**: 5 workflows use Python 3.12 while platform target is 3.11.

### INFO: Node.js Version Consistent

All workflows use Node 20 (via env var or hardcoded `'20'`).

---

## 7. Helm Charts & Docker-Compose vs Helm

### CRITICAL: inventory-service Stuck at 15.3.2

| Source | Version |
|--------|---------|
| `helm/services/inventory-service/Chart.yaml` | `appVersion: 15.3.2` |
| `helm/services/inventory-service/values.yaml` | `image.tag: 15.3.2` |
| `helm/sahool/values.yaml` (umbrella) | `inventoryService.image.tag: 16.0.0` |

Standalone chart deploys v15.3.2 while umbrella chart deploys v16.0.0.

### CRITICAL: Qdrant Version Gap (Dev vs Prod)

| Source | Version |
|--------|---------|
| `docker-compose.yml` | `qdrant/qdrant:v1.7.4` |
| `helm/sahool/values.yaml` | `qdrant/qdrant:v1.10.1` |

3-minor-version gap could cause data format or API incompatibilities.

### CRITICAL: Kong Floating Tag in Helm

| Source | Version |
|--------|---------|
| `docker-compose.yml` | `kong:3.4.2` (exact) |
| `helm/sahool/values.yaml` | `kong:3.4` (floating) |

Floating tag `3.4` can resolve to different images across deployments.

### MEDIUM: Wildcard Helm Dependency Versions

Umbrella chart `helm/sahool/Chart.yaml` uses wildcards:
- `postgresql: "13.x.x"`, `nats: "1.x.x"`, `redis: "18.x.x"`

Could pull different sub-chart versions across builds.

### LOW: appVersion Mismatch

| Chart | appVersion |
|-------|-----------|
| Most charts | `16.0.0` |
| infra chart | `1.0.0` |

### LOW: Duplicate crop-intelligence-service Chart

Exists in both `helm/charts/` and `helm/services/` — maintenance risk.

---

## 8. Service Ports

### MEDIUM: Port 3025 Duplicate

Port `3025` appears twice in `packages/shared-types/src/contracts/service-ports.ts`. Both map to user-service/AUTH, so this is likely an alias, not a true conflict.

---

## 9. pyproject.toml vs constraints.txt

### INFO: Fully Compatible

All versions in `pyproject.toml` are compatible with `constraints.txt`. No conflicts found.

---

## Conflict Summary by Count

| Category | Conflicts | Affected Services |
|----------|-----------|-------------------|
| nats-py drift | 1 conflict | 50 services |
| python-dotenv drift | 1 conflict | 40 services |
| pydantic-settings | 1 conflict | 9 services |
| uvicorn | 1 conflict | 8 services |
| tortoise-orm | 1 conflict | 6 services |
| alembic | 1 conflict | 6 services |
| psycopg2-binary | 1 conflict | 6 services |
| PyJWT lower bound | 2 conflicts | 2 files |
| Geospatial (3 pkgs) | 3 conflicts | 2 services |
| structlog variants | 6 specs | ~55 services |
| pytest variants | 6 specs | ~29 services |
| ioredis (Node) | 4 specs | 8 packages |
| CI Python version | 3 variants | 5 workflows |
| Dual DB drivers | - | 3 services |
| Helm appVersion | 1 mismatch | 1 chart |
| Dart pubspec drift | 3 items | 2 files |
| Dev tools | 2 conflicts | 2 services |
| Module system split | CJS vs ESNext | 29 configs |
| esModuleInterop missing | 5 configs | 5 NestJS services |
| ESLint dead root config | 1 issue | 25 workspaces uncovered |
| Package version outlier | 1.0.0 vs 16.0.0 | code-review-agent |
| file: vs workspace resolution | 2 packages | nestjs-auth, field-shared |

---

## Recommended Action Plan

### Phase 1: Critical (Immediate)

1. **Update `constraints.txt`**: Set `tortoise-orm==1.1.6` to match active services
2. **Fix PyJWT bounds**: Raise to `>=2.10.1` in `docker/constraints-ai.txt` and `apps/services/requirements.txt`
3. **Audit dual-driver services**: Verify yolo26-vision-service, logistics-service, field-intelligence intentionally use both asyncpg and psycopg2
4. **Fix inventory-service Helm**: Update `appVersion` and `image.tag` from `15.3.2` to `16.0.0`
5. **Pin Kong version in Helm**: Change from `kong:3.4` to `kong:3.4.2` to match docker-compose
6. **Align Qdrant versions**: Upgrade docker-compose from `v1.7.4` to `v1.10.1` or downgrade Helm

### Phase 2: High Priority (This Sprint)

4. **Bulk update nats-py**: `==2.13.1` -> `==2.14.0` across 50 services
5. **Bulk update python-dotenv**: `==1.2.1` -> `==1.2.2` across 40 services
6. **Add bcrypt/argon2-cffi** to `constraints.txt`

### Phase 3: Medium Priority (Next Sprint)

7. **Update 9 services**: pydantic-settings `==2.12.0` -> `==2.13.1`
8. **Update 8 services**: uvicorn `==0.40.0` -> `==0.41.0`
9. **Update 6 services**: alembic `==1.18.3` -> `==1.18.4`
10. **Update 6 services**: psycopg2-binary `==2.9.9` -> `==2.9.11`
11. **Update 2 services**: geospatial libs to match constraints
12. **Fix CI workflows**: Standardize Python 3.12 -> 3.11 in 5 workflows
13. **Standardize structlog**: Choose `==24.4.0` or `>=24.4.0,<25.0.0`

### Phase 4: Low Priority (Backlog)

14. Standardize ioredis floor version to `^5.4.2`
15. Consolidate duplicate Flutter pubspec.yaml
16. Fix Helm appVersion mismatch
17. Standardize pytest version spec to `==8.4.2`
18. Add `esModuleInterop: true` to 5 NestJS services missing it
19. Migrate root `.eslintrc.base.json` to flat config or remove it
20. Align `@sahool/code-review-agent` version to `16.0.0`
21. Convert `file:` protocol refs to workspace resolution for nestjs-auth, field-shared

---

_Generated by 17 parallel dependency analysis agents_
_Analysis covered: constraints.txt, docker/constraints-ai.txt, 59 requirements.txt, 25+ package.json, 3 pubspec.yaml, 53 CI workflows, 32 Helm charts, service-ports.ts_
