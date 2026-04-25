# SAHOOL v16.1 Stabilization & Hardening Plan
# خطة تثبيت وتقوية منصة سهول الإصدار 16.1

> **Owner**: KAFAAT Engineering
> **Status**: Draft
> **Created**: 2026-04-04
> **Sprint Type**: Stabilization / Hardening Sprint

---

## 1. Objective | الهدف

Close **47+ confirmed security, quality, and operational gaps** discovered across
6 independent audit rounds covering Admin, Kong, Backend, IoT/Billing, CI/CD,
and Platform Infrastructure — **before** any production deployment.

## 2. Branch Strategy | استراتيجية الفروع

```
main (protected — no direct pushes)
 └── stabilization/v16.1-hardening  ← all PRs merge here first
      ├── fix/vault-auto-unseal          (PR3)
      ├── fix/satellite-ndvi-production  (PR1)
      ├── fix/webhook-hmac-verification  (PR2)
      ├── fix/terraform-egress-restrict  (PR4)
      ├── fix/backend-critical           (PR5)  ← highest risk
      ├── fix/billing-hardening          (PR6)  ← highest risk
      ├── fix/data-flow-integration      (PR8)
      └── fix/kpi-observability          (PR7)
```

**Rules:**
- All PRs target `stabilization/v16.1-hardening`, NOT `main`
- `main` receives a single merge after full integration testing passes
- Each PR requires 1 CODEOWNER approval + CI green
- No force-pushes on the stabilization branch

## 3. PR Execution Order (Dependency-Aware) | ترتيب التنفيذ

```
PR3 (Vault) → PR1 (Satellite) → PR2 (Webhooks) → PR4 (Terraform)
→ PR5 (Backend) → PR6 (Billing) → PR8 (Data Flow) → PR7 (KPI)
```

| Day | PR | Scope | Risk | Rollback |
|-----|----|-------|------|----------|
| **Day 1** | **PR3** Vault Auto-Unseal | Enable AWS KMS seal, remove CHANGE_ME | HIGH | Comment `seal "awskms"`, manual unseal |
| **Day 1** | **PR1** Satellite NDVI | Production guard, reject mock data | MEDIUM | Set `ENVIRONMENT=development` to re-enable mock data (guard is keyed off ENVIRONMENT) |
| **Day 2** | **PR2** Webhooks HMAC | WhatsApp + USSD + pre-deploy validation | LOW | `WHATSAPP_HMAC_REQUIRED=false`, `USSD_VERIFY_DISABLED=true` |
| **Day 2** | **PR4** Terraform EKS | Restrict egress to HTTPS/DNS/NTP | HIGH | Revert SG rules to `0.0.0.0/0` (terraform apply) |
| **Day 3-4** | **PR5** Backend Critical | Auth bypass, JWT algo, tenant isolation, rate limiter, exception disclosure | **VERY HIGH** | Feature flags per service; staged rollout |
| **Day 5** | **PR6** Billing Hardening | Startup validation, server-side pricing, idempotency | **VERY HIGH** | `BILLING_LEGACY_MODE=true` bypasses new checks |
| **Day 6** | **PR8** Data Flow | Kong config consolidation, NATS dedup | HIGH | Revert Kong YAML, restart |
| **Day 6** | **PR7** KPI Observability | Connect agricultural KPIs to Prometheus | LOW | Remove new metrics (no data loss) |
| **Day 7** | — | **Full Integration Testing** | — | — |
| **Day 8** | — | **Staging Deployment** | — | — |
| **Day 9** | — | **Production Deployment** (canary 10% → 50% → 100%) | — | — |

## 4. PR Scope Details | تفاصيل كل PR

### PR3 — Vault Auto-Unseal + Secrets Hygiene
| Item | File | Status |
|------|------|--------|
| Enable AWS KMS seal (me-south-1) | `infrastructure/core/vault/vault-production.hcl` | DONE |
| Remove CHANGE_ME from Azure seal | `infrastructure/core/vault/vault-production.hcl` | DONE |
| Pre-deploy validation script | `scripts/pre-deploy-validation.sh` | DONE |
| Pre-deploy CI workflow | `.github/workflows/pre-deploy-validation.yml` | DONE |
| **Remaining**: Create KMS key in AWS | Terraform / AWS Console | TODO |

### PR1 — Satellite NDVI Production Guard
| Item | File | Status |
|------|------|--------|
| Reject mock data in production | `shared/satellite/sentinel_ndvi.py` | DONE |
| Clear data_source="mock" flag | `shared/satellite/sentinel_ndvi.py` | DONE |
| Add `sentinelhub>=3.10.0` to requirements | `requirements/satellite.txt` | DONE |
| **Remaining**: Configure Sentinel Hub credentials | Vault / env vars | TODO |

