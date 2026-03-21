import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/env_config.dart';
import '../security/security_config.dart';
import '../security/certificate_pinning_service.dart';
import '../security/certificate_config.dart';
import '../security/signing_key_service.dart';
import '../utils/app_logger.dart';
import '../auth/token_manager.dart';
import '../auth/secure_storage_service.dart';
import '../network/network.dart';
import 'rate_limiter.dart';
import 'request_signing_interceptor.dart';
import 'security_headers_interceptor.dart';
import 'retry_interceptor.dart';

/// SAHOOL API Client with offline handling and certificate pinning
class ApiClient {
  late final Dio _dio;
  String? _authToken;
  String _tenantId = EnvConfig.defaultTenantId;
  CertificatePinningService? _certificatePinningService;
  late final RateLimiter _rateLimiter;

  /// Robust retry interceptor with circuit breaker support
  late final RobustRetryInterceptor _robustRetryInterceptor;

  /// Token interceptor for advanced token management
  _TokenInterceptorWrapper? _tokenInterceptorWrapper;

  ApiClient({
    String? baseUrl,
    SecurityConfig? securityConfig,
    CertificatePinningService? certificatePinningService,
    RateLimiter? rateLimiter,
    SigningKeyService? signingKeyService,
    bool enableRequestSigning = true,
    SecurityHeaderConfig? securityHeaderConfig,
    bool enableSecurityHeaderValidation = true,
    RobustRetryInterceptor? robustRetryInterceptor,
    bool enableRobustRetry = true,
    RetryPolicy? defaultRetryPolicy,
    OnRetryCallback? onRetry,
    bool enableOfflineQueue = true,
  }) {
    // Use security config based on environment or build mode
    final config = securityConfig ?? SecurityConfig.fromBuildMode();

    // Initialize rate limiter
    _rateLimiter = rateLimiter ?? RateLimiter();

    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? EnvConfig.apiBaseUrl,
      connectTimeout: EnvConfig.connectTimeout,
      receiveTimeout: config.requestTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Configure certificate pinning if enabled
    if (config.enableCertificatePinning) {
      // Determine environment for pin configuration
      final environment = EnvConfig.isProduction ? 'production'
          : EnvConfig.isStaging ? 'staging'
          : 'development';

      final pins = CertificateConfig.getPinsForEnvironment(environment);

      _certificatePinningService = certificatePinningService ??
          CertificatePinningService(
            certificatePins: pins,
            allowDebugBypass: config.allowPinningDebugBypass,
            enforceStrict: config.strictCertificatePinning,
          );
      _certificatePinningService!.configureDio(_dio);

      if (kDebugMode) {
        AppLogger.i('SSL Certificate Pinning enabled', tag: 'ApiClient', data: {
          'environment': environment,
          'strictMode': config.strictCertificatePinning,
          'debugBypass': config.allowPinningDebugBypass,
          'domains': _certificatePinningService!.getConfiguredDomains(),
        });
      }
    } else if (kDebugMode) {
      AppLogger.w('Certificate pinning is disabled', tag: 'ApiClient');
    }

    // Add interceptors
    // Rate limiter must be first to control request flow
    _dio.interceptors.add(RateLimitInterceptor(
      rateLimiter: _rateLimiter,
      queueExceededRequests: true,
      dio: _dio,
    ));

    // Initialize and add robust retry interceptor with circuit breaker
    if (enableRobustRetry) {
      _robustRetryInterceptor = robustRetryInterceptor ?? RobustRetryInterceptor(
        defaultPolicy: defaultRetryPolicy ?? RetryPolicies.standard,
        onRetry: onRetry,
        enableOfflineQueue: enableOfflineQueue,
        onCircuitStateChange: (endpoint, state) {
          if (kDebugMode) {
            AppLogger.i(
              'Circuit breaker state changed',
              tag: 'ApiClient',
              data: {'endpoint': endpoint, 'state': state.name},
            );
          }
        },
      );
      _dio.interceptors.add(_robustRetryInterceptor);
    } else {
      // Fallback to basic retry interceptor
      _robustRetryInterceptor = RobustRetryInterceptor(
        defaultPolicy: RetryPolicies.none,
        enableOfflineQueue: false,
      );
      _dio.interceptors.add(RetryInterceptor(
        dio: _dio,
        maxRetries: 3,
        initialDelay: const Duration(seconds: 1),
      ));
    }

    _dio.interceptors.add(_AuthInterceptor(this));

    // Add request signing interceptor after auth
    // This ensures requests are signed after authentication headers are added
    if (enableRequestSigning && signingKeyService != null) {
      _dio.interceptors.add(RequestSigningInterceptor(signingKeyService));
      if (kDebugMode) {
        AppLogger.i('Request signing enabled', tag: 'ApiClient');
      }
    } else if (kDebugMode && !enableRequestSigning) {
      AppLogger.w('Request signing is disabled', tag: 'ApiClient');
    } else if (kDebugMode && signingKeyService == null) {
      AppLogger.w('Request signing disabled: no signing key service provided', tag: 'ApiClient');
    }

    // Add security header validation interceptor
    // Validates response headers for security best practices
    if (enableSecurityHeaderValidation) {
      final headerConfig = securityHeaderConfig ?? SecurityHeaderConfig.fromEnvironment();
      _dio.interceptors.add(SecurityHeadersInterceptor(config: headerConfig));

      if (kDebugMode) {
        AppLogger.i('Security header validation enabled', tag: 'ApiClient', data: {
          'mode': headerConfig.mode.name,
          'requiredHeaders': headerConfig.requiredHeaders.toList(),
          'validateContentLength': headerConfig.validateContentLength,
          'validateApiVersion': headerConfig.validateApiVersion,
          'validateJsonStructure': headerConfig.validateJsonStructure,
        });
      }
    } else if (kDebugMode) {
      AppLogger.w('Security header validation is disabled', tag: 'ApiClient');
    }

    _dio.interceptors.add(_LoggingInterceptor());
  }

