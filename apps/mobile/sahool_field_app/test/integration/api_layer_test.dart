/// SAHOOL Field App - API Layer Integration Tests
/// اختبارات تكامل طبقة واجهة البرمجة
///
/// Tests the MockServer/MockHttpClient stack to verify:
/// - Auth flow (login, refresh, logout) via mock API
/// - Fields CRUD operations via mock API
/// - Weather data retrieval
/// - Inventory operations
/// - Error handling (401, 404, 500)
/// - Request logging and verification
/// - Network error simulation
/// - Slow network simulation
import 'package:flutter_test/flutter_test.dart';

import '../../../integration_test/helpers/mock_server.dart';
import '../../../integration_test/fixtures/test_data.dart';

void main() {
  late MockHttpClient client;

  setUp(() {
    setupMockServer();
    client = MockHttpClient();
  });

  tearDown(() {
    resetMockServer();
  });

  // ===========================================================================
  // Auth API Integration
  // تكامل واجهة المصادقة
  // ===========================================================================

  group('Auth API Integration - تكامل واجهة المصادقة', () {
    test('login with valid credentials returns tokens', () async {
      // Act
      final response = await client.post(
        '/api/v1/auth/login',
        body: {
          'email': TestUsers.validEmail,
          'password': TestUsers.validPassword,
        },
      );

      // Assert
      expect(response.statusCode, equals(200));
      expect(response.body['access_token'], isNotNull);
      expect(response.body['refresh_token'], isNotNull);
      expect(response.body['token_type'], equals('Bearer'));
      expect(response.body['expires_in'], equals(3600));
      expect(response.body['user']['email'], equals(TestUsers.validEmail));
      expect(response.body['user']['role'], equals('farmer'));
    });

    test('login with admin credentials returns admin role', () async {
      final response = await client.post(
        '/api/v1/auth/login',
        body: {
          'email': TestUsers.adminEmail,
          'password': TestUsers.adminPassword,
        },
      );

      expect(response.statusCode, equals(200));
      expect(response.body['user']['role'], equals('admin'));
    });

    test('login with invalid credentials returns 401', () async {
      final response = await client.post(
        '/api/v1/auth/login',
        body: {
          'email': TestUsers.invalidEmail,
          'password': TestUsers.invalidPassword,
        },
      );

      expect(response.statusCode, equals(401));
      expect(response.body['error'], isNotNull);
    });

    test('login without body returns 400', () async {
      final response = await client.post('/api/v1/auth/login');

      expect(response.statusCode, equals(400));
    });

    test('token refresh returns new tokens', () async {
      final response = await client.post(
        '/api/v1/auth/refresh',
        body: {'refresh_token': 'mock_refresh_token'},
      );

      expect(response.statusCode, equals(200));
      expect(response.body['access_token'], isNotNull);
      expect(response.body['refresh_token'], isNotNull);
    });

    test('logout returns success', () async {
      final response = await client.post('/api/v1/auth/logout');

      expect(response.statusCode, equals(200));
      expect(response.body['message'], equals('Logged out'));
    });
  });

  // ===========================================================================
  // Fields API Integration
  // تكامل واجهة الحقول
  // ===========================================================================

  group('Fields API Integration - تكامل واجهة الحقول', () {
    test('GET /fields returns paginated list', () async {
      final response = await client.get('/api/v1/fields');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(2));
      expect(response.body['total'], equals(2));
      expect(response.body['page'], equals(1));

      final firstField = response.body['data'][0];
      expect(firstField['id'], equals(TestFields.field1['id']));
      expect(firstField['name'], isNotNull);
    });

    test('GET /fields/:id returns single field', () async {
      final response = await client.get('/api/v1/fields/field-test-001');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isNotNull);
    });

    test('POST /fields creates new field', () async {
      final response = await client.post(
        '/api/v1/fields',
        body: {
          'name': 'حقل جديد',
          'area': 4.5,
          'cropType': 'barley',
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['data']['id'], startsWith('field-new-'));
      expect(response.body['data']['name'], equals('حقل جديد'));
      expect(response.body['data']['area'], equals(4.5));
      expect(response.body['message'], contains('بنجاح'));
    });

    test('PUT /fields/:id updates field', () async {
      final response = await client.put(
        '/api/v1/fields/field-test-001',
        body: {'name': 'اسم محدث'},
      );

      expect(response.statusCode, equals(200));
      expect(response.body['data']['name'], equals('اسم محدث'));
      expect(response.body['message'], contains('بنجاح'));
    });

    test('PATCH /fields/:id partially updates field', () async {
      final response = await client.patch(
        '/api/v1/fields/field-test-001',
        body: {'area': 10.0},
      );

      expect(response.statusCode, equals(200));
    });

    test('DELETE /fields/:id deletes field', () async {
      final response = await client.delete('/api/v1/fields/field-test-001');

      expect(response.statusCode, equals(200));
      expect(response.body['message'], contains('حذف'));
    });
  });

  // ===========================================================================
  // Weather API Integration
  // تكامل واجهة الطقس
  // ===========================================================================

  group('Weather API Integration - تكامل واجهة الطقس', () {
    test('GET /weather returns current conditions with forecast', () async {
      final response = await client.get('/api/v1/weather');

      expect(response.statusCode, equals(200));
      final data = response.body['data'];
      expect(data['current'], isNotNull);
      expect(data['current']['temperature'], isA<num>());
      expect(data['current']['humidity'], isA<num>());
      expect(data['current']['windSpeed'], isA<num>());

      // Hourly forecast
      expect(data['hourly'], isList);
      expect(data['hourly'].length, equals(24));

      // Daily forecast
      expect(data['daily'], isList);
      expect(data['daily'].length, equals(7));

      // Agricultural impacts
      expect(data['agricultural_impacts'], isList);
      expect(data['agricultural_impacts'].length, greaterThan(0));
    });
  });

  // ===========================================================================
  // Inventory API Integration
  // تكامل واجهة المخزون
  // ===========================================================================

  group('Inventory API Integration - تكامل واجهة المخزون', () {
    test('GET /inventory returns items with low stock count', () async {
      final response = await client.get('/api/v1/inventory');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['total'], equals(4));
      expect(response.body['lowStockCount'], equals(1));
    });

    test('POST /inventory creates new item', () async {
      final response = await client.post(
        '/api/v1/inventory',
        body: {
          'name': 'سماد يوريا',
          'type': 'fertilizer',
          'quantity': 100,
          'unit': 'kg',
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['data']['id'], startsWith('inv-new-'));
    });

    test('PUT /inventory/:id updates item', () async {
      final response = await client.put(
        '/api/v1/inventory/inv-001',
        body: {'quantity': 50},
      );

      expect(response.statusCode, equals(200));
    });

    test('DELETE /inventory/:id removes item', () async {
      final response = await client.delete('/api/v1/inventory/inv-001');

      expect(response.statusCode, equals(200));
    });
  });

  // ===========================================================================
  // VRA & Satellite API Integration
  // تكامل واجهة الزراعة الدقيقة والأقمار الصناعية
  // ===========================================================================

  group('VRA API Integration - تكامل واجهة الزراعة الدقيقة', () {
    test('GET /vra returns prescriptions', () async {
      final response = await client.get('/api/v1/vra');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['total'], equals(1));
    });

    test('POST /vra creates new prescription', () async {
      final response = await client.post(
        '/api/v1/vra',
        body: {
          'fieldId': 'field-test-001',
          'type': 'fertilizer',
          'zones': [
            {'area': 2.0, 'rate': 46},
            {'area': 3.0, 'rate': 30},
          ],
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['data']['status'], equals('draft'));
    });
  });

  group('Satellite API Integration - تكامل واجهة الأقمار الصناعية', () {
    test('GET /satellite returns imagery and history', () async {
      final response = await client.get('/api/v1/satellite');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isNotNull);
      expect(response.body['history'], isNotNull);
    });
  });

  // ===========================================================================
  // Error Handling
  // معالجة الأخطاء
  // ===========================================================================

  group('Error Handling - معالجة الأخطاء', () {
    test('unknown endpoint returns 404', () async {
      final response = await client.get('/api/v1/nonexistent');

      expect(response.statusCode, equals(404));
      expect(response.body['error'], equals('Not Found'));
      expect(response.body['message'], equals('غير موجود'));
    });

    test('stubbed 401 returns unauthorized', () async {
      stubResponse('/api/v1/fields', MockResponse.unauthorized);

      final response = await client.get('/api/v1/fields');

      expect(response.statusCode, equals(401));
      expect(response.body['error'], equals('Unauthorized'));
    });

    test('stubbed 500 returns server error', () async {
      stubResponse('/api/v1/fields', MockResponse.serverError);

      final response = await client.get('/api/v1/fields');

      expect(response.statusCode, equals(500));
    });

    test('custom error stub works', () async {
      stubError('/api/v1/fields', 422, 'Validation failed');

      final response = await client.get('/api/v1/fields');

      expect(response.statusCode, equals(422));
      expect(response.body['message'], equals('Validation failed'));
    });
  });

  // ===========================================================================
  // Request Logging & Verification
  // تسجيل الطلبات والتحقق
  // ===========================================================================

  group('Request Logging - تسجيل الطلبات', () {
    test('requests are logged in order', () async {
      await client.get('/api/v1/fields');
      await client.post('/api/v1/fields', body: {'name': 'Test'});
      await client.delete('/api/v1/fields/field-001');

      final log = getMockRequestLog();
      expect(log.length, equals(3));
      expect(log[0].method, equals('GET'));
      expect(log[1].method, equals('POST'));
      expect(log[2].method, equals('DELETE'));
    });

    test('verifyRequest checks method and path', () async {
      await client.post(
        '/api/v1/auth/login',
        body: {'email': 'test@test.com', 'password': 'pass'},
      );

      expect(verifyRequest('POST', '/auth/login'), isTrue);
      expect(verifyRequest('GET', '/auth/login'), isFalse);
      expect(verifyRequest('POST', '/fields'), isFalse);
    });

    test('countRequests counts matching requests', () async {
      await client.get('/api/v1/fields');
      await client.get('/api/v1/fields');
      await client.get('/api/v1/weather');

      expect(countRequests('/fields'), equals(2));
      expect(countRequests('/weather'), equals(1));
    });

    test('request body is captured', () async {
      final body = {'name': 'حقل اختبار', 'area': 5.0};
      await client.post('/api/v1/fields', body: body);

      final log = getMockRequestLog();
      expect(log.last.body, equals(body));
    });

    test('clearLog resets request history', () async {
      await client.get('/api/v1/fields');
      expect(getMockRequestLog().length, equals(1));

      MockServer.instance.clearLog();
      expect(getMockRequestLog().length, equals(0));
    });
  });

  // ===========================================================================
  // Stub Overrides
  // تجاوزات الاستجابة
  // ===========================================================================

  group('Stub Overrides - تجاوزات الاستجابة', () {
    test('stub overrides default response', () async {
      // Default returns field list
      final defaultResp = await client.get('/api/v1/fields');
      expect(defaultResp.statusCode, equals(200));
      expect(defaultResp.body['data'], isList);

      // Override with custom
      stubResponse(
        '/api/v1/fields',
        MockResponse.success({'data': [], 'total': 0, 'page': 1, 'limit': 20}),
      );

      final overrideResp = await client.get('/api/v1/fields');
      expect(overrideResp.statusCode, equals(200));
      expect(overrideResp.body['data'], isEmpty);
      expect(overrideResp.body['total'], equals(0));
    });

    test('dynamic stub using request handler', () async {
      MockServer.instance.stub('/api/v1/fields', (request) {
        if (request.method == 'POST') {
          return MockResponse.created({
            'data': {'id': 'custom-id', ...?request.body},
          });
        }
        return MockResponse.success({'data': [], 'total': 0});
      });

      final getResp = await client.get('/api/v1/fields');
      expect(getResp.body['total'], equals(0));

      final postResp = await client.post(
        '/api/v1/fields',
        body: {'name': 'Dynamic'},
      );
      expect(postResp.statusCode, equals(201));
      expect(postResp.body['data']['id'], equals('custom-id'));
      expect(postResp.body['data']['name'], equals('Dynamic'));
    });
  });

  // ===========================================================================
  // Network Configuration
  // تكوين الشبكة
  // ===========================================================================

  group('Network Configuration - تكوين الشبكة', () {
    test('slow network config increases latency', () async {
      MockServer.instance.configure(MockServerConfig.slowNetwork);

      final stopwatch = Stopwatch()..start();
      await client.get('/api/v1/fields');
      stopwatch.stop();

      // With 2000ms delay, response should take at least 1900ms
      expect(stopwatch.elapsedMilliseconds, greaterThan(1900));
    });

    test('unstable network config may return errors', () async {
      MockServer.instance.configure(const MockServerConfig(
        simulateErrors: true,
        errorRate: 1.0, // 100% error rate for deterministic test
      ));

      final response = await client.get('/api/v1/fields');
      expect(response.statusCode, equals(500));
    });

    test('custom delay config applies', () async {
      MockServer.instance.configure(const MockServerConfig(
        responseDelayMs: 50,
      ));

      final stopwatch = Stopwatch()..start();
      await client.get('/api/v1/fields');
      stopwatch.stop();

      expect(stopwatch.elapsedMilliseconds, greaterThanOrEqualTo(45));
    });
  });

  // ===========================================================================
  // Auth + API Flow Integration
  // تكامل المصادقة مع واجهة البرمجة
  // ===========================================================================

  group('Auth + API Flow - تكامل المصادقة مع الواجهة', () {
    test('full login → fetch data → logout flow', () async {
      // Step 1: Login
      final loginResp = await client.post(
        '/api/v1/auth/login',
        body: {
          'email': TestUsers.validEmail,
          'password': TestUsers.validPassword,
        },
      );
      expect(loginResp.statusCode, equals(200));
      final token = loginResp.body['access_token'];
      expect(token, isNotNull);

      // Step 2: Fetch fields with token
      final fieldsResp = await client.get(
        '/api/v1/fields',
        headers: {'Authorization': 'Bearer $token'},
      );
      expect(fieldsResp.statusCode, equals(200));
      expect(fieldsResp.body['data'].length, greaterThan(0));

      // Step 3: Fetch weather
      final weatherResp = await client.get('/api/v1/weather');
      expect(weatherResp.statusCode, equals(200));

      // Step 4: Logout
      final logoutResp = await client.post('/api/v1/auth/logout');
      expect(logoutResp.statusCode, equals(200));

      // Verify request sequence
      final log = getMockRequestLog();
      expect(log.length, equals(4));
      expect(log[0].path, contains('/auth/login'));
      expect(log[1].path, contains('/fields'));
      expect(log[2].path, contains('/weather'));
      expect(log[3].path, contains('/auth/logout'));
    });

    test('token refresh mid-session', () async {
      // Login
      await client.post('/api/v1/auth/login', body: {
        'email': TestUsers.validEmail,
        'password': TestUsers.validPassword,
      });

      // Refresh token
      final refreshResp = await client.post('/api/v1/auth/refresh');
      expect(refreshResp.statusCode, equals(200));
      final newToken = refreshResp.body['access_token'];
      expect(newToken, isNotNull);

      // Continue using API with new token
      final resp = await client.get(
        '/api/v1/fields',
        headers: {'Authorization': 'Bearer $newToken'},
      );
      expect(resp.statusCode, equals(200));
    });
  });
}
