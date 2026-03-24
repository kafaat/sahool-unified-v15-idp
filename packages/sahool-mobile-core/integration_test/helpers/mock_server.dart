/// SAHOOL Integration Test - Mock Server
/// خادم وهمي للاختبارات
///
/// Provides mock API responses for integration testing
/// without requiring a real backend connection.
///
/// Features:
/// - Mock HTTP responses
/// - Configurable response delays
/// - Error simulation
/// - Request logging
/// - Response stubbing

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import '../fixtures/test_data.dart';

/// Mock server configuration
/// إعدادات الخادم الوهمي
class MockServerConfig {
  /// Response delay in milliseconds
  final int responseDelayMs;

  /// Simulate network errors
  final bool simulateErrors;

  /// Error rate (0.0 to 1.0)
  final double errorRate;

  /// Enable request logging
  final bool enableLogging;

  const MockServerConfig({
    this.responseDelayMs = 100,
    this.simulateErrors = false,
    this.errorRate = 0.1,
    this.enableLogging = true,
  });

  static const MockServerConfig defaultConfig = MockServerConfig();

  static const MockServerConfig slowNetwork = MockServerConfig(
    responseDelayMs: 2000,
  );

  static const MockServerConfig unstableNetwork = MockServerConfig(
    simulateErrors: true,
    errorRate: 0.3,
  );
}

/// Mock HTTP response
/// استجابة HTTP وهمية
class MockResponse {
  final int statusCode;
  final Map<String, dynamic> body;
  final Map<String, String> headers;
  final Duration? delay;

  const MockResponse({
    this.statusCode = 200,
    this.body = const {},
    this.headers = const {'Content-Type': 'application/json'},
    this.delay,
  });

  static MockResponse success(Map<String, dynamic> data) =>
      MockResponse(statusCode: 200, body: data);

  static MockResponse created(Map<String, dynamic> data) =>
      MockResponse(statusCode: 201, body: data);

  static MockResponse error(int statusCode, String message) => MockResponse(
        statusCode: statusCode,
        body: {'error': message, 'message': message},
      );

  static const MockResponse unauthorized = MockResponse(
    statusCode: 401,
    body: {'error': 'Unauthorized', 'message': 'غير مصرح'},
  );

  static const MockResponse notFound = MockResponse(
    statusCode: 404,
    body: {'error': 'Not Found', 'message': 'غير موجود'},
  );

  static const MockResponse serverError = MockResponse(
    statusCode: 500,
    body: {'error': 'Internal Server Error', 'message': 'خطأ في الخادم'},
  );
}

/// Mock request
/// طلب وهمي
class MockRequest {
  final String method;
  final String path;
  final Map<String, dynamic>? body;
  final Map<String, String> headers;
  final DateTime timestamp;

  MockRequest({
    required this.method,
    required this.path,
    this.body,
    this.headers = const {},
  }) : timestamp = DateTime.now();

  @override
  String toString() => '$method $path ${body != null ? jsonEncode(body) : ''}';
}

/// Mock server for API testing
/// خادم وهمي لاختبار واجهة برمجة التطبيقات
class MockServer {
  static MockServer? _instance;
  static MockServer get instance {
    _instance ??= MockServer._();
    return _instance!;
  }

  MockServer._();

  MockServerConfig _config = MockServerConfig.defaultConfig;
  final List<MockRequest> _requestLog = [];
  final Map<String, MockResponse Function(MockRequest)> _stubs = {};

  /// Configure the mock server
  /// تكوين الخادم الوهمي
  void configure(MockServerConfig config) {
    _config = config;
  }

  /// Reset configuration to default
  /// إعادة تعيين التكوين
  void reset() {
    _config = MockServerConfig.defaultConfig;
    _requestLog.clear();
    _stubs.clear();
  }

  /// Get request log
  /// الحصول على سجل الطلبات
  List<MockRequest> get requestLog => List.unmodifiable(_requestLog);

  /// Clear request log
  /// مسح سجل الطلبات
  void clearLog() => _requestLog.clear();

