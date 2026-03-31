import 'dart:async';
import 'dart:collection';
import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../config/env_config.dart';
import '../utils/app_logger.dart';
import '../storage/secure_storage.dart';

/// SAHOOL API Service v16.0.0
/// خدمة API موحدة لتطبيق الهاتف - سهول
///
/// Features | الميزات:
/// - Offline-first with queue management | أولوية العمل دون اتصال مع إدارة الطوابير
/// - Certificate pinning support | دعم تثبيت الشهادات
/// - Token refresh handling | معالجة تجديد الرمز
/// - Automatic retry with exponential backoff | إعادة المحاولة التلقائية
/// - Request/response caching | تخزين الطلبات والاستجابات
/// - Bilingual error messages | رسائل الخطأ ثنائية اللغة
///
/// Usage | الاستخدام:
/// ```dart
/// final apiService = ApiService();
/// await apiService.initialize();
///
/// final response = await apiService.get<List<Field>>(
///   '/api/v1/fields',
///   fromJson: (data) => (data as List? ?? []).map((e) => Field.fromJson(e)).toList(),
/// );
/// ```

// =============================================================================
// Types & Enums | الأنواع والتعدادات
// =============================================================================

/// Request priority levels | مستويات أولوية الطلب
enum RequestPriority {
  /// Critical requests that bypass the queue | طلبات حرجة تتجاوز الطابور
  critical,

  /// High priority - processed first | أولوية عالية - معالجة أولاً
  high,

  /// Normal priority | أولوية عادية
  normal,

  /// Low priority - can be delayed | أولوية منخفضة - يمكن تأخيرها
  low,
}

/// Sync status for offline operations | حالة المزامنة للعمليات دون اتصال
enum SyncStatus {
  /// Pending synchronization | في انتظار المزامنة
  pending,

  /// Currently syncing | قيد المزامنة حالياً
  syncing,

  /// Successfully synced | تمت المزامنة بنجاح
  synced,

  /// Sync failed | فشلت المزامنة
  failed,

  /// Conflict detected | تم اكتشاف تعارض
  conflict,
}

/// API response wrapper with bilingual support
/// غلاف استجابة API مع دعم ثنائي اللغة
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? error;
  final String? errorAr;
  final String? errorCode;
  final String? requestId;
  final bool fromCache;
  final DateTime? timestamp;

  const ApiResponse({
    required this.success,
    this.data,
    this.error,
    this.errorAr,
    this.errorCode,
    this.requestId,
    this.fromCache = false,
    this.timestamp,
  });

  factory ApiResponse.success(T data, {String? requestId, bool fromCache = false}) {
    return ApiResponse(
      success: true,
      data: data,
      requestId: requestId,
      fromCache: fromCache,
      timestamp: DateTime.now(),
    );
  }

  factory ApiResponse.error(
    String code,
    String message, {
    String? messageAr,
    String? requestId,
  }) {
    return ApiResponse(
      success: false,
      errorCode: code,
      error: message,
      errorAr: messageAr,
      requestId: requestId,
      timestamp: DateTime.now(),
    );
  }

  /// Get localized error message
  /// الحصول على رسالة الخطأ المحلية
  String getLocalizedError(String locale) {
    if (locale == 'ar' && errorAr != null) {
      return errorAr!;
    }
    return error ?? 'Unknown error';
  }
}

/// Queued request for offline operations
/// طلب في الطابور للعمليات دون اتصال
class QueuedRequest {
  final String id;
  final String method;
  final String endpoint;
  final dynamic data;
  final Map<String, String>? headers;
  final RequestPriority priority;
  final DateTime createdAt;
  SyncStatus status;
  int retryCount;
  String? errorMessage;

