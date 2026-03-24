import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../http/api_client.dart';
import '../config/env_config.dart';
import '../di/providers.dart';
import '../utils/app_logger.dart';
import 'secure_storage_service.dart';
import 'biometric_service.dart';
import 'token_manager.dart';
import 'user_context.dart';

/// SAHOOL Authentication Service
/// خدمة المصادقة مع Token Refresh تلقائي
///
/// Features:
/// - Automatic token refresh with proactive refresh before expiration
/// - Secure token storage using flutter_secure_storage
/// - Biometric authentication support
/// - Session management with TokenManager integration
/// - Background refresh support
/// - Refresh token rotation

// Providers
final authServiceProvider = Provider<AuthService>((ref) {
  // Import apiClientProvider from core/di/providers.dart
  // We use read here to avoid circular dependencies
  try {
    final apiClient = ref.read(apiClientProvider);
    final tokenManager = ref.read(tokenManagerProvider);
    return AuthService(
      secureStorage: ref.read(secureStorageProvider),
      biometricService: ref.read(biometricServiceProvider),
      tokenManager: tokenManager,
      apiClient: apiClient,
    );
  } catch (e) {
    // If apiClientProvider is not available, create AuthService without it
    // This allows for graceful fallback to mock mode
    AppLogger.w('ApiClient not available, using mock mode', tag: 'AUTH');
    final tokenManager = ref.read(tokenManagerProvider);
    return AuthService(
      secureStorage: ref.read(secureStorageProvider),
      biometricService: ref.read(biometricServiceProvider),
      tokenManager: tokenManager,
    );
  }
});

final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthState>((ref) {
  return AuthStateNotifier(ref.read(authServiceProvider));
});

/// Auth State
enum AuthStatus { initial, authenticated, unauthenticated, loading }

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? accessToken;
  final String? error;

  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.accessToken,
    this.error,
  });

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? accessToken,
    String? error,
    bool clearToken = false,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      accessToken: clearToken ? null : (accessToken ?? this.accessToken),
      error: error,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
}

