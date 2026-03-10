# SAHOOL Documentation Gap Analysis Report

**Date:** 2026-03-10
**Scope:** Full platform documentation, dependency, and governance review
**Agents Used:** 15+ parallel analysis agents

---

## Executive Summary

| Category | Status | Issues Found |
|----------|--------|-------------|
| Dependency Completeness | ✅ FIXED | 4 missing packages all fixed |
| Governance Registry | OK | All 70 active services registered; 14 deprecated properly archived |
| Deprecated References | ✅ FIXED | All active code/test/frontend refs updated; CI docs updated |
| Services-Docs Coverage | MEDIUM | 5 stale docs, 1 missing doc |
| Shared Module Docs | MEDIUM | 16 modules without README, 13 missing from CLAUDE.md |
| Documentation Structure | ✅ FIXED | Layer mismatches corrected in SERVICES_MAP.md |
| NATS Event Architecture | WARNING | 216 defined, ~35-40 published (18%); 10+ hardcoded subjects; 3 fragmented sources |
| Knowledge Base | GOOD | 91 docs, 100% bilingual; 9 module topics undocumented |
| Port Conflicts | OK | No conflicts; 3 code-contract mismatches |
| Dockerfiles | OK | Only `migrations` missing (expected) |
| CI/CD Action Versions | ✅ FIXED | 82 non-existent action versions all fixed |

---

## 1. Missing Dependencies (HIGH)

### 1.1 ai-advisor: Missing `a2a` package
- **File:** `apps/services/ai-advisor/src/main.py:93`
- **Import:** `from a2a.server import create_a2a_router`
- **Fix:** Add `a2a>=0.1.0` to `apps/services/ai-advisor/requirements.txt`

### 1.2 yolo26-vision-service: Missing `torch` in requirements.txt
- **File:** `apps/services/yolo26-vision-service/src/main.py:17`
- **Import:** `import torch`
- **Note:** torch is installed via Dockerfile (CUDA variant) but not declared in requirements.txt
- **Fix:** Add `torch>=2.2.0,<2.7.0` to requirements.txt

### 1.3 vegetation-analysis-service: `structlog` (FIXED)
- Previously missing, fixed in this session.

### 1.4 irrigation-smart: Missing `asyncpg` (FIXED)
- **File:** `apps/services/irrigation-smart/src/database_utils.py:335`
- **Import:** `import asyncpg` (inside function, guarded by try/except)
- **Note:** Database functionality silently broken without it
- **Fix:** Added `asyncpg>=0.30.0,<1.0.0` to requirements.txt

### 1.5 Dead Code Dependencies (Not Runtime Risk)
The following services have imports to missing packages, but the importing files are **dead code** (not imported by `main.py`):
- `inventory-service`: `prisma` imported in `inventory_service.py`/`stock_manager.py` (unused alternative to SQLAlchemy implementation)
- `field-management-service`: `sqlalchemy` imported in `rotation_models.py` (Node.js service, Python file is dead code)

### 1.6 Optional Dependencies (Guarded by try/except)
These are missing but won't crash services (features silently disabled):
- `code-fix-agent`: `jedi`, `pyflakes` (LSP features disabled)
- `ai-agents-core`: `onnxruntime`, `safetensors`, `torch`, `torchvision` (disease CNN model disabled)
- `ground-vision-service`: `aiohttp`, `ultralytics` (MLLM reasoning and YOLO classification disabled)
- `vegetation-analysis-service`: `eolearn`, `s2cloudless`, `sentinelhub` (Earth observation features disabled)

---

## 2. Governance Registry (OK)

After thorough analysis, `governance/services.yaml` is **accurate and well-maintained**:

- **70/70 active services** properly registered with correct ports
- **14 deprecated services** correctly archived with replacement mappings
- **0 port conflicts** detected across all services
- Sub-module IDs (e.g., `phenology`, `biomass`) are internal sub-components of larger services, not standalone services - this is by design

Initial automated grep suggested mismatches, but deep analysis confirmed the governance YAML uses nested structures that map correctly to actual services.

---

## 3. Deprecated Service References (HIGH)

### 3.1 Active Source Code (Runtime Risk)

