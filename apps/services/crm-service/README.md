# SAHOOL Farmer CRM Service

**Customer Relationship Management for Agricultural Operations**

| Property | Value |
|----------|-------|
| **Service Name** | crm-service |
| **Arabic Name** | خدمة إدارة علاقات المزارعين |
| **Version** | 16.0.0 |
| **Port** | 8131 |
| **Framework** | FastAPI (Python) |
| **License** | Proprietary - KAFAAT |

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Examples](#examples)
- [Development](#development)
- [Testing](#testing)
- [Arabic Documentation](#arabic-documentation)

---

## Overview

The CRM Service provides comprehensive Farmer Relationship Management capabilities for the SAHOOL platform. Inspired by CordysCRM's AI-powered architecture, this service adapts traditional CRM concepts for agricultural contexts, enabling:

- Complete farmer lifecycle management from lead to premium customer
- Harvest deal pipeline tracking similar to sales opportunity management
- Interaction logging with sentiment analysis
- Natural language queries in both Arabic and English (SQLBot-inspired)
- Engagement scoring and analytics

### Key Integrations

- **NATS**: Event-driven messaging for real-time updates
- **PostgreSQL**: Persistent storage with PostGIS support
- **Redis**: Session caching and rate limiting
- **Kong**: API Gateway for authentication and rate limiting

---

## Features

### 1. Farmer Lifecycle Management

Manage farmers through their complete engagement lifecycle:

| Status | Arabic | Description |
|--------|--------|-------------|
| `lead` | مهتم | Initial contact, potential farmer |
| `registered` | مسجل | Completed registration |
| `active` | نشط | Actively using platform |
| `premium` | مميز | Premium subscriber |
| `churned` | متوقف | Stopped using platform |

### 2. Harvest Deal Pipeline

Track agricultural deals through a CRM-style pipeline:

| Stage | Arabic | Probability | Description |
|-------|--------|-------------|-------------|
| `prospecting` | استكشاف | 10% | Identifying harvest opportunity |
| `qualification` | تأهيل | 25% | Assessing crop quality and viability |
| `negotiation` | تفاوض | 50% | Price and terms discussion |
| `contracted` | متعاقد | 75% | Supply agreement signed |
| `delivered` | مسلم | 90% | Crop delivered to buyer |
| `paid` | مدفوع | 100% | Payment received (Won) |
| `closed_lost` | خسارة | 0% | Deal fell through |

### 3. Interaction Logging

Log all farmer communications with automatic sentiment tracking:

| Type | Arabic | Description |
|------|--------|-------------|
| `call` | مكالمة | Phone call |
| `visit` | زيارة | Field visit |
| `whatsapp` | واتساب | WhatsApp message |
| `sms` | رسالة نصية | SMS message |
| `email` | بريد إلكتروني | Email communication |
| `advisory` | استشارة | Advisory session |
| `support` | دعم فني | Technical support |

### 4. Natural Language Queries (SQLBot-inspired)

Query farmer data using natural language in Arabic or English:

```
English: "Show me all active farmers"
Arabic: "أرني جميع المزارعين النشطين"

English: "Deals in negotiation stage"
Arabic: "صفقات في مرحلة التفاوض"

English: "Lead farmers with farm size > 10 hectares"
Arabic: "المزارعين المحتملين بمساحة أكبر من 10 هكتار"
```

### 5. Engagement Scoring

Automatic calculation of farmer engagement score (0-100) based on:

- **Recency** (30 points max): Last interaction date
- **Interactions** (25 points max): Total number of interactions
- **Deals** (25 points max): Active deals in pipeline
- **Profile** (20 points max): Profile completeness

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Kong)                      │
│                   Port: 8000 (Rate Limited)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CRM Service (FastAPI)                     │
│                        Port: 8131                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Farmers   │  │    Deals    │  │    Interactions     │  │
│  │    CRUD     │  │   Pipeline  │  │      Logging        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────────────────────────────┐   │
│  │   Query     │  │         Pipeline Analytics          │   │
│  │    Bot      │  │    (Conversion, Value, Stats)       │   │
│  └─────────────┘  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  PostgreSQL │      │    NATS     │      │    Redis    │
│   Database  │      │  Messaging  │      │   Caching   │
└─────────────┘      └─────────────┘      └─────────────┘
```

### Event Subjects

The service publishes events to NATS on the following subjects:

| Subject Pattern | Description |
|-----------------|-------------|
| `sahool.{tenant_id}.crm.farmer.created` | New farmer registered |
| `sahool.{tenant_id}.crm.farmer.updated` | Farmer data updated |
| `sahool.{tenant_id}.crm.farmer.status_changed` | Farmer status changed |
| `sahool.{tenant_id}.crm.deal.created` | New deal created |
| `sahool.{tenant_id}.crm.deal.stage_changed` | Deal stage advanced |
| `sahool.{tenant_id}.crm.interaction.logged` | Interaction recorded |

---

## API Endpoints

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/healthz` | Liveness probe |
| `GET` | `/readyz` | Readiness probe |
| `GET` | `/health` | Detailed health status |
| `GET` | `/metrics` | Prometheus metrics |

### Farmers API

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/farmers` | Create new farmer | 30/min |
| `GET` | `/api/v1/farmers` | List farmers (paginated) | 60/min |
| `GET` | `/api/v1/farmers/{farmer_id}` | Get farmer by ID | 60/min |
| `PATCH` | `/api/v1/farmers/{farmer_id}` | Update farmer | 60/min |

**Query Parameters for GET /api/v1/farmers:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant identifier |
| `status` | string | No | Filter by status (lead, active, etc.) |
| `search` | string | No | Search by name, Arabic name, or phone |
| `limit` | int | No | Max results (default: 50, max: 200) |
| `offset` | int | No | Pagination offset (default: 0) |

### Deals API

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/deals` | Create harvest deal | 30/min |
| `GET` | `/api/v1/deals` | List deals | 60/min |
| `PATCH` | `/api/v1/deals/{deal_id}/stage` | Update deal stage | 60/min |
| `GET` | `/api/v1/deals/pipeline` | Get pipeline statistics | 60/min |

**Query Parameters for GET /api/v1/deals:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant identifier |
| `farmer_id` | string | No | Filter by farmer |
| `stage` | string | No | Filter by pipeline stage |
| `limit` | int | No | Max results (default: 50, max: 200) |

### Interactions API

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/interactions` | Log interaction | 60/min |
| `GET` | `/api/v1/interactions` | List interactions | 60/min |

**Query Parameters for GET /api/v1/interactions:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `farmer_id` | string | Yes | Farmer identifier |
| `interaction_type` | string | No | Filter by type |
| `limit` | int | No | Max results (default: 50, max: 200) |

### Query API (Natural Language)

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/query` | Natural language query | 10/min |

---

## Configuration

### Environment Variables

```bash
# Service Configuration
ENVIRONMENT=development          # development | staging | production
LOG_LEVEL=INFO                   # DEBUG | INFO | WARNING | ERROR

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool?sslmode=require

# Messaging (NATS)
NATS_URL=nats://nats:4222

# Authentication (JWT)
JWT_SECRET_KEY=your-32-character-minimum-secret-key
JWT_ALGORITHM=HS256

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Rate Limiting (via SlowAPI)
# Configured in code: 30/min for writes, 60/min for reads, 10/min for queries
```

### Docker Configuration

The service runs as a non-root user (`sahool:sahool`) for security:

```dockerfile
EXPOSE 8131
USER sahool
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8131"]
```

---

## Examples

### Authentication

All API endpoints require JWT authentication. Include the token in the Authorization header:

```bash
# Get auth token (from user-service)
TOKEN="your-jwt-token"

# Use in requests
curl -H "Authorization: Bearer $TOKEN" ...
```

### Create a Farmer

```bash
curl -X POST http://localhost:8131/api/v1/farmers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Ahmed Mohammed",
    "name_ar": "أحمد محمد",
    "phone": "+966501234567",
    "email": "ahmed@example.com",
    "national_id": "1234567890",
    "farm_location": "Riyadh",
    "farm_location_ar": "الرياض",
    "farm_size_hectares": 25.5,
    "primary_crops": ["wheat", "barley"],
    "tenant_id": "sahool-tenant"
  }'
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Ahmed Mohammed",
  "name_ar": "أحمد محمد",
  "phone": "+966501234567",
  "email": "ahmed@example.com",
  "national_id": "1234567890",
  "farm_location": "Riyadh",
  "farm_location_ar": "الرياض",
  "farm_size_hectares": 25.5,
  "primary_crops": ["wheat", "barley"],
  "status": "lead",
  "tags": [],
  "created_at": "2026-01-22T10:30:00Z",
  "updated_at": "2026-01-22T10:30:00Z",
  "last_interaction_at": null
}
```

### List Farmers with Search

```bash
# List all farmers
curl "http://localhost:8131/api/v1/farmers?tenant_id=sahool-tenant" \
  -H "Authorization: Bearer $TOKEN"

# Search by name
curl "http://localhost:8131/api/v1/farmers?tenant_id=sahool-tenant&search=ahmed" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl "http://localhost:8131/api/v1/farmers?tenant_id=sahool-tenant&status=active" \
  -H "Authorization: Bearer $TOKEN"

# Paginated results
curl "http://localhost:8131/api/v1/farmers?tenant_id=sahool-tenant&limit=10&offset=20" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Farmer Status

```bash
curl -X PATCH http://localhost:8131/api/v1/farmers/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "active",
    "tags": ["vip", "wheat-producer"]
  }'
```

### Create a Harvest Deal

```bash
curl -X POST http://localhost:8131/api/v1/deals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "farmer_id": "550e8400-e29b-41d4-a716-446655440000",
    "crop_type": "wheat",
    "crop_type_ar": "قمح",
    "expected_quantity_tons": 50.0,
    "expected_harvest_date": "2026-06-15",
    "price_per_ton": 1850.0,
    "notes": "First wheat harvest deal",
    "notes_ar": "أول صفقة حصاد قمح"
  }'
```

**Response:**

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "farmer_id": "550e8400-e29b-41d4-a716-446655440000",
  "crop_type": "wheat",
  "crop_type_ar": "قمح",
  "expected_quantity_tons": 50.0,
  "actual_quantity_tons": null,
  "expected_harvest_date": "2026-06-15",
  "actual_harvest_date": null,
  "price_per_ton": 1850.0,
  "total_value": null,
  "stage": "prospecting",
  "notes": "First wheat harvest deal",
  "notes_ar": "أول صفقة حصاد قمح",
  "created_at": "2026-01-22T10:35:00Z",
  "updated_at": "2026-01-22T10:35:00Z"
}
```

### Advance Deal Stage

```bash
curl -X PATCH "http://localhost:8131/api/v1/deals/660e8400-e29b-41d4-a716-446655440001/stage?stage=negotiation" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Pipeline Statistics

```bash
curl "http://localhost:8131/api/v1/deals/pipeline?tenant_id=sahool-tenant" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "total_deals": 15,
  "total_value": 2775000.0,
  "by_stage": {
    "prospecting": {
      "count": 3,
      "total_value": 555000.0,
      "name_ar": "استكشاف"
    },
    "qualification": {
      "count": 4,
      "total_value": 740000.0,
      "name_ar": "تأهيل"
    },
    "negotiation": {
      "count": 3,
      "total_value": 555000.0,
      "name_ar": "تفاوض"
    },
    "contracted": {
      "count": 2,
      "total_value": 370000.0,
      "name_ar": "متعاقد"
    },
    "delivered": {
      "count": 1,
      "total_value": 185000.0,
      "name_ar": "مسلم"
    },
    "paid": {
      "count": 2,
      "total_value": 370000.0,
      "name_ar": "مدفوع"
    },
    "closed_lost": {
      "count": 0,
      "total_value": 0.0,
      "name_ar": "خسارة"
    }
  },
  "conversion_rate": 13.33,
  "average_deal_size": 185000.0
}
```

### Log an Interaction

```bash
curl -X POST http://localhost:8131/api/v1/interactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "farmer_id": "550e8400-e29b-41d4-a716-446655440000",
    "interaction_type": "call",
    "subject": "Follow-up on irrigation advice",
    "subject_ar": "متابعة نصيحة الري",
    "notes": "Farmer confirmed implementing the irrigation schedule",
    "notes_ar": "أكد المزارع تطبيق جدول الري",
    "outcome": "positive",
    "follow_up_date": "2026-02-01"
  }'
