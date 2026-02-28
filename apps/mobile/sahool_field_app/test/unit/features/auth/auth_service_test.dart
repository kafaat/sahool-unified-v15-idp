import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/http/api_client.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/features/auth/data/auth_service.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════════

class MockApiClient extends Mock implements ApiClient {}

class MockSecureStorageService extends Mock implements SecureStorageService {}

void main() {
  late MockApiClient mockApiClient;
  late MockSecureStorageService mockSecureStorage;
  late RegistrationAuthService authService;

  setUp(() {
    mockApiClient = MockApiClient();
    mockSecureStorage = MockSecureStorageService();
    authService = RegistrationAuthService(
      apiClient: mockApiClient,
      secureStorage: mockSecureStorage,
    );
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // RegisterRequest Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('RegisterRequest', () {
    test('toJson includes all required fields', () {
      // Arrange
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'SecurePass123!',
        firstName: 'Ahmed',
        lastName: 'Mohamed',
      );

      // Act
      final json = request.toJson();

      // Assert
      expect(json['email'], 'test@sahool.app');
      expect(json['password'], 'SecurePass123!');
      expect(json['firstName'], 'Ahmed');
      expect(json['lastName'], 'Mohamed');
      expect(json.containsKey('phone'), isFalse);
    });

    test('toJson includes phone when provided', () {
      // Arrange
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'SecurePass123!',
        firstName: 'Ahmed',
        lastName: 'Mohamed',
        phone: '+966501234567',
      );

      // Act
      final json = request.toJson();

      // Assert
      expect(json['phone'], '+966501234567');
    });

    test('toJson excludes phone when empty string', () {
      // Arrange
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'SecurePass123!',
        firstName: 'Ahmed',
        lastName: 'Mohamed',
        phone: '',
      );

      // Act
      final json = request.toJson();

      // Assert
      expect(json.containsKey('phone'), isFalse);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // AuthResponse Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('AuthResponse.fromJson', () {
    test('parses complete JSON correctly', () {
      // Arrange
      final json = {
        'access_token': 'test-access-token',
        'refresh_token': 'test-refresh-token',
        'expires_at': '2026-12-31T23:59:59Z',
        'user': {
          'id': 'user-123',
          'email': 'test@sahool.app',
          'first_name': 'Ahmed',
          'last_name': 'Mohamed',
          'phone': '+966501234567',
          'tenant_id': 'tenant-456',
        },
      };

      // Act
      final response = AuthResponse.fromJson(json);

      // Assert
      expect(response.accessToken, 'test-access-token');
      expect(response.refreshToken, 'test-refresh-token');
      expect(response.expiresAt, isNotNull);
      expect(response.expiresAt!.year, 2026);
      expect(response.user.id, 'user-123');
      expect(response.user.email, 'test@sahool.app');
    });

    test('handles null optional fields', () {
      // Arrange
      final json = {
        'access_token': 'test-access-token',
        'refresh_token': null,
        'expires_at': null,
        'user': {
          'id': 'user-123',
          'email': 'test@sahool.app',
        },
      };

      // Act
      final response = AuthResponse.fromJson(json);

      // Assert
      expect(response.accessToken, 'test-access-token');
      expect(response.refreshToken, isNull);
      expect(response.expiresAt, isNull);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // UserInfo Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('UserInfo', () {
    test('fromJson parses all fields correctly', () {
      // Arrange
      final json = {
        'id': 'user-123',
        'email': 'test@sahool.app',
        'first_name': 'Ahmed',
        'last_name': 'Mohamed',
        'phone': '+966501234567',
        'tenant_id': 'tenant-456',
      };

      // Act
      final user = UserInfo.fromJson(json);

      // Assert
      expect(user.id, 'user-123');
      expect(user.email, 'test@sahool.app');
      expect(user.firstName, 'Ahmed');
      expect(user.lastName, 'Mohamed');
      expect(user.phone, '+966501234567');
      expect(user.tenantId, 'tenant-456');
    });

    test('fromJson uses empty string defaults for missing name fields', () {
      // Arrange
      final json = {
        'id': 'user-123',
        'email': 'test@sahool.app',
      };

      // Act
      final user = UserInfo.fromJson(json);

      // Assert
      expect(user.firstName, '');
      expect(user.lastName, '');
      expect(user.phone, isNull);
      expect(user.tenantId, isNull);
    });

    test('fullName returns trimmed concatenation', () {
      // Arrange & Act
      final user = UserInfo(
        id: 'user-123',
        email: 'test@sahool.app',
        firstName: 'Ahmed',
        lastName: 'Mohamed',
      );

      // Assert
      expect(user.fullName, 'Ahmed Mohamed');
    });

    test('fullName handles empty first name', () {
      // Arrange & Act
      final user = UserInfo(
        id: 'user-123',
        email: 'test@sahool.app',
        firstName: '',
        lastName: 'Mohamed',
      );

      // Assert
      expect(user.fullName, 'Mohamed');
    });

    test('toJson produces correct map', () {
      // Arrange
      final user = UserInfo(
        id: 'user-123',
        email: 'test@sahool.app',
        firstName: 'Ahmed',
        lastName: 'Mohamed',
        phone: '+966501234567',
        tenantId: 'tenant-456',
      );

      // Act
      final json = user.toJson();

      // Assert
      expect(json['id'], 'user-123');
      expect(json['email'], 'test@sahool.app');
      expect(json['first_name'], 'Ahmed');
      expect(json['last_name'], 'Mohamed');
      expect(json['phone'], '+966501234567');
      expect(json['tenant_id'], 'tenant-456');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // AuthResult Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('AuthResult', () {
    test('success factory creates successful result', () {
      // Arrange
      final authResponse = AuthResponse(
        accessToken: 'token',
        user: UserInfo(
          id: 'u1',
          email: 'a@b.c',
          firstName: 'A',
          lastName: 'B',
        ),
      );

      // Act
      final result = AuthResult.success(authResponse);

      // Assert
      expect(result.success, isTrue);
      expect(result.response, isNotNull);
      expect(result.response!.accessToken, 'token');
      expect(result.errorMessage, isNull);
      expect(result.errorMessageAr, isNull);
    });

    test('failure factory creates failed result with bilingual messages', () {
      // Act
      final result = AuthResult.failure(
        message: 'Network error',
        messageAr: 'خطأ في الشبكة',
      );

      // Assert
      expect(result.success, isFalse);
      expect(result.response, isNull);
      expect(result.errorMessage, 'Network error');
      expect(result.errorMessageAr, 'خطأ في الشبكة');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // RegistrationAuthService.register Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('RegistrationAuthService.register', () {
    final validRequest = RegisterRequest(
      email: 'test@sahool.app',
      password: 'SecurePass123!',
      firstName: 'Ahmed',
      lastName: 'Mohamed',
    );

    final successApiResponse = {
      'access_token': 'test-access-token',
      'refresh_token': 'test-refresh-token',
      'expires_at': '2026-12-31T23:59:59Z',
      'user': {
        'id': 'user-123',
        'email': 'test@sahool.app',
        'first_name': 'Ahmed',
        'last_name': 'Mohamed',
        'tenant_id': 'tenant-456',
      },
    };

    test('successful registration stores tokens and returns success', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any()))
          .thenAnswer((_) async => successApiResponse);
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
      when(() => mockApiClient.setAuthToken(any())).thenReturn(null);
      when(() => mockApiClient.setTenantId(any())).thenReturn(null);

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isTrue);
      expect(result.response, isNotNull);
      expect(result.response!.accessToken, 'test-access-token');
      expect(result.response!.user.id, 'user-123');

      // Verify tokens were stored
      verify(() => mockSecureStorage.setAccessToken('test-access-token'))
          .called(1);
      verify(() => mockSecureStorage.setRefreshToken('test-refresh-token'))
          .called(1);
      verify(() => mockSecureStorage.setTokenExpiry(any())).called(1);
      verify(() => mockSecureStorage.setUserData(any())).called(1);
      verify(() => mockApiClient.setAuthToken('test-access-token')).called(1);
    });

    test('stores tenant ID when available in response', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any()))
          .thenAnswer((_) async => successApiResponse);
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
      when(() => mockApiClient.setAuthToken(any())).thenReturn(null);
      when(() => mockApiClient.setTenantId(any())).thenReturn(null);

      // Act
      await authService.register(validRequest);

      // Assert
      verify(() => mockApiClient.setTenantId('tenant-456')).called(1);
      verify(() => mockSecureStorage.setTenantId('tenant-456')).called(1);
    });

    test('returns failure when API returns null', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any()))
          .thenAnswer((_) async => null);

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isFalse);
      expect(result.errorMessage, 'No response from server');
      expect(result.errorMessageAr, contains('لا يوجد رد'));
    });

    test('handles network error from ApiException', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any())).thenThrow(
        ApiException(
          code: 'NETWORK_ERROR',
          message: 'Connection failed',
          isNetworkError: true,
        ),
      );

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isFalse);
      expect(result.errorMessage, contains('internet'));
      expect(result.errorMessageAr, contains('اتصال'));
    });

    test('handles 400 Bad Request from ApiException', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any())).thenThrow(
        ApiException(
          code: 'BAD_REQUEST',
          message: 'Invalid data',
          statusCode: 400,
        ),
      );

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isFalse);
      expect(result.errorMessage, contains('Invalid registration data'));
    });

    test('handles 409 Conflict (duplicate email) from ApiException', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any())).thenThrow(
        ApiException(
          code: 'CONFLICT',
          message: 'Email exists',
          statusCode: 409,
        ),
      );

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isFalse);
      expect(result.errorMessage, contains('already exists'));
      expect(result.errorMessageAr, contains('بالفعل'));
    });

    test('handles 500 server error from ApiException', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any())).thenThrow(
        ApiException(
          code: 'SERVER_ERROR',
          message: 'Internal server error',
          statusCode: 500,
        ),
      );

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isFalse);
      expect(result.errorMessage, contains('Server error'));
      expect(result.errorMessageAr, contains('الخادم'));
    });

    test('handles 422 validation error from ApiException', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any())).thenThrow(
        ApiException(
          code: 'VALIDATION',
          message: 'Email format invalid',
          statusCode: 422,
        ),
      );

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isFalse);
      expect(result.errorMessage, 'Email format invalid');
    });

    test('handles unexpected exceptions gracefully', () async {
      // Arrange
      when(() => mockApiClient.post(any(), any()))
          .thenThrow(Exception('Unexpected'));

      // Act
      final result = await authService.register(validRequest);

      // Assert
      expect(result.success, isFalse);
      expect(result.errorMessage, contains('Registration failed'));
      expect(result.errorMessageAr, contains('فشل التسجيل'));
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // RegistrationAuthService.isLoggedIn Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('RegistrationAuthService.isLoggedIn', () {
    test('returns true when token exists and not expired', () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => 'valid-token');
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => DateTime.now().add(const Duration(hours: 1)));

      // Act
      final result = await authService.isLoggedIn();

      // Assert
      expect(result, isTrue);
    });

    test('returns false when token is null', () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => null);

      // Act
      final result = await authService.isLoggedIn();

      // Assert
      expect(result, isFalse);
    });

    test('returns false when token expiry is null', () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => 'valid-token');
      when(() => mockSecureStorage.getTokenExpiry())
          .thenAnswer((_) async => null);

      // Act
      final result = await authService.isLoggedIn();

      // Assert
      expect(result, isFalse);
    });

    test('returns false when token is expired', () async {
      // Arrange
      when(() => mockSecureStorage.getAccessToken())
          .thenAnswer((_) async => 'valid-token');
      when(() => mockSecureStorage.getTokenExpiry()).thenAnswer(
          (_) async => DateTime.now().subtract(const Duration(hours: 1)));

      // Act
      final result = await authService.isLoggedIn();

      // Assert
      expect(result, isFalse);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // RegistrationAuthService.logout Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('RegistrationAuthService.logout', () {
    test('clears tokens and user data', () async {
      // Arrange
      when(() => mockSecureStorage.deleteTokens()).thenAnswer((_) async {});
      when(() => mockSecureStorage.deleteUserData()).thenAnswer((_) async {});

      // Act
      await authService.logout();

      // Assert
      verify(() => mockSecureStorage.deleteTokens()).called(1);
      verify(() => mockSecureStorage.deleteUserData()).called(1);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // RegistrationAuthService.getCurrentUser Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('RegistrationAuthService.getCurrentUser', () {
    test('returns UserInfo when user data exists', () async {
      // Arrange
      when(() => mockSecureStorage.getUserData()).thenAnswer((_) async => {
            'id': 'user-123',
            'email': 'test@sahool.app',
            'first_name': 'Ahmed',
            'last_name': 'Mohamed',
          });

      // Act
      final user = await authService.getCurrentUser();

      // Assert
      expect(user, isNotNull);
      expect(user!.id, 'user-123');
      expect(user.email, 'test@sahool.app');
      expect(user.firstName, 'Ahmed');
    });

    test('returns null when no user data stored', () async {
      // Arrange
      when(() => mockSecureStorage.getUserData())
          .thenAnswer((_) async => null);

      // Act
      final user = await authService.getCurrentUser();

      // Assert
      expect(user, isNull);
    });
  });
}
