# SAHOOL Repository Map - خريطة المستودع
> Single Source of Truth for Repository Structure

## Quick Reference

| Category | Official Path | Status |
|----------|--------------|--------|
| **Backend Services** | `apps/services/` | ✅ Active |
| **Web Dashboard** | `apps/web/` | ✅ Active |
| **Admin Panel** | `apps/admin/` | ✅ Active |
| **Mobile App** | `apps/mobile/` | ✅ Active |
| **API Gateway** | `infra/kong/` | ✅ Active |
| **Infrastructure** | `infra/` | ✅ Active |
| **Shared Packages** | `packages/` | ✅ Active |
| **Observability** | `observability/` | ✅ Active |

---

## ✅ Official Paths (المسارات المعتمدة)

### Backend Services
```
apps/services/               # 20 microservices
├── crop-growth-model/       # Crop modeling, Digital Twin, GIS (15 modules)
├── disaster-assessment/     # Disaster & alert management
├── lai-estimation/          # LAI & vegetation indices
├── yield-prediction/        # Yield forecasting
├── marketplace-service/     # Market & fintech
├── community-chat/          # Expert chat system
├── iot-service/             # IoT gateway
├── research-core/           # Scientific research
├── billing-core/            # Billing & payments
├── satellite-service/       # Satellite imagery
├── weather-advanced/        # Weather forecasting
├── indicators-service/      # Agricultural indicators
├── crop-health-ai/          # Disease detection (SahoolVision)
├── virtual-sensors/         # Virtual sensor calculations
├── yield-engine/            # ML yield predictions
├── fertilizer-advisor/      # Fertilizer recommendations
├── irrigation-smart/        # Smart irrigation
└── notification-service/    # Push notifications
```

### Frontend Applications
```
apps/
├── web/                     # Main web dashboard (Next.js)
├── admin/                   # Admin panel (Next.js)
└── mobile/                  # Mobile app (Flutter)
    └── sahool_field_app/
```

### Infrastructure
```
infra/
├── kong/                    # API Gateway configuration
│   └── kong.yml             # Kong declarative config
├── docker/                  # Docker configurations
└── terraform/               # IaC (if applicable)

helm/
└── sahool/                  # Kubernetes Helm charts

gitops/                      # ArgoCD configurations

observability/
├── grafana/                 # Dashboards & provisioning
├── prometheus/              # Metrics
└── loki/                    # Logs
```

### Shared Packages
```
packages/
├── advisor/                 # AI advisory system (RAG, LLM, context)
├── field-suite/             # Spatial & field domain models
├── api-client/              # TypeScript API client
├── shared-hooks/            # React hooks
├── shared-ui/               # UI components
├── shared-utils/            # Utility functions
├── tailwind-config/         # Tailwind configuration
└── typescript-config/       # TypeScript configs

shared/
├── domain/                  # Auth, Users, Tenancy (cross-cutting)
├── contracts/               # API contracts
├── events/                  # Event schemas
└── libs/                    # Shared libraries
```

### Governance
```
governance/
├── services.yaml            # Service registry (Single Source of Truth)
├── decisions/               # Architecture Decision Records
│   └── 0001-backend-root.md # Backend structure decision
├── schemas/                 # JSON schemas
├── policies/                # Kyverno policies
└── templates/               # Service templates
```

### Configuration Files (Root)
```
./
├── docker-compose.yml       # Development compose
├── package.json             # Monorepo root
├── Makefile                 # Unified commands
├── .env.example             # Environment template
└── turbo.json               # Turborepo config
```

---

## 🧊 Frozen/Archive (المجمد - للمراجعة فقط)

> These paths contain historical code. Do NOT modify.

```
archive/
├── frontend-legacy/         # Old frontend (migrated to apps/web/)
└── kernel-legacy/           # Old kernel services (migrated to apps/services/)
    └── kernel/
        └── services/        # FROZEN - see kernel/services/FROZEN.md
```

---

## 🗑️ Deprecated (سيُحذف لاحقًا)

> These will be removed in future cleanup sprints.

```
legacy/                      # Old implementations
sahool-unified-v15.2-*/      # Old version snapshots (to archive)
```

> **Migrated (No Longer Deprecated):**
> - `kernel-services-v15.3/*` → `apps/services/*`
> - `web/` → `apps/web/`
> - `web_admin/` → `apps/admin/`
> - `mobile/` → `apps/mobile/`
> - `advisor/` → `packages/advisor/`
> - `field_suite/` → `packages/field-suite/`
> - `kernel_domain/` → `shared/domain/`

---

## Service Registry

### Active Microservices (v16)

| Service | Port | Category | Status |
|---------|------|----------|--------|
| crop-growth-model | 3000 | crop | ✅ |
| disaster-assessment | 3001 | analytics | ✅ |
| lai-estimation | 3002 | analytics | ✅ |
| yield-prediction | 3003 | analytics | ✅ |
| marketplace-service | 3004 | community | ✅ |
| community-chat | 3005 | community | ✅ |
| iot-service | 3006 | integration | ✅ |
| research-core | 3015 | core | ✅ |
| billing-core | 8021 | core | ✅ |
| satellite-service | 8090 | analytics | ✅ |
| indicators-service | 8091 | analytics | ✅ |
| weather-advanced | 8092 | integration | ✅ |
| fertilizer-advisor | 8093 | core | ✅ |
| irrigation-smart | 8094 | core | ✅ |
| crop-health-ai | 8095 | analytics | ✅ |
| virtual-sensors | 8096 | analytics | ✅ |
| yield-engine | 8098 | analytics | ✅ |
| notification-service | 8110 | core | ✅ |

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
| 2025-12-19 | `apps/services/` is official backend | Single Source of Truth |
| 2025-12-19 | `kernel-services-v15.3/` archived | Migrated to apps/services/ |
| 2025-12-19 | `kernel/services/` archived | Superseded, moved to archive/ |
| 2025-12-19 | `web/` → `apps/web/` | Unified apps structure |
| 2025-12-19 | `web_admin/` → `apps/admin/` | Unified apps structure |
| 2025-12-19 | Domain modules to packages | advisor, field_suite → packages/ |
| 2025-12-19 | Auth domain to shared | kernel_domain → shared/domain/ |
| 2025-12-19 | CI Guard enabled | Prevents structure regression |

---

## Contacts

- **Backend Owner**: apps/services/
- **Frontend Owner**: apps/web/, apps/admin/
- **DevOps Owner**: infra/ + helm/ + gitops/

---

*Last Updated: 2025-12-19*
