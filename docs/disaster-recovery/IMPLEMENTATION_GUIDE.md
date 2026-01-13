# SAHOOL Platform - Disaster Recovery Implementation Guide

# دليل تنفيذ التعافي من الكوارث

**Version:** 1.0.0
**Date:** 2026-01-06
**Status:** IMPLEMENTATION READY

---

## 📋 Overview

This guide provides step-by-step instructions for implementing the disaster recovery improvements for the SAHOOL platform, addressing the gaps identified in the DR audit (score: 5.5/10 → target: 9/10).

## 🎯 Implementation Objectives

Based on the audit findings, this implementation will:

1. ✅ Implement PostgreSQL streaming replication with Patroni
2. ✅ Add automated failover capabilities (RTO: <30 seconds)
3. ✅ Enable WAL archiving for Point-in-Time Recovery (RPO: <5 minutes)
4. ✅ Configure cross-region backup replication
5. ✅ Add comprehensive monitoring for RTO/RPO compliance
6. ✅ Create DR runbooks and testing procedures

## 📁 Files Created

### PostgreSQL HA Configuration

```
/home/user/sahool-unified-v15-idp/infrastructure/core/postgres/ha-replication/
├── patroni-config.yml                  # Patroni configuration for HA
├── docker-compose.ha.yml               # 3-node HA cluster setup
├── haproxy.cfg                         # Load balancer configuration
└── scripts/
    ├── wal-archive.sh                  # WAL archiving to S3
    ├── wal-restore.sh                  # WAL restoration for PITR
    ├── on-role-change.sh               # Failover callback
    └── post-bootstrap.sh               # Initial cluster setup
```

### Disaster Recovery Scripts

```
/home/user/sahool-unified-v15-idp/scripts/disaster-recovery/
├── failover-postgres.sh                # Automated failover management
├── test-failover.sh                    # DR testing suite
├── verify-backups.sh                   # Backup verification
├── setup-cross-region-replication.sh   # Cross-region setup
└── backup-metrics-exporter.sh          # Prometheus metrics
```

### Documentation

```
/home/user/sahool-unified-v15-idp/docs/disaster-recovery/
├── DR_RUNBOOK.md                       # Comprehensive DR procedures
└── IMPLEMENTATION_GUIDE.md             # This file
```

### Monitoring

```
/home/user/sahool-unified-v15-idp/infrastructure/monitoring/
├── prometheus/rules/disaster-recovery.yml
└── grafana/dashboards/disaster-recovery-dashboard.json
```

---

## 🚀 Phase 1: PostgreSQL HA Setup (Critical Priority)

### Current State

- ❌ Single PostgreSQL instance
- ❌ No replication
- ❌ RPO: 24 hours
- ❌ Manual failover only

### Target State

- ✅ 3-node PostgreSQL cluster
- ✅ Streaming replication
- ✅ RPO: <5 seconds
- ✅ Automated failover (<30 seconds)

### Implementation Steps

#### Step 1: Prepare Environment Variables

Create or update `.env` file:

```bash
cd /home/user/sahool-unified-v15-idp

# Add these variables to .env
cat >> .env <<EOF

# PostgreSQL HA Configuration
POSTGRES_PASSWORD=<your-secure-password>
REPLICATION_PASSWORD=<replication-password>

# S3/MinIO for WAL Archive
S3_ENDPOINT=http://minio:9000
S3_BUCKET=sahool-backups
S3_ACCESS_KEY=<your-access-key>
S3_SECRET_KEY=<your-secret-key>

# Monitoring
PROMETHEUS_PUSHGATEWAY_URL=http://prometheus-pushgateway:9091
SLACK_WEBHOOK_URL=<your-slack-webhook>
EOF
```

#### Step 2: Deploy PostgreSQL HA Cluster

```bash
# Navigate to HA configuration
cd infrastructure/core/postgres/ha-replication

# Review configuration
cat patroni-config.yml
cat docker-compose.ha.yml

# Start the HA cluster
docker-compose -f docker-compose.ha.yml up -d

# Wait for cluster to initialize (2-3 minutes)
sleep 180

# Verify cluster status
docker-compose -f docker-compose.ha.yml ps

# Check Patroni cluster
curl http://localhost:8008/cluster | jq .
```

#### Step 3: Verify Replication

```bash
# Check replication status
docker exec sahool-postgres-primary psql -U postgres -c \
  "SELECT client_addr, state, sync_state, replay_lag FROM pg_stat_replication;"

# Verify HAProxy routing
curl http://localhost:7000/stats
```

#### Step 4: Test Failover

