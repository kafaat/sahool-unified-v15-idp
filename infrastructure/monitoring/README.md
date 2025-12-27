# SAHOOL Platform Monitoring Stack
# مجموعة المراقبة لمنصة سهول الزراعية

## Overview | نظرة عامة

This monitoring stack provides comprehensive observability for the SAHOOL agricultural platform, monitoring **39 microservices** plus infrastructure components.

توفر مجموعة المراقبة هذه رؤية شاملة لمنصة سهول الزراعية، مع مراقبة **39 خدمة دقيقة** بالإضافة إلى مكونات البنية التحتية.

## Components | المكونات

### 1. Prometheus
- **Time-series database** for metrics collection
- **Scrapes metrics** from all 39 services every 15 seconds
- **Retention**: 30 days, max 10GB
- **Port**: 9090

### 2. Grafana
- **Visualization platform** with pre-configured dashboards
- **Port**: 3002
- **Default credentials**: admin / (set via GRAFANA_ADMIN_PASSWORD)

### 3. Alertmanager
- **Alert routing and notifications**
- Supports Email, Slack, PagerDuty
- **Port**: 9093

### 4. Exporters | المُصدِّرات
- **PostgreSQL Exporter**: Database metrics (port 9187)
- **Redis Exporter**: Cache metrics (port 9121)
- **Node Exporter**: System metrics (port 9100)

## Monitored Services | الخدمات المراقبة

### Infrastructure Services (6)
- PostgreSQL (PostGIS)
- Redis
- NATS
- Qdrant
- MQTT
- Kong API Gateway

### Core Services (33)
- field-core, field-ops, field-chat
- ndvi-engine, weather-core, weather-advanced
- crop-health, crop-health-ai, crop-growth-model
- agro-advisor, agro-rules, fertilizer-advisor
- irrigation-smart, virtual-sensors, yield-engine, yield-prediction
- satellite-service, indicators-service
- iot-gateway, equipment-service, task-service
- community-chat, notification-service, ws-gateway
- ai-advisor, astronomical-calendar
- research-core, disaster-assessment, lai-estimation
- marketplace-service, billing-core
- admin-dashboard, provider-config

## Quick Start | البدء السريع

### Prerequisites | المتطلبات الأساسية

```bash
# 1. Ensure main SAHOOL platform is running
# تأكد من تشغيل منصة سهول الرئيسية
docker network ls | grep sahool-network

# 2. Set required environment variables
# قم بتعيين متغيرات البيئة المطلوبة
cp .env.example .env
# Edit .env with your values
```

### Start Monitoring Stack | تشغيل مجموعة المراقبة

```bash
# Start all monitoring services
# تشغيل جميع خدمات المراقبة
docker-compose -f docker-compose.monitoring.yml up -d

# Check service health
# فحص صحة الخدمات
docker-compose -f docker-compose.monitoring.yml ps

# View logs
# عرض السجلات
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Access Dashboards | الوصول إلى لوحات المراقبة

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3002
- **Alertmanager**: http://localhost:9093

## Configuration | الإعدادات

### Environment Variables | متغيرات البيئة

Create a `.env` file with the following variables:

```bash
# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password
GRAFANA_ROOT_URL=http://localhost:3002
GRAFANA_DOMAIN=localhost

# Database Credentials (for exporters)
POSTGRES_USER=sahool
POSTGRES_PASSWORD=your_postgres_password
REDIS_PASSWORD=your_redis_password

# Alert Notifications - Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@sahool.io
SMTP_PASSWORD=your_smtp_password
ALERT_EMAIL_DEFAULT=devops@sahool.io
ALERT_EMAIL_CRITICAL=sre@sahool.io,devops@sahool.io
ALERT_EMAIL_DATABASE=dba@sahool.io
ALERT_EMAIL_PERFORMANCE=performance@sahool.io
ALERT_EMAIL_AI_ML=ai-team@sahool.io

# Alert Notifications - Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL_DEFAULT=#sahool-alerts
SLACK_CHANNEL_CRITICAL=#sahool-critical
SLACK_CHANNEL_DATABASE=#sahool-database
SLACK_CHANNEL_PERFORMANCE=#sahool-performance
SLACK_CHANNEL_AI_ML=#sahool-ai-ml

# Alert Notifications - PagerDuty
PAGERDUTY_SERVICE_KEY=your_pagerduty_key

