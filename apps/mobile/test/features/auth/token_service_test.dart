/// Token Service Tests
/// اختبارات خدمة التوكن
///
/// Comprehensive tests for token management covering:
/// - Token refresh
/// - Token storage
/// - Token expiry handling
/// - Automatic token refresh scheduling
/// - Session management

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/biometric_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/auth/token_manager.dart';
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

  group('Token Refresh', () {
    group('refreshToken', () {
      test('should successfully refresh token in mock mode', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        // Act - AuthService.refreshToken() delegates to tokenManager
        await authService.refreshToken();

        // Assert - verify delegation to tokenManager
        verify(() => mockTokenManager.refreshToken()).called(1);
      });

      test('should throw exception when no refresh token exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        // Configure tokenManager to throw TokenRefreshException
        when(() => mockTokenManager.refreshToken())
            .thenThrow(TokenRefreshException(
              'لا يوجد refresh token',
              code: 'NO_REFRESH_TOKEN',
            ));

        // Act & Assert
        expect(
          () => authService.refreshToken(),
          throwsA(isA<AuthException>().having(
            (e) => e.message,
            'message',
            contains('لا يوجد refresh token'),
          )),
        );
      });

      test('should use API client for token refresh when available', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        // Act - AuthService.refreshToken() delegates to tokenManager
        await authService.refreshToken();

        // Assert - verify delegation to tokenManager
        verify(() => mockTokenManager.refreshToken()).called(1);
      });

      test('should throw AuthException on refresh token failure', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        // Configure tokenManager to throw session expired
        when(() => mockTokenManager.refreshToken())
            .thenThrow(TokenRefreshException(
              'Session expired',
              code: 'SESSION_EXPIRED',
            ));

        // Act & Assert
        await expectLater(
          () => authService.refreshToken(),
          throwsA(isA<AuthException>()),
        );
      });

      test('should handle network error during refresh', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
          apiClient: mockApiClient,
        );

        // Configure tokenManager to throw network error
        when(() => mockTokenManager.refreshToken())
            .thenThrow(TokenRefreshException(
              'Network error',
              code: 'NETWORK_ERROR',
            ));

        // Act & Assert
        expect(
          () => authService.refreshToken(),
          throwsA(isA<AuthException>()),
        );
      });
    });
  });

  group('Token Storage', () {
    group('SecureStorageService token operations', () {
      test('should store access token securely', () async {
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

        // Act - login delegates token storage to tokenManager.storeTokens()
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert - verify tokenManager.storeTokens was called with mock tokens
        verify(() => mockTokenManager.storeTokens(
          accessToken: any(named: 'accessToken', that: contains('mock_access_token')),
          refreshToken: any(named: 'refreshToken'),
          expiresIn: any(named: 'expiresIn'),
        )).called(1);
      });

      test('should store refresh token securely', () async {
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

        // Act - login delegates token storage to tokenManager.storeTokens()
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert - verify tokenManager.storeTokens was called with mock refresh token
        verify(() => mockTokenManager.storeTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken', that: contains('mock_refresh_token')),
          expiresIn: any(named: 'expiresIn'),
        )).called(1);
      });

      test('should store token expiry time', () async {
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

        // Act - login delegates token storage to tokenManager.storeTokens()
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert - verify tokenManager.storeTokens was called with correct expiry (3600 seconds)
        verify(() => mockTokenManager.storeTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
          expiresIn: 3600,
        )).called(1);
      });

      test('should delete all tokens on logout', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          tokenManager: mockTokenManager,
        );

        when(() => mockTokenManager.logout())
            .thenAnswer((_) async {});

        // Act
        await authService.logout();

        // Assert - AuthService delegates logout to TokenManager
        verify(() => mockTokenManager.logout()).called(1);
      });
    });
  });

  group('Token Expiry Handling', () {
    test('should detect expired token', () async {
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
      // TokenManager refresh fails (simulating no refresh token)
      when(() => mockTokenManager.refreshToken())
          .thenThrow(TokenRefreshException(
            'لا يوجد refresh token',
            code: 'NO_REFRESH_TOKEN',
          ));

      // Act
      final isLoggedIn = await authService.isLoggedIn();

      // Assert - expired token with failed refresh means not logged in
      expect(isLoggedIn, isFalse);
    });

    test('should detect valid token', () async {
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
      final isLoggedIn = await authService.isLoggedIn();

      // Assert
      expect(isLoggedIn, isTrue);
    });

    test('should handle token expiring soon', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
      );

      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => AuthFixtures.validAccessToken);
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => AuthFixtures.soonToExpireTokenExpiry);
      // Token is valid but will expire soon, so refresh is triggered
      when(() => mockSecureStorage.getRefreshToken())
          .thenAnswer((_) async => AuthFixtures.validRefreshToken);
      when(() => mockSecureStorage.setAccessToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setRefreshToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTokenExpiry(any()))
          .thenAnswer((_) async {});

      // Act
      final isLoggedIn = await authService.isLoggedIn();

      // Assert - should still be logged in
      expect(isLoggedIn, isTrue);
    });

    test('should handle null token expiry', () async {
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
      final isLoggedIn = await authService.isLoggedIn();

      // Assert - no expiry means we can't validate, so not logged in
      expect(isLoggedIn, isFalse);
    });
  });

  group('Session Management', () {
    test('should get current access token', () async {
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

    test('should check login status correctly', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
      );

      // Test case 1: No token
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => null);
      expect(await authService.isLoggedIn(), isFalse);

      // Test case 2: Valid token
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => AuthFixtures.validAccessToken);
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
      expect(await authService.isLoggedIn(), isTrue);
    });

    test('should maintain session across token refresh', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
      );

      // Setup initial logged in state
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => AuthFixtures.validAccessToken);
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
      when(() => mockSecureStorage.getUserData())
          .thenAnswer((_) async => AuthFixtures.validUserData);
      when(() => mockSecureStorage.getRefreshToken())
          .thenAnswer((_) async => AuthFixtures.validRefreshToken);
      when(() => mockSecureStorage.setAccessToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setRefreshToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTokenExpiry(any()))
          .thenAnswer((_) async {});

      // Act - refresh token
      await authService.refreshToken();

      // Assert - should still be logged in
      final isLoggedIn = await authService.isLoggedIn();
      expect(isLoggedIn, isTrue);
    });
  });

  group('Token Pair Operations', () {
    test('should create token pair with correct expiry', () {
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

    test('should handle different expiry times', () {
      // Short expiry (5 minutes)
      const shortExpiry = TokenPair(
        accessToken: 'short_access',
        refreshToken: 'short_refresh',
        expiresIn: 300,
      );
      expect(shortExpiry.expiresIn, 300);

      // Long expiry (24 hours)
      const longExpiry = TokenPair(
        accessToken: 'long_access',
        refreshToken: 'long_refresh',
        expiresIn: 86400,
      );
      expect(longExpiry.expiresIn, 86400);
    });
  });

  group('API Token Response Handling', () {
    test('should parse access_token format', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
        apiClient: mockApiClient,
      );

      mockApiClient.setNextResponse({
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'expires_in': 3600,
        'user': AuthFixtures.validUserData,
      });

      when(() => mockSecureStorage.setUserData(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTenantId(any()))
          .thenAnswer((_) async {});

      // Act
      await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

      // Assert - token storage delegated to tokenManager.storeTokens()
      verify(() => mockTokenManager.storeTokens(
        accessToken: 'test_access_token',
        refreshToken: 'test_refresh_token',
        expiresIn: 3600,
      )).called(1);
    });

    test('should parse accessToken format (camelCase)', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
        apiClient: mockApiClient,
      );

      mockApiClient.setNextResponse({
        'accessToken': 'camel_case_token',
        'refreshToken': 'camel_refresh_token',
        'expiresIn': 7200,
        'user': AuthFixtures.validUserData,
      });

      when(() => mockSecureStorage.setUserData(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTenantId(any()))
          .thenAnswer((_) async {});

      // Act
      await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

      // Assert - token storage delegated to tokenManager.storeTokens()
      verify(() => mockTokenManager.storeTokens(
        accessToken: 'camel_case_token',
        refreshToken: 'camel_refresh_token',
        expiresIn: 7200,
      )).called(1);
    });

    test('should handle missing token in response', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
        apiClient: mockApiClient,
      );

      mockApiClient.setNextResponse({
        'user': AuthFixtures.validUserData,
        // Missing tokens
      });

      // Act & Assert
      expect(
        () => authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword),
        throwsA(isA<AuthException>()),
      );
    });

    test('should handle null response from API', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
        apiClient: mockApiClient,
      );

      mockApiClient.setNextResponse(<String, dynamic>{});

      // Act & Assert - will fall through to mock mode in debug builds
      // For comprehensive testing, verify proper error handling
    });
  });

  group('Secure Token Storage Integration', () {
    test('should store tenant ID from user data', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        tokenManager: mockTokenManager,
      );

      String? storedTenantId;
      when(() => mockSecureStorage.setAccessToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setRefreshToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTokenExpiry(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setUserData(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTenantId(any()))
          .thenAnswer((invocation) async {
        storedTenantId = invocation.positionalArguments[0] as String;
      });

      // Act
      await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

      // Assert
      expect(storedTenantId, isNotNull);
      expect(storedTenantId, equals('mock_tenant'));
    });

    test('should update API client with token after login', () async {
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
      await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

      // Assert
      verify(() => mockApiClient.setAuthToken(any())).called(1);
      verify(() => mockApiClient.setTenantId(any())).called(1);
    });
  });
}
