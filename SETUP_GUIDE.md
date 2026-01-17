# دليل الإعداد والتشغيل - Setup and Deployment Guide

## SAHOOL Platform v15.3 - Complete Setup Instructions

**التاريخ / Date:** 2026-01-05  
**الإصدار / Version:** 15.3.0

---

## 🚀 البدء السريع - Quick Start

### 1. المتطلبات الأساسية - Prerequisites

```bash
# التحقق من تثبيت الأدوات المطلوبة
docker --version          # يجب أن يكون >= 20.10
docker compose version    # يجب أن يكون >= 2.0
make --version           # يجب أن يكون >= 4.0
python3 --version        # يجب أن يكون >= 3.9
node --version           # يجب أن يكون >= 18.0
```

### 2. إعداد ملف البيئة - Environment Setup

**الخطوة 1: نسخ ملف القالب**

```bash
cp .env.example .env
```

**الخطوة 2: توليد كلمات المرور الآمنة**

```bash
# توليد كلمة مرور PostgreSQL
python3 -c "import secrets, base64; print('POSTGRES_PASSWORD=' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# توليد كلمة مرور Redis
python3 -c "import secrets, base64; print('REDIS_PASSWORD=' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# توليد مفتاح JWT السري
python3 -c "import secrets, base64; print('JWT_SECRET_KEY=' + base64.urlsafe_b64encode(secrets.token_bytes(48)).decode())"

# توليد كلمة مرور MQTT
python3 -c "import secrets, base64; print('MQTT_PASSWORD=' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

**الخطوة 3: تحديث ملف .env**
افتح ملف `.env` وقم بتحديث القيم التالية:

```bash
# المتغيرات الحرجة المطلوبة
POSTGRES_PASSWORD=<القيمة المُولدة>
REDIS_PASSWORD=<القيمة المُولدة>
JWT_SECRET_KEY=<القيمة المُولدة>
MQTT_PASSWORD=<القيمة المُولدة>

# تحديث عناوين URL لتعكس كلمات المرور الجديدة
DATABASE_URL=postgresql://sahool:<POSTGRES_PASSWORD>@postgres:5432/sahool
REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/0
```

### 3. التحقق من الإعداد - Validation

```bash
# التحقق من صحة تكوين Docker Compose
docker compose config --quiet && echo "✅ Docker Compose configuration is valid"

# التحقق من صحة ملف البيئة
make env-check
```

---

## 🏗️ البناء والتشغيل - Build and Run

### بناء جميع الخدمات - Build All Services

```bash
# بناء جميع صور Docker
make build

# أو بناء خدمة محددة
docker compose build <service-name>
```

### تشغيل البيئة - Start Environment

#### بيئة التطوير الكاملة - Full Development

```bash
make dev
# أو
docker compose up -d
```

#### حزمة المبتدئين - Starter Package

```bash
make dev-starter
```

#### حزمة الاحترافية - Professional Package

```bash
make dev-professional
```

#### حزمة المؤسسات - Enterprise Package

```bash
make dev-enterprise
```

---

## 🧪 الاختبارات - Testing

### تشغيل جميع الاختبارات - Run All Tests

```bash
make test
```

### اختبارات Python فقط

```bash
make test-python
```

### اختبارات Node.js فقط

```bash
make test-node
```

### اختبارات التكامل - Integration Tests

```bash
make test-integration
```

---

## 🔍 المراقبة والفحص - Monitoring and Health Checks

### فحص صحة الخدمات - Health Check

```bash
make health
```

### عرض السجلات - View Logs

```bash
# جميع الخدمات
make logs

# خدمة محددة
make logs-service SERVICE=field-management-service

# متابعة السجلات الحية
make watch
```

### التحقق من حالة الخدمات - Service Status

```bash
make status
```

---

## 🔧 الصيانة - Maintenance

### تحديث قاعدة البيانات - Database Updates

```bash
# تشغيل الترحيلات
make db-migrate

# ملء البيانات التجريبية
make db-seed

# نسخ احتياطي
make db-backup
```

### التنظيف - Cleanup

```bash
# إيقاف جميع الخدمات
make down

# تنظيف الحاويات والأحجام
make clean

