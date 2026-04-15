# Mobile Apps Merge Plan

## خطة دمج تطبيقات الجوال

**التاريخ**: 2026-03-23
**النسخة**: 16.0.0
**الحالة**: مسودة - تحتاج موافقة الفريق
**المرجع**: [MOBILE_APPS_FEATURE_COMPARISON_REVIEW.md](MOBILE_APPS_FEATURE_COMPARISON_REVIEW.md)

---

## الاكتشاف الجوهري

التحليل كشف أن البنية الحالية تعاني من مشكلة معمارية أساسية:

```
apps/mobile/
├── lib/                      ← مكتبة يتيمة (Orphaned)
│                                غير مستوردة من أي تطبيق!
├── sahool_field_app/         ← التطبيق الفعلي المستقل
│   └── lib/                     كود مكرر بالكامل
├── sahol_atmosphere/         ← تطبيق الطقس المستقل
│   └── lib/                     كود مكرر أيضاً
└── sahool-mobile/            ← TypeScript/Node.js (مختلف تماماً)
```

**المشكلة**: لا يوجد `path:` dependencies بين التطبيقات. كل تطبيق Flutter يحتوي على نسخة كاملة من الـ core. أي إصلاح bug يجب تطبيقه في مكانين أو أكثر.

---

## الأهداف

1. **إنشاء مكتبة مشتركة** (`packages/mobile-shared/`) كمصدر وحيد للحقيقة
2. **دمج أفضل التنفيذات** من كلا التطبيقين
3. **إزالة الازدواجية** وتقليل تكلفة الصيانة
4. **عدم كسر أي وظيفة قائمة** أثناء الدمج

---

## المرحلة 0: التحضير (أسبوع 1)

### 0.1 إنشاء مكتبة Flutter المشتركة

```bash
# إنشاء الحزمة المشتركة
mkdir -p packages/mobile-shared
cd packages/mobile-shared
flutter create --template=package .
```

**الملف**: `packages/mobile-shared/pubspec.yaml`

```yaml
name: sahool_mobile_shared
description: Shared Flutter code for SAHOOL mobile apps
version: 16.0.0
publish_to: none

environment:
  sdk: '>=3.2.0 <4.0.0'
  flutter: '>=3.27.0'

dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.6.1
  dio: ^5.7.0
  drift: ^2.24.0
  freezed_annotation: ^2.4.0
  json_annotation: ^4.9.0
  nats_client: ^1.0.0
  connectivity_plus: ^6.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.0
  freezed: ^2.5.0
  json_serializable: ^6.8.0
```

**البنية المستهدفة:**

```
packages/mobile-shared/
├── lib/
│   ├── sahool_mobile_shared.dart    # Barrel export
│   ├── core/
│   │   ├── api/                     # API client + interceptors
│   │   ├── auth/                    # JWT + providers
│   │   ├── config/                  # Environment + feature flags
│   │   ├── http/                    # Dio + retry + certificate pinning
│   │   ├── offline/                 # Sync engine + outbox + conflict
│   │   ├── security/               # Device integrity + request signing
│   │   ├── storage/                # Drift DB + SQLCipher
│   │   └── sync/                   # Background sync + outbox
│   ├── domain/
│   │   ├── models/                 # Shared domain models
│   │   └── services/               # Shared domain services
│   └── utils/                      # Shared utilities
├── test/
└── pubspec.yaml
```

### 0.2 تحديث pubspec.yaml في التطبيقات

```yaml
# في sahool_field_app/pubspec.yaml و أي تطبيق آخر
dependencies:
  sahool_mobile_shared:
    path: ../../packages/mobile-shared
```

### 0.3 إنشاء فرع الدمج

```bash
git checkout -b feature/mobile-shared-package
```

---

## المرحلة 1: دمج البنية الأساسية Core (أسبوع 2)

### 1.1 نقل Offline/Sync Infrastructure

**المصدر**: `sahool_field_app/lib/core/` (الأكمل)
**الهدف**: `packages/mobile-shared/lib/core/`

