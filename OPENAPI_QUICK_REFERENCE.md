# SAHOOL OpenAPI Quick Reference

**Version:** 16.0.0  
**Last Updated:** 2026-02-11

> 📖 **Full Documentation:** See [openapi-schema.md](./openapi-schema.md) for complete OpenAPI specifications

---

## Quick Access

### Base URLs

```
Development:  http://localhost:8000 (Kong Gateway)
Staging:      https://api-staging.sahool.io
Production:   https://api.sahool.io
```

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/v1/fields
```

---

## Service Quick Reference

### 🔐 Authentication & Users

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | User login → JWT token |
| `/api/v1/auth/register` | POST | Create new account |
| `/api/v1/auth/refresh` | POST | Refresh access token |
| `/api/v1/auth/logout` | POST | Logout (revoke token) |
| `/api/v1/auth/me` | GET | Get current user profile |
| `/api/v1/users` | GET | List users (admin) |

**Service:** user-service (Port 3025)  
**Rate Limit:** 30/min (auth), 100/min (protected)

---

### 🌾 Field Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fields` | GET | List farmer's fields |
| `/api/v1/fields` | POST | Register new field |
| `/api/v1/fields/{id}` | GET | Get field details |
| `/api/v1/fields/{id}` | PATCH | Update field |
| `/api/v1/fields/{id}/zones` | GET | List field zones |
| `/api/v1/fields/{id}/crops` | GET | Crop history |

**Service:** field-management-service (Port 3000)

**Example: Create Field**
```json
POST /api/v1/fields
{
  "name": "حقل القمح الشمالي",
  "name_en": "North Wheat Field",
  "area_hectares": 5.2,
  "boundary": {
    "type": "Polygon",
    "coordinates": [[[44.191, 15.369], [44.192, 15.369], ...]]
  },
  "crop_type": "wheat",
  "irrigation_type": "pivot"
}
```

---

### 💧 Irrigation Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/irrigation/{field_id}/schedule` | GET | Get irrigation schedule |
| `/api/v1/irrigation/{field_id}/schedule` | POST | Create/update schedule |
| `/api/v1/irrigation/{field_id}/recommendation` | GET | Get recommendation |

**Service:** irrigation-smart (Port 8094)

**Example Response:**
```json
{
  "field_id": "field_001",
  "recommendation": {
    "action": "irrigate",
    "amount_mm": 25,
    "timing": "within_24_hours",
    "reason": "Low soil moisture (35%) + no rain forecast"
  }
}
```

---

### 🌱 Crop Health & Intelligence

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/crop-health/{field_id}/diagnosis` | GET | Get field diagnosis |
| `/api/v1/crop-health/{field_id}/zones/{zone_id}/observations` | POST | Add observation |
| `/api/v1/crop-health/{field_id}/vrt` | GET | Export VRT for precision ag |

**Service:** crop-intelligence-service (Port 8095)

**Example: Field Diagnosis**
```json
GET /api/v1/crop-health/field_23/diagnosis?date=2026-02-11
Response:
{
  "summary": {
    "zones_total": 12,
    "zones_critical": 2,
    "zones_warning": 4
  },
  "actions": [
    {
      "zone_id": "zone_c",
      "type": "irrigation",
      "priority": "P0",
      "title_en": "Urgent irrigation within 24 hours"
    }
  ]
}
```

---

### 📊 Advisory & Recommendations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/advisory/{field_id}` | GET | Field advisory |
| `/api/v1/fertilizer/recommendation` | POST | Fertilizer recommendation |

**Service:** advisory-service (Port 8093)

**Example: Fertilizer Recommendation**
```json
POST /api/v1/fertilizer/recommendation
{
  "field_id": "field_001",
  "crop_type": "wheat",
  "crop_stage": "tillering",
  "soil_test": {
    "nitrogen_ppm": 18,
    "phosphorus_ppm": 25,
    "potassium_ppm": 150,
    "ph": 7.2
  },
  "target_yield_ton_per_ha": 5.0
}

Response:
{
  "product": "Urea 46%",
  "rate_kg_per_ha": 46,
  "application_method": "broadcast",
  "timing": "early_morning",
  "cost_estimate_sar": 850
}
```

---

