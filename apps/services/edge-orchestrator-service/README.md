# Edge Orchestrator Service

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/kafaat/sahool)
[![Coverage](https://img.shields.io/badge/coverage-81%25-green)](https://github.com/kafaat/sahool)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## خدمة تنسيق الحافة

> **Edge device orchestration service for managing AI inference on agricultural edge devices (Jetson Orin), supporting offline-first operations, model deployment, job scheduling, and data synchronization.**

> **خدمة تنسيق أجهزة الحافة لإدارة استدلال الذكاء الاصطناعي على أجهزة الحافة الزراعية (Jetson Orin)، مع دعم العمليات دون اتصال ونشر النماذج وجدولة المهام ومزامنة البيانات.**

---

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Edge Orchestrator Service                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Device    │  │    Job      │  │   Model     │  │    Sync     │        │
│  │  Registry   │  │  Scheduler  │  │  Deployer   │  │   Engine    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐        │
│  │                   WebSocket Communication Layer                 │        │
│  │              Real-time bi-directional communication             │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                              │                                             │
│         ┌────────────────────┼────────────────────┐                        │
│         ▼                    ▼                    ▼                        │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│  │ Jetson Orin │      │ Jetson Orin │      │ Jetson Orin │                 │
│  │   Nano      │      │     NX      │      │     AGX     │                 │
│  │  (15W/8GB)  │      │  (25W/16GB) │      │  (60W/64GB) │                 │
│  └─────────────┘      └─────────────┘      └─────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Port | المنفذ

```
8180
```

---

## Features | الميزات

### Device Management | إدارة الأجهزة

- Device registration and discovery
- Real-time status monitoring (heartbeat)
- Device capability tracking (GPU, memory, storage)
- Health metrics collection (CPU, GPU, temperature)
- Multi-farm device organization
- Location tracking with GPS

### Job Scheduling | جدولة المهام

- Inference job scheduling
- Model deployment jobs
- Data sync jobs
- Diagnostic and calibration tasks
- Priority-based execution (low, normal, high, critical)
- Job retry and timeout handling

### Model Deployment | نشر النماذج

- TensorRT optimized model deployment
- Model version management
- Over-the-air (OTA) updates
- Validation after deployment
- Rollback support

### Data Synchronization | مزامنة البيانات

- Offline-first data buffering
- Bi-directional sync (upload/download)
- Incremental sync since last timestamp
- Checksum validation
- Conflict resolution

### Supported Edge Devices | الأجهزة المدعومة

| Device | Arabic | GPU Memory | Power | AI Performance |
|--------|--------|------------|-------|----------------|
| **Jetson Orin Nano** | جيتسون أورين نانو | 8 GB | 15W | 40 TOPS |
| **Jetson Orin NX** | جيتسون أورين NX | 16 GB | 25W | 100 TOPS |
| **Jetson AGX Orin** | جيتسون AGX أورين | 64 GB | 60W | 275 TOPS |
| **Raspberry Pi 5 + AI HAT** | راسبيري باي 5 | - | 5W | 13 TOPS |

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Device Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/devices` | GET | List all edge devices |
| `/api/v1/devices` | POST | Register new device |
| `/api/v1/devices/{device_id}` | GET | Get device details |
| `/api/v1/devices/{device_id}` | PUT | Update device |
| `/api/v1/devices/{device_id}` | DELETE | Remove device |
| `/api/v1/devices/{device_id}/status` | GET | Get device status |
| `/api/v1/devices/{device_id}/metrics` | GET | Get device metrics |
| `/api/v1/devices/farm/{farm_id}` | GET | Get devices by farm |
| `/api/v1/devices/{device_id}/reconnect` | POST | Reconnect to device |

### Job Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jobs` | GET | List jobs |
| `/api/v1/jobs` | POST | Create new job |
| `/api/v1/jobs/{job_id}` | GET | Get job details |
| `/api/v1/jobs/{job_id}` | DELETE | Cancel job |
| `/api/v1/jobs/{job_id}/status` | GET | Get job status |
| `/api/v1/jobs/{job_id}/result` | GET | Get job result |
| `/api/v1/jobs/{job_id}/retry` | POST | Retry failed job |
| `/api/v1/jobs/device/{device_id}` | GET | Get jobs for device |
| `/api/v1/jobs/batch` | POST | Create batch jobs |

### Model Deployment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/deploy` | POST | Deploy model to device |
| `/api/v1/deploy/{deploy_id}` | GET | Get deployment status |
| `/api/v1/deploy/{deploy_id}/cancel` | POST | Cancel deployment |
| `/api/v1/models` | GET | List available models |
| `/api/v1/models/{model_name}/devices` | GET | Devices with model |

### Data Synchronization

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/sync` | POST | Initiate sync operation |
| `/api/v1/sync/{sync_id}` | GET | Get sync status |
| `/api/v1/sync/{sync_id}/cancel` | POST | Cancel sync |
| `/api/v1/sync/device/{device_id}/pending` | GET | Get pending sync items |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/device/{device_id}` | Device communication channel |
| `/ws/dashboard` | Dashboard real-time updates |
| `/ws` | General WebSocket endpoint |

---

## Request/Response Examples | أمثلة الطلبات

### Register Edge Device

```bash
curl -X POST "http://localhost:8180/api/v1/devices" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Field-003-Camera-01",
    "name_ar": "كاميرا الحقل 003-01",
    "device_type": "jetson_orin_nano",
    "farm_id": "550e8400-e29b-41d4-a716-446655440000",
    "field_id": "550e8400-e29b-41d4-a716-446655440001",
    "location": {
      "latitude": 24.7136,
      "longitude": 46.6753,
      "altitude_m": 612.0
    },
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "serial_number": "ORIN-2026-001"
  }'
```

### Device Registration Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440003",
  "name": "Field-003-Camera-01",
  "name_ar": "كاميرا الحقل 003-01",
  "device_type": "jetson_orin_nano",
  "status": "offline",
  "farm_id": "550e8400-e29b-41d4-a716-446655440000",
  "field_id": "550e8400-e29b-41d4-a716-446655440001",
  "location": {
    "latitude": 24.7136,
    "longitude": 46.6753,
    "altitude_m": 612.0
  },
  "capabilities": {
    "gpu_memory_gb": 8.0,
    "cpu_cores": 6,
    "ram_gb": 8.0,
    "storage_gb": 64.0,
    "max_power_watts": 15,
    "supported_models": ["yolo26-s", "yolo26-n", "pest-detection-v2"],
    "camera_interfaces": ["csi", "usb"]
  },
  "metrics": {
    "cpu_usage_percent": 0.0,
    "gpu_usage_percent": 0.0,
    "memory_usage_percent": 0.0,
    "temperature_celsius": 0.0
  },
  "created_at": "2026-01-31T10:30:00Z"
}
```

### Create Inference Job

```bash
curl -X POST "http://localhost:8180/api/v1/jobs" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "inference",
    "device_id": "550e8400-e29b-41d4-a716-446655440002",
    "priority": "normal",
    "config": {
      "model_name": "yolo26-s",
      "confidence_threshold": 0.5,
      "input_source": "camera:csi0",
      "save_images": true,
      "batch_size": 1,
      "timeout_seconds": 300
    },
    "scheduled_at": null
  }'
