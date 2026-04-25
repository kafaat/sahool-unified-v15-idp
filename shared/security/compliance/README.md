# shared/security/compliance — Region-Aware Compliance Plug-ins (ADR-016)

> **Status:** Phase 4 — implemented. TTL-cached registry and
> default/FIPS/NESA/GDPR plug-ins are live with unit tests. See
> [ADR-016](../../../docs/adr/ADR-016-compliance-plugin-interface.md).

`Protocol`-based plug-in abstraction so business services can ask
"is this allowed under tenant X's compliance profile?" without branching
on region.

## Modules

| File                   | Responsibility                                       |
| ---------------------- | ---------------------------------------------------- |
| `models.py`            | `ComplianceOp`, `Decision`, `EncryptionPolicy`, etc. |
| `protocol.py`          | `CompliancePlugin` typing-`Protocol`                 |
| `registry.py`          | TTL-cached resolver from JWT `tid` → plug-in         |
| `plugins/default.py`   | Permissive default                                   |
| `plugins/fips.py`      | FIPS 140-3                                           |
| `plugins/nesa.py`      | KSA NESA / SDAIA                                     |
| `plugins/gdpr.py`      | EU GDPR                                              |

## Boundaries

- Plug-ins are **pure Python**. No external network calls. OPA can be
  wrapped behind the same `Protocol` later without changing callers.
- Decisions always carry a human-readable `reason` and a structured
  `evidence` payload; both are written to `shared/audit_trail`.
- Tenant config (`region`, `compliance_profile`) is resolved once per
  request and cached for 60 s in `ComplianceRegistry`.

## FastAPI dependency (planned)

```python
from shared.security.compliance import get_compliance_context

@router.post("/something")
async def handler(c = Depends(get_compliance_context)):
    decision = c.allow(ComplianceOp.EXPORT_PII)
    if not decision.allowed:
        raise HTTPException(403, decision.reason)
```
