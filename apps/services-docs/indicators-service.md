# Indicators Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | indicators-service |
| **Arabic Name** | خدمة المؤشرات الزراعية |
| **Version** | 15.3.0 (code) / 16.0.0 (healthcheck) |
| **Port** | 8091 |
| **Type** | Python / FastAPI |
| **Layer** | Bridge (Intelligence Layer) |
| **Container Name** | sahool-indicators-service |

### Purpose

The Indicators Service is a comprehensive agricultural indicators dashboard and analytics service. It provides:
- Vegetation indices (NDVI, EVI, LAI, NDWI)
- Water management indicators (soil moisture, irrigation efficiency)
- Soil health indicators (pH, nitrogen, phosphorus, potassium)
- Weather indicators (temperature, humidity, rainfall)
- Crop health indicators (disease risk, pest pressure, growth rate)
- Productivity indicators (yield estimate, crop stage progress)
- Financial indicators (cost per hectare, ROI estimate)

The service transforms raw data into actionable indicators and generates alerts when thresholds are exceeded.

---

## API Endpoints

### Health Endpoints

#### GET /healthz
Liveness probe for Kubernetes.

**Response:**
```json
{
    "status": "ok",
    "service": "indicators-service",
    "version": "16.0.0"
}
```

#### GET /readyz
Readiness probe for Kubernetes.

**Response:**
```json
{
    "status": "ready",
    "service": "indicators-service",
    "version": "16.0.0",
    "checks": {
        "indicators": "loaded"
    },
    "indicators_count": 19
}
```

---

### Indicator Definitions

#### GET /v1/indicators/definitions
Returns all indicator definitions with their metadata, ranges, and optimal values.

**Response Schema:**
```json
{
    "indicators": [
        {
            "id": "string",
            "name_ar": "string",
            "name_en": "string",
            "category": "vegetation|water|soil|weather|crop_health|productivity|financial",
            "unit": "string",
            "range": {
                "min": "number",
                "max": "number"
            },
            "optimal_range": {
                "min": "number|null",
                "max": "number|null"
            }
        }
    ],
    "categories": ["vegetation", "water", "soil", "weather", "crop_health", "productivity", "financial"]
}
```

---

### Field Indicators

#### GET /v1/field/{field_id}/indicators
Returns all indicators for a specific field.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| field_id | string | Yes | Unique field identifier |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | IndicatorCategory | No | Filter by category |

**Response Model: FieldIndicators**
```json
{
    "field_id": "string",
    "field_name": "string",
    "area_hectares": "number",
    "crop_type": "string",
    "indicators": [
        {
            "id": "string",
            "name_ar": "string",
            "name_en": "string",
            "category": "IndicatorCategory",
            "value": "number",
            "unit": "string",
            "min_value": "number",
            "max_value": "number",
            "optimal_min": "number",
            "optimal_max": "number",
            "trend": "up|down|stable",
            "trend_percent": "number",
            "status": "optimal|warning|critical|info",
            "last_updated": "datetime"
        }
    ],
    "overall_score": "number (0-100)",
    "alerts": [
        {
            "alert_id": "string",
            "field_id": "string",
            "indicator_id": "string",
            "indicator_name_ar": "string",
            "severity": "info|warning|critical",
            "message_ar": "string",
            "message_en": "string",
            "current_value": "number",
            "threshold_value": "number",
            "recommended_action_ar": "string",
            "recommended_action_en": "string",
            "created_at": "datetime"
        }
    ]
}
```

---

### Dashboard Summary

#### GET /v1/dashboard/{tenant_id}
Returns a comprehensive dashboard summary for a tenant.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| num_fields | integer | No | 10 | Number of fields (1-100) |

**Response Model: DashboardSummary**
```json
{
    "tenant_id": "string",
    "total_fields": "integer",
    "total_area_hectares": "number",
    "average_health_score": "number",
    "indicators_summary": {
        "vegetation": {
            "average_value": "number",
            "optimal_percentage": "number",
            "indicators_count": "integer"
        },
        "water": { ... },
        "soil": { ... },
        "weather": { ... },
        "crop_health": { ... },
        "productivity": { ... },
        "financial": { ... }
    },
    "active_alerts": "integer",
    "critical_alerts": "integer",
    "top_performing_fields": [
        {
            "field_id": "string",
            "name": "string",
            "score": "number",
            "crop": "string"
        }
    ],
    "attention_needed_fields": [
        {
            "field_id": "string",
            "name": "string",
            "score": "number",
            "crop": "string",
            "alerts": "integer"
        }
    ],
    "generated_at": "datetime"
}
```

---

