# SAHOOL Platform - Database Monitoring Guide
# دليل مراقبة قواعد البيانات - منصة سهول

**Version:** 2.0.0
**Date:** 2026-01-06
**Status:** ✅ Production-Ready
**Author:** SAHOOL Engineering Team

---

## Table of Contents | جدول المحتويات

1. [Overview](#overview)
2. [Monitoring Architecture](#monitoring-architecture)
3. [Metrics Collection](#metrics-collection)
4. [Alert Rules](#alert-rules)
5. [Grafana Dashboards](#grafana-dashboards)
6. [Backup Monitoring](#backup-monitoring)
7. [Deployment Guide](#deployment-guide)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Appendix](#appendix)

---

## Overview

SAHOOL platform implements a **comprehensive database monitoring solution** that provides deep insights into PostgreSQL and Redis performance, health, and reliability. This guide covers all aspects of the monitoring infrastructure.

### Key Features | الميزات الرئيسية

- ✅ **Advanced PostgreSQL Metrics** - Query performance, autovacuum, WAL, buffer cache
- ✅ **Redis Cache Monitoring** - Memory usage, eviction rates, connection pooling
- ✅ **Automated Backup Monitoring** - Age, size, integrity verification
- ✅ **Connection Pool Tracking** - PgBouncer metrics, pool exhaustion detection
- ✅ **Replication Lag Monitoring** - Real-time lag tracking for HA setups
- ✅ **Disk Space Alerts** - Proactive warnings for storage issues
- ✅ **Performance Dashboards** - Grafana visualizations for all metrics
- ✅ **Automated Alerting** - Multi-channel notifications (Email, Slack, PagerDuty)

### Component Stack | مكونات المراقبة

| Component | Version | Purpose |
|-----------|---------|---------|
| **Prometheus** | v2.48.0 | Time-series metrics database |
| **Grafana** | 10.2.0 | Visualization and dashboards |
| **Alertmanager** | v0.26.0 | Alert routing and notifications |
| **postgres_exporter** | v0.15.0 | PostgreSQL metrics collector |
| **redis_exporter** | v1.55.0 | Redis metrics collector |
| **node_exporter** | v1.7.0 | System metrics collector |
| **pushgateway** | v1.6.2 | Batch job metrics collection |

---

## Monitoring Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     SAHOOL Monitoring Stack                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │  PostgreSQL  │─────▶│   postgres   │─────▶│              │ │
│  │   Database   │      │   exporter   │      │              │ │
│  └──────────────┘      └──────────────┘      │              │ │
│                                               │              │ │
│  ┌──────────────┐      ┌──────────────┐      │  Prometheus  │ │
│  │    Redis     │─────▶│    redis     │─────▶│              │ │
│  │    Cache     │      │   exporter   │      │              │ │
│  └──────────────┘      └──────────────┘      │              │ │
│                                               │              │ │
│  ┌──────────────┐      ┌──────────────┐      │              │ │
│  │    System    │─────▶│     node     │─────▶│              │ │
│  │   Metrics    │      │   exporter   │      │              │ │
│  └──────────────┘      └──────────────┘      └──────┬───────┘ │
│                                                      │         │
│  ┌──────────────┐      ┌──────────────┐             │         │
│  │    Backup    │─────▶│  pushgateway │────────────▶│         │
│  │   Scripts    │      │              │             │         │
│  └──────────────┘      └──────────────┘             │         │
│                                                      │         │
│                        ┌──────────────┐             │         │
│                        │              │◀────────────┘         │
│                        │   Grafana    │                       │
│                        │  Dashboards  │                       │
│                        └──────────────┘                       │
│                                │                              │
│                        ┌───────▼──────┐                       │
│                        │ Alertmanager │                       │
│                        │              │                       │
│                        └───────┬──────┘                       │
│                                │                              │
│              ┌─────────────────┼─────────────────┐           │
│              │                 │                 │           │
│         ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐    │
│         │  Email  │      │   Slack   │    │ PagerDuty │    │
│         └─────────┘      └───────────┘    └───────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Exporters** collect metrics from databases and system
2. **Prometheus** scrapes metrics every 15-30 seconds
3. **Alert rules** evaluate conditions continuously
4. **Alertmanager** routes alerts to appropriate channels
5. **Grafana** visualizes metrics in real-time dashboards

---

## Metrics Collection

### PostgreSQL Custom Metrics

The monitoring system includes **14 custom metric queries** for deep database insights:

#### 1. Top Slow Queries (`pg_stat_statements_top_queries`)
- **Purpose:** Track the slowest queries by total execution time
- **Source:** `pg_stat_statements` extension
- **Metrics:**
  - `calls` - Number of executions
  - `total_exec_time` - Total time spent (ms)
  - `mean_exec_time` - Average execution time (ms)
  - `max_exec_time` - Maximum execution time (ms)
  - `rows` - Rows retrieved/affected

**Example PromQL:**
```promql
topk(10, pg_stat_statements_top_queries_mean_exec_time)
```

#### 2. Table Bloat Detection (`pg_table_bloat`)
- **Purpose:** Identify tables with excessive bloat
- **Metrics:**
  - `total_bytes` - Total table size
  - `table_bytes` - Table size excluding indexes
  - `bloat_bytes` - Estimated bloat size

#### 3. Autovacuum Activity (`pg_autovacuum_activity`)
- **Purpose:** Monitor automatic vacuum operations
- **Metrics:**
  - `seconds_since_last_autovacuum` - Time since last vacuum
  - `n_dead_tup` - Number of dead tuples
  - `dead_tuple_ratio` - Ratio of dead to live tuples

**Alert Threshold:**
```yaml
expr: pg_autovacuum_activity_dead_tuple_ratio > 0.20
```

#### 4. WAL Size Monitoring (`pg_wal_size`)
- **Purpose:** Prevent disk space exhaustion from WAL files
- **Metrics:**
  - `wal_size_bytes` - Total WAL directory size
  - `wal_file_count` - Number of WAL files

**Alert Levels:**
- ⚠️ Warning: WAL > 1GB
- 🔴 Critical: WAL > 5GB

#### 5. Buffer Cache Hit Ratio (`pg_buffer_cache_hit_ratio`)
- **Purpose:** Measure database cache efficiency
- **Metrics:**
  - `cache_hit_ratio` - Ratio of cache hits to total reads (0-1)
  - `blks_hit` - Buffer cache hits
  - `blks_read` - Disk reads

**Optimal Value:** > 0.95 (95% cache hit ratio)

#### 6. Replication Lag (`pg_replication_lag`)
- **Purpose:** Track replication delay for HA setups
- **Metrics:**
  - `lag_seconds` - Replication lag in seconds
  - `lag_bytes` - Replication lag in bytes

#### 7. Transaction Wraparound Distance (`pg_txid_wraparound`)
- **Purpose:** Prevent database shutdown from transaction ID wraparound
- **Metrics:**
  - `txid_age` - Age of oldest frozen transaction
  - `txid_remaining` - Transactions until wraparound

**Critical Threshold:** < 100M transactions remaining

#### 8. Index Usage Statistics (`pg_index_usage`)
- **Purpose:** Identify unused indexes wasting space
- **Metrics:**
  - `idx_scan` - Number of index scans
  - `index_size_bytes` - Index size

**Unused Index Criteria:**
- Scan count < 10
- Size > 10MB
- Age > 24 hours

### Redis Metrics

Redis monitoring includes:

- **Memory Usage:** `redis_memory_used_bytes / redis_memory_max_bytes`
- **Key Eviction:** `redis_evicted_keys_total`
- **Connection Count:** `redis_connected_clients`
- **Hit Rate:** `redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)`
- **Command Stats:** Per-command execution counts

### Backup Metrics (via Pushgateway)

The backup monitoring script pushes metrics:

- **Backup Age:** `postgres_backup_age_seconds`
- **Backup Size:** `postgres_backup_size_bytes`
- **Backup Status:** `postgres_backup_status` (1=exists, 0=missing)
- **Integrity:** `postgres_backup_integrity` (1=valid, 0=invalid)
- **Last Check:** `postgres_backup_monitoring_timestamp_seconds`

---

## Alert Rules

### Database Alert Groups

#### 1. Connection Pool Alerts

**DatabaseConnectionPoolExhausted**
```yaml
expr: (pg_stat_database_numbackends{datname="sahool"} / pg_settings_max_connections) > 0.85
for: 3m
severity: critical
```
**Action:** Investigate connection leaks or increase `max_connections`

**DatabaseHighConnectionRate**
```yaml
expr: rate(pg_stat_database_numbackends[5m]) > 50
for: 5m
severity: warning
```

#### 2. Performance Alerts

**DatabaseSlowQueries**
```yaml
expr: pg_stat_activity_max_tx_duration > 30
for: 5m
severity: warning
```

**DatabaseBufferCacheHitRatioLow**
```yaml
expr: pg_buffer_cache_hit_ratio_cache_hit_ratio < 0.90
for: 10m
severity: warning
```
**Action:** Consider increasing `shared_buffers`

#### 3. Maintenance Alerts

**DatabaseWALSizeHigh**
```yaml
expr: pg_wal_size_bytes > 1073741824  # 1GB
for: 10m
severity: warning
```

**DatabaseAutovacuumNotRunning**
```yaml
expr: pg_autovacuum_activity_seconds_since_last_autovacuum > 86400
for: 1h
severity: warning
```

#### 4. Storage Alerts

**DatabaseDiskSpaceLow**
```yaml
expr: (node_filesystem_avail_bytes{mountpoint=~".*postgres.*"} /
       node_filesystem_size_bytes{mountpoint=~".*postgres.*"}) < 0.15
for: 5m
severity: critical
```

#### 5. Backup Alerts

**DatabaseBackupOld**
```yaml
expr: postgres_backup_age_seconds > 86400  # 24 hours
for: 1h
severity: critical
```

**DatabaseBackupMissing**
```yaml
expr: postgres_backup_status == 0
for: 30m
severity: critical
```

**DatabaseBackupCorrupted**
```yaml
expr: postgres_backup_integrity == 0
for: 5m
severity: critical
```

### Complete Alert List

| Alert Name | Threshold | Duration | Severity |
|------------|-----------|----------|----------|
| DatabaseConnectionPoolExhausted | >85% | 3m | Critical |
| DatabaseHighConnectionRate | >50/sec | 5m | Warning |
| DatabaseSlowQueries | >30s | 5m | Warning |
| DatabaseDeadlocks | >0 | 1m | Warning |
| DatabaseWALSizeHigh | >1GB | 10m | Warning |
| DatabaseWALSizeCritical | >5GB | 5m | Critical |
| DatabaseAutovacuumNotRunning | >24h | 1h | Warning |
| DatabaseHighDeadTuples | >20% | 15m | Warning |
| DatabaseBufferCacheHitRatioLow | <90% | 10m | Warning |
| DatabaseDiskSpaceLow | <15% | 5m | Critical |
| DatabaseReplicationLagHigh | >10s | 5m | Warning |
| DatabaseReplicationLagCritical | >60s | 2m | Critical |
| DatabaseTransactionWraparoundWarning | <500M | 1h | Warning |
| DatabaseTransactionWraparoundCritical | <100M | 10m | Critical |
| DatabaseBackupOld | >24h | 1h | Critical |
| DatabaseBackupMissing | - | 30m | Critical |
| DatabaseBackupTooSmall | <10MB | 15m | Warning |
| DatabaseBackupCorrupted | - | 5m | Critical |
| RedisMemoryHigh | >85% | 5m | Warning |
| RedisCriticalMemory | >95% | 2m | Critical |
| RedisHighEvictionRate | >100/sec | 5m | Warning |

---

## Grafana Dashboards

### SAHOOL Database Performance Dashboard

**Dashboard UID:** `sahool-db-performance`
**Refresh Rate:** 30 seconds
**Timezone:** Asia/Riyadh

#### Panels Overview

1. **Connection Pool Usage** (Gauge)
   - Shows percentage of active connections
   - Thresholds: Green <70%, Yellow <85%, Red >=85%

2. **Buffer Cache Hit Ratio** (Gauge)
   - Displays cache efficiency
   - Optimal: >95%

3. **WAL Size** (Time Series)
   - Tracks WAL directory growth
   - Helps identify archiving issues

4. **Database Size** (Time Series)
   - Monitors total database size
   - Useful for capacity planning

5. **Top 10 Slow Queries** (Time Series)
   - Shows queries with highest mean execution time
   - Includes max and mean calculations

6. **Dead Tuples by Table** (Time Series)
   - Identifies tables needing vacuum
   - Sorted by dead tuple count

7. **Potentially Unused Indexes** (Table)
   - Lists indexes with <10 scans and >10MB size
   - Candidates for removal

8. **Replication Lag** (Time Series)
   - Tracks lag in seconds
   - Critical for HA deployments

9. **Checkpoint Frequency** (Bar Chart)
   - Compares timed vs requested checkpoints
   - High requested checkpoints indicate tuning needed

10. **Database Locks by Mode** (Time Series)
    - Shows lock distribution
    - Helps identify contention

11. **Last Backup Age** (Gauge)
    - Displays time since last backup
    - Thresholds: Green <24h, Yellow <48h, Red >=48h

12. **Last Backup Size** (Gauge)
    - Shows backup file size
    - Detects abnormally small backups

13. **Dead Tuple Ratio by Table** (Time Series)
    - Percentage of dead tuples
    - Threshold: >20% needs attention

### Accessing Dashboards

**URL:** `http://localhost:3002/d/sahool-db-performance`
**Credentials:**
- Username: `admin`
- Password: Set via `GRAFANA_ADMIN_PASSWORD` env var

---

## Backup Monitoring

### Backup Monitor Script

**Location:** `/scripts/backup_monitor.sh`
**Purpose:** Monitor database backups and push metrics to Prometheus

#### Features

- ✅ Automatic backup file detection
- ✅ Age calculation (seconds since creation)
- ✅ Size verification
- ✅ Integrity checking (gzip/bzip2 validation)
- ✅ Prometheus Pushgateway integration
- ✅ Verbose logging
- ✅ Configurable thresholds

#### Usage

```bash
# Basic usage
./backup_monitor.sh

# Custom backup directory
./backup_monitor.sh --backup-dir /var/backups/postgres

# With Pushgateway
./backup_monitor.sh --pushgateway prometheus-pushgateway:9091

# Enable integrity checking
./backup_monitor.sh --check-integrity --verbose

# Show help
./backup_monitor.sh --help
```

#### Environment Variables

```bash
export BACKUP_DIR=/backups/postgres
export PUSHGATEWAY=localhost:9091
export BACKUP_MAX_AGE_HOURS=24
```

#### Cron Setup

Add to crontab for automated monitoring:

```cron
# Run every 15 minutes
*/15 * * * * /home/user/sahool-unified-v15-idp/scripts/backup_monitor.sh --pushgateway pushgateway:9091 >> /var/log/backup-monitor.log 2>&1
```

#### Metrics Pushed

```prometheus
# Backup age in seconds
postgres_backup_age_seconds{backup_dir="/backups/postgres"} 3600

# Backup size in bytes
postgres_backup_size_bytes{backup_dir="/backups/postgres"} 524288000

# Backup status (1=exists, 0=missing)
postgres_backup_status{backup_dir="/backups/postgres"} 1

# Backup integrity (1=valid, 0=invalid/unknown)
postgres_backup_integrity{backup_dir="/backups/postgres"} 1

# Monitoring timestamp
postgres_backup_monitoring_timestamp_seconds 1704556800
```

---

## Deployment Guide

### Prerequisites

1. **Docker and Docker Compose** installed
2. **PostgreSQL** with `pg_stat_statements` extension enabled
3. **Environment variables** configured
4. **Network connectivity** between services

### Step 1: Environment Configuration

Create `.env` file in `infrastructure/monitoring/`:

```bash
# PostgreSQL credentials
POSTGRES_USER=sahool
POSTGRES_PASSWORD=your_secure_password

# Redis credentials
REDIS_PASSWORD=your_redis_password

# Grafana admin credentials
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# Environment
ENVIRONMENT=production

# Alerting (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@sahool.example.com
SMTP_PASSWORD=your_smtp_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_SERVICE_KEY=your_pagerduty_key
```

### Step 2: Enable pg_stat_statements

Connect to PostgreSQL and run:

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify
SELECT * FROM pg_stat_statements LIMIT 1;
```

Add to `postgresql.conf`:

```conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

### Step 3: Deploy Monitoring Stack

```bash
cd /home/user/sahool-unified-v15-idp/infrastructure/monitoring

# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services
docker-compose -f docker-compose.monitoring.yml ps

# Check logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Step 4: Verify Exporters

**PostgreSQL Exporter:**
```bash
curl http://localhost:9187/metrics | grep pg_
```

**Redis Exporter:**
```bash
curl http://localhost:9121/metrics | grep redis_
```

**Node Exporter:**
```bash
curl http://localhost:9100/metrics | grep node_
```

### Step 5: Access Dashboards

**Prometheus UI:**
- URL: http://localhost:9090
- Status → Targets to verify scrape targets

**Grafana:**
- URL: http://localhost:3002
- Login with admin credentials
- Navigate to Dashboards → SAHOOL Database Performance

**Alertmanager:**
- URL: http://localhost:9093
- View active alerts

### Step 6: Configure Backup Monitoring

```bash
# Make script executable
chmod +x /home/user/sahool-unified-v15-idp/scripts/backup_monitor.sh

# Test manually
./scripts/backup_monitor.sh --backup-dir /backups/postgres --pushgateway localhost:9091 --verbose

# Add to cron
crontab -e
```

Add this line:
```cron
*/15 * * * * /home/user/sahool-unified-v15-idp/scripts/backup_monitor.sh --pushgateway pushgateway:9091
```

---

## Troubleshooting

### Common Issues

#### 1. Exporter Not Scraping

**Symptom:** Targets show as "DOWN" in Prometheus

**Solutions:**
```bash
# Check exporter logs
docker logs sahool-monitoring-postgres-exporter

# Verify database connection
docker exec -it sahool-monitoring-postgres-exporter sh
# Inside container:
wget -O- http://localhost:9187/metrics

# Check network connectivity
docker network inspect sahool-network
```

#### 2. Custom Queries Not Loading

**Symptom:** Custom metrics not appearing

**Solutions:**
```bash
# Verify queries file is mounted
docker exec sahool-monitoring-postgres-exporter cat /etc/postgres-exporter/queries.yaml

# Check exporter logs for query errors
docker logs sahool-monitoring-postgres-exporter 2>&1 | grep -i error

# Restart exporter
docker-compose -f docker-compose.monitoring.yml restart postgres-exporter
```

#### 3. Alerts Not Firing

**Symptom:** No alerts despite meeting thresholds

**Solutions:**
```bash
# Check alert rules loaded
curl http://localhost:9090/api/v1/rules | jq .

# Verify Alertmanager connection
curl http://localhost:9090/api/v1/alertmanagers

# Check Alertmanager logs
docker logs sahool-monitoring-alertmanager

# Test alert rule manually in Prometheus UI
# Alerts → Rule name → View in Explorer
```

#### 4. Grafana Dashboard Empty

**Symptom:** Panels show "No data"

**Solutions:**
```bash
# Verify Prometheus datasource
# Grafana → Configuration → Data Sources → Prometheus
# Click "Test" button

# Check query syntax in panel
# Edit panel → Query tab → Check PromQL syntax

# Verify metrics exist
curl http://localhost:9090/api/v1/query?query=pg_wal_size_bytes
```

#### 5. Backup Metrics Missing

**Symptom:** `postgres_backup_*` metrics not in Prometheus

**Solutions:**
```bash
# Run backup monitor manually
./scripts/backup_monitor.sh --verbose

# Check Pushgateway
curl http://localhost:9091/metrics | grep backup

# Verify Prometheus scrapes Pushgateway
# Prometheus → Status → Targets → pushgateway
```

### Logging and Debugging

**Enable debug logging for postgres_exporter:**
```yaml
environment:
  - PG_EXPORTER_LOG_LEVEL=debug
```

**Enable Prometheus debug:**
```yaml
command:
  - '--log.level=debug'
```

**View all container logs:**
```bash
docker-compose -f docker-compose.monitoring.yml logs --tail=100 -f
```

---

## Best Practices

### Metric Collection

1. **Scrape Intervals**
   - Infrastructure (DB, Redis): 30s
   - Application services: 15s
   - Backup scripts: On-demand (cron)

2. **Data Retention**
   - Prometheus: 30 days
   - Longer retention: Use Thanos or VictoriaMetrics

3. **Query Optimization**
   - Use `rate()` for counters
   - Use `increase()` for total changes
   - Limit `topk()` results to avoid cardinality explosion

### Alerting

1. **Alert Fatigue Prevention**
   - Set appropriate `for` durations
   - Use severity levels correctly
   - Implement alert routing by team

2. **Notification Channels**
   - Critical alerts → PagerDuty (immediate)
   - Warnings → Slack (batched)
   - Info → Email (daily digest)

3. **Alert Naming**
   - Use descriptive names
   - Include component name
   - Indicate severity in summary

### Dashboard Design

1. **Organization**
   - Group related metrics
   - Use consistent color schemes
   - Include thresholds on gauges

2. **Performance**
   - Limit queries per dashboard
   - Use query caching
   - Set appropriate refresh rates

3. **Accessibility**
   - Add descriptions to panels
   - Use bilingual labels (EN/AR)
   - Include links to runbooks

### Security

1. **Credentials**
   - Use environment variables
   - Rotate passwords regularly
   - Enable TLS for exporters

2. **Access Control**
   - Disable anonymous access
   - Use RBAC in Grafana
   - Audit dashboard changes

3. **Network Isolation**
   - Use dedicated monitoring network
   - Restrict exporter ports
   - Enable firewall rules

---

## Appendix

### A. Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.monitoring.yml` | Monitoring stack definition |
| `prometheus/prometheus.yml` | Prometheus configuration |
| `prometheus/alerts.yml` | Alert rules |
| `alertmanager/alertmanager.yml` | Alert routing |
| `postgres-exporter-queries.yaml` | Custom PostgreSQL queries |
| `grafana/provisioning/dashboards/sahool-database-performance.json` | Database dashboard |
| `scripts/backup_monitor.sh` | Backup monitoring script |

### B. Useful PromQL Queries

**Connection pool usage percentage:**
```promql
(pg_stat_database_numbackends{datname="sahool"} / pg_settings_max_connections) * 100
```

**Cache hit ratio:**
```promql
rate(pg_stat_database_blks_hit{datname="sahool"}[5m]) /
(rate(pg_stat_database_blks_hit{datname="sahool"}[5m]) +
 rate(pg_stat_database_blks_read{datname="sahool"}[5m]))
```

**Database size growth rate (MB/day):**
```promql
increase(pg_database_size_size_bytes{datname="sahool"}[1d]) / 1024 / 1024
```

**Top 5 tables by dead tuples:**
```promql
topk(5, pg_autovacuum_activity_n_dead_tup)
```

**Replication lag (all replicas):**
```promql
max(pg_replication_lag_lag_seconds) by (application_name)
```

**WAL generation rate (MB/hour):**
```promql
rate(pg_wal_size_bytes[1h]) / 1024 / 1024
```

### C. PostgreSQL Tuning Guide

Based on monitoring insights:

**If cache hit ratio < 95%:**
```sql
-- Increase shared_buffers
ALTER SYSTEM SET shared_buffers = '4GB';
```

**If checkpoints too frequent:**
```sql
ALTER SYSTEM SET max_wal_size = '2GB';
ALTER SYSTEM SET checkpoint_timeout = '15min';
```

**If autovacuum not keeping up:**
```sql
ALTER SYSTEM SET autovacuum_max_workers = 4;
ALTER SYSTEM SET autovacuum_naptime = '30s';
```

**If connections near limit:**
```sql
-- Increase max connections (requires restart)
ALTER SYSTEM SET max_connections = 200;

-- Or use connection pooling (PgBouncer)
```

### D. Support and Resources

**Documentation:**
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- postgres_exporter: https://github.com/prometheus-community/postgres_exporter
- PostgreSQL Monitoring: https://www.postgresql.org/docs/current/monitoring.html

**Internal Resources:**
- Audit Report: `/tests/database/MONITORING_AUDIT.md`
- Runbooks: `/docs/RUNBOOKS.md`
- Architecture: `/docs/OBSERVABILITY.md`

**Support Contacts:**
- Database Team: database-team@sahool.example.com
- Infrastructure Team: infra-team@sahool.example.com
- On-Call: Use PagerDuty escalation

---

## Conclusion

This monitoring configuration provides **production-grade database observability** for the SAHOOL platform. With comprehensive metrics, automated alerts, and detailed dashboards, the operations team can proactively identify and resolve issues before they impact users.

**Key Achievements:**
- ✅ 15+ advanced database metrics
- ✅ 20+ alert rules covering critical scenarios
- ✅ 13-panel Grafana dashboard
- ✅ Automated backup monitoring
- ✅ Multi-channel alerting
- ✅ Production-ready deployment

**Next Steps:**
1. Deploy monitoring stack to production
2. Configure alerting channels (Slack, PagerDuty)
3. Schedule backup monitoring cron
4. Train operations team on dashboards
5. Establish on-call procedures
6. Regular review and tuning

---

**Document Version:** 2.0.0
**Last Updated:** 2026-01-06
**Status:** ✅ Production-Ready
