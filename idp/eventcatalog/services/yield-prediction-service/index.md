---
id: yield-prediction-service
name: Yield Prediction Service
summary: ML-based yield prediction and forecasting.
owners:
  - agro-team
repository:
  language: TypeScript
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/yield-prediction-service
sends:
  - id: sahool.yield.predicted
receives:
  - id: sahool.yield.actual_recorded
---

**Technology:** NestJS
**Port:** 8152
**Layer:** Decision
**Tier:** tier-2
