# SAHOOL Platform - Production Deployment Guide

# دليل النشر للإنتاج - منصة سهول

**Version:** v16.0.0  
**Last Updated:** 2026-01-05  
**Status:** Production Ready ✅

---

## 📋 Overview | نظرة عامة

This comprehensive guide covers production deployment of the SAHOOL platform including:

- Environment configuration
- Database setup and optimization
- Security hardening
- Monitoring and logging
- Scaling strategies
- Backup and disaster recovery

هذا الدليل الشامل يغطي النشر للإنتاج لمنصة سهول بما في ذلك:

- تكوين البيئة
- إعداد قاعدة البيانات والتحسين
- تعزيز الأمان
- المراقبة والسجلات
- استراتيجيات التوسع
- النسخ الاحتياطي والاسترداد من الكوارث

---

## 🔐 Environment Variables Reference | مرجع المتغيرات البيئية

### Core Database | قاعدة البيانات الأساسية

```bash
# PostgreSQL Configuration
DATABASE_URL="postgresql://sahool_user:STRONG_PASSWORD@postgres:5432/sahool_db"
DATABASE_POOL_MIN=2          # Minimum connection pool size
DATABASE_POOL_MAX=10         # Maximum connection pool size
DATABASE_TIMEOUT=30000       # Connection timeout (ms)
DATABASE_SSL_MODE="require"  # SSL mode for production
DATABASE_STATEMENT_TIMEOUT=30000  # Query timeout (ms)

# PgBouncer Connection Pooler
PGBOUNCER_POOL_MODE="transaction"  # or "session"
PGBOUNCER_MAX_CLIENT_CONN=100
PGBOUNCER_DEFAULT_POOL_SIZE=20
```

### Security & Authentication | الأمان والمصادقة

```bash
# JWT Configuration
JWT_SECRET="GENERATE_STRONG_SECRET_KEY_MINIMUM_32_CHARS"
JWT_ALGORITHM="RS256"        # Recommended for production
JWT_EXPIRY="3600"           # Access token: 1 hour
REFRESH_TOKEN_EXPIRY="604800"  # Refresh token: 7 days

# Encryption
ENCRYPTION_KEY="GENERATE_32_BYTE_KEY"  # AES-256 requires 32 bytes
ENCRYPTION_ALGORITHM="AES-256-GCM"

# Password Policy
MIN_PASSWORD_LENGTH=12
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_NUMBERS=true
REQUIRE_SPECIAL_CHARS=true

# Security Headers (Already implemented in middleware)
ENABLE_HSTS=true            # Enforce HTTPS
ENABLE_CSP=true             # Content Security Policy
ENABLE_FRAME_PROTECTION=true
```

### API Gateway (Kong) | بوابة API

```bash
# Kong Configuration
KONG_ADMIN_URL="http://kong:8001"
KONG_PROXY_URL="http://kong:8000"
KONG_DATABASE="postgres"
KONG_PG_HOST="postgres"
KONG_PG_PORT=5432
KONG_PG_USER="kong_user"
KONG_PG_PASSWORD="KONG_DB_PASSWORD"
KONG_PG_DATABASE="kong_db"

# Rate Limiting (Default Tiers)
RATE_LIMIT_TIER_FREE="100/hour"
RATE_LIMIT_TIER_BASIC="1000/hour"
RATE_LIMIT_TIER_PRO="10000/hour"
RATE_LIMIT_TIER_ENTERPRISE="unlimited"
```

### Event Bus (NATS) | ناقل الأحداث

```bash
# NATS Configuration
NATS_URL="nats://nats:4222"
NATS_CLUSTER_URL="nats://nats:6222"
NATS_USER="sahool_nats"
NATS_PASSWORD="NATS_PASSWORD"
NATS_MAX_RECONNECT_ATTEMPTS=10
NATS_RECONNECT_TIME_WAIT=2000  # ms
```

### Caching (Redis) | التخزين المؤقت

```bash
# Redis Configuration
REDIS_URL="redis://redis:6379/0"
REDIS_PASSWORD="STRONG_REDIS_PASSWORD"
REDIS_MAX_RETRIES=3
REDIS_CONNECT_TIMEOUT=10000  # ms
REDIS_COMMAND_TIMEOUT=5000   # ms

# Redis Sentinel (for HA)
REDIS_SENTINEL_HOSTS="sentinel1:26379,sentinel2:26379,sentinel3:26379"
REDIS_SENTINEL_MASTER="sahool-master"
```

### Object Storage (MinIO) | تخزين الكائنات

```bash
# MinIO Configuration
MINIO_ENDPOINT="minio:9000"
MINIO_ACCESS_KEY="MINIO_ACCESS_KEY_MIN_24_CHARS"  # Recommended: 24+ chars (192 bits)
MINIO_SECRET_KEY="MINIO_SECRET_KEY_MIN_48_CHARS"  # Recommended: 48+ chars (384 bits)
MINIO_BUCKET="sahool-storage"
MINIO_USE_SSL=true
MINIO_REGION="us-east-1"
```

### External Services | الخدمات الخارجية

