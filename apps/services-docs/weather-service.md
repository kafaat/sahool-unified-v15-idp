# Weather Service Analysis

**Service Name:** weather-service
**Type:** Python/FastAPI (with NestJS/Prisma components)
**Port:** 8092 (Kong Gateway), 8108 (Application)
**Version:** 16.0.0
**Path:** `/home/user/sahool-unified-v15-idp/apps/services/weather-service/`

---

## Overview

The Weather Service is a unified agricultural weather service providing real-time weather data, risk assessment, forecasting, and irrigation recommendations for the SAHOOL platform. It consolidates the previous `weather-core` and `weather-advanced` services into a single service.

### Key Features
- Multi-provider weather data aggregation (Open-Meteo, OpenWeatherMap, WeatherAPI)
- Agricultural risk assessment (heat stress, frost, drought, disease risk)
- Weather forecasting (hourly and daily)
- Irrigation scheduling and recommendations
- Growing Degree Days (GDD) calculation
- Evapotranspiration (ET0) estimation
- Spray window recommendations
- Yemen-specific location database (22 governorates)
- NATS event publishing for weather alerts

---

## Kong Gateway Configuration

| Property | Value |
|----------|-------|
| Host | `weather-service` |
| Port | `8092` |
| Routes | `/api/v1/weather`, `/weather` |
| Strip Path | `true` |

---

## API Endpoints

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Liveness probe - returns service health status |
| GET | `/readyz` | Readiness probe - returns readiness status |

#### Health Response Schema
```json
{
  "status": "healthy",
  "service": "weather-service",
  "version": "16.0.0",
  "timestamp": "2026-01-25T12:00:00Z"
}
```

### Weather Data Endpoints

#### POST `/weather/current`
Get current weather from API provider with automatic fallback.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "lat": "float (required, -90 to 90)",
  "lon": "float (required, -180 to 180)",
  "correlation_id": "string (optional)"
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
  "provider": "string",
  "current": {
    "temperature_c": "float",
    "humidity_pct": "float",
    "wind_speed_kmh": "float",
    "wind_direction_deg": "int",
    "wind_direction": "string",
    "precipitation_mm": "float",
    "cloud_cover_pct": "float",
    "pressure_hpa": "float",
    "uv_index": "float",
    "condition": "string",
    "condition_ar": "string",
    "timestamp": "string"
  },
  "alerts": ["WeatherAlert[]"],
  "event_ids": ["string[]"]
}
```

#### POST `/weather/forecast`
Get weather forecast for specified location.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "lat": "float (required, -90 to 90)",
  "lon": "float (required, -180 to 180)",
  "correlation_id": "string (optional)"
}
```

**Query Parameters:**
- `days`: Number of forecast days (1-16, default: 7)

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
      "date": "string",
      "temp_max_c": "float",
      "temp_min_c": "float",
      "precipitation_mm": "float",
      "precipitation_probability_pct": "float",
      "wind_speed_max_kmh": "float",
      "uv_index_max": "float",
      "condition": "string",
      "condition_ar": "string",
      "sunrise": "string",
      "sunset": "string"
    }
  ],
  "days": "int"
}
```

#### POST `/weather/assess`
Assess weather conditions and generate agricultural alerts.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_c": "float (required)",
  "humidity_pct": "float (optional)",
  "wind_speed_kmh": "float (optional)",
  "precipitation_mm": "float (optional)",
  "uv_index": "float (optional)",
  "correlation_id": "string (optional)"
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "alerts": [
    {
      "alert_type": "string",
      "severity": "low|medium|high|critical",
      "title_ar": "string",
      "title_en": "string",
      "description_ar": "string",
      "description_en": "string",
      "window_hours": "int",
      "recommendations_ar": ["string[]"],
      "recommendations_en": ["string[]"]
    }
  ],
  "alert_count": "int",
  "event_ids": ["string[]"],
  "published": "boolean"
}
```

