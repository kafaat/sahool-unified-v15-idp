# SAHOOL API Comprehensive Guide

# دليل واجهة برمجة التطبيقات الشامل

This guide provides a comprehensive overview of the SAHOOL platform APIs for developers.

يقدم هذا الدليل نظرة شاملة على واجهات برمجة تطبيقات منصة سهول للمطورين.

**Version | الإصدار**: 16.0.0
**Last Updated | آخر تحديث**: February 2026

---

## Table of Contents | جدول المحتويات

1. [Quick Start](#quick-start--البدء-السريع)
2. [Base URLs](#base-urls--عناوين-url-الأساسية)
3. [Authentication](#authentication--المصادقة)
4. [Request & Response Format](#request--response-format--تنسيق-الطلب-والاستجابة)
5. [Error Handling](#error-handling--معالجة-الأخطاء)
6. [Rate Limiting](#rate-limiting--تحديد-المعدل)
7. [Service Categories](#service-categories--فئات-الخدمات)
8. [Common Endpoints](#common-endpoints--نقاط-النهاية-الشائعة)
9. [WebSocket API](#websocket-api--واجهة-websocket)
10. [SDK & Client Libraries](#sdk--client-libraries--مكتبات-العميل)

---

## Quick Start | البدء السريع

### Making Your First API Call

```bash
# 1. Get authentication token
TOKEN=$(curl -s -X POST https://api.sahool.io/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+966500000000", "password": "your_password"}' \
  | jq -r '.access_token')

# 2. Make authenticated request
curl https://api.sahool.io/api/v1/fields \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### JavaScript Example

```javascript
import { SahoolClient } from '@sahool/api-client';

const client = new SahoolClient({
  baseUrl: 'https://api.sahool.io',
  token: 'your_jwt_token'
});

// Get all fields
const fields = await client.fields.list();

// Get weather for a location
const weather = await client.weather.getCurrent({
  latitude: 24.7136,
  longitude: 46.6753
});
```

### Python Example

```python
import httpx

BASE_URL = "https://api.sahool.io/api/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get fields
response = httpx.get(f"{BASE_URL}/fields", headers=headers)
fields = response.json()

# Create a new field
new_field = {
    "name": "North Field",
    "boundary": {
        "type": "Polygon",
        "coordinates": [[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]]
    },
    "crop_type": "wheat"
}
response = httpx.post(f"{BASE_URL}/fields", json=new_field, headers=headers)
```

---

## Base URLs | عناوين URL الأساسية

| Environment | Base URL | Description |
|-------------|----------|-------------|
| **Production** | `https://api.sahool.io` | Live production API |
| **Staging** | `https://staging-api.sahool.io` | Pre-production testing |
| **Development** | `http://localhost:8000` | Local development |

All API endpoints follow the pattern:
```
{base_url}/api/v1/{service}/{endpoint}
```

---

## Authentication | المصادقة

### Obtaining a Token | الحصول على رمز

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "phone": "+966500000000",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Using the Token | استخدام الرمز

Include the token in the `Authorization` header:

```http
GET /api/v1/fields
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Refreshing Tokens | تحديث الرموز

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Token Expiration | انتهاء صلاحية الرمز

| Token Type | Expiration |
|------------|------------|
| Access Token | 24 hours |
| Refresh Token | 30 days |

---

## Request & Response Format | تنسيق الطلب والاستجابة

### Request Headers | رؤوس الطلب

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes* | JWT Bearer token |
| `Content-Type` | Yes | `application/json` |
| `Accept` | No | `application/json` |
| `X-Request-ID` | No | Correlation ID for tracing |
| `X-Tenant-ID` | No** | Tenant identifier |
| `Accept-Language` | No | `ar` or `en` (default: `en`) |

*Not required for health check and public endpoints
**Required for multi-tenant operations

### Success Response | استجابة النجاح

```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2026-02-07T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Paginated Response | استجابة مرقمة

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

### Pagination Parameters | معلمات الترقيم

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max: 100) |
| `sort` | string | - | Sort field (e.g., `created_at`) |
| `order` | string | `desc` | Sort order (`asc` or `desc`) |

---

## Error Handling | معالجة الأخطاء

### Error Response Format | تنسيق استجابة الخطأ

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid field boundary",
    "message_ar": "حدود الحقل غير صالحة",
    "details": [
      {
        "field": "boundary",
        "message": "Coordinates must form a closed polygon"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-02-07T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes | رموز حالة HTTP

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created |
| `204` | No Content | Request successful, no content |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Authentication required |
| `403` | Forbidden | Access denied |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource conflict |
| `422` | Unprocessable Entity | Validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | Service temporarily unavailable |

### Error Codes | رموز الخطأ

| Code | Description |
|------|-------------|
| `AUTH_TOKEN_EXPIRED` | JWT token has expired |
| `AUTH_INVALID_TOKEN` | Invalid JWT token |
| `AUTH_INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `VALIDATION_ERROR` | Request validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RESOURCE_CONFLICT` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |

---

## Rate Limiting | تحديد المعدل

### Rate Limit Tiers | مستويات تحديد المعدل

| Tier | Requests/Minute | Requests/Hour | Use Case |
|------|-----------------|---------------|----------|
| **Free** | 30 | 500 | Trial users |
| **Starter** | 100 | 5,000 | Basic subscription |
| **Professional** | 500 | 25,000 | Professional subscription |
| **Enterprise** | 1,000 | 50,000 | Enterprise subscription |
| **Internal** | 5,000 | 100,000 | Service-to-service |

### Rate Limit Headers | رؤوس تحديد المعدل

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1707300000
X-RateLimit-Retry-After: 60
```

### Handling Rate Limits | التعامل مع حدود المعدل

```javascript
async function makeRequest(url) {
  const response = await fetch(url);

  if (response.status === 429) {
    const retryAfter = response.headers.get('X-RateLimit-Retry-After');
    await sleep(retryAfter * 1000);
    return makeRequest(url); // Retry
  }

  return response.json();
}
```

---

## Service Categories | فئات الخدمات

### 1. Core Services (Starter) | الخدمات الأساسية

Essential field management and operations.

| Service | Port | Base Path | Description |
|---------|------|-----------|-------------|
| Field Management | 3000 | `/api/v1/fields` | Field CRUD, boundaries, zones |
| Weather Service | 8092 | `/api/v1/weather` | Weather data and forecasts |
| Task Service | 8103 | `/api/v1/tasks` | Task management |
| Notification | 8110 | `/api/v1/notifications` | Push notifications |
| Calendar | 8111 | `/api/v1/calendar` | Astronomical calendar |

### 2. Intelligence Services (Professional) | خدمات الذكاء

Advanced analytics and AI-powered insights.

| Service | Port | Base Path | Description |
|---------|------|-----------|-------------|
| Vegetation Analysis | 8090 | `/api/v1/vegetation` | Satellite imagery analysis |
| Crop Intelligence | 8095 | `/api/v1/crop-intelligence` | Crop health AI |
| NDVI Processor | 8118 | `/api/v1/ndvi` | NDVI computation |
| Indicators | 8091 | `/api/v1/indicators` | Field health indicators |
| Vision Service | 8150 | `/api/v1/vision` | AI image analysis |

### 3. Decision Services (Enterprise) | خدمات القرار

Recommendations and optimization.

| Service | Port | Base Path | Description |
|---------|------|-----------|-------------|
| Advisory Service | 8093 | `/api/v1/advisory` | AI recommendations |
| Irrigation Smart | 8094 | `/api/v1/irrigation` | Smart irrigation |
| Yield Engine | 8098 | `/api/v1/yield` | Yield predictions |
| Hydrology | 8165 | `/api/v1/hydrology` | Drainage analysis |
| Leveling Optimizer | 8170 | `/api/v1/leveling` | Field leveling |

### 4. Business Services | خدمات الأعمال

User-facing operations and integrations.

| Service | Port | Base Path | Description |
|---------|------|-----------|-------------|
| Marketplace | 3010 | `/api/v1/marketplace` | Agricultural marketplace |
| Billing | 8089 | `/api/v1/billing` | Billing and subscriptions |
| Community Chat | 8097 | `/api/v1/chat` | Community features |
| Equipment | 8101 | `/api/v1/equipment` | Equipment tracking |
| Inventory | 8116 | `/api/v1/inventory` | Inventory management |

---

## Common Endpoints | نقاط النهاية الشائعة

### Health Check Endpoints | نقاط فحص الصحة

All services expose standardized health endpoints:

```http
GET /healthz        # Liveness probe
GET /readyz         # Readiness probe
GET /health         # Detailed health status
GET /metrics        # Prometheus metrics
```

### Field Management | إدارة الحقول

```http
# List fields
GET /api/v1/fields
GET /api/v1/fields?page=1&page_size=20

# Get single field
GET /api/v1/fields/{field_id}

# Create field
POST /api/v1/fields
{
  "name": "North Field",
  "boundary": {
    "type": "Polygon",
    "coordinates": [[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]]
  },
  "crop_type": "wheat",
  "irrigation_type": "drip"
}

# Update field
PATCH /api/v1/fields/{field_id}
{
  "name": "Updated Field Name"
}

# Delete field
DELETE /api/v1/fields/{field_id}

# Get field NDVI history
GET /api/v1/fields/{field_id}/ndvi/history

# Export as GeoJSON
GET /api/v1/fields/{field_id}/export/geojson
```

### Weather | الطقس

```http
# Get current weather
POST /api/v1/weather/current
{
  "latitude": 24.7136,
  "longitude": 46.6753
}

# Get weather forecast
POST /api/v1/weather/forecast
{
  "latitude": 24.7136,
  "longitude": 46.6753,
  "days": 7
}

# Calculate evapotranspiration
POST /api/v1/weather/evapotranspiration
{
  "latitude": 24.7136,
  "longitude": 46.6753,
  "crop_coefficient": 1.15
}

# Check spray window
POST /api/v1/weather/spray-window
{
  "latitude": 24.7136,
  "longitude": 46.6753,
  "hours_ahead": 24
}
```

### Irrigation | الري

```http
# Get irrigation recommendation
POST /api/v1/irrigation/recommend
{
  "field_id": "field_123",
  "crop_type": "wheat",
  "growth_stage": "tillering"
}

# Calculate water needs
POST /api/v1/irrigation/calculate
{
  "field_id": "field_123",
  "soil_moisture": 35.0,
  "target_moisture": 50.0
}

# Get irrigation schedule
GET /api/v1/irrigation/schedule/{field_id}
```

### Advisory | الاستشارات

```http
# Get crop advisory
POST /api/v1/advisory/crop
{
  "field_id": "field_123",
  "crop_type": "wheat",
  "issue_type": "disease"
}

# Get fertilizer recommendation
POST /api/v1/advisory/fertilizer
{
  "field_id": "field_123",
  "soil_test": {
    "nitrogen": 18,
    "phosphorus": 25,
    "potassium": 150
  },
  "target_yield": 5.0
}

# Get pest management advice
POST /api/v1/advisory/pest
{
  "field_id": "field_123",
  "pest_type": "aphids",
  "severity": "moderate"
}
```

### Vision AI | الرؤية بالذكاء الاصطناعي

```http
# Detect diseases/pests in image
POST /api/v1/vision/detect
Content-Type: multipart/form-data

image: <binary>
detection_type: disease|pest|weed

# Batch detection
POST /api/v1/vision/batch
{
  "images": ["base64_image_1", "base64_image_2"],
  "detection_type": "disease"
}
```

---

## WebSocket API | واجهة WebSocket

### Connection | الاتصال

```javascript
const ws = new WebSocket('wss://api.sahool.io/ws');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### Subscribing to Events | الاشتراك في الأحداث

```javascript
// Subscribe to field updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'field.updates',
  field_id: 'field_123'
}));

// Subscribe to alerts
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'alerts',
  severity: ['critical', 'warning']
}));
```

### Event Types | أنواع الأحداث

| Channel | Event Types | Description |
|---------|-------------|-------------|
| `field.updates` | `field.created`, `field.updated`, `field.deleted` | Field changes |
| `weather.alerts` | `frost.warning`, `heat.warning`, `rain.forecast` | Weather alerts |
| `sensor.data` | `sensor.reading`, `sensor.alert` | IoT sensor data |
| `task.updates` | `task.created`, `task.completed` | Task changes |
| `alerts` | `critical`, `warning`, `info` | System alerts |

---

## SDK & Client Libraries | مكتبات العميل

### JavaScript/TypeScript

```bash
npm install @sahool/api-client
```

```typescript
import { SahoolClient } from '@sahool/api-client';

const client = new SahoolClient({
  baseUrl: 'https://api.sahool.io',
  token: 'your_jwt_token'
});

// Fields
const fields = await client.fields.list();
const field = await client.fields.get('field_123');
const newField = await client.fields.create({ name: 'New Field', ... });

// Weather
const weather = await client.weather.getCurrent({ lat: 24.7, lon: 46.6 });

// Advisory
const advice = await client.advisory.getRecommendation({ field_id: 'field_123' });
```

### Flutter/Dart

```yaml
# pubspec.yaml
dependencies:
  sahool_api: ^16.0.0
```

```dart
import 'package:sahool_api/sahool_api.dart';

final client = SahoolApiClient(
  baseUrl: 'https://api.sahool.io',
  token: 'your_jwt_token',
);

// Get fields
final fields = await client.fields.list();

// Get weather
final weather = await client.weather.getCurrent(
  latitude: 24.7136,
  longitude: 46.6753,
);
```

### Python

```bash
pip install sahool-client
```

```python
from sahool_client import SahoolClient

client = SahoolClient(
    base_url='https://api.sahool.io',
    token='your_jwt_token'
)

# Get fields
fields = client.fields.list()

# Create field
new_field = client.fields.create(
    name='New Field',
    boundary=geojson_polygon,
    crop_type='wheat'
)

# Get weather
weather = client.weather.get_current(
    latitude=24.7136,
    longitude=46.6753
)
```

---

## Additional Resources | موارد إضافية

- [API Endpoints Reference](./API_ENDPOINTS_REFERENCE.md) - Complete endpoint listing
- [API Gateway Documentation](./API_GATEWAY.md) - Kong configuration
- [Rate Limiting Guide](./RATE_LIMITING.md) - Rate limiting policies
- [Authentication Guide](./api/authentication.md) - Detailed auth documentation
<<<<<<< HEAD
- [WebSocket Guide](./api/websocket.md) - Real-time API documentation
=======
- WebSocket Guide - Real-time connections via `ws-gateway` service (port 8081)
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

---

_Last Updated | آخر تحديث: February 2026_
