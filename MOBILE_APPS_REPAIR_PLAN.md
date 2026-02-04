# خطة إصلاح التطبيقات المحمولة - دليل التنفيذ
# Mobile Apps Repair Plan - Implementation Guide

**مستوى الأولوية | Priority Level:** 🔴 حرج | CRITICAL  
**الوقت المقدر | Estimated Time:** 3-4 أشهر | 3-4 months  
**الموارد المطلوبة | Resources Required:** 5 مطورين | 5 developers

---

## المرحلة 1: الإصلاحات الفورية (أسبوع 1)
## Phase 1: Immediate Fixes (Week 1)

### 🎯 الهدف | Goal
إصلاح المشاكل الحرجة في sahool_field_app لجعله جاهزاً للإنتاج
Fix critical issues in sahool_field_app to make it production-ready

### ✅ المهام | Tasks

#### 1.1 إنشاء pubspec.lock (5 دقائق)
**Create pubspec.lock (5 minutes)**

```bash
cd /home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/mobile/sahool_field_app

# تثبيت الاعتماديات | Install dependencies
flutter pub get

# التحقق من الملف | Verify file created
ls -la pubspec.lock

# إضافة للـ Git | Add to Git
git add pubspec.lock
git commit -m "feat(mobile): Add pubspec.lock for dependency locking"
```

**الناتج المتوقع | Expected Output:**
- ✅ ملف pubspec.lock موجود
- ✅ جميع الاعتماديات مثبتة بإصدارات محددة

---

#### 1.2 استبدال بصمات الشهادات الوهمية (2 ساعة)
**Replace Placeholder Certificate Fingerprints (2 hours)**

**الخطوة 1 | Step 1:** الحصول على البصمات الفعلية من الخادم
**Get actual fingerprints from server**

```bash
# للحصول على بصمة شهادة الخادم | To get server certificate fingerprint
openssl s_client -servername api.sahool.com -connect api.sahool.com:443 < /dev/null 2>/dev/null | \
  openssl x509 -fingerprint -sha256 -noout -in /dev/stdin | \
  sed 's/://g' | \
  awk -F= '{print $2}' | \
  xxd -r -p | \
  openssl base64
```

**الخطوة 2 | Step 2:** تحديث الملفات

**ملف: `lib/core/security/certificate_config.dart`**

```dart
class CertificateConfig {
  // بصمات الإنتاج | Production fingerprints
  static const List<String> productionPins = [
    // ⚠️ استبدل هذه البصمات بالبصمات الفعلية من خادمك
    // ⚠️ Replace these fingerprints with actual ones from your server
    'sha256/YLh1dUR9y6Kja30RrAn7JKnbQG+uEwrcn3pJFlergPE=', // Primary
    'sha256/C5+lpZ7tcVwmwQIMcRtPbsQtWLABXhQzejna0wHFr8M=', // Backup
    'sha256/VjLZe/p3W/PJnd6lL8JVNBCGQBZynFLdZSTIqcO0SJ8=', // Tertiary
  ];
  
  static const List<String> stagingPins = [
    'sha256/[STAGING_FINGERPRINT_1]',
    'sha256/[STAGING_FINGERPRINT_2]',
  ];
}
```

**الخطوة 3 | Step 3:** التحقق من التكامل

```bash
# تشغيل الاختبارات | Run tests
flutter test test/core/security/

# بناء التطبيق | Build app
flutter build apk --release
```

**المدة | Duration:** 2 ساعة  
**المسؤول | Responsible:** مطور الأمان | Security Developer

---

#### 1.3 تفعيل Certificate Pinning في API Client (2 ساعة)
**Enable Certificate Pinning in API Client (2 hours)**

**ملف: `lib/core/http/api_client.dart`**

```dart
import 'package:dio/dio.dart';
import 'package:sahool_field_app/core/security/certificate_pinning_service.dart';
import 'package:sahool_field_app/core/config/config.dart';

class ApiClient {
  late final Dio _dio;
  final CertificatePinningService _certPinning;
  
  ApiClient() : _certPinning = CertificatePinningService() {
    _dio = Dio(BaseOptions(
      baseUrl: Config.apiBaseUrl,
      connectTimeout: Duration(seconds: 30),
      receiveTimeout: Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));
    
    // ✅ إضافة تثبيت الشهادات | Add certificate pinning
    _dio.interceptors.add(_certPinning.createInterceptor());
    
    // إضافة interceptors أخرى | Add other interceptors
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
  }
  
  // مناهج API | API methods
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return _dio.get(path, queryParameters: queryParameters);
  }
  
  Future<Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }
}
```

