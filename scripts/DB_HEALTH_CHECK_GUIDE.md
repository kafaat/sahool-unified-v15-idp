# Database Health Check Guide

# دليل فحص صحة قاعدة البيانات

## Overview / نظرة عامة

The `db_health_check.sh` script provides comprehensive database health monitoring for SAHOOL's PostgreSQL and PgBouncer infrastructure.

يوفر سكريبت `db_health_check.sh` مراقبة شاملة لصحة قاعدة البيانات لبنية PostgreSQL و PgBouncer الخاصة بـ SAHOOL.

---

## Features / المميزات

### Health Checks Performed / الفحوصات المُجراة

1. **PostgreSQL Connectivity / اتصال PostgreSQL**
   - Verifies direct connection to PostgreSQL
   - يتحقق من الاتصال المباشر بـ PostgreSQL

2. **PgBouncer Pool Status / حالة تجمع PgBouncer**
   - Checks PgBouncer availability and pool status
   - يفحص توافر PgBouncer وحالة التجمع

3. **Active Connections / الاتصالات النشطة**
   - Monitors connection count vs max_connections
   - يراقب عدد الاتصالات مقابل max_connections
   - Alerts when usage exceeds thresholds (80% warning, 95% critical)
   - ينبه عند تجاوز الحدود (80% تحذير، 95% حرج)

4. **Long-Running Queries / الاستعلامات طويلة التنفيذ**
   - Detects queries running longer than 30 seconds (configurable)
   - يكتشف الاستعلامات التي تعمل لأكثر من 30 ثانية (قابل للتكوين)

5. **Disk Space Usage / استخدام مساحة القرص**
   - Monitors database data directory disk usage
   - يراقب استخدام القرص لدليل بيانات قاعدة البيانات
   - Alerts at 80% (warning) and 90% (critical)
   - ينبه عند 80% (تحذير) و 90% (حرج)

6. **Replication Lag / تأخر النسخ الاحتياطي** (Optional)
   - Checks replication lag for primary-replica setups
   - يفحص تأخر النسخ لإعدادات الأساسي-النسخة
   - Alerts on lag > 10s (warning) or > 60s (critical)
   - ينبه عند التأخر > 10 ثانية (تحذير) أو > 60 ثانية (حرج)

7. **Database Size / حجم قاعدة البيانات**
   - Reports current database size
   - يعرض حجم قاعدة البيانات الحالي

---

## Quick Start / البداية السريعة

### Basic Usage / الاستخدام الأساسي

```bash
# Set required environment variable / تعيين متغير البيئة المطلوب
export POSTGRES_PASSWORD="your_password"

# Run basic health check / تشغيل فحص الصحة الأساسي
./scripts/db_health_check.sh
```

### JSON Output for Monitoring / مخرجات JSON للمراقبة

```bash
# Get JSON output suitable for monitoring systems
# الحصول على مخرجات JSON مناسبة لأنظمة المراقبة
./scripts/db_health_check.sh --json
```

**Example JSON Output:**

```json
{
  "timestamp": "2025-01-06T12:00:00Z",
  "status": "healthy",
  "exit_code": 0,
  "checks": {
    "postgres_connectivity": "healthy",
    "pgbouncer_status": "healthy",
    "connection_count": "healthy",
    "long_queries": "healthy",
    "disk_space": "healthy"
  },
  "metrics": {
    "active_connections": 45,
    "max_connections": 100,
    "connection_usage_pct": 45,
    "long_running_queries": 0,
    "disk_usage_pct": 65,
    "disk_total": "100G",
    "disk_available": "35G",
    "database_size": "2.5GB",
    "pgbouncer_pools": 5
  }
}
```

---

## Configuration / التكوين

### Environment Variables / متغيرات البيئة

| Variable            | Default      | Description (EN)    | الوصف (AR)               |
| ------------------- | ------------ | ------------------- | ------------------------ |
| `POSTGRES_HOST`     | localhost    | PostgreSQL hostname | اسم مضيف PostgreSQL      |
| `POSTGRES_PORT`     | 5432         | PostgreSQL port     | منفذ PostgreSQL          |
| `PGBOUNCER_HOST`    | localhost    | PgBouncer hostname  | اسم مضيف PgBouncer       |
| `PGBOUNCER_PORT`    | 6432         | PgBouncer port      | منفذ PgBouncer           |
| `POSTGRES_USER`     | sahool       | Database user       | مستخدم قاعدة البيانات    |
| `POSTGRES_PASSWORD` | _(required)_ | Database password   | كلمة مرور قاعدة البيانات |
| `POSTGRES_DB`       | sahool       | Database name       | اسم قاعدة البيانات       |
| `DB_CHECK_TIMEOUT`  | 30           | Timeout in seconds  | المهلة الزمنية بالثواني  |

### Command Line Options / خيارات سطر الأوامر