### 🛰️ Satellite & NDVI

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/vegetation/{field_id}/ndvi` | GET | NDVI analysis |
| `/api/v1/vegetation/{field_id}/timeseries` | GET | NDVI time series |
| `/api/v1/satellite/{field_id}` | GET | Satellite imagery |

**Service:** vegetation-analysis-service (Port 8090)  
**Caching:** 30 minutes

**Example:**
```json
GET /api/v1/vegetation/field_001/ndvi?date=2026-02-11&source=sentinel-2
Response:
{
  "field_id": "field_001",
  "date": "2026-02-11",
  "source": "sentinel-2",
  "ndvi_mean": 0.72,
  "health_status": "good",
  "cloud_coverage_pct": 5,
  "raster_url": "https://cdn.sahool/ndvi/field_001_2026-02-11.tiff"
}
```

---

### 🌤️ Weather

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/weather/current` | GET | Current weather |
| `/api/v1/weather/forecast` | GET | Weather forecast (up to 14 days) |
| `/api/v1/weather/field/{field_id}` | GET | Field-specific weather |

**Service:** weather-service (Port 8092)  
**Caching:** 15 minutes

**Example:**
```bash
GET /api/v1/weather/current?latitude=15.369&longitude=44.191
```

---

### 📡 IoT Sensors & Actuators

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/iot/fields/{field_id}/sensors` | GET | List sensors |
| `/api/v1/iot/sensors/{sensor_id}/readings` | GET | Sensor readings |
| `/api/v1/iot/actuators/{actuator_id}/control` | POST | Control actuator (pump/valve) |

**Service:** iot-service (Port 8117)

**Example: Control Pump**
```json
POST /api/v1/iot/actuators/pump-001/control
{
  "action": "on",
  "duration_minutes": 30,
  "reason": "Scheduled irrigation"
}
```

---

### 🛒 Marketplace

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/marketplace/products` | GET | List products (seeds, fertilizers, equipment) |
| `/api/v1/marketplace/orders` | POST | Create order |

**Service:** marketplace-service (Port 3010)  
**Rate Limit:** 60/min, 1000/hour

---

### 🤖 AI/ML Services

#### Vision (Pest/Disease/Weed Detection)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/vision/detect` | POST | Detect pests/diseases in image |
| `/api/v1/vision/batch` | POST | Batch image processing |

**Service:** yolo26-vision-service (Port 8150)

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/vision/detect \
  -H "Authorization: Bearer {token}" \
  -F "image=@wheat_leaf.jpg" \
  -F "detection_type=disease" \
  -F "crop_type=wheat"
```

#### LLM Chat Assistant

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/llm/chat` | POST | Chat with agricultural assistant |
| `/api/v1/llm/advisory` | POST | Generate advisory |

**Service:** llm-orchestrator-service (Port 8127)

---

### 🏔️ Terrain & Hydrology

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/terrain/{field_id}/slope` | GET | Slope analysis |
| `/api/v1/terrain/{field_id}/aspect` | GET | Aspect analysis |
| `/api/v1/hydrology/{field_id}/drainage` | GET | Drainage analysis |

**Services:** 
- terrain-core-service (Port 8106)
- hydrology-service (Port 8170)

---

### 📱 Edge Computing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/edge/devices` | GET | List edge devices |
| `/api/v1/edge/deploy` | POST | Deploy model to edge |

**Service:** edge-orchestrator-service (Port 8150)

---

## Common Patterns

### Pagination

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20, max: 100)

---

### Error Response

```json
{
  "error": {
    "code": "FIELD_NOT_FOUND",
    "message": "Field with ID 'field_001' not found",
    "message_ar": "لم يتم العثور على الحقل",
    "request_id": "uuid",
    "timestamp": "2026-02-11T19:51:45Z"
  }
}
```

**Common Error Codes:**
- `INVALID_TOKEN` - JWT expired/invalid
- `UNAUTHORIZED_ACCESS` - Insufficient permissions
- `VALIDATION_ERROR` - Invalid input
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `SERVICE_UNAVAILABLE` - Backend down

---

### Health Checks

```bash
# Liveness
GET /healthz
GET /health/live

# Readiness
GET /readyz
GET /health/ready

# Metrics (Prometheus)
GET /metrics
```

**All services implement these endpoints**

---

## Rate Limiting

### Headers

```http
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 95
X-RateLimit-Reset: 1707674460
```

### Limits by Service

| Service | Per Minute | Per Hour |
|---------|------------|----------|
| **Public Auth** | 30 | 500 |
| **Protected APIs** | 100 | 2000 |
| **Marketplace** | 60 | 1000 |
| **Billing** | 20 | 200 |

---

## Security

### JWT Token Structure

```json
{
  "sub": "user_id",
  "tenant_id": "tenant_001",
  "role": "farmer|admin|agronomist",
  "permissions": ["field:read", "field:write"],
  "iat": 1707674400,
  "exp": 1707760800
}
```

