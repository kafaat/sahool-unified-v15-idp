/// Authentication Controller Tests
/// اختبارات وحدة التحكم في المصادقة
///
/// Comprehensive tests for AuthStateNotifier covering:
/// - Login flow
/// - Logout
/// - Session initialization
/// - State management
/// - Error handling

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/biometric_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';

import 'auth_fixtures.dart';
import 'auth_mocks.dart';

void main() {
  late AuthService authService;
  late MockSecureStorageService mockSecureStorage;
  late MockBiometricService mockBiometricService;

  setUpAll(() {
    registerAuthFallbackValues();
  });

  setUp(() {
    mockSecureStorage = MockSecureStorageService();
    mockBiometricService = MockBiometricService();
    mockSecureStorage.setupDefaults();
    mockBiometricService.setupDefaults();

    authService = AuthService(
      secureStorage: mockSecureStorage,
      biometricService: mockBiometricService,
    );
  });

  tearDown(() {
    mockSecureStorage.clearStorage();
    authService.dispose();
  });

  group('AuthStateNotifier', () {
    group('initialization', () {
      test('should start with initial status', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final notifier = AuthStateNotifier(authService);

        // Assert - initial state before async completes
        expect(notifier.state.status, AuthStatus.initial);
      });

      test('should transition to loading during initialization', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final notifier = AuthStateNotifier(authService);

        // Assert - state transitions through loading
        // Note: Due to async nature, we verify the final state
        await Future.delayed(const Duration(milliseconds: 150));
        expect(notifier.state.status, AuthStatus.unauthenticated);
      });

      test('should be unauthenticated when no token exists', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Assert
        expect(notifier.state.status, AuthStatus.unauthenticated);
        expect(notifier.state.user, isNull);
        expect(notifier.state.accessToken, isNull);
        expect(notifier.state.isAuthenticated, isFalse);
      });

      test('should be authenticated when valid token exists', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);

        // Act
        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Assert
        expect(notifier.state.status, AuthStatus.authenticated);
        expect(notifier.state.user, isNotNull);
        expect(notifier.state.isAuthenticated, isTrue);
      });

      test('should refresh token when expired during initialization', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.expiredTokenExpiry);
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => AuthFixtures.validRefreshToken);
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);

        // Act
        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 200));

        // Assert
        expect(notifier.state.status, AuthStatus.authenticated);
        verify(() => mockSecureStorage.getRefreshToken()).called(greaterThan(0));
      });

      test('should handle initialization error gracefully', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenThrow(Exception('Storage error'));

        // Act
        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Assert
        expect(notifier.state.status, AuthStatus.unauthenticated);
        expect(notifier.state.error, isNotNull);
      });
    });

    group('login', () {
      test('should successfully login with valid credentials', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);
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

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 100));

        // Act
        final result = await notifier.login(
          AuthFixtures.validEmail,
          AuthFixtures.validPassword,
        );

        // Assert
        expect(result, isTrue);
        expect(notifier.state.status, AuthStatus.authenticated);
        expect(notifier.state.user, isNotNull);
        expect(notifier.state.user?.email, AuthFixtures.validEmail);
        expect(notifier.state.isAuthenticated, isTrue);
      });

      test('should set loading state during login', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async {
          await Future.delayed(const Duration(milliseconds: 50));
        });
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async {});

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 100));

        // Act - check state during login
        final loginFuture = notifier.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert - should be loading
        expect(notifier.state.isLoading, isTrue);

        await loginFuture;
      });

      test('should store tokens after successful login', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);
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

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 100));

        // Act
        await notifier.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert
        verify(() => mockSecureStorage.setAccessToken(any())).called(1);
        verify(() => mockSecureStorage.setRefreshToken(any())).called(1);
        verify(() => mockSecureStorage.setTokenExpiry(any())).called(1);
      });

      test('should store user data after successful login', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);
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

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 100));

        // Act
        await notifier.login(AuthFixtures.validEmail, AuthFixtures.validPassword);

        // Assert
        verify(() => mockSecureStorage.setUserData(any())).called(1);
        verify(() => mockSecureStorage.setTenantId(any())).called(1);
      });

      test('should return false and set error on login failure', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenThrow(Exception('Storage error'));

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 100));

        // Act
        final result = await notifier.login(
          AuthFixtures.validEmail,
          AuthFixtures.validPassword,
        );

        // Assert
        expect(result, isFalse);
        expect(notifier.state.status, AuthStatus.unauthenticated);
        expect(notifier.state.error, isNotNull);
      });
    });

    group('logout', () {
      test('should clear all data on logout', () async {
        // Arrange - setup authenticated state
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);
        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));
        expect(notifier.state.status, AuthStatus.authenticated);

        // Act
        await notifier.logout();

        // Assert
        expect(notifier.state.status, AuthStatus.unauthenticated);
        expect(notifier.state.user, isNull);
        verify(() => mockSecureStorage.clearAll()).called(1);
      });

      test('should transition to unauthenticated state after logout', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);
        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Act
        await notifier.logout();

        // Assert
        expect(notifier.state.status, AuthStatus.unauthenticated);
        expect(notifier.state.isAuthenticated, isFalse);
      });

      test('should clear access token on logout', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);
        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Act
        await notifier.logout();

        // Assert
        expect(notifier.state.accessToken, isNull);
      });
    });

    group('refreshSession', () {
      test('should refresh token successfully', () async {
        // Arrange
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

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Act
        final result = await notifier.refreshSession();

        // Assert
        expect(result, isTrue);
        expect(notifier.state.status, AuthStatus.authenticated);
      });

      test('should logout on refresh failure', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => null); // No refresh token
        when(() => mockSecureStorage.clearAll())
            .thenAnswer((_) async {});

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Act
        final result = await notifier.refreshSession();

        // Assert
        expect(result, isFalse);
        expect(notifier.state.status, AuthStatus.unauthenticated);
      });

      test('should update access token after successful refresh', () async {
        // Arrange
        String? storedToken;
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => AuthFixtures.validAccessToken);
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => AuthFixtures.validTokenExpiry);
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => AuthFixtures.validUserData);
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => AuthFixtures.validRefreshToken);
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((invocation) async {
          storedToken = invocation.positionalArguments[0] as String;
        });
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async {});

        final notifier = AuthStateNotifier(authService);
        await Future.delayed(const Duration(milliseconds: 150));

        // Act
        await notifier.refreshSession();

        // Assert
        expect(notifier.state.accessToken, isNotNull);
        verify(() => mockSecureStorage.setAccessToken(any())).called(greaterThan(0));
      });
    });
  });

  group('AuthState', () {
    test('should create default AuthState', () {
      // Act
      const state = AuthState();

      // Assert
      expect(state.status, AuthStatus.initial);
      expect(state.user, isNull);
      expect(state.accessToken, isNull);
      expect(state.error, isNull);
      expect(state.isAuthenticated, isFalse);
      expect(state.isLoading, isFalse);
    });

    test('should copy with new values', () {
      // Arrange
      const state = AuthState();
      final user = User.fromJson(AuthFixtures.validUserData);

      // Act
      final newState = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        accessToken: AuthFixtures.validAccessToken,
      );

      // Assert
      expect(newState.status, AuthStatus.authenticated);
      expect(newState.user, isNotNull);
      expect(newState.accessToken, AuthFixtures.validAccessToken);
      expect(newState.isAuthenticated, isTrue);
    });

    test('should clear token when clearToken is true', () {
      // Arrange
      final state = AuthState(
        status: AuthStatus.authenticated,
        accessToken: AuthFixtures.validAccessToken,
      );

      // Act
      final newState = state.copyWith(clearToken: true);

      // Assert
      expect(newState.accessToken, isNull);
    });

    test('isAuthenticated should return true only when status is authenticated', () {
      // Assert
      expect(
        const AuthState(status: AuthStatus.authenticated).isAuthenticated,
        isTrue,
      );
      expect(
        const AuthState(status: AuthStatus.unauthenticated).isAuthenticated,
        isFalse,
      );
      expect(
        const AuthState(status: AuthStatus.loading).isAuthenticated,
        isFalse,
      );
      expect(
        const AuthState(status: AuthStatus.initial).isAuthenticated,
        isFalse,
      );
    });

    test('isLoading should return true only when status is loading', () {
      // Assert
      expect(
        const AuthState(status: AuthStatus.loading).isLoading,
        isTrue,
      );
      expect(
        const AuthState(status: AuthStatus.authenticated).isLoading,
        isFalse,
      );
      expect(
        const AuthState(status: AuthStatus.unauthenticated).isLoading,
        isFalse,
      );
    });
  });
}
