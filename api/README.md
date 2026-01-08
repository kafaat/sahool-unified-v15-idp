# SAHOOL Platform API Documentation
## دليل واجهات برمجة التطبيقات لمنصة SAHOOL

**Version:** 16.0.0
**Last Updated:** 2026-01-07

Welcome to the SAHOOL Platform API documentation. This guide provides comprehensive information about our RESTful APIs for agricultural management.

مرحباً بك في دليل واجهات برمجة التطبيقات لمنصة SAHOOL. يوفر هذا الدليل معلومات شاملة حول واجهات برمجة التطبيقات RESTful لإدارة الزراعة.

---

## Table of Contents | جدول المحتويات

1. [Overview](#overview)
2. [API Specifications](#api-specifications)
3. [Authentication](#authentication)
4. [Getting Started](#getting-started)
5. [Rate Limiting](#rate-limiting)
6. [Error Handling](#error-handling)
7. [Versioning](#versioning)
8. [Examples](#examples)
9. [Tools & Resources](#tools--resources)
10. [Legacy Services](#legacy-services)

---

## Overview

The SAHOOL Platform provides a comprehensive set of REST APIs for managing agricultural operations, including:

- **Core Services**: User management, authentication, notifications, and alerts
- **Field Services**: Field management, NDVI tracking, pest management, and geospatial queries
- **Weather Services**: Weather forecasting and alerts
- **IoT Services**: Sensor integration and data collection
- **AI Services**: Agricultural advisory and analysis

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Kong)                      │
│                    https://api.sahool.sa                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
│ Core Services  │  │ Field Services  │  │ Other Services  │
├────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Auth         │  │ • Field Mgmt    │  │ • Weather       │
│ • Users        │  │ • NDVI          │  │ • IoT           │
│ • Notifications│  │ • Pests         │  │ • Marketplace   │
│ • Alerts       │  │ • Geospatial    │  │ • Analytics     │
└────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## API Specifications

We provide OpenAPI 3.0 specifications for all our services:

### Core Services API
**File**: [`openapi/core-services.yaml`](./openapi/core-services.yaml)

**Services Included**:
- **Authentication API**: Login, logout, token refresh
- **User Management API**: CRUD operations for user accounts
- **Notification Service API**: Push notifications, SMS, email, in-app alerts
- **Alert Service API**: Agricultural alerts and warnings

**Base URL**: `https://api.sahool.sa/v1`

### Field Services API
**File**: [`openapi/field-services.yaml`](./openapi/field-services.yaml)

**Services Included**:
- **Field Management API**: Create, read, update, delete fields
- **NDVI Tracking API**: Vegetation index monitoring
- **Pest Management API**: Pest incident reporting and treatment tracking
- **Geospatial API**: Location-based queries

**Base URL**: `https://api.sahool.sa/v1`

---

## Authentication

All API endpoints require authentication using JWT (JSON Web Tokens).

### Getting a Token

**Endpoint**: `POST /auth/login`

```bash
curl -X POST https://api.sahool.sa/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@sahool.com",
    "password": "your-password"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800,
  "token_type": "Bearer",
  "user": {
    "id": "usr_123456",
    "email": "user@sahool.com",
    "firstName": "Ahmed",
    "lastName": "Ali",
    "role": "FARMER"
  }
}
```

### Using the Token

Include the access token in the `Authorization` header for all subsequent requests:

```bash
curl -X GET https://api.sahool.sa/v1/fields \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: your-tenant-id"
```

### Token Refresh

Access tokens expire after 30 minutes. Use the refresh token to get a new access token:

```bash
curl -X POST https://api.sahool.sa/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "YOUR_REFRESH_TOKEN"
  }'
```

---

## Getting Started

### Prerequisites

1. **Account**: Sign up for a SAHOOL account at [https://sahool.sa](https://sahool.sa)
2. **Credentials**: Obtain your API credentials from the dashboard
3. **Tenant ID**: Note your tenant ID for multi-tenant operations

### Quick Start Example

Here's a complete example of authenticating and retrieving your fields:

```javascript
// 1. Login
const loginResponse = await fetch('https://api.sahool.sa/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@sahool.com',
    password: 'your-password'
  })
});

const { access_token, user } = await loginResponse.json();

// 2. Get Fields
const fieldsResponse = await fetch('https://api.sahool.sa/v1/fields', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'X-Tenant-ID': user.tenantId
  }
});

const fields = await fieldsResponse.json();
console.log('My Fields:', fields.data);
```

### Python Example

```python
import requests

# 1. Login
login_response = requests.post(
    'https://api.sahool.sa/v1/auth/login',
    json={
        'email': 'user@sahool.com',
        'password': 'your-password'
    }
)

auth_data = login_response.json()
access_token = auth_data['access_token']
tenant_id = auth_data['user']['tenantId']

# 2. Get Fields
fields_response = requests.get(
    'https://api.sahool.sa/v1/fields',
    headers={
        'Authorization': f'Bearer {access_token}',
        'X-Tenant-ID': tenant_id
    }
)

fields = fields_response.json()
print('My Fields:', fields['data'])
```

---

## Rate Limiting

API requests are rate-limited based on your subscription tier:

| Tier | Requests per Minute | Requests per Hour |
|------|---------------------|-------------------|
| Free | 30 | 1,000 |
| Standard | 60 | 3,000 |
| Premium | 120 | 10,000 |
| Enterprise | Custom | Custom |

### Rate Limit Headers

All API responses include rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "statusCode": 429,
  "message": "Too many requests. Please try again later."
}
```

**Best Practices**:
- Implement exponential backoff
- Cache responses when possible
- Use webhooks for real-time updates instead of polling
- Consider upgrading your tier for higher limits

---

## Error Handling

All API errors follow a consistent format:

### Error Response Structure

```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message",
  "statusCode": 400,
  "timestamp": "2026-01-07T10:30:00Z",
  "path": "/api/v1/fields",
  "details": {
    "field": "name",
    "code": "required"
  }
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Versioning

The SAHOOL API uses URL-based versioning. The current version is **v1**.

**Format**: `https://api.sahool.sa/{version}/{endpoint}`

**Example**: `https://api.sahool.sa/v1/fields`

---

## Examples

### Create a Field

```bash
curl -X POST https://api.sahool.sa/v1/fields \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "حقل القمح الشمالي",
    "cropType": "wheat",
    "coordinates": [
      [46.7, 24.6],
      [46.8, 24.6],
      [46.8, 24.7],
      [46.7, 24.7]
    ],
    "irrigationType": "drip",
    "soilType": "sandy_loam",
    "plantingDate": "2024-01-15"
  }'
```

### Report Pest Incident

```bash
curl -X POST https://api.sahool.sa/v1/pests/incidents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "fieldId": "123e4567-e89b-12d3-a456-426614174000",
    "tenantId": "tenant-001",
    "pestType": "INSECT",
    "pestName": "Aphids",
    "severityLevel": 3,
    "affectedArea": 0.5,
    "detectedAt": "2026-01-07T10:00:00Z",
    "reportedBy": "Field Inspector",
    "notes": "Found on wheat leaves"
  }'
```

---

## Tools & Resources

### Swagger UI

Interactive API documentation is available at:
- **Production**: [https://api.sahool.sa/docs](https://api.sahool.sa/docs)
- **Staging**: [https://staging-api.sahool.sa/docs](https://staging-api.sahool.sa/docs)

### Postman Collection

Import our Postman collection: [SAHOOL.postman_collection.json](./SAHOOL.postman_collection.json)

### SDKs

Official SDKs:
- **JavaScript/TypeScript**: [`@sahool/api-client`](../../packages/api-client)
- **Python**: Coming soon

---

## Legacy Services

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

### Documentation

- **API Reference**: See OpenAPI specs in [`/docs/api/openapi/`](./openapi/)
- **Architecture Docs**: [`/docs/architecture/`](../architecture/)
- **Legacy Services**: See sections above for backward compatibility

### Community

- **Developer Forum**: [https://community.sahool.sa](https://community.sahool.sa)
- **GitHub Issues**: [GitHub Repository](https://github.com/sahool/sahool-platform)

### Contact

- **Email**: api-support@sahool.sa
- **Technical Support**: support@sahool.sa

---

## Best Practices

### Security

1. **Never share API tokens** in public repositories or client-side code
2. **Use HTTPS** for all API requests
3. **Rotate tokens regularly** (every 90 days recommended)
4. **Implement proper token storage** (secure keychain, environment variables)
5. **Use tenant isolation** - Always include X-Tenant-ID header

### Performance

1. **Implement caching** for frequently accessed data
2. **Use pagination** for large datasets
3. **Batch requests** when possible
4. **Monitor rate limits** and implement backoff strategies

---

## Changelog

### Version 16.0.0 (2026-01-07)
- ✨ Added comprehensive OpenAPI 3.0 specifications
- ✨ Enhanced alert service with new endpoints
- ✨ Improved notification service with multi-channel support
- 🔧 Updated authentication with token rotation
- 📚 Complete API documentation overhaul

### Version 15.3.0 (2024-12-01)
- ✨ Added geospatial query endpoints
- ✨ Enhanced pest management API
- 🐛 Fixed NDVI data retrieval issues

---

## License

© 2024-2026 SAHOOL Platform. All rights reserved.

---

**Last Updated**: 2026-01-07
**Version**: 16.0.0
**Maintained by**: SAHOOL Platform API Team
