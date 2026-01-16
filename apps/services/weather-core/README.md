# ⚠️ DEPRECATED - Use weather-service instead

This service has been deprecated and merged into `weather-service`.
Please update your references to use `weather-service` on port 8108.

# Weather Core Service

**خدمة الطقس الأساسية - التقييم والتنبيهات الزراعية**

## Overview | نظرة عامة

Agricultural weather assessment, forecasting, and alert service. Provides weather data, risk assessment, and irrigation recommendations based on current and forecasted conditions.

خدمة تقييم الطقس الزراعي والتنبؤ والتنبيهات. توفر بيانات الطقس وتقييم المخاطر وتوصيات الري بناءً على الظروف الحالية والمتوقعة.

## Port

```
8098
```

## Features | الميزات

### Weather Data | بيانات الطقس

- Current conditions
- Hourly forecast (48 hours)
- Daily forecast (7 days)
- Historical data

### Risk Assessment | تقييم المخاطر

- Heat stress detection
- Frost risk
- Disease conditions
- Strong wind alerts

### Irrigation Adjustment | تعديل الري

- ET-based calculations
- Rainfall integration
- Humidity factors

### Alert System | نظام التنبيهات

- Real-time weather alerts
- Severity classification
- Multi-language messages

## API Endpoints

### Health

| Method | Path       | Description  |
| ------ | ---------- | ------------ |
| GET    | `/healthz` | Health check |

### Weather

| Method | Path                  | Description        |
| ------ | --------------------- | ------------------ |
| GET    | `/weather/current`    | Current conditions |
| GET    | `/weather/forecast`   | Weather forecast   |
| GET    | `/weather/historical` | Historical data    |

### Assessment

| Method | Path            | Description             |
| ------ | --------------- | ----------------------- |
| POST   | `/assess`       | Full weather assessment |
| GET    | `/heat-stress`  | Heat stress risk        |
| GET    | `/frost-risk`   | Frost risk              |
| GET    | `/disease-risk` | Disease conditions      |

### Irrigation

| Method | Path                     | Description                      |
| ------ | ------------------------ | -------------------------------- |
| GET    | `/irrigation/adjustment` | Get irrigation adjustment factor |
| POST   | `/irrigation/calculate`  | Calculate ET-based irrigation    |

## Usage Examples | أمثلة الاستخدام

### Get Current Weather

```bash
curl "http://localhost:8098/weather/current?lat=15.35&lon=44.20"
```

### Full Weather Assessment

```bash
curl -X POST http://localhost:8098/assess \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "lat": 15.35,
    "lon": 44.20,
    "crop": "wheat",
    "growth_stage": "vegetative"
  }'
```

### Get Irrigation Adjustment

```bash
curl "http://localhost:8098/irrigation/adjustment?lat=15.35&lon=44.20&crop=wheat"
```

## Weather Providers

| Provider   | Type    | Description      |
| ---------- | ------- | ---------------- |
| Open-Meteo | Primary | Free, no API key |
| Mock       | Testing | Simulated data   |

## Alert Types

| Type           | Arabic      | Severity Levels             |
| -------------- | ----------- | --------------------------- |
| `heat_stress`  | إجهاد حراري | low, medium, high, critical |
| `frost`        | صقيع        | medium, high, critical      |
| `heavy_rain`   | أمطار غزيرة | medium, high, critical      |
| `strong_wind`  | رياح قوية   | medium, high                |
| `disease_risk` | خطر أمراض   | medium, high                |

## Response Format

### Weather Assessment

```json
{
  "field_id": "field_001",
  "timestamp": "2025-12-23T10:00:00Z",
  "current": {
    "temp_c": 32.5,
    "humidity": 45,
    "wind_kph": 15,
    "condition": "sunny"
  },
  "risks": {
    "heat_stress": "medium",
    "frost": "none",
    "disease": "low"
  },
  "alerts": [...],
  "irrigation_factor": 1.15,
  "recommendation": "زيادة الري بنسبة 15%"
}
```

## Irrigation Adjustment Factors

| Condition     | Factor    | Description         |
| ------------- | --------- | ------------------- |
| Normal        | 1.0       | Standard irrigation |
| Hot & Dry     | 1.3 - 1.5 | Increase irrigation |
| Rain Expected | 0.5 - 0.7 | Reduce irrigation   |
| After Rain    | 0.0 - 0.3 | Skip irrigation     |
| High Humidity | 0.8 - 0.9 | Slight reduction    |

## Dependencies

- FastAPI
- httpx (for API calls)
- NATS

## Environment Variables

| Variable              | Description         | Default |
| --------------------- | ------------------- | ------- |
| `PORT`                | Service port        | `8098`  |
| `NATS_URL`            | NATS server URL     | -       |
| `USE_MOCK_WEATHER`    | Use mock provider   | `false` |
| `OPENMETEO_CACHE_TTL` | Cache TTL (seconds) | `300`   |

## Events Published

- `weather.current` - Current weather update
- `weather.alert` - Weather alert triggered
- `weather.forecast` - Forecast updated
- `irrigation.adjustment` - Irrigation recommendation
