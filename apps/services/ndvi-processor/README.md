# NDVI Processor Service

خدمة معالجة صور الأقمار الصناعية وحساب NDVI

**Port:** 8118 | **Type:** Python / FastAPI | **Version:** 16.0.0

> **Deprecation Notice**: This service is being migrated to `vegetation-analysis-service` (port 8090).
> New integrations should use `vegetation-analysis-service`. Sunset: v17.0.0.

---

## Overview | نظرة عامة

The NDVI Processor converts satellite imagery from Sentinel-2, Landsat, and MODIS sources into Normalized Difference Vegetation Index (NDVI) values for field health monitoring. Processing runs asynchronously in the background with a job queue, enabling non-blocking HTTP responses. Results are persisted to PostgreSQL when available, with in-memory fallback for development.

يقوم معالج NDVI بتحويل صور الأقمار الصناعية من مصادر Sentinel-2 وLandsat وMODIS إلى قيم مؤشر الغطاء النباتي للرصد الصحي للحقول.

---

## Features | الميزات

- Background job queue for asynchronous processing
- Multi-source: `sentinel_2`, `landsat_8`, `landsat_9`, `modis`
- Atmospheric correction and cloud masking pipeline
- NDVI time series retrieval with date filtering
- Change analysis between two dates with zone mapping
- Seasonal analysis by crop year
- Anomaly detection vs historical baseline
- Monthly composite generation (mean, median, max-NDVI)
- Export formats: GeoTIFF, PNG, CSV, JSON
- PostgreSQL persistence + in-memory fallback
- NATS event publishing on job completion
- JWT tenant isolation

---

## Quick Start | البدء السريع

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8118 --reload

# Docker
docker build -t ndvi-processor .
docker run -p 8118:8118 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e NATS_URL=nats://localhost:4222 \
  ndvi-processor
```

---

## API Endpoints | نقاط الوصول

### Health Checks | فحص الصحة

```
GET  /health     - Combined health with job metrics
GET  /healthz    - Kubernetes liveness probe
GET  /readyz     - Kubernetes readiness probe
```

### Processing Jobs | معالجة المهام

```
POST /process                    - Submit new NDVI processing job (202 Accepted)
GET  /process                    - List jobs (filter: tenant_id, field_id, status)
GET  /process/{job_id}/status    - Get job status and progress (0-100%)
DELETE /process/{job_id}         - Cancel a job
```

### NDVI Data | بيانات NDVI

```
GET  /fields/{field_id}/ndvi             - Get NDVI for a field and date
GET  /fields/{field_id}/ndvi/latest      - Get most recent NDVI result
GET  /fields/{field_id}/ndvi/timeseries  - Time series (?start=YYYY-MM-DD&end=YYYY-MM-DD)
```

### Analysis | التحليل

```
GET  /fields/{field_id}/ndvi/change      - Change analysis (?date1=&date2=)
POST /fields/{field_id}/ndvi/change      - Change analysis (POST body)
GET  /fields/{field_id}/ndvi/seasonal    - Seasonal analysis (?year=)
GET  /fields/{field_id}/ndvi/anomaly     - Anomaly detection (?date=)
```

### Export | التصدير

```
GET  /fields/{field_id}/ndvi/export      - Export (?format=geotiff|png|csv|json)
```

### Composites | المركبات

```
POST /composites/monthly                 - Create monthly composite
GET  /fields/{field_id}/composites       - List composites for a field
GET  /composites/{composite_id}          - Get composite metadata
GET  /composites/{composite_id}/download - Download composite file
```

---

## Processing Pipeline | خط معالجة NDVI

```
POST /process
  → create_job() (status: queued)
  → BackgroundTask starts
    → Atmospheric correction (progress: 30%)
    → Cloud masking (progress: 50%)
    → NDVI calculation (progress: 70%)
    → store.save_result() → PostgreSQL + NATS publish (progress: 90%)
    → status: COMPLETED (progress: 100%)
```

---

## Environment Variables | متغيرات البيئة

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8118` | No | Service port |
| `HOST` | `0.0.0.0` | No | Bind address |
| `DATABASE_URL` | - | No | PostgreSQL (in-memory fallback if unset) |
| `NATS_URL` | - | No | NATS for event publishing |
| `JWT_SECRET_KEY` | - | Yes | JWT verification secret |
| `ENVIRONMENT` | `development` | No | TLS enforced in non-dev environments |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |

---

## Directory Structure | هيكل المجلدات

```
ndvi-processor/
├── Dockerfile
├── requirements.txt
├── README.md              (this file)
└── src/
    ├── __init__.py
    ├── main.py            - FastAPI app and all HTTP endpoints
    ├── models.py          - Pydantic request/response models
    ├── processing.py      - NDVI computation engine, job store
    └── store.py           - Production persistence (asyncpg + NATS)
```

---

## NATS Events Published | أحداث NATS المنشورة

| Subject | Trigger |
|---------|---------|
| `sahool.ndvi.result_saved` | NDVI result persisted to database |
| `sahool.{tenant_id}.ndvi.completed` | Tenant-scoped processing completion |

---

## Testing | الاختبار

```bash
# Run tests
pytest tests/ -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html

# Smoke test (import verification)
python -c "from src.main import app; print('Import OK')"

# Manual test via curl
curl -s http://localhost:8118/healthz | jq .
curl -s http://localhost:8118/fields/test-field/ndvi/latest | jq .
```

---

## Migration to vegetation-analysis-service | الهجرة

This service is superseded by `vegetation-analysis-service` (port 8090).

| Feature | ndvi-processor (8118) | vegetation-analysis-service (8090) |
|---------|----------------------|-------------------------------------|
| Status | Deprecated | Active |
| Sentinel Hub | Mock/simulated | Real API integration |
| LAI Estimation | Not available | Available |
| Atmospheric correction | Simulated | Real processing |
| Cloud masking | Simulated | Real processing |

---

## Related Services | الخدمات المرتبطة

- **vegetation-analysis-service** (8090) — Active replacement for this service
- **field-management-service** (3000) — Field geometry and crop context
- **advisory-service** (8093) — Consumes NDVI for recommendations
- **crop-intelligence-service** (8095) — Crop health AI using NDVI data
- **indicators-service** (8091) — Composite indicator computation