```

### Deploy Model to Device

```bash
curl -X POST "http://localhost:8180/api/v1/deploy" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "550e8400-e29b-41d4-a716-446655440002",
    "model_name": "pest-detection-v2",
    "model_version": "latest",
    "model_format": "tensorrt",
    "force_update": false,
    "validate_after_deploy": true
  }'
```

### Sync Data from Device

```bash
curl -X POST "http://localhost:8180/api/v1/sync" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "550e8400-e29b-41d4-a716-446655440002",
    "direction": "upload",
    "data_types": ["inference_results", "images"],
    "since": "2026-01-30T00:00:00Z",
    "force": false
  }'
```

---

## WebSocket Protocol | بروتوكول WebSocket

### Connection

```javascript
const ws = new WebSocket('wss://edge-orchestrator:8180/ws/device/DEVICE_ID');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  switch(message.type) {
    case 'heartbeat':
      // Handle heartbeat acknowledgment
      break;
    case 'job_status':
      // Handle job status update
      break;
    case 'detection':
      // Handle real-time detection result
      break;
  }
};
```

### Message Types | أنواع الرسائل

| Type | Direction | Description |
|------|-----------|-------------|
| `heartbeat` | Device -> Cloud | Device alive signal (every 30s) |
| `metrics` | Device -> Cloud | Device metrics update |
| `job_status` | Bi-directional | Job status updates |
| `detection` | Device -> Cloud | Real-time detection result |
| `sync_progress` | Device -> Cloud | Sync operation progress |
| `deploy_progress` | Cloud -> Device | Model deployment progress |
| `alert` | Device -> Cloud | Alert notification |
| `error` | Bi-directional | Error message |

### Heartbeat Message

```json
{
  "type": "heartbeat",
  "device_id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2026-01-31T10:30:00Z",
  "payload": {
    "cpu_usage_percent": 45.2,
    "gpu_usage_percent": 82.5,
    "memory_usage_percent": 65.0,
    "temperature_celsius": 52.3,
    "inference_fps": 28.5,
    "active_job_id": "job-123"
  }
}
```

### Detection Message

```json
{
  "type": "detection",
  "device_id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2026-01-31T10:30:15Z",
  "payload": {
    "job_id": "job-123",
    "model_name": "pest-detection-v2",
    "model_version": "2.1.0",
    "inference_time_ms": 35.2,
    "detections": [
      {
        "class_name": "Red Palm Weevil",
        "class_name_ar": "سوسة النخيل الحمراء",
        "confidence": 0.92,
        "bbox": [120, 240, 280, 380]
      }
    ],
    "field_id": "550e8400-e29b-41d4-a716-446655440001",
    "location": {
      "latitude": 24.7136,
      "longitude": 46.6753
    }
  }
}
```

---

## Supported Models | النماذج المدعومة

| Model | Description | Size | Jetson Orin Nano FPS |
|-------|-------------|------|----------------------|
| `yolo26-n` | YOLO26 Nano | 6.5 MB | 83 |
| `yolo26-s` | YOLO26 Small | 22 MB | 40 |
| `yolo11-s` | YOLO11 Small | 18 MB | 45 |
| `crop-disease-v3` | Crop disease detection | 35 MB | 32 |
| `pest-detection-v2` | Pest detection | 28 MB | 38 |
| `weed-classifier-v1` | Weed classification | 15 MB | 52 |

---

## Environment Variables | متغيرات البيئة

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8180` | Service port | No |
| `HOST` | `0.0.0.0` | Bind address | No |
| `ENVIRONMENT` | `development` | Environment | No |
| `DATABASE_URL` | - | PostgreSQL connection | Yes |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection | Yes |
| `NATS_URL` | `nats://localhost:4222` | NATS server URL | Yes |
| `JWT_SECRET_KEY` | - | JWT secret (32+ chars) | Yes |
| `EDGE_HEARTBEAT_INTERVAL` | `30` | Heartbeat interval (seconds) | No |
| `EDGE_TIMEOUT_THRESHOLD` | `120` | Device timeout (seconds) | No |
| `MAX_DEVICES_PER_FARM` | `50` | Max devices per farm | No |
| `DEFAULT_MODEL` | `yolo26-s` | Default AI model | No |
| `MODEL_STORAGE_PATH` | `/models` | Model storage path | No |
| `JETSON_SSH_PORT` | `22` | SSH port for Jetson | No |
| `JETSON_API_PORT` | `8000` | API port on Jetson | No |
| `JETSON_MAX_POWER_MODE` | `15` | Max power (watts) | No |
| `SYNC_BATCH_SIZE` | `100` | Sync batch size | No |
| `SYNC_RETRY_ATTEMPTS` | `3` | Sync retry attempts | No |
| `WS_PING_INTERVAL` | `30` | WebSocket ping (seconds) | No |
| `WS_PING_TIMEOUT` | `10` | WebSocket timeout (seconds) | No |
| `WS_MAX_CONNECTIONS` | `1000` | Max WebSocket connections | No |
| `MAX_UPLOAD_SIZE_MB` | `500` | Max upload size | No |
| `LOG_LEVEL` | `INFO` | Logging level | No |

