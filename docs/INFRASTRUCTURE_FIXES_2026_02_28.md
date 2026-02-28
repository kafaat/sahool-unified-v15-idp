# إصلاحات البنية التحتية | Infrastructure Fixes

> **التاريخ**: 2026-02-28
> **الإصدار**: v16.0.0
> **الفرع**: `claude/add-claude-documentation-48GdK`

---

## ملخص التغييرات | Changes Summary

### 1. إصلاح منافذ Kong Gateway (حرج)

**المشكلة**: خدمتان في Kong تشيران لمنافذ خاطئة → الطلبات تفشل

| الخدمة | المنفذ القديم | المنفذ الصحيح | السبب |
|--------|-------------|-------------|-------|
| `chat-service` | 8000 | **8115** | الحاوية تعمل على PORT=8115 |
| `mcp-server` | 8200 | **8201** | الحاوية تعمل على MCP_SERVER_PORT=8201 |

> **ملاحظة**: `copilot-api` (Kong port 8088) صحيح - Kong يستخدم المنفذ الداخلي للحاوية (8088)، والمنفذ 8163 هو للوصول من المضيف فقط.

**الملف**: `infrastructure/gateway/kong/kong.yml`

---

### 2. إزالة 11 خدمة وهمية من Kong (حرج)

**المشكلة**: 11 خدمة معرّفة في Kong بدون backend → تُرجع 502 Bad Gateway

| الخدمة المُزالة | البديل النشط | المنفذ |
|----------------|-------------|-------|
| `community-chat` | `chat-service` | 8115 |
| `field-ops` | `field-management-service` | 3000 |
| `field-chat` | `chat-service` | 8115 |
| `field-service` | `field-management-service` | 3000 |
| `field-core` | `field-management-service` | 3000 |
| `crop-health` | `crop-intelligence-service` | 8095 |
| `yield-engine` | `yield-prediction-service` | 8152 |
| `satellite-service` | `vegetation-analysis-service` | 8090 |
| `weather-advanced` | `weather-service` | 8092 |
| `crop-health-ai` | `crop-intelligence-service` | 8095 |
| `fertilizer-advisor` | `advisory-service` | 8093 |

**النتيجة**: تقليل خدمات Kong من 79 → 68 خدمة نشطة
**الملف**: `infrastructure/gateway/kong/kong.yml`

---

### 3. إصلاح قيد NumPy لتوافق TensorFlow (عالي)

**المشكلة**: القيد `numpy>=1.26.0,<3.0.0` يسمح بتثبيت NumPy 2.5+ الذي يكسر TensorFlow 2.20

**الإصلاح**:
```diff
- "numpy>=1.26.0,<3.0.0",  # CRITICAL: Must be <2.5.0 for TensorFlow 2.20 compatibility
+ "numpy>=1.26.0,<2.5.0",  # Pinned <2.5.0 for TensorFlow 2.20 compatibility
```

**الملف**: `pyproject.toml`

---

### 4. تحديث سجل الحوكمة

- تحديث إصدار `governance/services.yaml` من 3.2.0 → 3.3.0
- تحديث تاريخ آخر تعديل إلى 2026-02-28

---

## التأثير | Impact

| المقياس | قبل | بعد |
|---------|-----|-----|
| أخطاء Kong 502 | ~11 | 0 |
| خدمات Kong نشطة | 79 (11 وهمية) | 68 (جميعها حقيقية) |
| توافق NumPy/TF | مكسور محتملاً | مضمون |
| منافذ Kong خاطئة | 2 | 0 |

---

## الملفات المعدلة | Modified Files

1. `infrastructure/gateway/kong/kong.yml` - إصلاح منافذ + إزالة خدمات وهمية
2. `pyproject.toml` - تقييد NumPy
3. `governance/services.yaml` - تحديث الإصدار

---

_آخر تحديث: 2026-02-28_
