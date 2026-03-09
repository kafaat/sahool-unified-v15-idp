# Dependency Version Conflict Analysis Report

**Date**: 2026-03-09
**Platform**: SAHOOL v16.0.0
**Analysis Method**: 18 parallel agents covering all dependency layers (including AI/ML deep analysis)
**Scope**: 72 active services, 24 npm packages, 3 Flutter apps, 32 Helm charts, 53 CI workflows

---

## Executive Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 11 | Version mismatches, broken OTel exports, dev/prod divergence, torch/torchvision contradictions |
| **HIGH** | 10 | Version drift, skipped constraints, strict-markers, langchain/sentence-transformers splits |
| **MEDIUM** | 23 | Patch-level mismatches, module conflicts, test config, openai bounds, opencv variant clash |
| **LOW** | 18 | Minor inconsistencies, duplicates, missing upper bounds, non-blocking |
| **INFO** | 8 | Observations and recommendations |

**Total conflicts found: 70 across 18 analysis categories (including AI/ML libraries)**

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

### CRITICAL: field-management-service Uses Python 3.12

`field-management-service/Dockerfile.python` uses `python:3.12-slim` instead of the standard `python:3.11-slim-bookworm`. Also uses **UID 1001** instead of the standard **UID 1000**. This is a triple deviation (Python version, Debian variant, UID).

### HIGH: 6 Services Skip constraints.txt in Docker Builds

These services install pip packages without `-c constraints.txt`, enabling version drift:
- ai-advisor, ai-agents-service, crop-intelligence-service, field-intelligence, llm-orchestrator-service, vllm-deepseek

(yolo26-vision-service properly uses `constraints-ai.txt` instead)

### MEDIUM: Pip Mirror Order Contradicts Documentation

~37 services use Aliyun-first fallback while ~12 use PyPI-first. Documentation recommends PyPI-first (Pattern A).

### LOW: Alpine vs Bookworm for Node.js Frontends

`apps/admin` and `apps/web` use `node:20-alpine` (musl libc) while all backend NestJS services use `node:20-bookworm-slim` (glibc). Native module compatibility risk.

### INFO: Other Base Images Consistent

All other Python services use `python:${PYTHON_VERSION}-slim-bookworm` (default 3.11). CUDA services consistent at `12.1.1-cudnn8-runtime-ubuntu22.04`.

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

### INFO: No Port Conflicts

All 67 active services have consistent port assignments across `service-ports.ts`, `docker-compose.yml`, `governance/services.yaml`, and service code. Zero duplicates, zero mismatches.

3 services (agro-rules, code-review-agent, demo-data) are absent from `service-ports.ts` but use unique ports that don't collide.

---

## 9. Monitoring & Observability Libraries

### CRITICAL: OpenTelemetry Exporter Version Ranges Broken

`shared/observability/requirements.txt` specifies `opentelemetry-exporter-otlp-proto-grpc>=1.39.1` — but OTLP exporter packages follow 0.x versioning. Version `1.39.1` does not exist. These lines will cause pip resolution failures.

Also: `opentelemetry-exporter-jaeger>=1.39.1` — Jaeger exporter was deprecated, last published at 1.21.0.

### HIGH: OpenTelemetry API/SDK Pin Conflict

| Location | Version |
|----------|---------|
| `constraints.txt` | `==1.40.0` / `==0.61b0` |
| `apps/services/requirements.txt` | `==1.39.1` / `==0.60b1` |
| `idp/templates/.../requirements.txt` | `==1.39.1` / `==0.60b1` |

Hard-pinned `==1.39.1` vs constraint `==1.40.0` — pip will **fail** when used together. IDP template means every new scaffolded service inherits this conflict.

### MEDIUM: structlog 7 Different Specs (57 services)

33 services lack an upper bound on structlog. Without constraints, they could install 25.x (breaking major version).

### MEDIUM: prometheus-client 5 Different Specs (20 services)

2 services allow `>=0.19.0`, while constraint pins `==0.24.1`.

---

## 10. Testing Framework Conflicts

### CRITICAL: Playwright Version Gap

| Location | Version |
|----------|---------|
| `apps/web/package.json` | `^1.57.0` |
| `apps/web/e2e/package.json` | `^1.48.0` |

The e2e subdirectory could install Playwright 1.48-1.56, missing APIs assumed by the config.

### HIGH: --strict-markers + Undeclared Markers

Root `pyproject.toml` uses `--strict-markers` but 7 service-specific markers (`redis`, `agent`, `coordinator`, `specialist`, `edge`, `mock`, `event_flow`) are not registered. Root-level test collection will **reject** tests bearing these markers.

### MEDIUM: pytest 7.x vs 8.x Split

`copilot-api`, `globalgap-compliance`, `kernel/field_ops`, and `sahool-eo` allow pytest 7.x while the canonical pin is 8.4.2.

