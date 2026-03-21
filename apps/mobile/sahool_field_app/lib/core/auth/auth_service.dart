import 'dart:async';
import 'dart:math' show pow;
import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../http/api_client.dart';
import '../config/env_config.dart';
import '../di/providers.dart';
import '../utils/app_logger.dart';
import '../security/security_audit_service.dart';
import 'secure_storage_service.dart';
import 'biometric_service.dart';
import 'user_context.dart';

/// SAHOOL Authentication Service
/// خدمة المصادقة مع Token Refresh تلقائي
///
/// Features:
/// - Automatic token refresh with race condition protection
/// - Secure token storage with validation
/// - Biometric authentication support
/// - Session management with app lifecycle handling
/// - Proper logout and token revocation

// Providers
final userContextProvider = Provider<UserContext>((ref) {
  return UserContext();
});

final authServiceProvider = Provider<AuthService>((ref) {
  // Import apiClientProvider from core/di/providers.dart
  // We use read here to avoid circular dependencies
  try {
    final apiClient = ref.read(apiClientProvider);
    return AuthService(
      secureStorage: ref.read(secureStorageProvider),
      biometricService: ref.read(biometricServiceProvider),
      userContext: ref.read(userContextProvider),
      apiClient: apiClient,
      auditService: ref.read(securityAuditServiceProvider),
    );
  } catch (e) {
    // If apiClientProvider is not available, create AuthService without it
    // This allows for graceful fallback to mock mode
    AppLogger.w('ApiClient not available, using mock mode', tag: 'AUTH');
    return AuthService(
      secureStorage: ref.read(secureStorageProvider),
      biometricService: ref.read(biometricServiceProvider),
      userContext: ref.read(userContextProvider),
    );
  }
});

final authStateProvider =
    StateNotifierProvider<AuthStateNotifier, AuthState>((ref) {
  return AuthStateNotifier(ref.read(authServiceProvider));
});

/// Auth State
enum AuthStatus {
  initial,
  authenticated,
  unauthenticated,
  loading,
  sessionExpired
}

/// Session information for tracking session health
class SessionInfo {
  final DateTime? tokenExpiresAt;
  final DateTime? lastActivity;
  final DateTime? sessionStartedAt;
  final bool isBiometricSession;

  const SessionInfo({
    this.tokenExpiresAt,
    this.lastActivity,
    this.sessionStartedAt,
    this.isBiometricSession = false,
  });

  /// Check if session is about to expire (within buffer)
  bool isExpiringSoon(Duration buffer) {
    if (tokenExpiresAt == null) return true;
    return DateTime.now().add(buffer).isAfter(tokenExpiresAt!);
  }

  /// Check if session has been idle too long
  bool isIdleTooLong(Duration maxIdleTime) {
    if (lastActivity == null) return false;
    return DateTime.now().difference(lastActivity!) > maxIdleTime;
  }

  SessionInfo copyWith({
    DateTime? tokenExpiresAt,
    DateTime? lastActivity,
    DateTime? sessionStartedAt,
    bool? isBiometricSession,
  }) {
    return SessionInfo(
      tokenExpiresAt: tokenExpiresAt ?? this.tokenExpiresAt,
      lastActivity: lastActivity ?? this.lastActivity,
      sessionStartedAt: sessionStartedAt ?? this.sessionStartedAt,
      isBiometricSession: isBiometricSession ?? this.isBiometricSession,
    );
  }
}

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? accessToken;
  final String? error;
  final SessionInfo sessionInfo;

  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.accessToken,
    this.error,
    this.sessionInfo = const SessionInfo(),
  });

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? accessToken,
    String? error,
    SessionInfo? sessionInfo,
    bool clearToken = false,
    bool clearUser = false,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: clearUser ? null : (user ?? this.user),
      accessToken: clearToken ? null : (accessToken ?? this.accessToken),
      error: error,
      sessionInfo: sessionInfo ?? this.sessionInfo,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
  bool get isSessionExpired => status == AuthStatus.sessionExpired;
}