#### POST `/weather/irrigation`
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
  "correlation_id": "string (optional)"
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
  "adjustment_factor": "float (0.3-1.5)",
  "recommendation_ar": "string",
  "recommendation_en": "string",
  "event_id": "string|null",
  "published": "boolean"
}
```

### Advanced Agricultural Endpoints

#### POST `/weather/evapotranspiration`
Calculate Reference Evapotranspiration (ET0) using FAO-56 Penman-Monteith.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_c": "float (required, -50 to 60)",
  "humidity_pct": "float (required, 0 to 100)",
  "wind_speed_kmh": "float (required, >= 0)",
  "solar_radiation_mj": "float (default: 15.0, 0 to 50)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "evapotranspiration": {
    "et0_mm_day": "float",
    "daily_water_liters_per_sqm": "float",
    "weekly_water_liters_per_sqm": "float",
    "vapor_pressure_deficit_kpa": "float",
    "classification": "very_low|low|moderate|high|very_high",
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

#### POST `/weather/gdd`
Calculate Growing Degree Days (GDD) for crop development prediction.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_max_c": "float (required, -50 to 60)",
  "temp_min_c": "float (required, -50 to 60)",
  "base_temp_c": "float (default: 10.0, 0 to 30)",
  "upper_temp_c": "float (default: 30.0, 20 to 50)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "growing_degree_days": {
    "gdd_daily": "float",
    "temp_avg_c": "float",
    "base_temp_c": "float",
    "upper_temp_c": "float",
    "growth_rate": "dormant|slow|moderate|fast|very_fast",
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

#### POST `/weather/spray-window`
Assess spray window suitability for pesticide/herbicide application.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_c": "float (required, -50 to 60)",
  "humidity_pct": "float (required, 0 to 100)",
  "wind_speed_kmh": "float (required, >= 0)",
  "precipitation_probability": "float (default: 0, 0 to 100)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "spray_window": {
    "score": "int (0-100)",
    "suitability": "excellent|good|fair|poor",
    "color": "green|yellow|orange|red",
    "is_suitable": "boolean",
    "issues": ["string[]"],
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

#### POST `/weather/frost-risk`
Assess frost risk with protection recommendations.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_c": "float (required, -50 to 60)",
  "humidity_pct": "float (required, 0 to 100)",
  "wind_speed_kmh": "float (required, >= 0)",
  "cloud_cover_pct": "float (default: 0, 0 to 100)",
  "dew_point_c": "float (optional, -50 to 50)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "frost_risk": {
    "risk_score": "int",
    "risk_level": "none|low|moderate|high|critical",
    "color": "green|blue|yellow|orange|red",
    "temp_risk": "string",
    "dew_point_c": "float",
    "frost_likely": "boolean",
    "protection_measures": [
      {
        "method_en": "string",
        "method_ar": "string",
        "description_en": "string",
        "description_ar": "string",
        "effectiveness": "low|medium|high"
      }
    ],
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

#### POST `/weather/heat-stress`
Calculate heat stress index for crops.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "temp_c": "float (required, -50 to 60)",
  "humidity_pct": "float (required, 0 to 100)",
  "solar_radiation_mj": "float (default: 15.0, 0 to 50)",
  "wind_speed_kmh": "float (default: 10.0, >= 0)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "heat_stress": {
    "temperature_humidity_index": "float",
    "effective_stress_score": "float",
    "stress_level": "none|low|moderate|high|severe|extreme",
    "color": "green|lightgreen|yellow|orange|red|darkred",
    "crop_impact": "optimal|minor_stress|reduced_growth|significant_damage|severe_damage",
    "is_critical": "boolean",
    "mitigation_measures": [
      {
        "method_en": "string",
        "method_ar": "string",
        "description_en": "string",
        "description_ar": "string",
        "priority": "low|medium|high"
      }
    ],
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

#### POST `/weather/chill-hours`
Calculate chill hours/units for fruit trees.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "hourly_temps": ["float[] (required)"],
  "model": "string (default: 'utah', options: simple|utah|dynamic)",
  "base_temp_c": "float (default: 7.2, 0 to 15)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "chill_hours": {
    "chill_units": "float",
    "model": "string",
    "base_temp_c": "float|null",
    "hours_analyzed": "int",
    "satisfied_crops": [
      {
        "crop": "string",
        "crop_ar": "string",
        "requirement_met_pct": "int"
      }
    ],
    "insufficient_crops": [
      {
        "crop": "string",
        "crop_ar": "string",
        "required": "int",
        "current": "int",
        "deficit": "int"
      }
    ],
    "crop_requirements": "object",
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

#### POST `/weather/drought-index`
Calculate drought stress index based on water balance.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "precipitation_mm": "float (required, >= 0)",
  "et0_mm": "float (required, >= 0)",
  "days": "int (default: 30, 1 to 365)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "drought_index": {
    "water_balance_mm": "float",
    "aridity_index": "float",
    "drought_level": "none|mild|moderate|severe|extreme",
    "color": "green|yellow|orange|red|darkred",
    "irrigation_need_mm": "float",
    "irrigation_need_liters_per_sqm": "float",
    "period_days": "int",
    "precipitation_mm": "float",
    "evapotranspiration_mm": "float",
    "recommendation_ar": "string",
    "recommendation_en": "string"
  }
}
```