**الاختبار | Testing:**

```dart
// test/core/http/api_client_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/http/api_client.dart';

void main() {
  group('ApiClient Certificate Pinning', () {
    test('Should reject invalid certificates', () async {
      final client = ApiClient();
      
      // محاولة الاتصال بخادم وهمي | Try to connect to fake server
      expect(
        () => client.get('https://fake-server.com/api'),
        throwsA(isA<DioException>()),
      );
    });
    
    test('Should accept valid certificates', () async {
      final client = ApiClient();
      
      // الاتصال بخادم حقيقي | Connect to real server
      final response = await client.get('/health');
      expect(response.statusCode, 200);
    });
  });
}
```

**المدة | Duration:** 2 ساعة  
**المسؤول | Responsible:** مطور Backend | Backend Developer

---

#### 1.4 تحديث ProGuard Rules (1 ساعة)
**Update ProGuard Rules (1 hour)**

**ملف: `android/app/proguard-rules.pro`**

```proguard
# إضافة في نهاية الملف | Add at the end of file

#========================================
# قواعد SAHOOL المخصصة | SAHOOL Custom Rules
#========================================

# SQLCipher - قاعدة البيانات المشفرة | Encrypted Database
-keep class net.sqlcipher.** { *; }
-keep class net.sqlcipher.database.** { *; }
-keepclassmembers class net.sqlcipher.database.SQLiteDatabase {
    public <methods>;
}

# Drift ORM
-keep class drift.** { *; }
-keep class com.simolus.drift.** { *; }
-keepclassmembers class * extends drift.GeneratedDatabase {
    *;
}
-keepclassmembers @drift.DriftTable class * {
    *;
}

# Flutter Local Notifications
-keep class com.dexterous.** { *; }
-keep class androidx.core.app.NotificationCompat** { *; }
-dontwarn com.dexterous.**

# Mobile Scanner (QR/Barcode)
-keep class dev.steenbakker.mobile_scanner.** { *; }
-keep class com.google.zxing.** { *; }
-keep class com.google.mlkit.** { *; }
-dontwarn com.google.zxing.**

# Riverpod State Management
-keep class com.riverpod.** { *; }
-keepclassmembers class * {
    @riverpod_annotation.riverpod *;
}

# Dio HTTP Client
-keep class io.flutter.plugins.** { *; }
-keep class com.sahool.sahool_field_app.MainActivity { *; }

# Geolocator
-keep class com.baseflow.geolocator.** { *; }
-keep class com.google.android.gms.location.** { *; }

# Camera
-keep class io.flutter.plugins.camera.** { *; }
-dontwarn io.flutter.plugins.camera.**

# Image Picker
-keep class io.flutter.plugins.imagepicker.** { *; }

# Shared Preferences
-keep class io.flutter.plugins.sharedpreferences.** { *; }

# Flutter Secure Storage
-keep class com.it_nomads.fluttersecurestorage.** { *; }

# Local Auth (Biometric)
-keep class io.flutter.plugins.localauth.** { *; }

# Safe Device (Root Detection)
-keep class com.jhomlala.** { *; }

# Connectivity Plus
-keep class dev.fluttercommunity.plus.connectivity.** { *; }

# Package Info Plus
-keep class dev.fluttercommunity.plus.packageinfo.** { *; }

# Device Info Plus
-keep class dev.fluttercommunity.plus.device_info.** { *; }

#========================================
# إعدادات عامة للفلاتر | General Flutter Settings
#========================================

# Flutter Engine
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Kotlin
-keep class kotlin.** { *; }
-keep class kotlin.Metadata { *; }
-dontwarn kotlin.**
-keepclassmembers class **$WhenMappings {
    <fields>;
}

# Gson (if used)
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.google.gson.** { *; }

# نهاية القواعد | End of Rules
```

**التحقق | Verification:**

```bash
cd android

# بناء Release APK | Build Release APK
./gradlew assembleRelease

# التحقق من عدم وجود أخطاء | Check for no errors
./gradlew assembleRelease --stacktrace

# اختبار التطبيق | Test app
adb install -r app/build/outputs/apk/release/app-release.apk
```

**المدة | Duration:** 1 ساعة  
**المسؤول | Responsible:** مطور Android | Android Developer