```bash
cd /home/user/sahool-unified-v15-idp

# Check cluster health
./scripts/disaster-recovery/failover-postgres.sh status

# Perform test switchover
./scripts/disaster-recovery/failover-postgres.sh switchover

# Verify new primary
./scripts/disaster-recovery/failover-postgres.sh verify
```

**Expected Results:**

- ✅ 3 PostgreSQL nodes running
- ✅ Replication lag < 1MB
- ✅ Failover completes in <30 seconds
- ✅ Zero data loss during failover

---

## 🔄 Phase 2: WAL Archiving & PITR Setup

### Implementation Steps

#### Step 1: Verify WAL Archive Configuration

WAL archiving is already configured in `patroni-config.yml`:

```yaml
archive_mode: on
archive_command: "/usr/local/bin/wal-archive.sh %p %f"
archive_timeout: 300 # 5 minutes
```

#### Step 2: Create S3 Bucket for WAL Archive

```bash
# Using MinIO client
mc alias set minio http://minio:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
mc mb minio/sahool-wal-archive
mc version enable minio/sahool-wal-archive

# Or using AWS CLI for AWS S3
aws s3 mb s3://sahool-wal-archive --region me-south-1
aws s3api put-bucket-versioning \
  --bucket sahool-wal-archive \
  --versioning-configuration Status=Enabled
```

#### Step 3: Verify WAL Archiving

```bash
# Check WAL files are being archived
docker exec sahool-postgres-primary ls -lh /var/lib/postgresql/wal-archive/

# Check S3/MinIO
mc ls minio/sahool-wal-archive/

# Force a WAL switch to test
docker exec sahool-postgres-primary psql -U postgres -c "SELECT pg_switch_wal();"

# Wait 30 seconds and check again
sleep 30
mc ls minio/sahool-wal-archive/
```

**Expected Results:**

- ✅ WAL files appear in archive directory
- ✅ WAL files uploaded to S3/MinIO
- ✅ New WAL files every 5 minutes (or on activity)

---

## 🌍 Phase 3: Cross-Region Replication

### Implementation Steps

#### Step 1: Configure Cross-Region Replication

```bash
cd /home/user/sahool-unified-v15-idp

# For AWS S3
./scripts/disaster-recovery/setup-cross-region-replication.sh aws

# For MinIO
./scripts/disaster-recovery/setup-cross-region-replication.sh minio

# Verify replication
./scripts/disaster-recovery/setup-cross-region-replication.sh verify
```

#### Step 2: Test Cross-Region Failover (AWS RDS)

If using AWS RDS with cross-region read replica:

```bash
# Promote read replica in secondary region
aws rds promote-read-replica \
  --db-instance-identifier sahool-db-replica \
  --region me-central-1

# Wait for promotion
aws rds wait db-instance-available \
  --db-instance-identifier sahool-db-replica \
  --region me-central-1
```

**Expected Results:**

- ✅ Backups replicated to secondary region
- ✅ Replication lag < 15 minutes
- ✅ Read replica can be promoted

---

## 📊 Phase 4: Monitoring Setup

### Implementation Steps

#### Step 1: Deploy Prometheus Rules

```bash
cd /home/user/sahool-unified-v15-idp

# Copy DR rules to Prometheus configuration
cp infrastructure/monitoring/prometheus/rules/disaster-recovery.yml \
   /etc/prometheus/rules/

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

#### Step 2: Import Grafana Dashboard

```bash
# Using Grafana API
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @infrastructure/monitoring/grafana/dashboards/disaster-recovery-dashboard.json
```

#### Step 3: Setup Metrics Exporter Cron Job

```bash
# Add to crontab
crontab -e

# Add this line (runs every 5 minutes)
*/5 * * * * /home/user/sahool-unified-v15-idp/scripts/disaster-recovery/backup-metrics-exporter.sh
```

#### Step 4: Verify Monitoring

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="sahool_backup_metrics")'

# View Grafana dashboard
# Navigate to: http://localhost:3000/d/sahool-dr/disaster-recovery-monitoring
```

**Expected Results:**

- ✅ Prometheus alerts configured
- ✅ Grafana dashboard showing metrics
- ✅ Backup metrics updating every 5 minutes

---

## 🧪 Phase 5: DR Testing

### Implementation Steps

#### Step 1: Run Basic DR Tests

```bash
cd /home/user/sahool-unified-v15-idp

# Run basic tests (no actual failover)
./scripts/disaster-recovery/test-failover.sh basic
```

#### Step 2: Run Full DR Test Suite

```bash
# Run comprehensive tests (includes failover)
./scripts/disaster-recovery/test-failover.sh comprehensive
```

#### Step 3: Verify Backups

