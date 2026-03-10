# SAHOOL Field App 🌾

تطبيق ساهول الميداني - تطبيق الزراعة الذكية

## نظرة عامة

تطبيق Flutter للعمليات الزراعية الميدانية مع دعم كامل للعمل دون اتصال (Offline-First).

## المتطلبات

| المتطلب        | الإصدار          |
| -------------- | ---------------- |
| Flutter        | 3.27.1+          |
| Dart SDK       | 3.6.0+           |
| Android minSdk | 23 (Android 6.0) |
| iOS            | 12.0+            |
| Java           | 17               |

## التثبيت

```bash
# استنساخ المشروع
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp/apps/mobile

# تثبيت التبعيات
flutter pub get

# توليد الكود (Freezed, Drift, JSON)
flutter pub run build_runner build --delete-conflicting-outputs

# تشغيل التطبيق
flutter run
```

## البنية المعمارية

```
lib/
├── core/                    # المكونات الأساسية
│   ├── auth/               # المصادقة والأمان
│   ├── config/             # الإعدادات
│   ├── database/           # Drift Database
│   ├── http/               # API Client & Interceptors
│   ├── notifications/      # الإشعارات
│   ├── performance/        # تحسينات الأداء
│   ├── services/           # الخدمات
│   ├── theme/              # الثيمات
│   ├── utils/              # الأدوات المساعدة
│   └── widgets/            # الودجات المشتركة
├── features/               # الميزات
│   ├── daily_brief/        # الملخص اليومي
│   ├── equipment/          # المعدات
│   ├── fields/             # الحقول
│   ├── research/           # البحث
│   ├── smart_alerts/       # التنبيهات الذكية
│   └── tasks/              # المهام
└── main.dart
```

## التبعيات الرئيسية

### إدارة الحالة

```yaml
flutter_riverpod: ^2.6.1 # State Management
riverpod_annotation: ^2.6.1 # Annotations
```

### قاعدة البيانات (Offline)

```yaml
drift: ^2.24.0 # SQLite ORM
sqlite3_flutter_libs: ^0.5.28
```

### الشبكة

```yaml
dio: ^5.7.0 # HTTP Client
connectivity_plus: ^6.1.1 # Network Status
```

### الخرائط

```yaml
flutter_map: ^7.0.2 # Maps
latlong2: ^0.9.1 # Coordinates
```

### التخزين الآمن

```yaml
flutter_secure_storage: ^9.2.2
shared_preferences: ^2.3.3
```

## 🔌 الاتصال بالخدمات الخلفية | Backend Integration

### إعداد البيئة | Environment Setup

قم بنسخ ملف `.env.example` إلى `.env`:

```bash
cp .env.example .env
```

### عناوين الخدمات | Service URLs

| البيئة                             | API Gateway                      | WebSocket                     |
| ---------------------------------- | -------------------------------- | ----------------------------- |
| **Development (Android Emulator)** | `http://10.0.2.2:8000`           | `ws://10.0.2.2:8081`          |
| **Development (iOS Simulator)**    | `http://localhost:8000`          | `ws://localhost:8081`         |
| **Development (Real Device)**      | `http://<YOUR-IP>:8000`          | `ws://<YOUR-IP>:8081`         |
| **Staging**                        | `https://api-staging.sahool.app` | `wss://ws-staging.sahool.app` |
| **Production**                     | `https://api.sahool.io`          | `wss://ws.sahool.io`          |

### خريطة المنافذ | Port Map

```
البوابة الرئيسية (Kong Gateway):
└── 8000  → جميع الـ API تمر عبر هذا المنفذ

WebSocket Gateway:
└── 8081  → الأحداث المباشرة (Real-time)

الخدمات الداخلية (عبر Gateway):
├── /api/v1/fields      → field-core (3000)
├── /api/v1/tasks       → task-service (8103)
├── /api/v1/weather     → weather-service (8092)
├── /api/v1/ndvi        → satellite-service (8090)
├── /api/v1/alerts      → notification-service (8110)
├── /api/v1/equipment   → equipment-service (8101)
├── /api/v1/irrigation  → irrigation-smart (8094)
├── /api/v1/fertilizer  → advisory-service (8093)
└── /api/v1/crop-health → crop-health-ai (8095)
```

### استخدام API Client

```dart
import 'package:sahool_field_app/core/http/api_client.dart';

// التهيئة
final apiClient = ApiClient();

// جلب الحقول
final fields = await apiClient.getFields();

// جلب المهام
final tasks = await apiClient.getTasks(fieldId: 'field_001');

// تحديث مهمة
await apiClient.updateTask('task_001', status: 'completed');
```

### استخدام Service Switcher

للتبديل بين الخدمات القديمة والحديثة للمقارنة:

```dart
import 'package:sahool_field_app/core/config/service_switcher.dart';

// التهيئة
final switcher = ServiceSwitcher.instance;
await switcher.initialize();

// التبديل لخدمة حديثة
await switcher.setVersion(ServiceType.weather, ServiceVersion.modern);

// التبديل لخدمة قديمة للمقارنة
await switcher.setVersion(ServiceType.weather, ServiceVersion.legacy);

// فحص صحة الخدمات
final health = await switcher.checkAllHealth();
```

### تشغيل المحاكاة المحلية | Local Mock Server

للتطوير بدون خدمات Backend حقيقية:

```bash
# من مجلد apps/web
cd ../web

# تشغيل Mock API Server
node mock-server.js    # Port 8000

# تشغيل Mock WebSocket Server
node mock-ws-server.js # Port 8081
```

### متغيرات البيئة | Environment Variables

```env
# .env
ENV=development
API_URL=http://10.0.2.2:8000/api/v1
WS_URL=ws://10.0.2.2:8081

# Feature Flags
ENABLE_OFFLINE_MODE=true
ENABLE_BACKGROUND_SYNC=true

# Timeouts
CONNECT_TIMEOUT_SECONDS=10
RECEIVE_TIMEOUT_SECONDS=30
```

### معالجة الأخطاء | Error Handling

```dart
try {
  final data = await apiClient.getFields();
} on DioException catch (e) {
  if (e.type == DioExceptionType.connectionTimeout) {
    // عرض رسالة "لا يوجد اتصال"
    showOfflineSnackbar();
  } else if (e.response?.statusCode == 401) {
    // إعادة تسجيل الدخول
    navigateToLogin();
  }
}
```

---

## إعدادات البناء

### Android (build.gradle.kts)

```kotlin
android {
    compileSdk = 36

    defaultConfig {
        minSdk = 23        // مطلوب للكاميرا
        targetSdk = 36
    }

    // تقسيم APK حسب المعمارية
    splits {
        abi {
            isEnable = true
            include("arm64-v8a", "armeabi-v7a", "x86_64")
            isUniversalApk = true
        }
    }
}
```

### الخطوط المحلية

الخطوط مضمنة محلياً للأداء الأفضل:

```yaml
flutter:
  fonts:
    - family: IBMPlexSansArabic
      fonts:
        - asset: assets/fonts/IBMPlexSansArabic-Regular.ttf
          weight: 400
        - asset: assets/fonts/IBMPlexSansArabic-Medium.ttf
          weight: 500
        - asset: assets/fonts/IBMPlexSansArabic-SemiBold.ttf
          weight: 600
        - asset: assets/fonts/IBMPlexSansArabic-Bold.ttf
          weight: 700
```

## توليد الكود

### build.yaml

```yaml
targets:
  $default:
    builders:
      json_serializable:
        generate_for:
          - lib/models/**/*.dart
      freezed:
        generate_for:
          - lib/models/**/*.dart
      drift_dev:
        generate_for:
          - lib/core/database/**/*.dart
```

### أوامر التوليد

```bash
# توليد مرة واحدة
flutter pub run build_runner build

# توليد مع المراقبة
flutter pub run build_runner watch

# حذف الملفات المتعارضة
flutter pub run build_runner build --delete-conflicting-outputs
```

## الاختبارات

```bash
# تشغيل جميع الاختبارات
flutter test

# اختبارات الوحدة
flutter test test/unit/

# اختبارات الـ Widget
flutter test test/widget/

# اختبارات التكامل
flutter test test/integration/

# مع التغطية
flutter test --coverage
```

## بناء APK (Android)

```bash
# Debug APK
flutter build apk --debug

# Release APK (Universal)
flutter build apk --release

# Release APK (Split by ABI)
flutter build apk --release --split-per-abi

# App Bundle للـ Play Store
flutter build appbundle --release
```

## بناء IPA (iOS)

### المتطلبات

- macOS مع Xcode 14.0+
- حساب Apple Developer مفعل
- شهادة توزيع (Distribution Certificate)
- Provisioning Profile للتطبيق

### معرف الحزمة (Bundle Identifier)

تم تكوين التطبيق بمعرف حزمة الإنتاج:

```
Bundle ID: io.sahool.field
Test Bundle ID: io.sahool.field.RunnerTests
```

**ملاحظة مهمة للـ App Store:**

- معرف الحزمة مكون في `/apps/mobile/ios/Runner.xcodeproj/project.pbxproj`
- يجب أن يتطابق مع معرف التطبيق المسجل في Apple Developer Console
- لتغيير معرف الحزمة، قم بتحديث `PRODUCT_BUNDLE_IDENTIFIER` في جميع التكوينات (Debug, Release, Profile)