/// Auth State Notifier with session management
class AuthStateNotifier extends StateNotifier<AuthState>
    with WidgetsBindingObserver {
  final AuthService _authService;
  Timer? _sessionCheckTimer;
  DateTime? _lastActiveTime;

  // Session configuration
  static const _sessionCheckInterval = Duration(minutes: 1);
  static const _maxIdleTime = Duration(minutes: 30);

  AuthStateNotifier(this._authService) : super(const AuthState()) {
    WidgetsBinding.instance.addObserver(this);
    _init();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _sessionCheckTimer?.cancel();
    _authService.dispose();
    super.dispose();
  }

  /// Handle app lifecycle changes
  @override
  void didChangeAppLifecycleState(AppLifecycleState appState) {
    switch (appState) {
      case AppLifecycleState.resumed:
        _onAppResumed();
        break;
      case AppLifecycleState.paused:
        _onAppPaused();
        break;
      case AppLifecycleState.inactive:
      case AppLifecycleState.detached:
      case AppLifecycleState.hidden:
        break;
    }
  }

  void _onAppResumed() {
    AppLogger.d('App resumed, checking session', tag: 'AUTH');
    _checkSessionOnResume();
    _startSessionMonitoring();
  }

  void _onAppPaused() {
    AppLogger.d('App paused', tag: 'AUTH');
    _lastActiveTime = DateTime.now();
    _stopSessionMonitoring();
  }

  Future<void> _checkSessionOnResume() async {
    if (state.status != AuthStatus.authenticated) return;

    try {
      // Check if we were paused for too long (idle timeout)
      if (_lastActiveTime != null) {
        final idleDuration = DateTime.now().difference(_lastActiveTime!);
        if (idleDuration > _maxIdleTime) {
          AppLogger.w('Session idle for too long, requiring re-authentication',
              tag: 'AUTH');
          await _handleSessionExpired(reason: 'انتهت الجلسة بسبب عدم النشاط');
          return;
        }
      }

      // Validate session is still valid
      final isValid = await _authService.validateSession();
      if (!isValid) {
        AppLogger.w('Session invalidated while app was paused', tag: 'AUTH');
        await _handleSessionExpired(reason: 'انتهت صلاحية الجلسة');
        return;
      }

      // Proactively refresh if token is expiring soon
      final tokenExpiry = await _authService.getTokenExpiry();
      if (tokenExpiry != null) {
        final timeUntilExpiry = tokenExpiry.difference(DateTime.now());
        if (timeUntilExpiry < const Duration(minutes: 10)) {
          AppLogger.i('Token expiring soon, proactively refreshing',
              tag: 'AUTH');
          await refreshSession();
        }
      }

      // Update session info
      _updateSessionInfo();
    } catch (e) {
      AppLogger.e('Session check on resume failed', error: e, tag: 'AUTH');
    }
  }

  void _startSessionMonitoring() {
    _sessionCheckTimer?.cancel();
    _sessionCheckTimer = Timer.periodic(_sessionCheckInterval, (_) {
      _checkSession();
    });
  }

  void _stopSessionMonitoring() {
    _sessionCheckTimer?.cancel();
    _sessionCheckTimer = null;
  }

  Future<void> _checkSession() async {
    if (state.status != AuthStatus.authenticated) return;

    try {
      final isValid = await _authService.validateSession();
      if (!isValid) {
        await _handleSessionExpired(reason: 'انتهت صلاحية الجلسة');
      }
    } catch (e) {
      AppLogger.e('Periodic session check failed', error: e, tag: 'AUTH');
    }
  }

  Future<void> _handleSessionExpired({required String reason}) async {
    _stopSessionMonitoring();
    await _authService.clearLocalSession();
    state = AuthState(
      status: AuthStatus.sessionExpired,
      error: reason,
    );
  }

  Future<void> _updateSessionInfo() async {
    final tokenExpiry = await _authService.getTokenExpiry();
    state = state.copyWith(
      sessionInfo: state.sessionInfo.copyWith(
        tokenExpiresAt: tokenExpiry,
        lastActivity: DateTime.now(),
      ),
    );
  }

  Future<void> _init() async {
    state = state.copyWith(status: AuthStatus.loading);

    try {
      final isLoggedIn = await _authService.isLoggedIn();
      if (isLoggedIn) {
        final user = await _authService.getCurrentUser();
        final token = await _authService.getAccessToken();
        final tokenExpiry = await _authService.getTokenExpiry();

        state = state.copyWith(
          status: AuthStatus.authenticated,
          user: user,
          accessToken: token,
          sessionInfo: SessionInfo(
            tokenExpiresAt: tokenExpiry,
            lastActivity: DateTime.now(),
            sessionStartedAt: DateTime.now(),
          ),
        );
        _startSessionMonitoring();
      } else {
        state = state.copyWith(status: AuthStatus.unauthenticated);
      }
    } catch (e) {
      AppLogger.e('Auth init error', error: e, tag: 'AUTH');
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
      final tokenExpiry = await _authService.getTokenExpiry();

      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        accessToken: token,
        sessionInfo: SessionInfo(
          tokenExpiresAt: tokenExpiry,
          lastActivity: DateTime.now(),
          sessionStartedAt: DateTime.now(),
          isBiometricSession: false,
        ),
      );
      _startSessionMonitoring();
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
      return false;
    }
  }

  /// Login with biometric authentication
  Future<bool> loginWithBiometric() async {
    state = state.copyWith(status: AuthStatus.loading);

    try {
      final user = await _authService.loginWithBiometric();
      if (user == null) {
        state = state.copyWith(
          status: AuthStatus.unauthenticated,
          error: 'فشل تسجيل الدخول بالبصمة',
        );
        return false;
      }

      final token = await _authService.getAccessToken();
      final tokenExpiry = await _authService.getTokenExpiry();

      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        accessToken: token,
        sessionInfo: SessionInfo(
          tokenExpiresAt: tokenExpiry,
          lastActivity: DateTime.now(),
          sessionStartedAt: DateTime.now(),
          isBiometricSession: true,
        ),
      );
      _startSessionMonitoring();
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
    _stopSessionMonitoring();
    await _authService.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  /// Force logout (e.g., from remote session invalidation)
  Future<void> forceLogout({String? reason}) async {
    _stopSessionMonitoring();
    await _authService.clearLocalSession();
    state = AuthState(
      status: AuthStatus.unauthenticated,
      error: reason ?? 'تم تسجيل الخروج من جلستك',
    );
  }

  Future<bool> refreshSession() async {
    try {
      await _authService.refreshToken();
      final token = await _authService.getAccessToken();
      final tokenExpiry = await _authService.getTokenExpiry();

      state = state.copyWith(
        accessToken: token,
        sessionInfo: state.sessionInfo.copyWith(
          tokenExpiresAt: tokenExpiry,
          lastActivity: DateTime.now(),
        ),
      );
      return true;
    } catch (e) {
      AppLogger.e('Session refresh failed', error: e, tag: 'AUTH');
      await _handleSessionExpired(reason: 'فشل تجديد الجلسة');
      return false;
    }
  }

  /// Record user activity to prevent idle timeout
  void recordActivity() {
    _lastActiveTime = DateTime.now();
    if (state.status == AuthStatus.authenticated) {
      state = state.copyWith(
        sessionInfo: state.sessionInfo.copyWith(
          lastActivity: DateTime.now(),
        ),
      );
    }
  }
}

