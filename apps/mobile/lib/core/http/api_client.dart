import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/env_config.dart';
import '../security/security_config.dart';
import '../security/certificate_pinning_service.dart';
import '../security/certificate_config.dart';
import '../security/signing_key_service.dart';
import '../utils/app_logger.dart';
import 'rate_limiter.dart';
import 'request_signing_interceptor.dart';
import 'security_headers_interceptor.dart';

/// SAHOOL API Client with offline handling and certificate pinning
class ApiClient {
  late final Dio _dio;
  String? _authToken;
  String _tenantId = EnvConfig.defaultTenantId;
  CertificatePinningService? _certificatePinningService;
  late final RateLimiter _rateLimiter;

  ApiClient({
    String? baseUrl,
    SecurityConfig? securityConfig,
    CertificatePinningService? certificatePinningService,
    RateLimiter? rateLimiter,
    SigningKeyService? signingKeyService,
    bool enableRequestSigning = true,
    SecurityHeaderConfig? securityHeaderConfig,
    bool enableSecurityHeaderValidation = true,
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
          message = data['message'] ?? data['error'] ?? message;
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
