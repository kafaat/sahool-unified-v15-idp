# SAHOOL Platform - API Reference
# مرجع واجهات برمجة التطبيقات

**Version:** 15.3.3
**Last Updated:** December 2024

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Services](#services)
   - [Weather Core](#weather-core-service)
   - [NDVI Engine](#ndvi-engine-service)
   - [Agro Advisor](#agro-advisor-service)
   - [IoT Gateway](#iot-gateway-service)
   - [Field Core](#field-core-service)
   - [Field Chat](#field-chat-service)
   - [Expert Support System](#expert-support-system)
   - [Crop Health](#crop-health-service)
   - [Vector Service](#vector-service-rag)
   - [WebSocket Gateway](#websocket-gateway)
4. [Common Response Formats](#common-response-formats)
5. [Error Codes](#error-codes)

---

## Overview

SAHOOL provides a microservices architecture for agricultural management with a focus on:
- Smart irrigation and weather monitoring
- Crop health analysis via satellite imagery
- AI-powered agricultural recommendations
- Real-time IoT sensor data
- Multi-tenant support for Yemen's governorates

### Base URLs

| Environment | URL |
|-------------|-----|
| Production | `https://api.sahool.io` |
| Staging | `https://staging-api.sahool.io` |
| Development | `http://localhost:PORT` |

---

## Authentication

All API endpoints require JWT authentication unless otherwise noted.

### Headers

```http
Authorization: Bearer <jwt_token>
X-Tenant-Id: <tenant_uuid>
Content-Type: application/json
Accept-Language: ar-YE  # or en-US
```

---

## Services

---

## Weather Core Service

**Port:** 8082
**Base Path:** `/weather`

Provides weather data, forecasts, and agricultural calculations.

### Endpoints

#### GET /weather/current/{governorate}

Get current weather for a Yemen governorate.

**Parameters:**
- `governorate` (path): Yemen governorate name (e.g., "sana'a", "aden", "taiz")

**Response:**
```json
{
  "governorate": "sana'a",
  "temperature_c": 28.5,
  "humidity_percent": 45,
  "wind_speed_kmh": 12.3,
  "conditions": "partly_cloudy",
  "conditions_ar": "غائم جزئياً",
  "timestamp": "2024-12-18T10:00:00Z"
}
```

#### GET /weather/forecast/{governorate}

Get 7-day forecast for a governorate.

**Query Parameters:**
- `days` (optional): Number of days (1-14, default: 7)

**Response:**
```json
{
  "governorate": "sana'a",
  "forecast": [
    {
      "date": "2024-12-18",
      "temp_max_c": 32,
      "temp_min_c": 18,
      "humidity_avg": 40,
      "precipitation_mm": 0,
      "conditions": "sunny"
    }
  ]
}
```

#### POST /weather/gdd

Calculate Growing Degree Days for crop development tracking.

**Request:**
```json
{
  "temp_max_c": 32.5,
  "temp_min_c": 18.2,
  "crop": "tomato",
  "accumulated_gdd": 450.0
}
```

**Response:**
```json
{
  "daily_gdd": 15.35,
  "accumulated_gdd": 465.35,
  "crop": "tomato",
  "growth_stage": "flowering",
  "growth_stage_ar": "مرحلة الإزهار",
  "percent_to_maturity": 62.5,
  "base_temp_c": 10.0,
  "days_to_maturity_estimate": 28
}
```

#### POST /weather/et0

Calculate reference evapotranspiration (Penman-Monteith).

**Request:**
```json
{
  "temp_c": 28.5,
  "humidity_pct": 45,
  "wind_speed_kmh": 12.0,
  "solar_radiation_mj": 22.5,
  "elevation_m": 2200
}
```

**Response:**
```json
{
  "et0_mm_day": 5.8,
  "irrigation_recommendation_mm": 5.8,
  "irrigation_recommendation_ar": "ري 5.8 مم/يوم",
  "crop_water_needs": {
    "tomato": 6.96,
    "wheat": 5.22
  }
}
```

#### POST /weather/spray-windows

Find optimal spray windows based on weather conditions.

**Request:**
```json
{
  "hourly_forecasts": [
    {
      "hour": 6,
      "temp_c": 22,
      "humidity_pct": 65,
      "wind_speed_kmh": 5,
      "precipitation_mm": 0
    }
  ],
  "min_window_hours": 3
}
```

**Response:**
```json
{
  "windows": [
    {
      "start_hour": 6,
      "end_hour": 10,
      "duration_hours": 4,
      "quality": "excellent",
      "quality_ar": "ممتاز",
      "avg_conditions": {
        "temp_c": 24,
        "humidity_pct": 55,
        "wind_speed_kmh": 6
      }
    }
  ],
  "recommendation_ar": "أفضل وقت للرش: 6:00 - 10:00"
}
```

#### GET /weather/crop-calendar/{crop}

Get planting calendar for a specific crop.

**Response:**
```json
{
  "crop": "tomato",
  "crop_ar": "طماطم",
  "current_month": 12,
  "current_activity": "Harvesting season",
  "current_activity_ar": "موسم الحصاد",
  "calendar": {
    "1": {"activity": "Seedling preparation", "activity_ar": "إعداد الشتلات"},
    "2": {"activity": "Transplanting", "activity_ar": "الشتل"}
  },
  "gdd_to_maturity": 1200,
  "base_temp_c": 10
}
```

#### GET /weather/crops

List all supported crops with their agricultural parameters.

---

## NDVI Engine Service

**Port:** 8083
**Base Path:** `/ndvi`

Satellite imagery analysis for vegetation health monitoring.

### Endpoints

#### POST /ndvi/analyze

Analyze field vegetation using satellite imagery.

**Request:**
```json
{
  "field_id": "field-123",
  "satellite": "sentinel-2",
  "cloud_cover_max": 20.0
}
```

**Response:**
```json
{
  "field_id": "field-123",
  "satellite": "sentinel-2",
  "acquisition_date": "2024-12-15",
  "indices": {
    "ndvi": 0.72,
    "ndvi_interpretation": "Healthy vegetation",
    "ndvi_interpretation_ar": "غطاء نباتي صحي",
    "evi": 0.65,
    "savi": 0.68,
    "gndvi": 0.58,
    "grvi": 0.45,
    "lai": 3.2
  },
  "health_status": "good",
  "health_status_ar": "جيد",
  "recommendations": [
    "Vegetation is healthy, continue current irrigation schedule",
    "الغطاء النباتي صحي، استمر في جدول الري الحالي"
  ],
  "zones": [
    {
      "zone_id": "zone-1",
      "area_hectares": 2.5,
      "avg_ndvi": 0.75,
      "status": "excellent"
    }
  ]
}
```

#### GET /ndvi/satellites

List available satellite sources.

**Response:**
```json
{
  "satellites": [
    {
      "id": "sentinel-2",
      "name": "Sentinel-2 (ESA)",
      "resolution_m": 10,
      "revisit_days": 5,
      "bands": ["B02", "B03", "B04", "B08"]
    },
    {
      "id": "landsat-8",
      "name": "Landsat-8 (USGS)",
      "resolution_m": 30,
      "revisit_days": 16
    }
  ]
}
```

#### GET /ndvi/history/{field_id}

Get historical NDVI trends for a field.

**Query Parameters:**
- `start_date`: ISO date (YYYY-MM-DD)
- `end_date`: ISO date (YYYY-MM-DD)
- `satellite` (optional): Filter by satellite source

---

## Agro Advisor Service

**Port:** 8084
**Base Path:** `/advisor`

AI-powered agricultural recommendations and soil analysis.

### Endpoints

#### POST /advisor/recommend

Get crop recommendations based on conditions.

**Request:**
```json
{
  "governorate": "sana'a",
  "field_id": "field-123",
  "soil_type": "clay_loam",
  "water_availability": "moderate",
  "season": "winter"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "crop": "wheat",
      "crop_ar": "قمح",
      "suitability_score": 92,
      "reasons": ["Ideal temperature", "Low water requirement"],
      "reasons_ar": ["درجة حرارة مثالية", "احتياج مائي منخفض"],
      "planting_window": "October - December",
      "expected_yield_kg_ha": 3500
    }
  ]
}
```

#### POST /soil/analyze

Analyze soil sample and get recommendations.

**Request:**
```json
{
  "field_id": "field-123",
  "ph": 6.8,
  "nitrogen_ppm": 35,
  "phosphorus_ppm": 22,
  "potassium_ppm": 180,
  "organic_matter_pct": 2.5,
  "ec_ds_m": 1.2,
  "texture": "clay_loam"
}
```

**Response:**
```json
{
  "field_id": "field-123",
  "overall_rating": "good",
  "overall_rating_ar": "جيد",
  "ph_interpretation": {
    "status": "optimal",
    "status_ar": "مثالي",
    "recommendation_ar": "درجة الحموضة مثالية لمعظم المحاصيل"
  },
  "nutrients": {
    "nitrogen": {
      "level": "medium",
      "level_ar": "متوسط",
      "deficiency_risk": false,
      "recommendation_ar": "أضف 50 كجم/هكتار يوريا"
    },
    "phosphorus": {
      "level": "low",
      "level_ar": "منخفض",
      "deficiency_risk": true,
      "recommendation_ar": "أضف 30 كجم/هكتار سوبر فوسفات"
    }
  },
  "fertilizer_plan": {
    "urea_kg_ha": 50,
    "superphosphate_kg_ha": 30,
    "potash_kg_ha": 0,
    "timing": "Apply before planting",
    "timing_ar": "ضع قبل الزراعة"
  }
}
```

#### POST /soil/fertilizer-adjustment

Calculate fertilizer needs based on crop and target yield.

**Request:**
```json
{
  "soil_analysis": {
    "nitrogen_ppm": 35,
    "phosphorus_ppm": 22,
    "potassium_ppm": 180
  },
  "crop": "tomato",
  "target_yield_kg_ha": 50000
}
```

#### GET /soil/deficiency-symptoms/{crop}

Get visual symptoms of nutrient deficiencies for a crop.

#### GET /soil/optimal-ranges

Get optimal soil parameter ranges for all nutrients.

---

## IoT Gateway Service

**Port:** 8085
**Base Path:** `/iot`

Real-time sensor data and actuator control.

### Endpoints

#### GET /iot/field/{field_id}/sensors

Get all sensor readings for a field.

**Response:**
```json
{
  "field_id": "field-123",
  "sensors": [
    {
      "sensor_id": "soil-moisture-1",
      "type": "soil_moisture",
      "value": 42.5,
      "unit": "%",
      "status": "online",
      "last_reading": "2024-12-18T10:30:00Z"
    },
    {
      "sensor_id": "temp-1",
      "type": "temperature",
      "value": 28.3,
      "unit": "°C",
      "status": "online"
    }
  ]
}
```

#### POST /iot/field/{field_id}/pump

Control irrigation pump.

**Request:**
```json
{
  "action": "on",
  "duration_minutes": 30,
  "zone_id": "zone-1"
}
```

**Response:**
```json
{
  "success": true,
  "pump_id": "pump-1",
  "status": "running",
  "scheduled_off": "2024-12-18T11:00:00Z"
}
```

#### POST /iot/field/{field_id}/valve/{valve_id}

Control individual valve.

#### GET /iot/field/{field_id}/actuators

Get status of all actuators (pumps, valves).

#### POST /iot/field/{field_id}/irrigation/schedule

Set automated irrigation schedule.

**Request:**
```json
{
  "schedules": [
    {
      "zone_id": "zone-1",
      "start_time": "06:00",
      "duration_minutes": 45,
      "days": ["sun", "tue", "thu"],
      "enabled": true
    }
  ]
}
```

---

## Field Core Service

**Port:** 8086
**Base Path:** `/fields`

Field management and data CRUD operations.

### Endpoints

#### GET /fields

List all fields for tenant.

**Query Parameters:**
- `governorate` (optional): Filter by governorate
- `crop` (optional): Filter by current crop
- `status` (optional): Filter by status (active, fallow, harvested)

#### POST /fields

Create a new field.

**Request:**
```json
{
  "name": "حقل الطماطم",
  "name_en": "Tomato Field",
  "governorate": "sana'a",
  "area_hectares": 5.2,
  "crop": "tomato",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[44.2, 15.3], [44.3, 15.3], [44.3, 15.4], [44.2, 15.4], [44.2, 15.3]]]
  }
}
```

#### GET /fields/{field_id}

Get field details.

#### PUT /fields/{field_id}

Update field information.

#### DELETE /fields/{field_id}

Delete a field.

---

## Field Chat Service

**Port:** 8087
**Base Path:** `/chat`

Real-time chat for field collaboration with expert support system.

### REST Endpoints

#### GET /chat/threads

List chat threads for a field or user.

#### POST /chat/threads

Create a new chat thread.

#### GET /chat/threads/{thread_id}/messages

Get messages in a thread.

#### POST /chat/threads/{thread_id}/messages

Send a message to a thread.

### WebSocket

Connect to `/ws/chat/{thread_id}?user_id=xxx&user_name=xxx&user_type=farmer` for real-time updates.

**Message Types:**

```json
// Typing indicator
{"type": "typing_start"}
{"type": "typing_stop"}

// Send message
{"type": "message", "text": "Hello", "attachments": []}

// Keep-alive
{"type": "ping"}
```

**Server Events:**

```json
// User joined/left
{"type": "user_joined", "user_id": "...", "user_name": "...", "user_type": "farmer"}
{"type": "user_left", "user_id": "...", "user_name": "..."}

// Typing indicator
{"type": "typing", "user_id": "...", "is_typing": true, "typing_users": ["user1", "user2"]}

// New message
{"type": "message", "user_id": "...", "text": "...", "timestamp": "..."}
```

---

## Expert Support System

**Port:** 8087 (same as Field Chat)
**Base Path:** `/experts`

نظام دعم الخبراء - Real-time expert consultation for farmers.

### Expert Profile Endpoints

#### POST /experts/profiles

Create expert profile.

**Request:**
```json
{
  "tenant_id": "tenant-123",
  "user_id": "expert-456",
  "name": "Dr. Ahmed",
  "name_ar": "د. أحمد",
  "specialties": ["crop_diseases", "pest_control"],
  "bio": "10 years experience in plant pathology",
  "governorates": ["sana'a", "taiz"]
}
```

**Response:**
```json
{
  "expert_id": "uuid",
  "user_id": "expert-456",
  "name": "Dr. Ahmed",
  "specialties": ["crop_diseases", "pest_control"],
  "specialties_ar": ["أمراض المحاصيل", "مكافحة الآفات"],
  "is_available": true,
  "is_verified": false,
  "total_consultations": 0,
  "avg_rating": 5.0
}
```

#### GET /experts/profiles

List experts with filters.

**Query Parameters:**
- `tenant_id` (required)
- `specialty` (optional): Filter by specialty
- `governorate` (optional): Filter by governorate
- `available_only` (optional): Only show available experts

### Support Request Endpoints

#### POST /experts/requests

Farmer creates support request.

**Request:**
```json
{
  "tenant_id": "tenant-123",
  "farmer_id": "farmer-789",
  "farmer_name": "محمد",
  "governorate": "sana'a",
  "topic": "مشكلة في أوراق الطماطم",
  "specialty_needed": "crop_diseases",
  "field_id": "field-123",
  "diagnosis_id": "diag-456",
  "priority": "high"
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "farmer_name": "محمد",
  "topic": "مشكلة في أوراق الطماطم",
  "status": "pending",
  "status_ar": "في انتظار خبير",
  "priority": "high"
}
```

#### GET /experts/requests/pending

List pending requests for experts.

#### POST /experts/requests/{request_id}/accept

Expert accepts a support request.

**Request:**
```json
{
  "tenant_id": "tenant-123",
  "expert_id": "expert-456",
  "expert_name": "د. أحمد"
}
```

Creates a chat thread and links it to the request.

#### POST /experts/requests/{request_id}/resolve

Expert resolves the request.

**Request:**
```json
{
  "tenant_id": "tenant-123",
  "expert_id": "expert-456",
  "resolution_notes": "Applied fungicide treatment",
  "resolution_notes_ar": "تم تطبيق العلاج بالمبيد الفطري"
}
```

#### POST /experts/requests/{request_id}/rate

Farmer rates the expert.

**Request:**
```json
{
  "tenant_id": "tenant-123",
  "farmer_id": "farmer-789",
  "rating": 5,
  "feedback": "ممتاز، شكراً"
}
```

### Online Experts

#### GET /experts/online

Get count of online experts.

**Response:**
```json
{
  "count": 12,
  "available_count": 8,
  "by_specialty": {
    "crop_diseases": 5,
    "irrigation": 3,
    "general": 4
  }
}
```

#### GET /experts/stats

Get expert system statistics.

**Response:**
```json
{
  "experts": {
    "total": 45,
    "verified": 32,
    "available": 28,
    "online": 12
  },
  "requests": {
    "total": 1250,
    "pending": 8,
    "resolved": 1180,
    "resolution_rate": 94.4
  }
}
```

### Expert Specialties

| Code | English | Arabic |
|------|---------|--------|
| `crop_diseases` | Crop Diseases | أمراض المحاصيل |
| `irrigation` | Irrigation | الري |
| `soil` | Soil | التربة |
| `pest_control` | Pest Control | مكافحة الآفات |
| `fertilization` | Fertilization | التسميد |
| `general` | General | استشارة عامة |

---

## Crop Health Service

**Port:** 8088
**Base Path:** `/health`

Disease detection and pest management.

### Endpoints

#### POST /health/diagnose

Upload image for disease diagnosis.

**Request:** `multipart/form-data`
- `image`: Image file (JPG, PNG)
- `field_id`: Field identifier
- `crop`: Crop type

**Response:**
```json
{
  "diagnosis_id": "diag-123",
  "confidence": 0.92,
  "disease": "early_blight",
  "disease_ar": "اللفحة المبكرة",
  "severity": "moderate",
  "treatment": {
    "chemical": "Apply fungicide containing chlorothalonil",
    "chemical_ar": "رش مبيد فطري يحتوي على كلوروثالونيل",
    "organic": "Remove affected leaves, improve air circulation",
    "organic_ar": "إزالة الأوراق المصابة وتحسين التهوية"
  },
  "prevention": [
    "Rotate crops annually",
    "تدوير المحاصيل سنوياً"
  ]
}
```

#### GET /health/alerts/{field_id}

Get active health alerts for a field.

---

## Vector Service (RAG)

**Port:** 8089
**Base Path:** `/vector`

Knowledge retrieval and RAG functionality.

### Endpoints

#### POST /vector/search

Search agricultural knowledge base.

**Request:**
```json
{
  "query": "كيفية علاج اللفحة المتأخرة في الطماطم",
  "top_k": 5,
  "filters": {
    "crop": "tomato",
    "category": "diseases"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "doc-123",
      "content": "اللفحة المتأخرة (Phytophthora infestans)...",
      "score": 0.92,
      "metadata": {
        "source": "yemen_agri_manual",
        "crop": "tomato",
        "category": "diseases"
      }
    }
  ]
}
```

#### POST /vector/add

Add document to knowledge base.

#### DELETE /vector/delete/{doc_id}

Remove document from knowledge base.

---

## WebSocket Gateway

**Port:** 8090
**Base Path:** `/ws`

Central WebSocket hub for real-time events.

### Connection

```javascript
const ws = new WebSocket('wss://api.sahool.io/ws?tenant_id=xxx&token=yyy');
```

### Message Types

#### Subscribe to Topics

```json
{
  "type": "subscribe",
  "topics": ["field.123.sensors", "alerts.*"]
}
```

#### Receive Events

```json
{
  "type": "event",
  "topic": "field.123.sensors",
  "data": {
    "sensor_id": "soil-1",
    "value": 42.5,
    "timestamp": "2024-12-18T10:30:00Z"
  }
}
```

---

## Common Response Formats

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2024-12-18T10:00:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid field_id format",
    "message_ar": "تنسيق معرف الحقل غير صالح",
    "details": { ... }
  },
  "timestamp": "2024-12-18T10:00:00Z"
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Read operations | 1000/minute |
| Write operations | 100/minute |
| File uploads | 10/minute |
| WebSocket connections | 50/tenant |

---

## SDK Support

Official SDKs available for:
- Python: `pip install sahool-sdk`
- JavaScript/TypeScript: `npm install @sahool/sdk`
- Dart/Flutter: `sahool_sdk` package

---

## Support

- Documentation: https://docs.sahool.io
- API Status: https://status.sahool.io
- Support: support@sahool.io
