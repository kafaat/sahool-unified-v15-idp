import 'dart:async';
import 'dart:math';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';
import 'jwt_validator.dart';
import 'secure_storage_service.dart';
import 'token_manager.dart';

/// SAHOOL Token Interceptor
/// معترض التوكن مع Token Refresh محسن
///
/// Features:
/// - Automatic token attachment
/// - Proactive token refresh before expiration (5 min buffer)
/// - Token refresh with exponential backoff retry
/// - Mutex lock for refresh operation (prevents concurrent refreshes)
/// - Request queue during refresh
/// - Graceful logout on refresh failure
/// - Support for background refresh

/// Provider for the token interceptor
final tokenInterceptorProvider = Provider.family<TokenInterceptor, Dio>((ref, dio) {
  final tokenManager = ref.read(tokenManagerProvider);
  final secureStorage = ref.read(secureStorageProvider);
  return TokenInterceptor(
    dio: dio,
    tokenManager: tokenManager,
    secureStorage: secureStorage,
  );
});

class TokenInterceptor extends Interceptor {
  final Dio _dio;
  final TokenManager _tokenManager;
  final SecureStorageService _secureStorage;

  /// Buffer time before token expiration to trigger proactive refresh
  static const Duration _refreshBuffer = Duration(minutes: 5);

  /// Maximum retry attempts for token refresh
  static const int _maxRefreshRetries = 3;

  /// Initial delay for exponential backoff
  static const Duration _initialRetryDelay = Duration(seconds: 1);

  /// Maximum delay for exponential backoff
  static const Duration _maxRetryDelay = Duration(seconds: 30);

  /// Lock for preventing concurrent refresh operations
  bool _isRefreshing = false;

  /// Completer for coordinating refresh operations
  Completer<bool>? _refreshCompleter;

  /// Queue of pending requests waiting for refresh
  final List<_QueuedRequest> _requestQueue = [];

  TokenInterceptor({
    required Dio dio,
    required TokenManager tokenManager,
    required SecureStorageService secureStorage,
  })  : _dio = dio,
        _tokenManager = tokenManager,
        _secureStorage = secureStorage;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Skip auth for public endpoints
    if (_isPublicEndpoint(options.path)) {
      AppLogger.d('Public endpoint - no auth required: ${options.path}', tag: 'TOKEN');
      return handler.next(options);
    }

    try {
      // Check if token needs proactive refresh
      await _checkAndRefreshTokenIfNeeded();
    } catch (e) {
      // Proactive refresh failed - log but continue with existing token
      // The server will return 401 if it's expired, and onError will handle it
      AppLogger.w('Proactive token refresh failed, continuing with current token: $e', tag: 'TOKEN');
    }

    // Get current access token
    final accessToken = await _secureStorage.getAccessToken();

    if (accessToken != null && accessToken.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }

    // Add tenant ID
    final tenantId = await _secureStorage.getTenantId();
    if (tenantId != null) {
      options.headers['X-Tenant-Id'] = tenantId;
    }

    // Sanitized logging - no token values
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
    AppLogger.network(
      response.requestOptions.method,
      response.requestOptions.path,
      statusCode: response.statusCode,
      data: {'statusMessage': response.statusMessage},
    );
    handler.next(response);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    // Log error (sanitized)
    AppLogger.network(
      err.requestOptions.method,
      err.requestOptions.path,
      statusCode: err.response?.statusCode,
      data: {
        'error': err.type.toString(),
        'statusMessage': err.response?.statusMessage,
      },
    );

    // Handle 401 Unauthorized
    if (err.response?.statusCode == 401) {
      AppLogger.w('Received 401 - attempting token refresh', tag: 'TOKEN');

      // Skip refresh for public endpoints or refresh endpoint itself
      if (_isPublicEndpoint(err.requestOptions.path) ||
          err.requestOptions.path.contains('/auth/refresh')) {
        return handler.next(err);
      }

      final success = await _handleUnauthorizedError(err, handler);
      if (success) return;
    }

