import 'dart:async';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/env_config.dart';
import '../utils/app_logger.dart';

/// SAHOOL Kong Gateway Client
/// عميل بوابة Kong الموحد للاتصال بالخدمات
///
/// Features:
/// - Automatic token refresh
/// - Retry with exponential backoff
/// - Circuit breaker pattern
/// - Health monitoring
/// - Rate limit handling
///
/// ميزات:
/// - تجديد التوكن التلقائي
/// - إعادة المحاولة مع تأخير متصاعد
/// - نمط قاطع الدارة
/// - مراقبة الصحة
/// - التعامل مع حدود المعدل

/// Service configuration
class KongService {
  final String name;
  final String nameAr;
  final String basePath;
  final Duration timeout;
  final int maxRetries;

  const KongService({
    required this.name,
    required this.nameAr,
    required this.basePath,
    this.timeout = const Duration(seconds: 30),
    this.maxRetries = 3,
  });
}

/// Service health status
enum ServiceHealthStatus { healthy, degraded, unhealthy, unknown }

/// Service health result
class ServiceHealth {
  final String serviceName;
  final ServiceHealthStatus status;
  final int latencyMs;
  final DateTime timestamp;
  final String? errorMessage;

  const ServiceHealth({
    required this.serviceName,
    required this.status,
    required this.latencyMs,
    required this.timestamp,
    this.errorMessage,
  });

  bool get isHealthy => status == ServiceHealthStatus.healthy;
}

/// API response wrapper
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? errorCode;
  final String? errorMessage;
  final String? errorMessageAr;
  final String? requestId;

  const ApiResponse({
    required this.success,
    this.data,
    this.errorCode,
    this.errorMessage,
    this.errorMessageAr,
    this.requestId,
  });

  factory ApiResponse.success(T data, {String? requestId}) {
    return ApiResponse(success: true, data: data, requestId: requestId);
  }

  factory ApiResponse.error(String code, String message, {String? messageAr, String? requestId}) {
    return ApiResponse(
      success: false,
      errorCode: code,
      errorMessage: message,
      errorMessageAr: messageAr,
      requestId: requestId,
    );
  }
}

/// Available services through Kong gateway
class KongServices {
  static const fields = KongService(
    name: 'field-management',
    nameAr: 'إدارة الحقول',
    basePath: '/api/v1/fields',
  );

  static const auth = KongService(
    name: 'user-service',
    nameAr: 'المصادقة',
    basePath: '/api/v1/auth',
  );

  static const weather = KongService(
    name: 'weather-service',
    nameAr: 'الطقس',
    basePath: '/api/v1/weather',
  );

  static const vegetation = KongService(
    name: 'vegetation-analysis',
    nameAr: 'تحليل الغطاء النباتي',
    basePath: '/api/v1/vegetation',
  );

  static const satellite = KongService(
    name: 'satellite',
    nameAr: 'الأقمار الصناعية',
    basePath: '/api/v1/satellite',
  );

  static const ndvi = KongService(
    name: 'ndvi',
    nameAr: 'NDVI',
    basePath: '/api/v1/ndvi',
  );

  static const irrigation = KongService(
    name: 'irrigation-smart',
    nameAr: 'الري الذكي',
    basePath: '/api/v1/irrigation',
  );

  static const advisory = KongService(
    name: 'advisory-service',
    nameAr: 'الاستشارات',
    basePath: '/api/v1/advisory',
  );

  static const cropHealth = KongService(
    name: 'crop-intelligence',
    nameAr: 'صحة المحاصيل',
    basePath: '/api/v1/crop-health',
  );

  static const tasks = KongService(
    name: 'task-service',
    nameAr: 'المهام',
    basePath: '/api/v1/tasks',
  );

  static const equipment = KongService(
    name: 'equipment-service',
    nameAr: 'المعدات',
    basePath: '/api/v1/equipment',
  );

  static const alerts = KongService(
    name: 'alert-service',
    nameAr: 'التنبيهات',
    basePath: '/api/v1/alerts',
  );

  static const notifications = KongService(
    name: 'notification-service',
    nameAr: 'الإشعارات',
    basePath: '/api/v1/notifications',
  );

  static const marketplace = KongService(
    name: 'marketplace',
    nameAr: 'السوق',
    basePath: '/api/v1/marketplace',
  );

