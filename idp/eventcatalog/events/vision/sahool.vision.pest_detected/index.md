---
id: sahool.vision.pest_detected
name: Pest Detected (Vision)
version: 1.0.0
summary: Emitted when YOLO26 detects a pest
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

## Pest Detected (Vision)

Emitted by `yolo26-vision-service` when the YOLO26 computer-vision model detects a pest in a submitted image, including species, confidence score, and bounding box.

### NATS Subject

`sahool.vision.pest_detected`
