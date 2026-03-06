# Yield Prediction Service - Technical Analysis

**Service Name:** yield-prediction-service
**Arabic Name:** خدمة التنبؤ بالإنتاجية الزراعية
**Version:** 16.0.0
**Technology:** Node.js / NestJS (TypeScript)
**Container Name:** sahool-yield-prediction-service

---

## Critical: Port Configuration Mismatch

There is a **significant port configuration discrepancy** across different configuration files:

| Configuration Source | Port | Status |
|---------------------|------|--------|
| Kong Gateway (`infrastructure/gateway/kong/kong.yml`) | 8098 | Incorrect |
| `docker-compose.yml` (main) | 8152 | Correct |
| `main.ts` (default) | 8098 | Outdated default |
| Dockerfile EXPOSE | 8152 | Correct |
| Professional package (`packages/professional/docker-compose.yml`) | 8098 | Needs update |
| Enterprise package (`packages/enterprise/docker-compose.yml`) | 8098 | Needs update |
| README.md | 8103 | Incorrect (documentation error) |

### Recommended Resolution:
1. Update Kong gateway config to use port **8152**
2. Update professional/enterprise docker-compose files to use port **8152**
3. Update `main.ts` default port from `8098` to `8152`
4. Update README.md documentation

---

## Service Overview

The Yield Prediction Service provides agricultural yield forecasting capabilities using multi-factor analysis models. It supports field-level, regional, and historical yield analysis with bilingual (Arabic/English) responses.

### Key Features

- **Crop Yield Prediction** (التنبؤ بإنتاجية المحاصيل)
- **Growth Stage Monitoring** (مراقبة مراحل النمو)
- **Harvest Date Prediction** (التنبؤ بموعد الحصاد)
- **Historical Yield Analysis** (تحليل الإنتاجية التاريخية)
- **Regional Statistics Comparison** (المقارنة مع المعدلات الإقليمية)
- **Maturity Monitoring** (مراقبة النضج)
- **Pre-Harvest Alerts with ActionTemplate** (تنبيهات ما قبل الحصاد)

### Architecture Context

This service consolidates functionality from:
- `yield-engine` (Port 8098 - ML models)
- `yield-prediction` (Port 3021 - Legacy forecasting)

---

## API Endpoints

### Base Path: `/api/v1/yield`

### Health Check

```http
GET /api/v1/yield/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "yield-prediction",
  "timestamp": "2026-01-25T10:30:00.000Z"
}
```

---

### Predict Field Yield

```http
GET /api/v1/yield/predict/:fieldId
```

**Description:** التنبؤ بإنتاجية حقل معين بناءً على بيانات الاستشعار عن بُعد

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fieldId | string | Yes | Field identifier |

**Response Schema:**
```json
{
  "fieldId": "string",
  "cropType": "string",
  "cropTypeAr": "string",
  "areaHectares": "number",
  "plantingDate": "string (YYYY-MM-DD)",
  "prediction": {
    "yieldPerHectareKg": "number",
    "totalYieldKg": "number",
    "totalYieldTons": "number",
    "confidencePercent": "number"
  },
  "factors": {
    "ndvi": {
      "value": "number",
      "factor": "number",
      "status": "string (good|below_average)"
    },
    "weather": {
      "factor": "number",
      "status": "string (favorable|challenging)"
    },
    "soil": {
      "factor": "number",
      "status": "string (healthy|needs_attention)"
    }
  },
  "comparison": {
    "regionalAverageKg": "number",
    "differencePercent": "number",
    "status": "string (above_average|below_average)",
    "statusAr": "string"
  },
  "recommendations": {
    "en": ["string"],
    "ar": ["string"]
  },
  "predictedAt": "string (ISO 8601)"
}
```

---

### Get Growth Stage

```http
GET /api/v1/yield/growth-stage/:fieldId
```

**Description:** الحصول على مرحلة نمو المحصول الحالية

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fieldId | string | Yes | Field identifier |

