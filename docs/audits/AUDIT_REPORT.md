# SAHOOL Platform Audit Index

> **تقارير التدقيق الشاملة لمنصة سهول** | Comprehensive Audit Reports for the SAHOOL Platform

This file used to contain a stub from an earlier ad-hoc audit run. It has been replaced with a proper index pointing at the real, current audit deliverables stored alongside it. If you arrived here from an older link looking for a single "platform audit" document, follow the relevant entry below.

---

## Available audit reports | التقارير المتاحة

| Report | Scope | Status |
|--------|-------|--------|
| [`GAP_REPORT_VERIFICATION.md`](./GAP_REPORT_VERIFICATION.md) | Systematic verification of a 64-gap summary against current `v16.0.0` source state, with line-level citations | ✅ Current |
| [`GOVERNANCE_AUDIT.md`](./GOVERNANCE_AUDIT.md) | Governance posture: `governance/services.yaml`, agent registry, policy coverage | ✅ Current |
| [`E2E_USER_JOURNEY_AUDIT.md`](./E2E_USER_JOURNEY_AUDIT.md) | End-to-end user-journey coverage across web / mobile / admin | ✅ Current |
| [`RATE_LIMITING_AUDIT_REPORT.md`](./RATE_LIMITING_AUDIT_REPORT.md) | Kong rate-limit configuration audit | ✅ Current |
| [`SECRETS_DETECTION_AUDIT_REPORT.md`](./SECRETS_DETECTION_AUDIT_REPORT.md) | Gitleaks / secret-scanning results & remediation | ✅ Current |

---

## How a new audit should be added

1. Place the report alongside this file as `<TOPIC>_AUDIT_REPORT.md` or `<TOPIC>_AUDIT.md`.
2. Add a row to the table above and to [`README.md`](./README.md).
3. Cite specific files/lines for every finding; avoid unsourced claims.
4. Cross-link from the relevant section of [`../README.md`](../README.md).

---

## Related sections | الأقسام ذات الصلة

- [`../security/`](../security/) — Threat models, data classification.
- [`../reports/`](../reports/) — Longer-form analyses and reviews.
- [`../operations/`](../operations/) — Operational runbooks where audit findings are operationalised.
- [`../disaster-recovery/`](../disaster-recovery/) — DR runbook and implementation guide.

---

_Last updated: 2026-05-12._