---

#### 1.5 تكوين أذونات iOS (2 ساعة)
**Configure iOS Permissions (2 hours)**

**ملف: `ios/Runner/Info.plist`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- ✅ إضافة الأذونات التالية | Add the following permissions -->
    
    <!-- الكاميرا | Camera -->
    <key>NSCameraUsageDescription</key>
    <string>نحتاج الكاميرا لتصوير الحقول والمحاصيل والآفات لمساعدتك في إدارة المزرعة</string>
    <key>NSCameraUsageDescription_ar</key>
    <string>نحتاج الكاميرا لتصوير الحقول والمحاصيل</string>
    
    <!-- الموقع | Location -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>نحتاج موقعك لتحديد مكان الحقل بدقة وتوفير معلومات الطقس المحلية</string>
    <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
    <string>نحتاج موقعك لتتبع الحقول حتى في الخلفية</string>
    <key>NSLocationAlwaysUsageDescription</key>
    <string>نحتاج موقعك دائماً لمراقبة الحقول</string>
    
    <!-- الميكروفون | Microphone -->
    <key>NSMicrophoneUsageDescription</key>
    <string>نحتاج الميكروفون لتسجيل الملاحظات الصوتية عن الحقل</string>
    
    <!-- معرض الصور | Photo Library -->
    <key>NSPhotoLibraryUsageDescription</key>
    <string>نحتاج الوصول لمعرض الصور لحفظ وتحميل صور الحقول</string>
    <key>NSPhotoLibraryAddUsageDescription</key>
    <string>نحتاج حفظ صور الحقول في معرض الصور</string>
    
    <!-- Face ID / Touch ID -->
    <key>NSFaceIDUsageDescription</key>
    <string>نستخدم Face ID للمصادقة الآمنة وحماية بياناتك الزراعية</string>
    
    <!-- الحركة والنشاط | Motion & Activity -->
    <key>NSMotionUsageDescription</key>
    <string>نحتاج بيانات الحركة لتحسين دقة الموقع في الحقل</string>
    
    <!-- الملفات المحلية | Local Files -->
    <key>UIFileSharingEnabled</key>
    <true/>
    <key>LSSupportsOpeningDocumentsInPlace</key>
    <true/>
    
    <!-- تكوينات أخرى | Other Configurations -->
    <key>CFBundleDisplayName</key>
    <string>SAHOOL</string>
    <key>CFBundleName</key>
    <string>SAHOOL Field App</string>
</dict>
</plist>
```

**ملف: `ios/Runner/Runner.entitlements`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Keychain Access Groups -->
    <key>keychain-access-groups</key>
    <array>
        <string>$(AppIdentifierPrefix)com.sahool.fieldapp</string>
    </array>
    
    <!-- Network Extensions -->
    <key>com.apple.developer.networking.wifi-info</key>
    <true/>
    
    <!-- Background Modes -->
    <key>com.apple.developer.background-modes</key>
    <array>
        <string>fetch</string>
        <string>location</string>
        <string>processing</string>
    </array>
    
    <!-- Data Protection -->
    <key>com.apple.developer.default-data-protection</key>
    <string>NSFileProtectionComplete</string>
</dict>
</plist>
```

**التحقق | Verification:**

```bash
cd ios

# تثبيت CocoaPods | Install CocoaPods
pod install

# فتح Xcode | Open Xcode
open Runner.xcworkspace

# بناء المشروع | Build project
xcodebuild -workspace Runner.xcworkspace -scheme Runner -sdk iphoneos -configuration Release build
```

**المدة | Duration:** 2 ساعة  
**المسؤول | Responsible:** مطور iOS | iOS Developer

---

### 📊 ملخص المرحلة 1 | Phase 1 Summary

**الوقت الإجمالي | Total Time:** 7.5 ساعة  
**الموارد | Resources:** 3 مطورين (Android, iOS, Security)  
**النتائج | Deliverables:**
- ✅ pubspec.lock مثبت
- ✅ Certificate pinning مفعّل
- ✅ ProGuard rules محدثة
- ✅ iOS permissions مكوّنة
- ✅ sahool_field_app جاهز للإنتاج بنسبة 85%

---

## المرحلة 2: تحسينات sahool_field_app (أسبوع 2)
## Phase 2: sahool_field_app Improvements (Week 2)

### ✅ المهام | Tasks

