# Architecture Decision Records (ADRs)

> سجلات القرارات المعمارية | Architecture Decision Records

This directory contains Architecture Decision Records documenting significant architectural choices made for the SAHOOL platform.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-0001](./0001-backend-root.md) | Backend Services Root Directory | Accepted | 2025-12-19 |
| [ADR-0002](./0002-multi-tenancy.md) | Multi-Tenancy Strategy (RLS) | Accepted | 2026-04-02 |
| [ADR-0003](./0003-event-versioning.md) | Event Versioning Strategy | Accepted | 2026-04-02 |
| [ADR-0004](./0004-api-versioning.md) | API Versioning Strategy | Accepted | 2026-04-02 |
| [ADR-0005](./0005-service-mesh.md) | Service Mesh Strategy | Accepted | 2026-04-02 |

## ADR Process

### Creating a New ADR

1. Copy the template: `cp template.md NNNN-title.md`
2. Fill in: Status, Context, Decision, Consequences
3. Submit PR for review
4. Status transitions: `Proposed` → `Accepted` / `Rejected` / `Superseded`

### ADR Format

```markdown
# ADR-NNNN: Title

- **Status**: Proposed | Accepted | Rejected | Superseded
- **Date**: YYYY-MM-DD
- **Deciders**: [list]

## Context
[Problem statement]

## Decision
[The change proposed]

## Consequences
[Positive and negative impacts]
```

## Key Decisions Summary

- **ADR-0001**: All backend microservices must reside in `apps/services/` (eliminates fragmentation across kernel/, kernel-services-v15.3/, services/)
- **ADR-0002**: PostgreSQL Row-Level Security (RLS) as primary tenant isolation with application-layer middleware
- **ADR-0003**: Semantic versioning for event schemas with 90-day deprecation and CI-enforced breaking change detection
- **ADR-0004**: URL path versioning (`/api/v1/`, `/api/v2/`) with unified TypeScript/Dart contract system
- **ADR-0005**: Phased service mesh adoption — Application-level (current) → NetworkPolicy → Istio (future)

## Related

- [Service Registry](../services.yaml) — Source of truth for services
- [Design Patterns](../design/) — Design tokens and standards
- [Policies](../policies/) — Security and operational policies