```

### Natural Language Query

```bash
# English query
curl -X POST http://localhost:8131/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "Show me all active farmers",
    "tenant_id": "sahool-tenant"
  }'

# Arabic query
curl -X POST http://localhost:8131/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "أرني جميع المزارعين النشطين",
    "tenant_id": "sahool-tenant"
  }'
```

**Response:**

```json
{
  "query": "Show me all active farmers",
  "interpreted_as": "SELECT * FROM farmers WHERE status = 'active'",
  "interpreted_as_ar": "اختر جميع المزارعين حيث الحالة = نشط",
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Ahmed Mohammed",
      "name_ar": "أحمد محمد",
      "status": "active",
      "farm_size_hectares": 25.5
    }
  ],
  "result_count": 1,
  "execution_time_ms": 12
}
```

### Health Check

```bash
# Liveness probe
curl http://localhost:8131/healthz

# Readiness probe
curl http://localhost:8131/readyz

# Detailed health
curl http://localhost:8131/health
```

### Prometheus Metrics

```bash
curl http://localhost:8131/metrics
```

**Response:**

```
# HELP crm_farmers_total Total number of farmers
# TYPE crm_farmers_total gauge
crm_farmers_total 150

# HELP crm_deals_total Total number of deals
# TYPE crm_deals_total gauge
crm_deals_total 45