| File | Deprecated Reference | Should Be |
|------|---------------------|-----------|
| `apps/services/alert-service/src/main.py:220` | `ndvi-engine` | `vegetation-analysis-service` |
| `apps/services/llm-orchestrator-service/src/agents/registry.py:204-207` | `yield-engine` | `yield-prediction-service` |
| `apps/services/llm-orchestrator-service/src/agents/routing_rules.py:234,261` | `yield-engine` | `yield-prediction-service` |
| `apps/services/shared/contracts/actions/factory.py:271,379` | `crop-health-ai` | `crop-intelligence-service` |
| `apps/services/shared/globalgap/integrations/fertilizer_integration.py` | `fertilizer-advisor` | `advisory-service` |
| `apps/services/shared/globalgap/integrations/crop_health_integration.py` | `crop-health-ai` | `crop-intelligence-service` |
| `apps/services/field-intelligence/src/models/events.py:69` | `ndvi-engine` | `vegetation-analysis-service` |

### 3.2 Frontend & TypeScript Contracts (Runtime Risk)

| File | Deprecated Reference | Should Be |
|------|---------------------|-----------|
| `apps/services/task-service/src/ndvi_client.py:27` | `http://ndvi-engine:8107` | `http://vegetation-analysis-service:8090` |
| `apps/web/src/lib/api/client.ts:797,804,815` | `/api/v1/agro-advisor/*` (3 methods) | `advisory-service` endpoints |
| `apps/web/src/lib/api/client.ts:856,893,901` | `/api/v1/field-chat/*` (3 methods) | `chat-service` endpoints |
| `apps/admin/src/lib/api-gateway/index.ts:366-373` | `field-chat` service config | `chat-service` config |
| `packages/shared-utils/src/api/kong-client.ts:242-250` | `community-chat` in KONG_SERVICES | Remove or redirect to `chat-service` |
| `packages/shared-utils/src/api/kong-client.ts:273-281` | `yield-engine` in KONG_SERVICES | `yield-prediction-service` |

### 3.3 Test Assertions (Test Risk)

| File | Issue |
|------|-------|
| `tests/integration/test_kong_routes.py:94` | REQUIRED_SERVICES includes `ndvi-engine`, `crop-health-ai`, `satellite-service`, `weather-core` |
| `tests/integration/test_field_workflow.py:179` | Hardcoded `http://localhost:8107` (ndvi-engine port) |
| `tests/integration/test_user_journey.py:548` | Hardcoded `http://localhost:8107` (ndvi-engine port) |

### 3.4 CI/CD Workflows (Build Risk)

10 deprecated services still referenced across workflow files:

| Deprecated Service | Workflows |
|-------------------|-----------|
| `satellite-service` | ci.yml, cd-staging.yml, container-tests.yml, docker-image.yml |
| `weather-advanced` | ci.yml, cd-staging.yml, container-tests.yml, docker-image.yml |
| `crop-health-ai` | cd-staging.yml, container-tests.yml, docker-image.yml |
| `fertilizer-advisor` | ci.yml, container-tests.yml, docker-image.yml |
| `agro-advisor` | agent-evaluation.yml, cd-staging.yml, container-tests.yml, release.yml |
| `ndvi-engine` | cd-staging.yml, release.yml |
| `weather-core` | cd-staging.yml, container-tests.yml, release.yml, security.yml |
| `community-chat` | container-tests.yml |
| `field-chat` | container-tests.yml, release.yml |
| `yield-engine` | ci.yml, cd-staging.yml, container-tests.yml, docker-image.yml, release.yml |

---

## 4. Services-Docs Gaps (MEDIUM)

### 4.1 Stale Docs (deprecated services still documented)
- `apps/services-docs/agro-advisor.md`
- `apps/services-docs/community-chat.md`
- `apps/services-docs/field-chat.md`
- `apps/services-docs/weather-core.md`
- `apps/services-docs/recommendations-and-fixes.md`

### 4.2 Missing Docs
- `vllm-deepseek` - Active service with no documentation

---

## 5. Shared Module Documentation (MEDIUM)

**Total shared modules:** 78 (all have `__init__.py` with docstrings)

### 5.1 Modules Without README.md (16 modules)
- `shared/dashboard/`
- `shared/financial_reports/`
- `shared/geospatial_metadata/`
- `shared/iot_dashboard/`
- `shared/marketplace_enhanced/`
- `shared/mobile_config/`
- `shared/notification_routing/`
- `shared/pivot_management/`
- `shared/regional/`
- `shared/vra_maps/`
- `shared/calibration/`
- `shared/digital_twin/`
- `shared/drift_detection/`
- `shared/process_models/`
- `shared/stability/`

### 5.2 Modules Not Documented in CLAUDE.md (13 modules)
- `calibration`, `digital_twin`, `drift_detection`
- `geospatial_metadata`, `iot_dashboard`, `marketplace_enhanced`
- `mobile_config`, `notification_routing`, `pivot_management`
- `process_models`, `regional`, `stability`, `vra_maps`

---

