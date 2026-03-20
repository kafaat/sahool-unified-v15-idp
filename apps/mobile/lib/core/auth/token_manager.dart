import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../http/api_client.dart';
import '../utils/app_logger.dart';
import 'secure_storage_service.dart';

/// SAHOOL Token Manager
/// مدير التوكن المركزي
///
/// Centralized token management with:
/// - Token refresh with rotation support
/// - Background refresh scheduling
/// - Refresh failure handling with logout
/// - Event notifications for auth state changes
/// - Thread-safe refresh operations

/// Provider for TokenManager
final tokenManagerProvider = Provider<TokenManager>((ref) {
  final secureStorage = ref.read(secureStorageProvider);
  return TokenManager(
    secureStorage: secureStorage,
    onAuthStateChanged: (isAuthenticated) {
      // This callback is called when auth state changes
      // It can be used to navigate to login screen or show messages
      AppLogger.i(
        'Auth state changed: ${isAuthenticated ? "authenticated" : "unauthenticated"}',
        tag: 'TOKEN_MANAGER',
      );
    },
  );
});

/// Token rotation metadata for tracking token family and revocation.
/// Aligns with backend Prisma RefreshToken model fields.
class TokenRotationInfo {
  /// JWT ID for revocation tracking
  final String? jti;
  /// Token family identifier for rotation chain
  final String? family;
  /// Whether this token has been revoked
  final bool revoked;
  /// Whether this token has been used (for rotation detection)
  final bool used;
  /// JTI of the replacement token (if rotated)
  final String? replacedBy;

  const TokenRotationInfo({
    this.jti,
    this.family,
    this.revoked = false,
    this.used = false,
    this.replacedBy,
  });

