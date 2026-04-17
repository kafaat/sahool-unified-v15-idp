---
id: sahool.vision.disease_detected
name: Disease Detected (Vision)
version: 1.0.0
summary: Emitted when YOLO26 detects a disease
owners:
  - agro-team
domain: Agriculture
badges:
  - content: NATS
producers:
  - yolo26-vision-service
consumers:
  - alert-service
  - advisory-service
---

## Disease Detected (Vision)

Emitted by `yolo26-vision-service` when the YOLO26 computer-vision model detects a crop disease in a submitted image, including disease class, confidence score, and affected area percentage.

### NATS Subject

`sahool.vision.disease_detected`
