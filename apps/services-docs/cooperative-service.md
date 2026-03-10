# Cooperative Service

**Port**: 8127 | **Type**: Python (FastAPI) | **Version**: 16.0.0

Multi-farm cooperative management service. Enables groups of smallholder farmers to pool resources, share advisory, coordinate bulk purchasing, and jointly access markets and financial services through a tenant-isolated API.

---

## Overview

`cooperative-service` manages the formation and operation of agricultural cooperatives on the SAHOOL platform. It provides CRUD operations for cooperatives, membership management, resource sharing (equipment, water, seeds), joint market access, and cooperative-level aggregated analytics. The service is backed by PostgreSQL (asyncpg connection pool) and publishes lifecycle events to NATS. The shared `shared/cooperatives/` Python module provides the core domain logic.

---

## Architecture

```
FastAPI Application
    ├── API Router: /api/v1/cooperatives   (CRUD)
    └── Middleware
        ├── CORS (configurable origins)
        ├── Request ID injection
        └── Unified exception handling
            |
     asyncpg pool  →  PostgreSQL (sslmode=require in production)
     nats.connect  →  NATS JetStream
```

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe (database + NATS flags) |
| GET | `/health` | Comprehensive status (ok / degraded) |
| GET | `/metrics` | Prometheus metrics (plaintext) |
| GET | `/` | Service information root |

### Cooperative Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/cooperatives` | Create a new cooperative |
| GET | `/api/v1/cooperatives` | List cooperatives (tenant-scoped) |
| GET | `/api/v1/cooperatives/{id}` | Get cooperative details |
| PUT | `/api/v1/cooperatives/{id}` | Update cooperative |
| DELETE | `/api/v1/cooperatives/{id}` | Delete cooperative |

### Membership

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/cooperatives/{id}/members` | Add member to cooperative |
| GET | `/api/v1/cooperatives/{id}/members` | List members |
| DELETE | `/api/v1/cooperatives/{id}/members/{farmer_id}` | Remove member |

### Resource Sharing

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/cooperatives/{id}/resources` | List shared resources |
| POST | `/api/v1/cooperatives/{id}/resources` | Register shared resource |

### Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/cooperatives/{id}/analytics` | Aggregate stats for cooperative |

---

## NATS Events Published

| Subject | Trigger |
|---------|---------|
| `sahool.cooperative.created` | New cooperative created |
| `sahool.cooperative.member_added` | Member joins |
| `sahool.cooperative.member_removed` | Member leaves |
| `sahool.cooperative.resource_shared` | Resource registered for sharing |

---

## Data Model (Core Fields)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Cooperative identifier |
| `name` | string | Cooperative name |
| `name_ar` | string | Arabic name |
| `tenant_id` | UUID | Multi-tenancy scope |
| `region` | string | Geographic region |
| `status` | enum | `active`, `pending`, `suspended` |
| `member_count` | int | Current member count |
| `created_at` | timestamp | Registration timestamp |

---

## Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `cooperative_service_up` | gauge | Service health (always 1 if running) |
| `cooperative_service_db_up` | gauge | Database connection status |
| `cooperative_service_nats_up` | gauge | NATS connection status |
| `cooperative_service_info` | gauge | Version label metric |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8127` | HTTP listen port |
| `ENVIRONMENT` | `development` | `production` enforces DB SSL |
| `DATABASE_URL` | - | PostgreSQL connection (sslmode=require in prod) |
| `NATS_URL` | - | NATS server URL |
| `CORS_ORIGINS` | `https://sahool.app,...` | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Dependencies

- `asyncpg` 0.31.0 for PostgreSQL async access (pool min=2, max=10)
- `nats-py` for NATS connectivity
- `structlog` for structured JSON logging
- `shared.errors_py` for request-ID middleware and exception handling
- `shared/cooperatives/` for domain business logic

---

## Security

- **Authentication**: DELETE endpoints (`DELETE /{coop_id}`, `DELETE /{coop_id}/members/{member_id}`) require JWT authentication via `get_current_user` dependency
- Multi-tenant isolation enforced via `tenant_id` scoping on all queries
- `X-Tenant-Id` header required on all protected endpoints
- TLS enforced for database connections in non-development environments (`sslmode=require`)
- Non-root container user (UID 1000)
- Unified error handling via `shared.errors_py` (`setup_exception_handlers`, `add_request_id_middleware`)

---

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "cooperative-service", "version": "16.0.0"}
GET /readyz   → {"status": "ok", "database": true|false, "nats": true|false}
GET /health   → {"status": "ok|degraded", "checks": {"database": "connected|disconnected", "nats": "connected|disconnected"}}
```

---

## Related Services

- **field-management-service** (3000) - field data for cooperative farms
- **marketplace-service** (3010) - joint market access for cooperatives
- **billing-core** (8089) - cooperative billing and invoicing
