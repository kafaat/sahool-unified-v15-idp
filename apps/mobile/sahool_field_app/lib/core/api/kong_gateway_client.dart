import 'dart:async';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';
import '../config/env_config.dart';
import '../http/network_config.dart';
import '../http/connectivity_aware_client.dart';
import '../performance/network_cache.dart';
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

  factory ApiResponse.error(String code, String message,
      {String? messageAr, String? requestId}) {
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
    name: 'yield-prediction-service',
    nameAr: 'الإنتاج',
    basePath: '/api/v1/yield',
  );

  /// Billing service - خدمة الفوترة
  static const billing = KongService(
    name: 'billing-core',
    nameAr: 'الفوترة',
    basePath: '/api/v1/billing',
  );

  /// Inventory service - خدمة المخزون
  static const inventory = KongService(
    name: 'inventory-service',
    nameAr: 'المخزون',
    basePath: '/api/v1/inventory',
  );

  /// Spray/Yield operations - عمليات الرش والمحصول
  static const spray = KongService(
    name: 'yield-prediction-service',
    nameAr: 'عمليات الرش',
    basePath: '/api/v1/spray',
  );

  /// User profile service - خدمة الملف الشخصي
  static const userProfile = KongService(
    name: 'user-service',
    nameAr: 'الملف الشخصي',
    basePath: '/api/v1/users',
  );

  /// Community/Social features - المجتمع
  static const community = KongService(
    name: 'chat-service',
    nameAr: 'المجتمع',
    basePath: '/api/v1/community',
  );

  /// Chat/Messaging service - خدمة الرسائل
  static const chat = KongService(
    name: 'chat-service',
    nameAr: 'الرسائل',
    basePath: '/api/v1/chat',
  );

  /// Virtual sensors service - المستشعرات الافتراضية
  static const virtualSensors = KongService(
    name: 'virtual-sensors',
    nameAr: 'المستشعرات الافتراضية',
    basePath: '/api/v1/virtual-sensors',
  );

  /// AI Advisor service - المستشار الذكي
  static const aiAdvisor = KongService(
    name: 'ai-advisor',
    nameAr: 'المستشار الذكي',
    basePath: '/api/v1/ai-advisor',
    timeout: Duration(seconds: 60), // Longer timeout for AI operations
  );

  /// Crops service - المحاصيل
  static const crops = KongService(
    name: 'crop-intelligence',
    nameAr: 'المحاصيل',
    basePath: '/api/v1/crops',
  );

  /// Indicators service - المؤشرات
  static const indicators = KongService(
    name: 'indicators-service',
    nameAr: 'المؤشرات',
    basePath: '/api/v1/indicators',
  );

  /// Research/Trials service - البحث والتجارب
  static const research = KongService(
    name: 'research-core',
    nameAr: 'البحث والتجارب',
    basePath: '/api/v1/research',
  );

  /// Copilot API - المساعد الذكي (RAG + Multi-LLM)
  static const copilot = KongService(
    name: 'copilot-api',
    nameAr: 'المساعد الذكي',
    basePath: '/api/v1/copilot',
    timeout: Duration(seconds: 120), // Longer timeout for AI/RAG operations
  );

  /// Pest Detection service - كشف الآفات
  static const pestDetection = KongService(
    name: 'pest-detection-service',
    nameAr: 'كشف الآفات',
    basePath: '/api/v1/pest-detection',
    timeout: Duration(seconds: 60),
  );

  /// Soil Analysis service - تحليل التربة
  static const soilAnalysis = KongService(
    name: 'soil-analysis-service',
    nameAr: 'تحليل التربة',
    basePath: '/api/v1/soil-analysis',
  );

  /// Irrigation Cycle Engine - محرك دورات الري
  static const irrigationEngine = KongService(
    name: 'irrigation-cycle-engine',
    nameAr: 'محرك الري المحوري',
    basePath: '/api/v1/irrigation-engine',
  );

  /// Field Intelligence service - ذكاء الحقل
  static const fieldIntelligence = KongService(
    name: 'field-intelligence',
    nameAr: 'ذكاء الحقل',
    basePath: '/api/v1/field-intelligence',
  );

  /// Astronomical Calendar - التقويم الفلكي
  static const astronomicalCalendar = KongService(
    name: 'astronomical-calendar',
    nameAr: 'التقويم الفلكي',
    basePath: '/api/v1/astronomical',
  );

  static List<KongService> get all => [
        fields,
        auth,
        weather,
        vegetation,
        satellite,
        ndvi,
        irrigation,
        advisory,
        cropHealth,
        tasks,
        equipment,
        alerts,
        notifications,
        marketplace,
        iot,
        yield_,
        billing,
        inventory,
        spray,
        userProfile,
        community,
        chat,
        virtualSensors,
        aiAdvisor,
        crops,
        indicators,
        research,
        copilot,
        pestDetection,
        soilAnalysis,
        irrigationEngine,
        fieldIntelligence,
        astronomicalCalendar,
      ];

  /// Get service by name
  static KongService? getByName(String name) {
    try {
      return all.firstWhere((s) => s.name == name);
    } catch (_) {
      return null;
    }
  }
}