  factory TokenRotationInfo.fromJson(Map<String, dynamic> json) {
    return TokenRotationInfo(
      jti: json['jti'] as String?,
      family: json['family'] as String?,
      revoked: json['revoked'] as bool? ?? false,
      used: json['used'] as bool? ?? false,
      replacedBy: json['replacedBy'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'jti': jti,
        'family': family,
        'revoked': revoked,
        'used': used,
        'replacedBy': replacedBy,
      };
}

/// Account lockout info aligned with backend User model fields.
class AccountLockoutInfo {
  final int failedLoginAttempts;
  final DateTime? lockoutUntil;
  final DateTime? lastFailedLoginAt;

  const AccountLockoutInfo({
    this.failedLoginAttempts = 0,
    this.lockoutUntil,
    this.lastFailedLoginAt,
  });

  bool get isLockedOut =>
      lockoutUntil != null && lockoutUntil!.isAfter(DateTime.now());

  factory AccountLockoutInfo.fromJson(Map<String, dynamic> json) {
    return AccountLockoutInfo(
      failedLoginAttempts: json['failedLoginAttempts'] as int? ?? 0,
      lockoutUntil: json['lockoutUntil'] != null
          ? DateTime.tryParse(json['lockoutUntil'] as String)
          : null,
      lastFailedLoginAt: json['lastFailedLoginAt'] != null
          ? DateTime.tryParse(json['lastFailedLoginAt'] as String)
          : null,
    );
  }
}

/// Token refresh result
class TokenRefreshResult {
  final bool success;
  final String? accessToken;
  final String? refreshToken;
  final int? expiresIn;
  final String? error;
  /// Token rotation metadata from server response
  final TokenRotationInfo? rotationInfo;

  const TokenRefreshResult({
    required this.success,
    this.accessToken,
    this.refreshToken,
    this.expiresIn,
    this.error,
    this.rotationInfo,
  });

  factory TokenRefreshResult.success({
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
  }) {
    return TokenRefreshResult(
      success: true,
      accessToken: accessToken,
      refreshToken: refreshToken,
      expiresIn: expiresIn,
    );
  }

  factory TokenRefreshResult.failure(String error) {
    return TokenRefreshResult(
      success: false,
      error: error,
    );
  }
}

/// Auth state change callback type
typedef AuthStateCallback = void Function(bool isAuthenticated);

/// Token refresh callback type for custom refresh implementations
typedef TokenRefreshCallback = Future<TokenRefreshResult> Function(String refreshToken);

class TokenManager {
  final SecureStorageService _secureStorage;
  final AuthStateCallback? onAuthStateChanged;

  /// Custom refresh callback (e.g., for API calls)
  TokenRefreshCallback? _refreshCallback;

  /// API client for making refresh requests
  ApiClient? _apiClient;

  /// Timer for background refresh
  Timer? _backgroundRefreshTimer;

  /// Buffer time before expiry to trigger background refresh
  static const Duration _backgroundRefreshBuffer = Duration(minutes: 5);

  /// Minimum time between background refresh attempts
  static const Duration _minRefreshInterval = Duration(minutes: 1);

  /// Stream controller for auth state changes
  final _authStateController = StreamController<bool>.broadcast();

  /// Last successful refresh time
  DateTime? _lastRefreshTime;

  /// Flag to prevent multiple simultaneous background refreshes
  bool _isBackgroundRefreshing = false;

  /// Completer-based lock for refresh operation to prevent concurrent refreshes
  Completer<void>? _refreshLock;

  TokenManager({
    required SecureStorageService secureStorage,
    this.onAuthStateChanged,
  }) : _secureStorage = secureStorage {
    // Schedule initial background refresh check
    _scheduleBackgroundRefreshCheck();
  }

  /// Stream of auth state changes
  Stream<bool> get authStateStream => _authStateController.stream;

  /// Set the API client for making refresh requests
  void setApiClient(ApiClient apiClient) {
    _apiClient = apiClient;
  }

  /// Set a custom refresh callback
  void setRefreshCallback(TokenRefreshCallback callback) {
    _refreshCallback = callback;
  }

  /// Refresh the access token (re-entrant safe via Completer lock)
  Future<void> refreshToken() async {
    // If a refresh is already in progress, wait for it to complete
    if (_refreshLock != null) {
      AppLogger.d('Refresh already in progress, waiting', tag: 'TOKEN_MANAGER');
      return _refreshLock!.future;
    }

    _refreshLock = Completer<void>();
    AppLogger.i('Refreshing token', tag: 'TOKEN_MANAGER');

    try {
      await _doRefreshToken();
      _refreshLock?.complete();
    } catch (e) {
      _refreshLock?.completeError(e);
      rethrow;
    } finally {
      _refreshLock = null;
    }
  }

  /// Internal refresh implementation
  Future<void> _doRefreshToken() async {
    final refreshToken = await _secureStorage.getRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      throw TokenRefreshException(
        'لا يوجد refresh token',
        code: 'NO_REFRESH_TOKEN',
      );
    }

    try {
      TokenRefreshResult result;

      // Use custom callback if available, otherwise use API client
      if (_refreshCallback != null) {
        result = await _refreshCallback!(refreshToken);
      } else if (_apiClient != null) {
        result = await _refreshWithApiClient(refreshToken);
      } else {
        // Fallback to mock refresh in debug mode
        if (kDebugMode) {
          AppLogger.w('Using mock token refresh (no API client)', tag: 'TOKEN_MANAGER');
          result = await _mockRefresh();
        } else {
          throw TokenRefreshException(
            'No refresh mechanism configured',
            code: 'NO_REFRESH_MECHANISM',
          );
        }
      }

      if (result.success) {
        await _storeRefreshedTokens(result);
        _lastRefreshTime = DateTime.now();
        _scheduleBackgroundRefresh(result.expiresIn ?? 3600);
        AppLogger.i('Token refresh successful', tag: 'TOKEN_MANAGER');
      } else {
        throw TokenRefreshException(
          result.error ?? 'Token refresh failed',
          code: 'REFRESH_FAILED',
        );
      }
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'TOKEN_MANAGER', error: e);
      rethrow;
    }
  }

