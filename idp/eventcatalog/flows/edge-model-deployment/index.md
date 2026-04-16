---
id: edge-model-deployment
name: Edge Model Deployment and Inference Sync
version: 1.0.0
summary: A model is deployed from the registry to an edge device, runs local inference, and syncs results back to the cloud.
steps:
  - id: sahool.edge.deploy_requested
    title: Deploy Requested
    service: edge-orchestrator-service
  - id: sahool.edge.model_deployed
    title: Model Deployed
    service: edge-device (Jetson Orin)
  - id: sahool.edge.inference_completed
    title: Local Inference Completed
    service: edge-device (Jetson Orin)
  - id: sahool.vegetation.analysis_synced
    title: Results Synced
    service: vegetation-analysis-service
---

The edge-orchestrator-service selects a model version from the registry and deploys it to a Jetson Orin edge device. The device runs local inference on field imagery without cloud connectivity. When connectivity is available, inference results are synced back via NATS to the vegetation-analysis-service for aggregation with satellite data.

```mermaid
sequenceDiagram
    participant EOS as edge-orchestrator-service
    participant REG as Model Registry
    participant EDGE as Jetson Orin (Edge)
    participant NATS as NATS JetStream
    participant VAS as vegetation-analysis-service

    EOS->>REG: fetch model artifact (version, variant)
    REG-->>EOS: model binary
    EOS->>EDGE: deploy model (OTA)
    EDGE->>EDGE: load model to GPU
    EDGE-->>EOS: deployment ACK
    Note over EDGE: Field imagery captured locally
    EDGE->>EDGE: run local inference (pest/disease/weed)
    EDGE->>EDGE: store results locally
    Note over EDGE,NATS: When connectivity available
    EDGE->>NATS: publish sahool.edge.inference_completed (batch)
    NATS->>VAS: deliver sahool.edge.inference_completed
    VAS->>VAS: merge with satellite analysis
```