**Response Schema:**
```json
{
  "fieldId": "string",
  "cropType": "string",
  "cropTypeAr": "string",
  "plantingDate": "string (YYYY-MM-DD)",
  "daysSincePlanting": "number",
  "totalGrowthDays": "number",
  "currentStage": {
    "name": "string",
    "nameAr": "string",
    "progress": "number (0-100)",
    "daysInStage": "number",
    "totalDaysInStage": "number"
  },
  "overallProgress": "number (0-100)",
  "allStages": [
    {
      "name": "string",
      "nameAr": "string",
      "days": "number",
      "status": "string (completed|current|upcoming)",
      "statusAr": "string"
    }
  ],
  "nextMilestone": {
    "name": "string",
    "nameAr": "string",
    "daysRemaining": "number"
  }
}
```

---

### Predict Harvest Date

```http
GET /api/v1/yield/harvest-date/:fieldId
```

**Description:** التنبؤ بموعد الحصاد الأمثل

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fieldId | string | Yes | Field identifier |

**Response Schema:**
```json
{
  "fieldId": "string",
  "cropType": "string",
  "cropTypeAr": "string",
  "plantingDate": "string (YYYY-MM-DD)",
  "prediction": {
    "predictedDate": "string (YYYY-MM-DD)",
    "daysUntilHarvest": "number",
    "confidencePercent": "number"
  },
  "harvestWindow": {
    "start": "string (YYYY-MM-DD)",
    "end": "string (YYYY-MM-DD)",
    "optimalDay": "string (YYYY-MM-DD)"
  },
  "adjustments": {
    "weather": {
      "days": "number",
      "reason": "string",
      "reasonAr": "string"
    },
    "ndvi": {
      "days": "number",
      "reason": "string",
      "reasonAr": "string"
    }
  },
  "recommendations": ["string"],
  "recommendationsAr": ["string"]
}
```

---

### Get Regional Statistics

```http
GET /api/v1/yield/regional/:governorate
```

**Description:** الحصول على إحصائيات الإنتاجية للمنطقة

**Parameters:**
| Parameter | Type | Required | Location | Description |
|-----------|------|----------|----------|-------------|
| governorate | string | Yes | Path | Governorate name |
| cropType | string | No | Query | Filter by crop type |
| year | number | No | Query | Filter by year |

**Supported Governorates:**
| Code | Arabic Name |
|------|-------------|
| sanaa | صنعاء |
| aden | عدن |
| taiz | تعز |
| hodeidah | الحديدة |
| ibb | إب |
| dhamar | ذمار |
| hadramaut | حضرموت |
| marib | مأرب |

**Response Schema:**
```json
{
  "governorate": "string",
  "governorateAr": "string",
  "year": "number",
  "cropType": "string",
  "cropTypeAr": "string",
  "statistics": {
    "totalFields": "number",
    "totalAreaHectares": "number",
    "averageYieldKgPerHectare": "number",
    "totalProductionTons": "number",
    "topPerformingFields": "number",
    "belowAverageFields": "number"
  },
  "comparison": {
    "nationalAverage": "number",
    "percentOfNational": "number",
    "rankAmongGovernorates": "number"
  },
  "trends": {
    "vsLastYear": "number",
    "vsFiveYearAvg": "number"
  },
  "forecast": {
    "expectedChangeNextYear": "number",
    "confidence": "number"
  }
}
```

---

### Get Historical Yields

```http
GET /api/v1/yield/history/:fieldId
```

**Description:** الحصول على بيانات الإنتاجية التاريخية للحقل

**Parameters:**
| Parameter | Type | Required | Location | Description |
|-----------|------|----------|----------|-------------|
| fieldId | string | Yes | Path | Field identifier |
| years | number | No | Query | Number of years (default: 5) |

**Response Schema:**
```json
{
  "fieldId": "string",
  "cropType": "string",
  "cropTypeAr": "string",
  "periodYears": "number",
  "history": [
    {
      "year": "number",
      "season": "string (completed|in_progress)",
      "seasonAr": "string",
      "yieldKgPerHectare": "number",
      "areaHectares": "number",
      "totalYieldTons": "number",
      "weatherConditions": "string (excellent|good|moderate|challenging)",
      "notes": "string|null",
      "notesAr": "string|null"
    }
  ],
  "summary": {
    "averageYieldKgPerHectare": "number",
    "maxYieldKgPerHectare": "number",
    "minYieldKgPerHectare": "number",
    "variabilityPercent": "number",
    "trend": "string (improving|declining)",
    "trendAr": "string"
  }
}
```