  /// Refresh token using API client
  Future<TokenRefreshResult> _refreshWithApiClient(String refreshToken) async {
    try {
      final response = await _apiClient!.post(
        '/api/v1/auth/refresh',
        {'refresh_token': refreshToken},
      );

      if (response == null) {
        return TokenRefreshResult.failure('Invalid response from server');
      }

      final data = response is Map<String, dynamic> ? response : response['data'];

      final accessToken = data['access_token'] ?? data['accessToken'];
      final newRefreshToken = data['refresh_token'] ?? data['refreshToken'] ?? refreshToken;
      final expiresIn = data['expires_in'] ?? data['expiresIn'] ?? 3600;

      if (accessToken == null) {
        return TokenRefreshResult.failure('Missing access token in response');
      }

      // Update API client with new token
      _apiClient!.setAuthToken(accessToken as String);

      return TokenRefreshResult.success(
        accessToken: accessToken,
        refreshToken: newRefreshToken as String,
        expiresIn: expiresIn is int ? expiresIn : int.parse(expiresIn.toString()),
      );
    } on ApiException catch (e) {
      if (e.statusCode == 401 || e.statusCode == 403) {
        return TokenRefreshResult.failure('Session expired');
      } else if (e.isNetworkError) {
        return TokenRefreshResult.failure('Network error');
      }
      return TokenRefreshResult.failure(e.message);
    }
  }

  /// Mock refresh for development
  Future<TokenRefreshResult> _mockRefresh() async {
    await Future.delayed(const Duration(milliseconds: 300));
    return TokenRefreshResult.success(
      accessToken: 'mock_access_token_${DateTime.now().millisecondsSinceEpoch}',
      refreshToken: 'mock_refresh_token_${DateTime.now().millisecondsSinceEpoch}',
      expiresIn: 3600,
    );
  }

  /// Store refreshed tokens securely
  Future<void> _storeRefreshedTokens(TokenRefreshResult result) async {
    if (result.accessToken != null) {
      await _secureStorage.setAccessToken(result.accessToken!);
    }

    // Refresh token rotation: store new refresh token
    if (result.refreshToken != null) {
      await _secureStorage.setRefreshToken(result.refreshToken!);
    }

    // Set token expiry
    if (result.expiresIn != null) {
      final expiry = DateTime.now().add(Duration(seconds: result.expiresIn!));
      await _secureStorage.setTokenExpiry(expiry);
    }
  }

  /// Schedule background refresh check
  void _scheduleBackgroundRefreshCheck() {
    // Check every minute if a background refresh is needed
    _backgroundRefreshTimer?.cancel();
    _backgroundRefreshTimer = Timer.periodic(
      _minRefreshInterval,
      (_) => _checkAndPerformBackgroundRefresh(),
    );
  }

  /// Schedule background refresh based on token expiry
  void _scheduleBackgroundRefresh(int expiresInSeconds) {
    _backgroundRefreshTimer?.cancel();

    // Calculate when to refresh (before expiry with buffer)
    final refreshIn = Duration(seconds: expiresInSeconds) - _backgroundRefreshBuffer;

    if (refreshIn.isNegative) {
      // Token already near expiry, refresh immediately
      _checkAndPerformBackgroundRefresh();
      return;
    }

    AppLogger.d(
      'Background refresh scheduled in ${refreshIn.inMinutes} minutes',
      tag: 'TOKEN_MANAGER',
    );

    _backgroundRefreshTimer = Timer(refreshIn, () {
      _checkAndPerformBackgroundRefresh();
    });
  }

