> **⚠️ DEPRECATED**: This service has been replaced by `weather-service`. See [weather-service.md](weather-service.md) for current documentation.

---

# Weather Core Service Analysis

> **DEPRECATED**: This service has been deprecated and merged into `weather-service`.
> Use `weather-service` on port 8092 for new deployments.

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | weather-core |
| **Language** | Python (FastAPI) |
| **Port** | 8108 |
| **Version** | 15.3.3 (code) / 16.0.0 (container) |
| **Status** | DEPRECATED |
| **Replacement** | weather-service (port 8092) |
| **Source Path** | `/home/user/sahool-unified-v15-idp/apps/services/weather-core/` |

### Purpose

Agricultural weather assessment, forecasting, and alert service for SAHOOL platform. Provides:
- Real-time weather data from multiple providers
- Risk assessment for crops (heat stress, frost, disease, heavy rain, strong wind)
- Irrigation adjustment recommendations
- Weather alerts with bilingual (Arabic/English) messaging

### Architecture

```
                    +------------------+
                    |   Kong Gateway   |
                    |  /weather-core   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Weather Core    |
                    |   (FastAPI)      |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
+--------v--------+  +-------v-------+  +-------v-------+
| Open-Meteo API  |  | OpenWeatherMap |  | WeatherAPI   |
| (Free - Primary)|  | (API Key)      |  | (API Key)    |
+-----------------+  +----------------+  +---------------+
                             |
                    +--------v---------+
                    |      NATS        |
                    |  Event Publishing|
                    +------------------+
```

---

## API Endpoints

### Health Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/healthz` | Liveness probe | No |
| GET | `/readyz` | Readiness probe | No |

#### GET /healthz

**Response:**
```json
{
  "status": "healthy",
  "service": "weather-core",
  "version": "15.3.3"
}
```

#### GET /readyz

**Response:**
```json
{
  "status": "ready",
  "service": "weather-core",
  "version": "16.0.0",
  "checks": {
    "service": "ready"
  }
}
```

---

### Weather Endpoints

#### POST /weather/assess

Assess weather conditions and generate alerts from manual input data.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_c": "float (required)",
  "humidity_pct": "float | null",
  "wind_speed_kmh": "float | null",
  "precipitation_mm": "float | null",
  "uv_index": "float | null",
  "correlation_id": "string | null"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "alerts": [
    {
      "alert_type": "heat_stress | frost | heavy_rain | strong_wind | disease_risk",
      "severity": "low | medium | high | critical",
      "title_ar": "string",
      "title_en": "string",
      "description_ar": "string",
      "description_en": "string",
      "window_hours": "integer",
      "recommendations_ar": ["string"],
      "recommendations_en": ["string"]
    }
  ],
  "alert_count": "integer",
  "event_ids": ["string (UUID)"],
  "published": "boolean"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8108/weather/assess \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "temp_c": 42.5,
    "humidity_pct": 25,
    "wind_speed_kmh": 15,
    "precipitation_mm": 0,
    "uv_index": 10
  }'
```

---

#### POST /weather/current

Get current weather from external API provider with risk assessment.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "lat": "float (required, -90 to 90)",
  "lon": "float (required, -180 to 180)",
  "correlation_id": "string | null"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "location": {
    "lat": "float",
    "lon": "float"
  },
  "provider": "Open-Meteo | OpenWeatherMap | WeatherAPI | cache",
  "current": {
    "temperature_c": "float",
    "humidity_pct": "float",
    "wind_speed_kmh": "float",
    "wind_direction_deg": "integer",
    "wind_direction": "string (N, NE, E, SE, S, SW, W, NW)",
    "precipitation_mm": "float",
    "cloud_cover_pct": "float",
    "pressure_hpa": "float",
    "uv_index": "float",
    "condition": "string (English)",
    "condition_ar": "string (Arabic)",
    "timestamp": "ISO8601 string"
  },
  "alerts": ["WeatherAlert objects"],
  "event_ids": ["string (UUID)"]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8108/weather/current \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "lat": 15.35,
    "lon": 44.20
  }'
```

---

#### POST /weather/forecast

Get weather forecast with automatic provider fallback.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "lat": "float (required)",
  "lon": "float (required)",
  "correlation_id": "string | null"
}
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | integer | 7 | Number of forecast days (1-16) |