## 6. Documentation Accuracy (LOW)

### 6.1 Event Architecture Layer Mismatches

| Service | CLAUDE.md/SERVICES_MAP | governance/services.yaml |
|---------|----------------------|--------------------------|
| `vegetation-analysis-service` | Acquisition | Intelligence |
| `ground-vision-service` | Intelligence | Acquisition |
| `agro-rules` | Decision | Intelligence |
| `hydrology-service` | Decision | Intelligence |

### 6.2 Port Documentation Issues
- `agro-rules` listed with port 8151 but has no HTTP server (NATS worker only)
- `code-review-agent` listed with port 8145 in CLAUDE.md but `port: None` in governance
- `demo-data` listed with port 8261 in CLAUDE.md but `port: None` in governance
- `vllm-deepseek` (port 8270) not mentioned in CLAUDE.md or SERVICES_MAP.md

### 6.3 `yield-prediction` Status
- Deprecated service still has an active directory at `apps/services/yield-prediction/`
- Listed as regular Decision layer service in SERVICES_MAP.md
- Should be archived to `archive/deprecated-services/`

### 6.4 Helm Chart Stale References
- `helm/sahool/templates/deployment-field-ops.yaml` - full deployment template for archived `field-ops` service
- Multiple Helm values files (`values-production.yaml`, `values-staging.yaml`, `values.generated.yaml`) reference deprecated services

---

## 7. NATS Event Architecture (WARNING)

### 7.1 Coverage Gap (Updated after deep audit)
- **216 event constants defined** in `shared/events/subjects.py` (+ specialized files)
- **~35-40 events actively published** across 8+ services (~18% coverage)
- **~60-70 events subscribed** but not published (consumer-side only)
- **~80-90 events completely unused** (~40% aspirational/planned)
- Key active publishers: yolo26-vision-service (8), copilot-api (7), globalgap-compliance (7), field-management-service (4), terrain services (3)

### 7.2 Fragmented Governance (3 separate sources)

| Source | Events | Purpose |
|--------|--------|---------|
| `shared/events/subjects.py` | 216 | Python constants |
| `governance/events/catalog.yaml` | 22 | YAML catalog |
| `governance/events/events-registry.yaml` | 16 | YAML registry |

Overlap between governance files: **only 3 events** (14% alignment):
`field.created`, `field.updated`, `weather.forecast_updated`

### 7.3 Hardcoded Event Subjects (10+ services)
- `sahool.irrigation.hmc` - ✅ FIXED (constant added to subjects.py)
- `sahool.field.profitability.analyzed` - hardcoded in field-management-service, **no constant exists**
- `sahool.crop.disease_detected` / `sahool.crop.health_assessed` - hardcoded in crop-intelligence-service
- `sahool.satellite.ndvi.computed` / `sahool.field.observation.ingested.v1` - hardcoded in ndvi-processor
- `sahool.inventory.alert` - hardcoded in inventory-service
- `sahool.terrain.leveling_recommended` - hardcoded in leveling-optimizer-service
- Tenant-scoped patterns hardcoded in edge-orchestrator and ground-vision services

### 7.4 Top Active Publishers

| Service | Events Published |
|---------|-----------------|
| yolo26-vision-service | 8 (pest/disease/weed detection, analysis lifecycle, critical alerts) |
| copilot-api | 7 (chat lifecycle, tool execution, prompt injection, rate limit) |
| globalgap-compliance | 7 (compliance updates, audit, non-conformity, certificates) |
| field-management-service | 4 (field CRUD + profitability) |
| terrain services | 3 (leveling, analysis start/complete) |
| crop-intelligence-service | 2 (disease detected, health assessed) |
| ndvi-processor | 2 (NDVI computed, observation ingested) |
| inventory-service | 1 (inventory alert) |
| shared/irrigation | 1 (HMC integration) |

---

## 8. Knowledge Base (GOOD with gaps)

**91 documents, 843.6 KB, 100% bilingual (EN/AR), 13 subdirectories, 0 stub files.**

### 8.1 Strengths
- 20 crop varieties with complete cultivation guides
- Comprehensive irrigation (11 docs), fertilization (8), soils (7), weather (6)
- 15 AI/smart-agriculture documents (233 KB)
- 6 remote sensing docs including NDVI, LAI, hyperspectral

### 8.2 Knowledge Gaps (9 undocumented modules)

