# SAHOOL De-duplication Matrix

# مصفوفة إزالة الازدواجية

> **Decision Date**: 2024-12-19
> **Status**: APPROVED
> **Affected Systems**: Backend, Frontend, Infrastructure

---

## Executive Summary

| Category         | Current Paths | Target                       | Action Required |
| ---------------- | ------------- | ---------------------------- | --------------- |
| Backend Services | 4 locations   | 1 (`apps/services/`) | Archive 3       |
| Frontend         | 3 locations   | 2 (`web/`, `web_admin/`)     | Archive 1       |
| Domain Logic     | 3 locations   | Merge into services          | Archive/Merge   |

---

## 1. Backend Services Matrix

### 1.1 Primary Backend (KEEP - Official)

| Service              | Path                                          | Port | Status  |
| -------------------- | --------------------------------------------- | ---- | ------- |
| crop-growth-model    | `apps/services/crop-growth-model/`    | 3023 | ✅ KEEP |
| disaster-assessment  | `apps/services/disaster-assessment/`  | 3020 | ✅ KEEP |
| lai-estimation       | `apps/services/lai-estimation/`       | 3022 | ✅ KEEP |
| yield-prediction     | `apps/services/yield-prediction/`     | 3021 | ✅ KEEP |
| marketplace-service  | `apps/services/marketplace-service/`  | 3010 | ✅ KEEP |
| crop-health-ai       | `apps/services/crop-health-ai/`       | 8095 | ✅ KEEP |
| virtual-sensors      | `apps/services/virtual-sensors/`      | 8096 | ✅ KEEP |
| community-chat       | `apps/services/community-chat/`       | 8097 | ✅ KEEP |
| yield-engine         | `apps/services/yield-engine/`         | 8098 | ✅ KEEP |
| irrigation-smart     | `apps/services/irrigation-smart/`     | 8094 | ✅ KEEP |
| fertilizer-advisor   | `apps/services/fertilizer-advisor/`   | 8093 | ✅ KEEP |
| indicators-service   | `apps/services/indicators-service/`   | 8091 | ✅ KEEP |
| satellite-service    | `apps/services/satellite-service/`    | 8090 | ✅ KEEP |
| weather-advanced     | `apps/services/weather-advanced/`     | 8092 | ✅ KEEP |
| notification-service | `apps/services/notification-service/` | 8110 | ✅ KEEP |
| iot-service          | `apps/services/iot-service/`          | 8106 | ✅ KEEP |

---

### 1.2 Legacy Backend (ARCHIVE)

| Service           | Current Path                         | Duplicate Of       | Decision   | Reason                        |
| ----------------- | ------------------------------------ | ------------------ | ---------- | ----------------------------- |
| field_core        | `kernel/services/field_core/`        | -                  | 🧊 ARCHIVE | Superseded by v15.3 structure |
| field_ops         | `kernel/services/field_ops/`         | -                  | 🧊 ARCHIVE | Superseded by v15.3 structure |
| ndvi_engine       | `kernel/services/ndvi_engine/`       | -                  | 🧊 ARCHIVE | Superseded by v15.3 structure |
| weather_core      | `kernel/services/weather_core/`      | weather-advanced   | 🧊 ARCHIVE | Duplicate functionality       |
| field_chat        | `kernel/services/field_chat/`        | community-chat     | 🧊 ARCHIVE | Duplicate functionality       |
| iot_gateway       | `kernel/services/iot_gateway/`       | iot-service        | 🧊 ARCHIVE | Duplicate functionality       |
| agro_advisor      | `kernel/services/agro_advisor/`      | fertilizer-advisor | 🧊 ARCHIVE | Duplicate functionality       |
| agro_rules        | `kernel/services/agro_rules/`        | -                  | 🧊 ARCHIVE | Business rules in services    |
| community_service | `kernel/services/community_service/` | community-chat     | 🧊 ARCHIVE | Duplicate functionality       |
| crop_health       | `kernel/services/crop_health/`       | crop-health-ai     | 🧊 ARCHIVE | Duplicate functionality       |
| equipment_service | `kernel/services/equipment_service/` | -                  | 🧊 ARCHIVE | Low priority                  |
| provider_config   | `kernel/services/provider_config/`   | -                  | 🧊 ARCHIVE | Config in env/secrets         |
| task_service      | `kernel/services/task_service/`      | -                  | 🧊 ARCHIVE | Can be feature in field-ops   |
| ws_gateway        | `kernel/services/ws_gateway/`        | -                  | 🧊 ARCHIVE | WebSocket in community-chat   |

