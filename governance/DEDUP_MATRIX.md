# SAHOOL De-duplication Matrix

# مصفوفة إزالة الازدواجية

> **Decision Date**: 2024-12-19
> **Status**: APPROVED
> **Affected Systems**: Backend, Frontend, Infrastructure

---

## Executive Summary

| Category         | Current Paths | Target                       | Action Required |
| ---------------- | ------------- | ---------------------------- | --------------- |
| Backend Services | 4 locations   | 1 (`kernel-services-v15.3/`) | Archive 3       |
| Frontend         | 3 locations   | 2 (`web/`, `web_admin/`)     | Archive 1       |
| Domain Logic     | 3 locations   | Merge into services          | Archive/Merge   |

---

## 1. Backend Services Matrix

### 1.1 Primary Backend (KEEP - Official)

| Service              | Path                                          | Port | Status  |
| -------------------- | --------------------------------------------- | ---- | ------- |
| crop-growth-model    | `kernel-services-v15.3/crop-growth-model/`    | 3023 | ✅ KEEP |
| disaster-assessment  | `kernel-services-v15.3/disaster-assessment/`  | 3020 | ✅ KEEP |
| lai-estimation       | `kernel-services-v15.3/lai-estimation/`       | 3022 | ✅ KEEP |
| yield-prediction     | `kernel-services-v15.3/yield-prediction/`     | 3021 | ✅ KEEP |
| marketplace-service  | `kernel-services-v15.3/marketplace-service/`  | 3010 | ✅ KEEP |
| crop-health-ai       | `kernel-services-v15.3/crop-health-ai/`       | 8095 | ✅ KEEP |
| virtual-sensors      | `kernel-services-v15.3/virtual-sensors/`      | 8096 | ✅ KEEP |
| community-chat       | `kernel-services-v15.3/community-chat/`       | 8097 | ✅ KEEP |
| yield-engine         | `kernel-services-v15.3/yield-engine/`         | 8098 | ✅ KEEP |
| irrigation-smart     | `kernel-services-v15.3/irrigation-smart/`     | 8094 | ✅ KEEP |
| fertilizer-advisor   | `kernel-services-v15.3/fertilizer-advisor/`   | 8093 | ✅ KEEP |
| indicators-service   | `kernel-services-v15.3/indicators-service/`   | 8091 | ✅ KEEP |
| satellite-service    | `kernel-services-v15.3/satellite-service/`    | 8090 | ✅ KEEP |
| weather-advanced     | `kernel-services-v15.3/weather-advanced/`     | 8092 | ✅ KEEP |
| notification-service | `kernel-services-v15.3/notification-service/` | 8110 | ✅ KEEP |
| iot-service          | `kernel-services-v15.3/iot-service/`          | 8106 | ✅ KEEP |

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
| research_core | `services/research_core/` | ✅ KEEP & MOVE | Move to `kernel-services-v15.3/research-core/` |
| billing-core  | `apps/billing-core/`      | ✅ KEEP & MOVE | Move to `kernel-services-v15.3/billing-core/`  |

**Move Commands:**

```bash
git mv services/research_core kernel-services-v15.3/research-core
git mv apps/billing-core kernel-services-v15.3/billing-core
rmdir services apps 2>/dev/null || true
```

---

## 2. Domain Logic Matrix

### 2.1 Root-Level Domains (MERGE or ARCHIVE)

| Module        | Current Path     | Contains                             | Decision | Target                                                     |
| ------------- | ---------------- | ------------------------------------ | -------- | ---------------------------------------------------------- |
| advisor       | `advisor/`       | AI, RAG, Context, Explainability     | 🔀 MERGE | `kernel-services-v15.3/crop-growth-model/src/advisor/`     |
| field_suite   | `field_suite/`   | Crops, Farms, Fields, Spatial, Zones | 🔀 MERGE | `kernel-services-v15.3/crop-growth-model/src/field-suite/` |
| kernel_domain | `kernel_domain/` | Auth, Tenancy, Users                 | 🔀 MERGE | `shared/domain/` or dedicated auth-service                 |

**Reasoning:**

- `advisor/` contains AI logic that belongs in crop-growth-model
- `field_suite/` contains spatial domain logic for fields
- `kernel_domain/` contains cross-cutting auth concerns

**Merge Commands (Phase 2):**

```bash
# After review, merge into appropriate services
cp -r advisor/* kernel-services-v15.3/crop-growth-model/src/advisor/
cp -r field_suite/* kernel-services-v15.3/crop-growth-model/src/field-suite/
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

### Phase 1: Archive Legacy (Safe)

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

### Phase 2: Consolidate Orphans

```bash
# Move orphan services to official location
git mv services/research_core kernel-services-v15.3/research-core
git mv apps/billing-core kernel-services-v15.3/billing-core

# Commit
git add -A && git commit -m "chore: consolidate orphan services into kernel-services-v15.3"
```

### Phase 3: Merge Domain Logic (Careful Review Required)

```bash
# This requires code review to avoid breaking imports
# Merge advisor AI logic into crop-growth-model
# Merge field_suite into crop-growth-model
# Move kernel_domain to shared/domain/
```

### Phase 4: Update docker-compose.yml

- Update all build contexts to point to `kernel-services-v15.3/*`
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

```
BEFORE (Current State):
├── kernel-services-v15.3/     ← Official Backend (16 services)
├── kernel/services/           ← Legacy (14 services) → ARCHIVE
├── services/research_core/    ← Orphan → MOVE to v15.3
├── apps/billing-core/         ← Orphan → MOVE to v15.3
├── advisor/                   ← Domain Logic → MERGE
├── field_suite/               ← Domain Logic → MERGE
├── kernel_domain/             ← Auth Domain → shared/domain/
├── frontend/                  ← Legacy → ARCHIVE
├── web/                       ← Official Web
└── web_admin/                 ← Official Admin

AFTER (Target State):
├── kernel-services-v15.3/     ← All Backend (18 services)
│   ├── crop-growth-model/     ← + advisor, field_suite merged
│   ├── research-core/         ← moved from services/
│   ├── billing-core/          ← moved from apps/
│   └── ... (all other services)
├── shared/domain/             ← kernel_domain moved
├── web/                       ← Official Web
├── web_admin/                 ← Official Admin
├── mobile/                    ← Official Mobile
└── archive/                   ← All legacy code preserved
    ├── kernel-legacy/
    └── frontend-legacy/
```

---

**Document Owner**: Platform Team
**Last Updated**: 2024-12-19
**Next Review**: Before v16 planning