### PR2 — Webhook HMAC Verification
| Item | File | Status |
|------|------|--------|
| WhatsApp X-Hub-Signature-256 | `whatsapp-bot-service/.../webhook.py` | DONE |
| WhatsApp app_secret config | `whatsapp-bot-service/.../config.py` | DONE |
| USSD IP whitelist + HMAC | `ussd-gateway/src/main.py` | DONE |
| **Remaining**: Configure WHATSAPP_APP_SECRET | Vault / env vars | TODO |
| **Remaining**: Configure USSD_PROVIDER_CIDRS | env vars | TODO |

### PR4 — Terraform EKS Egress Restriction
| Item | File | Status |
|------|------|--------|
| Cluster egress → HTTPS+DNS only | `infrastructure/terraform/modules/eks/main.tf` | DONE |
| Node egress → HTTPS+DNS+NTP only | `infrastructure/terraform/modules/eks/main.tf` | DONE |
| **Remaining**: VPC endpoint egress restriction | `modules/vpc/main.tf` | TODO |
| **Remaining**: RDS/Redis egress restriction | `modules/region/main.tf` | TODO |
| **Remaining**: `terraform plan` review | staging | TODO |

### PR5 — Backend Critical (HIGHEST RISK)
| Item | File | Status |
|------|------|--------|
| notification-service auth mandatory | `notification-service/src/main.py` | DONE |
| JWT algorithm restriction (HS256 only) | `shared/platform.py` | DONE |
| X-Tenant-ID header removal from rate limiter | `advisory-service/src/rate_limiter.py` | DONE |
| Exception disclosure fix (task-service) | `task-service/src/routes/tasks.py` | DONE |
| LRUDict __missing__ race condition | `shared/middleware/rate_limit.py` | DONE |
| Admin httpOnly bypass fix | `admin/src/lib/unified-client.ts` | DONE |
| Admin Open Redirect fix | `admin/src/app/(auth)/login/page.tsx` | DONE |
| Admin send-otp PUBLIC_ROUTES | `admin/src/lib/auth/route-protection.ts` | DONE |
| Admin NaN guard (refresh route) | `admin/src/app/api/auth/refresh/route.ts` | DONE |
| Admin middleware production logging | `admin/src/middleware.ts` | DONE |
| IDOR in marketplace service | `marketplace-service/src/app.controller.ts` | DONE |
| Race condition user creation (P2002) | `user-service/src/users/users.service.ts` | DONE |
| CORS wildcard enforcement (4 services) | `astronomical-calendar, globalgap-compliance, virtual-sensors, yolo26-vision-service` | DONE |
| Token revocation race condition (Redis-first write order) | `shared/security/token_revocation.py` | DONE |

### PR6 — Billing Hardening (HIGHEST RISK)
| Item | File | Status |
|------|------|--------|
| Startup validation for payment credentials | `billing-core/src/main.py` | DONE |
| IoT auto-register production block | `iot-gateway/src/main.py` | DONE |
| **Remaining**: Server-side plan pricing | `billing-core/src/main.py` | TODO |
| **Remaining**: Idempotency key for payments | `billing-core/src/main.py` | TODO |
| **Remaining**: Stripe webhook construct_event | `billing-core/src/main.py` | TODO |

### PR7 — KPI Observability
| Item | File | Status |
|------|------|--------|
| Connect agricultural KPIs to Prometheus (vegetation-analysis-service) | `vegetation-analysis-service/src/main.py` | DONE |
| Connect agricultural KPIs to Prometheus (indicators-service) | `indicators-service/src/main.py` | DONE |
| **Remaining**: Wire KPIs into crop-intelligence-service and advisory-service | Deferred to PR7 follow-up | TODO |

### PR8 — Data Flow Integration
| Item | File | Status |
|------|------|--------|
| Kong metrics port localhost binding | `infrastructure/gateway/kong/docker-compose.yml` | DONE |
| NATS Redis-based cross-instance dedup | `shared/events/subscriber.py` | DONE |
| **Remaining**: Kong YAML consolidation | `infrastructure/gateway/kong/` | TODO |

## 5. Definition of Done (per PR) | شروط الإنجاز

Every PR **must** satisfy ALL of the following before merge:

