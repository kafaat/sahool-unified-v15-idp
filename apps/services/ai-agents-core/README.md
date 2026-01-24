# AI Agents Core | نواة وكلاء الذكاء الاصطناعي

> Hierarchical Multi-Agent AI System for Smart Agriculture

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](package.json)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0+-red.svg)](https://fastapi.tiangolo.com)

## Overview | نظرة عامة

AI Agents Core provides a hierarchical multi-agent AI system for agricultural intelligence with a 4-layer architecture enabling distributed decision-making, real-time edge processing, and continuous learning.

نواة وكلاء الذكاء الاصطناعي توفر نظام وكلاء ذكاء اصطناعي هرمي للزراعة الذكية مع بنية من 4 طبقات تمكن من اتخاذ القرارات الموزعة والمعالجة الفورية والتعلم المستمر.

## Features | الميزات

- **4-Layer Agent Architecture**: Edge, Specialist, Coordinator, Learning agents
- **Real-time Edge Processing**: < 100ms response time for IoT and mobile
- **Disease Detection**: CNN-based plant disease diagnosis
- **Yield Prediction**: Ensemble model with 4 prediction components
- **Irrigation Advisory**: Smart water management recommendations
- **Weather Analysis**: Agricultural threshold monitoring
- **Reinforcement Learning**: Continuous improvement from feedback
- **Bilingual Support**: Arabic and English throughout

## Architecture | البنية

```
Layer 4: LEARNING (Continuous Improvement)
    └── FeedbackLearnerAgent (Reinforcement Learning)

Layer 3: COORDINATOR (Decision Integration)
    └── MasterCoordinatorAgent (Multi-agent orchestration)

Layer 2: SPECIALIST (Domain Expertise)
    ├── DiseaseExpertAgent (Plant health diagnosis)
    ├── IrrigationAdvisorAgent (Water management)
    ├── YieldPredictorAgent (Crop production)
    └── WeatherAnalystAgent (Climate analysis)

Layer 1: EDGE (Real-time Processing < 100ms)
    ├── IoTAgent (Sensor processing)
    ├── MobileAgent (On-device mobile processing)
    └── DroneAgent (Aerial field analysis)
```

## Directory Structure | هيكل المجلدات

```
ai-agents-core/
├── Dockerfile
├── requirements.txt
├── requirements-test.txt
├── pytest.ini
├── src/
│   ├── main.py                     # FastAPI entry point
│   ├── agents/
│   │   ├── base_agent.py           # Abstract base class
│   │   ├── coordinator/
│   │   │   └── master_coordinator.py
│   │   ├── specialist/
│   │   │   ├── disease_expert_agent.py
│   │   │   ├── irrigation_advisor_agent.py
│   │   │   ├── weather_analyst_agent.py
│   │   │   └── yield_predictor_agent.py
│   │   ├── edge/
│   │   │   ├── mobile_agent.py
│   │   │   ├── iot_agent.py
│   │   │   └── drone_agent.py
│   │   └── learning/
│   │       └── feedback_learner.py
│   └── models/
│       ├── disease_cnn.py
│       ├── yield_ensemble.py
│       ├── crop_parameters.py
│       └── config.yaml
└── tests/
    ├── unit/
    ├── integration/
    └── mocks/
```

## API Endpoints | نقاط النهاية

### Health Check | فحص الصحة

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/healthz` | GET | Kubernetes liveness probe | فحص الحياة |
| `/readyz` | GET | Kubernetes readiness probe | فحص الجاهزية |

**GET /healthz**
```json
{
    "status": "healthy",
    "service": "ai-agents-core",
    "timestamp": "2026-01-24T10:30:00Z"
}
```

**GET /readyz**
```json
{
    "status": "ready",
    "service": "ai-agents-core",
    "version": "16.0.0",
    "checks": {"service": "ready"}
}
```

### Analysis | التحليل

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/api/v1/analyze` | POST | Full field analysis | تحليل كامل للحقل |

**POST /api/v1/analyze**

Request:
```json
{
    "field_id": "field_001",
    "crop_type": "wheat",
    "sensor_data": {
        "soil_moisture": 0.35,
        "temperature": 28.5,
        "humidity": 65
    },
    "weather_data": {
        "forecast": [...],
        "rain_probability": 10
    },
    "image_data": {
        "type": "leaf_image",
        "data": "base64..."
    }
}
```

Response:
```json
{
    "success": true,
    "analysis": {
        "primary_action": {...},
        "supporting_actions": [...],
        "conflicts_resolved": 0,
        "confidence": 0.85,
        "summary_ar": "توصية بالري خلال 24 ساعة"
    },
    "timestamp": "2026-01-24T10:30:00Z"
}
```

### Edge Agents | وكلاء الحافة

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/api/v1/edge/sensor` | POST | IoT sensor processing | معالجة بيانات المستشعرات |
| `/api/v1/edge/mobile` | POST | Mobile edge processing | معالجة الجوال |

**POST /api/v1/edge/sensor**
```json
{
    "device_id": "sensor_001",
    "sensor_type": "soil_moisture",
    "value": 0.25,
    "timestamp": "2026-01-24T10:30:00Z"
}
```

### Feedback & Learning | التغذية الراجعة والتعلم

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/api/v1/feedback` | POST | Submit recommendation feedback | إرسال تغذية راجعة |

**POST /api/v1/feedback**
```json
{
    "recommendation_id": "rec_001",
    "agent_id": "disease_expert",
    "action_type": "treatment",
    "rating": 0.8,
    "success": true,
    "actual_result": {"yield_improvement": "15%"},
    "comments": "Treatment worked well"
}
```

### System Status | حالة النظام

| Endpoint | Method | Purpose | الوصف |
|----------|--------|---------|-------|
| `/api/v1/system/status` | GET | System metrics | مقاييس النظام |
| `/api/v1/agents/{agent_id}/metrics` | GET | Agent metrics | مقاييس الوكيل |

## Agents | الوكلاء

### Specialist Agents | الوكلاء المتخصصون

#### Disease Expert Agent | وكيل خبير الأمراض
- **Type**: Utility-Based
- **Supported Crops**: Wheat, Barley, Tomato, Potato, Coffee, Date Palm, Mango
- **Diseases**: Leaf Rust, Late Blight, Bayoud Disease, Anthracnose
- **Output**: Treatment recommendations with cost-benefit analysis

#### Irrigation Advisor Agent | وكيل مستشار الري
- **Type**: Goal-Based
- **Calculation**: ETc = ET0 × Kc (FAO-56)
- **Output**: Water amount (mm), urgency, duration

#### Yield Predictor Agent | وكيل توقع المحصول
- **Type**: Utility-Based
- **Ensemble**: NDVI (40%) + GDD (30%) + Water (20%) + Soil (10%)
- **Output**: Yield prediction with confidence interval

#### Weather Analyst Agent | وكيل محلل الطقس
- **Type**: Model-Based
- **Thresholds**: Frost (≤2°C), Heat (≥38°C), Drought (14+ days)
- **Output**: Agricultural alerts and GDD tracking

### Edge Agents | وكلاء الحافة

| Agent | Response Time | Purpose |
|-------|--------------|---------|
| IoT Agent | < 50ms | Sensor anomaly detection |
| Mobile Agent | < 100ms | Offline quick analysis |
| Drone Agent | < 100ms | Aerial NDVI mapping |

## Configuration | الإعدادات

### Environment Variables | متغيرات البيئة

```bash
# Server
PORT=8122
ENVIRONMENT=development|staging|production
LOG_LEVEL=INFO|DEBUG

# Redis (Rate Limiting)
REDIS_URL=redis://redis:6379

# NATS (Events)
NATS_URL=nats://nats:4222
```

### Rate Limiting | تحديد المعدل

| Tier | Requests/min | Requests/hour |
|------|-------------|---------------|
| Free | 30 | 500 |
| Standard | 60 | 2,000 |
| Premium | 120 | 5,000 |
| Internal | 1,000 | 50,000 |

## Development | التطوير

### Prerequisites | المتطلبات

- Python 3.11+
- Docker (optional)

### Installation | التثبيت

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m uvicorn src.main:app --host 0.0.0.0 --port 8122 --reload
```

### Docker

```bash
# Build
docker build -t sahool/ai-agents-core:latest .

# Run
docker run -p 8122:8122 \
  -e ENVIRONMENT=development \
  -e LOG_LEVEL=INFO \
  sahool/ai-agents-core:latest
```

### Testing | الاختبارات

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_disease_expert_agent.py -v
pytest -m integration
```

## ML Models | نماذج التعلم الآلي

### Disease Detection CNN
- **Input**: 224x224 images
- **Output**: Disease ID + confidence
- **Features**: TTA (5 augmentations)

### Yield Ensemble
- **Components**: NDVI, GDD, Water Balance, Soil Quality
- **Output**: Yield prediction with uncertainty

### Crop Parameters
- GDD requirements per crop
- Optimal NDVI ranges
- Water needs by growth stage

## Performance | الأداء

| Layer | Target Response Time |
|-------|---------------------|
| Edge Agents | < 100ms |
| Specialist Agents | < 500ms |
| Coordinator | < 2,000ms |
| API Endpoints | < 5,000ms |

## Kubernetes Deployment | النشر على Kubernetes

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: ai-agents-core
    image: sahool/ai-agents-core:latest
    ports:
    - containerPort: 8122
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8122
      initialDelaySeconds: 10
      periodSeconds: 30
    readinessProbe:
      httpGet:
        path: /readyz
        port: 8122
      initialDelaySeconds: 5
      periodSeconds: 10
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
```

## Related Services | الخدمات المرتبطة

- **field-management-service**: Field data source
- **weather-service**: Weather data provider
- **notification-service**: Alert delivery
- **iot-gateway**: Sensor data ingestion

## License | الترخيص

Proprietary - KAFAAT © 2026

---

**Version**: 1.0.0
**Port**: 8122
**Last Updated**: January 2026