# HELP crm_interactions_total Total number of interactions
# TYPE crm_interactions_total counter
crm_interactions_total 890
```

---

## Development

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 16+ (with PostGIS)
- NATS 2.x
- Redis 7.x

### Local Setup

```bash
# Navigate to service directory
cd apps/services/crm-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENVIRONMENT=development
export JWT_SECRET_KEY=dev-secret-key-for-local-testing-32chars
export DATABASE_URL=postgresql://sahool:sahool@localhost:5432/sahool
export NATS_URL=nats://localhost:4222

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8131 --reload
```

### Docker Development

```bash
# From project root
make dev

# Or run just CRM service
docker compose up crm-service

# View logs
docker compose logs -f crm-service

# Enter container shell
docker compose exec crm-service bash
```

### Database Migrations

```bash
# Run migrations
psql $DATABASE_URL -f migrations/001_initial_schema.sql

# Or via make command from project root
make db-migrate
```

### Code Quality

```bash
# Lint with Ruff
ruff check apps/services/crm-service/

# Format code
ruff format apps/services/crm-service/

# Type checking
mypy apps/services/crm-service/src/
```

---

## Testing

### Run All Tests

```bash
# From project root
pytest apps/services/crm-service/tests/ -v

# With coverage
pytest apps/services/crm-service/tests/ -v --cov=apps/services/crm-service/src --cov-report=html
```

### Test Categories

```bash
# Unit tests only
pytest apps/services/crm-service/tests/ -v -m unit