#### POST `/weather/agricultural-report`
Comprehensive agricultural weather report combining all metrics.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "lat": "float (required, -90 to 90)",
  "lon": "float (required, -180 to 180)",
  "correlation_id": "string (optional)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "location": {
    "lat": "float",
    "lon": "float"
  },
  "current_weather": "object",
  "evapotranspiration": "object",
  "growing_degree_days": "object",
  "spray_window": "object",
  "irrigation_adjustment": "object",
  "alerts": ["WeatherAlert[]"],
  "alert_count": "int"
}
```

#### POST `/weather/comprehensive-stress-report`
Comprehensive weather stress assessment combining frost, heat, and spray window.

**Request Schema:**
```json
{
  "tenant_id": "string (required)",
  "field_id": "string (required)",
  "lat": "float (required, -90 to 90)",
  "lon": "float (required, -180 to 180)",
  "correlation_id": "string (optional)"
}
```

**Response Schema:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "location": {
    "lat": "float",
    "lon": "float"
  },
  "current_weather": "object",
  "overall_status": "normal|caution|warning|critical",
  "overall_color": "green|yellow|orange|red",
  "frost_risk": "object",
  "heat_stress": "object",
  "spray_window": "object"
}
```

### Quick Check Endpoints

#### GET `/weather/heat-stress/{temp_c}`
Quick heat stress check for a temperature.

**Response Schema:**
```json
{
  "temperature_c": "float",
  "alert_type": "heat_stress",
  "severity": "none|low|medium|high|critical",
  "at_risk": "boolean"
}
```

#### GET `/weather/providers`
Get list of available weather providers.

**Response Schema:**
```json
{
  "multi_provider_enabled": "boolean",
  "providers": [
    {
      "name": "string",
      "configured": "boolean",
      "type": "string"
    }
  ],
  "total": "int",
  "configured": "int"
}
```

---

## NATS Events

### Published Events

| Event Type | Subject | Description |
|------------|---------|-------------|
| `weather_alert` | `sahool.weather.alert` | Published when weather conditions trigger agricultural alerts |
| `irrigation_adjustment` | `sahool.weather.irrigation_adjustment` | Published when irrigation adjustments are calculated |
| `weather_forecast_issued` | `sahool.weather.forecast_issued` | Published when new forecasts are generated |

### Event Envelope Schema

```json
{
  "event_id": "uuid",
  "event_type": "weather_alert|irrigation_adjustment|weather_forecast_issued",
  "version": 1,
  "aggregate_id": "field_id",
  "tenant_id": "string",
  "correlation_id": "string",
  "timestamp": "ISO-8601",
  "payload": {
    "field_id": "string",
    "alert_type": "string",
    "severity": "string",
    "window_hours": "int",
    "title_ar": "string",
    "title_en": "string"
  }
}
```

