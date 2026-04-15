# carbon-service

**Agricultural carbon footprint (IPCC Tier 1) — خدمة البصمة الكربونية الزراعية**

Port: **8195** | Stack: FastAPI (Python 3.11) | Version: 16.0.0

## What it does

Computes per-operation CO₂e emissions and sequestration for every
`field_operation` recorded in the platform, then aggregates them into
per-field and per-season summaries.

All calculations use IPCC 2019 Refinement Tier 1 default factors:
- Diesel combustion: **2.70 kg CO₂e / L**
- Synthetic nitrogen fertiliser: **6.11 kg CO₂e / kg N**
- Machinery embodied emissions: **3.2 kg CO₂e / operating hour**
- Cover cropping sequestration: **400 kg CO₂e / ha / yr**
- No-till sequestration: **300 kg CO₂e / ha / yr**
- Biochar sequestration: **2,500 kg CO₂e / tonne**

See `src/engine/ipcc_tier1.py` for the full factor table with citations.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/carbon/compute` | Stateless what-if compute |
| POST | `/api/v1/carbon/operations/{id}/compute` | DB-backed compute + persist |
| GET  | `/api/v1/carbon/fields/{id}/summary` | Per-field aggregate |
| GET  | `/api/v1/carbon/crop-seasons/{id}/summary` | Per-season aggregate |
| GET  | `/healthz` | Liveness |
| GET  | `/readyz` | Readiness (DB + NATS) |
| GET  | `/health` | Comprehensive health |
| GET  | `/metrics` | Prometheus scrape target |

## NATS events consumed

- `sahool.field.operation.recorded` — auto-compute carbon when a new
  field operation is created anywhere in the platform.

## Environment variables

```
PORT=8195
DATABASE_URL=postgresql://...              # field-mgmt-service DB
NATS_URL=nats://nats:4222                  # optional
ENVIRONMENT=development|staging|production
CORS_ORIGINS=https://sahool.app,...
```

## Carbon credit eligibility

An operation is flagged `carbon_credit_eligible = TRUE` only when:
1. `sequestration_kg > 0` (non-zero carbon locked in)
2. `net_kg < 0` (net negative overall)
3. The sequestration comes from a well-known source (cover cropping,
   no-till, biochar) — not just "I claim it"

This is conservative by design. Real carbon-credit issuance still
requires third-party verification per Verra VCS / Gold Standard.

## Scaling

Stateless — horizontally scalable behind Kong. All state lives in the
shared `field-management-service` PostgreSQL DB. Can be killed /
restarted without data loss.

## Testing

```bash
cd apps/services/carbon-service
python -m pytest tests/ -v
```
