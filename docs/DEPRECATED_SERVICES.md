# SAHOOL Deprecated Services Registry

# سجل الخدمات المتوقفة والمدمجة

> **تاريخ التحديث**: 2026-02-10
> **الحالة**: محدّث - تم حل جميع تعارضات المنافذ

---

## 📋 ملخص تنفيذي

هذه الوثيقة توضح الخدمات المتوقفة (Deprecated) التي تم استبدالها بخدمات موحدة جديدة.

This document lists deprecated services that have been replaced by consolidated new services.

---

## 🔴 الخدمات المتوقفة | Deprecated Services

### الخدمات المدمجة (تم نقل وظائفها بالكامل) | Fully Consolidated Services

| الخدمة المتوقفة | Deprecated Service | البديل | Replacement | المنفذ الجديد | New Port | تاريخ الإيقاف | Date |
|-----------------|-------------------|--------|-------------|---------------|----------|---------------|------|
| `field-ops` | field-ops | `field-management-service` | field-management-service | 3000 | 3000 | قديم | Legacy |
| `field-core` | field-core | `field-management-service` | field-management-service | 3000 | 3000 | قديم | Legacy |
| `field-service` | field-service | `field-management-service` | field-management-service | 3000 | 3000 | قديم | Legacy |
| `satellite-service` | satellite-service | `vegetation-analysis-service` | vegetation-analysis-service | 8090 | 8090 | 2026-01-11 |
| `weather-advanced` | weather-advanced | `weather-service` | weather-service | 8092 | 8092 | 2026-01-11 |
| `crop-health-ai` | crop-health-ai | `crop-intelligence-service` | crop-intelligence-service | 8095 | 8095 | 2026-01-11 |
| `fertilizer-advisor` | fertilizer-advisor | `advisory-service` | advisory-service | 8093 | 8093 | 2026-01-11 |

### خدمات قيد الإزالة | Services Pending Removal

| الخدمة | Service | المنفذ | Port | البديل | Replacement | الملاحظات | Notes |
|--------|---------|--------|------|--------|-------------|----------|-------|
| `ndvi-engine` | ndvi-engine | 8107 | 8107 | `vegetation-analysis-service` (8090) | vegetation-analysis-service | قيد الإزالة | Pending removal |
| `weather-core` | weather-core | 8108 | 8108 | `weather-service` (8092) | weather-service | قيد الإزالة | Pending removal |

---

## ✅ تعارضات المنافذ المحلولة | Resolved Port Conflicts

تم حل جميع تعارضات المنافذ التالية في فبراير 2026:

All the following port conflicts were resolved in February 2026:

| الخدمة | Service | المنفذ القديم | Old Port | المنفذ الجديد | New Port | سبب التغيير | Reason |
|--------|---------|---------------|----------|---------------|----------|-------------|--------|
| `agent-registry` | agent-registry | 8121 | 8121 | **8160** | **8160** | تعارض مع skills-service | Conflict with skills-service |
| `ai-agents-core` | ai-agents-core | 8120 | 8120 | **8161** | **8161** | تعارض مع field-intelligence | Conflict with field-intelligence |
| `globalgap-compliance` | globalgap-compliance | 8120/8123 | 8120/8123 | **8128** | **8128** | تعارض مع field-intelligence/traceability | Conflict with field-intelligence/traceability |
| `ussd-gateway` | ussd-gateway | 8180 | 8180 | **8183** | **8183** | تعارض مع edge-orchestrator | Conflict with edge-orchestrator |
| `logistics-service` | logistics-service | 8181 | 8181 | **8167** | **8167** | محاذاة مع Dockerfile | Aligned with Dockerfile |
| `user-service` | user-service | 3020 | 3020 | **3025** | **3025** | تعارض مع disaster-assessment | Conflict with disaster-assessment |

---

## ⚠️ تحذيرات مهمة | Important Warnings

1. **لا تشغل الخدمات المتوقفة مع البدائل في نفس الوقت** | Do not run deprecated services alongside their replacements
2. **جميع الخدمات المتوقفة تُظهر تحذير DEPRECATION في السجلات** | All deprecated services show DEPRECATION WARNING in logs
3. **المرجع الأساسي للمنافذ**: `governance/services.yaml` و `docker-compose.yml` | Port source of truth: `governance/services.yaml` and `docker-compose.yml`

---

## 📝 سجل التغييرات | Changelog

| التاريخ | Date | التغيير | Change |
|---------|------|---------|--------|
| 2026-02-10 | 2026-02-10 | تحديث شامل: حل جميع تعارضات المنافذ، تحديث المنافذ الجديدة | Comprehensive update: resolved all port conflicts, updated new ports |
| 2026-01-03 | 2026-01-03 | إنشاء الوثيقة | Document creation |
