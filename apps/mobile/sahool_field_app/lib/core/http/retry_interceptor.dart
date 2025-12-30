import 'dart:async';
import 'dart:math';

import 'package:dio/dio.dart';
import '../utils/app_logger.dart';

/// Retry interceptor with exponential backoff and circuit breaker
class RetryInterceptor extends Interceptor {
  final int maxRetries;
  final Duration baseDelay;
  final Duration maxDelay;
  final bool enableJitter;
  final CircuitBreaker? circuitBreaker;

  /// Retry configuration
  RetryInterceptor({
    this.maxRetries = 3,
    this.baseDelay = const Duration(milliseconds: 500),
    this.maxDelay = const Duration(seconds: 10),
    this.enableJitter = true,
    this.circuitBreaker,
  });

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    // Get retry count from request options
    final retryCount = err.requestOptions.extra['retry_count'] as int? ?? 0;

    // Check if we should retry
    if (!_shouldRetry(err, retryCount)) {
      AppLogger.d(
        'Not retrying request: ${err.requestOptions.path}',
        tag: 'RETRY',
        data: {
          'reason': _getNoRetryReason(err, retryCount),
          'retryCount': retryCount,
        },
      );
      return handler.next(err);
    }

    // Check circuit breaker
    if (circuitBreaker != null && !circuitBreaker!.canExecute()) {
      AppLogger.w(
        'Circuit breaker is OPEN - blocking request',
        tag: 'CIRCUIT_BREAKER',
        data: {'path': err.requestOptions.path},
      );
      return handler.next(err);
    }

    // Calculate delay with exponential backoff
    final delay = _calculateDelay(retryCount);

    AppLogger.i(
      'Retrying request (${retryCount + 1}/$maxRetries) after ${delay.inMilliseconds}ms',
      tag: 'RETRY',
      data: {
        'path': err.requestOptions.path,
        'statusCode': err.response?.statusCode,
        'type': err.type.name,
      },
    );

    // Wait before retry
    await Future.delayed(delay);

    try {
      // Update retry count
      final options = err.requestOptions;
      options.extra['retry_count'] = retryCount + 1;

      // Retry the request
      final response = await Dio().fetch(options);

      // Record success in circuit breaker
      circuitBreaker?.recordSuccess();

      AppLogger.i(
        'Retry successful',
        tag: 'RETRY',
        data: {
          'path': options.path,
          'attempt': retryCount + 1,
          'statusCode': response.statusCode,
        },
      );

      return handler.resolve(response);
    } catch (e) {
      // Record failure in circuit breaker
      circuitBreaker?.recordFailure();

      // If this is our last retry, pass the error along
      if (retryCount + 1 >= maxRetries) {
        AppLogger.w(
          'Max retries reached',
          tag: 'RETRY',
          data: {
            'path': err.requestOptions.path,
            'attempts': retryCount + 1,
          },
        );
      }

      // Pass the original or new error
      if (e is DioException) {
        return handler.next(e);
      } else {
        return handler.next(err);
      }
    }
  }

  /// Check if request should be retried
  bool _shouldRetry(DioException err, int retryCount) {
    // Don't retry if max retries reached
    if (retryCount >= maxRetries) {
      return false;
    }

    // Check error type
    return switch (err.type) {
      // Retry on timeout errors
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout =>
        true,

      // Retry on connection errors (network issues)
      DioExceptionType.connectionError => true,

      // Retry on specific HTTP status codes
      DioExceptionType.badResponse => _shouldRetryStatusCode(
          err.response?.statusCode,
        ),

      // Don't retry on other error types
      DioExceptionType.badCertificate ||
      DioExceptionType.cancel ||
      DioExceptionType.unknown =>
        false,
    };
  }

  /// Check if status code should be retried
  bool _shouldRetryStatusCode(int? statusCode) {
    if (statusCode == null) return false;

    return switch (statusCode) {
      // Retry on server errors (5xx)
      >= 500 && < 600 => true,

      // Retry on rate limiting (with backoff)
      429 => true,

      // Retry on request timeout
      408 => true,

      // Retry on service unavailable
      503 => true,

      // Retry on gateway timeout
      504 => true,

      // Don't retry on client errors (4xx) except the above
      _ => false,
    };
  }

  /// Get reason for not retrying
  String _getNoRetryReason(DioException err, int retryCount) {
    if (retryCount >= maxRetries) {
      return 'Max retries reached';
    }

    return switch (err.type) {
      DioExceptionType.badCertificate => 'Certificate error',
      DioExceptionType.cancel => 'Request cancelled',
      DioExceptionType.badResponse =>
        'Status code ${err.response?.statusCode} not retryable',
      _ => 'Error type ${err.type.name} not retryable',
    };
  }

  /// Calculate delay with exponential backoff and jitter
  Duration _calculateDelay(int attemptCount) {
    // Exponential backoff: baseDelay * 2^attemptCount
    final exponentialDelay = baseDelay * pow(2, attemptCount);

    // Add jitter if enabled (random value between 0-1000ms)
    final jitter = enableJitter
        ? Duration(milliseconds: Random().nextInt(1000))
        : Duration.zero;

    // Calculate total delay
    final totalDelay = exponentialDelay + jitter;

    // Cap at max delay
    return totalDelay > maxDelay ? maxDelay : totalDelay;
  }
}

