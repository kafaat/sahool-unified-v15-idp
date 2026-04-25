# prescription-safety-gateway — Prescription Safety Gateway (ADR-013)

> **Status:** Phase 4 first cut. The service runs and exposes a working
> `POST /api/v1/prescription/check` endpoint backed by
> `shared.prescription_safety.PrescriptionGateway` with three default
> checkers (forbidden-substance, dosage tolerance, pesticide adapter).

A thin FastAPI aggregator over the v16 compliance checkers. Returns one
of `APPROVED | REVIEW | REJECTED` with bilingual reasons and per-checker
evidence.

- **Port:** 8275
- **Kong route:** `/api/v1/prescription/*`
- **Layer:** Decision
- **ADR:** [docs/adr/ADR-013-prescription-safety-gateway.md](../../../docs/adr/ADR-013-prescription-safety-gateway.md)
- **Library:** [`shared.prescription_safety`](../../../shared/prescription_safety/)

## Endpoints

| Method | Path                              | Description                              |
| ------ | --------------------------------- | ---------------------------------------- |
| `POST` | `/api/v1/prescription/check`      | Aggregate decision (APPROVED/REVIEW/REJECTED) |
| `GET`  | `/api/v1/prescription/checkers`   | Introspect configured checkers           |
| `GET`  | `/healthz` `/readyz` `/metrics` `/` | Standard SAHOOL service surface          |

## Configuration

| Env var                      | Default        | Purpose                                    |
| ---------------------------- | -------------- | ------------------------------------------ |
| `SERVICE_NAME`               | `prescription-safety-gateway` | Service identity                |
| `SERVICE_VERSION`            | `0.1.0`        | Reported in `/healthz`                     |
| `PRESCRIPTION_GATEWAY_MODE`  | `standalone`   | `standalone` or `embed`                    |
| `FORBIDDEN_SUBSTANCES`       | (empty)        | Comma-separated blocklist                  |

The default rate table is intentionally small in this first cut; Phase
4.1 wires it to `agro-rules` over HTTP.

## Local development

```bash
cd apps/services/prescription-safety-gateway
pip install -r requirements.txt
uvicorn src.main:app --port 8275 --reload
curl -s -X POST http://localhost:8275/api/v1/prescription/check \
  -H 'content-type: application/json' \
  -d '{"tenant_id":"farm-01","prescription_id":"rx-1","prescription_type":"fertilizer","field_id":"FIELD-003","crop":"wheat","product":"Urea 46%","rate":50,"rate_unit":"kg/ha"}' | jq
```

## Tests

```bash
pytest apps/services/prescription-safety-gateway/tests/ -v
```
