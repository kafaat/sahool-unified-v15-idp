# SAHOOL Field App

تطبيق سهول للعمليات الميدانية - تطبيق موبايل يعمل بدون إنترنت

## الإصدار

**15.5.0** - تم التحديث في 2025-12-20

## المتطلبات

### بيئة التطوير

- Flutter SDK: `>=3.2.0 <4.0.0`
- Dart SDK: `>=3.2.0`
- Android SDK: API 23+ (Android 6.0+)
- iOS: 12.0+

### الأدوات المطلوبة

```bash
flutter --version  # Flutter 3.19+
dart --version     # Dart 3.6+
```

## التثبيت

```bash
# استنساخ المستودع
git clone <repo-url>
cd apps/mobile/sahool_field_app

# تثبيت المكتبات
flutter pub get

# تشغيل build_runner لتوليد الكود
dart run build_runner build --delete-conflicting-outputs

# تشغيل التطبيق
flutter run
```

## البنية المعمارية

```
lib/
├── core/                    # المكونات الأساسية
│   ├── auth/               # خدمات المصادقة
│   ├── config/             # الإعدادات والتكوين
│   ├── domain/models/      # النماذج الموحدة
│   ├── http/               # عميل API
│   ├── storage/            # قاعدة البيانات المحلية
│   ├── sync/               # محرك المزامنة
│   └── theme/              # السمات والألوان
│
├── features/               # الوحدات الوظيفية
│   ├── auth/               # تسجيل الدخول
│   ├── fields/             # إدارة الحقول
│   ├── home/               # الشاشة الرئيسية
│   ├── market/             # السوق
│   ├── notifications/      # الإشعارات
│   ├── profile/            # الملف الشخصي
│   └── wallet/             # المحفظة المالية
│
└── main.dart               # نقطة البداية
```

## إدارة الحالة

نستخدم **Riverpod 2.x** لإدارة الحالة:

```dart
// قراءة provider
final wallet = ref.watch(walletProvider);

// استخدام notifier
ref.read(authProvider.notifier).login(email, password);
```

## الخدمات الخلفية

| الخدمة          | المنفذ | الوصف             |
| --------------- | ------ | ----------------- |
| Kong Gateway    | 8000   | بوابة API الموحدة |
| Field Service   | 3000   | خدمة الحقول       |
| Weather Service | 8092   | خدمة الطقس        |
| Marketplace     | 3010   | خدمة السوق        |
| WebSocket       | 8090   | التحديثات الفورية |

## التكوين

### ملف .env

```env
# البيئة
ENV=development

# API
API_URL=http://10.0.2.2:8000/api/v1
WS_URL=ws://10.0.2.2:8090

# الميزات
ENABLE_OFFLINE_MODE=true
ENABLE_BACKGROUND_SYNC=true
ENABLE_PUSH=false

# التزامن
SYNC_INTERVAL_SECONDS=30
BG_SYNC_INTERVAL_MINUTES=15
```

### dart-define (أولوية أعلى)

```bash
flutter run --dart-define=ENV=production --dart-define=API_URL=https://api.sahool.app/api/v1
```

## المكتبات الرئيسية

| المكتبة          | الإصدار | الاستخدام              |
| ---------------- | ------- | ---------------------- |
| flutter_riverpod | ^2.6.1  | إدارة الحالة           |
| drift            | ^2.22.1 | قاعدة البيانات المحلية |
| dio              | ^5.7.0  | HTTP Client            |
| go_router        | ^14.6.2 | التنقل                 |
| flutter_map      | ^7.0.2  | الخرائط                |
| fl_chart         | ^0.69.2 | الرسوم البيانية        |

## البناء والنشر

### Android APK

```bash
flutter build apk --release --dart-define=ENV=production
```

### Android App Bundle

```bash
flutter build appbundle --release --dart-define=ENV=production
```

### iOS

```bash
flutter build ios --release --dart-define=ENV=production
```

## الاختبارات

```bash
# تشغيل جميع الاختبارات
flutter test

# اختبارات الوحدات فقط
flutter test test/unit/

# مع تغطية الكود
flutter test --coverage
```

## التغييرات الأخيرة (15.5.0)

### التحسينات:

- ✅ توحيد مزودات الإشعارات (3→1)
- ✅ توحيد خدمات المصادقة (2→1)
- ✅ إنشاء نموذج CreditTier موحد
- ✅ حذف الكود المكرر والمهجور

### الملفات المحذوفة:

- `core/services/auth_service.dart`
- `features/notifications/notification_provider.dart`
- `features/wallet/ui/wallet_screen.dart`
- `features/home_v16/*`

### الملفات المضافة:

- `core/domain/models/credit_tier.dart`

## المساهمة

1. إنشاء فرع جديد: `git checkout -b feature/my-feature`
2. تنفيذ التغييرات
3. تشغيل الاختبارات: `flutter test`
4. تشغيل التحليل: `flutter analyze`
5. إنشاء PR

## الدعم

للمساعدة والاستفسارات:

- GitHub Issues
- فريق التطوير

---

**SAHOOL - سهول الزراعية**
