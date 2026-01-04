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
/// - Automatic token refresh
/// - Secure token storage
/// - Biometric authentication support
/// - Session management

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

  AuthStateNotifier(this._authService) : super(const AuthState()) {
    _init();
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
}

/// Auth Service Implementation
class AuthService {
  final SecureStorageService secureStorage;
  final BiometricService biometricService;

  Timer? _refreshTimer;
  static const _tokenRefreshBuffer = Duration(minutes: 5);

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

      // Store user data and tenant ID
      await _storeUserData(user);

      // Schedule token refresh
      _scheduleTokenRefresh(tokens.expiresIn);

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
    await refreshToken();

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
  Future<void> refreshToken() async {
    AppLogger.i('Refreshing token', tag: 'AUTH');

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

      AppLogger.i('Token refreshed successfully', tag: 'AUTH');
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'AUTH', error: e);
      await logout();
      rethrow;
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
