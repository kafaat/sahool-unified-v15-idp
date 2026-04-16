---
id: field-boundary-update
name: Field Boundary Update to NDVI Refresh
version: 1.0.0
summary: When a field boundary is modified, the vegetation analysis pipeline re-runs to produce an updated NDVI for the new geometry.
steps:
  - id: sahool.field.boundary_updated
    title: Boundary Updated
    service: field-management-service
  - id: sahool.vegetation.analysis_requested
    title: Re-analysis Triggered
    service: vegetation-analysis-service
  - id: sahool.ndvi.calculated
    title: Updated NDVI
    service: vegetation-analysis-service
---

A farmer edits a field boundary in the mobile or web app. The field-management-service persists the new PostGIS geometry and publishes a boundary update event. The vegetation-analysis-service fetches fresh Sentinel Hub imagery matching the new polygon and recomputes the NDVI, publishing the updated result for downstream consumers.

```mermaid
sequenceDiagram
    participant FMS as field-management-service
    participant PG as PostgreSQL (PostGIS)
    participant NATS as NATS JetStream
    participant VAS as vegetation-analysis-service
    participant SH as Sentinel Hub

    FMS->>PG: UPDATE field boundary (new geometry)
    FMS->>NATS: publish sahool.field.boundary_updated
    NATS->>VAS: deliver sahool.field.boundary_updated
    VAS->>SH: request imagery (new polygon)
    SH-->>VAS: Sentinel-2 bands
    VAS->>VAS: recompute NDVI for new area
    VAS->>NATS: publish sahool.ndvi.calculated
```
