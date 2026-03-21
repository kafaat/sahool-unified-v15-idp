/// Authentication Test Fixtures
/// بيانات اختبار المصادقة الثابتة
///
/// Provides test data and fixtures for authentication unit tests.
/// يوفر بيانات اختبار ثابتة لاختبارات وحدة المصادقة

/// Sample user data for tests
class AuthFixtures {
  /// Valid test user data
  static const validUserData = {
    'id': 'user_001',
    'email': 'test@sahool.com',
    'name': 'Test User',
    'role': 'farmer',
    'tenant_id': 'tenant_1',
    'phone': '+966501234567',
    'avatar_url': 'https://example.com/avatar.jpg',
  };

  /// Admin user data
  static const adminUserData = {
    'id': 'admin_001',
    'email': 'admin@sahool.com',
    'name': 'Admin User',
    'role': 'admin',
    'tenant_id': 'tenant_1',
    'phone': '+966509876543',
    'avatar_url': null,
  };

  /// Valid test credentials (test-only domain, never matches production)
  static const validEmail = 'test@test.sahool.local';
  static const validPassword = 'SecurePass123!';
  static const invalidEmail = 'invalid@test.sahool.local';
  static const invalidPassword = 'wrong';

  /// Token fixtures
  static const validAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzAwMSJ9.mock_token';
  static const validRefreshToken = 'refresh_token_mock_12345';
  static const expiredAccessToken = 'expired_token_12345';
  static const invalidToken = 'invalid_token';
  static const tokenExpiresInSeconds = 3600;

  /// Token pair for successful login
  static Map<String, dynamic> get validTokenPair => {
        'access_token': validAccessToken,
        'refresh_token': validRefreshToken,
        'expires_in': tokenExpiresInSeconds,
      };

  /// API login response
  static Map<String, dynamic> get successfulLoginResponse => {
        'access_token': validAccessToken,
        'refresh_token': validRefreshToken,
        'expires_in': tokenExpiresInSeconds,
        'user': validUserData,
      };

  /// API refresh token response
  static Map<String, dynamic> get successfulRefreshResponse => {
        'access_token': 'new_access_token_${DateTime.now().millisecondsSinceEpoch}',
        'refresh_token': 'new_refresh_token_${DateTime.now().millisecondsSinceEpoch}',
        'expires_in': tokenExpiresInSeconds,
      };

  /// Error responses
  static Map<String, dynamic> get invalidCredentialsError => {
        'error': 'INVALID_CREDENTIALS',
        'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
      };

  static Map<String, dynamic> get sessionExpiredError => {
        'error': 'SESSION_EXPIRED',
        'message': 'انتهت صلاحية الجلسة',
      };

  static Map<String, dynamic> get networkError => {
        'error': 'NETWORK_ERROR',
        'message': 'لا يوجد اتصال بالإنترنت',
      };

  /// Token expiry times
  static DateTime get validTokenExpiry =>
      DateTime.now().add(const Duration(hours: 1));
  static DateTime get expiredTokenExpiry =>
      DateTime.now().subtract(const Duration(hours: 1));
  static DateTime get soonToExpireTokenExpiry =>
      DateTime.now().add(const Duration(minutes: 3));

  /// Biometric fixtures
  static const biometricReasonArabic = 'سجل دخولك باستخدام البصمة';
  static const biometricEnableReasonArabic = 'قم بالتحقق لتفعيل تسجيل الدخول بالبصمة';
}

/// Test user factory
class TestUserFactory {
  static Map<String, dynamic> createUser({
    String? id,
    String? email,
    String? name,
    String role = 'farmer',
    String tenantId = 'tenant_1',
    String? phone,
    String? avatarUrl,
  }) {
    return {
      'id': id ?? 'user_${DateTime.now().millisecondsSinceEpoch}',
      'email': email ?? 'test_${DateTime.now().millisecondsSinceEpoch}@sahool.com',
      'name': name ?? 'Test User',
      'role': role,
      'tenant_id': tenantId,
      'phone': phone,
      'avatar_url': avatarUrl,
    };
  }

  static Map<String, dynamic> createLoginResponse({
    Map<String, dynamic>? userData,
    String? accessToken,
    String? refreshToken,
    int expiresIn = 3600,
  }) {
    return {
      'access_token': accessToken ?? 'access_${DateTime.now().millisecondsSinceEpoch}',
      'refresh_token': refreshToken ?? 'refresh_${DateTime.now().millisecondsSinceEpoch}',
      'expires_in': expiresIn,
      'user': userData ?? AuthFixtures.validUserData,
    };
  }
}
