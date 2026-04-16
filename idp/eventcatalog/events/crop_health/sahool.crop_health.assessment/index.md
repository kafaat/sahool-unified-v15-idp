---
id: sahool.crop_health.assessment
name: Crop Health Assessment
version: 1.0.0
summary: Emitted with crop health assessment results
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - crop-intelligence-service
consumers:
  - alert-service
  - advisory-service
  - analytics-service
---

## Crop Health Assessment

Emitted by `crop-intelligence-service` after completing a full crop health assessment for a field, aggregating NDVI, disease, and growth-stage data.

### NATS Subject

`sahool.crop_health.assessment`