#### 2.1 إضافة خدمة الإشعارات البديلة (يومين)
**Add Alternative Push Notification Service (2 days)**

**الخيار الموصى به: OneSignal**

```yaml
# pubspec.yaml
dependencies:
  onesignal_flutter: ^5.2.5
```

```dart
// lib/core/notifications/onesignal_service.dart
import 'package:onesignal_flutter/onesignal_flutter.dart';
import 'package:sahool_field_app/core/config/config.dart';

class OneSignalNotificationService {
  static Future<void> initialize() async {
    // تفعيل وضع التطوير | Enable development mode
    OneSignal.Debug.setLogLevel(OSLogLevel.verbose);
    
    // تهيئة OneSignal | Initialize OneSignal
    OneSignal.initialize(Config.oneSignalAppId);
    
    // طلب إذن الإشعارات | Request notification permission
    final permission = await OneSignal.Notifications.requestPermission(true);
    
    if (permission) {
      print('✅ تم منح إذن الإشعارات | Notification permission granted');
    }
    
    // الاستماع للإشعارات | Listen to notifications
    OneSignal.Notifications.addForegroundWillDisplayListener((event) {
      print('📬 إشعار جديد: ${event.notification.title}');
      event.preventDefault();
      event.notification.display();
    });
    
    OneSignal.Notifications.addClickListener((event) {
      print('👆 تم النقر على الإشعار');
      _handleNotificationClick(event.notification);
    });
  }
  
  static void _handleNotificationClick(OSNotification notification) {
    final data = notification.additionalData;
    if (data != null) {
      // التنقل حسب نوع الإشعار | Navigate based on notification type
      if (data['type'] == 'field_alert') {
        // navigateTo('/field/${data['field_id']}');
      } else if (data['type'] == 'irrigation_reminder') {
        // navigateTo('/irrigation');
      }
    }
  }
  
  /// تعيين معرف المستخدم | Set user ID
  static Future<void> setUserId(String userId) async {
    await OneSignal.login(userId);
  }
  
  /// إزالة المستخدم | Remove user
  static Future<void> removeUser() async {
    await OneSignal.logout();
  }
  
  /// إرسال تاغ | Send tag
  static Future<void> sendTag(String key, String value) async {
    await OneSignal.User.addTagWithKey(key, value);
  }
}
```

```dart
// lib/main.dart - التهيئة | Initialization
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // تهيئة OneSignal | Initialize OneSignal
  await OneSignalNotificationService.initialize();
  
  runApp(MyApp());
}
```

**Android Configuration:**

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest>
    <application>
        <!-- إضافة معرف OneSignal | Add OneSignal app ID -->
        <meta-data
            android:name="onesignal_app_id"
            android:value="${ONESIGNAL_APP_ID}" />
    </application>
</manifest>
```

**iOS Configuration:**

```xml
<!-- ios/Runner/Info.plist -->
<key>OneSignalAppID</key>
<string>${ONESIGNAL_APP_ID}</string>
```

**المدة | Duration:** يومان  
**المسؤول | Responsible:** مطور Full Stack

---

#### 2.2 تطبيق ضغط الصور WebP (يومان)
**Implement WebP Image Compression (2 days)**

```yaml
# pubspec.yaml
dependencies:
  image: ^4.2.0
```

```dart
// lib/core/utils/image_compressor.dart
import 'dart:io';
import 'package:image/image.dart' as img;
import 'package:path/path.dart' as path;

class ImageCompressor {
  /// ضغط صورة واحدة | Compress single image
  static Future<File> compressToWebP({
    required File imageFile,
    int quality = 85,
    int? maxWidth,
    int? maxHeight,
  }) async {
    try {
      // قراءة الملف | Read file
      final bytes = await imageFile.readAsBytes();
      
      // فك تشفير الصورة | Decode image
      final image = img.decodeImage(bytes);
      if (image == null) {
        throw Exception('فشل فك تشفير الصورة | Failed to decode image');
      }
      
      // تغيير الحجم إذا لزم الأمر | Resize if needed
      img.Image resized = image;
      if (maxWidth != null || maxHeight != null) {
        resized = img.copyResize(
          image,
          width: maxWidth,
          height: maxHeight,
          interpolation: img.Interpolation.linear,
        );
      }
      
      // ضغط إلى WebP | Compress to WebP
      final webpBytes = img.encodeWebP(resized, quality: quality);
      
      // حفظ الملف | Save file
      final directory = path.dirname(imageFile.path);
      final fileName = path.basenameWithoutExtension(imageFile.path);
      final compressedFile = File('$directory/$fileName.webp');
      await compressedFile.writeAsBytes(webpBytes);
      
      // حذف الملف الأصلي | Delete original file
      await imageFile.delete();
      
      return compressedFile;
    } catch (e) {
      throw Exception('فشل ضغط الصورة: $e | Image compression failed: $e');
    }
  }
  