  /// Stub a specific endpoint
  /// إعداد استجابة وهمية لنقطة نهاية محددة
  void stub(String path, MockResponse Function(MockRequest) handler) {
    _stubs[path] = handler;
  }

  /// Stub with fixed response
  /// إعداد استجابة ثابتة
  void stubFixed(String path, MockResponse response) {
    _stubs[path] = (_) => response;
  }

  /// Process a mock request
  /// معالجة طلب وهمي
  Future<MockResponse> processRequest(MockRequest request) async {
    // Log request
    if (_config.enableLogging) {
      _requestLog.add(request);
      debugPrint('Mock Request: ${request.method} ${request.path}');
    }

    // Add delay
    final delay = Duration(milliseconds: _config.responseDelayMs);
    await Future.delayed(delay);

    // Simulate errors
    if (_config.simulateErrors) {
      if (_shouldSimulateError()) {
        debugPrint('Mock: Simulating error');
        return MockResponse.serverError;
      }
    }

    // Check for stub
    if (_stubs.containsKey(request.path)) {
      return _stubs[request.path]!(request);
    }

    // Default responses based on endpoint
    return _getDefaultResponse(request);
  }

  bool _shouldSimulateError() {
    return (DateTime.now().millisecondsSinceEpoch % 100) / 100 <
        _config.errorRate;
  }

  MockResponse _getDefaultResponse(MockRequest request) {
    final path = request.path;
    final method = request.method;

    // Auth endpoints
    if (path.contains('/auth/login')) {
      return _handleLogin(request);
    }
    if (path.contains('/auth/logout')) {
      return MockResponse.success({'message': 'Logged out'});
    }
    if (path.contains('/auth/refresh')) {
      return _handleTokenRefresh(request);
    }

    // Fields endpoints
    if (path.contains('/fields')) {
      return _handleFields(request);
    }

    // Weather endpoints
    if (path.contains('/weather')) {
      return _handleWeather(request);
    }

    // Inventory endpoints
    if (path.contains('/inventory')) {
      return _handleInventory(request);
    }

    // VRA endpoints
    if (path.contains('/vra')) {
      return _handleVRA(request);
    }

    // Satellite endpoints
    if (path.contains('/satellite')) {
      return _handleSatellite(request);
    }

    // Default: not found
    return MockResponse.notFound;
  }

  // ============================================================================
  // Auth Handlers
  // معالجات المصادقة
  // ============================================================================

  MockResponse _handleLogin(MockRequest request) {
    final body = request.body;
    if (body == null) {
      return MockResponse.error(400, 'Missing credentials');
    }

    final email = body['email'] ?? body['phone'];
    final password = body['password'];

    if (email == TestUsers.validEmail && password == TestUsers.validPassword) {
      return MockResponse.success({
        'access_token':
            'mock_access_token_${DateTime.now().millisecondsSinceEpoch}',
        'refresh_token': 'mock_refresh_token',
        'token_type': 'Bearer',
        'expires_in': 3600,
        'user': {
          'id': 'user-001',
          'email': TestUsers.validEmail,
          'name': TestUsers.validUsername,
          'role': 'farmer',
        },
      });
    }

    if (email == TestUsers.adminEmail && password == TestUsers.adminPassword) {
      return MockResponse.success({
        'access_token': 'mock_admin_token',
        'refresh_token': 'mock_admin_refresh',
        'token_type': 'Bearer',
        'expires_in': 3600,
        'user': {
          'id': 'admin-001',
          'email': TestUsers.adminEmail,
          'name': 'المدير',
          'role': 'admin',
        },
      });
    }

    return MockResponse.error(401, 'بيانات الدخول غير صحيحة');
  }

  MockResponse _handleTokenRefresh(MockRequest request) {
    return MockResponse.success({
      'access_token':
          'mock_refreshed_token_${DateTime.now().millisecondsSinceEpoch}',
      'refresh_token': 'mock_new_refresh_token',
      'token_type': 'Bearer',
      'expires_in': 3600,
    });
  }

  // ============================================================================
  // Fields Handlers
  // معالجات الحقول
  // ============================================================================

