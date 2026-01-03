// SAHOOL PII Filtering - Integration Examples
// أمثلة تكامل نظام تصفية البيانات الشخصية

import 'package:dio/dio.dart';
import 'pii_filter.dart';
import 'app_logger.dart';
import '../http/logging_interceptor.dart';

/// Example 1: Basic Logging with Automatic PII Filtering
/// مثال 1: التسجيل الأساسي مع التصفية التلقائية للبيانات الشخصية
void exampleBasicLogging() {
  // All these logs are automatically sanitized
  AppLogger.d('User phone: +966501234567');
  // Output: 'User phone: +966****4567'

  AppLogger.i('Email sent to ahmed@example.com');
  // Output: 'Email sent to ah****@example.com'

  AppLogger.w('Token expired: Bearer eyJhbGc...');
  // Output: 'Token expired: Bearer [REDACTED]'

  AppLogger.e('Credit card: 4532-1234-5678-9010', error: Exception('Payment failed'));
  // Output: 'Credit card: ****-****-****-9010'
}

/// Example 2: Network Logging with Data Sanitization
/// مثال 2: تسجيل الشبكة مع تنظيف البيانات
void exampleNetworkLogging() {
  // Network logs automatically sanitize all data
  AppLogger.network(
    'POST',
    '/api/auth/login',
    statusCode: 200,
    data: {
      'email': 'user@example.com',
      'password': 'secret123', // Automatically redacted
      'phone': '+966501234567',
    },
  );
  // Logged data:
  // {
  //   'email': 'us****@example.com',
  //   'password': '[REDACTED]',
  //   'phone': '+966****4567'
  // }
}

/// Example 3: Manual Sanitization
/// مثال 3: التنظيف اليدوي
void exampleManualSanitization() {
  // Sanitize a string
  final sanitizedText = PiiFilter.sanitize('Contact: +966501234567');
  print(sanitizedText); // 'Contact: +966****4567'

  // Sanitize a map
  final userData = {
    'name': 'Ahmed',
    'email': 'ahmed@example.com',
    'phone': '+966501234567',
    'password': 'secret',
  };

  final sanitizedData = PiiFilter.sanitize(userData);
  print(sanitizedData);
  // {
  //   'name': 'Ahmed',
  //   'email': 'ah****@example.com',
  //   'phone': '+966****4567',
  //   'password': '[REDACTED]'
  // }

  // Using string extension
  final phone = '+966501234567'.sanitizePii();
  print(phone); // '+966****4567'

  // Check if text contains PII
  if ('ahmed@example.com'.containsPii()) {
    print('Warning: PII detected!');
  }
}

/// Example 4: Dio Configuration with Secure Logging
/// مثال 4: إعداد Dio مع التسجيل الآمن
Dio exampleDioSetup() {
  final dio = Dio(BaseOptions(
    baseUrl: 'https://api.sahool.sa',
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
  ));

  // Simple setup - use default secure logging
  dio.addSecureLogging();

  // Or advanced configuration
  dio.interceptors.add(LoggingInterceptor(
    logRequestHeaders: true,
    logRequestBody: true,
    logResponseHeaders: false,
    logResponseBody: false, // Disable in production
    logErrorBody: true,
    maxBodyLength: 2000,
  ));

  return dio;
}

/// Example 5: Error Handling with Sanitization
/// مثال 5: معالجة الأخطاء مع التنظيف
Future<void> exampleErrorHandling() async {
  try {
    // Some operation that might fail
    throw Exception('Authentication failed for user ahmed@example.com with token: Bearer abc123');
  } catch (e, stackTrace) {
    // Error messages are automatically sanitized
    AppLogger.e(
      'Operation failed',
      tag: 'AUTH',
      error: e, // Automatically sanitized
      stackTrace: stackTrace,
    );
    // Logged error: 'Authentication failed for user ah****@example.com with token: Bearer [REDACTED]'
  }
}