### MEDIUM: asyncio_default_fixture_loop_scope Mismatch

`edge-orchestrator` and `crm-service` set `function` scope locally, but root lacks this setting. Running their async tests from root uses `session` scope — causing potential event loop contamination.

### MEDIUM: 29 Python Services Lack pytest

29 services have no pytest in `requirements.txt` — cannot run tests in isolated Docker builds.

### LOW: fail_under Silently Ignored

`edge-orchestrator-service` expects 60% coverage but root config sets `fail_under = 0`. CI from root never enforces it.

---

## 11. pyproject.toml vs constraints.txt

### INFO: Fully Compatible

All versions in `pyproject.toml` are compatible with `constraints.txt`. No conflicts found.

---

## 12. AI/ML Library Conflicts

### CRITICAL: PyTorch Version Contradiction

| Source | Version | Notes |
|--------|---------|-------|
| `docker/constraints-ai.txt` | `==2.10.0` | Locked for CUDA 12.1 |
| `yolo26-vision-service/Dockerfile` | `==2.2.0` | Hardcoded in Dockerfile |
| `copilot-api/requirements.txt` | `>=2.2.0,<2.7.0` | Range incompatible with 2.10.0 |

**Risk**: Three mutually contradictory specs. `torch==2.10.0` satisfies neither `==2.2.0` (yolo26) nor `<2.7.0` (copilot-api). Services using `constraints-ai.txt` will get 2.10.0, breaking copilot-api.

### CRITICAL: torchvision Version Contradiction

| Source | Version |
|--------|---------|
| `docker/constraints-ai.txt` | `==0.25.0` |
| `yolo26-vision-service/Dockerfile` | `==0.17.0` |

**Risk**: `torchvision==0.17.0` pairs with `torch==2.2.0`, and `torchvision==0.25.0` pairs with `torch==2.10.0`. The yolo26 Dockerfile is internally consistent but disagrees with constraints-ai.txt.

### HIGH: langchain Ecosystem Version Split

| Library | constraints-ai.txt | ai-advisor/requirements.txt |
|---------|--------------------|-----------------------------|
| langchain | `>=0.3.26,<0.4.0` | `>=0.3.26` (no upper bound) |
| langchain-core | `==0.3.83` | `==0.3.81` |
| langchain-community | `==0.4.1` | `==0.3.27` |
| langchain-anthropic | `==0.3.22` | `==0.3.1` |

**Risk**: ai-advisor pins older versions across the entire langchain stack. If constraints-ai.txt is applied, pip resolution will **fail** on conflicting exact pins.

### HIGH: sentence-transformers Pin Mismatch

| Source | Version |
|--------|---------|
| `docker/constraints-ai.txt` | `==5.2.3` |
| `ai-advisor/requirements.txt` | `==5.2.2` |
| `copilot-api/requirements.txt` | `>=2.2.0,<6.0.0` |

**Risk**: Exact pin conflict between constraints (5.2.3) and ai-advisor (5.2.2).

### MEDIUM: openai Upper Bound Divergence

| Source | Version |
|--------|---------|
| `docker/constraints-ai.txt` | `>=1.0.0,<2.0.0` |
| `llm-orchestrator-service/requirements.txt` | `>=1.0.0,<3.0.0` |
| `ai-advisor/requirements.txt` | `>=1.0.0` (no upper bound) |
| `ground-vision-service/requirements.txt` | `>=1.55.0` (no upper bound) |

**Risk**: llm-orchestrator allows `<3.0.0` while constraints restrict to `<2.0.0`. Services without upper bounds could install breaking major versions.

### MEDIUM: opencv-python vs opencv-python-headless

| Source | Package | Version |
|--------|---------|---------|
| `docker/constraints-ai.txt` | opencv-python-headless | `>=4.9.0,<5.0.0` |
| `yolo26-vision-service` | opencv-python-headless | `>=4.8.0,<5.0.0` |
| `ground-vision-service` | opencv-python-headless | `>=4.10.0` (no upper bound) |
| `ai-agents-core` | **opencv-python** (GUI) | `>=4.8.0` (no upper bound) |

**Risk**: ai-agents-core uses `opencv-python` (with GUI/X11 deps) while all others use `opencv-python-headless`. These two packages **conflict** when co-installed. ground-vision-service has no upper bound.

### LOW: Missing Upper Bounds (Multiple AI Services)

| Service | Package | Version |
|---------|---------|---------|
| ai-advisor | openai, langchain | No upper bound |
| ground-vision-service | opencv, openai, anthropic | No upper bounds |
| ground-vision-service | anthropic | `>=0.40.0` (constraints require `>=0.41.0`) |

### INFO: Constraints Gap — No AI/ML Governance in Main constraints.txt