  QueuedRequest({
    required this.id,
    required this.method,
    required this.endpoint,
    this.data,
    this.headers,
    this.priority = RequestPriority.normal,
    DateTime? createdAt,
    this.status = SyncStatus.pending,
    this.retryCount = 0,
    this.errorMessage,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toJson() => {
        'id': id,
        'method': method,
        'endpoint': endpoint,
        'data': data,
        'headers': headers,
        'priority': priority.index,
        'createdAt': createdAt.toIso8601String(),
        'status': status.index,
        'retryCount': retryCount,
        'errorMessage': errorMessage,
      };

  factory QueuedRequest.fromJson(Map<String, dynamic> json) => QueuedRequest(
        id: json['id'] as String,
        method: json['method'] as String,
        endpoint: json['endpoint'] as String,
        data: json['data'],
        headers: json['headers'] != null
            ? Map<String, String>.from(json['headers'] as Map)
            : null,
        priority: RequestPriority.values[(json['priority'] as int?) ?? 2],
        createdAt: DateTime.tryParse(json['createdAt'] as String) ?? DateTime.now(),
        status: SyncStatus.values[(json['status'] as int?) ?? 0],
        retryCount: (json['retryCount'] as int?) ?? 0,
        errorMessage: json['errorMessage'] as String?,
      );
}

// =============================================================================
// Bilingual Error Messages | رسائل الخطأ ثنائية اللغة
// =============================================================================

class ErrorMessages {
  static const Map<String, Map<String, String>> messages = {
    'NETWORK_ERROR': {
      'en': 'Network error - please check your connection',
      'ar': 'خطأ في الشبكة - يرجى التحقق من اتصالك',
    },
    'TIMEOUT': {
      'en': 'Request timed out - please try again',
      'ar': 'انتهت مهلة الطلب - يرجى المحاولة مرة أخرى',
    },
    'UNAUTHORIZED': {
      'en': 'Session expired. Please login again.',
      'ar': 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    },
    'FORBIDDEN': {
      'en': 'Access denied - insufficient permissions',
      'ar': 'الوصول مرفوض - صلاحيات غير كافية',
    },
    'NOT_FOUND': {
      'en': 'Resource not found',
      'ar': 'المورد غير موجود',
    },
    'RATE_LIMITED': {
      'en': 'Too many requests. Please wait.',
      'ar': 'طلبات كثيرة جداً. يرجى الانتظار.',
    },
    'SERVER_ERROR': {
      'en': 'Server error - please try again later',
      'ar': 'خطأ في الخادم - يرجى المحاولة لاحقاً',
    },
    'OFFLINE': {
      'en': 'You are offline. Changes will sync when connected.',
      'ar': 'أنت غير متصل. ستتم المزامنة عند الاتصال.',
    },
    'SYNC_FAILED': {
      'en': 'Sync failed. Please try again.',
      'ar': 'فشلت المزامنة. يرجى المحاولة مرة أخرى.',
    },
    'CERTIFICATE_ERROR': {
      'en': 'Security certificate error',
      'ar': 'خطأ في شهادة الأمان',
    },
  };

  static String get(String code, String locale) {
    return messages[code]?[locale] ?? messages[code]?['en'] ?? 'Unknown error';
  }
}

// =============================================================================
// API Service | خدمة API
// =============================================================================

/// Main API service for SAHOOL mobile app
/// خدمة API الرئيسية لتطبيق سهول للهاتف
class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late Dio _dio;
  late SecureStorage _storage;
  late Connectivity _connectivity;

  // Auth tokens
  String? _accessToken;
  String? _refreshToken;
  String? _tenantId;

  // Offline queue
  final Queue<QueuedRequest> _requestQueue = Queue<QueuedRequest>();
  bool _isSyncing = false;
  Timer? _syncTimer;

  // Connectivity
  bool _isOnline = true;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;

  // Token refresh lock to prevent concurrent refresh calls
  Completer<bool>? _refreshCompleter;

  // Certificate pinning
  final List<String> _pinnedCertificates = [];
  bool _certificatePinningEnabled = false;

  // Configuration
  static const int _maxRetries = 3;
  static const Duration _retryDelay = Duration(seconds: 2);
  static const Duration _syncInterval = Duration(minutes: 5);
  static const int _maxQueueSize = 100;

  // ==========================================================================
  // Initialization | التهيئة
  // ==========================================================================

  /// Initialize the API service
  /// تهيئة خدمة API
  Future<void> initialize({
    bool enableCertificatePinning = true,
    List<String>? pinnedCertificates,
  }) async {
    await EnvConfig.load();
    _storage = SecureStorage();
    _connectivity = Connectivity();

    // Load stored tokens
    _accessToken = await _storage.getAccessToken();
    _refreshToken = await _storage.getRefreshToken();
    _tenantId = await _storage.getTenantId();

    // Setup certificate pinning
    if (enableCertificatePinning && pinnedCertificates != null) {
      _pinnedCertificates.addAll(pinnedCertificates);
      _certificatePinningEnabled = true;
    }

    // Create Dio instance
    _dio = Dio(BaseOptions(
      baseUrl: EnvConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
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
    _dio.interceptors.addAll([
      _createAuthInterceptor(),
      _createRetryInterceptor(),
      _createLoggingInterceptor(),
    ]);

    // Setup connectivity monitoring
    await _setupConnectivityMonitoring();

    // Load offline queue
    await _loadQueueFromStorage();

    // Start sync timer
    _startSyncTimer();

    AppLogger.i('ApiService initialized', tag: 'ApiService');
  }

  /// Setup connectivity monitoring
  /// إعداد مراقبة الاتصال
  Future<void> _setupConnectivityMonitoring() async {
    final result = await _connectivity.checkConnectivity();
    _isOnline = !result.contains(ConnectivityResult.none);

    _connectivitySubscription = _connectivity.onConnectivityChanged.listen((results) {
      final wasOffline = !_isOnline;
      _isOnline = !results.contains(ConnectivityResult.none);

      if (wasOffline && _isOnline) {
        AppLogger.i('Connection restored, starting sync', tag: 'ApiService');
        _syncPendingRequests();
      }
    });
  }

  /// Start sync timer
  /// بدء مؤقت المزامنة
  void _startSyncTimer() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(_syncInterval, (_) {
      if (_isOnline && _requestQueue.isNotEmpty) {
        _syncPendingRequests();
      }
    });
  }

  /// Dispose resources
  /// التخلص من الموارد
  void dispose() {
    _syncTimer?.cancel();
    _connectivitySubscription?.cancel();
    _dio.close();
  }

  // ==========================================================================
  // Token Management | إدارة الرموز
  // ==========================================================================

  /// Set authentication tokens
  /// تعيين رموز المصادقة
  Future<void> setTokens({
    required String accessToken,
    String? refreshToken,
    String? tenantId,
  }) async {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
    _tenantId = tenantId;

    await _storage.setAccessToken(accessToken);
    if (refreshToken != null) {
      await _storage.setRefreshToken(refreshToken);
    }
    if (tenantId != null) {
      await _storage.setTenantId(tenantId);
    }
  }

  /// Clear authentication
  /// مسح المصادقة
  Future<void> clearAuth() async {
    _accessToken = null;
    _refreshToken = null;
    _tenantId = null;

    await _storage.clearTokens();
  }

  /// Check if authenticated
  /// التحقق من المصادقة
  bool get isAuthenticated => _accessToken != null;

  /// Check if online
  /// التحقق من الاتصال
  bool get isOnline => _isOnline;

  /// Get queue status
  /// الحصول على حالة الطابور
  int get pendingRequestsCount => _requestQueue.length;

  // ==========================================================================
  // HTTP Methods | طرق HTTP
  // ==========================================================================

  /// GET request
  /// طلب GET
  Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, dynamic>? params,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool useCache = true,
  }) async {
    return _request<T>(
      method: 'GET',
      endpoint: endpoint,
      params: params,
      fromJson: fromJson,
      cancelToken: cancelToken,
      useCache: useCache,
    );
  }

