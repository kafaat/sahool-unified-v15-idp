# Soil Analysis Service | خدمة تحليل التربة

Comprehensive soil testing, interpretation, and amendment recommendation service tailored for Middle East agricultural conditions.

**Port:** 8134 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The Soil Analysis Service is the agronomic intelligence layer for soil health management. It ingests lab test results, interprets nutrient levels against crop-specific thresholds calibrated for Middle East soils, generates cost-effective amendment plans from a 50+ product fertilizer database, and tracks multi-year soil health trends.

Key capabilities:
- Soil test record management with GPS sample location tracking
- Support for NPK, pH, EC, organic matter, and micronutrient parameters
- Crop-specific nutrient interpretation using regional thresholds
- Deficiency and toxicity classification
- Amendment plan generation with cost-effective fertilizer selection
- Application rate calculation
- Multi-year historical trend analysis with anomaly detection
- Prometheus metrics endpoint for observability
- Bilingual responses (Arabic / English)

---

## Architecture

```
Soil Analysis Service (8134)
├── src/api/v1/soil_tests.py   — All API routes
└── Shared modules:
    └── shared/soil_testing/
        ├── SoilTestResult       — Core data model
        ├── SoilTestInterpreter  — Nutrient level classification
        ├── SoilAmendmentRecommender — Fertilizer plan engine
        └── SoilTrendAnalyzer   — Historical trend processing

External:
├── PostgreSQL — Soil test record persistence
└── NATS       — Event publishing and subscription
```

The service uses asyncpg for database connections and a standard NATS client. Both are optional; the service degrades gracefully when they are unavailable (status reported in `/health`).

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Readiness probe (DB + NATS status) |
| GET | `/health` | Comprehensive health check |
| GET | `/metrics` | Prometheus metrics |

### Soil Tests

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/soil/tests` | Create new soil test record |
| GET | `/api/v1/soil/tests/{test_id}` | Get specific soil test result |
| DELETE | `/api/v1/soil/tests/{test_id}` | Delete soil test record |
| GET | `/api/v1/soil/tests/field/{field_id}` | Get all tests for a field |

### Interpretation

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/soil/interpret` | Full crop-specific interpretation of a soil test |
| POST | `/api/v1/soil/interpretation/nutrient-status` | Status for a single nutrient (value + extraction method) |
| POST | `/api/v1/soil/interpretation/ph-status` | Soil pH classification and lime recommendation |
| POST | `/api/v1/soil/interpretation/ec-status` | EC/salinity status and salt tolerance assessment |

### Amendment Recommendations

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/soil/recommendations/amendment-plan` | Full amendment plan (crop, target yield, field area) |
| POST | `/api/v1/soil/recommendations/calculate-rate` | Fertilizer rate from nutrient need and product content |
| GET | `/api/v1/soil/products` | List available fertilizer products (50+ entries) |
| GET | `/api/v1/soil/crops/{crop}/requirements` | Nutrient requirements for a crop |

### Trends

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/soil/trends` | Multi-year soil health trend for a field |
| POST | `/api/v1/soil/trends/nutrient` | Trend for a specific nutrient |
| POST | `/api/v1/soil/trends/compare-periods` | Compare soil health between two time periods |

---

## NATS Events

### Publishes

| Subject | Trigger |
|---------|---------|
| `SoilAnalysisCompleted.v1` | Soil test analysis completed |
| `AmendmentPlanGenerated.v1` | Amendment plan generated |
| `SoilTrendAlert.v1` | Significant soil health change detected |

### Subscribes

| Subject | Purpose |
|---------|---------|
| `FieldCreated.v1` | Initialize default soil profile for new field |
| `WeatherForecastReady.v1` | Weather data for amendment application timing |
| `TaskCompleted.v1` | Track completed soil amendment tasks |

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8134` | No | Service port |
| `HOST` | `0.0.0.0` | No | Bind address |
| `ENVIRONMENT` | `development` | No | Environment name |
| `DATABASE_URL` | - | Yes | PostgreSQL connection string (TLS enforced in non-dev) |
| `REDIS_URL` | - | Yes | Redis connection string |
| `NATS_URL` | - | Yes | NATS server URL |
| `CORS_ORIGINS` | `https://sahool.app,...` | No | Allowed CORS origins |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL async driver (pool: min 2, max 10)
- **nats-py** — NATS event integration
- **structlog** — Structured JSON logging
- `shared/soil_testing/` — Core soil science logic
- `shared.errors_py` — Unified error handling

---

## Security

- **Authentication**: DELETE endpoints (`DELETE /tests/{test_id}`) require JWT authentication via `get_current_user` dependency
- Auth fallback uses `HTTPBearer` scheme when `shared.auth` is unavailable
- Multi-tenant isolation via `tenant_id` scoping
- TLS enforced for database connections in non-development environments
- Unified error handling via `shared.errors_py`

## Related Services

- **advisory-service** (8093) — Consumes amendment plans as recommendations
- **fertilizer-management** (shared module) — Fertilizer product database
- **field-management-service** (3000) — Field and crop context
- **weather-service** (8092) — Application timing data
- **task-service** (8103) — Amendment tasks tracked here