/// Kong Gateway Client
/// عميل بوابة Kong
class KongGatewayClient {
  static final KongGatewayClient _instance = KongGatewayClient._internal();
  factory KongGatewayClient() => _instance;
  KongGatewayClient._internal();

  late Dio _dio;
  late NetworkConfig _networkConfig;
  String? _accessToken;
  String? _refreshToken;
  String? _tenantId;
  NetworkConnectivityService? _connectivityService;

  // Circuit breaker state
  final Map<String, int> _failureCount = {};
  final Map<String, DateTime> _circuitOpenTime = {};
  static const int _failureThreshold = 3;
  static const Duration _circuitTimeout = Duration(seconds: 30);

  // Rate limit tracking
  int? _rateLimitRemaining;
  DateTime? _rateLimitReset;

  /// Initialize the client
  Future<void> initialize({
    NetworkConnectivityService? connectivityService,
    NetworkConfig? networkConfig,
  }) async {
    await EnvConfig.load();

    // Use centralized network configuration
    _networkConfig = networkConfig ?? NetworkConfig.fromEnvironment();
    _connectivityService = connectivityService;

    _dio = Dio(BaseOptions(
      baseUrl: EnvConfig.apiBaseUrl,
      connectTimeout: _networkConfig.connectTimeout,
      receiveTimeout: _networkConfig.receiveTimeout,
      sendTimeout: _networkConfig.sendTimeout,
      followRedirects: _networkConfig.followRedirects,
      maxRedirects: _networkConfig.maxRedirects,
      headers: _networkConfig.getDefaultHeaders(),
    ));

    // Configure TLS settings
    _configureTlsSettings();

    // Add connectivity monitoring interceptor
    if (_connectivityService != null) {
      _dio.interceptors.add(ConnectivityInterceptor(
        connectivityService: _connectivityService!,
        blockOfflineRequests: false,
      ));
    }

    // Add interceptors
    _dio.interceptors.add(_createAuthInterceptor());
    _dio.interceptors.add(_createRetryInterceptor());
    _dio.interceptors.add(_createLoggingInterceptor());

    if (kDebugMode) {
      AppLogger.i('KongGatewayClient initialized', tag: 'KongGateway', data: {
        'baseUrl': EnvConfig.apiBaseUrl,
        'connectTimeout': _networkConfig.connectTimeout.inSeconds,
        'sendTimeout': _networkConfig.sendTimeout.inSeconds,
        'receiveTimeout': _networkConfig.receiveTimeout.inSeconds,
      });
    }
  }

  /// Configure TLS settings for the HTTP client
  void _configureTlsSettings() {
    try {
      final adapter = _dio.httpClientAdapter;
      if (adapter is IOHttpClientAdapter) {
        adapter.createHttpClient = () {
          final client = HttpClient();
          client.idleTimeout = _networkConfig.keepAliveTimeout;
          client.maxConnectionsPerHost = _networkConfig.maxConnectionsPerHost;
          client.autoUncompress = true;
          return client;
        };
      }
    } catch (e) {
      AppLogger.e('Error configuring TLS settings',
          tag: 'KongGateway', error: e);
    }
  }

