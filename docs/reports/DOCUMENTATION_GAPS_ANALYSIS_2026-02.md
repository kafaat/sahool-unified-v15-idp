# Documentation Gaps Analysis Report

**Date**: 2026-02-25
**Platform Version**: 16.0.0
**Analyzed By**: Automated Documentation Audit
**Scope**: Full platform — services, shared modules, packages, tests, infrastructure, governance

---

## Executive Summary

The SAHOOL platform contains **385+ documentation files** across the codebase. However, significant gaps exist in critical areas. This report identifies **4 critical**, **6 moderate**, and **5 minor** documentation gaps that affect developer onboarding, maintenance, and operational readiness.

### Key Metrics

| Area | Total | Documented | Undocumented | Coverage |
|------|-------|------------|--------------|----------|
| Services (`apps/services/`) | 69 | 67 | 2 | 97% |
| Service Docs (`services-docs/`) | 69 | 34 | 35 | 49% |
| Shared Modules (`shared/`) | 71 | 14 | 57 | 20% |
| Packages (`packages/`) | 24 | 11 | 13 | 46% |
| Test Suites (`tests/`) | 18 | 4 | 14 | 22% |
| ADRs (`docs/adr/`) | 7 | 7 | ~10+ missing | ~40% |

**Overall Documentation Health Score: 45/100**

---

## 1. Critical Gaps (Priority: HIGH)

### 1.1 Shared Modules — 57 of 71 Without README (80% Undocumented)

The `shared/` directory is the backbone of the platform with 65+ Python modules, yet **only 14 modules** have a README.md file. The remaining 57 modules rely solely on `__init__.py` docstrings.

**Most Critical Undocumented Modules:**

| Module | Python Files | Impact | Risk |
|--------|-------------|--------|------|
| `shared/ai/` | 82 | Entire AI/RAG/Auto-Fix engine | Very High |
| `shared/security/` | 15 | RBAC, JWT, policy engine | Very High |
| `shared/libs/` | 24 | Outbox, audit, caching core | High |
| `shared/irrigation/` | 6 | Smart irrigation scheduling | High |
| `shared/mobile_sync/` | 5 | Offline-first sync engine | High |
| `shared/monitoring/` | 7 | Prometheus metrics, SLI/SLO | High |
| `shared/middleware/` | 15 | Rate limiting, CORS, logging (has 5 .md files but no README) | High |
| `shared/llm/` | 8 | LLM provider config & routing | High |
| `shared/terrain/` | 6 | DEM processing, terrain analysis | Medium |
| `shared/nlp/` | 2 | Arabic NLP (AraBERT) | Medium |
| `shared/satellite/` | 2 | Sentinel Hub NDVI integration | Medium |
| `shared/fertilizer_management/` | 5 | Nutrient recommendations | Medium |
| `shared/pest_scouting/` | 5 | Pest identification, IPM | Medium |
| `shared/field_boundaries/` | 5 | Field geometry, geospatial ops | Medium |
| `shared/secrets/` | 4 | HashiCorp Vault integration | Medium |

**Full list of undocumented shared modules (57):**
agents, agri_calendar, ai, audit_trail, batch_operations, calibration, cooperatives, crm, crop_insurance, crop_rotation, db, design-system, digital_twin, drift_detection, drone_integration, edge_cloud, equipment_maintenance, farm_documents, fertilizer_management, field_boundaries, geofencing, harvest_quality, integrations, irrigation, labor_management, learning_marketplace, libs, llm, lowcode, market_prices, ml, ml_irrigation, mobile_sync, monitoring, nlp, notification_preferences, pest_scouting, pesticide_compliance, process_models, python-lib, salinity, satellite, scraping, secrets, security, service_enhancements, smart_agriculture, soil_sensors, soil_testing, stability, templates, terrain, traceability, water_management, weather_alerts, yemen

**Documented shared modules (14):**
a2a, auth, cache, contracts, domain, events, file_validation, globalgap (partial), guardrails, mcp, middleware (partial — no README), observability, telemetry, versioning

### 1.2 Service-Docs — 35 of 69 Services Missing Detailed Documentation

Only **34 services** have detailed documentation in `apps/services-docs/`. The remaining **35 active services** lack a dedicated service documentation file.

**Missing Service Documentation (by category):**

**AI & Agent Services (9 missing):**
| Service | Port | README Lines |
|---------|------|-------------|
| agent-registry | 8160 | 285 |
| ai-agents-core | 8161 | 373 |
| ai-chat-assistant | 8260 | 329 |
| code-fix-agent | 8162 | 147 |
| code-review-agent | 8145 | 212 |
| copilot-api | 8088 | 1,491 |
| knowledge-graph | 8140 | 430 |
| llm-orchestrator-service | 8164 | 152 |

