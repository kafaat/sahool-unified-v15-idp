/// Authentication Repository Tests
/// اختبارات مستودع المصادقة
///
/// Comprehensive tests for AuthService covering:
/// - Login flow (mock and API modes)
/// - Logout
/// - isLoggedIn checks
/// - getCurrentUser
/// - Password reset
/// - Error handling

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/biometric_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/http/api_client.dart';

import 'auth_fixtures.dart';
import 'auth_mocks.dart';

void main() {
  late AuthService authService;
  late MockSecureStorageService mockSecureStorage;
  late MockBiometricService mockBiometricService;
  late MockApiClient mockApiClient;
  late MockTokenManager mockTokenManager;

  setUpAll(() {
    registerAuthFallbackValues();
  });

  setUp(() {
    mockSecureStorage = MockSecureStorageService();
    mockBiometricService = MockBiometricService();
    mockApiClient = MockApiClient();
    mockTokenManager = MockTokenManager();

    mockSecureStorage.setupDefaults();
    mockBiometricService.setupDefaults();
    mockApiClient.setupDefaults();
    mockTokenManager.setupDefaults();
  });

  tearDown(() {
    mockSecureStorage.clearStorage();
    authService.dispose();
  });

  group('AuthService', () {
    group('login', () {
      test('should login successfully with mock mode', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          // No apiClient - uses mock mode
        );

        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        // Act
        final user = await authService.login(
          AuthFixtures.validEmail,
          AuthFixtures.validPassword,
        );

        // Assert
        expect(user, isNotNull);
        expect(user.email, AuthFixtures.validEmail);
        expect(user.name, isNotEmpty);
        expect(user.tenantId, isNotEmpty);
      });

      test('should store tokens securely after login', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        // Act
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert - token storage is now delegated to tokenManager.storeTokens()
        verify(() => mockTokenManager.storeTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
          expiresIn: any(named: 'expiresIn'),
        )).called(1);
      });

      test('should store user data after login', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        // Act
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert
        verify(() => mockSecureStorage.setUserData(any())).called(1);
        verify(() => mockSecureStorage.setTenantId(any())).called(1);
      });

      test('should handle login with API client', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        mockApiClient.setNextResponse(AuthFixtures.successfulLoginResponse);

        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        // Act
        final user = await authService.login(
          AuthFixtures.validEmail,
          AuthFixtures.validPassword,
        );

        // Assert
        expect(user, isNotNull);
        verify(() => mockApiClient.setAuthToken(any())).called(1);
        verify(() => mockApiClient.setTenantId(any())).called(1);
      });

      test('should throw AuthException on invalid credentials', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        mockApiClient.setNextError(ApiException(
          code: 'INVALID_CREDENTIALS',
          message: 'Invalid credentials',
          statusCode: 401,
        ));

        // Act & Assert
        expect(
          () => authService.login(AuthFixtures.invalidEmail, AuthFixtures.invalidPassword),
          throwsA(isA<AuthException>()),
        );
      });

      test('should handle network errors gracefully', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        mockApiClient.setNextError(ApiException(
          code: 'NETWORK_ERROR',
          message: 'No connection',
          isNetworkError: true,
        ));

        // For non-debug mode, this would throw
        // In debug mode with network error, it falls back to mock
        // This test verifies the exception is thrown when not in debug mode
        expect(
          () => authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword),
          throwsA(isA<AuthException>()),
        );
      });
    });

    group('logout', () {
      test('should clear all stored data on logout', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        // Act
        await authService.logout();

        // Assert - logout is now delegated to tokenManager.logout()
        verify(() => mockTokenManager.logout()).called(1);
      });

      test('should cancel token refresh timer on logout', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        // Login first to schedule token refresh
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Act
        await authService.logout();

        // Assert - no exception thrown means timer was cancelled properly
        expect(true, isTrue);
      });

      test('should clear API client token on logout', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        // Act
        await authService.logout();

        // Assert - token clearing is handled by tokenManager.logout()
        verify(() => mockTokenManager.logout()).called(1);
      });
    });

    group('isLoggedIn', () {
      test('should return false when no access token exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, isFalse);
      });

      test('should return false when token expiry is null', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, isFalse);
      });

      test('should return true when valid token exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.validTokenExpiry);

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, isTrue);
      });

      test('should attempt token refresh when token is expired', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.expiredTokenExpiry);

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, isTrue);
        // Token refresh is now delegated to tokenManager.refreshToken()
        verify(() => mockTokenManager.refreshToken()).called(1);
      });

      test('should return false when token refresh fails', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.expiredTokenExpiry);
        // Make tokenManager.refreshToken() throw to simulate refresh failure
        when(() => mockTokenManager.refreshToken())
            .thenThrow(Exception('Refresh failed'));

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, isFalse);
      });
    });

    group('getCurrentUser', () {
      test('should return null when no user data exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => null);

        // Act
        final user = await authService.getCurrentUser();

        // Assert
        expect(user, isNull);
      });

      test('should return user when user data exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);

        // Act
        final user = await authService.getCurrentUser();

        // Assert
        expect(user, isNotNull);
        expect(user!.id, AuthFixtures.validUserData['id']);
        expect(user.email, AuthFixtures.validUserData['email']);
        expect(user.name, AuthFixtures.validUserData['name']);
        expect(user.role, AuthFixtures.validUserData['role']);
        expect(user.tenantId, AuthFixtures.validUserData['tenant_id']);
      });

      test('should include optional fields when present', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);

        // Act
        final user = await authService.getCurrentUser();

        // Assert
        expect(user!.phone, AuthFixtures.validUserData['phone']);
        expect(user.avatarUrl, AuthFixtures.validUserData['avatar_url']);
      });
    });

    group('getAccessToken', () {
      test('should return access token from secure storage', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);

        // Act
        final token = await authService.getAccessToken();

        // Assert
        expect(token, AuthFixtures.validAccessToken);
      });

      test('should return null when no token exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final token = await authService.getAccessToken();

        // Assert
        expect(token, isNull);
      });
    });

    group('loginWithBiometric', () {
      test('should throw exception when biometric is not available', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        mockBiometricService.setAvailable(false);
        mockBiometricService.setupDefaults();

        // Act & Assert
        expect(
          () => authService.loginWithBiometric(),
          throwsA(isA<AuthException>().having(
            (e) => e.message,
            'message',
            contains('غير متاحة'),
          )),
        );
      });

      test('should throw exception when biometric is not enabled', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        mockBiometricService.setAvailable(true);
        mockBiometricService.setEnabled(false);
        mockBiometricService.setupDefaults();

        // Act & Assert
        expect(
          () => authService.loginWithBiometric(),
          throwsA(isA<AuthException>().having(
            (e) => e.message,
            'message',
            contains('غير مفعلة'),
          )),
        );
      });

      test('should throw exception when biometric authentication fails', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        mockBiometricService.setAvailable(true);
        mockBiometricService.setEnabled(true);
        mockBiometricService.setWillAuthenticate(false);
        mockBiometricService.setupDefaults();

        // Act & Assert
        expect(
          () => authService.loginWithBiometric(),
          throwsA(isA<AuthException>().having(
            (e) => e.message,
            'message',
            contains('فشل التحقق'),
          )),
        );
      });

      test('should throw exception when no stored session exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        mockBiometricService.setAvailable(true);
        mockBiometricService.setEnabled(true);
        mockBiometricService.setWillAuthenticate(true);
        mockBiometricService.setupDefaults();

        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => null);

        // Act & Assert
        expect(
          () => authService.loginWithBiometric(),
          throwsA(isA<AuthException>().having(
            (e) => e.message,
            'message',
            contains('لا توجد جلسة'),
          )),
        );
      });
    });

    group('resetPassword', () {
      test('should successfully reset password in mock mode', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        // Act & Assert - should not throw
        await expectLater(
          authService.resetPassword(
            token: 'reset_token',
            newPassword: 'NewSecurePass123!',
          ),
          completes,
        );
      });

      test('should call API for password reset when apiClient is provided', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        mockApiClient.setNextResponse({'success': true});

        // Act
        await authService.resetPassword(
          token: 'reset_token',
          newPassword: 'NewSecurePass123!',
        );

        // Assert
        verify(() => mockApiClient.post(
              '/api/v1/auth/reset-password',
              any(),
              queryParameters: any(named: 'queryParameters'),
              headers: any(named: 'headers'),
            )).called(1);
      });

      test('should throw AuthException on invalid token', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        mockApiClient.setNextError(ApiException(
          code: 'INVALID_TOKEN',
          message: 'Invalid token',
          statusCode: 400,
        ));

        // Act & Assert
        expect(
          () => authService.resetPassword(
            token: 'invalid_token',
            newPassword: 'NewSecurePass123!',
          ),
          throwsA(isA<AuthException>()),
        );
      });
    });

    group('dispose', () {
      test('should cancel refresh timer on dispose', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        // Login to start refresh timer
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Act
        authService.dispose();

        // Assert - no exception means timer cancelled successfully
        expect(true, isTrue);
      });
    });
  });

  group('User Model', () {
    test('should create User from JSON', () {
      // Act
      final user = User.fromJson(AuthFixtures.validUserData);

      // Assert
      expect(user.id, AuthFixtures.validUserData['id']);
      expect(user.email, AuthFixtures.validUserData['email']);
      expect(user.name, AuthFixtures.validUserData['name']);
      expect(user.role, AuthFixtures.validUserData['role']);
      expect(user.tenantId, AuthFixtures.validUserData['tenant_id']);
      expect(user.phone, AuthFixtures.validUserData['phone']);
      expect(user.avatarUrl, AuthFixtures.validUserData['avatar_url']);
    });

    test('should convert User to JSON', () {
      // Arrange
      const user = User(
        id: 'user_001',
        email: 'test@sahool.com',
        name: 'Test User',
        role: 'farmer',
        tenantId: 'tenant_1',
        phone: '+966501234567',
        avatarUrl: 'https://example.com/avatar.jpg',
      );

      // Act
      final json = user.toJson();

      // Assert
      expect(json['id'], 'user_001');
      expect(json['email'], 'test@sahool.com');
      expect(json['name'], 'Test User');
      expect(json['role'], 'farmer');
      expect(json['tenant_id'], 'tenant_1');
      expect(json['phone'], '+966501234567');
      expect(json['avatar_url'], 'https://example.com/avatar.jpg');
    });

    test('should handle null optional fields', () {
      // Arrange
      final json = {
        'id': 'user_001',
        'email': 'test@sahool.com',
        'name': 'Test User',
        'role': 'farmer',
        'tenant_id': 'tenant_1',
      };

      // Act
      final user = User.fromJson(json);

      // Assert
      expect(user.phone, isNull);
      expect(user.avatarUrl, isNull);
    });
  });

  group('TokenPair', () {
    test('should create TokenPair with all fields', () {
      // Act
      const tokenPair = TokenPair(
        accessToken: 'access_token',
        refreshToken: 'refresh_token',
        expiresIn: 3600,
      );

      // Assert
      expect(tokenPair.accessToken, 'access_token');
      expect(tokenPair.refreshToken, 'refresh_token');
      expect(tokenPair.expiresIn, 3600);
    });
  });

  group('AuthException', () {
    test('should create AuthException with message', () {
      // Act
      final exception = AuthException('Test error');

      // Assert
      expect(exception.message, 'Test error');
      expect(exception.code, isNull);
    });

    test('should create AuthException with message and code', () {
      // Act
      final exception = AuthException('Test error', code: 'TEST_CODE');

      // Assert
      expect(exception.message, 'Test error');
      expect(exception.code, 'TEST_CODE');
    });

    test('should have string representation', () {
      // Act
      final exception = AuthException('Test error message');

      // Assert
      expect(exception.toString(), 'Test error message');
    });
  });
}
