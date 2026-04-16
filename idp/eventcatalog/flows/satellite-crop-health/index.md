---
id: satellite-crop-health
name: Satellite Crop Health Assessment
version: 1.0.0
summary: Sentinel satellite imagery is processed for NDVI, assessed for crop health, and advisory recommendations are generated.
steps:
  - id: sahool.vegetation.imagery_received
    title: Satellite Imagery Received
    service: vegetation-analysis-service
  - id: sahool.ndvi.calculated
    title: NDVI Calculated
    service: vegetation-analysis-service
  - id: sahool.crop.health_assessed
    title: Health Assessed
    service: crop-intelligence-service
  - id: sahool.advisory.generated
    title: Advisory Generated
    service: advisory-service
---

The vegetation-analysis-service periodically fetches Sentinel-2 imagery from Sentinel Hub, computes NDVI per field, and publishes the results. The crop-intelligence-service classifies health status (healthy, moderate, stressed, critical) and identifies anomaly zones. For stressed or critical fields, the advisory-service generates targeted treatment or irrigation advice.

```mermaid
sequenceDiagram
    participant VAS as vegetation-analysis-service
    participant SH as Sentinel Hub
    participant NATS as NATS JetStream
    participant CIS as crop-intelligence-service
    participant ADV as advisory-service

    VAS->>SH: fetch Sentinel-2 imagery (all fields)
    SH-->>VAS: satellite bands
    VAS->>VAS: compute per-field NDVI
    VAS->>NATS: publish sahool.ndvi.calculated
    NATS->>CIS: deliver sahool.ndvi.calculated
    CIS->>CIS: classify health (healthy/moderate/stressed/critical)
    CIS->>NATS: publish sahool.crop.health_assessed
    NATS->>ADV: deliver sahool.crop.health_assessed
    alt Stressed or Critical
        ADV->>ADV: generate treatment/irrigation advisory
        ADV->>NATS: publish sahool.advisory.generated
    end
```
