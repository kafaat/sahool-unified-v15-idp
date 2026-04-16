---
id: yield-prediction
name: Yield Prediction Pipeline
version: 1.0.0
summary: Growth model data feeds the ML yield prediction service, whose results are pushed to the web dashboard in real time.
steps:
  - id: sahool.crop.growth_updated
    title: Growth Data Updated
    service: crop-growth-model
  - id: sahool.yield.predicted
    title: Yield Predicted
    service: yield-prediction-service
  - id: sahool.dashboard.updated
    title: Dashboard Updated
    service: ws-gateway
---

The crop-growth-model service publishes updated phenological stage and biomass accumulation data. The yield-prediction-service consumes this event, runs its ML model to produce a yield estimate with confidence intervals, and publishes the prediction. The ws-gateway pushes the result as a Server-Sent Event to the web dashboard for real-time display.

```mermaid
sequenceDiagram
    participant CGM as crop-growth-model
    participant NATS as NATS JetStream
    participant YPS as yield-prediction-service
    participant WSG as ws-gateway
    participant WD as Web Dashboard

    CGM->>NATS: publish sahool.crop.growth_updated
    NATS->>YPS: deliver sahool.crop.growth_updated
    YPS->>YPS: run ML prediction model
    YPS->>NATS: publish sahool.yield.predicted
    NATS->>WSG: deliver sahool.yield.predicted
    WSG->>WD: SSE push (yield forecast)
```