| الملف المصدر | الهدف | الملاحظات |
|:---|:---|:---|
| `sahool_field_app/lib/core/offline/offline_sync_engine.dart` | `mobile-shared/lib/core/offline/` | الأكمل |
| `sahool_field_app/lib/core/offline/outbox_repository.dart` | `mobile-shared/lib/core/offline/` | حصري لـ Field App |
| `sahool_field_app/lib/core/offline/sync_conflict_resolver.dart` | `mobile-shared/lib/core/offline/` | دمج مع Main lib version |
| `sahool_field_app/lib/core/offline/offline_data_manager.dart` | `mobile-shared/lib/core/offline/` | حصري لـ Field App |
| `sahool_field_app/lib/core/offline/offline_completeness.dart` | `mobile-shared/lib/core/offline/` | حصري لـ Field App |
| `sahool_field_app/lib/core/sync/sync_engine.dart` | `mobile-shared/lib/core/sync/` | دمج أفضل من الاثنين |
| `sahool_field_app/lib/core/sync/background_sync_task.dart` | `mobile-shared/lib/core/sync/` | متشابه في الاثنين |
| `sahool_field_app/lib/core/sync/network_status.dart` | `mobile-shared/lib/core/sync/` | متشابه |
| `sahool_field_app/lib/core/sync/queue_manager.dart` | `mobile-shared/lib/core/sync/` | متشابه |
| `sahool_field_app/lib/core/sync/sync_worker.dart` | `mobile-shared/lib/core/sync/` | متشابه |
| `sahool_field_app/lib/core/sync/sync_metrics_providers.dart` | `mobile-shared/lib/core/sync/` | حصري لـ Field App |
| `sahool_field_app/lib/core/sync/sync_metrics_service.dart` | `mobile-shared/lib/core/sync/` | حصري لـ Field App |

**Outbox Sub-system** (كامل من Field App):

| الملف | الهدف |
|:---|:---|
| `sahool_field_app/lib/core/sync/outbox/outbox_entry.dart` | `mobile-shared/lib/core/sync/outbox/` |
| `sahool_field_app/lib/core/sync/outbox/outbox_processor.dart` | `mobile-shared/lib/core/sync/outbox/` |
| `sahool_field_app/lib/core/sync/outbox/outbox_service.dart` | `mobile-shared/lib/core/sync/outbox/` |
| `sahool_field_app/lib/core/sync/outbox/outbox_tables.dart` | `mobile-shared/lib/core/sync/outbox/` |
| `sahool_field_app/lib/core/sync/outbox/conflict_handler.dart` | `mobile-shared/lib/core/sync/outbox/` |
| `sahool_field_app/lib/core/sync/outbox/sync_status_provider.dart` | `mobile-shared/lib/core/sync/outbox/` |
| `sahool_field_app/lib/core/sync/outbox/sync_status_widget.dart` | `mobile-shared/lib/core/sync/outbox/` |

**خطوات التنفيذ:**

```bash
# 1. نسخ الملفات
cp -r apps/mobile/sahool_field_app/lib/core/offline/ packages/mobile-shared/lib/core/offline/
cp -r apps/mobile/sahool_field_app/lib/core/sync/ packages/mobile-shared/lib/core/sync/

# 2. تحديث imports في الملفات المنسوخة
# تغيير: import '../../storage/database.dart';
# إلى:   import 'package:sahool_mobile_shared/core/storage/database.dart';

# 3. تحديث imports في sahool_field_app
# تغيير: import '../core/offline/outbox_repository.dart';
# إلى:   import 'package:sahool_mobile_shared/core/offline/outbox_repository.dart';
```

### 1.2 نقل Security Layer

**المصدر**: Field App (الأكمل - يحتوي Request Signing)

| الملف | الاتجاه | الملاحظات |
|:---|:---|:---|
| `sahool_field_app/lib/core/security/certificate_pinning.dart` | → mobile-shared | الأكمل (3-tier) |
| `sahool_field_app/lib/core/security/device_integrity.dart` | → mobile-shared | متشابه |
| `sahool_field_app/lib/core/security/request_signing.dart` | → mobile-shared | **حصري Field App** |
| `lib/core/security/screenshot_prevention.dart` | → mobile-shared | من Main lib |

