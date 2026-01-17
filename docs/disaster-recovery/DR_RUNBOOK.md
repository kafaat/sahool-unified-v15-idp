# SAHOOL Platform - Disaster Recovery Runbook

# دليل التعافي من الكوارث لمنصة سهول

**Version:** 2.0.0
**Last Updated:** 2026-01-06
**Classification:** CRITICAL - Internal Use Only
**Owner:** Platform Infrastructure & DR Team

---

## 📋 Table of Contents | جدول المحتويات

1. [Executive Summary](#executive-summary)
2. [Emergency Contacts](#emergency-contacts)
3. [RTO/RPO Targets](#rtorpo-targets)
4. [PostgreSQL Failover Procedures](#postgresql-failover-procedures)
5. [Multi-Region Failover](#multi-region-failover)
6. [Complete Datacenter Loss Recovery](#complete-datacenter-loss-recovery)
7. [Service-Specific Recovery](#service-specific-recovery)
8. [Rollback Procedures](#rollback-procedures)
9. [Post-Recovery Checklist](#post-recovery-checklist)
10. [Appendix: Command Reference](#appendix-command-reference)

---

## Executive Summary

This runbook provides step-by-step procedures for disaster recovery scenarios in the SAHOOL agricultural platform. It covers automated and manual failover procedures, complete datacenter loss recovery, and service-specific recovery operations.

**Critical Information:**

- **RTO Target:** 2 hours for database, 6 hours for full system
- **RPO Target:** <5 minutes (with streaming replication)
- **On-Call Escalation:** +966-XXX-XXXX-XXX
- **Incident Slack Channel:** #platform-incidents
- **DR Team Email:** dr-team@sahool.sa

---

## Emergency Contacts

### Primary DR Team

| Role                | Name   | Phone            | Email                | Availability |
| ------------------- | ------ | ---------------- | -------------------- | ------------ |
| DR Lead             | [Name] | +966-XXX-XXX-XXX | dr-lead@sahool.sa    | 24/7         |
| Database Admin      | [Name] | +966-XXX-XXX-XXX | dba@sahool.sa        | 24/7         |
| Infrastructure Lead | [Name] | +966-XXX-XXX-XXX | infra-lead@sahool.sa | 24/7         |
| Security Lead       | [Name] | +966-XXX-XXX-XXX | security@sahool.sa   | On-call      |
| Platform Architect  | [Name] | +966-XXX-XXX-XXX | architect@sahool.sa  | On-call      |

### External Contacts

| Service          | Contact    | Phone            | Email                 |
| ---------------- | ---------- | ---------------- | --------------------- |
| AWS Support      | Enterprise | +966-XXX-XXX-XXX | aws-support@sahool.sa |
| Network Provider | STC        | +966-XXX-XXX-XXX | support@stc.sa        |
| MinIO Support    | Community  | N/A              | support@min.io        |

### Escalation Path

```
Level 1: On-Call Engineer (0-15 min)
    ↓
Level 2: DR Lead (15-30 min)
    ↓
Level 3: Infrastructure Lead + Database Admin (30-60 min)
    ↓
Level 4: CTO / Platform Architect (60+ min)
```

---

## RTO/RPO Targets

### Component-Level Targets

| Component                | RTO        | RPO        | Failover Type | Priority |
| ------------------------ | ---------- | ---------- | ------------- | -------- |
| **PostgreSQL**           | 30 seconds | <5 seconds | Automated     | Critical |
| **Redis**                | 15 seconds | 0          | Automated     | Critical |
| **NATS**                 | 2 minutes  | 0          | Manual        | High     |
| **MinIO**                | 30 minutes | 15 minutes | Manual        | High     |
| **Kong Gateway**         | 1 minute   | 0          | Automated     | Critical |
| **Application Services** | 5 minutes  | 0          | Automated     | High     |

### Disaster Scenario Targets

| Scenario                       | RTO        | RPO         | Recovery Method      |
| ------------------------------ | ---------- | ----------- | -------------------- |
| Single PostgreSQL node failure | 30 seconds | <5 seconds  | Automated failover   |
| Redis master failure           | 15 seconds | 0           | Sentinel failover    |
| Single AZ failure              | 5 minutes  | <5 seconds  | K8s auto-healing     |
| Region failure                 | 2 hours    | <5 minutes  | Manual region switch |
| Complete datacenter loss       | 6 hours    | <15 minutes | Full DR activation   |

---

## PostgreSQL Failover Procedures

### Scenario 1: Automated Failover (Primary Node Failure)

**Detection:** Patroni automatically detects primary failure via health checks (5-10 seconds)

**Automatic Actions:**

1. Patroni detects primary is unreachable
2. ETCD consensus confirms failure
3. Best replica is selected (lowest lag)
4. Replica is promoted to primary
5. HAProxy routes traffic to new primary
6. Old primary rejoins as replica (when available)

**Expected RTO:** 15-30 seconds
**Expected RPO:** <5 seconds (synchronous replication)

**Monitoring:**

```bash
# Watch cluster status during failover
watch -n 2 '/home/user/sahool-unified-v15-idp/scripts/disaster-recovery/failover-postgres.sh status'

# Check HAProxy stats
curl http://localhost:7000/stats
```

**No manual intervention required unless:**

- Failover does not complete within 2 minutes
- Multiple nodes fail simultaneously
- Data corruption is suspected

### Scenario 2: Planned Switchover (Maintenance)

**Use Case:** Planned maintenance, patching, or testing

**Prerequisites:**

- [ ] Announce maintenance window
- [ ] Verify all replicas are healthy and synchronized
- [ ] Verify replication lag is minimal (<1MB)
- [ ] Take backup before proceeding
- [ ] Notify stakeholders

**Procedure:**

```bash
# Step 1: Verify cluster health
cd /home/user/sahool-unified-v15-idp
./scripts/disaster-recovery/failover-postgres.sh check

# Step 2: Check current topology
./scripts/disaster-recovery/failover-postgres.sh status

# Step 3: Perform switchover to best candidate
./scripts/disaster-recovery/failover-postgres.sh switchover

# Step 4: Or switchover to specific node
./scripts/disaster-recovery/failover-postgres.sh switchover postgres-replica1

# Step 5: Verify new primary
./scripts/disaster-recovery/failover-postgres.sh verify
```

**Expected Duration:** 15-30 seconds
**Expected Downtime:** <5 seconds

**Rollback:**
If issues occur, switch back to original primary:

```bash
./scripts/disaster-recovery/failover-postgres.sh switchover postgres-primary
```

### Scenario 3: Manual Failover (Emergency)

**When to Use:**

- Automated failover failed
- Primary node experiencing severe performance issues
- Data corruption suspected
- Compliance or security incident

**Emergency Procedure:**

```bash
# Step 1: Assess situation
./scripts/disaster-recovery/failover-postgres.sh status | tee /tmp/dr-status.log

# Step 2: If primary is healthy but needs failover
./scripts/disaster-recovery/failover-postgres.sh switchover

# Step 3: If primary is unhealthy/unreachable
./scripts/disaster-recovery/failover-postgres.sh failover

# Step 4: Verify cluster health
./scripts/disaster-recovery/failover-postgres.sh verify

# Step 5: Test database connectivity
docker exec sahool-postgres-haproxy nc -z localhost 5432
docker exec sahool-postgres-primary psql -U postgres -c "SELECT version();"
```

**Post-Failover Actions:**

1. Document the incident
2. Verify application connectivity
3. Check replication status
4. Review logs for errors
5. Notify stakeholders
6. Schedule post-mortem

### Scenario 4: Split-Brain Prevention

**Detection:** Multiple nodes claim to be primary

**Prevention Mechanisms:**

- ETCD consensus requires quorum
- Patroni uses distributed locks
- Synchronous replication prevents data divergence
- Watchdog timers prevent dual primary

**If Split-Brain Occurs:**

```bash
# Step 1: STOP all applications immediately
docker-compose -f docker-compose.yml stop api-gateway field-service

# Step 2: Identify true primary (most recent LSN)
docker exec postgres-primary psql -U postgres -c \
  "SELECT pg_current_wal_lsn();"
docker exec postgres-replica1 psql -U postgres -c \
  "SELECT pg_last_wal_receive_lsn();"

# Step 3: Demote false primary via Patroni
curl -X POST http://postgres-replica1:8008/reinitialize

# Step 4: Verify single primary
./scripts/disaster-recovery/failover-postgres.sh status

# Step 5: Restart applications
docker-compose -f docker-compose.yml up -d
```

---

## Multi-Region Failover

### Architecture Overview

```
Primary Region: Riyadh (me-south-1)
├── EKS Cluster (3 AZs)
├── RDS Multi-AZ Primary
├── ElastiCache (3 nodes)
└── S3 with Cross-Region Replication

Secondary Region: Jeddah (me-central-1)
├── Standby EKS Cluster
├── RDS Read Replica (can be promoted)
├── S3 Replica Bucket
└── Warm Standby Configuration
```

### Scenario 1: Planned Region Failover

**Use Case:** Planned maintenance, testing, or region migration

**Prerequisites:**

- [ ] Secondary region infrastructure is healthy
- [ ] Database replication lag is minimal
- [ ] DNS TTL reduced to 60 seconds (24 hours before)
- [ ] All teams notified
- [ ] Runbook reviewed

**Procedure:**

```bash
# Phase 1: Pre-Failover Checks (15 minutes)
# ─────────────────────────────────────────

# Check secondary region health
aws eks describe-cluster --name sahool-jeddah --region me-central-1

# Check RDS replica lag
aws rds describe-db-instances --db-instance-identifier sahool-db-replica \
  --region me-central-1 --query 'DBInstances[0].ReplicaLag'

# Verify S3 replication
aws s3api get-bucket-replication --bucket sahool-backups-primary \
  --region me-south-1

# Phase 2: Prepare Secondary Region (30 minutes)
# ─────────────────────────────────────────────

# Promote RDS read replica to standalone
aws rds promote-read-replica --db-instance-identifier sahool-db-replica \
  --region me-central-1

# Wait for promotion to complete
aws rds wait db-instance-available \
  --db-instance-identifier sahool-db-replica --region me-central-1

# Update application configuration in Jeddah cluster
kubectl config use-context sahool-jeddah
kubectl create configmap app-config \
  --from-literal=DB_HOST=sahool-db-replica.xxxxx.me-central-1.rds.amazonaws.com \
  --dry-run=client -o yaml | kubectl apply -f -

# Phase 3: DNS Failover (5 minutes)
# ─────────────────────────────────

# Update Route53 to point to Jeddah
aws route53 change-resource-record-sets --hosted-zone-id ZXXXXX \
  --change-batch file://dns-failover-jeddah.json

# Phase 4: Verification (15 minutes)
# ──────────────────────────────────

# Test application endpoints
curl -I https://api.sahool.sa/health
curl -I https://api.sahool.sa/v1/status

# Verify database connectivity
kubectl exec -it deploy/api-gateway -- \
  psql -h $DB_HOST -U sahool -c "SELECT version();"

# Check application logs
kubectl logs -f deploy/api-gateway --tail=100

# Phase 5: Monitor (60 minutes)
# ────────────────────────────

# Monitor error rates
kubectl get pods --all-namespaces
kubectl top nodes

# Check application metrics
curl http://prometheus.sahool.sa/api/v1/query?query=up
```

**Expected RTO:** 60 minutes
**Expected RPO:** <5 minutes

### Scenario 2: Emergency Region Failover

**When to Use:**

- Complete region outage
- Network partition
- Natural disaster
- Critical security incident

**Fast-Track Procedure:**

```bash
# EMERGENCY FAILOVER - EXECUTE IMMEDIATELY

# 1. Promote Jeddah RDS (2 minutes)
aws rds promote-read-replica \
  --db-instance-identifier sahool-db-replica \
  --region me-central-1 \
  --backup-retention-period 30

# 2. Update DNS (1 minute)
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXX \
  --change-batch file://emergency-failover.json

# 3. Scale up Jeddah EKS (3 minutes)
kubectl config use-context sahool-jeddah
kubectl scale deployment api-gateway --replicas=10
kubectl scale deployment field-service --replicas=5

# 4. Verify (2 minutes)
curl https://api.sahool.sa/health
kubectl get pods -A

# Total Expected Time: 8-10 minutes
```

**Communication Template:**

```
INCIDENT: Primary region (Riyadh) is unavailable
STATUS: Failing over to secondary region (Jeddah)
ETA: 10 minutes
EXPECTED IMPACT: 10 minutes downtime
UPDATES: Every 5 minutes via #platform-incidents

Next Update: [TIME]
DR Lead: [NAME]
```

---

## Complete Datacenter Loss Recovery

### Scenario: Total Infrastructure Loss

**Assumption:** All infrastructure destroyed, must rebuild from backups

**Recovery Phases:**

### Phase 1: Assessment & Preparation (30 minutes)

```bash
# 1. Gather DR team
# 2. Assess scope of damage
# 3. Locate latest backups
# 4. Verify backup integrity
# 5. Prepare clean environment

# List available backups
aws s3 ls s3://sahool-backups/postgres/daily/ --recursive

# Verify latest backup
aws s3 cp s3://sahool-backups/postgres/daily/latest/metadata.json - | jq .

# Check WAL archive availability
aws s3 ls s3://sahool-wal-archive/ --recursive | tail -20
```

### Phase 2: Infrastructure Provisioning (60-90 minutes)

```bash
# 1. Deploy new EKS cluster via Terraform
cd /home/user/sahool-unified-v15-idp/infrastructure/terraform/aws/riyadh
terraform init
terraform plan -out=dr-recovery.tfplan
terraform apply dr-recovery.tfplan

# 2. Configure kubectl
aws eks update-kubeconfig --name sahool-dr-cluster --region me-south-1

# 3. Deploy core infrastructure
helm install redis bitnami/redis -f values-redis-ha.yaml
helm install postgresql bitnami/postgresql-ha -f values-postgres-ha.yaml
helm install nats nats/nats -f values-nats.yaml
helm install minio minio/minio -f values-minio.yaml

# 4. Wait for all pods to be ready
kubectl wait --for=condition=ready pod --all --timeout=600s
```

### Phase 3: Database Recovery (45-90 minutes)

```bash
# 1. Restore PostgreSQL from backup
cd /home/user/sahool-unified-v15-idp/scripts/backup

# Download latest backup
aws s3 sync s3://sahool-backups/postgres/daily/latest/ /tmp/restore/

# Restore database
./restore_postgres.sh /tmp/restore/sahool_20260106_020000.dump

# 2. Apply WAL files for PITR
# Restore to specific point in time
RECOVERY_TARGET="2026-01-06 01:55:00"
docker exec postgres-primary sh -c "
  echo \"recovery_target_time = '${RECOVERY_TARGET}'\" >> /var/lib/postgresql/data/recovery.conf
  pg_ctl restart
"

# 3. Verify database
docker exec postgres-primary psql -U postgres -c "SELECT COUNT(*) FROM farms;"
docker exec postgres-primary psql -U postgres -c "SELECT pg_last_wal_replay_lsn();"
```

### Phase 4: Application Deployment (30-45 minutes)

```bash
# 1. Deploy applications via ArgoCD
kubectl apply -f infrastructure/deployment/argocd/

# 2. Sync all applications
argocd app sync sahool-api-gateway
argocd app sync sahool-field-service
argocd app sync sahool-admin-dashboard

# 3. Verify deployments
kubectl get pods -n sahool-prod
kubectl get svc -n sahool-prod
```

### Phase 5: Verification & Testing (45 minutes)

```bash
# 1. Run DR test suite
cd /home/user/sahool-unified-v15-idp/scripts/disaster-recovery
./test-failover.sh comprehensive

# 2. Manual verification
curl https://api.sahool.sa/health
curl https://api.sahool.sa/v1/farms?limit=10

# 3. Database integrity checks
docker exec postgres-primary psql -U postgres -d sahool <<EOF
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
EOF
```

### Phase 6: DNS Cutover (15 minutes)

```bash
# Update DNS to point to new infrastructure
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXX \
  --change-batch file://dns-recovery.json

# Verify DNS propagation
dig api.sahool.sa +short
curl -H "Host: api.sahool.sa" http://$(kubectl get svc api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
```

**Total Recovery Time:** 3.5 - 6.5 hours
**Aligns with RTO target:** 6 hours ✅

---

## Service-Specific Recovery

### Redis Recovery

```bash
# Check Redis Sentinel status
docker exec sahool-redis-sentinel redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

# Manual failover if needed
docker exec sahool-redis-sentinel redis-cli -p 26379 SENTINEL failover mymaster

# Verify replication
docker exec sahool-redis redis-cli INFO replication
```

### NATS Recovery

```bash
# Restore NATS JetStream data
cd /home/user/sahool-unified-v15-idp/scripts/backup
./backup_nats.sh restore /backups/nats/latest

# Verify streams
docker exec sahool-nats nats stream ls
docker exec sahool-nats nats stream info EVENTS
```

### MinIO Recovery

```bash
# Restore MinIO data
cd /home/user/sahool-unified-v15-idp/scripts/backup
./restore_minio.sh /backups/minio/latest

# Verify buckets
docker exec sahool-minio mc ls local/
```

---

## Rollback Procedures

### Rollback After Failed Failover

```bash
# 1. Stop all application traffic
kubectl scale deployment --all --replicas=0

# 2. Restore original primary
./scripts/disaster-recovery/failover-postgres.sh switchover postgres-primary-original

# 3. Verify restoration
./scripts/disaster-recovery/failover-postgres.sh verify

# 4. Resume traffic
kubectl scale deployment api-gateway --replicas=10
```

### Rollback After Region Failover

```bash
# 1. Reduce DNS TTL (if not already done)
# 2. Revert DNS to primary region
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXX \
  --change-batch file://dns-rollback-riyadh.json

# 3. Scale down secondary region
kubectl config use-context sahool-jeddah
kubectl scale deployment --all --replicas=1

# 4. Demote promoted RDS replica back to replica
# Note: This requires re-creating replication, cannot demote directly
```

---

## Post-Recovery Checklist

### Immediate (Within 1 hour)

- [ ] Verify all services are operational
- [ ] Check database replication status
- [ ] Review error logs for anomalies
- [ ] Validate backup processes are running
- [ ] Confirm monitoring and alerting is active
- [ ] Update incident documentation
- [ ] Notify all stakeholders of recovery completion

### Short-term (Within 24 hours)

- [ ] Complete incident report
- [ ] Review and update runbooks based on learnings
- [ ] Replenish consumed backups
- [ ] Verify data integrity across all services
- [ ] Check financial transaction consistency
- [ ] Review access logs for security concerns
- [ ] Update DR test schedule

### Medium-term (Within 1 week)

- [ ] Conduct post-mortem meeting
- [ ] Document lessons learned
- [ ] Update DR procedures
- [ ] Train team on any new procedures
- [ ] Review and optimize RTO/RPO targets
- [ ] Update monitoring thresholds
- [ ] Schedule follow-up DR drill

---

## Appendix: Command Reference

### Quick Status Checks

```bash
# PostgreSQL cluster status
./scripts/disaster-recovery/failover-postgres.sh status

# HAProxy stats
curl http://localhost:7000/stats

# Database connection
docker exec postgres-primary psql -U postgres -c "SELECT version();"

# Replication lag
docker exec postgres-primary psql -U postgres -c \
  "SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
   pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
   FROM pg_stat_replication;"

# Redis Sentinel status
docker exec sahool-redis-sentinel redis-cli -p 26379 SENTINEL masters

# Kubernetes cluster health
kubectl get nodes
kubectl get pods --all-namespaces
kubectl top nodes
```

### Emergency Commands

```bash
# Emergency stop all services
docker-compose -f docker-compose.yml stop

# Emergency PostgreSQL failover
./scripts/disaster-recovery/failover-postgres.sh failover

# Force promote specific replica
curl -X POST http://postgres-replica1:8008/failover \
  -d '{"candidate":"postgres-replica1"}'

# Emergency database backup
./scripts/backup/backup_postgres.sh manual
```

---

## Document Control

| Version | Date       | Author  | Changes                                               |
| ------- | ---------- | ------- | ----------------------------------------------------- |
| 1.0.0   | 2025-12-27 | DR Team | Initial version                                       |
| 2.0.0   | 2026-01-06 | DR Team | Added PostgreSQL HA procedures, multi-region failover |

**Next Review Date:** 2026-04-06
**Classification:** CRITICAL - Internal Use Only
**Distribution:** DR Team, Infrastructure Team, On-Call Engineers

---

**END OF RUNBOOK**

_For questions or clarifications, contact: dr-team@sahool.sa_