```bash
# Custom PostgreSQL host and port
./scripts/db_health_check.sh --postgres-host db.example.com --postgres-port 5432

# Custom PgBouncer connection
./scripts/db_health_check.sh --pgbouncer-host pgbouncer.example.com --pgbouncer-port 6432

# Enable replication lag check
./scripts/db_health_check.sh --check-replication

# Custom thresholds
./scripts/db_health_check.sh \
  --disk-warning 85 \
  --disk-critical 95 \
  --conn-warning 75 \
  --conn-critical 90 \
  --query-timeout 60

# JSON output only (no colored logs)
./scripts/db_health_check.sh --json
```

---

## Exit Codes / رموز الخروج

| Code  | Status   | Description (EN)                           | الوصف (AR)                              |
| ----- | -------- | ------------------------------------------ | --------------------------------------- |
| **0** | Healthy  | All checks passed                          | كل الفحوصات نجحت                        |
| **1** | Warning  | Some metrics exceed warning thresholds     | بعض المقاييس تجاوزت حدود التحذير        |
| **2** | Critical | Critical issues detected or cannot connect | تم اكتشاف مشاكل حرجة أو لا يمكن الاتصال |

---

## Integration Examples / أمثلة التكامل

### 1. Cron Job / مهمة Cron

```bash
# Add to crontab to run every 5 minutes
# أضف إلى crontab للتشغيل كل 5 دقائق
*/5 * * * * /path/to/scripts/db_health_check.sh --json >> /var/log/db_health.log 2>&1
```

### 2. Systemd Timer / مؤقت Systemd

**Service file** (`/etc/systemd/system/db-health-check.service`):

```ini
[Unit]
Description=Database Health Check
After=network.target

[Service]
Type=oneshot
Environment="POSTGRES_PASSWORD=your_password"
ExecStart=/opt/sahool/scripts/db_health_check.sh --json
User=sahool
StandardOutput=journal
StandardError=journal
```

**Timer file** (`/etc/systemd/system/db-health-check.timer`):

```ini
[Unit]
Description=Run Database Health Check every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Unit=db-health-check.service

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable --now db-health-check.timer
sudo systemctl list-timers
```

### 3. Docker Container / حاوية Docker

```dockerfile
FROM postgres:16-alpine

# Install dependencies
RUN apk add --no-cache bash bc coreutils

# Copy health check script
COPY scripts/db_health_check.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/db_health_check.sh

# Set as healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD /usr/local/bin/db_health_check.sh --json || exit 1
```

### 4. Kubernetes Probes / مجسات Kubernetes

See `db_health_check.k8s.example.yaml` for complete examples.

**Quick example:**

```yaml
livenessProbe:
  exec:
    command:
      - /scripts/db_health_check.sh
      - --json
  initialDelaySeconds: 30
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 3

readinessProbe:
  exec:
    command:
      - /scripts/db_health_check.sh
      - --json
  initialDelaySeconds: 10
  periodSeconds: 15
  timeoutSeconds: 10
  failureThreshold: 2
```

### 5. Monitoring Integration / تكامل المراقبة

#### Prometheus Exporter

```bash
#!/bin/bash
# prometheus_db_metrics.sh

METRICS=$(./scripts/db_health_check.sh --json)

# Parse JSON and expose as Prometheus metrics
echo "# HELP db_health_status Database health status (0=healthy, 1=warning, 2=critical)"
echo "# TYPE db_health_status gauge"
echo "db_health_status $(echo $METRICS | jq -r '.exit_code')"

echo "# HELP db_active_connections Number of active database connections"
echo "# TYPE db_active_connections gauge"
echo "db_active_connections $(echo $METRICS | jq -r '.metrics.active_connections')"

echo "# HELP db_connection_usage_pct Database connection usage percentage"
echo "# TYPE db_connection_usage_pct gauge"
echo "db_connection_usage_pct $(echo $METRICS | jq -r '.metrics.connection_usage_pct')"

echo "# HELP db_long_running_queries Number of long-running queries"
echo "# TYPE db_long_running_queries gauge"
echo "db_long_running_queries $(echo $METRICS | jq -r '.metrics.long_running_queries')"

echo "# HELP db_disk_usage_pct Disk usage percentage"
echo "# TYPE db_disk_usage_pct gauge"
echo "db_disk_usage_pct $(echo $METRICS | jq -r '.metrics.disk_usage_pct')"
```

#### Grafana Alert

```yaml
# Grafana alerting rule example
apiVersion: 1
groups:
  - name: database_health
    interval: 1m
    rules:
      - alert: DatabaseConnectionsHigh
        expr: db_connection_usage_pct > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connections high ({{ $value }}%)"
          description: "Database connection usage is above 80%"

      - alert: DatabaseConnectionsCritical
        expr: db_connection_usage_pct > 95
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connections critical ({{ $value }}%)"
          description: "Database connection usage is above 95%"

      - alert: LongRunningQueries
        expr: db_long_running_queries > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Multiple long-running queries detected"
          description: "{{ $value }} queries running longer than threshold"
```

