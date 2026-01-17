# Docker Deployment Guide | دليل نشر Docker

# SAHOOL Platform v15.5

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

| الخدمة                | المنفذ | اللغة   | الوصف                 |
| --------------------- | ------ | ------- | --------------------- |
| crop_health_ai        | 8095   | Python  | تشخيص صحة المحاصيل    |
| virtual_sensors       | 8096   | Python  | المستشعرات الافتراضية |
| community_chat        | 8097   | Node.js | الدردشة المجتمعية     |
| yield_engine          | 8098   | Python  | توقع الإنتاجية        |
| billing_core          | 8089   | Python  | الفوترة والاشتراكات   |
| satellite_service     | 8090   | Python  | صور الأقمار الصناعية  |
| indicators_service    | 8091   | Python  | المؤشرات الزراعية     |
| weather_advanced      | 8092   | Python  | التنبؤات الجوية       |
| fertilizer_advisor    | 8093   | Python  | مستشار التسميد        |
| irrigation_smart      | 8094   | Python  | الري الذكي            |
| notification_service  | 8110   | Python  | الإشعارات             |
| astronomical_calendar | 8111   | Python  | التقويم الفلكي        |

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
# بناء جميع الصور
docker compose build

# بناء خدمة محددة
docker compose build billing_core

# بناء بدون cache
docker compose build --no-cache billing_core
```

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
  <strong>SAHOOL Platform v15.5</strong>
  <br>
  <sub>آخر تحديث: ديسمبر 2025</sub>
</p>
