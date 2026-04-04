# Deployment Checklist — SAHOOL v16.1
# قائمة فحص النشر — سهول 16.1

> **Use**: Run through this checklist for staging AND production deployments
> **Print**: Keep a physical copy during production deployments

---

## Phase 1: Pre-Deployment (T-24h)

### 1.1 Code Readiness
- [ ] All 8 PRs merged to `stabilization/v16.1-hardening`
- [ ] Integration tests passed (7/7 categories)
- [ ] No open critical/high Dependabot alerts on the branch
- [ ] `pre-deploy-validation.sh --strict` passes (no CHANGE_ME)
- [ ] Git tag created: `v16.1.0-rc1`

### 1.2 Infrastructure Readiness
- [ ] AWS KMS key `alias/sahool-vault-unseal` exists in `me-south-1`
- [ ] Vault backup taken before seal change
- [ ] `terraform plan` reviewed for EKS security group changes
- [ ] Database backup taken (`make db-backup`)
- [ ] Redis snapshot taken

### 1.3 Secrets & Configuration
- [ ] `WHATSAPP_APP_SECRET` configured in Vault/env
- [ ] `USSD_PROVIDER_CIDRS` configured for telecom provider
- [ ] `USSD_HMAC_SECRET` configured
- [ ] `STRIPE_API_KEY` verified (not empty)
- [ ] `STRIPE_WEBHOOK_SECRET` verified
- [ ] `SENTINEL_HUB_CLIENT_ID/SECRET` configured (if enabling real NDVI)
- [ ] `API_GATEWAY_URL` set for admin server-side routes

### 1.4 Monitoring Readiness
- [ ] Grafana dashboards accessible
- [ ] Prometheus scraping all targets
- [ ] Alert rules loaded (check `prometheus/rules/`)
- [ ] PagerDuty/Slack alerting configured
- [ ] Log aggregation working (Loki/ELK)

### 1.5 Team Readiness
- [ ] On-call engineer assigned
- [ ] Rollback procedures reviewed by team
- [ ] Communication channel ready (#sahool-deployment)
- [ ] Stakeholders notified of deployment window

---

## Phase 2: Staging Deployment (T-8h)

### 2.1 Deploy to Staging
```bash
# 1. Tag the release candidate
git tag v16.1.0-rc1 stabilization/v16.1-hardening
git push origin v16.1.0-rc1

# 2. Deploy to staging via ArgoCD or direct
# (Follow your standard staging deployment process)
```

### 2.2 Staging Validation
- [ ] All services healthy (`/healthz` = OK)
- [ ] All services ready (`/readyz` = OK, DB + NATS connected)
- [ ] Admin portal login works
- [ ] Webhook test: WhatsApp HMAC accepted
- [ ] Webhook test: USSD callback accepted
- [ ] NDVI request returns real data (or None if sentinelhub not installed)
- [ ] Vault unsealed automatically after restart
- [ ] Kong loads without errors
- [ ] Billing: test payment succeeds (test mode)
- [ ] Notifications: send test notification

### 2.3 Soak Test (4 hours minimum)
- [ ] No error rate increase in logs
- [ ] No memory leaks (check container memory)
- [ ] No connection pool exhaustion
- [ ] Response times within SLO
- [ ] Error budget not burning

---

## Phase 3: Production Deployment (T-0)

### 3.1 Final Go/No-Go
- [ ] Staging soak test passed
- [ ] No new critical issues discovered
- [ ] On-call engineer confirmed available
- [ ] Rollback scripts ready
- [ ] **GO decision from team lead**

### 3.2 Canary Deployment (10% traffic)
```bash
# Deploy canary (10% of traffic)
# Monitor for 30 minutes before proceeding
```
- [ ] Canary deployed successfully
- [ ] Error rate < 0.1% (30 min observation)
- [ ] P99 latency within SLO
- [ ] No 5xx spike
- [ ] **Decision: Proceed / Rollback**

### 3.3 Progressive Rollout
```
10% → (30 min) → 50% → (30 min) → 100%
```
- [ ] 50% rollout — error rate stable
- [ ] 100% rollout — error rate stable
- [ ] All services healthy

### 3.4 Post-Deployment Verification
- [ ] Admin portal login works
- [ ] Mobile app connects successfully
- [ ] Webhooks processing (check logs)
- [ ] NATS events flowing
- [ ] Billing endpoints responding
- [ ] NDVI analysis working
- [ ] Prometheus collecting new metrics
- [ ] No CHANGE_ME in production configs

---

## Phase 4: Post-Deployment Monitoring (T+48h)

### 4.1 First Hour
- [ ] Error rate baseline established
- [ ] Response time baseline established
- [ ] Active users count normal
- [ ] No PagerDuty alerts fired

### 4.2 First 24 Hours
- [ ] Error budget consumption normal
- [ ] No customer reports of issues
- [ ] Webhook delivery rate > 99%
- [ ] Background jobs completing normally
- [ ] Database query performance normal

### 4.3 48-Hour Sign-Off
- [ ] All SLOs met for 48 hours
- [ ] No rollbacks needed
- [ ] No hotfixes required
- [ ] **Sign-off from team lead**
- [ ] Post-mortem scheduled (if any incidents)
- [ ] Tag final release: `v16.1.0`

---

## Emergency Rollback Procedures

### Scenario A: Single Service Failure
```bash
# Rollback specific service via feature flag
# Example: notification-service auth issue
export AUTH_STRICT_MODE=false
# Restart the affected service
docker-compose restart notification-service
```

### Scenario B: Vault Sealed
```bash
# Revert to manual unseal
# 1. Comment out seal "awskms" in vault-production.hcl
# 2. Restart Vault
# 3. Manual unseal with shamir keys
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
```

### Scenario C: Kong Config Failure
```bash
# Revert to previous kong.yml
cp infrastructure/gateway/kong/kong.yml.bak infrastructure/gateway/kong/kong.yml
docker-compose restart kong
```

### Scenario D: Full Rollback
```bash
# Revert entire deployment to previous version
# Via ArgoCD:
argocd app rollback sahool-platform
# Via Helm:
helm rollback sahool <previous-revision>
# Via Docker Compose:
git checkout v16.0.0
docker-compose down && docker-compose up -d
```

---

## Contacts

| Role | Name | Contact |
|------|------|---------|
| Deployment Lead | | |
| On-Call Engineer | | |
| Database Admin | | |
| Security Lead | | |
| Product Owner | | |