**Archive Command:**

```bash
mkdir -p archive/kernel-legacy
git mv kernel/services archive/kernel-legacy/
```

---

### 1.3 Orphan Services (DECISION REQUIRED)

| Service       | Current Path              | Decision       | Action                                         |
| ------------- | ------------------------- | -------------- | ---------------------------------------------- |
| research_core | `services/research_core/` | ✅ KEEP & MOVE | Move to `apps/services/research-core/` |
| billing-core  | `apps/billing-core/`      | ✅ KEEP & MOVE | Move to `apps/services/billing-core/`  |

**Move Commands:**

```bash
git mv services/research_core apps/services/research-core
git mv apps/billing-core apps/services/billing-core
rmdir services 2>/dev/null || true
```

---

## 2. Domain Logic Matrix

### 2.1 Root-Level Domains (MERGE or ARCHIVE)

| Module        | Current Path     | Contains                             | Decision | Target                                                     |
| ------------- | ---------------- | ------------------------------------ | -------- | ---------------------------------------------------------- |
| advisor       | `advisor/`       | AI, RAG, Context, Explainability     | 🔀 MERGE | `apps/services/crop-growth-model/src/advisor/`     |
| field_suite   | `field_suite/`   | Crops, Farms, Fields, Spatial, Zones | 🔀 MERGE | `apps/services/crop-growth-model/src/field-suite/` |
| kernel_domain | `kernel_domain/` | Auth, Tenancy, Users                 | 🔀 MERGE | `shared/domain/` or dedicated auth-service                 |

**Reasoning:**

- `advisor/` contains AI logic that belongs in crop-growth-model
- `field_suite/` contains spatial domain logic for fields
- `kernel_domain/` contains cross-cutting auth concerns

**Merge Commands (Phase 2):**

```bash
# After review, merge into appropriate services
cp -r advisor/* apps/services/crop-growth-model/src/advisor/
cp -r field_suite/* apps/services/crop-growth-model/src/field-suite/
git mv advisor archive/
git mv field_suite archive/
git mv kernel_domain shared/domain/
```

---

## 3. Frontend Matrix

| App             | Current Paths              | Decision                         | Official Path |
| --------------- | -------------------------- | -------------------------------- | ------------- |
| Web App         | `web/src/`, `frontend/`    | Keep `web/`, Archive `frontend/` | `web/`        |
| Admin Dashboard | `web_admin/`               | ✅ KEEP                          | `web_admin/`  |
| Mobile          | `mobile/sahool_field_app/` | ✅ KEEP                          | `mobile/`     |

**Archive Command:**

```bash
git mv frontend archive/frontend-legacy
```

---

## 4. Infrastructure Matrix

| Component        | Current Path           | Status               |
| ---------------- | ---------------------- | -------------------- |
| Docker Compose   | `docker-compose.yml`   | ✅ KEEP (main entry) |
| Compose Profiles | `docker/compose.*.yml` | ✅ KEEP              |
| Kong Config      | `infra/kong/kong.yml`  | ✅ KEEP              |
| Helm Charts      | `helm/`                | ✅ KEEP              |
| GitOps           | `gitops/`              | ✅ KEEP              |
| Observability    | `observability/`       | ✅ KEEP              |

---

## 5. Execution Plan

### Phase 1: Archive Legacy (Safe) — ✅ COMPLETE

```bash
# Create archive structure
mkdir -p archive/{kernel-legacy,frontend-legacy}

# Archive kernel/services (duplicates)
git mv kernel/services archive/kernel-legacy/

# Archive frontend (duplicate of web/)
git mv frontend archive/frontend-legacy/

# Commit
git add -A && git commit -m "chore: archive legacy duplicates (kernel/services, frontend)"
```

### Phase 2: Consolidate Orphans — ✅ COMPLETE

```bash
# Move orphan services to official location
git mv services/research_core apps/services/research-core
git mv apps/billing-core apps/services/billing-core

# Commit
git add -A && git commit -m "chore: consolidate orphan services into apps/services"
```

### Phase 3: Merge Domain Logic (Careful Review Required) — ⏳ IN PROGRESS

```bash
# This requires code review to avoid breaking imports
# Merge advisor AI logic into crop-growth-model
# Merge field_suite into crop-growth-model
# Move kernel_domain to shared/domain/
```

