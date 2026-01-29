# Irrigation Smart Service Documentation

**Service**: `irrigation-smart`
**Version**: 15.3.0 (FastAPI App), 16.0.0 (Health endpoints)
**Port**: 8094
**Type**: Python/FastAPI
**Path**: `/home/user/sahool-unified-v15-idp/apps/services/irrigation-smart/`

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [NATS Events](#nats-events)
5. [Irrigation Algorithms](#irrigation-algorithms)
6. [IoT Integration](#iot-integration)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Bugs and Recommended Fixes](#bugs-and-recommended-fixes)

---

## Overview

The Irrigation Smart Service is an AI-powered irrigation scheduling and water conservation system for the SAHOOL agricultural platform. It provides:

- **Intelligent Scheduling**: AI-driven irrigation recommendations based on crop requirements, weather conditions, and soil data
- **Water Balance Tracking**: Daily evapotranspiration (ET) calculations and cumulative deficit monitoring
- **Multi-Crop Support**: 15 crop types with growth-stage-specific water requirements
- **Efficiency Comparison**: ROI analysis for different irrigation methods (drip, sprinkler, flood, furrow, traditional)
- **Field-First Architecture**: ActionTemplate generation for offline-executable recommendations
- **Bilingual Support**: Full Arabic and English throughout the service
- **IoT Integration**: Real-time soil moisture sensor data processing

### Key Features

| Feature | Description |
|---------|-------------|
| Crop Types | 15 crops: tomato, wheat, coffee, qat, banana, cucumber, pepper, potato, corn, grapes, date_palm, mango, onion, garlic, alfalfa |
| Growth Stages | 5 stages: seedling, vegetative, flowering, fruiting, maturity |
| Soil Types | 5 types: sandy, clay, loamy, silt, rocky |
| Irrigation Methods | 5 methods: drip (90%), sprinkler (75%), furrow (60%), flood (50%), traditional (45%) |
| Urgency Levels | 4 levels: critical, high, medium, low |
| Water Cost | 150 YER per cubic meter |

### Event Architecture Layer

The service belongs to the **Decision Layer** in SAHOOL's 4-layer event architecture:

| Layer | Role |
|-------|------|
| Acquisition | Data ingestion (weather, IoT, satellite) |
| Intelligence | Feature extraction, AI analysis |
| **Decision** | **irrigation-smart operates here** - Advisory & planning |
| Business | User-facing operations |

---

## Architecture

### Kong Gateway Routes

| Route | Strip Path | Target |
|-------|------------|--------|
| `/api/v1/irrigation` | true | `irrigation-smart:8094` |
| `/irrigation` | true | `irrigation-smart:8094` |

Additional routes in various Kong configurations:
- `/api/v1/irrigation/calculate`
- `/api/v1/water-balance`
- `/api/v1/professional/irrigation` (Professional tier)

### Infrastructure Dependencies

```
docker-compose.yml dependencies:
  - postgres (healthy)
  - nats (healthy)
  - iot-gateway (healthy)
```

### Service Layers

```
main.py (FastAPI Application)
    |
    +-- Pydantic Models (Request/Response schemas)
    |
    +-- Calculation Functions (ET0, ETc, water needs)
    |
    +-- shared/errors_py (Error handling & request ID middleware)
    |
    +-- shared/middleware/security_headers (Security headers middleware)
    |
    +-- shared/contracts/actions (ActionTemplate factory for Field-First)
```

### Docker Configuration

| Setting | Value |
|---------|-------|
| Base Image | python:3.11-slim-bookworm |
| User | sahool (non-root, UID 1000) |
| Working Directory | /app |
| Exposed Port | 8094 |
| Health Check Interval | 30s |
| Health Check Timeout | 10s |
| Health Check Retries | 3 |
| Start Period | 15s |

### Resource Limits (docker-compose)

| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

## API Endpoints

### Health Checks

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/healthz` | None | Liveness probe |
| `GET` | `/readyz` | None | Readiness probe (checks crop requirements loaded) |

#### Response: `/healthz`
```json
{
  "status": "ok",
  "service": "irrigation-smart",
  "version": "16.0.0"
}
```

#### Response: `/readyz`
```json
{
  "status": "ready",
  "service": "irrigation-smart",
  "version": "16.0.0",
  "checks": {
    "crop_requirements": "loaded"
  },
  "crops_supported": 15
}
```

---

### Reference Data Endpoints

#### GET `/v1/crops`

**Description**: List all supported crops with Arabic translations and water requirements

**Response**:
```json
{
  "crops": [
    {
      "id": "tomato",
      "name_ar": "طماطم",
      "water_requirements_mm_day": {
        "seedling": 2.5,
        "vegetative": 4.5,
        "flowering": 6.0,
        "fruiting": 7.5,
        "maturity": 4.0
      }
    },
    {
      "id": "wheat",
      "name_ar": "قمح",
      "water_requirements_mm_day": {
        "seedling": 2.0,
        "vegetative": 4.0,
        "flowering": 5.5,
        "fruiting": 4.5,
        "maturity": 2.5
      }
    }
    // ... 15 total crops
  ]
}
```

---

#### GET `/v1/methods`

**Description**: List all irrigation methods with efficiency percentages

**Response**:
```json
{
  "methods": [
    {
      "id": "drip",
      "name_ar": "ري بالتنقيط",
      "efficiency_percent": 90
    },
    {
      "id": "sprinkler",
      "name_ar": "ري رشاش",
      "efficiency_percent": 75
    },
    {
      "id": "furrow",
      "name_ar": "ري أخدود",
      "efficiency_percent": 60
    },
    {
      "id": "flood",
      "name_ar": "ري غمر",
      "efficiency_percent": 50
    },
    {
      "id": "traditional",
      "name_ar": "ري تقليدي",
      "efficiency_percent": 45
    }
  ]
}
```

---

### Irrigation Calculation Endpoints

#### POST `/v1/calculate`

**Description**: Calculate irrigation requirements and generate a multi-day schedule

**Request Body** (`IrrigationRequest`):
```json
{
  "field_id": "field-001",
  "crop": "tomato",
  "growth_stage": "flowering",
  "area_hectares": 2.5,
  "soil_type": "loamy",
  "irrigation_method": "drip",
  "current_soil_moisture": 35.0,
  "last_irrigation_date": "2026-01-20",
  "weather_forecast": {
    "temperature": 32,
    "humidity": 45,
    "rainfall_mm": 0
  }
}
```

**Request Schema**:
| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| `field_id` | string | Yes | - | - |
| `crop` | CropType enum | Yes | - | One of 15 crops |
| `growth_stage` | GrowthStage enum | Yes | - | seedling/vegetative/flowering/fruiting/maturity |
| `area_hectares` | float | Yes | - | > 0 |
| `soil_type` | SoilType enum | No | loamy | sandy/clay/loamy/silt/rocky |
| `irrigation_method` | IrrigationMethod enum | No | drip | drip/sprinkler/furrow/flood/traditional |
| `current_soil_moisture` | float | No | null | 0-100 |
| `last_irrigation_date` | date | No | null | ISO date |
| `weather_forecast` | object | No | null | {temperature, humidity, rainfall_mm} |

**Response** (`IrrigationPlan`):
```json
{
  "plan_id": "uuid",
  "field_id": "field-001",
  "crop": "tomato",
  "crop_name_ar": "طماطم",
  "growth_stage": "flowering",
  "growth_stage_ar": "إزهار",
  "area_hectares": 2.5,
  "soil_type": "loamy",
  "current_water_need_mm": 18.5,
  "daily_et_mm": 6.2,
  "schedules": [
    {
      "schedule_id": "uuid",
      "field_id": "field-001",
      "crop": "tomato",
      "crop_name_ar": "طماطم",
      "irrigation_date": "2026-01-25",
      "start_time": "06:00",
      "duration_minutes": 45,
      "water_amount_liters": 92500,
      "water_amount_m3": 92.5,
      "urgency": "high",
      "urgency_ar": "عالي",
      "method": "drip",
      "method_ar": "ري بالتنقيط",
      "reasoning_ar": "🔴 طماطم يحتاج ري عاجل. الاحتياج المتراكم 18.5 ملم.",
      "reasoning_en": "🔴 tomato needs urgent irrigation. Accumulated need 18.5 mm.",
      "weather_adjusted": false,
      "savings_percent": 0
    }
  ],
  "total_water_m3": 185.0,
  "estimated_cost_yer": 27750,
  "water_savings_m3": 0,
  "recommendations_ar": [
    "💧 كفاءة الري الحالية: 90%"
  ],
  "recommendations_en": [
    "💧 Current irrigation efficiency: 90%"
  ],
  "alerts_ar": [
    "🚨 طماطم يحتاج ري عاجل!"
  ],
  "created_at": "2026-01-25T10:30:00Z"
}
```

---

#### POST `/v1/calculate-with-action`

**Description**: Calculate irrigation with Field-First ActionTemplate for offline execution

**Request Body**: Same as `/v1/calculate`

**Response**:
```json
{
  "plan": {
    // Same as /v1/calculate response
  },
  "action_template": {
    "action_id": "uuid",
    "action_type": "irrigation",
    "title_ar": "ري الحقل - عالي",
    "title_en": "Field Irrigation - High",
    "description_ar": "يُنصح بري الحقل بكمية 92,500 لتر باستخدام نظام تنقيط",
    "description_en": "Irrigate field with 92,500 liters using drip system",
    "summary_ar": "ري 92,500 لتر - عالي",
    "source_service": "irrigation-smart",
    "source_analysis_id": "plan_uuid",
    "source_analysis_type": "irrigation_recommendation",
    "confidence": 0.95,
    "reasoning_ar": "رطوبة التربة: 35%",
    "reasoning_en": "Soil moisture: 35%",
    "urgency": "high",
    "deadline": "2026-01-25T18:00:00Z",
    "field_id": "field-001",
    "steps": [
      {
        "step_number": 1,
        "title_ar": "فحص نظام الري",
        "title_en": "Check irrigation system",
        "description_ar": "تأكد من عمل المضخة والأنابيب بشكل صحيح",
        "description_en": "Ensure pump and pipes are working correctly",
        "duration_minutes": 10
      },
      {
        "step_number": 2,
        "title_ar": "تشغيل الري",
        "title_en": "Start irrigation",
        "description_ar": "شغّل نظام الري بطريقة تنقيط لمدة 45 دقيقة",
        "description_en": "Run drip irrigation for 45 minutes",
        "duration_minutes": 45,
        "requires_confirmation": true
      },
      {
        "step_number": 3,
        "title_ar": "التحقق من التغطية",
        "title_en": "Verify coverage",
        "description_ar": "تأكد من وصول المياه لجميع أجزاء الحقل",
        "description_en": "Ensure water reaches all field areas",
        "duration_minutes": 15,
        "requires_photo": true
      }
    ],
    "resources_needed": [
      {
        "resource_type": "water",
        "name_ar": "مياه",
        "name_en": "Water",
        "quantity": 92500,
        "unit": "liters",
        "unit_ar": "لتر"
      }
    ],
    "estimated_duration_minutes": 70,
    "offline_executable": true,
    "fallback_instructions_ar": "في حال عدم توفر البيانات: قم بري الحقل لمدة 45 دقيقة في الصباح الباكر (قبل الساعة 8)",
    "fallback_instructions_en": "If data unavailable: Irrigate field for 45 minutes in early morning (before 8 AM)",
    "tags": ["irrigation", "drip", "high"],
    "priority_score": 72.5
  },
  "action_template_available": true,
  "task_card": {
    "id": "uuid",
    "type": "irrigation",
    "title_ar": "ري الحقل - عالي",
    "title_en": "Field Irrigation - High",
    "urgency": {
      "level": "high",
      "label_ar": "عالي",
      "color": "#F97316"
    },
    "field_id": "field-001",
    "duration_minutes": 70,
    "steps_count": 3,
    "resources_count": 1,
    "confidence_percent": 95,
    "status": "pending",
    "offline_ready": true
  },
  "notification_payload": {
    "action_id": "uuid",
    "type": "irrigation",
    "title": "ري الحقل - عالي",
    "summary": "ري 92,500 لتر - عالي",
    "urgency": "high",
    "urgency_label": "عالي",
    "field_id": "field-001",
    "deadline": "2026-01-25T18:00:00Z",
    "confidence": 0.95,
    "offline_executable": true
  }
}
```

---

#### GET `/v1/water-balance/{field_id}`

**Description**: Get water balance history and cumulative deficit for a field

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `field_id` | string | Field identifier |

**Query Parameters**:
| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `crop` | CropType | tomato | Valid crop type | Crop for ET calculation |
| `days` | int | 14 | 7-60 | Number of days of history |

**Response**:
```json
{
  "field_id": "field-001",
  "crop": "tomato",
  "period_days": 14,
  "summary": {
    "total_et_mm": 84.5,
    "total_rainfall_mm": 12.3,
    "total_irrigation_mm": 65.0,
    "net_water_balance_mm": -7.2,
    "cumulative_deficit_mm": 18.5
  },
  "daily_data": [
    {
      "field_id": "field-001",
      "date": "2026-01-11",
      "et_mm": 6.1,
      "rainfall_mm": 0,
      "irrigation_mm": 0,
      "soil_moisture_change_mm": -6.1,
      "water_deficit_mm": 6.1,
      "cumulative_deficit_mm": 6.1
    }
    // ... 14 days
  ],
  "recommendation_ar": "💧 يُنصح بري تعويضي"
}
```

---

### Sensor Integration Endpoints

#### POST `/v1/sensor-reading`

**Description**: Record a soil moisture sensor reading and get analysis

**Request Body** (`SoilMoistureReading`):
```json
{
  "field_id": "field-001",
  "sensor_id": "sensor-123",
  "reading_time": "2026-01-25T08:30:00Z",
  "depth_cm": 30,
  "moisture_percent": 28.5,
  "temperature_c": 22.0,
  "ec_ds_m": 1.2
}
```

**Response**:
```json
{
  "reading_id": "uuid",
  "field_id": "field-001",
  "sensor_id": "sensor-123",
  "moisture_percent": 28.5,
  "status": "low",
  "action_ar": "⚠️ جدولة ري خلال 24 ساعة",
  "action_en": "⚠️ Schedule irrigation within 24 hours",
  "recorded_at": "2026-01-25T08:30:00Z"
}
```

**Moisture Status Thresholds**:
| Status | Moisture % | Action |
|--------|------------|--------|
| critical | < 25% | Immediate irrigation required |
| low | 25-40% | Schedule within 24 hours |
| optimal | 40-70% | Moisture level is optimal |
| high | > 70% | Reduce irrigation |

---

#### POST `/v1/sensor-reading-with-action`

**Description**: Record sensor reading with ActionTemplate if moisture is low

**Request Body**: Same as `/v1/sensor-reading`

**Response** (when moisture is critical/low):
```json
{
  "reading_id": "uuid",
  "field_id": "field-001",
  "sensor_id": "sensor-123",
  "moisture_percent": 22.0,
  "status": "critical",
  "action_ar": "🚨 ري فوري مطلوب!",
  "action_en": "🚨 Immediate irrigation required!",
  "recorded_at": "2026-01-25T08:30:00Z",
  "action_template": {
    // ActionTemplate for emergency irrigation (5000L, 60min)
  },
  "task_card": {
    // Task card for mobile display
  }
}
```

---

### Efficiency Analysis Endpoints

#### GET `/v1/efficiency-report/{field_id}`

**Description**: Compare irrigation method efficiency and calculate ROI

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `field_id` | string | Field identifier |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `current_method` | IrrigationMethod | traditional | Current irrigation method |
| `area_hectares` | float | 1.0 | Field area (must be > 0) |

**Response**:
```json
{
  "field_id": "field-001",
  "area_hectares": 2.5,
  "current_method": {
    "method": "traditional",
    "method_ar": "ري تقليدي",
    "efficiency_percent": 45,
    "annual_water_m3": 25000,
    "annual_cost_yer": 3750000
  },
  "alternatives": [
    {
      "method": "drip",
      "method_ar": "ري بالتنقيط",
      "efficiency_percent": 90,
      "annual_water_m3": 11250,
      "annual_cost_yer": 1687500,
      "water_saved_m3": 13750,
      "cost_saved_yer": 2062500,
      "savings_percent": 55.0
    },
    {
      "method": "sprinkler",
      "method_ar": "ري رشاش",
      "efficiency_percent": 75,
      "annual_water_m3": 15000,
      "annual_cost_yer": 2250000,
      "water_saved_m3": 10000,
      "cost_saved_yer": 1500000,
      "savings_percent": 40.0
    }
    // ... more methods
  ],
  "recommendation_ar": "💡 التحويل إلى الري بالتنقيط يوفر 13750 م³ سنوياً (55.0%)",
  "roi_months": 12
}
```

---

## NATS Events

### Events Produced

Based on `governance/services.yaml`:

| Event | Description |
|-------|-------------|
| `IrrigationPlanProposed.v1` | Published when a new irrigation plan is generated |
| `IrrigationAlertIssued.v1` | Published when urgent irrigation is needed (critical/high urgency) |

**Event Subject Pattern**: `sahool.{tenant_id}.{event_type}`

### Events Consumed

| Event | Source | Description |
|-------|--------|-------------|
| `WeatherForecastReady.v1` | weather-service | Weather data for ET calculations |
| `VirtualSensorEstimated.v1` | virtual-sensors | Estimated soil moisture from models |
| `CropStressDetected.v1` | crop-intelligence-service | Crop stress indicators requiring irrigation |

### Current Implementation Note

**Important**: The current implementation does **NOT** have explicit NATS publishing/subscribing code in `main.py`. The service operates in request-response mode only. Events are defined in governance but not implemented in code.

---

## Irrigation Algorithms

### Reference Evapotranspiration (ET0)

Uses simplified Hargreaves method:

```python
def calculate_et0(temperature, humidity, wind_speed, solar_radiation=20):
    """
    ET0 = 0.0023 * Ra * (T + 17.8) * TD^0.5

    Where:
    - Ra = solar radiation (MJ/m²/day)
    - T = mean temperature (°C)
    - TD = daily temperature range (assumed 10°C)
    """
    td = 10  # Temperature range
    et0 = 0.0023 * solar_radiation * (temperature + 17.8) * math.sqrt(td)

    # Adjustment factors
    humidity_factor = 1 + (50 - humidity) / 100
    wind_factor = 1 + wind_speed / 100

    return et0 * humidity_factor * wind_factor
```

### Crop Evapotranspiration (ETc)

```python
def calculate_crop_et(et0, crop, stage):
    """
    ETc = ET0 * Kc

    Crop coefficients by growth stage:
    - Seedling: 0.5
    - Vegetative: 0.8
    - Flowering: 1.0
    - Fruiting: 1.15
    - Maturity: 0.8

    Crop-specific adjustments:
    - Banana: Kc * 1.1
    - Date Palm: Kc * 1.2
    - Wheat: Kc * 0.9
    """
```

### Water Need Calculation

```python
def calculate_water_need(crop, stage, area_ha, soil_type, method,
                         current_moisture, days_since_irrigation,
                         temperature=30, humidity=50, rainfall_forecast=0):
    """
    1. Get base ET from crop data table
    2. Adjust for temperature and humidity
    3. Calculate ET0 and ETc
    4. Use higher of adjusted ET and ETc
    5. Multiply by days since last irrigation
    6. Subtract expected rainfall
    7. Adjust for soil moisture deficit if available
    8. Apply irrigation efficiency factor
    9. Convert to volume (mm * ha * 10 = m³)
    """
```

### Urgency Level Determination

| Condition | Urgency |
|-----------|---------|
| Accumulated need > 3x daily ET | CRITICAL |
| Accumulated need > 2x daily ET | HIGH |
| Accumulated need > 1x daily ET | MEDIUM |
| Otherwise | LOW |

### Optimal Irrigation Time

| Temperature | Recommended Start Time |
|-------------|------------------------|
| > 35°C | 05:00 |
| 30-35°C | 06:00 |
| < 30°C | 07:00 |

### Schedule Splitting by Soil Type

Maximum water per session as percentage of total:

| Soil Type | Max Per Session |
|-----------|-----------------|
| Sandy | 30% |
| Loamy | 50% |
| Clay | 40% |
| Silt | 45% |
| Rocky | 25% |

### Soil Water Holding Capacity

| Soil Type | Capacity (mm/m depth) |
|-----------|----------------------|
| Sandy | 80 |
| Loamy | 150 |
| Clay | 200 |
| Silt | 170 |
| Rocky | 50 |

---

## IoT Integration

### Supported Sensor Data

The service accepts soil moisture sensor readings via `/v1/sensor-reading` endpoint:

| Field | Unit | Description |
|-------|------|-------------|
| `depth_cm` | cm | Sensor depth in soil |
| `moisture_percent` | % | Volumetric water content |
| `temperature_c` | °C | Soil temperature |
| `ec_ds_m` | dS/m | Electrical conductivity |

### IoT Gateway Integration

The service depends on `iot-gateway` (port 8106) for real-time sensor data:

```yaml
environment:
  - IOT_GATEWAY_URL=http://iot-gateway:8106
```

**Note**: The current implementation does not actively fetch from IoT Gateway. Sensor data is expected to be pushed via the `/v1/sensor-reading` endpoint.

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
| python-dotenv | 1.0.1 | Environment loading |
| structlog | >=24.1.0 | Structured logging |

### Shared Modules Used

| Module | Path | Purpose |
|--------|------|---------|
| `shared.errors_py` | `/app/shared/errors_py.py` | Unified error handling, request ID middleware |
| `shared.middleware.security_headers` | `/app/shared/middleware/security_headers.py` | Security headers middleware (optional) |
| `shared.contracts.actions` | `/app/shared/contracts/actions/` | ActionTemplate factory for Field-First architecture |

### Service Dependencies (docker-compose)

| Service | Port | Purpose |
|---------|------|---------|
| postgres | 5432 | Database (via pgbouncer) |
| pgbouncer | 6432 | Connection pooling |
| nats | 4222 | Event messaging |
| iot-gateway | 8106 | IoT sensor data |

### Governance Dependencies

| Service | Purpose |
|---------|---------|
| weather-service | Weather forecast data |
| virtual-sensors | Estimated soil moisture |

---

## Environment Variables

### Defined in docker-compose.yml

| Variable | Value | Required | Description |
|----------|-------|----------|-------------|
| `PORT` | 8094 | Yes | Service port |
| `LOG_LEVEL` | INFO | No | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | development | No | Environment (development, staging, production) |
| `DATABASE_URL` | postgresql://... | No | PostgreSQL connection string |
| `NATS_URL` | nats://... | No | NATS connection string |
| `IOT_GATEWAY_URL` | http://iot-gateway:8106 | No | IoT Gateway URL |

### Missing Environment Variables

The following environment variables are referenced but **NOT defined** in docker-compose:

| Variable | Used In | Recommended |
|----------|---------|-------------|
| `ENABLE_HSTS` | security_headers.py | Add for production HSTS control |
| `ENABLE_CSP` | security_headers.py | Add for CSP control |
| `CSP_POLICY` | security_headers.py | Add for custom CSP policy |
| `REDIS_URL` | Not used but common | Consider adding for caching |
| `JWT_SECRET_KEY` | Not used | Add if adding authentication |

### Environment Variables NOT Used

The service defines environment variables in docker-compose but does **NOT** use them in code:

| Variable | Status |
|----------|--------|
| `DATABASE_URL` | Defined but not used - no database operations |
| `NATS_URL` | Defined but not used - no NATS publishing |
| `IOT_GATEWAY_URL` | Defined but not used - no HTTP calls to IoT Gateway |

---

## Bugs and Recommended Fixes

### Critical Issues

#### 1. Missing Database Integration

**Issue**: `DATABASE_URL` is passed but never used. All data is simulated with `random.uniform()`.

**Location**: `main.py:553-556, 703-714`

**Impact**: Water balance data and sensor readings are not persisted.

**Recommendation**:
```python
# Add database pool initialization in lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
    yield
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
```

#### 2. Missing NATS Event Publishing

**Issue**: Governance defines events but service never publishes them.

**Location**: Not implemented

**Impact**: Decision layer events not propagated to Business layer.

**Recommendation**:
```python
# Add NATS connection and publish on plan generation
async def publish_irrigation_plan(plan: IrrigationPlan):
    await app.state.nc.publish(
        f"sahool.{tenant_id}.IrrigationPlanProposed.v1",
        plan.json().encode()
    )
```

#### 3. No Authentication

**Issue**: All endpoints are public with no JWT validation.

**Location**: All endpoints

**Impact**: Security vulnerability in production.

**Recommendation**: Add `Depends(get_current_user)` from `shared.auth.dependencies`.

---

### Medium Priority Issues

#### 4. Version Inconsistency

**Issue**: FastAPI app title says "15.3.0" but health endpoints return "16.0.0".

**Location**: `main.py:52-56, 486-491`

**Current**:
```python
app = FastAPI(
    title="SAHOOL Smart Irrigation Service | خدمة الري الذكي",
    version="15.3.0",  # <-- Old version
)

@app.get("/healthz")
def health():
    return {
        "version": "16.0.0",  # <-- New version
    }
```

**Recommendation**: Use environment variable or constant for version consistency.

#### 5. Random Data in Water Balance

**Issue**: `/v1/water-balance/{field_id}` returns simulated random data.

**Location**: `main.py:703-714`

**Impact**: Unreliable data for planning decisions.

**Recommendation**: Implement actual data persistence and retrieval.

#### 6. Import Statement Inside Function

**Issue**: `import random` inside endpoint functions.

**Location**: `main.py:540, 703`

**Impact**: Minor performance overhead, code smell.

**Recommendation**: Move import to top of file.

---

### Low Priority Issues

#### 7. Missing Lifespan Context Manager

**Issue**: No proper startup/shutdown lifecycle management.

**Location**: `main.py`

**Recommendation**: Add lifespan for resource management:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)
```

#### 8. sys.path Manipulation

**Issue**: Multiple `sys.path.insert()` calls for shared module imports.

**Location**: `main.py:14, 27`

**Impact**: Fragile import mechanism.

**Recommendation**: Use proper Python package structure or Docker PYTHONPATH.

#### 9. Hardcoded Water Cost

**Issue**: Water cost (150 YER/m³) is hardcoded.

**Location**: `main.py:310`

**Impact**: Cannot adjust for regional pricing.

**Recommendation**: Make configurable via environment variable:
```python
WATER_COST_PER_M3 = float(os.getenv("WATER_COST_PER_M3", "150"))
```

#### 10. No Input Sanitization for field_id

**Issue**: `field_id` path parameter is not validated for format or length.

**Location**: All endpoints with `field_id`

**Recommendation**: Add Pydantic validation or regex pattern.

---

### Test Coverage Issues

#### 11. Tests Use Mocked App

**Issue**: Unit tests create a completely separate mocked FastAPI app instead of testing actual service.

**Location**: `tests/test_irrigation.py:12-139`

**Impact**: Tests do not validate actual service behavior.

**Recommendation**: Use `TestClient` with actual `main.app`:
```python
from src.main import app
client = TestClient(app)
```

#### 12. README vs Implementation Mismatch

**Issue**: README documents endpoints that don't exist in actual implementation.

**README Endpoints** (not implemented):
- `GET /fields/{field_id}/irrigation/schedule`
- `POST /fields/{field_id}/irrigation/schedule`
- `PATCH /irrigation/schedule/{schedule_id}`
- `DELETE /irrigation/schedule/{schedule_id}`
- `POST /fields/{field_id}/irrigation/start`
- `POST /fields/{field_id}/irrigation/stop`
- `GET /fields/{field_id}/irrigation/status`
- `GET /fields/{field_id}/irrigation/history`
- `GET /fields/{field_id}/irrigation/stats`
- `GET /fields/{field_id}/soil-moisture`

**Actual Endpoints**:
- `GET /v1/crops`
- `GET /v1/methods`
- `POST /v1/calculate`
- `POST /v1/calculate-with-action`
- `GET /v1/water-balance/{field_id}`
- `POST /v1/sensor-reading`
- `POST /v1/sensor-reading-with-action`
- `GET /v1/efficiency-report/{field_id}`

**Recommendation**: Update README to match actual implementation or implement missing endpoints.

---

## Summary

### What Works Well

1. Comprehensive crop and soil type support (15 crops, 5 soil types)
2. Field-First ActionTemplate integration for offline execution
3. Bilingual (Arabic/English) throughout
4. Scientific ET calculation algorithms
5. Multi-day schedule generation with soil-aware splitting
6. Efficiency comparison with ROI calculation
7. Security headers middleware integration
8. Unified error handling

### What Needs Improvement

1. **Critical**: Missing database persistence (all data is simulated)
2. **Critical**: Missing NATS event publishing (governance-defined events not implemented)
3. **Critical**: No authentication on endpoints
4. **Medium**: Version inconsistency between app and health endpoints
5. **Medium**: Tests don't test actual service code
6. **Low**: README documents non-existent endpoints

### Recommended Next Steps

1. Implement database persistence with asyncpg
2. Add NATS JetStream event publishing
3. Add JWT authentication from shared.auth
4. Implement IoT Gateway integration for real-time sensor data
5. Add actual weather service integration
6. Update tests to test real service
7. Synchronize README with actual API
