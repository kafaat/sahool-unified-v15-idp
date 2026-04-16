---
id: sahool.yield.predicted
name: Yield Predicted
version: 1.0.0
summary: Emitted with ML yield prediction
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - yield-prediction-service
consumers:
  - analytics-service
  - frontend-sse
---

## Yield Predicted

Emitted by `yield-prediction-service` after running the ML yield prediction model for a field, including the predicted yield and confidence interval.

### NATS Subject

`sahool.yield.predicted`