```bash
# Email (SMTP)
SMTP_HOST="smtp.example.com"
SMTP_PORT=587
SMTP_SECURE=true  # Use TLS
SMTP_USER="noreply@sahool.com"
SMTP_PASSWORD="SMTP_PASSWORD"
SMTP_FROM_NAME="SAHOOL Platform"
SMTP_FROM_EMAIL="noreply@sahool.com"

# SMS Provider (Twilio)
SMS_PROVIDER="twilio"
TWILIO_ACCOUNT_SID="YOUR_ACCOUNT_SID"
TWILIO_AUTH_TOKEN="YOUR_AUTH_TOKEN"
TWILIO_PHONE_NUMBER="+1234567890"

# Maps & Geocoding
GOOGLE_MAPS_API_KEY="YOUR_GOOGLE_MAPS_KEY"
MAPBOX_ACCESS_TOKEN="YOUR_MAPBOX_TOKEN"

# Satellite Imagery
SENTINEL_HUB_CLIENT_ID="YOUR_CLIENT_ID"
SENTINEL_HUB_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

### Monitoring & Logging | المراقبة والسجلات

```bash
# Application Logging
LOG_LEVEL="info"  # debug, info, warn, error
LOG_FORMAT="json"  # or "text"
LOG_OUTPUT="stdout"  # or file path

# Prometheus Metrics
ENABLE_METRICS=true
METRICS_PORT=9090
METRICS_PATH="/metrics"

# Sentry Error Tracking
SENTRY_DSN="https://your-sentry-dsn@sentry.io/project"
SENTRY_ENVIRONMENT="production"
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions

# OpenTelemetry (Optional)
OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4318"
OTEL_SERVICE_NAME="sahool-platform"
```

---

## 🔄 Database Migration Strategy | استراتيجية ترحيل قاعدة البيانات

### Pre-Production Checklist | قائمة التحقق قبل الإنتاج

```bash
# 1. Test migrations in staging
psql -U sahool_user -d sahool_staging \
  -f infrastructure/core/postgres/migrations/V20260105__add_additional_improvements.sql

# 2. Create database backup
pg_dump -U sahool_user sahool_db | gzip > backup_pre_migration_$(date +%Y%m%d).sql.gz

# 3. Verify backup
gunzip -c backup_pre_migration_*.sql.gz | head -100

# 4. Run migrations with rollback plan ready
psql -U sahool_user -d sahool_db \
  -f infrastructure/core/postgres/migrations/V20260105__add_additional_improvements.sql

# 5. Verify indexes were created
psql -U sahool_user -d sahool_db -c "
SELECT
  schemaname,
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE indexname LIKE 'idx_%_metadata_gin'
   OR indexname LIKE 'idx_sensor_readings_tenant_time'
ORDER BY tablename, indexname;
"
```

---

## 🚀 Production Deployment Steps | خطوات النشر للإنتاج

### Step 1: Prepare Infrastructure | الخطوة 1: تجهيز البنية التحتية

```bash
# Create production namespace (Kubernetes)
kubectl create namespace sahool-prod

# Create secrets with enhanced security
kubectl create secret generic sahool-secrets \
  --from-literal=jwt-secret=$(openssl rand -hex 32) \
  --from-literal=db-password=$(openssl rand -base64 32) \
  --from-literal=redis-password=$(openssl rand -base64 32) \
  --from-literal=minio-access-key=$(openssl rand -hex 24) \
  --from-literal=minio-secret-key=$(openssl rand -hex 48) \
  -n sahool-prod
```

### Step 2: Deploy Database | الخطوة 2: نشر قاعدة البيانات

```bash
# Deploy PostgreSQL with PostGIS
helm install postgresql bitnami/postgresql \
  --namespace sahool-prod \
  --set auth.username=sahool_user \
  --set auth.password=$DB_PASSWORD \
  --set auth.database=sahool_db \
  --set primary.persistence.size=100Gi \
  --set primary.resources.requests.memory=4Gi \
  --set primary.resources.requests.cpu=2 \
  --set image.tag=15

# Install PostGIS extension
kubectl exec -it postgresql-0 -n sahool-prod -- \
  psql -U sahool_user -d sahool_db -c "
  CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
  CREATE EXTENSION IF NOT EXISTS \"postgis\";
  CREATE EXTENSION IF NOT EXISTS \"postgis_topology\";
"
```

### Step 3: Run Migrations | الخطوة 3: تشغيل الترحيلات

```bash
# Create migration job
kubectl create job db-migrate \
  --image=sahool/migration-tool:latest \
  --namespace sahool-prod \
  -- /bin/sh -c "npm run db:migrate"

# Monitor migration
kubectl logs -f job/db-migrate -n sahool-prod
```

### Step 4: Deploy Services | الخطوة 4: نشر الخدمات

```bash
# Deploy using Helm
helm install sahool-prod ./helm/sahool \
  --namespace sahool-prod \
  --values helm/values.prod.yaml \
  --wait \
  --timeout 10m

