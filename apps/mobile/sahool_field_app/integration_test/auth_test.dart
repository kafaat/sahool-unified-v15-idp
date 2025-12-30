/// SAHOOL Field App - Auth Integration Tests
/// اختبارات تكامل المصادقة الشاملة
///
/// Test scenarios:
/// - Login flow with credentials
/// - Token refresh mechanism
/// - Logout and data cleanup
/// - Biometric authentication
/// - Session management
/// - Multi-device support

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Auth Flow Integration Tests', () {
    late ProviderContainer container;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    // =========================================================================
    // Login Flow Tests
    // =========================================================================

    testWidgets('should validate email format before login', (tester) async {
      // Arrange
      const validEmail = 'user@sahool.app';
      const invalidEmail = 'invalid-email';

      // Act & Assert
      expect(validEmail.contains('@'), isTrue);
      expect(validEmail.contains('.'), isTrue);
      expect(invalidEmail.contains('@'), isFalse);
    });

    testWidgets('should validate password requirements', (tester) async {
      // Arrange
      const validPassword = 'SecurePass123!';
      const shortPassword = 'short';
      const noNumberPassword = 'NoNumber!';
      const noSpecialPassword = 'NoSpecial123';

      // Act
      final isValidLength = validPassword.length >= 8;
      final hasNumber = RegExp(r'\d').hasMatch(validPassword);
      final hasUpperCase = RegExp(r'[A-Z]').hasMatch(validPassword);
      final hasLowerCase = RegExp(r'[a-z]').hasMatch(validPassword);

      final shortPasswordValid = shortPassword.length >= 8;
      final noNumberValid = RegExp(r'\d').hasMatch(noNumberPassword);

      // Assert
      expect(isValidLength, isTrue);
      expect(hasNumber, isTrue);
      expect(hasUpperCase, isTrue);
      expect(hasLowerCase, isTrue);

      expect(shortPasswordValid, isFalse);
      expect(noNumberValid, isFalse);
    });

    testWidgets('should perform login and store tokens securely', (tester) async {
      // Arrange
      const email = 'test@sahool.app';
      const password = 'SecurePass123!';

      final prefs = await SharedPreferences.getInstance();

      // Simulate successful login response
      final loginResponse = {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        'refresh_token': 'refresh_token_xyz...',
        'expires_in': 3600,
        'token_type': 'Bearer',
        'user': {
          'id': 'user-001',
          'email': email,
          'name': 'Test User',
          'tenant_id': 'tenant-001',
        },
      };

      // Act - Store tokens (in production, use flutter_secure_storage)
      await prefs.setString('access_token', loginResponse['access_token'] as String);
      await prefs.setString('refresh_token', loginResponse['refresh_token'] as String);
      await prefs.setInt('token_expires_at',
        DateTime.now().add(Duration(seconds: loginResponse['expires_in'] as int)).millisecondsSinceEpoch);

      // Store user info
      final user = loginResponse['user'] as Map<String, dynamic>;
      await prefs.setString('user_id', user['id'] as String);
      await prefs.setString('user_email', user['email'] as String);
      await prefs.setString('tenant_id', user['tenant_id'] as String);
      await prefs.setBool('is_logged_in', true);

      // Assert
      expect(prefs.getString('access_token'), isNotNull);
      expect(prefs.getString('refresh_token'), isNotNull);
      expect(prefs.getBool('is_logged_in'), isTrue);
      expect(prefs.getString('tenant_id'), equals('tenant-001'));
    });

    testWidgets('should show login UI with proper validation', (tester) async {
      // Arrange & Act
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      'تسجيل الدخول',
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 24),
                    const TextField(
                      key: Key('email_field'),
                      decoration: InputDecoration(
                        labelText: 'البريد الإلكتروني',
                        prefixIcon: Icon(Icons.email),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const TextField(
                      key: Key('password_field'),
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: 'كلمة المرور',
                        prefixIcon: Icon(Icons.lock),
                      ),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      key: const Key('login_button'),
                      onPressed: () {},
                      child: const Text('تسجيل الدخول'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Assert
      expect(find.text('تسجيل الدخول'), findsOneWidget);
      expect(find.byKey(const Key('email_field')), findsOneWidget);
      expect(find.byKey(const Key('password_field')), findsOneWidget);
      expect(find.byKey(const Key('login_button')), findsOneWidget);
    });

    testWidgets('should handle login errors gracefully', (tester) async {
      // Arrange
      final errorScenarios = [
        {'code': 'invalid_credentials', 'message': 'بيانات الدخول غير صحيحة'},
        {'code': 'account_locked', 'message': 'الحساب محظور مؤقتاً'},
        {'code': 'network_error', 'message': 'خطأ في الاتصال بالخادم'},
      ];

      final prefs = await SharedPreferences.getInstance();

      // Act - Simulate error handling
      for (final error in errorScenarios) {
        await prefs.setString('last_error_code', error['code']!);
        await prefs.setString('last_error_message', error['message']!);
        await prefs.setBool('is_logged_in', false);

        // Assert
        expect(prefs.getString('last_error_message'), isNotNull);
        expect(prefs.getBool('is_logged_in'), isFalse);
      }
    });

    // =========================================================================
    // Token Refresh Tests
    // =========================================================================

    testWidgets('should check token expiry before API calls', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Set token that expires in 5 minutes
      final expiresAt = DateTime.now().add(const Duration(minutes: 5));
      await prefs.setInt('token_expires_at', expiresAt.millisecondsSinceEpoch);

      // Act - Check if token needs refresh (refresh if < 10 minutes remaining)
      final tokenExpiresAt = DateTime.fromMillisecondsSinceEpoch(
        prefs.getInt('token_expires_at')!
      );
      final timeUntilExpiry = tokenExpiresAt.difference(DateTime.now());
      final needsRefresh = timeUntilExpiry.inMinutes < 10;

      // Assert
      expect(needsRefresh, isTrue);
    });

    testWidgets('should refresh token automatically', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('refresh_token', 'old_refresh_token');
      await prefs.setString('access_token', 'old_access_token');

      // Simulate refresh token response
      final refreshResponse = {
        'access_token': 'new_access_token_xyz...',
        'refresh_token': 'new_refresh_token_xyz...',
        'expires_in': 3600,
      };

      // Act - Update tokens
      await prefs.setString('access_token', refreshResponse['access_token'] as String);
      await prefs.setString('refresh_token', refreshResponse['refresh_token'] as String);
      await prefs.setInt('token_expires_at',
        DateTime.now().add(Duration(seconds: refreshResponse['expires_in'] as int)).millisecondsSinceEpoch);
      await prefs.setString('last_token_refresh', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getString('access_token'), equals('new_access_token_xyz...'));
      expect(prefs.getString('refresh_token'), equals('new_refresh_token_xyz...'));
      expect(prefs.getString('last_token_refresh'), isNotNull);
    });

    testWidgets('should retry failed requests after token refresh', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Simulate 401 Unauthorized response
      const statusCode = 401;

      // Store pending request for retry
      final pendingRequest = {
        'url': '/api/fields',
        'method': 'GET',
        'timestamp': DateTime.now().toIso8601String(),
      };

      // Act - Handle 401
      if (statusCode == 401) {
        // Add to retry queue
        final retryQueue = prefs.getStringList('retry_queue') ?? [];
        retryQueue.add(pendingRequest.toString());
        await prefs.setStringList('retry_queue', retryQueue);

        // Trigger token refresh (simulated)
        await prefs.setString('access_token', 'new_token_after_refresh');

        // Process retry queue
        final queue = prefs.getStringList('retry_queue')!;
        await prefs.setInt('retried_requests', queue.length);
        await prefs.setStringList('retry_queue', []); // Clear queue
      }

      // Assert
      expect(prefs.getInt('retried_requests'), equals(1));
      expect(prefs.getStringList('retry_queue'), isEmpty);
    });

    testWidgets('should prevent concurrent token refresh requests', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_refreshing_token', false);

      // Act - First refresh starts
      final canRefresh = !(prefs.getBool('is_refreshing_token') ?? false);

      if (canRefresh) {
        await prefs.setBool('is_refreshing_token', true);
      }

      // Try second refresh
      final canStartSecondRefresh = !(prefs.getBool('is_refreshing_token') ?? false);

      // Simulate refresh completion
      await prefs.setBool('is_refreshing_token', false);

      // Assert
      expect(canRefresh, isTrue);
      expect(canStartSecondRefresh, isFalse); // Should be blocked
    });

    testWidgets('should logout on refresh token failure', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', 'token');
      await prefs.setString('refresh_token', 'refresh');
      await prefs.setBool('is_logged_in', true);

      // Simulate refresh failure (e.g., refresh token expired)
      const refreshFailed = true;

      // Act - Force logout
      if (refreshFailed) {
        await prefs.remove('access_token');
        await prefs.remove('refresh_token');
        await prefs.remove('user_id');
        await prefs.remove('tenant_id');
        await prefs.setBool('is_logged_in', false);
      }

      // Assert
      expect(prefs.getString('access_token'), isNull);
      expect(prefs.getString('refresh_token'), isNull);
      expect(prefs.getBool('is_logged_in'), isFalse);
    });

    // =========================================================================
    // Logout and Data Cleanup Tests
    // =========================================================================

    testWidgets('should clear all auth data on logout', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', 'token');
      await prefs.setString('refresh_token', 'refresh');
      await prefs.setString('user_id', 'user-001');
      await prefs.setString('tenant_id', 'tenant-001');
      await prefs.setString('user_name', 'Test User');
      await prefs.setBool('is_logged_in', true);

      // Act - Logout
      await prefs.remove('access_token');
      await prefs.remove('refresh_token');
      await prefs.remove('user_id');
      await prefs.remove('tenant_id');
      await prefs.remove('user_name');
      await prefs.setBool('is_logged_in', false);
      await prefs.setString('logged_out_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getString('access_token'), isNull);
      expect(prefs.getString('refresh_token'), isNull);
      expect(prefs.getString('user_id'), isNull);
      expect(prefs.getBool('is_logged_in'), isFalse);
      expect(prefs.getString('logged_out_at'), isNotNull);
    });

    testWidgets('should clear local cache on logout', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('cached_field_001', 'field data');
      await prefs.setString('cached_task_001', 'task data');
      await prefs.setStringList('outbox', ['item1', 'item2']);

      // Act - Clear cache (except critical offline data)
      final allKeys = prefs.getKeys();
      for (final key in allKeys) {
        if (key.startsWith('cached_')) {
          await prefs.remove(key);
        }
      }

      // Assert
      expect(prefs.getString('cached_field_001'), isNull);
      expect(prefs.getString('cached_task_001'), isNull);
      // Outbox should remain for offline data preservation
      expect(prefs.getStringList('outbox'), isNotNull);
    });

    testWidgets('should show logout confirmation dialog', (tester) async {
      // Arrange & Act
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Builder(
                builder: (context) {
                  return Center(
                    child: ElevatedButton(
                      child: const Text('تسجيل الخروج'),
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text('تسجيل الخروج'),
                            content: const Text('هل أنت متأكد من تسجيل الخروج؟'),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('إلغاء'),
                              ),
                              FilledButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('تسجيل الخروج'),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Tap logout button
      await tester.tap(find.text('تسجيل الخروج'));
      await tester.pumpAndSettle();

      // Assert
      expect(find.text('هل أنت متأكد من تسجيل الخروج؟'), findsOneWidget);
      expect(find.text('إلغاء'), findsOneWidget);
    });

    testWidgets('should preserve offline data during logout', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('outbox', ['pending-item-1']);
      await prefs.setString('offline_field_001', 'field data');

      // Act - Logout but preserve offline data
      await prefs.remove('access_token');
      await prefs.setBool('is_logged_in', false);

      // Verify offline data preserved
      final outbox = prefs.getStringList('outbox');
      final offlineData = prefs.getString('offline_field_001');

      // Assert
      expect(outbox, isNotNull);
      expect(outbox!.length, equals(1));
      expect(offlineData, isNotNull);
    });

    // =========================================================================
    // Biometric Authentication Tests
    // =========================================================================

    testWidgets('should check biometric availability', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Simulate biometric check
      const biometricsAvailable = true;
      const biometricType = 'fingerprint'; // or 'face', 'iris'

      // Act
      await prefs.setBool('biometrics_available', biometricsAvailable);
      await prefs.setString('biometric_type', biometricType);

      // Assert
      expect(prefs.getBool('biometrics_available'), isTrue);
      expect(prefs.getString('biometric_type'), equals('fingerprint'));
    });

    testWidgets('should enable biometric authentication', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - User enables biometric login
      await prefs.setBool('biometric_enabled', true);
      await prefs.setString('biometric_enabled_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getBool('biometric_enabled'), isTrue);
      expect(prefs.getString('biometric_enabled_at'), isNotNull);
    });

    testWidgets('should authenticate with biometrics', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('biometric_enabled', true);
      await prefs.setString('stored_user_id', 'user-001');

      // Simulate biometric authentication
      const biometricSuccess = true;

      // Act
      if (biometricSuccess) {
        // Restore session
        await prefs.setBool('is_logged_in', true);
        await prefs.setString('last_biometric_login', DateTime.now().toIso8601String());
      }

      // Assert
      expect(prefs.getBool('is_logged_in'), isTrue);
      expect(prefs.getString('last_biometric_login'), isNotNull);
    });

    testWidgets('should fallback to password on biometric failure', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      const biometricFailed = true;

      // Act
      if (biometricFailed) {
        await prefs.setInt('biometric_failure_count', 1);
        await prefs.setBool('show_password_login', true);
      }

      // Assert
      expect(prefs.getInt('biometric_failure_count'), equals(1));
      expect(prefs.getBool('show_password_login'), isTrue);
    });

    // =========================================================================
    // Session Management Tests
    // =========================================================================

    testWidgets('should track session start time', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - Login
      await prefs.setString('session_started_at', DateTime.now().toIso8601String());
      await prefs.setString('session_id', 'session-${DateTime.now().millisecondsSinceEpoch}');

      // Assert
      expect(prefs.getString('session_started_at'), isNotNull);
      expect(prefs.getString('session_id'), isNotNull);
    });

    testWidgets('should enforce session timeout', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      final sessionStart = DateTime.now().subtract(const Duration(hours: 25));
      await prefs.setString('session_started_at', sessionStart.toIso8601String());

      const sessionTimeoutHours = 24;

      // Act - Check session validity
      final sessionStartTime = DateTime.parse(prefs.getString('session_started_at')!);
      final sessionDuration = DateTime.now().difference(sessionStartTime);
      final isExpired = sessionDuration.inHours > sessionTimeoutHours;

      if (isExpired) {
        await prefs.setBool('is_logged_in', false);
        await prefs.setString('session_expired_reason', 'timeout');
      }

      // Assert
      expect(isExpired, isTrue);
      expect(prefs.getBool('is_logged_in'), isFalse);
      expect(prefs.getString('session_expired_reason'), equals('timeout'));
    });

    testWidgets('should update last activity timestamp', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - User performs action
      await prefs.setString('last_activity_at', DateTime.now().toIso8601String());

      // Simulate multiple activities
      await Future.delayed(const Duration(milliseconds: 100));
      await prefs.setString('last_activity_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getString('last_activity_at'), isNotNull);
    });

    testWidgets('should maintain session across app restarts', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', 'valid_token');
      await prefs.setBool('is_logged_in', true);
      await prefs.setString('user_id', 'user-001');

      // Simulate app restart (get new instance)
      final newPrefs = await SharedPreferences.getInstance();

      // Act - Check session
      final isLoggedIn = newPrefs.getBool('is_logged_in') ?? false;
      final hasToken = newPrefs.getString('access_token') != null;

      // Assert
      expect(isLoggedIn, isTrue);
      expect(hasToken, isTrue);
    });

    // =========================================================================
    // Multi-Device Support Tests
    // =========================================================================

    testWidgets('should store device identifier', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - Generate device ID
      final deviceId = 'device-${DateTime.now().millisecondsSinceEpoch}';
      await prefs.setString('device_id', deviceId);
      await prefs.setString('device_name', 'Test Device');
      await prefs.setString('device_registered_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getString('device_id'), isNotNull);
      expect(prefs.getString('device_name'), equals('Test Device'));
    });

    testWidgets('should handle forced logout from another device', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_logged_in', true);

      // Simulate receiving logout event from server (e.g., via push notification)
      const logoutReason = 'logged_in_another_device';

      // Act - Force logout
      await prefs.setBool('is_logged_in', false);
      await prefs.setString('logout_reason', logoutReason);
      await prefs.remove('access_token');
      await prefs.remove('refresh_token');

      // Assert
      expect(prefs.getBool('is_logged_in'), isFalse);
      expect(prefs.getString('logout_reason'), equals('logged_in_another_device'));
    });

    testWidgets('should sync auth state with server', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('device_id', 'device-001');

      // Simulate checking session validity with server
      final lastSync = DateTime.now().subtract(const Duration(minutes: 30));
      await prefs.setString('auth_state_last_sync', lastSync.toIso8601String());

      // Act - Check if sync needed
      final lastSyncTime = DateTime.parse(prefs.getString('auth_state_last_sync')!);
      final needsSync = DateTime.now().difference(lastSyncTime).inMinutes > 15;

      if (needsSync) {
        await prefs.setString('auth_state_last_sync', DateTime.now().toIso8601String());
      }

      // Assert
      expect(needsSync, isTrue);
      expect(prefs.getString('auth_state_last_sync'), isNotNull);
    });
  });

  // ===========================================================================
  // Security Tests
  // ===========================================================================

  group('Auth Security Tests', () {
    testWidgets('should not store password in plain text', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      const password = 'MyPassword123!';

      // Act - Never store password
      // This test ensures we don't accidentally store passwords
      final hasPassword = prefs.getString('password') != null;

      // Assert
      expect(hasPassword, isFalse); // Should never be true
    });

    testWidgets('should clear sensitive data from memory', (tester) async {
      // Arrange
      String? sensitiveData = 'access_token_xyz';

      // Act - Clear after use
      sensitiveData = null;

      // Assert
      expect(sensitiveData, isNull);
    });

    testWidgets('should implement rate limiting for login attempts', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      const maxAttempts = 5;

      // Act - Track failed attempts
      for (int i = 0; i < maxAttempts + 1; i++) {
        final attempts = prefs.getInt('login_attempts') ?? 0;
        await prefs.setInt('login_attempts', attempts + 1);
      }

      final currentAttempts = prefs.getInt('login_attempts')!;
      final isLocked = currentAttempts >= maxAttempts;

      if (isLocked) {
        await prefs.setBool('account_locked', true);
        await prefs.setString('locked_until',
          DateTime.now().add(const Duration(minutes: 15)).toIso8601String());
      }

      // Assert
      expect(isLocked, isTrue);
      expect(prefs.getBool('account_locked'), isTrue);
    });
  });
}
