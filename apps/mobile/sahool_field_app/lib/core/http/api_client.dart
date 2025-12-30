import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/config.dart';
import '../utils/app_logger.dart';
import 'api_error_handler.dart';
import 'api_result.dart';
import 'certificate_pinning.dart';
import 'retry_interceptor.dart';

/// SAHOOL API Client with improved error handling, retry logic, and SSL certificate pinning
class ApiClient {
  late final Dio _dio;
  late final CircuitBreaker _circuitBreaker;
  String? _authToken;
  String _tenantId = AppConfig.defaultTenantId;

  ApiClient({
    String? baseUrl,
    int maxRetries = 3,
    Duration baseRetryDelay = const Duration(milliseconds: 500),
    bool enableCircuitBreaker = true,
  }) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Initialize circuit breaker
    _circuitBreaker = CircuitBreaker(
      failureThreshold: 5,
      resetTimeout: const Duration(seconds: 60),
      halfOpenTimeout: const Duration(seconds: 30),
    );

    // Configure SSL certificate pinning
    CertificatePinning.configureDio(_dio);

    // Verify certificate pinning configuration
    CertificatePinning.verifyConfiguration();

    // Add interceptors (order matters!)
    // 1. Retry interceptor (should be first to catch and retry errors)
    _dio.interceptors.add(
      RetryInterceptor(
        maxRetries: maxRetries,
        baseDelay: baseRetryDelay,
        circuitBreaker: enableCircuitBreaker ? _circuitBreaker : null,
      ),
    );

    // 2. Auth interceptor (adds authentication headers)
    _dio.interceptors.add(_AuthInterceptor(this));

    // 3. Logging interceptor (should be last to log final requests)
    _dio.interceptors.add(_LoggingInterceptor());

    AppLogger.i(
      'ApiClient initialized',
      tag: 'API_CLIENT',
      data: {
        'baseUrl': _dio.options.baseUrl,
        'maxRetries': maxRetries,
        'circuitBreakerEnabled': enableCircuitBreaker,
      },
    );
  }

  void setAuthToken(String token) {
    _authToken = token;
  }

  void setTenantId(String tenantId) {
    _tenantId = tenantId;
  }

  String? get authToken => _authToken;
  String get tenantId => _tenantId;

  /// Get circuit breaker status
  Map<String, dynamic> getCircuitBreakerStatus() => _circuitBreaker.getStatus();

  /// Reset circuit breaker
  void resetCircuitBreaker() => _circuitBreaker.reset();

  // ═══════════════════════════════════════════════════════════════════════════
  // Type-safe ApiResult methods (recommended for new code)
  // ═══════════════════════════════════════════════════════════════════════════

  /// GET request with ApiResult
  Future<ApiResult<T>> getSafe<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
      );
      return ApiResult.success(response.data as T);
    } on DioException catch (e, stackTrace) {
      return ApiResult.failure(ApiErrorHandler.handleError(e, stackTrace: stackTrace));
    } catch (e, stackTrace) {
      return ApiResult.failure(
        ApiErrorHandler.handleGenericError(
          e as Exception,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  /// POST request with ApiResult
  Future<ApiResult<T>> postSafe<T>(
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
      return ApiResult.success(response.data as T);
    } on DioException catch (e, stackTrace) {
      return ApiResult.failure(ApiErrorHandler.handleError(e, stackTrace: stackTrace));
    } catch (e, stackTrace) {
      return ApiResult.failure(
        ApiErrorHandler.handleGenericError(
          e as Exception,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  /// PUT request with ApiResult
  Future<ApiResult<T>> putSafe<T>(
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
      return ApiResult.success(response.data as T);
    } on DioException catch (e, stackTrace) {
      return ApiResult.failure(ApiErrorHandler.handleError(e, stackTrace: stackTrace));
    } catch (e, stackTrace) {
      return ApiResult.failure(
        ApiErrorHandler.handleGenericError(
          e as Exception,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  /// DELETE request with ApiResult
  Future<ApiResult<T>> deleteSafe<T>(
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
      return ApiResult.success(response.data as T);
    } on DioException catch (e, stackTrace) {
      return ApiResult.failure(ApiErrorHandler.handleError(e, stackTrace: stackTrace));
    } catch (e, stackTrace) {
      return ApiResult.failure(
        ApiErrorHandler.handleGenericError(
          e as Exception,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  /// Upload file with ApiResult
  Future<ApiResult<T>> uploadFileSafe<T>(
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
      return ApiResult.success(response.data as T);
    } on DioException catch (e, stackTrace) {
      return ApiResult.failure(ApiErrorHandler.handleError(e, stackTrace: stackTrace));
    } catch (e, stackTrace) {
      return ApiResult.failure(
        ApiErrorHandler.handleGenericError(
          e as Exception,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Legacy exception-based methods (for backward compatibility)
  // ═══════════════════════════════════════════════════════════════════════════

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

  /// Convert ApiError to legacy ApiException for backward compatibility
  ApiException _convertToLegacyException(ApiError error) {
    return ApiException(
      code: error.code ?? error.type.name.toUpperCase(),
      message: error.message,
      statusCode: error.statusCode,
      isNetworkError: error.isNetworkError,
    );
  }

  /// Handle error and convert to legacy ApiException
  ApiException _handleError(DioException e) {
    final apiError = ApiErrorHandler.handleError(e);
    return _convertToLegacyException(apiError);
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
  final _stopwatches = <int, Stopwatch>{};

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Start timing the request
    final stopwatch = Stopwatch()..start();
    _stopwatches[options.hashCode] = stopwatch;

    AppLogger.network(
      options.method,
      options.path,
      data: {
        'queryParams': options.queryParameters.isNotEmpty
            ? options.queryParameters
            : null,
      },
    );
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // Stop timing
    final stopwatch = _stopwatches.remove(response.requestOptions.hashCode);
    stopwatch?.stop();

    AppLogger.network(
      response.requestOptions.method,
      response.requestOptions.path,
      statusCode: response.statusCode,
      duration: stopwatch?.elapsed,
    );
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Stop timing
    final stopwatch = _stopwatches.remove(err.requestOptions.hashCode);
    stopwatch?.stop();

    AppLogger.network(
      err.requestOptions.method,
      err.requestOptions.path,
      statusCode: err.response?.statusCode,
      duration: stopwatch?.elapsed,
      data: {
        'error': err.type.name,
        'message': err.message,
      },
    );
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
