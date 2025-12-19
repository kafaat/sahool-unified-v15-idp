# ADR-0001: Backend Services Root Directory

## Status
**Accepted** - 2025-12-19

## Context

The SAHOOL platform has accumulated multiple backend service locations over time:
- `kernel/services/` - Original legacy services
- `kernel-services-v15.3/` - v15.3 migration target
- `services/` - Orphan services
- `apps/` - Billing and other new services

This fragmentation causes:
1. Confusion about where to add new services
2. Inconsistent docker-compose paths
3. CI/CD complexity
4. Onboarding friction

## Decision

**All backend microservices MUST reside in `apps/services/`**

### Structure
```
apps/
├── services/          # All backend microservices
│   ├── crop-growth-model/
│   ├── disaster-assessment/
│   ├── lai-estimation/
│   ├── yield-prediction/
│   ├── marketplace-service/
│   ├── community-chat/
│   ├── iot-service/
│   ├── research-core/
│   ├── billing-core/
│   ├── satellite-service/
│   ├── weather-advanced/
│   ├── indicators-service/
│   ├── crop-health-ai/
│   ├── virtual-sensors/
│   ├── yield-engine/
│   ├── fertilizer-advisor/
│   ├── irrigation-smart/
│   └── notification-service/
├── web/               # Main web dashboard
├── admin/             # Admin panel
└── mobile/            # Mobile app
```

### Migration
1. All services from `kernel-services-v15.3/` → `apps/services/`
2. All services from `kernel/services/` → `archive/kernel-legacy/`
3. All references updated in `governance/services.yaml`
4. Docker-compose updated to use `apps/services/` paths

## Consequences

### Positive
- Single source of truth for all services
- Clear onboarding path for new developers
- Simplified CI/CD configuration
- Consistent with modern monorepo patterns

### Negative
- Requires migration effort
- May break existing tooling temporarily
- Need to update all documentation

### Mitigations
- Archive old paths (don't delete)
- Add CI guard to prevent regression
- Update all documentation in same PR

## Enforcement

- CI workflow `governance-structure.yml` blocks PRs that:
  - Add services outside `apps/services/`
  - Reference `kernel/` or `kernel-services-v15.3/` paths
  - Create new top-level service directories

## References
- `governance/services.yaml` - Service registry
- `.github/workflows/governance-structure.yml` - CI enforcement
- `REPO_MAP.md` - Repository structure documentation