### بناء للـ App Store

```bash
# من مجلد apps/mobile
cd /home/user/sahool-unified-v15-idp/apps/mobile

# بناء IPA للإصدار
flutter build ios --release

# أو بناء وأرشفة من Xcode
cd ios
xcodebuild -workspace Runner.xcworkspace \
  -scheme Runner \
  -configuration Release \
  -archivePath build/Runner.xcarchive \
  archive

# تصدير IPA
xcodebuild -exportArchive \
  -archivePath build/Runner.xcarchive \
  -exportPath build/ipa \
  -exportOptionsPlist ExportOptions.plist
```

### قائمة التحقق قبل النشر على App Store

- [ ] تحديث رقم الإصدار في `pubspec.yaml`
- [ ] التأكد من معرف الحزمة صحيح: `io.sahool.field`
- [ ] تحديث شهادات SSL Pinning (راجع `ios/README_CERTIFICATE_PINNING.md`)
- [ ] التأكد من جميع الـ SPKI hashes محدثة في `Info.plist`
- [ ] اختبار التطبيق على أجهزة iOS فعلية
- [ ] التأكد من جميع الأذونات موثقة في `Info.plist`:
  - `NSCameraUsageDescription` - للكاميرا
  - `NSPhotoLibraryUsageDescription` - لمكتبة الصور
  - `NSLocationWhenInUseUsageDescription` - للموقع
- [ ] مراجعة إعدادات App Transport Security
- [ ] التأكد من عدم وجود مفاتيح API مشفرة في الكود
- [ ] بناء في وضع Release واختبار الأداء
- [ ] إعداد لقطات الشاشة ووصف التطبيق للـ App Store
- [ ] مراجعة إرشادات مراجعة App Store من Apple

### ملفات مهمة للـ iOS

```
ios/
├── Runner/
│   ├── Info.plist                    # إعدادات التطبيق والأذونات
│   └── Assets.xcassets/              # الأيقونات والصور
├── Runner.xcodeproj/
│   └── project.pbxproj               # إعدادات المشروع (Bundle ID هنا)
├── Runner.xcworkspace/               # مساحة عمل Xcode
└── README_CERTIFICATE_PINNING.md     # دليل تثبيت الشهادات
```

## مصفوفة التوافق

| الحزمة       | الإصدار | ملاحظات                        |
| ------------ | ------- | ------------------------------ |
| Flutter      | 3.27.1  | Dart 3.6.0                     |
| freezed      | 2.5.8   | آخر إصدار متوافق مع Dart 3.6.0 |
| build_runner | 2.4.13  | متوافق مع analyzer 7.x         |
| drift        | 2.24.0  | قاعدة بيانات Offline           |

### الحزم المحذوفة

| الحزمة       | السبب                      |
| ------------ | -------------------------- |
| mockito      | غير متوافق مع analyzer 7.x |
| google_fonts | استُبدل بخطوط محلية        |

## إدارة الذاكرة

### MemoryManager

```dart
// تهيئة
MemoryManager.instance.initialize();

// تخزين في الكاش
MemoryManager().put('key', data);

// استرجاع
final data = MemoryManager().get<MyType>('key');

// إزالة تلقائية للبيانات القديمة
await MemoryManager().autoEvict();
```

## الثيمات

### استخدام الثيم

```dart
MaterialApp(
  theme: SahoolTheme.lightTheme,
  darkTheme: SahoolTheme.darkTheme,
  themeMode: ThemeMode.system,
)
```

### ألوان الحالة

```dart
SahoolColors.success   // نجاح
SahoolColors.warning   // تحذير
SahoolColors.danger    // خطر
SahoolColors.info      // معلومات
```

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/mobile-ci.yml
env:
  FLUTTER_VERSION: "3.27.1"
  JAVA_VERSION: "17"

jobs:
  build:
    steps:
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: ${{ env.FLUTTER_VERSION }}
      - run: flutter pub get
      - run: flutter analyze
      - run: flutter test
      - run: flutter build apk --release
```

## المساهمة

1. Fork المشروع
2. إنشاء فرع للميزة (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'feat: add amazing feature'`)
4. Push للفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

### معايير الكود

- استخدام `flutter analyze` قبل كل commit
- كتابة اختبارات للميزات الجديدة
- اتباع نمط Conventional Commits
- التوثيق بالعربية والإنجليزية

## الترخيص

© 2024 SAHOOL - Smart Agriculture Solutions

## الدعم

- 📧 Email: support@sahool.io
- 📖 Documentation: [docs.sahool.io](https://docs.sahool.io)
- 🐛 Issues: [GitHub Issues](https://github.com/kafaat/sahool-unified-v15-idp/issues)