### Tenant Alerts

#### GET /v1/alerts/{tenant_id}
Returns all alerts for a tenant.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| severity | AlertSeverity | No | null | Filter by severity |
| limit | integer | No | 50 | Max alerts (1-200) |

**Response:**
```json
{
    "tenant_id": "string",
    "total_alerts": "integer",
    "alerts": [
        {
            "alert_id": "string",
            "field_id": "string",
            "indicator_id": "string",
            "indicator_name_ar": "string",
            "indicator_name_en": "string",
            "severity": "info|warning|critical",
            "message_ar": "string",
            "message_en": "string",
            "created_at": "datetime"
        }
    ]
}
```

---

### Indicator Trends

#### GET /v1/trends/{field_id}/{indicator_id}
Returns historical trend data for a specific indicator.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| field_id | string | Yes | Field identifier |
| indicator_id | string | Yes | Indicator ID (must exist in definitions) |

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days | integer | No | 30 | History period (7-365) |

**Response:**
```json
{
    "field_id": "string",
    "indicator": {
        "id": "string",
        "name_ar": "string",
        "name_en": "string",
        "unit": "string"
    },
    "period_days": "integer",
    "statistics": {
        "average": "number",
        "minimum": "number",
        "maximum": "number",
        "optimal_range": {
            "min": "number",
            "max": "number"
        }
    },
    "data_points": [
        {
            "date": "string (YYYY-MM-DD)",
            "value": "number",
            "status": "optimal|warning|critical|info"
        }
    ],
    "overall_trend": "up|down|stable"
}
```

**Error Response (404):**
```json
{
    "detail": "Indicator {indicator_id} not found"
}
```

---

## Data Models

### Enums

#### IndicatorCategory
```python
class IndicatorCategory(str, Enum):
    VEGETATION = "vegetation"
    WATER = "water"
    SOIL = "soil"
    WEATHER = "weather"
    CROP_HEALTH = "crop_health"
    PRODUCTIVITY = "productivity"
    FINANCIAL = "financial"
```

#### TrendDirection
```python
class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
```

#### AlertSeverity
```python
class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
```

### Pydantic Models

#### Indicator
```python
class Indicator(BaseModel):
    id: str
    name_ar: str
    name_en: str
    category: IndicatorCategory
    value: float
    unit: str
    min_value: float
    max_value: float
    optimal_min: float
    optimal_max: float
    trend: TrendDirection
    trend_percent: float
    status: str  # optimal, warning, critical
    last_updated: datetime
```

#### FieldIndicators
```python
class FieldIndicators(BaseModel):
    field_id: str
    field_name: str
    area_hectares: float
    crop_type: str
    indicators: list[Indicator]
    overall_score: float
    alerts: list[dict[str, Any]]
```

#### DashboardSummary
```python
class DashboardSummary(BaseModel):
    tenant_id: str
    total_fields: int
    total_area_hectares: float
    average_health_score: float
    indicators_summary: dict[str, Any]
    active_alerts: int
    critical_alerts: int
    top_performing_fields: list[dict[str, Any]]
    attention_needed_fields: list[dict[str, Any]]
    generated_at: datetime
```

#### IndicatorAlert
```python
class IndicatorAlert(BaseModel):
    alert_id: str
    field_id: str
    indicator_id: str
    indicator_name_ar: str
    severity: AlertSeverity
    message_ar: str
    message_en: str
    current_value: float
    threshold_value: float
    recommended_action_ar: str
    recommended_action_en: str
    created_at: datetime
```

---

## Indicator Definitions

### Vegetation Indicators

| ID | Name (EN) | Name (AR) | Unit | Range | Optimal Range |
|----|-----------|-----------|------|-------|---------------|
| ndvi | NDVI | مؤشر الغطاء النباتي | index | -1.0 to 1.0 | 0.4 to 0.8 |
| evi | Enhanced Vegetation Index | مؤشر النباتات المحسن | index | -1.0 to 1.0 | 0.3 to 0.7 |
| lai | Leaf Area Index | مؤشر مساحة الأوراق | m2/m2 | 0 to 8 | 2.5 to 5.0 |

### Water Indicators

| ID | Name (EN) | Name (AR) | Unit | Range | Optimal Range |
|----|-----------|-----------|------|-------|---------------|
| ndwi | Water Index | مؤشر المياه | index | -1.0 to 1.0 | 0.0 to 0.4 |
| soil_moisture | Soil Moisture | رطوبة التربة | % | 0 to 100 | 40 to 70 |
| irrigation_efficiency | Irrigation Efficiency | كفاءة الري | % | 0 to 100 | 75 to 95 |

