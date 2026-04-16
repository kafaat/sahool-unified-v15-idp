---
id: sahool.ndvi.anomaly_detected
name: NDVI Anomaly Detected
version: 1.0.0
summary: Emitted when NDVI anomaly is detected
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - vegetation-analysis-service
consumers:
  - alert-service
  - notification-service
---

## NDVI Anomaly Detected

Emitted by `vegetation-analysis-service` when the computed NDVI value deviates significantly from the historical baseline for a field, indicating potential crop stress.

### NATS Subject

`sahool.ndvi.anomaly_detected`
