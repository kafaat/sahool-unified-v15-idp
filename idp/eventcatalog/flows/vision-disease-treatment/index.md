---
id: vision-disease-treatment
name: Vision Disease Detection to Treatment Plan
version: 1.0.0
summary: A field image is classified for disease by YOLO26 and crop intelligence, producing a treatment plan sent to the farmer.
steps:
  - id: sahool.vision.image_uploaded
    title: Image Uploaded
    service: mobile-app
  - id: sahool.vision.disease_detected
    title: Disease Detected
    service: yolo26-vision-service
  - id: sahool.crop.disease_classified
    title: Disease Classified
    service: crop-intelligence-service
  - id: sahool.advisory.treatment_generated
    title: Treatment Plan Generated
    service: advisory-service
  - id: sahool.notification.sent
    title: Notification Sent
    service: notification-service
---

The farmer uploads an image of a symptomatic crop. The yolo26-vision-service detects disease regions and confidence scores. The crop-intelligence-service classifies the specific disease (e.g., wheat rust) and severity. The advisory-service generates a step-by-step treatment plan including product, dosage, PHI, and safety instructions. The notification-service delivers the plan.

```mermaid
sequenceDiagram
    participant MA as Mobile App
    participant K as Kong Gateway
    participant YV as yolo26-vision-service
    participant NATS as NATS JetStream
    participant CIS as crop-intelligence-service
    participant ADV as advisory-service
    participant NS as notification-service
    participant F as Farmer (Mobile)

    MA->>K: POST /api/v1/detect/disease (image)
    K->>YV: forward request
    YV->>YV: YOLO26 inference (disease detection)
    YV-->>K: detection result
    K-->>MA: immediate response
    YV->>NATS: publish sahool.vision.disease_detected
    NATS->>CIS: deliver sahool.vision.disease_detected
    CIS->>CIS: classify disease type & severity
    CIS->>NATS: publish sahool.crop.disease_classified
    NATS->>ADV: deliver sahool.crop.disease_classified
    ADV->>ADV: generate treatment plan (product, dosage, PHI)
    ADV->>NATS: publish sahool.advisory.treatment_generated
    NATS->>NS: deliver sahool.advisory.treatment_generated
    NS->>F: push notification (treatment plan)
```
