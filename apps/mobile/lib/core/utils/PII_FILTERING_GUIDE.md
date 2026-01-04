# PII Filtering Guide - SAHOOL Mobile App
# دليل تصفية البيانات الشخصية - تطبيق سهول للجوال

## Overview / نظرة عامة

The SAHOOL PII (Personally Identifiable Information) filtering system automatically sanitizes sensitive data in logs to prevent data leaks and ensure compliance with privacy regulations.

يقوم نظام تصفية البيانات الشخصية في سهول بتنظيف البيانات الحساسة تلقائياً في السجلات لمنع تسرب البيانات وضمان الامتثال لأنظمة الخصوصية.

## Features / المميزات

### 1. Automatic Data Masking / إخفاء البيانات التلقائي

The system automatically masks:
- **Phone Numbers**: `+966501234567` → `+966****4567`
- **Email Addresses**: `ahmed@example.com` → `ah****@example.com`
- **National IDs**: `1234567890` → `12******90`
- **Credit Cards**: `1234-5678-9012-3456` → `****-****-****-3456`
- **GPS Coordinates**: `24.7135517, 46.6752957` → `24.714, 46.675` (reduced precision)
- **Arabic Names**: `محمد بن سلمان` → `م****د ب*ن س****ن`

### 2. Complete Removal / الحذف الكامل

The system completely removes:
- **Tokens**: JWT tokens, Bearer tokens
- **Passwords**: All password fields
- **API Keys**: Long alphanumeric keys
- **Secrets**: Any field marked as sensitive

## Usage / الاستخدام

### Basic Logging

```dart
import 'package:sahool_mobile/core/utils/app_logger.dart';

// All logs are automatically filtered for PII
AppLogger.d('User phone: +966501234567');
// Output: 'User phone: +966****4567'

AppLogger.i('Email sent to ahmed@example.com');
// Output: 'Email sent to ah****@example.com'

AppLogger.e('Token expired: eyJhbGc...', error: error);
// Output: 'Token expired: [TOKEN_REDACTED]'
```

### Network Logging

```dart
import 'package:sahool_mobile/core/utils/app_logger.dart';

// Automatic PII filtering for network requests
AppLogger.network(
  'POST',
  '/api/users',
  statusCode: 200,
  data: {
    'phone': '+966501234567',
    'email': 'user@example.com',
  },
);
// Data is automatically sanitized before logging
```

### Using the Logging Interceptor

```dart
import 'package:dio/dio.dart';
import 'package:sahool_mobile/core/http/logging_interceptor.dart';

final dio = Dio();

// Add secure logging with PII protection
dio.addSecureLogging(
  logRequestHeaders: true,
  logRequestBody: true,
  logResponseBody: false, // Disable in production
  logErrorBody: true,
);

// Or use the interceptor directly
dio.interceptors.add(LoggingInterceptor(
  logRequestBody: true,
  logResponseBody: false,
  maxBodyLength: 2000,
));
```

### Manual Sanitization

```dart
import 'package:sahool_mobile/core/utils/pii_filter.dart';

// Sanitize a string
final sanitized = PiiFilter.sanitize('My phone is +966501234567');
// Output: 'My phone is +966****4567'

// Sanitize a map
final sanitizedData = PiiFilter.sanitize({
  'name': 'Ahmed',
  'phone': '+966501234567',
  'password': 'secret123',
});
// Output: { 'name': 'Ahmed', 'phone': '+966****4567', 'password': '[REDACTED]' }

// Check if text contains PII
if (PiiFilter.containsPii(text)) {
  print('Warning: PII detected!');
}

// Get PII statistics
final stats = PiiFilter.getPiiSummary(text);
print('Found ${stats['phones']} phone numbers');
```

### Using String Extensions

```dart
import 'package:sahool_mobile/core/utils/pii_filter.dart';

// Sanitize using extension
final sanitized = 'Phone: +966501234567'.sanitizePii();

// Check for PII using extension
if ('ahmed@example.com'.containsPii()) {
  print('Contains PII!');
}
```

## Configuration / الإعدادات

### Enable/Disable PII Filtering

```dart
import 'package:sahool_mobile/core/utils/app_logger.dart';

// Configure logger (usually in main.dart)
AppLogger.configure(
  enabled: true,
  minLevel: LogLevel.debug,
  enablePiiFiltering: true, // Always true in production!
);
```

**CRITICAL**: PII filtering is **always enabled** in release mode, regardless of configuration.

### Export Logs Safely