### Security Headers (Auto-Applied)

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
X-Correlation-Id: {uuid}
```

---

## Testing with cURL

### Login & Get Token

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@example.com","password":"password"}' \
  | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/fields
```

### Create Field

```bash
curl -X POST http://localhost:8000/api/v1/fields \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "حقل القمح",
    "area_hectares": 5.2,
    "boundary": {
      "type": "Polygon",
      "coordinates": [[[44.191, 15.369], [44.192, 15.369], [44.192, 15.370], [44.191, 15.369]]]
    },
    "crop_type": "wheat"
  }'
```

### Get Irrigation Recommendation

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/irrigation/field_001/recommendation"
```

---

## Service Categories

### 📊 Agricultural Intelligence (Core)
- advisory-service, irrigation-smart, crop-intelligence-service, yield-prediction-service

### 🛰️ Geospatial & Remote Sensing
- vegetation-analysis-service, ndvi-processor, terrain-core-service, hydrology-service

### 📡 IoT & Monitoring
- iot-service, iot-gateway, iot-sensor-hub, virtual-sensors

### 🌤️ Environmental Data
- weather-service, weather-core, astronomical-calendar

### 🤖 AI/ML
- yolo26-vision-service, llm-orchestrator-service, ai-agents-service, pest-detection-service

### 💼 Business Operations
- marketplace-service, billing-core, equipment-service, task-service, inventory-service

### 🔐 Platform Infrastructure
- user-service, field-management-service, audit-service, notification-service

---

## Kong API Gateway Plugins

### Global Plugins (All Routes)

✅ **cors** - Cross-origin resource sharing  
✅ **prometheus** - Metrics collection  
✅ **correlation-id** - Distributed tracing  
✅ **request-size-limiting** - Max 10MB  
✅ **response-transformer** - Security headers  
✅ **bot-detection** - Block malicious bots

### Service-Specific

- **rate-limiting** - user-service, marketplace-service, billing-core
- **ip-restriction** - billing-core (admin only)
- **proxy-cache** - weather-service (15min), vegetation-analysis-service (30min)

---

## WebSocket Support

### Real-Time Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket(
  'ws://localhost:8117/ws/fields/field_001?token=JWT_TOKEN'
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'sensor_reading':
      console.log(`Sensor ${data.sensor_id}: ${data.value}`);
      break;
    case 'alert':
      showAlert(data);
      break;
  }
};
```

**Service:** ws-gateway (Port 8081)

---

## NATS Event Streams

### Event Subjects

```
sahool.{tenant_id}.fields.created
sahool.{tenant_id}.fields.updated
sahool.{tenant_id}.irrigation.scheduled
sahool.{tenant_id}.alerts.generated
sahool.{tenant_id}.harvest.completed
```

**Broker:** nats:4222  
**Monitoring:** http://localhost:8222/varz

---

## Database Access

### Connection Pooling

```
PostgreSQL → PgBouncer → Services
postgres:5432 → pgbouncer:6432
```

**Connection String:**
```
postgresql://sahool:password@pgbouncer:6432/sahool
```

**Pool Settings:**
- Max DB Connections: 250
- Default Pool Size: 30
- Max Client Connections: 800

---

## Storage Services

### MinIO (S3-Compatible)

```bash
# Upload file
mc cp image.jpg myminio/fields/field_001/

# Get presigned URL
mc share download myminio/fields/field_001/image.jpg
```

**Endpoint:** http://localhost:9000  
**Console:** http://localhost:9001

### Redis Cache

```bash
# Set value
redis-cli SET field:001:ndvi 0.72 EX 1800

# Get value
redis-cli GET field:001:ndvi
```

**Endpoint:** redis://localhost:6379

---

## Development Tools

### Check Service Health

```bash
# Check all services
for service in $(docker compose ps --services); do
  echo "$service:"
  curl -s http://localhost:8000/healthz 2>/dev/null || echo "Not available"
done
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f advisory-service
```

### API Gateway Admin

```bash
# List routes
curl http://localhost:8001/routes

# List services
curl http://localhost:8001/services
```

---

## Additional Resources

- **Full API Documentation:** [openapi-schema.md](./openapi-schema.md)
- **Service Registry:** [governance/services.yaml](./governance/services.yaml)
- **Kong Configuration:** [infrastructure/gateway/kong/kong.yml](./infrastructure/gateway/kong/kong.yml)
- **Docker Compose:** [docker-compose.yml](./docker-compose.yml)
- **Architecture Docs:** [docs/](./docs/)

---

**Generated:** 2026-02-11  
**Maintainer:** KAFAAT DevOps Team  
**License:** Proprietary
