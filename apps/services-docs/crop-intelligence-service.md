# Crop Intelligence Service - Comprehensive Analysis

**Service Name**: `crop-intelligence-service`
**Port**: 8095
**Type**: Python / FastAPI
**Version**: 16.0.0
**Path**: `/home/user/sahool-unified-v15-idp/apps/services/crop-intelligence-service/`

---

## Table of Contents

1. [Overview](#overview)
2. [Service Architecture](#service-architecture)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Schemas](#requestresponse-schemas)
5. [NATS Events](#nats-events)
6. [ML Model Integration](#ml-model-integration)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Kong Gateway Routes](#kong-gateway-routes)
10. [Bugs and Recommended Fixes](#bugs-and-recommended-fixes)

---

## Overview

The Crop Intelligence Service is a unified crop analysis service providing:

- **Health Monitoring** - Zone-based field analysis using vegetation indices
- **Disease Detection** - Rule-based disease detection from spectral indices
- **Nutrient Deficiency Detection** - Detection of NPK, Fe, Mg, Zn deficiencies
- **Yield Prediction** - Crop yield estimation for Yemen crops
- **Pest Risk Assessment** - Environmental-based pest risk evaluation
- **VRT Export** - Variable Rate Technology export for precision agriculture

### Service Consolidation

This service consolidates three deprecated services:

| Deprecated Service | Former Port | Status |
|-------------------|-------------|--------|
| `crop-health` | 8100 | Deprecated 2026-01-06 |
| `crop-health-ai` | 8095 | Deprecated 2026-01-11 |
| `crop-growth-model` | 3023 | Deprecated 2026-01-11 |

### Supported Crops (Yemen Focus)

- Wheat (قمح), Sorghum (ذرة رفيعة), Millet (دخن)
- Tomato (طماطم), Potato (بطاطس), Corn (ذرة)
- Coffee (قهوة/بن يمني), Date Palm (نخيل), Mango (مانجو)
- Citrus (حمضيات), Grape (عنب), Cotton (قطن)
- Qat (قات), Sesame (سمسم), Alfalfa (برسيم)

---

## Service Architecture

```
crop-intelligence-service/
├── Dockerfile           # Python 3.11-slim-bookworm
├── requirements.txt     # FastAPI 0.126.0, Pydantic 2.9.2
├── openapi.yaml         # OpenAPI 3.0.3 specification
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app (1496 lines)
│   ├── decision_engine.py   # Diagnosis rules engine (301 lines)
│   ├── disease_detection.py # Disease detection module (472 lines)
│   ├── nutrient_deficiency.py # Nutrient analysis (813 lines)
│   ├── pest_assessment.py   # Pest risk assessment (783 lines)
│   └── yield_prediction.py  # Yield prediction (579 lines)
└── tests/
    ├── conftest.py
    ├── test_crop_analysis.py
    ├── test_crop_health_service.py
    └── test_disease_detection.py
```

### Source File Breakdown

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 1496 | FastAPI app, endpoints, schemas |
| `decision_engine.py` | 301 | Zone diagnosis rules (NDVI, NDWI, NDRE, LCI, SAVI) |
| `disease_detection.py` | 472 | Disease detection (powdery mildew, rust, stress) |
| `nutrient_deficiency.py` | 813 | NPK + micronutrient deficiency detection |
| `pest_assessment.py` | 783 | 50+ pest types risk assessment |
| `yield_prediction.py` | 579 | Yield prediction with crop parameters |

---

## API Endpoints

### Health Check Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Liveness probe |
| `GET` | `/readyz` | Readiness probe |
| `GET` | `/` | Service info and endpoint list |

### Zone Management Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/fields/{field_id}/zones` | Create new zone |
| `GET` | `/api/v1/fields/{field_id}/zones` | List zones in field |
| `GET` | `/api/v1/fields/{field_id}/zones.geojson` | Export zones as GeoJSON |

### Observation Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | Ingest vegetation indices |
| `GET` | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | List zone observations |

### Diagnosis Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/fields/{field_id}/diagnosis` | Full field diagnosis |
| `POST` | `/api/v1/diagnose` | Quick diagnosis without storage |
| `GET` | `/api/v1/fields/{field_id}/zones/{zone_id}/timeline` | Zone time series |
| `GET` | `/api/v1/fields/{field_id}/vrt` | VRT export for precision agriculture |

### Disease Detection Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/disease/detect` | Detect diseases from indices |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/disease-analysis` | Zone disease analysis |
| `GET` | `/api/v1/disease/types` | List supported disease types |

### Nutrient Deficiency Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/nutrients/detect` | Detect nutrient deficiencies |
| `POST` | `/api/v1/nutrients/fertilizer-plan` | Generate fertilizer plan |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/nutrient-analysis` | Zone nutrient analysis |
| `GET` | `/api/v1/nutrients/types` | List nutrient types |

### Yield Prediction Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/yield/predict` | Predict crop yield |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/yield-prediction` | Zone yield prediction |
| `GET` | `/api/v1/yield/crop-parameters` | Get crop parameters |

### Pest Assessment Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/pests/assess` | Assess pest risks |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/pest-assessment` | Zone pest assessment |
| `GET` | `/api/v1/pests/types` | List pest types |

### Comprehensive Analysis Endpoint

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/comprehensive-analysis` | Combined disease, nutrient, yield, pest analysis |

---

## Request/Response Schemas

### Indices Schema (Input)

```json
{
  "ndvi": 0.78,   // Normalized Difference Vegetation Index [-1, 1]
  "evi": 0.62,    // Enhanced Vegetation Index [-1, 1]
  "ndre": 0.21,   // Normalized Difference Red Edge [-1, 1] (nitrogen)
  "lci": 0.32,    // Leaf Chlorophyll Index [-1, 1]
  "ndwi": -0.05,  // Normalized Difference Water Index [-1, 1]
  "savi": 0.65    // Soil-Adjusted Vegetation Index [-1, 1]
}
```

### Observation Input Schema

```json
{
  "captured_at": "2025-12-14T11:10:00Z",
  "source": "sentinel-2",  // sentinel-2, drone, planet, landsat, other
  "growth_stage": "mid",   // seedling, rapid, mid, late
  "indices": { /* Indices object */ },
  "cloud_pct": 8.0,
  "notes": "auto ingest"
}
```

### Observation Output Schema

```json
{
  "observation_id": "obs_field_23_zone_a_1734172200",
  "status": "stored",
  "zone_id": "zone_a",
  "field_id": "field_23"
}
```

### Field Diagnosis Response

```json
{
  "field_id": "field_23",
  "date": "2025-12-14",
  "summary": {
    "zones_total": 12,
    "zones_critical": 2,
    "zones_warning": 4,
    "zones_ok": 6
  },
  "actions": [
    {
      "zone_id": "zone_c",
      "type": "irrigation",      // irrigation, fertilization, scouting, none
      "priority": "P0",          // P0 (24h), P1 (48-72h), P2 (week), P3 (low)
      "title": "ري عاجل خلال 24 ساعة",
      "title_en": "Urgent irrigation within 24 hours",
      "reason": "NDWI منخفض جدًا مع NDVI متراجع",
      "reason_en": "Very low NDWI with declining NDVI",
      "evidence": { "ndwi": -0.12, "ndvi": 0.41 },
      "recommended_window_hours": 24,
      "recommended_dose_hint": "high",  // low, medium, high
      "severity": "critical"     // ok, low, moderate, warning, critical
    }
  ],
  "map_layers": {
    "ndvi_raster_url": "https://cdn.sahool.io/maps/field_23/2025-12-14/ndvi.tiff",
    "ndwi_raster_url": "https://cdn.sahool.io/maps/field_23/2025-12-14/ndwi.tiff",
    "ndre_raster_url": "https://cdn.sahool.io/maps/field_23/2025-12-14/ndre.tiff",
    "zones_geojson_url": "/api/v1/fields/field_23/zones.geojson"
  }
}
```

### Disease Detection Request

```json
{
  "ndvi": 0.45,
  "evi": 0.38,
  "ndre": 0.18,
  "ndwi": -0.12,
  "lci": 0.15,
  "savi": 0.40,
  "crop_type": "wheat",  // wheat, tomato, date_palm, etc.
  "humidity_pct": 75,
  "temp_c": 25
}
```

### Disease Detection Response

```json
{
  "overall_health": {
    "status_en": "fair",
    "status_ar": "متوسط"
  },
  "detection_count": 2,
  "detections": [
    {
      "disease_type": "water_stress",
      "severity": "medium",       // healthy, low, medium, high, critical
      "confidence": 0.75,
      "name_en": "Water Stress",
      "name_ar": "إجهاد مائي",
      "description_en": "Water shortage causing wilting...",
      "description_ar": "نقص المياه يؤدي إلى ذبول...",
      "affected_indicator": "NDWI",
      "evidence": { "ndwi": -0.12, "threshold": -0.1 },
      "treatments": [
        {
          "treatment_type": "irrigation",
          "product_name": "Irrigation",
          "product_name_ar": "ري",
          "dosage": "Based on crop ET requirements",
          "dosage_ar": "حسب احتياجات التبخر-نتح",
          "application_method": "Drip or furrow irrigation",
          "application_method_ar": "ري بالتنقيط أو الأخاديد",
          "urgency_days": 2,
          "precautions": ["Irrigate in early morning or evening"],
          "precautions_ar": ["اروِ في الصباح الباكر أو المساء"]
        }
      ],
      "prevention": ["Install moisture sensors", "Use mulching"],
      "prevention_ar": ["ركب حساسات رطوبة", "استخدم التغطية"]
    }
  ]
}
```

### Yield Prediction Response

```json
{
  "prediction": {
    "crop_type": "wheat",
    "crop_name_ar": "قمح",
    "predicted_yield_kg_ha": 3250,
    "predicted_yield_range": { "min": 2762, "max": 3737 },
    "confidence": "medium",
    "confidence_percent": 72,
    "trend": "stable",          // increasing, stable, decreasing
    "estimated_revenue_usd": 1137.50,
    "recommendations": ["Apply nitrogen fertilizer..."],
    "recommendations_ar": ["تطبيق سماد نيتروجيني..."],
    "limiting_factors": ["Moderate water stress"],
    "limiting_factors_ar": ["إجهاد مائي معتدل"]
  },
  "field_area_hectares": 1.0,
  "total_predicted_yield_kg": 3250
}
```

### Pest Assessment Response

```json
{
  "pest_assessment": {
    "overall_status_en": "High Risk - Monitor Closely",
    "overall_status_ar": "مخاطر عالية - راقب عن كثب",
    "total_pests_assessed": 5,
    "critical_risks": 0,
    "high_risks": 2,
    "moderate_risks": 3,
    "action_required": true
  },
  "risks": [
    {
      "pest_type": "aphids",
      "risk_level": "high",       // very_low, low, moderate, high, critical
      "risk_score": 68.5,
      "name_en": "Aphids",
      "name_ar": "المن",
      "description_en": "Small sap-sucking insects...",
      "favorable_conditions": ["Temperature in favorable range (15-28°C)"],
      "favorable_conditions_ar": ["الحرارة في النطاق الملائم"],
      "damage_symptoms_en": ["Leaf curling", "Honeydew on leaves"],
      "damage_symptoms_ar": ["تجعد الأوراق", "ندوة عسلية"],
      "controls": [
        {
          "method": "biological",
          "product_name": "Ladybugs/Lacewings release",
          "product_name_ar": "إطلاق أبو العيد/أسد المن",
          "dosage": "5000-10000 per hectare",
          "effectiveness": "medium",
          "safety_interval_days": 0
        }
      ],
      "monitoring_advice_en": "Check undersides of leaves weekly...",
      "monitoring_advice_ar": "افحص أسفل الأوراق أسبوعياً..."
    }
  ]
}
```

---

## NATS Events

### Current Status: NOT IMPLEMENTED

**Analysis**: Despite `NATS_URL` being configured in docker-compose, the service does NOT currently implement any NATS event publishing or subscription. This is a gap that should be addressed.

### Recommended NATS Events (To Be Implemented)

| Subject Pattern | Direction | Description |
|----------------|-----------|-------------|
| `sahool.{tenant_id}.crop.observation.created` | Publish | When observation is ingested |
| `sahool.{tenant_id}.crop.diagnosis.completed` | Publish | When field diagnosis is complete |
| `sahool.{tenant_id}.crop.disease.detected` | Publish | When disease is detected |
| `sahool.{tenant_id}.crop.alert.critical` | Publish | When critical issue found (P0) |
| `sahool.{tenant_id}.field.ndvi.updated` | Subscribe | When NDVI raster is available |
| `sahool.{tenant_id}.weather.updated` | Subscribe | For pest assessment context |

### Suggested Implementation Pattern

```python
# In lifespan startup
nats_url = os.getenv("NATS_URL")
if nats_url:
    app.state.nc = await nats.connect(nats_url)

# On observation creation
await app.state.nc.publish(
    f"sahool.{tenant_id}.crop.observation.created",
    json.dumps({
        "field_id": field_id,
        "zone_id": zone_id,
        "observation_id": observation_id,
        "indices": indices,
        "timestamp": datetime.utcnow().isoformat()
    }).encode()
)
```

---

## ML Model Integration

### Current Status: RULE-BASED ONLY

**Analysis**: The service is configured for ML models (`MODEL_PATH=/app/models/plant_disease.tflite`) but currently uses **rule-based detection only**. No ML model loading or inference is implemented.

### Rule-Based Detection Thresholds

#### Water Stress Detection (NDWI-based)
| NDWI Range | Severity |
|------------|----------|
| <= -0.20 | Critical |
| <= -0.15 | High |
| <= -0.10 | Medium |

#### Nitrogen Deficiency Detection (NDRE + NDVI)
| Condition | Severity |
|-----------|----------|
| NDRE <= 0.10 OR LCI <= 0.08 | Severely Deficient |
| NDRE <= 0.15 OR LCI <= 0.12 | Deficient |
| NDRE <= 0.20 OR LCI <= 0.18 | Marginal |

#### Disease Risk Patterns
| Disease | Indicators |
|---------|------------|
| Powdery Mildew | NDVI 0.3-0.6, Humidity >= 60%, Temp 15-28°C |
| Rust | NDVI 0.25-0.55, NDRE <= 0.25, Humidity >= 70% |
| Chlorophyll Deficiency | LCI < 0.15, NDVI >= 0.35 |

#### Yield Prediction Model

```python
# Combined factor calculation
combined_factor = (
    ndvi_factor * 0.35 +
    evi_factor * 0.20 +
    water_factor * water_sens * 0.20 +
    nitrogen_factor * 0.15 +
    savi_factor * 0.10
)

predicted_yield = base_yield + (max_yield - base_yield) * combined_factor
```

### Recommended ML Integration

If ML models are to be used, implement:

1. **Model Loading** in lifespan:
```python
import tensorflow as tf

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = os.getenv("MODEL_PATH")
    if model_path and os.path.exists(model_path):
        app.state.disease_model = tf.lite.Interpreter(model_path=model_path)
        app.state.disease_model.allocate_tensors()
```

2. **Inference endpoint** for image-based detection (currently not available)

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.126.0 | Web framework |
| `starlette` | >=0.49.1 | ASGI framework |
| `uvicorn[standard]` | >=0.30.0,<1.0.0 | ASGI server |
| `pydantic` | 2.9.2 | Data validation |
| `httpx` | 0.28.1 | HTTP client |
| `python-dotenv` | 1.0.1 | Environment loading |
| `python-dateutil` | 2.8.2 | Date utilities |
| `structlog` | >=24.1.0 | Structured logging |

### Shared Module Dependencies

| Module | Import Path | Purpose |
|--------|-------------|---------|
| `shared.errors_py` | `from shared.errors_py import ...` | Exception handlers |
| `shared.middleware.security_headers` | Optional import | Security headers |
| `shared.cors_config` | Optional import | CORS settings |

### Missing Dependencies (Should be added for full functionality)

| Package | Purpose |
|---------|---------|
| `nats-py` | NATS event bus connectivity |
| `asyncpg` | PostgreSQL async driver |
| `tensorflow` / `tflite-runtime` | ML model inference |
| `numpy` | Numerical computations for ML |

---

## Environment Variables

### Documented Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8095` | No | Service port |
| `LOG_LEVEL` | `INFO` | No | Logging level |
| `ENVIRONMENT` | `development` | No | Environment name |
| `DATABASE_URL` | - | No | PostgreSQL connection string |
| `NATS_URL` | - | No | NATS connection string |
| `MODEL_PATH` | `/app/models/plant_disease.tflite` | No | ML model path |
| `CDN_BASE_URL` | `https://cdn.sahool.io` | No | CDN URL for raster maps |
| `CORS_ORIGINS` | `https://sahool.io,...` | No | Allowed CORS origins |

### Missing from Docker-Compose (Should be Added)

| Variable | Purpose |
|----------|---------|
| `REDIS_URL` | Caching (mentioned in README but not in code) |
| `AI_MODEL_PATH` | Alternative model path (README uses this) |

### Environment Variable Inconsistencies

1. **DATABASE_URL** - Configured in docker-compose but **NOT USED** in code (uses in-memory storage)
2. **NATS_URL** - Configured in docker-compose but **NOT USED** in code
3. **MODEL_PATH** - Configured but **NO ML INFERENCE** implemented
4. **REDIS_URL** - Documented in README but **NOT IN docker-compose or code**

---

## Kong Gateway Routes

### Primary Kong Configuration (`infrastructure/gateway/kong/kong.yml`)

```yaml
- name: crop-intelligence-service
  host: crop-intelligence-service
  port: 8095
  protocol: http
  routes:
    - name: crop-intelligence-service-route
      paths:
        - /api/v1/crop-health
        - /api/v1/crop
        - /crop
      strip_path: true
      protocols: ["http", "https"]
```

### Kong HA Configuration (`infrastructure/gateway/kong-ha/kong/declarative/kong.yml`)

```yaml
- name: crop-intelligence-service
  url: http://crop-intelligence-service:8095
  connect_timeout: 5000
  read_timeout: 60000
  retries: 2
  routes:
    - name: crop-intelligence-route
      paths:
        - /api/v1/crop-health
        - /api/v1/crop-intelligence
      strip_path: true
  plugins:
    - name: rate-limiting
      config:
        minute: 500
        hour: 25000
        policy: redis
```

### Upstream Configuration

```yaml
- name: crop-intelligence-upstream
  algorithm: round-robin
  slots: 10000
  targets:
    - target: crop-intelligence-service:8095
      weight: 100
  healthchecks:
    active:
      type: http
      http_path: /healthz
      healthy:
        interval: 5
        successes: 2
```

### Rate Limiting

| Tier | Requests/minute | Requests/hour |
|------|-----------------|---------------|
| Standard | 500 | 25000 |
| Legacy routes | 60 | 1000 |

---

## Bugs and Recommended Fixes

### Critical Issues

#### 1. In-Memory Storage Instead of PostgreSQL

**Location**: `main.py` lines 197-203

**Issue**: Data is stored in Python dictionaries, not PostgreSQL. All data is lost on restart.

```python
# Current implementation
OBSERVATIONS: dict[str, dict[str, list[dict[str, Any]]]] = {}
ZONES: dict[str, dict[str, dict[str, Any]]] = {}
```

**Impact**: HIGH - No data persistence
**Fix**: Implement asyncpg database connection as shown in lifespan comment

#### 2. NATS Connection Not Implemented

**Location**: `main.py` lifespan function

**Issue**: Despite NATS_URL environment variable, no NATS connection or event publishing

**Impact**: MEDIUM - No event-driven communication with other services
**Fix**: Add NATS connection in lifespan and publish events on key actions

#### 3. ML Model Not Loaded

**Location**: `main.py`

**Issue**: MODEL_PATH configured but no TensorFlow/TFLite integration

**Impact**: MEDIUM - Only rule-based detection available
**Fix**: Add model loading in lifespan if ML inference is required

### Medium Issues

#### 4. Datetime.utcnow() Deprecation

**Location**: Multiple files (`main.py` lines 382, 731)

**Issue**: `datetime.utcnow()` is deprecated in Python 3.12+

```python
# Current
"created_at": datetime.utcnow().isoformat(),

# Recommended
from datetime import datetime, timezone
"created_at": datetime.now(timezone.utc).isoformat(),
```

#### 5. Version Mismatch

**Location**: `main.py`

**Issue**: FastAPI app title says "1.0.0" but healthz returns "16.0.0"

```python
# Line 286-291
app = FastAPI(
    title="SAHOOL Crop Health Service",
    version="1.0.0",  # Should be "16.0.0"
    ...
)
```

#### 6. Missing Tenant ID in Requests

**Location**: All endpoints

**Issue**: No tenant isolation - data is stored globally without tenant context

**Fix**: Add `X-Tenant-Id` header requirement and partition data by tenant

#### 7. No Authentication

**Location**: All endpoints

**Issue**: No JWT authentication implemented (unlike Kong configuration expects)

**Fix**: Add `get_current_user` dependency from `shared.auth.dependencies`

### Low Issues

#### 8. OpenAPI Server Port Mismatch

**Location**: `openapi.yaml` line 19

**Issue**: Local development URL uses port 8100 instead of 8095

```yaml
servers:
  - url: http://localhost:8100  # Should be 8095
```

#### 9. README Endpoint Mismatch

**Location**: `README.md`

**Issue**: Documented endpoints don't match actual implementation:
- `/zones/analyze` - Not implemented
- `/zones/{zone_id}/health` - Not implemented
- `/diagnose/batch` - Not implemented
- `/diseases` - Not implemented (only `/disease/types`)
- `/growth/simulate` - Not implemented
- `/growth/stages/{field_id}` - Not implemented
- `/growth/predict-harvest` - Not implemented
- `/recommendations/{field_id}` - Not implemented
- `/vrt/export` - Different path (`/api/v1/fields/{field_id}/vrt`)

#### 10. Missing Input Validation

**Location**: `main.py` disease detection endpoint

**Issue**: No validation that humidity_pct and temp_c are within reasonable ranges when provided

```python
# Current - no validation
humidity_pct: float | None = Field(default=None, ge=0, le=100)

# Should also validate combinations (temp + humidity together or neither)
```

### Security Issues

#### 11. No Rate Limiting at Application Level

**Location**: All endpoints

**Issue**: Relies entirely on Kong for rate limiting - no application-level protection

**Fix**: Add `slowapi` or custom middleware for defense in depth

#### 12. CORS Allow All Methods

**Location**: `main.py` lines 307-313

**Issue**: Allows DELETE and PATCH methods that aren't used

```python
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
# Should be: allow_methods=["GET", "POST", "OPTIONS"],
```

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total API Endpoints | 28 |
| Health Endpoints | 3 |
| Zone Management | 3 |
| Observations | 2 |
| Diagnosis | 4 |
| Disease Detection | 3 |
| Nutrient Analysis | 4 |
| Yield Prediction | 3 |
| Pest Assessment | 3 |
| Comprehensive | 1 |
| Supported Crop Types | 15 |
| Supported Pest Types | 50+ |
| Detected Diseases | 16 types |
| Detected Nutrients | 12 types |
| Lines of Code | ~4,444 |
| Test Coverage | Partial (disease detection tests) |

---

## Recommendations Summary

### Priority 1 (Critical)

1. Implement PostgreSQL database persistence
2. Add NATS event publishing for integration
3. Add authentication using shared auth module

### Priority 2 (Important)

1. Fix version numbers and documentation
2. Add tenant isolation
3. Implement ML model loading if needed
4. Update deprecated datetime usage

### Priority 3 (Enhancement)

1. Add application-level rate limiting
2. Implement missing documented endpoints
3. Add comprehensive test coverage
4. Update OpenAPI specification to match implementation

---

*Analysis Date: 2026-01-25*
*Service Version: 16.0.0*
*Analysis Author: Claude Code*
