# CRM Service Analysis

**Comprehensive Microservice Analysis for SAHOOL Platform**

| Property | Value |
|----------|-------|
| **Service Name** | crm-service |
| **Arabic Name** | خدمة إدارة علاقات المزارعين |
| **Version** | 16.0.0 |
| **Port** | 8131 |
| **Framework** | FastAPI (Python) |
| **Type** | Business Layer Service |
| **License** | Proprietary - KAFAAT |
| **Last Analyzed** | 2026-01-25 |

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Request/Response Schemas](#requestresponse-schemas)
- [NATS Events](#nats-events)
- [CRM Features](#crm-features)
- [Database Schema](#database-schema)
- [Dependencies](#dependencies)
- [Environment Variables](#environment-variables)
- [Security Features](#security-features)
- [Bugs and Issues](#bugs-and-issues)
- [Recommendations](#recommendations)

---

## Overview

The CRM Service provides comprehensive **Farmer Customer Relationship Management** capabilities for the SAHOOL agricultural platform. Inspired by CordysCRM's AI-powered architecture, this service adapts traditional CRM concepts for agricultural contexts.

### Key Features

1. **Farmer Lifecycle Management**: Lead to Premium customer journey
2. **Harvest Deal Pipeline**: Agricultural sales opportunity management
3. **Interaction Tracking**: All farmer communications with sentiment analysis
4. **Natural Language Queries (SQLBot-inspired)**: Query data in Arabic/English
5. **Engagement Scoring**: Automatic farmer engagement calculation (0-100)
6. **Pipeline Analytics**: Deal conversion rates and value tracking

### Kong Gateway Configuration

```yaml
Host: crm-service
Port: 8131
Routes:
  - /api/v1/crm (strip_path: true)
  - /crm (strip_path: true)
```

---

## Architecture

```
+----------------------------------------------------------+
|                    API Gateway (Kong)                     |
|                   Port: 8000 (Rate Limited)               |
+----------------------------------------------------------+
                              |
                              v
+----------------------------------------------------------+
|                CRM Service (FastAPI)                      |
|                     Port: 8131                            |
+----------------------------------------------------------+
|  +-------------+  +-------------+  +-------------------+  |
|  |   Farmers   |  |    Deals    |  |   Interactions    |  |
|  |    CRUD     |  |   Pipeline  |  |     Logging       |  |
|  +-------------+  +-------------+  +-------------------+  |
|  +-------------+  +-----------------------------------+   |
|  |   Query     |  |       Pipeline Analytics          |   |
|  |    Bot      |  |   (Conversion, Value, Stats)      |   |
|  +-------------+  +-----------------------------------+   |
+----------------------------------------------------------+
         |                    |                    |
         v                    v                    v
+-------------+      +-------------+      +-------------+
|  PostgreSQL |      |    NATS     |      |    Redis    |
|   Database  |      |  Messaging  |      |   Caching   |
+-------------+      +-------------+      +-------------+
```

### Data Flow

1. **Request Flow**: Kong -> FastAPI -> Auth Validation -> Tenant Validation -> Business Logic
2. **Event Flow**: API Endpoint -> Business Logic -> NATS Publish -> Event Consumers
3. **Cache Flow**: Request -> Redis Check -> DB Query (if miss) -> Redis Set -> Response

---

## API Endpoints

### Health Endpoints

| Method | Endpoint | Description | Rate Limit | Auth |
|--------|----------|-------------|------------|------|
| `GET` | `/healthz` | Liveness probe | None | No |
| `GET` | `/readyz` | Readiness probe (DB, NATS, Redis status) | None | No |
| `GET` | `/health` | Detailed health with farmer/deal counts | None | No |
| `GET` | `/metrics` | Prometheus-compatible metrics | None | No |

### Farmers API

| Method | Endpoint | Description | Rate Limit | Auth |
|--------|----------|-------------|------------|------|
| `POST` | `/api/v1/farmers` | Create new farmer | 30/min | Yes |
| `GET` | `/api/v1/farmers` | List farmers (paginated, filterable) | 60/min | Yes |
| `GET` | `/api/v1/farmers/{farmer_id}` | Get farmer by ID | 60/min | Yes |
| `PATCH` | `/api/v1/farmers/{farmer_id}` | Update farmer details | 60/min | Yes |

**Query Parameters for GET /api/v1/farmers:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tenant_id` | string | Yes | - | Tenant identifier for isolation |
| `status` | string | No | - | Filter by status (lead, registered, active, premium, churned) |
| `search` | string | No | - | Search by name, Arabic name, or phone |
| `limit` | int | No | 50 | Max results (1-200) |
| `offset` | int | No | 0 | Pagination offset |

### Deals API

| Method | Endpoint | Description | Rate Limit | Auth |
|--------|----------|-------------|------------|------|
| `POST` | `/api/v1/deals` | Create harvest deal | 30/min | Yes |
| `GET` | `/api/v1/deals` | List deals | 60/min | Yes |
| `PATCH` | `/api/v1/deals/{deal_id}/stage` | Update deal stage | 60/min | Yes |
| `GET` | `/api/v1/deals/pipeline` | Get pipeline statistics | 60/min | Yes |

**Query Parameters for GET /api/v1/deals:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tenant_id` | string | Yes | - | Tenant identifier |
| `farmer_id` | string | No | - | Filter by farmer |
| `stage` | string | No | - | Filter by pipeline stage |
| `limit` | int | No | 50 | Max results (1-200) |

### Interactions API

| Method | Endpoint | Description | Rate Limit | Auth |
|--------|----------|-------------|------------|------|
| `POST` | `/api/v1/interactions` | Log farmer interaction | 60/min | Yes |
| `GET` | `/api/v1/interactions` | List interactions by farmer | 60/min | Yes |

**Query Parameters for GET /api/v1/interactions:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `farmer_id` | string | Yes | - | Farmer identifier |
| `interaction_type` | string | No | - | Filter by type (call, visit, whatsapp, sms, email) |
| `limit` | int | No | 50 | Max results (1-200) |

### Query API (Natural Language)

| Method | Endpoint | Description | Rate Limit | Auth |
|--------|----------|-------------|------------|------|
| `POST` | `/api/v1/query` | Natural language query | 10/min | Yes |

---

## Request/Response Schemas

### FarmerCreateRequest

```json
{
  "name": "string (required, 2-100 chars)",
  "name_ar": "string | null (max 100 chars)",
  "phone": "string (required, pattern: ^\\+?[0-9]{10,15}$)",
  "email": "string | null (valid email)",
  "national_id": "string | null",
  "farm_location": "string | null",
  "farm_location_ar": "string | null",
  "farm_size_hectares": "float | null (>= 0)",
  "primary_crops": "string[] (default: [])",
  "tenant_id": "string (required)"
}
```

### FarmerResponse

```json
{
  "id": "string (UUID)",
  "name": "string",
  "name_ar": "string | null",
  "phone": "string",
  "email": "string | null",
  "national_id": "string | null",
  "farm_location": "string | null",
  "farm_location_ar": "string | null",
  "farm_size_hectares": "float | null",
  "primary_crops": "string[]",
  "status": "string (lead|registered|active|premium|churned)",
  "tags": "string[]",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)",
  "last_interaction_at": "datetime | null"
}
```

### FarmerUpdateRequest

```json
{
  "name": "string | null (2-100 chars)",
  "name_ar": "string | null (max 100 chars)",
  "phone": "string | null (pattern: ^\\+?[0-9]{10,15}$)",
  "email": "string | null (valid email)",
  "farm_location": "string | null",
  "farm_location_ar": "string | null",
  "farm_size_hectares": "float | null (>= 0)",
  "primary_crops": "string[] | null",
  "status": "string | null",
  "tags": "string[] | null"
}
```

### HarvestDealCreateRequest

```json
{
  "farmer_id": "string (required)",
  "crop_type": "string (required)",
  "crop_type_ar": "string | null",
  "expected_quantity_tons": "float (required, > 0)",
  "expected_harvest_date": "date (required, YYYY-MM-DD)",
  "price_per_ton": "float | null (> 0)",
  "notes": "string | null",
  "notes_ar": "string | null"
}
```

### HarvestDealResponse

```json
{
  "id": "string (UUID)",
  "farmer_id": "string",
  "crop_type": "string",
  "crop_type_ar": "string | null",
  "expected_quantity_tons": "float",
  "actual_quantity_tons": "float | null",
  "expected_harvest_date": "date",
  "actual_harvest_date": "date | null",
  "price_per_ton": "float | null",
  "total_value": "float | null (computed)",
  "stage": "string",
  "notes": "string | null",
  "notes_ar": "string | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### InteractionCreateRequest

```json
{
  "farmer_id": "string (required)",
  "interaction_type": "string (required: call|visit|whatsapp|sms|email|advisory|support)",
  "subject": "string (required)",
  "subject_ar": "string | null",
  "notes": "string | null",
  "notes_ar": "string | null",
  "outcome": "string | null",
  "follow_up_date": "date | null (YYYY-MM-DD)"
}
```

### InteractionResponse

```json
{
  "id": "string (UUID)",
  "farmer_id": "string",
  "interaction_type": "string",
  "subject": "string",
  "subject_ar": "string | null",
  "notes": "string | null",
  "notes_ar": "string | null",
  "outcome": "string | null",
  "follow_up_date": "date | null",
  "created_at": "datetime",
  "created_by": "string | null"
}
```

### QueryRequest

```json
{
  "query": "string (required, max 500 chars)",
  "tenant_id": "string (required)"
}
```

### QueryResponse

```json
{
  "query": "string",
  "interpreted_as": "string (SQL-like interpretation)",
  "interpreted_as_ar": "string | null",
  "results": "object[]",
  "result_count": "int",
  "execution_time_ms": "int"
}
```

### PipelineStatsResponse

```json
{
  "total_deals": "int",
  "total_value": "float",
  "by_stage": {
    "prospecting": { "count": "int", "total_value": "float", "name_ar": "string" },
    "qualification": { "count": "int", "total_value": "float", "name_ar": "string" },
    "negotiation": { "count": "int", "total_value": "float", "name_ar": "string" },
    "contracted": { "count": "int", "total_value": "float", "name_ar": "string" },
    "delivered": { "count": "int", "total_value": "float", "name_ar": "string" },
    "paid": { "count": "int", "total_value": "float", "name_ar": "string" },
    "closed_lost": { "count": "int", "total_value": "float", "name_ar": "string" }
  },
  "conversion_rate": "float (percentage)",
  "average_deal_size": "float"
}
```

### ErrorResponse

```json
{
  "error": "string",
  "error_ar": "string | null",
  "error_code": "string (BAD_REQUEST|UNAUTHORIZED|FORBIDDEN|NOT_FOUND|CONFLICT|RATE_LIMIT_EXCEEDED|INTERNAL_ERROR|SERVICE_UNAVAILABLE)",
  "detail": "string | null",
  "request_id": "string | null (UUID)"
}
```

---

## NATS Events

### Published Events

The service publishes events to NATS using the subject pattern: `sahool.{tenant_id}.crm.{entity}.{action}`

| Event Subject | Event Type | Payload Fields | Trigger |
|---------------|------------|----------------|---------|
| `sahool.{tenant_id}.crm.farmer.created` | `farmer.created` | farmer_id, tenant_id, name, name_ar, phone, status, timestamp | POST /api/v1/farmers |
| `sahool.{tenant_id}.crm.farmer.updated` | `farmer.updated` | farmer_id, tenant_id, name, name_ar, status, timestamp | PATCH /api/v1/farmers/{id} |
| `sahool.{tenant_id}.crm.farmer.status_changed` | `farmer.status_changed` | farmer_id, tenant_id, old_status, new_status, timestamp | PATCH /api/v1/farmers/{id} (when status changes) |
| `sahool.{tenant_id}.crm.deal.created` | `deal.created` | deal_id, farmer_id, tenant_id, crop_type, crop_type_ar, expected_quantity_tons, expected_harvest_date, price_per_ton, stage, timestamp | POST /api/v1/deals |
| `sahool.{tenant_id}.crm.deal.stage_advanced` | `deal.stage_advanced` | deal_id, farmer_id, tenant_id, crop_type, old_stage, new_stage, expected_quantity_tons, timestamp | PATCH /api/v1/deals/{id}/stage |
| `sahool.{tenant_id}.crm.interaction.logged` | `interaction.logged` | interaction_id, farmer_id, tenant_id, interaction_type, subject, subject_ar, outcome, follow_up_date, timestamp | POST /api/v1/interactions |

### Event Payload Examples

**farmer.created:**
```json
{
  "event_type": "farmer.created",
  "farmer_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "sahool-tenant",
  "name": "Ahmed Mohammed",
  "name_ar": "أحمد محمد",
  "phone": "+966501234567",
  "status": "lead",
  "timestamp": "2026-01-25T10:30:00Z"
}
```

**deal.stage_advanced:**
```json
{
  "event_type": "deal.stage_advanced",
  "deal_id": "660e8400-e29b-41d4-a716-446655440001",
  "farmer_id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "sahool-tenant",
  "crop_type": "wheat",
  "old_stage": "prospecting",
  "new_stage": "negotiation",
  "expected_quantity_tons": 50.0,
  "timestamp": "2026-01-25T11:00:00Z"
}
```

### Subscribed Events

**Currently None** - The service does not subscribe to any NATS events. It only publishes events.

---

## CRM Features

### 1. Farmer Status Lifecycle

| Status | Arabic | Description | Use Case |
|--------|--------|-------------|----------|
| `lead` | مهتم | Initial contact, potential farmer | New signup, inquiry |
| `registered` | مسجل | Completed registration | Account created |
| `active` | نشط | Actively using platform | Regular engagement |
| `premium` | مميز | Premium subscriber | Paid subscription |
| `churned` | متوقف | Stopped using platform | Inactive > 90 days |

### 2. Harvest Deal Pipeline Stages

| Stage | Arabic | Probability | Description |
|-------|--------|-------------|-------------|
| `prospecting` | استكشاف | 10% | Identifying harvest opportunity |
| `qualification` | تأهيل | 25% | Assessing crop quality and viability |
| `negotiation` | تفاوض | 50% | Price and terms discussion |
| `contracted` | متعاقد | 75% | Supply agreement signed |
| `delivered` | مسلم | 90% | Crop delivered to buyer |
| `paid` | مدفوع | 100% | Payment received (Won) |
| `closed_lost` | خسارة | 0% | Deal fell through |

### 3. Interaction Types

| Type | Arabic | Description |
|------|--------|-------------|
| `call` | مكالمة | Phone call |
| `visit` | زيارة | Field visit |
| `whatsapp` | واتساب | WhatsApp message |
| `sms` | رسالة نصية | SMS message |
| `email` | بريد إلكتروني | Email communication |
| `advisory` | استشارة | Advisory session |
| `support` | دعم فني | Technical support |
| `sales` | مبيعات | Sales communication |
| `training` | تدريب | Training session |
| `inspection` | فحص ميداني | Field inspection |

### 4. Natural Language Query (NLQ) Patterns

**Supported Query Patterns:**

| Query Type | English Examples | Arabic Examples |
|------------|------------------|-----------------|
| Active Farmers | "Show me all active farmers", "active farmers" | "أرني جميع المزارعين النشطين", "نشط" |
| Lead Farmers | "Show me lead farmers", "leads" | "المزارعين المحتملين", "محتمل" |
| All Farmers | "Show all farmers", "list farmers" | "جميع المزارعين", "مزارع" |
| Deals | "Show me all deals", "deals" | "جميع الصفقات", "صفقة" |
| Negotiation Deals | "deals in negotiation" | "صفقات في مرحلة التفاوض", "تفاوض" |

### 5. Engagement Scoring (0-100)

| Component | Max Points | Criteria |
|-----------|------------|----------|
| Recency | 30 | Last interaction: <=7 days (30), <=30 days (20), <=90 days (10) |
| Interactions | 25 | 5 points per interaction (max 25) |
| Active Deals | 25 | 10 points per active deal (max 25) |
| Profile Completeness | 20 | Email (+5), Coordinates (+5), Crops (+5), Area (+5) |

---

## Database Schema

### Tables

#### farmers

```sql
CREATE TABLE farmers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,

    -- Basic Information
    name VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    national_id VARCHAR(50),

    -- Farm Details
    farm_size_hectares DECIMAL(10, 2),
    location VARCHAR(255),
    location_ar VARCHAR(255),
    crops JSONB DEFAULT '[]'::jsonb,

    -- CRM Fields
    status VARCHAR(50) NOT NULL DEFAULT 'lead',
    engagement_score DECIMAL(5, 2) DEFAULT 0.0,
    tags JSONB DEFAULT '[]'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_interaction_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_farmer_status CHECK (
        status IN ('lead', 'registered', 'active', 'premium', 'churned')
    ),
    CONSTRAINT chk_engagement_score CHECK (
        engagement_score >= 0 AND engagement_score <= 100
    )
);
```

#### harvest_deals

```sql
CREATE TABLE harvest_deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,

    -- Deal Details
    crop_type VARCHAR(100) NOT NULL,
    crop_type_ar VARCHAR(100),
    quantity_tons DECIMAL(10, 2) NOT NULL,
    price_per_ton DECIMAL(12, 2),
    total_value DECIMAL(14, 2) GENERATED ALWAYS AS (
        COALESCE(quantity_tons * price_per_ton, 0)
    ) STORED,

    -- Actual Values
    actual_quantity_tons DECIMAL(10, 2),
    actual_harvest_date DATE,

    -- Timing
    expected_harvest_date DATE,

    -- Pipeline Stage
    stage VARCHAR(50) NOT NULL DEFAULT 'prospecting',
    probability DECIMAL(3, 2) DEFAULT 0.1,

    -- Notes
    notes TEXT,
    notes_ar TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_deal_stage CHECK (
        stage IN ('prospecting', 'qualification', 'negotiation',
                  'contracted', 'delivered', 'paid', 'closed_lost')
    ),
    CONSTRAINT chk_quantity_positive CHECK (quantity_tons > 0),
    CONSTRAINT chk_price_positive CHECK (price_per_ton IS NULL OR price_per_ton > 0),
    CONSTRAINT chk_probability CHECK (probability >= 0 AND probability <= 1)
);
```

#### interactions

```sql
CREATE TABLE interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100) NOT NULL,
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,

    -- Interaction Details
    interaction_type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) DEFAULT 'app',

    -- Content
    subject VARCHAR(255) NOT NULL,
    subject_ar VARCHAR(255),
    notes TEXT,
    notes_ar TEXT,

    -- Outcome
    outcome VARCHAR(255),
    sentiment_score DECIMAL(3, 2),

    -- Follow-up
    follow_up_date DATE,
    follow_up_completed BOOLEAN DEFAULT FALSE,

    -- User who created
    created_by VARCHAR(100),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_interaction_type CHECK (
        interaction_type IN ('advisory', 'support', 'sales', 'training',
                             'inspection', 'call', 'visit', 'whatsapp', 'sms', 'email')
    ),
    CONSTRAINT chk_channel CHECK (
        channel IN ('app', 'phone', 'whatsapp', 'sms', 'email', 'in_person', 'web')
    ),
    CONSTRAINT chk_sentiment_score CHECK (
        sentiment_score IS NULL OR (sentiment_score >= -1 AND sentiment_score <= 1)
    )
);
```

### Indexes

```sql
-- farmers
CREATE INDEX idx_farmers_tenant_id ON farmers(tenant_id);
CREATE INDEX idx_farmers_status ON farmers(status);
CREATE INDEX idx_farmers_phone ON farmers(phone);
CREATE INDEX idx_farmers_email ON farmers(email) WHERE email IS NOT NULL;
CREATE INDEX idx_farmers_created_at ON farmers(created_at);
CREATE INDEX idx_farmers_tenant_status ON farmers(tenant_id, status);

-- harvest_deals
CREATE INDEX idx_harvest_deals_tenant_id ON harvest_deals(tenant_id);
CREATE INDEX idx_harvest_deals_farmer_id ON harvest_deals(farmer_id);
CREATE INDEX idx_harvest_deals_stage ON harvest_deals(stage);
CREATE INDEX idx_harvest_deals_crop_type ON harvest_deals(crop_type);
CREATE INDEX idx_harvest_deals_created_at ON harvest_deals(created_at);
CREATE INDEX idx_harvest_deals_tenant_stage ON harvest_deals(tenant_id, stage);
CREATE INDEX idx_harvest_deals_tenant_farmer ON harvest_deals(tenant_id, farmer_id);

-- interactions
CREATE INDEX idx_interactions_tenant_id ON interactions(tenant_id);
CREATE INDEX idx_interactions_farmer_id ON interactions(farmer_id);
CREATE INDEX idx_interactions_type ON interactions(interaction_type);
CREATE INDEX idx_interactions_created_at ON interactions(created_at);
CREATE INDEX idx_interactions_tenant_farmer ON interactions(tenant_id, farmer_id);
CREATE INDEX idx_interactions_follow_up ON interactions(follow_up_date)
    WHERE follow_up_date IS NOT NULL AND follow_up_completed = FALSE;
```

### Triggers

1. **update_updated_at_column**: Auto-updates `updated_at` on farmers and harvest_deals
2. **update_farmer_last_interaction**: Auto-updates farmer's `last_interaction_at` when a new interaction is created

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.126.0,<1.0.0 | Web framework |
| `uvicorn[standard]` | >=0.30.0,<1.0.0 | ASGI server |
| `pydantic` | >=2.10.0,<3.0.0 | Data validation |
| `email-validator` | >=2.2.0,<3.0.0 | Email validation for Pydantic |
| `httpx` | >=0.27.0,<1.0.0 | Async HTTP client |
| `aiofiles` | >=24.0.0,<25.0.0 | Async file operations |
| `nats-py` | >=2.9.0,<3.0.0 | NATS messaging client |
| `asyncpg` | >=0.30.0,<1.0.0 | PostgreSQL async driver |
| `structlog` | >=24.0.0,<25.0.0 | Structured logging |
| `pyjwt` | >=2.9.0,<3.0.0 | JWT token handling |
| `slowapi` | >=0.1.9,<1.0.0 | Rate limiting |
| `redis` | >=5.0.0,<6.0.0 | Redis async client for caching |

### Shared Module Dependencies

| Module | Import Path | Purpose |
|--------|-------------|---------|
| `shared.crm` | FarmerCRMService, FarmerQueryBot, Farmer, FarmerStatus, HarvestDeal, DealStage, Interaction, InteractionType | CRM domain models and services |
| `shared.auth.dependencies` | get_current_user | JWT authentication dependency |
| `shared.auth.models` | User | User model for authentication |
| `shared.events.publisher` | get_publisher | NATS event publishing |

### External Service Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| PostgreSQL | Persistent data storage | Yes (or in-memory fallback) |
| Redis | Session caching, rate limiting | Optional |
| NATS | Event publishing | Optional |
| Kong | API Gateway (rate limiting, auth) | Production |

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for JWT validation (min 32 chars) | `your-32-character-minimum-secret-key` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ENVIRONMENT` | Environment name | `development` | `development`, `staging`, `production` |
| `DATABASE_URL` | PostgreSQL connection URL | Empty (uses in-memory) | `postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require` |
| `NATS_URL` | NATS server URL | Empty (events disabled) | `nats://nats:4222` |
| `REDIS_URL` | Redis connection URL | Empty (caching disabled) | `redis://redis:6379` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000,http://localhost:8080` | `https://app.sahool.io` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | `HS256` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `HOST` | Server bind host | `0.0.0.0` | `127.0.0.1` |

### Missing Environment Variables (Identified)

| Variable | Recommended | Purpose |
|----------|-------------|---------|
| `REDIS_PASSWORD` | Yes | Redis authentication (if Redis requires auth) |
| `SENTRY_DSN` | Yes | Error tracking in production |
| `POSTGRES_SSL_MODE` | Yes | Explicit SSL mode control |
| `MAX_POOL_SIZE` | Yes | Database connection pool size control |
| `MIN_POOL_SIZE` | Yes | Database connection pool minimum |

---

## Security Features

### Authentication

- JWT-based authentication via `shared.auth.dependencies.get_current_user`
- All API endpoints (except health) require valid JWT token

### Multi-Tenancy

- Strict tenant isolation via `tenant_id` validation
- `validate_tenant_access(user, tenant_id)` checks user's tenant matches request
- Returns 403 Forbidden on tenant mismatch

### Rate Limiting (via SlowAPI)

| Endpoint Type | Rate Limit |
|---------------|------------|
| Write operations (POST) | 30/minute |
| Read operations (GET, PATCH) | 60/minute |
| NLQ queries | 10/minute |

### NLQ Security

| Feature | Implementation |
|---------|----------------|
| Query Length Limit | 500 characters max |
| Query Complexity Limit | Max 5 conditions (and/or) |
| SQL Injection Prevention | Removes DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE keywords |
| Control Character Removal | Strips characters 0x00-0x1F |
| Result Limit | Max 100 results returned |
| Audit Logging | Query hash logged for security review |

### Request Tracing

- X-Request-ID header tracking
- Auto-generated UUID if not provided
- Returned in all responses

### CORS Configuration

- Configurable via `CORS_ALLOWED_ORIGINS`
- Supports credentials
- Whitelisted methods and headers

---

## Bugs and Issues

### Critical Issues

None identified.

### Medium Severity Issues

1. **PATCH /api/v1/farmers/{farmer_id} Missing Database Support**
   - **File**: `/home/user/sahool-unified-v15-idp/apps/services/crm-service/src/main.py` (line 1141-1222)
   - **Issue**: The update_farmer endpoint only uses in-memory storage and doesn't check for `crm_repo` database support like create_farmer and list_farmers do.
   - **Impact**: When DATABASE_URL is configured, updates will modify in-memory data instead of the database.
   - **Recommended Fix**: Add database repository support similar to create_farmer endpoint.

2. **Pipeline Stats Cache Not Used in Database Mode**
   - **File**: `/home/user/sahool-unified-v15-idp/apps/services/crm-service/src/main.py` (line 1415-1478)
   - **Issue**: The `get_pipeline_stats` endpoint caches results but only uses in-memory storage, not the database repository.
   - **Impact**: Pipeline statistics won't reflect database data when DATABASE_URL is configured.
   - **Recommended Fix**: Use `crm_repo.deals.get_pipeline_stats()` when database is available.

3. **Deals Endpoints Missing Database Support**
   - **File**: `/home/user/sahool-unified-v15-idp/apps/services/crm-service/src/main.py` (line 1229-1413)
   - **Issue**: POST /deals, GET /deals, and PATCH /deals/stage only use in-memory storage.
   - **Impact**: Deals not persisted to database when DATABASE_URL is configured.
   - **Recommended Fix**: Add `crm_repo` database support for all deal operations.

4. **Interactions Endpoints Missing Database Support**
   - **File**: `/home/user/sahool-unified-v15-idp/apps/services/crm-service/src/main.py` (line 1485-1592)
   - **Issue**: POST /interactions and GET /interactions only use in-memory storage.
   - **Impact**: Interactions not persisted to database when DATABASE_URL is configured.
   - **Recommended Fix**: Add `crm_repo` database support for all interaction operations.

### Low Severity Issues

1. **Missing DELETE Endpoints**
   - **Issue**: No DELETE endpoints for farmers, deals, or interactions
   - **Impact**: Cannot delete records via API (only possible via direct database access)
   - **Recommended Fix**: Add DELETE endpoints with soft-delete capability

2. **NLQ Limited Pattern Support**
   - **File**: `/home/user/sahool-unified-v15-idp/apps/services/crm-service/src/main.py` (line 1599-1752)
   - **Issue**: Natural language query only supports basic patterns (active, lead, farmer, deal, negotiation)
   - **Impact**: Many queries return "Unknown query pattern"
   - **Recommended Fix**: Consider integrating with LLM for more intelligent query parsing

3. **Metrics Endpoint Limited**
   - **File**: `/home/user/sahool-unified-v15-idp/apps/services/crm-service/src/main.py` (line 1759-1773)
   - **Issue**: Metrics only show in-memory counts, not database totals
   - **Impact**: Prometheus metrics don't reflect actual data when using database
   - **Recommended Fix**: Query database for accurate metrics when available

4. **Redis Cache Key Collision Risk**
   - **Issue**: Cache keys use simple pattern `crm:farmer:{tenant_id}:{farmer_id}`
   - **Impact**: Potential collisions if different services use same cache keys
   - **Recommended Fix**: Add service name prefix: `crm-service:crm:farmer:{tenant_id}:{farmer_id}`

5. **Missing Pagination Metadata**
   - **Issue**: List endpoints return arrays without total count or pagination metadata
   - **Impact**: Clients cannot determine if more pages exist
   - **Recommended Fix**: Return `{ items: [], total: int, limit: int, offset: int }`

---

## Recommendations

### High Priority

1. **Complete Database Integration**
   - Implement database support for all endpoints (deals, interactions, farmer updates)
   - Follow the pattern established in `create_farmer` and `list_farmers` endpoints
   - Use the existing `CRMRepository`, `DealRepository`, and `InteractionRepository` classes

2. **Add Missing Tests for Database Mode**
   - Current tests only cover in-memory mode
   - Add integration tests with actual database connection

3. **Fix Metrics for Database Mode**
   - Query database counts when `crm_repo` is available
   - Cache database counts in Redis with short TTL (30-60 seconds)

### Medium Priority

1. **Add Pagination Metadata**
   - Modify list endpoints to return structured response with total count
   - Example: `{ "items": [], "total": 150, "limit": 50, "offset": 0, "has_more": true }`

2. **Implement Soft Delete**
   - Add `deleted_at` column to all tables
   - Implement DELETE endpoints that set `deleted_at` timestamp
   - Filter out deleted records in queries

3. **Enhance NLQ Capabilities**
   - Support more query patterns (by crop type, by date range, by location)
   - Consider LLM integration for complex queries
   - Add query history/suggestions feature

4. **Add Farmer Analytics Endpoint**
   - Endpoint: `GET /api/v1/farmers/{farmer_id}/analytics`
   - Include: engagement score, deal history, interaction summary

### Low Priority

1. **Add Bulk Operations**
   - Bulk create farmers: `POST /api/v1/farmers/bulk`
   - Bulk update status: `PATCH /api/v1/farmers/bulk/status`

2. **Add Export Functionality**
   - CSV export: `GET /api/v1/farmers/export?format=csv`
   - Excel export: `GET /api/v1/farmers/export?format=xlsx`

3. **Implement WebSocket for Real-time Updates**
   - Subscribe to farmer status changes
   - Real-time deal stage updates
   - Live pipeline statistics

4. **Add Audit Trail**
   - Log all changes to farmers, deals, interactions
   - Who changed what and when
   - Store in separate audit table

---

## Test Coverage

### Test Files

| File | Purpose |
|------|---------|
| `tests/conftest.py` | Test fixtures and mock setup |
| `tests/test_main.py` | API endpoint tests (1413 lines) |
| `tests/test_models.py` | Data model tests |
| `tests/test_query_bot.py` | NLQ tests (813 lines) |

### Test Categories

| Category | Coverage |
|----------|----------|
| Health Endpoints | Full |
| Farmer CRUD | Full (in-memory) |
| Deal Operations | Full (in-memory) |
| Interaction Logging | Full (in-memory) |
| NLQ Queries | Full |
| Security (Rate Limiting) | Partial |
| Security (Tenant Isolation) | Full |
| Database Mode | Missing |

### Running Tests

```bash
# From project root
pytest apps/services/crm-service/tests/ -v

# With coverage
pytest apps/services/crm-service/tests/ -v --cov=apps/services/crm-service/src --cov-report=html
```

---

## Docker Configuration

### Dockerfile Summary

```dockerfile
FROM python:3.11-slim-bookworm
WORKDIR /app

# Security: Non-root user (sahool:sahool)
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Health check included
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8131/healthz || exit 1

EXPOSE 8131
USER sahool
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8131"]
```

---

## Summary

The CRM Service is a well-structured FastAPI microservice providing comprehensive farmer relationship management for the SAHOOL platform. It features:

- **Strong multi-tenancy support** with strict tenant isolation
- **Bilingual support** (Arabic/English) throughout
- **Event-driven architecture** with NATS integration
- **Comprehensive security** including rate limiting, JWT auth, and NLQ sanitization
- **Flexible storage** supporting both in-memory and PostgreSQL modes

**Primary concerns:**
1. Database integration is incomplete for deals, interactions, and farmer updates
2. Metrics don't reflect database state
3. Limited NLQ pattern support

**Overall Assessment:** Production-ready for basic CRM operations in in-memory mode. Database mode requires completion of repository integration for full production deployment.

---

*Analysis completed: 2026-01-25*
*Analyst: Claude Code (Opus 4.5)*
