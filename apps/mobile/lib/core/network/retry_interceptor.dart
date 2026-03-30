/// SAHOOL Network Retry Interceptor
/// معترض إعادة المحاولة للشبكة
///
/// Dio interceptor with robust retry logic:
/// - Exponential backoff (1s, 2s, 4s)
/// - Circuit breaker integration
/// - Network quality awareness
/// - Offline request queueing
/// - Configurable retry policies per endpoint
library;

import 'dart:async';
import 'dart:collection';
import 'dart:io';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../utils/app_logger.dart';
import 'circuit_breaker.dart';
import 'retry_policy.dart';

/// Network quality monitor
class NetworkQualityMonitor {
  final Connectivity _connectivity = Connectivity();
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  NetworkQuality _currentQuality = NetworkQuality.unknown;
  DateTime? _lastLatencyCheck;
  int _averageLatencyMs = 0;
  final List<int> _latencyHistory = [];

  /// Stream controller for quality changes
  final _qualityController = StreamController<NetworkQuality>.broadcast();

  NetworkQualityMonitor() {
    _initialize();
  }

  NetworkQuality get currentQuality => _currentQuality;
  Stream<NetworkQuality> get qualityStream => _qualityController.stream;
  int get averageLatencyMs => _averageLatencyMs;

  void _initialize() {
    // Check initial connectivity
    unawaited(_connectivity.checkConnectivity().then(_updateFromConnectivity));

    // Listen for changes
    _subscription = _connectivity.onConnectivityChanged.listen(_updateFromConnectivity);
  }

  void _updateFromConnectivity(List<ConnectivityResult> results) {
    final wasOnline = _currentQuality != NetworkQuality.offline;
    final isNowOnline = results.isNotEmpty &&
        !results.every((r) => r == ConnectivityResult.none);

    if (!isNowOnline) {
      _setQuality(NetworkQuality.offline);
    } else if (!wasOnline) {
      // Just came online, assume good until we measure
      _setQuality(NetworkQuality.good);
    }
  }

  /// Record a request latency measurement
  void recordLatency(int latencyMs) {
    _latencyHistory.add(latencyMs);

    // Keep only last 10 measurements
    if (_latencyHistory.length > 10) {
      _latencyHistory.removeAt(0);
    }

    // Calculate average
    _averageLatencyMs = _latencyHistory.reduce((a, b) => a + b) ~/ _latencyHistory.length;
    _lastLatencyCheck = DateTime.now();

    // Update quality based on latency
    _updateQualityFromLatency();
  }

  void _updateQualityFromLatency() {
    if (_currentQuality == NetworkQuality.offline) return;

    if (_averageLatencyMs < 500) {
      _setQuality(NetworkQuality.good);
    } else if (_averageLatencyMs < 2000) {
      _setQuality(NetworkQuality.slow);
    } else {
      _setQuality(NetworkQuality.verySlow);
    }
  }

  void _setQuality(NetworkQuality quality) {
    if (_currentQuality != quality) {
      final previousQuality = _currentQuality;
      _currentQuality = quality;

      AppLogger.i(
        'Network quality changed',
        tag: 'NetworkQuality',
        data: {
          'from': previousQuality.name,
          'to': quality.name,
          'averageLatency': '${_averageLatencyMs}ms',
        },
      );

      if (!_qualityController.isClosed) {
        _qualityController.add(quality);
      }
    }
  }

  /// Force update to offline
  void markOffline() {
    _setQuality(NetworkQuality.offline);
  }

  /// Force update to online (quality will be determined by latency)
  void markOnline() {
    if (_currentQuality == NetworkQuality.offline) {
      _setQuality(NetworkQuality.unknown);
    }
  }

  void dispose() {
    _subscription?.cancel();
    _qualityController.close();
  }
}

/// Queued request for offline handling
class QueuedNetworkRequest {
  final RequestOptions options;
  final Completer<Response> completer;
  final DateTime queuedAt;
  final RetryPolicy policy;
  int retryCount;

  QueuedNetworkRequest({
    required this.options,
    required this.completer,
    required this.queuedAt,
    required this.policy,
    this.retryCount = 0,
  });

  /// Check if request has expired
  bool get isExpired {
    // Requests expire after 5 minutes in queue
    return DateTime.now().difference(queuedAt) > const Duration(minutes: 5);
  }
}

/// Retry interceptor statistics
class RetryInterceptorStats {
  int totalRequests = 0;
  int successfulRequests = 0;
  int failedRequests = 0;
  int retriedRequests = 0;
  int queuedRequests = 0;
  int circuitBrokenRequests = 0;
  int totalRetries = 0;
  Map<int, int> statusCodeCounts = {};

