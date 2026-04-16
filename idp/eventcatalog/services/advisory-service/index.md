---
id: advisory-service
name: Advisory Service
summary: Crop management advisory and bilingual recommendations.
owners:
  - agro-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/advisory-service
sends:
  - id: sahool.irrigation.recommendation
receives:
  - id: sahool.weather.forecast_updated
  - id: sahool.ndvi.trend_changed
  - id: sahool.crop_health.assessment
  - id: sahool.crop_health.disease_detected
---

**Technology:** FastAPI
**Port:** 8093
**Layer:** Decision
**Tier:** tier-1
