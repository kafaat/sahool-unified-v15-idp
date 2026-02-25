import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';
import '../config/env_config.dart';
import '../error_handling/app_exceptions.dart';
import '../security/security_config.dart';
import '../security/certificate_pinning_service.dart';
import '../security/certificate_config.dart';
import '../security/signing_key_service.dart';
import '../utils/app_logger.dart';
import 'network_config.dart';
import 'rate_limiter.dart';
import 'request_signing_interceptor.dart';
import 'security_headers_interceptor.dart';
import 'retry_interceptor.dart';
import 'logging_interceptor.dart';
import 'connectivity_aware_client.dart';

/// SAHOOL API Client with offline handling and certificate pinning
class ApiClient {
  late final Dio _dio;
  String? _authToken;
  String _tenantId = EnvConfig.defaultTenantId;
  CertificatePinningService? _certificatePinningService;
  late final RateLimiter _rateLimiter;
  late final NetworkConfig _networkConfig;
  NetworkConnectivityService? _connectivityService;

  ApiClient({
    String? baseUrl,
    SecurityConfig? securityConfig,
    CertificatePinningService? certificatePinningService,
    RateLimiter? rateLimiter,
    SigningKeyService? signingKeyService,
    bool enableRequestSigning = true,
    SecurityHeaderConfig? securityHeaderConfig,
    bool enableSecurityHeaderValidation = true,
    NetworkConfig? networkConfig,
    NetworkConnectivityService? connectivityService,
    bool enableConnectivityMonitoring = true,
    bool useAdvancedLogging = true,
  }) {
    // Use security config based on environment or build mode
    final config = securityConfig ?? SecurityConfig.fromBuildMode();

    // Use network config based on environment
    _networkConfig = networkConfig ?? NetworkConfig.fromEnvironment();

    // Store connectivity service for monitoring
    _connectivityService = connectivityService;

    // Initialize rate limiter
    _rateLimiter = rateLimiter ?? RateLimiter();

    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? EnvConfig.apiBaseUrl,
      connectTimeout: _networkConfig.connectTimeout,
      sendTimeout: _networkConfig.sendTimeout,
      receiveTimeout: _networkConfig.receiveTimeout,
      followRedirects: _networkConfig.followRedirects,
      maxRedirects: _networkConfig.maxRedirects,
      headers: _networkConfig.getDefaultHeaders(),
    ));

    // Configure TLS settings for enhanced security
    _configureTlsSettings(config);

    // Configure certificate pinning if enabled
    if (config.enableCertificatePinning) {
      // Determine environment for pin configuration
      final environment = EnvConfig.isProduction
          ? 'production'
          : EnvConfig.isStaging
              ? 'staging'
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
      dio: _dio,
      rateLimiter: _rateLimiter,
      queueExceededRequests: true,
    ));

    // Add retry interceptor for automatic retry on network errors
    _dio.interceptors.add(RetryInterceptor(
      dio: _dio,
      maxRetries: 3,
      initialDelay: const Duration(seconds: 1),
    ));

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
      AppLogger.w('Request signing disabled: no signing key service provided',
          tag: 'ApiClient');
    }

    // Add security header validation interceptor
    // Validates response headers for security best practices
    if (enableSecurityHeaderValidation) {
      final headerConfig =
          securityHeaderConfig ?? SecurityHeaderConfig.fromEnvironment();
      _dio.interceptors.add(SecurityHeadersInterceptor(config: headerConfig));

      if (kDebugMode) {
        AppLogger.i('Security header validation enabled',
            tag: 'ApiClient',
            data: {
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

    // Add connectivity monitoring interceptor if enabled
    if (enableConnectivityMonitoring && _connectivityService != null) {
      _dio.interceptors.add(ConnectivityInterceptor(
        connectivityService: _connectivityService!,
        blockOfflineRequests:
            false, // Allow requests, let retry handle failures
        queueOfflineRequests: false,
      ));
    }

    // Add advanced logging interceptor with PII protection instead of basic one
    if (useAdvancedLogging) {
      _dio.interceptors.add(LoggingInterceptor(
        logRequestHeaders: kDebugMode,
        logRequestBody: kDebugMode,
        logResponseHeaders: false,
        logResponseBody: false, // Avoid logging sensitive response data
        logErrorBody: kDebugMode,
        maxBodyLength: 2000,
      ));
    } else {
      _dio.interceptors.add(_BasicLoggingInterceptor());
    }

    if (kDebugMode) {
      AppLogger.i('ApiClient initialized', tag: 'ApiClient', data: {
        'baseUrl': baseUrl ?? EnvConfig.apiBaseUrl,
        'connectTimeout': _networkConfig.connectTimeout.inSeconds,
        'sendTimeout': _networkConfig.sendTimeout.inSeconds,
        'receiveTimeout': _networkConfig.receiveTimeout.inSeconds,
        'certificatePinning': config.enableCertificatePinning,
        'connectivityMonitoring':
            enableConnectivityMonitoring && _connectivityService != null,
      });
    }
  }

  /// Configure TLS settings for enhanced security
  void _configureTlsSettings(SecurityConfig securityConfig) {
    try {
      final adapter = _dio.httpClientAdapter;
      if (adapter is IOHttpClientAdapter) {
        adapter.createHttpClient = () {
          final client = HttpClient();

          // Set idle timeout for connection pooling
          client.idleTimeout = _networkConfig.keepAliveTimeout;

          // Set maximum connections per host
          client.maxConnectionsPerHost = _networkConfig.maxConnectionsPerHost;

          // Enable connection keep-alive
          client.autoUncompress = true;

          // Configure certificate validation
          if (!_networkConfig.validateCertificates && kDebugMode) {
            // Only in debug mode, allow self-signed certificates
            client.badCertificateCallback = (cert, host, port) => true;
            AppLogger.w('Certificate validation disabled (debug only)',
                tag: 'ApiClient');
          }

          return client;
        };

        if (kDebugMode) {
          AppLogger.d('TLS settings configured', tag: 'ApiClient', data: {
            'idleTimeout': _networkConfig.keepAliveTimeout.inSeconds,
            'maxConnectionsPerHost': _networkConfig.maxConnectionsPerHost,
            'minTlsVersion': _networkConfig.minTlsVersion.name,
          });
        }
      }
    } catch (e) {
      AppLogger.e('Error configuring TLS settings', tag: 'ApiClient', error: e);
    }
  }

  void setAuthToken(String token) {
    _authToken = token;
  }

  void setTenantId(String tenantId) {
    _tenantId = tenantId;
  }

  String? get authToken => _authToken;
  String get tenantId => _tenantId;
  CertificatePinningService? get certificatePinningService =>
      _certificatePinningService;
  RateLimiter get rateLimiter => _rateLimiter;
  NetworkConfig get networkConfig => _networkConfig;
  NetworkConnectivityService? get connectivityService => _connectivityService;

  /// Check if network is currently connected
  bool get isNetworkConnected => _connectivityService?.isConnected ?? true;

  /// Get current network state
  NetworkConnectivityState? get networkState =>
      _connectivityService?.currentState;

  /// Check if certificate pinning is enabled
  bool get isCertificatePinningEnabled => _certificatePinningService != null;

  /// Check for expiring certificate pins
  List<ExpiringPin> getExpiringPins({int daysThreshold = 30}) {
    if (_certificatePinningService == null) return [];
    return _certificatePinningService!
        .getExpiringPins(daysThreshold: daysThreshold);
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

  /// Convert DioException to AppException using unified error handling
  AppException _handleError(DioException e) {
    // Check for security header validation errors
    if (e.error is SecurityHeaderException) {
      final securityError = e.error as SecurityHeaderException;
      return SecurityException(
        message: 'Security header validation failed: ${securityError.code}',
        messageAr: 'فشل التحقق من رؤوس الأمان',
        code: securityError.code,
        originalError: e,
      );
    }

    // Use unified exception conversion
    return fromDioException(e);
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

/// Basic Logging Interceptor (fallback when advanced logging is disabled)
/// Only logs in debug mode to prevent sensitive data exposure in production
class _BasicLoggingInterceptor extends Interceptor {
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
      AppLogger.d('${response.statusCode} ${response.requestOptions.path}',
          tag: 'HTTP');
      // Note: Response body is intentionally not logged to prevent data leakage
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      AppLogger.e('${err.type} ${err.requestOptions.path}',
          tag: 'HTTP', error: err);
    }
    handler.next(err);
  }
}

/// API Exception - Legacy wrapper for backwards compatibility
///
/// New code should use [AppException] and its subclasses directly.
/// This class is kept for backwards compatibility with existing code.
@Deprecated('Use AppException from error_handling/app_exceptions.dart instead')
class ApiException extends AppException {
  @override
  bool get isNetworkError => type == ErrorType.network;

  bool get isSecurityError => type == ErrorType.security;

  ApiException({
    required String code,
    required String message,
    int? statusCode,
    bool isNetworkError = false,
    bool isSecurityError = false,
  }) : super(
          message: message,
          messageAr: message, // For backwards compatibility, use same message
          code: code,
          statusCode: statusCode,
          type: isSecurityError
              ? ErrorType.security
              : isNetworkError
                  ? ErrorType.network
                  : statusCode != null && statusCode >= 500
                      ? ErrorType.server
                      : ErrorType.client,
          isRetryable:
              isNetworkError || (statusCode != null && statusCode >= 500),
        );

  @override
  String toString() => 'ApiException($code): $message';
}
