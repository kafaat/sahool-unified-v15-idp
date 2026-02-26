# LLM Orchestrator Service

**Port**: 8164 | **Type**: Python (FastAPI) | **Version**: 16.0.0

Intelligent LLM orchestration hub for the SAHOOL platform. Routes bilingual (Arabic/English) user queries to the appropriate specialist AI agents, executes them in parallel, synthesizes responses, and exposes integrations for Arabic NLP, satellite NDVI, agricultural ML datasets, and CrewAI multi-agent coordination.

---

## Overview

`llm-orchestrator-service` is the central AI coordination layer for SAHOOL. It performs intent classification on natural language queries, selects and executes one or more specialist agents in parallel, and synthesizes a bilingual response with actionable recommendations. It also provides unified REST endpoints for the AraBERT NLP pipeline, Sentinel Hub satellite analysis, AgML dataset management, and CrewAI crew queries. An Agent Lightning (AGL) fine-tuning module and feedback collection system continuously improve agent performance.

---

## Architecture

```
FastAPI Application
    ├── Orchestrator Router     /api/v1/orchestrate (intent → agent routing)
    ├── Integrations Router     /api/v1/integrations (NLP, satellite, ML, crew)
    ├── Training Router         /api/v1/training (fine-tuning, feedback)
    └── Agent Executor          (parallel agent dispatch, response synthesis)
        |
    Integration Services (initialized at startup)
    ├── NLPService      (AraBERT: intent classification, NER, sentiment)
    ├── SatelliteService (Sentinel Hub: NDVI, crop health)
    ├── MLService        (AgML datasets: disease classification)
    └── CrewService      (CrewAI multi-agent crews)
        |
    Optional Connections
    ├── Redis       → response caching
    ├── NATS        → event publishing
    └── PostgreSQL  → history and feedback persistence
```

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe (Redis, NATS, database connectivity) |
| GET | `/` | Root endpoint with full endpoint map |

### Orchestration

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/orchestrate` | Main entry: classify intent, dispatch agents, synthesize bilingual response |
| POST | `/api/v1/orchestrate/image` | Image-based orchestration (crop disease from photo) |
| GET | `/api/v1/orchestrate/plans` | Get recent orchestration plans |
| POST | `/api/v1/orchestrate/execute-action` | Execute a specific recommended action |
| GET | `/api/v1/agents` | List available specialist agents |
| GET | `/api/v1/agents/health` | Health status of all agents |

### NLP Integration (AraBERT)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/integrations/nlp/process` | Full NLP analysis (intent + NER + sentiment) |
| GET | `/api/v1/integrations/nlp/intent/{text}` | Quick intent classification |

### Satellite Integration (Sentinel Hub)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/integrations/satellite/ndvi` | Compute NDVI for a field boundary |
| POST | `/api/v1/integrations/satellite/crop-health` | Full crop health analysis (NDVI + LAI + time series) |

### ML Dataset Integration (AgML)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/integrations/ml/datasets` | List available agricultural ML datasets |
| GET | `/api/v1/integrations/ml/diseases/{crop}` | Get disease classes for a crop type |

### CrewAI Integration

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/integrations/crew/query` | Query a specialist agent crew |
| GET | `/api/v1/integrations/crew/agents` | List available crew agents |

### Training and Feedback (AGL)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/training/start` | Start an Agent Lightning training job |
| GET | `/api/v1/training/jobs` | List training jobs |
| POST | `/api/v1/training/feedback` | Submit feedback for a recommendation |
| GET | `/api/v1/training/feedback/statistics` | Feedback aggregation statistics |

---

## Supported Intents

| Intent | Arabic | Routed To |
|--------|--------|-----------|
| `crop_disease` | مرض المحصول | crop-intelligence-service, yolo26-vision-service |
| `irrigation` | الري | irrigation-smart, weather-service |
| `fertilizer` | الأسمدة | advisory-service |
| `pest` | الآفات | pest-detection-service, advisory-service |
| `weather` | الطقس | weather-service |
| `yield` | الإنتاجية | yield-prediction-service, crop-growth-model |
| `field_analysis` | تحليل الحقل | vegetation-analysis-service, indicators-service |
| `terrain` | التضاريس | terrain-core-service |
| `soil` | التربة | soil-analysis-service |

---

## Orchestration Request Schema

```json
POST /api/v1/orchestrate
{
  "query": "متى أسقي القمح؟",
  "language": "ar",
  "field_id": "field_001",
  "context": {
    "crop_type": "wheat",
    "location": "Yemen",
    "soil_moisture": 35,
    "weather": {"temperature": 28, "rain_probability": 10}
  }
}
```

---

## NATS Events Published

| Subject | Trigger |
|---------|---------|
| `sahool.orchestrator.query_processed` | Query successfully routed and responded |
| `sahool.orchestrator.agent_failed` | Agent execution failure |
| `sahool.orchestrator.training_completed` | AGL training job finished |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8164` | HTTP listen port |
| `HOST` | `0.0.0.0` | Bind address |
| `ENVIRONMENT` | `development` | `development` enables hot-reload |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `REDIS_URL` | - | Redis for response caching |
| `NATS_URL` | - | NATS server URL |
| `DATABASE_URL` | - | PostgreSQL for history and feedback |
| `DB_POOL_MIN_SIZE` | `2` | DB pool minimum connections |
| `DB_POOL_MAX_SIZE` | `10` | DB pool maximum connections |
| `AGL_ENABLED` | `false` | Enable Agent Lightning fine-tuning |
| `ARABERT_MODEL` | `aubmindlab/bert-base-arabertv2` | AraBERT model identifier |
| `SENTINEL_HUB_CLIENT_ID` | - | Sentinel Hub API credentials |
| `SENTINEL_HUB_CLIENT_SECRET` | - | Sentinel Hub API credentials |
| `CORS_ORIGINS` | `https://sahool.io,...` | Comma-separated allowed origins |

---

## Dependencies

- `structlog` for structured JSON logging
- `asyncpg` for PostgreSQL async pool
- `redis.asyncio` for response caching
- `nats-py` for event publishing
- `shared.errors_py` for request-ID middleware and exception handling
- `shared.middleware.security_headers` for HTTP security headers
- `shared.auth.dependencies` for JWT authentication (when available)
- Local `integrations/`: `NLPService`, `SatelliteService`, `MLService`, `CrewService`
- Local `training/`: `AGLTrainer`, `FeedbackCollector`

---

## Health Endpoints

```
GET /healthz → {"status": "ok", "service": "llm-orchestrator-service", "version": "16.0.0"}
GET /readyz  → {"status": "ready", "checks": {"service": "ready", "redis": "connected|not_configured", "nats": "connected|not_configured", "database": "connected|not_configured"}}
```

---

## Related Services

- **ai-chat-assistant** (8260) - primary consumer of orchestration
- **advisory-service** (8093) - specialist advisory agent
- **weather-service** (8092) - weather data integration
- **agent-registry** (8160) - agent discovery registry
- **copilot-api** (8088) - AI copilot with RAG integration
