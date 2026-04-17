---
id: vegetation-analysis-service
name: Vegetation Analysis Service
summary: Satellite imagery NDVI/LAI processing and anomaly detection.
owners:
  - agro-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/vegetation-analysis-service
sends:
  - id: sahool.ndvi.calculated
  - id: sahool.ndvi.anomaly_detected
receives:
  - id: sahool.field.created
  - id: sahool.field.boundary.changed
---

**Technology:** FastAPI + asyncpg
**Port:** 8090
**Layer:** Intelligence
**Tier:** tier-1
