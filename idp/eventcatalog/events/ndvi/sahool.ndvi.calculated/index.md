---
id: sahool.ndvi.calculated
name: NDVI Calculated
version: 1.0.0
summary: Emitted when NDVI is computed from satellite imagery
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - vegetation-analysis-service
consumers:
  - alert-service
  - analytics-service
  - frontend-sse
---

## NDVI Calculated

Emitted by `vegetation-analysis-service` after computing the Normalized Difference Vegetation Index from Sentinel Hub satellite imagery for a given field.

### NATS Subject

`sahool.ndvi.calculated`
