---
id: weather-service
name: Weather Service
summary: Weather data ingestion, forecast normalization, and severe weather alerts.
owners:
  - iot-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/weather-service
sends:
  - id: sahool.weather.updated
  - id: sahool.weather.forecast_updated
  - id: sahool.weather.alert
receives: []
---

**Technology:** FastAPI
**Port:** 8092
**Layer:** Acquisition
**Tier:** tier-1
