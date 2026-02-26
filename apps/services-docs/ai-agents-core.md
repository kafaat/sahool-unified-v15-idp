# AI Agents Core Service

**Port**: 8161 | **Type**: Python (FastAPI) | **Version**: 16.0.0

Hierarchical multi-agent AI system for smart agricultural intelligence. Provides a 4-layer agent architecture enabling distributed decision-making, real-time edge processing, and continuous reinforcement learning.

---

## Overview

`ai-agents-core` exposes SAHOOL's layered agent system as a REST API. It coordinates specialist agents (disease diagnosis, irrigation, yield prediction, weather analysis) through a master coordinator, and provides sub-100 ms edge agents for IoT sensors, mobile devices, and drone telemetry. A feedback-learning agent improves recommendations continuously from field outcomes.

---

## Architecture

```
Layer 4: LEARNING
    └── FeedbackLearnerAgent  (Reinforcement Learning from outcomes)

Layer 3: COORDINATOR
    └── MasterCoordinatorAgent  (multi-agent orchestration, conflict resolution)

Layer 2: SPECIALIST
    ├── DiseaseExpertAgent   (CNN-based plant disease diagnosis, 7 crops)
    ├── IrrigationAdvisorAgent (ETc = ET0 × Kc, FAO-56)
    ├── YieldPredictorAgent  (Ensemble: NDVI 40% + GDD 30% + Water 20% + Soil 10%)
    └── WeatherAnalystAgent  (GDD tracking, threshold alerts)

Layer 1: EDGE  (< 100 ms response)
    ├── IoTAgent     (sensor anomaly detection, < 50 ms)
    ├── MobileAgent  (offline quick analysis, < 100 ms)
    └── DroneAgent   (aerial NDVI mapping, < 100 ms)
```

Rate limiting is applied per tier (Standard/Premium/Internal) via shared Redis middleware.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe (service + version) |

### Analysis

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/analyze` | Full field analysis through all specialist agents |

**Request body**:
```json
{
  "field_id": "field_001",
  "crop_type": "wheat",
  "sensor_data": {"soil_moisture": 0.35, "temperature": 28.5, "humidity": 65},
  "weather_data": {"rain_probability": 10},
  "image_data": {"type": "leaf_image", "data": "base64..."}
}
```

### Edge Agents

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/edge/sensor` | Process IoT sensor reading |
| POST | `/api/v1/edge/mobile` | Mobile quick-action processing |

### Feedback & Learning

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/feedback` | Submit recommendation outcome for RL |

### System Monitoring

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/system/status` | Coordinator and edge agent metrics |
| GET | `/api/v1/agents/{agent_id}/metrics` | Per-agent performance metrics |

Valid `agent_id` values: `coordinator`, `mobile`, `iot`, `drone`, `feedback`

---

## ML Models

| Model | Input | Output |
|-------|-------|--------|
| Disease CNN | 224x224 images (5-augmentation TTA) | Disease ID + confidence |
| Yield Ensemble | NDVI, GDD, water balance, soil quality | Yield prediction + uncertainty |
| Crop Parameters | Crop type | GDD requirements, NDVI ranges, water needs by stage |

---

## NATS Events

This service does not publish NATS events directly. Analysis results are returned synchronously; downstream services (notification-service, advisory-service) consume data from the LLM orchestrator tier.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8161` | HTTP listen port |
| `ENVIRONMENT` | `development` | `development`, `staging`, `production` |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `REDIS_URL` | - | Redis URL for rate limiting |
| `NATS_URL` | - | NATS URL for event publishing |

---

## Rate Limiting

| Tier | Requests/min | Requests/hour |
|------|-------------|---------------|
| Standard | 60 | 2,000 |
| Premium | 120 | 5,000 |
| Internal (`X-Internal-Service` header) | 1,000 | 50,000 |

Edge endpoints (`/api/v1/edge/*`) receive Premium tier treatment. Analysis endpoints (`/api/v1/analyze`) use Standard tier.

---

## Dependencies

- `agents` package (local): `MasterCoordinatorAgent`, `IoTAgent`, `MobileAgent`, `DroneAgent`, `FeedbackLearnerAgent`
- `shared.errors_py` for exception handling
- `shared.middleware` for CORS and rate limiting
- Kubernetes resource limits: 512 Mi–2 Gi RAM, 250 m–1000 m CPU

---

## Health Endpoints

```
GET /healthz → {"status": "healthy", "service": "ai-agents-core", "timestamp": "..."}
GET /readyz  → {"status": "ready", "service": "ai-agents-core", "version": "16.0.0", "checks": {"service": "ready"}}
```

---

## Related Services

- **field-management-service** (3000) - field data source
- **weather-service** (8092) - weather data provider
- **iot-gateway** (8106) - sensor data ingestion
- **notification-service** (8110) - alert delivery
