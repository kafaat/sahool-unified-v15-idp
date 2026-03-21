/// SAHOOL Service Connector
/// موصل الخدمات - الفئة الأساسية للاتصال بالخدمات الخلفية
///
/// Features:
/// - Authentication header injection
/// - Request/response logging
/// - Error transformation
/// - Retry logic
/// - Offline support
/// - Rate limiting awareness
library;

import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../auth/secure_storage_service.dart';
import '../config/api_config.dart';
import '../config/env_config.dart';
import '../http/auth_interceptor.dart';
import '../http/logging_interceptor.dart';
import '../http/retry_interceptor.dart';
import '../network/api_result.dart';
import '../network/dio_error_handler.dart';
import '../utils/app_logger.dart';
import 'service_registry.dart';

/// Request method enumeration
enum HttpMethod { get, post, put, patch, delete }

/// Service request configuration
/// تكوين طلب الخدمة
class ServiceRequest {
  final String endpoint;
  final HttpMethod method;
  final Map<String, dynamic>? queryParameters;
  final dynamic data;
  final Map<String, String>? headers;
  final Duration? timeout;
  final bool requiresAuth;
  final bool useCache;
  final Duration? cacheExpiry;
  final String? cacheKey;

  const ServiceRequest({
    required this.endpoint,
    this.method = HttpMethod.get,
    this.queryParameters,
    this.data,
    this.headers,
    this.timeout,
    this.requiresAuth = true,
    this.useCache = false,
    this.cacheExpiry,
    this.cacheKey,
  });
}

/// Service response wrapper
/// غلاف استجابة الخدمة
class ServiceResponse<T> {
  final T? data;
  final int? statusCode;
  final Map<String, dynamic>? headers;
  final Duration? latency;
  final bool fromCache;
  final String? errorMessage;
  final String? errorMessageAr;

  const ServiceResponse({
    this.data,
    this.statusCode,
    this.headers,
    this.latency,
    this.fromCache = false,
    this.errorMessage,
    this.errorMessageAr,
  });

  bool get isSuccess => statusCode != null && statusCode! >= 200 && statusCode! < 300;
  bool get isError => !isSuccess;
}

/// Base Service Connector class
/// فئة موصل الخدمات الأساسية
abstract class ServiceConnector {
  final String serviceId;
  final Ref ref;
  late final Dio _dio;
  late final ServiceConfig? _serviceConfig;

  ServiceConnector({
    required this.serviceId,
    required this.ref,
  }) {
    _serviceConfig = ref.read(serviceRegistryProvider).getService(serviceId);
    _dio = _createDioInstance();
  }

  /// Service configuration
  ServiceConfig? get serviceConfig => _serviceConfig;

  /// Base URL for this service
  String get baseUrl => _serviceConfig?.baseUrl ?? '';

  /// Get endpoint URL
  String? getEndpoint(String key) {
    return _serviceConfig?.endpoints[key];
  }