  MockResponse _handleFields(MockRequest request) {
    final method = request.method;
    final path = request.path;

    // GET /fields - List fields
    if (method == 'GET' && !path.contains('/fields/')) {
      return MockResponse.success({
        'data': [
          TestFields.field1,
          TestFields.field2,
        ],
        'total': 2,
        'page': 1,
        'limit': 20,
      });
    }

    // GET /fields/:id - Get single field
    if (method == 'GET' && path.contains('/fields/')) {
      return MockResponse.success({
        'data': TestFields.field1,
      });
    }

    // POST /fields - Create field
    if (method == 'POST') {
      final body = request.body ?? {};
      return MockResponse.created({
        'data': {
          'id': 'field-new-${DateTime.now().millisecondsSinceEpoch}',
          ...body,
          'createdAt': DateTime.now().toIso8601String(),
        },
        'message': 'تم إنشاء الحقل بنجاح',
      });
    }

    // PUT /fields/:id - Update field
    if (method == 'PUT' || method == 'PATCH') {
      final body = request.body ?? {};
      return MockResponse.success({
        'data': {
          ...TestFields.field1,
          ...body,
          'updatedAt': DateTime.now().toIso8601String(),
        },
        'message': 'تم تحديث الحقل بنجاح',
      });
    }

    // DELETE /fields/:id - Delete field
    if (method == 'DELETE') {
      return MockResponse.success({
        'message': 'تم حذف الحقل بنجاح',
      });
    }

    return MockResponse.notFound;
  }

  // ============================================================================
  // Weather Handlers
  // معالجات الطقس
  // ============================================================================

  MockResponse _handleWeather(MockRequest request) {
    return MockResponse.success({
      'data': {
        'current': {
          'temperature': 28.5,
          'humidity': 45,
          'windSpeed': 12.3,
          'windDirection': 'NW',
          'precipitation': 0,
          'pressure': 1013,
          'uvIndex': 6,
          'visibility': 10,
          'description': 'صافي',
          'icon': 'sunny',
        },
        'hourly': List.generate(24, (i) {
          return {
            'time': DateTime.now().add(Duration(hours: i)).toIso8601String(),
            'temperature': 25 + (i % 10),
            'precipitation': i % 4 == 0 ? 10 : 0,
            'icon': i > 6 && i < 18 ? 'sunny' : 'moon',
          };
        }),
        'daily': List.generate(7, (i) {
          return {
            'date': DateTime.now().add(Duration(days: i)).toIso8601String(),
            'temperatureMax': 30 + i,
            'temperatureMin': 20 + i,
            'precipitation': i % 3 == 0 ? 20 : 0,
            'icon': 'partly_cloudy',
          };
        }),
        'alerts': [],
        'agricultural_impacts': [
          {
            'type': 'irrigation',
            'status': 'favorable',
            'message': 'الظروف مناسبة للري',
          },
          {
            'type': 'spraying',
            'status': 'caution',
            'message': 'تجنب الرش في منتصف النهار',
          },
        ],
      },
    });
  }

  // ============================================================================
  // Inventory Handlers
  // معالجات المخزون
  // ============================================================================

  MockResponse _handleInventory(MockRequest request) {
    final method = request.method;

    if (method == 'GET') {
      return MockResponse.success({
        'data': [
          TestInventory.fertilizer1,
          TestInventory.pesticide1,
          TestInventory.seed1,
          TestInventory.lowStockItem,
        ],
        'total': 4,
        'lowStockCount': 1,
      });
    }

    if (method == 'POST') {
      final body = request.body ?? {};
      return MockResponse.created({
        'data': {
          'id': 'inv-new-${DateTime.now().millisecondsSinceEpoch}',
          ...body,
          'createdAt': DateTime.now().toIso8601String(),
        },
        'message': 'تمت إضافة العنصر بنجاح',
      });
    }

    if (method == 'PUT' || method == 'PATCH') {
      return MockResponse.success({
        'data': TestInventory.fertilizer1,
        'message': 'تم تحديث العنصر بنجاح',
      });
    }

    if (method == 'DELETE') {
      return MockResponse.success({
        'message': 'تم حذف العنصر بنجاح',
      });
    }

    return MockResponse.notFound;
  }

