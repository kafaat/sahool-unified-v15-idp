# YOLO26 Vision Service

**Type:** Python/FastAPI | **Port:** 8150 | **Version:** 16.0.0 | **Status:** Active

AI-powered agricultural computer vision service for pest detection, disease diagnosis, weed identification, plant counting, ripeness classification, and object tracking.

خدمة الرؤية الحاسوبية بالذكاء الاصطناعي للكشف عن الآفات وتشخيص الأمراض وتحديد الأعشاب الضارة وعد النباتات وتصنيف النضج وتتبع الكائنات.

---

## Overview

The YOLO26 Vision Service provides production-grade computer vision inference for agricultural field operations. It runs five model variants (nano through xlarge) on NVIDIA GPU hardware with optional TensorRT optimization and FP16 half-precision inference. All detections produce bilingual (Arabic/English) results with severity assessments and treatment recommendations. Critical pest detections (Red Palm Weevil, Locust) auto-escalate via NATS alerts.

---

## Architecture

```
FastAPI Application Layer
├── Detection Endpoints (pest, disease, weed)
├── Analysis Endpoints (counting, ripeness, segmentation, tracking)
├── Batch Endpoints (multi-image processing)
└── Model Management Endpoints (version registry)
    ↓
Model Manager & Inference Engine
├── YOLO26 Model Loader (5 variants: n/s/m/l/x)
├── LRU Cache (5 models max in-memory)
├── TensorRT Optimization (optional)
└── GPU Memory Management (FP16 half-precision)
    ↓
External Integrations (Optional)
├── PostgreSQL (asyncpg), Redis, NATS
└── NVIDIA GPU (CUDA 12.1)
```

**Base Image:** `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` (5-stage Dockerfile includes a CPU-only variant)

---

## Model Variants

| Variant | Size | Parameters | Latency (RTX 3090) | mAP@0.5 | Best For |
|---------|------|------------|-------------------|---------|----------|
| Nano (n) | 6.5 MB | 3.2M | 2.2 ms | 0.78 | Edge devices, real-time |
| Small (s) | 22 MB | 11.2M | 3.6 ms | 0.84 | Balanced performance |
| **Medium (m)** | 49 MB | 25.9M | 5.5 ms | 0.88 | **Default** |
| Large (l) | 85 MB | 43.7M | 8.3 ms | 0.91 | High accuracy |
| XLarge (x) | 131 MB | 68.2M | 12.5 ms | 0.93 | Research |

**Edge Performance (Jetson Orin Nano):** Nano 12ms/83fps, Small 25ms/40fps, Medium 45ms/22fps

---

## Detection Tasks

| Task | Classes | Description |
|------|---------|-------------|
| Pest Detection | 22 species | Red Palm Weevil, aphid, whitefly, locust, spider mite, etc. |
| Disease Detection | 34 diseases | Wheat rust, powdery mildew, blight, nutrient deficiencies, etc. |
| Weed Detection | 12 species | Wild oat, bermuda grass, nutsedge, ryegrass, etc. |
| Plant Counting | 1 class | Grid-based density mapping with GSD support |
| Ripeness Classification | 5 stages | Unripe → early → half → ripe → overripe |
| Leaf Segmentation | 1 class | Instance segmentation + LAI calculation |
| Object Tracking | Generic | ByteTrack/BoT-SORT with persistent IDs |

---

## API Endpoints

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /healthz` | GET | Kubernetes liveness probe |
| `GET /readyz` | GET | Kubernetes readiness probe |
| `GET /health` | GET | Comprehensive health with GPU status |
| `GET /metrics` | GET | Prometheus metrics |

### Detection

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/detect/pest` | POST | Pest detection with severity and treatment recommendations |
| `POST /api/v1/detect/disease` | POST | Disease detection with affected area percentage |
| `POST /api/v1/detect/weed` | POST | Weed detection with coverage percentage |
| `POST /api/v1/detect/batch` | POST | Batch detection (multiple images) |

### Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/count/plants` | POST | Plant counting with density map |
| `POST /api/v1/classify/ripeness` | POST | 5-stage fruit ripeness classification |
| `POST /api/v1/segment/leaves` | POST | Leaf segmentation and LAI estimation |
| `POST /api/v1/track/objects` | POST | Object tracking across frames |
| `DELETE /api/v1/track/{tracker_id}` | DELETE | Clear tracking session |

