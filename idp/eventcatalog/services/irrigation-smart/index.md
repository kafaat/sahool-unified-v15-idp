---
id: irrigation-smart
name: Irrigation Smart
summary: Smart irrigation scheduling based on weather, soil, and crop data.
owners:
  - agro-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/irrigation-smart
sends:
  - id: sahool.irrigation.scheduled
  - id: sahool.irrigation.completed
receives:
  - id: sahool.weather.updated
  - id: sahool.weather.forecast_updated
  - id: sahool.irrigation.recommendation
---

**Technology:** FastAPI
**Port:** 8094
**Layer:** Decision
**Tier:** tier-1