The main `constraints.txt` has **no entries** for: torch, torchvision, ultralytics, opencv-python-headless, transformers, sentence-transformers, langchain, crewai, openai, anthropic, or onnxruntime. AI/ML version governance exists only in `docker/constraints-ai.txt`, leaving non-AI services that transitively pull these packages ungoverned.

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
| OTel exporter broken versions | 5 packages | shared/observability |
| OTel API/SDK pin conflict | 2 files | services + IDP template |
| torch version contradiction | 3 specs | constraints-ai, yolo26, copilot-api |
| torchvision contradiction | 2 specs | constraints-ai, yolo26 |
| langchain ecosystem split | 4 libs | constraints-ai vs ai-advisor |
| sentence-transformers pin | 2 specs | constraints-ai vs ai-advisor |
| openai upper bound divergence | 4 specs | constraints-ai, llm-orch, ai-advisor, ground-vision |
| opencv-python vs headless | 1 clash | ai-agents-core vs all others |
| AI/ML libs missing from constraints.txt | 11 packages | Main constraints gap |
| Playwright version gap | 1 conflict | apps/web vs e2e |
| --strict-markers undeclared | 7 markers | 3 service pytest configs |
| asyncio loop scope mismatch | 2 configs | edge-orchestrator, crm |
| pytest 7.x vs 8.x | 4 services | copilot-api, globalgap, kernel, eo |
| Services lacking pytest | 29 services | Cannot test in Docker |
| Docker Python 3.12 outlier | 1 service | field-management-service |
| 6 services skip constraints | 6 services | ai-advisor, ai-agents, etc. |

---

## Recommended Action Plan

### Phase 1: Critical (Immediate)

1. **Update `constraints.txt`**: Set `tortoise-orm==1.1.6` to match active services
2. **Fix PyJWT bounds**: Raise to `>=2.10.1` in `docker/constraints-ai.txt` and `apps/services/requirements.txt`
3. **Audit dual-driver services**: Verify yolo26-vision-service, logistics-service, field-intelligence intentionally use both asyncpg and psycopg2
4. **Fix inventory-service Helm**: Update `appVersion` and `image.tag` from `15.3.2` to `16.0.0`
5. **Pin Kong version in Helm**: Change from `kong:3.4` to `kong:3.4.2` to match docker-compose
6. **Align Qdrant versions**: Upgrade docker-compose from `v1.7.4` to `v1.10.1` or downgrade Helm
7. **Fix OTel exporter versions**: Change `>=1.39.1` to `>=0.61b0,<1.0.0` in `shared/observability/requirements.txt`; remove deprecated `opentelemetry-exporter-jaeger`
8. **Update OTel pins**: Bump `apps/services/requirements.txt` and IDP template from `1.39.1`/`0.60b1` to `1.40.0`/`0.61b0`
9. **Fix Playwright gap**: Update `apps/web/e2e/package.json` from `^1.48.0` to `^1.57.0`
10. **Resolve torch/torchvision contradiction**: Either update yolo26-vision-service Dockerfile to use `torch==2.10.0`/`torchvision==0.25.0` (requires YOLO compatibility testing) or create a separate `constraints-vision.txt` for yolo26. Update copilot-api upper bound from `<2.7.0` to `<3.0.0`
11. **Fix langchain pin conflicts**: Update ai-advisor to match constraints-ai.txt: langchain-core `==0.3.83`, langchain-community `==0.4.1`, langchain-anthropic `==0.3.22`

### Phase 2: High Priority (This Sprint)

12. **Bulk update nats-py**: `==2.13.1` -> `==2.14.0` across 50 services
13. **Bulk update python-dotenv**: `==1.2.1` -> `==1.2.2` across 40 services
14. **Add bcrypt/argon2-cffi** to `constraints.txt`
15. **Register undeclared pytest markers** in root `pyproject.toml`: `redis`, `agent`, `coordinator`, `specialist`, `edge`, `mock`, `event_flow`
16. **Fix sentence-transformers pin**: Update ai-advisor from `==5.2.2` to `==5.2.3` to match constraints-ai.txt
17. **Standardize openai upper bounds**: Set `>=1.0.0,<2.0.0` in llm-orchestrator-service, ai-advisor, ground-vision-service
18. **Fix opencv-python variant**: Change ai-agents-core from `opencv-python` to `opencv-python-headless`

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
22. Add missing upper bounds to ground-vision-service (opencv, openai, anthropic)
23. Add AI/ML core packages (torch, openai, anthropic, langchain, sentence-transformers) to main `constraints.txt` for transitive governance

---

_Generated by 18 parallel dependency analysis agents_
_Analysis covered: constraints.txt, docker/constraints-ai.txt, 59 requirements.txt, 25+ package.json, 3 pubspec.yaml, 53 CI workflows, 32 Helm charts, service-ports.ts, AI/ML library cross-references across Dockerfiles_