  /// Check and perform background refresh if needed
  Future<void> _checkAndPerformBackgroundRefresh() async {
    if (_isBackgroundRefreshing) return;

    // Check if we've refreshed recently
    if (_lastRefreshTime != null) {
      final timeSinceRefresh = DateTime.now().difference(_lastRefreshTime!);
      if (timeSinceRefresh < _minRefreshInterval) {
        return;
      }
    }

    // Check token expiry
    final expiry = await _secureStorage.getTokenExpiry();
    if (expiry == null) return;

    final timeUntilExpiry = expiry.difference(DateTime.now());
    if (timeUntilExpiry > _backgroundRefreshBuffer) {
      // Token still has time, schedule next check
      return;
    }

    _isBackgroundRefreshing = true;

    try {
      AppLogger.i('Performing background token refresh', tag: 'TOKEN_MANAGER');
      await refreshToken();
    } catch (e) {
      AppLogger.w('Background token refresh failed', tag: 'TOKEN_MANAGER');
      // Don't call handleRefreshFailure for background refresh
      // Let the next API call trigger proper error handling
    } finally {
      _isBackgroundRefreshing = false;
    }
  }

  /// Handle refresh failure - clear tokens and notify
  Future<void> handleRefreshFailure() async {
    AppLogger.w('Handling refresh failure', tag: 'TOKEN_MANAGER');

    // Cancel background refresh
    _backgroundRefreshTimer?.cancel();
    _backgroundRefreshTimer = null;

    // Clear tokens
    await _secureStorage.deleteTokens();

    // Clear API client token
    if (_apiClient != null) {
      _apiClient!.setAuthToken('');
    }

    // Notify listeners
    _authStateController.add(false);
    onAuthStateChanged?.call(false);
  }

  /// Check if user is currently authenticated
  Future<bool> isAuthenticated() async {
    final accessToken = await _secureStorage.getAccessToken();
    if (accessToken == null || accessToken.isEmpty) return false;

    final expiry = await _secureStorage.getTokenExpiry();
    if (expiry == null) return false;

    // Check if token is still valid
    return DateTime.now().isBefore(expiry);
  }

  /// Get time until token expires
  Future<Duration?> getTimeUntilExpiry() async {
    final expiry = await _secureStorage.getTokenExpiry();
    if (expiry == null) return null;

    final timeUntil = expiry.difference(DateTime.now());
    return timeUntil.isNegative ? Duration.zero : timeUntil;
  }

  /// Logout and clear all tokens
  Future<void> logout() async {
    AppLogger.i('Logging out', tag: 'TOKEN_MANAGER');

    // Cancel background refresh
    _backgroundRefreshTimer?.cancel();
    _backgroundRefreshTimer = null;

    // Clear all stored data
    await _secureStorage.clearAll();

    // Clear API client token
    if (_apiClient != null) {
      _apiClient!.setAuthToken('');
    }

    // Notify listeners
    _authStateController.add(false);
    onAuthStateChanged?.call(false);
  }

  /// Store new tokens after login
  Future<void> storeTokens({
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
  }) async {
    await _secureStorage.setAccessToken(accessToken);
    await _secureStorage.setRefreshToken(refreshToken);

    final expiry = DateTime.now().add(Duration(seconds: expiresIn));
    await _secureStorage.setTokenExpiry(expiry);

    // Update API client
    if (_apiClient != null) {
      _apiClient!.setAuthToken(accessToken);
    }

    // Schedule background refresh
    _scheduleBackgroundRefresh(expiresIn);

    // Notify listeners
    _authStateController.add(true);
    onAuthStateChanged?.call(true);

    AppLogger.i('Tokens stored successfully', tag: 'TOKEN_MANAGER');
  }

  /// Dispose resources
  void dispose() {
    _backgroundRefreshTimer?.cancel();
    _backgroundRefreshTimer = null;
    _authStateController.close();
  }
}

/// Exception thrown during token refresh
class TokenRefreshException implements Exception {
  final String message;
  final String? code;

  TokenRefreshException(this.message, {this.code});

  @override
  String toString() => 'TokenRefreshException($code): $message';
}