### Soil Indicators

| ID | Name (EN) | Name (AR) | Unit | Range | Optimal Range |
|----|-----------|-----------|------|-------|---------------|
| soil_ph | Soil pH | حموضة التربة | pH | 0 to 14 | 6.0 to 7.5 |
| nitrogen_level | Nitrogen Level | مستوى النيتروجين | kg/ha | 0 to 300 | 80 to 150 |
| phosphorus_level | Phosphorus Level | مستوى الفوسفور | kg/ha | 0 to 200 | 30 to 80 |
| potassium_level | Potassium Level | مستوى البوتاسيوم | kg/ha | 0 to 400 | 100 to 250 |

### Weather Indicators

| ID | Name (EN) | Name (AR) | Unit | Range | Optimal Range |
|----|-----------|-----------|------|-------|---------------|
| temperature | Temperature | درجة الحرارة | C | -10 to 50 | 20 to 32 |
| humidity | Relative Humidity | الرطوبة النسبية | % | 0 to 100 | 50 to 75 |
| rainfall | Rainfall | هطول الأمطار | mm | 0 to 500 | 20 to 100 |

### Crop Health Indicators

| ID | Name (EN) | Name (AR) | Unit | Range | Optimal Range |
|----|-----------|-----------|------|-------|---------------|
| disease_risk | Disease Risk | خطر الأمراض | % | 0 to 100 | 0 to 20 |
| pest_pressure | Pest Pressure | ضغط الآفات | index | 0 to 10 | 0 to 2 |
| growth_rate | Growth Rate | معدل النمو | cm/week | 0 to 30 | 5 to 15 |

### Productivity Indicators

| ID | Name (EN) | Name (AR) | Unit | Range | Optimal Range |
|----|-----------|-----------|------|-------|---------------|
| yield_estimate | Yield Estimate | تقدير المحصول | kg/ha | 0 to 50000 | 15000 to 35000 |
| crop_stage_progress | Crop Stage Progress | تقدم مرحلة المحصول | % | 0 to 100 | N/A* |

*Note: crop_stage_progress has no optimal range as it depends on expected timing.

### Financial Indicators

| ID | Name (EN) | Name (AR) | Unit | Range | Optimal Range |
|----|-----------|-----------|------|-------|---------------|
| cost_per_hectare | Cost per Hectare | التكلفة لكل هكتار | YER | 0 to 1000000 | 50000 to 200000 |
| roi_estimate | ROI Estimate | العائد المتوقع | % | -100 to 500 | 50 to 200 |

---

## Calculation Algorithms

### Status Determination Algorithm

```python
def determine_status(value, optimal_min, optimal_max, min_val, max_val) -> str:
    """
    Determine indicator status based on value and thresholds.

    Returns:
    - "info": When optimal_min or optimal_max is None
    - "optimal": When value is within optimal range
    - "warning": When value is outside optimal but within 50% of extreme
    - "critical": When value is more than 50% towards the extreme
    """
    if optimal_min is None or optimal_max is None:
        return "info"

    if optimal_min <= value <= optimal_max:
        return "optimal"
    elif value < optimal_min:
        distance = (optimal_min - value) / (optimal_min - min_val)
        return "critical" if distance > 0.5 else "warning"
    else:  # value > optimal_max
        distance = (value - optimal_max) / (max_val - optimal_max)
        return "critical" if distance > 0.5 else "warning"
```

### Indicator Value Generation (Mock Data)

The service currently generates simulated data using a Gaussian distribution centered around the optimal midpoint, with variance influenced by a base health score:

```python
def generate_indicator_value(definition, base_health=0.7):
    """
    Generate realistic indicator value based on definition and base health.

    - Higher base_health (0.5-0.9) means values closer to optimal
    - Uses random walk with mean reversion for trend data
    - Returns (value, trend_direction, trend_percent)
    """
    optimal_mid = (opt_min + opt_max) / 2
    range_width = (opt_max - opt_min) / 2
    noise = random.gauss(0, range_width * (1.5 - base_health))
    value = optimal_mid + noise
    # Clamp to valid range
    value = max(min_v, min(max_v, value))
```

### Overall Score Calculation

```python
# Percentage of indicators in "optimal" status
optimal_count = sum(1 for ind in indicators if ind.status == "optimal")
overall_score = (optimal_count / len(indicators)) * 100
```

### Trend Calculation for Time Series

Uses a random walk with mean reversion:
```python
# For each day in the time series:
change = random.gauss(0, (opt_max - opt_min) * 0.05)
reversion = (optimal_mid - current_value) * 0.1
current_value += change + reversion
current_value = max(min_val, min(max_val, current_value))
```

