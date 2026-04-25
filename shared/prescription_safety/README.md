# shared/prescription_safety — Prescription Safety Gateway (ADR-013)

> **Status:** Phase 4 first cut. Library + service are live with three
> default checkers. See
> [ADR-013](../../docs/adr/ADR-013-prescription-safety-gateway.md).

This package hosts the unified decision contract for any prescription
(pesticide, fertilizer, irrigation), aggregating the existing checkers
through a small Protocol so concrete implementations stay
single-purpose and testable in isolation.

## Modules

| File             | Responsibility                                                             |
| ---------------- | -------------------------------------------------------------------------- |
| `models.py`      | `PrescriptionRequest`, `Decision`, `Reason`, `Evidence`, `DecisionEnum`    |
| `protocols.py`   | `PrescriptionChecker` Protocol + `CheckerResult` dataclass                 |
| `checkers.py`    | Default checkers: forbidden-substance, dosage ±10 %, pesticide PHI/REI     |
| `gateway.py`     | `PrescriptionGateway.check()` orchestrator (sequential short-circuit)      |

## Aggregation rules

* Any checker returning `blocking=True` short-circuits to **REJECTED**.
* Otherwise, any `passed=False` demotes the decision to **REVIEW**.
* All clean → **APPROVED**.
* Unexpected exceptions and bad return types are caught and surfaced as
  non-blocking `UNCHECKED_*` reasons so a buggy checker can't break the
  pipeline.

## Reused checkers (do not duplicate)

| Concern                | Source                                                    |
| ---------------------- | --------------------------------------------------------- |
| PHI / REI              | `shared/pesticide_compliance/PesticideComplianceChecker` (wrapped by `PesticideComplianceCheckerAdapter`) |
| Forbidden substance    | `shared/agri_taxonomy_client` (Phase 4.1)                 |
| Dosage ±10 % gate      | `apps/services/agro-rules` (Phase 4.1, HTTP)              |
| GlobalGAP registration | `apps/services/globalgap-compliance` (Phase 4.1, HTTP)    |

## Boundaries

- **No DB schema.** Audit goes through `shared/audit_trail`.
- **NATS subject:** `sahool.prescription.decided` (tenant-scoped, Phase 4.1).
- **Embed-mode flag:** `PRESCRIPTION_GATEWAY_MODE=standalone|embed`.

## Decision contract

```
POST /api/v1/prescription/check
→ { decision: APPROVED|REVIEW|REJECTED,
    reasons: [{code, message_en, message_ar, severity, source_checker}, ...],
    evidence: [{checker, payload, checked_at}, ...],
    decided_at, correlation_id }
```

`reasons` is ordered by severity (`critical` first). `evidence` carries
per-checker payloads so reviewers can audit any decision after the fact.

## Tests

```bash
pytest shared/prescription_safety/tests/ -v
```
