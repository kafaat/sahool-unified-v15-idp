# ADR-0003: Event Versioning Strategy

- **Status**: Accepted
- **Date**: 2026-04-02
- **Deciders**: Platform Architecture Team

## Context

> السياق | Context

SAHOOL uses a 4-layer event-driven architecture via NATS JetStream with 20+ domain events across 7 categories (field, crop, weather, iot, analytics, user, system). As the platform evolves, event schemas change, and we need a strategy to handle backward compatibility.

Key requirements:
1. **Backward compatibility** — Consumers must not break when producers add fields
2. **Breaking change detection** — Removed fields or type changes must be caught in CI
3. **Migration path** — Deprecation period for old event versions
4. **Documentation** — All events must be documented with producers/consumers
5. **Bilingual** — Event schemas support Arabic/English descriptions

Options considered:
- **A) No versioning** — All changes must be backward-compatible forever
- **B) URL/subject versioning** — `sahool.v2.field.created` (separate subjects per version)
- **C) Schema versioning** — Version in event payload, single subject
- **D) Semantic versioning with deprecation** — SemVer on schemas, 90-day deprecation

## Decision

> القرار | Decision

We adopt **Option D: Semantic versioning with deprecation**:

### Versioning Rules

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| **Breaking** (field removed, type changed) | **Major** | 1.0.0 → 2.0.0 |
| **New optional field** | **Minor** | 1.0.0 → 1.1.0 |
| **Documentation, description fix** | **Patch** | 1.0.0 → 1.0.1 |

### Governance Rules (EVT-001 through EVT-005)

1. **EVT-001**: All events MUST have a JSON schema in `governance/events/schemas/`
2. **EVT-002**: Breaking changes MUST bump the major version and require `BREAKING:` commit prefix
3. **EVT-003**: Deprecated events MUST be supported for 90 days before removal
4. **EVT-004**: High-priority events MUST be processed within 100ms (SLO)
5. **EVT-005**: All events MUST include `correlation_id` for distributed tracing

### Subject Patterns

- **Base**: `sahool.{domain}.{action}` (e.g., `sahool.field.created`)
- **Tenant-scoped**: `sahool.tenant.{tenant_id}.{domain}.{action}`
- **Inline tenant**: `sahool.{tenant_id}.{domain}.{action}` (legacy, being migrated)

### Schema Validation

- Event schemas are defined in `governance/events/schemas/*.json` (JSON Schema Draft 7)
- `event-contracts-guard.yml` CI workflow validates:
  - Schema structural validity
  - Backward compatibility (detects removed events, new required fields, property removals, type changes)
  - Documentation completeness (description, producers, consumers, examples)
  - TypeScript type generation synchronization

### Breaking Change Policy (Updated)

Breaking changes in event schemas are now **blocking** (not just warnings):
- CI workflow `event-contracts-guard.yml` will **fail** the PR if breaking changes are detected without `BREAKING:` commit prefix
- This ensures breaking changes are intentional and documented

### Maximum Supported Versions

- At most **3 versions** of an event may be supported simultaneously
- Producers MUST support the latest 2 versions during deprecation

## Consequences

> النتائج | Consequences

### Positive

- **Safe evolution** — Schemas evolve without breaking consumers
- **CI enforcement** — Breaking changes caught before merge
- **Clear deprecation** — 90-day window gives consumers time to migrate
- **Documentation** — Event catalog serves as single source of truth

### Negative

- **Complexity** — Managing multiple schema versions adds overhead
- **Coordination** — Breaking changes require cross-team coordination
- **Testing** — Need to test against multiple schema versions during deprecation

### Mitigations

- Event catalog (`governance/events/catalog.yaml`) tracks all versions and consumers
- CI guard automates compatibility checking
- Type generators keep TypeScript/Dart types in sync with schemas

## Related

- [Event Catalog](../events/catalog.yaml)
- [Event Registry](../events/events-registry.yaml)
- [Event Contracts Guard](../../.github/workflows/event-contracts-guard.yml)
- [NATS Configuration](../../config/nats/)
