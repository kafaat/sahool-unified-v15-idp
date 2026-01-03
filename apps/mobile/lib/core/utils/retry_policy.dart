import 'dart:math';
import 'app_logger.dart';

/// Exponential Backoff Retry Policy with Circuit Breaker
///
/// Implements exponential backoff algorithm to prevent excessive API calls:
/// - Initial delay: 1 second
/// - Multiplier: 2x per retry
/// - Max delay: 5 minutes
/// - Max retries: 5
/// - Jitter to prevent thundering herd
class ExponentialBackoff {
  final int initialDelayMs;
  final double multiplier;
  final int maxDelayMs;
  final int maxRetries;
  final bool enableJitter;
  final Random _random = Random();

  ExponentialBackoff({
    this.initialDelayMs = 1000, // 1 second
    this.multiplier = 2.0,
    this.maxDelayMs = 300000, // 5 minutes
    this.maxRetries = 5,
    this.enableJitter = true,
  });

  /// Calculate delay for a given retry attempt
  /// Returns delay in milliseconds
  int calculateDelay(int retryCount) {
    if (retryCount >= maxRetries) {
      return maxDelayMs;
    }

    // Calculate exponential delay: initialDelay * (multiplier ^ retryCount)
    final exponentialDelay = initialDelayMs * pow(multiplier, retryCount);

    // Cap at max delay
    final cappedDelay = min(exponentialDelay, maxDelayMs.toDouble());

    // Add jitter if enabled (0-25% random variation)
    if (enableJitter) {
      final jitter = _random.nextDouble() * 0.25 * cappedDelay;
      return (cappedDelay + jitter).toInt();
    }

    return cappedDelay.toInt();
  }

  /// Calculate next retry time based on current retry count
  DateTime calculateNextRetryTime(int retryCount) {
    final delayMs = calculateDelay(retryCount);
    return DateTime.now().add(Duration(milliseconds: delayMs));
  }

  /// Check if should retry based on retry count
  bool shouldRetry(int retryCount) {
    return retryCount < maxRetries;
  }

  /// Get human-readable delay description
  String getDelayDescription(int retryCount) {
    final delayMs = calculateDelay(retryCount);

    if (delayMs < 1000) {
      return '${delayMs}ms';
    } else if (delayMs < 60000) {
      return '${(delayMs / 1000).toStringAsFixed(1)}s';
    } else {
      return '${(delayMs / 60000).toStringAsFixed(1)}m';
    }
  }

  /// Execute with exponential backoff
  /// Throws exception if all retries exhausted
  Future<T> execute<T>(
    Future<T> Function() operation, {
    int currentRetry = 0,
    Function(int retry, Duration delay)? onRetry,
  }) async {
    try {
      return await operation();
    } catch (e) {
      if (!shouldRetry(currentRetry)) {
        rethrow;
      }

      final delayMs = calculateDelay(currentRetry);
      final delay = Duration(milliseconds: delayMs);

      onRetry?.call(currentRetry, delay);

      await Future.delayed(delay);

      return execute(
        operation,
        currentRetry: currentRetry + 1,
        onRetry: onRetry,
      );
    }
  }
}

/// Circuit Breaker State
enum CircuitState { closed, open, halfOpen }

/// Circuit Breaker to prevent cascading failures
///
/// - Closed: Normal operation, requests pass through
/// - Open: Too many failures, all requests fail fast
/// - Half-Open: Testing if service recovered
class CircuitBreaker {
  final String name;
  final int failureThreshold;
  final Duration openTimeout;
  final int halfOpenMaxAttempts;

  CircuitState _state = CircuitState.closed;
  int _failureCount = 0;
  int _halfOpenAttempts = 0;
  DateTime? _lastFailureTime;
  DateTime? _openedAt;

  CircuitBreaker({
    required this.name,
    this.failureThreshold = 5,
    this.openTimeout = const Duration(minutes: 2),
    this.halfOpenMaxAttempts = 3,
  });