/// Auth Service Implementation
class AuthService {
  final SecureStorageService secureStorage;
  final BiometricService biometricService;
  final UserContext userContext;
  final ApiClient? apiClient;
  final SecurityAuditService? auditService;

  Timer? _refreshTimer;
  bool _isRefreshing = false;
  Completer<void>? _refreshCompleter;

  static const _tokenRefreshBuffer = Duration(minutes: 5);
  static const _tokenRefreshBaseDelay = Duration(seconds: 2);
  static const _maxRefreshRetries = 3;

  // Session tracking
  String? _currentSessionId;
  int _refreshRetryCount = 0;

  AuthService({
    required this.secureStorage,
    required this.biometricService,
    required this.userContext,
    this.apiClient,
    this.auditService,
  });

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
        return await _loginWithMock(email, password);
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

      final data =
          response is Map<String, dynamic> ? response : response['data'];

      // Extract tokens
      final accessToken = data['access_token'] ?? data['accessToken'];
      final refreshToken = data['refresh_token'] ?? data['refreshToken'];
      final expiresIn = data['expires_in'] ?? data['expiresIn'] ?? 3600;
      final sessionId = data['session_id'] ?? data['sessionId'];

      if (accessToken == null || refreshToken == null) {
        throw AuthException('بيانات التوكن مفقودة في الاستجابة');
      }

      final tokens = TokenPair(
        accessToken: accessToken as String,
        refreshToken: refreshToken as String,
        expiresIn:
            expiresIn is int ? expiresIn : int.parse(expiresIn.toString()),
      );

