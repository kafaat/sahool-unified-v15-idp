# دليل الحزم الموحدة - SAHOOL Platform

## نظرة عامة

هذا الدليل يوثق جميع الحزم والمكتبات المستخدمة في منصة SAHOOL عبر جميع التطبيقات (Web, Admin, Mobile) والخدمات الخلفية.

---

## 1. تطبيقات الواجهة الأمامية (Frontend)

### 1.1 الحزم المشتركة بين Web و Admin

| الحزمة                  | الإصدار | الوظيفة                        |
| ----------------------- | ------- | ------------------------------ |
| `next`                  | 15.5.9  | إطار عمل React للواجهات        |
| `react`                 | 19.0.0  | مكتبة UI الأساسية              |
| `react-dom`             | 19.0.0  | DOM rendering                  |
| `typescript`            | 5.9.3   | لغة البرمجة                    |
| `tailwindcss`           | 3.4.17  | CSS framework                  |
| `axios`                 | 1.13.2  | HTTP client                    |
| `@tanstack/react-query` | 5.90.12 | إدارة البيانات والتخزين المؤقت |
| `leaflet`               | 1.9.4   | مكتبة الخرائط                  |
| `react-leaflet`         | 5.0.0   | React wrapper للخرائط          |
| `recharts`              | 3.6.0   | مكتبة الرسوم البيانية          |
| `date-fns`              | 4.1.0   | معالجة التواريخ                |
| `lucide-react`          | 0.562.0 | أيقونات                        |
| `jose`                  | 5.9.6   | JWT والتشفير                   |
| `clsx`                  | 2.1.1   | Class names utility            |
| `tailwind-merge`        | 2.6.0   | Tailwind class merging         |

### 1.2 حزم التطوير (DevDependencies)

| الحزمة                      | الإصدار | الوظيفة           |
| --------------------------- | ------- | ----------------- |
| `vitest`                    | 3.1.3   | إطار الاختبارات   |
| `@vitejs/plugin-react`      | 5.1.2   | Vite React plugin |
| `@vitest/coverage-v8`       | 3.1.3   | تغطية الكود       |
| `@testing-library/react`    | 16.3.1  | اختبار React      |
| `@testing-library/jest-dom` | 6.9.1   | DOM matchers      |
| `eslint`                    | 9.39.2  | فحص الكود         |
| `eslint-config-next`        | 15.5.9  | ESLint config     |
| `postcss`                   | 8.5.6   | CSS processing    |
| `autoprefixer`              | 10.4.23 | CSS prefixing     |

### 1.3 الحزم الداخلية المشتركة

```
packages/
├── @sahool/api-client      # عميل API الموحد
├── @sahool/shared-ui       # مكونات UI مشتركة
├── @sahool/shared-utils    # دوال مساعدة
├── @sahool/shared-hooks    # React Hooks مشتركة
├── @sahool/design-system   # نظام التصميم
├── @sahool/tailwind-config # إعدادات Tailwind
└── @sahool/typescript-config # إعدادات TypeScript
```

---

## 2. تطبيق الموبايل (Flutter)

### 2.1 البيئة

```yaml
environment:
  sdk: ">=3.2.0 <4.0.0"
```

### 2.2 إدارة الحالة (State Management)

| الحزمة                | الإصدار | الوظيفة         |
| --------------------- | ------- | --------------- |
| `flutter_riverpod`    | ^2.6.1  | إدارة الحالة    |
| `riverpod_annotation` | ^2.6.1  | Annotations     |
| `riverpod_generator`  | ^2.6.3  | Code generation |

### 2.3 قاعدة البيانات والتخزين

| الحزمة                   | الإصدار | الوظيفة             |
| ------------------------ | ------- | ------------------- |
| `drift`                  | ^2.22.1 | قاعدة بيانات SQLite |
| `sqlite3_flutter_libs`   | ^0.5.28 | SQLite libraries    |
| `shared_preferences`     | ^2.3.3  | التخزين المحلي      |
| `flutter_secure_storage` | ^9.2.2  | تخزين آمن           |
| `path_provider`          | ^2.1.5  | مسارات الملفات      |