# Integration tests
pytest apps/services/crm-service/tests/ -v -m integration

# Smoke tests
pytest apps/services/crm-service/tests/ -v -m smoke
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Test fixtures and configuration
├── test_main.py             # API endpoint tests
│   ├── TestHealthEndpoints  # Health check tests
│   ├── TestFarmerEndpoints  # Farmer CRUD tests
│   ├── TestDealEndpoints    # Deal pipeline tests
│   ├── TestInteractionEndpoints  # Interaction tests
│   ├── TestNaturalLanguageQuery  # Query bot tests
│   └── TestEdgeCases        # Edge case and error handling
└── test_models.py           # Data model tests
```

### Test Environment Variables

```bash
export ENVIRONMENT=test
export JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars
export JWT_ALGORITHM=HS256
export DATABASE_URL=""   # Empty for unit tests (uses in-memory storage)
export NATS_URL=""       # Empty for unit tests
```

---

## Arabic Documentation

# وثائق خدمة إدارة علاقات المزارعين

## نظرة عامة

خدمة إدارة علاقات المزارعين (CRM) هي نظام شامل لإدارة علاقات العملاء في القطاع الزراعي ضمن منصة سهول. توفر هذه الخدمة:

- **إدارة دورة حياة المزارع**: من عميل محتمل إلى عميل مميز
- **خط أنابيب صفقات الحصاد**: تتبع الصفقات من الاستكشاف إلى الدفع
- **تسجيل التفاعلات**: توثيق جميع الاتصالات مع المزارعين
- **استعلامات اللغة الطبيعية**: البحث بالعربية أو الإنجليزية
- **حساب درجة التفاعل**: تقييم تلقائي لمشاركة المزارع

## حالات المزارع

| الحالة | الوصف |
|--------|-------|
| مهتم (lead) | اتصال أولي، مزارع محتمل |
| مسجل (registered) | أكمل التسجيل |
| نشط (active) | يستخدم المنصة بنشاط |
| مميز (premium) | مشترك في الباقة المميزة |
| متوقف (churned) | توقف عن استخدام المنصة |

## مراحل الصفقات

| المرحلة | الاحتمالية | الوصف |
|---------|------------|-------|
| استكشاف | 10% | تحديد فرصة الحصاد |
| تأهيل | 25% | تقييم جودة المحصول |
| تفاوض | 50% | مناقشة السعر والشروط |
| متعاقد | 75% | توقيع اتفاقية التوريد |
| مسلم | 90% | تسليم المحصول |
| مدفوع | 100% | استلام الدفعة |
| خسارة | 0% | فشل الصفقة |

## أمثلة الاستعلامات بالعربية

```bash
# استعلام عن المزارعين النشطين
curl -X POST http://localhost:8131/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "أرني جميع المزارعين النشطين",
    "tenant_id": "sahool-tenant"
  }'