---

### Get Maturity Monitoring

```http
GET /api/v1/yield/maturity/:fieldId
```

**Description:** مراقبة نضج المحصول

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fieldId | string | Yes | Field identifier |

**Response Schema:**
```json
{
  "fieldId": "string",
  "cropType": "string",
  "cropTypeAr": "string",
  "maturity": {
    "status": "string (green|yellowing|mature|ready_for_harvest)",
    "statusAr": "string",
    "progress": "number (0-100)"
  },
  "indicators": {
    "grainMoisture": {
      "current": "number",
      "target": "number",
      "unit": "string (%)",
      "status": "string (optimal|drying)"
    },
    "ndvi": {
      "current": "number",
      "trend": "string (declining)",
      "status": "string (senescence|active)"
    },
    "canopyTemperature": {
      "current": "number",
      "unit": "string (C)",
      "status": "string (stress|normal)"
    }
  },
  "timeline": [
    {
      "date": "string (YYYY-MM-DD)",
      "moisture": "number",
      "status": "string",
      "predicted": "boolean (optional)"
    }
  ],
  "recommendations": ["string"],
  "recommendationsAr": ["string"],
  "lastUpdated": "string (ISO 8601)"
}
```

---

### Predict Yield with ActionTemplate (Field-First)

```http
GET /api/v1/yield/predict-with-action/:fieldId
```

**Description:** التنبؤ بالإنتاجية مع قالب إجراء ما قبل الحصاد - Field-First Architecture

**Parameters:**
| Parameter | Type | Required | Location | Description |
|-----------|------|----------|----------|-------------|
| fieldId | string | Yes | Path | Field identifier |
| farmerId | string | No | Query | Farmer identifier |
| tenantId | string | No | Query | Tenant identifier |

**Response Schema:**
```json
{
  "prediction": {
    "yieldPerHectareKg": "number",
    "totalYieldKg": "number",
    "totalYieldTons": "number",
    "confidencePercent": "number",
    "harvestDate": "string (YYYY-MM-DD)",
    "daysUntilHarvest": "number"
  },
  "action_template": {
    "action_id": "string (UUID)",
    "action_type": "string (pre_harvest_alert)",
    "what": "string",
    "what_ar": "string",
    "why": "string",
    "why_ar": "string",
    "when": {
      "deadline": "string (YYYY-MM-DD)",
      "optimal_window": "string",
      "optimal_window_ar": "string"
    },
    "how": ["string"],
    "how_ar": ["string"],
    "fallback": "string",
    "fallback_ar": "string",
    "badge": {
      "type": "string",
      "label_ar": "string",
      "label_en": "string",
      "color": "string (hex)"
    },
    "confidence": "number (0-1)",
    "source_service": "string (yield-prediction)",
    "field_id": "string",
    "farmer_id": "string|undefined",
    "tenant_id": "string|undefined",
    "data": {
      "predicted_yield_kg_ha": "number",
      "total_yield_tons": "number",
      "harvest_date": "string",
      "days_until_harvest": "number",
      "maturity_status": "string",
      "grain_moisture": "number",
      "ndvi_factor": "number",
      "weather_factor": "number"
    },
    "created_at": "string (ISO 8601)"
  },
  "task_card": {
    "id": "string (UUID)",
    "type": "string (pre_harvest_alert)",
    "title_ar": "string",
    "title_en": "string",
    "urgency": {
      "level": "string (critical|high|medium|low)",
      "label_ar": "string",
      "color": "string (hex)"
    },
    "field_id": "string",
    "confidence_percent": "number",
    "offline_ready": "boolean",
    "badge": { ... }
  },
  "nats_topic": "string (sahool.alerts.pre_harvest)"
}
```

---

### Get Harvest Readiness

```http
GET /api/v1/yield/harvest-readiness/:fieldId
```

