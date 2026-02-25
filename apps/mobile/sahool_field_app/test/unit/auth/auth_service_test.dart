import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/auth/biometric_service.dart';
import 'package:sahool_field_app/core/auth/user_context.dart';

/// Mock dependencies
class MockSecureStorageService extends Mock implements SecureStorageService {}

class MockBiometricService extends Mock implements BiometricService {}

class MockUserContext extends Mock implements UserContext {}

void main() {
  group('AuthService', () {
    late AuthService authService;
    late MockSecureStorageService mockSecureStorage;
    late MockBiometricService mockBiometricService;
    late MockUserContext mockUserContext;

    setUp(() {
      mockSecureStorage = MockSecureStorageService();
      mockBiometricService = MockBiometricService();
      mockUserContext = MockUserContext();

      // Default stubs for SecureStorageService async methods
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.getRefreshToken())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.getTenantId()).thenAnswer((_) async => null);
      when(() => mockSecureStorage.getUserData()).thenAnswer((_) async => null);
      when(() => mockSecureStorage.clearAll()).thenAnswer((_) async {});
      when(() => mockSecureStorage.read(any())).thenAnswer((_) async => null);
      when(() => mockSecureStorage.setAccessToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setRefreshToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTokenExpiry(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setUserData(any())).thenAnswer((_) async {});
      when(() => mockSecureStorage.setTenantId(any())).thenAnswer((_) async {});

      // Default stubs for UserContext methods
      when(() => mockUserContext.setUser(any(),
          tenantId: any(named: 'tenantId'),
          role: any(named: 'role'))).thenReturn(null);
      when(() => mockUserContext.clearUser()).thenReturn(null);

      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        userContext: mockUserContext,
      );
    });

    tearDown(() {
      authService.dispose();
    });

    group('login', () {
      test('should successfully login with valid credentials', () async {
        // Arrange
        const email = 'test@sahool.com';
        const password = 'password123';

        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async => {});

        // Act
        final user = await authService.login(email, password);

        // Assert
        expect(user, isNotNull);
        expect(user.email, email);
        expect(user.name, isNotEmpty);
        expect(user.tenantId, isNotEmpty);
        verify(() => mockSecureStorage.setAccessToken(any())).called(1);
        verify(() => mockSecureStorage.setRefreshToken(any())).called(1);
        verify(() => mockSecureStorage.setUserData(any())).called(1);
      });

      test('should store tokens securely after login', () async {
        // Arrange
        const email = 'test@sahool.com';
        const password = 'password123';

        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setUserData(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setTenantId(any()))
            .thenAnswer((_) async => {});

        // Act
        await authService.login(email, password);

        // Assert
        verify(() => mockSecureStorage.setAccessToken(any())).called(1);
        verify(() => mockSecureStorage.setRefreshToken(any())).called(1);
        verify(() => mockSecureStorage.setTokenExpiry(any())).called(1);
      });
    });

    group('logout', () {
      test('should clear all stored data on logout', () async {
        // Arrange
        when(() => mockSecureStorage.clearAll()).thenAnswer((_) async => {});

        // Act
        await authService.logout();

        // Assert
        verify(() => mockSecureStorage.clearAll()).called(1);
      });
    });

    group('isLoggedIn', () {
      test('should return false when no access token exists', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, false);
      });

      test('should return true when valid access token exists', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => 'valid_token');
        when(() => mockSecureStorage.getTokenExpiry()).thenAnswer(
            (_) async => DateTime.now().add(const Duration(hours: 1)));

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, true);
      });

      test('should attempt token refresh when token is expired', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => 'expired_token');
        when(() => mockSecureStorage.getTokenExpiry()).thenAnswer(
            (_) async => DateTime.now().subtract(const Duration(hours: 1)));
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => 'refresh_token');
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async => {});

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, true);
        verify(() => mockSecureStorage.getRefreshToken()).called(1);
      });
    });

    group('getTokenExpiry', () {
      test('should return null when token expiry is null', () async {
        // Arrange
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getTokenExpiry();

        // Assert
        expect(result, null);
      });

      test('should return expiry time when token exists', () async {
        // Arrange
        final futureTime = DateTime.now().add(const Duration(hours: 1));
        when(() => mockSecureStorage.getTokenExpiry())
            .thenAnswer((_) async => futureTime);

        // Act
        final result = await authService.getTokenExpiry();

        // Assert
        expect(result, isNotNull);
        expect(result!.isAfter(DateTime.now()), isTrue);
      });
    });

    group('validateSession', () {
      test('should return false when no access token exists', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.validateSession();

        // Assert
        expect(result, false);
      });

      test('should return true when token is valid', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => 'valid_token');
        when(() => mockSecureStorage.getTokenExpiry()).thenAnswer(
            (_) async => DateTime.now().add(const Duration(hours: 1)));

        // Act
        final result = await authService.validateSession();

        // Assert
        expect(result, true);
      });

      test('should attempt token refresh when token is expired', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => 'expired_token');
        when(() => mockSecureStorage.getTokenExpiry()).thenAnswer(
            (_) async => DateTime.now().subtract(const Duration(hours: 1)));
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => 'refresh_token');
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async => {});

        // Act
        final result = await authService.validateSession();

        // Assert
        expect(result, true);
      });
    });

    group('getCurrentUser', () {
      test('should return null when no user data exists', () async {
        // Arrange
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getCurrentUser();

        // Assert
        expect(result, null);
      });

      test('should return user when user data exists', () async {
        // Arrange
        final userData = {
          'id': 'user_001',
          'email': 'test@sahool.com',
          'name': 'Test User',
          'role': 'farmer',
          'tenant_id': 'tenant_1',
        };
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => userData);

        // Act
        final result = await authService.getCurrentUser();

        // Assert
        expect(result, isNotNull);
        expect(result!.id, 'user_001');
        expect(result.email, 'test@sahool.com');
        expect(result.name, 'Test User');
      });
    });

    group('refreshToken', () {
      test('should successfully refresh token', () async {
        // Arrange
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => 'refresh_token');
        when(() => mockSecureStorage.setAccessToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setRefreshToken(any()))
            .thenAnswer((_) async => {});
        when(() => mockSecureStorage.setTokenExpiry(any()))
            .thenAnswer((_) async => {});

        // Act
        await authService.refreshToken();

        // Assert
        verify(() => mockSecureStorage.setAccessToken(any())).called(1);
        verify(() => mockSecureStorage.setRefreshToken(any())).called(1);
        verify(() => mockSecureStorage.setTokenExpiry(any())).called(1);
      });

      test('should throw exception when refresh token is null', () async {
        // Arrange
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => null);

        // Act & Assert
        await expectLater(
          authService.refreshToken(),
          throwsA(isA<AuthException>()),
        );
      });
    });

    group('loginWithBiometric', () {
      test('should throw exception when biometric is not available', () async {
        // Arrange
        when(() => mockBiometricService.isAvailable())
            .thenAnswer((_) async => false);

        // Act & Assert
        await expectLater(
          authService.loginWithBiometric(),
          throwsA(isA<AuthException>()),
        );
      });

      test('should throw exception when biometric is not enabled', () async {
        // Arrange
        when(() => mockBiometricService.isAvailable())
            .thenAnswer((_) async => true);
        when(() => mockBiometricService.isEnabled())
            .thenAnswer((_) async => false);

        // Act & Assert
        await expectLater(
          authService.loginWithBiometric(),
          throwsA(isA<AuthException>()),
        );
      });

      test('should throw exception when biometric authentication fails',
          () async {
        // Arrange
        when(() => mockBiometricService.isAvailable())
            .thenAnswer((_) async => true);
        when(() => mockBiometricService.isEnabled())
            .thenAnswer((_) async => true);
        when(() =>
                mockBiometricService.authenticate(reason: any(named: 'reason')))
            .thenAnswer((_) async => false);

        // Act & Assert
        await expectLater(
          authService.loginWithBiometric(),
          throwsA(isA<AuthException>()),
        );
      });

      test('should return user when biometric authentication succeeds',
          () async {
        // Arrange
        when(() => mockBiometricService.isAvailable())
            .thenAnswer((_) async => true);
        when(() => mockBiometricService.isEnabled())
            .thenAnswer((_) async => true);
        when(() =>
                mockBiometricService.authenticate(reason: any(named: 'reason')))
            .thenAnswer((_) async => true);
        when(() => mockSecureStorage.getRefreshToken())
            .thenAnswer((_) async => 'refresh_token');

        final userData = {
          'id': 'user_001',
          'email': 'test@sahool.com',
          'name': 'Test User',
          'role': 'farmer',
          'tenant_id': 'tenant_1',
        };
        when(() => mockSecureStorage.getUserData())
            .thenAnswer((_) async => userData);

        // Act
        final result = await authService.loginWithBiometric();

        // Assert
        expect(result, isNotNull);
        expect(result!.email, 'test@sahool.com');
      });
    });

    group('getTenantId', () {
      test('should return tenant id when it exists', () async {
        // Arrange
        when(() => mockSecureStorage.getTenantId())
            .thenAnswer((_) async => 'tenant_001');

        // Act
        final result = await authService.getTenantId();

        // Assert
        expect(result, 'tenant_001');
      });

      test('should return null when tenant id does not exist', () async {
        // Arrange
        when(() => mockSecureStorage.getTenantId())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getTenantId();

        // Assert
        expect(result, null);
      });
    });

    group('getAccessToken', () {
      test('should return access token when it exists', () async {
        // Arrange
        const token = 'test_access_token';
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => token);

        // Act
        final result = await authService.getAccessToken();

        // Assert
        expect(result, token);
      });

      test('should return null when access token does not exist', () async {
        // Arrange
        when(() => mockSecureStorage.getAccessToken())
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getAccessToken();

        // Assert
        expect(result, null);
      });
    });
  });

  group('AuthStateNotifier', () {
    late AuthStateNotifier authStateNotifier;
    late MockSecureStorageService mockSecureStorage;
    late MockBiometricService mockBiometricService;
    late MockUserContext mockUserContext;
    late AuthService authService;

    setUp(() {
      mockSecureStorage = MockSecureStorageService();
      mockBiometricService = MockBiometricService();
      mockUserContext = MockUserContext();

      // Default stubs for SecureStorageService async methods
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.getRefreshToken())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.getTenantId()).thenAnswer((_) async => null);
      when(() => mockSecureStorage.getUserData()).thenAnswer((_) async => null);
      when(() => mockSecureStorage.clearAll()).thenAnswer((_) async {});
      when(() => mockSecureStorage.read(any())).thenAnswer((_) async => null);
      when(() => mockSecureStorage.setAccessToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setRefreshToken(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setTokenExpiry(any()))
          .thenAnswer((_) async {});
      when(() => mockSecureStorage.setUserData(any())).thenAnswer((_) async {});
      when(() => mockSecureStorage.setTenantId(any())).thenAnswer((_) async {});

      // Default stubs for UserContext methods
      when(() => mockUserContext.setUser(any(),
          tenantId: any(named: 'tenantId'),
          role: any(named: 'role'))).thenReturn(null);
      when(() => mockUserContext.clearUser()).thenReturn(null);

      authService = AuthService(
        secureStorage: mockSecureStorage,
        biometricService: mockBiometricService,
        userContext: mockUserContext,
      );
    });

    tearDown(() {
      authService.dispose();
    });

    test('should initialize with unauthenticated state when no token exists',
        () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => null);

      // Act
      authStateNotifier = AuthStateNotifier(authService);
      await Future.delayed(const Duration(milliseconds: 100));

      // Assert
      expect(authStateNotifier.state.status, AuthStatus.unauthenticated);
    });

    test('should initialize with authenticated state when valid token exists',
        () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => 'valid_token');
      when(() => mockSecureStorage.getTokenExpiry()).thenAnswer(
          (_) async => DateTime.now().add(const Duration(hours: 1)));

      final userData = {
        'id': 'user_001',
        'email': 'test@sahool.com',
        'name': 'Test User',
        'role': 'farmer',
        'tenant_id': 'tenant_1',
      };
      when(() => mockSecureStorage.getUserData())
          .thenAnswer((_) async => userData);

      // Act
      authStateNotifier = AuthStateNotifier(authService);
      await Future.delayed(const Duration(milliseconds: 100));

      // Assert
      expect(authStateNotifier.state.status, AuthStatus.authenticated);
      expect(authStateNotifier.state.user, isNotNull);
    });

    test('should update state to authenticated after successful login',
        () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => null);
      when(() => mockSecureStorage.setAccessToken(any()))
          .thenAnswer((_) async => {});
      when(() => mockSecureStorage.setRefreshToken(any()))
          .thenAnswer((_) async => {});
      when(() => mockSecureStorage.setTokenExpiry(any()))
          .thenAnswer((_) async => {});
      when(() => mockSecureStorage.setUserData(any()))
          .thenAnswer((_) async => {});
      when(() => mockSecureStorage.setTenantId(any()))
          .thenAnswer((_) async => {});

      authStateNotifier = AuthStateNotifier(authService);
      await Future.delayed(const Duration(milliseconds: 100));

      // Act
      final result =
          await authStateNotifier.login('test@sahool.com', 'password123');

      // Assert
      expect(result, true);
      expect(authStateNotifier.state.status, AuthStatus.authenticated);
      expect(authStateNotifier.state.user, isNotNull);
    });

    test('should update state to unauthenticated after logout', () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => 'token');
      when(() => mockSecureStorage.getTokenExpiry()).thenAnswer(
          (_) async => DateTime.now().add(const Duration(hours: 1)));

      final userData = {
        'id': 'user_001',
        'email': 'test@sahool.com',
        'name': 'Test User',
        'role': 'farmer',
        'tenant_id': 'tenant_1',
      };
      when(() => mockSecureStorage.getUserData())
          .thenAnswer((_) async => userData);
      when(() => mockSecureStorage.clearAll()).thenAnswer((_) async => {});

      authStateNotifier = AuthStateNotifier(authService);
      await Future.delayed(const Duration(milliseconds: 100));

      // Act
      await authStateNotifier.logout();

      // Assert
      expect(authStateNotifier.state.status, AuthStatus.unauthenticated);
      expect(authStateNotifier.state.user, null);
    });
  });

  group('User', () {
    test('should create User from JSON', () {
      // Arrange
      final json = {
        'id': 'user_001',
        'email': 'test@sahool.com',
        'name': 'Test User',
        'role': 'farmer',
        'tenant_id': 'tenant_1',
        'phone': '+966501234567',
        'avatar_url': 'https://example.com/avatar.jpg',
      };

      // Act
      final user = User.fromJson(json);

      // Assert
      expect(user.id, 'user_001');
      expect(user.email, 'test@sahool.com');
      expect(user.name, 'Test User');
      expect(user.role, 'farmer');
      expect(user.tenantId, 'tenant_1');
      expect(user.phone, '+966501234567');
      expect(user.avatarUrl, 'https://example.com/avatar.jpg');
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
  });
}
