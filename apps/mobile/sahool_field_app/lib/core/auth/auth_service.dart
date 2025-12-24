import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../http/api_client.dart';
import '../utils/app_logger.dart';
import 'secure_storage_service.dart';
import 'biometric_service.dart';

/// SAHOOL Authentication Service
/// خدمة المصادقة مع Token Refresh تلقائي
///
/// Features:
/// - Automatic token refresh with retry mechanism
/// - Token expiration checking
/// - Secure token storage using flutter_secure_storage
/// - Biometric authentication support
/// - Session management
/// - Exponential backoff retry strategy

// Providers
final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(
    secureStorage: ref.read(secureStorageProvider),
    biometricService: ref.read(biometricServiceProvider),
  );
});

final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthState>((ref) {
  return AuthStateNotifier(ref.read(authServiceProvider));
});

/// Alias for backward compatibility
/// اسم بديل للتوافق مع الكود القديم
final authProvider = authStateProvider;

/// Provider for login state
final isLoggedInProvider = Provider<bool>((ref) {
  return ref.watch(authStateProvider).isAuthenticated;
});

/// Provider for current user name
final currentUserNameProvider = Provider<String?>((ref) {
  return ref.watch(authStateProvider).user?.name;
});

/// Auth State
enum AuthStatus { initial, authenticated, unauthenticated, loading }

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? error;

  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.error,
  });

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? error,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      error: error,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
}

/// Auth State Notifier
class AuthStateNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;

  AuthStateNotifier(this._authService) : super(const AuthState()) {
    _init();
  }

  Future<void> _init() async {
    state = state.copyWith(status: AuthStatus.loading);

    try {
      final isLoggedIn = await _authService.isLoggedIn();
      if (isLoggedIn) {
        final user = await _authService.getCurrentUser();
        state = state.copyWith(
          status: AuthStatus.authenticated,
          user: user,
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
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
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
      return true;
    } catch (e) {
      await logout();
      return false;
    }
  }
}

/// Auth Service Implementation
class AuthService {
  final SecureStorageService secureStorage;
  final BiometricService biometricService;

  Timer? _refreshTimer;
  static const _tokenRefreshBuffer = Duration(minutes: 5);

  // Retry configuration
  static const _maxRetries = 3;
  static const _initialRetryDelay = Duration(seconds: 2);
  int _retryCount = 0;

  AuthService({
    required this.secureStorage,
    required this.biometricService,
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Authentication Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Login with email and password
  Future<User> login(String email, String password) async {
    AppLogger.i('Login attempt', tag: 'AUTH', data: {'email': email});

    try {
      // In production, this would call the API
      // final response = await _apiClient.post('/auth/login', {
      //   'email': email,
      //   'password': password,
      // });

      // Simulated response for development
      final tokens = TokenPair(
        accessToken: 'access_token_${DateTime.now().millisecondsSinceEpoch}',
        refreshToken: 'refresh_token_${DateTime.now().millisecondsSinceEpoch}',
        expiresIn: 3600, // 1 hour
      );

      final user = User(
        id: 'user_001',
        email: email,
        name: 'مستخدم سهول',
        role: 'farmer',
        tenantId: 'tenant_1',
      );

      // Store tokens securely
      await _storeTokens(tokens);

      // Store user data securely
      await secureStorage.setUserData(user.toJson());

      // Store tenant ID
      await secureStorage.setTenantId(user.tenantId);

      // Schedule token refresh
      _scheduleTokenRefresh(tokens.expiresIn);

      // Reset retry count on successful login
      _retryCount = 0;

      AppLogger.i('Login successful', tag: 'AUTH');
      return user;
    } catch (e) {
      AppLogger.e('Login failed', tag: 'AUTH', error: e);
      rethrow;
    }
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
    await refreshToken;

    // Get current user
    return getCurrentUser();
  }

  /// Logout
  Future<void> logout() async {
    AppLogger.i('Logout', tag: 'AUTH');

    _cancelTokenRefresh();

    // Clear stored tokens
    await secureStorage.clearAll();

    // In production, also call logout API
    // await _apiClient.post('/auth/logout');
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    final accessToken = await secureStorage.getAccessToken();
    if (accessToken == null) return false;

    // Check if token is expired or about to expire
    if (await isTokenExpired()) {
      // Token expired, try to refresh
      try {
        await refreshToken();
        return true;
      } catch (e) {
        AppLogger.e('Token refresh failed during login check', tag: 'AUTH', error: e);
        return false;
      }
    }

    return true;
  }

  /// Check if token is expired or will expire soon
  Future<bool> isTokenExpired() async {
    final expiry = await secureStorage.getTokenExpiry();
    if (expiry == null) return true;

    // Consider token expired if it expires within the buffer time
    final expiryWithBuffer = expiry.subtract(_tokenRefreshBuffer);
    return DateTime.now().isAfter(expiryWithBuffer);
  }

  /// Get token time until expiry
  Future<Duration?> getTokenTimeUntilExpiry() async {
    final expiry = await secureStorage.getTokenExpiry();
    if (expiry == null) return null;

    final now = DateTime.now();
    if (now.isAfter(expiry)) return Duration.zero;

    return expiry.difference(now);
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

  /// Refresh access token with automatic retry
  Future<void> refreshToken() async {
    return await _refreshTokenWithRetry();
  }

  /// Internal method to refresh token with retry logic
  Future<void> _refreshTokenWithRetry({int attempt = 0}) async {
    AppLogger.i('Refreshing token (attempt ${attempt + 1}/$_maxRetries)', tag: 'AUTH');

    final refreshToken = await secureStorage.getRefreshToken();
    if (refreshToken == null) {
      throw AuthException('لا يوجد refresh token');
    }

    try {
      // In production, call refresh endpoint
      // final response = await _apiClient.post('/auth/refresh', {
      //   'refresh_token': refreshToken,
      // });

      // Simulated response
      final tokens = TokenPair(
        accessToken: 'new_access_token_${DateTime.now().millisecondsSinceEpoch}',
        refreshToken: 'new_refresh_token_${DateTime.now().millisecondsSinceEpoch}',
        expiresIn: 3600,
      );

      await _storeTokens(tokens);
      _scheduleTokenRefresh(tokens.expiresIn);

      // Reset retry count on success
      _retryCount = 0;

      AppLogger.i('Token refreshed successfully', tag: 'AUTH');
    } catch (e) {
      AppLogger.e('Token refresh failed (attempt ${attempt + 1})', tag: 'AUTH', error: e);

      // Retry with exponential backoff
      if (attempt < _maxRetries - 1) {
        final delay = _calculateRetryDelay(attempt);
        AppLogger.i('Retrying token refresh in ${delay.inSeconds}s', tag: 'AUTH');

        await Future.delayed(delay);
        return await _refreshTokenWithRetry(attempt: attempt + 1);
      } else {
        // Max retries reached, logout
        AppLogger.e('Max retry attempts reached, logging out', tag: 'AUTH');
        await logout();
        throw AuthException('فشل تحديث الجلسة بعد عدة محاولات', code: 'MAX_RETRY_REACHED');
      }
    }
  }

  /// Calculate retry delay with exponential backoff
  Duration _calculateRetryDelay(int attempt) {
    // Exponential backoff: 2s, 4s, 8s, etc.
    final multiplier = 1 << attempt; // 2^attempt
    return _initialRetryDelay * multiplier;
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
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      name: json['name'] as String,
      role: json['role'] as String,
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
