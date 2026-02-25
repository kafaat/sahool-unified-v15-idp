# Ground Vision Service

**Port**: 8182 | **Type**: Python (FastAPI) | **Version**: 16.0.0

High-frequency agricultural monitoring service using tower-mounted cameras. Provides real-time, parcel-level field monitoring through quaternion-based georeferencing, GIS-guided SAM segmentation, YOLO-based operation detection, MLLM crop timeline analysis, and anomaly detection.

---

## Overview

`ground-vision-service` bridges the gap between low-frequency satellite imagery (5–10 day revisit) and high-frequency IoT sensors by processing continuous video streams from tower cameras at field edges. It detects agricultural operations (plowing, sowing, irrigation, spraying, harvesting), tracks crop phenological stages in near real-time, and automatically detects anomalies for early intervention. The service is based on Qin et al. (2026) - *A Real-Time, High-Frequency, Parcel-Level Agricultural Monitoring Framework*.

---

## Architecture

```
FastAPI Application
    ├── Camera Management API   (registration, listing)
    ├── Frame Processing API    (change detection, operation classification, anomaly detection)
    ├── Detection API           (operation history, per-detection details)
    ├── Timeline API            (crop phenology, MLLM-based stage analysis)
    └── Anomaly API             (list, acknowledge, resolve)
            |
    Core Modules
    ├── ChangeDetector          (pixel-level change detection, configurable threshold)
    ├── OperationClassifier     (YOLO-based agricultural operation detection)
    ├── CropTimelineReasoner    (MLLM crop phenology inference from frame sequences)
    └── AnomalyDetector         (statistical anomaly detection from change signals)
            |
    External
    ├── asyncpg pool  →  PostgreSQL
    ├── NATS         →  Events (publisher + subscriber)
    └── httpx        →  Frame image download
```

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/health/live` | Kubernetes liveness alias |
| GET | `/readyz` | Readiness probe (database + NATS + models) |
| GET | `/health/ready` | Kubernetes readiness alias |
| GET | `/metrics` | Prometheus metrics (plaintext) |

### Camera Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/cameras` | Register a new tower camera with geolocation and optics parameters |
| GET | `/api/v1/cameras` | List cameras (filter: `tenant_id`, `tower_id`) |
| GET | `/api/v1/cameras/{camera_id}` | Get camera details |

### Frame Processing

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/frames/process` | Process a captured frame: change detection, operation classification, anomaly detection |

### Detections

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/detections` | List detected operations (filter: `field_id`, `operation_type`, date range) |
| GET | `/api/v1/detections/{detection_id}` | Detection detail |

### Timeline Analysis

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/timeline/analyze` | Analyze crop growth stage from up to 10 frames (MLLM) |
| GET | `/api/v1/timeline/{field_id}` | Crop timeline history for a field |

### Anomaly Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/anomalies` | List anomalies (filter: `field_id`, `severity`, `status`) |
| GET | `/api/v1/anomalies/{anomaly_id}` | Anomaly detail |
| POST | `/api/v1/anomalies/{anomaly_id}/acknowledge` | Acknowledge an anomaly |
| POST | `/api/v1/anomalies/{anomaly_id}/resolve` | Mark anomaly resolved with resolution notes |

---

## NATS Events Published

| Subject | Trigger |
|---------|---------|
| `sahool.{tenant_id}.ground_vision.camera_status` | Camera registered or status change |
| `sahool.{tenant_id}.ground_vision.frame_captured` | Frame processed and stored |
| `sahool.{tenant_id}.ground_vision.operation_detected` | Agricultural operation detected |
| `sahool.{tenant_id}.ground_vision.anomaly_detected` | Anomaly flagged |
| `sahool.{tenant_id}.ground_vision.timeline_updated` | Crop timeline analysis completed |

---

## Detectable Operations

| Operation | Description |
|-----------|-------------|
| `plowing` | Soil tillage detected |
| `sowing` | Seed broadcast or row planting |
| `irrigation` | Overhead or drip irrigation running |
| `spraying` | Pesticide or fertilizer spray application |
| `harvesting` | Combine or manual harvesting activity |
| `mulching` | Mulch or cover crop spreading |

---

## Camera Registration Parameters

| Parameter | Description |
|-----------|-------------|
| `camera_id` | Unique camera identifier |
| `tower_id` | Parent tower identifier |
| `latitude`, `longitude`, `altitude_m` | Tower geolocation |
| `focal_length_mm` | Lens focal length |
| `sensor_width_mm`, `sensor_height_mm` | Sensor dimensions |
| `image_width_px`, `image_height_px` | Capture resolution |
| `zoom_min`, `zoom_max` | Zoom range (default: 1.0–40.0x) |

---

## Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `ground_vision_up` | gauge | Service health (always 1) |
| `ground_vision_db_up` | gauge | Database connection status |
| `ground_vision_nats_up` | gauge | NATS connection status |
| `ground_vision_models_loaded` | gauge | AI models loaded |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8182` | HTTP listen port |
| `ENVIRONMENT` | `development` | `production` enforces DB SSL |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `NATS_URL` | - | NATS server URL |
| `DEVICE` | `cuda` | Compute device for inference (`cuda` or `cpu`) |
| `YOLO_MODEL_PATH` | - | Path to YOLO model weights |
| `CHANGE_DETECTION_THRESHOLD` | `0.15` | Pixel-change ratio to trigger operation detection |
| `CORS_ORIGINS` | `https://sahool.io,...` | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Dependencies

- `fastapi` + `pydantic` v2
- `asyncpg` for PostgreSQL async connection pool
- `nats-py` for event streaming
- `httpx` for asynchronous frame image download
- `shared.errors_py` for request-ID middleware and exception handling
- Local `core/` module: `ChangeDetector`, `OperationClassifier`
- Local `intelligence/` module: `CropTimelineReasoner`, `AnomalyDetector`
- Local `events/` module: `GroundVisionPublisher`, `GroundVisionSubscriber`

---

## Health Endpoints

```
GET /healthz → {"status": "ok", "service": "ground-vision-service", "version": "16.0.0"}
GET /readyz  → {"status": "ok|degraded", "database": bool, "nats": bool, "models_loaded": bool}
```

---

## Related Services

- **yolo26-vision-service** (8150) - aerial image analysis (drone imagery)
- **vegetation-analysis-service** (8090) - satellite NDVI complement
- **iot-gateway** (8106) - IoT sensor data from the same towers
- **alert-service** (8113) - escalation of critical anomalies