---

## Sync Protocol | بروتوكول المزامنة

### Sync Flow

```
┌─────────────────┐                    ┌────────────────────┐
│   Edge Device   │                    │ Edge Orchestrator  │
└────────┬────────┘                    └─────────┬──────────┘
         │                                       │
         │  1. Request sync (since: timestamp)   │
         │──────────────────────────────────────>│
         │                                       │
         │  2. Return pending items count        │
         │<──────────────────────────────────────│
         │                                       │
         │  3. Upload batch (100 items)          │
         │──────────────────────────────────────>│
         │                                       │
         │  4. Acknowledge batch                 │
         │<──────────────────────────────────────│
         │                                       │
         │  5. Upload next batch...              │
         │──────────────────────────────────────>│
         │                                       │
         │  6. Sync complete                     │
         │<──────────────────────────────────────│
         │                                       │
```

### Conflict Resolution

- **Last-write-wins**: Cloud data takes precedence for configuration
- **Append-only**: Detection results are always appended (no conflicts)
- **Checksum validation**: Data integrity verified on both ends

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Navigate to service directory
cd apps/services/edge-orchestrator-service

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/sahool"
export NATS_URL="nats://localhost:4222"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET_KEY="your-32-char-secret-key-here-min"

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8180 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/edge-orchestrator-service .

