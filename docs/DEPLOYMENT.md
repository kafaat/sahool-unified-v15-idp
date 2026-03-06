# SAHOOL Deployment Guide

# دليل نشر سهول

Comprehensive deployment guide for the SAHOOL National Agricultural Intelligence Platform.

دليل شامل لنشر منصة سهول للذكاء الزراعي الوطني.

**Version | الإصدار**: 16.0.0
**Last Updated | آخر تحديث**: February 2026

---

## Table of Contents | جدول المحتويات

1. [Overview](#overview--نظرة-عامة)
2. [Prerequisites](#prerequisites--المتطلبات-الأساسية)
3. [Quick Start (Docker Compose)](#quick-start-docker-compose--البدء-السريع)
4. [Production Deployment (Kubernetes)](#production-deployment-kubernetes--نشر-الإنتاج)
5. [Environment Configuration](#environment-configuration--تكوين-البيئة)
6. [Service Architecture](#service-architecture--هندسة-الخدمات)
7. [Database Setup](#database-setup--إعداد-قاعدة-البيانات)
8. [Security Configuration](#security-configuration--تكوين-الأمان)
9. [Monitoring Setup](#monitoring-setup--إعداد-المراقبة)
10. [Scaling Guidelines](#scaling-guidelines--إرشادات-التوسع)
11. [Backup & Recovery](#backup--recovery--النسخ-الاحتياطي-والاستعادة)
12. [Troubleshooting](#troubleshooting--استكشاف-الأخطاء)
13. [Post-Deployment Checklist](#post-deployment-checklist--قائمة-ما-بعد-النشر)

---

## Overview | نظرة عامة

SAHOOL can be deployed using two methods:

يمكن نشر سهول باستخدام طريقتين:

| Method | Use Case | Complexity |
|--------|----------|------------|
| **Docker Compose** | Development, Testing, Staging | Low |
| **Kubernetes + Helm** | Production, Enterprise | High |

### Deployment Tiers | مستويات النشر

| Tier | Services | Resources | Use Case |
|------|----------|-----------|----------|
| **Starter** | 15 core services | 8GB RAM, 4 CPU | Small farms |
| **Professional** | 35 services | 16GB RAM, 8 CPU | Medium operations |
| **Enterprise** | 57+ services | 32GB+ RAM, 16+ CPU | Large enterprises |

---

## Prerequisites | المتطلبات الأساسية

### Required Software | البرامج المطلوبة

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | Multi-container orchestration |
| Git | 2.x | Source control |
| OpenSSL | 1.1+ | Certificate generation |
| curl | 7.x+ | Health checks |

### For Kubernetes Deployment | لنشر Kubernetes

| Software | Version | Purpose |
|----------|---------|---------|
| kubectl | 1.25+ | Kubernetes CLI |
| Helm | 3.12+ | Package manager |
| K8s Cluster | 1.25+ | Container orchestration |
| Ingress Controller | - | Traffic routing (nginx recommended) |

### Hardware Requirements | متطلبات الأجهزة

| Environment | CPU | RAM | Storage | Network |
|-------------|-----|-----|---------|---------|
| Development | 4 cores | 8GB | 50GB SSD | 100 Mbps |
| Staging | 8 cores | 16GB | 100GB SSD | 1 Gbps |
| Production | 16+ cores | 32GB+ | 500GB+ SSD | 10 Gbps |

---

## Quick Start (Docker Compose) | البدء السريع

### Step 1: Clone Repository | استنساخ المستودع

```bash
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp
```

### Step 2: Configure Environment | تكوين البيئة

```bash
# Copy environment template
cp .env.example .env

# Generate secure secrets
./tools/env/generate_secrets.sh

# Or manually edit .env file
nano .env
```

**Key Environment Variables:**

```bash
# Database
DATABASE_URL=postgresql://sahool:secure_password@postgres:5432/sahool
POSTGRES_PASSWORD=secure_password_here

# JWT Authentication
JWT_SECRET_KEY=your-32-character-secret-key-here
JWT_ALGORITHM=HS256

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=redis_password_here

# NATS
NATS_URL=nats://nats:4222

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Step 3: Start Infrastructure | بدء البنية التحتية

```bash
# Start infrastructure services only
make infra-up

# Verify infrastructure is healthy
docker compose ps
```

### Step 4: Start Application Services | بدء خدمات التطبيق

```bash
# Start all services
make dev

# Or start specific package
make dev-starter        # Core services only
make dev-professional   # Professional package
make dev-enterprise     # All services
```

### Step 5: Run Database Migrations | تشغيل ترحيل قاعدة البيانات

```bash
# Run all migrations
make db-migrate

# Seed initial data (optional)
make db-seed
```

### Step 6: Verify Deployment | التحقق من النشر

```bash
# Check service health
make health

# View service status
make status

# Run smoke tests
make test-smoke
```

### Health Check Endpoints | نقاط فحص الصحة

```bash
# Kong API Gateway
curl http://localhost:8000/healthz

# Core Services
curl http://localhost:3000/healthz   # Field Management
curl http://localhost:8092/healthz   # Weather Service
curl http://localhost:8093/healthz   # Advisory Service
curl http://localhost:8110/healthz   # Notification Service

# Infrastructure
curl http://localhost:8222/healthz   # NATS
```

---

## Service Profiles (Docker Compose) | ملفات تعريف الخدمات

Some services are configured with Docker Compose profiles and will **NOT** start with the default `docker compose up`. They require explicit profile activation.

بعض الخدمات مُعدّة بملفات تعريف Docker Compose ولن تبدأ مع الأمر الافتراضي. تتطلب تفعيل الملف الشخصي بشكل صريح.

### Available Profiles | الملفات المتاحة

| Profile | Services | Requirements | Description |
|---------|----------|-------------|-------------|
| `default` | 68 services | - | All active application + infrastructure services |
| `gpu` | ollama, ollama-model-loader, vllm-deepseek, code-review-service | NVIDIA GPU, 16GB+ VRAM | GPU-accelerated AI/ML services |
| `deprecated` | yield-prediction | - | Legacy services replaced by newer versions |
| `demo` | demo-data | - | Demo data generator for testing |
| `optional` + `ai-agents` | code-review-agent | - | Optional AI agent services (dual profile) |

### Usage Examples | أمثلة الاستخدام

```bash
# Start all default services (68 active services)
# تشغيل جميع الخدمات النشطة الافتراضية
docker compose up -d

# Start with GPU services (vision, LLM inference)
# التشغيل مع خدمات GPU (الرؤية الحاسوبية والاستدلال)
docker compose --profile gpu up -d

# Start with demo data for testing
# التشغيل مع بيانات تجريبية للاختبار
docker compose --profile demo up -d

# Start AI agent services
# تشغيل خدمات وكلاء الذكاء الاصطناعي
docker compose --profile optional --profile ai-agents up -d

# Start with deprecated services (for migration testing only)
# تشغيل الخدمات المهملة (لاختبار الترحيل فقط)
docker compose --profile deprecated up -d

# Full stack (all profiles)
# التشغيل الكامل (جميع الملفات)
docker compose --profile gpu --profile demo --profile optional --profile ai-agents up -d
```

### GPU Profile Details | تفاصيل ملف GPU

The GPU profile includes services that require NVIDIA GPU hardware:

| Service | Port | GPU VRAM | Description |
|---------|------|----------|-------------|
| ollama | 11434 | 8GB+ | Local LLM server (Ollama 0.5.x) |
| ollama-model-loader | - | - | Model download and cache |
| vllm-deepseek | 8270 | 16GB+ | DeepSeek Coder 6.7B inference |
| code-review-service | 8102 | 4GB+ | GPU-accelerated code review |

> **Note**: Ensure NVIDIA Container Toolkit is installed before using the GPU profile.
> Install with: `apt-get install nvidia-container-toolkit`

---

## Production Deployment (Kubernetes) | نشر الإنتاج

### Step 1: Prepare Cluster | إعداد العنقود

```bash
# Verify kubectl is configured
kubectl cluster-info

# Create namespace
kubectl create namespace sahool

# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo update
```

### Step 2: Configure Secrets | تكوين الأسرار

```bash
# Create secrets
kubectl create secret generic sahool-secrets \
  --from-literal=database-password='secure_password' \
  --from-literal=jwt-secret='your-32-char-secret' \
  --from-literal=redis-password='redis_password' \
  -n sahool

# Or use HashiCorp Vault (recommended)
kubectl apply -f infrastructure/vault/vault-config.yaml
```

### Step 3: Deploy Infrastructure | نشر البنية التحتية

```bash
# Deploy PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace sahool \
  --set auth.postgresPassword=secure_password \
  --set auth.database=sahool \
  --set primary.persistence.size=100Gi

# Deploy Redis
helm install redis bitnami/redis \
  --namespace sahool \
  --set auth.password=redis_password \
  --set master.persistence.size=10Gi

# Deploy NATS
helm install nats nats/nats \
  --namespace sahool \
  --set cluster.enabled=true \
  --set cluster.replicas=3
```

### Step 4: Deploy SAHOOL Application | نشر تطبيق سهول

```bash
# Navigate to Helm chart
cd helm/sahool

# Build dependencies
helm dependency build

# Install with custom values
helm install sahool . \
  --namespace sahool \
  --values values-production.yaml \
  --set global.environment=production \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=api.sahool.io

# Or use ArgoCD for GitOps
kubectl apply -f gitops/argocd/applications/sahool-app.yaml
```

### Step 5: Configure Ingress | تكوين Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sahool-ingress
  namespace: sahool
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.sahool.io
      secretName: sahool-tls
  rules:
    - host: api.sahool.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: kong
                port:
                  number: 8000
```

### Step 6: Verify Production Deployment | التحقق من نشر الإنتاج

```bash
# Check pods
kubectl get pods -n sahool

# Check services
kubectl get svc -n sahool

# Check ingress
kubectl get ingress -n sahool

# View logs
kubectl logs -n sahool -l app=field-management-service --tail=100

# Run health checks
kubectl exec -n sahool deploy/kong -- curl localhost:8000/healthz
```

---

## Environment Configuration | تكوين البيئة

### Complete Environment Variables | متغيرات البيئة الكاملة

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| **Database** ||||
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `POSTGRES_USER` | Yes | sahool | Database username |
| `POSTGRES_PASSWORD` | Yes | - | Database password |
| `POSTGRES_DB` | Yes | sahool | Database name |
| `DB_POOL_SIZE` | No | 20 | Connection pool size |
| `DB_MAX_OVERFLOW` | No | 10 | Max overflow connections |
| **Authentication** ||||
| `JWT_SECRET_KEY` | Yes | - | JWT signing key (32+ chars) |
| `JWT_ALGORITHM` | No | HS256 | JWT algorithm |
| `JWT_EXPIRY_HOURS` | No | 24 | Token expiration |
| **Redis** ||||
| `REDIS_URL` | Yes | - | Redis connection URL |
| `REDIS_PASSWORD` | No | - | Redis password |
| `CACHE_TTL_SECONDS` | No | 300 | Default cache TTL |
| **NATS** ||||
| `NATS_URL` | Yes | - | NATS server URL |
| `NATS_CLUSTER_ID` | No | sahool | NATS cluster ID |
| **General** ||||
| `ENVIRONMENT` | Yes | development | Environment name |
| `LOG_LEVEL` | No | INFO | Logging level |
| `CORS_ORIGINS` | No | * | Allowed CORS origins |

### Feature Flags | علامات الميزات

| Flag | Default | Description |
|------|---------|-------------|
| `ENABLE_SECURITY` | true | Enable JWT authentication |
| `ENABLE_AUDIT_LOGGING` | true | Enable audit trail |
| `ENABLE_MTLS` | false | Enable mutual TLS |
| `ENABLE_RATE_LIMITING` | true | Enable rate limiting |
| `ENABLE_CACHING` | true | Enable Redis caching |
| `ENABLE_METRICS` | true | Enable Prometheus metrics |
| `ENABLE_TRACING` | false | Enable OpenTelemetry tracing |

---

## Service Architecture | هندسة الخدمات

### Service Categories & Ports | فئات الخدمات والمنافذ

#### Core Services (Starter Package) | الخدمات الأساسية

| Service | Port | Technology | Description |
|---------|------|------------|-------------|
| kong | 8000 | Kong | API Gateway |
| field-management | 3000 | Node.js | Field CRUD operations |
| weather-service | 8092 | Python | Weather data |
| task-service | 8103 | Python | Task management |
| notification-service | 8110 | Python | Push notifications |
| astronomical-calendar | 8111 | Python | Islamic calendar |

#### Intelligence Services (Professional) | خدمات الذكاء

| Service | Port | Technology | Description |
|---------|------|------------|-------------|
| vegetation-analysis | 8090 | Python | Satellite imagery |
| crop-intelligence | 8095 | Python | Crop health AI |
| ndvi-processor | 8118 | Python | NDVI computation |
| indicators-service | 8091 | Python | Field indicators |
| lai-estimation | 3022 | Node.js | Leaf Area Index |

#### Decision Services (Enterprise) | خدمات القرار

| Service | Port | Technology | Description |
|---------|------|------------|-------------|
| advisory-service | 8093 | Python | AI recommendations |
| irrigation-smart | 8094 | Python | Smart irrigation |
| yield-engine | 8098 | Python | Yield prediction |
| hydrology-service | 8165 | Python | Drainage analysis |
| leveling-optimizer | 8170 | Python | Field leveling |
| vision-service | 8150 | Python | Computer vision |

#### Infrastructure Services | خدمات البنية التحتية

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL + PostGIS |
| redis | 6379 | Redis cache |
| nats | 4222 | NATS message queue |
| pgbouncer | 6432 | Connection pooler |

---

## Database Setup | إعداد قاعدة البيانات

### PostgreSQL with PostGIS | PostgreSQL مع PostGIS

```bash
# Connect to database
make db-shell

# Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

# Verify extensions
SELECT PostGIS_Version();
```

### Run Migrations | تشغيل الترحيل

```bash
# Python services (Alembic)
alembic upgrade head

# Node.js services (Prisma)
npx prisma migrate deploy
npx prisma generate
```

### Database Optimization | تحسين قاعدة البيانات

```sql
-- Create spatial indexes
CREATE INDEX idx_fields_geom ON fields USING GIST (boundary);
CREATE INDEX idx_fields_tenant ON fields (tenant_id);

-- Vacuum and analyze
VACUUM ANALYZE fields;
VACUUM ANALYZE tasks;
```

---

## Security Configuration | تكوين الأمان

### TLS/SSL Certificates | شهادات TLS/SSL

```bash
# Generate self-signed certificates (development)
./tools/security/certs/generate_certs.sh

# For production, use Let's Encrypt
certbot certonly --webroot -w /var/www/html -d api.sahool.io
```

### Kong Security Plugins | إضافات أمان Kong

```yaml
# Rate limiting
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 5000
      policy: redis
      redis_host: redis

# JWT authentication
  - name: jwt
    config:
      claims_to_verify:
        - exp
        - nbf

# CORS
  - name: cors
    config:
      origins:
        - https://app.sahool.io
      methods:
        - GET
        - POST
        - PUT
        - DELETE
      headers:
        - Authorization
        - Content-Type
```

### Security Best Practices | أفضل ممارسات الأمان

1. **Rotate secrets regularly** - Use Vault for secret management
2. **Enable TLS everywhere** - Minimum TLS 1.2
3. **Use network policies** - Isolate service communication
4. **Enable audit logging** - Track all API access
5. **Regular security scans** - Run Trivy, Bandit, CodeQL

---

## Monitoring Setup | إعداد المراقبة

### Start Monitoring Stack | بدء مجموعة المراقبة

```bash
make monitoring-up
```

### Access Monitoring Tools | الوصول لأدوات المراقبة

| Tool | URL | Purpose |
|------|-----|---------|
| Prometheus | http://localhost:9090 | Metrics collection |
| Grafana | http://localhost:3002 | Dashboards |
| Jaeger | http://localhost:16686 | Distributed tracing |

### Key Metrics to Monitor | المقاييس الرئيسية للمراقبة

| Metric | Threshold | Action |
|--------|-----------|--------|
| Request latency (p99) | < 500ms | Investigate if exceeded |
| Error rate | < 1% | Alert if exceeded |
| CPU usage | < 80% | Scale if exceeded |
| Memory usage | < 85% | Scale if exceeded |
| Database connections | < 80% of pool | Increase pool size |

### Prometheus Alerts | تنبيهات Prometheus

```yaml
groups:
  - name: sahool-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Service {{ $labels.job }} is down
```

---

## Scaling Guidelines | إرشادات التوسع

### Horizontal Scaling | التوسع الأفقي

```bash
# Docker Compose
docker compose up -d --scale field-management=3 --scale weather-service=2

# Kubernetes
kubectl scale deployment field-management --replicas=3 -n sahool
```

### Recommended Replicas | النسخ الموصى بها

| Service | Development | Staging | Production |
|---------|-------------|---------|------------|
| Kong | 1 | 2 | 3-5 |
| Field Management | 1 | 2 | 3-5 |
| Weather Service | 1 | 2 | 2-3 |
| Advisory Service | 1 | 2 | 3-5 |
| NDVI Processor | 1 | 1 | 2-3 |
| WebSocket Gateway | 1 | 2 | 3-5 |

### Autoscaling (Kubernetes) | التوسع التلقائي

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: field-management-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: field-management
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## Backup & Recovery | النسخ الاحتياطي والاستعادة

### Database Backup | نسخ قاعدة البيانات احتياطيًا

```bash
# Full backup
pg_dump -h localhost -U sahool -d sahool -F c -f backup_$(date +%Y%m%d).dump

# With Docker
docker exec sahool-postgres pg_dump -U sahool sahool > backup.sql

# Restore
pg_restore -h localhost -U sahool -d sahool backup.dump
```

### Automated Backup Script | سكريبت النسخ الاحتياطي التلقائي

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -h postgres -U sahool -d sahool -F c -f $BACKUP_DIR/db_$DATE.dump

# Compress
gzip $BACKUP_DIR/db_$DATE.dump

# Retain last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_$DATE.dump.gz s3://sahool-backups/
```

### NATS JetStream Backup | نسخ NATS JetStream احتياطيًا

```bash
# Backup all streams
nats stream backup --all /backups/nats/

# Restore
nats stream restore /backups/nats/
```

---

## Troubleshooting | استكشاف الأخطاء

### Common Issues | المشكلات الشائعة

| Issue | Cause | Solution |
|-------|-------|----------|
| Service won't start | Missing env vars | Check `.env` file |
| Database connection failed | Wrong credentials | Verify DATABASE_URL |
| Port already in use | Another process | Kill conflicting process |
| Out of memory | Too many services | Increase RAM or reduce services |
| Slow responses | Database queries | Add indexes, optimize queries |

### Diagnostic Commands | أوامر التشخيص

```bash
# Check service logs
make logs-service SERVICE=field-management

# Check all logs
make logs

# Check service health
curl http://localhost:8000/healthz

# Check database connections
docker exec sahool-postgres psql -U sahool -c "SELECT count(*) FROM pg_stat_activity;"

# Check NATS status
curl http://localhost:8222/varz
```

### Debug Mode | وضع التصحيح

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Restart services
make restart
```

For detailed troubleshooting, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

---

## Post-Deployment Checklist | قائمة ما بعد النشر

### Required Checks | الفحوصات المطلوبة

- [ ] All services are healthy (`make health`)
- [ ] Database migrations completed
- [ ] SSL/TLS certificates configured
- [ ] DNS records pointing to correct IPs
- [ ] Monitoring alerts configured
- [ ] Backup jobs scheduled
- [ ] Rate limiting enabled
- [ ] Authentication working
- [ ] CORS configured correctly
- [ ] Logging to central system

### Security Checks | فحوصات الأمان

- [ ] No default passwords
- [ ] JWT secret is unique and strong
- [ ] Database not exposed publicly
- [ ] Redis password set
- [ ] Firewall rules configured
- [ ] Security headers enabled
- [ ] Audit logging enabled

### Performance Checks | فحوصات الأداء

- [ ] Database indexes created
- [ ] Connection pooling enabled
- [ ] Caching working
- [ ] CDN configured for static assets
- [ ] Compression enabled

---

## Next Steps | الخطوات التالية

- [Security Configuration](./SECURITY.md)
- [Operations Runbook](./RUNBOOKS.md)
- [Monitoring Guide](./OBSERVABILITY.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [Disaster Recovery](./disaster-recovery/README.md)

---

_Last Updated | آخر تحديث: February 2026_
