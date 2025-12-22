# SAHOOL Field App 🌾

تطبيق ساهول الميداني - تطبيق الزراعة الذكية

## نظرة عامة

تطبيق Flutter للعمليات الزراعية الميدانية مع دعم كامل للعمل دون اتصال (Offline-First).

## المتطلبات

| المتطلب | الإصدار |
|---------|---------|
| Flutter | 3.27.1+ |
| Dart SDK | 3.6.0+ |
| Android minSdk | 23 (Android 6.0) |
| iOS | 12.0+ |
| Java | 17 |

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
flutter_riverpod: ^2.6.1     # State Management
riverpod_annotation: ^2.6.1  # Annotations
```

### قاعدة البيانات (Offline)
```yaml
drift: ^2.24.0               # SQLite ORM
sqlite3_flutter_libs: ^0.5.28
```

### الشبكة
```yaml
dio: ^5.7.0                  # HTTP Client
connectivity_plus: ^6.1.1    # Network Status
```

### الخرائط
```yaml
flutter_map: ^7.0.2          # Maps
latlong2: ^0.9.1             # Coordinates
```

### التخزين الآمن
```yaml
flutter_secure_storage: ^9.2.2
shared_preferences: ^2.3.3
```

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

## بناء APK

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

## مصفوفة التوافق

| الحزمة | الإصدار | ملاحظات |
|--------|---------|---------|
| Flutter | 3.27.1 | Dart 3.6.0 |
| freezed | 2.5.8 | آخر إصدار متوافق مع Dart 3.6.0 |
| build_runner | 2.4.13 | متوافق مع analyzer 7.x |
| drift | 2.24.0 | قاعدة بيانات Offline |

### الحزم المحذوفة

| الحزمة | السبب |
|--------|-------|
| mockito | غير متوافق مع analyzer 7.x |
| google_fonts | استُبدل بخطوط محلية |

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
  FLUTTER_VERSION: '3.27.1'
  JAVA_VERSION: '17'

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
