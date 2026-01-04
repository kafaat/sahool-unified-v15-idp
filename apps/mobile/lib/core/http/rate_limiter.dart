import 'dart:async';
import 'dart:collection';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../utils/app_logger.dart';

/// Token Bucket Rate Limiter for API requests
/// Implements per-endpoint rate limiting with automatic retry and exponential backoff
class RateLimiter {
  final Map<String, TokenBucket> _buckets = {};
  final Map<String, EndpointConfig> _endpointConfigs;
  final EndpointConfig _defaultConfig;
  final Queue<_QueuedRequest> _requestQueue = Queue();
  bool _processingQueue = false;

  RateLimiter({
    Map<String, EndpointConfig>? endpointConfigs,
    EndpointConfig? defaultConfig,
  })  : _endpointConfigs = endpointConfigs ?? _getDefaultEndpointConfigs(),
        _defaultConfig = defaultConfig ?? EndpointConfig.defaultConfig();

  /// Default endpoint configurations
  static Map<String, EndpointConfig> _getDefaultEndpointConfigs() {
    return {
      // Auth endpoints - strictest limits
      'auth': EndpointConfig(
        maxRequests: 5,
        windowDuration: const Duration(minutes: 1),
        maxRetries: 3,
        initialBackoff: const Duration(seconds: 2),
        maxBackoff: const Duration(seconds: 30),
      ),
      // Sync endpoints - moderate limits
      'sync': EndpointConfig(
        maxRequests: 30,
        windowDuration: const Duration(minutes: 1),
        maxRetries: 5,
        initialBackoff: const Duration(seconds: 1),
        maxBackoff: const Duration(seconds: 60),
      ),
      // Upload endpoints - lower limits
      'upload': EndpointConfig(
        maxRequests: 10,
        windowDuration: const Duration(minutes: 1),
        maxRetries: 3,
        initialBackoff: const Duration(seconds: 3),
        maxBackoff: const Duration(seconds: 120),
      ),
      // Default for other endpoints
      'default': EndpointConfig(
        maxRequests: 60,
        windowDuration: const Duration(minutes: 1),
        maxRetries: 3,
        initialBackoff: const Duration(seconds: 1),
        maxBackoff: const Duration(seconds: 30),
      ),
    };
  }

  /// Get token bucket for an endpoint
  TokenBucket _getBucket(String endpointType) {
    return _buckets.putIfAbsent(
      endpointType,
      () {
        final config = _endpointConfigs[endpointType] ?? _defaultConfig;
        return TokenBucket(
          capacity: config.maxRequests,
          refillRate: config.maxRequests / config.windowDuration.inSeconds,
        );
      },
    );
  }

  /// Determine endpoint type from path
  String _getEndpointType(String path) {
    if (path.contains('/auth') ||
        path.contains('/login') ||
        path.contains('/register') ||
        path.contains('/refresh-token')) {
      return 'auth';
    } else if (path.contains('/sync') ||
               path.contains('/tasks') ||
               path.contains('/outbox')) {
      return 'sync';
    } else if (path.contains('/upload') ||
               path.contains('/file') ||
               path.contains('/attachment')) {
      return 'upload';
    }
    return 'default';
  }

  /// Check if request can proceed
  Future<bool> tryAcquire(String path) async {
    final endpointType = _getEndpointType(path);
    final bucket = _getBucket(endpointType);
    return bucket.tryConsume();
  }

  /// Wait until a token is available (with timeout)
  Future<void> waitForToken(String path, {Duration? timeout}) async {
    final endpointType = _getEndpointType(path);
    final bucket = _getBucket(endpointType);

    final maxWaitTime = timeout ?? const Duration(seconds: 30);
    final startTime = DateTime.now();

    while (!bucket.tryConsume()) {
      if (DateTime.now().difference(startTime) > maxWaitTime) {
        throw RateLimitException(
          'Rate limit exceeded for endpoint: $path. '
          'Waited ${maxWaitTime.inSeconds}s without token availability.',
          endpointType: endpointType,
        );
      }

      // Wait for token refill (calculated based on refill rate)
      final waitTime = bucket.getWaitTime();
      await Future.delayed(waitTime);
    }
  }

  /// Queue a request for later execution
  Future<Response<dynamic>> queueRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final completer = Completer<Response<dynamic>>();
    final queuedRequest = _QueuedRequest(
      options: options,
      handler: handler,
      completer: completer,
    );

    _requestQueue.add(queuedRequest);

    if (!_processingQueue) {
      _processQueue();
    }

