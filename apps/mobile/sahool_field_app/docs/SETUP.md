# SAHOOL Field App Setup Guide
# دليل إعداد تطبيق سهول الميداني

**Version:** 16.0.0  
**Last Updated:** 2026-02-11

---

## Prerequisites | المتطلبات المسبقة

### Required Software
- Flutter 3.27.x or higher
- Dart SDK 3.2.0 or higher
- Android Studio / Xcode
- Git

### Verify Installation
```bash
flutter --version
dart --version
```

---

## Initial Setup | الإعداد الأولي

### 1. Clone Repository
```bash
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp/apps/mobile/sahool_field_app
```

### 2. Install Dependencies
```bash
# This will create pubspec.lock file with locked dependency versions
flutter pub get
```

**IMPORTANT:** The `pubspec.lock` file must be committed to version control to ensure consistent dependency versions across all environments.

**هام:** يجب إضافة ملف `pubspec.lock` إلى نظام التحكم بالإصدارات لضمان إصدارات متسقة للاعتماديات عبر جميع البيئات.

### 3. Generate Build Files
```bash
# Generate Drift database code
dart run build_runner build --delete-conflicting-outputs

# Generate Riverpod providers
dart run build_runner build
```

### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env.development

# Edit .env.development with your settings
# Required: API_BASE_URL, JWT_SECRET_KEY
```

---

## Building the App | بناء التطبيق

### Debug Build (Android)
```bash
flutter build apk --debug
```

### Release Build (Android)
```bash
# Requires signing configuration in android/app/build.gradle
flutter build apk --release

# With ProGuard enabled (recommended for production)
flutter build apk --release --obfuscate --split-debug-info=build/app/outputs/symbols
```

### iOS Build
```bash
flutter build ios --release
```

---

## Running Tests | تشغيل الاختبارات

### Unit Tests
```bash
flutter test
```

### Integration Tests
```bash
flutter test integration_test/
```

### Widget Tests
```bash
flutter test test/widgets/
```

---

## Common Issues | المشاكل الشائعة

### Issue: Missing pubspec.lock
**Problem:** Dependencies not consistent across environments  
**Solution:**
```bash
flutter pub get
git add pubspec.lock
git commit -m "Add pubspec.lock for dependency locking"
```

### Issue: Build fails in Release mode
**Problem:** ProGuard rules missing for plugins  
**Solution:** Verify `android/app/proguard-rules.pro` includes all plugin rules

### Issue: Certificate pinning fails
**Problem:** Using placeholder certificate fingerprints  
**Solution:** Replace with actual production certificates in `lib/core/security/certificate_config.dart`

---

## Mobile Sync Setup | إعداد المزامنة المحمولة

### Network Timeouts
Mobile sync uses extended timeouts for rural/low-connectivity areas:

```dart
NetworkConfig.forMobileSync()
// Connect: 60s, Send: 90s, Receive: 90s
```

### Sync Engine Configuration
```dart
final syncEngine = SyncEngine(database: database);
syncEngine.startPeriodic(); // Syncs every 15 minutes
```

For detailed sync API contract, see [MOBILE_SYNC_API.md](MOBILE_SYNC_API.md)

---

## Security Checklist | قائمة التحقق الأمنية

- [ ] Certificate pinning enabled with real fingerprints
- [ ] ProGuard rules complete for all plugins
- [ ] SQLCipher enabled for encrypted database
- [ ] Biometric authentication configured
- [ ] Request signing enabled for sensitive endpoints
- [ ] TLS 1.2+ enforced

---

## References | المراجع

- [Flutter Documentation](https://flutter.dev/docs)
- [Drift ORM](https://drift.simonbinder.eu/)
- [Riverpod State Management](https://riverpod.dev/)
- [Mobile Sync API](MOBILE_SYNC_API.md)

---

**Support:** mobile-team@sahool.app  
**Documentation:** https://docs.sahool.app/mobile