**Response Schema:**
```json
{
  "field_id": "string",
  "location": {
    "lat": "float",
    "lon": "float"
  },
  "provider": "string",
  "forecast": [
    {
      "date": "YYYY-MM-DD",
      "temp_max_c": "float",
      "temp_min_c": "float",
      "precipitation_mm": "float",
      "precipitation_probability_pct": "float",
      "wind_speed_max_kmh": "float",
      "uv_index_max": "float",
      "condition": "string",
      "condition_ar": "string",
      "sunrise": "HH:MM | null",
      "sunset": "HH:MM | null"
    }
  ],
  "days": "integer"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8108/weather/forecast?days=7" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "lat": 15.35,
    "lon": 44.20
  }'
```

---

#### POST /weather/irrigation

Calculate irrigation adjustment based on weather conditions.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_c": "float (required)",
  "humidity_pct": "float (required)",
  "wind_speed_kmh": "float (required)",
  "precipitation_mm": "float (default: 0)",
  "correlation_id": "string | null"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "weather_input": {
    "temp_c": "float",
    "humidity_pct": "float",
    "wind_speed_kmh": "float",
    "precipitation_mm": "float"
  },
  "adjustment_factor": "float (0.3 - 1.5)",
  "recommendation_ar": "string",
  "recommendation_en": "string",
  "event_id": "string | null",
  "published": "boolean"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8108/weather/irrigation \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "temp_c": 38,
    "humidity_pct": 25,
    "wind_speed_kmh": 20,
    "precipitation_mm": 0
  }'