### 2.4 الشبكة والاتصال

| الحزمة              | الإصدار | الوظيفة       |
| ------------------- | ------- | ------------- |
| `dio`               | ^5.7.0  | HTTP client   |
| `http`              | ^1.2.2  | HTTP requests |
| `connectivity_plus` | ^6.1.1  | فحص الاتصال   |

### 2.5 واجهة المستخدم

| الحزمة                 | الإصدار | الوظيفة         |
| ---------------------- | ------- | --------------- |
| `flutter_svg`          | ^2.0.16 | عرض SVG         |
| `google_fonts`         | ^6.2.1  | خطوط Google     |
| `cached_network_image` | ^3.4.1  | تخزين الصور     |
| `fl_chart`             | ^0.69.2 | الرسوم البيانية |
| `cupertino_icons`      | ^1.0.8  | أيقونات iOS     |

### 2.6 الخرائط

| الحزمة        | الإصدار | الوظيفة          |
| ------------- | ------- | ---------------- |
| `flutter_map` | ^7.0.2  | خرائط تفاعلية    |
| `latlong2`    | ^0.9.1  | إحداثيات جغرافية |

### 2.7 الكاميرا والماسح

| الحزمة           | الإصدار   | الوظيفة         |
| ---------------- | --------- | --------------- |
| `camera`         | ^0.11.0+2 | الكاميرا        |
| `image_picker`   | ^1.1.2    | اختيار الصور    |
| `mobile_scanner` | ^6.0.2    | ماسح QR/Barcode |

### 2.8 أدوات أخرى

| الحزمة                        | الإصدار | الوظيفة         |
| ----------------------------- | ------- | --------------- |
| `go_router`                   | ^14.6.2 | التنقل          |
| `workmanager`                 | ^0.6.0  | المهام الخلفية  |
| `flutter_local_notifications` | ^18.0.1 | الإشعارات       |
| `flutter_dotenv`              | ^5.2.1  | متغيرات البيئة  |
| `uuid`                        | ^4.5.1  | توليد UUID      |
| `intl`                        | ^0.19.0 | التعريب         |
| `equatable`                   | ^2.0.7  | مقارنة الكائنات |
| `jiffy`                       | ^6.3.1  | معالجة التواريخ |

### 2.9 Code Generation

| الحزمة               | الإصدار | الوظيفة             |
| -------------------- | ------- | ------------------- |
| `build_runner`       | ^2.4.13 | Code generation     |
| `freezed`            | ^2.5.7  | Immutable classes   |
| `freezed_annotation` | ^2.4.4  | Freezed annotations |
| `json_serializable`  | ^6.8.0  | JSON serialization  |
| `json_annotation`    | ^4.9.0  | JSON annotations    |
| `drift_dev`          | ^2.22.1 | Drift code gen      |

---

## 3. خدمات API (Backend Services)

### 3.1 منافذ الخدمات

| الخدمة          | المنفذ | الوصف                 |
| --------------- | ------ | --------------------- |
| Field Core      | 3000   | الخدمة الأساسية       |
| Marketplace     | 3010   | السوق والمحفظة        |
| Kong Gateway    | 8000   | بوابة API             |
| Satellite       | 8090   | الأقمار الصناعية      |
| Indicators      | 8091   | المؤشرات الزراعية     |
| Weather         | 8092   | الطقس                 |
| Fertilizer      | 8093   | التسميد               |
| Irrigation      | 8094   | الري                  |
| Crop Health     | 8095   | صحة المحاصيل          |
| Virtual Sensors | 8096   | المستشعرات الافتراضية |
| Community Chat  | 8097   | الدردشة               |
| Equipment       | 8101   | المعدات               |
| Notifications   | 8110   | الإشعارات             |