# إعادة بناء كاملة
make rebuild
```

---

## 📊 المنافذ المستخدمة - Ports Reference

### الخدمات الأساسية - Core Services

- **PostgreSQL**: 5432
- **Redis**: 6379
- **NATS**: 4222
- **Kong Gateway**: 8000, 8001, 8443, 8444
- **PgBouncer**: 6432

### خدمات التطبيق - Application Services

- **Field Management**: 3000
- **Weather Service**: 8092
- **Astronomical Calendar**: 8111
- **Advisory Service**: 8093
- **IoT Service**: 8117
- **Virtual Sensors**: 8119 ⚠️ (تم تحديثه من 8096)
- **Code Review**: 8096
- **AI Advisor**: 8112
- **Crop Intelligence**: 8095

_(راجع `docker-compose.yml` للقائمة الكاملة)_

---

## 🔐 الأمان - Security

### أفضل الممارسات - Best Practices

1. **لا تشارك ملف .env أبداً**
   - ملف `.env` يحتوي على أسرار حساسة
   - تأكد من وجوده في `.gitignore`

2. **استخدم كلمات مرور قوية**
   - استخدم المولد المذكور أعلاه
   - 32 بايت على الأقل لكل سر

3. **قم بتحديث الأسرار بانتظام**
   - في الإنتاج، قم بتدوير الأسرار كل 90 يوماً

4. **استخدم HTTPS في الإنتاج**
   - قم بتكوين شهادات SSL/TLS
   - فعّل CORS بشكل صحيح

---

## 🐛 استكشاف الأخطاء - Troubleshooting

### المشاكل الشائعة - Common Issues

#### 1. فشل بناء Docker

```bash
# التحقق من المساحة المتاحة
df -h

# تنظيف صور Docker غير المستخدمة
docker system prune -a

# إعادة البناء بدون cache
docker compose build --no-cache
```

#### 2. مشاكل الاتصال بقاعدة البيانات

```bash
# التحقق من تشغيل PostgreSQL
docker compose ps postgres

# التحقق من السجلات
docker compose logs postgres

# إعادة تشغيل قاعدة البيانات
docker compose restart postgres
```

#### 3. تعارضات المنافذ

```bash
# التحقق من المنافذ المستخدمة
netstat -tulpn | grep LISTEN

# إيقاف الخدمات المتعارضة
sudo systemctl stop <service-name>
```

#### 4. مشاكل الذاكرة

```bash
# التحقق من استخدام الذاكرة
docker stats

# زيادة حد الذاكرة في docker-compose.yml
# في قسم deploy.resources.limits
```

---

## 📚 الموارد الإضافية - Additional Resources

### الوثائق

- `README.md` - نظرة عامة على المشروع
- `BUILD_GUIDE.md` - دليل البناء التفصيلي
- `PROJECT_REVIEW_REPORT.md` - تقرير المراجعة الشاملة
- `MERGE_CONFLICT_RESOLUTION.md` - حل التعارضات

### الأوامر المفيدة

```bash
# قائمة جميع الأوامر المتاحة
make help

# فحص البيئة
make env-check

# فحص الأمان
make security-check

# فحص الأداء
make performance-check
```

---

## ✅ قائمة التحقق للإعداد - Setup Checklist

- [ ] تثبيت المتطلبات الأساسية (Docker, Docker Compose, Make)
- [ ] نسخ `.env.example` إلى `.env`
- [ ] توليد كلمات مرور آمنة لجميع الخدمات
- [ ] تحديث ملف `.env` بالقيم المُولدة
- [ ] التحقق من صحة تكوين Docker Compose
- [ ] بناء جميع صور Docker
- [ ] تشغيل الخدمات الأساسية
- [ ] تشغيل ترحيلات قاعدة البيانات
- [ ] فحص صحة جميع الخدمات
- [ ] تشغيل الاختبارات
- [ ] التحقق من السجلات

---

## 🎯 الخطوات التالية - Next Steps

بعد إكمال الإعداد الأساسي:

1. **تكوين المراقبة**

   ```bash
   docker compose -f docker-compose.telemetry.yml up -d
   ```

2. **إعداد النسخ الاحتياطي التلقائي**

   ```bash
   # إضافة cron job للنسخ الاحتياطي اليومي
   0 2 * * * cd /path/to/project && make db-backup
   ```

3. **تكوين CI/CD**
   - راجع `.github/workflows/` للتكوينات

4. **مراجعة الأمان**
   ```bash
   make security-scan
   ```

---

**للدعم:** راجع الوثائق الكاملة في مجلد `docs/`  
**الترخيص:** راجع ملف `LICENSE`  
**المساهمة:** راجع `CONTRIBUTING.md`