**Description:** فحص جاهزية الحصاد مع توصيات عملية

**Parameters:**
| Parameter | Type | Required | Location | Description |
|-----------|------|----------|----------|-------------|
| fieldId | string | Yes | Path | Field identifier |
| farmerId | string | No | Query | Farmer identifier |

**Response Schema:**
```json
{
  "maturity": { ... },
  "action_template": {
    "action_id": "string (UUID)",
    "action_type": "string (harvest_now|harvest_soon|prepare_harvest|monitor)",
    "what": "string",
    "what_ar": "string",
    "why": "string",
    "why_ar": "string",
    "when": { ... },
    "how": ["string"],
    "how_ar": ["string"],
    "fallback": "string",
    "fallback_ar": "string",
    "badge": {
      "type": "string (maturity_model)",
      "label_ar": "string (نموذج النضج)",
      "label_en": "string (Maturity Model)",
      "color": "string (#8B5CF6)"
    },
    "confidence": "number (0.85)",
    "source_service": "string (yield-prediction)",
    "field_id": "string",
    "farmer_id": "string|undefined",
    "data": {
      "maturity_status": "string",
      "maturity_progress": "number",
      "grain_moisture": "number",
      "target_moisture": "number",
      "ndvi": "number",
      "is_ready": "boolean"
    },
    "created_at": "string (ISO 8601)"
  },
  "is_ready": "boolean",
  "nats_topic": "string (sahool.alerts.harvest_readiness)"
}
```

---

## NATS Events

### Published Events

| Event Topic | Description | Triggered By |
|-------------|-------------|--------------|
| `sahool.alerts.pre_harvest` | Pre-harvest alert with ActionTemplate | `predictWithAction()` |
| `sahool.alerts.harvest_readiness` | Harvest readiness notification | `getHarvestReadiness()` |

**Note:** The service currently only **defines** the NATS topics in response payloads but does not actively publish to NATS. This appears to be designed for the consuming client/gateway to publish the events.

### Event Payload Structure (Pre-Harvest Alert)

```json
{
  "action_id": "uuid",
  "action_type": "pre_harvest_alert",
  "field_id": "string",
  "farmer_id": "string",
  "tenant_id": "string",
  "prediction": {
    "yieldPerHectareKg": "number",
    "totalYieldTons": "number",
    "harvestDate": "string",
    "daysUntilHarvest": "number"
  },
  "urgency": {
    "level": "critical|high|medium|low",
    "label_ar": "string"
  },
  "created_at": "ISO 8601 timestamp"
}
```

---

## Yield Prediction Algorithms

### 1. NDVI Factor Calculation

The service uses NDVI (Normalized Difference Vegetation Index) to assess crop health and adjust yield predictions:

```typescript
calculateNDVIFactor(ndvi: number): number {
  if (ndvi >= 0.8) return 1.15;  // Excellent health: +15%
  if (ndvi >= 0.7) return 1.05;  // Good health: +5%
  if (ndvi >= 0.6) return 1.00;  // Average health: no adjustment
  if (ndvi >= 0.5) return 0.90;  // Below average: -10%
  if (ndvi >= 0.4) return 0.80;  // Poor: -20%
  return 0.70;                    // Very poor: -30%
}
```

### 2. Yield Prediction Formula

```
Predicted Yield = Base Yield x NDVI Factor x Weather Factor x Soil Factor
```

Where:
- **Base Yield**: Crop-specific average yield (kg/hectare)
- **NDVI Factor**: Calculated from current NDVI (0.7 - 1.15)
- **Weather Factor**: Based on weather conditions (currently mock: 0.95)
- **Soil Factor**: Based on soil health assessment (currently mock: 0.92)

### 3. Harvest Date Prediction

```
Base Harvest Date = Planting Date + Crop Growth Days
Predicted Harvest Date = Base Harvest Date + Weather Adjustment + NDVI Adjustment
```

Adjustments:
- **Weather Adjustment**: Earlier (-) if warm, later (+) if cold
- **NDVI Adjustment**: Earlier (-) if high NDVI, later (+) if low

