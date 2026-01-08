# SAHOOL Grafana Infrastructure Monitoring Dashboards
# لوحات مراقبة البنية التحتية لمنصة سهول

## Overview - نظرة عامة

This directory contains comprehensive Grafana dashboards for monitoring the SAHOOL agricultural platform infrastructure, including PostgreSQL databases, Redis cache, NATS message queue, and Docker containers.

يحتوي هذا المجلد على لوحات مراقبة شاملة لبنية منصة سهول الزراعية، بما في ذلك قواعد بيانات PostgreSQL وذاكرة Redis المؤقتة ونظام الرسائل NATS وحاويات Docker.

## Dashboard Files - ملفات اللوحات

### 1. Infrastructure Overview Dashboard
**File:** `dashboards/infrastructure-overview.json`
**UID:** `sahool-infrastructure-overview`
**Folder:** Infrastructure

#### Metrics Covered:
- **Service Health Status** - حالة صحة الخدمات
  - PostgreSQL, Redis, NATS, Kong Gateway availability
  - Running container count
  - System uptime

- **PostgreSQL Metrics** - مقاييس PostgreSQL
  - Active database connections by database
  - Transaction rate (commits/rollbacks per second)
  - Replication lag monitoring
  - Cache hit ratio percentage
  - Database size tracking

- **Redis Metrics** - مقاييس Redis
  - Memory usage (used vs max)
  - Connected clients (active and blocked)
  - Operations per second
  - Cache hit rate percentage

- **NATS Metrics** - مقاييس NATS
  - Total connections
  - Message rate (in/out per second)
  - JetStream total streams
  - JetStream memory usage

- **Docker Container Metrics** - مقاييس الحاويات
  - CPU usage per container
  - Memory usage per container
  - Network I/O (receive/transmit)
  - Disk I/O (read/write)

#### Refresh Rate: 30 seconds
#### Time Range: Last 1 hour (default)

---

### 2. Database Performance Dashboard
**File:** `dashboards/database-performance.json`
**UID:** `sahool-database-performance`
**Folder:** Database

#### Metrics Covered:
- **PostgreSQL Overview** - نظرة عامة
  - Total active connections
  - Queries per second
  - Cache hit ratio gauge
  - Database size

- **Query Performance** - أداء الاستعلامات
  - Query duration percentiles (p50, p95, p99)
  - Query rate by type (SELECT, INSERT, UPDATE, DELETE)
  - Top 10 slowest queries table

- **Connection Pool Statistics (PgBouncer)** - إحصائيات مجموعة الاتصالات
  - Pool connections (active, waiting, server active, server idle)
  - Average wait times
  - Pool usage percentage
  - Query throughput and bytes sent/received

- **Slow Query Tracking** - تتبع الاستعلامات البطيئة
  - Detection of queries exceeding thresholds
  - High fetch rate monitoring

- **Replication Status** - حالة النسخ المتماثل
  - Replication lag in seconds
  - WAL archiving status (archived/failed counts)
  - Replication status details table

- **Database Locks** - أقفال قاعدة البيانات
  - Lock count by mode
  - Deadlock rate monitoring

#### Refresh Rate: 30 seconds
#### Time Range: Last 1 hour (default)
#### Variables:
- `interval`: Time range for queries (1m, 5m, 15m, 1h)
- `database`: Filter by database name (multi-select)

---

## Provisioning Configuration - إعدادات التوفير

**File:** `provisioning/dashboards/infrastructure.yml`

This configuration file enables automatic loading of dashboards into Grafana on startup.

### Providers:
1. **SAHOOL Infrastructure Dashboards**
   - Folder: Infrastructure
   - Path: `/var/lib/grafana/dashboards/infrastructure`
   - Auto-reload: Every 30 seconds

2. **SAHOOL Database Dashboards**
   - Folder: Database
   - Path: `/var/lib/grafana/dashboards/database`
   - Auto-reload: Every 30 seconds

### Features:
- ✅ Auto-reload dashboards every 30 seconds
- ✅ UI updates allowed
- ✅ Organized into separate folders
- ✅ Bilingual labels (English/Arabic)

---

## Prometheus Data Sources - مصادر بيانات Prometheus

The dashboards use metrics from the following Prometheus exporters:

### 1. PostgreSQL Exporter (Port 9187)
Metrics: `pg_stat_database_*`, `pg_stat_replication_*`, `pg_locks_*`, etc.

### 2. Redis Exporter (Port 9121)
Metrics: `redis_memory_*`, `redis_connected_clients`, `redis_commands_*`, etc.

### 3. NATS Exporter (Port 7777)
Metrics: `gnatsd_*`, `nats_jetstream_*`

### 4. Node Exporter (Port 9100)
Metrics: `node_*`, `container_*`

### 5. PgBouncer Exporter
Metrics: `pgbouncer_pools_*`, `pgbouncer_stats_*`

---

## Installation & Setup - التثبيت والإعداد

### 1. Using Docker Compose

