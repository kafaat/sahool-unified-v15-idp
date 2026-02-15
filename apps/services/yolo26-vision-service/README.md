# YOLO26 Vision Service

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/kafaat/sahool)
[![Coverage](https://img.shields.io/badge/coverage-85%25-green)](https://github.com/kafaat/sahool)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## خدمة الرؤية الحاسوبية YOLO26

> **AI-powered agricultural computer vision service for pest detection, disease diagnosis, weed identification, plant counting, ripeness classification, and object tracking.**

> **خدمة الرؤية الحاسوبية بالذكاء الاصطناعي للكشف عن الآفات وتشخيص الأمراض وتحديد الأعشاب الضارة وعد النباتات وتصنيف النضج وتتبع الكائنات.**

---

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         YOLO26 Vision Service                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Pest     │  │   Disease   │  │    Weed     │  │   Plant     │        │
│  │  Detection  │  │  Detection  │  │  Detection  │  │  Counting   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐        │
│  │                     YOLO26 Model Engine                        │        │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │        │
│  │  │ YOLO26-n│  │ YOLO26-s│  │ YOLO26-m│  │ YOLO26-l│           │        │
│  │  │ (nano)  │  │ (small) │  │ (medium)│  │ (large) │           │        │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                              │                                             │
│  ┌───────────────────────────┴───────────────────────────────────┐        │
│  │                    TensorRT / CUDA Engine                      │        │
│  │            GPU Acceleration | FP16 Half Precision              │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                              │                                             │
│  ┌───────────────────────────┴───────────────────────────────────┐        │
│  │                    NATS Event Publisher                         │        │
│  │  sahool.vision.pest_detected | disease_detected | weed_detected│        │
│  │  sahool.vision.critical_alert | analysis_completed             │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Port | المنفذ

```
8150
```

---

## Features | الميزات

### Pest Detection | كشف الآفات

- 22+ agricultural pest species (Middle East focus)
- Red Palm Weevil priority detection (سوسة النخيل الحمراء)
- Severity level assessment (NONE, LOW, MEDIUM, HIGH, CRITICAL)
- Life stage identification (egg, larva, pupa, adult)
- Bilingual treatment recommendations

### Disease Detection | كشف الأمراض

- 34+ crop diseases including nutrient deficiencies
- Wheat rust, powdery mildew, bacterial infections
- Affected area percentage calculation
- Spread risk assessment
- Treatment recommendations (Arabic/English)

### Weed Detection | كشف الأعشاب الضارة

- 12+ weed species database
- Coverage percentage calculation
- Growth stage identification
- Regional weed species (Middle East focus)

### Plant Counting | عد النباتات

- Density map generation
- Plants per square meter calculation
- Grid-based counting
- Average spacing computation

### Ripeness Classification | تصنيف النضج

- 5 ripeness stages (unripe to overripe)
- Fruit type specific models
- Days-to-optimal estimation
- Harvest readiness percentage

### Leaf Segmentation | تجزئة الأوراق

- Instance segmentation masks
- Leaf area calculation (pixels/m²)
- LAI estimation
- Health indicator per leaf

### Object Tracking | تتبع الكائنات

- ByteTrack / BotSort algorithms
- Persistent track IDs
- Velocity estimation
- Multi-frame tracking

---

## Model Variants | إصدارات النموذج

| Variant | Size | Parameters | FPS (RTX 3090) | mAP@0.5 | Use Case |
|---------|------|------------|----------------|---------|----------|
| **YOLO26-n** (nano) | 6.5 MB | 3.2M | 450+ | 0.78 | Edge devices, real-time |
| **YOLO26-s** (small) | 22 MB | 11.2M | 280+ | 0.84 | Balanced performance |
| **YOLO26-m** (medium) | 49 MB | 25.9M | 180+ | 0.88 | **Default** - Best accuracy/speed |
| **YOLO26-l** (large) | 85 MB | 43.7M | 120+ | 0.91 | Maximum accuracy |
| **YOLO26-x** (xlarge) | 131 MB | 68.2M | 80+ | 0.93 | Research & validation |

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Comprehensive health with GPU status |
| `/metrics` | GET | Prometheus metrics |

### Detection Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/detect/pest` | POST | Detect pests in image |
| `/api/v1/detect/disease` | POST | Detect diseases in image |
| `/api/v1/detect/weed` | POST | Detect weeds in image |
| `/api/v1/detect/batch` | POST | Batch detection (multiple images) |

### Analysis Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/count/plants` | POST | Count plants in image |
| `/api/v1/classify/ripeness` | POST | Classify fruit ripeness |
| `/api/v1/segment/leaves` | POST | Segment leaves |
| `/api/v1/track/objects` | POST | Track objects across frames |

### Cache Management | إدارة الكاش

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/batch/cache/stats` | GET | Get cache statistics (hit rate, memory usage) |
| `/api/v1/batch/cache/clear` | POST | Clear all cached results |

Cache supports pattern-based invalidation by `task` (pest/disease/weed) and `variant` (n/s/m/l/x), allowing selective cache clearing without flushing the entire cache.

يدعم الكاش إبطال بالأنماط حسب `task` (آفات/أمراض/أعشاب) و`variant` (n/s/m/l/x)، مما يتيح مسح انتقائي دون حذف الكاش بالكامل.

### Model Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/models` | GET | List available models |
| `/api/v1/models/{variant}/info` | GET | Get model information |
| `/api/v1/models/warmup` | POST | Warm up model for inference |

---

## Request/Response Examples | أمثلة الطلبات

### Pest Detection Request

```bash
curl -X POST "http://localhost:8150/api/v1/detect/pest" \
  -H "Authorization: Bearer <token>" \
  -F "image=@field_image.jpg" \
  -F "confidence_threshold=0.25" \
  -F "model_variant=m" \
  -F "include_recommendations=true"
```

### Pest Detection Response

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-31T10:30:00Z",
  "processing_time_ms": 45.2,
  "model_variant": "m",
  "image_metadata": {
    "width": 1920,
    "height": 1080,
    "channels": 3
  },
  "detections": [
    {
      "class_id": 0,
      "class_name_en": "Red Palm Weevil",
      "class_name_ar": "سوسة النخيل الحمراء",
      "scientific_name": "Rhynchophorus ferrugineus",
      "confidence": 0.92,
      "bbox": {
        "x1": 120,
        "y1": 240,
        "x2": 280,
        "y2": 380
      },
      "severity": "critical",
      "life_stage": "adult",
      "recommended_action_en": "Immediate treatment required. Apply pheromone traps and contact agricultural authority.",
      "recommended_action_ar": "يتطلب العلاج الفوري. استخدم مصائد الفيرومونات واتصل بالسلطة الزراعية."
    }
  ],
  "total_count": 1,
  "severity_summary": {
    "critical": 1
  }
}
```

---

## Supported Classes | الفئات المدعومة

### Pest Classes (22+) | فئات الآفات

| ID | English | Arabic | Scientific Name |
|----|---------|--------|-----------------|
| 0 | Red Palm Weevil | سوسة النخيل الحمراء | Rhynchophorus ferrugineus |
| 1 | Aphid | المن | Aphidoidea |
| 2 | Whitefly | الذبابة البيضاء | Aleyrodidae |
| 3 | Spider Mite | العنكبوت الأحمر | Tetranychidae |
| 4 | Thrips | التربس | Thysanoptera |
| 5 | Leaf Miner | صانعة الأنفاق | Agromyzidae |
| 6 | Cutworm | الدودة القارضة | Noctuidae |
| 7 | Armyworm | دودة الحشد | Spodoptera |
| 8 | Fruit Fly | ذبابة الفاكهة | Tephritidae |
| 11 | Locust | الجراد | Acrididae |
| 12 | Date Moth | فراشة التمر | Ephestia cautella |

### Disease Classes (34+) | فئات الأمراض

| ID | English | Arabic | Scientific Name |
|----|---------|--------|-----------------|
| 0 | Wheat Rust | صدأ القمح | Puccinia |
| 1 | Powdery Mildew | البياض الدقيقي | Erysiphales |
| 2 | Downy Mildew | البياض الزغبي | Peronosporaceae |
| 3 | Early Blight | اللفحة المبكرة | Alternaria solani |
| 4 | Late Blight | اللفحة المتأخرة | Phytophthora infestans |
| 28 | Date Palm Bayoud | مرض البيوض | Fusarium oxysporum |
| 31 | Nitrogen Deficiency | نقص النيتروجين | - |
| 32 | Phosphorus Deficiency | نقص الفوسفور | - |

### Weed Classes (12+) | فئات الأعشاب الضارة

| ID | English | Arabic | Scientific Name |
|----|---------|--------|-----------------|
| 0 | Wild Oat | الشوفان البري | Avena fatua |
| 1 | Bermuda Grass | النجيل | Cynodon dactylon |
| 6 | Nutsedge | السعد | Cyperus |
| 9 | Ryegrass | الزوان | Lolium |

---

## Environment Variables | متغيرات البيئة

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8150` | Service port | No |
| `HOST` | `0.0.0.0` | Bind address | No |
| `ENVIRONMENT` | `development` | Environment | No |
| `DATABASE_URL` | - | PostgreSQL connection | Yes |
| `REDIS_URL` | - | Redis connection | Yes |
| `NATS_URL` | - | NATS server URL | Yes |
| `JWT_SECRET_KEY` | - | JWT secret (32+ chars) | Yes |
| `MODEL_BASE_PATH` | `/models` | Path to YOLO26 models | No |
| `DEFAULT_MODEL_VARIANT` | `m` | Default model (n/s/m/l/x) | No |
| `ENABLE_TENSORRT` | `false` | Enable TensorRT optimization | No |
| `DEVICE` | `cuda:0` | Inference device | No |
| `HALF_PRECISION` | `true` | Use FP16 for faster inference | No |
| `DEFAULT_CONFIDENCE_THRESHOLD` | `0.25` | Detection confidence | No |
| `DEFAULT_IOU_THRESHOLD` | `0.45` | NMS IoU threshold | No |
| `MAX_DETECTIONS` | `300` | Max detections per image | No |
| `DEFAULT_IMAGE_SIZE` | `640` | Input image size | No |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max upload size | No |
| `LOG_LEVEL` | `INFO` | Logging level | No |

---

## Performance Benchmarks | معايير الأداء

### GPU Performance (NVIDIA RTX 3090)

| Model | Batch Size | Resolution | Latency (ms) | Throughput (FPS) |
|-------|------------|------------|--------------|------------------|
| YOLO26-n | 1 | 640x640 | 2.2 | 450 |
| YOLO26-s | 1 | 640x640 | 3.6 | 280 |
| YOLO26-m | 1 | 640x640 | 5.5 | 180 |
| YOLO26-l | 1 | 640x640 | 8.3 | 120 |
| YOLO26-x | 1 | 640x640 | 12.5 | 80 |

### Edge Performance (Jetson Orin Nano)

| Model | Batch Size | Resolution | Latency (ms) | Throughput (FPS) |
|-------|------------|------------|--------------|------------------|
| YOLO26-n | 1 | 640x640 | 12 | 83 |
| YOLO26-s | 1 | 640x640 | 25 | 40 |
| YOLO26-m | 1 | 640x640 | 45 | 22 |

### Detection Accuracy (mAP@0.5)

| Task | YOLO26-n | YOLO26-s | YOLO26-m | YOLO26-l |
|------|----------|----------|----------|----------|
| Pest Detection | 0.76 | 0.82 | 0.87 | 0.90 |
| Disease Detection | 0.74 | 0.80 | 0.86 | 0.89 |
| Weed Detection | 0.78 | 0.84 | 0.88 | 0.91 |

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Navigate to service directory
cd apps/services/yolo26-vision-service

# Install dependencies
pip install -r requirements.txt

# Download models (if not available)
python scripts/download_models.py

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8150 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/yolo26-vision-service .

# Run with GPU support
docker run --gpus all -p 8150:8150 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  -e JWT_SECRET_KEY=your-32-char-secret-key-here-min \
  -v /path/to/models:/models \
  sahool/yolo26-vision-service
```

### Docker Compose

```yaml
version: '3.8'
services:
  yolo26-vision-service:
    image: sahool/yolo26-vision-service:latest
    ports:
      - "8150:8150"
    environment:
      - DATABASE_URL=postgresql://sahool:password@postgres:5432/sahool
      - REDIS_URL=redis://redis:6379
      - NATS_URL=nats://nats:4222
      - DEVICE=cuda:0
      - ENABLE_TENSORRT=true
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## Events (NATS) | الأحداث

The service publishes events to NATS after each detection. Event models are defined in `shared/events/vision_events.py` and published via `src/events/publisher.py`.

### Produces | يُنتج

| NATS Subject | Event | Description |
|-------------|-------|-------------|
| `sahool.vision.pest_detected` | PestDetectedEvent | Pest identified in image with severity & recommendations |
| `sahool.vision.disease_detected` | VisionDiseaseDetectedEvent | Disease detected with affected area % & health score |
| `sahool.vision.weed_detected` | WeedDetectedEvent | Weed species identified with coverage % |
| `sahool.vision.plant_count_completed` | PlantCountCompletedEvent | Plant counting results with density map |
| `sahool.vision.critical_alert` | VisionCriticalAlertEvent | Critical pest alert (RPW, locust) - auto-escalates |
| `sahool.vision.analysis_started` | VisionAnalysisStartedEvent | Analysis job started |
| `sahool.vision.analysis_completed` | VisionAnalysisCompletedEvent | Analysis completed with results summary |
| `sahool.vision.analysis_failed` | VisionAnalysisFailedEvent | Analysis failed with error details |

### Consumes | يستهلك

| NATS Subject | Event | Description |
|-------------|-------|-------------|
| `sahool.edge.data_collected` | DataCollectedEvent | Process new field image from edge device |
| `sahool.field.created` | FieldCreatedEvent | Register field for monitoring |

### Critical Alerts | تنبيهات حرجة

Critical alerts are auto-published when:
- **Red Palm Weevil** (سوسة النخيل الحمراء) detected - class_id 0
- **Locust** (الجراد) detected - class_id 11
- **Severe disease outbreak** - 3+ critical detections or health_score < 30

These trigger `sahool.vision.critical_alert` with `priority: 1` and `auto_notify_agronomist: true`.

---

## Testing | الاختبار

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test suite
pytest tests/test_pest_detection.py -v

# Run performance tests
pytest tests/test_performance.py -v --benchmark
```

---

## Troubleshooting | استكشاف الأخطاء

### GPU Not Detected

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check GPU memory
nvidia-smi
```

### Model Loading Issues

```bash
# Verify model files exist
ls -la /models/

# Check model integrity
python scripts/verify_models.py
```

### Out of Memory

- Reduce batch size
- Use smaller model variant (n or s)
- Enable half precision (FP16)
- Reduce image size

---

## Dependencies | التبعيات

- **PyTorch** >= 2.0
- **Ultralytics** (YOLO framework)
- **OpenCV** >= 4.8
- **FastAPI** >= 0.126.0
- **CUDA** >= 11.8 (for GPU)
- **TensorRT** >= 8.6 (optional)

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: February 2026