  void reset() {
    totalRequests = 0;
    successfulRequests = 0;
    failedRequests = 0;
    retriedRequests = 0;
    queuedRequests = 0;
    circuitBrokenRequests = 0;
    totalRetries = 0;
    statusCodeCounts.clear();
  }

  double get successRate =>
      totalRequests > 0 ? (successfulRequests / totalRequests) * 100 : 0;

  double get retryRate =>
      totalRequests > 0 ? (retriedRequests / totalRequests) * 100 : 0;

  @override
  String toString() {
    return 'RetryInterceptorStats(total: $totalRequests, success: $successfulRequests, '
        'failed: $failedRequests, retried: $retriedRequests, '
        'successRate: ${successRate.toStringAsFixed(1)}%)';
  }
}

/// SAHOOL Robust Retry Interceptor
///
/// Features:
/// - Exponential backoff with configurable delays (default: 1s, 2s, 4s)
/// - Circuit breaker pattern (opens after 5 failures, recovers after 30s)
/// - Network quality detection (good, slow, offline)
/// - Offline request queueing
/// - Per-endpoint retry policies
/// - Detailed logging and statistics
class RobustRetryInterceptor extends Interceptor {
  /// Circuit breaker manager for per-endpoint tracking
  final CircuitBreakerManager _circuitBreakerManager;

  /// Network quality monitor
  final NetworkQualityMonitor _networkMonitor;

  /// Queue for offline requests
  final Queue<QueuedNetworkRequest> _offlineQueue = Queue();

  /// Default retry policy
  final RetryPolicy defaultPolicy;

  /// Maximum queue size
  final int maxQueueSize;

  /// Whether to enable offline queueing
  final bool enableOfflineQueue;

  /// Callback for retry events
  final OnRetryCallback? onRetry;

  /// Callback for circuit breaker events
  final void Function(String endpoint, CircuitBreakerState state)? onCircuitStateChange;

  /// Statistics
  final RetryInterceptorStats stats = RetryInterceptorStats();

  /// Subscription for network quality changes
  StreamSubscription<NetworkQuality>? _networkQualitySubscription;

  RobustRetryInterceptor({
    CircuitBreakerManager? circuitBreakerManager,
    NetworkQualityMonitor? networkMonitor,
    this.defaultPolicy = RetryPolicies.standard,
    this.maxQueueSize = 50,
    this.enableOfflineQueue = true,
    this.onRetry,
    this.onCircuitStateChange,
  })  : _circuitBreakerManager = circuitBreakerManager ?? CircuitBreakerManager(),
        _networkMonitor = networkMonitor ?? NetworkQualityMonitor() {
    // Listen to network quality changes to process queue
    _networkQualitySubscription = _networkMonitor.qualityStream.listen((quality) {
      if (quality != NetworkQuality.offline) {
        _processOfflineQueue();
      }
    });
  }

  /// Get circuit breaker for an endpoint
  CircuitBreaker _getCircuitBreaker(String endpoint) {
    return _circuitBreakerManager.getBreaker(
      _normalizeEndpoint(endpoint),
      config: const CircuitBreakerConfig(
        failureThreshold: 5,
        recoveryTimeout: Duration(seconds: 30),
        successThreshold: 2,
        halfOpenMaxRequests: 3,
      ),
    );
  }

  /// Normalize endpoint for circuit breaker grouping
  String _normalizeEndpoint(String path) {
    // Extract base path (first two segments)
    final uri = Uri.parse(path);
    final segments = uri.pathSegments;

    if (segments.length >= 2) {
      return '/${segments[0]}/${segments[1]}';
    } else if (segments.isNotEmpty) {
      return '/${segments[0]}';
    }
    return path;
  }

  /// Get retry policy for a request
  RetryPolicy _getPolicyForRequest(RequestOptions options) {
    // Check for custom policy in extra data
    final customPolicy = options.extra['retryPolicy'] as RetryPolicy?;
    if (customPolicy != null) return customPolicy;

    // Get policy based on path
    return RetryPolicies.forPath(options.path);
  }

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    stats.totalRequests++;

    final endpoint = _normalizeEndpoint(options.path);
    final circuitBreaker = _getCircuitBreaker(endpoint);

