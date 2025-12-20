# تحليل المرحلة الأولى - فحص الاعتماديات والتعارضات
# Phase 1 Analysis - Dependency Scan & Conflicts Report

**التاريخ:** 20 ديسمبر 2025
**المنصة:** SAHOOL Unified v15-IDP

---

## 1. ملخص الفحص | Scan Summary

### الملفات المفحوصة | Files Scanned

| التقنية | عدد الملفات | الموقع |
|---------|-------------|--------|
| Node.js (package.json) | 13 ملف نشط | packages/*, apps/web, apps/admin, apps/services/* |
| Python (requirements.txt) | 12 ملف نشط | apps/services/* |
| Flutter (pubspec.yaml) | 1 ملف | apps/mobile/sahool_field_app |
| Docker | 2 base images | docker/Dockerfile.*.base |

---

## 2. التعارضات المكتشفة | Conflicts Found

### 🔴 تعارضات حرجة | Critical Conflicts

#### 2.1 تعارض numpy في Python
```
crop-health-ai: numpy>=1.26.0,<2.1.0  (مطلوب من tensorflow-cpu 2.18.0)
yield-engine:   numpy==2.1.3         (غير متوافق)
```
**السبب:** TensorFlow 2.18.0 لا يدعم numpy 2.x
**الحل:** توحيد إصدار numpy إلى 1.26.x لجميع الخدمات أو تحديث TensorFlow

#### 2.2 تعارض @nestjs/swagger في Node.js
```
iot-service:         @nestjs/swagger ^8.1.0
marketplace-service: @nestjs/swagger ^7.4.0
```
**الحل:** توحيد الإصدار إلى ^8.1.0 (الأحدث)

---

### 🟡 عدم تناسق الإصدارات | Version Inconsistencies

#### 2.3 React Versions
| الحزمة | الإصدار |
|--------|---------|
| apps/web, apps/admin | 19.0.0 |
| shared-hooks (dev) | ^19.2.3 |
| design-system (dev) | ^19.0.0 |
| **Latest Available** | **19.2.3** |

#### 2.4 TypeScript Versions
| الحزمة | الإصدار |
|--------|---------|
| root, apps/web, apps/admin | 5.7.2 |
| packages/* (wanted) | 5.9.3 |
| **Latest Available** | **5.9.3** |

#### 2.5 @types/node Versions
| الموقع | الإصدار الحالي | الأحدث |
|--------|---------------|--------|
| root, apps/* | 22.10.2 | 25.0.3 |

---

## 3. الترقيات المتاحة | Available Upgrades

### 🟢 Node.js - ترقيات آمنة (Minor/Patch)

| الحزمة | الحالي | الأحدث | المستوى |
|--------|--------|--------|---------|
| @tanstack/react-query | 5.62.8 | 5.90.12 | Minor ✅ |
| axios | 1.7.9 | 1.13.2 | Minor ✅ |
| @types/react | 19.0.2 | 19.2.7 | Patch ✅ |
| @types/react-dom | 19.0.2 | 19.2.3 | Patch ✅ |
| @types/leaflet | 1.9.15 | 1.9.21 | Patch ✅ |
| @testing-library/react | 16.1.0 | 16.3.1 | Minor ✅ |
| @testing-library/jest-dom | 6.6.3 | 6.9.1 | Minor ✅ |
| autoprefixer | 10.4.20 | 10.4.23 | Patch ✅ |
| postcss | 8.4.49 | 8.5.6 | Minor ✅ |
| eslint | 9.17.0 | 9.39.2 | Minor ✅ |
| typescript | 5.7.2 | 5.9.3 | Minor ✅ |

### 🟡 Node.js - ترقيات Major (تحتاج اختبار)

| الحزمة | الحالي | الأحدث | ملاحظات |
|--------|--------|--------|---------|
| next | 15.1.2 | 16.1.0 | Major upgrade - API changes |
| react | 19.0.0 | 19.2.3 | Minor but needs testing |
| tailwindcss | 3.4.17 | 4.1.18 | **Major** - Complete rewrite |
| tailwind-merge | 2.6.0 | 3.4.0 | Major - API changes |
| vitest | 2.1.8 | 4.0.16 | Major - Breaking changes |
| @vitejs/plugin-react | 4.3.4 | 5.1.2 | Major |
| jose | 5.9.6 | 6.1.3 | Major - JWT handling |
| jsdom | 25.0.1 | 27.3.0 | Major |
| recharts | 2.14.1 | 3.6.0 | Major - Chart API changes |
| react-leaflet | 4.2.1 | 5.0.0 | Major - Map integration |
| next-intl | 3.26.3 | 4.6.1 | Major - i18n changes |
| lucide-react | 0.468.0 | 0.562.0 | Minor but large change |

### 🟢 Python - الإصدار الحالي هو الأحدث

| الحزمة | الإصدار | الحالة |
|--------|---------|--------|
| fastapi | 0.126.0 | ✅ Latest |
| uvicorn | 0.34.0 | ✅ Latest |
| pydantic | 2.10.3 | ✅ Latest |
| httpx | 0.28.1 | ✅ Latest |
| redis | 5.2.1 | ✅ Latest |

---

## 4. القيود والحدود | Constraints & Blockers

### 4.1 Flutter/Dart Constraints
```
Flutter Version: 3.27.1 (stable)
Dart SDK: 3.6.0
```
**محدودية الترقية:**
- mockito: محدود بـ ^5.4.4 (≥5.4.6 يتطلب Dart 3.7.0)
- json_serializable: محدود بـ ^6.8.0 (≥6.10.0 يتطلب Dart 3.8.0)
- freezed: ^2.5.7 متوافق مع Dart 3.6.0

### 4.2 TensorFlow Constraint
```
tensorflow-cpu: 2.18.0 → يتطلب numpy<2.1.0
```
**التأثير:** جميع خدمات Python التي تستخدم numpy يجب أن تستخدم <2.1.0

### 4.3 Node.js Runtime
```
Required: >=20.0.0
Docker Base: node:20-slim
```

### 4.4 Python Runtime
```
Required: 3.11
Docker Base: python:3.11-slim
```

---

## 5. خريطة الاعتماديات المشتركة | Shared Dependency Map

```
┌─────────────────────────────────────────────────────────────┐
│                     ROOT (sahool-unified)                    │
│  typescript: 5.7.2, @types/node: 22.10.2                    │
└─────────────────────────────────────────────────────────────┘
         │
         ├── packages/shared-utils ─────┐
         │   └── clsx, tailwind-merge   │
         │                              │
         ├── packages/shared-ui ────────┼── → apps/web
         │   └── lucide-react           │   → apps/admin
         │                              │
         ├── packages/api-client ───────┤
         │   └── axios                  │
         │                              │
         └── packages/shared-hooks ─────┘
             └── @tanstack/react-query (dev)
```

---

## 6. قائمة الترقيات ذات الأولوية | Prioritized Upgrade List

### المرحلة B: ترقيات منخفضة المخاطر
1. ✅ typescript 5.7.2 → 5.9.3
2. ✅ @types/node 22.10.2 → 22.19.3 (not 25.x)
3. ✅ @types/react 19.0.2 → 19.2.7
4. ✅ @types/react-dom 19.0.2 → 19.2.3
5. ✅ axios 1.7.9 → 1.13.2
6. ✅ @tanstack/react-query 5.62.8 → 5.90.12
7. ✅ autoprefixer 10.4.20 → 10.4.23
8. ✅ postcss 8.4.49 → 8.5.6

### المرحلة C: ترقيات متوسطة المخاطر
1. ⚠️ react 19.0.0 → 19.2.3
2. ⚠️ react-dom 19.0.0 → 19.2.3
3. ⚠️ lucide-react 0.468.0 → 0.562.0
4. ⚠️ eslint 9.17.0 → 9.39.2 (may need config updates)

### المرحلة D: ترقيات عالية المخاطر (تحتاج تخطيط)
1. 🔴 tailwindcss 3.4.17 → 4.x (Complete rewrite - defer)
2. 🔴 next 15.1.2 → 16.x (Major changes - defer)
3. 🔴 vitest 2.1.8 → 4.x (Breaking changes)
4. 🔴 recharts 2.14.1 → 3.x (API changes)

### إصلاحات التعارضات (أولوية قصوى)
1. 🔴 توحيد numpy إلى <2.1.0 في yield-engine
2. 🔴 توحيد @nestjs/swagger إلى ^8.1.0

---

## 7. التوصيات | Recommendations

### للتنفيذ الفوري:
1. **إصلاح تعارض numpy:** تغيير yield-engine من numpy==2.1.3 إلى numpy==1.26.4
2. **توحيد @nestjs/swagger:** رفع marketplace-service إلى ^8.1.0
3. **تنفيذ ترقيات المرحلة B:** جميعها آمنة ولا تحتاج تعديل كود

### للتنفيذ المؤجل:
1. **Tailwind CSS 4.x:** انتظار استقرار الإصدار والتوثيق الكامل
2. **Next.js 16.x:** تحتاج مراجعة Breaking Changes
3. **Vitest 4.x:** تحتاج تحديث ملفات الاختبار

---

## 8. الخطوات التالية | Next Steps

- [ ] المرحلة B: تنفيذ الترقيات منخفضة المخاطر
- [ ] المرحلة C: اختبار وتنفيذ الترقيات المتوسطة
- [ ] المرحلة D: تخطيط وتنفيذ الترقيات الكبرى
- [ ] المرحلة E: التحقق والاختبار النهائي

---

*تم إنشاء هذا التقرير بواسطة Claude في 20 ديسمبر 2025*
