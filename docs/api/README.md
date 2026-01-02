# SAHOOL API Documentation
# توثيق واجهة برمجة تطبيقات سحول

**Version:** 15.3.0
**Last Updated:** 2026-01-02

## Overview | نظرة عامة

SAHOOL is an Agricultural Intelligence Platform that provides comprehensive APIs for:
- Field management and crop monitoring
- Weather forecasting and alerts
- Satellite imagery and NDVI analysis
- AI-powered agricultural advisory
- IoT sensor integration
- Market intelligence

منصة سحول هي منصة ذكاء زراعي توفر واجهات برمجية شاملة لـ:
- إدارة الحقول ومراقبة المحاصيل
- التنبؤ بالطقس والتنبيهات
- صور الأقمار الصناعية وتحليل NDVI
- الاستشارات الزراعية بالذكاء الاصطناعي
- تكامل أجهزة استشعار إنترنت الأشياء
- معلومات السوق

## Quick Start | البدء السريع

### Authentication | المصادقة

All API requests require authentication using JWT tokens:

```bash
# Login to get access token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -X GET http://localhost:8090/v1/crops/list \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Base URLs | عناوين URL الأساسية

| Service | Port | Base URL |
|---------|------|----------|
| SAHOOL Field Service | 3000 | http://localhost:3000 |
| SAHOOL Agent Registry Service | 8000 | http://localhost:8000 |
| AI Advisor Service | 8000 | http://localhost:8000 |
| SAHOOL Field Chat | 8000 | http://localhost:8000 |
| Sahool Virtual Sensors Engine | 8000 | http://localhost:8000 |
| SAHOOL Field Operations | 8080 | http://localhost:8080 |
| SAHOOL WebSocket Gateway | 8081 | http://localhost:8081 |
| SAHOOL Billing Core | خدمة الفوترة | 8089 | http://localhost:8089 |
| SAHOOL Field Core | 8090 | http://localhost:8090 |
| SAHOOL Field Core | 8090 | http://localhost:8090 |
| SAHOOL Satellite Service | خدمة الأقمار الصناعية | 8090 | http://localhost:8090 |
| SAHOOL Satellite Service | خدمة الأقمار الصناعية | 8090 | http://localhost:8090 |
| SAHOOL Agricultural Indicators | خدمة المؤشرات الزراعية | 8091 | http://localhost:8091 |
| SAHOOL Advanced Weather Service | خدمة الطقس المتقدمة | 8092 | http://localhost:8092 |
| SAHOOL Fertilizer Advisor | مستشار السماد | 8093 | http://localhost:8093 |
| SAHOOL Smart Irrigation Service | خدمة الري الذكي | 8094 | http://localhost:8094 |
| SAHOOL Agro Advisor | 8095 | http://localhost:8095 |
| SAHOOL Agro Advisor | 8095 | http://localhost:8095 |
| سهول فيجن - Sahool Vision | 8095 | http://localhost:8095 |
| SAHOOL Crop Health Service | 8095 | http://localhost:8095 |
| SAHOOL NDVI Engine | 8097 | http://localhost:8097 |
| محرك سهول للتنبؤ بالإنتاجية | 8098 | http://localhost:8098 |
| SAHOOL Crop Health Service | 8100 | http://localhost:8100 |
| SAHOOL Equipment Service | 8101 | http://localhost:8101 |
| SAHOOL NDVI Processor | 8101 | http://localhost:8101 |
| SAHOOL Task Service | 8103 | http://localhost:8103 |
| SAHOOL Provider Configuration Service | 8104 | http://localhost:8104 |
| SAHOOL IoT Gateway | 8106 | http://localhost:8106 |
| SAHOOL Weather Core | 8108 | http://localhost:8108 |
| SAHOOL Weather Core | 8108 | http://localhost:8108 |
| SAHOOL Notification Service | خدمة الإشعارات | 8110 | http://localhost:8110 |
| SAHOOL Astronomical Calendar Service | 8111 | http://localhost:8111 |
| SAHOOL Alert Service | 8113 | http://localhost:8113 |
| SAHOOL Inventory Service | 8116 | http://localhost:8116 |
| SAHOOL GlobalGAP Compliance Service | 8120 | http://localhost:8120 |
| SAHOOL AI Agents Core | 8120 | http://localhost:8120 |
| SAHOOL MCP Server | 8200 | http://localhost:8200 |

## API Categories | تصنيفات API

### 1. [Authentication APIs](./authentication.md) | واجهات المصادقة
- User login and registration
- Token management
- Password reset

### 2. [Field Management APIs](./fields.md) | واجهات إدارة الحقول
- Field CRUD operations
- Crop profitability analysis
- Field boundaries and mapping

### 3. [Sensor/IoT APIs](./sensors.md) | واجهات أجهزة الاستشعار
- IoT gateway integration
- Virtual sensors
- Sensor data retrieval

### 4. [Weather APIs](./weather.md) | واجهات الطقس
- Current weather conditions
- Weather forecasts
- Weather alerts and warnings

### 5. [AI/Analysis APIs](./ai.md) | واجهات الذكاء الاصطناعي
- AI advisor and recommendations
- Crop health analysis
- Disease detection
- Yield prediction

### 6. [Satellite APIs](./satellite.md) | واجهات الأقمار الصناعية
- NDVI analysis
- Vegetation indices
- Field boundary detection
- Growing Degree Days (GDD)

## Common Patterns | الأنماط الشائعة

### Error Responses | استجابات الخطأ

All errors follow a consistent format:

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "message_ar": "رسالة خطأ بالعربية",
  "details": {}
}
```

### Pagination | التصفح

List endpoints support pagination:

```
GET /api/v1/resource?page=1&limit=20
```

Response includes:
```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```

### Rate Limiting | حدود المعدل

Rate limits are enforced per user/IP:
- Standard endpoints: 60 requests/minute
- Authentication endpoints: 5 requests/minute
- Heavy operations: 10 requests/minute

Headers:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## Services Overview | نظرة عامة على الخدمات

Total Services: 37
Total Endpoints: 392


### Authentication

Endpoints: 2


### Field Management

Endpoints: 58


### Sensors

Endpoints: 22


### Weather

Endpoints: 19


### Ai Analysis

Endpoints: 79


### Notifications

Endpoints: 22


### Crop Health

Endpoints: 6


### Irrigation

Endpoints: 9


### Satellite

Endpoints: 74


### Tasks

Endpoints: 1


### Equipment

Endpoints: 1


### Inventory

Endpoints: 2


### Billing

Endpoints: 19


### Misc

Endpoints: 78


## OpenAPI Specification | مواصفات OpenAPI

Full OpenAPI 3.0 specification: [openapi.json](./openapi.json)

Import into:
- Swagger UI
- Postman
- Insomnia
- Any OpenAPI-compatible tool

## Postman Collection | مجموعة Postman

Download: [SAHOOL.postman_collection.json](./SAHOOL.postman_collection.json)

Includes:
- Pre-configured requests for all endpoints
- Environment variables
- Authentication setup
- Example requests and responses

## Support | الدعم

For API support or questions:
- Email: api-support@sahool.com
- Documentation: https://docs.sahool.com
- Issues: https://github.com/sahool/api/issues

---

*Generated automatically by SAHOOL API Documentation Generator*
*تم إنشاؤه تلقائيًا بواسطة مولد توثيق SAHOOL API*