    // Check circuit breaker
    if (!circuitBreaker.canAttemptRequest()) {
      stats.circuitBrokenRequests++;

      final status = circuitBreaker.status;
      if (kDebugMode) {
        AppLogger.w(
          'Request blocked by circuit breaker',
          tag: 'RetryInterceptor',
          data: {
            'endpoint': endpoint,
            'state': status.state.name,
            'timeUntilRecovery': status.timeUntilRecovery?.inSeconds,
          },
        );
      }

      // Check if should queue
      final policy = _getPolicyForRequest(options);
      if (enableOfflineQueue && policy.queueWhenOffline) {
        _queueRequest(options, handler);
        return;
      }

      handler.reject(
        DioException(
          requestOptions: options,
          type: DioExceptionType.unknown,
          error: CircuitOpenException(
            endpoint: endpoint,
            timeUntilRecovery: status.timeUntilRecovery,
          ),
          message: 'Circuit breaker is open for $endpoint',
        ),
      );
      return;
    }

    // Check network quality for offline queueing
    if (_networkMonitor.currentQuality == NetworkQuality.offline) {
      final policy = _getPolicyForRequest(options);
      if (enableOfflineQueue && policy.queueWhenOffline) {
        _queueRequest(options, handler);
        return;
      }
    }

    // Record request start time for latency tracking
    options.extra['_requestStartTime'] = DateTime.now().millisecondsSinceEpoch;

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final endpoint = _normalizeEndpoint(response.requestOptions.path);
    final circuitBreaker = _getCircuitBreaker(endpoint);

    // Record success
    circuitBreaker.recordSuccess();
    stats.successfulRequests++;

    // Record latency
    final startTime = response.requestOptions.extra['_requestStartTime'] as int?;
    if (startTime != null) {
      final latency = DateTime.now().millisecondsSinceEpoch - startTime;
      _networkMonitor.recordLatency(latency);
    }

    // Track status codes
    final statusCode = response.statusCode ?? 0;
    stats.statusCodeCounts[statusCode] = (stats.statusCodeCounts[statusCode] ?? 0) + 1;

    handler.next(response);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final options = err.requestOptions;
    final endpoint = _normalizeEndpoint(options.path);
    final circuitBreaker = _getCircuitBreaker(endpoint);
    final policy = _getPolicyForRequest(options);

    // Get current retry count
    final retryCount = options.extra['_retryCount'] as int? ?? 0;

    // Track status codes
    final statusCode = err.response?.statusCode;
    if (statusCode != null) {
      stats.statusCodeCounts[statusCode] = (stats.statusCodeCounts[statusCode] ?? 0) + 1;
    }

    // Check if should retry
    if (_shouldRetry(err, policy, retryCount)) {
      final nextRetryCount = retryCount + 1;

      // Calculate delay
      final delay = policy.getDelayDuration(
        retryCount,
        networkQuality: _networkMonitor.currentQuality,
      );

      // Create retry info
      final retryInfo = RetryAttemptInfo(
        attempt: retryCount,
        maxAttempts: policy.maxRetries,
        delay: delay,
        statusCode: statusCode,
        errorMessage: err.message,
        timestamp: DateTime.now(),
        networkQuality: _networkMonitor.currentQuality,
      );

      // Notify callback
      onRetry?.call(retryInfo);

      if (kDebugMode) {
        AppLogger.w(
          'Retrying request',
          tag: 'RetryInterceptor',
          data: {
            'endpoint': endpoint,
            'attempt': '$nextRetryCount/${policy.maxRetries}',
            'delay': '${delay.inMilliseconds}ms',
            'errorType': err.type.name,
            'statusCode': statusCode,
            'networkQuality': _networkMonitor.currentQuality.name,
          },
        );
      }

      stats.retriedRequests++;
      stats.totalRetries++;

      // Wait before retry
      await Future.delayed(delay);

      // Clone and update options
      options.extra['_retryCount'] = nextRetryCount;

      try {
        // Create new Dio instance for retry to avoid interceptor loops
        final retryDio = Dio(BaseOptions(
          baseUrl: options.baseUrl,
          connectTimeout: options.connectTimeout,
          receiveTimeout: options.receiveTimeout,
          sendTimeout: options.sendTimeout,
        ));

        final response = await retryDio.request(
          options.path,
          data: options.data,
          queryParameters: options.queryParameters,
          options: Options(
            method: options.method,
            headers: options.headers,
            responseType: options.responseType,
            contentType: options.contentType,
            validateStatus: options.validateStatus,
            receiveDataWhenStatusError: options.receiveDataWhenStatusError,
            followRedirects: options.followRedirects,
            maxRedirects: options.maxRedirects,
            extra: options.extra,
          ),
        );

        // Record success
        circuitBreaker.recordSuccess();
        stats.successfulRequests++;

        if (kDebugMode) {
          AppLogger.i(
            'Retry successful',
            tag: 'RetryInterceptor',
            data: {
              'endpoint': endpoint,
              'attempt': nextRetryCount,
              'statusCode': response.statusCode,
            },
          );
        }

        return handler.resolve(response);
      } on DioException catch (retryError) {
        // Retry failed, continue to next handler or retry again
        return onError(retryError, handler);
      }
    }

