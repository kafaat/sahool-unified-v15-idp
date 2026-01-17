# Provider Configuration Service - خدمة إدارة المزودين

## نظرة عامة | Overview

خدمة إدارة وتكوين المزودين الخارجيين للخرائط والطقس والأقمار الصناعية.

External provider management service for Maps, Weather, and Satellite imagery.

**Port:** 8104
**Version:** 16.0.0

---

## الميزات | Features

### أنواع المزودين | Provider Types

| النوع        | Type      | المزودون                               |
| ------------ | --------- | -------------------------------------- |
| خرائط        | Maps      | OSM, Google, Mapbox, ESRI              |
| طقس          | Weather   | Open-Meteo, OpenWeatherMap, WeatherAPI |
| أقمار صناعية | Satellite | Sentinel Hub, Planet Labs, Landsat     |

### إدارة التكوين | Configuration Management

- تكوين لكل مستأجر (Tenant-based config)
- أولويات المزودين (Primary, Secondary, Tertiary)
- فحص صحة المزودين (Health checks)
- توصيات حسب الميزانية

---

## مزودو الخرائط | Map Providers

| المزود           | Provider | API Key | التكلفة/1000 | Offline |
| ---------------- | -------- | ------- | ------------ | ------- |
| OpenStreetMap    | ❌       | مجاني   | ✅           |
| Google Maps      | ✅       | $7.00   | ❌           |
| Google Satellite | ✅       | $7.00   | ❌           |
| Mapbox Streets   | ✅       | $0.50   | ✅           |
| Mapbox Satellite | ✅       | $0.50   | ✅           |
| ESRI Satellite   | ❌       | مجاني   | ✅           |
| OpenTopoMap      | ❌       | مجاني   | ✅           |

## مزودو الطقس | Weather Providers

| المزود          | Provider | API Key | التوقعات | التاريخي |
| --------------- | -------- | ------- | -------- | -------- |
| Open-Meteo      | ❌       | 16 يوم  | ✅       |
| OpenWeatherMap  | ✅       | 8 أيام  | ❌       |
| WeatherAPI      | ✅       | 14 يوم  | ✅       |
| Visual Crossing | ✅       | 15 يوم  | ✅       |

## مزودو الأقمار الصناعية | Satellite Providers

| المزود       | Provider | الدقة  | التكرار               | المؤشرات |
| ------------ | -------- | ------ | --------------------- | -------- |
| Sentinel Hub | 10m      | 5 أيام | NDVI, NDWI, EVI, LAI  |
| Planet Labs  | 3m       | يومي   | NDVI, NDWI, EVI       |
| Landsat      | 30m      | 16 يوم | NDVI, NDWI, EVI, SAVI |
| Maxar        | 30cm     | 3 أيام | NDVI                  |

---

## API Endpoints

### قائمة المزودين | Provider Listing

```http
# جميع المزودين
GET /providers

# مزودو الخرائط
GET /providers/maps

# مزودو الطقس
GET /providers/weather

# مزودو الأقمار الصناعية
GET /providers/satellite
```

### فحص الصحة | Health Checks

```http
# فحص مزود محدد
POST /providers/check
{
    "provider_type": "map",
    "provider_name": "openstreetmap",
    "api_key": "optional_key"
}

Response:
{
    "provider_name": "openstreetmap",
    "status": "available",
    "last_check": "2024-02-15T10:30:00Z",
    "response_time_ms": 145.5
}

# فحص جميع المزودين المجانيين
GET /providers/check/all
```

### تكوين المستأجر | Tenant Configuration

```http
# جلب التكوين
GET /config/{tenant_id}

Response:
{
    "tenant_id": "tenant_001",
    "map_providers": [
        {"provider_name": "openstreetmap", "priority": "primary", "enabled": true},
        {"provider_name": "esri_satellite", "priority": "secondary", "enabled": true}
    ],
    "weather_providers": [
        {"provider_name": "open_meteo", "priority": "primary", "enabled": true}
    ],
    "satellite_providers": []
}

# تحديث التكوين
POST /config/{tenant_id}
{
    "tenant_id": "tenant_001",
    "map_providers": [
        {"provider_name": "mapbox_streets", "api_key": "pk.xxx", "priority": "primary"}
    ]
}

# إعادة التعيين للافتراضي
DELETE /config/{tenant_id}
```

### التوصيات | Recommendations

```http
GET /providers/recommend?use_case=agricultural&budget=free&offline_required=true

Response:
{
    "use_case": "agricultural",
    "budget": "free",
    "map": [
        {"provider": "openstreetmap", "reason_ar": "مجاني، يدعم الاستخدام غير المتصل"}
    ],
    "weather": [
        {"provider": "open_meteo", "reason_ar": "مجاني، 16 يوم توقعات"}
    ]
}

# الميزانيات المدعومة: free, low, medium, high
```

---

## حالات المزود | Provider Status

| الحالة         | Status    | الوصف           |
| -------------- | --------- | --------------- |
| `available`    | متاح      | يعمل بشكل طبيعي |
| `unavailable`  | غير متاح  | لا يستجيب       |
| `rate_limited` | محدود     | تجاوز الحد      |
| `error`        | خطأ       | مشكلة تقنية     |
| `checking`     | قيد الفحص | جاري التحقق     |

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8104

# CORS
CORS_ORIGINS=https://sahool.io,https://admin.sahool.io

# API Keys (اختياري - للفحص)
GOOGLE_MAPS_API_KEY=...
MAPBOX_ACCESS_TOKEN=...
OPENWEATHERMAP_API_KEY=...
SENTINEL_HUB_CLIENT_ID=...
SENTINEL_HUB_CLIENT_SECRET=...
```

---

## Health Check

```http
GET /health
Response: {"status": "healthy", "timestamp": "2024-02-15T10:30:00Z"}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
