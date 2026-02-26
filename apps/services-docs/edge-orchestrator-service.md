# Edge Orchestrator Service

**Type:** Python/FastAPI | **Port:** 8180 | **Version:** 16.0.0 | **Status:** Active

Edge device orchestration service for managing AI inference on agricultural edge devices (Jetson Orin), supporting offline-first operations, model deployment, job scheduling, and data synchronization.

خدمة تنسيق أجهزة الحافة لإدارة استدلال الذكاء الاصطناعي على أجهزة الحافة الزراعية مع دعم العمليات دون اتصال ونشر النماذج وجدولة المهام ومزامنة البيانات.

---

## Overview

The Edge Orchestrator Service is the cloud-side control plane for SAHOOL's agricultural edge computing fleet. It manages Jetson Orin and Raspberry Pi 5 AI HAT devices deployed in farm fields, handling device registration, real-time WebSocket communication, OTA model deployment, job lifecycle management, and offline-first data synchronization. Devices communicate over WebSocket with a 30-second heartbeat protocol; devices missing two consecutive heartbeats are marked offline.

---

## Architecture

```
Edge Orchestrator Service (Port 8180)
├── Device Registry     - Registration, capability tracking, GPS location
├── Job Scheduler       - Priority-based inference/deployment/sync jobs
├── Model Deployer      - OTA TensorRT model deployment with validation
├── Sync Engine         - Bi-directional data sync with conflict resolution
└── WebSocket Layer     - Real-time bi-directional device communication
        ↓
Edge Devices
├── Jetson Orin Nano  (8 GB, 40 TOPS, 15W)
├── Jetson Orin NX    (16 GB, 100 TOPS, 25W)
├── Jetson AGX Orin   (64 GB, 275 TOPS, 60W)
└── Raspberry Pi 5 + AI HAT (13 TOPS, 5W)
```

**Dependencies:** PostgreSQL, Redis, NATS, optional model storage volume at `/models`

---

## API Endpoints

### Health

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /healthz` | GET | Kubernetes liveness probe |
| `GET /readyz` | GET | Readiness probe (DB + NATS status) |
| `GET /metrics` | GET | Prometheus metrics |

### Device Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/v1/devices` | GET | List all registered edge devices |
| `POST /api/v1/devices` | POST | Register new device (returns capabilities object) |
| `GET /api/v1/devices/{device_id}` | GET | Get device details and current status |
| `PUT /api/v1/devices/{device_id}` | PUT | Update device configuration |
| `DELETE /api/v1/devices/{device_id}` | DELETE | Remove device from registry |
| `GET /api/v1/devices/{device_id}/status` | GET | Real-time device status |
| `GET /api/v1/devices/{device_id}/metrics` | GET | CPU/GPU/temperature metrics |
| `GET /api/v1/devices/farm/{farm_id}` | GET | List all devices for a farm |
| `POST /api/v1/devices/{device_id}/reconnect` | POST | Trigger reconnection to device |

### Job Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/v1/jobs` | GET | List jobs with optional status filter |
| `POST /api/v1/jobs` | POST | Create inference/deployment/sync/diagnostic job |
| `GET /api/v1/jobs/{job_id}` | GET | Get job details |
| `DELETE /api/v1/jobs/{job_id}` | DELETE | Cancel queued or running job |
| `GET /api/v1/jobs/{job_id}/status` | GET | Poll job status |
| `GET /api/v1/jobs/{job_id}/result` | GET | Retrieve completed job result |
| `POST /api/v1/jobs/{job_id}/retry` | POST | Retry failed job |
| `GET /api/v1/jobs/device/{device_id}` | GET | All jobs for a specific device |
| `POST /api/v1/jobs/batch` | POST | Create multiple jobs in one request |

**Job types:** `inference`, `model_deployment`, `data_sync`, `diagnostic`, `calibration`
**Priority levels:** `low`, `normal`, `high`, `critical`

### Model Deployment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/deploy` | POST | Deploy model to device (OTA with validation) |
| `GET /api/v1/deploy/{deploy_id}` | GET | Deployment status and progress |
| `POST /api/v1/deploy/{deploy_id}/cancel` | POST | Cancel in-progress deployment |
| `GET /api/v1/models` | GET | List available models for deployment |
| `GET /api/v1/models/{model_name}/devices` | GET | List devices running a model |

