# Drone Service

**Port**: 8126 | **Type**: Python (FastAPI) | **Version**: 16.0.0

Drone integration and flight management service. Handles drone registration, autonomous flight planning, mission execution, Variable Rate Application (VRA), and telemetry for precision agriculture operations.

---

## Overview

`drone-service` provides the SAHOOL platform with a unified interface for managing agricultural drones. It supports MAVLink-compatible drone hardware, plans autonomous survey and spray missions, computes VRA prescription maps from NDVI data, and streams real-time telemetry to the platform. The service is backed by PostgreSQL and publishes drone lifecycle and mission events to NATS.

---

## Architecture

```
FastAPI Application
    ├── API Router: /api/v1/drones    (registration, status)
    ├── API Router: /api/v1/flights   (flight planning and execution)
    ├── API Router: /api/v1/missions  (mission management)
    ├── API Router: /api/v1/vra       (Variable Rate Application maps)
    └── Middleware
        ├── CORS
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
| GET | `/readyz` | Readiness probe (database + NATS) |
| GET | `/health` | Comprehensive status check |
| GET | `/metrics` | Prometheus metrics (plaintext) |

### Drone Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/drones` | Register a new drone |
| GET | `/api/v1/drones` | List drones (tenant-scoped) |
| GET | `/api/v1/drones/{drone_id}` | Get drone status and specs |
| PUT | `/api/v1/drones/{drone_id}` | Update drone configuration |
| DELETE | `/api/v1/drones/{drone_id}` | Deregister drone |
| GET | `/api/v1/drones/{drone_id}/telemetry` | Latest telemetry snapshot |

### Flight Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/flights` | Create a flight plan |
| GET | `/api/v1/flights` | List flights |
| GET | `/api/v1/flights/{flight_id}` | Get flight details |
| PUT | `/api/v1/flights/{flight_id}/start` | Start a planned flight |
| PUT | `/api/v1/flights/{flight_id}/abort` | Emergency abort flight |
| GET | `/api/v1/flights/{flight_id}/waypoints` | Get flight waypoints |

### Mission Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/missions` | Create a new mission |
| GET | `/api/v1/missions` | List missions |
| GET | `/api/v1/missions/{mission_id}` | Mission details and status |
| PUT | `/api/v1/missions/{mission_id}/execute` | Execute a planned mission |
| GET | `/api/v1/missions/{mission_id}/report` | Mission completion report |

### Variable Rate Application (VRA)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/vra/maps` | Generate VRA prescription map from NDVI |
| GET | `/api/v1/vra/maps/{field_id}` | Get current VRA map for a field |
| POST | `/api/v1/vra/execute` | Execute VRA spray mission |

---

## NATS Events Published

| Subject | Trigger |
|---------|---------|
| `sahool.drone.registered` | New drone registered |
| `sahool.drone.flight_started` | Flight begins |
| `sahool.drone.flight_completed` | Flight ends successfully |
| `sahool.drone.flight_aborted` | Flight aborted (emergency) |
| `sahool.drone.mission_completed` | Mission finalized |
| `sahool.drone.telemetry_update` | Real-time telemetry snapshot |
| `sahool.drone.vra_map_generated` | VRA prescription map ready |

---

## Supported Drone Types

- Fixed-wing (survey missions, large area coverage)
- Multi-rotor (spray missions, precision application)
- Hybrid VTOL (mixed operations)

---

## Mission Types

| Type | Description |
|------|-------------|
| `survey` | Aerial imagery for NDVI and crop health |
| `spray` | Pesticide or fertilizer application |
| `inspection` | Visual field inspection |
| `seeding` | Direct seeding applications |

---

## Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `drone_service_up` | gauge | Service health (always 1) |
| `drone_service_db_up` | gauge | Database connection status |
| `drone_service_nats_up` | gauge | NATS connection status |
| `drone_service_info` | gauge | Version label metric |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8126` | HTTP listen port |
| `ENVIRONMENT` | `development` | `production` enforces DB SSL |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `NATS_URL` | - | NATS server URL |
| `CORS_ORIGINS` | `https://sahool.app,...` | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Dependencies

- `asyncpg` 0.31.0 for PostgreSQL async connection pool (min=2, max=10)
- `nats-py` for NATS event publishing
- `structlog` for structured JSON logging
- `shared.errors_py` for request-ID middleware and exception handling
- `shared/drone_integration/` for MAVLink integration and flight planning logic

---

## Security

- Tenant-scoped operations via `X-Tenant-Id` header
- TLS enforced for database in non-development environments
- JWT Bearer token required on all management endpoints
- Geofence enforcement prevents missions outside registered field boundaries
- Non-root container user (UID 1000)

---

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "drone-service", "version": "16.0.0"}
GET /readyz   → {"status": "ok", "database": true|false, "nats": true|false}
GET /health   → {"status": "ok|degraded", "checks": {"database": "connected|disconnected", "nats": "connected|disconnected"}}
```

---

## Related Services

- **vegetation-analysis-service** (8090) - provides NDVI data for VRA maps
- **field-management-service** (3000) - field boundary data for geofencing
- **iot-service** (8117) - drone telemetry stream integration
- **yolo26-vision-service** (8150) - processes aerial imagery for pest/disease detection
