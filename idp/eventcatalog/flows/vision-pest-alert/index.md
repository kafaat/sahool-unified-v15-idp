---
id: vision-pest-alert
name: Vision Pest Detection Alert
version: 1.0.0
summary: A farmer uploads a field image; YOLO26 detects pests, triggers an alert, and notifies the farmer with severity details.
steps:
  - id: sahool.vision.image_uploaded
    title: Image Uploaded
    service: mobile-app
  - id: sahool.vision.pest_detected
    title: Pest Detected
    service: yolo26-vision-service
  - id: sahool.alert.created
    title: Alert Created
    service: alert-service
  - id: sahool.notification.sent
    title: Notification Sent
    service: notification-service
---

The farmer captures a photo of a suspicious crop area using the mobile app. The image is sent through Kong to the yolo26-vision-service, which runs YOLO26 inference to detect pest species and severity. Detection results are published via NATS. The alert-service creates a priority alert and the notification-service informs the farmer with actionable details.

```mermaid
sequenceDiagram
    participant MA as Mobile App
    participant K as Kong Gateway
    participant YV as yolo26-vision-service
    participant NATS as NATS JetStream
    participant AS as alert-service
    participant NS as notification-service
    participant F as Farmer (Mobile)

    MA->>K: POST /api/v1/detect/pest (image)
    K->>YV: forward request
    YV->>YV: YOLO26 inference (pest detection)
    YV-->>K: detection result (species, confidence, severity)
    K-->>MA: response
    YV->>NATS: publish sahool.vision.pest_detected
    NATS->>AS: deliver sahool.vision.pest_detected
    AS->>AS: evaluate severity
    AS->>NATS: publish sahool.alert.created
    NATS->>NS: deliver sahool.alert.created
    NS->>F: push notification (pest alert)
```
