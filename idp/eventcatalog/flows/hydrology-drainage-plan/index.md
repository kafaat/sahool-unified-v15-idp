---
id: hydrology-drainage-plan
name: Hydrology Analysis to Drainage Plan
version: 1.0.0
summary: Terrain data feeds hydrology analysis which produces a drainage plan stored against the field record.
steps:
  - id: sahool.terrain.analysis_completed
    title: Terrain Analysis Completed
    service: terrain-core-service
  - id: sahool.hydrology.analysis_completed
    title: Hydrology Analysis Completed
    service: hydrology-service
  - id: sahool.field.drainage_plan_recorded
    title: Drainage Plan Recorded
    service: field-management-service
---

The terrain-core-service publishes completed terrain analysis data (DEM, slope, flow accumulation). The hydrology-service consumes it, delineates watersheds, computes flow paths, and generates a drainage plan with recommended drain placement and capacity. The field-management-service persists the drainage plan in the field record for farmer review.

```mermaid
sequenceDiagram
    participant TCS as terrain-core-service
    participant NATS as NATS JetStream
    participant HS as hydrology-service
    participant FMS as field-management-service
    participant PG as PostgreSQL

    TCS->>NATS: publish sahool.terrain.analysis_completed
    NATS->>HS: deliver sahool.terrain.analysis_completed
    HS->>HS: delineate watersheds
    HS->>HS: compute flow paths & accumulation
    HS->>HS: generate drainage plan (placement, capacity)
    HS->>NATS: publish sahool.hydrology.drainage_plan_generated
    NATS->>FMS: deliver sahool.hydrology.drainage_plan_generated
    FMS->>PG: store drainage plan
```
