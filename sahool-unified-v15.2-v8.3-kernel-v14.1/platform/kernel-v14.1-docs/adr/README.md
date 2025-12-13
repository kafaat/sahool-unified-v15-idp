# Architecture Decision Records (ADR)

> قرارات المعمارية الموثقة

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./ADR-001-event-bus.md) | Event Bus (NATS JetStream) | Accepted | 2025-01-01 |
| [ADR-002](./ADR-002-layering.md) | Service Layering Architecture | Accepted | 2025-01-01 |
| [ADR-003](./ADR-003-calendar.md) | Yemeni Agricultural Calendar | Accepted | 2025-01-01 |
| [ADR-004](./ADR-004-event-subject-naming.md) | Event Subject Naming | Accepted | 2025-01-01 |

## Quick Reference

### ADR-001: Event Bus
- **Decision**: Use NATS JetStream
- **Key**: Built-in persistence, KV store for saga state
- **Streams**: SAHOOL (main), SAHOOL_DLQ (dead letters)

### ADR-002: Layering
- **Layers**: Core → Signal → Decision → Execution
- **Key Rule**: Layer 2 has NO public API
- **Communication**: Events only (no HTTP between services)

### ADR-003: Calendar
- **Decision**: Yemeni astronomical calendar as Knowledge Signal
- **28 Stars**: Each produces events
- **Regional**: Support for highlands, Tihama, Hadramout

### ADR-004: Naming
- **Decision**: event_type == NATS subject
- **Format**: `<domain>.<entity>.<action>`
- **Example**: `astro.star.rising`

## Template

```markdown
# ADR-XXX: Title

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue?

## Decision
What did we decide?

## Consequences
What are the trade-offs?
```