---

## Troubleshooting / استكشاف الأخطاء وإصلاحها

### Common Issues / المشاكل الشائعة

#### 1. "POSTGRES_PASSWORD is required"

**Problem:** Missing password environment variable
**Solution:**

```bash
export POSTGRES_PASSWORD="your_password"
# Or pass via file
export POSTGRES_PASSWORD=$(cat /path/to/password/file)
```

#### 2. "Cannot connect to PostgreSQL"

**Possible causes:**

- Database is down / قاعدة البيانات متوقفة
- Incorrect host/port / المضيف/المنفذ غير صحيح
- Network connectivity issues / مشاكل اتصال الشبكة
- Firewall blocking connection / جدار الحماية يحجب الاتصال

**Debug:**

```bash
# Test connectivity manually
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;"

# Check if PostgreSQL is listening
netstat -tlnp | grep 5432

# Check logs
docker logs sahool-postgres
# or
journalctl -u postgresql
```

#### 3. "PgBouncer not available"

**Note:** This is a WARNING, not CRITICAL. The script continues checking PostgreSQL directly.

**If PgBouncer should be available:**

```bash
# Check PgBouncer status
docker logs sahool-pgbouncer

# Test connection
psql -h $PGBOUNCER_HOST -p $PGBOUNCER_PORT -U $POSTGRES_USER -d pgbouncer -c "SHOW POOLS;"
```

#### 4. High Connection Usage

**Investigation:**

```sql
-- Check active connections by state
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;

-- Find idle connections
SELECT pid, usename, application_name, client_addr, state,
       now() - state_change as idle_time
FROM pg_stat_activity
WHERE state = 'idle'
ORDER BY state_change;

-- Kill idle connections (be careful!)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND now() - state_change > interval '10 minutes';
```

#### 5. Long-Running Queries

**Investigation:**

```sql
-- View long-running queries
SELECT pid, usename, application_name, client_addr,
       now() - query_start as runtime,
       state, query
FROM pg_stat_activity
WHERE state = 'active'
  AND query NOT LIKE '%pg_stat_activity%'
  AND now() - query_start > interval '30 seconds'
ORDER BY runtime DESC;

-- Cancel a query
SELECT pg_cancel_backend(pid);

-- Terminate a connection (more forceful)
SELECT pg_terminate_backend(pid);
```

---

## Security Considerations / اعتبارات الأمان

1. **Password Storage / تخزين كلمة المرور**
   - Never hardcode passwords / لا تقم بترميز كلمات المرور
   - Use environment variables or secret management / استخدم متغيرات البيئة أو إدارة الأسرار
   - In Kubernetes, use Secrets / في Kubernetes، استخدم Secrets
   - In production, use Vault, AWS Secrets Manager, etc. / في الإنتاج، استخدم Vault أو AWS Secrets Manager

2. **Network Access / الوصول إلى الشبكة**
   - Run health checks from trusted networks only / قم بتشغيل فحوصات الصحة من الشبكات الموثوقة فقط
   - Use read-only database user if possible / استخدم مستخدم قاعدة بيانات للقراءة فقط إن أمكن
   - Restrict `pg_hba.conf` appropriately / قم بتقييد `pg_hba.conf` بشكل مناسب

3. **Logging / التسجيل**
   - JSON output doesn't contain passwords / مخرجات JSON لا تحتوي على كلمات مرور
   - Avoid logging sensitive connection strings / تجنب تسجيل سلاسل الاتصال الحساسة

---

## Performance Impact / تأثير الأداء

The health check script is designed to be lightweight:

- **CPU**: Minimal (< 50m CPU in Kubernetes)
- **Memory**: < 64Mi RAM
- **Network**: Few small SQL queries
- **Execution Time**: Typically 1-3 seconds

**Recommended frequency:**

- Development: Every 30-60 seconds / كل 30-60 ثانية
- Production: Every 15-30 seconds for critical systems / كل 15-30 ثانية للأنظمة الحرجة
- Monitoring: Every 1-5 minutes / كل 1-5 دقائق

---

## Related Documentation / الوثائق ذات الصلة

- [PostgreSQL Monitoring Best Practices](https://www.postgresql.org/docs/current/monitoring.html)
- [PgBouncer Documentation](https://www.pgbouncer.org/)
- [Kubernetes Health Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [SAHOOL Infrastructure Guide](../infrastructure/README.md)

---

## Support / الدعم

For issues or questions:

- GitHub Issues: https://github.com/kafaat/sahool-unified-v15-idp/issues
- Documentation: `/docs/operations/database-monitoring.md`
- Team Contact: devops@sahool.com

---

<p align="center">
  <sub>SAHOOL Database Health Check v1.0</sub>
  <br>
  <sub>January 2026</sub>
</p>