  // ============================================================================
  // VRA Handlers
  // معالجات الزراعة الدقيقة
  // ============================================================================

  MockResponse _handleVRA(MockRequest request) {
    final method = request.method;

    if (method == 'GET') {
      return MockResponse.success({
        'data': [TestVRA.prescription1],
        'total': 1,
      });
    }

    if (method == 'POST') {
      final body = request.body ?? {};
      return MockResponse.created({
        'data': {
          'id': 'vra-new-${DateTime.now().millisecondsSinceEpoch}',
          ...body,
          'status': 'draft',
          'createdAt': DateTime.now().toIso8601String(),
        },
        'message': 'تم إنشاء الوصفة بنجاح',
      });
    }

    return MockResponse.notFound;
  }

  // ============================================================================
  // Satellite Handlers
  // معالجات الأقمار الصناعية
  // ============================================================================

  MockResponse _handleSatellite(MockRequest request) {
    return MockResponse.success({
      'data': TestSatellite.imagery1,
      'history': TestSatellite.historicalData,
    });
  }
}

// =============================================================================
// Mock HTTP Client
// عميل HTTP وهمي
// =============================================================================

/// Mock HTTP client that intercepts requests
/// عميل HTTP وهمي يعترض الطلبات
class MockHttpClient {
  final MockServer _server = MockServer.instance;

  /// GET request
  Future<MockResponse> get(String path, {Map<String, String>? headers}) async {
    return _server.processRequest(MockRequest(
      method: 'GET',
      path: path,
      headers: headers ?? {},
    ));
  }

  /// POST request
  Future<MockResponse> post(
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    return _server.processRequest(MockRequest(
      method: 'POST',
      path: path,
      body: body,
      headers: headers ?? {},
    ));
  }

  /// PUT request
  Future<MockResponse> put(
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    return _server.processRequest(MockRequest(
      method: 'PUT',
      path: path,
      body: body,
      headers: headers ?? {},
    ));
  }

  /// PATCH request
  Future<MockResponse> patch(
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    return _server.processRequest(MockRequest(
      method: 'PATCH',
      path: path,
      body: body,
      headers: headers ?? {},
    ));
  }

  /// DELETE request
  Future<MockResponse> delete(String path,
      {Map<String, String>? headers}) async {
    return _server.processRequest(MockRequest(
      method: 'DELETE',
      path: path,
      headers: headers ?? {},
    ));
  }
}

// =============================================================================
// Test Helpers for Mock Server
// دوال مساعدة للخادم الوهمي
// =============================================================================

/// Setup mock server for testing
/// إعداد الخادم الوهمي للاختبار
void setupMockServer([MockServerConfig? config]) {
  MockServer.instance.configure(config ?? MockServerConfig.defaultConfig);
}

/// Reset mock server
/// إعادة تعيين الخادم الوهمي
void resetMockServer() {
  MockServer.instance.reset();
}

/// Get mock server request log
/// الحصول على سجل طلبات الخادم الوهمي
List<MockRequest> getMockRequestLog() {
  return MockServer.instance.requestLog;
}

/// Verify a request was made
/// التحقق من تنفيذ طلب
bool verifyRequest(String method, String path) {
  return MockServer.instance.requestLog.any(
    (r) => r.method == method && r.path.contains(path),
  );
}

/// Count requests to a path
/// حساب عدد الطلبات لمسار
int countRequests(String path) {
  return MockServer.instance.requestLog
      .where((r) => r.path.contains(path))
      .length;
}

/// Stub a specific response
/// إعداد استجابة محددة
void stubResponse(String path, MockResponse response) {
  MockServer.instance.stubFixed(path, response);
}

/// Stub error response
/// إعداد استجابة خطأ
void stubError(String path, int statusCode, String message) {
  MockServer.instance.stubFixed(path, MockResponse.error(statusCode, message));
}

/// Stub delayed response
/// إعداد استجابة متأخرة
void stubDelayedResponse(String path, MockResponse response, Duration delay) {
  MockServer.instance.stub(
      path,
      (request) {
        // Note: Delay is handled by MockServer.processRequest
        // Additional delay would need async stub support
        return response;
      });
}