**Vision, Terrain & Edge Services (6 missing):**
| Service | Port | README Lines |
|---------|------|-------------|
| yolo26-vision-service | 8150 | 492 |
| ground-vision-service | 8182 | 147 |
| terrain-core-service | 8185 | 416 |
| hydrology-service | 8165 | 474 |
| leveling-optimizer-service | 8170 | 479 |
| edge-orchestrator-service | 8180 | 689 |

**Decision & Analytics Services (6 missing):**
| Service | Port | README Lines |
|---------|------|-------------|
| crop-growth-model | 3023 | 255 |
| digital-twin-engine | 8253 | 1,033 |
| fertigation-engine | 8252 | 1,015 |
| irrigation-cycle-engine | 8250 | 642 |
| lai-estimation | 3022 | 297 |
| pest-detection-service | 8125 | 298 |

**IoT Services (2 missing):**
| Service | Port | README Lines |
|---------|------|-------------|
| iot-sensor-hub | 8251 | 928 |
| drone-service | 8126 | 319 |

**Business Services (8 missing):**
| Service | Port | README Lines |
|---------|------|-------------|
| audit-service | 8114 | 82 |
| cooperative-service | 8127 | 325 |
| globalgap-compliance | 8128 | 393 |
| logistics-service | 8167 | 179 |
| supply-chain-service | 8230 | 153 |
| traceability-service | 8123 | 349 |
| soil-analysis-service | 8134 | 268 |
| yield-prediction | 3021 | 350 |

**Integration Services (3 missing):**
| Service | Port | README Lines |
|---------|------|-------------|
| ussd-gateway | 8183 | 80 |
| wechat-service | 8133 | 200 |
| whatsapp-bot-service | 8240 | 227 |

**Utility (2 missing):**
| Service | Port | README Lines |
|---------|------|-------------|
| demo-data | 8261 | 42 |
| ndvi-processor | 8118 | 0 (NO README) |

### 1.3 Test Suites — 14 of 18 Without README (78% Undocumented)

Only **4 of 18** test directories have README documentation.

| Test Suite | README | Test Files | Notes |
|------------|--------|------------|-------|
| `tests/unit/` | NO | 165 | Largest test suite, no docs |
| `tests/integration/` | YES | 39 | Documented |
| `tests/e2e/` | NO | 13 | No docs |
| `tests/evaluation/` | YES | 11 | Documented |
| `tests/load/` | YES | 3 | Documented |
| `tests/golden-datasets/` | YES | 1 | Documented |
| `tests/factories/` | NO | 5 | No docs |
| `tests/security/` | NO | 4 | No docs |
| `tests/smoke/` | NO | 4 | No docs |
| `tests/database/` | NO | 3 | No docs |
| `tests/guardrails/` | NO | 3 | No docs |
| `tests/middleware/` | NO | 3 | No docs |
| `tests/simulation/` | NO | 3 | No docs |
| `tests/snapshots/` | NO | 3 | No docs |
| `tests/a2a/` | NO | 2 | No docs |
| `tests/container/` | NO | 2 | No docs |
| `tests/frontend/` | NO | 1 | No docs |
| `tests/utils/` | NO | 4 | No docs |

### 1.4 Packages — 13 of 24 Without README (54% Undocumented)

**Undocumented packages (high impact first):**

| Package | Type | Files | Impact |
|---------|------|-------|--------|
| `shared-types` | npm | 18 .ts | Very High — contract source of truth |
| `shared-ui` | npm | 24 .ts | High — shared UI components |
| `shared-utils` | npm | 10 .ts | High — common utilities |
| `shared-hooks` | npm | 16 .ts | High — shared React hooks |
| `design-system` | npm | 6 .ts | Medium — design system |
| `sahool-eo` | python | 12 .py | Medium — Earth Observation |
| `mock-data` | npm | 7 .ts | Low — test data |
| `tailwind-config` | npm | 1 .ts | Low |
| `typescript-config` | npm | 0 | Low |
| `enterprise` | config | 0 | Low — only docker-compose.yml |
| `professional` | config | 0 | Low — only docker-compose.yml |
| `starter` | config | 0 | Low — only docker-compose.yml |
| `shared` | — | 0 | Low — empty directory |

---

## 2. Moderate Gaps (Priority: MEDIUM)

### 2.1 Architecture Decision Records — Only 7 ADRs for 71 Services

Current ADRs cover only foundational decisions:
- ADR-001: Offline-first architecture
- ADR-002: Riverpod state management
- ADR-003: Drift local database
- ADR-004: Kong API gateway
- ADR-005: NATS event bus
- ADR-006: Circuit breaker
- ADR-007: Redis caching

