import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../auth/auth_service.dart';
import '../auth/secure_storage_service.dart';
import '../utils/app_logger.dart';

/// SAHOOL Auth Interceptor
/// معترض المصادقة مع Token Refresh تلقائي
///
/// Features:
/// - Automatic token attachment to requests
/// - Automatic token refresh on 401 (Unauthorized)
/// - Request queue during refresh to prevent race conditions
/// - Retry failed requests after successful token refresh
/// - Logout on refresh failure
/// - Support for multiple simultaneous 401 responses

class AuthInterceptor extends Interceptor {
  final Ref _ref;
  final Dio _dio;

  bool _isRefreshing = false;
  final List<_RequestRetry> _pendingRequests = [];
  DateTime? _lastRefreshAttempt;
  static const _minRefreshInterval = Duration(seconds: 5);

  AuthInterceptor(this._ref, this._dio);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Skip auth for public endpoints
    if (_isPublicEndpoint(options.path)) {
      return handler.next(options);
    }

    // Get access token
    final secureStorage = _ref.read(secureStorageProvider);
    final accessToken = await secureStorage.getAccessToken();

    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }

    // Add tenant ID
    final tenantId = await secureStorage.getTenantId();
    if (tenantId != null) {
      options.headers['X-Tenant-Id'] = tenantId;
    }

    AppLogger.network(
      options.method,
      options.path,
      data: {'hasToken': accessToken != null},
    );

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Handle 401 Unauthorized
    if (err.response?.statusCode == 401) {
      AppLogger.w('Received 401 - attempting token refresh', tag: 'AUTH');

      // Prevent too frequent refresh attempts
      if (_shouldSkipRefresh()) {
        AppLogger.w('Skipping refresh - too soon after last attempt', tag: 'AUTH');
        await _handleRefreshFailure();
        handler.next(err);
        return;
      }

      final success = await _handleTokenRefresh(err, handler);
      if (success) return;
    }

    // Handle other errors
    _logError(err);
    handler.next(err);
  }

  /// Check if we should skip refresh attempt
  bool _shouldSkipRefresh() {
    if (_lastRefreshAttempt == null) return false;

    final timeSinceLastRefresh = DateTime.now().difference(_lastRefreshAttempt!);
    return timeSinceLastRefresh < _minRefreshInterval;
  }

  /// Log error details
  void _logError(DioException err) {
    final statusCode = err.response?.statusCode;
    final path = err.requestOptions.path;

    if (statusCode != null) {
      AppLogger.e('HTTP $statusCode error on $path', tag: 'HTTP', error: err);
    } else {
      AppLogger.e('Network error on $path', tag: 'HTTP', error: err);
    }
  }

  /// Handle token refresh
  Future<bool> _handleTokenRefresh(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final requestOptions = err.requestOptions;

    // If already refreshing, queue this request
    if (_isRefreshing) {
      AppLogger.d('Token refresh in progress, queuing request', tag: 'AUTH');

      try {
        final response = await _queueRequest(requestOptions);
        handler.resolve(response);
        return true;
      } catch (e) {
        handler.reject(err);
        return true;
      }
    }

    _isRefreshing = true;
    _lastRefreshAttempt = DateTime.now();

    try {
      // Attempt to refresh token
      final authService = _ref.read(authServiceProvider);
      await authService.refreshToken();

      AppLogger.i('Token refreshed successfully', tag: 'AUTH');

      // Get new token
      final secureStorage = _ref.read(secureStorageProvider);
      final newToken = await secureStorage.getAccessToken();

      if (newToken == null) {
        throw Exception('Failed to get new access token');
      }

      // Retry original request with new token
      requestOptions.headers['Authorization'] = 'Bearer $newToken';

      final response = await _dio.fetch(requestOptions);
      handler.resolve(response);

      // Process queued requests
      await _processQueuedRequests(newToken);

      return true;
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'AUTH', error: e);

      // Clear auth state and logout
      await _handleRefreshFailure();

      // Reject all queued requests
      _rejectQueuedRequests(err);

      return false;
    } finally {
      _isRefreshing = false;
    }
  }

  /// Queue a request while refresh is in progress
  Future<Response<dynamic>> _queueRequest(RequestOptions options) {
    final completer = _RequestRetry(options);
    _pendingRequests.add(completer);
    return completer.future;
  }

  /// Process all queued requests with new token
  Future<void> _processQueuedRequests(String newToken) async {
    AppLogger.d(
      'Processing ${_pendingRequests.length} queued requests',
      tag: 'AUTH',
    );

    for (final retry in _pendingRequests) {
      retry.options.headers['Authorization'] = 'Bearer $newToken';

      try {
        final response = await _dio.fetch(retry.options);
        retry.complete(response);
      } catch (e) {
        retry.completeError(e);
      }
    }

    _pendingRequests.clear();
  }

  /// Reject all queued requests
  void _rejectQueuedRequests(DioException error) {
    for (final retry in _pendingRequests) {
      retry.completeError(error);
    }
    _pendingRequests.clear();
  }

  /// Handle refresh failure - logout user
  Future<void> _handleRefreshFailure() async {
    try {
      // Clear stored tokens
      final secureStorage = _ref.read(secureStorageProvider);
      await secureStorage.clearAll();

      // Update auth state
      // This would typically trigger a navigation to login screen
      AppLogger.w('User logged out due to token refresh failure', tag: 'AUTH');
    } catch (e) {
      AppLogger.e('Error during logout', tag: 'AUTH', error: e);
    }
  }

  /// Check if endpoint is public (doesn't require auth)
  bool _isPublicEndpoint(String path) {
    const publicPaths = [
      '/auth/login',
      '/auth/register',
      '/auth/forgot-password',
      '/auth/refresh',
      '/health',
      '/version',
    ];

    return publicPaths.any((p) => path.contains(p));
  }
}

/// Request retry holder
class _RequestRetry {
  final RequestOptions options;
  final _completer = Completer<Response<dynamic>>();

  _RequestRetry(this.options);

  Future<Response<dynamic>> get future => _completer.future;

  void complete(Response<dynamic> response) {
    if (!_completer.isCompleted) {
      _completer.complete(response);
    }
  }

  void completeError(Object error) {
    if (!_completer.isCompleted) {
      _completer.completeError(error);
    }
  }
}