### Weather Alert Event Payload

```json
{
  "field_id": "string",
  "alert_type": "heat_stress|frost|heavy_rain|strong_wind|disease_risk",
  "severity": "low|medium|high|critical",
  "window_hours": "int",
  "title_ar": "string",
  "title_en": "string"
}
```

### Irrigation Adjustment Event Payload

```json
{
  "field_id": "string",
  "adjustment_factor": "float",
  "recommendation_ar": "string",
  "recommendation_en": "string"
}
```

---

## Weather Provider Integrations

### 1. Open-Meteo (Primary - Free)

| Property | Value |
|----------|-------|
| Base URL | `https://api.open-meteo.com/v1/forecast` |
| API Key Required | No |
| Rate Limit | 10,000 requests/day |
| Timeout | 30 seconds |
| Priority | Primary |

**Features:**
- Current weather (temperature, humidity, wind, precipitation, pressure, UV, cloud cover)
- Daily forecast (up to 16 days)
- Hourly forecast (up to 168 hours)
- WMO weather code translation to English/Arabic

### 2. OpenWeatherMap (Secondary)

| Property | Value |
|----------|-------|
| Base URL | `https://api.openweathermap.org/data/2.5` |
| API Key Required | Yes (`OPENWEATHERMAP_API_KEY`) |
| Rate Limit | 1,000 requests/day (free tier) |
| Timeout | 30 seconds |
| Priority | Secondary |

**Features:**
- Current weather
- 5-day/3-hour forecast (grouped to daily)
- Condition translation to Arabic

**Limitations:**
- UV index not available in basic API
- 3-hour intervals for forecast (not true hourly)

### 3. WeatherAPI (Secondary)

| Property | Value |
|----------|-------|
| Base URL | `https://api.weatherapi.com/v1` |
| API Key Required | Yes (`WEATHERAPI_KEY`) |
| Rate Limit | 1,000 requests/day (free tier) |
| Timeout | 30 seconds |
| Priority | Secondary |

**Features:**
- Current weather with full data
- Up to 14-day forecast
- Astronomy data (sunrise/sunset)
- True hourly forecast

### 4. Yemen Met Service (Future/Mock)

| Property | Value |
|----------|-------|
| Status | Not Implemented (Mock) |
| API Key Required | Yes (`YEMEN_MET_API_KEY`) |
| Rate Limit | 500 requests/day |
| Priority | Fallback |

Placeholder for future integration with Yemen's national meteorological service.

### Multi-Provider Fallback Logic

1. Open-Meteo is always tried first (free, no key required)
2. If Open-Meteo fails and `OPENWEATHERMAP_API_KEY` is set, try OpenWeatherMap
3. If both fail and `WEATHERAPI_KEY` is set, try WeatherAPI
4. Results are cached for 10 minutes to reduce API calls

---

## Database Schema (Prisma)

### WeatherObservation

Stores actual observed weather data.

```prisma
model WeatherObservation {
  id            String   @id @default(uuid())
  locationId    String   @map("location_id")
  tenantId      String?  @map("tenant_id")
  latitude      Float
  longitude     Float
  timestamp     DateTime
  temperature   Float    // Celsius
  humidity      Float    // %
  pressure      Float    // hPa
  windSpeed     Float    // m/s
  windDirection Float    // degrees
  rainfall      Float?   // mm
  uvIndex       Float?
  cloudCover    Float?   // %
  visibility    Float?   // meters
  source        String   // open-meteo, openweathermap, weatherapi
  rawData       Json?    @map("raw_data")
  createdAt     DateTime @default(now()) @map("created_at")
}
```

### WeatherForecast

Stores weather forecast data.