  void setAuthToken(String token) {
    _authToken = token;
  }

  void setTenantId(String tenantId) {
    _tenantId = tenantId;
  }

  String? get authToken => _authToken;
  String get tenantId => _tenantId;
  CertificatePinningService? get certificatePinningService => _certificatePinningService;
  RateLimiter get rateLimiter => _rateLimiter;
  RobustRetryInterceptor get retryInterceptor => _robustRetryInterceptor;

  // ─────────────────────────────────────────────────────────────────────────────
  // Network Quality & Circuit Breaker Methods
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get current network quality (good, slow, offline)
  NetworkQuality get networkQuality => _robustRetryInterceptor.getNetworkQuality();

  /// Check if network is offline
  bool get isOffline => networkQuality == NetworkQuality.offline;

  /// Get circuit breaker status for a specific endpoint
  CircuitBreakerStatus? getCircuitBreakerStatus(String endpoint) {
    return _robustRetryInterceptor.getCircuitBreakerStatus(endpoint);
  }

  /// Get health summary for all circuit breakers
  CircuitBreakerHealthSummary get circuitBreakerHealth {
    return _robustRetryInterceptor.getCircuitBreakerHealth();
  }

  /// Get retry interceptor statistics
  RetryInterceptorStats get retryStats => _robustRetryInterceptor.getStats();

  /// Get number of requests queued for offline retry
  int get queuedRequestCount => _robustRetryInterceptor.queuedRequestCount;

  /// Process offline queue manually
  Future<void> processOfflineQueue() => _robustRetryInterceptor.processQueue();

  /// Reset all circuit breakers
  void resetCircuitBreakers() => _robustRetryInterceptor.resetCircuitBreakers();

  /// Reset retry statistics
  void resetRetryStats() => _robustRetryInterceptor.resetStats();

  /// Get the underlying Dio instance (for advanced configuration)
  Dio get dio => _dio;

  /// Configure advanced token management with TokenManager
  /// This adds proactive refresh, retry logic, and request queueing
  void configureTokenInterceptor({
    required TokenManager tokenManager,
    required SecureStorageService secureStorage,
  }) {
    // Remove existing basic auth interceptor
    _dio.interceptors.removeWhere((i) => i is _AuthInterceptor);

    // Add advanced token interceptor wrapper
    _tokenInterceptorWrapper = _TokenInterceptorWrapper(
      dio: _dio,
      tokenManager: tokenManager,
      secureStorage: secureStorage,
    );
    _dio.interceptors.insert(0, _tokenInterceptorWrapper!);

    // Update token manager with API client
    tokenManager.setApiClient(this);

    if (kDebugMode) {
      AppLogger.i('Advanced token interceptor configured', tag: 'ApiClient');
    }
  }

  /// Check if advanced token interceptor is configured
  bool get hasTokenInterceptor => _tokenInterceptorWrapper != null;

  /// Get pending request count (if token interceptor is configured)
  int get pendingRequestCount => _tokenInterceptorWrapper?.pendingRequestCount ?? 0;

  /// Check if token refresh is in progress
  bool get isRefreshing => _tokenInterceptorWrapper?.isRefreshing ?? false;

  /// Check if certificate pinning is enabled
  bool get isCertificatePinningEnabled => _certificatePinningService != null;