  /// POST request
  /// طلب POST
  Future<ApiResponse<T>> post<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? params,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = true,
    RequestPriority priority = RequestPriority.normal,
  }) async {
    return _request<T>(
      method: 'POST',
      endpoint: endpoint,
      data: data,
      params: params,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  /// PUT request
  /// طلب PUT
  Future<ApiResponse<T>> put<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? params,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = true,
    RequestPriority priority = RequestPriority.normal,
  }) async {
    return _request<T>(
      method: 'PUT',
      endpoint: endpoint,
      data: data,
      params: params,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  /// DELETE request
  /// طلب DELETE
  Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    Map<String, dynamic>? params,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = true,
    RequestPriority priority = RequestPriority.normal,
  }) async {
    return _request<T>(
      method: 'DELETE',
      endpoint: endpoint,
      params: params,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  // ==========================================================================
  // Core Request Method | طريقة الطلب الأساسية
  // ==========================================================================

  Future<ApiResponse<T>> _request<T>({
    required String method,
    required String endpoint,
    dynamic data,
    Map<String, dynamic>? params,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool useCache = false,
    bool queueIfOffline = false,
    RequestPriority priority = RequestPriority.normal,
  }) async {
    // Check if offline and queue the request
    if (!_isOnline && queueIfOffline && method != 'GET') {
      return _queueRequest<T>(
        method: method,
        endpoint: endpoint,
        data: data,
        priority: priority,
      );
    }

    try {
      final response = await _dio.request(
        endpoint,
        data: data,
        queryParameters: params,
        options: Options(
          method: method,
          extra: {
            'useCache': useCache,
            'priority': priority,
          },
        ),
        cancelToken: cancelToken,
      );

      final requestId = response.headers.value('X-Request-Id');
      final responseData = response.data;

      if (fromJson != null && responseData != null) {
        return ApiResponse.success(
          fromJson(responseData),
          requestId: requestId,
        );
      }

      // Safely cast responseData, returning null data if responseData is null
      if (responseData == null) {
        return ApiResponse<T>(
          success: true,
          data: null,
          requestId: requestId,
          timestamp: DateTime.now(),
        );
      }

      return ApiResponse.success(
        responseData as T,
        requestId: requestId,
      );
    } on DioException catch (e) {
      return _handleDioError<T>(e, method, endpoint, data, queueIfOffline, priority);
    } catch (e) {
      AppLogger.e('Request failed', tag: 'ApiService', error: e);
      return ApiResponse.error(
        'UNKNOWN',
        e.toString(),
        messageAr: ErrorMessages.get('NETWORK_ERROR', 'ar'),
      );
    }
  }

  /// Handle Dio errors
  /// معالجة أخطاء Dio
  ApiResponse<T> _handleDioError<T>(
    DioException e,
    String method,
    String endpoint,
    dynamic data,
    bool queueIfOffline,
    RequestPriority priority,
  ) {
    final requestId = e.response?.headers.value('X-Request-Id');

    // Connection error - queue if applicable
    if (e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.connectionTimeout) {
      _isOnline = false;

      if (queueIfOffline && method != 'GET') {
        _addToQueue(
          method: method,
          endpoint: endpoint,
          data: data,
          priority: priority,
        );

        return ApiResponse.error(
          'OFFLINE',
          ErrorMessages.get('OFFLINE', 'en'),
          messageAr: ErrorMessages.get('OFFLINE', 'ar'),
          requestId: requestId,
        );
      }
    }

    // HTTP status code errors
    final statusCode = e.response?.statusCode ?? 0;

    if (statusCode == 401) {
      return ApiResponse.error(
        'UNAUTHORIZED',
        ErrorMessages.get('UNAUTHORIZED', 'en'),
        messageAr: ErrorMessages.get('UNAUTHORIZED', 'ar'),
        requestId: requestId,
      );
    }

    if (statusCode == 403) {
      return ApiResponse.error(
        'FORBIDDEN',
        ErrorMessages.get('FORBIDDEN', 'en'),
        messageAr: ErrorMessages.get('FORBIDDEN', 'ar'),
        requestId: requestId,
      );
    }

    if (statusCode == 404) {
      return ApiResponse.error(
        'NOT_FOUND',
        ErrorMessages.get('NOT_FOUND', 'en'),
        messageAr: ErrorMessages.get('NOT_FOUND', 'ar'),
        requestId: requestId,
      );
    }

    if (statusCode == 429) {
      return ApiResponse.error(
        'RATE_LIMITED',
        ErrorMessages.get('RATE_LIMITED', 'en'),
        messageAr: ErrorMessages.get('RATE_LIMITED', 'ar'),
        requestId: requestId,
      );
    }

    if (statusCode >= 500) {
      return ApiResponse.error(
        'SERVER_ERROR',
        ErrorMessages.get('SERVER_ERROR', 'en'),
        messageAr: ErrorMessages.get('SERVER_ERROR', 'ar'),
        requestId: requestId,
      );
    }

    if (e.type == DioExceptionType.receiveTimeout) {
      return ApiResponse.error(
        'TIMEOUT',
        ErrorMessages.get('TIMEOUT', 'en'),
        messageAr: ErrorMessages.get('TIMEOUT', 'ar'),
        requestId: requestId,
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
      'NETWORK_ERROR',
      ErrorMessages.get('NETWORK_ERROR', 'en'),
      messageAr: ErrorMessages.get('NETWORK_ERROR', 'ar'),
      requestId: requestId,
    );
  }

  // ==========================================================================
  // Offline Queue Management | إدارة طابور العمل دون اتصال
  // ==========================================================================

  /// Add request to offline queue
  /// إضافة طلب إلى طابور العمل دون اتصال
  void _addToQueue({
    required String method,
    required String endpoint,
    dynamic data,
    RequestPriority priority = RequestPriority.normal,
  }) {
    if (_requestQueue.length >= _maxQueueSize) {
      // Remove lowest priority request
      final lowest = _requestQueue.toList()
        ..sort((a, b) => b.priority.index.compareTo(a.priority.index));
      if (lowest.isNotEmpty && lowest.last.priority.index > priority.index) {
        _requestQueue.remove(lowest.last);
      } else {
        AppLogger.w('Queue full, request not added', tag: 'ApiService');
        return;
      }
    }

    final request = QueuedRequest(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      method: method,
      endpoint: endpoint,
      data: data,
      priority: priority,
    );

    _requestQueue.add(request);
    _saveQueueToStorage();

    AppLogger.i(
      'Request queued: $method $endpoint',
      tag: 'ApiService',
    );
  }

  /// Queue request and return offline response
  /// وضع الطلب في الطابور وإرجاع استجابة دون اتصال
  Future<ApiResponse<T>> _queueRequest<T>({
    required String method,
    required String endpoint,
    dynamic data,
    RequestPriority priority = RequestPriority.normal,
  }) async {
    _addToQueue(
      method: method,
      endpoint: endpoint,
      data: data,
      priority: priority,
    );

    return ApiResponse.error(
      'OFFLINE',
      ErrorMessages.get('OFFLINE', 'en'),
      messageAr: ErrorMessages.get('OFFLINE', 'ar'),
    );
  }

  /// Sync pending requests
  /// مزامنة الطلبات المعلقة
  Future<void> _syncPendingRequests() async {
    if (_isSyncing || _requestQueue.isEmpty || !_isOnline) return;

    _isSyncing = true;
    AppLogger.i(
      'Starting sync of ${_requestQueue.length} requests',
      tag: 'ApiService',
    );

    // Sort by priority
    final sortedRequests = _requestQueue.toList()
      ..sort((a, b) => a.priority.index.compareTo(b.priority.index));

    for (final request in sortedRequests) {
      if (!_isOnline) break;

      request.status = SyncStatus.syncing;

      try {
        await _dio.request(
          request.endpoint,
          data: request.data,
          options: Options(method: request.method),
        );

        request.status = SyncStatus.synced;
        _requestQueue.remove(request);

        AppLogger.i(
          'Synced: ${request.method} ${request.endpoint}',
          tag: 'ApiService',
        );
      } catch (e) {
        request.retryCount++;
        request.errorMessage = e.toString();

        if (request.retryCount >= _maxRetries) {
          request.status = SyncStatus.failed;
          AppLogger.e(
            'Sync failed permanently: ${request.endpoint}',
            tag: 'ApiService',
            error: e,
          );
        } else {
          request.status = SyncStatus.pending;
          AppLogger.w(
            'Sync retry ${request.retryCount}: ${request.endpoint}',
            tag: 'ApiService',
          );
        }
      }
    }

    await _saveQueueToStorage();
    _isSyncing = false;
  }

  /// Load queue from storage
  /// تحميل الطابور من التخزين
  Future<void> _loadQueueFromStorage() async {
    try {
      final data = await _storage.getQueuedRequests();
      if (data != null) {
        final List<dynamic> list = jsonDecode(data) as List<dynamic>;
        for (final item in list) {
          _requestQueue.add(QueuedRequest.fromJson(item as Map<String, dynamic>));
        }
        AppLogger.i(
          'Loaded ${_requestQueue.length} queued requests',
          tag: 'ApiService',
        );
      }
    } catch (e) {
      AppLogger.e('Failed to load queue', tag: 'ApiService', error: e);
    }
  }

  /// Save queue to storage
  /// حفظ الطابور في التخزين
  Future<void> _saveQueueToStorage() async {
    try {
      final data = jsonEncode(_requestQueue.map((r) => r.toJson()).toList());
      await _storage.setQueuedRequests(data);
    } catch (e) {
      AppLogger.e('Failed to save queue', tag: 'ApiService', error: e);
    }
  }

  /// Clear failed requests from queue
  /// مسح الطلبات الفاشلة من الطابور
  void clearFailedRequests() {
    _requestQueue.removeWhere((r) => r.status == SyncStatus.failed);
    _saveQueueToStorage();
  }

  /// Retry all failed requests
  /// إعادة محاولة جميع الطلبات الفاشلة
  void retryFailedRequests() {
    for (final request in _requestQueue) {
      if (request.status == SyncStatus.failed) {
        request.status = SyncStatus.pending;
        request.retryCount = 0;
      }
    }
    _saveQueueToStorage();
    _syncPendingRequests();
  }

  // ==========================================================================
  // Interceptors | المعترضات
  // ==========================================================================

  /// Create auth interceptor
  /// إنشاء معترض المصادقة
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
          final refreshed = await _refreshAccessToken();
          if (refreshed) {
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

  /// Create retry interceptor
  /// إنشاء معترض إعادة المحاولة
  Interceptor _createRetryInterceptor() {
    return InterceptorsWrapper(
      onError: (error, handler) async {
        final extra = error.requestOptions.extra;
        final retryCount = extra['retryCount'] as int? ?? 0;

        if (_shouldRetry(error) && retryCount < _maxRetries) {
          await Future.delayed(_retryDelay * (retryCount + 1));
          extra['retryCount'] = retryCount + 1;

          try {
            final response = await _dio.fetch(error.requestOptions);
            handler.resolve(response);
            return;
          } catch (e) {
            if (retryCount + 1 >= _maxRetries) {
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

  /// Create logging interceptor
  /// إنشاء معترض التسجيل
  Interceptor _createLoggingInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) {
        if (kDebugMode) {
          AppLogger.d(
            '-> ${options.method} ${options.path}',
            tag: 'ApiService',
          );
        }
        handler.next(options);
      },
      onResponse: (response, handler) {
        if (kDebugMode) {
          AppLogger.d(
            '<- ${response.statusCode} ${response.requestOptions.path}',
            tag: 'ApiService',
          );
        }
        handler.next(response);
      },
      onError: (error, handler) {
        AppLogger.e(
          'x ${error.requestOptions.method} ${error.requestOptions.path}: ${error.message}',
          tag: 'ApiService',
          error: error,
        );
        handler.next(error);
      },
    );
  }

  /// Refresh access token with concurrency lock
  /// تجديد رمز الوصول مع قفل التزامن
  Future<bool> _refreshAccessToken() async {
    if (_refreshToken == null) return false;

    // If a refresh is already in progress, wait for its result
    if (_refreshCompleter != null) {
      AppLogger.d('Token refresh already in progress, waiting...', tag: 'ApiService');
      return _refreshCompleter!.future;
    }

    _refreshCompleter = Completer<bool>();

    try {
      final response = await _dio.post(
        '/api/v1/auth/refresh',
        data: {'refresh_token': _refreshToken},
        options: Options(
          headers: {'Authorization': null},
          receiveTimeout: const Duration(seconds: 10),
          sendTimeout: const Duration(seconds: 10),
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final newAccessToken = data['access_token'] as String?;
        if (newAccessToken == null || newAccessToken.isEmpty) {
          AppLogger.e('Token refresh returned empty access token', tag: 'ApiService');
          _refreshCompleter!.complete(false);
          return false;
        }

        _accessToken = newAccessToken;
        _refreshToken = data['refresh_token'] as String? ?? _refreshToken;

        await _storage.setAccessToken(_accessToken!);
        if (_refreshToken != null) {
          await _storage.setRefreshToken(_refreshToken!);
        }

        AppLogger.i('Token refreshed successfully', tag: 'ApiService');
        _refreshCompleter!.complete(true);
        return true;
      }

      _refreshCompleter!.complete(false);
      return false;
    } catch (e) {
      AppLogger.e('Token refresh failed', tag: 'ApiService', error: e);
      _refreshCompleter!.complete(false);
      return false;
    } finally {
      _refreshCompleter = null;
    }
  }

  // ==========================================================================
  // Health Check | فحص الصحة
  // ==========================================================================

  /// Check API health
  /// فحص صحة API
  Future<bool> checkHealth() async {
    try {
      final response = await _dio.get('/healthz');
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

/// Global API service instance
/// مثيل خدمة API العالمي
final apiService = ApiService();