### Phase 4: Update docker-compose.yml — ✅ COMPLETE

- Update all build contexts to point to `apps/services/*`
- Remove references to archived paths

---

## 6. Impact Assessment

| System             | Impact                    | Risk Level |
| ------------------ | ------------------------- | ---------- |
| docker-compose.yml | Update build contexts     | Medium     |
| Kong routes        | No change                 | Low        |
| CI/CD              | Update paths in workflows | Medium     |
| Helm charts        | Update image paths        | Medium     |
| Imports            | Review after domain merge | High       |

---

## 7. Validation Checklist

After each phase:

- [ ] `make up` succeeds
- [ ] `docker compose ps` shows all services healthy
- [ ] `curl localhost:8000/health` returns OK
- [ ] No broken imports in TypeScript/Python
- [ ] CI pipeline passes

---

## Appendix: Full Path Map

> **Note (March 2026):** Migration from kernel-services-v15.3/ to apps/services/ is COMPLETE. All services now reside in apps/services/.

```
BEFORE (Original State — pre-v16):
├── kernel-services-v15.3/     ← Official Backend (16 services)
├── kernel/services/           ← Legacy (14 services) → ARCHIVE
├── services/research_core/    ← Orphan → MOVE
├── apps/billing-core/         ← Orphan → MOVE
├── advisor/                   ← Domain Logic → MERGE
├── field_suite/               ← Domain Logic → MERGE
├── kernel_domain/             ← Auth Domain → shared/domain/
├── frontend/                  ← Legacy → ARCHIVE
├── web/                       ← Official Web
└── web_admin/                 ← Official Admin

AFTER (Current State — v16.0.0):
├── apps/services/             ← All Backend (72 active services)
│   ├── crop-growth-model/     ← + advisor, field_suite merged
│   ├── research-core/         ← moved from services/
│   ├── billing-core/          ← moved from apps/
│   └── ... (all other services)
├── shared/domain/             ← kernel_domain moved
├── apps/web/                  ← Official Web
├── apps/admin/                ← Official Admin
├── apps/mobile/               ← Official Mobile
└── archive/                   ← All legacy code preserved
    ├── kernel-legacy/
    └── frontend-legacy/
```

---

## 8. Active Service Similarity Matrix (v16.0.0)

The following pairs of similarly-named services have been reviewed and their distinct purposes documented.

### 8.1 Reviewed & Resolved

| Service 1 | Service 2 | Resolution | Date |
|-----------|-----------|------------|------|
| yield-prediction (3021) | yield-prediction-service (8152) | **DEPRECATED** yield-prediction. Code 100% identical. yield-prediction-service has rate limiting + Prisma. | 2026-02-19 |
| ndvi-processor (8118) | vegetation-analysis-service (8090) | **DISTINCT** purposes. ndvi-processor handles satellite NDVI computation. vegetation-analysis-service is broader (multi-index, multi-provider). | 2026-02-19 |

### 8.2 Clarified (Previously Requires Clarification)

| Service 1 | Port | Service 2 | Port | Distinction | Status |
|-----------|------|-----------|------|-------------|--------|
| code-review-agent | 8145 | code-review-service | 8102 | **code-review-agent** is a Claude SDK-powered autonomous agent that performs deep AI code review with context-aware analysis. **code-review-service** is a general-purpose API service for rule-based code review (linting, complexity, standards). They are **complementary**: the service handles deterministic checks while the agent handles nuanced analysis. | ✅ DISTINCT |
| ai-advisor | 8112 | ai-agents-core | 8161 | **ai-advisor** is a domain-specific service for agricultural advisory (crop recommendations, irrigation scheduling, fertilizer guidance). **ai-agents-core** is the foundational framework providing agent lifecycle management, tool registration, and multi-agent orchestration (CrewAI). ai-advisor may *use* ai-agents-core as infrastructure. | ✅ DISTINCT |
| ai-agents-core | 8161 | ai-agents-service | 8130 | **ai-agents-core** provides the base framework (agent definitions, tool registry, memory management). **ai-agents-service** handles deployment, orchestration, and external API exposure for end-user agent interactions. Core = library, Service = runtime orchestration. | ✅ DISTINCT |

---

**Document Owner**: Platform Team
**Last Updated**: 2026-04-02
**Next Review**: v17 planning
