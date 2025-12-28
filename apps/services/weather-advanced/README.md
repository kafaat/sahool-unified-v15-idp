# ⚠️ DEPRECATED - Use weather-service instead
This service has been deprecated and merged into `weather-service`.
Please update your references to use `weather-service` on port 8108.

# 🌤️ SAHOOL Weather Advanced Service
# خدمة الطقس المتقدمة

## نظرة عامة | Overview

خدمة الطقس المتقدمة توفر بيانات طقس حقيقية من APIs خارجية مع توقعات 7-14 يوم وتنبيهات زراعية.

The Weather Advanced Service provides real weather data from external APIs with 7-14 day forecasts and agricultural alerts.

**Version:** 15.4.0
**Port:** 8092
**Status:** Production Ready

---

## المميزات | Features

### 1. بيانات طقس حقيقية | Real Weather Data
- تكامل مع Open-Meteo API (مجاني، بدون مفتاح)
- دعم OpenWeatherMap (اختياري)
- تخزين مؤقت ذكي (30 دقيقة)
- fallback تلقائي للمحاكاة

### 2. تغطية اليمن الكاملة | Full Yemen Coverage
- جميع المحافظات الـ 22
- بيانات الارتفاع والمنطقة
- تعديلات موسمية دقيقة

### 3. التنبؤات | Forecasts
- توقعات ساعية (48 ساعة)
- توقعات يومية (حتى 14 يوم)
- دقة عالية للزراعة

### 4. التنبيهات الزراعية | Agricultural Alerts
- موجات الحر
- الأمطار الغزيرة
- الرطوبة العالية
- الرياح القوية

### 5. أدوات زراعية | Agricultural Tools
- حساب Evapotranspiration (ET0)
- Growing Degree Days (GDD)
- نوافذ الرش المثالية
- توصيات الري

---

## API Endpoints

### Health Check
```http
GET /healthz
Response: {
  "status": "ok",
  "service": "weather-advanced",
  "version": "15.4.0",
  "api_provider": "open-meteo",
  "cache_ttl_minutes": 30
}
```

### Locations | المواقع
```http
GET /v1/locations
```

### Current Weather | الطقس الحالي
```http
GET /v1/current/{location_id}

Response: {
  "location_id": "sanaa",
  "location_name_ar": "صنعاء",
  "temperature_c": 22.5,
  "humidity_percent": 45,
  "condition": "clear",
  "condition_ar": "صافي"
}
```

### Forecast | التوقعات
```http
GET /v1/forecast/{location_id}?days=7

Response: {
  "current": {...},
  "hourly_forecast": [...],
  "daily_forecast": [...],
  "alerts": [...],
  "growing_degree_days": 85.5,
  "evapotranspiration_mm": 4.2,
  "spray_window_hours": [...],
  "irrigation_recommendation_ar": "..."
}
```

### Alerts | التنبيهات
```http
GET /v1/alerts/{location_id}
```

### Agricultural Calendar | التقويم الزراعي
```http
GET /v1/agricultural-calendar/{location_id}?crop=tomato
```

---

## المواقع المدعومة | Supported Locations

| المحافظة | ID | الارتفاع | المنطقة |
|---------|-------|---------|--------|
| صنعاء | sanaa | 2250م | مرتفعات |
| عدن | aden | 6م | ساحلية |
| تعز | taiz | 1400م | مرتفعات |
| الحديدة | hodeidah | 12م | ساحلية |
| إب | ibb | 2050م | مرتفعات |
| حضرموت | hadramaut | 650م | صحراء |
| مأرب | marib | 1100م | صحراء |
| ... | ... | ... | ... |

---

## الاستخدام | Usage

### Python Client
```python
from shared.integration import get_service_client, ServiceName

weather = get_service_client(ServiceName.WEATHER)

# الطقس الحالي
current = await weather.get("/v1/current/sanaa")
print(f"درجة الحرارة: {current.data['temperature_c']}°C")

# التوقعات
forecast = await weather.get("/v1/forecast/sanaa", params={"days": 7})
for day in forecast.data["daily_forecast"]:
    print(f"{day['date']}: {day['temp_max_c']}°C / {day['temp_min_c']}°C")
```

### cURL Examples
```bash
# الطقس الحالي
curl http://localhost:8092/v1/current/sanaa

# التوقعات
curl "http://localhost:8092/v1/forecast/sanaa?days=7"

# التنبيهات
curl http://localhost:8092/v1/alerts/sanaa
```

---

## متغيرات البيئة | Environment Variables

```env
# Weather API Provider
WEATHER_API_PROVIDER=open-meteo  # أو openweathermap

# OpenWeatherMap (اختياري)
OPENWEATHERMAP_API_KEY=your_api_key

# Cache
WEATHER_CACHE_TTL_MINUTES=30

# Service
SERVICE_PORT=8092
LOG_LEVEL=INFO
```

---

## مقدمو الطقس | Weather Providers

### Open-Meteo (الافتراضي)
- مجاني بدون حدود
- 16 يوم توقعات
- لا يحتاج مفتاح API
- https://open-meteo.com

### OpenWeatherMap
- يحتاج مفتاح API
- 5 أيام توقعات (مجاني)
- https://openweathermap.org

---

## Changelog

### v15.4.0 (December 2025)
- تكامل Open-Meteo API الحقيقي
- دعم OpenWeatherMap
- نظام تخزين مؤقت ذكي
- fallback تلقائي للمحاكاة
- تحسين دقة التوقعات

### v15.3.0
- المحاكاة فقط