# Run container
docker run -p 8180:8180 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  -e JWT_SECRET_KEY=your-32-char-secret-key-here-min \
  -v /path/to/models:/models \
  sahool/edge-orchestrator-service
```

### Docker Compose

```yaml
version: '3.8'
services:
  edge-orchestrator:
    image: sahool/edge-orchestrator-service:latest
    ports:
      - "8180:8180"
    environment:
      - DATABASE_URL=postgresql://sahool:password@postgres:5432/sahool
      - REDIS_URL=redis://redis:6379
      - NATS_URL=nats://nats:4222
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./models:/models
      - ./data/uploads:/data/uploads
    depends_on:
      - postgres
      - redis
      - nats
```

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `EdgeDeviceRegistered.v1` | New device registered |
| `EdgeDeviceOnline.v1` | Device came online |
| `EdgeDeviceOffline.v1` | Device went offline |
| `EdgeJobCompleted.v1` | Job completed |
| `EdgeJobFailed.v1` | Job failed |
| `EdgeModelDeployed.v1` | Model deployed to device |
| `EdgeSyncCompleted.v1` | Sync operation completed |
| `EdgeDetection.v1` | Real-time detection result |
| `EdgeAlert.v1` | Critical alert from device |

### Consumes

| Event | Description |
|-------|-------------|
| `FieldCreated.v1` | Register field for edge devices |
| `ModelUpdated.v1` | New model version available |
| `FarmConfigUpdated.v1` | Update device configurations |
| `CriticalPestAlert.v1` | Trigger device alert mode |

---

## Kubernetes Deployment | نشر Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-orchestrator-service
  namespace: sahool
  labels:
    app: edge-orchestrator-service
    tier: integration
spec:
  replicas: 2
  selector:
    matchLabels:
      app: edge-orchestrator-service
  template:
    metadata:
      labels:
        app: edge-orchestrator-service
    spec:
      containers:
        - name: edge-orchestrator
          image: sahool/edge-orchestrator-service:latest
          ports:
            - containerPort: 8180
          env:
            - name: PORT
              value: "8180"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: sahool-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: sahool-secrets
                  key: redis-url
            - name: NATS_URL
              valueFrom:
                configMapKeyRef:
                  name: sahool-config
                  key: nats-url
            - name: JWT_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: sahool-secrets
                  key: jwt-secret-key
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8180
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8180
            initialDelaySeconds: 10
            periodSeconds: 10
          volumeMounts:
            - name: models
              mountPath: /models
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: edge-orchestrator-service
  namespace: sahool
spec:
  selector:
    app: edge-orchestrator-service
  ports:
    - port: 8180
      targetPort: 8180
  type: ClusterIP
```

---

## Testing | الاختبار

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_device_management.py -v

# Run WebSocket tests
pytest tests/test_websocket.py -v
```

---

## Troubleshooting | استكشاف الأخطاء

### Device Not Connecting

```
Error: WebSocket connection failed
```

- Verify device IP and network connectivity
- Check firewall rules for port 8180
- Ensure device has valid JWT token
- Check device time synchronization

### Model Deployment Failed

- Verify model file exists in `/models`
- Check device has sufficient storage
- Ensure TensorRT version compatibility
- Review device logs for errors

### Sync Errors

- Check network connectivity
- Verify device has pending data
- Review checksum validation errors
- Check Redis connection for sync state

### Device Timeout

- Increase `EDGE_TIMEOUT_THRESHOLD`
- Check network latency
- Verify device heartbeat interval

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: January 2026
