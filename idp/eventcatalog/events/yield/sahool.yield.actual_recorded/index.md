---
id: sahool.yield.actual_recorded
name: Actual Yield Recorded
version: 1.0.0
summary: Emitted when actual harvest yield is recorded
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - field-management-service
consumers:
  - yield-prediction-service
  - analytics-service
---

## Actual Yield Recorded

Emitted by `field-management-service` when a farmer records the actual harvest yield for a field, enabling model retraining and accuracy tracking.

### NATS Subject

`sahool.yield.actual_recorded`