  static const iot = KongService(
    name: 'iot-service',
    nameAr: 'إنترنت الأشياء',
    basePath: '/api/v1/iot',
  );

  static const yield_ = KongService(
    name: 'yield-engine',
    nameAr: 'الإنتاج',
    basePath: '/api/v1/yield',
  );

  static const billing = KongService(
    name: 'billing-core',
    nameAr: 'الفوترة',
    basePath: '/api/v1/billing',
  );

  static const community = KongService(
    name: 'community-service',
    nameAr: 'المجتمع الزراعي',
    basePath: '/api/v1/community',
  );

  static const ai = KongService(
    name: 'copilot-api',
    nameAr: 'المستشار الذكي',
    basePath: '/api/v1/ai',
  );

  static const crm = KongService(
    name: 'crm-service',
    nameAr: 'إدارة المزارعين',
    basePath: '/api/v1/crm',
  );

  static const vision = KongService(
    name: 'yolo26-vision-service',
    nameAr: 'الرؤية الحاسوبية',
    basePath: '/api/v1/vision',
  );

  static List<KongService> get all => [
    fields, auth, weather, vegetation, satellite, ndvi,
    irrigation, advisory, cropHealth, tasks, equipment,
    alerts, notifications, marketplace, iot, yield_,
    billing, community, ai, crm, vision,
  ];
}

/// Kong Gateway Client
/// عميل بوابة Kong
class KongGatewayClient {
  static final KongGatewayClient _instance = KongGatewayClient._internal();
  factory KongGatewayClient() => _instance;
  KongGatewayClient._internal();

  late Dio _dio;
  String? _accessToken;
  String? _refreshToken;
  String? _tenantId;

  // Circuit breaker state
  final Map<String, int> _failureCount = {};
  final Map<String, DateTime> _circuitOpenTime = {};
  static const int _failureThreshold = 3;
  static const Duration _circuitTimeout = Duration(seconds: 30);

  // Rate limit tracking
  int? _rateLimitRemaining;
  DateTime? _rateLimitReset;

  /// Initialize the client
  Future<void> initialize() async {
    await EnvConfig.load();

    _dio = Dio(BaseOptions(
      baseUrl: EnvConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Client-Platform': Platform.isAndroid ? 'android' : 'ios',
        'X-Client-Version': EnvConfig.appVersion,
        'Accept-Language': 'ar,en',
      },
    ));

