# SAHOOL Platform API Documentation | توثيق واجهات برمجة تطبيقات منصة سهول

OpenAPI 3.0.3 specifications for all SAHOOL platform services.

> **Version**: 16.0.0
> **Last Updated**: 2026-02-21

## Overview | نظرة عامة

This directory contains comprehensive OpenAPI/Swagger documentation for all SAHOOL agricultural platform APIs, organized by service category.

## API Specifications | مواصفات واجهات البرمجة

| File | Services | Description | الوصف |
|------|----------|-------------|-------|
| **[core-services.yaml](./core-services.yaml)** | user-service, notification-service, alert-service, audit-service | Authentication, Users, Notifications, Alerts, Audit | المصادقة، المستخدمين، الإشعارات، التنبيهات، التدقيق |
| **[field-services.yaml](./field-services.yaml)** | field-management-service | Field CRUD, Boundaries, NDVI, Geospatial | إدارة الحقول، الحدود، مؤشر الغطاء النباتي |
| **[weather-services.yaml](./weather-services.yaml)** | weather-service, weather-core | Weather Assessment, Forecasts, ET0, GDD, Frost/Heat Risk | تقييم الطقس، التنبؤات، البخر-نتح، مخاطر الصقيع والحرارة |
| **[ai-services.yaml](./ai-services.yaml)** | advisory-service, crop-intelligence-service, ai-advisor, agro-advisor | Disease Detection, Fertilizer Recommendations, Crop Health AI | اكتشاف الأمراض، توصيات الأسمدة، ذكاء صحة المحاصيل |
| **[analysis-services.yaml](./analysis-services.yaml)** | vegetation-analysis-service, indicators-service, field-intelligence, virtual-sensors | NDVI Analysis, Satellite Imagery, LAI Estimation, Virtual Sensors | تحليل الغطاء النباتي، صور الأقمار الصناعية، المستشعرات الافتراضية |
| **[iot-services.yaml](./iot-services.yaml)** | iot-service, iot-gateway, ws-gateway | Device Management, Sensor Data, WebSocket Events | إدارة الأجهزة، بيانات المستشعرات، أحداث WebSocket |
| **[marketplace-services.yaml](./marketplace-services.yaml)** | marketplace-service, community-chat, research-core, disaster-assessment | Products, Orders, Community Posts, Research Trials, Disaster Assessment | المنتجات، الطلبات، منشورات المجتمع، التجارب البحثية، تقييم الكوارث |
| **[billing-services.yaml](./billing-services.yaml)** | billing-core | Plans, Subscriptions, Invoices, Payments, Usage | الخطط، الاشتراكات، الفواتير، المدفوعات، الاستخدام |
| **[task-services.yaml](./task-services.yaml)** | task-service, equipment-service, inventory-service | Tasks, Equipment, Inventory, Maintenance | المهام، المعدات، المخزون، الصيانة |
| **[agent-services.yaml](./agent-services.yaml)** | agent-registry, ai-agents-core, ai-agents-service, knowledge-graph, mcp-server, skills-service | AI Agents, Knowledge Graph, MCP Tools, Skills | وكلاء الذكاء الاصطناعي، رسم المعرفة، أدوات MCP، المهارات |
| **[irrigation-services.yaml](./irrigation-services.yaml)** | irrigation-smart | Smart Irrigation Scheduling, Water Balance, Efficiency Reports | الري الذكي، التوازن المائي، تقارير الكفاءة |
| **[pest-detection-services.yaml](./pest-detection-services.yaml)** | pest-detection-service | Pest Identification, IPM, Scout Reports, Economic Thresholds | كشف الآفات، الإدارة المتكاملة، تقارير الاستكشاف، العتبات الاقتصادية |

## Quick Start | البدء السريع

### Viewing the Documentation | عرض التوثيق

#### Option 1: Swagger UI (Recommended)

