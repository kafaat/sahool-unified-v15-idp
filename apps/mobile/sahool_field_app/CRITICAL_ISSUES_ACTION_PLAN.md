# خطة العمل لإصلاح المشاكل الحرجة المتبقية
# Action Plan for Remaining Critical Issues

**التطبيق | Application:** SAHOOL Field App  
**تاريخ الإنشاء | Created:** 2026-02-17  
**الحالة | Status:** 🔴 يتطلب عمل فوري | REQUIRES IMMEDIATE ACTION  

---

## 📋 ملخص المشاكل الحرجة | Critical Issues Summary

| # | المشكلة | Issue | الأولوية | Priority | الحالة | Status |
|---|---------|-------|----------|----------|--------|--------|
| 1 | شهادات التثبيت الوهمية | Placeholder Certificate Pins | P0 | P0 | ⚠️ يتطلب إجراء | Requires Action |
| 2 | عناوين API المشفرة | Hardcoded API URLs | P0 | P0 | ⚠️ يتطلب إجراء | Requires Action |
| 3 | الأصول المفقودة | Missing Assets | P1 | P1 | ⚠️ يتطلب إجراء | Requires Action |

---

## 🔴 المشكلة #1: شهادات التثبيت الوهمية
## Critical Issue #1: Placeholder Certificate Pins

### التفاصيل | Details

**الملف | File:** `lib/core/security/certificate_config.dart`  
**الخطورة | Severity:** 🔴 حرج - يمنع الإطلاق الإنتاجي | CRITICAL - Blocks Production Release  

### الوضع الحالي | Current State

```dart
// lib/core/security/certificate_config.dart
class CertificateConfig {
  // TODO: CRITICAL - Replace with actual production certificate fingerprint
  static const String productionApiCert = 
    '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877';
  
  // TODO: CRITICAL - Replace with actual staging certificate fingerprint  
  static const String stagingApiCert =
    '2e51707gc303g06d66db96efce8d8eg4408g271d9835741043de87ged0ageg988';
    
  // TODO: REPLACE with backup certificate fingerprint for rotation
  static const String backupApiCert =
    '3f62818hd414h17e77ec07fgdf9e9fh5519h382e0946852154ef98hfe1bghfh099';
}
```

### المخاطر | Risks

1. **هجمات MITM** | Man-in-the-Middle attacks
   - التطبيق يقبل أي شهادة TLS | App accepts any TLS certificate
   - يمكن اعتراض البيانات الحساسة | Sensitive data can be intercepted
   - معلومات المزارعين معرضة للخطر | Farmer information at risk

2. **عدم الامتثال الأمني** | Security Compliance Failure
   - فشل اختبارات الأمان | Security tests will fail
   - لا يتوافق مع OWASP Mobile | Not OWASP Mobile compliant

### الحل | Solution

#### الخطوة 1: الحصول على البصمات الحقيقية | Step 1: Get Real Fingerprints

```bash
#!/bin/bash
# get_cert_fingerprints.sh

# Production API Certificate
echo "=== Production API Certificate ==="
openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | \
  cut -d'=' -f2 | \
  tr -d ':' | \
  tr '[:upper:]' '[:lower:]'

# Production WebSocket Certificate  
echo -e "\n=== Production WebSocket Certificate ==="
openssl s_client -connect ws.sahool.app:443 -servername ws.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | \
  cut -d'=' -f2 | \
  tr -d ':' | \
  tr '[:upper:]' '[:lower:]'

# Staging API Certificate
echo -e "\n=== Staging API Certificate ==="
openssl s_client -connect api.staging.sahool.app:443 -servername api.staging.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | \
  cut -d'=' -f2 | \
  tr -d ':' | \
  tr '[:upper:]' '[:lower:]'

# Staging WebSocket Certificate
echo -e "\n=== Staging WebSocket Certificate ==="
openssl s_client -connect ws.staging.sahool.app:443 -servername ws.staging.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | \
  cut -d'=' -f2 | \
  tr -d ':' | \
  tr '[:upper:]' '[:lower:]'

# Backup Certificate (if different)
echo -e "\n=== Backup Certificate (if configured) ==="
openssl s_client -connect api-backup.sahool.app:443 -servername api-backup.sahool.app < /dev/null 2>/dev/null | \
  openssl x509 -noout -fingerprint -sha256 | \
  cut -d'=' -f2 | \
  tr -d ':' | \
  tr '[:upper:]' '[:lower:]'
```