---

## NATS Events

### Published Events

**NONE** - The current implementation does not publish any NATS events.

### Subscribed Events

**NONE** - The current implementation does not subscribe to any NATS events.

### Expected Event Integration (Based on Service Registry)

According to `config/service-registry.yaml`, the indicators-service should transform:

| Input Event | Output Event |
|-------------|--------------|
| ndvi_result | risk_score |
| weather_forecast | irrigation_advice |
| soil_analysis | fertilizer_recommendation |

**These transformations are not yet implemented in the current codebase.**

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
| structlog | >=24.1.0 | Structured logging |

### Internal Dependencies

| Module | Path | Purpose |
|--------|------|---------|
| shared.errors_py | shared/errors_py.py | Unified error handling |

### Infrastructure Dependencies

| Service | Required | Purpose |
|---------|----------|---------|
| PostgreSQL | Yes (declared) | Database storage |
| NATS | Yes (declared) | Event messaging |
| PgBouncer | Yes | Connection pooling |

---

## Environment Variables

### Configured in docker-compose.yml

| Variable | Value | Required |
|----------|-------|----------|
| PORT | 8091 | Yes |
| LOG_LEVEL | ${LOG_LEVEL:-INFO} | No |
| ENVIRONMENT | ${ENVIRONMENT:-development} | No |
| DATABASE_URL | postgresql://${POSTGRES_USER:-sahool}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB:-sahool} | Yes |
| NATS_URL | nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222 | Yes |

### Missing Environment Variables

The following environment variables are referenced in the README but NOT used in the actual code:

| Variable | Expected | Status |
|----------|----------|--------|
| HOST | 0.0.0.0 | NOT USED |
| REDIS_URL | redis://redis:6379 | NOT USED |
| SATELLITE_SERVICE_URL | http://satellite-service:8090 | NOT USED |

### Environment Variables Used BUT Not Declared

| Variable | Used In | Status |
|----------|---------|--------|
| DATABASE_URL | docker-compose (injected) | NOT USED by code |
| NATS_URL | docker-compose (injected) | NOT USED by code |

---

## Issues and Bugs

### Critical Issues