  /// Check for expiring certificate pins
  List<ExpiringPin> getExpiringPins({int daysThreshold = 30}) {
    if (_certificatePinningService == null) return [];
    return _certificatePinningService!.getExpiringPins(daysThreshold: daysThreshold);
  }

  /// Update certificate pins for a domain
  void updateCertificatePins(String domain, List<CertificatePin> pins) {
    _certificatePinningService?.addPins(domain, pins);
  }

  /// Get rate limit status for an endpoint type
  RateLimitStatus getRateLimitStatus(String endpointType) {
    return _rateLimiter.getStatus(endpointType);
  }

  /// Get rate limit configuration for an endpoint type
  EndpointConfig getRateLimitConfig(String endpointType) {
    return _rateLimiter.getConfig(endpointType);
  }

  /// Reset rate limiters (useful for testing or manual reset)
  void resetRateLimits() {
    _rateLimiter.reset();
    if (kDebugMode) {
      AppLogger.d('Rate limiters reset', tag: 'ApiClient');
    }
  }

  /// GET request
  Future<dynamic> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// POST request
  Future<dynamic> post(
    String path,
    dynamic data, {
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: headers != null ? Options(headers: headers) : null,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// PUT request
  Future<dynamic> put(
    String path,
    dynamic data, {
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: headers != null ? Options(headers: headers) : null,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// DELETE request
  Future<dynamic> delete(
    String path, {
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        queryParameters: queryParameters,
        options: headers != null ? Options(headers: headers) : null,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Upload file
  Future<dynamic> uploadFile(
    String path,
    String filePath, {
    String fieldName = 'file',
    Map<String, dynamic>? extraData,
  }) async {
    try {
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(filePath),
        ...?extraData,
      });

      final response = await _dio.post(path, data: formData);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  ApiException _handleError(DioException e) {
    // Check for security header validation errors
    if (e.error is SecurityHeaderException) {
      final securityError = e.error as SecurityHeaderException;
      return ApiException(
        code: securityError.code,
        message: 'فشل التحقق من رؤوس الأمان',
        statusCode: e.response?.statusCode,
        isSecurityError: true,
      );
    }

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          code: 'TIMEOUT',
          message: 'انتهت مهلة الاتصال',
          isNetworkError: true,
        );

      case DioExceptionType.connectionError:
        return ApiException(
          code: 'NO_CONNECTION',
          message: 'لا يوجد اتصال بالإنترنت',
          isNetworkError: true,
        );

      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode ?? 0;
        final data = e.response?.data;
        String message = 'حدث خطأ غير متوقع';

        if (data is Map) {
          message = (data['message'] ?? data['error'] ?? message) as String;
        }

        return ApiException(
          code: 'HTTP_$statusCode',
          message: message,
          statusCode: statusCode,
        );

      default:
        return ApiException(
          code: 'UNKNOWN',
          message: 'حدث خطأ غير متوقع',
        );
    }
  }
}

/// Auth Interceptor
class _AuthInterceptor extends Interceptor {
  final ApiClient _client;

  _AuthInterceptor(this._client);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Add auth token
    if (_client.authToken != null) {
      options.headers['Authorization'] = 'Bearer ${_client.authToken}';
    }

    // Add tenant ID
    options.headers['X-Tenant-Id'] = _client.tenantId;

    handler.next(options);
  }
}

/// Logging Interceptor
/// Only logs in debug mode to prevent sensitive data exposure in production
class _LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (kDebugMode) {
      AppLogger.d('${options.method} ${options.path}', tag: 'HTTP');
      // Note: Authorization headers and request body are intentionally not logged
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (kDebugMode) {
      AppLogger.d('${response.statusCode} ${response.requestOptions.path}', tag: 'HTTP');
      // Note: Response body is intentionally not logged to prevent data leakage
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      AppLogger.e('${err.type} ${err.requestOptions.path}', tag: 'HTTP', error: err);
    }
    handler.next(err);
  }
}

/// API Exception
class ApiException implements Exception {
  final String code;
  final String message;
  final int? statusCode;
  final bool isNetworkError;
  final bool isSecurityError;

  ApiException({
    required this.code,
    required this.message,
    this.statusCode,
    this.isNetworkError = false,
    this.isSecurityError = false,
  });

  @override
  String toString() => 'ApiException($code): $message';
}

/// Token Interceptor Wrapper for advanced token management
/// This is an inline implementation to avoid circular dependencies
class _TokenInterceptorWrapper extends Interceptor {
  final Dio _dio;
  final TokenManager _tokenManager;
  final SecureStorageService _secureStorage;

  /// Buffer time before token expiration to trigger proactive refresh
  static const Duration _refreshBuffer = Duration(minutes: 5);

  /// Maximum retry attempts for token refresh
  static const int _maxRefreshRetries = 3;

  /// Initial delay for exponential backoff
  static const Duration _initialRetryDelay = Duration(seconds: 1);

  /// Lock for preventing concurrent refresh operations
  bool _isRefreshing = false;

  /// Completer for coordinating refresh operations
  Completer<bool>? _refreshCompleter;

  /// Queue of pending requests waiting for refresh
  final List<_QueuedRequest> _requestQueue = [];

  _TokenInterceptorWrapper({
    required Dio dio,
    required TokenManager tokenManager,
    required SecureStorageService secureStorage,
  })  : _dio = dio,
        _tokenManager = tokenManager,
        _secureStorage = secureStorage;

  int get pendingRequestCount => _requestQueue.length;
  bool get isRefreshing => _isRefreshing;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Skip auth for public endpoints
    if (_isPublicEndpoint(options.path)) {
      return handler.next(options);
    }

    try {
      // Check if token needs proactive refresh
      await _checkAndRefreshTokenIfNeeded();

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

      handler.next(options);
    } catch (e) {
      AppLogger.e('Error in token interceptor onRequest', tag: 'TOKEN', error: e);
      handler.next(options);
    }
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    // Handle 401 Unauthorized
    if (err.response?.statusCode == 401) {
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
  Future<void> _checkAndRefreshTokenIfNeeded() async {
    final expiry = await _secureStorage.getTokenExpiry();
    if (expiry == null) return;

    final now = DateTime.now();
    final timeUntilExpiry = expiry.difference(now);

    // If token expires within buffer time, refresh proactively
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
      return false;
    }

    // If already refreshing, queue this request
    if (_isRefreshing) {
      return _queueRequest(requestOptions, handler);
    }

    // Attempt to refresh token
    final refreshSuccess = await _performTokenRefresh();

    if (refreshSuccess) {
      return _retryRequest(requestOptions, handler);
    } else {
      return false;
    }
  }

  /// Perform token refresh with retry logic
  Future<bool> _performTokenRefresh() async {
    if (_isRefreshing) {
      return _refreshCompleter?.future ?? Future.value(false);
    }

    _isRefreshing = true;
    _refreshCompleter = Completer<bool>();

    bool success = false;
    int retryCount = 0;
    Duration delay = _initialRetryDelay;

    while (retryCount < _maxRefreshRetries && !success) {
      try {
        if (retryCount > 0) {
          await Future.delayed(delay);
        }

        await _tokenManager.refreshToken();
        success = true;
      } catch (e) {
        retryCount++;
        delay = Duration(milliseconds: delay.inMilliseconds * 2);

        if (_isPermanentRefreshError(e)) {
          break;
        }
      }
    }

    _isRefreshing = false;
    _refreshCompleter?.complete(success);
    _refreshCompleter = null;

    if (success) {
      await _processQueuedRequests();
    } else {
      await _handleRefreshFailure();
      _rejectQueuedRequests();
    }

    return success;
  }

  bool _isPermanentRefreshError(dynamic error) {
    if (error is DioException) {
      final statusCode = error.response?.statusCode;
      return statusCode == 401 || statusCode == 403;
    }
    return false;
  }

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
    await _refreshCompleter?.future;
    return queuedRequest.completer.future;
  }

  Future<void> _processQueuedRequests() async {
    final newToken = await _secureStorage.getAccessToken();
    if (newToken == null) {
      _rejectQueuedRequests();
      return;
    }

    for (final queuedRequest in _requestQueue) {
      try {
        queuedRequest.options.headers['Authorization'] = 'Bearer $newToken';
        queuedRequest.options.extra['_token_retry'] = true;

        final response = await _dio.fetch(queuedRequest.options);
        queuedRequest.handler.resolve(response);
        queuedRequest.completer.complete(true);
      } catch (e) {
        if (e is DioException) {
          queuedRequest.handler.reject(e);
        }
        queuedRequest.completer.complete(false);
      }
    }

    _requestQueue.clear();
  }

  void _rejectQueuedRequests() {
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

  Future<bool> _retryRequest(
    RequestOptions options,
    ErrorInterceptorHandler handler,
  ) async {
    try {
      final newToken = await _secureStorage.getAccessToken();
      if (newToken == null) return false;

      options.headers['Authorization'] = 'Bearer $newToken';
      options.extra['_token_retry'] = true;

      final response = await _dio.fetch(options);
      handler.resolve(response);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> _handleRefreshFailure() async {
    try {
      await _secureStorage.deleteTokens();
      await _tokenManager.handleRefreshFailure();
    } catch (e) {
      AppLogger.e('Error clearing auth state', tag: 'TOKEN', error: e);
    }
  }

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