```prisma
model WeatherForecast {
  id          String   @id @default(uuid())
  locationId  String   @map("location_id")
  tenantId    String?  @map("tenant_id")
  forecastFor DateTime @map("forecast_for")
  fetchedAt   DateTime @map("fetched_at")
  provider    String
  hourlyData  Json     @map("hourly_data")
  dailyData   Json     @map("daily_data")
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")
}
```

### WeatherAlert

Stores weather alerts and warnings.

```prisma
model WeatherAlert {
  id          String        @id @default(uuid())
  locationId  String        @map("location_id")
  tenantId    String?       @map("tenant_id")
  alertType   AlertType     @map("alert_type")
  severity    AlertSeverity
  headline    String
  description String        @db.Text
  startTime   DateTime      @map("start_time")
  endTime     DateTime      @map("end_time")
  source      String
  createdAt   DateTime      @default(now()) @map("created_at")
  updatedAt   DateTime      @updatedAt @map("updated_at")
}

enum AlertType {
  HEAT_STRESS
  FROST
  HEAVY_RAIN
  DROUGHT
  STRONG_WIND
  STORM
  DISEASE_RISK
  OTHER
}

enum AlertSeverity {
  INFO
  MINOR
  MODERATE
  SEVERE
  EXTREME
}
```

### LocationConfig

Stores monitored location configurations.

```prisma
model LocationConfig {
  id            String   @id @default(uuid())
  tenantId      String   @map("tenant_id")
  name          String
  latitude      Float
  longitude     Float
  timezone      String   @default("Asia/Aden")
  isActive      Boolean  @default(true) @map("is_active")
  fetchInterval Int      @default(3600) @map("fetch_interval")
  createdAt     DateTime @default(now()) @map("created_at")
  updatedAt     DateTime @updatedAt @map("updated_at")
}
```

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| httpx | 0.28.1 | HTTP client for external APIs |
| python-dotenv | 1.0.1 | Environment variable loading |
| nats-py | 2.9.0 | NATS messaging |
| python-dateutil | 2.8.2 | Date utilities |
| structlog | >=24.1.0 | Structured logging |

### Node.js Dependencies (package.json)

| Package | Version | Purpose |
|---------|---------|---------|
| @nestjs/common | ^10.4.15 | NestJS core |
| @nestjs/core | ^10.4.15 | NestJS core |
| @nestjs/platform-express | ^10.4.15 | Express adapter |
| @nestjs/swagger | ^8.1.0 | API documentation |
| @nestjs/throttler | ^6.2.1 | Rate limiting |
| @prisma/client | ^5.22.0 | Database ORM |
| prisma | ^5.22.0 | Database tooling |
| typescript | ^5.7.2 | TypeScript |
| class-transformer | ^0.5.1 | Object transformation |
| class-validator | ^0.14.1 | Input validation |
| rxjs | ^7.8.1 | Reactive extensions |

### Shared Module Dependencies

- `shared.errors_py` - Unified error handling
- `shared.middleware.security_headers` - Security headers middleware

---

## Environment Variables

### Required Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string with TLS | Yes (for Prisma) |
| `DATABASE_URL_DIRECT` | Direct PostgreSQL URL (bypasses PgBouncer) | Yes (for migrations) |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8092` (Docker) / `8108` (app) | Service port |
| `NATS_URL` | `nats://nats:4222` | NATS server URL |
| `USE_MOCK_WEATHER` | `false` | Use mock data for testing |
| `USE_MULTI_PROVIDER` | `true` | Enable multi-provider fallback |
| `OPENWEATHERMAP_API_KEY` | - | OpenWeatherMap API key |
| `WEATHERAPI_KEY` | - | WeatherAPI.com API key |
| `YEMEN_MET_ENABLED` | `false` | Enable Yemen Met Service |
| `YEMEN_MET_API_KEY` | - | Yemen Met Service API key |

