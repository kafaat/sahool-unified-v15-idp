# Architecture Decision Records (ADRs)

> سجلات القرارات المعمارية | Architecture Decision Records

This directory contains Architecture Decision Records documenting significant architectural choices made for the SAHOOL platform.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-0001](./0001-backend-root.md) | Backend Services Root Directory | Accepted | 2025-12-19 |

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

## Related

- [Service Registry](../services.yaml) — Source of truth for services
- [Design Patterns](../design/) — Design tokens and standards
- [Policies](../policies/) — Security and operational policies