**Missing ADRs for:**
- PostGIS/geospatial data strategy
- YOLO26 computer vision framework selection
- Flutter mobile framework choice
- HashiCorp Vault secrets management
- Multi-tenancy architecture
- AI model strategy (Ollama, multi-LLM)
- Edge computing architecture (Jetson Orin)
- Event-driven 4-layer architecture design
- Microservice decomposition strategy
- Digital twin approach

**Additional issue:** ADR directories are fragmented — `docs/adr/` (7 ADRs) vs `governance/decisions/` (1 ADR). Should be consolidated.

### 2.2 API Narrative Documentation — Only 5 of 16+ Domains Covered

`docs/api/` has **16 OpenAPI YAML specs** but narrative (human-readable) docs for only **5 domains**:

| Domain | Narrative Doc | OpenAPI Spec |
|--------|--------------|--------------|
| Fields | YES (1,107 lines) | YES |
| Authentication | YES (374 lines) | YES (core-services) |
| AI | YES (381 lines) | YES |
| Weather | YES (294 lines) | YES |
| Sensors | YES (133 lines) | YES (iot-services) |
| Billing | NO | YES |
| Marketplace | NO | YES |
| IoT | NO | YES |
| Vision (YOLO26) | NO | YES |
| Terrain | NO | YES |
| Hydrology | NO | YES |
| Leveling | NO | YES |
| Edge | NO | YES |
| Tasks | NO | YES |
| Analysis | NO | YES |
| Agent | NO | YES |

### 2.3 Knowledge Base — Sparse Agricultural Content

`docs/knowledge-base/` covers only basic topics:

| Category | Documented | Missing |
|----------|-----------|---------|
| Crops | wheat, barley, dates | tomato, cucumber, vegetables, rice, corn |
| Diseases | fungal, pests | bacterial, viral, nutrient deficiencies |
| Irrigation | drip, scheduling | flood, sprinkler, fertigation, salinity |
| Monitoring | remote sensing/AI | soil sensors, weather stations, drone |
| Best Practices | sustainable farming | crop rotation, IPM, organic, post-harvest |

### 2.4 Deprecated Service Docs — 4 Stale Files in services-docs

These files document deprecated services but are still in the active `services-docs/` directory without deprecation notices:

| File | Lines | Deprecated Service | Replaced By |
|------|-------|--------------------|-------------|
| `agro-advisor.md` | 1,168 | agro-advisor | advisory-service |
| `field-chat.md` | 1,068 | field-chat | chat-service |
| `weather-core.md` | 900 | weather-core | weather-service |
| `community-chat.md` | 666 | community-chat | chat-service |

### 2.5 Infrastructure Documentation Gaps

Several infrastructure directories lack documentation:

| Directory | README | .md Files | Status |
|-----------|--------|-----------|--------|
| `infrastructure/deployment/` | NO | 0 | No docs |
| `infrastructure/istio/` | NO | 0 | No docs |
| `infrastructure/nats/` | NO | 0 | No docs |
| `infrastructure/observability/` | NO | 0 | No docs |
| `infrastructure/resilience/` | NO | 0 | No docs |
| `infrastructure/security/` | NO | 0 | No docs |
| `infrastructure/redis/` | NO | 4 | Has guides but no README |

### 2.6 Missing Developer Guides

`docs/guides/` has 20 guides but is missing several critical ones:

| Missing Guide | Impact |
|---------------|--------|
| Developer Onboarding / Getting Started | High — new developer friction |
| Contributing Guide (CONTRIBUTING.md) | High — open source standards |
| Flutter/Mobile Developer Guide | High — mobile team onboarding |
| Arabic/i18n Developer Guide | Medium — bilingual support |
| Shared Module Usage Guide | Medium — how to use `shared/` |
| Event-Driven Architecture Guide | Medium — NATS patterns |
| Database Migration Guide | Medium — Prisma/Tortoise |
| Debugging & Profiling Guide | Low |

---

## 3. Minor Gaps (Priority: LOW)

### 3.1 Services with Thin README (<100 lines)

| Service | README Lines | Notes |
|---------|-------------|-------|
| demo-data | 42 | Minimal |
| ussd-gateway | 80 | Thin |
| audit-service | 82 | Thin |
| agro-rules | 91 | Thin |

### 3.2 Missing Root README

- `apps/kernel/` — No root README.md (has 16 .md files in subdirectories)

### 3.3 Governance README is Minimal

`governance/README.md` is only 45 lines for a directory governing 71+ services, agent definitions, event schemas, policies, and SLO definitions.

### 3.4 Docker Directory Documentation

