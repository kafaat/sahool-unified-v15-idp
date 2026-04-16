---
id: soil-analysis-fertilizer
name: Soil Analysis to Fertilizer Recommendation
version: 1.0.0
summary: Soil test results are analysed to produce a targeted fertilizer recommendation delivered to the farmer.
steps:
  - id: sahool.soil.test_completed
    title: Soil Test Completed
    service: soil-analysis-service
  - id: sahool.advisory.fertilizer_generated
    title: Fertilizer Advisory Generated
    service: advisory-service
  - id: sahool.notification.sent
    title: Notification Sent
    service: notification-service
---

The soil-analysis-service processes lab results (N, P, K, pH, EC) and publishes them via NATS. The advisory-service compares nutrient levels against crop-stage requirements, selects an appropriate fertilizer product and rate, and generates a bilingual recommendation. The notification-service delivers the advisory with a cost-benefit summary.

```mermaid
sequenceDiagram
    participant SAS as soil-analysis-service
    participant NATS as NATS JetStream
    participant ADV as advisory-service
    participant NS as notification-service
    participant F as Farmer (Mobile)

    SAS->>NATS: publish sahool.soil.test_completed (N, P, K, pH, EC)
    NATS->>ADV: deliver sahool.soil.test_completed
    ADV->>ADV: compare nutrients vs crop-stage requirements
    ADV->>ADV: select fertilizer product & rate
    ADV->>NATS: publish sahool.advisory.fertilizer_generated
    NATS->>NS: deliver sahool.advisory.fertilizer_generated
    NS->>F: push notification (fertilizer recommendation)
```
