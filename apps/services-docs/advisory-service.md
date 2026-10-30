# Advisory Service - Comprehensive Analysis

**Service Name:** advisory-service
**Type:** Python/FastAPI
**Port:** 8093
**Version:** 16.0.0 (health endpoints) / 15.3.3 (FastAPI app)
**Status:** Active (Consolidates deprecated `agro-advisor` and `fertilizer-advisor`)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [NATS Events](#nats-events)
5. [Advisory Algorithms](#advisory-algorithms)
6. [Knowledge Base](#knowledge-base)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Kong Gateway Routes](#kong-gateway-routes)
10. [Bugs and Issues](#bugs-and-issues)
11. [Recommended Fixes](#recommended-fixes)

---

## Overview

The Advisory Service is a unified agricultural advisory platform for the SAHOOL system, providing:

- **Disease Diagnosis**: Image-based and symptom-based disease detection
- **Nutrient Assessment**: NDVI-based and visual indicator assessment
- **Fertilizer Planning**: Crop-stage-based fertilizer recommendations
- **Crop Information**: Yemen-specific crop varieties and requirements

### Arabic Description

خدمة الاستشارات الزراعية الموحدة. توفر تشخيص الأمراض وتقييم المغذيات وتخطيط التسميد وتوصيات المحاصيل.

### Migration Note

This service consolidates two deprecated services:
- `agro-advisor` (Port 8095/8105) - Disease diagnosis & nutrients
- `fertilizer-advisor` (Port 8093) - Fertilizer planning

---

## Architecture

### Directory Structure

```
apps/services/advisory-service/
├── Dockerfile                    # Container configuration
├── requirements.txt              # Python dependencies
├── README.md                     # Service documentation
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── engine/                   # Advisory algorithms
│   │   ├── __init__.py
│   │   ├── disease_rules.py      # Disease assessment rules
│   │   ├── nutrient_rules.py     # Nutrient deficiency rules
│   │   └── planner.py            # Fertilizer planning engine
│   ├── events/                   # NATS event handling
│   │   ├── __init__.py
│   │   ├── publish.py            # Event publisher
│   │   └── types.py              # Event type definitions
│   ├── hooks/                    # Automation hooks
│   │   ├── __init__.py
│   │   └── task_automation.py    # Task creation automation
│   └── kb/                       # Knowledge base
│       ├── __init__.py
│       ├── diseases.py           # Disease database
│       ├── fertilizers.py        # Fertilizer database
│       └── nutrients.py          # Nutrient deficiency database
└── tests/
    ├── __init__.py
    ├── test_health.py            # Health check tests
    └── test_planner.py           # Planner engine tests
```

### External Dependencies (Shared Modules)

The service imports from `/app/shared/` (Docker) or relative `shared/` directory:

- `shared.errors_py` - Unified error handling
- `shared.crops` - Crop catalog (41KB, comprehensive crop data)
- `shared.yemen_varieties` - Yemen-specific crop varieties (46KB)
- `shared.auth.dependencies` - JWT authentication
- `shared.auth.models` - User model
- `shared.auth.revocation_middleware` - Token revocation middleware
- `shared.auth.token_revocation` - Token revocation store

---

## API Endpoints

### Health Check Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/healthz` | Liveness probe | `{"status": "ok", "service": "agro_advisor", "version": "16.0.0"}` |
| GET | `/readyz` | Readiness probe | `{"status": "ready", "service": "agro_advisor", "version": "16.0.0", "checks": {...}}` |

### Disease Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/disease/assess` | Assess disease from image classification result | Yes |
| POST | `/disease/symptoms` | Assess possible diseases from reported symptoms | Yes |
| GET | `/disease/search` | Search diseases by name or symptoms | No |
| GET | `/disease/crop/{crop}` | Get all diseases for a specific crop | No |
| GET | `/disease/{disease_id}` | Get disease information by ID | No |

#### POST /disease/assess

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "condition_id": "string (required) - Disease ID from classifier",
  "confidence": "float (required, 0-1)",
  "crop": "string (optional)",
  "weather": "object (optional) - {humidity, temperature, precipitation}",
  "correlation_id": "string (optional)"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "result": {
    "disease_id": "string",
    "category": "disease",
    "severity": "low|medium|high|critical",
    "title_ar": "string",
    "title_en": "string",
    "actions": ["string"],
    "confidence": "float",
    "urgency_hours": "int",
    "details": {
      "symptoms_ar": ["string"],
      "symptoms_en": ["string"],
      "pathogen": "string"
    }
  },
  "event_id": "string|null",
  "published": "boolean"
}
```

#### POST /disease/symptoms

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "crop": "string (required)",
  "symptoms": ["string"] (required),
  "lang": "ar|en (default: ar)",
  "correlation_id": "string (optional)"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "results": [
    {
      "disease_id": "string",
      "category": "disease",
      "severity": "string",
      "title_ar": "string",
      "title_en": "string",
      "actions": ["string"],
      "confidence": "float",
      "urgency_hours": "int",
      "details": {
        "matched_symptoms": "int",
        "total_symptoms": "int"
      }
    }
  ],
  "event_id": "string|null"
}
```

### Nutrient Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/nutrient/ndvi` | Assess nutrient deficiency from NDVI data | Yes |
| POST | `/nutrient/visual` | Assess nutrient deficiency from visual indicators | Yes |
| GET | `/nutrient/{deficiency_id}` | Get nutrient deficiency information by ID | No |

#### POST /nutrient/ndvi

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "ndvi": "float (required, -1 to 1)",
  "ndvi_history": ["float"] (optional),
  "crop": "string (optional)",
  "stage": "string (optional)",
  "correlation_id": "string (optional)"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "ndvi": "float",
  "results": [
    {
      "deficiency_id": "string",
      "nutrient": "N|P|K|Ca|Mg|Fe|Zn",
      "category": "nutrient_deficiency",
      "severity": "string",
      "title_ar": "string",
      "title_en": "string",
      "corrections": [
        {
          "type": "fertilizer|practice",
          "product": "string",
          "dose_kg_ha": "float"
        }
      ],
      "confidence": "float",
      "urgency_hours": "int",
      "details": {
        "diagnosis_reason": "string",
        "ndvi_value": "float",
        "symptoms_ar": ["string"]
      }
    }
  ],
  "event_id": "string|null"
}
```

#### POST /nutrient/visual

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "leaf_color": "string (optional) - e.g., pale_yellow, purple, brown_edges",
  "pattern": "string (optional) - e.g., uniform, interveinal, marginal",
  "location": "string (optional) - e.g., older_leaves, new_leaves, all",
  "crop": "string (optional)",
  "lang": "ar|en (default: ar)",
  "correlation_id": "string (optional)"
}
```

### Fertilizer Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/fertilizer/plan` | Generate fertilizer plan for crop and stage | Yes |
| GET | `/fertilizer/{fertilizer_id}` | Get fertilizer information by ID | No |
| GET | `/fertilizer/nutrient/{nutrient}` | Get fertilizers that provide a specific nutrient | No |

#### POST /fertilizer/plan

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "crop": "string (required)",
  "stage": "string (required)",
  "field_size_ha": "float (default: 1.0)",
  "soil_fertility": "low|medium|high (default: medium)",
  "irrigation_type": "drip|surface|sprinkler (default: drip)",
  "correlation_id": "string (optional)"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "crop": "string",
  "stage": "string",
  "field_size_ha": "float",
  "applications": [
    {
      "product": "string",
      "product_ar": "string",
      "dose_kg_per_ha": "float",
      "total_kg": "float",
      "timing_days": "int",
      "method": "fertigation|broadcast|side_dress|banding|foliar"
    }
  ],
  "total_cost_estimate": "float|null",
  "notes": ["string"],
  "event_id": "string|null",
  "published": "boolean"
}
```

### Crop Information Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/crops/categories` | List crop categories with counts | No |
| GET | `/crops/search` | Search crops by Arabic or English name | No |
| GET | `/crops` | List all crops grouped by category | No |
| GET | `/crops/{crop_code}` | Get single crop details with Yemen varieties | No |
| GET | `/crops/{crop_code}/varieties` | Get Yemen-specific varieties for a crop | No |
| GET | `/crops/{crop}/stages` | Get growth stages for a crop | No |
| GET | `/crops/{crop}/requirements` | Get nutrient requirements for a crop (legacy) | No |

### Action Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/actions/{action_id}` | Get detailed action instructions | No |

---

## NATS Events

### Event Subjects (Published)

| Event Type | Subject | Version | Description |
|------------|---------|---------|-------------|
| `recommendation_issued` | `sahool.advisor.recommendation_issued` | 1 | Disease/pest recommendation |
| `fertilizer_plan_issued` | `sahool.advisor.fertilizer_plan_issued` | 1 | Fertilizer plan generated |
| `nutrient_assessment_issued` | `sahool.advisor.nutrient_assessment_issued` | 1 | Nutrient deficiency detected |
| `disease_detected` | `sahool.advisor.disease_detected` | 1 | Disease detection event |

### Event Envelope Format

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "version": "int",
  "aggregate_id": "field_id",
  "tenant_id": "string",
  "correlation_id": "uuid",
  "timestamp": "ISO8601",
  "payload": { ... }
}
```

### Recommendation Event Payload

```json
{
  "field_id": "string",
  "category": "disease|nutrient_deficiency",
  "severity": "low|medium|high|critical",
  "title_ar": "string",
  "title_en": "string",
  "actions": ["string"],
  "confidence": "float",
  "details": { ... }
}
```

### Fertilizer Plan Event Payload

```json
{
  "field_id": "string",
  "crop": "string",
  "stage": "string",
  "plan": [
    {
      "product": "string",
      "product_ar": "string",
      "dose_kg_per_ha": "float",
      "total_kg": "float",
      "timing_days": "int",
      "method": "string"
    }
  ],
  "notes": ["string"]
}
```

### Nutrient Assessment Event Payload

```json
{
  "field_id": "string",
  "deficiency_id": "string",
  "nutrient": "string",
  "severity": "string",
  "title_ar": "string",
  "title_en": "string",
  "corrections": [...],
  "confidence": "float"
}
```

### Subscribed Events (Task Automation Hook)

The `TaskAutomationHook` subscribes to its own published events to create tasks:

| Subject | Handler |
|---------|---------|
| `advisor.recommendation_issued` | `_handle_recommendation` - Creates spray/manual/irrigation tasks |
| `advisor.fertilizer_plan_issued` | `_handle_fertilizer_plan` - Creates fertilization tasks |
| `advisor.nutrient_assessment_issued` | `_handle_nutrient_assessment` - Creates inspection tasks |

**Note:** The subscription subjects use a different prefix (`advisor.*`) than the publish subjects (`sahool.advisor.*`). This is a **BUG** - see [Bugs and Issues](#bugs-and-issues).

---

## Advisory Algorithms

### Disease Assessment Algorithm

#### Image-Based Assessment (`assess_from_image_event`)

1. **Confidence Threshold**: Requires minimum 60% confidence
2. **Disease Lookup**: Retrieves disease from knowledge base
3. **Weather Adjustment**: Modifies severity and urgency based on:
   - Humidity (if >= disease threshold, increases severity)
   - Temperature (if in optimal disease range, reduces urgency)
   - Precipitation (if > 5mm and disease spreads via rain, increases severity)
4. **Output**: `DiseaseAssessment` with actions and urgency

#### Symptom-Based Assessment (`assess_from_symptoms`)

1. **Crop Filtering**: Matches diseases for specific crop or "general" diseases
2. **Symptom Matching**: Calculates match score based on symptom overlap
3. **Confidence Calculation**: `min(0.9, match_ratio + 0.3)`
4. **Ranking**: Returns top 5 matches sorted by confidence

### Nutrient Assessment Algorithm

#### NDVI-Based Assessment (`assess_from_ndvi`)

| NDVI Range | Primary Diagnosis | Confidence |
|------------|-------------------|------------|
| < 0.3 | Nitrogen deficiency | 0.7 |
| 0.3 - 0.5 | Nitrogen (0.5) / Potassium (0.3) | Variable |
| Declining trend (>0.1 drop) | Phosphorus deficiency | 0.4 |

#### Visual Assessment (`assess_from_visual`)

Scoring system based on visual indicators:
- Leaf color match: +3 points
- Pattern match: +2 points
- Location match: +2 points
- Minimum threshold: 3 points
- Confidence: `min(0.9, 0.3 + (score * 0.1))`

### Fertilizer Planning Algorithm

#### Stage-Based Nutrient Calculation

1. **Lookup Crop Requirements**: From `CROP_REQUIREMENTS` database
2. **Calculate Stage Needs**: `stage_needs[nutrient] = total_needs[nutrient] * stage_ratio[nutrient]`
3. **Fertility Adjustment**:
   - Low fertility: +20% (factor 1.2)
   - Medium fertility: baseline (factor 1.0)
   - High fertility: -20% (factor 0.8)

#### Fertilizer Selection Logic

1. **Balanced NPK Check**: If N, P, K needs are within 10 kg/ha of each other, use compound NPK
2. **Individual Selection**:
   - For drip irrigation: Prefer soluble fertilizers (Calcium Nitrate)
   - For surface: Prefer granular (Urea, DAP)
3. **Dose Calculation**: Based on fertilizer nutrient content percentage

### Supported Crops (22 crops)

| Crop | Target Yield (t/ha) | N | P | K |
|------|---------------------|---|---|---|
| Tomato | 40 | 150 | 60 | 200 |
| Wheat | 5 | 120 | 40 | 60 |
| Potato | 30 | 180 | 80 | 250 |
| Maize | 8 | 200 | 50 | 100 |
| Onion | 35 | 120 | 50 | 150 |
| Coffee | 1.5 | 150 | 30 | 180 |
| Qat | 4 | 200 | 40 | 150 |
| Barley | 3.5 | 100 | 35 | 50 |
| Sorghum | 3 | 80 | 40 | 60 |
| Millet | 2 | 50 | 25 | 40 |
| Faba Bean | 3 | 40 | 60 | 80 |
| Lentil | 1.5 | 30 | 50 | 60 |
| Chickpea | 1.8 | 35 | 55 | 70 |
| Pepper | 30 | 140 | 55 | 180 |
| Eggplant | 35 | 150 | 60 | 190 |
| Cucumber | 45 | 120 | 50 | 220 |
| Garlic | 10 | 100 | 45 | 120 |
| Grape | 15 | 80 | 35 | 150 |
| Date Palm | 10 | 100 | 40 | 200 |
| Banana | 35 | 200 | 50 | 400 |
| Mango | 12 | 120 | 40 | 160 |
| Sesame | 1 | 60 | 40 | 50 |
| Alfalfa | 20 | 50 | 80 | 120 |

---

## Knowledge Base

### Disease Database (7 diseases)

| ID | Name (AR) | Name (EN) | Crop | Severity | Urgency |
|----|-----------|-----------|------|----------|---------|
| `tomato_late_blight` | اللفحة المتأخرة | Late Blight | tomato | high | 24h |
| `tomato_early_blight` | اللفحة المبكرة | Early Blight | tomato | medium | 48h |
| `tomato_powdery_mildew` | البياض الدقيقي | Powdery Mildew | tomato | medium | 72h |
| `wheat_rust` | صدأ القمح | Wheat Rust | wheat | high | 24h |
| `potato_late_blight` | اللفحة المتأخرة للبطاطس | Potato Late Blight | potato | high | 24h |
| `aphid_infestation` | إصابة المن | Aphid Infestation | general | medium | 48h |
| `whitefly_infestation` | إصابة الذبابة البيضاء | Whitefly Infestation | general | high | 24h |

### Fertilizer Database (14 products)

| ID | Name (EN) | Type | N% | P% | K% | Form |
|----|-----------|------|----|----|----|----|
| `urea` | Urea | nitrogen | 46 | 0 | 0 | granular |
| `ammonium_sulfate` | Ammonium Sulfate | nitrogen | 21 | 0 | 0 | crystalline |
| `calcium_nitrate` | Calcium Nitrate | nitrogen_calcium | 15.5 | 0 | 0 | granular |
| `tsp` | Triple Super Phosphate | phosphorus | 0 | 46 | 0 | granular |
| `dap` | Di-Ammonium Phosphate | nitrogen_phosphorus | 18 | 46 | 0 | granular |
| `potassium_sulfate` | Potassium Sulfate (SOP) | potassium | 0 | 0 | 50 | granular |
| `potassium_chloride` | Potassium Chloride (MOP) | potassium | 0 | 0 | 60 | granular |
| `npk_20_20_20` | NPK 20-20-20 Balanced | compound | 20 | 20 | 20 | soluble |
| `npk_15_15_15` | NPK 15-15-15 | compound | 15 | 15 | 15 | granular |
| `npk_12_12_36` | NPK 12-12-36 High-K | compound | 12 | 12 | 36 | soluble |
| `iron_chelate` | Iron Chelate (EDDHA) | micronutrient | - | - | - | granular |
| `zinc_sulfate` | Zinc Sulfate | micronutrient | - | - | - | crystalline |
| `magnesium_sulfate` | Magnesium Sulfate | secondary | - | - | - | crystalline |
| `compost` | Compost | organic | 1.5 | 1 | 1 | bulk |

### Nutrient Deficiency Database (7 deficiencies)

| ID | Nutrient | Severity | Urgency | Visual Indicators |
|----|----------|----------|---------|-------------------|
| `nitrogen_deficiency` | N | high | 48h | pale_yellow, uniform_chlorosis, older_leaves_first |
| `phosphorus_deficiency` | P | medium | 72h | purple_bronze, purple_veins_undersides, older_leaves_first |
| `potassium_deficiency` | K | medium | 72h | brown_edges, marginal_necrosis, older_leaves_first |
| `calcium_deficiency` | Ca | high | 24h | distorted_tips, tip_burn, new_leaves_first |
| `magnesium_deficiency` | Mg | medium | 72h | interveinal_yellow, green_veins_yellow_between, older_leaves_first |
| `iron_deficiency` | Fe | medium | 72h | pale_new_leaves, interveinal_chlorosis_new, new_leaves_first |
| `zinc_deficiency` | Zn | medium | 72h | mottled_yellow, small_clustered_leaves, new_growth |

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | HTTP client |
| python-dotenv | 1.0.1 | Environment variables |
| nats-py | 2.9.0 | NATS messaging |
| structlog | >=24.1.0 | Structured logging |
| redis[hiredis] | 5.2.1 | Token revocation storage |
| pytest | 8.3.4 | Testing |
| pytest-asyncio | 0.24.0 | Async testing |
| pytest-cov | 4.1.0 | Coverage |
| pytest-mock | 3.12.0 | Mocking |

### External Service Dependencies

| Service | Purpose | URL |
|---------|---------|-----|
| PostgreSQL (via PgBouncer) | Database | `DATABASE_URL` |
| NATS | Event messaging | `NATS_URL` |
| Redis | Token revocation (optional) | Not configured |
| FieldOps Service | Task creation | `FIELDOPS_URL` (http://fieldops:8080) |

### Shared Module Dependencies

| Module | Purpose |
|--------|---------|
| `shared.errors_py` | Unified error handling |
| `shared.crops` | Crop catalog with 50+ crops |
| `shared.yemen_varieties` | Yemen-specific varieties |
| `shared.auth.dependencies` | JWT authentication |
| `shared.auth.models` | User model |
| `shared.auth.revocation_middleware` | Token revocation middleware |
| `shared.auth.token_revocation` | Token revocation store |

---

## Environment Variables

### Currently Used

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | 8095 (code) / 8093 (docker) | No | Service port |
| `NATS_URL` | `nats://nats:4222` | No | NATS connection URL |
| `FIELDOPS_URL` | `http://fieldops:8080` | No | FieldOps service URL |

### Configured in docker-compose.yml

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | 8093 | Service port |
| `LOG_LEVEL` | INFO | Logging level |
| `ENVIRONMENT` | development | Environment name |
| `DATABASE_URL` | PostgreSQL via PgBouncer | Database connection |
| `NATS_URL` | nats://nats:4222 | NATS connection |

### Documented but NOT Used

| Variable | Documented In | Actually Used? |
|----------|--------------|----------------|
| `DATABASE_URL` | README, docker-compose | **NO** - No database operations in code |
| `REDIS_URL` | README | **NO** - Redis used only for token revocation |
| `WEATHER_SERVICE_URL` | README | **NO** - No weather service integration |

### Missing from Documentation

| Variable | Used In | Description |
|----------|---------|-------------|
| `FIELDOPS_URL` | task_automation.py | FieldOps service URL for task creation |
| `JWT_SECRET_KEY` | auth module | JWT secret (from shared auth) |
| `JWT_ALGORITHM` | auth module | JWT algorithm (from shared auth) |

---

## Kong Gateway Routes

### Primary Configuration (`infra/kong/kong.yml`)

```yaml
- name: advisory-service
  url: http://advisory-service:8093
  tags:
    - starter
    - advisory
  routes:
    - name: advisory-route
      paths:
        - /api/v1/advice
        - /api/v1/advisory
        - /api/v1/agro-advisor  # Legacy path
      strip_path: false
  plugins:
    - name: jwt
    - name: acl
      config:
        allow:
          - starter-users
          - professional-users
          - enterprise-users
```

### Fertilizer Route (Points to same upstream)

```yaml
- name: fertilizer-advisor
  host: advisory-service-upstream
  routes:
    - name: fertilizer-route
      paths:
        - /api/v1/fertilizer
      strip_path: false
```

### Alternative Configuration (`infrastructure/gateway/kong/kong.yml`)

```yaml
- name: advisory-service
  host: advisory-service
  port: 8093
  routes:
    - name: advisory-service-route
      paths:
        - /api/v1/advisory
        - /api/v1/fertilizer
        - /advisory
        - /fertilizer
      strip_path: true
```

**Note:** Different Kong configurations have different `strip_path` settings (true vs false), which affects how paths are passed to the service.

---

## Bugs and Issues

### Critical Issues

#### 1. NATS Subject Mismatch (High Priority)

**File:** `/home/user/sahool-unified-v15-idp/apps/services/advisory-service/src/hooks/task_automation.py`

**Problem:** Task automation hook subscribes to wrong subjects:
- Subscribes to: `advisor.recommendation_issued`
- Publishes to: `sahool.advisor.recommendation_issued`

**Impact:** Task automation will never receive events from the publisher.

**Code:**
```python
# Line 145-160 in task_automation.py
await self.nc.subscribe(
    "advisor.recommendation_issued",  # WRONG - should be "sahool.advisor.recommendation_issued"
    cb=self._handle_recommendation,
)
```

#### 2. Port Mismatch in Code vs Configuration

**Problem:** Port specified in code differs from Docker/Kong configuration:
- `main.py` line 4: "Port: 8095" in docstring
- `main.py` line 112: "ready on port 8095" in log
- `main.py` line 734: `port = int(os.getenv("PORT", 8095))`
- `Dockerfile`: `ENV PORT=8093`
- `docker-compose.yml`: `- PORT=8093`

**Impact:** Confusion and potential port conflicts if running locally without env var.

### Medium Priority Issues

#### 3. Version Inconsistency

**Problem:** Multiple version numbers in the codebase:
- `main.py` line 139: `version="15.3.3"` (FastAPI app)
- `main.py` line 160: `"version": "16.0.0"` (health endpoint)
- `main.py` line 187: `"version": "16.0.0"` (readiness endpoint)
- `requirements.txt`: `# Version: 16.0.0`
- `Dockerfile`: `ARG SERVICE_VERSION=16.0.0`

#### 4. Unused Import and Module

**File:** `/home/user/sahool-unified-v15-idp/apps/services/advisory-service/src/main.py`

**Problem:** `timezone` imported from datetime but never used (line 9 in publish.py).

**Code:**
```python
from datetime import timezone, datetime, UTC  # timezone is unused
```

#### 5. Test Import Path Issues

**Files:** `tests/test_health.py`, `tests/test_planner.py`

**Problem:** Tests import from `kernel.services.agro_advisor.src.main` which doesn't match the actual service path `apps.services.advisory-service.src.main`.

**Code:**
```python
# test_health.py line 7
from kernel.services.agro_advisor.src.main import app  # Wrong path
```

#### 6. Database URL Not Used

**Problem:** `DATABASE_URL` is configured in docker-compose but the service never connects to a database. All data is stored in-memory in knowledge base dictionaries.

### Low Priority Issues

#### 7. Missing Error Handling for Empty Crop Requirements

**File:** `/home/user/sahool-unified-v15-idp/apps/services/advisory-service/src/engine/planner.py`

**Problem:** If `CROP_REQUIREMENTS` is empty, `_default_plan` could fail if `npk_15_15_15` fertilizer doesn't exist.

**Code:**
```python
# Line 444
npk = get_fertilizer("npk_15_15_15")  # Could return None
# Line 452-453
"product": npk["name_en"] if npk else "NPK 15-15-15",  # Handles None but inconsistent
```

#### 8. Hardcoded Stage Durations Only for 3 Crops

**File:** `/home/user/sahool-unified-v15-idp/apps/services/advisory-service/src/engine/planner.py`

**Problem:** `STAGE_DURATIONS` only defined for tomato, wheat, and potato (lines 476-492). Other crops get default 21 days.

#### 9. Task Hook Uses Different NATS URL Constant

**File:** `/home/user/sahool-unified-v15-idp/apps/services/advisory-service/src/hooks/task_automation.py`

**Problem:** Defines its own `NATS_URL` constant instead of importing from events module, could lead to inconsistency.

---

## Recommended Fixes

### High Priority

1. **Fix NATS Subject Mismatch**
```python
# In task_automation.py, change subscriptions:
await self.nc.subscribe(
    "sahool.advisor.recommendation_issued",  # Fixed
    cb=self._handle_recommendation,
)
await self.nc.subscribe(
    "sahool.advisor.fertilizer_plan_issued",  # Fixed
    cb=self._handle_fertilizer_plan,
)
await self.nc.subscribe(
    "sahool.advisor.nutrient_assessment_issued",  # Fixed
    cb=self._handle_nutrient_assessment,
)
```

2. **Standardize Port Configuration**
```python
# In main.py, update docstring and default port:
"""
SAHOOL Advisory Service - Main API Service
Disease diagnosis, nutrient assessment, and fertilizer planning
Port: 8093
"""
# ...
port = int(os.getenv("PORT", 8093))  # Change default to 8093
```

### Medium Priority

3. **Standardize Version Numbers**
```python
# Create a single version constant
VERSION = "16.0.0"

app = FastAPI(
    title="SAHOOL Advisory Service",
    version=VERSION,
    lifespan=lifespan,
)

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "advisory_service", "version": VERSION}
```

4. **Fix Test Import Paths**
```python
# In test files:
from src.main import app  # Use relative import
# Or
from advisory_service.src.main import app  # Use package name
```

5. **Remove Unused DATABASE_URL**
   - Either implement database persistence
   - Or remove from docker-compose.yml and README

### Low Priority

6. **Add Complete Stage Durations**
   - Add `STAGE_DURATIONS` for all 22 supported crops

7. **Document Missing Environment Variables**
   - Add `FIELDOPS_URL` to README

8. **Remove Unused Imports**
```python
# In publish.py
from datetime import datetime, UTC  # Remove timezone
```

---

## Test Coverage

### Existing Tests

| Test File | Tests | Coverage Areas |
|-----------|-------|----------------|
| `test_health.py` | 11 tests | Health check, crops, diseases, fertilizers, actions |
| `test_planner.py` | 12 tests | Fertilizer planning engine and API |

### Missing Test Coverage

- Disease assessment endpoints (`/disease/assess`, `/disease/symptoms`)
- Nutrient assessment endpoints (`/nutrient/ndvi`, `/nutrient/visual`)
- NATS event publishing
- Task automation hook
- Error handling scenarios
- Authentication/authorization

---

## Related Documentation

- **Service README:** `/home/user/sahool-unified-v15-idp/apps/services/advisory-service/README.md`
- **CLAUDE.md:** `/home/user/sahool-unified-v15-idp/CLAUDE.md` (Section: Key Services Overview)
- **Kong Configuration:** `/home/user/sahool-unified-v15-idp/infra/kong/kong.yml`
- **Shared Crops Module:** `/home/user/sahool-unified-v15-idp/apps/services/shared/crops.py`
- **Shared Yemen Varieties:** `/home/user/sahool-unified-v15-idp/apps/services/shared/yemen_varieties.py`

---

*Generated: 2026-01-25*
*Analyzer: Claude Code*