### 1.3 نقل Feature Flags

**المصدر**: Main lib (بنية أكثر تطوراً)

| الملف | الاتجاه |
|:---|:---|
| `lib/core/feature_flags/feature_flags.dart` | → mobile-shared |
| `lib/core/feature_flags/feature_flag.dart` | → mobile-shared |
| `lib/core/feature_flags/feature_flags_config.dart` | → mobile-shared |
| `lib/core/feature_flags/feature_flags_service.dart` | → mobile-shared |
| `lib/core/feature_flags/remote_config.dart` | → mobile-shared |

---

## المرحلة 2: دمج الميزات (أسبوع 3-4)

### 2.1 نقل Vision Feature → Main lib

**المصدر**: `sahool_field_app/lib/features/vision/` (5 ملفات)
**الهدف**: `packages/mobile-shared/lib/features/vision/`

| الملف | الوصف |
|:---|:---|
| `vision.dart` | Barrel export |
| `data/yolo26_service.dart` | خدمة YOLO26 للكشف |
| `domain/detection_model.dart` | نماذج الكشف |
| `presentation/detection_screen.dart` | شاشة الكشف |
| `presentation/providers/vision_providers.dart` | Riverpod providers |

**التبعيات**: يعتمد على `core/api/` و `core/http/` - يجب نقلها أولاً.

### 2.2 نقل Irrigation Domain Services → Main lib

**المصدر**: `sahool_field_app/lib/features/irrigation/domain/services/` (3 ملفات)
**الهدف**: `apps/mobile/lib/features/irrigation/domain/services/` (إضافة للموجود)

| الملف | الوصف |
|:---|:---|
| `irrigation_scheduler.dart` | جدولة الري التلقائية |
| `water_calculator.dart` | حساب كميات المياه |
| `weather_irrigation_integration.dart` | تكامل الطقس مع الري |

**ملاحظة**: Main lib يحتوي على presentation layer كامل. الدمج يضيف domain services بدون تعديل الموجود.

### 2.3 نقل CRM → Field App

**المصدر**: `apps/mobile/lib/features/crm/` (18 ملف)
**الهدف**: `sahool_field_app/lib/features/crm/`

```
crm/
├── data/
│   ├── crm_api.dart                    # API client
│   ├── crm_local_database.dart         # Local DB
│   └── crm_repository.dart             # Repository pattern
├── domain/models/
│   ├── farmer_profile.dart             # ملف المزارع
│   ├── interaction.dart                # التفاعلات
│   ├── opportunity.dart                # الفرص
│   └── activity_log.dart               # سجل الأنشطة
├── state/
│   ├── crm_controller.dart             # State controller
│   └── crm_providers.dart              # Riverpod providers
└── presentation/
    ├── screens/
    │   ├── farmers_list_screen.dart     # قائمة المزارعين
    │   ├── farmer_profile_screen.dart   # ملف المزارع
    │   ├── farmer_analytics_screen.dart # تحليلات المزارع
    │   ├── interaction_history_screen.dart
    │   └── add_interaction_screen.dart
    └── widgets/
        ├── farmer_card.dart
        ├── activity_chart.dart
        ├── interaction_timeline.dart
        └── contact_actions.dart
```

**التبعيات**: يعتمد على `core/sync/network_status.dart` - موجود في Field App.

### 2.4 نقل Reports → Field App

**المصدر**: `apps/mobile/lib/features/reports/` (19 ملف)
**الهدف**: `sahool_field_app/lib/features/reports/`

