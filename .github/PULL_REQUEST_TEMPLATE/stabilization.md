## Stabilization PR — SAHOOL v16.1 Hardening

<!-- Use this template for all PRs targeting stabilization/v16.1-hardening -->

### PR ID
<!-- e.g., PR5 — Backend Critical -->

### Summary | الملخص
<!-- 1-3 bullet points describing what this PR fixes -->

-
-
-

### Audit Source | مصدر المراجعة
<!-- Which audit report identified these issues? -->

- [ ] L0 Final Critical Gaps
- [ ] Admin Portal Audit
- [ ] Kong API Gateway Review
- [ ] Backend Services Review
- [ ] IoT/Billing/AI Deep Review
- [ ] Platform/Infrastructure Review
- [ ] Functional Review

### Changes | التغييرات

| File | Change | Issue # |
|------|--------|---------|
| | | |

### Risk Level | مستوى الخطر

- [ ] LOW — No runtime behavior change, additive only
- [ ] MEDIUM — Changes behavior but has feature flag
- [ ] HIGH — Changes auth/security/infra, tested in staging
- [ ] VERY HIGH — Changes billing/payments/data integrity

### Rollback Plan | خطة التراجع

<!-- REQUIRED: Every PR MUST have a rollback plan -->
<!-- Use feature flags, NOT commit reverts -->

**How to rollback:**
```bash
# Environment variable(s) to toggle:

# Expected behavior after rollback:

```

**Rollback tested?**
- [ ] Yes, tested locally
- [ ] Yes, tested in staging
- [ ] No (explain why)

### Testing | الاختبارات

- [ ] Existing tests pass (`make test`)
- [ ] New unit tests added for each fix
- [ ] Integration tests pass (`make test-integration`)
- [ ] Manual testing completed

**Test commands:**
```bash
# Commands to verify this PR:

```

### Security | الأمان

- [ ] No new `nosec` / `# type: ignore` annotations
- [ ] No hardcoded secrets or credentials
- [ ] No `detail=str(e)` exception disclosure
- [ ] Auth required on all new/modified endpoints
- [ ] Tenant isolation verified

### Monitoring | المراقبة

- [ ] Health checks verified (`/healthz`, `/readyz`)
- [ ] No error spike in logs after change
- [ ] Prometheus metrics working (if applicable)
- [ ] Grafana dashboard updated (if applicable)

### Documentation | التوثيق

- [ ] CLAUDE.md updated (if behavior changes)
- [ ] STABILIZATION_PLAN_v16.1.md status updated
- [ ] API docs updated (if endpoints changed)
- [ ] Environment variables documented (if new)

### Definition of Done | شروط الإنجاز

- [ ] Code reviewed by 1 CODEOWNER
- [ ] All CI checks green
- [ ] No new security warnings
- [ ] Rollback plan documented and tested
- [ ] Services health = OK after deployment
- [ ] Post-merge: update STABILIZATION_PLAN status to DONE