  /// ضغط عدة صور | Compress multiple images
  static Future<List<File>> compressBatch(
    List<File> images, {
    int quality = 85,
  }) async {
    final compressed = <File>[];
    
    for (final image in images) {
      try {
        final result = await compressToWebP(
          imageFile: image,
          quality: quality,
          maxWidth: 1920,
        );
        compressed.add(result);
      } catch (e) {
        print('⚠️ فشل ضغط ${image.path}: $e');
      }
    }
    
    return compressed;
  }
  
  /// حساب نسبة التوفير | Calculate savings
  static Future<CompressionStats> getStats({
    required File original,
    required File compressed,
  }) async {
    final originalSize = await original.length();
    final compressedSize = await compressed.length();
    final savedBytes = originalSize - compressedSize;
    final savedPercent = ((savedBytes / originalSize) * 100).round();
    
    return CompressionStats(
      originalSize: originalSize,
      compressedSize: compressedSize,
      savedBytes: savedBytes,
      savedPercent: savedPercent,
    );
  }
}

class CompressionStats {
  final int originalSize;
  final int compressedSize;
  final int savedBytes;
  final int savedPercent;
  
  CompressionStats({
    required this.originalSize,
    required this.compressedSize,
    required this.savedBytes,
    required this.savedPercent,
  });
  
  @override
  String toString() {
    return 'الأصلي: ${(originalSize / 1024).round()} KB, '
           'المضغوط: ${(compressedSize / 1024).round()} KB, '
           'التوفير: $savedPercent%';
  }
}
```

**الاستخدام | Usage:**

```dart
// في أي مكان تلتقط فيه صورة | Wherever you capture images
import 'package:image_picker/image_picker.dart';
import 'package:sahool_field_app/core/utils/image_compressor.dart';

class FieldPhotoService {
  final ImagePicker _picker = ImagePicker();
  
  Future<File?> captureAndCompressPhoto() async {
    try {
      // التقاط الصورة | Capture photo
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 95,
      );
      
      if (photo == null) return null;
      
      // ضغط الصورة | Compress image
      final compressed = await ImageCompressor.compressToWebP(
        imageFile: File(photo.path),
        quality: 85,
        maxWidth: 1920,
      );
      
      // عرض الإحصائيات | Show stats
      final stats = await ImageCompressor.getStats(
        original: File(photo.path),
        compressed: compressed,
      );
      print('📊 إحصائيات الضغط: $stats');
      
      return compressed;
    } catch (e) {
      print('❌ خطأ في التقاط الصورة: $e');
      return null;
    }
  }
}
```

**المدة | Duration:** يومان  
**المسؤول | Responsible:** مطور Flutter

---

#### 2.3 تطبيق فلترة PII بشكل شامل (يوم واحد)
**Implement Comprehensive PII Filtering (1 day)**

```dart
// lib/core/logging/logger.dart
import 'package:sahool_field_app/core/utils/pii_filter.dart';

class AppLogger {
  static void info(String message, {Map<String, dynamic>? data}) {
    _log('INFO', message, data);
  }
  
  static void error(String message, {Object? error, StackTrace? stackTrace, Map<String, dynamic>? data}) {
    _log('ERROR', message, data, error: error, stackTrace: stackTrace);
  }
  
  static void warning(String message, {Map<String, dynamic>? data}) {
    _log('WARNING', message, data);
  }
  
  static void debug(String message, {Map<String, dynamic>? data}) {
    _log('DEBUG', message, data);
  }
  