```bash
# Install swagger-ui
npm install -g swagger-ui-watcher

# View any specification
swagger-ui-watcher docs/api/openapi/core-services.yaml
swagger-ui-watcher docs/api/openapi/field-services.yaml
swagger-ui-watcher docs/api/openapi/weather-services.yaml
```

Open your browser to `http://localhost:8000`

#### Option 2: Redoc

```bash
# Install redoc-cli
npm install -g redoc-cli

# Generate HTML documentation
redoc-cli bundle docs/api/openapi/core-services.yaml -o core-services.html
redoc-cli bundle docs/api/openapi/ai-services.yaml -o ai-services.html
```

#### Option 3: Online Swagger Editor

1. Go to https://editor.swagger.io/
2. File → Import file → Select the YAML file

### Generating Client SDKs | إنشاء مكتبات العملاء

#### Python Client

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i docs/api/openapi/core-services.yaml \
  -g python \
  -o clients/python/sahool-core-client \
  --additional-properties=packageName=sahool_core

# Generate for all services
for spec in core-services field-services weather-services ai-services analysis-services iot-services marketplace-services billing-services task-services agent-services; do
  openapi-generator-cli generate \
    -i docs/api/openapi/${spec}.yaml \
    -g python \
    -o clients/python/sahool-${spec%-services}-client \
    --additional-properties=packageName=sahool_${spec%-services}
done
```

#### TypeScript/JavaScript Client

```bash
# Generate TypeScript Axios client
openapi-generator-cli generate \
  -i docs/api/openapi/core-services.yaml \
  -g typescript-axios \
  -o clients/typescript/sahool-core-client
```

## Service Architecture | معمارية الخدمات

```
┌─────────────────────────────────────────────────────────────────────┐
│                      API Gateway (Kong :8000)                        │
│                     https://api.sahool.sa/api/v1                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Core Services   │    │  Field Services  │    │ Weather Services │
│    (Node.js)     │    │    (Node.js)     │    │    (Python)      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
│ user-service:3025│    │field-mgmt:3000   │    │weather:8092      │
│ alert:8113       │    │                  │    │weather-core:8108 │
│ notification:8110│    │                  │    │                  │
│ audit:8114       │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   AI Services    │    │ Analysis Services│    │   IoT Services   │
│    (Python)      │    │    (Python)      │    │  (Python/Node)   │
└──────────────────┘    └──────────────────┘    └──────────────────┘
│ advisory:8093    │    │ vegetation:8090  │    │ iot-service:8117 │
│ crop-intel:8095  │    │ indicators:8091  │    │ iot-gateway:8106 │
│ ai-advisor:8112  │    │ field-intel:8120 │    │ ws-gateway:8081  │
│ agro-advisor:8105│    │ virtual-sens:8119│    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Agent Services  │    │ Business Services│    │  Task Services   │
│    (Python)      │    │    (Node.js)     │    │    (Python)      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
│ agent-reg:8160   │    │ marketplace:3010 │    │ task:8103        │
│ ai-agents:8122   │    │ community:8097   │    │ equipment:8101   │
│ knowledge:8140   │    │ research:3015    │    │ inventory:8116   │
│ mcp-server:8200  │    │ disaster:3020    │    │                  │
│ skills:8121      │    │ billing:8089     │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Authentication | المصادقة

All API endpoints require JWT authentication via the `Authorization` header unless otherwise specified.

### Getting a Token | الحصول على رمز

```bash
# Login to get access token
curl -X POST https://api.sahool.sa/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "your-password"
  }'
```

### Using the Token | استخدام الرمز

```bash
# Include token in Authorization header
curl -X GET "https://api.sahool.sa/api/v1/fields" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: your-tenant-id"
```

## Rate Limiting | حدود الطلبات

| Tier | Requests/min | Requests/hour |
|------|--------------|---------------|
| Free | 30 | 500 |
| Standard | 60 | 2000 |
| Premium | 120 | 5000 |
| Internal | 1000 | 50000 |

