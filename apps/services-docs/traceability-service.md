# Traceability Service | خدمة التتبع

Farm-to-table supply chain traceability with QR codes, blockchain anchoring, and consumer-facing product journey visualization.

**Port:** 8123 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The Traceability Service implements end-to-end product tracking from field harvest through processing, storage, transportation, and retail. Each produce batch receives a unique, checksum-validated batch code. QR codes are generated for physical labeling. The consumer-facing journey view lets end customers scan a label and see the complete provenance, certifications, and carbon footprint of their food.

Key capabilities:
- Produce batch creation with auto-generated batch codes (format: `{PRODUCT_CODE}-{YY}-{SEQ}`)
- Batch splitting into sub-batches
- Supply chain event recording (harvest, processing, storage, transport)
- QR code generation in PNG, SVG, and PDF formats
- Bilingual labels (Arabic / English)
- Consumer-facing journey endpoint (public, no auth)
- Carbon footprint estimation from transport events
- Certification tracking (GlobalGAP, Organic, SASO, ISO)
- Optional blockchain anchoring for immutable record

---

## Architecture

```
Traceability Service (8123)
├── src/api/v1/batches.py   — All batch and event routes
└── Shared modules:
    └── shared/traceability/
        ├── SupplyChainTracker  — Event recording logic
        ├── QRCodeGenerator     — QR generation (qrcode library)
        ├── generate_batch_code — Code generation + checksum
        └── calculate_carbon_footprint — Transport CO₂ estimation

External:
├── PostgreSQL — Batch and event persistence
└── NATS       — Supply chain event publishing
```

Both PostgreSQL and NATS connections are optional; the service reports degraded status in `/health` when unavailable.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Readiness probe (DB + NATS) |
| GET | `/health` | Comprehensive health check |
| GET | `/metrics` | Prometheus metrics |

### Batches

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/traceability/batches` | List batches (optional `tenant_id`, `farm_id` filters) |
| POST | `/api/v1/traceability/batches` | Create new batch (auto-generates batch code) |
| GET | `/api/v1/traceability/batches/{batch_id}` | Get batch details |
| PUT | `/api/v1/traceability/batches/{batch_id}` | Update batch (product name, quantity, status) |
| POST | `/api/v1/traceability/batches/{batch_id}/split` | Split batch into sub-batches |
| POST | `/api/v1/traceability/batches/generate-code` | Generate batch code from product code + year + sequence |
| GET | `/api/v1/traceability/batches/verify-code/{code}` | Verify batch code format and existence |

### Supply Chain Events

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/traceability/batches/{batch_id}/events` | List all supply chain events for a batch |
| POST | `/api/v1/traceability/batches/{batch_id}/events/harvest` | Record harvest event with field data |
| POST | `/api/v1/traceability/batches/{batch_id}/events/processing` | Record processing facility event |
| POST | `/api/v1/traceability/batches/{batch_id}/events/storage` | Record storage with conditions |
| POST | `/api/v1/traceability/batches/{batch_id}/events/transport` | Record transport with vehicle and route |

### QR Codes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/traceability/batches/{batch_id}/qr` | Get QR code for batch (format: PNG/SVG/PDF, size: S/M/L/XL) |

### Consumer Journey

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/traceability/journey/{batch_code}` | Public consumer product journey (no auth) |
| GET | `/api/v1/traceability/carbon/{batch_id}` | Estimate carbon footprint from transport events |

---

## NATS Events

### Publishes

| Subject | Trigger |
|---------|---------|
| `BatchCreated.v1` | New produce batch registered |
| `HarvestRecorded.v1` | Harvest event recorded |
| `BatchProcessed.v1` | Processing event recorded |
| `BatchShipped.v1` | Transport event recorded |
| `ConsumerScanned.v1` | Consumer QR code scan |
| `CertificationAttached.v1` | Certification attached to batch |

### Subscribes

| Subject | Purpose |
|---------|---------|
| `FieldCreated.v1` | Producer record initialization |
| `YieldEstimated.v1` | Batch quantity planning |
| `TaskCompleted.v1` | Harvest task completion triggers batch event |
| `QualityGraded.v1` | Quality grade attached to batch |

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8123` | No | Service port |
| `HOST` | `0.0.0.0` | No | Bind address |
| `ENVIRONMENT` | `development` | No | Environment name |
| `DATABASE_URL` | - | Yes | PostgreSQL connection string |
| `REDIS_URL` | - | Yes | Redis connection string |
| `NATS_URL` | - | Yes | NATS server URL |
| `QR_BASE_URL` | - | No | Base URL embedded in QR codes (e.g., `https://trace.sahool.app`) |
| `BLOCKCHAIN_ENABLED` | `false` | No | Enable blockchain anchoring |
| `BLOCKCHAIN_RPC_URL` | - | No | Blockchain RPC endpoint |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |

---

## Consumer Journey Response Example

```json
{
  "product": { "name_en": "Organic Tomatoes", "name_ar": "طماطم عضوية", "batch_code": "TM-25-001", "grade": "A" },
  "producer": { "name": "Al-Falah Farm", "location": "Riyadh, Saudi Arabia", "certifications": ["GlobalGAP", "Organic"] },
  "journey": [
    { "event": "Harvested", "date": "2025-01-15", "location": "Field A" },
    { "event": "Packed", "date": "2025-01-16", "facility": "Packing House" },
    { "event": "Shipped", "date": "2025-01-17", "destination": "Distribution Center" }
  ],
  "carbon_footprint": { "total_kg_co2": 0.45, "per_kg": 0.09 }
}
```

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL async driver
- **nats-py** — NATS event integration
- **structlog** — Structured JSON logging
- `shared/traceability/` — Core traceability logic (QR, batch codes, carbon)
- `shared.errors_py` — Unified error handling

---

## Related Services

- **field-management-service** (3000) — Field and producer data
- **harvest-quality** (shared module) — Quality grade data
- **globalgap-compliance** (8128) — Certification verification
- **supply-chain-service** (8230) — Downstream order fulfillment
- **logistics-service** (8167) — Transport event data