  CircuitState get state => _state;
  int get failureCount => _failureCount;
  DateTime? get lastFailureTime => _lastFailureTime;

  /// Check if circuit should allow request
  bool canAttempt() {
    if (_state == CircuitState.closed) {
      return true;
    }

    if (_state == CircuitState.open) {
      // Check if timeout elapsed
      if (_openedAt != null &&
          DateTime.now().difference(_openedAt!) > openTimeout) {
        _transitionToHalfOpen();
        return true;
      }
      return false;
    }

    // Half-open state
    return _halfOpenAttempts < halfOpenMaxAttempts;
  }

  /// Record successful operation
  void recordSuccess() {
    if (_state == CircuitState.halfOpen) {
      _transitionToClosed();
    }
    _failureCount = 0;
    _lastFailureTime = null;
  }

  /// Record failed operation
  void recordFailure() {
    _failureCount++;
    _lastFailureTime = DateTime.now();

    if (_state == CircuitState.halfOpen) {
      _halfOpenAttempts++;
      if (_halfOpenAttempts >= halfOpenMaxAttempts) {
        _transitionToOpen();
      }
    } else if (_state == CircuitState.closed) {
      if (_failureCount >= failureThreshold) {
        _transitionToOpen();
      }
    }
  }

  /// Reset circuit breaker
  void reset() {
    _state = CircuitState.closed;
    _failureCount = 0;
    _halfOpenAttempts = 0;
    _lastFailureTime = null;
    _openedAt = null;
  }

  void _transitionToOpen() {
    _state = CircuitState.open;
    _openedAt = DateTime.now();
    _halfOpenAttempts = 0;
    AppLogger.w('Circuit breaker OPEN - too many failures', tag: 'CircuitBreaker', data: {'name': name});
  }

  void _transitionToHalfOpen() {
    _state = CircuitState.halfOpen;
    _halfOpenAttempts = 0;
    AppLogger.i('Circuit breaker HALF-OPEN - testing recovery', tag: 'CircuitBreaker', data: {'name': name});
  }

  void _transitionToClosed() {
    _state = CircuitState.closed;
    _failureCount = 0;
    _halfOpenAttempts = 0;
    _openedAt = null;
    AppLogger.i('Circuit breaker CLOSED - service recovered', tag: 'CircuitBreaker', data: {'name': name});
  }

  /// Get human-readable state description
  String getStateDescription() {
    switch (_state) {
      case CircuitState.closed:
        return 'Normal';
      case CircuitState.open:
        final timeUntilRetry = _openedAt != null
            ? openTimeout - DateTime.now().difference(_openedAt!)
            : Duration.zero;
        return 'Failed (retry in ${timeUntilRetry.inSeconds}s)';
      case CircuitState.halfOpen:
        return 'Testing recovery';
    }
  }
}

/// Endpoint-specific retry tracker
class EndpointRetryTracker {
  final Map<String, CircuitBreaker> _circuitBreakers = {};
  final Map<String, int> _retryCounters = {};
  final Map<String, DateTime> _nextRetryTimes = {};
  final ExponentialBackoff backoffPolicy;

  EndpointRetryTracker({
    ExponentialBackoff? backoffPolicy,
  }) : backoffPolicy = backoffPolicy ?? ExponentialBackoff();

  /// Get or create circuit breaker for endpoint
  CircuitBreaker getCircuitBreaker(String endpoint) {
    return _circuitBreakers.putIfAbsent(
      endpoint,
      () => CircuitBreaker(
        name: endpoint,
        failureThreshold: 5,
        openTimeout: const Duration(minutes: 2),
      ),
    );
  }

  /// Check if endpoint can be retried now
  bool canRetryNow(String endpoint) {
    final circuitBreaker = getCircuitBreaker(endpoint);

    // Circuit breaker check
    if (!circuitBreaker.canAttempt()) {
      return false;
    }

    // Backoff time check
    final nextRetryTime = _nextRetryTimes[endpoint];
    if (nextRetryTime != null && DateTime.now().isBefore(nextRetryTime)) {
      return false;
    }

    return true;
  }