### 4. Maturity Status Determination

Based on grain moisture content:

| Moisture (%) | Status | Arabic |
|--------------|--------|--------|
| > 25 | green | اخضر |
| 18 - 25 | yellowing | اصفرار |
| 14 - 18 | mature | ناضج |
| <= 14 | ready_for_harvest | جاهز للحصاد |

### 5. Urgency Level Calculation

Based on days until harvest:

| Days Until Harvest | Urgency Level | Arabic | Color |
|--------------------|---------------|--------|-------|
| <= 3 | critical | حرج | #EF4444 |
| 4 - 7 | high | عالي | #F97316 |
| 8 - 14 | medium | متوسط | #EAB308 |
| > 14 | low | منخفض | #22C55E |

---

## Supported Crops

### Crop Data Constants

| Crop | Arabic | Avg Yield (kg/ha) | Growth Days |
|------|--------|-------------------|-------------|
| wheat | قمح | 3,500 | 120 |
| coffee | بن | 800 | 270 |
| sorghum | ذرة رفيعة | 2,500 | 100 |
| tomato | طماطم | 45,000 | 90 |

### Growth Stages

#### Wheat (قمح) - 120 days
| Stage | Arabic | Days |
|-------|--------|------|
| germination | إنبات | 10 |
| tillering | تفرع | 25 |
| stem_extension | استطالة الساق | 30 |
| heading | طرد السنابل | 20 |
| flowering | إزهار | 10 |
| grain_filling | امتلاء الحبوب | 20 |
| maturity | نضج | 5 |

#### Coffee (بن) - 270 days
| Stage | Arabic | Days |
|-------|--------|------|
| flowering | إزهار | 30 |
| fruit_set | عقد الثمار | 60 |
| green_fruit | ثمار خضراء | 90 |
| ripening | نضج | 60 |
| harvest_ready | جاهز للحصاد | 30 |

#### Sorghum (ذرة رفيعة) - 100 days
| Stage | Arabic | Days |
|-------|--------|------|
| emergence | بزوغ | 10 |
| vegetative | نمو خضري | 35 |
| boot | انتفاخ | 15 |
| heading | طرد السنابل | 10 |
| flowering | إزهار | 10 |
| grain_filling | امتلاء الحبوب | 15 |
| maturity | نضج | 5 |

#### Tomato (طماطم) - 90 days
| Stage | Arabic | Days |
|-------|--------|------|
| seedling | شتلة | 20 |
| vegetative | نمو خضري | 25 |
| flowering | إزهار | 15 |
| fruit_set | عقد الثمار | 15 |
| ripening | نضج | 15 |

---

## Dependencies

### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| @nestjs/common | ^10.4.15 | NestJS core framework |
| @nestjs/core | ^10.4.15 | NestJS core |
| @nestjs/platform-express | ^10.4.15 | Express adapter |
| @nestjs/swagger | ^8.1.0 | OpenAPI documentation |
| @nestjs/throttler | ^6.2.1 | Rate limiting |
| @prisma/client | ^5.22.0 | Database ORM |
| reflect-metadata | ^0.2.2 | Decorator support |
| axios | ^1.7.9 | HTTP client |
| class-transformer | ^0.5.1 | Object transformation |
| class-validator | ^0.14.1 | Validation |
| rxjs | ^7.8.1 | Reactive extensions |
| uuid | ^11.0.3 | UUID generation |
| @sahool/nestjs-auth | 16.0.0 | JWT authentication & token revocation |
| @liaoliaots/nestjs-redis | ^9.0.0 | NestJS Redis module |
| ioredis | ^5.0.0 | Redis client |
| redis | ^4.6.0 | Redis client (token revocation) |
| typescript | ^5.7.2 | TypeScript compiler |
| prisma | ^5.22.0 | Prisma CLI |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| @nestjs/testing | ^10.4.15 | Testing utilities |
| @types/express | ^5.0.0 | Express types |
| @types/jest | ^30.0.0 | Jest types |
| @types/node | ^22.10.2 | Node.js types |
| @types/supertest | ^6.0.3 | Supertest types |
| @types/uuid | ^10.0.0 | UUID types |
| express | ^4.21.2 | Express for testing |
| jest | ^29.7.0 | Test framework |
| supertest | ^7.1.4 | HTTP testing |
| ts-jest | ^29.4.6 | TypeScript Jest preset |