# Environment
ENVIRONMENT=production
```

## Dashboards | لوحات المراقبة

### SAHOOL Platform Overview
**Path**: Grafana → SAHOOL Platform Overview

**Panels**:
1. **Service Health Status** - حالة صحة الخدمات
   - Visual status of all 39 services

2. **Active Users** - المستخدمون النشطون
   - Real-time active user count

3. **Fields by Region** - الحقول حسب المنطقة
   - Distribution of agricultural fields

4. **Request Rate** - معدل الطلبات
   - Requests per second across services

5. **Error Rate** - معدل الأخطاء
   - 5xx error percentage by service

6. **Latency Percentiles** - نسب زمن الاستجابة المئوية
   - P50, P95, P99 latency metrics

7. **Database Connection Pool** - مجموعة اتصالات قاعدة البيانات
   - PostgreSQL connection usage

8. **Redis Memory Usage** - استخدام ذاكرة Redis
   - Cache memory consumption

9. **NATS Queue Backlog** - تراكم طابور NATS
   - Message queue pending messages

10. **Infrastructure Health** - صحة البنية التحتية
    - Status of all infrastructure services

## Alerts | التنبيهات

### Alert Categories | فئات التنبيهات

#### 1. Availability Alerts | تنبيهات التوفر
- **ServiceDown**: Service unavailable for >2 minutes
- **MultipleServicesDown**: >3 services down
- **PostgreSQLDown**: Critical database outage
- **RedisDown**: Cache unavailable
- **NATSDown**: Message queue unavailable

#### 2. Performance Alerts | تنبيهات الأداء
- **HighLatencyP95**: P95 latency >500ms for 5 minutes
- **HighLatencyP99**: P99 latency >1s for 3 minutes
- **HighAverageLatency**: Average latency >300ms

#### 3. Error Rate Alerts | تنبيهات معدل الأخطاء
- **HighErrorRate**: Error rate >1% for 3 minutes
- **CriticalErrorRate**: Error rate >5% for 1 minute

#### 4. Database Alerts | تنبيهات قاعدة البيانات
- **DatabaseConnectionPoolExhausted**: >85% connections used
- **DatabaseSlowQueries**: Queries running >30 seconds
- **DatabaseDeadlocks**: Deadlocks detected

#### 5. Redis Alerts | تنبيهات Redis
- **RedisMemoryHigh**: >85% memory usage
- **RedisCriticalMemory**: >95% memory usage
- **RedisHighEvictionRate**: >100 keys/sec evicted

#### 6. NATS Alerts | تنبيهات NATS
- **NATSQueueBacklog**: >10,000 pending messages
- **NATSCriticalBacklog**: >50,000 pending messages
- **NATSConsumerLag**: >1,000 unacked messages

## Maintenance | الصيانة

### Backup Configuration | نسخ الإعدادات احتياطياً

```bash
# Backup Grafana dashboards and datasources
# نسخ لوحات Grafana ومصادر البيانات
docker exec sahool-monitoring-grafana \
  tar -czf /var/lib/grafana/backup.tar.gz \
  /var/lib/grafana/dashboards \
  /etc/grafana/provisioning

# Copy backup to host
# نسخ النسخة الاحتياطية إلى المضيف
docker cp sahool-monitoring-grafana:/var/lib/grafana/backup.tar.gz ./grafana-backup.tar.gz
```

### Update Dashboards | تحديث لوحات المراقبة

```bash
# Reload Prometheus configuration
# إعادة تحميل إعدادات Prometheus
curl -X POST http://localhost:9090/-/reload

# Restart Grafana to load new dashboards
# إعادة تشغيل Grafana لتحميل اللوحات الجديدة
docker-compose -f docker-compose.monitoring.yml restart grafana
```

### Clean Up Data | تنظيف البيانات

```bash
# Stop monitoring stack
# إيقاف مجموعة المراقبة
docker-compose -f docker-compose.monitoring.yml down

# Remove volumes (WARNING: deletes all metrics data)
# حذف وحدات التخزين (تحذير: يحذف جميع بيانات المقاييس)
docker volume rm sahool-monitoring-prometheus-data
docker volume rm sahool-monitoring-grafana-data
docker volume rm sahool-monitoring-alertmanager-data
```

## Troubleshooting | استكشاف الأخطاء

### Prometheus Not Scraping Services | Prometheus لا يجمع البيانات

```bash
# Check Prometheus targets
# فحص أهداف Prometheus
curl http://localhost:9090/api/v1/targets

# Check if services are exposing metrics
# فحص إذا كانت الخدمات تعرض المقاييس
curl http://field-ops:8080/metrics
curl http://weather-core:8108/metrics
```

### Grafana Cannot Connect to Prometheus | Grafana لا يمكنه الاتصال بـ Prometheus

```bash
# Check network connectivity
# فحص الاتصال بالشبكة
docker exec sahool-monitoring-grafana ping -c 3 prometheus

# Verify datasource configuration
# التحقق من إعدادات مصدر البيانات
docker exec sahool-monitoring-grafana \
  cat /etc/grafana/provisioning/datasources/prometheus.yml
```

### Alerts Not Sending | التنبيهات لا ترسل

```bash
# Check Alertmanager configuration
# فحص إعدادات Alertmanager
curl http://localhost:9093/api/v1/status

# Test alert routing
# اختبار توجيه التنبيهات
curl -X POST http://localhost:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[{"labels":{"alertname":"TestAlert","severity":"warning"},"annotations":{"summary":"Test"}}]'
```

## Best Practices | أفضل الممارسات

1. **Regular Backups** | النسخ الاحتياطي المنتظم
   - Backup Grafana dashboards weekly
   - Export Prometheus data for long-term storage

2. **Alert Tuning** | ضبط التنبيهات
   - Adjust thresholds based on actual platform usage
   - Reduce alert fatigue by grouping related alerts

3. **Dashboard Customization** | تخصيص لوحات المراقبة
   - Create service-specific dashboards
   - Add business metrics (active users, fields created, etc.)

4. **Retention Policy** | سياسة الاحتفاظ بالبيانات
   - Default: 30 days
   - Adjust based on storage capacity and compliance requirements

5. **Security** | الأمان
   - Change default Grafana password immediately
   - Restrict access to monitoring ports (use firewall/VPN)
   - Enable HTTPS for production deployments

## Support | الدعم

For issues or questions:
- **Documentation**: `/docs/monitoring`
- **Email**: devops@sahool.io
- **Slack**: #sahool-monitoring

## License | الترخيص

© 2025 SAHOOL Platform. All rights reserved.