## Common Headers | الرؤوس الشائعة

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes* | `Bearer <JWT_TOKEN>` |
| `X-Tenant-ID` | Yes | Tenant identifier (UUID) |
| `X-Correlation-Id` | No | Request correlation ID for tracing |
| `Content-Type` | Yes | `application/json` |
| `Accept-Language` | No | `ar` or `en` for response language |

*Public endpoints (login, register, health) don't require Authorization

## Error Responses | استجابات الأخطاء

All APIs use standard HTTP status codes and return errors in this format:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "message_ar": "معاملات الطلب غير صالحة",
  "details": {
    "field": "email",
    "reason": "Must be a valid email address"
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Common Error Codes | رموز الأخطاء الشائعة

| Code | Description | الوصف |
|------|-------------|-------|
| `400` | Bad Request (invalid parameters) | طلب غير صالح |
| `401` | Unauthorized (missing/invalid token) | غير مصرح |
| `403` | Forbidden (insufficient permissions) | ممنوع |
| `404` | Not Found | غير موجود |
| `409` | Conflict (duplicate resource) | تعارض |
| `429` | Too Many Requests (rate limit) | طلبات كثيرة جداً |
| `500` | Internal Server Error | خطأ في الخادم |
| `503` | Service Unavailable | الخدمة غير متاحة |

## WebSocket Events | أحداث WebSocket

Connect to real-time events via WebSocket:

```javascript
const ws = new WebSocket('wss://api.sahool.sa/ws');

// Authenticate
ws.send(JSON.stringify({
  type: 'auth',
  token: 'YOUR_JWT_TOKEN'
}));

// Subscribe to channels
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['field.updates', 'alert.created', 'sensor.reading']
}));

// Handle events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Event: ${data.type}`, data.payload);
};
```

### Available Channels | القنوات المتاحة

| Channel | Description | الوصف |
|---------|-------------|-------|
| `field.updates` | Field data changes | تحديثات بيانات الحقل |
| `alert.created` | New alerts | تنبيهات جديدة |
| `sensor.reading` | Sensor data | قراءات المستشعرات |
| `device.status` | Device status changes | تغييرات حالة الأجهزة |
| `irrigation.event` | Irrigation events | أحداث الري |

## Validation | التحقق

Validate your OpenAPI specs:

```bash
# Install validator
npm install -g @apidevtools/swagger-cli

# Validate all specs
for spec in docs/api/openapi/*.yaml; do
  echo "Validating $spec..."
  swagger-cli validate "$spec"
done
```

## Examples | أمثلة

### Create a Field | إنشاء حقل

```bash
curl -X POST "https://api.sahool.sa/api/v1/fields" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "حقل القمح الشمالي",
    "cropType": "wheat",
    "areaHectares": 5.5,
    "irrigationType": "drip",
    "boundary": {
      "type": "Polygon",
      "coordinates": [[[46.7, 24.6], [46.8, 24.6], [46.8, 24.7], [46.7, 24.7], [46.7, 24.6]]]
    }
  }'
```

### Get Weather Forecast | الحصول على توقعات الطقس

```bash
curl -X POST "https://api.sahool.sa/api/v1/weather/forecast" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "fieldId": "field-123",
    "lat": 24.7136,
    "lon": 46.6753,
    "days": 7
  }'
```

### Get Fertilizer Recommendation | الحصول على توصية الأسمدة

```bash
curl -X POST "https://api.sahool.sa/api/v1/advisory/fertilizer/plan" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "fieldId": "field-123",
    "crop": "wheat",
    "stage": "tillering",
    "fieldSizeHa": 5.5,
    "soilFertility": "medium",
    "irrigationType": "drip"
  }'
```

## Support | الدعم

For API support and questions:

- **Documentation**: https://docs.sahool.sa
- **GitHub Issues**: https://github.com/kafaat/sahool-unified-v15-idp/issues
- **Email**: support@sahool.sa

## License | الترخيص

Proprietary - Copyright (c) 2026 KAFAAT / SAHOOL Platform

---

_Last Updated: 2026-01-24_
