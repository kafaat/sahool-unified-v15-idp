# Yield Prediction Service | خدمة توقع الإنتاجية (Legacy)

> **DEPRECATED** — This service has been merged into `yield-prediction-service` (port 8152, NestJS).
> New integrations should use `yield-prediction-service`. This service remains active for backward compatibility.

Agricultural yield forecasting service providing per-field predictions, regional statistics, harvest date estimation, and maturity monitoring using remote sensing data.

**Port:** 3021 | **Type:** Node.js / NestJS | **Version:** 16.0.0

---

## Overview

The Yield Prediction service provides crop yield forecasting capabilities built on the Agricultural Remote Sensing On-Demand Service model. It consumes satellite-derived NDVI time series, weather patterns, and historical yield records to generate predictions for individual fields, compare against regional averages, and identify optimal harvest windows.

Key capabilities:
- Per-field yield prediction with confidence range and key factor attribution
- Crop growth stage monitoring (Zadoks-based for wheat, general for other crops)
- Harvest date prediction with actionable pre-harvest alert templates
- Harvest readiness check with field-first ActionTemplate response format
- Historical yield analysis with model accuracy metrics (MAE, RMSE, MAPE)
- Regional statistics by governorate and crop type
- Maturity monitoring dashboard

Supported crops: Wheat (92% accuracy), Sorghum (89%), Coffee (87%), Tomato (91%), Onion (88%)

---

## Architecture

```
Yield Prediction Service (3021)  [NestJS]
└── src/
    ├── main.ts                  — Bootstrap, Swagger, CORS, graceful shutdown
    ├── app.module.ts            — Module composition
    ├── auth/                    — JwtAuthGuard (Bearer token)
    ├── yield/
    │   ├── yield.controller.ts  — REST endpoints (GET-based predictions)
    │   └── yield.service.ts     — Prediction logic, ActionTemplate builder
    └── utils/
        ├── http-exception.filter.ts       — Unified error responses
        └── request-logging.interceptor.ts — Correlation ID logging

External dependencies:
├── Database (PostgreSQL via Prisma)
├── Weather Service (8092) — Forecast data for predictions
└── Satellite / NDVI data  — Remote sensing inputs
```

---

## API Endpoints

All endpoints require JWT Bearer authentication (`JwtAuthGuard`). Swagger docs at `GET /docs`.

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/yield/health` | Service health check |
| GET | `/healthz` | Kubernetes liveness probe |

### Field Yield Prediction

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/yield/predict/:fieldId` | Predict yield for a specific field |
| GET | `/api/v1/yield/predict-with-action/:fieldId` | Predict with pre-harvest ActionTemplate (Field-First) |
| GET | `/api/v1/yield/growth-stage/:fieldId` | Current crop growth stage |
| GET | `/api/v1/yield/harvest-date/:fieldId` | Predicted optimal harvest date |
| GET | `/api/v1/yield/harvest-readiness/:fieldId` | Harvest readiness check with recommendations |
| GET | `/api/v1/yield/maturity/:fieldId` | Maturity monitoring data |

Query parameters for `predict-with-action` and `harvest-readiness`: `farmerId`, `tenantId`

### Historical & Regional

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/yield/history/:fieldId` | Historical yields with model accuracy stats (default: 5 years) |
| GET | `/api/v1/yield/regional/:governorate` | Regional statistics by governorate, crop type, year |

Query parameters for `/history`: `years` (integer)
Query parameters for `/regional`: `cropType`, `year`

### Legacy Endpoints (from README - pre-NestJS version)

These endpoints were part of the original Express implementation and remain documented for backward compatibility:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/predict/field` | Field yield prediction (original format) |
| POST | `/predict/region` | Regional yield forecast |
| GET | `/predict/historical/:field_id` | Historical comparison |
| POST | `/optimize` | Yield optimization recommendations |
| GET | `/predict/risks/:field_id` | Risk forecasting |
| GET | `/reports/season` | Seasonal report |

---

## ActionTemplate Response (Field-First Architecture)

The `predict-with-action` and `harvest-readiness` endpoints return a `PreHarvestAlertResponse` following the Field-First ActionTemplate pattern:

```json
{
  "field_id": "field-001",
  "alert_type": "pre_harvest",
  "prediction": {
    "yield_kg_ha": 3750,
    "confidence": 0.88,
    "harvest_window": { "start": "2025-05-18", "end": "2025-05-25" }
  },
  "action_template": {
    "title": "Pre-Harvest Action Plan",
    "steps": [
      { "step": 1, "action": "Reduce irrigation 5 days before harvest" },
      { "step": 2, "action": "Schedule equipment inspection" }
    ],
    "estimated_roi": "285%"
  }
}
```

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `3021` | No | Service port |
| `DATABASE_URL` | - | Yes | PostgreSQL connection string |
| `JWT_SECRET` | - | Yes | JWT verification secret |
| `WEATHER_SERVICE_URL` | `http://weather-service:8092` | No | Weather data endpoint |
| `MODEL_PATH` | `/models/yield` | No | Path to ML model files |
| `DEFAULT_MODEL` | `ensemble_v3` | No | Default prediction model |
| `CORS_ALLOWED_ORIGINS` | `https://sahool.com,...` | No | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | No | Logging level |

---

## Deprecation Note

This service is deprecated. It has been superseded by:

- **yield-prediction-service** (port 8152) — Full NestJS implementation with additional features, Prisma ORM, and active maintenance

Migration references: The `yield-prediction-service` documentation is at `apps/services-docs/yield-prediction-service.md`.

---

## Dependencies

- **NestJS** 10.x — Application framework
- **TypeScript** 5.9.x — Language
- **@nestjs/swagger** — Swagger/OpenAPI documentation
- **class-validator** / **class-transformer** — Input validation
- **Prisma** — Database ORM (production)

---

## Related Services

- **yield-prediction-service** (8152) — Active replacement service
- **vegetation-analysis-service** (8090) — NDVI / satellite data provider
- **weather-service** (8092) — Weather forecast integration
- **field-management-service** (3000) — Field context and crop data
- **crop-growth-model** (3023) — Growth stage modeling
