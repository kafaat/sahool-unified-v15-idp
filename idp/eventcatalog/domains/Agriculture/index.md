---
id: agriculture
name: Agriculture
summary: |
  Core agricultural domain – field management, crop health, irrigation,
  weather, yield prediction, and advisory.
owners:
  - agro-team
---

The Agriculture domain encompasses all events related to crop lifecycle
management, from field creation through harvest and yield tracking.

## Event Architecture (4 Layers)

| Layer         | Purpose                           |
|---------------|-----------------------------------|
| Acquisition   | Sensor / satellite data ingestion |
| Intelligence  | Feature extraction & AI           |
| Decision      | Advisory & scheduling             |
| Business      | User-facing operations            |

Transport: **NATS JetStream**
Subject pattern: `sahool.{domain}.{action}`