### Cache Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WEATHER_CACHE_ENABLED` | `true` | Enable weather data caching |
| `WEATHER_CACHE_CURRENT_TTL` | `10` | Current weather cache TTL (minutes) |
| `WEATHER_CACHE_FORECAST_TTL` | `60` | Forecast cache TTL (minutes) |

### Alert Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WEATHER_ALERTS_ENABLED` | `true` | Enable alert generation |
| `WEATHER_AG_INDICES_ENABLED` | `true` | Enable agricultural indices |
| `FROST_CRITICAL_TEMP` | `0` | Critical frost temperature (C) |
| `HEAT_WAVE_CRITICAL_TEMP` | `45` | Critical heat wave temperature (C) |
| `HEAVY_RAIN_CRITICAL_MM` | `50` | Critical rain threshold (mm) |

### Agricultural Indices Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GDD_BASE_TEMP` | `10` | GDD base temperature (C) |
| `CHILL_HOURS_THRESHOLD` | `7.2` | Chill hours threshold (C) |

---

## Missing Environment Variables

Based on the analysis, the following environment variables are referenced in the code but not documented in docker-compose:

| Variable | Location | Status |
|----------|----------|--------|
| `OPENWEATHER_API_KEY` | docker-compose | **Inconsistent naming** - Code uses `OPENWEATHERMAP_API_KEY` |
| `DATABASE_URL_DIRECT` | Prisma schema | Missing in docker-compose |
| `YEMEN_MET_ENABLED` | config.py | Not in docker-compose |
| `YEMEN_MET_API_KEY` | config.py | Not in docker-compose |
| `WEATHER_CACHE_ENABLED` | config.py | Not in docker-compose |
| `WEATHER_CACHE_CURRENT_TTL` | config.py | Not in docker-compose |
| `WEATHER_CACHE_FORECAST_TTL` | config.py | Not in docker-compose |
| `WEATHER_ALERTS_ENABLED` | config.py | Not in docker-compose |
| `WEATHER_AG_INDICES_ENABLED` | config.py | Not in docker-compose |
| `FROST_CRITICAL_TEMP` | config.py | Not in docker-compose |
| `HEAT_WAVE_CRITICAL_TEMP` | config.py | Not in docker-compose |
| `HEAVY_RAIN_CRITICAL_MM` | config.py | Not in docker-compose |
| `GDD_BASE_TEMP` | config.py | Not in docker-compose |
| `CHILL_HOURS_THRESHOLD` | config.py | Not in docker-compose |

---

## Bugs, Issues, and Recommendations

### Critical Issues

#### 1. Port Inconsistency
**Severity:** High

The service has conflicting port configurations:
- **main.py** (line 4): States port 8108
- **Dockerfile** (line 49): Sets `ENV PORT=8092` and exposes 8092
- **README.md**: States port 8108
- **Kong Gateway**: Configured for port 8092

**Recommendation:** Standardize to a single port (8092 for Kong compatibility) and update all documentation.

#### 2. Environment Variable Naming Inconsistency
**Severity:** Medium

- docker-compose uses `OPENWEATHER_API_KEY`
- Code uses `OPENWEATHERMAP_API_KEY` (line 161 in config.py, line 409 in multi_provider.py)

**Recommendation:** Standardize naming to `OPENWEATHERMAP_API_KEY` across all configuration.

#### 3. Unused Prisma/NestJS Components
**Severity:** Low

The service has both Python/FastAPI and NestJS/Prisma components:
- `package.json` with NestJS dependencies
- `prisma/schema.prisma` with database models
- TypeScript test files (`__tests__/weather.service.spec.ts`)

But the main application is Python/FastAPI. The Prisma schema appears unused by the Python code.

**Recommendation:** Either:
- Remove unused NestJS components if not needed
- Implement database persistence using Prisma in Python (via prisma-client-py) or asyncpg
- Clarify the purpose of the dual-stack architecture

### Medium Issues

#### 4. Missing `get_current_weather` Method
**Severity:** Medium
**Location:** `main.py` lines 576-579 and 791-795

