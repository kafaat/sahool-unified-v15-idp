# NDVI Processor | معالج NDVI

Satellite imagery NDVI processing service supporting Sentinel-2, Landsat, and MODIS sources with background job management, time series analysis, anomaly detection, and composite generation.

**Port:** 8118 | **Type:** Python / FastAPI | **Version:** 16.0.0

> **Deprecation Notice**: This service is being migrated to `vegetation-analysis-service` (port 8090). Sunset target: v17.0.0. New integrations should use `vegetation-analysis-service`.

---

## Overview

The NDVI Processor handles the compute-intensive pipeline of converting raw satellite imagery into actionable vegetation health indicators. It processes multi-source satellite data through atmospheric correction and cloud masking, computes NDVI indices, and persists results for downstream consumption by advisory, irrigation, and crop health services.

Key capabilities:
- Background job queue for asynchronous NDVI processing (non-blocking HTTP)
- Multi-source satellite support: Sentinel-2, Landsat 8/9, MODIS
- Atmospheric correction and cloud masking steps (simulated in current implementation)
- Per-field NDVI statistics (mean, min, max, std dev)
- Time series retrieval with date range filtering
- Change analysis between two dates with zone mapping
- Seasonal analysis (by crop year / calendar year)
- Anomaly detection vs historical baseline
- Monthly composite generation (mean, median, max-NDVI methods)
- Export in GeoTIFF, PNG, CSV, and JSON formats
- Persistent storage via asyncpg with in-memory fallback
- NATS event publishing on job completion

---

## Architecture

```
NDVI Processor (8118)
├── src/main.py        — FastAPI app, endpoints, background task dispatch
├── src/models.py      — Pydantic request/response models
├── src/processing.py  — NDVI computation engine and in-memory job store
└── src/store.py       — Production persistence (asyncpg + NATS publish)

Background Processing Pipeline:
  POST /process → create_job() → BackgroundTask →
    Atmospheric correction (10%) → Cloud mask (30%) →
    NDVI calculation (70%) → store.save_result() →
    NATS publish → job status = COMPLETED

Authentication:
  shared.auth.dependencies.get_current_user — JWT required on write endpoints
  Tenant isolation enforced on all job and data operations
```

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe (includes job queue size) |
| GET | `/readyz` | Kubernetes readiness probe |
| GET | `/health` | Combined health with job metrics |

### Processing Jobs

| Method | Path | Description |
|--------|------|-------------|
| POST | `/process` | Submit new NDVI processing job (202 Accepted, background task) |
| GET | `/process` | List jobs (filter by `tenant_id`, `field_id`, `status`) |
| GET | `/process/{job_id}/status` | Get job status and progress (0–100%) |
| DELETE | `/process/{job_id}` | Cancel a queued or processing job |

Job status flow: `queued` → `processing` → `completed` / `failed`
Satellite sources: `sentinel_2`, `landsat_8`, `landsat_9`, `modis`
Priority: integer (lower = higher priority)

### NDVI Data

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fields/{field_id}/ndvi` | Get NDVI result for a field and date |
| GET | `/fields/{field_id}/ndvi/latest` | Get most recent NDVI result for a field |
| GET | `/fields/{field_id}/ndvi/timeseries` | Time series between `start` and `end` dates |

### Analysis

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fields/{field_id}/ndvi/change` | Change analysis between `date1` and `date2` |
| POST | `/fields/{field_id}/ndvi/change` | Change analysis (POST body) |
| GET | `/fields/{field_id}/ndvi/seasonal` | Seasonal NDVI analysis for a `year` |
| GET | `/fields/{field_id}/ndvi/anomaly` | Anomaly detection at a `date` vs baseline |

### Export

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fields/{field_id}/ndvi/export` | Export data as `geotiff`, `png`, `csv`, or `json` |

### Composites

| Method | Path | Description |
|--------|------|-------------|
| POST | `/composites/monthly` | Create monthly NDVI composite (mean/median/max) |
| GET | `/fields/{field_id}/composites` | List composites for a field (optional `year` filter) |
| GET | `/composites/{composite_id}` | Get composite metadata |
| GET | `/composites/{composite_id}/download` | Download composite file |

---

## NATS Events

### Publishes (via `store.save_result()`)

| Subject | Trigger |
|---------|---------|
| `sahool.ndvi.result_saved` | NDVI processing result persisted |
| `sahool.{tenant_id}.ndvi.completed` | Tenant-scoped processing completion |

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8118` | No | Service port |
| `HOST` | `0.0.0.0` | No | Bind address |
| `ENVIRONMENT` | `development` | No | Environment name (TLS enforced in non-dev) |
| `DATABASE_URL` | - | No | PostgreSQL connection string |
| `NATS_URL` | - | No | NATS server URL |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |
| `JWT_SECRET_KEY` | - | Yes | JWT verification secret |

When `DATABASE_URL` is not set, the service uses in-memory storage (suitable for development).

---

## Job Response Schema

```json
{
  "job_id": "uuid",
  "tenant_id": "uuid",
  "field_id": "uuid",
  "job_type": "ndvi_calculation",
  "status": "queued | processing | completed | failed",
  "progress": 0,
  "priority": 0,
  "parameters": {
    "source": "sentinel_2",
    "date_range": ["2025-01-01", "2025-01-31"],
    "options": {}
  },
  "result": {
    "ndvi_id": "uuid",
    "ndvi_mean": 0.72,
    "files": { "geotiff": "url", "png": "url" }
  },
  "error": null,
  "created_at": "ISO8601"
}
```

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL persistence layer
- **nats-py** — NATS event publishing
- `shared.auth.dependencies` — JWT authentication
- `shared.errors_py` — Unified error handling
- `shared.auth.models.User` — Tenant isolation

---

## Migration Path

This service is being deprecated in favor of `vegetation-analysis-service` (8090), which provides:
- Full integration with Sentinel Hub API
- LAI estimation alongside NDVI
- Improved cloud masking with real atmospheric correction
- Direct database persistence without in-memory fallback

---

## Related Services

- **vegetation-analysis-service** (8090) — Active replacement
- **field-management-service** (3000) — Field geometry and crop data
- **advisory-service** (8093) — Consumes NDVI for irrigation and crop recommendations
- **crop-intelligence-service** (8095) — Crop health AI consumers
- **indicators-service** (8091) — Composite indicator computation