---

## Environment Variables

### Required Variables

| Variable | Default | Description | Used In |
|----------|---------|-------------|---------|
| `DATABASE_URL` | - | PostgreSQL connection string | docker-compose |
| `NATS_URL` | - | NATS server connection | docker-compose |

### Optional Variables

| Variable | Default | Description | Used In |
|----------|---------|-------------|---------|
| `PORT` | 8098 (main.ts) / 8152 (docker) | Service port | main.ts, Dockerfile |
| `LOG_LEVEL` | INFO | Logging level | docker-compose |
| `ENVIRONMENT` | development | Runtime environment | docker-compose |
| `CORS_ALLOWED_ORIGINS` | https://sahool.com,http://localhost:3000 | CORS origins | main.ts |

### Missing Environment Variables

The following variables are referenced in code but **not configured** in docker-compose:

| Variable | Referenced In | Recommendation |
|----------|--------------|----------------|
| `CORS_ALLOWED_ORIGINS` | main.ts | Add to docker-compose |
| `REDIS_URL` | README.md (documented) | Add for caching if needed |
| `MODEL_PATH` | README.md (documented) | Add for ML model integration |
| `WEATHER_SERVICE_URL` | README.md (documented) | Add for live weather integration |
| `SATELLITE_SERVICE_URL` | README.md (documented) | Add for satellite data integration |
| `JWT_SECRET_KEY` | Not used | Add for authentication |

---

## Rate Limiting Configuration

The service implements multi-tier rate limiting via NestJS Throttler:

| Tier | TTL | Limit | Description |
|------|-----|-------|-------------|
| short | 1 second | 10 requests | Burst protection |
| medium | 60 seconds | 100 requests | Per-minute limit |
| long | 3600 seconds | 1000 requests | Hourly limit |

---

## Kong Gateway Configuration

### Current Configuration (infrastructure/gateway/kong/kong.yml)

```yaml
- name: yield-prediction-service
  host: yield-prediction-service
  port: 8098  # BUG: Should be 8152
  protocol: http
  routes:
    - name: yield-prediction-service-route
      paths: ["/api/v1/yield", "/yield"]
      strip_path: true
      protocols: ["http", "https"]
```

### Recommended Configuration

```yaml
- name: yield-prediction-service
  host: yield-prediction-service
  port: 8152  # CORRECTED
  protocol: http
  routes:
    - name: yield-prediction-service-route
      paths: ["/api/v1/yield", "/yield"]
      strip_path: true
      protocols: ["http", "https"]
  plugins:
    - name: jwt
    - name: rate-limiting
      config:
        minute: 100
        policy: local
```

---

## Middleware & Utilities

### HTTP Exception Filter

Located at: `/src/utils/http-exception.filter.ts`

Provides unified error response format:

```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "messageAr": "string",
    "details": {},
    "timestamp": "ISO 8601",
    "path": "string",
    "requestId": "string"
  }
}
```

### Request Logging Interceptor

Located at: `/src/utils/request-logging.interceptor.ts`

Features:
- Correlation ID generation/propagation
- Tenant ID extraction
- User ID extraction
- Structured JSON logging
- Request/response timing
- Excluded paths: `/healthz`, `/readyz`, `/health`, `/metrics`, `/docs`

---

## Docker Configuration

