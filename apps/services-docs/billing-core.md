# Billing Core Service Documentation

**Service**: `billing-core`
**Version**: 16.0.0 (Docker: 15.4.0)
**Port**: 8089
**Type**: Python/FastAPI
**Path**: `/home/user/sahool-unified-v15-idp/apps/services/billing-core/`

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [NATS Events](#nats-events)
5. [Payment Provider Integrations](#payment-provider-integrations)
6. [Database Schema](#database-schema)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Bugs and Recommended Fixes](#bugs-and-recommended-fixes)

---

## Overview

The Billing Core Service is a comprehensive billing, subscription, and payment management system for the SAHOOL agricultural platform. It provides:

- **Plan Management**: Tiered subscription plans (Free, Starter, Professional, Enterprise)
- **Tenant/Subscription Lifecycle**: Full CRUD operations for tenants and subscriptions
- **Usage-Based Billing**: Tracking and enforcement of usage quotas
- **Invoice Generation**: Automatic and manual invoice generation with overage charges
- **Payment Processing**: Integration with Stripe and Tharwatt (Yemeni payment gateway)
- **Multi-Currency Support**: USD and YER (Yemeni Rial)
- **Event-Driven Architecture**: NATS JetStream for billing events
- **Bilingual Support**: Arabic and English throughout

### Key Features

| Feature | Description |
|---------|-------------|
| Multi-tier Plans | Free, Starter ($29), Professional ($99), Enterprise ($499) monthly |
| Usage Tracking | Fields, satellite analyses, AI diagnoses, PDF reports, storage, API calls |
| Overage Billing | Automatic calculation of excess usage charges |
| Currency Conversion | Real-time USD to YER conversion (configurable rate) |
| Webhook Support | Stripe and Tharwatt payment confirmation callbacks |

---

## Architecture

### Kong Gateway Routes

| Route | Strip Path | Target |
|-------|------------|--------|
| `/api/v1/billing` | true | `billing-core:8089` |
| `/billing` | true | `billing-core:8089` |

### Infrastructure Dependencies

- **pgbouncer**: Database connection pooling (PostgreSQL)
- **redis**: Session caching and rate limiting
- **nats**: Event messaging via JetStream

### Service Layers

```
main.py (FastAPI Application)
    |
    +-- database.py (Async SQLAlchemy Engine/Session)
    |
    +-- models.py (SQLAlchemy ORM Models)
    |
    +-- repository.py (Data Access Layer)
```

---

## API Endpoints

### Health Checks

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/healthz` | None | Liveness probe |
| `GET` | `/readyz` | None | Readiness probe (checks DB, NATS, plans count) |

#### Response: `/healthz`
```json
{
  "status": "ok",
  "service": "billing-core",
  "version": "16.0.0"
}
```

#### Response: `/readyz`
```json
{
  "status": "ready",
  "service": "billing-core",
  "version": "16.0.0",
  "checks": {
    "database": "connected",
    "nats": "connected"
  },
  "plans_count": 4
}
```

---

### Plans API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/v1/plans` | None | List all available plans |
| `GET` | `/v1/plans/{plan_id}` | None | Get plan details |
| `POST` | `/v1/plans` | `super_admin`, `tenant_admin` | Create new plan |

#### `GET /v1/plans`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active_only` | boolean | `true` | Filter active plans only |

**Response:**
```json
{
  "plans": [
    {
      "plan_id": "starter",
      "name": "Starter",
      "name_ar": "المبتدئ",
      "tier": "starter",
      "pricing": {
        "monthly_usd": 29.0,
        "monthly_yer": 7250.0,
        "yearly_usd": 290.0,
        "yearly_yer": 72500.0
      },
      "limits": {
        "fields": 10,
        "satellite_analyses_per_month": 50,
        "ai_diagnoses_per_month": 20,
        "pdf_reports_per_month": 10,
        "storage_gb": 5,
        "api_calls_per_day": 500
      },
      "trial_days": 14
    }
  ]
}
```

#### `GET /v1/plans/{plan_id}`

**Response:**
```json
{
  "plan": {
    "plan_id": "professional",
    "name": "Professional",
    "name_ar": "الاحترافي",
    "description": "For professional farmers and agricultural businesses",
    "description_ar": "للمزارعين المحترفين والأعمال الزراعية",
    "tier": "professional",
    "pricing": {
      "monthly_usd": "99",
      "quarterly_usd": "269",
      "yearly_usd": "990"
    },
    "features": {...},
    "limits": {...},
    "is_active": true,
    "trial_days": 14,
    "created_at": "2025-01-20T10:00:00Z"
  },
  "pricing_yer": {
    "monthly": 24750.0,
    "quarterly": 67250.0,
    "yearly": 247500.0
  }
}
```

#### `POST /v1/plans`

**Request Body:**
```json
{
  "name": "Custom Plan",
  "name_ar": "خطة مخصصة",
  "description": "Custom plan description",
  "description_ar": "وصف الخطة المخصصة",
  "tier": "professional",
  "monthly_price_usd": 149.99,
  "features": {
    "fields": true,
    "satellite": true,
    "ai_diagnosis": true
  },
  "limits": {
    "fields": 100,
    "satellite_analyses_per_month": 500
  },
  "trial_days": 7
}
```

---

### Tenants API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/tenants` | None | Create tenant with subscription |
| `GET` | `/v1/tenants/{tenant_id}` | Authenticated | Get tenant info |
| `GET` | `/v1/tenants/{tenant_id}/subscription` | Authenticated | Get subscription details |
| `PATCH` | `/v1/tenants/{tenant_id}/subscription` | Authenticated | Update subscription |
| `POST` | `/v1/tenants/{tenant_id}/cancel` | Authenticated | Cancel subscription |

#### `POST /v1/tenants`

**Request Body:**
```json
{
  "name": "Al-Rashid Farm",
  "name_ar": "مزرعة الرشيد",
  "email": "contact@alrashid.farm",
  "phone": "+967123456789",
  "plan_id": "starter",
  "billing_cycle": "monthly"
}
```

**Response:**
```json
{
  "success": true,
  "tenant_id": "uuid-here",
  "subscription_id": "uuid-here",
  "status": "trial",
  "trial_ends": "2025-02-03",
  "message_ar": "مرحباً مزرعة الرشيد! تم إنشاء حسابك بنجاح."
}
```

#### `GET /v1/tenants/{tenant_id}`

**Response:**
```json
{
  "tenant": {
    "tenant_id": "uuid",
    "name": "Al-Rashid Farm",
    "name_ar": "مزرعة الرشيد",
    "contact": {
      "name": "Al-Rashid Farm",
      "name_ar": "مزرعة الرشيد",
      "email": "contact@alrashid.farm",
      "phone": "+967123456789"
    },
    "tax_id": null,
    "is_active": true,
    "created_at": "2025-01-20T10:00:00Z"
  },
  "subscription": {
    "subscription_id": "uuid",
    "plan_id": "starter",
    "status": "active",
    "billing_cycle": "monthly",
    "start_date": "2025-01-20",
    "end_date": "2025-02-19"
  },
  "usage": {
    "fields": {"allowed": true, "limit": 10, "used": 5, "remaining": 5},
    "satellite_analyses_per_month": {"allowed": true, "limit": 50, "used": 12, "remaining": 38}
  }
}
```

#### `PATCH /v1/tenants/{tenant_id}/subscription`

**Request Body:**
```json
{
  "plan_id": "professional",
  "billing_cycle": "yearly",
  "payment_method": "credit_card"
}
```

#### `POST /v1/tenants/{tenant_id}/cancel`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `immediate` | boolean | `false` | Cancel immediately or at end of period |

---

### Usage & Quotas API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/tenants/{tenant_id}/usage` | Authenticated | Record usage |
| `GET` | `/v1/tenants/{tenant_id}/quota` | Authenticated | Get quota status |
| `GET` | `/v1/enforce` | API Key | Enforce quota (for Gateway) |

#### `POST /v1/tenants/{tenant_id}/usage`

**Request Body:**
```json
{
  "metric": "satellite_analyses_per_month",
  "quantity": 1,
  "metadata": {"field_id": "field-123", "analysis_type": "ndvi"}
}
```

**Response:**
```json
{
  "success": true,
  "record_id": "uuid",
  "remaining": 37
}
```

**Error (429 - Quota Exceeded):**
```json
{
  "detail": "تم تجاوز الحد الأقصى للاستخدام: satellite_analyses_per_month. الحد: 50, المستخدم: 50"
}
```

#### `GET /v1/tenants/{tenant_id}/quota`

**Response:**
```json
{
  "tenant_id": "uuid",
  "plan": "Professional",
  "plan_ar": "الاحترافي",
  "subscription_status": "active",
  "usage": {
    "fields": {"limit": 50, "used": 15, "remaining": 35, "percentage": 30.0},
    "satellite_analyses_per_month": {"limit": 200, "used": 45, "remaining": 155, "percentage": 22.5},
    "ai_diagnoses_per_month": {"limit": 100, "used": 20, "remaining": 80, "percentage": 20.0}
  },
  "billing_cycle_ends": "2025-02-19"
}
```

#### `GET /v1/enforce`

**Headers Required:**
- `X-Tenant-Id`: Tenant identifier

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `metric` | string | Yes | Metric to check |

**Response (Allowed):**
```json
{
  "allowed": true,
  "tenant_id": "uuid",
  "metric": "api_calls_per_day",
  "remaining": 1850
}
```

**Response (Quota Exceeded - 429):**
```json
{
  "detail": {
    "error": "quota_exceeded",
    "metric": "api_calls_per_day",
    "limit": 2000,
    "used": 2000
  }
}
```

---

### Invoices API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/v1/tenants/{tenant_id}/invoices` | Authenticated | List tenant invoices |
| `GET` | `/v1/invoices/{invoice_id}` | Authenticated | Get invoice details |
| `POST` | `/v1/tenants/{tenant_id}/invoices/generate` | Authenticated | Generate invoice manually |

#### `GET /v1/tenants/{tenant_id}/invoices`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | InvoiceStatus | None | Filter by status |
| `limit` | int | 20 | Max results (max 100) |

**Response:**
```json
{
  "invoices": [
    {
      "invoice_id": "uuid",
      "invoice_number": "SAH-2025-0001",
      "tenant_id": "uuid",
      "status": "paid",
      "currency": "USD",
      "total": 99.00,
      "amount_due": 0.00,
      "issue_date": "2025-01-01",
      "due_date": "2025-01-08",
      "paid_date": "2025-01-03"
    }
  ],
  "total": 1
}
```

#### `GET /v1/invoices/{invoice_id}`

**Response:**
```json
{
  "invoice": {
    "invoice_id": "uuid",
    "invoice_number": "SAH-2025-0001",
    "tenant_id": "uuid",
    "subscription_id": "uuid",
    "status": "pending",
    "currency": "USD",
    "issue_date": "2025-01-20",
    "due_date": "2025-01-27",
    "paid_date": null,
    "subtotal": 99.00,
    "tax_amount": 0.00,
    "discount_amount": 0.00,
    "total": 99.00,
    "amount_paid": 0.00,
    "amount_due": 99.00,
    "line_items": [
      {
        "description": "Professional - Monthly",
        "description_ar": "الاحترافي - شهري",
        "quantity": 1,
        "unit_price": 99.00,
        "amount": 99.00,
        "is_usage_based": false
      }
    ],
    "notes": null,
    "notes_ar": "شكراً لاختياركم منصة سهول الزراعية"
  },
  "tenant": {
    "tenant_id": "uuid",
    "name": "Al-Rashid Farm",
    "name_ar": "مزرعة الرشيد",
    "contact": {...}
  },
  "amount_yer": 24750.00
}
```

---

### Payments API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/payments` | Authenticated | Create payment |
| `GET` | `/v1/tenants/{tenant_id}/payments` | Authenticated | List tenant payments |

#### `POST /v1/payments`

**Request Body:**
```json
{
  "invoice_id": "uuid",
  "amount": 99.00,
  "method": "credit_card",
  "stripe_token": "tok_xxx"
}
```

**Response:**
```json
{
  "success": true,
  "payment": {
    "payment_id": "uuid",
    "invoice_id": "uuid",
    "tenant_id": "uuid",
    "amount": 99.00,
    "currency": "USD",
    "method": "credit_card",
    "status": "succeeded",
    "created_at": "2025-01-20T10:30:00Z"
  },
  "invoice_status": "paid",
  "tharwatt_response": null,
  "stripe_response": {"stripe_charge_id": "ch_xxx", "status": "succeeded"}
}
```

---

### Webhooks API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/webhooks/tharwatt` | Signature Verification | Tharwatt payment callback |
| `POST` | `/v1/webhooks/stripe` | Signature Verification | Stripe event callback |

#### `POST /v1/webhooks/tharwatt`

**Headers Required:**
- `X-Tharwatt-Signature`: HMAC-SHA256 signature

**Request Body:**
```json
{
  "transaction_id": "THR-xxx",
  "status": "completed",
  "amount": 24750.00,
  "currency": "YER",
  "phone_number": "+967123456789",
  "reference": "payment-uuid",
  "timestamp": "2025-01-20T10:30:00Z",
  "error_message": null
}
```

#### `POST /v1/webhooks/stripe`

**Headers Required:**
- `stripe-signature`: Stripe webhook signature

**Handled Event Types:**
- `charge.succeeded`
- `charge.failed`
- `customer.subscription.updated`

---

### Reports API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/v1/reports/revenue` | `super_admin`, `tenant_admin` | Revenue report |
| `GET` | `/v1/reports/subscriptions` | `super_admin`, `tenant_admin` | Subscriptions report |

#### `GET /v1/reports/revenue`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_date` | date | First of month | Period start |
| `end_date` | date | Today | Period end |

**Response:**
```json
{
  "period": {"start": "2025-01-01", "end": "2025-01-20"},
  "total_revenue": {"usd": 4950.00, "yer": 1237500.00},
  "invoices_count": 50,
  "by_plan": {
    "starter": 870.00,
    "professional": 2970.00,
    "enterprise": 1110.00
  }
}
```

#### `GET /v1/reports/subscriptions`

**Response:**
```json
{
  "total_subscriptions": 75,
  "by_status": {
    "active": 60,
    "trial": 10,
    "canceled": 5
  },
  "by_plan": {
    "free": 20,
    "starter": 30,
    "professional": 20,
    "enterprise": 5
  },
  "mrr_usd": 5420.00,
  "mrr_yer": 1355000.00,
  "total_tenants": 75
}
```

---

## NATS Events

### Stream Configuration

| Setting | Value |
|---------|-------|
| Stream Name | `BILLING` |
| Subjects | `sahool.billing.*`, `sahool.payment.*`, `sahool.subscription.*` |
| Retention | `LIMITS` |
| Max Age | 30 days |

### Published Events

| Subject | Trigger | Payload |
|---------|---------|---------|
| `sahool.payment.created` | Payment created | `{payment_id, invoice_id, tenant_id, amount, currency, method, status}` |
| `sahool.payment.succeeded` | Payment successful | `{payment_id, invoice_id, tenant_id, amount, method, transaction_id/stripe_charge_id}` |
| `sahool.payment.failed` | Payment failed | `{payment_id, invoice_id, error}` |
| `sahool.subscription.updated` | Subscription status change | `{subscription_id, tenant_id, status}` |

### Example Event Payload

```json
// sahool.payment.succeeded
{
  "payment_id": "uuid",
  "invoice_id": "uuid",
  "tenant_id": "uuid",
  "amount": 99.00,
  "method": "stripe",
  "stripe_charge_id": "ch_xxx"
}
```

---

## Payment Provider Integrations

### Stripe Integration

**Purpose**: Credit card payments for international customers

**API Endpoints Used:**
- `stripe.Charge.create()` - Process card payments
- `stripe.Webhook.construct_event()` - Verify webhook signatures

**Configuration:**
```bash
STRIPE_API_KEY=sk_live_xxx          # Secret key
STRIPE_WEBHOOK_SECRET=whsec_xxx     # Webhook signing secret
```

**Supported Events:**
- `charge.succeeded` - Payment completed
- `charge.failed` - Payment declined
- `customer.subscription.updated` - Subscription status change

**Integration Flow:**
1. Client sends `stripe_token` from Stripe.js
2. Service calls `stripe.Charge.create()` with token
3. Stripe processes payment
4. Webhook confirms final status

---

### Tharwatt Integration

**Purpose**: Yemeni mobile money/wallet payments (local market)

**API Base URL**: `https://developers-test.tharwatt.com:5253`

**API Endpoint Used:**
- `POST /api/v1/payment/deposit` - Initiate payment

**Request Headers:**
```
Authorization: Bearer {THARWATT_API_KEY}
X-Merchant-Id: {THARWATT_MERCHANT_ID}
Content-Type: application/json
```

**Request Payload:**
```json
{
  "reference": "payment-uuid",
  "amount": 24750.00,
  "currency": "YER",
  "phone_number": "+967123456789",
  "description": "SAHOOL Invoice Payment - invoice-uuid",
  "callback_url": "https://api.sahool.com/api/v1/webhooks/tharwatt"
}
```

**Configuration:**
```bash
THARWATT_BASE_URL=https://developers-test.tharwatt.com:5253
THARWATT_API_KEY=xxx
THARWATT_MERCHANT_ID=xxx
THARWATT_WEBHOOK_SECRET=xxx    # For HMAC-SHA256 verification
```

**Webhook Signature Verification:**
```python
expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
is_valid = hmac.compare_digest(received_signature, expected)
```

---

## Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `plans` | Subscription plans (Free, Starter, Professional, Enterprise) |
| `tenants` | Customer/tenant records |
| `subscriptions` | Tenant subscription records |
| `invoices` | Generated invoices |
| `payments` | Payment transactions |
| `usage_records` | Usage tracking for metered billing |

### Enums

| Enum | Values |
|------|--------|
| `subscription_status_enum` | `active`, `trial`, `past_due`, `canceled`, `suspended`, `expired` |
| `billing_cycle_enum` | `monthly`, `quarterly`, `yearly` |
| `currency_enum` | `USD`, `YER` |
| `invoice_status_enum` | `draft`, `pending`, `paid`, `overdue`, `canceled`, `refunded` |
| `payment_method_enum` | `credit_card`, `bank_transfer`, `mobile_money`, `cash`, `tharwatt` |
| `payment_status_enum` | `pending`, `processing`, `succeeded`, `failed`, `refunded` |
| `plan_tier_enum` | `free`, `starter`, `professional`, `enterprise` |

### Key Indexes

- `idx_subscription_tenant_status` - Tenant+Status lookup
- `idx_subscription_next_billing` - Due billing queries
- `idx_invoice_tenant_status` - Tenant invoice listing
- `idx_invoice_due_date_status` - Overdue invoice queries
- `idx_payment_tenant_status` - Tenant payment history
- `idx_usage_tenant_metric_date` - Usage aggregation

### Relationships

```
plans (1) --> (N) subscriptions.plan_id
tenants (1) --> (N) subscriptions.tenant_id
subscriptions (1) --> (N) invoices
subscriptions (1) --> (N) usage_records
invoices (1) --> (N) payments
```

---

## Dependencies

### Python Packages (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.126.0 | Web framework |
| `starlette` | >=0.49.1 | ASGI framework |
| `uvicorn[standard]` | >=0.30.0,<1.0.0 | ASGI server |
| `pydantic` | 2.9.2 | Data validation |
| `email-validator` | 2.2.0 | Email validation |
| `sqlalchemy` | 2.0.36 | ORM |
| `asyncpg` | 0.30.0 | Async PostgreSQL driver |
| `alembic` | 1.14.0 | Database migrations |
| `stripe` | 11.3.0 | Stripe SDK |
| `python-dateutil` | 2.8.2 | Date utilities |
| `httpx` | 0.28.1 | Async HTTP client (Tharwatt API) |
| `nats-py` | 2.9.0 | NATS messaging |
| `python-dotenv` | 1.0.1 | Environment variables |
| `apscheduler` | 3.10.4 | Job scheduling |
| `structlog` | >=24.1.0 | Structured logging |

### Shared Libraries

| Library | Purpose |
|---------|---------|
| `shared.middleware` | `RequestLoggingMiddleware`, `TenantContextMiddleware`, `setup_cors` |
| `shared.observability.middleware` | `ObservabilityMiddleware` |
| `shared.errors_py` | `setup_exception_handlers`, `add_request_id_middleware` |
| `shared.middleware.security_headers` | `setup_security_headers` |
| `auth.dependencies` | `get_current_active_user`, `require_roles`, `api_key_auth` |

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection (asyncpg) | `postgresql+asyncpg://user:pass@pgbouncer:6432/sahool?sslmode=require` |
| `NATS_URL` | NATS server URL | `nats://nats:4222` |
| `REDIS_URL` | Redis URL (for rate limiting) | `redis://redis:6379` |

### Payment Provider Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `STRIPE_API_KEY` | Stripe secret key | For Stripe payments |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | For Stripe webhooks |
| `THARWATT_BASE_URL` | Tharwatt API base URL | For Tharwatt payments |
| `THARWATT_API_KEY` | Tharwatt API key | For Tharwatt payments |
| `THARWATT_MERCHANT_ID` | Tharwatt merchant ID | For Tharwatt payments |
| `THARWATT_WEBHOOK_SECRET` | Tharwatt HMAC secret | For Tharwatt webhooks |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8089` | Service port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `production` | Environment (development/production) |
| `DEFAULT_CURRENCY` | `USD` | Default currency |
| `YER_EXCHANGE_RATE` | `250` | USD to YER exchange rate |
| `DB_POOL_SIZE` | `5` (dev) / `20` (prod) | Connection pool size |
| `DB_MAX_OVERFLOW` | `10` (dev) / `40` (prod) | Pool overflow |
| `DB_POOL_TIMEOUT` | `30` | Pool connection timeout |
| `DB_POOL_RECYCLE` | `3600` | Connection recycle time |

### Database Fallback Variables

If `DATABASE_URL` is not set, these are used:

| Variable | Default |
|----------|---------|
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `postgres` |
| `POSTGRES_DB` | `sahool_billing` |

### Missing Environment Variables

The following variables are referenced in docker-compose but may need explicit documentation:

1. **JWT_SECRET_KEY** - Not directly used in billing-core but may be needed by shared auth module
2. **JWT_ALGORITHM** - Not directly used in billing-core but may be needed by shared auth module

---

## Bugs and Recommended Fixes

### Critical Issues

#### 1. Webhook Handlers Use In-Memory Storage Instead of Database

**Location**: `main.py` lines 2533-2596 (Tharwatt webhook), 2667-2745 (Stripe webhook)

**Problem**: The webhook handlers reference `PAYMENTS`, `INVOICES`, and `SUBSCRIPTIONS` dictionaries (in-memory storage) instead of using the `BillingRepository` database layer. This means webhook callbacks will fail to update actual database records.

**Current Code:**
```python
# Tharwatt webhook - uses in-memory PAYMENTS dict
for p in PAYMENTS.values():
    if p.payment_id == payload.reference:
        payment = p
        break
```

**Recommended Fix:**
```python
# Should use database repository
from .database import get_db_context

async with get_db_context() as db:
    repo = BillingRepository(db)
    payment = await repo.payments.get_by_id(uuid.UUID(payload.reference))
    if payment:
        if payload.status == "completed":
            await repo.payments.mark_succeeded(payment.id)
            # Update invoice...
```

**Impact**: HIGH - Payment confirmations from webhooks will not persist

---

#### 2. Reports API Uses In-Memory Storage

**Location**: `main.py` lines 2755-2832

**Problem**: `get_revenue_report()` and `get_subscriptions_report()` use `INVOICES`, `SUBSCRIPTIONS`, and `TENANTS` dictionaries instead of database queries.

**Recommended Fix**: Use `BillingRepository` methods like:
- `repo.invoices.get_total_revenue()`
- `repo.subscriptions.count_by_status()`
- `repo.subscriptions.count_by_plan()`

---

#### 3. PlanRepository.list_all() Filter Bug

**Location**: `repository.py` line 106

**Problem**: Boolean comparison uses `is True` instead of `== True`, which compares identity rather than value in SQLAlchemy.

**Current Code:**
```python
if active_only:
    query = query.where(Plan.is_active is True)  # BUG: identity comparison
```

**Recommended Fix:**
```python
if active_only:
    query = query.where(Plan.is_active == True)  # or: Plan.is_active.is_(True)
```

**Same Issue**: `TenantRepository.list_all()` line 245, `TenantRepository.count_total()` line 281

---

### Medium Issues

#### 4. Missing phone_number in CreatePaymentRequest

**Location**: `main.py` line 568

**Problem**: `CreatePaymentRequest` does not include `phone_number` field, but it's needed for Tharwatt payments.

**Current Code:**
```python
class CreatePaymentRequest(BaseModel):
    invoice_id: str
    amount: Decimal
    method: PaymentMethod
    stripe_token: str | None = None
    # Missing: phone_number for Tharwatt
```

**Recommended Fix:**
```python
class CreatePaymentRequest(BaseModel):
    invoice_id: str
    amount: Decimal
    method: PaymentMethod
    stripe_token: str | None = None
    phone_number: str | None = None  # Required for Tharwatt
```

---

#### 5. Overage Calculation Uses In-Memory USAGE_RECORDS

**Location**: `main.py` lines 1369-1429

**Problem**: `calculate_overage_charges()` uses in-memory `USAGE_RECORDS` dict instead of querying the database.

**Recommended Fix**: Accept database session and query usage from `repo.usage_records.get_usage_summary()`.

---

#### 6. generate_invoice() Uses Deprecated Pattern

**Location**: `main.py` lines 1432-1476

**Problem**: Uses in-memory `PLANS` dict and deprecated `generate_invoice_number()`.

**Recommended Fix**: Mark as deprecated or refactor to accept database-fetched plan and use async `get_next_invoice_number()`.

---

### Low Issues

#### 7. Version Mismatch

**Locations**:
- `main.py` declares version `15.6.0` in app title
- `/healthz` returns `16.0.0`
- `/readyz` returns `16.0.0`
- Dockerfile labels `15.4.0`

**Recommended Fix**: Standardize version across all locations. Use environment variable or shared constant.

---

#### 8. Deprecation Warning for datetime.utcnow()

**Location**: Multiple places in `models.py` and `repository.py`

**Problem**: `datetime.utcnow()` is deprecated in Python 3.12+. Should use `datetime.now(UTC)`.

**Current Code:**
```python
default=datetime.utcnow
```

**Recommended Fix:**
```python
from datetime import UTC, datetime
default=lambda: datetime.now(UTC)
```

---

#### 9. Missing Error Handling for Subscription Update

**Location**: `main.py` line 1856

**Problem**: If `update_data` is empty (no changes requested), the response returns an unchanged subscription without informing the user.

**Recommended Fix**: Return early with message "No changes requested" or similar.

---

### Security Considerations

#### 10. Auth Fallback in Development Mode

**Location**: `main.py` lines 106-128

**Note**: The auth fallback allows unauthenticated access in development mode. This is intentional but should be clearly documented and never enabled in production.

**Mitigation**: The code properly checks `ENVIRONMENT` and logs critical warning if auth module unavailable in production.

---

## Summary

The billing-core service is a well-structured FastAPI application with comprehensive billing functionality. The main issues are:

1. **Critical**: Webhook handlers don't persist to database (use in-memory dicts)
2. **Critical**: Reports use in-memory storage instead of database
3. **Medium**: Boolean comparison bug in repository filters
4. **Medium**: Missing phone_number in payment request model
5. **Low**: Version inconsistencies

After fixing the critical webhook and reports issues, the service will be production-ready for payment processing.
