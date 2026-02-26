# Architecture Documentation

> وثائق البنية المعمارية | Architecture Documentation

Architecture proposals, principles, and service maps for the SAHOOL platform.

## Contents

| Document | Description |
|----------|-------------|
| [PRINCIPLES.md](./PRINCIPLES.md) | Core architecture principles |
| [AI_ARCHITECTURE_PROPOSAL_2026.md](./AI_ARCHITECTURE_PROPOSAL_2026.md) | AI architecture proposal for 2026 |
| [ASSET_INVESTMENT_PLAN.md](./ASSET_INVESTMENT_PLAN.md) | Technology asset investment plan |
| [EVENT_SEQUENCES.md](./EVENT_SEQUENCES.md) | Event-driven architecture sequences |
| [FIELD_FIRST_ARCHITECTURE.md](./FIELD_FIRST_ARCHITECTURE.md) | Field-first architecture pattern |
| [FIELD_FIRST_ASSESSMENT.md](./FIELD_FIRST_ASSESSMENT.md) | Field-first readiness assessment |
| [FIELD_FIRST_IMPLEMENTATION_PLAN.md](./FIELD_FIRST_IMPLEMENTATION_PLAN.md) | Field-first implementation plan |
| [SERVICE_ACTIVATION_MAP.md](./SERVICE_ACTIVATION_MAP.md) | Service activation and dependency map |
| [frontend-governance.md](./frontend-governance.md) | Frontend governance standards |

## Key Concepts

- **Field-First Architecture**: All features center around the field entity as primary domain object
- **4-Layer Event Architecture**: Acquisition → Intelligence → Decision → Business
- **Offline-First**: Full functionality without internet connectivity
- **71+ Microservices**: Distributed across Python FastAPI and Node.js NestJS

## Related

- [Architecture Diagrams](../ARCHITECTURE_DIAGRAMS.md) — Platform-wide diagrams
- [ADRs](../../governance/decisions/) — Architecture decision records
- [Services Map](../SERVICES_MAP.md) — Complete service directory
