# خدمات مجمدة / متوقفة - SAHOOL Platform
# Frozen / Deprecated Services

## ملخص - Summary

هذا الملف يوثق الخدمات التي تم تجميدها أو إيقافها أو استبدالها في منصة SAHOOL.
This document lists services that are frozen, deprecated, or replaced in the SAHOOL platform.

**تاريخ التحديث:** 2025-01-04
**Last Updated:** 2025-01-04

---

## 1. خدمات مهجورة (Deprecated Services)

هذه الخدمات لا تزال تعمل لكنها ستُزال في المستقبل.

| الخدمة القديمة | البديل | المنفذ | تاريخ الإيقاف |
|---------------|--------|--------|---------------|
| `weather-advanced` | `weather-service` | 8092 → 8108 | 2025-06-01 |
| `crop-health-ai` | `crop-intelligence-service` | 8095 | 2025-06-01 |
| `satellite-service` | `vegetation-analysis-service` | 8090 | 2025-06-01 |

---

## 2. خدمات مجمدة (Frozen Services)

هذه الخدمات موجودة في الكود لكنها غير مفعّلة في docker-compose.yml:

| الخدمة | السبب | الحالة |
|--------|-------|--------|
| `fertilizer-advisor` | تم دمجها في `advisory-service` | مجمدة |
| `agent-registry` | قيد التطوير | مجمدة |
| `ai-agents-core` | قيد التطوير | مجمدة |
| `field-core` | تم استبدالها بـ `field-management-service` | مجمدة |
| `globalgap-compliance` | قيد التطوير | مجمدة |
| `user-service` | تم دمجها في `billing-core` | مجمدة |
| `yield-engine` | تم دمجها في `yield-prediction-service` | مجمدة |

---

## 3. خدمات مشتركة (Shared)

| المجلد | الوصف |
|--------|-------|
| `shared/` | مكتبات مشتركة بين الخدمات - ليست خدمة مستقلة |

---

## 4. ملفات أرشيفية

| الملف | الوصف |
|-------|-------|
| `docker-compose.yml.deprecated` | ملف compose قديم للمرجع |
| `DEPRECATION_SUMMARY.md` | توثيق الخدمات المهجورة |
| `IN_MEMORY_STORAGE_MIGRATION.md` | توثيق ترحيل التخزين |

---

## 5. كيفية تفعيل خدمة مجمدة

إذا احتجت لتفعيل خدمة مجمدة:

```bash
# 1. تحقق من وجود Dockerfile
ls apps/services/<service-name>/Dockerfile

# 2. أضف الخدمة إلى docker-compose.yml
# 3. تحقق من المتطلبات في requirements.txt أو package.json
# 4. شغّل الخدمة
docker-compose up -d <service-name>
```

---

## 6. جدول الخدمات النشطة

**إجمالي الخدمات النشطة:** 53
**إجمالي الخدمات المجمدة:** 7
**إجمالي الخدمات المهجورة:** 3

---

## المراجع

- `/apps/services/DEPRECATION_SUMMARY.md` - تفاصيل الإهمال
- `/docker-compose.yml` - الخدمات النشطة
- `/archive/` - الكود المؤرشف

---

**ملاحظة:** لا تُزيل الخدمات المجمدة من الكود حتى يتم التأكد من عدم الحاجة إليها.
