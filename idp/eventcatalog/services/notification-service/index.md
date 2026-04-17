---
id: notification-service
name: Notification Service
summary: Push, SMS, email, and WhatsApp notification delivery.
owners:
  - platform-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/notification-service
sends: []
receives:
  - id: sahool.alert.created
  - id: sahool.alert.resolved
  - id: sahool.weather.alert
  - id: sahool.irrigation.scheduled
  - id: sahool.crop_health.disease_detected
  - id: sahool.ndvi.anomaly_detected
---

**Technology:** FastAPI
**Port:** 8110
**Layer:** Business
**Tier:** tier-1
