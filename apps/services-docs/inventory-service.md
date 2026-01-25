# Inventory Service Analysis

**Service Name:** inventory-service
**Type:** Python/FastAPI
**Port:** 8116
**Version:** 1.0.0
**Status:** Active

---

## Table of Contents

1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [NATS Events](#nats-events)
4. [Database Schema](#database-schema)
5. [Core Features](#core-features)
6. [Dependencies](#dependencies)
7. [Environment Variables](#environment-variables)
8. [Issues and Recommendations](#issues-and-recommendations)

---

## Overview

The Inventory Service is a comprehensive agricultural inventory management system for the SAHOOL platform. It provides:

- **Inventory Item Management**: CRUD operations for seeds, fertilizers, pesticides, equipment, and other agricultural inputs
- **Stock Movement Tracking**: FIFO-based stock consumption, receipts, transfers, and adjustments
- **Batch/Lot Management**: Track batches with expiry dates, certifications, and quality grades
- **Warehouse Management**: Multi-warehouse support with zones, storage locations, and transfer workflows
- **Alert System**: Low stock alerts, expiry warnings, storage condition alerts
- **Analytics & Forecasting**: Consumption forecasting, ABC analysis, turnover metrics, dead stock identification
- **Application Tracking**: Field input applications with withholding period calculations
- **Supplier Management**: Track suppliers with lead times and ratings
- **Bilingual Support**: Arabic and English throughout (names, descriptions, alerts)

### Architecture

- **Database**: PostgreSQL (via SQLAlchemy async + asyncpg for main.py, Prisma ORM for service modules)
- **Messaging**: NATS for alert notifications
- **API Framework**: FastAPI
- **Authentication**: JWT via shared auth module (dependency injection ready)

---

## API Endpoints

### Health & Readiness

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with database status |
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Kubernetes readiness probe |

### Categories

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/v1/categories` | Create item category | `ItemCategoryCreate` | `ItemCategoryResponse` |

**Request Schema - ItemCategoryCreate:**
```json
{
  "name_en": "string",
  "name_ar": "string",
  "code": "string",
  "description": "string | null"
}
```

**Response Schema - ItemCategoryResponse:**
```json
{
  "id": "string",
  "name_en": "string",
  "name_ar": "string",
  "code": "string",
  "is_active": "boolean"
}
```

### Analytics Endpoints

| Method | Endpoint | Description | Query Params |
|--------|----------|-------------|--------------|
| GET | `/v1/analytics/forecast/{item_id}` | Get consumption forecast for item | `tenant_id` (required), `forecast_days` (1-365, default: 90) |
| GET | `/v1/analytics/forecasts` | Get all item forecasts | `tenant_id` (required), `category`, `low_stock_only` |
| GET | `/v1/analytics/reorder-recommendations` | Get items needing reorder | `tenant_id` (required) |
| GET | `/v1/analytics/valuation` | Get inventory valuation | `tenant_id` (required), `warehouse_id` |
| GET | `/v1/analytics/turnover` | Get turnover analysis | `tenant_id` (required), `period_days` (30-730, default: 365) |
| GET | `/v1/analytics/slow-moving` | Identify slow-moving items | `tenant_id` (required), `days_threshold` (30-365, default: 90) |
| GET | `/v1/analytics/dead-stock` | Identify dead stock | `tenant_id` (required), `days_threshold` (90-730, default: 180) |
| GET | `/v1/analytics/abc-analysis` | ABC/Pareto analysis | `tenant_id` (required) |
| GET | `/v1/analytics/seasonal-patterns/{item_id}` | Get seasonal patterns | `tenant_id` (required) |
| GET | `/v1/analytics/cost-analysis` | Analyze input costs | `tenant_id` (required), `field_id`, `crop_season_id`, `start_date`, `end_date` |
| GET | `/v1/analytics/waste-analysis` | Analyze inventory waste | `tenant_id` (required), `period_days` (30-730, default: 365) |
| GET | `/v1/analytics/dashboard` | Dashboard metrics | `tenant_id` (required) |

**Response Schema - ConsumptionForecast:**
```json
{
  "item_id": "string",
  "item_name": "string",
  "current_stock": "float",
  "avg_daily_consumption": "float",
  "avg_weekly_consumption": "float",
  "avg_monthly_consumption": "float",
  "days_until_stockout": "integer",
  "reorder_date": "date (ISO format)",
  "recommended_order_qty": "float",
  "confidence": "float (0-1)"
}
```

**Response Schema - InventoryValuation:**
```json
{
  "total_value": "float",
  "currency": "YER",
  "by_category": {"category_name": "value"},
  "by_warehouse": {"warehouse_name": "value"},
  "top_items": [
    {
      "item_id": "string",
      "item_name": "string",
      "value": "float",
      "quantity": "float",
      "unit_cost": "float",
      "percentage": "float"
    }
  ],
  "expiring_value": "float"
}
```

**Response Schema - ABC Analysis:**
```json
{
  "tenant_id": "string",
  "total_value": "float",
  "total_items": "integer",
  "a_class": {
    "items": [],
    "count": "integer",
    "percentage_of_items": "float",
    "value": "float",
    "percentage_of_value": "float"
  },
  "b_class": { "..." },
  "c_class": { "..." }
}
```

### Alert Endpoints (via alert_endpoints router)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/v1/alerts` | Get active alerts | Query: `priority`, `alert_type`, `limit`, `offset` |
| GET | `/v1/alerts/{alert_id}` | Get specific alert | - |
| GET | `/v1/alerts/summary` | Get alert statistics | - |
| POST | `/v1/alerts/{alert_id}/acknowledge` | Acknowledge alert | `{"acknowledged_by": "string"}` |
| POST | `/v1/alerts/{alert_id}/resolve` | Resolve alert | `{"resolved_by": "string", "resolution_notes": "string | null"}` |
| POST | `/v1/alerts/{alert_id}/snooze` | Snooze alert | `{"snooze_hours": "integer (1-168)"}` |
| POST | `/v1/alerts/check-now` | Trigger immediate alert check | - |
| GET | `/v1/alerts/settings` | Get alert settings | Query: `tenant_id` |
| PUT | `/v1/alerts/settings` | Update alert settings | `AlertSettingsModel` |

**Alert Types:**
- `LOW_STOCK` - Stock below reorder level
- `OUT_OF_STOCK` - Zero available quantity
- `EXPIRING_SOON` - Items expiring within threshold
- `EXPIRED` - Items already expired
- `REORDER_POINT` - Reached reorder point
- `OVERSTOCK` - Stock exceeds maximum
- `STORAGE_CONDITION` - Temperature/humidity out of range

**Alert Priorities:**
- `LOW` - In-app notification only
- `MEDIUM` - In-app + push notification
- `HIGH` - In-app + push notification
- `CRITICAL` - In-app + push + SMS notification

**Alert Statuses:**
- `ACTIVE` - New/active alert
- `ACKNOWLEDGED` - User has acknowledged
- `RESOLVED` - Issue resolved
- `SNOOZED` - Temporarily hidden

---

## NATS Events

### Published Events

| Subject | Publisher | Description | Payload |
|---------|-----------|-------------|---------|
| `sahool.alerts.inventory` | NATSPublisher | Inventory alert notification | See below |

**Alert Notification Payload:**
```json
{
  "event_type": "inventory_alert",
  "event_id": "alert_uuid",
  "source_service": "inventory-service",
  "timestamp": "ISO datetime",
  "alert": {
    "id": "string",
    "alert_type": "LOW_STOCK | OUT_OF_STOCK | ...",
    "priority": "low | medium | high | critical",
    "status": "active",
    "item_id": "string",
    "item_name": "string",
    "item_name_ar": "string",
    "title_en": "string",
    "title_ar": "string",
    "message_en": "string",
    "message_ar": "string",
    "current_value": "float",
    "threshold_value": "float",
    "recommended_action_en": "string",
    "recommended_action_ar": "string",
    "action_url": "string | null",
    "created_at": "ISO datetime"
  },
  "recipients": ["farm_manager", "owner"],
  "notification_priority": "critical | high | medium | low",
  "notification_channels": ["in_app", "push", "sms"],
  "action_template": {
    "title_en": "string",
    "title_ar": "string",
    "description_en": "string",
    "description_ar": "string",
    "urgency": "string",
    "action_url": "string | null"
  }
}
```

### Subscribed Events

The service does not currently subscribe to any NATS events. Alert checks are performed on a scheduled interval (default: hourly).

---

## Database Schema

### Primary Tables (SQLAlchemy Models)

| Table | Description |
|-------|-------------|
| `inventory_categories` | Item categories (fertilizer, pesticide, seed, etc.) |
| `inventory_warehouses` | Warehouse/storage locations |
| `inventory_suppliers` | Supplier master data |
| `inventory_items` | Main inventory item master |
| `inventory_movements` | All stock movements (receipt, issue, transfer, adjustment) |
| `inventory_transactions` | Financial transactions for inventory |

### Prisma Schema Tables

| Table | Description |
|-------|-------------|
| `inventory_items` | Core inventory item with tenant isolation |
| `inventory_movements` | Stock movement records |
| `inventory_alerts` | Alert records |
| `alert_settings` | Per-tenant alert configuration |
| `warehouses` | Warehouse definitions |
| `zones` | Zones within warehouses |
| `storage_locations` | Specific bin/shelf locations |
| `stock_transfers` | Inter-warehouse transfer records |

### Key Enums

**ItemCategory:**
- `SEEDS`, `FERTILIZER`, `PESTICIDE`, `HERBICIDE`, `FUNGICIDE`, `INSECTICIDE`
- `EQUIPMENT`, `TOOLS`, `IRRIGATION`, `PACKAGING`, `FUEL`, `OTHER`

**MovementType:**
- `PURCHASE`, `SALE`, `RETURN`, `ADJUSTMENT`, `TRANSFER`
- `WASTE`, `USAGE`, `PRODUCTION`, `RESTOCK`

**WarehouseType:**
- `MAIN`, `FIELD`, `COLD`, `CHEMICAL`, `SEED`, `FUEL`

**StorageCondition:**
- `AMBIENT`, `COOL`, `COLD`, `FROZEN`, `DRY`, `CONTROLLED`

### Database Indexes

The service uses several performance-optimized indexes:

- `idx_inventory_items_sku_tenant` - SKU lookups within tenant
- `idx_inventory_items_low_stock` - Partial index for low stock items
- `idx_inventory_items_expiry` - Partial index for expiring items
- `idx_inventory_items_barcode` - Partial index for barcode lookups
- `idx_inventory_movements_date_range` - Movement history queries
- `idx_inventory_transactions_party` - Party-related transactions

---

## Core Features

### 1. FIFO Stock Consumption

The `StockManager` implements First-In-First-Out batch consumption with transaction locking to prevent race conditions:

```python
async def consume_stock_fifo(self, item_id: str, quantity: float):
    async with self.db.tx() as transaction:
        batches = await transaction.batchlot.find_many(
            where={"itemId": item_id, "remainingQty": {"gt": 0}},
            order={"receivedDate": "asc"}
        )
        # Consume from oldest batches first
```

### 2. Inventory Analytics

**ConsumptionForecast:** Uses 90-day moving average with confidence scoring based on coefficient of variation.

**ABC Analysis (Pareto):**
- A-class: Top items representing 80% of value (~20% of items)
- B-class: Next 15% of value (~30% of items)
- C-class: Remaining 5% of value (~50% of items)

**Turnover Analysis:**
- Turnover Ratio = Cost of Goods Used / Average Inventory Value
- Velocity Classification: fast (4+ turns/year), medium (2-4), slow (0.5-2), dead (<0.5)

### 3. Alert System

The `AlertManager` checks multiple conditions:
- Low stock (50-100% of reorder = MEDIUM, 25-50% = HIGH, <25% = CRITICAL)
- Out of stock (always CRITICAL)
- Expiring items (7-30 days = MEDIUM, <7 days = HIGH, expired = CRITICAL)
- Reorder point reached
- Storage conditions (temperature/humidity out of range)

### 4. Application Tracking

The `ApplicationTracker` links inventory with field operations:
- Records input applications with FIFO batch deduction
- Calculates safe harvest dates based on withholding periods
- Tracks application methods (broadcast, band, foliar, drip, aerial, etc.)
- Supports efficacy rating and PPE tracking

### 5. Warehouse Management

The `WarehouseManager` provides:
- Multi-warehouse support with different types (main, field, cold, chemical, seed, fuel)
- Zone and bin-level storage location tracking
- Inter-warehouse stock transfers with approval workflow
- Storage condition monitoring (temperature/humidity ranges)

---

## Dependencies

### Python Packages (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | 0.27.0 | ASGI server |
| pydantic | 2.9.2 | Data validation |
| python-dotenv | 1.0.1 | Environment loading |
| sqlalchemy | >=2.0.0 | ORM (async) |
| asyncpg | >=0.29.0 | PostgreSQL async driver |
| greenlet | >=3.0.0 | Coroutine support for SQLAlchemy |
| python-dateutil | 2.8.2 | Date utilities |
| httpx | 0.28.1 | HTTP client |
| structlog | >=24.1.0 | Structured logging |

### Optional Dependencies (Not in requirements.txt)

| Package | Purpose | Notes |
|---------|---------|-------|
| nats-py | NATS messaging | Lazy import, gracefully disabled if unavailable |
| prisma | Prisma ORM | Used by service modules (inventory_service.py, stock_manager.py) |
| apscheduler | Alert scheduling | Referenced in integration docs but not in requirements |

### Shared Module Dependencies

| Module | Import Path | Purpose |
|--------|-------------|---------|
| errors_py | `shared.errors_py` | Unified error handling |
| security_headers | `shared.middleware.security_headers` | Security headers middleware |
| rate_limiter | `middleware.rate_limiter` | Rate limiting (optional) |

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db?sslmode=require` |

### Conditional Variables

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `ALLOW_DEV_DEFAULTS` | Enable fallback database config | `false` | Only for local development |
| `POSTGRES_HOST` | Database host | `localhost` | Only when ALLOW_DEV_DEFAULTS=true |
| `POSTGRES_PORT` | Database port | `5432` | Only when ALLOW_DEV_DEFAULTS=true |
| `POSTGRES_USER` | Database user | `postgres` | Only when ALLOW_DEV_DEFAULTS=true |
| `POSTGRES_PASSWORD` | Database password | `postgres` | Only when ALLOW_DEV_DEFAULTS=true |
| `POSTGRES_DB` | Database name | `sahool_inventory` | Only when ALLOW_DEV_DEFAULTS=true |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8116` |
| `SQL_ECHO` | Enable SQL logging | `false` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:3001,http://localhost:8080` |
| `CORS_ORIGINS` | Alternative CORS config | Same as above |
| `REDIS_URL` | Redis URL for rate limiting | `null` |
| `NATS_URL` | NATS server URL | `nats://nats:4222` |

### Missing Environment Variables

The following variables should be documented but are not handled:

| Variable | Should Be | Purpose |
|----------|-----------|---------|
| `DATABASE_URL_DIRECT` | Optional | Direct database URL for Prisma migrations (bypasses PgBouncer) |
| `JWT_SECRET_KEY` | Required | JWT authentication (if using shared auth) |
| `JWT_ALGORITHM` | Optional | JWT algorithm (default: HS256) |
| `LOG_LEVEL` | Optional | Logging level |
| `ENVIRONMENT` | Optional | Environment name (development/staging/production) |

---

## Issues and Recommendations

### Critical Issues

#### 1. Dual ORM Architecture Mismatch

**Issue:** The service uses both SQLAlchemy (main.py, models/inventory.py) and Prisma (inventory_service.py, stock_manager.py, etc.). These are incompatible ORMs with different schemas.

**Files Affected:**
- `/home/user/sahool-unified-v15-idp/apps/services/inventory-service/src/main.py` - Uses SQLAlchemy
- `/home/user/sahool-unified-v15-idp/apps/services/inventory-service/src/inventory_service.py` - Uses Prisma
- `/home/user/sahool-unified-v15-idp/apps/services/inventory-service/src/stock_manager.py` - Uses Prisma

**Impact:**
- The `InventoryService` and `StockManager` classes cannot work with the SQLAlchemy session from `main.py`
- Routes defined in main.py only use analytics (which works with SQLAlchemy), but service/stock operations won't work
- Schema mismatch between SQLAlchemy models and Prisma schema

**Recommendation:**
- Standardize on one ORM (recommend SQLAlchemy for consistency with shared modules)
- OR properly integrate both with separate sessions and migration strategies
- Add integration tests to verify end-to-end functionality

#### 2. Alert Router Not Included

**Issue:** The `alert_endpoints.py` defines a router but it's never included in `main.py`.

**File:** `/home/user/sahool-unified-v15-idp/apps/services/inventory-service/src/main.py`

**Impact:** Alert endpoints (`/v1/alerts/*`) are not accessible.

**Recommendation:** Add to main.py:
```python
from .alert_endpoints import router as alert_router, init_alert_manager
from .alert_manager import AlertManager

# After app creation
app.include_router(alert_router)

# In lifespan
app.state.alert_manager = AlertManager(inventory_db={}, alerts_db={})
init_alert_manager(app.state.alert_manager)
```

#### 3. Missing Prisma Client Dependency

**Issue:** Prisma is used in multiple files but not in requirements.txt.

**Files Using Prisma:**
- `inventory_service.py` - `from prisma import Prisma`
- `stock_manager.py` - `from prisma import Prisma`
- `warehouse_manager.py` - Uses `self.db.warehouse`, `self.db.zone`, etc.
- `application_tracker.py` - Uses `self.db.inventoryitem`, `self.db.batchlot`, etc.

**Impact:** Container builds may fail or runtime errors will occur.

**Recommendation:** Add to requirements.txt:
```
prisma>=0.11.0
```

#### 4. Missing NATS Dependency

**Issue:** `nats-py` package is used but not in requirements.txt.

**File:** `/home/user/sahool-unified-v15-idp/apps/services/inventory-service/src/nats_publisher.py`

**Impact:** NATS functionality silently disabled, alerts won't be published.

**Recommendation:** Add to requirements.txt:
```
nats-py>=2.6.0
```

### Medium Issues

#### 5. In-Memory Alert Storage

**Issue:** AlertManager uses in-memory dictionaries for storage:
```python
self.inventory_db = inventory_db or {}
self.alerts_db = alerts_db or {}
```

**Impact:**
- Alerts lost on service restart
- No persistence across instances
- Not suitable for horizontal scaling

**Recommendation:** Use the Prisma `InventoryAlert` model for persistence.

#### 6. Missing APScheduler Dependency

**Issue:** Integration documentation references APScheduler for alert scheduling, but it's not in requirements.txt.

**File:** `/home/user/sahool-unified-v15-idp/apps/services/inventory-service/src/alert_integration.py`

**Impact:** Scheduled alert checks won't work without manual setup.

**Recommendation:** Add to requirements.txt:
```
apscheduler>=3.10.0
```

#### 7. Inconsistent Model Field Naming

**Issue:** Mix of camelCase and snake_case in Pydantic models (models.py):
- `unitSize`, `unitCost`, `reorderLevel` (camelCase)
- `name_ar`, `description_ar` (snake_case)

**Impact:** API inconsistency, confusing for clients.

**Recommendation:** Standardize on snake_case with `alias` for API compatibility if needed.

#### 8. Analytics Query Uses Wrong Model Reference

**Issue:** In `inventory_analytics.py`, the query references `InventoryItem.is_active` but the comparison should be `InventoryItem.is_active == True` (explicit boolean comparison for SQLAlchemy).

**File:** `/home/user/sahool-unified-v15-idp/apps/services/inventory-service/src/inventory_analytics.py`
```python
# Line 218
InventoryItem.is_active is True,  # Should be == True
```

**Impact:** May cause unexpected query behavior.

### Low Issues

#### 9. Hardcoded Currency

**Issue:** Currency hardcoded as "YER" (Yemeni Rial) in multiple places.

**Files:** `inventory_analytics.py`, `inventory_service.py`

**Recommendation:** Make configurable via environment or tenant settings.

#### 10. Missing Input Validation

**Issue:** Some endpoints don't validate item_id format (should be UUID).

**Recommendation:** Add UUID validation to path parameters.

#### 11. UTC vs Timezone-Aware Datetimes

**Issue:** Mix of `datetime.utcnow()` (deprecated) and `datetime.now(UTC)`.

**Files:** Multiple files use both patterns.

**Recommendation:** Standardize on `datetime.now(UTC)` or `datetime.now(timezone.utc)`.

### Recommended Fixes Priority

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| P0 | Add missing dependencies (prisma, nats-py, apscheduler) | Low | High |
| P0 | Include alert router in main.py | Low | High |
| P1 | Resolve ORM architecture (choose one) | High | Critical |
| P1 | Implement persistent alert storage | Medium | High |
| P2 | Standardize field naming conventions | Medium | Medium |
| P2 | Fix boolean comparison in analytics | Low | Low |
| P3 | Make currency configurable | Low | Low |
| P3 | Add UUID validation | Low | Low |

---

## File Structure

```
apps/services/inventory-service/
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── README.md
├── ALERT_SYSTEM_README.md
├── ANALYTICS_IMPLEMENTATION.md
├── APPLICATION_TRACKING.md
├── FILES_CREATED.md
├── IMPLEMENTATION_SUMMARY.md
├── test_application_tracker.http
├── migrations/
│   ├── README.md
│   ├── __init__.py
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── __init__.py
│       └── add_performance_indexes.py
├── prisma/
│   └── schema.prisma
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── models.py                  # Pydantic models for API
│   ├── models/
│   │   ├── __init__.py
│   │   └── inventory.py           # SQLAlchemy ORM models
│   ├── inventory_service.py       # Business logic (Prisma)
│   ├── stock_manager.py           # FIFO stock operations (Prisma)
│   ├── warehouse_manager.py       # Warehouse operations (Prisma)
│   ├── application_tracker.py     # Field application tracking (Prisma)
│   ├── inventory_analytics.py     # Analytics & forecasting (SQLAlchemy)
│   ├── alert_manager.py           # Alert logic (in-memory)
│   ├── alert_endpoints.py         # Alert API router
│   ├── alert_integration.py       # Integration helpers
│   └── nats_publisher.py          # NATS event publishing
└── tests/
    ├── README.md
    ├── __init__.py
    ├── conftest.py
    ├── test_api_endpoints.py
    ├── test_inventory_analytics.py
    └── test_inventory_service.py
```

---

## Kong Gateway Configuration

```yaml
services:
  - name: inventory-service
    host: inventory-service
    port: 8116
    routes:
      - name: inventory-api-v1
        paths:
          - /api/v1/inventory
        strip_path: true
      - name: inventory-direct
        paths:
          - /inventory
        strip_path: true
```

---

## Quick Start

```bash
# Set required environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/sahool_inventory"

# Optional: Enable development defaults
export ALLOW_DEV_DEFAULTS=true

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8116 --reload

# Or via Docker
docker build -t inventory-service .
docker run -p 8116:8116 -e DATABASE_URL="..." inventory-service
```

---

## Testing

```bash
# Run all tests
pytest apps/services/inventory-service/tests/ -v

# Run with coverage
pytest apps/services/inventory-service/tests/ --cov=src --cov-report=html

# Run specific test file
pytest apps/services/inventory-service/tests/test_inventory_analytics.py -v
```

---

*Generated: 2026-01-25*
*Source: /home/user/sahool-unified-v15-idp/apps/services/inventory-service/*