  /// Get current retry count for endpoint
  int getRetryCount(String endpoint) {
    return _retryCounters[endpoint] ?? 0;
  }

  /// Calculate next retry time for endpoint
  DateTime? getNextRetryTime(String endpoint) {
    return _nextRetryTimes[endpoint];
  }

  /// Record failure and calculate next retry time
  void recordFailure(String endpoint, int currentRetryCount) {
    final circuitBreaker = getCircuitBreaker(endpoint);
    circuitBreaker.recordFailure();

    _retryCounters[endpoint] = currentRetryCount;
    _nextRetryTimes[endpoint] =
        backoffPolicy.calculateNextRetryTime(currentRetryCount);
  }

  /// Record success and reset counters
  void recordSuccess(String endpoint) {
    final circuitBreaker = getCircuitBreaker(endpoint);
    circuitBreaker.recordSuccess();

    _retryCounters.remove(endpoint);
    _nextRetryTimes.remove(endpoint);
  }

  /// Get time until next retry for endpoint
  Duration? getTimeUntilRetry(String endpoint) {
    final nextRetryTime = _nextRetryTimes[endpoint];
    if (nextRetryTime == null) {
      return null;
    }

    final now = DateTime.now();
    if (now.isAfter(nextRetryTime)) {
      return Duration.zero;
    }

    return nextRetryTime.difference(now);
  }

  /// Get status for all endpoints
  Map<String, EndpointStatus> getAllEndpointStatuses() {
    final statuses = <String, EndpointStatus>{};

    for (final endpoint in _circuitBreakers.keys) {
      statuses[endpoint] = getEndpointStatus(endpoint);
    }

    return statuses;
  }

  /// Get status for specific endpoint
  EndpointStatus getEndpointStatus(String endpoint) {
    final circuitBreaker = getCircuitBreaker(endpoint);
    final retryCount = getRetryCount(endpoint);
    final nextRetryTime = getNextRetryTime(endpoint);
    final timeUntilRetry = getTimeUntilRetry(endpoint);

    return EndpointStatus(
      endpoint: endpoint,
      circuitState: circuitBreaker.state,
      retryCount: retryCount,
      failureCount: circuitBreaker.failureCount,
      nextRetryTime: nextRetryTime,
      timeUntilRetry: timeUntilRetry,
      canRetry: canRetryNow(endpoint),
    );
  }

  /// Reset all trackers
  void resetAll() {
    for (final breaker in _circuitBreakers.values) {
      breaker.reset();
    }
    _retryCounters.clear();
    _nextRetryTimes.clear();
  }

  /// Reset specific endpoint
  void resetEndpoint(String endpoint) {
    _circuitBreakers[endpoint]?.reset();
    _retryCounters.remove(endpoint);
    _nextRetryTimes.remove(endpoint);
  }
}

/// Endpoint status information
class EndpointStatus {
  final String endpoint;
  final CircuitState circuitState;
  final int retryCount;
  final int failureCount;
  final DateTime? nextRetryTime;
  final Duration? timeUntilRetry;
  final bool canRetry;

  EndpointStatus({
    required this.endpoint,
    required this.circuitState,
    required this.retryCount,
    required this.failureCount,
    this.nextRetryTime,
    this.timeUntilRetry,
    required this.canRetry,
  });

  bool get isHealthy => circuitState == CircuitState.closed && retryCount == 0;

  String get statusDescription {
    if (isHealthy) return 'Healthy';
    if (circuitState == CircuitState.open) return 'Circuit Open';
    if (circuitState == CircuitState.halfOpen) return 'Testing';
    if (!canRetry && timeUntilRetry != null) {
      return 'Retry in ${timeUntilRetry!.inSeconds}s';
    }
    return 'Retrying';
  }
}
