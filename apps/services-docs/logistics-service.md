# Logistics Service | خدمة اللوجستيات الزراعية

Agricultural logistics management service for the SAHOOL platform covering fleet, storage, harvest collection, route optimization, and shipment tracking.

**Port:** 8167 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The Logistics Service coordinates the movement of harvested produce from fields to storage facilities and onward to buyers. It manages vehicle fleets, cold and dry storage facilities, harvest collection scheduling, nearest-neighbor route optimization, and end-to-end shipment tracking.

Key capabilities:
- Fleet management with real-time GPS vehicle tracking
- Multi-type storage facility management (cold, dry, grain silo, controlled atmosphere)
- Priority-based harvest collection scheduling
- Route optimization using nearest-neighbor algorithm
- Shipment lifecycle tracking with status timestamps
- Bilingual responses (Arabic / English) throughout all payloads
- Multi-tenant with JWT-based tenant isolation; falls back to `X-Tenant-Id` header

---

## Architecture

```
Mobile App / Admin Portal
        |
   Kong Gateway
        |
Logistics Service (8167)
├── In-Memory Storage (CI/test mode)
├── PostgreSQL (production persistence)
├── NATS JetStream (event publishing)
└── Integration points:
    ├── field-management-service (field/crop data)
    ├── equipment-service (vehicle cross-reference)
    ├── notification-service (delivery alerts)
    └── inventory-service (storage inventory)
```

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Kubernetes readiness probe |
| GET | `/health` | Combined health check |

### Fleet Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/vehicles` | List vehicles (filter by type, status) |
| GET | `/api/v1/vehicles/{id}` | Get vehicle details |
| POST | `/api/v1/vehicles` | Register a new vehicle |
| PUT | `/api/v1/vehicles/{id}` | Update vehicle information |
| POST | `/api/v1/vehicles/{id}/location` | Update GPS coordinates and fuel level |

Vehicle types: `truck`, `pickup`, `refrigerated_truck`, `van`, `motorcycle`

### Storage Facilities

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/storage-facilities` | List all facilities |
| GET | `/api/v1/storage-facilities/{id}` | Get facility details with capacity |
| POST | `/api/v1/storage-facilities` | Create a new storage facility |
| POST | `/api/v1/storage-facilities/{id}/conditions` | Update temperature, humidity, status |

Storage types: `cold_storage`, `dry_storage`, `grain_silo`, `controlled_atmosphere`

### Harvest Collections

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/collections` | List collection schedules |
| POST | `/api/v1/collections` | Schedule a new harvest collection |
| POST | `/api/v1/collections/{id}/assign` | Assign a vehicle to a collection |
| POST | `/api/v1/collections/{id}/status` | Update collection status |

Status flow: `scheduled` → `collecting` → `in_transit` → `delivered`
Priority levels: `low`, `medium`, `high`, `urgent`

### Route Optimization

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/routes/optimize` | Generate optimized collection route (nearest-neighbor) |

The optimizer returns ordered waypoints with estimated distance, duration per leg, and total trip metrics including return-to-base.

### Shipments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/shipments` | List shipments |
| POST | `/api/v1/shipments` | Create a shipment |
| POST | `/api/v1/shipments/{id}/status` | Update shipment status with location |

### Statistics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/stats` | Logistics statistics (fleet utilization, collections, shipments) |

---

## NATS Events Published

All subjects follow the pattern `sahool.{tenant_id}.logistics.{entity}.{action}`:

| Subject | Trigger |
|---------|---------|
| `sahool.{tenant_id}.logistics.vehicle.created` | New vehicle registered |
| `sahool.{tenant_id}.logistics.vehicle.location` | GPS location updated |
| `sahool.{tenant_id}.logistics.facility.created` | New storage facility added |
| `sahool.{tenant_id}.logistics.collection.scheduled` | Collection scheduled |
| `sahool.{tenant_id}.logistics.collection.status_changed` | Collection status update |
| `sahool.{tenant_id}.logistics.shipment.created` | New shipment created |
| `sahool.{tenant_id}.logistics.shipment.status_changed` | Shipment status update |

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8167` | No | Service port (note: README shows 8131 — canonical port is 8167) |
| `DATABASE_URL` | - | Yes (prod) | PostgreSQL connection string |
| `NATS_URL` | - | No | NATS server URL |
| `REDIS_URL` | - | No | Redis connection URL |
| `CORS_ORIGINS` | `https://sahool.io,...` | No | Comma-separated allowed origins |
| `ENVIRONMENT` | `development` | No | Environment name |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL async driver
- **nats-py** — NATS event publishing
- **Pydantic v2** — Data validation
- `shared.auth.dependencies` — JWT authentication
- `shared.errors_py` — Unified error handling
- `shared.middleware.security_headers` — HTTP security headers

---

## Related Services

- **field-management-service** (3000) — Field and crop data source
- **equipment-service** (8101) — Equipment cross-reference
- **notification-service** (8110) — Delivery notifications
- **inventory-service** (8116) — Storage inventory management
- **supply-chain-service** (8230) — Downstream supply chain
