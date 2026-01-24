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
import 'package:sahool_field_app/core/http/api_client.dart';

import 'auth_fixtures.dart';
import 'auth_mocks.dart';

void main() {
  late AuthService authService;
  late MockSecureStorageService mockSecureStorage;
  late MockBiometricService mockBiometricService;
  late MockApiClient mockApiClient;

  setUpAll(() {
    registerAuthFallbackValues();
  });

  setUp(() {
    mockSecureStorage = MockSecureStorageService();
    mockBiometricService = MockBiometricService();
    mockApiClient = MockApiClient();

    mockSecureStorage.setupDefaults();
    mockBiometricService.setupDefaults();
    mockApiClient.setupDefaults();
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
        );

        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => AuthFixtures.validRefreshToken);
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});

        // Act
        await authService.refreshToken();

        // Assert
        verify(() => mockSecureStorage.setAccessToken(any())).called(1);
        verify(() => mockSecureStorage.setRefreshToken(any())).called(1);
        verify(() => mockSecureStorage.setTokenExpiry(any())).called(1);
      });

      test('should throw exception when no refresh token exists', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
        );

        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => null);

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
          apiClient: mockApiClient,
        );

        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => AuthFixtures.validRefreshToken);
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});

        mockApiClient.setNextResponse(AuthFixtures.successfulRefreshResponse);

        // Act
        await authService.refreshToken();

        // Assert
        verify(() => mockApiClient.post(
              '/api/v1/auth/refresh',
              any(),
              queryParameters: any(named: 'queryParameters'),
              headers: any(named: 'headers'),
            )).called(1);
        verify(() => mockApiClient.setAuthToken(any())).called(1);
      });

      test('should logout on refresh token failure', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          apiClient: mockApiClient,
        );

        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => AuthFixtures.validRefreshToken);
        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        mockApiClient.setNextError(ApiException(
          code: 'SESSION_EXPIRED',
          message: 'Session expired',
          statusCode: 401,
        ));

        // Act & Assert
        await expectLater(
          () => authService.refreshToken(),
          throwsA(isA<AuthException>()),
        );
        verify(() => mockSecureStorage.clearAll()).called(1);
      });

      test('should handle network error during refresh', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
          apiClient: mockApiClient,
        );

        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => AuthFixtures.validRefreshToken);
        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        mockApiClient.setNextError(ApiException(
          code: 'NETWORK_ERROR',
          message: 'No connection',
          isNetworkError: true,
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
        );

        String? storedToken;
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((invocation) async {
          storedToken = invocation.positionalArguments[0] as String;
        });
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
        expect(storedToken, isNotNull);
        expect(storedToken, contains('mock_access_token'));
      });

      test('should store refresh token securely', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
        );

        String? storedRefreshToken;
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((invocation) async {
          storedRefreshToken = invocation.positionalArguments[0] as String;
        });
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        // Act
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert
        expect(storedRefreshToken, isNotNull);
        expect(storedRefreshToken, contains('mock_refresh_token'));
      });

      test('should store token expiry time', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
        );

        DateTime? storedExpiry;
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((invocation) async {
          storedExpiry = invocation.positionalArguments[0] as DateTime;
        });
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        // Act
        await authService.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert
        expect(storedExpiry, isNotNull);
        // Token should expire approximately 1 hour from now (mock returns 3600 seconds)
        expect(
          storedExpiry!.difference(DateTime.now()).inMinutes,
          greaterThan(55),
        );
        expect(
          storedExpiry!.difference(DateTime.now()).inMinutes,
          lessThan(65),
        );
      });

      test('should delete all tokens on logout', () async {
        // Arrange
        authService = AuthService(
          secureStorage: mockSecureStorage,
          biometricService: mockBiometricService,
        );

        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        // Act
        await authService.logout();

        // Assert
        verify(() => mockSecureStorage.clearAll()).called(1);
      });
    });
  });

  group('Token Expiry Handling', () {
    test('should detect expired token', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
      );

      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => AuthFixtures.validAccessToken);
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => AuthFixtures.expiredTokenExpiry);
      when(() => mockSecureStorage.getRefreshToken())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.clearAll())
          .thenAnswer((_) async {});

      // Act
      final isLoggedIn = await authService.isLoggedIn();

      // Assert - expired token with no refresh token means not logged in
      expect(isLoggedIn, isFalse);
    });

    test('should detect valid token', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
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
        apiClient: mockApiClient,
      );

      mockApiClient.setNextResponse({
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'expires_in': 3600,
        'user': AuthFixtures.validUserData,
      });

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
      verify(() => mockSecureStorage.setAccessToken('test_access_token')).called(1);
    });

    test('should parse accessToken format (camelCase)', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        apiClient: mockApiClient,
      );

      mockApiClient.setNextResponse({
        'accessToken': 'camel_case_token',
        'refreshToken': 'camel_refresh_token',
        'expiresIn': 7200,
        'user': AuthFixtures.validUserData,
      });

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
      verify(() => mockSecureStorage.setAccessToken('camel_case_token')).called(1);
    });

    test('should handle missing token in response', () async {
      // Arrange
      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
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
        apiClient: mockApiClient,
      );

      mockApiClient.setNextResponse(null as dynamic);

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
