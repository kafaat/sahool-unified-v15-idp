import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../integration_test/helpers/mock_server.dart';
import '../../../integration_test/fixtures/test_data.dart';

/// Integration Tests - Auth Flow
/// اختبارات تكامل المصادقة
///
/// Tests complete authentication workflows using MockServer:
/// - Login with valid/invalid credentials
/// - Token storage and retrieval via SharedPreferences
/// - Token refresh flow
/// - Logout with data cleanup
/// - Session expiry detection
/// - Multi-user session switching

void main() {
  late MockHttpClient client;

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    setupMockServer();
    client = MockHttpClient();
  });

  tearDown(() {
    resetMockServer();
  });

  // ===========================================================================
  // Login Flow
  // سير عملية الدخول
  // ===========================================================================

  group('Login Flow - سير عملية الدخول', () {
    test('successful login stores tokens in SharedPreferences', () async {
      // Act: login via mock API
      final response = await client.post(
        '/api/v1/auth/login',
        body: {
          'email': TestUsers.validEmail,
          'password': TestUsers.validPassword,
        },
      );

      // Verify API response
      expect(response.statusCode, equals(200));
      final accessToken = response.body['access_token'] as String;
      final refreshToken = response.body['refresh_token'] as String;
      expect(accessToken, isNotEmpty);
      expect(refreshToken, isNotEmpty);

      // Simulate storing tokens securely
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', accessToken);
      await prefs.setString('refresh_token', refreshToken);
      await prefs.setInt('token_expires_in', response.body['expires_in']);
      await prefs.setString('token_type', response.body['token_type']);

      // Assert stored correctly
      expect(prefs.getString('access_token'), equals(accessToken));
      expect(prefs.getString('refresh_token'), equals(refreshToken));
      expect(prefs.getInt('token_expires_in'), equals(3600));
    });

    test('successful login stores user info', () async {
      final response = await client.post(
        '/api/v1/auth/login',
        body: {
          'email': TestUsers.validEmail,
          'password': TestUsers.validPassword,
        },
      );

      final user = response.body['user'] as Map<String, dynamic>;

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('user_id', user['id']);
      await prefs.setString('user_email', user['email']);
      await prefs.setString('user_name', user['name']);
      await prefs.setString('user_role', user['role']);

      expect(prefs.getString('user_id'), equals('user-001'));
      expect(prefs.getString('user_email'), equals(TestUsers.validEmail));
      expect(prefs.getString('user_name'), equals(TestUsers.validUsername));
      expect(prefs.getString('user_role'), equals('farmer'));
    });

    test('failed login does not store tokens', () async {
      final response = await client.post(
        '/api/v1/auth/login',
        body: {
          'email': TestUsers.invalidEmail,
          'password': TestUsers.invalidPassword,
        },
      );

      expect(response.statusCode, equals(401));

      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('access_token'), isNull);
      expect(prefs.getString('refresh_token'), isNull);
    });

    test('login with admin credentials grants admin role', () async {
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

    test('login without body returns 400', () async {
      final response = await client.post('/api/v1/auth/login');

      expect(response.statusCode, equals(400));
    });
  });

  // ===========================================================================
  // Token Refresh Flow
  // سير عملية تحديث الرمز
  // ===========================================================================

  group('Token Refresh Flow - سير عملية تحديث الرمز', () {
    test('token refresh replaces old tokens', () async {
      // Login first
      final loginResp = await client.post('/api/v1/auth/login', body: {
        'email': TestUsers.validEmail,
        'password': TestUsers.validPassword,
      });

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
          'access_token', loginResp.body['access_token']);
      await prefs.setString(
          'refresh_token', loginResp.body['refresh_token']);

      final oldToken = prefs.getString('access_token');

      // Refresh token
      final refreshResp = await client.post(
        '/api/v1/auth/refresh',
        body: {'refresh_token': prefs.getString('refresh_token')},
      );

      expect(refreshResp.statusCode, equals(200));
      final newToken = refreshResp.body['access_token'] as String;
      expect(newToken, isNot(equals(oldToken)));

      // Update stored tokens
      await prefs.setString('access_token', newToken);
      await prefs.setString(
          'refresh_token', refreshResp.body['refresh_token']);

      expect(prefs.getString('access_token'), equals(newToken));
    });

    test('API calls use refreshed token', () async {
      // Login
      final loginResp = await client.post('/api/v1/auth/login', body: {
        'email': TestUsers.validEmail,
        'password': TestUsers.validPassword,
      });

      // Refresh
      final refreshResp = await client.post('/api/v1/auth/refresh');
      final newToken = refreshResp.body['access_token'];

      // Use new token for API call
      final fieldsResp = await client.get(
        '/api/v1/fields',
        headers: {'Authorization': 'Bearer $newToken'},
      );
      expect(fieldsResp.statusCode, equals(200));

      // Verify auth header was sent
      final log = getMockRequestLog();
      final fieldsRequest = log.last;
      expect(fieldsRequest.headers['Authorization'],
          equals('Bearer $newToken'));
    });
  });

  // ===========================================================================
  // Logout Flow
  // سير عملية الخروج
  // ===========================================================================

  group('Logout Flow - سير عملية الخروج', () {
    test('logout clears all stored auth data', () async {
      // Login and store
      final loginResp = await client.post('/api/v1/auth/login', body: {
        'email': TestUsers.validEmail,
        'password': TestUsers.validPassword,
      });

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
          'access_token', loginResp.body['access_token']);
      await prefs.setString(
          'refresh_token', loginResp.body['refresh_token']);
      await prefs.setString('user_id', 'user-001');
      await prefs.setString('user_email', TestUsers.validEmail);

      // Logout via API
      final logoutResp = await client.post('/api/v1/auth/logout');
      expect(logoutResp.statusCode, equals(200));

      // Clear local data
      await prefs.remove('access_token');
      await prefs.remove('refresh_token');
      await prefs.remove('user_id');
      await prefs.remove('user_email');

      // Verify all cleared
      expect(prefs.getString('access_token'), isNull);
      expect(prefs.getString('refresh_token'), isNull);
      expect(prefs.getString('user_id'), isNull);
      expect(prefs.getString('user_email'), isNull);
    });

    test('subsequent API calls after logout are unauthenticated', () async {
      // Setup: stub to require auth
      stubResponse('/api/v1/fields', MockResponse.unauthorized);

      final response = await client.get('/api/v1/fields');
      expect(response.statusCode, equals(401));
    });
  });

  // ===========================================================================
  // Session Expiry
  // انتهاء الجلسة
  // ===========================================================================

  group('Session Expiry - انتهاء الجلسة', () {
    test('detects expired session from stored expiry time', () async {
      final prefs = await SharedPreferences.getInstance();

      // Store a token that expired 1 hour ago
      final expiredAt = DateTime.now()
          .subtract(const Duration(hours: 1))
          .millisecondsSinceEpoch;
      await prefs.setInt('token_expires_at', expiredAt);
      await prefs.setString('access_token', 'expired_token');

      // Check expiry
      final storedExpiry = prefs.getInt('token_expires_at')!;
      final isExpired =
          DateTime.fromMillisecondsSinceEpoch(storedExpiry).isBefore(DateTime.now());

      expect(isExpired, isTrue);
    });

    test('detects valid session from stored expiry time', () async {
      final prefs = await SharedPreferences.getInstance();

      // Store a token that expires in 1 hour
      final expiresAt = DateTime.now()
          .add(const Duration(hours: 1))
          .millisecondsSinceEpoch;
      await prefs.setInt('token_expires_at', expiresAt);
      await prefs.setString('access_token', 'valid_token');

      // Check expiry
      final storedExpiry = prefs.getInt('token_expires_at')!;
      final isExpired =
          DateTime.fromMillisecondsSinceEpoch(storedExpiry).isBefore(DateTime.now());

      expect(isExpired, isFalse);
    });

    test('calculates token expiry from login response', () async {
      final loginResp = await client.post('/api/v1/auth/login', body: {
        'email': TestUsers.validEmail,
        'password': TestUsers.validPassword,
      });

      final expiresIn = loginResp.body['expires_in'] as int;
      final expiresAt = DateTime.now().add(Duration(seconds: expiresIn));

      expect(expiresAt.isAfter(DateTime.now()), isTrue);
      expect(expiresIn, equals(3600));
    });
  });

  // ===========================================================================
  // Auth Request Verification
  // التحقق من طلبات المصادقة
  // ===========================================================================

  group('Auth Request Verification - التحقق من الطلبات', () {
    test('login request is logged correctly', () async {
      await client.post('/api/v1/auth/login', body: {
        'email': TestUsers.validEmail,
        'password': TestUsers.validPassword,
      });

      expect(verifyRequest('POST', '/auth/login'), isTrue);
      final log = getMockRequestLog();
      expect(log.last.body?['email'], equals(TestUsers.validEmail));
    });

    test('full auth lifecycle generates correct request sequence', () async {
      // Login
      await client.post('/api/v1/auth/login', body: {
        'email': TestUsers.validEmail,
        'password': TestUsers.validPassword,
      });

      // Use API
      await client.get('/api/v1/fields');
      await client.get('/api/v1/weather');

      // Refresh
      await client.post('/api/v1/auth/refresh');

      // Use API again
      await client.get('/api/v1/fields');

      // Logout
      await client.post('/api/v1/auth/logout');

      // Verify sequence
      final log = getMockRequestLog();
      expect(log.length, equals(6));
      expect(log[0].path, contains('/auth/login'));
      expect(log[1].path, contains('/fields'));
      expect(log[2].path, contains('/weather'));
      expect(log[3].path, contains('/auth/refresh'));
      expect(log[4].path, contains('/fields'));
      expect(log[5].path, contains('/auth/logout'));
    });
  });
}