#### 1. **No Database Integration**
- **Severity:** CRITICAL
- **Description:** The service declares DATABASE_URL dependency but does not establish any database connection.
- **Impact:** All data is mock/simulated with no persistence.
- **Location:** `src/main.py` - No asyncpg or database pool setup
- **Recommendation:** Add proper database connection in lifespan handler

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
    yield
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
```

#### 2. **No NATS Integration**
- **Severity:** CRITICAL
- **Description:** The service declares NATS_URL dependency but does not connect to NATS.
- **Impact:** Cannot participate in event-driven architecture.
- **Location:** `src/main.py` - No NATS connection setup
- **Recommendation:** Add NATS connection and event handlers

#### 3. **Mock Data Only**
- **Severity:** HIGH
- **Description:** All endpoints return randomly generated mock data.
- **Impact:** Service provides no real analytics value.
- **Location:** `generate_indicator_value()` function

### Medium Issues

#### 4. **Version Mismatch**
- **Severity:** MEDIUM
- **Description:** App title shows v15.3, healthcheck shows v16.0.0, README shows v15.4.0
- **Location:**
  - `src/main.py` line 2: "v15.3"
  - `src/main.py` line 463: "16.0.0"
  - `README.md` line 10: "15.4.0"
- **Recommendation:** Standardize version across all files

#### 5. **Missing Lifespan Handler**
- **Severity:** MEDIUM
- **Description:** No FastAPI lifespan context manager for proper startup/shutdown.
- **Impact:** No graceful resource management.
- **Recommendation:** Add async context manager for resource lifecycle

#### 6. **Inconsistent API Paths**
- **Severity:** MEDIUM
- **Description:** README documents endpoints that don't exist in the actual code.
- **Documented but missing:**
  - `GET /fields/{field_id}/indices/current`
  - `GET /fields/{field_id}/indices/timeseries`
  - `POST /indices/compare`
  - `GET /fields/{field_id}/performance`
  - `GET /fields/{field_id}/zones/analysis`
  - `POST /alerts/rules`
  - `GET /fields/{field_id}/report`
  - `GET /fields/{field_id}/export`
- **Recommendation:** Update README or implement missing endpoints

#### 7. **Test File Uses Different API Structure**
- **Severity:** MEDIUM
- **Description:** Test file mocks different API paths than actual implementation.
- **Tests use:** `/api/v1/fields/...` prefix
- **Actual code:** `/v1/field/...` (no `api` prefix, singular `field`)
- **Location:** `tests/test_indicators.py`

### Low Issues

#### 8. **Import Inside Function**
- **Severity:** LOW
- **Description:** `random` module imported inside functions instead of top-level.
- **Location:** Multiple functions in `src/main.py`
- **Recommendation:** Move import to top of file

#### 9. **Deprecated `.dict()` Method**
- **Severity:** LOW
- **Description:** Uses Pydantic v1 `.dict()` method instead of v2 `.model_dump()`.
- **Location:** `src/main.py` line 549: `alert.dict()`
- **Recommendation:** Change to `alert.model_dump()`

#### 10. **Missing Prometheus Metrics Endpoint**
- **Severity:** LOW
- **Description:** Helm values configure Prometheus scraping on `/metrics` but endpoint not implemented.
- **Location:** `helm/sahool/values.generated.yaml` line 395

---

## Security Considerations

### Current Security Features

1. **Error Handling:** Uses unified error handling with request ID tracing
2. **Input Validation:** Uses Pydantic models for request validation
3. **Query Parameter Limits:** Enforces min/max on query parameters

### Authentication (March 2026 Update)

- **DELETE endpoint** (`DELETE /v1/field/{field_id}/indicators`) now requires JWT authentication via `get_current_user` dependency
- Other endpoints remain unprotected (Kong gateway handles external auth)

### Remaining Security Gaps

1. **Partial Authentication:** Only DELETE endpoints are protected at service level; GET/POST rely on Kong gateway
2. **No Authorization:** No RBAC or tenant isolation verification
3. **No Rate Limiting:** Service-level rate limiting not implemented
4. **No Input Sanitization:** Field IDs and tenant IDs not validated

---

## Deployment Configuration

### Docker Resources

| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

### Health Checks

| Property | Value |
|----------|-------|
| Test | HTTP GET /healthz |
| Interval | 30s |
| Timeout | 10s |
| Retries | 3 |
| Start Period | 15s |

### Kong Gateway Routes

| Route | Strip Path |
|-------|------------|
| /api/v1/indicators | true |
| /indicators | true |

---

## Recommendations for Improvement

### High Priority

1. **Implement database integration** - Connect to PostgreSQL and persist indicators
2. **Implement NATS integration** - Subscribe to events and publish indicator updates
3. **Add authentication middleware** - Protect endpoints with JWT validation
4. **Implement real indicator calculations** - Replace mock data with actual computations

### Medium Priority

5. **Add missing endpoints** - Implement endpoints documented in README
6. **Standardize API paths** - Align with test expectations (`/api/v1/`)
7. **Fix version numbers** - Use consistent version across all files
8. **Add Prometheus metrics** - Implement `/metrics` endpoint

### Low Priority

9. **Refactor imports** - Move random import to top level
10. **Update Pydantic methods** - Use `.model_dump()` instead of `.dict()`
11. **Add API documentation** - Include OpenAPI examples in endpoints

---

## Kong Gateway Configuration

```yaml
services:
  - name: indicators-service
    host: indicators-service
    port: 8091
    routes:
      - name: indicators-api
        paths:
          - /api/v1/indicators
        strip_path: true
      - name: indicators-direct
        paths:
          - /indicators
        strip_path: true
```

---

## File Structure

```
apps/services/indicators-service/
├── .dockerignore
├── Dockerfile
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── main.py           # Main FastAPI application
└── tests/
    ├── __init__.py
    └── test_indicators.py
```

---

## Related Services

| Service | Relationship | Description |
|---------|--------------|-------------|
| vegetation-analysis-service | Upstream | Provides NDVI/EVI data |
| weather-service | Upstream | Provides weather data |
| field-management-service | Upstream | Provides field metadata |
| advisory-service | Downstream | Consumes indicator alerts |
| notification-service | Downstream | Sends alert notifications |

---

## Analysis Summary

The indicators-service is a **partially implemented** service that provides a solid API structure and data model definitions but lacks actual functionality. The service currently returns mock/simulated data and does not integrate with the declared infrastructure dependencies (PostgreSQL, NATS).

**Completion Status:** ~30%
- API structure: Complete
- Data models: Complete
- Indicator definitions: Complete
- Database integration: Not implemented
- NATS integration: Not implemented
- Real calculations: Not implemented
- Authentication: Not implemented

**Priority for completion:** HIGH - This service is critical for the dashboard and analytics functionality of the SAHOOL platform.

---

*Generated: 2026-01-25*
*Service Path: /home/user/sahool-unified-v15-idp/apps/services/indicators-service*