The code calls `get_current_weather` method on providers:
```python
weather_data = await app.state.multi_provider.get_current_weather(lat=req.lat, lon=req.lon)
```

But the `MultiWeatherService` class only has `get_current` method, not `get_current_weather`.

**Recommendation:** Fix the method name to `get_current` or add the missing method.

#### 5. Import Statement with Unused `datetime` Alias
**Severity:** Low
**Location:** `publish.py` line 8

```python
from datetime import timezone, datetime, UTC
```

`timezone` is imported but never used.

**Recommendation:** Remove unused import.

#### 6. Deprecated `datetime.utcnow()`
**Severity:** Low
**Location:** Multiple files (open_meteo.py, multi_provider.py)

Using deprecated `datetime.utcnow()` instead of timezone-aware alternatives.

**Recommendation:** Replace with `datetime.now(UTC)` or `datetime.now(timezone.utc)`.

### Low Issues

#### 7. Missing Error Handling for Provider Sorting
**Severity:** Low
**Location:** `forecast_integration.py` lines 268-273

The provider sorting logic may fail if provider config doesn't have expected attributes.

**Recommendation:** Add defensive checks for attribute access.

#### 8. Hardcoded Default Values
**Severity:** Low

Several default values are hardcoded that should be configurable:
- Solar radiation default (15.0 MJ/m²/day for Yemen)
- Forecast max days (16)
- Cache duration (10 minutes)

**Recommendation:** Move these to configuration.

### Recommendations for Improvement

1. **Add Rate Limiting:** Implement rate limiting for external API calls to prevent quota exhaustion.

2. **Add Circuit Breaker:** Implement circuit breaker pattern for external provider calls.

3. **Add Metrics:** Add Prometheus metrics for:
   - API response times
   - Provider success/failure rates
   - Cache hit/miss rates
   - Alert counts by type

4. **Add Database Persistence:** The Prisma schema is defined but not connected. Consider implementing actual persistence for:
   - Historical weather data
   - Alert history
   - Forecast accuracy tracking

5. **Add Webhook Support:** Allow subscribing to weather alerts via webhooks in addition to NATS.

6. **Add Caching Layer:** The in-memory cache is basic. Consider Redis for distributed caching.

7. **Improve Test Coverage:** Add more tests for:
   - Multi-provider fallback scenarios
   - NATS event publishing
   - Error handling edge cases

---

## File Structure

```
apps/services/weather-service/
├── Dockerfile                          # Docker build configuration
├── README.md                           # Service documentation
├── FORECAST_INTEGRATION.md             # Forecast integration docs
├── package.json                        # Node.js dependencies
├── requirements.txt                    # Python dependencies
├── prisma/
│   └── schema.prisma                   # Database schema
├── src/
│   ├── __init__.py
│   ├── main.py                         # FastAPI application entry point
│   ├── config.py                       # Service configuration
│   ├── risks.py                        # Weather risk assessment logic
│   ├── locations.py                    # Yemen locations database
│   ├── forecast_integration.py         # Forecast integration service
│   ├── forecast_example.py             # Forecast usage examples
│   ├── events/
│   │   ├── __init__.py
│   │   ├── publish.py                  # NATS event publisher
│   │   └── types.py                    # Event type definitions
│   └── providers/
│       ├── __init__.py
│       ├── open_meteo.py               # Open-Meteo provider
│       └── multi_provider.py           # Multi-provider service
└── tests/
    ├── __init__.py
    ├── test_risks.py                   # Risk assessment tests
    ├── test_weather_api.py             # API endpoint tests
    └── test_weather_forecast.py        # Forecast tests
```

---

## Yemen Locations Database

The service includes a built-in database of all 22 Yemen governorates:

| ID | Name (AR) | Latitude | Longitude | Elevation (m) | Region |
|----|-----------|----------|-----------|---------------|--------|
| sanaa | صنعاء | 15.3694 | 44.1910 | 2250 | highland |
| amanat_al_asimah | أمانة العاصمة | 15.3556 | 44.2067 | 2200 | highland |
| amran | عمران | 15.6594 | 43.9439 | 2300 | highland |
| saadah | صعدة | 16.9400 | 43.7614 | 1850 | highland |
| al_jawf | الجوف | 16.5833 | 45.5000 | 1200 | desert |
| hajjah | حجة | 15.6917 | 43.6028 | 1800 | highland |
| al_mahwit | المحويت | 15.4700 | 43.5447 | 2100 | highland |
| dhamar | ذمار | 14.5500 | 44.4000 | 2400 | highland |
| ibb | إب | 13.9667 | 44.1667 | 2050 | highland |
| taiz | تعز | 13.5789 | 44.0219 | 1400 | highland |
| al_bayda | البيضاء | 13.9833 | 45.5667 | 2250 | highland |
| raymah | ريمة | 14.6333 | 43.7167 | 2600 | highland |
| marib | مأرب | 15.4667 | 45.3500 | 1100 | desert |
| hodeidah | الحديدة | 14.7979 | 42.9540 | 12 | coastal |
| aden | عدن | 12.7855 | 45.0187 | 6 | coastal |
| lahij | لحج | 13.0500 | 44.8833 | 150 | highland |
| ad_dali | الضالع | 13.7000 | 44.7333 | 1500 | highland |
| abyan | أبين | 13.0167 | 45.3667 | 50 | coastal |
| hadramaut | حضرموت | 15.9500 | 48.7833 | 650 | desert |
| shabwah | شبوة | 14.5333 | 46.8333 | 900 | desert |
| al_mahrah | المهرة | 16.0667 | 52.2333 | 200 | coastal |
| socotra | سقطرى | 12.4634 | 53.8237 | 250 | island |

---

## Alert Thresholds

### Temperature Thresholds

| Alert Type | Critical | High | Medium |
|------------|----------|------|--------|
| Heat Stress | >= 45°C | >= 42°C | >= 38°C |
| Frost | <= 0°C | <= 2°C | <= 5°C |
| Heat Wave (consecutive days) | >= 45°C (3+ days) | >= 42°C (3+ days) | >= 38°C (3+ days) |

### Precipitation Thresholds

| Alert Type | Critical | High | Medium |
|------------|----------|------|--------|
| Heavy Rain | >= 50mm | >= 30mm | >= 15mm |
| Drought | < 5mm in 14 days | - | - |

### Wind Thresholds

| Alert Type | Critical | High | Medium |
|------------|----------|------|--------|
| Strong Wind | >= 60 km/h | >= 45 km/h | >= 30 km/h |

### Disease Risk Conditions

| Condition | Risk Level |
|-----------|------------|
| Temp 20-30°C + Humidity >= 85% | High |
| Temp 18-32°C + Humidity >= 75% | Medium |
| Humidity >= 80% | Low |

---

## Testing

### Running Tests

```bash
# Python tests
cd apps/services/weather-service
pytest tests/ -v

# Specific test file
pytest tests/test_risks.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

| Module | Coverage |
|--------|----------|
| Risk Assessment | Good |
| API Endpoints | Good |
| Provider Integration | Moderate (mocked) |
| NATS Events | Low |

---

## Related Services

| Service | Relationship |
|---------|-------------|
| `advisory-service` | Consumes weather alerts for crop recommendations |
| `irrigation-smart` | Uses irrigation adjustments for scheduling |
| `notification-service` | Forwards weather alerts to users |
| `field-management-service` | Associates weather data with fields |
| `crop-intelligence-service` | Uses GDD/ET0 for growth modeling |

---

## Migration Notes

This service consolidates:
- `weather-core` (Port 8098/8108) - Core assessment features
- `weather-advanced` (Port 8092) - Advanced forecasting features

All functionality is now available in this unified service.

---

**Last Updated:** 2026-01-25
**Analyzed By:** Claude Opus 4.5
**Version:** 16.0.0