- [ ] Code changes reviewed by 1 CODEOWNER
- [ ] All existing tests pass (`make test`)
- [ ] New tests added for each fix
- [ ] No new security warnings in CI (Bandit, CodeQL, Semgrep)
- [ ] All affected services health = OK (`/healthz`, `/readyz`)
- [ ] No error spike in structured logs (compare before/after)
- [ ] Rollback plan documented in PR description
- [ ] Rollback tested (feature flag toggle or revert)
- [ ] CLAUDE.md / relevant docs updated if behavior changes
- [ ] Metrics/monitoring verified (Prometheus, Grafana)

## 6. Risk Matrix | مصفوفة المخاطر

| PR | Risk Level | Impact if Failed | Mitigation |
|----|-----------|-----------------|------------|
| PR3 Vault | HIGH | Vault locked, all secrets inaccessible | Manual unseal keys as backup |
| PR4 Terraform | HIGH | Services lose internet, ECR pulls fail | Pre-tested in staging; instant revert |
| PR5 Backend | **VERY HIGH** | Auth bypass, data leaks, service crashes | Staged rollout, feature flags, canary |
| PR6 Billing | **VERY HIGH** | Double charges, revenue loss, legal | Idempotency keys, shadow mode first |
| PR8 Data Flow | HIGH | Kong fails to start, all APIs down | Keep old kong.yml as rollback |
| PR1 Satellite | MEDIUM | NDVI unavailable (not critical path) | Feature flag to mock mode |
| PR2 Webhooks | LOW | Webhooks rejected (retry mechanism) | Disable HMAC check via env var |
| PR7 KPI | LOW | Metrics missing (no data loss) | Remove metrics, no side effects |

## 7. Production Readiness Checklist | قائمة جاهزية الإنتاج

After ALL PRs are merged to stabilization branch and integration tested:

### Security
- [ ] Vault auto-unseal operational
- [ ] No CHANGE_ME_BEFORE_DEPLOY in codebase
- [ ] All webhooks verify signatures (WhatsApp, USSD, Stripe, Tharwatt)
- [ ] EKS egress restricted
- [ ] JWT algorithm = HS256 only
- [ ] Auth mandatory on all sensitive endpoints
- [ ] No exception details leaked to clients

### Billing
- [ ] Server-side pricing enforced
- [ ] Idempotency keys on all payment endpoints
- [ ] Stripe webhook signature verification
- [ ] Payment credential validation at startup

### Data Integrity
- [ ] Tenant isolation verified (no cross-tenant data access)
- [ ] NDVI returns real data (not mock) in production
- [ ] Kong loads all config files (upstreams, consumers, security)

### Monitoring
- [ ] Agricultural KPIs visible in Grafana
- [ ] DLQ alerting active
- [ ] Error budgets configured
- [ ] No PII in Prometheus labels

### Operations
- [ ] Backups verified (WAL-G)
- [ ] Disaster recovery tested
- [ ] CI/CD stable (all workflows green)
- [ ] Logs centralized and searchable
- [ ] Rollback tested for each PR
- [ ] Load test passed (k6/Locust)

## 8. Timeline | الجدول الزمني

```
Week 1 (Days 1-6):  Execute PRs in dependency order
Day 7:              Full integration testing
Day 8:              Deploy to staging
Day 9:              Staging validation (24h soak test)
Day 10:             Production canary (10%)
Day 11:             Production rollout (50% → 100%)
Day 12:             Post-deployment monitoring (48h)
```

## 9. Rollback Strategy | استراتيجية التراجع

**Golden Rule**: Every change must be reversible via feature flag, NOT commit revert.

| Change | Rollback Mechanism |
|--------|--------------------|
| Vault KMS seal | Comment seal block, manual unseal |
| NDVI production guard | Set `ENVIRONMENT=development` (guard keyed off ENVIRONMENT) |
| Webhook HMAC | `WHATSAPP_HMAC_REQUIRED=false` |
| EKS egress | `terraform apply` with old SG rules |
| Auth mandatory | `AUTH_STRICT_MODE=false` (per service) |
| Billing validation | `BILLING_LEGACY_MODE=true` |
| Kong config | Swap back to old `kong.yml` |
| KPI metrics | Remove Prometheus scrape targets |

## 10. Communication Plan | خطة التواصل

| Event | Who | Channel |
|-------|-----|---------|
| Sprint kickoff | Engineering team | Meeting |
| Each PR merged | PR author → team | GitHub notification |
| Integration test results | QA → team | Slack #sahool-stabilization |
| Staging deploy | DevOps → team | Slack #deployments |
| Production deploy | DevOps → stakeholders | Email + Slack |
| Incident during rollout | On-call → all | PagerDuty + Slack #incidents |