    // Add interceptors
    _dio.interceptors.add(_createAuthInterceptor());
    _dio.interceptors.add(_createRetryInterceptor());
    _dio.interceptors.add(_createLoggingInterceptor());
  }

  /// Set authentication tokens
  void setTokens({required String accessToken, String? refreshToken, String? tenantId}) {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    _tenantId = tenantId;
  }

  /// Clear authentication
  void clearAuth() {
    _accessToken = null;
    _refreshToken = null;
    _tenantId = null;
  }

  /// Check if authenticated
  bool get isAuthenticated => _accessToken != null;

  // ═══════════════════════════════════════════════════════════════════════════
  // HTTP Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// GET request
  Future<ApiResponse<T>> get<T>(
    KongService service,
    String path, {
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) async {
    return _request<T>(
      service: service,
      method: 'GET',
      path: path,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );
  }

  /// POST request
  Future<ApiResponse<T>> post<T>(
    KongService service,
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) async {
    return _request<T>(
      service: service,
      method: 'POST',
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );
  }

  /// PUT request
  Future<ApiResponse<T>> put<T>(
    KongService service,
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) async {
    return _request<T>(
      service: service,
      method: 'PUT',
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );
  }

  /// DELETE request
  Future<ApiResponse<T>> delete<T>(
    KongService service,
    String path, {
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) async {
    return _request<T>(
      service: service,
      method: 'DELETE',
      path: path,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Checks
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check health of a single service
  Future<ServiceHealth> checkHealth(KongService service) async {
    final stopwatch = Stopwatch()..start();

    try {
      final response = await _dio.get(
        '${service.basePath}/healthz',
        options: Options(
          receiveTimeout: const Duration(seconds: 5),
          validateStatus: (status) => true,
        ),
      );

      stopwatch.stop();
      final latency = stopwatch.elapsedMilliseconds;

      if (response.statusCode == 200) {
        return ServiceHealth(
          serviceName: service.name,
          status: latency > 2000 ? ServiceHealthStatus.degraded : ServiceHealthStatus.healthy,
          latencyMs: latency,
          timestamp: DateTime.now(),
        );
      } else {
        return ServiceHealth(
          serviceName: service.name,
          status: ServiceHealthStatus.degraded,
          latencyMs: latency,
          timestamp: DateTime.now(),
          errorMessage: 'HTTP ${response.statusCode}',
        );
      }
    } catch (e) {
      stopwatch.stop();
      return ServiceHealth(
        serviceName: service.name,
        status: ServiceHealthStatus.unhealthy,
        latencyMs: stopwatch.elapsedMilliseconds,
        timestamp: DateTime.now(),
        errorMessage: e.toString(),
      );
    }
  }

  /// Check health of all services
  Future<List<ServiceHealth>> checkAllServicesHealth() async {
    final futures = KongServices.all.map((service) => checkHealth(service));
    return Future.wait(futures);
  }

  /// Get rate limit info
  Map<String, dynamic> get rateLimitInfo => {
    'remaining': _rateLimitRemaining,
    'resetAt': _rateLimitReset?.toIso8601String(),
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods
  // ═══════════════════════════════════════════════════════════════════════════

  Future<ApiResponse<T>> _request<T>({
    required KongService service,
    required String method,
    required String path,
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) async {
    // Check circuit breaker
    if (_isCircuitOpen(service.name)) {
      return ApiResponse.error(
        'CIRCUIT_OPEN',
        'Service temporarily unavailable',
        messageAr: 'الخدمة غير متاحة مؤقتاً',
      );
    }

    final url = '${service.basePath}$path';

    try {
      final response = await _dio.request(
        url,
        data: data,
        queryParameters: queryParams,
        options: Options(
          method: method,
          receiveTimeout: service.timeout,
          extra: {'service': service.name, 'maxRetries': service.maxRetries},
        ),
        cancelToken: cancelToken,
      );

      // Reset circuit breaker on success
      _resetCircuitBreaker(service.name);

      // Parse response
      final responseData = response.data;
      final requestId = response.headers.value('X-Request-Id');

      // Update rate limit info
      _updateRateLimitInfo(response.headers);

      if (fromJson != null && responseData != null) {
        return ApiResponse.success(fromJson(responseData), requestId: requestId);
      }

      return ApiResponse.success(responseData as T, requestId: requestId);

    } on DioException catch (e) {
      _recordFailure(service.name);

      final requestId = e.response?.headers.value('X-Request-Id');

      if (e.response?.statusCode == 429) {
        // Rate limited
        return ApiResponse.error(
          'RATE_LIMITED',
          'Too many requests. Please wait.',
          messageAr: 'طلبات كثيرة جداً. الرجاء الانتظار.',
          requestId: requestId,
        );
      }

      if (e.response?.statusCode == 401) {
        return ApiResponse.error(
          'UNAUTHORIZED',
          'Authentication required',
          messageAr: 'المصادقة مطلوبة',
          requestId: requestId,
        );
      }

      if (e.response?.statusCode == 403) {
        return ApiResponse.error(
          'FORBIDDEN',
          'Access denied',
          messageAr: 'الوصول مرفوض',
          requestId: requestId,
        );
      }

      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        return ApiResponse.error(
          'TIMEOUT',
          'Request timed out',
          messageAr: 'انتهت مهلة الطلب',
          requestId: requestId,
        );
      }

      if (e.type == DioExceptionType.connectionError) {
        return ApiResponse.error(
          'NO_CONNECTION',
          'No internet connection',
          messageAr: 'لا يوجد اتصال بالإنترنت',
        );
      }

      // Extract error from response
      final errorData = e.response?.data;
      if (errorData is Map) {
        return ApiResponse.error(
          errorData['code']?.toString() ?? 'ERROR',
          errorData['message']?.toString() ?? e.message ?? 'Unknown error',
          messageAr: errorData['message_ar']?.toString(),
          requestId: requestId,
        );
      }

      return ApiResponse.error(
        'ERROR',
        e.message ?? 'Unknown error',
        requestId: requestId,
      );
    } catch (e) {
      _recordFailure(service.name);

      return ApiResponse.error(
        'UNKNOWN',
        e.toString(),
        messageAr: 'خطأ غير معروف',
      );
    }
  }

  // Circuit breaker helpers
  bool _isCircuitOpen(String serviceName) {
    final openTime = _circuitOpenTime[serviceName];
    if (openTime == null) return false;

    if (DateTime.now().difference(openTime) > _circuitTimeout) {
      _circuitOpenTime.remove(serviceName);
      _failureCount.remove(serviceName);
      return false;
    }

    return true;
  }

  void _recordFailure(String serviceName) {
    _failureCount[serviceName] = (_failureCount[serviceName] ?? 0) + 1;

    if (_failureCount[serviceName]! >= _failureThreshold) {
      _circuitOpenTime[serviceName] = DateTime.now();
      AppLogger.w('Circuit breaker opened for $serviceName', tag: 'KongGateway');
    }
  }

  void _resetCircuitBreaker(String serviceName) {
    _failureCount.remove(serviceName);
    _circuitOpenTime.remove(serviceName);
  }

  void _updateRateLimitInfo(Headers headers) {
    final remaining = headers.value('X-RateLimit-Remaining-Minute');
    if (remaining != null) {
      _rateLimitRemaining = int.tryParse(remaining);
    }
  }

  // Interceptors
  Interceptor _createAuthInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_accessToken != null) {
          options.headers['Authorization'] = 'Bearer $_accessToken';
        }
        if (_tenantId != null) {
          options.headers['X-Tenant-Id'] = _tenantId;
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401 && _refreshToken != null) {
          // Try to refresh token
          final refreshed = await _refreshAccessToken();
          if (refreshed) {
            // Retry the request
            final opts = error.requestOptions;
            opts.headers['Authorization'] = 'Bearer $_accessToken';
            try {
              final response = await _dio.fetch(opts);
              handler.resolve(response);
              return;
            } catch (e) {
              // Fall through to error handler
            }
          }
        }
        handler.next(error);
      },
    );
  }

  Interceptor _createRetryInterceptor() {
    return InterceptorsWrapper(
      onError: (error, handler) async {
        final extra = error.requestOptions.extra;
        final maxRetries = extra['maxRetries'] as int? ?? 3;
        final retryCount = extra['retryCount'] as int? ?? 0;

        if (_shouldRetry(error) && retryCount < maxRetries) {
          // Exponential backoff
          final delay = Duration(milliseconds: 1000 * (retryCount + 1));
          await Future.delayed(delay);

          extra['retryCount'] = retryCount + 1;
          try {
            final response = await _dio.fetch(error.requestOptions);
            handler.resolve(response);
            return;
          } catch (e) {
            if (retryCount + 1 >= maxRetries) {
              handler.next(error);
              return;
            }
          }
        }
        handler.next(error);
      },
    );
  }

  bool _shouldRetry(DioException error) {
    return error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        (error.response?.statusCode ?? 0) >= 500;
  }

  Interceptor _createLoggingInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) {
        if (kDebugMode) {
          AppLogger.d(
            '→ ${options.method} ${options.path}',
            tag: 'KongGateway',
          );
        }
        handler.next(options);
      },
      onResponse: (response, handler) {
        if (kDebugMode) {
          AppLogger.d(
            '← ${response.statusCode} ${response.requestOptions.path}',
            tag: 'KongGateway',
          );
        }
        handler.next(response);
      },
      onError: (error, handler) {
        AppLogger.e(
          '✕ ${error.requestOptions.method} ${error.requestOptions.path}: ${error.message}',
          tag: 'KongGateway',
          error: error,
        );
        handler.next(error);
      },
    );
  }

  Future<bool> _refreshAccessToken() async {
    if (_refreshToken == null) return false;

    try {
      final response = await _dio.post(
        '${KongServices.auth.basePath}/refresh',
        data: {'refresh_token': _refreshToken},
        options: Options(
          headers: {'Authorization': null}, // Remove old token
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        _accessToken = data['access_token'] as String?;
        _refreshToken = data['refresh_token'] as String? ?? _refreshToken;
        return true;
      }
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'KongGateway', error: e);
    }

    return false;
  }
}

/// Global Kong gateway client instance
final kongGateway = KongGatewayClient();
