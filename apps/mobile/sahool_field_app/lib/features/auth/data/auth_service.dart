import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';
import '../../../core/config/api_config.dart';
import '../../../core/auth/secure_storage_service.dart';
import '../../../core/di/providers.dart';

/// SAHOOL Authentication Service
/// خدمة المصادقة - تسجيل الدخول والتسجيل
///
/// Features:
/// - User registration with email/password
/// - Token management (store/retrieve/refresh)
/// - Bilingual error handling

/// Provider for auth service
final authServiceProvider = Provider<AuthService>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  final secureStorage = ref.watch(secureStorageProvider);
  return AuthService(
    apiClient: apiClient,
    secureStorage: secureStorage,
  );
});

/// Registration request model
class RegisterRequest {
  final String email;
  final String password;
  final String firstName;
  final String lastName;
  final String? phone;

  RegisterRequest({
    required this.email,
    required this.password,
    required this.firstName,
    required this.lastName,
    this.phone,
  });

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
        if (phone != null && phone!.isNotEmpty) 'phone': phone,
      };
}

/// Auth response model
class AuthResponse {
  final String accessToken;
  final String? refreshToken;
  final DateTime? expiresAt;
  final UserInfo user;

  AuthResponse({
    required this.accessToken,
    this.refreshToken,
    this.expiresAt,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String?,
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      user: UserInfo.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}

/// User info model
class UserInfo {
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String? phone;
  final String? tenantId;

  UserInfo({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.phone,
    this.tenantId,
  });

  factory UserInfo.fromJson(Map<String, dynamic> json) {
    return UserInfo(
      id: json['id'] as String,
      email: json['email'] as String,
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
      phone: json['phone'] as String?,
      tenantId: json['tenant_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'phone': phone,
        'tenant_id': tenantId,
      };

  String get fullName => '$firstName $lastName'.trim();
}

/// Authentication result
class AuthResult {
  final bool success;
  final AuthResponse? response;
  final String? errorMessage;
  final String? errorMessageAr;

  AuthResult({
    required this.success,
    this.response,
    this.errorMessage,
    this.errorMessageAr,
  });

  factory AuthResult.success(AuthResponse response) => AuthResult(
        success: true,
        response: response,
      );

  factory AuthResult.failure({
    required String message,
    required String messageAr,
  }) =>
      AuthResult(
        success: false,
        errorMessage: message,
        errorMessageAr: messageAr,
      );
}

/// Authentication Service
class AuthService {
  final ApiClient _apiClient;
  final SecureStorageService _secureStorage;

  AuthService({
    required ApiClient apiClient,
    required SecureStorageService secureStorage,
  })  : _apiClient = apiClient,
        _secureStorage = secureStorage;

  /// Register a new user
  /// تسجيل مستخدم جديد
  Future<AuthResult> register(RegisterRequest request) async {
    try {
      final response = await _apiClient.post(
        ApiConfig.authRegister,
        request.toJson(),
      );

      if (response == null) {
        return AuthResult.failure(
          message: 'No response from server',
          messageAr: 'لا يوجد رد من الخادم',
        );
      }

      final authResponse = AuthResponse.fromJson(response as Map<String, dynamic>);

      // Store tokens securely
      await _storeAuthData(authResponse);

      // Set auth token on API client
      _apiClient.setAuthToken(authResponse.accessToken);

      // Set tenant ID if available
      if (authResponse.user.tenantId != null) {
        _apiClient.setTenantId(authResponse.user.tenantId!);
        await _secureStorage.setTenantId(authResponse.user.tenantId!);
      }

      return AuthResult.success(authResponse);
    } on ApiException catch (e) {
      return _handleApiError(e);
    } catch (e) {
      return AuthResult.failure(
        message: 'Registration failed: ${e.toString()}',
        messageAr: 'فشل التسجيل: ${e.toString()}',
      );
    }
  }

  /// Store authentication data securely
  Future<void> _storeAuthData(AuthResponse response) async {
    await _secureStorage.setAccessToken(response.accessToken);

    if (response.refreshToken != null) {
      await _secureStorage.setRefreshToken(response.refreshToken!);
    }

    if (response.expiresAt != null) {
      await _secureStorage.setTokenExpiry(response.expiresAt!);
    }

    await _secureStorage.setUserData(response.user.toJson());
  }

  /// Handle API errors with bilingual messages
  AuthResult _handleApiError(ApiException e) {
    if (e.isNetworkError) {
      return AuthResult.failure(
        message: 'No internet connection. Please check your network.',
        messageAr: 'لا يوجد اتصال بالإنترنت. يرجى التحقق من الشبكة.',
      );
    }

    switch (e.statusCode) {
      case 400:
        return AuthResult.failure(
          message: 'Invalid registration data. Please check your inputs.',
          messageAr: 'بيانات التسجيل غير صالحة. يرجى التحقق من المدخلات.',
        );
      case 409:
        return AuthResult.failure(
          message: 'An account with this email already exists.',
          messageAr: 'يوجد حساب بهذا البريد الإلكتروني بالفعل.',
        );
      case 422:
        return AuthResult.failure(
          message: e.message.isNotEmpty ? e.message : 'Validation error',
          messageAr: e.message.isNotEmpty ? e.message : 'خطأ في التحقق من البيانات',
        );
      case 500:
        return AuthResult.failure(
          message: 'Server error. Please try again later.',
          messageAr: 'خطأ في الخادم. يرجى المحاولة مرة أخرى لاحقاً.',
        );
      default:
        return AuthResult.failure(
          message: e.message.isNotEmpty ? e.message : 'An unexpected error occurred',
          messageAr: e.message.isNotEmpty ? e.message : 'حدث خطأ غير متوقع',
        );
    }
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await _secureStorage.getAccessToken();
    if (token == null) return false;

    final isValid = await _secureStorage.isTokenValid();
    return isValid;
  }

  /// Logout user
  Future<void> logout() async {
    await _secureStorage.deleteTokens();
    await _secureStorage.deleteUserData();
  }

  /// Get current user info
  Future<UserInfo?> getCurrentUser() async {
    final userData = await _secureStorage.getUserData();
    if (userData == null) return null;
    return UserInfo.fromJson(userData);
  }
}