#### الخطوة 2: تحديث التكوين | Step 2: Update Configuration

```dart
// lib/core/security/certificate_config.dart
class CertificateConfig {
  // Production Certificates - REPLACE WITH ACTUAL VALUES FROM STEP 1
  static const String productionApiCert = 
    'ACTUAL_PRODUCTION_API_SHA256_FINGERPRINT_HERE';
  
  static const String productionWsCert =
    'ACTUAL_PRODUCTION_WS_SHA256_FINGERPRINT_HERE';
    
  // Staging Certificates
  static const String stagingApiCert =
    'ACTUAL_STAGING_API_SHA256_FINGERPRINT_HERE';
    
  static const String stagingWsCert =
    'ACTUAL_STAGING_WS_SHA256_FINGERPRINT_HERE';
    
  // Backup Certificate (for rotation)
  static const String backupApiCert =
    'ACTUAL_BACKUP_SHA256_FINGERPRINT_HERE';
    
  // Development Certificates (self-signed accepted)
  static const String developmentApiCert = '';
  static const String developmentWsCert = '';
  
  // Get certificates for current environment
  static List<String> getApiCertificates(String environment) {
    switch (environment) {
      case 'production':
        return [productionApiCert, backupApiCert];
      case 'staging':
        return [stagingApiCert];
      case 'development':
      default:
        return []; // Allow any certificate in development
    }
  }
  
  static List<String> getWsCertificates(String environment) {
    switch (environment) {
      case 'production':
        return [productionWsCert, backupApiCert];
      case 'staging':
        return [stagingWsCert];
      case 'development':
      default:
        return []; // Allow any certificate in development
    }
  }
}
```

#### الخطوة 3: الاختبار | Step 3: Testing

```bash
# Test certificate pinning in staging
flutter run --release --dart-define=ENVIRONMENT=staging

# Test certificate pinning in production (with test backend)
flutter run --release --dart-define=ENVIRONMENT=production
```

### الجدول الزمني | Timeline

- **الوقت المطلوب | Time Required:** 2-4 ساعات | 2-4 hours
- **الموعد النهائي | Deadline:** قبل أي إطلاق إنتاجي | Before any production release
- **المسؤول | Responsible:** فريق DevOps + فريق الأمان | DevOps Team + Security Team

---

## 🔴 المشكلة #2: عناوين API المشفرة
## Critical Issue #2: Hardcoded API URLs

### التفاصيل | Details

**الملف | File:** `lib/core/config/config.dart`  
**الخطورة | Severity:** 🔴 حرج - لن يعمل في الإنتاج | CRITICAL - Won't work in production  

### الوضع الحالي | Current State

```dart
// lib/core/config/config.dart
@deprecated Use EnvConfig instead for environment-specific configuration
class AppConfig {
  static const String apiBaseUrl = 'http://192.168.8.205:8000/api/v1';
  static const String wsBaseUrl = 'ws://192.168.8.205:8081';
  // ... more hardcoded values
}
```

### المشاكل | Problems

1. عنوان IP محلي للتطوير | Local development IP address
2. لن يعمل خارج الشبكة المحلية | Won't work outside local network
3. لا دعم لبيئات متعددة | No multi-environment support
4. ملف مهمل لكنه لا يزال مستخدماً | Deprecated file still in use

### الحل | Solution

#### الخطوة 1: حذف الملف المهمل | Step 1: Delete Deprecated File

```bash
# Find all usages first
grep -r "AppConfig\." lib/ --include="*.dart" > /tmp/appconfig_usage.txt

# Review the output
cat /tmp/appconfig_usage.txt

# After confirming all usages are migrated, delete
rm lib/core/config/config.dart
```

#### الخطوة 2: التأكد من EnvConfig | Step 2: Verify EnvConfig