```dart
import 'package:sahool_mobile/core/utils/app_logger.dart';

// Export logs with PII filtering (default)
final safeLogs = AppLogger.exportLogs(sanitize: true);

// Export logs as JSON
final jsonLogs = AppLogger.exportLogsAsJson(sanitize: true);

// Get PII filtering statistics
final stats = AppLogger.getPiiStats();
print('Filtered ${stats['filtered_count']} PII instances');
```

## Best Practices / أفضل الممارسات

### DO ✅

1. **Always use AppLogger** instead of print() or debugPrint()
   ```dart
   // ✅ Good
   AppLogger.d('User logged in');

   // ❌ Bad
   print('User logged in with token: $token');
   ```

2. **Use structured logging with data maps**
   ```dart
   // ✅ Good
   AppLogger.i('User login', tag: 'AUTH', data: {
     'userId': userId,
     'timestamp': DateTime.now().toIso8601String(),
   });
   ```

3. **Log errors with context**
   ```dart
   // ✅ Good
   AppLogger.e(
     'Failed to fetch user data',
     tag: 'API',
     error: error,
     stackTrace: stackTrace,
   );
   ```

4. **Use the LoggingInterceptor for HTTP clients**
   ```dart
   // ✅ Good
   dio.addSecureLogging();
   ```

### DON'T ❌

1. **Never log raw tokens or passwords**
   ```dart
   // ❌ NEVER DO THIS
   AppLogger.d('Token: $accessToken');

   // ✅ The filter will catch it, but better to avoid
   AppLogger.d('Authentication successful');
   ```

2. **Don't bypass PII filtering in production**
   ```dart
   // ❌ NEVER DO THIS
   if (kReleaseMode) {
     AppLogger.configure(enablePiiFiltering: false);
   }
   ```

3. **Don't log entire user objects**
   ```dart
   // ❌ Bad - may contain sensitive data
   AppLogger.d('User: ${user.toJson()}');

   // ✅ Good - log specific non-sensitive fields
   AppLogger.d('User action', data: {'userId': user.id, 'action': 'login'});
   ```

## Sensitive Field Names / أسماء الحقول الحساسة

The following field names are **automatically redacted**:

- `password`, `token`, `access_token`, `refresh_token`
- `authorization`, `secret`, `api_key`, `apiKey`
- `private_key`, `privateKey`, `ssn`, `social_security`
- `credit_card`, `creditCard`, `cvv`, `pin`, `otp`
- `verification_code`, `verificationCode`

## Testing PII Filtering / اختبار التصفية

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile/core/utils/pii_filter.dart';

void main() {
  test('Should mask phone numbers', () {
    final result = PiiFilter.sanitize('+966501234567');
    expect(result, '+966****4567');
  });

  test('Should mask emails', () {
    final result = PiiFilter.sanitize('ahmed@example.com');
    expect(result, 'ah****@example.com');
  });

  test('Should remove tokens', () {
    final result = PiiFilter.sanitize('Bearer eyJhbGc...');
    expect(result, contains('[REDACTED]'));
  });
}
```

## Monitoring / المراقبة

### Check PII Filtering Stats

```dart
// Get statistics
final stats = AppLogger.getPiiStats();
print('PII Filtering Enabled: ${stats['enabled']}');
print('Total PII Filtered: ${stats['filtered_count']}');

// Get detailed PII summary for a string
final summary = PiiFilter.getPiiSummary(logText);
print('Phones: ${summary['phones']}');
print('Emails: ${summary['emails']}');
print('Tokens: ${summary['tokens']}');
```

## Performance Considerations / اعتبارات الأداء

- PII filtering is optimized with regex caching
- Minimal performance impact (~1-5ms per log)
- Only enabled for logged messages (no background scanning)
- Efficient for both small and large log entries

## Security Compliance / الامتثال الأمني

This PII filtering system helps comply with:

- **GDPR** (General Data Protection Regulation)
- **PDPL** (Saudi Personal Data Protection Law)
- **PCI DSS** (Payment Card Industry Data Security Standard)
- **HIPAA** (Health Insurance Portability and Accountability Act)

## Support / الدعم

For questions or issues:
1. Check existing logs for PII exposure
2. Review this guide
3. Contact the security team
4. File a security issue if you discover PII leaks

## Updates / التحديثات

- **v1.0.0**: Initial PII filtering implementation
  - Phone number masking
  - Email masking
  - Token removal
  - National ID masking
  - Credit card masking
  - GPS coordinate rounding
  - Arabic name masking

---

**Remember**: When in doubt, sanitize! It's better to over-filter than to leak sensitive data.

**تذكر**: في حالة الشك، قم بالتصفية! من الأفضل التصفية الزائدة على تسريب البيانات الحساسة.