### Data Synchronization

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/sync` | POST | Initiate sync operation (upload/download) |
| `GET /api/v1/sync/{sync_id}` | GET | Sync progress and status |
| `POST /api/v1/sync/{sync_id}/cancel` | POST | Cancel in-progress sync |
| `GET /api/v1/sync/device/{device_id}/pending` | GET | Pending sync items count |

### WebSocket Channels

| Endpoint | Description |
|----------|-------------|
| `WS /ws/device/{device_id}` | Per-device bi-directional communication channel |
| `WS /ws/dashboard` | Real-time dashboard updates for admin portal |
| `WS /ws` | General WebSocket endpoint |

**WebSocket message types:** `heartbeat`, `metrics`, `job_status`, `detection`, `sync_progress`, `deploy_progress`, `alert`, `error`

---

## NATS Events

### Produces

| Event | Description |
|-------|-------------|
| `EdgeDeviceRegistered.v1` | New device registered |
| `EdgeDeviceOnline.v1` | Device heartbeat restored |
| `EdgeDeviceOffline.v1` | Device missed heartbeat threshold |
| `EdgeJobCompleted.v1` | Inference or deployment job completed |
| `EdgeJobFailed.v1` | Job failed after retries |
| `EdgeModelDeployed.v1` | Model OTA deployment succeeded |
| `EdgeSyncCompleted.v1` | Data sync operation completed |
| `EdgeDetection.v1` | Real-time detection result from device |
| `EdgeAlert.v1` | Critical alert originated on device |

### Consumes

| Event | Action |
|-------|--------|
| `FieldCreated.v1` | Auto-register monitoring context for field |
| `ModelUpdated.v1` | Trigger OTA deployment to eligible devices |
| `FarmConfigUpdated.v1` | Push updated configuration to devices |
| `CriticalPestAlert.v1` | Activate alert mode on farm devices |

---

## Sync Protocol

Batch-based incremental sync: device sends `since` timestamp → server returns pending count → device uploads in 100-item batches with acknowledgement → server confirms. Conflict resolution: cloud wins for configuration, append-only for detection results. Checksum validation on both sides.

Supported sync data types: `inference_results`, `images`, `logs`, `metrics`

---

## Supported Edge Models

| Model | Format | Jetson Orin Nano FPS |
|-------|--------|----------------------|
| yolo26-n | TensorRT | 83 |
| yolo26-s | TensorRT | 40 |
| yolo11-s | TensorRT | 45 |
| crop-disease-v3 | TensorRT | 32 |
| pest-detection-v2 | TensorRT | 38 |
| weed-classifier-v1 | TensorRT | 52 |

---

## Environment Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8180` | Service port | No |
| `DATABASE_URL` | - | PostgreSQL connection | Yes |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection | Yes |
| `NATS_URL` | `nats://localhost:4222` | NATS server URL | Yes |
| `JWT_SECRET_KEY` | - | JWT secret (32+ chars) | Yes |
| `EDGE_HEARTBEAT_INTERVAL` | `30` | Expected heartbeat interval (seconds) | No |
| `EDGE_TIMEOUT_THRESHOLD` | `120` | Device offline timeout (seconds) | No |
| `MAX_DEVICES_PER_FARM` | `50` | Device limit per farm | No |
| `DEFAULT_MODEL` | `yolo26-s` | Default AI model for new devices | No |
| `MODEL_STORAGE_PATH` | `/models` | OTA model storage path | No |
| `JETSON_SSH_PORT` | `22` | SSH port for management | No |
| `JETSON_API_PORT` | `8000` | API port on device | No |
| `SYNC_BATCH_SIZE` | `100` | Items per sync batch | No |
| `WS_MAX_CONNECTIONS` | `1000` | Max concurrent WebSocket connections | No |
| `MAX_UPLOAD_SIZE_MB` | `500` | Max upload size (model files) | No |

---

## Admin Integration

- **Makefile target:** `make dev-edge`, `make test-edge`
- **CI workflow:** `.github/workflows/ci-edge-orchestrator.yml`
- **Docker Compose:** Defined in main `docker-compose.yml`; requires persistent volume for `/models`
- **Kong route:** `/api/v1/edge/*` proxied to `edge-orchestrator-service:8180`
- **Admin Portal:** Real-time device fleet map, job queue dashboard, and deployment status panels connect via `WS /ws/dashboard`
- **Kubernetes:** 2 replicas recommended; WebSocket sessions require sticky sessions (session affinity) on the Service load balancer

---

**Version:** 16.0.0 | **Last Updated:** January 2026 | **License:** Proprietary - KAFAAT