```dart
// lib/core/config/env_config.dart should have:
class EnvConfig {
  static String get apiBaseUrl {
    return dotenv.env['API_BASE_URL'] ?? _defaultApiUrl;
  }
  
  static String get wsBaseUrl {
    return dotenv.env['WS_BASE_URL'] ?? _defaultWsUrl;
  }
  
  // Default URLs based on environment
  static String get _defaultApiUrl {
    switch (environment) {
      case 'production':
        return 'https://api.sahool.app/api/v1';
      case 'staging':
        return 'https://api.staging.sahool.app/api/v1';
      case 'development':
      default:
        return 'http://localhost:8000/api/v1';
    }
  }
  
  static String get _defaultWsUrl {
    switch (environment) {
      case 'production':
        return 'wss://ws.sahool.app';
      case 'staging':
        return 'wss://ws.staging.sahool.app';
      case 'development':
      default:
        return 'ws://localhost:8081';
    }
  }
  
  static String get environment {
    return dotenv.env['ENVIRONMENT'] ?? 'development';
  }
}
```

#### الخطوة 3: إنشاء ملفات البيئة | Step 3: Create Environment Files

```bash
# .env.production
ENVIRONMENT=production
API_BASE_URL=https://api.sahool.app/api/v1
WS_BASE_URL=wss://ws.sahool.app

# .env.staging  
ENVIRONMENT=staging
API_BASE_URL=https://api.staging.sahool.app/api/v1
WS_BASE_URL=wss://ws.staging.sahool.app

# .env.development
ENVIRONMENT=development
API_BASE_URL=http://localhost:8000/api/v1
WS_BASE_URL=ws://localhost:8081
```

#### الخطوة 4: تحديث جميع الاستخدامات | Step 4: Update All Usages

```bash
# Find and replace all AppConfig usages
find lib/ -name "*.dart" -exec sed -i 's/AppConfig\./EnvConfig./g' {} +

# Verify changes
grep -r "AppConfig\." lib/ --include="*.dart"
# Should return no results
```

### الجدول الزمني | Timeline

- **الوقت المطلوب | Time Required:** 1-2 ساعات | 1-2 hours
- **الموعد النهائي | Deadline:** قبل أي إطلاق | Before any release
- **المسؤول | Responsible:** فريق التطوير | Development Team

---

## 🟡 المشكلة #3: الأصول المفقودة
## Issue #3: Missing Assets

### التفاصيل | Details

**الأولوية | Priority:** P1 - يؤثر على UX | P1 - Affects UX  
**الملفات المطلوبة | Required Files:** 5 صور | 5 images

### القائمة | List

| الملف | File | الاستخدام | Usage | الحل المؤقت | Temporary Fix |
|-------|------|-----------|-------|--------------|---------------|
| `assets/images/sahool_logo.png` | Logo | Profile screen | ✅ Icon fallback exists |
| `assets/avatars/farmer1.png` | Avatar | Community posts | ✅ Icon fallback exists |
| `assets/avatars/farmer2.png` | Avatar | Community posts | ✅ Icon fallback exists |
| `assets/avatars/expert1.png` | Avatar | Expert replies | ✅ Icon fallback exists |
| `assets/avatars/expert2.png` | Avatar | Expert replies | ✅ Icon fallback exists |

### الحالة | Status

✅ **البدائل موجودة** | Fallbacks exist: جميع الشاشات لديها Icon fallback | All screens have Icon fallback  
⚠️ **التحسين مطلوب** | Improvement needed: يجب إنشاء صور مخصصة | Custom images should be created

### الحل | Solution

#### الخيار 1: إنشاء صور مخصصة | Option 1: Create Custom Images

1. تصميم شعار SAHOOL (512x512 px)
2. تصميم 4 أفاتار افتراضية (128x128 px)
3. تصدير بصيغة PNG مع شفافية
4. تحسين الحجم (< 500 KB للشعار، < 50 KB للأفاتار)

#### الخيار 2: استخدام أيقونات دائمة | Option 2: Use Permanent Icons