```
reports/
├── data/
│   ├── reports_api.dart
│   ├── reports_repository.dart
│   └── report_generator.dart
├── domain/models/
│   ├── report_template.dart
│   ├── report_data.dart
│   ├── report_filter.dart
│   └── chart_config.dart
├── state/
│   ├── reports_providers.dart
│   └── report_builder_controller.dart
└── presentation/
    ├── screens/
    │   ├── reports_dashboard_screen.dart
    │   ├── report_builder_screen.dart
    │   ├── report_viewer_screen.dart
    │   └── report_share_screen.dart
    └── widgets/
        ├── chart_widget.dart
        ├── report_card.dart
        ├── report_data_table.dart
        ├── export_button.dart
        ├── date_range_picker_widget.dart
        └── filter_chips_widget.dart
```

---

## المرحلة 3: الإصلاحات والتنظيف (أسبوع 4)

### 3.1 إصلاح ازدواجية Diagnosis Models

**الإجراء**: حذف الملف غير المستخدم

```bash
# diagnosis_model.dart غير مستورد في أي مكان
# diagnosis_models.dart هو الملف النشط المستخدم فعلياً
rm apps/mobile/sahool_field_app/lib/features/crop_health/data/models/diagnosis_model.dart
rm apps/mobile/sahool_field_app/lib/features/crop_health/data/models/diagnosis_model.freezed.dart
rm apps/mobile/sahool_field_app/lib/features/crop_health/data/models/diagnosis_model.g.dart
```

### 3.2 توحيد الميزات المتطابقة

الميزات التالية متطابقة 100% في كلا التطبيقين ويجب نقلها لمكتبة مشتركة:

| الميزة | عدد الملفات | الأولوية |
|:---|:---:|:---|
| `weather/` | 15 | عالية - متطابقة تماماً |
| `chat/` | 11 | عالية - متطابقة تماماً |
| `satellite/` | 17 | عالية - متطابقة تماماً |

**الإجراء لكل ميزة:**

```bash
# 1. نقل إلى المكتبة المشتركة
mv apps/mobile/sahool_field_app/lib/features/weather/ packages/mobile-shared/lib/features/weather/

# 2. تحديث imports في sahool_field_app
# من: import '../features/weather/...'
# إلى: import 'package:sahool_mobile_shared/features/weather/...'

# 3. تحديث imports في Main lib (إذا تقرر استخدامه)
# نفس النمط
```

### 3.3 إكمال Equipment في Field App

**الحالة الحالية**: 6 ملفات (skeleton)
**المطلوب**: نقل التنفيذ الكامل من Main lib (22 ملف)

| المجلد | الملفات المطلوب نقلها |
|:---|:---|
| `domain/models/` | fuel_record, maintenance_record, usage_record |
| `domain/services/` | equipment lifecycle services |
| `presentation/screens/` | fuel_tracking, maintenance, usage_log |
| `presentation/widgets/` | equipment_card, fuel_chart, maintenance_timeline |
| `state/` | equipment state management |

### 3.4 تنظيف المكتبة اليتيمة

بعد اكتمال الدمج، يجب تقييم `apps/mobile/lib/`:

```
الخيار A: حذف المكتبة اليتيمة بالكامل (مفضل)
  - بعد التأكد من نقل كل الكود المفيد
  - نقلها لـ archive/ أولاً كاحتياط

الخيار B: تحويلها لتطبيق ثالث
  - إذا كان هناك حاجة لتطبيق منفصل
  - يتطلب pubspec.yaml صحيح
```

---

## المرحلة 4: التحقق والاختبار (أسبوع 5)

### 4.1 قائمة التحقق

- [ ] `flutter analyze` يمر بدون أخطاء في كل التطبيقات
- [ ] `flutter test` يمر في `packages/mobile-shared/`
- [ ] `flutter test` يمر في `sahool_field_app/`
- [ ] لا يوجد imports مكسورة (`dart fix --dry-run`)
- [ ] Freezed code generation يعمل (`dart run build_runner build`)
- [ ] الـ APK يُبنى بنجاح (`flutter build apk --debug`)
- [ ] الميزات المنقولة تعمل (اختبار يدوي):
  - [ ] CRM: عرض المزارعين، إضافة تفاعل
  - [ ] Reports: إنشاء تقرير، تصدير
  - [ ] Vision: كشف آفات من صورة
  - [ ] Irrigation Services: جدولة ري
  - [ ] Offline Sync: مزامنة بعد انقطاع الشبكة

