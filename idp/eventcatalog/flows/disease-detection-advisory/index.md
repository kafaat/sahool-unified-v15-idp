---
id: disease-detection-advisory
name: Disease Detection to Advisory
version: 1.0.0
summary: When a crop disease is detected, an alert is raised and the advisory service generates a treatment recommendation sent to the farmer.
steps:
  - id: sahool.crop.disease_detected
    title: Disease Detected
    service: crop-intelligence-service
  - id: sahool.alert.created
    title: Alert Created
    service: alert-service
  - id: sahool.advisory.generated
    title: Advisory Generated
    service: advisory-service
  - id: sahool.notification.sent
    title: Notification Sent
    service: notification-service
---

The crop-intelligence-service detects a disease through spectral or visual analysis and publishes a detection event. Both the alert-service and advisory-service consume this event in parallel. The alert-service creates a high-priority alert. The advisory-service generates a bilingual treatment recommendation. Both services trigger notifications to the farmer.

```mermaid
sequenceDiagram
    participant CIS as crop-intelligence-service
    participant NATS as NATS JetStream
    participant AS as alert-service
    participant ADV as advisory-service
    participant NS as notification-service
    participant F as Farmer (Mobile)

    CIS->>NATS: publish sahool.crop.disease_detected
    par Alert path
        NATS->>AS: deliver sahool.crop.disease_detected
        AS->>AS: create high-priority alert
        AS->>NATS: publish sahool.alert.created
        NATS->>NS: deliver sahool.alert.created
        NS->>F: push alert notification
    and Advisory path
        NATS->>ADV: deliver sahool.crop.disease_detected
        ADV->>ADV: generate treatment advisory
        ADV->>NATS: publish sahool.advisory.generated
        NATS->>NS: deliver sahool.advisory.generated
        NS->>F: push advisory notification
    end
```