      // Extract user data
      final userData = data['user'] ?? data;
      final user = User(
        id: userData['id'] ?? userData['_id'] ?? 'unknown',
        email: userData['email'] ?? email,
        name: userData['name'] ?? userData['username'] ?? 'مستخدم',
        role: userData['role'] ?? 'farmer',
        tenantId: userData['tenant_id'] ??
            userData['tenantId'] ??
            EnvConfig.defaultTenantId,
        phone: userData['phone'],
        avatarUrl: userData['avatar_url'] ?? userData['avatarUrl'],
      );

      // Set auth token in API client for subsequent requests
      apiClient!.setAuthToken(tokens.accessToken);
      apiClient!.setTenantId(user.tenantId);

      // Store tokens and user data securely
      await _storeTokens(tokens);
      await _storeUserData(user);

      // Store session ID for session management
      _currentSessionId = sessionId as String?;
      if (_currentSessionId != null) {
        await secureStorage.write('session_id', _currentSessionId!);
      }

      // Sync user context with full information
      userContext.setUser(user.id, tenantId: user.tenantId, role: user.role);

      // Reset refresh retry count on successful login
      _refreshRetryCount = 0;

      // Schedule token refresh
      _scheduleTokenRefresh(tokens.expiresIn);

      AppLogger.i('API login successful',
          tag: 'AUTH', data: {'userId': user.id});
      return user;
    } on ApiException catch (e) {
      AppLogger.e('API login failed', tag: 'AUTH', error: e);

      // Convert API exceptions to auth exceptions with Arabic messages
      if (e.statusCode == 401 || e.statusCode == 403) {
        throw AuthException('البريد الإلكتروني أو كلمة المرور غير صحيحة',
            code: 'INVALID_CREDENTIALS');
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
      refreshToken:
          'mock_refresh_token_${DateTime.now().millisecondsSinceEpoch}',
      expiresIn: 3600, // 1 hour
    );

    final user = User(
      id: 'mock_user_001',
      email: email,
      name: 'مستخدم تجريبي',
      role: 'farmer',
      tenantId: 'mock_tenant',
    );

    // Store tokens securely
    await _storeTokens(tokens);

    // Store user data and tenant ID
    await _storeUserData(user);

    // Sync user context with full information
    userContext.setUser(user.id, tenantId: user.tenantId, role: user.role);

    // Reset refresh retry count on successful login
    _refreshRetryCount = 0;

    // Schedule token refresh
    _scheduleTokenRefresh(tokens.expiresIn);

    AppLogger.i('Mock login successful', tag: 'AUTH');
    return user;
  }

  /// Check if mock mode should be used
  bool _shouldUseMockMode() {
    // Use mock mode only in debug builds when explicitly enabled
    // In production builds, always use real API
    return kDebugMode &&
        const bool.fromEnvironment('USE_MOCK_AUTH', defaultValue: false);
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

      final data =
          response is Map<String, dynamic> ? response : response['data'];
      final success = data['success'] ?? false;

      if (!success) {
        final message = data['message'] ?? 'فشل تغيير كلمة المرور';
        throw AuthException(message);
      }

      AppLogger.i('API password reset successful', tag: 'AUTH');
    } on ApiException catch (e) {
      AppLogger.e('API password reset failed', tag: 'AUTH', error: e);

      // Convert API exceptions to auth exceptions with Arabic messages
      if (e.statusCode == 400) {
        throw AuthException('رمز التحقق غير صالح أو منتهي الصلاحية',
            code: 'INVALID_TOKEN');
      } else if (e.statusCode == 429) {
        throw AuthException('محاولات كثيرة جداً. يرجى المحاولة لاحقاً',
            code: 'TOO_MANY_ATTEMPTS');
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
      throw AuthException('البصمة غير متاحة على هذا الجهاز',
          code: 'BIOMETRIC_NOT_AVAILABLE');
    }

    if (!await biometricService.isEnabled()) {
      throw AuthException('البصمة غير مفعلة', code: 'BIOMETRIC_NOT_ENABLED');
    }

    // Verify a valid session exists before attempting biometric auth
    final storedRefreshToken = await secureStorage.getRefreshToken();
    if (storedRefreshToken == null) {
      throw AuthException('لا توجد جلسة محفوظة. يرجى تسجيل الدخول أولاً',
          code: 'NO_STORED_SESSION');
    }

    // Check if refresh token might be expired (stored user data exists)
    final userData = await secureStorage.getUserData();
    if (userData == null) {
      // User data missing, session is invalid
      await clearLocalSession();
      throw AuthException('انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى',
          code: 'SESSION_INVALID');
    }

    // Authenticate with biometric
    final authenticated = await biometricService.authenticate(
      reason: 'سجل دخولك باستخدام البصمة',
    );

    if (!authenticated) {
      throw AuthException('فشل التحقق من البصمة', code: 'BIOMETRIC_FAILED');
    }

    try {
      // Refresh token to get a new access token
      await refreshToken();

      // Sync user context with full information
      final user = await getCurrentUser();
      if (user != null) {
        userContext.setUser(user.id, tenantId: user.tenantId, role: user.role);
      }

      // Get current user
      return user;
    } catch (e) {
      // If refresh fails, the session is invalid
      AppLogger.e('Biometric login failed during token refresh',
          error: e, tag: 'AUTH');
      await clearLocalSession();
      throw AuthException('انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى',
          code: 'SESSION_EXPIRED');
    }
  }

  /// Logout with proper token revocation
  Future<void> logout() async {
    AppLogger.i('Logout initiated', tag: 'AUTH');

    _cancelTokenRefresh();

    // Get refresh token before clearing storage (for revocation)
    final refreshToken = await secureStorage.getRefreshToken();
    final sessionId =
        _currentSessionId ?? await secureStorage.read('session_id');

    // Call logout API if available (best effort - don't fail if it errors)
    if (apiClient != null && !_shouldUseMockMode()) {
      try {
        // Revoke refresh token explicitly
        await apiClient!.post('/api/v1/auth/logout', {
          'refresh_token': refreshToken,
          'session_id': sessionId,
          'revoke_all_sessions': false,
        });
        AppLogger.i('Logout API call successful - tokens revoked', tag: 'AUTH');
      } catch (e) {
        // Log but don't fail - local logout should always succeed
        AppLogger.w('Logout API call failed (continuing with local logout): $e',
            tag: 'AUTH');
      }
    }

    // Clear auth token from API client
    if (apiClient != null) {
      apiClient!.setAuthToken('');
    }

    // Clear user context
    userContext.clearUser();

    // Clear session ID
    _currentSessionId = null;

    // Clear stored tokens and user data
    await secureStorage.clearAll();

    // Reset state
    _refreshRetryCount = 0;
    _isRefreshing = false;
    _refreshCompleter = null;

    AppLogger.i('Logout complete - all local data cleared', tag: 'AUTH');
  }

  /// Clear local session without calling logout API
  /// Used for session expiry or forced logout
  Future<void> clearLocalSession() async {
    AppLogger.i('Clearing local session', tag: 'AUTH');

    _cancelTokenRefresh();

    // Clear auth token from API client
    if (apiClient != null) {
      apiClient!.setAuthToken('');
    }

    // Clear user context
    userContext.clearUser();

    // Clear session ID
    _currentSessionId = null;

    // Clear stored tokens and user data
    await secureStorage.clearAll();

    // Reset state
    _refreshRetryCount = 0;
    _isRefreshing = false;
    _refreshCompleter = null;

    AppLogger.i('Local session cleared', tag: 'AUTH');
  }

  /// Logout from all devices
  Future<void> logoutAllDevices() async {
    AppLogger.i('Logout from all devices initiated', tag: 'AUTH');

    _cancelTokenRefresh();

    final refreshToken = await secureStorage.getRefreshToken();

    // Call logout API with revoke_all_sessions flag
    if (apiClient != null && !_shouldUseMockMode()) {
      try {
        await apiClient!.post('/api/v1/auth/logout', {
          'refresh_token': refreshToken,
          'revoke_all_sessions': true,
        });
        AppLogger.i('All sessions revoked via API', tag: 'AUTH');
      } catch (e) {
        AppLogger.w('Failed to revoke all sessions via API: $e', tag: 'AUTH');
      }
    }

    // Clear auth token from API client
    if (apiClient != null) {
      apiClient!.setAuthToken('');
    }

    // Clear user context
    userContext.clearUser();

    // Clear session ID
    _currentSessionId = null;

    // Clear stored tokens and user data
    await secureStorage.clearAll();

    // Reset state
    _refreshRetryCount = 0;

    AppLogger.i('Logout from all devices complete', tag: 'AUTH');
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

  /// Refresh access token with race condition protection
  /// Multiple calls while refresh is in progress will wait for the same refresh
  Future<void> refreshToken() async {
    // If a refresh is already in progress, wait for it
    if (_isRefreshing && _refreshCompleter != null) {
      AppLogger.d('Token refresh already in progress, waiting...', tag: 'AUTH');
      return _refreshCompleter!.future;
    }

    _isRefreshing = true;
    _refreshCompleter = Completer<void>();

    try {
      AppLogger.i('Refreshing token', tag: 'AUTH');

      final storedRefreshToken = await secureStorage.getRefreshToken();
      if (storedRefreshToken == null) {
        throw AuthException('لا يوجد refresh token', code: 'NO_REFRESH_TOKEN');
      }

      // Use real API if available, otherwise fall back to mock in development
      if (apiClient != null && !_shouldUseMockMode()) {
        await _refreshTokenWithApi(storedRefreshToken);
      } else {
        await _refreshTokenWithMock();
      }

      // Reset retry count on success
      _refreshRetryCount = 0;
      _refreshCompleter!.complete();

      // Log successful refresh to security audit
      await auditService?.logTokenRefresh(success: true);
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'AUTH', error: e);

      // Log failed refresh to security audit
      await auditService?.logTokenRefresh(
        success: false,
        errorCode: e is AuthException ? e.code : 'UNKNOWN',
        retryAttempt: _refreshRetryCount,
      );

      // In development, fallback to mock if API fails
      if (kDebugMode && e is ApiException && e.isNetworkError) {
        AppLogger.w('API unavailable, falling back to mock refresh',
            tag: 'AUTH');
        try {
          await _refreshTokenWithMock();
          _refreshRetryCount = 0;
          _refreshCompleter!.complete();
          return;
        } catch (mockError) {
          _refreshCompleter!.completeError(mockError);
          rethrow;
        } finally {
          _isRefreshing = false;
        }
      }

      // Handle retry logic for network errors with exponential backoff
      if (e is AuthException && e.code == 'NETWORK_ERROR') {
        _refreshRetryCount++;
        if (_refreshRetryCount < _maxRefreshRetries) {
          // Exponential backoff: 2s, 4s, 8s
          final backoffDelay = Duration(
            milliseconds: _tokenRefreshBaseDelay.inMilliseconds *
                pow(2, _refreshRetryCount - 1).toInt(),
          );
          AppLogger.w(
            'Token refresh network error, will retry in ${backoffDelay.inSeconds}s '
            '(attempt $_refreshRetryCount/$_maxRefreshRetries)',
            tag: 'AUTH',
          );
          _refreshCompleter!.completeError(e);
          _isRefreshing = false;

          // Schedule retry with exponential backoff
          Timer(backoffDelay, () {
            refreshToken().catchError((_) {});
          });
          rethrow;
        }
      }

      // For non-retryable errors or max retries exceeded, clear session
      _refreshCompleter!.completeError(e);
      await clearLocalSession();
      rethrow;
    } finally {
      _isRefreshing = false;
    }
  }

  /// Validate current session is still valid
  Future<bool> validateSession() async {
    try {
      // Check if we have tokens
      final accessToken = await secureStorage.getAccessToken();
      if (accessToken == null) return false;

      // Check if token is expired
      final expiry = await secureStorage.getTokenExpiry();
      if (expiry == null) return false;

      // If token is expired, try to refresh
      if (DateTime.now().isAfter(expiry)) {
        try {
          await refreshToken();
          return true;
        } catch (e) {
          return false;
        }
      }

      // Optionally validate with server (for remote session invalidation)
      if (apiClient != null && !_shouldUseMockMode()) {
        try {
          final response = await apiClient!.get('/api/v1/auth/validate');
          if (response is Map) {
            return response['valid'] == true;
          }
          return true;
        } catch (e) {
          // Network error - assume valid if token isn't expired
          if (e is ApiException && e.isNetworkError) {
            return true;
          }
          // Server says invalid
          return false;
        }
      }

      return true;
    } catch (e) {
      AppLogger.e('Session validation error', error: e, tag: 'AUTH');
      return false;
    }
  }

  /// Get token expiry time
  Future<DateTime?> getTokenExpiry() async {
    return secureStorage.getTokenExpiry();
  }

  /// Refresh token using real API
  Future<void> _refreshTokenWithApi(String refreshToken) async {
    AppLogger.i('Refreshing token via API', tag: 'AUTH');

    try {
      final response = await apiClient!.post(
        '/api/v1/auth/refresh',
        {
          'refresh_token': refreshToken,
        },
      );

      // Parse API response
      if (response == null) {
        throw AuthException('استجابة غير صالحة من الخادم');
      }

      final data =
          response is Map<String, dynamic> ? response : response['data'];

      // Extract new tokens
      final accessToken = data['access_token'] ?? data['accessToken'];
      final newRefreshToken =
          data['refresh_token'] ?? data['refreshToken'] ?? refreshToken;
      final expiresIn = data['expires_in'] ?? data['expiresIn'] ?? 3600;

      if (accessToken == null) {
        throw AuthException('بيانات التوكن مفقودة في الاستجابة');
      }

      final tokens = TokenPair(
        accessToken: accessToken as String,
        refreshToken: newRefreshToken as String,
        expiresIn:
            expiresIn is int ? expiresIn : int.parse(expiresIn.toString()),
      );

      // Update auth token in API client
      apiClient!.setAuthToken(tokens.accessToken);

      await _storeTokens(tokens);
      _scheduleTokenRefresh(tokens.expiresIn);

      AppLogger.i('API token refresh successful', tag: 'AUTH');
    } on ApiException catch (e) {
      AppLogger.e('API token refresh failed', tag: 'AUTH', error: e);

      // Convert API exceptions to auth exceptions
      if (e.statusCode == 401 || e.statusCode == 403) {
        throw AuthException('انتهت صلاحية الجلسة', code: 'SESSION_EXPIRED');
      } else if (e.isNetworkError) {
        throw AuthException('لا يوجد اتصال بالإنترنت', code: 'NETWORK_ERROR');
      } else {
        throw AuthException(e.message, code: e.code);
      }
    }
  }

  /// Refresh token using mock data (development only)
  Future<void> _refreshTokenWithMock() async {
    AppLogger.w('Using MOCK token refresh (development only)', tag: 'AUTH');

    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 300));

    // Simulated response
    final tokens = TokenPair(
      accessToken:
          'mock_new_access_token_${DateTime.now().millisecondsSinceEpoch}',
      refreshToken:
          'mock_new_refresh_token_${DateTime.now().millisecondsSinceEpoch}',
      expiresIn: 3600,
    );

    await _storeTokens(tokens);
    _scheduleTokenRefresh(tokens.expiresIn);

    AppLogger.i('Mock token refresh successful', tag: 'AUTH');
  }

  /// Get current access token
  Future<String?> getAccessToken() async {
    return secureStorage.getAccessToken();
  }

  /// Get current tenant ID
  Future<String?> getTenantId() async {
    return secureStorage.getTenantId();
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
    if (refreshIn.isNegative) {
      // Token is already near expiry, refresh immediately
      AppLogger.w('Token near expiry, refreshing immediately', tag: 'AUTH');
      refreshToken().catchError((e) {
        AppLogger.e('Immediate token refresh failed', tag: 'AUTH', error: e);
      });
      return;
    }

    _refreshTimer = Timer(refreshIn, () async {
      try {
        await refreshToken();
        AppLogger.i('Scheduled token refresh successful', tag: 'AUTH');
      } catch (e) {
        AppLogger.e('Scheduled token refresh failed', tag: 'AUTH', error: e);
        // The refreshToken method will handle retry logic
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

  /// Proactively refresh token if it's expiring soon
  /// Call this before making important API calls
  Future<void> ensureValidToken() async {
    final expiry = await secureStorage.getTokenExpiry();
    if (expiry == null) {
      throw AuthException('لا توجد جلسة نشطة', code: 'NO_SESSION');
    }

    final timeUntilExpiry = expiry.difference(DateTime.now());
    if (timeUntilExpiry < _tokenRefreshBuffer) {
      AppLogger.i('Token expiring soon, proactively refreshing', tag: 'AUTH');
      await refreshToken();
    }
  }

  /// Dispose resources
  void dispose() {
    _cancelTokenRefresh();
    _refreshCompleter = null;
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
