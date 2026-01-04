import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/config.dart' as config;
import '../config/env_config.dart';
import '../security/security_config.dart';
import '../security/certificate_pinning_service.dart';
import '../security/certificate_config.dart';

/// SAHOOL API Client with offline handling and certificate pinning
class ApiClient {
  late final Dio _dio;
  String? _authToken;
  String _tenantId = config.AppConfig.defaultTenantId;
  CertificatePinningService? _certificatePinningService;

  ApiClient({
    String? baseUrl,
    SecurityConfig? securityConfig,
    CertificatePinningService? certificatePinningService,
  }) {
    // Use security config based on environment or build mode
    final secConfig = securityConfig ?? SecurityConfig.fromBuildMode();

    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? config.AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: secConfig.requestTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Configure certificate pinning if enabled
    if (secConfig.enableCertificatePinning) {
      // Determine environment for pin configuration
      final environment = EnvConfig.isProduction ? 'production'
          : EnvConfig.isStaging ? 'staging'
          : 'development';

      final pins = CertificateConfig.getPinsForEnvironment(environment);

      _certificatePinningService = certificatePinningService ??
          CertificatePinningService(
            certificatePins: pins,
            allowDebugBypass: secConfig.allowPinningDebugBypass,
            enforceStrict: secConfig.strictCertificatePinning,
          );
      _certificatePinningService!.configureDio(_dio);

      if (kDebugMode) {
        print('🔒 SSL Certificate Pinning enabled');
        print('   Environment: $environment');
        print('   Strict mode: ${secConfig.strictCertificatePinning}');
        print('   Debug bypass: ${secConfig.allowPinningDebugBypass}');
        print('   Configured domains: ${_certificatePinningService!.getConfiguredDomains()}');
      }
    } else if (kDebugMode) {
      print('⚠️ Certificate pinning is disabled');
    }

    // Add interceptors
    _dio.interceptors.add(_AuthInterceptor(this));
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
      print('📤 ${options.method} ${options.path}');
      // Note: Authorization headers and request body are intentionally not logged
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (kDebugMode) {
      print('📥 ${response.statusCode} ${response.requestOptions.path}');
      // Note: Response body is intentionally not logged to prevent data leakage
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      print('❌ ${err.type} ${err.requestOptions.path}');
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

  ApiException({
    required this.code,
    required this.message,
    this.statusCode,
    this.isNetworkError = false,
  });

  @override
  String toString() => 'ApiException($code): $message';
}