    // Record failure in circuit breaker
    circuitBreaker.recordFailure(
      errorMessage: err.message,
      statusCode: statusCode,
      endpoint: endpoint,
    );
    stats.failedRequests++;

    // Log max retries exceeded
    if (retryCount >= policy.maxRetries && kDebugMode) {
      AppLogger.e(
        'Max retries exceeded',
        tag: 'RetryInterceptor',
        data: {
          'endpoint': endpoint,
          'attempts': retryCount,
          'errorType': err.type.name,
          'statusCode': statusCode,
        },
      );
    }

    // Check if should queue for offline retry
    if (enableOfflineQueue &&
        policy.queueWhenOffline &&
        _isNetworkError(err) &&
        _networkMonitor.currentQuality == NetworkQuality.offline) {
      _queueRequest(options, handler);
      return;
    }

    handler.next(err);
  }

  /// Determine if request should be retried
  bool _shouldRetry(DioException error, RetryPolicy policy, int currentRetry) {
    // Check max retries
    if (!policy.shouldRetry(currentRetry)) {
      return false;
    }

    // Check if cancelled
    if (error.type == DioExceptionType.cancel) {
      return false;
    }

    // Check status code
    if (error.response != null) {
      final statusCode = error.response!.statusCode ?? 0;

      // Never retry 4xx client errors (except specific ones in policy)
      if (statusCode >= 400 && statusCode < 500) {
        return policy.isStatusCodeRetryable(statusCode);
      }

      // Retry 5xx server errors if in retryable set
      if (statusCode >= 500) {
        return policy.isStatusCodeRetryable(statusCode);
      }
    }

    // Check error type
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return policy.retryOnTimeout;

      case DioExceptionType.connectionError:
        // Check for specific network errors
        if (error.error is SocketException) {
          return policy.retryOnConnectionError;
        }
        if (error.error is TimeoutException) {
          return policy.retryOnTimeout;
        }
        return policy.retryOnConnectionError;

      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode ?? 0;
        return policy.isStatusCodeRetryable(statusCode);

      case DioExceptionType.cancel:
        return false;

      default:
        return false;
    }
  }

  /// Check if error is a network error
  bool _isNetworkError(DioException error) {
    return error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.connectionTimeout ||
        error.error is SocketException;
  }

  /// Queue a request for later retry
  void _queueRequest(RequestOptions options, dynamic handler) {
    // Check queue size
    if (_offlineQueue.length >= maxQueueSize) {
      // Remove oldest expired requests
      _offlineQueue.removeWhere((req) => req.isExpired);

      // If still full, remove oldest
      if (_offlineQueue.length >= maxQueueSize) {
        final oldest = _offlineQueue.removeFirst();
        oldest.completer.completeError(
          DioException(
            requestOptions: oldest.options,
            type: DioExceptionType.unknown,
            message: 'Request removed from queue due to size limit',
          ),
        );
      }
    }

    final completer = Completer<Response>();
    final policy = _getPolicyForRequest(options);

    _offlineQueue.add(QueuedNetworkRequest(
      options: options,
      completer: completer,
      queuedAt: DateTime.now(),
      policy: policy,
    ));

    stats.queuedRequests++;

    if (kDebugMode) {
      AppLogger.i(
        'Request queued for offline retry',
        tag: 'RetryInterceptor',
        data: {
          'path': options.path,
          'method': options.method,
          'queueSize': _offlineQueue.length,
        },
      );
    }

    // Resolve with queued response or reject based on handler type
    if (handler is RequestInterceptorHandler) {
      handler.reject(
        DioException(
          requestOptions: options,
          type: DioExceptionType.connectionError,
          message: 'Request queued for offline retry',
          error: QueuedRequestException(
            message: 'Request queued - will retry when online',
            completer: completer,
          ),
        ),
      );
    } else if (handler is ErrorInterceptorHandler) {
      handler.reject(
        DioException(
          requestOptions: options,
          type: DioExceptionType.connectionError,
          message: 'Request queued for offline retry',
          error: QueuedRequestException(
            message: 'Request queued - will retry when online',
            completer: completer,
          ),
        ),
      );
    }
  }

  /// Process queued requests when coming online
  Future<void> _processOfflineQueue() async {
    if (_offlineQueue.isEmpty) return;

    if (kDebugMode) {
      AppLogger.i(
        'Processing offline queue',
        tag: 'RetryInterceptor',
        data: {'queueSize': _offlineQueue.length},
      );
    }

    // Create a copy to iterate
    final requests = List<QueuedNetworkRequest>.from(_offlineQueue);
    _offlineQueue.clear();

    for (final request in requests) {
      // Skip expired requests
      if (request.isExpired) {
        request.completer.completeError(
          DioException(
            requestOptions: request.options,
            type: DioExceptionType.unknown,
            message: 'Queued request expired',
          ),
        );
        continue;
      }

      try {
        // Retry the request
        final dio = Dio(BaseOptions(
          baseUrl: request.options.baseUrl,
          connectTimeout: request.options.connectTimeout,
          receiveTimeout: request.options.receiveTimeout,
        ));

        final response = await dio.request(
          request.options.path,
          data: request.options.data,
          queryParameters: request.options.queryParameters,
          options: Options(
            method: request.options.method,
            headers: request.options.headers,
            extra: request.options.extra,
          ),
        );

        request.completer.complete(response);
      } on DioException catch (e) {
        // Check if should re-queue
        if (_isNetworkError(e) &&
            request.policy.queueWhenOffline &&
            _networkMonitor.currentQuality == NetworkQuality.offline) {
          // Re-queue for later
          _offlineQueue.add(request);
        } else {
          request.completer.completeError(e);
        }
      }

      // Small delay between requests to avoid overwhelming the network
      await Future.delayed(const Duration(milliseconds: 100));
    }
  }

  /// Get current statistics
  RetryInterceptorStats getStats() => stats;

  /// Get network quality
  NetworkQuality getNetworkQuality() => _networkMonitor.currentQuality;

  /// Get circuit breaker status for an endpoint
  CircuitBreakerStatus? getCircuitBreakerStatus(String endpoint) {
    final normalizedEndpoint = _normalizeEndpoint(endpoint);
    return _circuitBreakerManager.getBreaker(normalizedEndpoint).status;
  }

  /// Get all circuit breaker statuses
  Map<String, CircuitBreakerStatus> getAllCircuitBreakerStatuses() {
    return _circuitBreakerManager.getAllStatuses();
  }

  /// Get circuit breaker health summary
  CircuitBreakerHealthSummary getCircuitBreakerHealth() {
    return _circuitBreakerManager.getHealthSummary();
  }

  /// Get queued request count
  int get queuedRequestCount => _offlineQueue.length;

  /// Reset statistics
  void resetStats() {
    stats.reset();
  }

  /// Reset all circuit breakers
  void resetCircuitBreakers() {
    _circuitBreakerManager.resetAll();
  }

  /// Force process offline queue
  Future<void> processQueue() => _processOfflineQueue();

  /// Dispose resources
  void dispose() {
    _networkQualitySubscription?.cancel();
    _networkMonitor.dispose();
    _circuitBreakerManager.dispose();

    // Reject all queued requests
    for (final request in _offlineQueue) {
      request.completer.completeError(
        DioException(
          requestOptions: request.options,
          type: DioExceptionType.unknown,
          message: 'Interceptor disposed',
        ),
      );
    }
    _offlineQueue.clear();
  }
}

/// Exception for queued requests
class QueuedRequestException implements Exception {
  final String message;
  final Completer<Response>? completer;

  const QueuedRequestException({
    required this.message,
    this.completer,
  });

  @override
  String toString() => 'QueuedRequestException: $message';
}

/// Extension to add retry policy to request options
extension RetryPolicyExtension on RequestOptions {
  /// Set custom retry policy for this request
  void setRetryPolicy(RetryPolicy policy) {
    extra['retryPolicy'] = policy;
  }

  /// Disable retry for this request
  void disableRetry() {
    extra['retryPolicy'] = RetryPolicies.none;
  }

  /// Get the retry policy for this request
  RetryPolicy? get retryPolicy => extra['retryPolicy'] as RetryPolicy?;
}

/// Extension to add retry options to Dio Options
extension RetryOptionsExtension on Options {
  /// Create options with custom retry policy
  static Options withRetryPolicy(RetryPolicy policy) {
    return Options(extra: {'retryPolicy': policy});
  }

  /// Create options with retry disabled
  static Options withRetryDisabled() {
    return Options(extra: {'retryPolicy': RetryPolicies.none});
  }
}
