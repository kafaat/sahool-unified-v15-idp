# Supply Chain Service | خدمة سلسلة التوريد

Connects farmers to agricultural suppliers for product browsing, order management, and auto-purchasing based on advisory system recommendations.

**Port:** 8230 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The Supply Chain Service bridges the gap between agronomic recommendations and procurement. When the advisory service recommends a fertilizer or pesticide, this service enables farmers to compare suppliers, request quotes, and place orders automatically. It maintains a product catalog, supplier directory with proximity search, and a full order lifecycle with delivery tracking.

Key capabilities:
- Product catalog browsing (seeds, fertilizers, pesticides, equipment)
- Supplier discovery by location and rating
- Quote requests and supplier comparison
- Order creation, tracking, and cancellation
- Auto-purchase triggered by advisory recommendation events
- Bulk purchase planning
- Real-time NATS event integration for automated workflows
- Bilingual Arabic / English support throughout

---

## Architecture

```
Supply Chain Service (8230)
├── src/api/endpoints/
│   ├── products.py       — Product catalog CRUD
│   ├── suppliers.py      — Supplier management and search
│   ├── orders.py         — Order lifecycle management
│   └── auto_purchase.py  — Automated purchasing logic
├── src/suppliers/
│   ├── finder.py         — Proximity and rating search
│   └── integrations.py   — External supplier API connectors
├── src/utils/
│   └── notifications.py  — Notification hooks
└── src/core/config.py    — Settings (Pydantic BaseSettings)

External dependencies:
├── PostgreSQL   — Orders and catalog persistence
├── Redis        — Caching (supplier search results, quotes)
├── NATS         — Advisory recommendation subscription
├── notification-service (8110) — Order status notifications
└── payment-gateway (configurable) — Payment processing
```

The lifespan manager initialises asyncpg, NATS, and Redis connection pools on startup and closes them gracefully on shutdown.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Readiness probe (DB, NATS, Redis status) |
| GET | `/health` | Combined health check |

### Products

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/products` | List products (filter by category, crop type) |
| GET | `/api/v1/products/{id}` | Get product details |
| GET | `/api/v1/products/search` | Full-text product search |

### Suppliers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/suppliers` | List all suppliers |
| GET | `/api/v1/suppliers/{id}` | Get supplier details |
| GET | `/api/v1/suppliers/nearby` | Find suppliers within radius (default 50 km) |
| POST | `/api/v1/suppliers/{id}/quote` | Request price quote from supplier |

### Orders

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/orders` | Create a new order |
| GET | `/api/v1/orders` | List orders (tenant-scoped) |
| GET | `/api/v1/orders/{id}` | Get order details |
| POST | `/api/v1/orders/{id}/cancel` | Cancel an order |
| GET | `/api/v1/orders/{id}/track` | Real-time delivery tracking |

### Auto-Purchase

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auto-purchase` | Execute auto-purchase from advisory recommendation |
| POST | `/api/v1/auto-purchase/compare` | Compare supplier options for a recommendation |
| POST | `/api/v1/auto-purchase/bulk` | Bulk purchase across multiple fields/recommendations |

---

## NATS Events

### Publishes

| Subject | Trigger |
|---------|---------|
| `sahool.{tenant}.order.created` | New order placed |
| `sahool.{tenant}.order.confirmed` | Order confirmed by supplier |
| `sahool.{tenant}.order.shipped` | Order dispatched |
| `sahool.{tenant}.order.delivered` | Order delivered |
| `sahool.{tenant}.order.cancelled` | Order cancelled |

### Subscribes

| Subject | Purpose |
|---------|---------|
| `sahool.{tenant}.advisory.recommendation` | Trigger auto-purchase evaluation |
| `sahool.{tenant}.field.alert` | High-severity alerts may trigger emergency purchases |

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8230` | No | Service port |
| `DATABASE_URL` | - | Yes | PostgreSQL connection string |
| `NATS_URL` | - | No | NATS server URL |
| `REDIS_URL` | - | No | Redis URL |
| `REDIS_PASSWORD` | - | No | Redis auth password |
| `PAYMENT_GATEWAY_URL` | - | No | Payment processor endpoint |
| `DELIVERY_SERVICE_URL` | - | No | Delivery tracking service |
| `NOTIFICATION_SERVICE_URL` | `http://notification-service:8110` | No | Notification endpoint |
| `AUTO_PURCHASE_ENABLED` | `true` | No | Enable auto-purchase feature |
| `SUPPLIER_SEARCH_RADIUS_KM` | `50` | No | Default proximity search radius |
| `DB_MIN_CONNECTIONS` | `2` | No | asyncpg pool min size |
| `DB_MAX_CONNECTIONS` | `10` | No | asyncpg pool max size |
| `CORS_ORIGINS` | `http://localhost:3000` | No | Allowed CORS origins |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |
| `ENVIRONMENT` | `development` | No | Environment name |

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL async driver
- **nats-py** — NATS event subscription and publishing
- **redis.asyncio** — Redis caching
- **structlog** — Structured JSON logging
- **Pydantic v2** — Data validation

---

## Related Services

- **advisory-service** (8093) — Recommendation events trigger auto-purchase
- **logistics-service** (8167) — Delivery of purchased supplies
- **notification-service** (8110) — Order status notifications to farmers
- **billing-core** (8089) — Payment processing integration
- **inventory-service** (8116) — Stock updates after order delivery
