# دليل تكوين Kong API Gateway
# Kong API Gateway Configuration Guide

**التاريخ:** 2026-01-05
**الإصدار:** v16.0.0

---

## 📋 نظرة عامة | Overview

يحتوي مشروع سهول على ملفين لتكوين Kong API Gateway:

| الملف | الموقع | الغرض |
|-------|--------|-------|
| **الأساسي** | `/infra/kong/kong.yml` | التكوين الرئيسي (المصدر الموثوق) |
| **الثانوي** | `/infrastructure/gateway/kong/kong.yml` | نسخة للبنية التحتية |

---

## ⚠️ مشكلة التكرار | Duplication Issue

### الوضع الحالي

الملفان متشابهان لكن **ليسا متطابقين**:

```
الاختلافات الرئيسية:
├── منافذ الخدمات (مثل ndvi-engine: 8107 vs 8118)
├── خدمات إضافية في الملف الثانوي (auth-service)
├── إعدادات healthcheck مختلفة
└── استخدام host vs url في بعض الخدمات
```

### المخاطر

1. **عدم الاتساق** - تغيير أحدهما دون الآخر يسبب مشاكل
2. **صعوبة الصيانة** - مضاعفة جهد التحديث
3. **أخطاء النشر** - استخدام الملف الخاطئ في الإنتاج

---

## 🎯 التوصيات | Recommendations

### الخيار 1: Symlink (الأبسط)

```bash
# حذف الملف الثانوي وإنشاء symlink
cd infrastructure/gateway/kong/
rm kong.yml
ln -s ../../../infra/kong/kong.yml kong.yml
```

**المميزات:** بسيط، يضمن التطابق دائماً
**العيوب:** قد لا يعمل في بعض بيئات Docker/CI

### الخيار 2: Single Source of Truth (الأفضل)

1. اعتماد `/infra/kong/kong.yml` كمصدر وحيد
2. حذف `/infrastructure/gateway/kong/kong.yml`
3. تحديث Docker Compose ليستخدم المسار الصحيح

```yaml
# docker-compose.yml
services:
  kong:
    volumes:
      - ./infra/kong/kong.yml:/etc/kong/kong.yml:ro
```

### الخيار 3: Validation Script (مؤقت)

إضافة script للتحقق من تطابق الملفين في CI/CD:

```bash
#!/bin/bash
# scripts/validate-kong-config.sh

diff -q infra/kong/kong.yml infrastructure/gateway/kong/kong.yml
if [ $? -ne 0 ]; then
    echo "❌ Kong configuration files are out of sync!"
    exit 1
fi
echo "✅ Kong configurations are synchronized"
```

---

## 📊 مقارنة الملفين | File Comparison

### الخدمات في `/infra/kong/kong.yml` فقط:
- (جميع الخدمات موجودة)

### الخدمات في `/infrastructure/gateway/kong/kong.yml` فقط:
- `auth-service` (placeholder للمصادقة)

### اختلافات المنافذ:

| الخدمة | infra | infrastructure |
|--------|-------|----------------|
| ndvi-engine | 8118 (ndvi-processor) | 8107 |
| inventory-service | 8115 | 8116 |
| weather-advanced | 8108 | 8092 |
| yield-engine | 3021 | 8098 |

---

## ✅ خطوات التوحيد | Unification Steps

### 1. تحديد الملف الرئيسي
```bash
# الملف الرئيسي هو:
/infra/kong/kong.yml
```

### 2. مزامنة التغييرات المهمة
```bash
# نسخ الخدمات المفقودة من الملف الثانوي للرئيسي
# مثل: auth-service
```

### 3. تحديث المراجع
```yaml
# في docker-compose.yml, استخدم المسار الموحد
volumes:
  - ./infra/kong/kong.yml:/etc/kong/kong.yml
```

### 4. حذف أو ربط الملف الثانوي
```bash
# إما حذف
rm infrastructure/gateway/kong/kong.yml

# أو إنشاء symlink
ln -s ../../../infra/kong/kong.yml infrastructure/gateway/kong/kong.yml
```

### 5. تحديث CI/CD
```yaml
# .github/workflows/ci.yml
- name: Validate Kong Config
  run: |
    if [ -L infrastructure/gateway/kong/kong.yml ]; then
      echo "Kong config is symlinked ✅"
    else
      echo "Warning: Kong configs may be out of sync"
    fi
```

---

## 🧪 اختبارات التكامل | Integration Tests

تم إنشاء اختبارات للتحقق من صحة تكوين Kong:

```bash
# تشغيل اختبارات Kong
pytest tests/integration/test_kong_routes.py -v
```

### الاختبارات المتوفرة:
- ✅ التحقق من هيكل التكوين
- ✅ التحقق من الخدمات المطلوبة
- ✅ التحقق من مسارات التقويم الفلكي (backward compatibility)
- ✅ التحقق من إضافات الأمان
- ✅ التحقق من Rate Limiting
- ✅ التحقق من ACL
- ✅ التحقق من Field Intelligence Service
- ✅ التحقق من تناسق الملفين

---

## 📝 ملاحظات إضافية | Additional Notes

### أفضل الممارسات

1. **استخدام Environment Variables** للقيم الحساسة
   ```yaml
   redis_password: ${REDIS_PASSWORD}
   ```

2. **استخدام Upstreams** للخدمات ذات الـ Load Balancing
   ```yaml
   host: field-management-upstream
   ```

3. **تفعيل Health Checks** لجميع الخدمات
   ```yaml
   healthchecks:
     active:
       http_path: /healthz
   ```

4. **استخدام Tags** لتصنيف الخدمات
   ```yaml
   tags:
     - starter
     - professional
     - enterprise
   ```

---

## 🔗 المراجع | References

- [Kong Gateway Documentation](https://docs.konghq.com/)
- [Kong Declarative Configuration](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [SAHOOL API Documentation](/docs/reports/SAHOOL_SERVICES_API_DOCUMENTATION.md)

---

**تم إعداد هذا الدليل لتسهيل صيانة تكوين Kong API Gateway في منصة سهول.**
