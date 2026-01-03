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
/// - Automatic token attachment
/// - Token refresh on 401
/// - Request queue during refresh
/// - Logout on refresh failure

class AuthInterceptor extends Interceptor {
  final Ref _ref;
  final Dio _dio;

  bool _isRefreshing = false;
  final List<_RequestRetry> _pendingRequests = [];

  AuthInterceptor(this._ref, this._dio);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Skip auth for public endpoints
    if (_isPublicEndpoint(options.path)) {
      AppLogger.d('Public endpoint - no auth required', tag: 'AUTH');
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

    // Sanitized network logging - NO token information
    AppLogger.network(
      options.method,
      options.path,
      data: {
        'authenticated': accessToken != null,
        'hasTenant': tenantId != null,
      },
    );

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // Log successful responses with sanitization
    AppLogger.network(
      response.requestOptions.method,
      response.requestOptions.path,
      statusCode: response.statusCode,
      data: {
        'statusMessage': response.statusMessage,
        // Response data is automatically sanitized by AppLogger
      },
    );

    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Log error with sanitization - NO sensitive data
    AppLogger.network(
      err.requestOptions.method,
      err.requestOptions.path,
      statusCode: err.response?.statusCode,
      data: {
        'error': err.type.toString(),
        'statusMessage': err.response?.statusMessage,
        // Error details are automatically sanitized by AppLogger
      },
    );

    // Handle 401 Unauthorized
    if (err.response?.statusCode == 401) {
      AppLogger.w('Received 401 - attempting token refresh', tag: 'AUTH');

      final success = await _handleTokenRefresh(err, handler);
      if (success) return;
    }

    handler.next(err);
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

    try {
      // Attempt to refresh token
      final authService = _ref.read(authServiceProvider);
      await authService.refreshToken();

      AppLogger.i('Token refreshed successfully', tag: 'AUTH');

      // Get new token
      final secureStorage = _ref.read(secureStorageProvider);
      final newToken = await secureStorage.getAccessToken();

      if (newToken == null) {
        throw Exception('Token refresh succeeded but no token available');
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