# Verify deployment
kubectl get pods -n sahool-prod
kubectl get svc -n sahool-prod
```

### Step 5: Configure Ingress | الخطوة 5: تكوين Ingress

```bash
# Apply ingress configuration
kubectl apply -f helm/ingress.prod.yaml -n sahool-prod

# Verify ingress
kubectl get ingress -n sahool-prod
```

---

## 📊 Performance Optimization | تحسين الأداء

### Database Optimization | تحسين قاعدة البيانات

```sql
-- Monitor index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC
LIMIT 20;

-- Analyze table statistics
ANALYZE geo.fields;
ANALYZE inventory_items;
ANALYZE sensor_readings;

-- Vacuum to reclaim space
VACUUM ANALYZE;

-- Check bloat
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### Connection Pooling | تجميع الاتصالات

```ini
# PgBouncer configuration (config/pgbouncer.ini)
[databases]
sahool_db = host=postgres port=5432 dbname=sahool_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
```

---

## 🔍 Monitoring & Alerting | المراقبة والتنبيهات

### Health Check Endpoints | نقاط فحص الصحة

```bash
# Kong Gateway
curl http://localhost:8000/health

# Field Service
curl http://localhost:8095/health

# User Service
curl http://localhost:8096/health

# Database
docker exec postgres pg_isready -U sahool_user
```

### Prometheus Queries | استعلامات Prometheus

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Database connections
pg_stat_database_numbackends

# Memory usage
container_memory_usage_bytes
```

---

## 🔄 Backup & Recovery | النسخ الاحتياطي والاسترداد

### Automated Backups | النسخ الاحتياطي الآلي

```bash
# Create backup script
cat > /usr/local/bin/sahool-backup.sh << 'SCRIPT'
#!/bin/bash
set -e

BACKUP_DIR="/var/backups/sahool"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo "Creating database backup..."
pg_dump -U sahool_user -h localhost sahool_db | \
  gzip > $BACKUP_DIR/sahool_db_$DATE.sql.gz

# Backup to S3 (optional)
if command -v aws &> /dev/null; then
  aws s3 cp $BACKUP_DIR/sahool_db_$DATE.sql.gz \
    s3://sahool-backups/database/
fi

# Clean old backups
find $BACKUP_DIR -name "sahool_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: sahool_db_$DATE.sql.gz"
SCRIPT

chmod +x /usr/local/bin/sahool-backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/sahool-backup.sh >> /var/log/sahool-backup.log 2>&1" | crontab -
```

### Point-in-Time Recovery | الاسترداد لنقطة زمنية

```bash
# Enable WAL archiving in postgresql.conf
cat >> /etc/postgresql/15/main/postgresql.conf << EOF
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
archive_timeout = 300
EOF

# Restart PostgreSQL
systemctl restart postgresql
```

---

## 📈 Scaling Guidelines | إرشادات التوسع

### Auto-Scaling Configuration | تكوين التوسع التلقائي

```yaml
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: field-service-hpa
  namespace: sahool-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: field-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Load Testing | اختبار الحمل

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://api.sahool.com/health

# Using k6
k6 run --vus 100 --duration 5m tests/load-test.js
```

---

## 🛡️ Security Hardening | تعزيز الأمان

### Network Policies | سياسات الشبكة

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: field-service-network-policy
  namespace: sahool-prod
spec:
  podSelector:
    matchLabels:
      app: field-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: kong
      ports:
        - protocol: TCP
          port: 8095
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

### Security Scanning | فحص الأمان

```bash
# Scan Docker images for vulnerabilities
trivy image sahool/field-service:latest

# Scan Kubernetes manifests
trivy config helm/

# Runtime security with Falco (optional)
helm install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace
```

---

## 🔧 Troubleshooting Guide | دليل حل المشاكل

### Common Issues | المشاكل الشائعة

#### High Database Load | حمل عالي على قاعدة البيانات

```sql
-- Find slow queries
SELECT
  pid,
  now() - pg_stat_activity.query_start AS duration,
  query,
  state
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Terminate long-running query
SELECT pg_terminate_backend(pid);
```

#### Memory Issues | مشاكل الذاكرة

```bash
# Check memory usage
kubectl top pods -n sahool-prod

# Increase memory limit
kubectl set resources deployment field-service \
  --limits=memory=2Gi \
  -n sahool-prod
```

---

## 📚 References | المراجع

<<<<<<< HEAD
- [High Priority Fixes Implementation](../HIGH_PRIORITY_FIXES_IMPLEMENTATION.md)
- [Gaps and Recommendations](../GAPS_AND_RECOMMENDATIONS.md)
=======
- [High Priority Fixes Implementation](./implementations/HIGH_PRIORITY_FIXES_IMPLEMENTATION.md)
- [Gaps and Recommendations](./reports/GAPS_AND_RECOMMENDATIONS.md)
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
- [Rate Limiting Documentation](./RATE_LIMITING.md)
- [Rate Limiting Guide](../shared/middleware/RATE_LIMITING_GUIDE.md)
- [Security Headers](../shared/middleware/security_headers.py)
- [Backup Strategy](./backup-strategy.md)

---

**Author:** GitHub Copilot Agent  
**Version:** v1.0  
**Last Updated:** 2026-01-05
