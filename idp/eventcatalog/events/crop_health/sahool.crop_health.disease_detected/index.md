---
id: sahool.crop_health.disease_detected
name: Disease Detected
version: 1.0.0
summary: Emitted when crop disease is detected
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - crop-intelligence-service
consumers:
  - alert-service
  - notification-service
  - advisory-service
---

## Disease Detected

Emitted by `crop-intelligence-service` when a crop disease is identified through AI analysis, including the disease type, severity, and affected area.

### NATS Subject

`sahool.crop_health.disease_detected`