```

---

#### GET /weather/heat-stress/{temp_c}

Quick heat stress check for a given temperature.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| temp_c | float | Temperature in Celsius |

**Response Schema:**
```json
{
  "temperature_c": "float",
  "alert_type": "heat_stress",
  "severity": "none | low | medium | high | critical",
  "at_risk": "boolean"
}
```

**Example Request:**
```bash
curl http://localhost:8108/weather/heat-stress/45
```

---

#### GET /weather/providers

List available weather providers and their configuration status.

**Response Schema:**
```json
{
  "multi_provider_enabled": "boolean",
  "providers": [
    {
      "name": "string",
      "configured": "boolean",
      "type": "string (class name)"
    }
  ],
  "total": "integer",
  "configured": "integer"
}
```

---

## Weather Assessment Algorithms

### Heat Stress Risk

| Temperature (C) | Severity | Alert Window |
|-----------------|----------|--------------|
| >= 45 | CRITICAL | 24 hours |
| >= 42 | HIGH | 24 hours |
| >= 38 | MEDIUM | 24 hours |
| >= 35 | LOW | 24 hours |
| < 35 | NONE | - |

**Recommendations (Arabic):**
- Increase irrigation in early morning or evening
- Use shade nets if possible
- Avoid field work during peak hours

### Frost Risk

| Temperature (C) | Severity | Alert Window |
|-----------------|----------|--------------|
| <= 0 | CRITICAL | 12 hours |
| <= 2 | HIGH | 12 hours |
| <= 5 | MEDIUM | 12 hours |
| > 5 | NONE | - |

**Recommendations:**
- Cover sensitive crops
- Irrigate before frost to protect roots
- Avoid harvesting until frost melts

### Heavy Rain Risk

| Precipitation (mm) | Intensity (mm/h) | Severity | Alert Window |
|--------------------|------------------|----------|--------------|
| >= 50 | >= 10 | CRITICAL | 24 hours |
| >= 30 | >= 5 | HIGH | 24 hours |
| >= 15 | - | MEDIUM | 24 hours |
| < 15 | - | NONE | - |

**Recommendations:**
- Improve field drainage
- Postpone spraying and fertilization
- Harvest ready crops if possible

### Strong Wind Risk

| Wind Speed (km/h) | Severity | Alert Window |
|-------------------|----------|--------------|
| >= 60 | CRITICAL | 12 hours |
| >= 45 | HIGH | 12 hours |
| >= 30 | MEDIUM | 12 hours |
| < 30 | NONE | - |

**Recommendations:**
- Secure covers and equipment
- Postpone spraying
- Support tall plants

### Disease Risk (Fungal)

Fungal diseases thrive in warm, humid conditions:

| Temperature (C) | Humidity (%) | Severity | Alert Window |
|-----------------|--------------|----------|--------------|
| 20-30 | >= 85 | HIGH | 48 hours |
| 18-32 | >= 75 | MEDIUM | 48 hours |
| Any | >= 80 | LOW | 48 hours |
| Otherwise | - | NONE | - |

**Recommendations:**
- Inspect plants for early symptoms
- Improve ventilation in greenhouses
- Apply preventive spray if needed

---

## Irrigation Adjustment Algorithm

The irrigation adjustment factor is calculated based on multiple weather conditions:

### Base Factor Adjustments

| Condition | Adjustment |
|-----------|------------|
| **Temperature** | |
| >= 40C | +0.3 |
| >= 35C | +0.2 |
| >= 30C | +0.1 |
| <= 15C | -0.2 |
| **Humidity** | |
| <= 30% | +0.2 |
| >= 80% | -0.2 |
| **Wind Speed** | |
| >= 30 km/h | +0.15 |
| >= 20 km/h | +0.1 |
| **Precipitation** | |
| >= 20 mm | -0.5 |
| >= 10 mm | -0.3 |
| >= 5 mm | -0.15 |

### Factor Bounds

The adjustment factor is clamped to range **0.3 - 1.5**

### Recommendation Mapping

| Factor Range | Arabic | English |
|--------------|--------|---------|
| >= 1.3 | Increase irrigation by 30% or more | |
| >= 1.15 | Increase irrigation by 15-30% | |
| 0.85 - 1.15 | Normal irrigation rate | |
| 0.6 - 0.85 | Reduce irrigation by 15-40% | |
| < 0.6 | Delay irrigation - sufficient moisture | |

---

## NATS Events

### Published Events

#### sahool.weather.alert

Published when weather alerts are generated.

**Subject:** `sahool.weather.alert`
**Version:** 1

**Envelope Schema:**
```json
{
  "event_id": "UUID",
  "event_type": "weather_alert",
  "version": 1,
  "aggregate_id": "field_id",
  "tenant_id": "string",
  "correlation_id": "string",
  "timestamp": "ISO8601",
  "payload": {
    "field_id": "string",
    "alert_type": "heat_stress | frost | heavy_rain | strong_wind | disease_risk",
    "severity": "low | medium | high | critical",
    "window_hours": "integer",
    "title_ar": "string (optional)",
    "title_en": "string (optional)"
  }
}
```

#### sahool.weather.irrigation_adjustment

Published when irrigation adjustments are calculated.

**Subject:** `sahool.weather.irrigation_adjustment`
**Version:** 1

**Envelope Schema:**
```json
{
  "event_id": "UUID",
  "event_type": "irrigation_adjustment",
  "version": 1,
  "aggregate_id": "field_id",
  "tenant_id": "string",
  "correlation_id": "string",
  "timestamp": "ISO8601",
  "payload": {
    "field_id": "string",
    "adjustment_factor": "float",
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

### Defined but Not Currently Published

| Event Type | Subject |
|------------|---------|
| weather_forecast_issued | sahool.weather.forecast_issued |

### Subscribed Events

**None** - This service only publishes events, it does not subscribe to any.

---

## Weather Providers

### Multi-Provider Service

The service supports multiple weather providers with automatic fallback:

| Priority | Provider | API Key Required | Features |
|----------|----------|------------------|----------|
| 1 | Open-Meteo | No (Free) | Current, Daily (16 days), Hourly (168 hours) |
| 2 | OpenWeatherMap | Yes | Current, Daily (5 days), Hourly (5 days) |
| 3 | WeatherAPI | Yes | Current, Daily (14 days), Hourly (48 hours) |

### Caching

- In-memory cache with 10-minute TTL
- Cache key format: `{type}_{lat:.2f}_{lon:.2f}_{params}`
- Cached results return with `provider: "cache"` and `is_cached: true`

### WMO Weather Code Translations

The Open-Meteo provider translates WMO weather codes to conditions:

| Code Range | English | Arabic |
|------------|---------|--------|
| 0 | Clear | |
| 1-3 | Partly Cloudy | |
| 4-49 | Foggy | |
| 50-59 | Drizzle | |
| 60-69 | Rain | |
| 70-79 | Snow | |
| 80-84 | Rain Showers | |
| 85-94 | Snow Showers | |
| 95+ | Thunderstorm | |

---

## Dependencies

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | HTTP client for weather APIs |
| python-dotenv | 1.0.1 | Environment variables |
| nats-py | 2.9.0 | NATS messaging |
| python-dateutil | 2.8.2 | Date utilities |
| structlog | >=24.1.0 | Structured logging |

### Shared Libraries

| Module | Purpose |
|--------|---------|
| shared.errors_py | Unified error handling |
| shared.logging_config | Structured logging configuration |
| shared.auth.dependencies | Authentication (optional) |
| shared.auth.models | User model |

### External APIs

| API | URL | Key Required |
|-----|-----|--------------|
| Open-Meteo | https://api.open-meteo.com/v1/forecast | No |
| OpenWeatherMap | https://api.openweathermap.org/data/2.5 | Yes |
| WeatherAPI | https://api.weatherapi.com/v1 | Yes |

### Infrastructure

| Component | Purpose |
|-----------|---------|
| NATS | Event publishing |
| Kong Gateway | API routing |

---

## Environment Variables

### Required

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Service port | 8108 |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| NATS_URL | NATS server URL | nats://nats:4222 |
| USE_MOCK_WEATHER | Use mock provider for testing | false |
| USE_MULTI_PROVIDER | Enable multi-provider fallback | true |
| OPENWEATHERMAP_API_KEY | OpenWeatherMap API key | (empty) |
| WEATHERAPI_KEY | WeatherAPI key | (empty) |
| LOG_LEVEL | Logging level | INFO |
| ENVIRONMENT | Environment name | development |
| JWT_SECRET_KEY | JWT secret for auth | (from docker-compose) |
| JWT_ALGORITHM | JWT algorithm | RS256 |
| DATABASE_URL | PostgreSQL connection | (from docker-compose) |

### Missing Environment Variables

The following environment variables are referenced in docker-compose but NOT used in the code:

1. **DATABASE_URL** - Defined but never used (no database connection in this service)
2. **JWT_SECRET_KEY** / **JWT_ALGORITHM** - Defined but authentication is optional fallback

---

## Kong Gateway Configuration

```yaml
- name: weather-core
  host: weather-core
  port: 8108
  protocol: http
  routes:
    - name: weather-core-route
      paths:
        - /api/v1/weather-core
        - /weather-core
        - /weather-core-legacy
      strip_path: true
      protocols: ["http", "https"]
```

**Access URLs:**
- `http://kong:8000/api/v1/weather-core/weather/current`
- `http://kong:8000/weather-core/weather/forecast`

---

## Docker Configuration

### Dockerfile Summary

- **Base Image:** python:3.11-slim-bookworm
- **Non-root User:** sahool
- **Healthcheck:** HTTP GET /healthz every 30s
- **Default Port:** 8108

### Docker Compose (Deprecated Profile)

```yaml
weather-core:
  profiles:
    - deprecated
    - legacy
  labels:
    - "com.sahool.deprecated=true"
    - "com.sahool.replacement=weather-service"
```

**Note:** Service requires explicit profile activation: `docker compose --profile deprecated up weather-core`

---

## Testing

### Test File

`/home/user/sahool-unified-v15-idp/apps/services/weather-core/tests/test_risks.py`

### Test Coverage

| Test Class | Methods | Coverage |
|------------|---------|----------|
| TestAssessWeather | 7 | Heat stress (critical, high), Frost, Heavy rain, Strong wind, Disease risk, Normal conditions |
| TestIrrigationAdjustment | 5 | Hot/dry increase, Rain decrease, Mild weather normal, Bilingual recommendations, Factor bounds |

### Running Tests

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/weather-core
pytest tests/ -v
```

---

## Bugs, Issues, and Recommendations

### Bugs

#### 1. Version Inconsistency
**Severity:** Low
**Location:** `/home/user/sahool-unified-v15-idp/apps/services/weather-core/src/main.py`

```python
# Line 55: version "15.3.3"
logger.info("weather_core_starting", port=8108, version="15.3.3")

# Line 118: version "15.3.3"
return {"status": "healthy", "service": "weather-core", "version": "15.3.3"}

# Line 127: version "16.0.0"
"version": "16.0.0",

# Line 101: FastAPI version "15.3.3"
version="15.3.3",
```

**Recommendation:** Standardize all version references to 16.0.0 or use a constant.

#### 2. Deprecated datetime.utcnow() Usage
**Severity:** Low
**Location:** Multiple files in providers

```python
# multi_provider.py line 228, 444, 602
timestamp=datetime.utcnow().isoformat()

# open_meteo.py line 123, 277
timestamp=datetime.utcnow().isoformat()
```

`datetime.utcnow()` is deprecated in Python 3.12+. Use `datetime.now(UTC)` instead (already correctly used in `publish.py`).

#### 3. Unused Imports
**Severity:** Low
**Location:** `/home/user/sahool-unified-v15-idp/apps/services/weather-core/src/providers/open_meteo.py`

```python
from datetime import date, datetime  # 'date' is unused
```

### Issues

#### 1. README Documentation Out of Sync
**Severity:** Medium
**Location:** `/home/user/sahool-unified-v15-idp/apps/services/weather-core/README.md`

The README documents:
- Port 8098 (actual: 8108)
- GET endpoints (actual: POST for weather data)
- Endpoints that don't exist: `/assess`, `/heat-stress`, `/frost-risk`, `/disease-risk`, `/irrigation/adjustment`, `/irrigation/calculate`, `/weather/historical`

**Recommendation:** Update README to match actual implementation or remove since service is deprecated.

#### 2. No Database Usage Despite DATABASE_URL
**Severity:** Low

The service receives `DATABASE_URL` from docker-compose but never uses it. This is unnecessary configuration.

#### 3. Optional Auth Without Clear Behavior
**Severity:** Low
**Location:** `/home/user/sahool-unified-v15-idp/apps/services/weather-core/src/main.py`

```python
AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    User = None

    def get_current_user():
        """Placeholder when auth not available"""
        return None
```

When auth is unavailable, endpoints still work but without authentication. This should be documented or made explicit.

#### 4. Event Type Defined But Not Published
**Severity:** Low
**Location:** `/home/user/sahool-unified-v15-idp/apps/services/weather-core/src/events/types.py`

`WEATHER_FORECAST_ISSUED` is defined but never published by any endpoint.

#### 5. Potential None Handling in forecast
**Severity:** Low
**Location:** `/home/user/sahool-unified-v15-idp/apps/services/weather-core/src/providers/multi_provider.py`

```python
precipitation_mm=daily.get("precipitation_sum", [0])[i] or 0,
```

This assumes `daily.get()` returns a list with at least `i` elements. If the API returns fewer elements, this will cause an IndexError.

### Recommendations

#### 1. Migrate to weather-service
This service is deprecated. All new development should use `weather-service` (port 8092).

#### 2. Add Request Timeout Configuration
The httpx client uses 30s timeout, but this should be configurable via environment variable.

#### 3. Add Retry Logic for External APIs
Currently, failures cascade to next provider. Consider adding retry logic with exponential backoff.

#### 4. Add Structured Error Responses
Error responses should follow a consistent schema with error codes for client handling.

#### 5. Add Prometheus Metrics
Consider adding `/metrics` endpoint for monitoring:
- Weather API request latency
- Provider failure counts
- Cache hit/miss ratio
- Alert generation counts

#### 6. Consider Redis for Caching
Current in-memory cache is lost on restart. Redis would provide persistence and shared caching across instances.

---

## File Manifest

| File | Lines | Purpose |
|------|-------|---------|
| src/main.py | 442 | FastAPI application entry point |
| src/risks.py | 354 | Weather risk assessment algorithms |
| src/events/publish.py | 187 | NATS event publisher |
| src/events/types.py | 37 | Event type definitions |
| src/events/__init__.py | 24 | Events module exports |
| src/providers/multi_provider.py | 845 | Multi-provider weather service |
| src/providers/open_meteo.py | 308 | Open-Meteo provider + mock |
| src/providers/__init__.py | 44 | Provider module exports |
| tests/test_risks.py | 179 | Unit tests for risk assessment |
| requirements.txt | 17 | Python dependencies |
| Dockerfile | 64 | Container build configuration |
| README.md | 184 | Documentation (outdated) |

---

## Migration Guide

### Migrating from weather-core to weather-service

1. **Update base URL:**
   - Old: `http://weather-core:8108` or `/api/v1/weather-core`
   - New: `http://weather-service:8092` or `/api/v1/weather`

2. **Update event subscriptions:**
   - Events remain on `sahool.weather.*` namespace
   - No changes needed for NATS subscribers

3. **API compatibility:**
   - weather-service provides superset of weather-core functionality
   - Check weather-service documentation for endpoint mappings

4. **Environment variables:**
   - Remove `DATABASE_URL` if not needed
   - Weather provider keys remain the same

---

*Generated: 2026-01-25*
*Service Status: DEPRECATED*