/// Circuit breaker pattern implementation
class CircuitBreaker {
  final int failureThreshold;
  final Duration resetTimeout;
  final Duration halfOpenTimeout;

  CircuitBreakerState _state = CircuitBreakerState.closed;
  int _failureCount = 0;
  int _successCount = 0;
  DateTime? _lastFailureTime;
  DateTime? _stateChangedTime;

  CircuitBreaker({
    this.failureThreshold = 5,
    this.resetTimeout = const Duration(seconds: 60),
    this.halfOpenTimeout = const Duration(seconds: 30),
  }) {
    _stateChangedTime = DateTime.now();
  }

  /// Get current state
  CircuitBreakerState get state => _state;

  /// Get failure count
  int get failureCount => _failureCount;

  /// Get success count
  int get successCount => _successCount;

  /// Check if requests can be executed
  bool canExecute() {
    _checkState();
    return _state != CircuitBreakerState.open;
  }

  /// Record a successful request
  void recordSuccess() {
    _successCount++;

    if (_state == CircuitBreakerState.halfOpen) {
      // If we're in half-open and get a success, close the circuit
      _transitionTo(CircuitBreakerState.closed);
      _resetCounters();
      AppLogger.i(
        'Circuit breaker CLOSED after successful request',
        tag: 'CIRCUIT_BREAKER',
      );
    } else if (_state == CircuitBreakerState.closed) {
      // Reset failure count on success in closed state
      _failureCount = 0;
    }
  }

  /// Record a failed request
  void recordFailure() {
    _lastFailureTime = DateTime.now();
    _failureCount++;

    AppLogger.d(
      'Circuit breaker recorded failure ($_failureCount/$failureThreshold)',
      tag: 'CIRCUIT_BREAKER',
    );

    if (_state == CircuitBreakerState.halfOpen) {
      // If we're in half-open and get a failure, open the circuit
      _transitionTo(CircuitBreakerState.open);
      AppLogger.w(
        'Circuit breaker OPENED after failure in half-open state',
        tag: 'CIRCUIT_BREAKER',
      );
    } else if (_state == CircuitBreakerState.closed &&
        _failureCount >= failureThreshold) {
      // If we reach the failure threshold, open the circuit
      _transitionTo(CircuitBreakerState.open);
      AppLogger.w(
        'Circuit breaker OPENED after $failureThreshold failures',
        tag: 'CIRCUIT_BREAKER',
      );
    }
  }

  /// Check and update circuit breaker state based on time
  void _checkState() {
    if (_state == CircuitBreakerState.open) {
      // Check if we should transition to half-open
      final timeSinceStateChange =
          DateTime.now().difference(_stateChangedTime!);

      if (timeSinceStateChange >= resetTimeout) {
        _transitionTo(CircuitBreakerState.halfOpen);
        AppLogger.i(
          'Circuit breaker HALF-OPEN - testing recovery',
          tag: 'CIRCUIT_BREAKER',
        );
      }
    } else if (_state == CircuitBreakerState.halfOpen) {
      // Check if we should go back to open
      final timeSinceStateChange =
          DateTime.now().difference(_stateChangedTime!);

      if (timeSinceStateChange >= halfOpenTimeout && _successCount == 0) {
        _transitionTo(CircuitBreakerState.open);
        AppLogger.w(
          'Circuit breaker back to OPEN - no successful requests in half-open',
          tag: 'CIRCUIT_BREAKER',
        );
      }
    }
  }

  /// Transition to a new state
  void _transitionTo(CircuitBreakerState newState) {
    _state = newState;
    _stateChangedTime = DateTime.now();

    if (newState == CircuitBreakerState.halfOpen) {
      _resetCounters();
    }
  }

  /// Reset counters
  void _resetCounters() {
    _failureCount = 0;
    _successCount = 0;
  }

  /// Reset circuit breaker to closed state
  void reset() {
    _transitionTo(CircuitBreakerState.closed);
    _resetCounters();
    _lastFailureTime = null;
    AppLogger.i('Circuit breaker manually reset to CLOSED', tag: 'CIRCUIT_BREAKER');
  }

  /// Get status information
  Map<String, dynamic> getStatus() {
    return {
      'state': _state.name,
      'failureCount': _failureCount,
      'successCount': _successCount,
      'failureThreshold': failureThreshold,
      'lastFailureTime': _lastFailureTime?.toIso8601String(),
      'stateChangedTime': _stateChangedTime?.toIso8601String(),
    };
  }
}

/// Circuit breaker states
enum CircuitBreakerState {
  /// Circuit is closed - requests flow normally
  closed,

  /// Circuit is open - requests are blocked
  open,

  /// Circuit is half-open - testing if service recovered
  halfOpen,
}
