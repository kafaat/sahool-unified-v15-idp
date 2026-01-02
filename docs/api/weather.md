# Weather APIs
# واجهات برمجة تطبيقات الطقس

## Overview | نظرة عامة

Weather APIs provide comprehensive weather data and forecasts for agricultural decision-making:
- Current weather conditions
- Multi-day forecasts
- Weather alerts and warnings
- Irrigation recommendations based on weather
- Multi-provider support with automatic fallback

توفر واجهات الطقس بيانات وتوقعات شاملة للطقس لاتخاذ القرارات الزراعية:
- ظروف الطقس الحالية
- توقعات متعددة الأيام
- تنبيهات وتحذيرات الطقس
- توصيات الري بناءً على الطقس
- دعم متعدد المزودين مع احتياطي تلقائي

## Base URLs

**Weather Core:** `http://localhost:8108`
**Weather Advanced:** `http://localhost:8109`
**Weather Service:** `http://localhost:8110`

## Weather Providers | مزودو الطقس

The system supports multiple weather data providers with automatic fallback:

1. **Open-Meteo** (Free, no API key required)
2. **OpenWeatherMap** (Requires: `OPENWEATHERMAP_API_KEY`)
3. **WeatherAPI** (Requires: `WEATHERAPI_KEY`)

## Endpoints | نقاط النهاية

### POST /weather/current

Get current weather conditions for a location.

**Request Body:**

```json
{
  "tenant_id": "tenant-123",
  "field_id": "field-456",
  "lat": 15.3694,
  "lon": 44.1910
}
```

**Response:**

```json
{
  "field_id": "field-456",
  "location": {
    "lat": 15.3694,
    "lon": 44.1910
  },
  "provider": "Open-Meteo",
  "current": {
    "temperature_c": 28.5,
    "humidity_pct": 45,
    "wind_speed_kmh": 15.2,
    "wind_direction_deg": 180,
    "wind_direction": "S",
    "precipitation_mm": 0,
    "cloud_cover_pct": 20,
    "pressure_hpa": 1013,
    "uv_index": 7.5,
    "condition": "Partly Cloudy",
    "condition_ar": "غائم جزئياً",
    "timestamp": "2024-01-15T12:30:00Z"
  },
  "alerts": [
    {
      "alert_type": "heat_stress",
      "severity": "medium",
      "title_en": "High Temperature Alert",
      "title_ar": "تنبيه درجة حرارة عالية",
      "window_hours": 6
    }
  ]
}
```

### POST /weather/forecast

Get weather forecast for a location.

**Request Body:**

```json
{
  "tenant_id": "tenant-123",
  "field_id": "field-456",
  "lat": 15.3694,
  "lon": 44.1910
}
```

**Query Parameters:**
- `days` (integer, optional): Number of forecast days (1-16, default: 7)

**Response:**

```json
{
  "field_id": "field-456",
  "location": {
    "lat": 15.3694,
    "lon": 44.1910
  },
  "provider": "Open-Meteo",
  "forecast": [
    {
      "date": "2024-01-16",
      "temp_max_c": 32,
      "temp_min_c": 18,
      "precipitation_mm": 0,
      "precipitation_probability_pct": 10,
      "wind_speed_max_kmh": 20,
      "uv_index_max": 9,
      "condition": "Sunny",
      "condition_ar": "مشمس",
      "sunrise": "06:15",
      "sunset": "18:30"
    }
  ],
  "days": 7
}
```

### POST /weather/irrigation

Get irrigation adjustment recommendations based on weather.

**Request Body:**

```json
{
  "tenant_id": "tenant-123",
  "field_id": "field-456",
  "temp_c": 32,
  "humidity_pct": 40,
  "wind_speed_kmh": 18,
  "precipitation_mm": 0
}
```

**Response:**

```json
{
  "field_id": "field-456",
  "weather_input": {
    "temp_c": 32,
    "humidity_pct": 40,
    "wind_speed_kmh": 18,
    "precipitation_mm": 0
  },
  "adjustment_factor": 1.3,
  "recommendation_en": "Increase irrigation by 30% due to high evapotranspiration",
  "recommendation_ar": "زيادة الري بنسبة 30٪ بسبب التبخر العالي",
  "factors": {
    "temperature": "high",
    "humidity": "low",
    "wind": "moderate",
    "precipitation": "none"
  }
}
```

### GET /weather/heat-stress/{temp_c}

Quick heat stress assessment for a temperature.

**Path Parameters:**
- `temp_c` (number, required): Temperature in Celsius

**Response:**

```json
{
  "temperature_c": 38,
  "alert_type": "heat_stress",
  "severity": "high",
  "at_risk": true
}
```

### GET /weather/providers

Get list of available weather providers.

**Response:**

```json
{
  "multi_provider_enabled": true,
  "providers": [
    {
      "name": "Open-Meteo",
      "configured": true,
      "type": "OpenMeteoProvider",
      "requires_api_key": false
    },
    {
      "name": "OpenWeatherMap",
      "configured": true,
      "type": "OpenWeatherMapProvider",
      "requires_api_key": true
    },
    {
      "name": "WeatherAPI",
      "configured": false,
      "type": "WeatherAPIProvider",
      "requires_api_key": true
    }
  ],
  "total": 3,
  "configured": 2
}
```

## Weather Alerts | تنبيهات الطقس

### Alert Types

| Type | Description |
|------|-------------|
| `heat_stress` | High temperature warning |
| `frost_risk` | Frost warning |
| `high_wind` | Strong wind warning |
| `heavy_rain` | Heavy precipitation warning |
| `low_humidity` | Low humidity alert |

### Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| `none` | No risk | No action needed |
| `low` | Minor risk | Monitor conditions |
| `medium` | Moderate risk | Take preventive measures |
| `high` | High risk | Immediate action required |
| `critical` | Extreme risk | Emergency measures |

## Data Models | نماذج البيانات

### Current Weather

```typescript
interface CurrentWeather {
  temperature_c: number;
  humidity_pct: number;
  wind_speed_kmh: number;
  wind_direction_deg: number;
  wind_direction: string;
  precipitation_mm: number;
  cloud_cover_pct: number;
  pressure_hpa: number;
  uv_index: number;
  condition: string;
  condition_ar: string;
  timestamp: string;
}
```

### Weather Forecast

```typescript
interface DailyForecast {
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  precipitation_mm: number;
  precipitation_probability_pct: number;
  wind_speed_max_kmh: number;
  uv_index_max: number;
  condition: string;
  condition_ar: string;
  sunrise: string;
  sunset: string;
}
```

---

*Last updated: 2026-01-02*
