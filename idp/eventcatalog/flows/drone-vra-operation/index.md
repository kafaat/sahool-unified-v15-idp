---
id: drone-vra-operation
name: Drone VRA Operation
version: 1.0.0
summary: A drone flight captures imagery, vision analysis produces a variable-rate application map, and field operations are updated.
steps:
  - id: sahool.drone.flight_completed
    title: Drone Flight Completed
    service: drone-service
  - id: sahool.vision.analysis_completed
    title: Vision Analysis Completed
    service: yolo26-vision-service
  - id: sahool.advisory.vra_generated
    title: VRA Map Generated
    service: advisory-service
  - id: sahool.field.ops_updated
    title: Field Operations Updated
    service: field-management-service
---

The drone-service completes an aerial survey and publishes the captured imagery. The yolo26-vision-service performs weed and pest detection across the flight mosaic. Results feed into the advisory-service which generates a variable-rate application (VRA) map for targeted spraying or fertilisation. The field-management-service records the VRA operation plan.

```mermaid
sequenceDiagram
    participant DS as drone-service
    participant NATS as NATS JetStream
    participant YV as yolo26-vision-service
    participant ADV as advisory-service
    participant FMS as field-management-service

    DS->>NATS: publish sahool.drone.flight_completed (imagery)
    NATS->>YV: deliver sahool.drone.flight_completed
    YV->>YV: detect weeds & pests (YOLO26)
    YV->>NATS: publish sahool.vision.analysis_completed
    NATS->>ADV: deliver sahool.vision.analysis_completed
    ADV->>ADV: generate VRA map (zones, rates)
    ADV->>NATS: publish sahool.advisory.vra_generated
    NATS->>FMS: deliver sahool.advisory.vra_generated
    FMS->>FMS: record VRA operation plan
```
