# ADR-013: Prescription Safety Gateway (thin aggregator)

## Status

Proposed

## Context

v3.1 requires a single decision endpoint for any prescription (pesticide,
fertilizer, irrigation) that returns one of `APPROVED | REVIEW | REJECTED`,
backed by:

- PHI / REI / PPE checks
- Tank-mix and drift checks
- Forbidden-substance blacklist
- Dosage tolerance gate (±10 %)
- GlobalGAP / regional registration check

v16 already implements **all the underlying checks**:

- `shared/pesticide_compliance/PesticideComplianceChecker` — PHI, REI, PPE,
  tank-mix, drift
- `apps/services/agro-rules/` (port 8151) — agronomic rules engine
- `apps/services/globalgap-compliance/` (port 8128) — GlobalGAP IFA v6

What is missing is **the decision endpoint** that aggregates them and returns
a single contract. Phase 1 (row #11) reclassified this from 🔴 (new heavy
service) to 🟠 (thin gateway, optionally hosted inside `agro-rules`).

## Decision

Add a thin **prescription-safety-gateway** as a new lightweight Python FastAPI
service whose **only job** is to fan out to the existing checkers and return
the unified decision contract.

Endpoint:

```
POST /api/v1/prescription/check
→ { decision: APPROVED|REVIEW|REJECTED, reasons: [...], evidence: {...} }
```

Internal flow (sequential short-circuit on REJECTED):

1. Forbidden-substance blacklist (in-process, hot-reloaded from `agri-taxonomy-service`)
2. `PesticideComplianceChecker` (PHI / REI / PPE / tank-mix / drift)
3. Dosage ±10 % gate (against `agro-rules`)
4. `globalgap-compliance` registration check
5. Audit-log emit on every decision (`sahool.prescription.decided`, tenant-scoped)

If operational footprint is a concern, the same router can be **embedded inside
`agro-rules`** as a sub-router under `/api/v1/prescription/*` — both options
share the same code in `shared/prescription_safety/`.

## Consequences

### Positive

- One contract for callers (mobile, advisory-service, drone-service,
  marketplace-service)
- Zero duplication of compliance logic — all existing checkers are reused
- Auditable: every decision is logged with the underlying evidence
- Easy to add new checks (e.g., regional pesticide blacklists) without
  touching callers

### Negative

- Adds one network hop per prescription decision (negligible at our scale)
- Two deployment options means we must pick one and document it; for now we
  default to a standalone gateway with an embed-mode flag

### Neutral

- New port (TBD) and Kong route
- New error codes for prescription decisions

## Alternatives Considered

### Alternative 1: New heavy `prescription-safety-service` that re-implements checks

Rejected. Duplicates `pesticide_compliance` and `globalgap-compliance`; creates
drift risk between the new service and the existing checkers.

### Alternative 2: Each caller orchestrates the checks itself

Rejected. Today this is what happens partially in `advisory-service` and
`drone-service`; it has caused inconsistent decisions. Centralizing the
aggregation is the whole point of the gateway.

### Alternative 3: Embed in `agro-rules` only (no separate gateway)

Acceptable; documented as an embed mode toggled by `PRESCRIPTION_GATEWAY_MODE`.
Default deployment is standalone for blast-radius isolation; embed mode is
available for resource-constrained tenants.

## References

- [Phase 1 Gap Analysis row #11](../architecture/GAP_ANALYSIS_v3.1_vs_v16.md)
- `shared/pesticide_compliance/checker.py::PesticideComplianceChecker`
- `apps/services/agro-rules/`
- `apps/services/globalgap-compliance/`
