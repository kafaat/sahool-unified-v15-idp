---
id: crop-intelligence-service
name: Crop Intelligence Service
summary: Crop health AI – disease and pest detection, health assessment.
owners:
  - agro-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/crop-intelligence-service
sends:
  - id: sahool.crop_health.assessment
  - id: sahool.crop_health.disease_detected
receives:
  - id: sahool.field.created
---

**Technology:** FastAPI
**Port:** 8095
**Layer:** Intelligence
**Tier:** tier-1