    return completer.future;
  }

  /// Process queued requests
  Future<void> _processQueue() async {
    if (_processingQueue) return;
    _processingQueue = true;

    while (_requestQueue.isNotEmpty) {
      final request = _requestQueue.first;
      final path = request.options.path;

      if (await tryAcquire(path)) {
        _requestQueue.removeFirst();
        request.handler.next(request.options);

        // Note: The completer will be completed by the response/error interceptor
        // We just signal that the request can proceed
      } else {
        // Wait a bit before checking again
        final endpointType = _getEndpointType(path);
        final bucket = _getBucket(endpointType);
        await Future.delayed(bucket.getWaitTime());
      }
    }

    _processingQueue = false;
  }

  /// Get current status for an endpoint type
  RateLimitStatus getStatus(String endpointType) {
    final bucket = _getBucket(endpointType);
    final config = _endpointConfigs[endpointType] ?? _defaultConfig;

    return RateLimitStatus(
      endpointType: endpointType,
      availableTokens: bucket.availableTokens,
      maxTokens: config.maxRequests,
      refillRate: config.maxRequests / config.windowDuration.inSeconds,
      queuedRequests: _requestQueue.where(
        (r) => _getEndpointType(r.options.path) == endpointType
      ).length,
    );
  }

  /// Reset all rate limiters (useful for testing)
  void reset() {
    _buckets.clear();
    _requestQueue.clear();
    _processingQueue = false;
  }

  /// Get endpoint configuration
  EndpointConfig getConfig(String endpointType) {
    return _endpointConfigs[endpointType] ?? _defaultConfig;
  }
}

/// Token Bucket implementation for rate limiting
class TokenBucket {
  final int capacity;
  final double refillRate; // tokens per second

  double _tokens;
  DateTime _lastRefill;

  TokenBucket({
    required this.capacity,
    required this.refillRate,
  })  : _tokens = capacity.toDouble(),
        _lastRefill = DateTime.now();

  /// Try to consume a token
  bool tryConsume({int tokens = 1}) {
    _refill();

    if (_tokens >= tokens) {
      _tokens -= tokens;
      return true;
    }
    return false;
  }

  /// Refill tokens based on elapsed time
  void _refill() {
    final now = DateTime.now();
    final elapsed = now.difference(_lastRefill).inMilliseconds / 1000.0;

    if (elapsed > 0) {
      final tokensToAdd = elapsed * refillRate;
      _tokens = (_tokens + tokensToAdd).clamp(0, capacity.toDouble());
      _lastRefill = now;
    }
  }

  /// Get number of available tokens
  int get availableTokens {
    _refill();
    return _tokens.floor();
  }

  /// Get estimated wait time for next token
  Duration getWaitTime() {
    _refill();

    if (_tokens >= 1) {
      return Duration.zero;
    }

    // Calculate time needed to refill one token
    final tokensNeeded = 1 - _tokens;
    final secondsNeeded = tokensNeeded / refillRate;

    return Duration(milliseconds: (secondsNeeded * 1000).ceil());
  }
}

/// Endpoint configuration
class EndpointConfig {
  final int maxRequests;
  final Duration windowDuration;
  final int maxRetries;
  final Duration initialBackoff;
  final Duration maxBackoff;
  final double backoffMultiplier;

  const EndpointConfig({
    required this.maxRequests,
    required this.windowDuration,
    this.maxRetries = 3,
    this.initialBackoff = const Duration(seconds: 1),
    this.maxBackoff = const Duration(seconds: 60),
    this.backoffMultiplier = 2.0,
  });

  factory EndpointConfig.defaultConfig() {
    return const EndpointConfig(
      maxRequests: 60,
      windowDuration: Duration(minutes: 1),
      maxRetries: 3,
      initialBackoff: Duration(seconds: 1),
      maxBackoff: Duration(seconds: 30),
    );
  }

  /// Calculate backoff duration for a given retry attempt
  Duration getBackoffDuration(int retryCount) {
    final backoff = initialBackoff * (backoffMultiplier * retryCount);
    return Duration(
      milliseconds: backoff.inMilliseconds.clamp(
        initialBackoff.inMilliseconds,
        maxBackoff.inMilliseconds,
      ),
    );
  }
}

/// Rate limit status
class RateLimitStatus {
  final String endpointType;
  final int availableTokens;
  final int maxTokens;
  final double refillRate;
  final int queuedRequests;

  RateLimitStatus({
    required this.endpointType,
    required this.availableTokens,
    required this.maxTokens,
    required this.refillRate,
    required this.queuedRequests,
  });

  double get utilizationPercent =>
      ((maxTokens - availableTokens) / maxTokens) * 100;

