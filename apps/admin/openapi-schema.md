# SAHOOL Platform — OpenAPI Service Schema Reference

> **Gateway**: `http://localhost:8000` (dev) | `https://api.sahool.app` (prod)
> **Auth**: `Authorization: Bearer <JWT>` on all protected routes
> **Source of Truth**: [`kong.yml`](file:///d:/PROJECTS/v75/sahool-unified-v15-idp/infra/kong/kong.yml)

---

## Table of Contents

| # | Service | Kong Path | Type |
|---|---------|-----------|------|
| 1 | [postgres](#1-postgres) | N/A (Infrastructure) | Infra |
| 2 | [pgbouncer](#2-pgbouncer) | N/A (Infrastructure) | Infra |
| 3 | [nats](#3-nats) | N/A (Infrastructure) | Infra |
| 4 | [kong](#4-kong) | `/health`, `/ping` | Infra |
| 5 | [user-service](#5-user-service) | `/api/v1/users`, `/api/v1/auth` | Core |
| 6 | [field-management-service](#6-field-management-service) | `/api/v1/fields` | Core |
| 7 | [marketplace-service](#7-marketplace-service) | `/api/v1/marketplace` | Enterprise |
| 8 | [research-core](#8-research-core) | `/api/v1/research` | Enterprise |
| 9 | [chat-service](#9-chat-service) | `/api/v1/chat` | Shared |
| 10 | [iot-service](#10-iot-service) | `/api/v1/iot-service` | Enterprise |
| 11 | [community-chat](#11-community-chat) | `/api/v1/community/chat` | Shared |
| 12 | [ws-gateway](#12-ws-gateway) | `/api/v1/ws` | Shared |
| 13 | [billing-core](#13-billing-core) | `/api/v1/billing` | Enterprise |
| 14 | [vegetation-analysis-service](#14-vegetation-analysis-service) | `/api/v1/vegetation`, `/api/v1/satellite` | Professional |
| 15 | [indicators-service](#15-indicators-service) | `/api/v1/indicators` | Shared |
| 16 | [weather-service](#16-weather-service) | `/api/v1/weather` | Starter |
| 17 | [advisory-service](#17-advisory-service) | `/api/v1/advisory`, `/api/v1/advice` | Starter |
| 18 | [irrigation-smart](#18-irrigation-smart) | `/api/v1/irrigation` | Professional |
| 19 | [crop-intelligence-service](#19-crop-intelligence-service) | `/api/v1/crop-health`, `/api/v1/crop-intelligence` | Professional |
| 20 | [virtual-sensors](#20-virtual-sensors) | `/api/v1/sensors/virtual` | Professional |
| 21 | [yield-prediction-service](#21-yield-prediction-service) | `/api/v1/yield` | Professional |
| 22 | [field-chat](#22-field-chat) | `/api/v1/field-chat` | Shared |
| 23 | [equipment-service](#23-equipment-service) | `/api/v1/equipment` | Professional |
| 24 | [task-service](#24-task-service) | `/api/v1/tasks` | Shared |
| 25 | [provider-config](#25-provider-config) | `/api/v1/providers` | Shared |
| 26 | [agro-advisor](#26-agro-advisor) | `/api/v1/agro-advisor` (legacy) | Deprecated |
| 27 | [iot-gateway](#27-iot-gateway) | `/api/v1/iot`, `/api/v1/agro-rules` | Enterprise |
| 28 | [weather-core](#28-weather-core) | N/A (deprecated) | Deprecated |
| 29 | [notification-service](#29-notification-service) | `/api/v1/notifications` | Starter |
| 30 | [astronomical-calendar](#30-astronomical-calendar) | `/api/v1/astronomical`, `/api/v1/calendar` | Starter |
| 31 | [alert-service](#31-alert-service) | `/api/v1/alerts` | Shared |
| 32 | [inventory-service](#32-inventory-service) | `/api/v1/inventory` | Professional |
| 33 | [field-intelligence](#33-field-intelligence) | `/api/v1/field-intelligence` | Professional |
| 34 | [mcp-server](#34-mcp-server) | `/api/v1/mcp` | Shared |
| 35 | [crm-service](#35-crm-service) | `/api/v1/crm` | Enterprise |
| 36 | [lowcode-engine](#36-lowcode-engine) | `/api/v1/lowcode` | Enterprise |
| 37 | [ai-agents-service](#37-ai-agents-service) | `/api/v1/ai-agents` | Enterprise |
| 38 | [agro-rules](#38-agro-rules) | `/api/v1/agro-rules` (via iot-gateway) | Enterprise |

---

## Infrastructure Services (No Kong Routes)

### 1. postgres

| Property | Value |
|----------|-------|
| **Container** | `sahool-postgres` |
| **Image** | `postgis/postgis:16-3.4` |
| **Internal Port** | `5432` |
| **DNS** | `postgres` |
| **Health** | `pg_isready -U $POSTGRES_USER` |

> [!NOTE]
> Not exposed via Kong. Used internally by all services via `pgbouncer`.

---

### 2. pgbouncer

| Property | Value |
|----------|-------|
| **Container** | `sahool-pgbouncer` |
| **Internal Port** | `6432` |
| **DNS** | `pgbouncer` |
| **Health** | `pidof pgbouncer` |

**Connection String**: `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}`

> [!NOTE]
> Not exposed via Kong. Connection pooler for PostgreSQL.

---

### 3. nats

| Property | Value |
|----------|-------|
| **Container** | `sahool-nats` |
| **Internal Port** | `4222` (client), `4223` (cluster) |
| **DNS** | `nats` |
| **Health** | `/healthz` on port `8222` |

**Connection String**: `nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222`

> [!NOTE]
> Not exposed via Kong. JetStream-enabled message broker for inter-service events.

---

### 4. kong

| Property | Value |
|----------|-------|
| **Container** | `sahool-kong` |
| **Proxy Port** | `8000` |
| **Admin Port** | `8001` (localhost only) |
| **Mode** | DB-less (Declarative) |
| **Config** | `/kong/declarative/kong.yml` |

#### Health Endpoints (Public)

```yaml
GET /health    → 200 "SAHOOL Platform is healthy"
GET /ping      → 200 "SAHOOL Platform is healthy"
GET /          → 200 { platform, version, status, endpoints }
```

#### Global Plugins

| Plugin | Purpose |
|--------|---------|
| `cors` | Cross-origin (origins: `*` in dev) |
| `request-size-limiting` | 10 MB max payload |
| `file-log` | Access logging |
| `prometheus` | Metrics |
| `response-transformer` | Security headers (HSTS, CSP, X-Frame-Options) |
| `correlation-id` | `X-Request-ID` injection |

---

## Application Services

### 5. user-service

| Property | Value |
|----------|-------|
| **Upstream** | `user-service:3025` |
| **Kong Service** | `user-service` |
| **Kong Paths** | `/api/v1/users`, `/api/v1/auth` |
| **Methods** | GET, POST, PUT, PATCH, DELETE |
| **ACL** | starter, professional, enterprise, admin |
| **Rate Limit** | 2000/min, 100000/hr |

#### Endpoints

```yaml
# === Authentication (Public — no JWT on /auth/login, /register, /refresh, /send-otp, /verify-otp) ===

POST /api/v1/auth/login:
  body: { email: string, password: string }
  response:
    access_token: string
    refresh_token: string
    token_type: "Bearer"
    expires_in: number
    user: { id, email, role, name }

POST /api/v1/auth/register:
  body: { email: string, password: string, name: string, phone?: string }
  response: { user: User, access_token: string }

POST /api/v1/auth/refresh:
  body: { refresh_token: string }
  response: { access_token: string, refresh_token: string }

POST /api/v1/auth/send-otp:
  body: { phone: string }
  response: { success: boolean, message: string }

POST /api/v1/auth/verify-otp:
  body: { phone: string, otp: string }
  response: { verified: boolean }

# === Protected (JWT required) ===

GET /api/v1/auth/me:
  response: { user: User, permissions: string[] }

POST /api/v1/auth/logout:
  response: { success: boolean }

GET /api/v1/users:
  query: { page?: number, limit?: number, role?: string, search?: string }
  response:
    data: User[]
    meta: { total, page, limit }

GET /api/v1/users/:id:
  response: User

PUT /api/v1/users/:id:
  body: { name?, email?, role?, phone?, status? }
  response: User

DELETE /api/v1/users/:id:
  response: { success: boolean }
```

**Types**:
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "manager" | "farmer" | "researcher";
  phone?: string;
  status: "active" | "inactive" | "suspended";
  created_at: string;
  updated_at: string;
}
```

---

### 6. field-management-service

| Property | Value |
|----------|-------|
| **Upstream** | `field-management-service:3000` |
| **Kong Service** | `field-core` |
| **Kong Paths** | `/api/v1/fields`, `/api/v1/field-core` |
| **Methods** | GET, POST, PUT, PATCH, DELETE |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 100/min, 5000/hr |
| **Max Payload** | 10 MB |

#### Endpoints

```yaml
GET /api/v1/fields:
  query: { page?, limit?, crop_type?, owner_id?, search? }
  response:
    data:
      - id: string
        name: string
        area_hectares: number
        coordinates: GeoJSON.Polygon
        crop_type: string
        owner_id: string
        health_status: "Healthy" | "Moderate" | "Stressed"
        created_at: string
    meta: { total, page, limit }

GET /api/v1/fields/:id:
  response: Field

POST /api/v1/fields:
  body: { name: string, coordinates: [number,number][], crop_type: string }
  response: Field

PUT /api/v1/fields/:id:
  body: { name?, coordinates?, crop_type? }
  response: Field

DELETE /api/v1/fields/:id:
  response: { success: boolean }

GET /api/v1/fields/:id/ndvi:
  response:
    field_id: string
    ndvi_value: number
    health_status: "Healthy" | "Moderate" | "Stressed"
    timestamp: string
```

---

### 7. marketplace-service

| Property | Value |
|----------|-------|
| **Upstream** | `marketplace-service:3010` |
| **Kong Paths** | `/api/v1/marketplace` |
| **ACL** | enterprise |
| **Rate Limit** | 10000/min |

#### Endpoints

```yaml
GET /api/v1/marketplace/listings:
  query: { page?, limit?, category?, search?, min_price?, max_price? }
  response: { data: Listing[], meta: Pagination }

POST /api/v1/marketplace/listings:
  body: { title: string, price: number, category: string, description: string, images?: string[] }
  response: Listing

GET /api/v1/marketplace/listings/:id:
  response: Listing

PUT /api/v1/marketplace/listings/:id:
  body: { title?, price?, category?, description?, status? }
  response: Listing

DELETE /api/v1/marketplace/listings/:id:
  response: { success: boolean }

GET /api/v1/marketplace/orders:
  query: { page?, limit?, status? }
  response: { data: Order[], meta: Pagination }

POST /api/v1/marketplace/orders:
  body: { listing_id: string, quantity: number }
  response: Order
```

---

### 8. research-core

| Property | Value |
|----------|-------|
| **Upstream** | `research-core:3015` |
| **Kong Paths** | `/api/v1/research` |
| **ACL** | enterprise, research |
| **Rate Limit** | 10000/min |

#### Endpoints

```yaml
GET /api/v1/research/projects:
  query: { page?, limit?, status?, search? }
  response: { data: ResearchProject[], meta: Pagination }

POST /api/v1/research/projects:
  body: { title: string, description: string, field_ids?: string[], methodology?: string }
  response: ResearchProject

GET /api/v1/research/projects/:id:
  response: ResearchProject

PUT /api/v1/research/projects/:id:
  body: { title?, description?, status?, findings? }
  response: ResearchProject

GET /api/v1/research/experiments:
  query: { project_id?: string, page?, limit? }
  response: { data: Experiment[], meta: Pagination }

POST /api/v1/research/experiments:
  body: { project_id: string, name: string, parameters: object }
  response: Experiment
```

---

### 9. chat-service

| Property | Value |
|----------|-------|
| **Upstream** | `chat-service:8000` |
| **Kong Paths** | `/api/v1/chat` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 2000/min |

#### Endpoints

```yaml
GET /api/v1/chat/conversations:
  query: { page?, limit? }
  response: { data: Conversation[], meta: Pagination }

POST /api/v1/chat/conversations:
  body: { participant_ids: string[], title?: string }
  response: Conversation

GET /api/v1/chat/conversations/:id/messages:
  query: { page?, limit?, before?: string }
  response: { data: Message[], meta: Pagination }

POST /api/v1/chat/conversations/:id/messages:
  body: { content: string, type?: "text" | "image" | "file" }
  response: Message

DELETE /api/v1/chat/conversations/:id:
  response: { success: boolean }
```

---

### 10. iot-service

| Property | Value |
|----------|-------|
| **Upstream** | `iot-service:8117` |
| **Kong Paths** | `/api/v1/iot-service` |
| **ACL** | enterprise |
| **Rate Limit** | 10000/min |

#### Endpoints

```yaml
GET /api/v1/iot-service/devices:
  query: { page?, limit?, field_id?, type?, status? }
  response: { data: IoTDevice[], meta: Pagination }

POST /api/v1/iot-service/devices:
  body: { name: string, type: string, field_id: string, serial_number: string }
  response: IoTDevice

GET /api/v1/iot-service/devices/:id:
  response: IoTDevice

GET /api/v1/iot-service/devices/:id/readings:
  query: { from?: string, to?: string, metric?: string }
  response: { data: SensorReading[], meta: Pagination }

PUT /api/v1/iot-service/devices/:id:
  body: { name?, status?, config? }
  response: IoTDevice

DELETE /api/v1/iot-service/devices/:id:
  response: { success: boolean }
```

---

### 11. community-chat

| Property | Value |
|----------|-------|
| **Upstream** | `chat-service:8115` |
| **Kong Paths** | `/api/v1/community/chat` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 2000/min |

#### Endpoints

```yaml
GET /api/v1/community/chat/channels:
  query: { page?, limit?, category? }
  response: { data: Channel[], meta: Pagination }

POST /api/v1/community/chat/channels:
  body: { name: string, description?: string, is_public: boolean }
  response: Channel

GET /api/v1/community/chat/channels/:id/messages:
  query: { page?, limit? }
  response: { data: Message[], meta: Pagination }

POST /api/v1/community/chat/channels/:id/messages:
  body: { content: string }
  response: Message

POST /api/v1/community/chat/channels/:id/join:
  response: { success: boolean }

POST /api/v1/community/chat/channels/:id/leave:
  response: { success: boolean }
```

> [!WARNING]
> **Deprecated** — Will be replaced by `chat-service` in v17.0.0.

---

### 12. ws-gateway

| Property | Value |
|----------|-------|
| **Upstream** | `ws-gateway:8081` |
| **Kong Paths** | `/api/v1/ws` |
| **Protocols** | HTTP, HTTPS |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 5000/min |

#### WebSocket Protocol

```yaml
# Connect: ws://localhost:8081/ws?token=<jwt>

# Client → Server messages:
{ type: "subscribe", channel: string }
{ type: "unsubscribe", channel: string }
{ type: "ping" }

# Server → Client messages:
{ type: "message", channel: string, data: any, timestamp: string }
{ type: "notification", data: Notification }
{ type: "pong" }

# Available channels:
- "field:{field_id}"         # Field updates
- "weather:{lat}:{lon}"     # Weather updates
- "alerts:{user_id}"        # User alerts
- "notifications:{user_id}" # User notifications
- "iot:{device_id}"         # IoT sensor data
```

---

### 13. billing-core

| Property | Value |
|----------|-------|
| **Upstream** | `billing-core:8089` |
| **Kong Paths** | `/api/v1/billing` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/billing/subscription:
  response:
    plan: "starter" | "professional" | "enterprise"
    status: "active" | "past_due" | "canceled"
    current_period_end: string
    usage: { fields: number, api_calls: number }

POST /api/v1/billing/checkout:
  body: { plan: string, billing_cycle: "monthly" | "annual" }
  response: { checkout_url: string, session_id: string }

GET /api/v1/billing/invoices:
  query: { page?, limit?, status? }
  response: { data: Invoice[], meta: Pagination }

POST /api/v1/billing/payments:
  body: { invoice_id: string, amount: number, method: "stripe" | "tharwatt" }
  response: { payment_id: string, status: string }

GET /api/v1/billing/usage:
  query: { period?: "current" | "previous" }
  response: { api_calls: number, storage_mb: number, fields_count: number }
```

---

### 14. vegetation-analysis-service

| Property | Value |
|----------|-------|
| **Upstream** | `vegetation-analysis-service:8090` |
| **Kong Paths** | `/api/v1/vegetation`, `/api/v1/satellite`, `/api/v1/ndvi` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min, 50000/hr |
| **Read Timeout** | 120s |
| **Max Payload** | 50 MB |

#### Endpoints

```yaml
POST /api/v1/vegetation/analyze:
  body: { field_id: string, date_range?: { start: string, end: string } }
  response:
    field_id: string
    indices: { ndvi: number, evi: number, ndre: number, ndwi: number }
    zones: [{ zone_id: string, health: string, area_percent: number }]
    timestamp: string

GET /api/v1/satellite/imagery/:field_id:
  query: { date?: string, index?: "ndvi" | "evi" | "rgb" }
  response: { image_url: string, metadata: object }

GET /api/v1/satellite/timeseries/:field_id:
  query: { start_date: string, end_date: string, index?: string }
  response: { data: [{ date: string, value: number }] }

GET /api/v1/ndvi/:field_id:
  response:
    field_id: string
    ndvi_value: number
    health_status: "Healthy" | "Moderate" | "Stressed"
    timestamp: string
```

---

### 15. indicators-service

| Property | Value |
|----------|-------|
| **Upstream** | `indicators-service:8091` |
| **Kong Paths** | `/api/v1/indicators` |
| **ACL** | professional, enterprise, research |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/indicators/dashboard:
  response:
    total_fields: number
    total_area_hectares: number
    active_users: number
    pending_tasks: number
    alerts_count: number
    crop_distribution: [{ crop: string, area: number }]
    health_summary: { healthy: number, moderate: number, stressed: number }

GET /api/v1/indicators/trends:
  query: { metric: string, period: "7d" | "30d" | "90d" }
  response: { data: [{ date: string, value: number }] }

GET /api/v1/indicators/field/:field_id:
  response:
    ndvi: number
    lai: number
    soil_moisture: number
    growth_stage: string
    last_updated: string
```

---

### 16. weather-service

| Property | Value |
|----------|-------|
| **Upstream** | `weather-service:8092` |
| **Kong Paths** | `/api/v1/weather`, `/api/v1/weather/advanced` |
| **ACL** | starter+ (basic), professional+ (advanced) |
| **Rate Limit** | 100/min (basic), 1000/min (advanced) |

#### Endpoints

```yaml
GET /api/v1/weather/current:
  query: { lat: number, lon: number }
  response:
    temperature: number
    humidity: number
    wind_speed: number
    conditions: string
    timestamp: string

GET /api/v1/weather/forecast:
  query: { lat: number, lon: number, days?: number }
  response: { daily: DayForecast[], hourly?: HourForecast[] }

GET /api/v1/weather/agricultural-indices:
  query: { lat: number, lon: number }
  response:
    gdd: number           # Growing Degree Days
    chill_hours: number
    frost_risk: boolean
    heat_stress_risk: boolean
    spray_conditions: "favorable" | "marginal" | "unfavorable"

GET /api/v1/weather/alerts:
  query: { lat: number, lon: number }
  response: { data: WeatherAlert[] }

GET /api/v1/weather/history:
  query: { lat: number, lon: number, start_date: string, end_date: string }
  response: { data: [{ date: string, temp_min: number, temp_max: number, precipitation: number }] }
```

---

### 17. advisory-service

| Property | Value |
|----------|-------|
| **Upstream** | `advisory-service:8093` |
| **Kong Paths** | `/api/v1/advice`, `/api/v1/advisory`, `/api/v1/agro-advisor` (legacy) |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 100/min |

#### Endpoints

```yaml
POST /api/v1/advisory/recommendations:
  body: { field_id: string, crop_type: string, issue_type?: string }
  response:
    recommendations: [{ title: string, description: string, priority: "low"|"medium"|"high" }]
    sources: [{ title: string, url: string }]

GET /api/v1/advisory/crop-calendar:
  query: { crop_type: string, region?: string }
  response: { stages: [{ stage: string, start_month: number, end_month: number, activities: string[] }] }

POST /api/v1/advisory/fertilizer:
  body: { field_id: string, crop_type: string, soil_data?: object }
  response:
    plan: [{ nutrient: string, amount_kg_ha: number, timing: string, product: string }]

GET /api/v1/advisory/pest-management:
  query: { crop_type: string, pest?: string }
  response: { data: PestManagementPlan[] }
```

---

### 18. irrigation-smart

| Property | Value |
|----------|-------|
| **Upstream** | `irrigation-smart:8094` |
| **Kong Paths** | `/api/v1/irrigation` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/irrigation/schedule/:field_id:
  response:
    field_id: string
    schedule: [{ zone: string, start_time: string, duration_min: number, volume_liters: number }]
    water_balance: { et0: number, rainfall: number, deficit: number }

POST /api/v1/irrigation/calculate:
  body: { field_id: string, crop_type: string, soil_type?: string }
  response: { recommended_mm: number, frequency: string, method: string }

GET /api/v1/irrigation/history/:field_id:
  query: { from?: string, to?: string }
  response: { data: IrrigationEvent[] }

POST /api/v1/irrigation/start:
  body: { field_id: string, zone?: string, duration_min: number }
  response: { success: boolean, event_id: string }

POST /api/v1/irrigation/stop:
  body: { field_id: string, zone?: string }
  response: { success: boolean }
```

---

### 19. crop-intelligence-service

| Property | Value |
|----------|-------|
| **Upstream** | `crop-intelligence-service:8095` |
| **Kong Paths** | `/api/v1/crop-health`, `/api/v1/crop-intelligence` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min |
| **Read Timeout** | 120s |
| **Max Payload** | 25 MB |

#### Endpoints

```yaml
POST /api/v1/crop-health/diagnose:
  body: FormData { image: File, field_id?: string }
  response:
    diagnosis:
      disease: string | null
      confidence: number
      severity: "low" | "medium" | "high"
    recommendations: string[]

GET /api/v1/crop-health/growth-stage/:field_id:
  response:
    current_stage: string
    days_since_planting: number
    estimated_harvest_date: string

GET /api/v1/crop-intelligence/analysis/:field_id:
  response:
    health_score: number
    stress_indicators: string[]
    growth_rate: number
    predicted_yield: number

GET /api/v1/crop-health/diagnoses:
  query: { page?, limit?, field_id?, status? }
  response: { data: Diagnosis[], meta: Pagination }

PATCH /api/v1/crop-health/diagnoses/:id/status:
  body: { status: "confirmed" | "rejected", expert_notes?: string }
  response: Diagnosis
```

---

### 20. virtual-sensors

| Property | Value |
|----------|-------|
| **Upstream** | `virtual-sensors:8119` |
| **Kong Paths** | `/api/v1/sensors/virtual` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/sensors/virtual/:field_id:
  response:
    field_id: string
    et0: number              # Reference evapotranspiration
    soil_moisture: number
    canopy_temperature: number
    leaf_wetness: boolean
    timestamp: string

GET /api/v1/sensors/virtual/:field_id/history:
  query: { from: string, to: string, metric?: string }
  response: { data: [{ timestamp: string, values: object }] }

POST /api/v1/sensors/virtual/calibrate:
  body: { field_id: string, ground_truth: object }
  response: { success: boolean, accuracy: number }
```

---

### 21. yield-prediction-service

| Property | Value |
|----------|-------|
| **Upstream** | `yield-prediction-service:8152` |
| **Kong Paths** | `/api/v1/yield` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
POST /api/v1/yield/predict:
  body: { field_id: string, crop_type: string, season?: string }
  response:
    predicted_yield_tons_ha: number
    confidence_interval: { low: number, high: number }
    factors: [{ factor: string, impact: "positive"|"negative", weight: number }]

GET /api/v1/yield/history/:field_id:
  query: { seasons?: number }
  response: { data: [{ season: string, actual: number, predicted: number }] }

GET /api/v1/yield/benchmarks:
  query: { crop_type: string, region?: string }
  response: { average: number, top_quartile: number, data: YieldBenchmark[] }
```

---

### 22. field-chat

| Property | Value |
|----------|-------|
| **Upstream** | `chat-service:8115` |
| **Kong Paths** | `/api/v1/field/chat`, `/api/v1/field-chat` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 2000/min |

#### Endpoints

```yaml
GET /api/v1/field-chat/:field_id/messages:
  query: { page?, limit? }
  response: { data: FieldMessage[], meta: Pagination }

POST /api/v1/field-chat/:field_id/messages:
  body: { content: string, attachments?: string[], type?: "text"|"image"|"location" }
  response: FieldMessage

GET /api/v1/field-chat/:field_id/participants:
  response: { data: Participant[] }

POST /api/v1/field-chat/:field_id/invite:
  body: { user_ids: string[] }
  response: { success: boolean }
```

---

### 23. equipment-service

| Property | Value |
|----------|-------|
| **Upstream** | `equipment-service:8101` |
| **Kong Paths** | `/api/v1/equipment` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/equipment:
  query: { page?, limit?, type?, status?, field_id? }
  response: { data: Equipment[], meta: Pagination }

POST /api/v1/equipment:
  body: { name: string, type: string, model?: string, serial_number?: string }
  response: Equipment

GET /api/v1/equipment/:id:
  response: Equipment

PUT /api/v1/equipment/:id:
  body: { name?, status?, assigned_field_id?, maintenance_date? }
  response: Equipment

DELETE /api/v1/equipment/:id:
  response: { success: boolean }

GET /api/v1/equipment/:id/maintenance:
  response: { data: MaintenanceRecord[] }

POST /api/v1/equipment/:id/maintenance:
  body: { type: string, description: string, cost?: number, date: string }
  response: MaintenanceRecord
```

---

### 24. task-service

| Property | Value |
|----------|-------|
| **Upstream** | `task-service:8103` |
| **Kong Paths** | `/api/v1/tasks` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/tasks:
  query: { page?, limit?, status?, priority?, field_id?, assignee_id? }
  response: { data: Task[], meta: Pagination }

POST /api/v1/tasks:
  body: { title: string, description?: string, field_id?: string, assignee_id?: string, priority?: "low"|"medium"|"high", due_date?: string }
  response: Task

GET /api/v1/tasks/:id:
  response: Task

PUT /api/v1/tasks/:id:
  body: { title?, description?, priority?, due_date?, assignee_id? }
  response: Task

PATCH /api/v1/tasks/:id/status:
  body: { status: "todo" | "in_progress" | "review" | "done" }
  response: Task

DELETE /api/v1/tasks/:id:
  response: { success: boolean }

GET /api/v1/tasks/summary:
  response: { todo: number, in_progress: number, review: number, done: number }

POST /api/v1/tasks/:id/comments:
  body: { content: string }
  response: Comment
```

---

### 25. provider-config

| Property | Value |
|----------|-------|
| **Upstream** | `provider-config:8104` |
| **Kong Paths** | `/api/v1/providers` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 500/min |

#### Endpoints

```yaml
GET /api/v1/providers:
  response: { data: Provider[] }

GET /api/v1/providers/:id:
  response: Provider

PUT /api/v1/providers/:id:
  body: { config: object, enabled: boolean }
  response: Provider

GET /api/v1/providers/categories:
  response: { data: ["weather", "satellite", "payment", "sms", "email", "ai"] }

POST /api/v1/providers/test:
  body: { provider_id: string }
  response: { success: boolean, latency_ms: number }
```

---

### 26. agro-advisor

| Property | Value |
|----------|-------|
| **Status** | **DEPRECATED** — Replaced by `advisory-service` |
| **Internal Port** | `8105` |
| **Kong Path** | `/api/v1/agro-advisor` (legacy compatibility via advisory-service route) |

> [!WARNING]
> Deprecated in v16.0.0. All requests to `/api/v1/agro-advisor` are forwarded to `advisory-service:8093`. Will be removed in v17.0.0. Use `advisory-service` endpoints instead.

---

### 27. iot-gateway

| Property | Value |
|----------|-------|
| **Upstream** | `iot-gateway:8106` |
| **Kong Paths** | `/api/v1/iot`, `/api/v1/agro-rules` |
| **ACL** | enterprise |
| **Rate Limit** | 10000/min |
| **IP Restriction** | Private networks only (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) |

#### Endpoints

```yaml
GET /api/v1/iot/devices:
  query: { page?, limit?, type?, status? }
  response: { data: GatewayDevice[], meta: Pagination }

POST /api/v1/iot/devices/register:
  body: { device_id: string, type: string, firmware_version: string }
  response: GatewayDevice

GET /api/v1/iot/telemetry/:device_id:
  query: { from?: string, to?: string }
  response: { data: TelemetryPoint[] }

POST /api/v1/iot/commands:
  body: { device_id: string, command: string, params?: object }
  response: { command_id: string, status: "queued" }

GET /api/v1/agro-rules:
  response: { data: AgroRule[] }

POST /api/v1/agro-rules:
  body: { name: string, condition: object, action: object, enabled: boolean }
  response: AgroRule

PUT /api/v1/agro-rules/:id:
  body: { name?, condition?, action?, enabled? }
  response: AgroRule

DELETE /api/v1/agro-rules/:id:
  response: { success: boolean }
```

---

### 28. weather-core

| Property | Value |
|----------|-------|
| **Status** | **DEPRECATED** — Replaced by `weather-service` |
| **Internal Port** | `8108` |

> [!WARNING]
> Deprecated in v16.0.0. Will be removed in v17.0.0. Use `weather-service` (port 8092) instead.

---

### 29. notification-service

| Property | Value |
|----------|-------|
| **Upstream** | `notification-service:8110` |
| **Kong Paths** | `/api/v1/notifications` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 100/min |

#### Endpoints

```yaml
GET /api/v1/notifications:
  query: { page?, limit?, read?: boolean, type?: string }
  response:
    data: Notification[]
    meta: Pagination
    unread_count: number

POST /api/v1/notifications/send:
  body:
    user_id: string
    channel: "push" | "sms" | "email" | "whatsapp"
    title: string
    body: string
    data?: object
  response: { notification_id: string, status: "sent" | "queued" }

PATCH /api/v1/notifications/:id/read:
  response: { success: boolean }

POST /api/v1/notifications/mark-all-read:
  response: { success: boolean, count: number }

GET /api/v1/notifications/preferences:
  response: { channels: { push: boolean, sms: boolean, email: boolean, whatsapp: boolean } }

PUT /api/v1/notifications/preferences:
  body: { push?: boolean, sms?: boolean, email?: boolean, whatsapp?: boolean }
  response: { success: boolean }
```

---

### 30. astronomical-calendar

| Property | Value |
|----------|-------|
| **Upstream** | `astronomical-calendar:8111` |
| **Kong Paths** | `/api/v1/astronomical`, `/api/v1/calendar` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 100/min |

#### Endpoints

```yaml
GET /api/v1/astronomical/today:
  query: { lat?: number, lon?: number }
  response:
    hijri_date: string
    star_season: string    # Yemeni agricultural star calendar
    planting_guidance: string
    sunrise: string
    sunset: string
    moon_phase: string

GET /api/v1/astronomical/season:
  query: { date?: string }
  response:
    season_name: string
    season_start: string
    season_end: string
    recommended_crops: string[]
    weather_pattern: string

GET /api/v1/calendar/events:
  query: { month?: number, year?: number }
  response: { data: CalendarEvent[] }
```

---

### 31. alert-service

| Property | Value |
|----------|-------|
| **Upstream** | `alert-service:8113` |
| **Kong Paths** | `/api/v1/alerts` |
| **ACL** | starter, professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/alerts:
  query: { page?, limit?, severity?, type?, acknowledged?: boolean, field_id? }
  response: { data: Alert[], meta: Pagination }

POST /api/v1/alerts:
  body: { type: string, severity: "info"|"warning"|"critical", title: string, message: string, field_id?: string }
  response: Alert

GET /api/v1/alerts/:id:
  response: Alert

PATCH /api/v1/alerts/:id/acknowledge:
  response: { success: boolean }

DELETE /api/v1/alerts/:id:
  response: { success: boolean }

GET /api/v1/alerts/rules:
  response: { data: AlertRule[] }

POST /api/v1/alerts/rules:
  body: { name: string, condition: object, severity: string, channels: string[] }
  response: AlertRule
```

---

### 32. inventory-service

| Property | Value |
|----------|-------|
| **Upstream** | `inventory-service:8116` |
| **Kong Paths** | `/api/v1/inventory` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/inventory:
  query: { page?, limit?, category?, search?, low_stock?: boolean }
  response: { data: InventoryItem[], meta: Pagination }

POST /api/v1/inventory:
  body: { name: string, category: string, quantity: number, unit: string, min_threshold?: number }
  response: InventoryItem

GET /api/v1/inventory/:id:
  response: InventoryItem

PUT /api/v1/inventory/:id:
  body: { name?, quantity?, unit?, min_threshold? }
  response: InventoryItem

DELETE /api/v1/inventory/:id:
  response: { success: boolean }

POST /api/v1/inventory/:id/adjust:
  body: { adjustment: number, reason: string }
  response: InventoryItem

GET /api/v1/inventory/summary:
  response: { total_items: number, low_stock_count: number, categories: object }
```

---

### 33. field-intelligence

| Property | Value |
|----------|-------|
| **Upstream** | `field-intelligence:8120` |
| **Kong Paths** | `/api/v1/field-intelligence`, `/api/v1/intelligence` |
| **ACL** | professional, enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/field-intelligence/:field_id:
  response:
    field_id: string
    health_score: number
    risk_assessment: { drought: number, pest: number, disease: number }
    recommendations: string[]
    insights: [{ type: string, message: string, confidence: number }]

GET /api/v1/field-intelligence/:field_id/timeline:
  query: { period?: "30d" | "90d" | "1y" }
  response: { data: [{ date: string, health_score: number, events: string[] }] }

POST /api/v1/field-intelligence/compare:
  body: { field_ids: string[] }
  response: { comparison: FieldComparison[] }
```

---

### 34. mcp-server

| Property | Value |
|----------|-------|
| **Upstream** | `mcp-server:8200` |
| **Kong Paths** | `/api/v1/mcp` |
| **ACL** | professional, enterprise, research |
| **Rate Limit** | 1000/min, 50000/hr |

#### Endpoints

```yaml
GET /api/v1/mcp/tools:
  response: { tools: [{ name: string, description: string, parameters: object }] }

POST /api/v1/mcp/execute:
  body: { tool: string, arguments: object }
  response: { result: any, execution_time_ms: number }

GET /api/v1/mcp/resources:
  response: { resources: [{ uri: string, name: string, type: string }] }

GET /api/v1/mcp/resources/:uri:
  response: { content: any, mime_type: string }
```

---

### 35. crm-service

| Property | Value |
|----------|-------|
| **Upstream** | `crm-service:8131` |
| **Kong Paths** | `/api/v1/crm` |
| **ACL** | enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/crm/contacts:
  query: { page?, limit?, type?, search? }
  response: { data: Contact[], meta: Pagination }

POST /api/v1/crm/contacts:
  body: { name: string, email?: string, phone?: string, type: "farmer"|"supplier"|"buyer", notes?: string }
  response: Contact

GET /api/v1/crm/contacts/:id:
  response: Contact

PUT /api/v1/crm/contacts/:id:
  body: { name?, email?, phone?, type?, notes? }
  response: Contact

DELETE /api/v1/crm/contacts/:id:
  response: { success: boolean }

GET /api/v1/crm/interactions:
  query: { contact_id?: string, page?, limit? }
  response: { data: Interaction[], meta: Pagination }

POST /api/v1/crm/interactions:
  body: { contact_id: string, type: "call"|"email"|"meeting"|"note", summary: string }
  response: Interaction

GET /api/v1/crm/dashboard:
  response: { total_contacts: number, recent_interactions: number, by_type: object }
```

---

### 36. lowcode-engine

| Property | Value |
|----------|-------|
| **Upstream** | `lowcode-engine:8132` |
| **Kong Paths** | `/api/v1/lowcode` |
| **ACL** | enterprise |
| **Rate Limit** | 1000/min |

#### Endpoints

```yaml
GET /api/v1/lowcode/apps:
  query: { page?, limit? }
  response: { data: LowCodeApp[], meta: Pagination }

POST /api/v1/lowcode/apps:
  body: { name: string, description?: string, schema: object }
  response: LowCodeApp

GET /api/v1/lowcode/apps/:id:
  response: LowCodeApp

PUT /api/v1/lowcode/apps/:id:
  body: { name?, description?, schema?, published? }
  response: LowCodeApp

DELETE /api/v1/lowcode/apps/:id:
  response: { success: boolean }

POST /api/v1/lowcode/apps/:id/execute:
  body: { input: object }
  response: { output: any, logs: string[] }

GET /api/v1/lowcode/templates:
  response: { data: Template[] }
```

---

### 37. ai-agents-service

| Property | Value |
|----------|-------|
| **Upstream** | `ai-agents-core:8161` |
| **Kong Paths** | `/api/v1/ai-agents`, `/api/v1/orchestration` |
| **ACL** | enterprise, research |
| **Rate Limit** | 5000/min, 250000/hr |
| **Read Timeout** | 180s |
| **Max Payload** | 50 MB |

#### Endpoints

```yaml
GET /api/v1/ai-agents:
  query: { page?, limit?, status? }
  response: { data: AIAgent[], meta: Pagination }

POST /api/v1/ai-agents/execute:
  body: { agent_id: string, task: string, context?: object, tools?: string[] }
  response:
    execution_id: string
    status: "running" | "completed" | "failed"
    result?: any
    steps?: [{ tool: string, input: object, output: any }]

GET /api/v1/ai-agents/executions/:id:
  response: AgentExecution

GET /api/v1/ai-agents/executions/:id/stream:
  response: text/event-stream  # SSE for real-time updates

POST /api/v1/orchestration/workflow:
  body: { name: string, agents: [{ agent_id: string, task: string }], strategy: "sequential"|"parallel" }
  response: { workflow_id: string, status: "queued" }

GET /api/v1/orchestration/workflow/:id:
  response: WorkflowExecution
```

---

### 38. agro-rules

| Property | Value |
|----------|-------|
| **Status** | Accessed via `iot-gateway` route `/api/v1/agro-rules` |
| **See** | [iot-gateway](#27-iot-gateway) |

> [!NOTE]
> `agro-rules` is not a standalone service in Kong. It shares the `iot-gateway` upstream. All agro-rules endpoints are documented under [iot-gateway](#27-iot-gateway).

---

## Common Types Reference

```typescript
interface Pagination {
  total: number;
  page: number;
  limit: number;
  total_pages?: number;
}

interface GeoJSON_Polygon {
  type: "Polygon";
  coordinates: [number, number][][];
}

// Standard error response (all services)
interface ErrorResponse {
  statusCode: number;
  message: string;
  error?: string;
  details?: object;
}

// Standard paginated query params (all list endpoints)
interface PaginationQuery {
  page?: number;   // default: 1
  limit?: number;  // default: 20, max: 100
  sort?: string;   // field name
  order?: "asc" | "desc";
}
```

---

## Authentication Flow

```
1. POST /api/v1/auth/login → { access_token, refresh_token }
2. All requests: Authorization: Bearer <access_token>
3. On 401: POST /api/v1/auth/refresh → { new access_token }
4. On refresh fail: Redirect to login
```

## ACL Groups

| Group | Access Level |
|-------|-------------|
| `starter-users` | Basic field management, weather, notifications, tasks |
| `professional-users` | + Satellite, NDVI, irrigation, sensors, AI crop health, equipment |
| `enterprise-users` | + Marketplace, IoT, billing, research, AI advisor, agents |
| `research-users` | + Research core, AI agents, compliance |
| `admin-users` | Full platform access, user management, audit logs |