```bash
# Run backup verification
./scripts/disaster-recovery/verify-backups.sh

# Check results
cat logs/backup-verification/verification_report_*.json | jq .
```

#### Step 4: Schedule Regular DR Drills

```bash
# Add to crontab for monthly DR drill
crontab -e

# Add this line (runs on 1st of each month at 2 AM)
0 2 1 * * /home/user/sahool-unified-v15-idp/scripts/disaster-recovery/test-failover.sh full >> /var/log/sahool/dr-drill.log 2>&1
```

**Expected Results:**

- ✅ All tests pass
- ✅ Failover completes successfully
- ✅ Backups verified
- ✅ Regular drills scheduled

---

## ✅ Verification Checklist

### PostgreSQL HA

- [ ] 3 PostgreSQL nodes running and healthy
- [ ] Replication lag < 1MB
- [ ] Automated failover tested and working
- [ ] Failover time < 30 seconds
- [ ] HAProxy routing traffic correctly

### Backup & Recovery

- [ ] Daily backups running automatically
- [ ] WAL archiving active
- [ ] Backups verified weekly
- [ ] PITR tested and working
- [ ] Backup age < 24 hours

### Cross-Region

- [ ] Secondary region configured
- [ ] Cross-region replication active
- [ ] Replication lag < 15 minutes
- [ ] Secondary region tested

### Monitoring

- [ ] Prometheus alerts firing correctly
- [ ] Grafana dashboard showing data
- [ ] Metrics exporter running
- [ ] Alert notifications working

### Documentation

- [ ] DR runbook updated
- [ ] Team trained on procedures
- [ ] Emergency contacts updated
- [ ] Escalation path documented

---

## 📈 Expected Improvements

### Before Implementation

| Metric             | Before    | Target      | Status     |
| ------------------ | --------- | ----------- | ---------- |
| DR Readiness Score | 5.5/10    | 9/10        | ⚠️ Gap     |
| PostgreSQL HA      | Single    | 3-node      | ❌ Missing |
| RPO                | 24 hours  | <5 minutes  | ❌ Exceeds |
| RTO                | 1-2 hours | <30 seconds | ❌ Exceeds |
| Automated Failover | No        | Yes         | ❌ Missing |
| DR Drills          | Never     | Monthly     | ❌ Missing |

### After Implementation

| Metric             | After       | Target      | Status      |
| ------------------ | ----------- | ----------- | ----------- |
| DR Readiness Score | 9/10        | 9/10        | ✅ Met      |
| PostgreSQL HA      | 3-node      | 3-node      | ✅ Met      |
| RPO                | <5 seconds  | <5 minutes  | ✅ Exceeded |
| RTO                | <30 seconds | <30 seconds | ✅ Met      |
| Automated Failover | Yes         | Yes         | ✅ Met      |
| DR Drills          | Monthly     | Monthly     | ✅ Met      |

---

## 🔧 Troubleshooting

### Issue: Patroni cluster won't start

**Solution:**

```bash
# Check ETCD health
docker exec sahool-etcd etcdctl endpoint health

# Check logs
docker logs sahool-postgres-primary
docker logs sahool-etcd

# Reset cluster if needed
docker-compose -f docker-compose.ha.yml down -v
docker-compose -f docker-compose.ha.yml up -d
```

### Issue: Replication lag is high

**Solution:**

```bash
# Check network connectivity
docker exec sahool-postgres-primary ping postgres-replica1

# Check disk I/O
docker exec sahool-postgres-primary iostat -x 1

# Increase max_wal_senders if needed
docker exec sahool-postgres-primary psql -U postgres -c \
  "ALTER SYSTEM SET max_wal_senders = 15; SELECT pg_reload_conf();"
```

### Issue: WAL archiving not working

**Solution:**

```bash
# Check S3/MinIO connectivity
mc ls minio/sahool-wal-archive/

# Check archive script permissions
docker exec sahool-postgres-primary ls -l /usr/local/bin/wal-archive.sh

# Check PostgreSQL logs
docker logs sahool-postgres-primary | grep archive
```

---

## 📞 Support

For issues or questions:

- **DR Team:** dr-team@sahool.sa
- **On-Call:** +966-XXX-XXX-XXX
- **Documentation:** https://docs.sahool.sa/dr
- **Incident Channel:** #platform-incidents

---

## 📝 Next Steps

1. **Week 1-2:** Implement PostgreSQL HA and WAL archiving
2. **Week 3:** Configure cross-region replication
3. **Week 4:** Setup monitoring and conduct first DR drill
4. **Monthly:** Run automated DR drills
5. **Quarterly:** Full region failover test

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-06
**Next Review:** 2026-04-06

---

**END OF IMPLEMENTATION GUIDE**
