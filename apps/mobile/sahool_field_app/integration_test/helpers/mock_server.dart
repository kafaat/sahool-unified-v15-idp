/// Mock HTTP Server for Integration Tests
/// خادم HTTP وهمي لاختبارات التكامل
///
/// Provides a lightweight in-process mock server that intercepts HTTP calls
/// and returns pre-configured responses. Used by integration tests that
/// exercise full API call flows without a real backend.
library;

import 'dart:convert';

// ═══════════════════════════════════════════════════════════════════════════
// Mock Request / Response Models
// ═══════════════════════════════════════════════════════════════════════════

/// Represents an intercepted HTTP request.
class MockRequest {
  final String method;
  final String path;
  final Map<String, String> headers;
  final Map<String, dynamic>? body;
  final Map<String, String>? queryParams;

  const MockRequest({
    required this.method,
    required this.path,
    this.headers = const {},
    this.body,
    this.queryParams,
  });
}

/// Represents a canned HTTP response returned by the mock server.
class MockResponse {
  final int statusCode;
  final Map<String, dynamic> body;
  final Map<String, String> headers;

  const MockResponse({
    required this.statusCode,
    required this.body,
    this.headers = const {},
  });

  // ── Convenience factories ──────────────────────────────────────────────

  /// 200 OK with a custom body.
  factory MockResponse.success(Map<String, dynamic> body) =>
      MockResponse(statusCode: 200, body: body);

  /// 201 Created with a custom body.
  factory MockResponse.created(Map<String, dynamic> body) =>
      MockResponse(statusCode: 201, body: body);

  /// 401 Unauthorized.
  static const unauthorized = MockResponse(
    statusCode: 401,
    body: {'error': 'Unauthorized', 'message': 'غير مصرح'},
  );

  /// 404 Not Found.
  static const notFound = MockResponse(
    statusCode: 404,
    body: {'error': 'Not Found', 'message': 'غير موجود'},
  );

  /// 500 Internal Server Error.
  static const serverError = MockResponse(
    statusCode: 500,
    body: {'error': 'Internal Server Error', 'message': 'خطأ داخلي في الخادم'},
  );
}

/// Handler signature for dynamic route stubs.
typedef MockRouteHandler = MockResponse Function(MockRequest request);

// ═══════════════════════════════════════════════════════════════════════════
// Mock Server Singleton
// ═══════════════════════════════════════════════════════════════════════════

/// In-process mock server that records requests and returns canned responses.
class MockServer {
  MockServer._();
  static final MockServer instance = MockServer._();

  final List<MockRequest> _requestLog = [];
  final Map<String, MockRouteHandler> _stubs = {};
  final Map<String, MockResponse> _staticStubs = {};

  // ── Default route handlers (set up by [setupMockServer]) ───────────────

  bool _isSetUp = false;

  void _registerDefaults() {
    // Auth: login
    stub('/api/v1/auth/login', (request) {
      if (request.method != 'POST') {
        return MockResponse.notFound;
      }
      final body = request.body;
      if (body == null || body['email'] == null || body['password'] == null) {
        return const MockResponse(
          statusCode: 400,
          body: {'error': 'Bad Request', 'message': 'Missing credentials'},
        );
      }
      if (body['email'] == 'invalid@example.com') {
        return MockResponse.unauthorized;
      }
      final role = body['email'] == 'admin@sahool.app' ? 'admin' : 'farmer';
      final name = role == 'admin' ? 'مدير النظام' : 'أحمد المزارع';
      return MockResponse.success({
        'access_token': 'mock-access-${DateTime.now().millisecondsSinceEpoch}',
        'refresh_token':
            'mock-refresh-${DateTime.now().millisecondsSinceEpoch}',
        'token_type': 'Bearer',
        'expires_in': 3600,
        'user': {
          'id': 'user-001',
          'email': body['email'],
          'name': name,
          'role': role,
        },
      });
    });

    // Auth: refresh
    stub('/api/v1/auth/refresh', (request) {
      return MockResponse.success({
        'access_token':
            'mock-refreshed-${DateTime.now().millisecondsSinceEpoch}',
        'refresh_token':
            'mock-refresh2-${DateTime.now().millisecondsSinceEpoch}',
        'token_type': 'Bearer',
        'expires_in': 3600,
      });
    });

    // Auth: logout
    stub('/api/v1/auth/logout', (_) {
      return MockResponse.success({'message': 'Logged out'});
    });

    // Fields: list
    stub('/api/v1/fields', (request) {
      if (request.method == 'GET') {
        return MockResponse.success({
          'data': [
            {
              'id': 'field-001',
              'name': 'حقل القمح',
              'area_hectares': 10.5,
              'crop_type': 'wheat',
              'status': 'active',
            },
            {
              'id': 'field-002',
              'name': 'حقل الشعير',
              'area_hectares': 8.2,
              'crop_type': 'barley',
              'status': 'active',
            },
          ],
          'total': 2,
          'page': 1,
          'limit': 20,
        });
      }
      if (request.method == 'POST') {
        return MockResponse.created({
          'data': {'id': 'field-new', ...?request.body},
        });
      }
      return MockResponse.notFound;
    });

    // Weather: current
    stub('/api/v1/weather', (request) {
      return MockResponse.success({
        'data': {
          'temperature': 28.5,
          'humidity': 45,
          'description': 'مشمس',
          'wind_speed': 3.5,
        },
      });
    });
  }

