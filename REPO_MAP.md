# SAHOOL Repository Map - خريطة المستودع
> Single Source of Truth for Repository Structure

## Quick Reference

| Category | Official Path | Status |
|----------|--------------|--------|
| **Backend Services** | `kernel-services-v15.3/` | ✅ Active |
| **Web Dashboard** | `frontend/dashboard/` | ✅ Active |
| **Admin Panel** | `web_admin/` | ✅ Active |
| **Mobile App** | `mobile/sahool_field_app/` | ✅ Active |
| **API Gateway** | `infra/kong/` | ✅ Active |
| **Infrastructure** | `infra/` | ✅ Active |
| **Shared Packages** | `packages/` | ✅ Active |
| **Observability** | `observability/` | ✅ Active |

---

## ✅ Official Paths (المسارات المعتمدة)

### Backend Services
```
kernel-services-v15.3/           # 18 services
├── crop-growth-model/           # Crop modeling, Digital Twin, GIS (15 modules)
├── disaster-assessment/         # Disaster & alert management
├── lai-estimation/              # LAI & vegetation indices
├── yield-prediction/            # Yield forecasting
├── marketplace-service/         # Market & fintech
├── community-chat/              # Expert chat system
├── iot-service/                # IoT gateway
├── research-core/              # Scientific research (NEW)
├── billing-core/               # Billing & payments (NEW)
└── [other v15.3 services]
```

### Frontend Applications
```
web/
└── src/                    # Main web dashboard (Next.js)

web_admin/                  # Admin panel (Next.js)
```

### Mobile Application
```
mobile/
└── sahool_field_app/       # Flutter mobile app
```

### Infrastructure
```
infra/
├── kong/                   # API Gateway configuration
│   └── kong.yml           # Kong declarative config
├── docker/                # Docker configurations
└── terraform/             # IaC (if applicable)

helm/
└── sahool/                # Kubernetes Helm charts

gitops/                    # ArgoCD configurations

observability/
├── grafana/               # Dashboards & provisioning
├── prometheus/            # Metrics
└── loki/                  # Logs
```

### Shared Packages
```
packages/
├── advisor/               # AI advisory system (RAG, LLM, context)
├── field-suite/           # Spatial & field domain models
├── api-client/            # TypeScript API client
├── shared-hooks/          # React hooks
├── shared-ui/             # UI components
├── shared-utils/          # Utility functions
├── tailwind-config/       # Tailwind configuration
└── typescript-config/     # TypeScript configs

shared/
├── domain/                # Auth, Users, Tenancy (cross-cutting)
├── contracts/             # API contracts
├── events/                # Event schemas
└── libs/                  # Shared libraries
```

### Configuration Files (Root)
```
./
├── docker-compose.yml     # Development compose
├── package.json           # Monorepo root
├── Makefile              # Unified commands
├── .env.example          # Environment template
└── turbo.json            # Turborepo config
```

---

## 🧊 Frozen/Archive (المجمد - للمراجعة فقط)

> These paths contain historical code. Do NOT modify.

```
archive/
├── frontend-legacy/       # Old frontend (migrated to web/)
└── kernel-legacy/         # (planned - kernel/services)

kernel/services/           # FROZEN - see kernel/services/FROZEN.md
legacy/                    # Old implementations
```

---

## 🗑️ Deprecated (سيُحذف لاحقًا)

> These will be removed in future cleanup sprints.

```
sahool-unified-v15.2-*/    # Old version snapshots (to archive)
```

> **Migrated (No Longer Deprecated):**
> - `apps/billing-core/` → `kernel-services-v15.3/billing-core/`
> - `services/research_core/` → `kernel-services-v15.3/research-core/`
> - `advisor/` → `packages/advisor/`
> - `field_suite/` → `packages/field-suite/`
> - `kernel_domain/` → `shared/domain/`

---

## Service Registry

### Active Microservices (v15.3)

| Service | Port | Database | Status |
|---------|------|----------|--------|
| crop-growth-model | 3000 | - | ✅ |
| disaster-assessment | 3001 | PostgreSQL | ✅ |
| lai-estimation | 3002 | - | ✅ |
| yield-prediction | 3003 | - | ✅ |
| marketplace-service | 3004 | PostgreSQL | ✅ |
| community-chat | 3005 | PostgreSQL | ✅ |
| iot-service | 3006 | TimescaleDB | ✅ |
| field-ops | 8080 | PostgreSQL | ✅ |
| ndvi-engine | 8107 | - | ✅ |
| weather-core | 8108 | PostgreSQL | ✅ |
| agro-advisor | 8105 | PostgreSQL | ✅ |

### API Gateway Routes

| Route | Service | Rate Limit |
|-------|---------|------------|
| `/api/v1/digital-twin/*` | crop-growth-model | 20/min |
| `/api/v1/rs-world-model/*` | crop-growth-model | 20/min |
| `/api/v1/planting-strategy/*` | crop-growth-model | 30/min |
| `/api/v1/gis/*` | crop-growth-model | 50/min |
| `/api/v1/disaster/*` | disaster-assessment | 60/min |
| `/api/v1/yield/*` | yield-prediction | 30/min |

---

## Development Commands

```bash
# Start all services
make up

# Start specific profile
make up-dev
make up-prod

# View logs
make logs

# Stop services
make down

# Build all
make build

# Run tests
make test
```

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-12-19 | `kernel-services-v15.3/` is official backend | Most complete, tested, documented |
| 2024-12-19 | `kernel/services/` FROZEN | Superseded by v15.3, docker-compose still uses it |
| 2024-12-19 | `frontend/` archived | Migrated to web/ |
| 2024-12-19 | Domain modules to packages | advisor, field_suite → packages/ |
| 2024-12-19 | Auth domain to shared | kernel_domain → shared/domain/ |
| 2024-12-19 | Orphan services consolidated | research_core, billing-core → v15.3 |
| 2024-12-19 | Unified Makefile commands | Single entry point for all operations |

---

## Contacts

- **Backend Owner**: kernel-services-v15.3/
- **Frontend Owner**: frontend/dashboard/
- **DevOps Owner**: infra/ + helm/ + gitops/

---

*Last Updated: 2025-12-19*