### Batch & Cache

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/v1/batch/cache/stats` | GET | Cache hit rate and memory usage |
| `POST /api/v1/batch/cache/clear` | POST | Clear cached results (supports pattern invalidation by task/variant) |
| `GET /api/v1/batch/status` | GET | Batch queue status |

### Model Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/v1/models` | GET | List available models |
| `GET /api/v1/models/{variant}/info` | GET | Model metadata |
| `POST /api/v1/models/warmup` | POST | Preload model for inference |
| `GET /api/v1/models/loaded` | GET | Currently loaded models |
| `POST /api/v1/models/register` | POST | Register new model version |
| `GET /api/v1/models/compare/{task}/{v1}/{v2}` | GET | Compare two model versions |

---

## NATS Events

### Produces

| Subject | Trigger |
|---------|---------|
| `sahool.vision.pest_detected` | Pest identified with severity and recommendations |
| `sahool.vision.disease_detected` | Disease detected with affected area percentage |
| `sahool.vision.weed_detected` | Weed species identified with coverage percentage |
| `sahool.vision.critical_alert` | Red Palm Weevil or Locust detected (priority: 1, auto-notify agronomist) |
| `sahool.vision.plant_count_completed` | Plant counting results with density map |
| `sahool.vision.analysis_completed` | Analysis job completed (ripeness, segmentation) |
| `sahool.vision.analysis_started` | Analysis job started |
| `sahool.vision.analysis_failed` | Analysis failed with error details |

### Consumes

| Subject | Action |
|---------|--------|
| `sahool.edge.data_collected` | Process new field image from edge device |
| `sahool.field.created` | Register field for monitoring |

---

## Environment Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8150` | Service port | No |
| `DATABASE_URL` | - | PostgreSQL connection | Yes |
| `REDIS_URL` | - | Redis connection | Yes |
| `NATS_URL` | - | NATS server URL | Yes |
| `JWT_SECRET_KEY` | - | JWT secret (32+ chars) | Yes |
| `MODEL_BASE_PATH` | `/models` | Path to YOLO26 models | No |
| `DEFAULT_MODEL_VARIANT` | `m` | Default model (n/s/m/l/x) | No |
| `DEVICE` | `cuda:0` | Inference device | No |
| `HALF_PRECISION` | `true` | FP16 for faster inference | No |
| `ENABLE_TENSORRT` | `false` | TensorRT optimization | No |
| `MODEL_CACHE_SIZE` | `5` | Max models in memory | No |
| `DEFAULT_CONFIDENCE_THRESHOLD` | `0.25` | Detection confidence | No |
| `DEFAULT_IOU_THRESHOLD` | `0.45` | NMS IoU threshold | No |
| `MAX_DETECTIONS` | `300` | Max detections per image | No |
| `DEFAULT_IMAGE_SIZE` | `640` | Input image size | No |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max upload file size | No |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | 2.2.0 (CUDA 12.1) | Deep learning framework |
| ultralytics | 8.1.0–9.0.0 | YOLO model framework |
| opencv-python-headless | 4.8.0–5.0.0 | Image processing |
| asyncpg | 0.29.0–0.31.0 | PostgreSQL async driver |
| nats-py | 2.6.0–3.0.0 | NATS event publishing |
| redis | 7.1.0–8.0.0 | Result caching |
| onnxruntime-gpu | 1.16.0–2.0.0 | ONNX inference (x86_64) |

---

## Error Handling

26 bilingual error codes across 8 categories: Validation (E1001–E1006), Model (E2001–E2005), Processing (E3001–E3004), Resource (E4001–E4004), External (E5001–E5003), Rate Limit (E6001–E6002), Timeout (E7001–E7002), Auth (E8001–E8003). Circuit breaker and retry patterns applied to all external dependencies.

---

## Admin Integration

- **Makefile targets:** `make dev-vision`, `make test-vision`, `make build-ai`
- **CI workflow:** `.github/workflows/ci-yolo26-vision.yml`
- **Docker Compose:** Include `--profile vision` or use `docker-compose.yml` service definition with `deploy.resources.reservations.devices` for GPU
- **Kong route:** `/api/v1/vision/*` proxied to `yolo26-vision-service:8150`
- **Kubernetes:** Requires NVIDIA GPU device plugin; VRAM requirement scales from 512 MB (nano) to 4 GB (xlarge)

---

**Version:** 16.0.0 | **Last Updated:** February 2026 | **License:** Proprietary - KAFAAT
