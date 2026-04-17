---
id: field-creation-to-ndvi
name: Field Creation to NDVI Analysis
version: 1.0.0
summary: When a new field is created, vegetation analysis is triggered to compute the initial NDVI and check for alerts.
steps:
  - id: sahool.field.created
    title: Field Created
    service: field-management-service
  - id: sahool.vegetation.analysis_requested
    title: Vegetation Analysis Requested
    service: vegetation-analysis-service
  - id: sahool.ndvi.calculated
    title: NDVI Calculated
    service: vegetation-analysis-service
  - id: sahool.alert.check
    title: Alert Check
    service: alert-service
---

A newly created field triggers an automated vegetation analysis pipeline. The field-management-service publishes a `sahool.field.created` event via NATS. The vegetation-analysis-service picks it up, fetches Sentinel Hub imagery for the field boundary, computes the NDVI, and publishes the result. The alert-service evaluates whether the NDVI falls below a critical threshold and raises an alert if needed.

```mermaid
sequenceDiagram
    participant FMS as field-management-service
    participant NATS as NATS JetStream
    participant VAS as vegetation-analysis-service
    participant SH as Sentinel Hub
    participant AS as alert-service

    FMS->>NATS: publish sahool.field.created
    NATS->>VAS: deliver sahool.field.created
    VAS->>SH: request satellite imagery (field boundary)
    SH-->>VAS: return Sentinel-2 bands
    VAS->>VAS: compute NDVI
    VAS->>NATS: publish sahool.ndvi.calculated
    NATS->>AS: deliver sahool.ndvi.calculated
    AS->>AS: evaluate alert thresholds
    alt NDVI below threshold
        AS->>NATS: publish sahool.alert.created
    end
```
