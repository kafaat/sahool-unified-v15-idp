# SAHOOL Documentation Gap Analysis Report

**Date:** 2026-03-10
**Scope:** Full platform documentation, dependency, and governance review
**Agents Used:** 15+ parallel analysis agents

---

## Executive Summary

| Category | Status | Issues Found |
|----------|--------|-------------|
| Dependency Completeness | WARNING | 4 missing packages (3 fixed, 1 added) |
| Governance Registry | OK | All 70 active services registered; 14 deprecated properly archived |
| Deprecated References | HIGH | 10 deprecated services referenced in CI/code |
| Services-Docs Coverage | MEDIUM | 5 stale docs, 1 missing doc |
| Shared Module Docs | MEDIUM | 16 modules without README, 13 missing from CLAUDE.md |
| Documentation Structure | LOW | Layer mismatches in SERVICES_MAP/CLAUDE.md |
| NATS Event Architecture | WARNING | 272 defined, only 7 published (2.6%); 3 fragmented sources |
| Knowledge Base | GOOD | 91 docs, 100% bilingual; 9 module topics undocumented |
| Port Conflicts | OK | No conflicts; 3 code-contract mismatches |
| Dockerfiles | OK | Only `migrations` missing (expected) |

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
- `vllm-deepseek` (port 8270) not mentioned in CLAUDE.md

### 6.3 `yield-prediction` Status
- Deprecated service still has an active directory at `apps/services/yield-prediction/`
- Listed as regular Decision layer service in SERVICES_MAP.md

---

## 7. NATS Event Architecture (WARNING)

### 7.1 Coverage Gap
- **272 event subjects defined** in `shared/events/subjects.py`
- **Only 7 events actually published** in production code (2.6% coverage)
- Most definitions are aspirational/planned, not yet implemented

### 7.2 Fragmented Governance (3 separate sources)

| Source | Events | Purpose |
|--------|--------|---------|
| `shared/events/subjects.py` | 272 | Python constants |
| `governance/events/catalog.yaml` | 22 | YAML catalog |
| `governance/events/events-registry.yaml` | 16 | YAML registry |

Overlap between governance files: **only 3 events** (14% alignment):
`field.created`, `field.updated`, `weather.forecast_updated`

### 7.3 Undefined Event Published
- `sahool.irrigation.hmc` is published in `shared/irrigation/integration.py` but has no constant in `subjects.py`

### 7.4 Active Events (7 total)

| Event | Publisher |
|-------|-----------|
| `sahool.field.observation.ingested.v1` | ndvi-processor |
| `sahool.inventory.alert` | inventory-service |
| `sahool.satellite.ndvi.computed` | ndvi-processor |
| `sahool.terrain.leveling_recommended` | leveling-optimizer-service |
| `sahool.traceability.harvest_recorded` | traceability-service |
| `sahool.vision.pest_detected` | pest-detection-service |
| `sahool.irrigation.hmc` | shared/irrigation |

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

---

## Recommended Actions (Priority Order)

### P0 - Critical (Runtime Impact)
1. ~~Add `a2a` to `ai-advisor/requirements.txt`~~ ✅ FIXED
2. ~~Add `torch` to `yolo26-vision-service/requirements.txt`~~ ✅ FIXED
3. ~~Add `asyncpg` to `irrigation-smart/requirements.txt`~~ ✅ FIXED
4. Update deprecated service references in active code (7 files)
5. Remove dead code: `inventory-service` prisma files, `field-management-service` rotation_models.py

### P1 - High (CI/CD Impact)
4. Clean deprecated service references from 7 CI workflow files

### P2 - Medium (Architecture/Documentation)
5. Consolidate NATS event governance into single source of truth
6. Add `sahool.irrigation.hmc` to `shared/events/subjects.py`
7. Add README.md to 16 undocumented shared modules
8. Add 13 missing modules to CLAUDE.md shared module listing
9. Add documentation for `vllm-deepseek` service
10. Archive/mark stale docs in services-docs

### P3 - Low (Documentation Alignment)
11. Fix event architecture layer mismatches in SERVICES_MAP.md and CLAUDE.md
12. Correct phantom port for `agro-rules` (NATS worker, no HTTP port)
13. Audit 266 unused NATS event definitions - archive or implement
14. Add `task-service` (8103) and `astronomical-calendar` (8111) to `service-ports.ts`
15. Fix `ussd-gateway` main.py to use `PORT` env var

---

_Generated by automated documentation gap analysis_