  static void _log(
    String level,
    String message,
    Map<String, dynamic>? data, {
    Object? error,
    StackTrace? stackTrace,
  }) {
    // تصفية PII تلقائياً | Auto-filter PII
    final filteredMessage = PIIFilter.filterMessage(message);
    final filteredData = data != null ? PIIFilter.filterMap(data) : null;
    
    // تنسيق الرسالة | Format message
    final timestamp = DateTime.now().toIso8601String();
    final logEntry = '[$timestamp] [$level] $filteredMessage';
    
    // طباعة | Print
    print(logEntry);
    if (filteredData != null && filteredData.isNotEmpty) {
      print('  Data: $filteredData');
    }
    if (error != null) {
      print('  Error: $error');
    }
    if (stackTrace != null) {
      print('  StackTrace: $stackTrace');
    }
  }
}
```

**تطبيق في Error Handler:**

```dart
// lib/core/error/error_handler.dart
import 'package:sahool_field_app/core/logging/logger.dart';

class ErrorHandler {
  static Future<void> handleError(Object error, StackTrace stackTrace) async {
    // تسجيل الخطأ مع فلترة PII | Log error with PII filtering
    AppLogger.error(
      'حدث خطأ في التطبيق | Application error occurred',
      error: error,
      stackTrace: stackTrace,
      data: {
        'error_type': error.runtimeType.toString(),
        'timestamp': DateTime.now().toIso8601String(),
      },
    );
    
    // إرسال للخدمة السحابية | Send to cloud service
    // await CrashReportingService.report(error, stackTrace);
  }
}
```

**المدة | Duration:** يوم واحد  
**المسؤول | Responsible:** مطور الأمان

---

### 📊 ملخص المرحلة 2 | Phase 2 Summary

**الوقت الإجمالي | Total Time:** 5 أيام  
**الموارد | Resources:** 2 مطورين  
**النتائج | Deliverables:**
- ✅ OneSignal notifications مطبّق
- ✅ WebP compression مطبّق
- ✅ PII filtering شامل
- ✅ sahool_field_app جاهز 95%

---

## المرحلة 3: sahol_atmosphere - البنية الأساسية (أسبوع 3-4)
## Phase 3: sahol_atmosphere - Core Infrastructure (Week 3-4)

### ✅ المهام الحرجة | Critical Tasks

#### 3.1 إضافة طبقة قاعدة البيانات (4 أيام)
**Add Database Layer (4 days)**

#### 3.2 نظام المصادقة (6 أيام)
**Authentication System (6 days)**

#### 3.3 تطبيق الشاشات الأساسية (10 أيام)
**Implement Core Screens (10 days)**

[التفاصيل الكاملة متوفرة في التقرير الرئيسي]
[Full details available in main report]

---

## المرحلة 4: sahool-mobile - التهيئة والتطوير (أسبوع 5-8)
## Phase 4: sahool-mobile - Setup & Development (Week 5-8)

### ✅ المهام الحرجة | Critical Tasks

#### 4.1 تهيئة React Native (يوم واحد)
**Initialize React Native (1 day)**

#### 4.2 إضافة الاعتماديات (يوم واحد)
**Add Dependencies (1 day)**

#### 4.3 نظام التنقل (يومان)
**Navigation System (2 days)**

#### 4.4 واجهة المستخدم (أسبوع واحد)
**User Interface (1 week)**

[التفاصيل الكاملة متوفرة في التقرير الرئيسي]
[Full details available in main report]

---

## قائمة التحقق الشاملة | Comprehensive Checklist

### sahool_field_app ✅
- [x] تحليل المشاكل
- [ ] pubspec.lock
- [ ] Certificate pinning
- [ ] ProGuard rules
- [ ] iOS permissions
- [ ] Push notifications
- [ ] WebP compression
- [ ] PII filtering
- [ ] E2E tests

### sahol_atmosphere 🔄
- [x] تحليل المشاكل
- [ ] Database layer
- [ ] Authentication
- [ ] Core screens
- [ ] HTTP client
- [ ] Navigation
- [ ] Custom fonts
- [ ] Tests
- [ ] Security review

### sahool-mobile 🔄
- [x] تحليل المشاكل
- [ ] Platform folders
- [ ] Dependencies
- [ ] Navigation
- [ ] UI screens
- [ ] SyncManager integration
- [ ] Database
- [ ] Authentication
- [ ] Tests

---

## الموارد المطلوبة | Required Resources

### الفريق | Team
- 2 مطور Flutter
- 1 مطور React Native
- 1 مطور Android Native
- 1 مطور iOS Native
- 1 مختبر QA
- 1 مدير مشروع

### الأدوات | Tools
- Flutter SDK 3.27.x
- Android Studio
- Xcode
- VS Code
- Git
- OneSignal Account
- Testing Devices

---

**نهاية خطة الإصلاح | End of Repair Plan**
