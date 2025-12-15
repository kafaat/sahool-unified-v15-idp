/// API Configuration for SAHOOL Field App
/// إعدادات الاتصال بالخادم
library;

import 'dart:io';

/// API configuration class
/// 10.0.2.2 للمحاكي الأندرويد، localhost للـ iOS Simulator
class ApiConfig {
  ApiConfig._();

  /// Base URL based on platform
  static String get baseUrl {
    if (Platform.isAndroid) {
      // Android Emulator sees host machine as 10.0.2.2
      return 'http://10.0.2.2:3000';
    }
    // iOS Simulator and real devices
    return 'http://localhost:3000';
  }

  /// Production base URL (Kong Gateway)
  static const String productionBaseUrl = 'https://api.sahool.io';

  /// Use production URL in release mode
  static String get effectiveBaseUrl {
    const isProduction = bool.fromEnvironment('dart.vm.product');
    return isProduction ? productionBaseUrl : baseUrl;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // API Endpoints
  // ─────────────────────────────────────────────────────────────────────────────

  /// Fields endpoints
  static String get fields => '$effectiveBaseUrl/api/v1/fields';
  static String fieldById(String id) => '$effectiveBaseUrl/api/v1/fields/$id';
  static String get fieldsSync => '$effectiveBaseUrl/api/v1/fields/sync';
  static String get fieldsBatch => '$effectiveBaseUrl/api/v1/fields/batch';
  static String get fieldsNearby => '$effectiveBaseUrl/api/v1/fields/nearby';

  /// NDVI endpoints
  static String get ndvi => '$effectiveBaseUrl/api/v1/ndvi';
  static String ndviByFieldId(String fieldId) => '$effectiveBaseUrl/api/v1/ndvi/field/$fieldId';
  static String get ndviAnalyze => '$effectiveBaseUrl/api/v1/ndvi/analyze';

  /// Weather endpoints
  static String get weather => '$effectiveBaseUrl/api/v1/weather';
  static String get forecast => '$effectiveBaseUrl/api/v1/forecast';

  /// Tasks endpoints
  static String get tasks => '$effectiveBaseUrl/api/v1/tasks';
  static String taskById(String id) => '$effectiveBaseUrl/api/v1/tasks/$id';

  /// Equipment endpoints
  static String get equipment => '$effectiveBaseUrl/api/v1/equipment';
  static String equipmentById(String id) => '$effectiveBaseUrl/api/v1/equipment/$id';

  /// Community endpoints
  static String get posts => '$effectiveBaseUrl/api/v1/posts';
  static String get stories => '$effectiveBaseUrl/api/v1/stories';
  static String get experts => '$effectiveBaseUrl/api/v1/experts';

  /// Provider config endpoints
  static String get providers => '$effectiveBaseUrl/api/v1/providers';
  static String get providerConfig => '$effectiveBaseUrl/api/v1/config';

  /// Auth endpoints
  static String get login => '$effectiveBaseUrl/api/v1/auth/login';
  static String get register => '$effectiveBaseUrl/api/v1/auth/register';
  static String get refreshToken => '$effectiveBaseUrl/api/v1/auth/refresh';

  // ─────────────────────────────────────────────────────────────────────────────
  // Timeouts Configuration
  // ─────────────────────────────────────────────────────────────────────────────

  /// Connection timeout for areas with poor connectivity
  static const Duration connectTimeout = Duration(seconds: 30);

  /// Send timeout
  static const Duration sendTimeout = Duration(seconds: 15);

  /// Receive timeout
  static const Duration receiveTimeout = Duration(seconds: 15);

  // ─────────────────────────────────────────────────────────────────────────────
  // Headers
  // ─────────────────────────────────────────────────────────────────────────────

  /// Default headers for API requests
  static Map<String, String> get defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Language': 'ar,en',
  };

  /// Get headers with authorization token
  static Map<String, String> authHeaders(String token) => {
    ...defaultHeaders,
    'Authorization': 'Bearer $token',
  };

  /// Get headers with ETag for optimistic locking
  static Map<String, String> etagHeaders(String token, String etag) => {
    ...authHeaders(token),
    'If-Match': etag,
  };
}