### Dockerfile Highlights

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /workspace
EXPOSE 8152
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD sh -c "curl -f http://localhost:${PORT:-8152}/api/v1/yield/health || exit 1"
```

### docker-compose.yml Configuration

```yaml
yield-prediction-service:
  build:
    context: .
    dockerfile: apps/services/yield-prediction-service/Dockerfile
  container_name: sahool-yield-prediction-service
  environment:
    - PORT=8152
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
    - ENVIRONMENT=${ENVIRONMENT:-development}
    - DATABASE_URL=postgresql://${POSTGRES_USER:-sahool}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB:-sahool}
    - NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
  ports:
    - "8152:8152"
  depends_on:
    postgres:
      condition: service_healthy
    nats:
      condition: service_healthy
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8152/api/v1/yield/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 15s
```

---

## Service Dependencies

### Infrastructure Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| postgres (pgbouncer) | Database storage | Yes |
| nats | Event messaging | Yes |
| redis | Caching (future) | No |

### Service Dependencies (Future Integration)

| Service | Purpose | Integration Status |
|---------|---------|-------------------|
| weather-service | Live weather data | Planned (mock data used) |
| vegetation-analysis-service | NDVI data | Planned (mock data used) |
| field-management-service | Field metadata | Planned |

---

## Test Coverage

### Test File: `/test/prediction.spec.ts`

The test file uses a mock Express app instead of the actual NestJS application. This is a testing anti-pattern.

**Current Test Coverage:**
- Health check endpoint
- Prediction endpoint (POST /api/v1/predict)
- Prediction history (GET /api/v1/fields/:fieldId/predictions)
- Model listing (GET /api/v1/models)
- Validation endpoint (POST /api/v1/validate)

**Note:** The test endpoints do not match the actual implemented endpoints in the controller.

---

## Known Issues & Recommendations

### Critical Issues

1. **Port Mismatch**: Kong gateway configured for port 8098, but service runs on 8152
   - **Impact**: Service unreachable via gateway in production
   - **Fix**: Update Kong config to use port 8152

2. **Test-Implementation Mismatch**: Test file tests different endpoints than implemented
   - **Impact**: False positive test results
   - **Fix**: Rewrite tests to match actual controller endpoints

### Warnings

1. **No NATS Publishing**: Service defines NATS topics but doesn't publish events
   - **Recommendation**: Implement NATS client and event publishing

2. **Mock Data**: Weather, soil, and some field data are hardcoded
   - **Recommendation**: Integrate with weather-service and field-management-service

3. **No Database Usage**: Prisma client is in dependencies but not used
   - **Recommendation**: Implement database persistence for predictions

4. **Missing Authentication**: No JWT validation in endpoints
   - **Recommendation**: Add `@UseGuards(JwtAuthGuard)` to protected endpoints

### Improvement Suggestions

1. Add input validation DTOs with class-validator decorators
2. Implement caching with Redis for repeated predictions
3. Add Prometheus metrics endpoint (`/metrics`)
4. Implement database persistence for historical predictions
5. Add comprehensive error handling for missing field data
6. Implement ML model integration (currently uses simple math)

---

## API Documentation

Swagger/OpenAPI documentation available at:
- Development: `http://localhost:8152/docs`
- Production: `https://api.sahool.com/yield/docs`

---

## File Structure

```
apps/services/yield-prediction-service/
├── Dockerfile
├── README.md
├── jest.config.js
├── nest-cli.json
├── package.json
├── tsconfig.json
├── src/
│   ├── main.ts                              # Application entry point
│   ├── app.module.ts                        # Root module with rate limiting
│   ├── utils/
│   │   ├── http-exception.filter.ts         # Unified error handling
│   │   └── request-logging.interceptor.ts   # Request logging
│   └── yield/
│       ├── yield.controller.ts              # API endpoints
│       └── yield.service.ts                 # Business logic
└── test/
    └── prediction.spec.ts                   # Unit tests
```

---

## Related Services

| Service | Relationship | Integration Point |
|---------|--------------|-------------------|
| field-management-service | Provider | Field metadata |
| weather-service | Provider | Weather data |
| vegetation-analysis-service | Provider | NDVI data |
| notification-service | Consumer | Pre-harvest alerts |
| ws-gateway | Consumer | Real-time updates |
| alert-service | Consumer | Alert management |

---

## Changelog

### v16.0.0 (Current)
- Initial unified service combining yield-engine and yield-prediction
- Field-First Architecture support with ActionTemplate
- Bilingual (Arabic/English) responses
- Growth stage tracking for 4 crop types
- Pre-harvest alert system

---

*Last Updated: 2026-01-25*
*Document Version: 1.0*