/// Example 6: Request/Response Sanitization
/// مثال 6: تنظيف الطلبات والاستجابات
void exampleRequestResponseSanitization() {
  // Sanitize request body
  final requestBody = {
    'username': 'ahmed',
    'password': 'secret123',
    'phone': '+966501234567',
  };

  final sanitizedRequest = PiiFilter.sanitizeRequestBody(requestBody);
  AppLogger.d('Request', data: sanitizedRequest);

  // Sanitize response body
  final responseBody = {
    'user': {
      'id': '123',
      'email': 'ahmed@example.com',
      'phone': '+966501234567',
      'token': 'eyJhbGc...',
    },
  };

  final sanitizedResponse = PiiFilter.sanitizeResponseBody(responseBody);
  AppLogger.d('Response', data: sanitizedResponse);

  // Sanitize headers
  final headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123',
    'X-API-Key': 'secret_key',
  };

  final sanitizedHeaders = PiiFilter.sanitizeHeaders(headers);
  AppLogger.d('Headers', data: sanitizedHeaders);
  // {
  //   'Content-Type': 'application/json',
  //   'Authorization': '[REDACTED]',
  //   'X-API-Key': '[REDACTED]'
  // }
}

/// Example 7: PII Detection and Statistics
/// مثال 7: اكتشاف البيانات الشخصية والإحصائيات
void examplePiiDetectionAndStats() {
  final text = '''
    User Information:
    Name: Ahmed
    Email: ahmed@example.com
    Phone: +966501234567
    National ID: 1234567890
    Token: Bearer eyJhbGc...
  ''';

  // Check if contains PII
  if (PiiFilter.containsPii(text)) {
    print('Warning: PII detected!');

    // Get detailed statistics
    final summary = PiiFilter.getPiiSummary(text);
    print('Found ${summary['phones']} phone numbers');
    print('Found ${summary['emails']} email addresses');
    print('Found ${summary['nationalIds']} national IDs');
    print('Found ${summary['tokens']} tokens');
  }

  // Get logger statistics
  final loggerStats = AppLogger.getPiiStats();
  print('PII Filtering Enabled: ${loggerStats['enabled']}');
  print('Total PII Filtered: ${loggerStats['filtered_count']}');
}

/// Example 8: Safe Log Export
/// مثال 8: تصدير السجلات بشكل آمن
void exampleSafeLogExport() {
  // Export logs with PII filtering (recommended)
  final safeLogs = AppLogger.exportLogs(sanitize: true);
  print('Safe logs for crash report:');
  print(safeLogs);

  // Export as JSON
  final jsonLogs = AppLogger.exportLogsAsJson(sanitize: true);
  print('JSON logs for analytics:');
  print(jsonLogs);

  // Get recent logs (automatically sanitized)
  final recentLogs = AppLogger.getRecentLogs(count: 50);
  for (final log in recentLogs) {
    print(log.toString()); // Already sanitized
  }
}

/// Example 9: Real-world Login Flow
/// مثال 9: سير عمل تسجيل الدخول الواقعي
Future<void> exampleLoginFlow(Dio dio) async {
  final email = 'user@example.com';
  final password = 'P@ssw0rd123';

  try {
    // Log attempt (credentials NOT logged)
    AppLogger.i('Login attempt started', tag: 'AUTH');

    // Make request (automatically logged with sanitization)
    final response = await dio.post('/auth/login', data: {
      'email': email,
      'password': password,
    });

    // Log success (token NOT logged)
    AppLogger.i('Login successful', tag: 'AUTH', data: {
      'userId': response.data['user']['id'],
      'timestamp': DateTime.now().toIso8601String(),
    });
  } on DioException catch (e) {
    // Error automatically sanitized
    AppLogger.e(
      'Login failed',
      tag: 'AUTH',
      error: e,
      data: {'statusCode': e.response?.statusCode},
    );
  }
}