  /// Set authentication tokens
  void setTokens(
      {required String accessToken, String? refreshToken, String? tenantId}) {
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

  /// PATCH request - for partial updates
  /// طلب PATCH - للتحديثات الجزئية
  Future<ApiResponse<T>> patch<T>(
    KongService service,
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) async {
    return _request<T>(
      service: service,
      method: 'PATCH',
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // File Upload
  // رفع الملفات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Upload a single file
  /// رفع ملف واحد
  Future<ApiResponse<T>> uploadFile<T>(
    KongService service,
    String path, {
    required String filePath,
    String fieldName = 'file',
    Map<String, dynamic>? extraData,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    void Function(int sent, int total)? onProgress,
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
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(
          filePath,
          filename: filePath.split('/').last,
        ),
        ...?extraData,
      });

      final response = await _dio.post(
        url,
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          receiveTimeout:
              const Duration(seconds: 120), // Longer timeout for uploads
        ),
        cancelToken: cancelToken,
        onSendProgress: onProgress,
      );

      _resetCircuitBreaker(service.name);
      final requestId = response.headers.value('X-Request-Id');

      if (fromJson != null && response.data != null) {
        return ApiResponse.success(fromJson(response.data),
            requestId: requestId);
      }
      return ApiResponse.success(response.data as T, requestId: requestId);
    } on DioException catch (e) {
      _recordFailure(service.name);
      return _handleDioError<T>(e);
    } catch (e) {
      _recordFailure(service.name);
      return ApiResponse.error('UPLOAD_ERROR', e.toString(),
          messageAr: 'فشل في رفع الملف');
    }
  }

