---
id: sahool.field.created
name: Field Created
version: 1.0.0
summary: Emitted when a new field is created
owners:
  - platform-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - field-management-service
consumers:
  - vegetation-analysis-service
  - alert-service
  - crop-intelligence-service
---

## Field Created

Emitted by `field-management-service` whenever a farmer registers a new field in the platform.

### Schema

| Field          | Type   | Description                     |
|----------------|--------|---------------------------------|
| field_id       | string | Unique field identifier (UUID)  |
| tenant_id      | string | Tenant identifier (UUID)        |
| name           | string | Human-readable field name       |
| area_hectares  | number | Field area in hectares          |
| crop_type      | string | Primary crop type               |

### NATS Subject

`sahool.field.created`