/// Example 10: Configuration in main.dart
/// مثال 10: الإعداد في main.dart
void exampleMainConfiguration() {
  // Configure logger at app startup
  AppLogger.configure(
    enabled: true,
    minLevel: LogLevel.debug, // or LogLevel.info for production
    enablePiiFiltering: true, // Always true in production
  );

  // Note: PII filtering is ALWAYS enabled in release mode,
  // regardless of configuration
}

/// Example 11: Custom Service with Logging
/// مثال 11: خدمة مخصصة مع التسجيل
class UserService {
  final Dio _dio;

  UserService(this._dio);

  Future<void> updateUserProfile(String userId, Map<String, dynamic> data) async {
    try {
      AppLogger.d('Updating user profile', tag: 'USER', data: {
        'userId': userId,
        'fields': data.keys.toList(), // Log field names, not values
      });

      final response = await _dio.put('/users/$userId', data: data);

      // Success - no sensitive data logged
      AppLogger.i('Profile updated successfully', tag: 'USER', data: {
        'userId': userId,
      });
    } catch (e, stackTrace) {
      // Error automatically sanitized
      AppLogger.e(
        'Profile update failed',
        tag: 'USER',
        error: e,
        stackTrace: stackTrace,
      );
      rethrow;
    }
  }
}

/// Example 12: Chat Message Sanitization
/// مثال 12: تنظيف رسائل الدردشة
void exampleChatMessageSanitization() {
  // Chat messages might contain PII
  final message = 'Please call me at +966501234567 or email ahmed@example.com';

  // Log the message (automatically sanitized)
  AppLogger.d('Chat message sent', tag: 'CHAT', data: {
    'message': message, // Will be sanitized
    'timestamp': DateTime.now().toIso8601String(),
  });
  // Logged: 'message': 'Please call me at +966****4567 or email ah****@example.com'
}

/// Example 13: Location Data Sanitization
/// مثال 13: تنظيف بيانات الموقع
void exampleLocationSanitization() {
  final lat = 24.7135517;
  final lng = 46.6752957;

  // Precise location (before sanitization)
  final preciseLocation = '$lat, $lng';

  // Log location (automatically rounded to reduce precision)
  AppLogger.d('User location', tag: 'GPS', data: {
    'location': preciseLocation,
  });
  // Logged: 'location': '24.714, 46.675' (rounded to ~111m precision)
}

/// Example 14: Form Data Sanitization
/// مثال 14: تنظيف بيانات النماذج
void exampleFormDataSanitization() {
  final formData = {
    'firstName': 'Ahmed',
    'lastName': 'Mohammed',
    'email': 'ahmed@example.com',
    'phone': '+966501234567',
    'nationalId': '1234567890',
    'creditCard': '4532-1234-5678-9010',
    'cvv': '123',
  };

  // Log form submission (automatically sanitized)
  AppLogger.i('Form submitted', tag: 'FORM', data: formData);
  // Logged data:
  // {
  //   'firstName': 'Ahmed',
  //   'lastName': 'Mohammed',
  //   'email': 'ah****@example.com',
  //   'phone': '+966****4567',
  //   'nationalId': '12******90',
  //   'creditCard': '****-****-****-9010',
  //   'cvv': '[REDACTED]' // or masked
  // }
}

/// Example 15: API Error Response Sanitization
/// مثال 15: تنظيف استجابات أخطاء API
void exampleApiErrorSanitization() {
  final errorResponse = {
    'error': 'Invalid credentials',
    'details': 'Email ahmed@example.com not found',
    'trace': 'Token eyJhbGc... expired',
  };

  // Log error response (automatically sanitized)
  AppLogger.e('API Error', tag: 'API', data: errorResponse);
  // Logged data:
  // {
  //   'error': 'Invalid credentials',
  //   'details': 'Email ah****@example.com not found',
  //   'trace': 'Token [TOKEN_REDACTED] expired'
  // }
}
