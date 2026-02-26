# Event Catalog & Schemas

> فهرس الأحداث والمخططات | Event Catalog & Schemas

Master event catalog for the SAHOOL platform's 4-layer event-driven architecture via NATS JetStream.

## Contents

```
events/
├── catalog.yaml           # Master event catalog (v1.0.0)
├── events-registry.yaml   # Event registry with producers/consumers
└── schemas/               # JSON schemas for event payloads
    ├── field-created.json
    ├── ndvi-updated.json
    ├── alert-triggered.json
    └── weather-updated.json
```

## Event Categories

| Category | Subject Pattern | Description |
|----------|----------------|-------------|
| `field` | `sahool.field.*` | Field lifecycle events (created, updated, deleted) |
| `ndvi` | `sahool.ndvi.*` | NDVI analysis events |
| `alert` | `sahool.alert.*` | Alert triggers and resolutions |
| `weather` | `sahool.weather.*` | Weather data updates |
| `irrigation` | `sahool.irrigation.*` | Irrigation scheduling events |
| `crop_health` | `sahool.crop_health.*` | Crop health assessments |
| `yield` | `sahool.yield.*` | Yield predictions |
| `system` | `sahool.system.*` | System lifecycle events |

## Subject Patterns

```
# Base pattern
sahool.{domain}.{action}

# Tenant-scoped
sahool.tenant.{tenant_id}.{domain}.{action}

# Examples
sahool.field.created
sahool.tenant.abc-123.ndvi.updated
sahool.vision.pest_detected
```

## Schema Validation

All events are validated against JSON schemas in `schemas/` before publishing. Each schema defines required fields, data types, and bilingual descriptions (EN/AR).

## Related

- [NATS Configuration](../../config/nats/) — NATS cluster config
- [Shared Events](../../shared/events/) — Python event definitions and DLQ
- [Shared Events Package](../../packages/shared-events/) — TypeScript event definitions
- [Event Architecture](../../docs/ARCHITECTURE_DIAGRAMS.md) — 4-layer architecture diagrams