`docker/` has only 1 .md file (`CONSTRAINTS_EXTRAS.md`). No README explaining the Docker build system, base images, or multi-stage build patterns.

### 3.5 GitHub Workflows Documentation

53 workflow files in `.github/workflows/` with no accompanying documentation file explaining the CI/CD pipeline structure, workflow dependencies, or trigger conditions.

---

## 4. Positive Findings

Areas with strong documentation coverage:

| Area | Coverage | Notes |
|------|----------|-------|
| `shared/auth/` | Excellent | 15 .md files, comprehensive guides |
| `shared/events/` | Good | 5 .md files with DLQ docs and examples |
| `shared/mcp/` | Good | 4 .md files with quick start |
| `shared/cache/` | Good | 3 .md files with implementation summary |
| `apps/mobile/` | Excellent | 109+ .md files, most documented app |
| `apps/web/` | Good | 12 .md files including security audits |
| `infrastructure/gateway/kong/` | Excellent | 16 .md files with runbook |
| `packages/nestjs-auth` | Excellent | 6 .md files with migration guide |
| `docs/adr/` | Good quality | Well-structured, follows template |
| `docs/api/openapi/` | Good | 16 OpenAPI specs (34,899 lines) |
| Service READMEs | Good | 97% coverage (67/69 have README) |

---

## 5. Recommendations

### Immediate Actions (Week 1-2)

1. **Create README.md for `shared/ai/`** — 82 Python files, zero README. This is the most critical gap.
2. **Create README.md for `shared/security/`** — 15 Python files covering RBAC, JWT, policy engine.
3. **Add README to `apps/kernel/`** — root-level README missing.
4. **Add README to `apps/services/ndvi-processor/`** — only service without any README.
5. **Add deprecation notices** to 4 stale service-docs files.

### Short-Term Actions (Week 3-6)

6. **Create service-docs for top 10 missing services** — prioritize: yolo26-vision-service, edge-orchestrator-service, copilot-api, digital-twin-engine, terrain-core-service, hydrology-service, fertigation-engine, knowledge-graph, iot-sensor-hub, irrigation-cycle-engine.
7. **Add README to `shared/` high-impact modules** — irrigation, mobile_sync, monitoring, libs, llm, middleware, secrets, field_boundaries.
8. **Add README to `packages/shared-types`** — contract source of truth needs documentation.
9. **Add test suite READMEs** — at minimum for `tests/unit/`, `tests/e2e/`, `tests/security/`.
10. **Create developer onboarding guide** and **contributing guide**.

### Medium-Term Actions (Month 2-3)

11. **Write missing ADRs** — PostGIS, YOLO26, multi-tenancy, AI model strategy, edge computing.
12. **Consolidate ADR directories** — merge `governance/decisions/` into `docs/adr/`.
13. **Expand knowledge base** — add tomato, vegetables, bacterial diseases, crop rotation, IPM.
14. **Create API narrative docs** — billing, marketplace, IoT, vision, terrain.
15. **Add infrastructure READMEs** — deployment, istio, nats, observability, resilience, security.
16. **Create Docker build documentation** — explain base images, mirror patterns, multi-stage builds.
17. **Document CI/CD pipeline** — workflow dependencies, triggers, and required secrets.

### Long-Term Actions (Quarter 2)

18. **Achieve 80%+ shared module documentation** — README for all modules with 4+ Python files.
19. **Achieve 100% service-docs coverage** — all 69 services documented.
20. **Achieve 100% test suite documentation** — all 18 test directories documented.
21. **Create automated documentation coverage CI check** — fail PR if new module lacks README.
22. **Implement doc freshness tracking** — flag docs not updated in 6+ months.

---

## 6. Documentation Coverage Matrix

### By Layer

```
Layer              Documented  Total  Coverage  Grade
─────────────────────────────────────────────────────
Service READMEs        67       69      97%      A
docs/ root            146      146     100%      A
Mobile app docs       109      109     100%      A
Service-docs           34       69      49%      F
Shared modules         14       71      20%      F
Packages               11       24      46%      F
Test suites             4       18      22%      F
Infrastructure          7       13      54%      D
ADRs                    7      ~17      41%      F
API narrative           5       16      31%      F
Knowledge base         14      ~30      47%      F
```

### By Priority

```
Priority   Gaps  Description
────────────────────────────────────
Critical     4   shared/ modules, service-docs, tests, packages
Moderate     6   ADRs, API docs, knowledge base, deprecated docs,
                 infrastructure, developer guides
Minor        5   thin READMEs, kernel README, governance, docker, CI/CD
```

---

_Report generated: 2026-02-25_
_Next review: 2026-03-25_