    handler.next(err);
  }

  /// Check if token is about to expire and refresh proactively
  /// Uses JWT exp claim as primary source, falls back to stored expiry
  Future<void> _checkAndRefreshTokenIfNeeded() async {
    final accessToken = await _secureStorage.getAccessToken();

    // Check expiry from JWT claims first (more reliable than stored timestamp)
    if (accessToken != null && accessToken.isNotEmpty) {
      final result = JwtValidator.parse(accessToken);
      if (result.isValid && result.claims != null) {
        final claims = result.claims!;
        if (claims.isExpired()) {
          AppLogger.w('Token already expired (JWT exp claim), refreshing', tag: 'TOKEN');
          await _performTokenRefresh();
          return;
        }
        if (claims.expiresWithin(_refreshBuffer)) {
          AppLogger.i(
            'Token expiring soon (${claims.timeUntilExpiry?.inMinutes} min from JWT), refreshing proactively',
            tag: 'TOKEN',
          );
          await _performTokenRefresh();
          return;
        }
        return; // Token still valid
      }
    }

    // Fallback to stored expiry
    final expiry = await _secureStorage.getTokenExpiry();
    if (expiry == null) return;

    final timeUntilExpiry = expiry.difference(DateTime.now());
    if (timeUntilExpiry <= _refreshBuffer && timeUntilExpiry.inSeconds > 0) {
      AppLogger.i(
        'Token expiring soon (${timeUntilExpiry.inMinutes} min), refreshing proactively',
        tag: 'TOKEN',
      );
      await _performTokenRefresh();
    }
  }

  /// Handle 401 error by refreshing token and retrying request
  Future<bool> _handleUnauthorizedError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final requestOptions = err.requestOptions;

    // Check if this request has already been retried
    final hasRetried = requestOptions.extra['_token_retry'] == true;
    if (hasRetried) {
      AppLogger.w('Request already retried after refresh, not retrying again', tag: 'TOKEN');
      return false;
    }

    // If already refreshing, queue this request
    if (_isRefreshing) {
      AppLogger.d('Token refresh in progress, queuing request', tag: 'TOKEN');
      return _queueRequest(requestOptions, handler);
    }

    // Attempt to refresh token
    final refreshSuccess = await _performTokenRefresh();

    if (refreshSuccess) {
      // Retry original request with new token
      return _retryRequest(requestOptions, handler);
    } else {
      // Refresh failed - logout will be handled by TokenManager
      return false;
    }
  }

  /// Perform token refresh with retry logic
  Future<bool> _performTokenRefresh() async {
    // Double-check lock (another request might have completed refresh)
    if (_isRefreshing) {
      // Wait for existing refresh to complete
      return _refreshCompleter?.future ?? Future.value(false);
    }

    _isRefreshing = true;
    _refreshCompleter = Completer<bool>();

    AppLogger.i('Starting token refresh', tag: 'TOKEN');

    bool success = false;
    int retryCount = 0;
    Duration delay = _initialRetryDelay;

    while (retryCount < _maxRefreshRetries && !success) {
      try {
        if (retryCount > 0) {
          AppLogger.d('Retry attempt $retryCount/$_maxRefreshRetries after ${delay.inSeconds}s delay', tag: 'TOKEN');
          await Future.delayed(delay);
        }

        // Perform the refresh using TokenManager
        await _tokenManager.refreshToken();
        success = true;
        AppLogger.i('Token refresh successful', tag: 'TOKEN');
      } catch (e) {
        retryCount++;
        AppLogger.w(
          'Token refresh attempt $retryCount failed: $e',
          tag: 'TOKEN',
        );

        // Calculate next delay with exponential backoff
        delay = _calculateBackoffDelay(retryCount);

        // Check if it's a permanent error (e.g., invalid refresh token)
        if (_isPermanentRefreshError(e)) {
          AppLogger.e('Permanent refresh error, stopping retries', tag: 'TOKEN');
          break;
        }
      }
    }

    _isRefreshing = false;

    // Complete the refresh completer
    _refreshCompleter?.complete(success);
    _refreshCompleter = null;

    if (success) {
      // Process queued requests
      await _processQueuedRequests();
    } else {
      // Handle refresh failure
      await _handleRefreshFailure();
      _rejectQueuedRequests();
    }

    return success;
  }

  /// Calculate exponential backoff delay with jitter
  Duration _calculateBackoffDelay(int retryCount) {
    // Exponential backoff: base * 2^retryCount
    final exponentialDelay = _initialRetryDelay.inMilliseconds * pow(2, retryCount - 1);

    // Add jitter (0-25% of delay) to prevent thundering herd
    final jitter = Random.secure().nextInt((exponentialDelay * 0.25).toInt());

    final totalDelay = Duration(milliseconds: exponentialDelay.toInt() + jitter);

    // Cap at max delay
    return totalDelay > _maxRetryDelay ? _maxRetryDelay : totalDelay;
  }

  /// Check if the error is a permanent refresh error that shouldn't be retried
  bool _isPermanentRefreshError(dynamic error) {
    // Invalid refresh token, revoked session, etc.
    if (error is DioException) {
      final statusCode = error.response?.statusCode;
      // 401, 403 - Authentication/authorization errors are permanent
      return statusCode == 401 || statusCode == 403;
    }
    return false;
  }

  /// Queue a request while refresh is in progress
  Future<bool> _queueRequest(
    RequestOptions options,
    ErrorInterceptorHandler handler,
  ) async {
    final queuedRequest = _QueuedRequest(
      options: options,
      handler: handler,
      completer: Completer<bool>(),
    );

    _requestQueue.add(queuedRequest);
    AppLogger.d('Request queued, queue size: ${_requestQueue.length}', tag: 'TOKEN');

    // Wait for refresh to complete
    final refreshSuccess = await _refreshCompleter?.future ?? false;

    // The request will be processed by _processQueuedRequests or rejected
    return queuedRequest.completer.future;
  }

  /// Process all queued requests with new token
  Future<void> _processQueuedRequests() async {
    final newToken = await _secureStorage.getAccessToken();

    if (newToken == null) {
      AppLogger.w('No new token available after refresh', tag: 'TOKEN');
      _rejectQueuedRequests();
      return;
    }

    AppLogger.d('Processing ${_requestQueue.length} queued requests', tag: 'TOKEN');

    for (final queuedRequest in _requestQueue) {
      try {
        // Update authorization header
        queuedRequest.options.headers['Authorization'] = 'Bearer $newToken';
        queuedRequest.options.extra['_token_retry'] = true;

        // Retry the request
        final response = await _dio.fetch(queuedRequest.options);
        queuedRequest.handler.resolve(response);
        queuedRequest.completer.complete(true);
      } catch (e) {
        AppLogger.e('Failed to retry queued request', tag: 'TOKEN', error: e);
        if (e is DioException) {
          queuedRequest.handler.reject(e);
        }
        queuedRequest.completer.complete(false);
      }
    }

    _requestQueue.clear();
  }

  /// Reject all queued requests
  void _rejectQueuedRequests() {
    AppLogger.w('Rejecting ${_requestQueue.length} queued requests', tag: 'TOKEN');

    for (final queuedRequest in _requestQueue) {
      queuedRequest.handler.reject(
        DioException(
          requestOptions: queuedRequest.options,
          type: DioExceptionType.unknown,
          error: 'Token refresh failed',
          message: 'Unable to refresh authentication token',
        ),
      );
      queuedRequest.completer.complete(false);
    }

    _requestQueue.clear();
  }

  /// Retry a single request with new token
  Future<bool> _retryRequest(
    RequestOptions options,
    ErrorInterceptorHandler handler,
  ) async {
    try {
      final newToken = await _secureStorage.getAccessToken();

      if (newToken == null) {
        AppLogger.w('No token available after refresh', tag: 'TOKEN');
        return false;
      }

      // Update authorization header
      options.headers['Authorization'] = 'Bearer $newToken';
      options.extra['_token_retry'] = true;

      AppLogger.d('Retrying request with new token: ${options.path}', tag: 'TOKEN');

      final response = await _dio.fetch(options);
      handler.resolve(response);
      return true;
    } catch (e) {
      AppLogger.e('Failed to retry request', tag: 'TOKEN', error: e);
      return false;
    }
  }

  /// Handle refresh failure - clear tokens and notify
  Future<void> _handleRefreshFailure() async {
    AppLogger.w('Token refresh failed, clearing auth state', tag: 'TOKEN');

    try {
      // Clear stored tokens
      await _secureStorage.deleteTokens();

      // Notify token manager about the failure
      await _tokenManager.handleRefreshFailure();

      AppLogger.i('Auth state cleared due to refresh failure', tag: 'TOKEN');
    } catch (e) {
      AppLogger.e('Error clearing auth state', tag: 'TOKEN', error: e);
    }
  }

  /// Check if endpoint is public (doesn't require auth)
  bool _isPublicEndpoint(String path) {
    const publicPaths = [
      '/auth/login',
      '/auth/register',
      '/auth/forgot-password',
      '/auth/reset-password',
      '/auth/verify-otp',
      '/auth/send-otp',
      '/health',
      '/healthz',
      '/readyz',
      '/version',
      '/api-docs',
      '/swagger',
    ];

    return publicPaths.any((p) => path.contains(p));
  }

  /// Get the number of pending requests in queue
  int get pendingRequestCount => _requestQueue.length;

  /// Check if a refresh is currently in progress
  bool get isRefreshing => _isRefreshing;
}

/// Internal class to track queued requests
class _QueuedRequest {
  final RequestOptions options;
  final ErrorInterceptorHandler handler;
  final Completer<bool> completer;

  _QueuedRequest({
    required this.options,
    required this.handler,
    required this.completer,
  });
}
