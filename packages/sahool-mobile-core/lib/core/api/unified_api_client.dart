import 'dart:async';
import 'dart:collection';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import '../config/env_config.dart';
import '../contracts/service_ports.dart';
import '../contracts/api_endpoints.dart';
import '../contracts/error_codes.dart';
import '../http/api_client.dart';
import '../utils/app_logger.dart';
import 'api_service.dart';
import 'kong_gateway_client.dart';

// =============================================================================
// SAHOOL Unified API Client v16.0.0
// عميل API الموحد لمنصة سهول
//
// Provides a single entry point for all service communication.
// يوفر نقطة دخول واحدة لجميع اتصالات الخدمات.
//
// Features | الميزات:
// - Typed service accessors (fieldService, weatherService, etc.)
//   موصّلات خدمات مصنّفة (خدمة الحقول، خدمة الطقس، إلخ)
// - Offline queue with priority-based processing
//   طابور العمل دون اتصال مع معالجة حسب الأولوية
// - Retry with exponential backoff and circuit breaker
//   إعادة المحاولة مع تأخير متصاعد وقاطع دارة
// - Kong Gateway routing via SERVICE_PORTS contracts
//   التوجيه عبر بوابة Kong باستخدام عقود منافذ الخدمات
// - Certificate pinning and request signing
//   تثبيت الشهادات وتوقيع الطلبات
// - Bilingual error messages (Arabic/English)
//   رسائل خطأ ثنائية اللغة (عربي/إنجليزي)
// =============================================================================

// =============================================================================
// Unified Response | الاستجابة الموحدة
// =============================================================================

/// Unified API response wrapping all service calls.
/// استجابة API موحدة تغلف جميع استدعاءات الخدمات.
class UnifiedApiResponse<T> {
  final bool success;
  final T? data;
  final String? errorCode;
  final String? errorMessage;
  final String? errorMessageAr;
  final String? requestId;
  final bool fromCache;
  final bool queued;
  final DateTime timestamp;

  const UnifiedApiResponse({
    required this.success,
    this.data,
    this.errorCode,
    this.errorMessage,
    this.errorMessageAr,
    this.requestId,
    this.fromCache = false,
    this.queued = false,
    required this.timestamp,
  });

  factory UnifiedApiResponse.success(
    T data, {
    String? requestId,
    bool fromCache = false,
  }) {
    return UnifiedApiResponse(
      success: true,
      data: data,
      requestId: requestId,
      fromCache: fromCache,
      timestamp: DateTime.now(),
    );
  }

  factory UnifiedApiResponse.error(
    String code, {
    String? requestId,
  }) {
    final msg = getErrorMessage(code);
    return UnifiedApiResponse(
      success: false,
      errorCode: code,
      errorMessage: msg.en,
      errorMessageAr: msg.ar,
      requestId: requestId,
      timestamp: DateTime.now(),
    );
  }

  factory UnifiedApiResponse.queued() {
    final msg = getErrorMessage(ErrorCodes.offline);
    return UnifiedApiResponse(
      success: false,
      errorCode: ErrorCodes.offline,
      errorMessage: msg.en,
      errorMessageAr: msg.ar,
      queued: true,
      timestamp: DateTime.now(),
    );
  }

  /// Get localized error message.
  /// الحصول على رسالة الخطأ بالعربية أو الإنجليزية.
  String getLocalizedError({String locale = 'ar'}) {
    if (locale == 'ar' && errorMessageAr != null) return errorMessageAr!;
    return errorMessage ?? 'Unknown error';
  }
}

// =============================================================================
// Service Proxy | وكيل الخدمة
// =============================================================================

/// Typed proxy for a single backend service.
/// وكيل مصنّف لخدمة خلفية واحدة.
///
/// All requests are routed through the Kong API gateway.
/// جميع الطلبات يتم توجيهها عبر بوابة Kong.
class ServiceProxy {
  final SahoolApiClient _client;
  final KongService _service;

  const ServiceProxy(this._client, this._service);

  /// Service name (English).
  String get name => _service.name;

