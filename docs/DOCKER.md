# Docker Deployment Guide | دليل نشر Docker

# SAHOOL Platform v16.0

---

## نظرة عامة | Overview

هذا الدليل يوضح كيفية تشغيل منصة سهول باستخدام Docker Compose.

This guide explains how to run the SAHOOL platform using Docker Compose.

---

## المتطلبات | Prerequisites

```bash
# Docker Engine 24+
docker --version

# Docker Compose v2+
docker compose version
```

---

## البدء السريع | Quick Start

```bash
# 1. إنشاء ملف البيئة
cp .env.example .env

# 2. تعديل المتغيرات المطلوبة
nano .env

# 3. تشغيل الخدمات
docker compose up -d

# 4. التحقق من الحالة
docker compose ps
```

---

## متغيرات البيئة المطلوبة | Required Environment Variables

```env
# قاعدة البيانات (مطلوب)
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<your-secure-password>
POSTGRES_DB=sahool

# Redis (مطلوب)
REDIS_PASSWORD=<your-redis-password>

# JWT Authentication (مطلوب)
JWT_SECRET_KEY=<your-256-bit-secret>

# Stripe (اختياري - للفوترة)
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Weather API (اختياري)
OPENWEATHER_API_KEY=<your-api-key>

# Planet API (اختياري - للأقمار الصناعية)
PLANET_API_KEY=<your-api-key>
```

---

## خريطة الخدمات والمنافذ | Services Port Map

### البنية التحتية | Infrastructure

| الخدمة   | المنفذ     | الوصف            |
| -------- | ---------- | ---------------- |
| postgres | 5432       | PostGIS Database |
| redis    | 6379       | Cache & Sessions |
| nats     | 4222, 8222 | Message Queue    |
| mqtt     | 1883, 9001 | IoT Protocol     |
| kong     | 8000, 8001 | API Gateway      |

### الخدمات الأساسية | Core Services

| الخدمة                       | المنفذ | اللغة   | الوصف                      |
| ---------------------------- | ------ | ------- | -------------------------- |
| crop-intelligence-service    | 8095   | Python  | تشخيص صحة المحاصيل         |
| virtual_sensors              | 8119   | Python  | المستشعرات الافتراضية      |
| chat-service                 | 8115   | Node.js | الدردشة والتراسل الفوري    |
| billing_core                 | 8089   | Python  | الفوترة والاشتراكات        |
| vegetation-analysis-service  | 8090   | Python  | تحليل صور الأقمار الصناعية |
| indicators_service           | 8091   | Python  | المؤشرات الزراعية          |
| weather-service              | 8092   | Python  | التنبؤات الجوية            |
| advisory-service             | 8093   | Python  | الاستشارات الزراعية        |
| irrigation_smart             | 8094   | Python  | الري الذكي                 |
| notification_service         | 8110   | Python  | الإشعارات                  |
| astronomical_calendar        | 8111   | Python  | التقويم الفلكي             |

### خدمات NestJS

| الخدمة              | المنفذ | الوصف              |
| ------------------- | ------ | ------------------ |
| marketplace_service | 3010   | سوق المنتجات       |
| research_core       | 3015   | البحث العلمي       |
| disaster_assessment | 3020   | تقييم الكوارث      |
| yield_prediction    | 3021   | التنبؤ بالإنتاج    |
| lai_estimation      | 3022   | تقدير LAI          |
| crop_growth_model   | 3023   | نموذج نمو المحاصيل |

### المراقبة | Observability

| الخدمة     | المنفذ | الوصف              |
| ---------- | ------ | ------------------ |
| prometheus | 9090   | Metrics Collection |
| grafana    | 3002   | Dashboards         |

### الواجهات | Frontends

| الخدمة          | المنفذ | الوصف              |
| --------------- | ------ | ------------------ |
| admin_dashboard | 3001   | لوحة تحكم المشرفين |

---

## أوامر Docker Compose | Docker Compose Commands

```bash
# تشغيل جميع الخدمات
docker compose up -d

# تشغيل خدمات محددة فقط
docker compose up -d postgres redis nats billing_core

# عرض السجلات
docker compose logs -f billing_core

# إعادة تشغيل خدمة
docker compose restart billing_core

# إيقاف جميع الخدمات
docker compose down

# إيقاف مع حذف البيانات
docker compose down -v

# تحديث الصور
docker compose pull
docker compose up -d
```

---

## التحقق من الصحة | Health Checks

```bash
# فحص صحة جميع الخدمات
for port in 8089 8090 8091 8092 8093 8094 8095 8096 8098 8110 8111; do
    echo "Port $port: $(curl -s http://localhost:$port/healthz | jq -r '.status // "error"')"
done

# فحص خدمة محددة
curl http://localhost:8089/healthz | jq
```

---

## البناء المحلي | Local Build

```bash
# تفعيل BuildKit (مطلوب لتحسين أداء البناء)
export DOCKER_BUILDKIT=1  # Linux/macOS
$env:DOCKER_BUILDKIT=1    # PowerShell

# بناء جميع الصور
docker compose build

# بناء خدمة محددة
docker compose build billing_core

# بناء بدون cache
docker compose build --no-cache billing_core
```

### حل مشاكل الشبكة | Network Resilience

إذا فشل البناء بسبب أخطاء الشبكة (npm network aborted أو DNS failures):

```bash
# تأكد من تفعيل BuildKit
export DOCKER_BUILDKIT=1

# أعد المحاولة - الـ Dockerfile يحتوي على retry loop تلقائي
docker compose build --progress=plain chat-service
```

