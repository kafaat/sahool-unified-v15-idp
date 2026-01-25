# Ground Vision Service - خدمة الرؤية الأرضية

High-frequency agricultural monitoring using tower-mounted cameras, integrating with SAHOOL's satellite and IoT infrastructure.

**Based on:** Qin et al. (2026) - "A Real-Time, High-Frequency, Parcel-Level Agricultural Monitoring Framework: Integrating Tower-Based Cameras and Artificial Intelligence"

## Features

- **Quaternion-based Georeferencing** - Direct pixel-to-geocoordinate transformation
- **YOLO Operation Detection** - Detect agricultural operations (harvest, tillage, irrigation, etc.)
- **MLLM Crop Timeline Analysis** - Semantic understanding of crop growth stages
- **Anomaly Detection** - Detect crop stress, pest infestation, unauthorized activity
- **NATS Event Integration** - Publish/subscribe to SAHOOL event bus

## API Endpoints

### Health
- `GET /healthz` - Liveness probe
- `GET /readyz` - Readiness probe
- `GET /metrics` - Prometheus metrics

### Cameras
- `POST /api/v1/cameras` - Register a new tower camera
- `GET /api/v1/cameras` - List registered cameras
- `GET /api/v1/cameras/{camera_id}` - Get camera details

### Frames
- `POST /api/v1/frames/process` - Process a captured frame

### Detections
- `GET /api/v1/detections` - List detected operations
- `GET /api/v1/detections/{detection_id}` - Get detection details

### Timeline
- `POST /api/v1/timeline/analyze` - Analyze crop timeline from frames
- `GET /api/v1/timeline/{field_id}` - Get crop timeline for a field

### Anomalies
- `GET /api/v1/anomalies` - List detected anomalies
- `GET /api/v1/anomalies/{anomaly_id}` - Get anomaly details
- `POST /api/v1/anomalies/{anomaly_id}/acknowledge` - Acknowledge anomaly
- `POST /api/v1/anomalies/{anomaly_id}/resolve` - Resolve anomaly

## NATS Events

### Published Events
- `sahool.{tenant_id}.ground_vision.frame_captured` - New frame captured
- `sahool.{tenant_id}.ground_vision.operation_detected` - Operation detected
- `sahool.{tenant_id}.ground_vision.growth_stage_changed` - Growth stage transition
- `sahool.{tenant_id}.ground_vision.anomaly_detected` - Anomaly detected
- `sahool.{tenant_id}.ground_vision.timeline_updated` - Timeline analysis completed

### Subscribed Events
- `sahool.*.satellite.ndvi_computed` - Correlate with satellite NDVI
- `sahool.*.weather.forecast_updated` - Adjust detection thresholds
- `sahool.*.fields.boundary_updated` - Update camera-field mapping

## Environment Variables

```bash
# Server
PORT=8180
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool

# NATS
NATS_URL=nats://user:pass@nats:4222

# Models
SAM_CHECKPOINT_PATH=/models/sam_vit_h.pth
SAM_DEVICE=cuda
YOLO_MODEL_PATH=/models/yolo_agri_ops.pt

# MLLM
MLLM_PROVIDER=anthropic  # or openai, ollama
ANTHROPIC_API_KEY=your_key
OLLAMA_BASE_URL=http://ollama:11434

# Processing
CHANGE_DETECTION_THRESHOLD=0.15
SAM_IOU_THRESHOLD=0.85
MAX_FRAMES_PER_ANALYSIS=5
```

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python -m uvicorn src.main:app --reload --port 8180
```

### Docker

```bash
# Build image
docker build -t ground-vision-service .

# Run container
docker run -p 8180:8180 \
  -e DATABASE_URL=postgresql://... \
  -e NATS_URL=nats://... \
  ground-vision-service
```

### Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Architecture

```
src/
├── main.py                 # FastAPI entry point
├── models/                 # Data models
│   ├── camera.py          # Tower camera models
│   ├── detection.py       # Operation detection models
│   ├── timeline.py        # Crop timeline models
│   └── anomaly.py         # Anomaly detection models
├── core/                   # Core algorithms
│   ├── geo_projection.py  # Quaternion-based georeferencing
│   ├── change_detection.py # Frame change detection
│   └── operation_classifier.py # YOLO operation detection
├── intelligence/           # AI modules
│   ├── mllm_reasoner.py   # MLLM crop timeline analysis
│   └── anomaly_detector.py # Anomaly detection
└── events/                 # NATS integration
    ├── publishers.py      # Event publishers
    └── subscribers.py     # Event subscribers
```

## License

Proprietary - KAFAAT
