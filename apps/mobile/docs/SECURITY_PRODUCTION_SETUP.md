# دليل إعداد الأمان للإنتاج - SAHOOL Security Production Setup

## نظرة عامة | Overview

هذا الدليل يشرح كيفية تكوين ميزات الأمان لتطبيق SAHOOL Mobile قبل النشر للإنتاج.

⚠️ **تحذير هام**: لا تنشر التطبيق للإنتاج بدون إكمال جميع الخطوات في هذا الدليل.

---

## قائمة التحقق قبل الإنتاج | Pre-Production Checklist

### 1. Certificate Pinning - تثبيت الشهادات

#### الحصول على بصمات الشهادات | Getting Certificate Fingerprints

**للحصول على بصمة SHA-256 (Android):**
```bash
# باستخدام OpenSSL
openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
openssl x509 -noout -fingerprint -sha256 | cut -d= -f2 | tr -d ':'

# أو باستخدام التطبيق في وضع التطوير
# سيطبع البصمة في سجل التصحيح
```

**للحصول على SPKI Hash (iOS):**
```bash
openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
openssl x509 -pubkey -noout | \
openssl pkey -pubin -outform der | \
openssl dgst -sha256 -binary | \
openssl enc -base64
```

#### تحديث الكود | Updating the Code

**ملف:** `lib/core/security/certificate_pinning_service.dart`

```dart
// استبدل القيم الوهمية بالقيم الحقيقية
static Map<String, List<CertificatePin>> _getDefaultPins() {
  return {
    'api.sahool.app': [
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_ACTUAL_SHA256_FINGERPRINT_HERE',  // ← استبدل هذا
        expiryDate: DateTime(2026, 12, 31),
        description: 'Production primary certificate',
      ),
      CertificatePin(
        type: PinType.sha256,
        value: 'YOUR_BACKUP_SHA256_FINGERPRINT_HERE',  // ← استبدل هذا
        expiryDate: DateTime(2027, 6, 30),
        description: 'Production backup certificate',
      ),
    ],
  };
}
```

#### تحديث iOS Info.plist

**ملف:** `ios/Runner/Info.plist`

```xml
<key>NSPinnedDomains</key>
<dict>
    <key>api.sahool.app</key>
    <dict>
        <key>NSPinnedCAIdentities</key>
        <array>
            <dict>
                <key>SPKI-SHA256-BASE64</key>
                <string>YOUR_ACTUAL_SPKI_HASH_HERE</string>
            </dict>
        </array>
    </dict>
</dict>
```

---

### 2. Security Configuration - تكوين الأمان

قم بإنشاء ملف `.env.production` مع الإعدادات التالية:

```env
# Production Security Settings
ENV=production

# تفعيل ميزات الأمان
ENABLE_CERTIFICATE_PINNING=true
ENABLE_DEVICE_INTEGRITY=true
ENABLE_BIOMETRIC_AUTH=true
ENABLE_SECURE_STORAGE=true

# تعطيل ميزات التطوير
ENABLE_DEBUG_LOGGING=false
ALLOW_INSECURE_CONNECTIONS=false
BYPASS_SSL_VERIFICATION=false
```

---

### 3. Device Integrity - سلامة الجهاز

**ملف:** `lib/core/security/device_integrity_service.dart`

تأكد من تفعيل الفحوصات التالية:

| الفحص | الحالة للإنتاج |
|-------|---------------|
| Jailbreak Detection | ✅ مُفعّل |
| Root Detection | ✅ مُفعّل |
| Emulator Detection | ✅ مُفعّل |
| Frida Detection | ✅ مُفعّل |
| Debug Mode Detection | ✅ مُفعّل |

---

### 4. Database Encryption - تشفير قاعدة البيانات

التطبيق يستخدم SQLCipher لتشفير قاعدة البيانات المحلية. تأكد من:

1. مفتاح التشفير يُخزن في Secure Storage
2. المفتاح فريد لكل جهاز
3. لا يتم تسجيل المفتاح في السجلات

```dart
// مثال على توليد مفتاح آمن
import 'dart:math';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

Future<String> getOrCreateEncryptionKey() async {
  final storage = FlutterSecureStorage();
  var key = await storage.read(key: 'db_encryption_key');

  if (key == null) {
    final random = Random.secure();
    final keyBytes = List<int>.generate(32, (_) => random.nextInt(256));
    key = base64Encode(keyBytes);
    await storage.write(key: 'db_encryption_key', value: key);
  }

  return key;
}
```

---

### 5. API Keys & Secrets - المفاتيح والأسرار

**لا تخزن المفاتيح في الكود!**

استخدم متغيرات البيئة أو خدمات إدارة الأسرار:

```dart
// ❌ خطأ - لا تفعل هذا
const apiKey = "sk-1234567890abcdef";

// ✅ صحيح - استخدم متغيرات البيئة
final apiKey = const String.fromEnvironment('API_KEY');
```

---

### 6. Build Configuration - تكوين البناء

#### Android (build.gradle)

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'

            // تعطيل التصحيح
            debuggable false
        }
    }
}
```

#### iOS (Release.xcconfig)

```
ENABLE_BITCODE = NO
VALIDATE_PRODUCT = YES
DEBUG_INFORMATION_FORMAT = dwarf
```

---

### 7. ProGuard Rules - قواعد ProGuard

**ملف:** `android/app/proguard-rules.pro`

```proguard
# حماية كود الأمان
-keep class com.sahool.app.security.** { *; }

# حماية مكتبات التشفير
-keep class org.bouncycastle.** { *; }
-keep class javax.crypto.** { *; }

# إزالة سجلات التصحيح
-assumenosideeffects class android.util.Log {
    public static int v(...);
    public static int d(...);
    public static int i(...);
}
```

---

## أوامر البناء للإنتاج | Production Build Commands

### Android

```bash
# بناء APK للإنتاج
flutter build apk --release \
  --dart-define=ENV=production \
  --dart-define=ENABLE_CERTIFICATE_PINNING=true \
  --dart-define=ENABLE_DEVICE_INTEGRITY=true

# بناء App Bundle للإنتاج
flutter build appbundle --release \
  --dart-define=ENV=production \
  --dart-define=ENABLE_CERTIFICATE_PINNING=true \
  --dart-define=ENABLE_DEVICE_INTEGRITY=true
```

### iOS

```bash
# بناء iOS للإنتاج
flutter build ios --release \
  --dart-define=ENV=production \
  --dart-define=ENABLE_CERTIFICATE_PINNING=true \
  --dart-define=ENABLE_DEVICE_INTEGRITY=true
```

---

## اختبار الأمان | Security Testing

### 1. اختبار Certificate Pinning

```bash
# استخدم mitmproxy لاختبار أن التطبيق يرفض الشهادات غير الموثوقة
mitmproxy --mode transparent

# يجب أن يفشل التطبيق في الاتصال
```

### 2. اختبار Device Integrity

```bash
# اختبر على محاكي (يجب أن يُكتشف)
# اختبر على جهاز مُخترق (يجب أن يُكتشف)
```

### 3. فحص التطبيق

```bash
# تحليل APK
apktool d app-release.apk

# البحث عن أسرار مُسربة
grep -r "api_key\|password\|secret" decoded_apk/
```

---

## الموارد | Resources

- [OWASP Mobile Security Testing Guide](https://owasp.org/www-project-mobile-security-testing-guide/)
- [Flutter Security Best Practices](https://docs.flutter.dev/security)
- [iOS App Security Guide](https://developer.apple.com/documentation/security)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)

---

## الدعم | Support

للأسئلة المتعلقة بالأمان، تواصل مع فريق الأمان:
- البريد: security@sahool.app
- Slack: #security-team
