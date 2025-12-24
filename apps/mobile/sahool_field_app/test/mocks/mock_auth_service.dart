import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/auth/biometric_service.dart';

/// Mock AuthService for testing
/// خدمة المصادقة الوهمية للاختبارات
class MockAuthService extends Mock implements AuthService {
  User? _currentUser;
  bool _isLoggedIn = false;
  String? _accessToken;

  MockAuthService({
    User? currentUser,
    bool isLoggedIn = false,
  }) {
    _currentUser = currentUser;
    _isLoggedIn = isLoggedIn;
    _accessToken = isLoggedIn ? 'mock_access_token' : null;
  }

  /// Set current user
  void setCurrentUser(User? user) {
    _currentUser = user;
    _isLoggedIn = user != null;
    _accessToken = user != null ? 'mock_access_token_${user.id}' : null;
  }

  /// Simulate successful login
  Future<User> simulateLogin(String email, String password) async {
    final user = User(
      id: 'user_${DateTime.now().millisecondsSinceEpoch}',
      email: email,
      name: 'Test User',
      role: 'farmer',
      tenantId: 'tenant_test',
    );
    setCurrentUser(user);
    return user;
  }

  /// Simulate logout
  Future<void> simulateLogout() async {
    _currentUser = null;
    _isLoggedIn = false;
    _accessToken = null;
  }

  @override
  Future<User> login(String email, String password) async {
    return simulateLogin(email, password);
  }

  @override
  Future<void> logout() async {
    return simulateLogout();
  }

  @override
  Future<bool> isLoggedIn() async {
    return _isLoggedIn;
  }

  @override
  Future<User?> getCurrentUser() async {
    return _currentUser;
  }

  @override
  Future<String?> getAccessToken() async {
    return _accessToken;
  }

  @override
  Future<void> refreshToken() async {
    if (_isLoggedIn) {
      _accessToken = 'refreshed_token_${DateTime.now().millisecondsSinceEpoch}';
    } else {
      throw AuthException('Not logged in');
    }
  }

  @override
  SecureStorageService get secureStorage => MockSecureStorageService();

  @override
  BiometricService get biometricService => MockBiometricService();
}

/// Mock SecureStorageService for testing
class MockSecureStorageService extends Mock implements SecureStorageService {
  final Map<String, String> _storage = {};

  @override
  Future<String?> getAccessToken() async {
    return _storage['access_token'];
  }

  @override
  Future<void> setAccessToken(String token) async {
    _storage['access_token'] = token;
  }

  @override
  Future<String?> getRefreshToken() async {
    return _storage['refresh_token'];
  }

  @override
  Future<void> setRefreshToken(String token) async {
    _storage['refresh_token'] = token;
  }

  @override
  Future<void> clearAll() async {
    _storage.clear();
  }
}

/// Mock BiometricService for testing
class MockBiometricService extends Mock implements BiometricService {
  bool _isAvailable = true;
  bool _isEnabled = false;
  bool _willAuthenticate = true;

  void setAvailable(bool available) {
    _isAvailable = available;
  }

  void setEnabled(bool enabled) {
    _isEnabled = enabled;
  }

  void setWillAuthenticate(bool willAuth) {
    _willAuthenticate = willAuth;
  }

  @override
  Future<bool> isAvailable() async {
    return _isAvailable;
  }

  @override
  Future<bool> isEnabled() async {
    return _isEnabled;
  }

  @override
  Future<bool> authenticate({required String reason}) async {
    return _willAuthenticate;
  }

  @override
  Future<void> enable() async {
    _isEnabled = true;
  }

  @override
  Future<void> disable() async {
    _isEnabled = false;
  }
}