### 3.2 نقاط API الرئيسية

#### Field Core (3000)

```
/api/v1/fields          - إدارة الحقول
/api/v1/tasks           - إدارة المهام
/api/v1/auth/login      - تسجيل الدخول
/api/v1/auth/register   - التسجيل
```

#### Satellite Service (8090)

```
/v1/analyze             - تحليل NDVI
/v1/timeseries          - السلسلة الزمنية
/v1/satellites          - الأقمار المتاحة
/v1/imagery             - طلب الصور
```

#### Weather Service (8092)

```
/v1/current/{location}  - الطقس الحالي
/v1/forecast/{location} - التنبؤات
/v1/alerts/{location}   - التنبيهات
/v1/agricultural-calendar - التقويم الزراعي
```

#### Crop Health AI (8095)

```
/v1/diagnose            - التشخيص
/v1/diagnose/batch      - تشخيص متعدد
/v1/crops               - المحاصيل المدعومة
/v1/diseases            - الأمراض
/v1/treatment/{id}      - العلاج
```

---

## 4. إعدادات التكامل

### 4.1 HTTP Headers

```dart
// Default headers
{
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Accept-Language': 'ar,en',
}

// Auth headers
{
  'Authorization': 'Bearer <token>',
}

// Tenant headers
{
  'X-Tenant-Id': '<tenant_id>',
}
```

### 4.2 Timeouts

| النوع          | المدة | الاستخدام        |
| -------------- | ----- | ---------------- |
| Connect        | 30s   | الاتصال          |
| Send           | 15s   | الإرسال          |
| Receive        | 15s   | الاستقبال        |
| Long Operation | 60s   | العمليات الطويلة |

### 4.3 Health Checks

```
/healthz - فحص صحة الخدمة
```

---

## 5. الاختبارات

### 5.1 Frontend Tests (Vitest)

```bash
# تشغيل اختبارات Web
npm run test --workspace=apps/web

# تشغيل اختبارات Admin
npm run test --workspace=apps/admin

# تشغيل اختبارات API Client
npm run test --workspace=packages/api-client
```

### 5.2 Mobile Tests (Flutter)

```bash
# تشغيل جميع الاختبارات
flutter test

# تشغيل اختبارات API
flutter test test/unit/api/

# تشغيل اختبارات مع التغطية
flutter test --coverage
```

---

## 6. إرشادات الترقية

### 6.1 ترقية Frontend

1. تحديث `package.json` في كل من web و admin
2. تشغيل `npm install` من الجذر
3. تشغيل `npm run type-check`
4. تشغيل الاختبارات
5. تشغيل `npm run build:all`

### 6.2 ترقية Mobile

1. تحديث `pubspec.yaml`
2. تشغيل `flutter pub get`
3. تشغيل `flutter pub outdated`
4. تشغيل `flutter test`
5. تشغيل `flutter build apk`

---

## 7. التوافق

### 7.1 متطلبات Node.js

```json
{
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=10.0.0"
  }
}
```

### 7.2 متطلبات Flutter

```yaml
environment:
  sdk: ">=3.2.0 <4.0.0"
```

### 7.3 متطلبات Android

```kotlin
minSdk = 23
compileSdk = 34
targetSdk = 34
```

---

## 8. الأمان

### 8.1 الحزم الآمنة

- جميع الحزم محدثة لآخر إصدار آمن
- `npm audit` يعرض 0 ثغرات
- تم إصلاح CVE-2025-29927 و CVE-2025-55182 في Next.js

### 8.2 فحوصات الأمان

```bash
# Frontend
npm audit

# Mobile
flutter pub outdated
```

---

## التاريخ

- **تاريخ الإنشاء:** 2025-12-20
- **آخر تحديث:** 2025-12-20
- **الإصدار:** 17.0.0 (Frontend) / 15.4.0 (Mobile)