  @override
  String toString() {
    return 'RateLimitStatus($endpointType: $availableTokens/$maxTokens tokens, '
           '${queuedRequests} queued, ${utilizationPercent.toStringAsFixed(1)}% utilized)';
  }
}

/// Rate limit exception
class RateLimitException implements Exception {
  final String message;
  final String endpointType;

  RateLimitException(this.message, {required this.endpointType});

  @override
  String toString() => 'RateLimitException: $message';
}

/// Queued request holder
class _QueuedRequest {
  final RequestOptions options;
  final RequestInterceptorHandler handler;
  final Completer<Response<dynamic>> completer;

  _QueuedRequest({
    required this.options,
    required this.handler,
    required this.completer,
  });
}

/// Dio Interceptor for rate limiting
class RateLimitInterceptor extends Interceptor {
  final RateLimiter rateLimiter;
  final bool queueExceededRequests;

  RateLimitInterceptor({
    RateLimiter? rateLimiter,
    this.queueExceededRequests = true,
  }) : rateLimiter = rateLimiter ?? RateLimiter();

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    try {
      final canProceed = await rateLimiter.tryAcquire(options.path);

      if (canProceed) {
        if (kDebugMode) {
          final endpointType = rateLimiter._getEndpointType(options.path);
          final status = rateLimiter.getStatus(endpointType);
          AppLogger.d('Rate Limit status', tag: 'RateLimiter', data: {
            'endpointType': endpointType,
            'availableTokens': status.availableTokens,
            'maxTokens': status.maxTokens,
          });
        }
        handler.next(options);
      } else {
        if (queueExceededRequests) {
          // Wait for token availability
          if (kDebugMode) {
            AppLogger.d('Rate limit reached, waiting...', tag: 'RateLimiter', data: {'path': options.path});
          }

          await rateLimiter.waitForToken(options.path);

          if (kDebugMode) {
            AppLogger.d('Token acquired, proceeding', tag: 'RateLimiter', data: {'path': options.path});
          }

          handler.next(options);
        } else {
          // Reject immediately
          final endpointType = rateLimiter._getEndpointType(options.path);
          handler.reject(
            DioException(
              requestOptions: options,
              type: DioExceptionType.unknown,
              error: RateLimitException(
                'Rate limit exceeded for ${options.path}',
                endpointType: endpointType,
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (e is RateLimitException) {
        handler.reject(
          DioException(
            requestOptions: options,
            type: DioExceptionType.unknown,
            error: e,
          ),
        );
      } else {
        rethrow;
      }
    }
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Check if we should retry based on rate limiting
    if (_shouldRetryWithBackoff(err)) {
      final retryCount = err.requestOptions.extra['retryCount'] as int? ?? 0;
      final endpointType = rateLimiter._getEndpointType(err.requestOptions.path);
      final config = rateLimiter.getConfig(endpointType);

      if (retryCount < config.maxRetries) {
        final backoffDuration = config.getBackoffDuration(retryCount);

        if (kDebugMode) {
          AppLogger.d('Retrying request', tag: 'RateLimiter', data: {
            'path': err.requestOptions.path,
            'backoff_seconds': backoffDuration.inSeconds,
            'attempt': retryCount + 1,
            'maxRetries': config.maxRetries,
          });
        }

        // Schedule retry with exponential backoff
        Future.delayed(backoffDuration, () async {
          try {
            final newOptions = err.requestOptions;
            newOptions.extra['retryCount'] = retryCount + 1;

            // Wait for rate limit token
            await rateLimiter.waitForToken(newOptions.path);

            // Create a new Dio instance to retry (using the same base)
            final dio = Dio()..options = newOptions;
            final response = await dio.fetch(newOptions);
            handler.resolve(response);
          } catch (e) {
            if (e is DioException) {
              handler.next(e);
            } else {
              handler.next(err);
            }
          }
        });

        return;
      }
    }

    handler.next(err);
  }

  /// Check if error should trigger retry with backoff
  bool _shouldRetryWithBackoff(DioException err) {
    // Retry on rate limit errors (429)
    if (err.response?.statusCode == 429) {
      return true;
    }

    // Retry on temporary server errors (503, 502, 504)
    if (err.response?.statusCode != null) {
      final statusCode = err.response!.statusCode!;
      if (statusCode == 503 || statusCode == 502 || statusCode == 504) {
        return true;
      }
    }

    // Retry on timeout errors
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.sendTimeout) {
      return true;
    }

    // Retry on connection errors (but not on other errors like 4xx client errors)
    if (err.type == DioExceptionType.connectionError) {
      return true;
    }

    return false;
  }
}
