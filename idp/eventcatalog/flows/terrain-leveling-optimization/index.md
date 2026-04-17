---
id: terrain-leveling-optimization
name: Terrain Analysis to Leveling Optimization
version: 1.0.0
summary: A DEM is uploaded and processed for terrain analysis, then optimised for leveling with a cost estimate stored in the field record.
steps:
  - id: sahool.terrain.dem_uploaded
    title: DEM Uploaded
    service: terrain-core-service
  - id: sahool.terrain.analysis_completed
    title: Terrain Analysis Completed
    service: terrain-core-service
  - id: sahool.leveling.plan_generated
    title: Leveling Plan Generated
    service: leveling-optimizer-service
  - id: sahool.field.leveling_recorded
    title: Leveling Recorded
    service: field-management-service
---

The terrain-core-service receives a Digital Elevation Model upload, computes slope, aspect, and flow direction, then publishes the analysis. The leveling-optimizer-service consumes the terrain data, runs cut-fill optimisation to minimise earthwork volume, and produces a leveling plan with a cost estimate. The field-management-service records the plan for the field.

```mermaid
sequenceDiagram
    participant TCS as terrain-core-service
    participant NATS as NATS JetStream
    participant LOS as leveling-optimizer-service
    participant FMS as field-management-service
    participant PG as PostgreSQL

    TCS->>TCS: process DEM (slope, aspect, flow)
    TCS->>NATS: publish sahool.terrain.analysis_completed
    NATS->>LOS: deliver sahool.terrain.analysis_completed
    LOS->>LOS: run cut-fill optimisation
    LOS->>LOS: compute cost estimate
    LOS->>NATS: publish sahool.leveling.plan_generated
    NATS->>FMS: deliver sahool.leveling.plan_generated
    FMS->>PG: store leveling plan & cost
```