  /// Service name (Arabic).
  String get nameAr => _service.nameAr;

  /// GET request at [path] relative to service base path.
  /// طلب GET على [path] نسبة إلى مسار الخدمة الأساسي.
  Future<UnifiedApiResponse<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) {
    return _client._serviceRequest<T>(
      service: _service,
      method: 'GET',
      path: path,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );
  }

  /// POST request.
  /// طلب POST.
  Future<UnifiedApiResponse<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = true,
    RequestPriority priority = RequestPriority.normal,
  }) {
    return _client._serviceRequest<T>(
      service: _service,
      method: 'POST',
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  /// PUT request.
  /// طلب PUT.
  Future<UnifiedApiResponse<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = true,
    RequestPriority priority = RequestPriority.normal,
  }) {
    return _client._serviceRequest<T>(
      service: _service,
      method: 'PUT',
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  /// DELETE request.
  /// طلب DELETE.
  Future<UnifiedApiResponse<T>> delete<T>(
    String path, {
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = true,
    RequestPriority priority = RequestPriority.normal,
  }) {
    return _client._serviceRequest<T>(
      service: _service,
      method: 'DELETE',
      path: path,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  /// PATCH request.
  /// طلب PATCH.
  Future<UnifiedApiResponse<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = true,
    RequestPriority priority = RequestPriority.normal,
  }) {
    return _client._serviceRequest<T>(
      service: _service,
      method: 'PATCH',
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  /// Check service health.
  /// فحص صحة الخدمة.
  Future<ServiceHealth> checkHealth() =>
      _client._gateway.checkHealth(_service);
}

// =============================================================================
// Offline Queue Entry | سجل طابور العمل دون اتصال
// =============================================================================

/// A single offline-queued request.
/// طلب واحد في طابور العمل دون اتصال.
class _OfflineEntry {
  final String id;
  final String serviceName;
  final String method;
  final String url;
  final dynamic data;
  final Map<String, dynamic>? queryParams;
  final RequestPriority priority;
  final DateTime createdAt;
  int retryCount;

  _OfflineEntry({
    required this.id,
    required this.serviceName,
    required this.method,
    required this.url,
    this.data,
    this.queryParams,
    this.priority = RequestPriority.normal,
    this.retryCount = 0,
  }) : createdAt = DateTime.now();

  Map<String, dynamic> toJson() => {
        'id': id,
        'serviceName': serviceName,
        'method': method,
        'url': url,
        'data': data,
        'queryParams': queryParams,
        'priority': priority.index,
        'createdAt': createdAt.toIso8601String(),
        'retryCount': retryCount,
      };

  factory _OfflineEntry.fromJson(Map<String, dynamic> json) => _OfflineEntry(
        id: json['id'] as String,
        serviceName: json['serviceName'] as String,
        method: json['method'] as String,
        url: json['url'] as String,
        data: json['data'],
        queryParams: json['queryParams'] != null
            ? Map<String, dynamic>.from(json['queryParams'] as Map)
            : null,
        priority: RequestPriority.values[(json['priority'] as int?) ?? 2],
        retryCount: (json['retryCount'] as int?) ?? 0,
      );
}

// =============================================================================
// SahoolApiClient | عميل سهول الموحد
// =============================================================================

/// Unified API client for the SAHOOL mobile platform.
/// عميل API الموحد لمنصة سهول للهاتف.
///
/// This class aggregates [KongGatewayClient], [ApiClient], and [ApiService]
/// into a single facade with typed service proxies, offline queue, and retry.
///
/// يجمع هذا الفئة [KongGatewayClient] و [ApiClient] و [ApiService]
/// في واجهة واحدة مع وكلاء خدمات مصنّفين وطابور دون اتصال وإعادة محاولة.
///
/// ```dart
/// // Via Riverpod provider
/// final client = ref.watch(sahoolApiClientProvider);
/// final fields = await client.fieldService.get(
///   '/nearby',
///   queryParams: {'lat': 24.7, 'lon': 46.7},
///   fromJson: (data) => (data as List).map((e) => Field.fromJson(e)).toList(),
/// );
/// ```
class SahoolApiClient {
  final KongGatewayClient _gateway;
  final ApiClient _httpClient;
  final Connectivity _connectivity;

  // Offline queue | طابور العمل دون اتصال
  final Queue<_OfflineEntry> _offlineQueue = Queue<_OfflineEntry>();
  bool _isSyncing = false;
  Timer? _syncTimer;
  bool _isOnline = true;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySub;

  // Configuration | الإعدادات
  static const int _maxRetries = 3;
  static const int _maxQueueSize = 200;
  static const Duration _syncInterval = Duration(minutes: 5);
  static const Duration _baseRetryDelay = Duration(seconds: 1);

  // ═══════════════════════════════════════════════════════════════════════════
  // Constructor | المُنشئ
  // ═══════════════════════════════════════════════════════════════════════════

  SahoolApiClient({
    KongGatewayClient? gateway,
    ApiClient? httpClient,
    Connectivity? connectivity,
  })  : _gateway = gateway ?? KongGatewayClient(),
        _httpClient = httpClient ?? ApiClient(),
        _connectivity = connectivity ?? Connectivity();

  // ═══════════════════════════════════════════════════════════════════════════
  // Lifecycle | دورة الحياة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the client (must call before using).
  /// تهيئة العميل (يجب الاستدعاء قبل الاستخدام).
  Future<void> initialize() async {
    await _gateway.initialize();

    // Check initial connectivity | فحص الاتصال الأولي
    final result = await _connectivity.checkConnectivity();
    _isOnline = !result.contains(ConnectivityResult.none);

    // Listen for connectivity changes | الاستماع لتغيرات الاتصال
    _connectivitySub = _connectivity.onConnectivityChanged.listen((results) {
      final wasOffline = !_isOnline;
      _isOnline = !results.contains(ConnectivityResult.none);

      if (wasOffline && _isOnline) {
        AppLogger.i(
          'Connection restored - processing offline queue',
          tag: 'SahoolApiClient',
        );
        // استعادة الاتصال - معالجة الطابور
        processOfflineQueue();
      }
    });

    // Periodic sync timer | مؤقت المزامنة الدورية
    _syncTimer = Timer.periodic(_syncInterval, (_) {
      if (_isOnline && _offlineQueue.isNotEmpty) {
        processOfflineQueue();
      }
    });

    AppLogger.i('SahoolApiClient initialized', tag: 'SahoolApiClient');
  }

  /// Release resources.
  /// تحرير الموارد.
  void dispose() {
    _syncTimer?.cancel();
    _connectivitySub?.cancel();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Service Proxies | وكلاء الخدمات
  //
  // Each getter returns a ServiceProxy routed through Kong.
  // كل موصّل يُرجع وكيل خدمة يمر عبر بوابة Kong.
  // ═══════════════════════════════════════════════════════════════════════════

  /// Field Management Service (port: 3000) | خدمة إدارة الحقول
  ServiceProxy get fieldService => ServiceProxy(this, KongServices.fields);

  /// Authentication & User Service (port: 3025) | خدمة المصادقة والمستخدمين
  ServiceProxy get authService => ServiceProxy(this, KongServices.auth);

  /// Weather Service (port: 8092) | خدمة الطقس
  ServiceProxy get weatherService => ServiceProxy(this, KongServices.weather);

  /// Vegetation Analysis / NDVI (port: 8090) | تحليل الغطاء النباتي
  ServiceProxy get vegetationService =>
      ServiceProxy(this, KongServices.vegetation);

  /// Irrigation Smart Service (port: 8094) | خدمة الري الذكي
  ServiceProxy get irrigationService =>
      ServiceProxy(this, KongServices.irrigation);

  /// Advisory Service (port: 8093) | خدمة الاستشارات
  ServiceProxy get advisoryService => ServiceProxy(this, KongServices.advisory);

  /// Crop Intelligence / Health (port: 8095) | صحة المحاصيل
  ServiceProxy get cropHealthService =>
      ServiceProxy(this, KongServices.cropHealth);

  /// Task Service (port: 8103) | خدمة المهام
  ServiceProxy get taskService => ServiceProxy(this, KongServices.tasks);

  /// Equipment Service (port: 8101) | خدمة المعدات
  ServiceProxy get equipmentService =>
      ServiceProxy(this, KongServices.equipment);

  /// Alert Service (port: 8113) | خدمة التنبيهات
  ServiceProxy get alertService => ServiceProxy(this, KongServices.alerts);

  /// Notification Service (port: 8110) | خدمة الإشعارات
  ServiceProxy get notificationService =>
      ServiceProxy(this, KongServices.notifications);

  /// Marketplace Service (port: 3010) | خدمة السوق
  ServiceProxy get marketplaceService =>
      ServiceProxy(this, KongServices.marketplace);

  /// IoT Service (port: 8117) | خدمة إنترنت الأشياء
  ServiceProxy get iotService => ServiceProxy(this, KongServices.iot);

  /// Billing Service (port: 8089) | خدمة الفوترة
  ServiceProxy get billingService => ServiceProxy(this, KongServices.billing);

  /// Chat Service (port: 8115) | خدمة الدردشة
  ServiceProxy get chatService => ServiceProxy(this, KongServices.community);

  /// AI Copilot / Advisor (port: 8088) | المستشار الذكي
  ServiceProxy get aiService => ServiceProxy(this, KongServices.ai);

  /// CRM Service (port: 8131) | خدمة إدارة المزارعين
  ServiceProxy get crmService => ServiceProxy(this, KongServices.crm);

  /// YOLO26 Vision Service (port: 8150) | خدمة الرؤية الحاسوبية
  ServiceProxy get visionService => ServiceProxy(this, KongServices.vision);

  /// Satellite / NDVI legacy (port: varies) | خدمة الأقمار الصناعية
  ServiceProxy get satelliteService =>
      ServiceProxy(this, KongServices.satellite);

  /// Yield Prediction (port: varies) | التنبؤ بالإنتاج
  ServiceProxy get yieldService => ServiceProxy(this, KongServices.yield_);

  // ═══════════════════════════════════════════════════════════════════════════
  // Auth Delegation | تفويض المصادقة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set authentication tokens on all underlying clients.
  /// تعيين رموز المصادقة على جميع العملاء الأساسيين.
  void setTokens({
    required String accessToken,
    String? refreshToken,
    String? tenantId,
  }) {
    _gateway.setTokens(
      accessToken: accessToken,
      refreshToken: refreshToken,
      tenantId: tenantId,
    );
    _httpClient.setAuthToken(accessToken);
    if (tenantId != null) _httpClient.setTenantId(tenantId);
  }

  /// Clear authentication from all underlying clients.
  /// مسح المصادقة من جميع العملاء الأساسيين.
  void clearAuth() {
    _gateway.clearAuth();
    _httpClient.setAuthToken('');
  }

  /// Whether the user is currently authenticated.
  /// هل المستخدم مصادق حالياً.
  bool get isAuthenticated => _gateway.isAuthenticated;

  // ═══════════════════════════════════════════════════════════════════════════
  // Connectivity & Queue Status | حالة الاتصال والطابور
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether the device has network connectivity.
  /// هل الجهاز متصل بالشبكة.
  bool get isOnline => _isOnline;

  /// Number of requests waiting in the offline queue.
  /// عدد الطلبات المعلقة في طابور العمل دون اتصال.
  int get pendingQueueCount => _offlineQueue.length;

  /// Whether the offline queue is currently being processed.
  /// هل يتم حالياً معالجة طابور العمل دون اتصال.
  bool get isSyncing => _isSyncing;

  /// Rate limit info from the gateway.
  /// معلومات حد المعدل من البوابة.
  Map<String, dynamic> get rateLimitInfo => _gateway.rateLimitInfo;

  /// Underlying HTTP client for advanced use cases.
  /// عميل HTTP الأساسي للاستخدامات المتقدمة.
  ApiClient get httpClient => _httpClient;

  /// Underlying Kong gateway client.
  /// عميل بوابة Kong الأساسي.
  KongGatewayClient get gateway => _gateway;

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Checks | فحص الصحة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check health of all services via Kong.
  /// فحص صحة جميع الخدمات عبر بوابة Kong.
  Future<List<ServiceHealth>> checkAllServicesHealth() =>
      _gateway.checkAllServicesHealth();

  /// Check health of a specific service.
  /// فحص صحة خدمة محددة.
  Future<ServiceHealth> checkServiceHealth(KongService service) =>
      _gateway.checkHealth(service);

  /// Quick liveness check via the gateway.
  /// فحص سريع عبر البوابة.
  Future<bool> checkGatewayHealth() async {
    try {
      final response = await _httpClient.get(HealthEndpoints.liveness);
      return response != null;
    } catch (_) {
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Core Request Engine | محرك الطلبات الأساسي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Internal: execute a service-scoped request with retry and offline queue.
  /// داخلي: تنفيذ طلب محدود بخدمة مع إعادة المحاولة وطابور العمل.
  Future<UnifiedApiResponse<T>> _serviceRequest<T>({
    required KongService service,
    required String method,
    required String path,
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = false,
    RequestPriority priority = RequestPriority.normal,
  }) async {
    // Offline: queue mutating requests | دون اتصال: وضع الطلبات المُعدّلة في الطابور
    if (!_isOnline && queueIfOffline && method != 'GET') {
      _enqueue(
        serviceName: service.name,
        method: method,
        url: '${service.basePath}$path',
        data: data,
        queryParams: queryParams,
        priority: priority,
      );
      return UnifiedApiResponse<T>.queued();
    }

    // Delegate to KongGatewayClient which handles circuit breaker and retry
    // التفويض إلى KongGatewayClient الذي يتعامل مع قاطع الدارة وإعادة المحاولة
    final kongResponse = await _gateway.request<T>(
      service: service,
      method: method,
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
    );

    if (kongResponse.success) {
      return UnifiedApiResponse<T>.success(
        kongResponse.data as T,
        requestId: kongResponse.requestId,
      );
    }

    // On connection failure, optionally queue | عند فشل الاتصال، يمكن وضعها في الطابور
    if (_isConnectionError(kongResponse.errorCode) &&
        queueIfOffline &&
        method != 'GET') {
      _enqueue(
        serviceName: service.name,
        method: method,
        url: '${service.basePath}$path',
        data: data,
        queryParams: queryParams,
        priority: priority,
      );
      return UnifiedApiResponse<T>.queued();
    }

    return UnifiedApiResponse<T>(
      success: false,
      errorCode: kongResponse.errorCode,
      errorMessage: kongResponse.errorMessage,
      errorMessageAr: kongResponse.errorMessageAr,
      requestId: kongResponse.requestId,
      timestamp: DateTime.now(),
    );
  }

  /// Fallback request method that directly uses the Kong gateway's typed API.
  /// طريقة طلب بديلة تستخدم API بوابة Kong المصنّف مباشرة.
  Future<UnifiedApiResponse<T>> request<T>({
    required KongService service,
    required String method,
    required String path,
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
    bool queueIfOffline = false,
    RequestPriority priority = RequestPriority.normal,
  }) {
    return _serviceRequest<T>(
      service: service,
      method: method,
      path: path,
      data: data,
      queryParams: queryParams,
      fromJson: fromJson,
      cancelToken: cancelToken,
      queueIfOffline: queueIfOffline,
      priority: priority,
    );
  }

  bool _isConnectionError(String? code) {
    return code == ErrorCodes.networkError ||
        code == ErrorCodes.timeout ||
        code == 'NO_CONNECTION' ||
        code == ErrorCodes.offline;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Offline Queue | طابور العمل دون اتصال
  // ═══════════════════════════════════════════════════════════════════════════

  /// Enqueue a request for later processing.
  /// وضع طلب في الطابور للمعالجة لاحقاً.
  void _enqueue({
    required String serviceName,
    required String method,
    required String url,
    dynamic data,
    Map<String, dynamic>? queryParams,
    RequestPriority priority = RequestPriority.normal,
  }) {
    if (_offlineQueue.length >= _maxQueueSize) {
      // Evict lowest priority entry | إزالة سجل بأقل أولوية
      final sorted = _offlineQueue.toList()
        ..sort((a, b) => b.priority.index.compareTo(a.priority.index));
      if (sorted.isNotEmpty &&
          sorted.last.priority.index > priority.index) {
        _offlineQueue.remove(sorted.last);
      } else {
        AppLogger.w(
          'Offline queue full ($_maxQueueSize), dropping request: $method $url',
          tag: 'SahoolApiClient',
        );
        // الطابور ممتلئ، تجاهل الطلب
        return;
      }
    }

    _offlineQueue.add(_OfflineEntry(
      id: '${DateTime.now().millisecondsSinceEpoch}_${_offlineQueue.length}',
      serviceName: serviceName,
      method: method,
      url: url,
      data: data,
      queryParams: queryParams,
      priority: priority,
    ));

    AppLogger.i(
      'Queued offline: $method $url (queue: ${_offlineQueue.length})',
      tag: 'SahoolApiClient',
    );
    // تم وضع الطلب في الطابور
  }

  /// Process all queued offline requests with exponential backoff.
  /// معالجة جميع الطلبات المعلقة مع تأخير متصاعد.
  Future<void> processOfflineQueue() async {
    if (_isSyncing || _offlineQueue.isEmpty || !_isOnline) return;

    _isSyncing = true;
    AppLogger.i(
      'Processing offline queue (${_offlineQueue.length} requests)',
      tag: 'SahoolApiClient',
    );
    // بدء معالجة الطابور

    // Sort by priority (critical first) | ترتيب حسب الأولوية (الحرجة أولاً)
    final sorted = _offlineQueue.toList()
      ..sort((a, b) => a.priority.index.compareTo(b.priority.index));

    for (final entry in sorted) {
      if (!_isOnline) break;

      bool success = false;
      for (int attempt = 0; attempt <= _maxRetries; attempt++) {
        if (attempt > 0) {
          // Exponential backoff: 1s, 2s, 4s | تأخير متصاعد
          final delay = _baseRetryDelay * (1 << (attempt - 1));
          await Future.delayed(delay);
        }

        try {
          await _httpClient.dio.request(
            entry.url,
            data: entry.data,
            queryParameters: entry.queryParams,
            options: Options(method: entry.method),
          );
          success = true;
          break;
        } catch (e) {
          entry.retryCount++;
          if (kDebugMode) {
            AppLogger.w(
              'Queue retry ${entry.retryCount}: ${entry.method} ${entry.url}',
              tag: 'SahoolApiClient',
            );
          }
        }
      }

      if (success) {
        _offlineQueue.remove(entry);
        AppLogger.i(
          'Queue sync OK: ${entry.method} ${entry.url}',
          tag: 'SahoolApiClient',
        );
        // تمت مزامنة الطلب بنجاح
      } else {
        AppLogger.e(
          'Queue sync FAILED: ${entry.method} ${entry.url}',
          tag: 'SahoolApiClient',
        );
        // فشلت مزامنة الطلب
      }
    }

    _isSyncing = false;
  }

  /// Discard all failed entries from the offline queue.
  /// حذف جميع السجلات الفاشلة من الطابور.
  void clearFailedEntries() {
    _offlineQueue.removeWhere((e) => e.retryCount >= _maxRetries);
  }

  /// Clear the entire offline queue.
  /// مسح طابور العمل بالكامل.
  void clearQueue() {
    _offlineQueue.clear();
  }
}

// =============================================================================
// KongGatewayClient extension: typed request method
// امتداد KongGatewayClient: طريقة طلب مصنّفة
// =============================================================================

/// Extension adding a generic [request] method to [KongGatewayClient].
extension KongGatewayRequestExtension on KongGatewayClient {
  /// Execute a typed request via the Kong gateway.
  /// تنفيذ طلب مصنّف عبر بوابة Kong.
  Future<ApiResponse<T>> request<T>({
    required KongService service,
    required String method,
    required String path,
    dynamic data,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    CancelToken? cancelToken,
  }) {
    switch (method.toUpperCase()) {
      case 'GET':
        return get<T>(service, path,
            queryParams: queryParams,
            fromJson: fromJson,
            cancelToken: cancelToken);
      case 'POST':
        return post<T>(service, path,
            data: data,
            queryParams: queryParams,
            fromJson: fromJson,
            cancelToken: cancelToken);
      case 'PUT':
        return put<T>(service, path,
            data: data,
            queryParams: queryParams,
            fromJson: fromJson,
            cancelToken: cancelToken);
      case 'DELETE':
        return delete<T>(service, path,
            queryParams: queryParams,
            fromJson: fromJson,
            cancelToken: cancelToken);
      default:
        return get<T>(service, path,
            queryParams: queryParams,
            fromJson: fromJson,
            cancelToken: cancelToken);
    }
  }
}

// =============================================================================
// Riverpod Providers | موفرو Riverpod
// =============================================================================

/// Provider for the unified SAHOOL API client.
/// موفر عميل API الموحد لسهول.
///
/// Usage:
/// ```dart
/// final client = ref.watch(sahoolApiClientProvider);
/// final response = await client.fieldService.get('/nearby');
/// ```
final sahoolApiClientProvider = Provider<SahoolApiClient>((ref) {
  final client = SahoolApiClient();
  ref.onDispose(() => client.dispose());
  return client;
});

/// Provider for the underlying Kong gateway client.
/// موفر عميل بوابة Kong الأساسي.
final kongGatewayProvider = Provider<KongGatewayClient>((ref) {
  final client = ref.watch(sahoolApiClientProvider);
  return client.gateway;
});

/// Provider for the underlying HTTP client.
/// موفر عميل HTTP الأساسي.
final httpClientProvider = Provider<ApiClient>((ref) {
  final client = ref.watch(sahoolApiClientProvider);
  return client.httpClient;
});

/// Provider tracking online/offline status.
/// موفر يتتبع حالة الاتصال/عدم الاتصال.
final isOnlineProvider = Provider<bool>((ref) {
  return ref.watch(sahoolApiClientProvider).isOnline;
});

/// Provider tracking offline queue count.
/// موفر يتتبع عدد الطلبات في طابور العمل.
final offlineQueueCountProvider = Provider<int>((ref) {
  return ref.watch(sahoolApiClientProvider).pendingQueueCount;
});

// =============================================================================
// Convenience Service Providers | موفرو الخدمات المختصرة
// =============================================================================

/// Direct access to the field service proxy.
/// وصول مباشر لوكيل خدمة الحقول.
final fieldServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).fieldService;
});

/// Direct access to the weather service proxy.
/// وصول مباشر لوكيل خدمة الطقس.
final weatherServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).weatherService;
});

/// Direct access to the irrigation service proxy.
/// وصول مباشر لوكيل خدمة الري.
final irrigationServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).irrigationService;
});

/// Direct access to the advisory service proxy.
/// وصول مباشر لوكيل خدمة الاستشارات.
final advisoryServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).advisoryService;
});

/// Direct access to the crop health service proxy.
/// وصول مباشر لوكيل خدمة صحة المحاصيل.
final cropHealthServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).cropHealthService;
});

/// Direct access to the vision service proxy.
/// وصول مباشر لوكيل خدمة الرؤية الحاسوبية.
final visionServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).visionService;
});

/// Direct access to the AI service proxy.
/// وصول مباشر لوكيل خدمة الذكاء الاصطناعي.
final aiServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).aiService;
});

/// Direct access to the task service proxy.
/// وصول مباشر لوكيل خدمة المهام.
final taskServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).taskService;
});

/// Direct access to the notification service proxy.
/// وصول مباشر لوكيل خدمة الإشعارات.
final notificationServiceProvider = Provider<ServiceProxy>((ref) {
  return ref.watch(sahoolApiClientProvider).notificationService;
});
