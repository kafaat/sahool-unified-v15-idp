---
id: yolo26-vision-service
name: YOLO26 Vision Service
summary: GPU-accelerated computer vision – pest, disease, weed detection.
owners:
  - agro-team
repository:
  language: Python
  url: https://github.com/kafaat/sahool-unified-v15-idp/tree/main/apps/services/yolo26-vision-service
sends:
  - id: sahool.vision.pest_detected
  - id: sahool.vision.disease_detected
  - id: sahool.vision.weed_detected
  - id: sahool.vision.critical.alert
receives: []
---

**Technology:** FastAPI + PyTorch + CUDA 12.1
**Port:** 8150
**Layer:** Intelligence
**Tier:** tier-2