### 4.2 اختبار الانحدار (Regression)

```bash
# تشغيل كل الاختبارات
cd apps/mobile/sahool_field_app && flutter test
cd packages/mobile-shared && flutter test

# تحليل ثابت
cd apps/mobile/sahool_field_app && flutter analyze
cd packages/mobile-shared && flutter analyze

# بناء تجريبي
cd apps/mobile/sahool_field_app && flutter build apk --debug
```

---

## مصفوفة المخاطر

| المخاطرة | الاحتمال | التأثير | التخفيف |
|:---|:---:|:---:|:---|
| كسر imports بعد النقل | عالي | متوسط | استخدام `dart fix` + IDE refactoring |
| تعارض Freezed codegen | متوسط | عالي | تشغيل `build_runner` بعد كل نقل |
| تعارض إصدارات الحزم | منخفض | عالي | توحيد pubspec.yaml أولاً |
| فقدان وظيفة أثناء الدمج | منخفض | عالي | اختبار يدوي لكل ميزة منقولة |
| تأثير على Atmosphere App | منخفض | منخفض | مستقل تماماً - لن يتأثر |

---

## ملخص الملفات حسب الاتجاه

### Field App → Mobile Shared (21 ملف)

```
core/offline/offline_sync_engine.dart
core/offline/outbox_repository.dart
core/offline/sync_conflict_resolver.dart
core/offline/offline_data_manager.dart
core/offline/offline_completeness.dart
core/offline/offline.dart
core/sync/sync_metrics_providers.dart
core/sync/sync_metrics_service.dart
core/sync/outbox/outbox_entry.dart
core/sync/outbox/outbox_processor.dart
core/sync/outbox/outbox_service.dart
core/sync/outbox/outbox_tables.dart
core/sync/outbox/conflict_handler.dart
core/sync/outbox/sync_status_provider.dart
core/sync/outbox/sync_status_widget.dart
core/sync/outbox/outbox.dart
core/security/request_signing.dart
features/vision/vision.dart
features/vision/data/yolo26_service.dart
features/vision/domain/detection_model.dart
features/vision/presentation/detection_screen.dart
features/vision/presentation/providers/vision_providers.dart
```

### Main lib → Field App (40 ملف)

```
features/crm/ (18 ملفات)
features/reports/ (19 ملفات)
core/feature_flags/ (5+ ملفات)
```

### Field App → Main lib (3 ملفات)

```
features/irrigation/domain/services/irrigation_scheduler.dart
features/irrigation/domain/services/water_calculator.dart
features/irrigation/domain/services/weather_irrigation_integration.dart
```

### للحذف (3 ملفات)

```
sahool_field_app/lib/features/crop_health/data/models/diagnosis_model.dart
sahool_field_app/lib/features/crop_health/data/models/diagnosis_model.freezed.dart
sahool_field_app/lib/features/crop_health/data/models/diagnosis_model.g.dart
```

---

## الجدول الزمني

| المرحلة | المدة | المخرجات |
|:---|:---:|:---|
| **0: التحضير** | أسبوع 1 | مكتبة `mobile-shared` فارغة + pubspec محدث |
| **1: Core Infrastructure** | أسبوع 2 | Offline, Sync, Security, Feature Flags في المكتبة المشتركة |
| **2: Features** | أسبوع 3-4 | Vision, CRM, Reports, Irrigation Services منقولة |
| **3: التنظيف** | أسبوع 4 | ازدواجية محذوفة، Equipment مكتمل، Weather/Chat/Satellite موحدة |
| **4: التحقق** | أسبوع 5 | كل الاختبارات تمر، APK يُبنى، اختبار يدوي مكتمل |

**المجموع**: ~5 أسابيع

---

_آخر تحديث: 2026-03-23_
_تم إنشاؤه بواسطة: Claude AI Agent_
_الفرع: claude/review-mobile-app-7bNhE_