### أنماط البناء المعيارية | Standardized Build Patterns

#### apt-get Mirror Fallback (جميع الخدمات)

جميع الحاويات تستخدم سكريبت `docker/apt-update.sh` المشترك بدلاً من `apt-get update` مباشرة.
السكريبت يتعامل مع فشل DNS تلقائياً بالتبديل إلى مرايا Aliyun:

```dockerfile
# نسخ السكريبت المشترك
COPY docker/apt-update.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/apt-update.sh

# الاستخدام - بدلاً من apt-get update
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    curl tini && rm -rf /var/lib/apt/lists/*
```

يدعم: Debian DEB822 (bookworm+)، Ubuntu DEB822 (noble+)، وصيغة sources.list التقليدية.

#### npm Install مع Retry و Mirror Fallback (خدمات Node.js)

جميع خدمات Node.js تستخدم نمط retry loop موحد مع 5 محاولات و mirror fallback:

```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    for i in 1 2 3 4 5; do \
        if npm install --legacy-peer-deps \
            --prefer-offline \
            --fetch-timeout=300000 \
            --no-audit \
            --no-fund; then break; fi; \
        if [ "$i" != "5" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmmirror.com && \
     npm install --legacy-peer-deps)
```

**المميزات:**
- **BuildKit cache mount**: إعادة استخدام حزم npm المحملة (`/root/.npm`)
- **5 محاولات**: مع تأخير متزايد (10s, 20s, 30s, 40s)
- **Mirror fallback**: التبديل إلى npmmirror.com عند فشل جميع المحاولات
- **Increased timeouts**: 5 دقائق لكل طلب

#### pip Multi-Mirror Fallback (خدمات Python)

خدمات Python تستخدم نمط المرايا المتعددة:

```dockerfile
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -r requirements.txt
```

**ترتيب المرايا:** PyPI الرسمي → Alibaba Cloud → Tencent Cloud

#### خدمات CLI (بدون منفذ HTTP)

بعض الخدمات مثل `code-review-agent` هي أدوات CLI بدون خادم HTTP.
هذه الخدمات لا تحتاج port mapping أو health check:

```yaml
# في governance/services.yaml
code-review-agent:
  port: null               # لا يوجد منفذ HTTP
  health_endpoint: null    # لا يوجد فحص صحة
  service_type: cli        # نوع الخدمة
```

المولّدات (`generate_infra.py`, `compose-generator.py`) تتخطى هذه الخدمات تلقائياً عند توليد Docker Compose و Helm.

---

## Profiles (Legacy Services)

بعض الخدمات القديمة موضوعة في profile منفصل:

```bash
# تشغيل الخدمات القديمة
docker compose --profile legacy up -d

# قائمة الخدمات القديمة
# - field_core
# - field_ops
# - ndvi_engine
# - weather_core
# - field_chat
# - iot_gateway
# - agro_advisor
# - ws_gateway
# - crop_health
# - agro_rules
```

---

## استكشاف الأخطاء | Troubleshooting

### الخدمة لا تبدأ

```bash
# عرض السجلات
docker compose logs billing_core

# فحص حالة الحاوية
docker inspect sahool-billing-core

# إعادة البناء
docker compose build --no-cache billing_core
docker compose up -d billing_core
```

### مشاكل الاتصال بقاعدة البيانات

```bash
# التحقق من تشغيل PostgreSQL
docker compose ps postgres

# الاتصال بقاعدة البيانات
docker compose exec postgres psql -U sahool -d sahool

# فحص الشبكة
docker network inspect sahool-network
```

### مشاكل الذاكرة

```bash
# عرض استخدام الموارد
docker stats

# تحديد حدود الذاكرة في docker-compose.yml
services:
  billing_core:
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## الأمان | Security

### مستخدم غير Root

جميع الحاويات تعمل بمستخدم غير root (sahool, UID 1000) للأمان:

```dockerfile
# Python services
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool sahool
USER sahool

# Node.js Alpine services
RUN addgroup -g 1000 sahool && \
    adduser -u 1000 -G sahool -s /bin/sh -D sahool
USER sahool
```

### الشبكة

جميع الخدمات تتواصل عبر شبكة داخلية معزولة:

```yaml
networks:
  sahool-network:
    driver: bridge
    name: sahool-network
```

### الأسرار

لا تضع الأسرار في docker-compose.yml مباشرة. استخدم:

- ملف `.env` (للتطوير)
- Docker Secrets (للإنتاج)
- HashiCorp Vault (موصى به)

---

## النسخ الاحتياطي | Backup

```bash
# نسخ قاعدة البيانات
docker compose exec postgres pg_dump -U sahool sahool > backup.sql

# استعادة قاعدة البيانات
docker compose exec -T postgres psql -U sahool sahool < backup.sql

# نسخ volumes
docker run --rm -v sahool-postgres-data:/data -v $(pwd):/backup \
    alpine tar cvf /backup/postgres-backup.tar /data
```

---

## الإنتاج | Production

للإنتاج، استخدم:

- Kubernetes (Helm charts في `/helm`)
- إعداد متغيرات البيئة الآمنة
- تفعيل TLS/SSL
- إعداد monitoring كامل
- استخدام CDN للأصول الثابتة

```bash
# نشر Kubernetes
helm install sahool ./helm/sahool \
    --namespace sahool \
    --create-namespace \
    -f values.production.yaml
```

---

<p align="center">
  <strong>SAHOOL Platform v16.0</strong>
  <br>
  <sub>آخر تحديث: مارس 2026</sub>
</p>