# استعلام عن الصفقات في مرحلة التفاوض
curl -X POST http://localhost:8131/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "صفقات في مرحلة التفاوض",
    "tenant_id": "sahool-tenant"
  }'
```

## إنشاء مزارع جديد

```bash
curl -X POST http://localhost:8131/api/v1/farmers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "محمد أحمد",
    "name_ar": "محمد أحمد",
    "phone": "+966501234567",
    "farm_location": "القصيم",
    "farm_location_ar": "القصيم",
    "farm_size_hectares": 15.0,
    "primary_crops": ["قمح", "شعير"],
    "tenant_id": "sahool-tenant"
  }'
```

## إنشاء صفقة حصاد

```bash
curl -X POST http://localhost:8131/api/v1/deals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "farmer_id": "معرف-المزارع",
    "crop_type": "wheat",
    "crop_type_ar": "قمح",
    "expected_quantity_tons": 30.0,
    "expected_harvest_date": "2026-06-01",
    "price_per_ton": 1900.0,
    "notes_ar": "صفقة قمح موسم الشتاء"
  }'
```

## تسجيل تفاعل

```bash
curl -X POST http://localhost:8131/api/v1/interactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "farmer_id": "معرف-المزارع",
    "interaction_type": "visit",
    "subject": "زيارة ميدانية",
    "subject_ar": "زيارة ميدانية للحقل",
    "notes_ar": "تم فحص المحصول وتقديم نصائح الري",
    "outcome": "إيجابي",
    "follow_up_date": "2026-02-15"
  }'
```

---

## Support

For issues and feature requests, please contact the SAHOOL Platform Team or create an issue in the repository.

**Last Updated:** January 2026