| Missing Topic | Relevant Services |
|---------------|-------------------|
| Terrain/DEM analysis | terrain-core-service, hydrology-service, leveling-optimizer-service |
| Crop rotation planning | crop-rotation module, agro-rules |
| Field boundaries/geospatial | field-boundaries module, field-management-service |
| Geofencing configuration | geofencing module, alert-service |
| Post-harvest quality | harvest-quality module, traceability-service |
| Soil sensor/IoT integration | soil_sensors module, iot-service |
| Pesticide compliance (PHI/REI) | pesticide_compliance module, advisory-service |
| Equipment maintenance | equipment_maintenance module, equipment-service |
| Drone integration guides | drone-integration module, drone-service |

---

## 9. Infrastructure (OK)

- **Port Conflicts:** None detected across 65 services
- **Dockerfiles:** All services have Dockerfiles except `migrations` (expected - utility only)
- **CI Short SHA:** Fixed in this session (checkov-action)

### 9.1 Port Contract Mismatches (3)

| Service | Port | Issue |
|---------|------|-------|
| `task-service` | 8103 | Defined in code but **missing from** `service-ports.ts` |
| `astronomical-calendar` | 8111 | Defined in code but **missing from** `service-ports.ts` |
| `ussd-gateway` | 8183 | In contracts and Dockerfile, but `main.py` doesn't use `PORT` env var |

## 10. CI/CD Workflow Action Versions (CRITICAL)

### 10.1 Non-Existent Action Versions (FIXED)

| Action | Wrong Version | Correct Version | Occurrences | Files |
|--------|--------------|-----------------|-------------|-------|
| `actions/upload-artifact` | `@v7` | `@v4` | 59 | 26 workflows |
| `actions/download-artifact` | `@v8` | `@v4` | 22 | 12 workflows |
| `actions/checkout` | `@v4` | `@v6` | 1 | dockerfile-lint.yml |

All 82 occurrences fixed in this session.

### 10.2 Version Inconsistency (FIXED)
- `anchore/sbom-action@v0` in ci-ai-rag-security.yml standardized to `@v0.18.0`

### 10.3 Unmaintained Action (Remaining)
- `8398a7/action-slack@v3` used in 4 workflows (cd-production, cd-staging, ci, security)
- **Recommendation:** Replace with `slackapi/slack-send-action@v2` or GitHub native notifications

---

## Recommended Actions (Priority Order)

### P0 - Critical (Runtime Impact) — ALL FIXED ✅
1. ~~Add `a2a` to `ai-advisor/requirements.txt`~~ ✅
2. ~~Add `torch` to `yolo26-vision-service/requirements.txt`~~ ✅
3. ~~Add `asyncpg` to `irrigation-smart/requirements.txt`~~ ✅
4. ~~Fix `upload-artifact@v7` → `@v4` (59 occurrences in 26 workflows)~~ ✅
5. ~~Fix `download-artifact@v8` → `@v4` (22 occurrences in 12 workflows)~~ ✅
6. ~~Fix `checkout@v4` → `@v6` in dockerfile-lint.yml~~ ✅
7. ~~Standardize `sbom-action` to `@v0.18.0`~~ ✅
8. ~~Update deprecated service references in active source code (7 files)~~ ✅
9. ~~Update deprecated service references in frontend/TypeScript (3 files)~~ ✅
10. ~~Update deprecated service references in test files (3 files)~~ ✅
11. ~~Remove dead code: `inventory-service` prisma files, `field-management-service` rotation_models.py~~ ✅

### P1 - High (CI/CD Impact) — MOSTLY FIXED
12. ~~Clean deprecated service references from CI workflow documentation~~ ✅
13. Replace unmaintained `8398a7/action-slack@v3` in 4 workflows

### P2 - Medium (Architecture/Documentation) — MOSTLY FIXED
14. ~~Add `sahool.irrigation.hmc` to `shared/events/subjects.py`~~ ✅
15. ~~Fix event architecture layer mismatches in SERVICES_MAP.md~~ ✅
16. ~~Mark stale docs in services-docs with deprecation notices~~ ✅
17. ~~Add `vllm-deepseek` to SERVICES_MAP.md~~ ✅
18. ~~Fix `ussd-gateway` main.py to use `PORT` env var~~ ✅
19. Consolidate NATS event governance into single source of truth
20. Standardize 10+ services using hardcoded NATS subjects to use constants
21. Add README.md to 16 undocumented shared modules
22. Add 13 missing modules to CLAUDE.md shared module listing

### P3 - Low (Documentation Alignment)
23. Archive ~80-90 unused NATS event definitions or document as planned
24. Add `sahool.field.profitability.analyzed` constant to subjects.py
25. Remove Helm deployment template for archived `field-ops` service
26. Archive `yield-prediction` directory to `archive/deprecated-services/`

---

_Generated by automated documentation gap analysis_