  // ── Public API ─────────────────────────────────────────────────────────

  /// Register a dynamic handler for a path prefix.
  void stub(String pathPrefix, MockRouteHandler handler) {
    _stubs[pathPrefix] = handler;
  }

  /// Register a static response for a path.
  void stubStatic(String path, MockResponse response) {
    _staticStubs[path] = response;
  }

  /// Process a request and return a response.
  MockResponse handle(MockRequest request) {
    _requestLog.add(request);

    // Check static stubs first (set via [stubResponse] top-level function)
    if (_staticStubs.containsKey(request.path)) {
      return _staticStubs[request.path]!;
    }

    // Find the longest matching stub prefix
    String? bestMatch;
    for (final prefix in _stubs.keys) {
      if (request.path.startsWith(prefix) || request.path == prefix) {
        if (bestMatch == null || prefix.length > bestMatch.length) {
          bestMatch = prefix;
        }
      }
    }

    if (bestMatch != null) {
      return _stubs[bestMatch]!(request);
    }

    return MockResponse.notFound;
  }

  /// Get the full request log.
  List<MockRequest> get requestLog => List.unmodifiable(_requestLog);

  /// Reset all state (stubs, log, defaults).
  void reset() {
    _requestLog.clear();
    _stubs.clear();
    _staticStubs.clear();
    _isSetUp = false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Mock HTTP Client
// ═══════════════════════════════════════════════════════════════════════════

/// Lightweight HTTP client that delegates to [MockServer].
class MockHttpClient {
  Future<MockResponse> get(
    String path, {
    Map<String, String>? headers,
    Map<String, String>? queryParams,
  }) async {
    return MockServer.instance.handle(MockRequest(
      method: 'GET',
      path: path,
      headers: headers ?? {},
      queryParams: queryParams,
    ));
  }

  Future<MockResponse> post(
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    return MockServer.instance.handle(MockRequest(
      method: 'POST',
      path: path,
      headers: headers ?? {},
      body: body,
    ));
  }

  Future<MockResponse> put(
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    return MockServer.instance.handle(MockRequest(
      method: 'PUT',
      path: path,
      headers: headers ?? {},
      body: body,
    ));
  }

  Future<MockResponse> patch(
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    return MockServer.instance.handle(MockRequest(
      method: 'PATCH',
      path: path,
      headers: headers ?? {},
      body: body,
    ));
  }

  Future<MockResponse> delete(
    String path, {
    Map<String, String>? headers,
  }) async {
    return MockServer.instance.handle(MockRequest(
      method: 'DELETE',
      path: path,
      headers: headers ?? {},
    ));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Top-Level Helpers
// ═══════════════════════════════════════════════════════════════════════════

/// Set up the mock server with default route handlers.
void setupMockServer() {
  final server = MockServer.instance;
  if (!server._isSetUp) {
    server._registerDefaults();
    server._isSetUp = true;
  }
}

/// Tear down / reset the mock server between tests.
void resetMockServer() {
  MockServer.instance.reset();
}

/// Override a path with a static [MockResponse].
void stubResponse(String path, MockResponse response) {
  MockServer.instance.stubStatic(path, response);
}

/// Check whether a request with the given [method] and path substring was logged.
bool verifyRequest(String method, String pathSubstring) {
  return MockServer.instance.requestLog.any(
    (r) => r.method == method && r.path.contains(pathSubstring),
  );
}

/// Return the full request log from the mock server.
List<MockRequest> getMockRequestLog() {
  return MockServer.instance.requestLog;
}
