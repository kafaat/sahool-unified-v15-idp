# shared/prescription_safety — Prescription Safety Gateway (ADR-013)

> **Status:** Skeleton (Phase 3). No runtime logic yet. See
> [ADR-013](../../docs/adr/ADR-013-prescription-safety-gateway.md).

This package will host the unified decision contract for any prescription
(pesticide, fertilizer, irrigation), aggregating the existing checkers.

## Modules

| File          | Responsibility                                                        |
| ------------- | --------------------------------------------------------------------- |
| `models.py`   | `PrescriptionRequest`, `Decision`, `Reason`, `Evidence`, `DecisionEnum` |
| `gateway.py`  | `check(request) → Decision` orchestrator (sequential short-circuit)   |

## Reused checkers (do not duplicate)

| Concern                | Source                                                    |
| ---------------------- | --------------------------------------------------------- |
| PHI / REI / PPE / drift | `shared/pesticide_compliance/PesticideComplianceChecker` |
| Tank-mix               | same                                                      |
| Forbidden substance    | `shared/agri_taxonomy_client` (hot-reloaded blacklist)    |
| Dosage ±10 % gate      | `apps/services/agro-rules` (port 8151)                    |
| GlobalGAP registration | `apps/services/globalgap-compliance` (port 8128)          |

## Boundaries

- **No DB schema.** Audit goes through `shared/audit_trail`.
- **NATS subject:** `sahool.prescription.decided` (tenant-scoped).
- **Embed-mode flag:** `PRESCRIPTION_GATEWAY_MODE=standalone|embed` controls
  whether the same router is mounted inside `agro-rules`.

## Decision contract

```
POST /api/v1/prescription/check
→ { decision: APPROVED|REVIEW|REJECTED,
    reasons: [Reason, ...],
    evidence: { ... } }
```

`reasons` is ordered by severity. `evidence` carries per-checker payloads
so reviewers can audit any decision after the fact.
