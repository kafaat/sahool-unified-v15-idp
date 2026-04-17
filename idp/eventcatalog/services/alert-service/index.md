---
id: alert-service
name: Alert Service
summary: Alert creation, escalation, and resolution management.
owners:
  - platform-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/alert-service
sends:
  - id: sahool.alert.created
  - id: sahool.alert.dismissed
  - id: sahool.alert.resolved
receives:
  - id: sahool.field.created
  - id: sahool.field.deleted
  - id: sahool.ndvi.calculated
  - id: sahool.ndvi.anomaly_detected
  - id: sahool.weather.alert
  - id: sahool.crop_health.assessment
  - id: sahool.crop_health.disease_detected
  - id: sahool.system.error
---

**Technology:** FastAPI
**Port:** 8113
**Layer:** Business
**Tier:** tier-2
