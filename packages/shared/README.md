# Shared Event Schemas

> مخططات الأحداث المشتركة | Shared Event Schemas

JSON Schema definitions for all SAHOOL platform domain events, following the 4-layer event-driven architecture via NATS JetStream.

**Version**: 1.0.0

## Directory Structure

```
packages/shared/
└── events/
    ├── _base.event.v1.json              # Base event schema (all events inherit)
    ├── index.json                        # Event registry index
    ├── SatelliteSceneIngested.v1.json    # Acquisition layer
    ├── SensorReadingIngested.v1.json     # Acquisition layer
    ├── WeatherForecastReady.v1.json      # Acquisition layer
    ├── FieldIndicatorsComputed.v1.json   # Intelligence layer
    ├── CropHealthAssessed.v1.json        # Intelligence layer
    ├── DisasterRiskScored.v1.json        # Intelligence layer
    ├── GrowthStageEstimated.v1.json      # Decision layer
    ├── YieldPredicted.v1.json            # Decision layer
    ├── IrrigationPlanProposed.v1.json    # Decision layer
    ├── FertilizerPlanProposed.v1.json    # Decision layer
    ├── NotificationQueued.v1.json        # Business layer
    └── OrderCreated.v1.json              # Business layer
```

## Event Layers

| Layer | Events | Description |
|-------|--------|-------------|
| **Acquisition** | SatelliteSceneIngested, SensorReadingIngested, WeatherForecastReady | Data ingestion and normalization |
| **Intelligence** | FieldIndicatorsComputed, CropHealthAssessed, DisasterRiskScored | Feature extraction and AI analysis |
| **Decision** | GrowthStageEstimated, YieldPredicted, IrrigationPlanProposed, FertilizerPlanProposed | Recommendations and planning |
| **Business** | NotificationQueued, OrderCreated | User-facing operations |

## Base Event Schema

All events inherit from `_base.event.v1.json` with required fields:

```json
{
  "event_id": "uuid",
  "event_type": "Domain.Action",
  "event_version": "v1",
  "tenant_id": "uuid",
  "timestamp": "ISO 8601",
  "source": {
    "service": "service-name",
    "version": "16.0.0"
  }
}
```

Optional fields: `field_id`, `correlation_id`, `causation_id`, `metadata`.

## Naming Convention

- **Pattern**: `{Domain}.{Action}` (e.g., `Satellite.SceneIngested`, `Crop.HealthAssessed`)
- **Versioning**: Append `.v{n}` to filename, use `event_version` field in payload
- **NATS Subject**: `sahool.{tenant_id}.{event_type}`

## Related

- [Event Catalog](../../governance/events/) — Event catalog and registry
- [Shared Events (Python)](../../shared/events/) — Python event definitions
- [Shared Events (TypeScript)](../shared-events/) — TypeScript event package
- [NATS Configuration](../../config/nats/) — NATS cluster config