```dart
// Update code to use Material Icons permanently
CircleAvatar(
  backgroundColor: Color(0xFF4CAF50),
  child: Icon(Icons.person, color: Colors.white),
)
```

### الجدول الزمني | Timeline

- **الوقت المطلوب | Time Required:** 1-3 أيام (حسب التصميم) | 1-3 days (depending on design)
- **الموعد النهائي | Deadline:** قبل الإطلاق النهائي | Before final release
- **المسؤول | Responsible:** فريق التصميم | Design Team

---

## 📝 قائمة المراجعة النهائية | Final Checklist

### قبل الإطلاق الإنتاجي | Before Production Release

- [ ] **شهادات الأمان** | Security Certificates
  - [ ] الحصول على بصمات الشهادات الحقيقية | Get real certificate fingerprints
  - [ ] تحديث `certificate_config.dart` | Update `certificate_config.dart`
  - [ ] اختبار التثبيت في staging | Test pinning in staging
  - [ ] اختبار التثبيت في production | Test pinning in production
  - [ ] إعداد شهادة احتياطية للدوران | Prepare backup cert for rotation

- [ ] **التكوين** | Configuration
  - [ ] حذف `config.dart` | Delete `config.dart`
  - [ ] التحقق من `EnvConfig` | Verify `EnvConfig`
  - [ ] إنشاء ملفات `.env` لجميع البيئات | Create `.env` files for all environments
  - [ ] تحديث جميع استخدامات AppConfig | Update all AppConfig usages
  - [ ] اختبار في جميع البيئات | Test in all environments

- [ ] **الأصول** | Assets
  - [ ] تصميم شعار SAHOOL | Design SAHOOL logo
  - [ ] تصميم الأفاتار الافتراضية | Design default avatars
  - [ ] تحسين أحجام الملفات | Optimize file sizes
  - [ ] إضافة إلى المشروع | Add to project
  - [ ] اختبار عرض الأصول | Test asset display

- [ ] **الاختبارات** | Testing
  - [ ] اختبار الاتصال الآمن | Test secure connection
  - [ ] اختبار التثبيت المرفوض | Test rejected pinning
  - [ ] اختبار التبديل بين البيئات | Test environment switching
  - [ ] اختبار عرض الأصول | Test asset display
  - [ ] اختبار البدائل | Test fallbacks

- [ ] **الوثائق** | Documentation
  - [ ] توثيق عملية الحصول على الشهادات | Document certificate obtaining process
  - [ ] توثيق التكوين للبيئات | Document environment configuration
  - [ ] توثيق متطلبات الأصول | Document asset requirements
  - [ ] تحديث CHANGELOG.md | Update CHANGELOG.md
  - [ ] تحديث README.md | Update README.md

---

## 🚨 تحذيرات هامة | Important Warnings

### ⚠️ عدم الامتثال = عدم الإطلاق | Non-Compliance = No Release

**لا تقوم بنشر التطبيق في الإنتاج حتى:**  
**DO NOT deploy to production until:**

1. ✅ جميع الشهادات الوهمية تم استبدالها | All placeholder certificates replaced
2. ✅ جميع عناوين API المشفرة تم إزالتها | All hardcoded API URLs removed
3. ✅ جميع الاختبارات الأمنية نجحت | All security tests passed

### 🔒 الأمان أولاً | Security First

- بيانات المزارعين حساسة | Farmer data is sensitive
- التطبيق يحمل معلومات زراعية قيمة | App carries valuable agricultural information
- الامتثال للمعايير الأمنية إلزامي | Security standards compliance is mandatory

---

## 📞 جهات الاتصال | Contact Information

**للمساعدة في تنفيذ هذه الخطة:**  
**For assistance with this action plan:**

- **فريق الأمان | Security Team:** security@sahool.app
- **فريق DevOps:** devops@sahool.app
- **فريق التطوير | Development Team:** dev@sahool.app
- **فريق التصميم | Design Team:** design@sahool.app

---

**آخر تحديث | Last Updated:** 2026-02-17  
**الإصدار | Version:** 1.0  
**الحالة | Status:** 🔴 نشط - يتطلب عمل فوري | ACTIVE - Requires Immediate Action