  /// Upload multiple files
  /// رفع ملفات متعددة
  Future<ApiResponse<T>> uploadMultipleFiles<T>(
    KongService service,
    String path, {
    required List<String> filePaths,
    String fieldName = 'files',
    Map<String, dynamic>? extraData,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    void Function(int sent, int total)? onProgress,
  }) async {
    if (_isCircuitOpen(service.name)) {
      return ApiResponse.error(
        'CIRCUIT_OPEN',
        'Service temporarily unavailable',
        messageAr: 'الخدمة غير متاحة مؤقتاً',
      );
    }

    final url = '${service.basePath}$path';

    try {
      final files = await Future.wait(
        filePaths.map((path) async => MultipartFile.fromFile(
              path,
              filename: path.split('/').last,
            )),
      );

      final formData = FormData.fromMap({
        fieldName: files,
        ...?extraData,
      });

      final response = await _dio.post(
        url,
        data: formData,
        options: Options(
          headers: {'Content-Type': 'multipart/form-data'},
          receiveTimeout:
              const Duration(seconds: 180), // Longer for multiple files
        ),
        cancelToken: cancelToken,
        onSendProgress: onProgress,
      );

      _resetCircuitBreaker(service.name);
      final requestId = response.headers.value('X-Request-Id');

      if (fromJson != null && response.data != null) {
        return ApiResponse.success(fromJson(response.data),
            requestId: requestId);
      }
      return ApiResponse.success(response.data as T, requestId: requestId);
    } on DioException catch (e) {
      _recordFailure(service.name);
      return _handleDioError<T>(e);
    } catch (e) {
      _recordFailure(service.name);
      return ApiResponse.error('UPLOAD_ERROR', e.toString(),
          messageAr: 'فشل في رفع الملفات');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cached Requests
  // الطلبات المخزنة مؤقتاً
  // ═══════════════════════════════════════════════════════════════════════════

  /// GET request with caching support
  /// طلب GET مع دعم التخزين المؤقت
  Future<ApiResponse<T>> getCached<T>(
    KongService service,
    String path, {
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    T Function(Map<String, dynamic>)? fromJsonMap,
    Duration cacheTtl = const Duration(minutes: 5),
    bool forceRefresh = false,
    CancelToken? cancelToken,
  }) async {
    final cacheKey = _buildCacheKey(service, path, queryParams);

    // Try to get from cache first (unless force refresh)
    if (!forceRefresh) {
      try {
        final cached = await NetworkCache.instance.get<dynamic>(
          cacheKey,
          fromJson: fromJsonMap,
        );
        if (cached != null) {
          if (kDebugMode) {
            AppLogger.d('Cache hit: $cacheKey', tag: 'KongGateway');
          }
          if (fromJson != null) {
            return ApiResponse.success(fromJson(cached));
          }
          return ApiResponse.success(cached as T);
        }
      } catch (e) {
        if (kDebugMode) {
          AppLogger.d('Cache miss or error: $cacheKey', tag: 'KongGateway');
        }
      }
    }

    // Make the actual request
    final response = await get<T>(
      service,
      path,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );

    // Cache the successful response
    if (response.success && response.data != null) {
      try {
        await NetworkCache.instance.set(cacheKey, response.data, ttl: cacheTtl);
      } catch (e) {
        if (kDebugMode) {
          AppLogger.w('Failed to cache response: $cacheKey',
              tag: 'KongGateway');
        }
      }
    }

    return response;
  }

  /// Invalidate cache for a specific service/path
  /// إبطال التخزين المؤقت لمسار معين
  Future<void> invalidateCache(KongService service, [String? path]) async {
    final pattern = path != null ? '${service.name}:$path' : service.name;
    await NetworkCache.instance.removePattern(pattern);
  }

  /// Clear all API cache
  /// مسح كل التخزين المؤقت
  Future<void> clearAllCache() async {
    await NetworkCache.instance.clear();
  }

  /// Build cache key from request parameters
  String _buildCacheKey(
      KongService service, String path, Map<String, dynamic>? queryParams) {
    final base = '${service.name}:$path';
    if (queryParams == null || queryParams.isEmpty) {
      return base;
    }
    final sortedParams = Map.fromEntries(
      queryParams.entries.toList()..sort((a, b) => a.key.compareTo(b.key)),
    );
    return '$base?${sortedParams.entries.map((e) => '${e.key}=${e.value}').join('&')}';
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Batch Requests
  // الطلبات المجمعة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Execute multiple requests in parallel
  /// تنفيذ طلبات متعددة بشكل متوازي
  Future<List<ApiResponse<dynamic>>> batch(List<BatchRequest> requests) async {
    final futures = requests.map((req) {
      switch (req.method.toUpperCase()) {
        case 'GET':
          return get(req.service, req.path,
              queryParams: req.queryParams, fromJson: req.fromJson);
        case 'POST':
          return post(req.service, req.path,
              data: req.data,
              queryParams: req.queryParams,
              fromJson: req.fromJson);
        case 'PUT':
          return put(req.service, req.path,
              data: req.data,
              queryParams: req.queryParams,
              fromJson: req.fromJson);
        case 'PATCH':
          return patch(req.service, req.path,
              data: req.data,
              queryParams: req.queryParams,
              fromJson: req.fromJson);
        case 'DELETE':
          return delete(req.service, req.path,
              queryParams: req.queryParams, fromJson: req.fromJson);
        default:
          return Future.value(ApiResponse<dynamic>.error(
              'INVALID_METHOD', 'Invalid HTTP method: ${req.method}'));
      }
    });

    return Future.wait(futures);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Conditional Requests (ETag support)
  // الطلبات الشرطية (دعم ETag)
  // ═══════════════════════════════════════════════════════════════════════════

  /// GET with ETag support for conditional requests
  /// طلب GET مع دعم ETag للطلبات الشرطية
  Future<ConditionalResponse<T>> getWithETag<T>(
    KongService service,
    String path, {
    String? etag,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) async {
    if (_isCircuitOpen(service.name)) {
      return ConditionalResponse(
        response: ApiResponse.error(
            'CIRCUIT_OPEN', 'Service temporarily unavailable',
            messageAr: 'الخدمة غير متاحة مؤقتاً'),
        notModified: false,
      );
    }

    final url = '${service.basePath}$path';

    try {
      final response = await _dio.get(
        url,
        queryParameters: queryParams,
        options: Options(
          headers: etag != null ? {'If-None-Match': etag} : null,
          validateStatus: (status) =>
              status != null && (status < 300 || status == 304),
        ),
        cancelToken: cancelToken,
      );

      _resetCircuitBreaker(service.name);

      if (response.statusCode == 304) {
        return ConditionalResponse(
          response: ApiResponse.success(null as T),
          notModified: true,
          etag: response.headers.value('ETag'),
        );
      }

      final requestId = response.headers.value('X-Request-Id');
      final newEtag = response.headers.value('ETag');

      T? data;
      if (fromJson != null && response.data != null) {
        data = fromJson(response.data);
      } else {
        data = response.data as T?;
      }

      return ConditionalResponse(
        response: ApiResponse.success(data as T, requestId: requestId),
        notModified: false,
        etag: newEtag,
      );
    } on DioException catch (e) {
      _recordFailure(service.name);
      return ConditionalResponse(
        response: _handleDioError<T>(e),
        notModified: false,
      );
    }
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
          status: latency > 2000
              ? ServiceHealthStatus.degraded
              : ServiceHealthStatus.healthy,
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
  // WebSocket Gateway
  // بوابة WebSocket
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get WebSocket gateway URL
  /// الحصول على عنوان بوابة WebSocket
  String get wsGatewayUrl => EnvConfig.wsGatewayUrl;

  /// Get WebSocket URL for a specific service
  /// الحصول على عنوان WebSocket لخدمة معينة
  String getWsUrl(KongService service) {
    return '${EnvConfig.wsGatewayUrl}${service.basePath}';
  }

  /// Get real-time socket URL for notifications
  /// عنوان الإشعارات الفورية
  String get notificationsWsUrl => '${EnvConfig.wsGatewayUrl}/ws/notifications';

  /// Get real-time socket URL for field updates
  /// عنوان تحديثات الحقول الفورية
  String get fieldUpdatesWsUrl => '${EnvConfig.wsGatewayUrl}/ws/fields';

  /// Get real-time socket URL for chat
  /// عنوان الدردشة الفورية
  String get chatWsUrl => '${EnvConfig.wsGatewayUrl}/ws/chat';

  // ═══════════════════════════════════════════════════════════════════════════
  // Connectivity & Network State
  // الاتصال وحالة الشبكة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if network is currently connected
  bool get isNetworkConnected => _connectivityService?.isConnected ?? true;

  /// Get current connectivity state
  NetworkConnectivityState? get networkState =>
      _connectivityService?.currentState;

  /// Check if the client can make requests
  /// (considers circuit breaker and connectivity)
  bool canMakeRequest(KongService service) {
    if (!isNetworkConnected) return false;
    if (_isCircuitOpen(service.name)) return false;
    return true;
  }

  /// Get circuit breaker status for a service
  Map<String, dynamic> getCircuitBreakerStatus(KongService service) {
    final isOpen = _isCircuitOpen(service.name);
    final failures = _failureCount[service.name] ?? 0;
    final openTime = _circuitOpenTime[service.name];

    return {
      'service': service.name,
      'isOpen': isOpen,
      'failureCount': failures,
      'openedAt': openTime?.toIso8601String(),
      'willResetAt': openTime?.add(_circuitTimeout).toIso8601String(),
    };
  }

  /// Reset circuit breaker for a specific service
  void resetServiceCircuitBreaker(KongService service) {
    _resetCircuitBreaker(service.name);
    if (kDebugMode) {
      AppLogger.d('Circuit breaker reset for ${service.name}',
          tag: 'KongGateway');
    }
  }

  /// Reset all circuit breakers
  void resetAllCircuitBreakers() {
    _failureCount.clear();
    _circuitOpenTime.clear();
    if (kDebugMode) {
      AppLogger.d('All circuit breakers reset', tag: 'KongGateway');
    }
  }

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
        return ApiResponse.success(fromJson(responseData),
            requestId: requestId);
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
      AppLogger.w('Circuit breaker opened for $serviceName',
          tag: 'KongGateway');
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

  /// Handle Dio errors with proper API response
  /// معالجة أخطاء Dio مع استجابة API مناسبة
  ApiResponse<T> _handleDioError<T>(DioException e) {
    final requestId = e.response?.headers.value('X-Request-Id');
    final statusCode = e.response?.statusCode;

    // Handle specific status codes
    if (statusCode != null) {
      switch (statusCode) {
        case 400:
          final errorData = e.response?.data;
          if (errorData is Map) {
            return ApiResponse.error(
              errorData['code']?.toString() ?? 'BAD_REQUEST',
              errorData['message']?.toString() ??
                  ApiErrorCodes.getMessageEn('BAD_REQUEST'),
              messageAr: errorData['message_ar']?.toString() ??
                  ApiErrorCodes.getMessageAr('BAD_REQUEST'),
              requestId: requestId,
            );
          }
          return ApiResponse.error(
            'BAD_REQUEST',
            ApiErrorCodes.getMessageEn('BAD_REQUEST'),
            messageAr: ApiErrorCodes.getMessageAr('BAD_REQUEST'),
            requestId: requestId,
          );
        case 401:
          return ApiResponse.error(
            'UNAUTHORIZED',
            ApiErrorCodes.getMessageEn('UNAUTHORIZED'),
            messageAr: ApiErrorCodes.getMessageAr('UNAUTHORIZED'),
            requestId: requestId,
          );
        case 403:
          return ApiResponse.error(
            'FORBIDDEN',
            ApiErrorCodes.getMessageEn('FORBIDDEN'),
            messageAr: ApiErrorCodes.getMessageAr('FORBIDDEN'),
            requestId: requestId,
          );
        case 404:
          return ApiResponse.error(
            'NOT_FOUND',
            ApiErrorCodes.getMessageEn('NOT_FOUND'),
            messageAr: ApiErrorCodes.getMessageAr('NOT_FOUND'),
            requestId: requestId,
          );
        case 409:
          return ApiResponse.error(
            'CONFLICT',
            ApiErrorCodes.getMessageEn('CONFLICT'),
            messageAr: ApiErrorCodes.getMessageAr('CONFLICT'),
            requestId: requestId,
          );
        case 422:
          final errorData = e.response?.data;
          if (errorData is Map) {
            return ApiResponse.error(
              errorData['code']?.toString() ?? 'VALIDATION_ERROR',
              errorData['message']?.toString() ??
                  ApiErrorCodes.getMessageEn('VALIDATION_ERROR'),
              messageAr: errorData['message_ar']?.toString() ??
                  ApiErrorCodes.getMessageAr('VALIDATION_ERROR'),
              requestId: requestId,
            );
          }
          return ApiResponse.error(
            'VALIDATION_ERROR',
            ApiErrorCodes.getMessageEn('VALIDATION_ERROR'),
            messageAr: ApiErrorCodes.getMessageAr('VALIDATION_ERROR'),
            requestId: requestId,
          );
        case 429:
          return ApiResponse.error(
            'RATE_LIMITED',
            ApiErrorCodes.getMessageEn('RATE_LIMITED'),
            messageAr: ApiErrorCodes.getMessageAr('RATE_LIMITED'),
            requestId: requestId,
          );
      }

      // Server errors (5xx)
      if (statusCode >= 500) {
        return ApiResponse.error(
          'SERVER_ERROR',
          ApiErrorCodes.getMessageEn('SERVER_ERROR'),
          messageAr: ApiErrorCodes.getMessageAr('SERVER_ERROR'),
          requestId: requestId,
        );
      }
    }

    // Handle Dio exception types
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiResponse.error(
          'TIMEOUT',
          ApiErrorCodes.getMessageEn('TIMEOUT'),
          messageAr: ApiErrorCodes.getMessageAr('TIMEOUT'),
          requestId: requestId,
        );
      case DioExceptionType.connectionError:
        return ApiResponse.error(
          'NO_CONNECTION',
          ApiErrorCodes.getMessageEn('NO_CONNECTION'),
          messageAr: ApiErrorCodes.getMessageAr('NO_CONNECTION'),
        );
      case DioExceptionType.cancel:
        return ApiResponse.error(
          'CANCELLED',
          'Request was cancelled',
          messageAr: 'تم إلغاء الطلب',
          requestId: requestId,
        );
      default:
        // Try to extract error from response data
        final errorData = e.response?.data;
        if (errorData is Map) {
          return ApiResponse.error(
            errorData['code']?.toString() ?? 'ERROR',
            errorData['message']?.toString() ?? e.message ?? 'Unknown error',
            messageAr: errorData['message_ar']?.toString() ??
                ApiErrorCodes.getMessageAr('UNKNOWN'),
            requestId: requestId,
          );
        }
        return ApiResponse.error(
          'UNKNOWN',
          e.message ?? ApiErrorCodes.getMessageEn('UNKNOWN'),
          messageAr: ApiErrorCodes.getMessageAr('UNKNOWN'),
          requestId: requestId,
        );
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
        final maxRetries =
            extra['maxRetries'] as int? ?? _networkConfig.maxRetries;
        final retryCount = extra['retryCount'] as int? ?? 0;

        if (_shouldRetry(error) && retryCount < maxRetries) {
          // Use network config's retry delay calculation
          final delay = _networkConfig.getRetryDelay(retryCount);

          if (kDebugMode) {
            AppLogger.d('Retrying request', tag: 'KongGateway', data: {
              'path': error.requestOptions.path,
              'attempt': retryCount + 1,
              'maxRetries': maxRetries,
              'delay': delay.inMilliseconds,
            });
          }

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
        final data = response.data;
        _accessToken = data['access_token'];
        _refreshToken = data['refresh_token'] ?? _refreshToken;
        return true;
      }
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'KongGateway', error: e);
    }

    return false;
  }
}

/// Batch request definition
/// تعريف طلب مجمع
class BatchRequest {
  final String method;
  final KongService service;
  final String path;
  final dynamic data;
  final Map<String, dynamic>? queryParams;
  final dynamic Function(dynamic)? fromJson;

  const BatchRequest({
    required this.method,
    required this.service,
    required this.path,
    this.data,
    this.queryParams,
    this.fromJson,
  });

  /// Create a GET batch request
  factory BatchRequest.get(
    KongService service,
    String path, {
    Map<String, dynamic>? queryParams,
    dynamic Function(dynamic)? fromJson,
  }) {
    return BatchRequest(
      method: 'GET',
      service: service,
      path: path,
      queryParams: queryParams,
      fromJson: fromJson,
    );
  }

  /// Create a POST batch request
  factory BatchRequest.post(
    KongService service,
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParams,
    dynamic Function(dynamic)? fromJson,
  }) {
    return BatchRequest(
      method: 'POST',
      service: service,
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
    );
  }
}

/// Conditional response wrapper (for ETag support)
/// غلاف الاستجابة الشرطية (لدعم ETag)
class ConditionalResponse<T> {
  final ApiResponse<T> response;
  final bool notModified;
  final String? etag;

  const ConditionalResponse({
    required this.response,
    required this.notModified,
    this.etag,
  });

  bool get success => response.success;
  T? get data => response.data;
}

/// API Error codes with bilingual messages
/// رموز أخطاء API مع رسائل ثنائية اللغة
class ApiErrorCodes {
  static const Map<String, Map<String, String>> errors = {
    'CIRCUIT_OPEN': {
      'en': 'Service temporarily unavailable',
      'ar': 'الخدمة غير متاحة مؤقتاً',
    },
    'RATE_LIMITED': {
      'en': 'Too many requests. Please wait.',
      'ar': 'طلبات كثيرة جداً. الرجاء الانتظار.',
    },
    'UNAUTHORIZED': {
      'en': 'Authentication required',
      'ar': 'المصادقة مطلوبة',
    },
    'FORBIDDEN': {
      'en': 'Access denied',
      'ar': 'الوصول مرفوض',
    },
    'NOT_FOUND': {
      'en': 'Resource not found',
      'ar': 'المورد غير موجود',
    },
    'TIMEOUT': {
      'en': 'Request timed out',
      'ar': 'انتهت مهلة الطلب',
    },
    'NO_CONNECTION': {
      'en': 'No internet connection',
      'ar': 'لا يوجد اتصال بالإنترنت',
    },
    'SERVER_ERROR': {
      'en': 'Server error occurred',
      'ar': 'حدث خطأ في الخادم',
    },
    'BAD_REQUEST': {
      'en': 'Invalid request',
      'ar': 'طلب غير صالح',
    },
    'CONFLICT': {
      'en': 'Resource conflict',
      'ar': 'تعارض في الموارد',
    },
    'VALIDATION_ERROR': {
      'en': 'Validation failed',
      'ar': 'فشل التحقق من الصحة',
    },
    'UPLOAD_ERROR': {
      'en': 'File upload failed',
      'ar': 'فشل رفع الملف',
    },
    'PARSE_ERROR': {
      'en': 'Failed to parse response',
      'ar': 'فشل في تحليل الاستجابة',
    },
    'UNKNOWN': {
      'en': 'An unexpected error occurred',
      'ar': 'حدث خطأ غير متوقع',
    },
  };

  static String getMessage(String code, {String locale = 'en'}) {
    return errors[code]?[locale] ?? errors['UNKNOWN']![locale]!;
  }

  static String getMessageAr(String code) => getMessage(code, locale: 'ar');
  static String getMessageEn(String code) => getMessage(code, locale: 'en');
}

/// Global Kong gateway client instance
final kongGateway = KongGatewayClient();
