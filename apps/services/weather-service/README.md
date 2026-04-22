# Weather Service (Unified)

**خدمة الطقس الموحدة - التقييم والتنبيهات الزراعية**

> **Note**: This service consolidates `weather-core` and `weather-advanced` into a single unified service.

## Overview | نظرة عامة

Unified agricultural weather service providing weather data, risk assessment, forecasting, and irrigation recommendations. Includes Yemen-specific location database with all 22 governorates.

خدمة الطقس الزراعية الموحدة. توفر بيانات الطقس وتقييم المخاطر والتنبؤ وتوصيات الري. تتضمن قاعدة بيانات مواقع اليمن مع جميع المحافظات الـ 22.

## Port

```
8092
```

## Features | الميزات

### Weather Data | بيانات الطقس

- Current conditions (الأحوال الحالية)
- Hourly forecast (48 hours) (توقعات كل ساعة)
- Daily forecast (7-14 days) (توقعات يومية)

### Risk Assessment | تقييم المخاطر

- Heat stress detection (كشف الإجهاد الحراري)
- Frost risk (خطر الصقيع)
- Disease conditions (ظروف المرض)
- Strong wind alerts (تنبيهات الرياح القوية)
- Drought monitoring (مراقبة الجفاف)

### Agricultural Intelligence | الذكاء الزراعي

- Growing Degree Days (GDD) calculation
- Evapotranspiration (ET0) estimation
- Spray window recommendations
- Irrigation scheduling

### Yemen Locations | مواقع اليمن

- 22 governorates with coordinates (22 محافظة مع الإحداثيات)
- Elevation data (بيانات الارتفاع)
- Regional classification (highland, coastal, desert, island)

## API Endpoints

### Health

- `GET /healthz` - Health check

### Weather Data

- `POST /weather/current` - Current weather by coordinates
- `POST /weather/forecast` - Weather forecast
- `POST /weather/assess` - Agricultural risk assessment
- `POST /weather/irrigation` - Irrigation recommendations

### Yemen Locations

- `GET /v1/locations` - List all Yemen governorates (optional `?region=` filter: `highland`, `coastal`, `desert`, `island`)
- `GET /v1/current/{location_id}` - Current weather by location
- `GET /v1/forecast/{location_id}` - Forecast by location (optional `?days=N`, max 16)
- `GET /v1/alerts/{location_id}` - Current-condition-driven weather alerts

### Quick Checks

- `GET /weather/heat-stress/{temp_c}` - Quick heat stress check
- `GET /weather/providers` - Available weather providers

## Environment Variables

| Variable                         | Default | Description                                                                                                 |
| -------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `PORT`                           | 8092    | Service port                                                                                                |
| `USE_MOCK_WEATHER`               | false   | Use mock data for testing                                                                                   |
| `USE_MULTI_PROVIDER`             | true    | Enable multi-provider fallback                                                                              |
| `OPENWEATHERMAP_API_KEY`         | -       | OpenWeatherMap API key                                                                                      |
| `WEATHERAPI_KEY`                 | -       | WeatherAPI key                                                                                              |
| `NATS_URL`                       | -       | NATS server URL for events                                                                                  |
| `ENVIRONMENT`                    | development | Deployment environment (`development`, `staging`, `production`). The service refuses to start in `staging`/`production` unless the graph signing secret below is set to a non-default value. |
| `WEATHER_GRAPH_SIGNING_SECRET`   | -       | HMAC secret used to sign `/api/v1/weather/graphs/{id}` URLs. **Required** in staging/production; a default development placeholder is rejected at startup. |

## Weather Providers

1. **Open-Meteo** (Default, Free) - No API key required
2. **OpenWeatherMap** - Set `OPENWEATHERMAP_API_KEY`
3. **WeatherAPI** - Set `WEATHERAPI_KEY`

## Migration from weather-core/weather-advanced

This service replaces both:

- `weather-core` (Port 8098/8108) - Core assessment features (deprecated)
- `weather-advanced` (Port 8092) - Advanced forecasting features (deprecated)

All functionality is now available in this unified service.

## Docker

```bash
docker build -t weather-service .
docker run -p 8092:8092 weather-service
```

## Development

```bash
cd apps/services/weather-service
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8092
```