The dashboards are automatically provisioned when you start the monitoring stack:

```bash
cd /home/user/sahool-unified-v15-idp/infrastructure/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Manual Import

If you need to import dashboards manually:

1. Open Grafana at http://localhost:3002
2. Login with admin credentials
3. Navigate to **Dashboards** → **Import**
4. Upload the JSON files from `dashboards/` directory

### 3. Verify Installation

```bash
# Check Grafana logs
docker logs sahool-monitoring-grafana

# Verify dashboard provisioning
curl -s http://admin:password@localhost:3002/api/search?type=dash-db | jq
```

---

## Dashboard Access - الوصول للوحات

### Default URLs:
- **Grafana UI:** http://localhost:3002
- **Default Credentials:**
  - Username: `admin`
  - Password: Set via `GRAFANA_ADMIN_PASSWORD` environment variable

### Dashboard Navigation:
1. **Infrastructure Overview:** Dashboards → Infrastructure → SAHOOL Infrastructure Overview
2. **Database Performance:** Dashboards → Database → SAHOOL Database Performance

---

## Configuration - الإعدادات

### Time Settings:
- **Timezone:** Asia/Riyadh (Yemen timezone)
- **Week Start:** Saturday (Islamic calendar alignment)
- **Default Time Range:** Last 1 hour
- **Refresh Intervals:** 10s, 30s, 1m, 5m, 15m, 30m, 1h

### Thresholds - العتبات:

#### PostgreSQL:
- Connections: Yellow at 80, Red at 95
- Cache Hit Ratio: Red below 90%, Yellow at 90-95%, Green above 95%
- Replication Lag: Yellow at 5s, Red at 10s

#### Redis:
- Memory: Yellow at 5GB, Red at 6GB
- Cache Hit Rate: Red below 80%, Yellow at 80-90%, Green above 90%

#### Containers:
- CPU: Yellow at 70%, Red at 85%
- Memory: Yellow at 70%, Red at 80%

---

## Customization - التخصيص

### Adding Custom Panels:
1. Edit the dashboard JSON files in `dashboards/` directory
2. Add new panel configuration
3. Save and restart Grafana or wait for auto-reload

### Modifying Queries:
All dashboard panels use PromQL queries. Example:

```promql
# PostgreSQL connections
pg_stat_database_numbackends{datname!=""}

# Redis memory usage
redis_memory_used_bytes

# NATS message rate
rate(gnatsd_varz_in_msgs[5m])
```

### Adding Variables:
Edit the `templating.list` section in dashboard JSON to add new variables.

---

## Troubleshooting - استكشاف الأخطاء

### No Data Displayed:
1. Verify Prometheus is running and scraping targets:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

2. Check exporter availability:
   ```bash
   curl http://localhost:9187/metrics  # PostgreSQL
   curl http://localhost:9121/metrics  # Redis
   curl http://localhost:7777/metrics  # NATS
   ```

3. Verify Grafana datasource configuration:
   - Navigate to Configuration → Data Sources → Prometheus
   - Test connection

### Dashboard Not Loading:
1. Check Grafana logs:
   ```bash
   docker logs sahool-monitoring-grafana
   ```

2. Verify provisioning path in docker-compose:
   ```yaml
   volumes:
     - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro
     - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
   ```

### Metrics Missing:
1. Ensure all exporters are running:
   ```bash
   docker ps | grep exporter
   ```

2. Check Prometheus configuration includes all scrape jobs:
   ```bash
   cat infrastructure/monitoring/prometheus/prometheus.yml
   ```

---

## Best Practices - أفضل الممارسات

### Performance:
- Use appropriate time ranges to avoid overloading Prometheus
- Limit the number of concurrent dashboard viewers
- Set reasonable refresh intervals (30s recommended)

### Monitoring:
- Review slow queries regularly
- Monitor replication lag closely in HA setups
- Set up alerts for critical thresholds
- Track connection pool usage to prevent exhaustion

### Maintenance:
- Regularly backup dashboard JSON files
- Version control dashboard changes
- Document custom modifications
- Test dashboards after Grafana upgrades

---

## Related Documentation - الوثائق ذات الصلة

- [Prometheus Configuration](../monitoring/prometheus/prometheus.yml)
- [Grafana Provisioning](./provisioning/dashboards/)
- [PostgreSQL Exporter Queries](../monitoring/postgres-exporter-queries.yaml)
- [SAHOOL Monitoring Stack](../monitoring/docker-compose.monitoring.yml)

---

## Support - الدعم

For issues or questions:
- Check Grafana documentation: https://grafana.com/docs/
- Review Prometheus best practices: https://prometheus.io/docs/practices/
- Contact SAHOOL platform team

---

## Version History - سجل الإصدارات

- **v1.0.0** (2025-01-07): Initial release
  - Infrastructure Overview Dashboard
  - Database Performance Dashboard
  - Provisioning configuration

---

## License - الترخيص

Part of the SAHOOL Agricultural Platform
© 2025 SAHOOL Platform Team