/// Auth State Notifier
class AuthStateNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;
  StreamSubscription<bool>? _authStreamSubscription;
  bool _disposed = false;

  AuthStateNotifier(this._authService) : super(const AuthState()) {
    _init();
    // Subscribe to auth state changes from TokenManager (via AuthService)
    _authStreamSubscription = _authService.authStateStream.listen((isAuthenticated) {
      if (!isAuthenticated && !_disposed) {
        AppLogger.i('Forcing logout due to token refresh failure', tag: 'AUTH');
        state = const AuthState(status: AuthStatus.unauthenticated);
      }
    });
  }

  Future<void> _init() async {
    state = state.copyWith(status: AuthStatus.loading);

    try {
      final isLoggedIn = await _authService.isLoggedIn();
      if (isLoggedIn) {
        final user = await _authService.getCurrentUser();
        final token = await _authService.getAccessToken();
        state = state.copyWith(
          status: AuthStatus.authenticated,
          user: user,
          accessToken: token,
        );
      } else {
        state = state.copyWith(status: AuthStatus.unauthenticated);
      }
    } catch (e) {
      AppLogger.e('Auth init error', error: e);
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
    }
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading);

    try {
      final user = await _authService.login(email, password);
      final token = await _authService.getAccessToken();
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        accessToken: token,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  Future<bool> refreshSession() async {
    try {
      await _authService.refreshToken();
      final token = await _authService.getAccessToken();
      state = state.copyWith(accessToken: token);
      return true;
    } catch (e) {
      await logout();
      return false;
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _authStreamSubscription?.cancel();
    super.dispose();
  }
}

/// Auth Service Implementation
class AuthService {
  final SecureStorageService secureStorage;
  final BiometricService biometricService;
  final TokenManager tokenManager;
  final ApiClient? apiClient;

  Timer? _refreshTimer;
  static const _tokenRefreshBuffer = Duration(minutes: 5);

  /// Stream subscription for auth state changes from TokenManager
  StreamSubscription<bool>? _authStateSubscription;

  /// Stream controller to propagate auth state changes to AuthStateNotifier
  final _authStateController = StreamController<bool>.broadcast();

  /// Stream of auth state changes (consumed by AuthStateNotifier)
  Stream<bool> get authStateStream => _authStateController.stream;

  AuthService({
    required this.secureStorage,
    required this.biometricService,
    required this.tokenManager,
    this.apiClient,
  }) {
    // Initialize TokenManager with API client
    if (apiClient != null) {
      tokenManager.setApiClient(apiClient!);
    }

    // Listen to auth state changes from TokenManager and propagate them
    _authStateSubscription = tokenManager.authStateStream.listen((isAuthenticated) {
      if (!isAuthenticated) {
        AppLogger.i('Auth state changed to unauthenticated via TokenManager', tag: 'AUTH');
        // Propagate to AuthStateNotifier via stream
        _authStateController.add(false);
      }
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Authentication Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Login with email and password
  Future<User> login(String email, String password) async {
    AppLogger.i('Login attempt', tag: 'AUTH', data: {'email': email});

    try {
      // Use real API if available, otherwise fall back to mock in development
      if (apiClient != null && !_shouldUseMockMode()) {
        return await _loginWithApi(email, password);
      } else {
        return await _loginWithMock(email, password);
      }
    } catch (e) {
      AppLogger.e('Login failed', tag: 'AUTH', error: e);

      // In development, fallback to mock if API fails
      if (kDebugMode && e is ApiException && e.isNetworkError) {
        AppLogger.w('API unavailable, falling back to mock mode', tag: 'AUTH');
        return _loginWithMock(email, password);
      }

      rethrow;
    }
  }

  /// Login using real API
  Future<User> _loginWithApi(String email, String password) async {
    AppLogger.i('Logging in via API', tag: 'AUTH');

    try {
      final response = await apiClient!.post(
        '/api/v1/auth/login',
        {
          'email': email,
          'password': password,
        },
      );

      // Parse API response
      if (response == null) {
        throw AuthException('استجابة غير صالحة من الخادم');
      }

      final Map<String, dynamic> data;
      if (response is Map<String, dynamic>) {
        data = response;
      } else {
        data = (response as Map<String, dynamic>)['data'] as Map<String, dynamic>;
      }

      // Extract tokens
      final accessToken = data['access_token'] ?? data['accessToken'];
      final refreshToken = data['refresh_token'] ?? data['refreshToken'];
      final expiresIn = data['expires_in'] ?? data['expiresIn'] ?? 3600;

      if (accessToken == null || refreshToken == null) {
        throw AuthException('بيانات التوكن مفقودة في الاستجابة');
      }

      final tokens = TokenPair(
        accessToken: accessToken as String,
        refreshToken: refreshToken as String,
        expiresIn: expiresIn is int ? expiresIn : int.parse(expiresIn.toString()),
      );

      // Extract user data
      final userData = (data['user'] ?? data) as Map<String, dynamic>;
      final user = User(
        id: (userData['id'] ?? userData['_id'] ?? 'unknown') as String,
        email: (userData['email'] ?? email) as String,
        name: (userData['name'] ?? userData['username'] ?? 'مستخدم') as String,
        role: (userData['role'] ?? 'farmer') as String,
        tenantId: (userData['tenant_id'] ?? userData['tenantId'] ?? EnvConfig.defaultTenantId) as String,
        phone: userData['phone'] as String?,
        avatarUrl: (userData['avatar_url'] ?? userData['avatarUrl']) as String?,
      );

      // Set auth token in API client for subsequent requests
      apiClient!.setAuthToken(tokens.accessToken);
      apiClient!.setTenantId(user.tenantId);

      // تعيين سياق المستأجر للعمليات الخلفية (مزامنة، إشعارات)
      // Set tenant context for background operations (sync, notifications)
      UserContext.setTenantId(user.tenantId);

      // Store tokens using TokenManager for centralized management
      await tokenManager.storeTokens(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        expiresIn: tokens.expiresIn,
      );

      // Store user data securely
      await _storeUserData(user);

      AppLogger.i('API login successful', tag: 'AUTH', data: {'userId': user.id});
      return user;
    } on ApiException catch (e) {
      AppLogger.e('API login failed', tag: 'AUTH', error: e);

      // Convert API exceptions to auth exceptions with Arabic messages
      if (e.statusCode == 401 || e.statusCode == 403) {
        throw AuthException('البريد الإلكتروني أو كلمة المرور غير صحيحة', code: 'INVALID_CREDENTIALS');
      } else if (e.isNetworkError) {
        throw AuthException('لا يوجد اتصال بالإنترنت', code: 'NETWORK_ERROR');
      } else {
        throw AuthException(e.message, code: e.code);
      }
    }
  }

  /// Login using mock data (development only)
  Future<User> _loginWithMock(String email, String password) async {
    AppLogger.w('Using MOCK login (development only)', tag: 'AUTH');

    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    // Simulated response for development
    final tokens = TokenPair(
      accessToken: 'mock_access_token_${DateTime.now().millisecondsSinceEpoch}',
      refreshToken: 'mock_refresh_token_${DateTime.now().millisecondsSinceEpoch}',
      expiresIn: 3600, // 1 hour
    );

    final user = User(
      id: 'mock_user_001',
      email: email,
      name: 'مستخدم تجريبي',
      role: 'farmer',
      tenantId: 'mock_tenant',
    );

    // Set tenant context for background operations
    UserContext.setTenantId(user.tenantId);

    // Store tokens using TokenManager for centralized management
    await tokenManager.storeTokens(
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
      expiresIn: tokens.expiresIn,
    );

    // Store user data and tenant ID
    await _storeUserData(user);

    AppLogger.i('Mock login successful', tag: 'AUTH');
    return user;
  }

  /// Check if mock mode should be used
  bool _shouldUseMockMode() {
    // Use mock mode only in debug builds when explicitly enabled
    // In production builds, always use real API
    return kDebugMode && const bool.fromEnvironment('USE_MOCK_AUTH', defaultValue: false);
  }

  /// Reset password with token
  /// إعادة تعيين كلمة المرور باستخدام رمز التحقق
  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    AppLogger.i('Reset password attempt', tag: 'AUTH');

    try {
      // Use real API if available, otherwise fall back to mock in development
      if (apiClient != null && !_shouldUseMockMode()) {
        await _resetPasswordWithApi(token, newPassword);
      } else {
        await _resetPasswordWithMock();
      }
    } catch (e) {
      AppLogger.e('Reset password failed', tag: 'AUTH', error: e);

      // In development, fallback to mock if API fails
      if (kDebugMode && e is ApiException && e.isNetworkError) {
        AppLogger.w('API unavailable, falling back to mock mode', tag: 'AUTH');
        await _resetPasswordWithMock();
        return;
      }

      rethrow;
    }
  }

  /// Reset password using real API
  Future<void> _resetPasswordWithApi(String token, String newPassword) async {
    AppLogger.i('Resetting password via API', tag: 'AUTH');

    try {
      final response = await apiClient!.post(
        '/api/v1/auth/reset-password',
        {
          'token': token,
          'newPassword': newPassword,
        },
      );

      // Parse API response
      if (response == null) {
        throw AuthException('استجابة غير صالحة من الخادم');
      }

      final Map<String, dynamic> data;
      if (response is Map<String, dynamic>) {
        data = response;
      } else {
        data = (response as Map<String, dynamic>)['data'] as Map<String, dynamic>;
      }
      final success = (data['success'] as bool?) ?? false;

      if (!success) {
        final message = (data['message'] ?? 'فشل تغيير كلمة المرور') as String;
        throw AuthException(message);
      }

      AppLogger.i('API password reset successful', tag: 'AUTH');
    } on ApiException catch (e) {
      AppLogger.e('API password reset failed', tag: 'AUTH', error: e);

      // Convert API exceptions to auth exceptions with Arabic messages
      if (e.statusCode == 400) {
        throw AuthException('رمز التحقق غير صالح أو منتهي الصلاحية', code: 'INVALID_TOKEN');
      } else if (e.statusCode == 429) {
        throw AuthException('محاولات كثيرة جداً. يرجى المحاولة لاحقاً', code: 'TOO_MANY_ATTEMPTS');
      } else if (e.isNetworkError) {
        throw AuthException('لا يوجد اتصال بالإنترنت', code: 'NETWORK_ERROR');
      } else {
        throw AuthException(e.message, code: e.code);
      }
    }
  }

  /// Reset password using mock data (development only)
  Future<void> _resetPasswordWithMock() async {
    AppLogger.w('Using MOCK password reset (development only)', tag: 'AUTH');

    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    AppLogger.i('Mock password reset successful', tag: 'AUTH');
  }

  /// Login with biometric
  Future<User?> loginWithBiometric() async {
    AppLogger.i('Biometric login attempt', tag: 'AUTH');

    // Check if biometric is available and enabled
    if (!await biometricService.isAvailable()) {
      throw AuthException('البصمة غير متاحة على هذا الجهاز');
    }

    if (!await biometricService.isEnabled()) {
      throw AuthException('البصمة غير مفعلة');
    }

    // Authenticate with biometric
    final authenticated = await biometricService.authenticate(
      reason: 'سجل دخولك باستخدام البصمة',
    );

    if (!authenticated) {
      throw AuthException('فشل التحقق من البصمة');
    }

    // Get stored credentials
    final refreshToken = await secureStorage.getRefreshToken();
    if (refreshToken == null) {
      throw AuthException('لا توجد جلسة محفوظة');
    }

    // Refresh token to get new access token
    await this.refreshToken();

    // Get current user
    return getCurrentUser();
  }

  /// Logout
  Future<void> logout() async {
    AppLogger.i('Logout', tag: 'AUTH');

    _cancelTokenRefresh();

    // Call logout API if available (best effort - don't fail if it errors)
    if (apiClient != null && !_shouldUseMockMode()) {
      try {
        await apiClient!.post('/api/v1/auth/logout', {});
        AppLogger.i('Logout API call successful', tag: 'AUTH');
      } catch (e) {
        // Log but don't fail - local logout should always succeed
        AppLogger.w('Logout API call failed (continuing with local logout)', tag: 'AUTH', data: {'error': e.toString()});
      }
    }

    // مسح سياق المستأجر عند تسجيل الخروج
    // Clear tenant context on logout
    UserContext.clear();

    // Use TokenManager for centralized logout
    // This handles clearing tokens, API client state, and notifying listeners
    await tokenManager.logout();

    AppLogger.i('Logout complete', tag: 'AUTH');
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    final accessToken = await secureStorage.getAccessToken();
    if (accessToken == null) return false;

    // Check if token is expired
    final expiry = await secureStorage.getTokenExpiry();
    if (expiry == null) return false;

    if (DateTime.now().isAfter(expiry)) {
      // Token expired, try to refresh
      try {
        await refreshToken();
        return true;
      } catch (e) {
        return false;
      }
    }

    return true;
  }

  /// Get current user
  Future<User?> getCurrentUser() async {
    final userData = await secureStorage.getUserData();
    if (userData == null) return null;

    return User.fromJson(userData);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Token Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Refresh access token
  /// Uses TokenManager for centralized token refresh with retry logic
  Future<void> refreshToken() async {
    AppLogger.i('Refreshing token via TokenManager', tag: 'AUTH');

    try {
      // Delegate to TokenManager which handles:
      // - Exponential backoff retries
      // - Token rotation
      // - Background refresh scheduling
      await tokenManager.refreshToken();
      AppLogger.i('Token refresh successful', tag: 'AUTH');
    } on TokenRefreshException catch (e) {
      AppLogger.e('Token refresh failed', tag: 'AUTH', error: e);

      // Convert to AuthException for backwards compatibility
      if (e.code == 'NO_REFRESH_TOKEN') {
        throw AuthException('لا يوجد refresh token', code: e.code);
      } else if (e.code == 'SESSION_EXPIRED') {
        throw AuthException('انتهت صلاحية الجلسة', code: e.code);
      } else {
        throw AuthException(e.message, code: e.code);
      }
    } catch (e) {
      AppLogger.e('Token refresh failed with unexpected error', tag: 'AUTH', error: e);

      // In development, log additional details
      if (kDebugMode) {
        AppLogger.d('Token refresh error details: $e', tag: 'AUTH');
      }

      throw AuthException('فشل تحديث التوكن', code: 'REFRESH_FAILED');
    }
  }

  /// Get current access token
  Future<String?> getAccessToken() async {
    return secureStorage.getAccessToken();
  }

  /// Store tokens securely
  Future<void> _storeTokens(TokenPair tokens) async {
    await secureStorage.setAccessToken(tokens.accessToken);
    await secureStorage.setRefreshToken(tokens.refreshToken);

    final expiry = DateTime.now().add(Duration(seconds: tokens.expiresIn));
    await secureStorage.setTokenExpiry(expiry);
  }

  /// Store user data securely
  Future<void> _storeUserData(User user) async {
    await secureStorage.setUserData(user.toJson());
    await secureStorage.setTenantId(user.tenantId);
  }

  /// Schedule automatic token refresh
  void _scheduleTokenRefresh(int expiresInSeconds) {
    _cancelTokenRefresh();

    // Refresh before expiry
    final refreshIn = Duration(seconds: expiresInSeconds) - _tokenRefreshBuffer;
    if (refreshIn.isNegative) return;

    _refreshTimer = Timer(refreshIn, () async {
      try {
        await refreshToken();
      } catch (e) {
        AppLogger.e('Scheduled token refresh failed', tag: 'AUTH', error: e);
      }
    });

    AppLogger.d(
      'Token refresh scheduled in ${refreshIn.inMinutes} minutes',
      tag: 'AUTH',
    );
  }

  /// Cancel scheduled token refresh
  void _cancelTokenRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = null;
  }

  /// Dispose resources
  void dispose() {
    _cancelTokenRefresh();
    _authStateSubscription?.cancel();
    _authStateSubscription = null;
    _authStateController.close();
    tokenManager.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Models
// ═══════════════════════════════════════════════════════════════════════════

/// User model
class User {
  final String id;
  final String email;
  final String name;
  final String role;
  final String tenantId;
  final String? phone;
  final String? avatarUrl;

  const User({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    required this.tenantId,
    this.phone,
    this.avatarUrl,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    final email = json['email'] as String;
    return User(
      id: json['id'] as String,
      email: email,
      name: (json['name'] as String?) ?? email,
      role: (json['role'] as String?) ?? 'viewer',
      tenantId: json['tenant_id'] as String,
      phone: json['phone'] as String?,
      avatarUrl: json['avatar_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'role': role,
      'tenant_id': tenantId,
      'phone': phone,
      'avatar_url': avatarUrl,
    };
  }
}

/// Token pair
class TokenPair {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;

  const TokenPair({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });
}

/// Auth exception
class AuthException implements Exception {
  final String message;
  final String? code;

  AuthException(this.message, {this.code});

  @override
  String toString() => message;
}
