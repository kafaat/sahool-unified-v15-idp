# ADR-016: Region-Aware Compliance Plug-in Interface

## Status

Proposed

## Context

SAHOOL is deployed across multiple jurisdictions (KSA / NESA, GCC, EU / GDPR,
US / FIPS-mode for federal partners). v3.1 requires a **plug-in abstraction**
so that compliance constraints (data residency, encryption-at-rest algorithms,
audit-log retention, PII handling, signature algorithms) can be swapped per
tenant or per region without code changes in business services.

v16 has:

- `shared/security/` — RBAC, JWT, policy engine
- `shared/secrets/` — Vault integration
- `governance/policies/` — Kyverno policies
- `shared/audit_trail/` — audit primitives

But no unified **compliance plug-in interface** that lets a service ask
"is this operation allowed under tenant X's compliance profile?" and receive
a deterministic answer with evidence.

Phase 1 (row #13) flagged this as 🟡 (no region-aware plug-in abstraction).

## Decision

Define a Python `Protocol`-based plug-in interface in
`shared/security/compliance/`:

```python
class CompliancePlugin(Protocol):
    name: str                        # "fips" | "nesa" | "gdpr" | ...
    region: str                      # ISO 3166-1 alpha-2 or "GLOBAL"

    def allow_operation(self, op: ComplianceOp, ctx: TenantContext) -> Decision: ...
    def encryption_requirements(self) -> EncryptionPolicy: ...
    def retention_policy(self, data_class: DataClass) -> RetentionPolicy: ...
    def pii_handling(self, field: PIIField) -> PIIPolicy: ...
    def signature_algorithms(self) -> list[SignatureAlgo]: ...
```

Initial plug-ins (one file each, no external deps beyond what we already use):

- `shared/security/compliance/plugins/fips.py` — FIPS 140-3 mode
- `shared/security/compliance/plugins/nesa.py` — KSA NESA / SDAIA
- `shared/security/compliance/plugins/gdpr.py` — EU GDPR
- `shared/security/compliance/plugins/default.py` — permissive default

A `ComplianceRegistry` resolves the active plug-in from the JWT `tid` claim →
tenant config (`region`, `compliance_profile`) → plug-in instance, with an
in-memory cache (TTL 60 s) keyed by `(tenant_id, profile)`.

Services consume it via a single FastAPI dependency:

```python
@router.post("/something")
async def handler(compliance: ComplianceContext = Depends(get_compliance_context)):
    decision = compliance.allow(ComplianceOp.EXPORT_PII)
    if not decision.allowed:
        raise HTTPException(status_code=403, detail=decision.reason)
```

## Consequences

### Positive

- New regions are added by writing one plug-in, not by editing dozens of services
- Compliance decisions are auditable (every `Decision` carries `reason` + `evidence`)
- Aligns with the existing tenant-scoped JWT and `get_tenant_subject` model
- Lets FIPS-mode tenants restrict to FIPS-approved signature algorithms without
  forking the codebase

### Negative

- All services must adopt the dependency to benefit; a migration window is needed
- Plug-ins can drift from the underlying regulations if not reviewed periodically
  (mitigation: link each plug-in to a documented review cadence in
  `governance/policies/`)

### Neutral

- New shared module under `shared/security/compliance/`
- Tenant config schema gains `compliance_profile` and `region` fields

## Alternatives Considered

### Alternative 1: Hard-code per-region branches in each service

Rejected. Already producing drift between `audit-service`, `user-service`, and
`marketplace-service`. The whole point of v3.1's plug-in system is to remove
this branching.

### Alternative 2: Use Open Policy Agent (OPA) for compliance decisions

Considered. Adds an external service dependency on every request. Rejected for
the first iteration because Python `Protocol` plug-ins are sufficient for the
decision types we need and avoid a network hop. OPA can be wrapped behind the
same `CompliancePlugin` interface in a future iteration without changing
callers.

### Alternative 3: Reuse `agro-rules` (8151) for compliance rules

Rejected. `agro-rules` is for **agronomic** rules (crop, pest, dosage) and has
a different evaluator and audience. Mixing regulatory compliance there would
blur the boundary and complicate audits.

## References

- [Phase 1 Gap Analysis row #13](../architecture/GAP_ANALYSIS_v3.1_vs_v16.md)
- `shared/security/`, `shared/secrets/`, `shared/audit_trail/`
- `governance/policies/`
- ADR-008: AI Architecture & Model Selection (for tenant context patterns)