  /// Create configured Dio instance
  Dio _createDioInstance() {
    final dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: EnvConfig.connectTimeout,
      receiveTimeout: EnvConfig.receiveTimeout,
      headers: ApiConfig.defaultHeaders,
    ));

    // Add interceptors
    dio.interceptors.addAll([
      AuthInterceptor(ref, dio),
      LoggingInterceptor(
        logRequestBody: true,
        logResponseBody: false,
        logErrorBody: true,
      ),
      RetryInterceptor(dio: dio, maxRetries: 3),
    ]);

    return dio;
  }

  /// Execute a service request
  /// تنفيذ طلب خدمة
  Future<ApiResult<T>> execute<T>(
    ServiceRequest request, {
    required T Function(dynamic data) parser,
  }) async {
    final startTime = DateTime.now();

    try {
      // Check if service is available
      final health = ref.read(serviceRegistryProvider).getServiceHealth(serviceId);
      if (health?.status == ServiceStatus.offline) {
        return const Failure(
          'الخدمة غير متوفرة حالياً',
          statusCode: 503,
        );
      }

      // Build full URL
      final url = _buildUrl(request.endpoint);

      // Add auth headers if required
      final headers = await _buildHeaders(request);

      // Execute request
      final response = await _executeRequest(
        url: url,
        method: request.method,
        queryParameters: request.queryParameters,
        data: request.data,
        headers: headers,
        timeout: request.timeout,
      );

      final latency = DateTime.now().difference(startTime);

      // Log successful request
      AppLogger.network(
        request.method.name.toUpperCase(),
        url,
        statusCode: response.statusCode,
        duration: latency,
      );

      // Update service health
      _updateServiceHealth(ServiceStatus.healthy, latency);

      // Parse response
      return Success(parser(response.data));
    } on DioException catch (e) {
      final latency = DateTime.now().difference(startTime);

      // Update service health based on error
      _handleDioError(e, latency);

      return DioErrorHandler.handle(e);
    } catch (e, stackTrace) {
      AppLogger.e(
        'Service request failed',
        tag: serviceId,
        error: e,
        stackTrace: stackTrace,
      );
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// Execute raw request and return response
  Future<Response> _executeRequest({
    required String url,
    required HttpMethod method,
    Map<String, dynamic>? queryParameters,
    dynamic data,
    Map<String, String>? headers,
    Duration? timeout,
  }) async {
    final options = Options(
      headers: headers,
      sendTimeout: timeout,
      receiveTimeout: timeout,
    );

    switch (method) {
      case HttpMethod.get:
        return _dio.get(url, queryParameters: queryParameters, options: options);
      case HttpMethod.post:
        return _dio.post(url, data: data, queryParameters: queryParameters, options: options);
      case HttpMethod.put:
        return _dio.put(url, data: data, queryParameters: queryParameters, options: options);
      case HttpMethod.patch:
        return _dio.patch(url, data: data, queryParameters: queryParameters, options: options);
      case HttpMethod.delete:
        return _dio.delete(url, data: data, queryParameters: queryParameters, options: options);
    }
  }

  /// Build full URL from endpoint
  String _buildUrl(String endpoint) {
    if (endpoint.startsWith('http')) {
      return endpoint;
    }
    if (endpoint.startsWith('/')) {
      return '$baseUrl$endpoint';
    }
    return '$baseUrl/$endpoint';
  }

  /// Build headers including auth token
  Future<Map<String, String>> _buildHeaders(ServiceRequest request) async {
    final headers = <String, String>{
      ...ApiConfig.defaultHeaders,
      if (request.headers != null) ...request.headers!,
    };

    if (request.requiresAuth) {
      final secureStorage = ref.read(secureStorageProvider);
      final token = await secureStorage.getAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final tenantId = await secureStorage.getTenantId();
      if (tenantId != null) {
        headers['X-Tenant-Id'] = tenantId;
      }
    }

    return headers;
  }

  /// Handle Dio errors and update service health
  void _handleDioError(DioException e, Duration latency) {
    ServiceStatus status;

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        status = ServiceStatus.degraded;
        break;
      case DioExceptionType.connectionError:
        status = ServiceStatus.offline;
        break;
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        if (statusCode != null && statusCode >= 500) {
          status = ServiceStatus.unhealthy;
        } else {
          status = ServiceStatus.degraded;
        }
        break;
      default:
        status = ServiceStatus.unknown;
    }

    _updateServiceHealth(status, latency, errorMessage: e.message);
  }

  /// Update service health in registry
  void _updateServiceHealth(
    ServiceStatus status,
    Duration latency, {
    String? errorMessage,
  }) {
    final registry = ref.read(serviceRegistryProvider);
    final currentHealth = registry.getServiceHealth(serviceId);

    if (currentHealth != null) {
      registry.updateHealth(
        serviceId,
        currentHealth.copyWith(
          status: status,
          lastCheck: DateTime.now(),
          latency: latency,
          errorMessage: errorMessage,
        ),
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Convenience Methods
  // ═══════════════════════════════════════════════════════════════════════════════

  /// GET request
  Future<ApiResult<T>> get<T>(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    required T Function(dynamic data) parser,
    bool requiresAuth = true,
  }) {
    return execute(
      ServiceRequest(
        endpoint: endpoint,
        method: HttpMethod.get,
        queryParameters: queryParameters,
        requiresAuth: requiresAuth,
      ),
      parser: parser,
    );
  }

  /// POST request
  Future<ApiResult<T>> post<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    required T Function(dynamic data) parser,
    bool requiresAuth = true,
  }) {
    return execute(
      ServiceRequest(
        endpoint: endpoint,
        method: HttpMethod.post,
        data: data,
        queryParameters: queryParameters,
        requiresAuth: requiresAuth,
      ),
      parser: parser,
    );
  }

  /// PUT request
  Future<ApiResult<T>> put<T>(
    String endpoint, {
    dynamic data,
    required T Function(dynamic data) parser,
    bool requiresAuth = true,
  }) {
    return execute(
      ServiceRequest(
        endpoint: endpoint,
        method: HttpMethod.put,
        data: data,
        requiresAuth: requiresAuth,
      ),
      parser: parser,
    );
  }

  /// PATCH request
  Future<ApiResult<T>> patch<T>(
    String endpoint, {
    dynamic data,
    required T Function(dynamic data) parser,
    bool requiresAuth = true,
  }) {
    return execute(
      ServiceRequest(
        endpoint: endpoint,
        method: HttpMethod.patch,
        data: data,
        requiresAuth: requiresAuth,
      ),
      parser: parser,
    );
  }

  /// DELETE request
  Future<ApiResult<T>> delete<T>(
    String endpoint, {
    dynamic data,
    required T Function(dynamic data) parser,
    bool requiresAuth = true,
  }) {
    return execute(
      ServiceRequest(
        endpoint: endpoint,
        method: HttpMethod.delete,
        data: data,
        requiresAuth: requiresAuth,
      ),
      parser: parser,
    );
  }

  /// Upload file
  Future<ApiResult<T>> uploadFile<T>(
    String endpoint, {
    required String filePath,
    required String fieldName,
    Map<String, dynamic>? additionalData,
    required T Function(dynamic data) parser,
    void Function(int sent, int total)? onProgress,
  }) async {
    final startTime = DateTime.now();

    try {
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(filePath),
        if (additionalData != null) ...additionalData,
      });

      final url = _buildUrl(endpoint);
      final headers = await _buildHeaders(
        const ServiceRequest(endpoint: '', requiresAuth: true),
      );

      final response = await _dio.post(
        url,
        data: formData,
        options: Options(headers: headers),
        onSendProgress: onProgress,
      );

      final latency = DateTime.now().difference(startTime);
      _updateServiceHealth(ServiceStatus.healthy, latency);

      return Success(parser(response.data));
    } on DioException catch (e) {
      final latency = DateTime.now().difference(startTime);
      _handleDioError(e, latency);
      return DioErrorHandler.handle(e);
    } catch (e) {
      return Failure('فشل رفع الملف: $e');
    }
  }

  /// Download file
  Future<ApiResult<String>> downloadFile(
    String endpoint, {
    required String savePath,
    void Function(int received, int total)? onProgress,
  }) async {
    final startTime = DateTime.now();

    try {
      final url = _buildUrl(endpoint);
      final headers = await _buildHeaders(
        const ServiceRequest(endpoint: '', requiresAuth: true),
      );

      await _dio.download(
        url,
        savePath,
        options: Options(headers: headers),
        onReceiveProgress: onProgress,
      );

      final latency = DateTime.now().difference(startTime);
      _updateServiceHealth(ServiceStatus.healthy, latency);

      return Success(savePath);
    } on DioException catch (e) {
      final latency = DateTime.now().difference(startTime);
      _handleDioError(e, latency);
      return DioErrorHandler.handle(e);
    } catch (e) {
      return Failure('فشل تحميل الملف: $e');
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Generic Service Connector Provider Factory
// ═══════════════════════════════════════════════════════════════════════════════

/// Generic service connector for dynamic service access
class GenericServiceConnector extends ServiceConnector {
  GenericServiceConnector({
    required super.serviceId,
    required super.ref,
  });
}

/// Provider for creating service connectors
final serviceConnectorProvider = Provider.family<ServiceConnector, String>((ref, serviceId) {
  return GenericServiceConnector(
    serviceId: serviceId,
    ref: ref,
  );
});
