---
id: crop-growth-advisory
name: Crop Growth Stage Advisory
version: 1.0.0
summary: Indicator changes trigger the crop growth model which generates stage-specific advisory recommendations sent to the farmer.
steps:
  - id: sahool.indicators.updated
    title: Indicators Updated
    service: indicators-service
  - id: sahool.crop.stage_changed
    title: Growth Stage Changed
    service: crop-growth-model
  - id: sahool.advisory.generated
    title: Advisory Generated
    service: advisory-service
  - id: sahool.notification.sent
    title: Notification Sent
    service: notification-service
---

When the indicators-service detects threshold-crossing changes, the crop-growth-model evaluates whether a growth stage transition has occurred. On stage change, the advisory-service generates bilingual recommendations (fertilisation, irrigation, pest scouting) for the new stage. The notification-service delivers the advisory to the farmer via push notification.

```mermaid
sequenceDiagram
    participant IND as indicators-service
    participant NATS as NATS JetStream
    participant CGM as crop-growth-model
    participant ADV as advisory-service
    participant NS as notification-service
    participant F as Farmer (Mobile)

    IND->>NATS: publish sahool.indicators.updated
    NATS->>CGM: deliver sahool.indicators.updated
    CGM->>CGM: evaluate growth stage (Zadoks)
    CGM->>NATS: publish sahool.crop.stage_changed
    NATS->>ADV: deliver sahool.crop.stage_changed
    ADV->>ADV: generate stage-specific advisory
    ADV->>NATS: publish sahool.advisory.generated
    NATS->>NS: deliver sahool.advisory.generated
    NS->>F: push notification (growth advisory)
```
