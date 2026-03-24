/// SAHOOL Network Circuit Breaker
/// قاطع الدائرة للشبكة
///
/// Implements the circuit breaker pattern for network resilience:
/// - Opens after 5 consecutive failures
/// - Auto-recovers after 30 seconds
/// - Half-open state for testing recovery
/// - Per-endpoint tracking
library;

import 'dart:async';
import '../utils/app_logger.dart';

/// Circuit breaker states
enum CircuitBreakerState {
  /// Normal operation - requests pass through
  closed,

  /// Circuit is open - requests fail fast
  open,

  /// Testing recovery - limited requests allowed
  halfOpen,
}

/// Extension for circuit breaker state descriptions
extension CircuitBreakerStateExtension on CircuitBreakerState {
  /// Arabic description
  String get descriptionAr {
    switch (this) {
      case CircuitBreakerState.closed:
        return 'عادي - الطلبات تمر';
      case CircuitBreakerState.open:
        return 'مفتوح - الطلبات محظورة';
      case CircuitBreakerState.halfOpen:
        return 'اختبار - التعافي قيد الفحص';
    }
  }

  /// English description
  String get descriptionEn {
    switch (this) {
      case CircuitBreakerState.closed:
        return 'Normal - requests pass through';
      case CircuitBreakerState.open:
        return 'Open - requests blocked';
      case CircuitBreakerState.halfOpen:
        return 'Testing - recovery in progress';
    }
  }
}

/// Configuration for circuit breaker behavior
class CircuitBreakerConfig {
  /// Number of consecutive failures before opening circuit
  final int failureThreshold;

  /// Duration to wait before attempting recovery (default: 30 seconds)
  final Duration recoveryTimeout;

  /// Number of successful requests in half-open state to close circuit
  final int successThreshold;

  /// Maximum number of requests allowed in half-open state
  final int halfOpenMaxRequests;

  /// Whether to track failures per endpoint or globally
  final bool perEndpointTracking;

  /// Sliding window duration for failure counting
  final Duration? slidingWindowDuration;

  const CircuitBreakerConfig({
    this.failureThreshold = 5,
    this.recoveryTimeout = const Duration(seconds: 30),
    this.successThreshold = 2,
    this.halfOpenMaxRequests = 3,
    this.perEndpointTracking = true,
    this.slidingWindowDuration,
  })  : assert(failureThreshold > 0, 'failureThreshold must be > 0'),
        assert(successThreshold > 0, 'successThreshold must be > 0'),
        assert(halfOpenMaxRequests > 0, 'halfOpenMaxRequests must be > 0');

  /// Default configuration
  static const CircuitBreakerConfig standard = CircuitBreakerConfig(
    failureThreshold: 5,
    recoveryTimeout: Duration(seconds: 30),
    successThreshold: 2,
    halfOpenMaxRequests: 3,
  );

  /// Aggressive configuration - opens faster, recovers slower
  static const CircuitBreakerConfig aggressive = CircuitBreakerConfig(
    failureThreshold: 3,
    recoveryTimeout: Duration(seconds: 60),
    successThreshold: 3,
    halfOpenMaxRequests: 2,
  );

  /// Lenient configuration - opens slower, recovers faster
  static const CircuitBreakerConfig lenient = CircuitBreakerConfig(
    failureThreshold: 10,
    recoveryTimeout: Duration(seconds: 15),
    successThreshold: 1,
    halfOpenMaxRequests: 5,
  );

  /// Copy with modifications
  CircuitBreakerConfig copyWith({
    int? failureThreshold,
    Duration? recoveryTimeout,
    int? successThreshold,
    int? halfOpenMaxRequests,
    bool? perEndpointTracking,
    Duration? slidingWindowDuration,
  }) {
    return CircuitBreakerConfig(
      failureThreshold: failureThreshold ?? this.failureThreshold,
      recoveryTimeout: recoveryTimeout ?? this.recoveryTimeout,
      successThreshold: successThreshold ?? this.successThreshold,
      halfOpenMaxRequests: halfOpenMaxRequests ?? this.halfOpenMaxRequests,
      perEndpointTracking: perEndpointTracking ?? this.perEndpointTracking,
      slidingWindowDuration:
          slidingWindowDuration ?? this.slidingWindowDuration,
    );
  }
}

/// Failure record for tracking
class FailureRecord {
  final DateTime timestamp;
  final String? errorMessage;
  final int? statusCode;
  final String? endpoint;

  const FailureRecord({
    required this.timestamp,
    this.errorMessage,
    this.statusCode,
    this.endpoint,
  });
}

/// Circuit breaker status information
class CircuitBreakerStatus {
  /// Current state of the circuit
  final CircuitBreakerState state;

  /// Number of consecutive failures
  final int failureCount;

  /// Number of successful requests in half-open state
  final int halfOpenSuccessCount;

  /// Number of requests attempted in half-open state
  final int halfOpenRequestCount;

  /// Time when circuit was opened
  final DateTime? openedAt;

  /// Time when circuit will attempt recovery
  final DateTime? nextRecoveryAttempt;

  /// Last failure time
  final DateTime? lastFailureTime;

  /// Configuration being used
  final CircuitBreakerConfig config;

  const CircuitBreakerStatus({
    required this.state,
    required this.failureCount,
    this.halfOpenSuccessCount = 0,
    this.halfOpenRequestCount = 0,
    this.openedAt,
    this.nextRecoveryAttempt,
    this.lastFailureTime,
    required this.config,
  });

  /// Check if circuit is allowing requests
  bool get isAllowingRequests =>
      state == CircuitBreakerState.closed ||
      (state == CircuitBreakerState.halfOpen &&
          halfOpenRequestCount < config.halfOpenMaxRequests);

  /// Get time until recovery attempt
  Duration? get timeUntilRecovery {
    if (nextRecoveryAttempt == null) return null;
    final now = DateTime.now();
    if (now.isAfter(nextRecoveryAttempt!)) return Duration.zero;
    return nextRecoveryAttempt!.difference(now);
  }

  /// Get failure ratio (failures / threshold)
  double get failureRatio => failureCount / config.failureThreshold;

  @override
  String toString() {
    return 'CircuitBreakerStatus(state: ${state.name}, '
        'failures: $failureCount/${config.failureThreshold}, '
        'isAllowing: $isAllowingRequests)';
  }
}

/// Exception thrown when circuit is open
class CircuitOpenException implements Exception {
  final String message;
  final String? endpoint;
  final Duration? timeUntilRecovery;

  const CircuitOpenException({
    this.message = 'Circuit breaker is open',
    this.endpoint,
    this.timeUntilRecovery,
  });

  @override
  String toString() {
    final buffer = StringBuffer('CircuitOpenException: $message');
    if (endpoint != null) {
      buffer.write(' (endpoint: $endpoint)');
    }
    if (timeUntilRecovery != null) {
      buffer.write(' - retry in ${timeUntilRecovery!.inSeconds}s');
    }
    return buffer.toString();
  }
}

/// Circuit breaker implementation
class CircuitBreaker {
  /// Name for identification/logging
  final String name;

  /// Configuration
  final CircuitBreakerConfig config;

  /// Current state
  CircuitBreakerState _state = CircuitBreakerState.closed;

  /// Failure records for sliding window
  final List<FailureRecord> _failureRecords = [];

  /// Success count in half-open state
  int _halfOpenSuccessCount = 0;

  /// Request count in half-open state
  int _halfOpenRequestCount = 0;

  /// Time when circuit was opened
  DateTime? _openedAt;

  /// Timer for automatic recovery
  Timer? _recoveryTimer;

  /// Stream controller for state changes
  final _stateController = StreamController<CircuitBreakerStatus>.broadcast();

  CircuitBreaker({
    required this.name,
    this.config = const CircuitBreakerConfig(),
  });

  /// Current state
  CircuitBreakerState get state => _state;

  /// Get current status
  CircuitBreakerStatus get status => CircuitBreakerStatus(
        state: _state,
        failureCount: _failureRecords.length,
        halfOpenSuccessCount: _halfOpenSuccessCount,
        halfOpenRequestCount: _halfOpenRequestCount,
        openedAt: _openedAt,
        nextRecoveryAttempt: _openedAt?.add(config.recoveryTimeout),
        lastFailureTime: _failureRecords.isNotEmpty
            ? _failureRecords.last.timestamp
            : null,
        config: config,
      );

  /// Stream of status changes
  Stream<CircuitBreakerStatus> get statusStream => _stateController.stream;

  /// Check if circuit allows request
  bool canAttemptRequest() {
    _cleanupOldFailures();

    switch (_state) {
      case CircuitBreakerState.closed:
        return true;

      case CircuitBreakerState.open:
        // Check if recovery timeout has elapsed
        if (_openedAt != null &&
            DateTime.now().difference(_openedAt!) >= config.recoveryTimeout) {
          _transitionToHalfOpen();
          return true;
        }
        return false;

      case CircuitBreakerState.halfOpen:
        return _halfOpenRequestCount < config.halfOpenMaxRequests;
    }
  }

  /// Record a successful request
  void recordSuccess() {
    _cleanupOldFailures();

    switch (_state) {
      case CircuitBreakerState.closed:
        // Clear failures on success in closed state
        _failureRecords.clear();
        break;

      case CircuitBreakerState.halfOpen:
        _halfOpenSuccessCount++;
        if (_halfOpenSuccessCount >= config.successThreshold) {
          _transitionToClosed();
        }
        break;

      case CircuitBreakerState.open:
        // Shouldn't happen, but handle gracefully
        break;
    }

    _notifyStatusChange();
  }

  /// Record a failed request
  void recordFailure({
    String? errorMessage,
    int? statusCode,
    String? endpoint,
  }) {
    _cleanupOldFailures();

    final record = FailureRecord(
      timestamp: DateTime.now(),
      errorMessage: errorMessage,
      statusCode: statusCode,
      endpoint: endpoint,
    );

    _failureRecords.add(record);

    switch (_state) {
      case CircuitBreakerState.closed:
        if (_failureRecords.length >= config.failureThreshold) {
          _transitionToOpen();
        }
        break;

      case CircuitBreakerState.halfOpen:
        _halfOpenRequestCount++;
        // Single failure in half-open state reopens the circuit
        _transitionToOpen();
        break;

      case CircuitBreakerState.open:
        // Already open, just recording
        break;
    }

    _notifyStatusChange();
  }

  /// Record that a request was attempted (for half-open tracking)
  void recordAttempt() {
    if (_state == CircuitBreakerState.halfOpen) {
      _halfOpenRequestCount++;
      _notifyStatusChange();
    }
  }

  /// Force transition to a specific state (for testing/manual override)
  void forceState(CircuitBreakerState newState) {
    _cancelRecoveryTimer();

    switch (newState) {
      case CircuitBreakerState.closed:
        _transitionToClosed();
        break;
      case CircuitBreakerState.open:
        _transitionToOpen();
        break;
      case CircuitBreakerState.halfOpen:
        _transitionToHalfOpen();
        break;
    }
  }

  /// Reset the circuit breaker to initial state
  void reset() {
    _cancelRecoveryTimer();
    _state = CircuitBreakerState.closed;
    _failureRecords.clear();
    _halfOpenSuccessCount = 0;
    _halfOpenRequestCount = 0;
    _openedAt = null;

    AppLogger.i(
      'Circuit breaker reset',
      tag: 'CircuitBreaker',
      data: {'name': name},
    );

    _notifyStatusChange();
  }

  /// Execute an operation with circuit breaker protection
  Future<T> execute<T>(Future<T> Function() operation) async {
    if (!canAttemptRequest()) {
      throw CircuitOpenException(
        message: 'Circuit breaker [$name] is open',
        timeUntilRecovery: status.timeUntilRecovery,
      );
    }

    recordAttempt();

    try {
      final result = await operation();
      recordSuccess();
      return result;
    } catch (e) {
      recordFailure(errorMessage: e.toString());
      rethrow;
    }
  }

  void _transitionToOpen() {
    final previousState = _state;
    _state = CircuitBreakerState.open;
    _openedAt = DateTime.now();
    _halfOpenSuccessCount = 0;
    _halfOpenRequestCount = 0;

    // Start recovery timer
    _startRecoveryTimer();

    AppLogger.w(
      'Circuit breaker OPENED',
      tag: 'CircuitBreaker',
      data: {
        'name': name,
        'previousState': previousState.name,
        'failureCount': _failureRecords.length,
        'recoveryTimeout': '${config.recoveryTimeout.inSeconds}s',
      },
    );
  }

  void _transitionToHalfOpen() {
    final previousState = _state;
    _state = CircuitBreakerState.halfOpen;
    _halfOpenSuccessCount = 0;
    _halfOpenRequestCount = 0;
    _cancelRecoveryTimer();

    AppLogger.i(
      'Circuit breaker HALF-OPEN - testing recovery',
      tag: 'CircuitBreaker',
      data: {
        'name': name,
        'previousState': previousState.name,
        'maxRequests': config.halfOpenMaxRequests,
        'successThreshold': config.successThreshold,
      },
    );
  }

  void _transitionToClosed() {
    final previousState = _state;
    _state = CircuitBreakerState.closed;
    _failureRecords.clear();
    _halfOpenSuccessCount = 0;
    _halfOpenRequestCount = 0;
    _openedAt = null;
    _cancelRecoveryTimer();

    AppLogger.i(
      'Circuit breaker CLOSED - service recovered',
      tag: 'CircuitBreaker',
      data: {
        'name': name,
        'previousState': previousState.name,
      },
    );
  }

  void _startRecoveryTimer() {
    _cancelRecoveryTimer();
    _recoveryTimer = Timer(config.recoveryTimeout, () {
      if (_state == CircuitBreakerState.open) {
        _transitionToHalfOpen();
        _notifyStatusChange();
      }
    });
  }

  void _cancelRecoveryTimer() {
    _recoveryTimer?.cancel();
    _recoveryTimer = null;
  }

  void _cleanupOldFailures() {
    if (config.slidingWindowDuration == null) return;

    final cutoff = DateTime.now().subtract(config.slidingWindowDuration!);
    _failureRecords.removeWhere((record) => record.timestamp.isBefore(cutoff));
  }

  void _notifyStatusChange() {
    if (!_stateController.isClosed) {
      _stateController.add(status);
    }
  }

  void dispose() {
    _cancelRecoveryTimer();
    _stateController.close();
  }
}

/// Manager for multiple circuit breakers (per-endpoint tracking)
class CircuitBreakerManager {
  /// Configuration for new circuit breakers
  final CircuitBreakerConfig defaultConfig;

  /// Circuit breakers by endpoint/name
  final Map<String, CircuitBreaker> _breakers = {};

  /// Stream controller for overall status
  final _statusController =
      StreamController<Map<String, CircuitBreakerStatus>>.broadcast();

  CircuitBreakerManager({
    this.defaultConfig = const CircuitBreakerConfig(),
  });

  /// Get or create circuit breaker for an endpoint
  CircuitBreaker getBreaker(String name, {CircuitBreakerConfig? config}) {
    return _breakers.putIfAbsent(
      name,
      () {
        final breaker = CircuitBreaker(
          name: name,
          config: config ?? defaultConfig,
        );
        // Subscribe to changes
        breaker.statusStream.listen((_) => _notifyStatusChange());
        return breaker;
      },
    );
  }

  /// Check if any circuit is open
  bool get hasOpenCircuits =>
      _breakers.values.any((b) => b.state == CircuitBreakerState.open);

  /// Get all open circuit names
  List<String> get openCircuitNames => _breakers.entries
      .where((e) => e.value.state == CircuitBreakerState.open)
      .map((e) => e.key)
      .toList();

  /// Get status for all circuit breakers
  Map<String, CircuitBreakerStatus> getAllStatuses() {
    return Map.fromEntries(
      _breakers.entries.map((e) => MapEntry(e.key, e.value.status)),
    );
  }

  /// Stream of all circuit breaker statuses
  Stream<Map<String, CircuitBreakerStatus>> get statusStream =>
      _statusController.stream;

  /// Check if a specific endpoint can accept requests
  bool canAttemptRequest(String name) {
    final breaker = _breakers[name];
    return breaker?.canAttemptRequest() ?? true;
  }

  /// Record success for an endpoint
  void recordSuccess(String name) {
    _breakers[name]?.recordSuccess();
  }

  /// Record failure for an endpoint
  void recordFailure(
    String name, {
    String? errorMessage,
    int? statusCode,
  }) {
    final breaker = getBreaker(name);
    breaker.recordFailure(
      errorMessage: errorMessage,
      statusCode: statusCode,
      endpoint: name,
    );
  }

  /// Reset a specific circuit breaker
  void resetBreaker(String name) {
    _breakers[name]?.reset();
  }

  /// Reset all circuit breakers
  void resetAll() {
    for (final breaker in _breakers.values) {
      breaker.reset();
    }
  }

  /// Get health summary
  CircuitBreakerHealthSummary getHealthSummary() {
    final int total = _breakers.length;
    int closed = 0;
    int open = 0;
    int halfOpen = 0;

    for (final breaker in _breakers.values) {
      switch (breaker.state) {
        case CircuitBreakerState.closed:
          closed++;
          break;
        case CircuitBreakerState.open:
          open++;
          break;
        case CircuitBreakerState.halfOpen:
          halfOpen++;
          break;
      }
    }

    return CircuitBreakerHealthSummary(
      total: total,
      closed: closed,
      open: open,
      halfOpen: halfOpen,
    );
  }

  void _notifyStatusChange() {
    if (!_statusController.isClosed) {
      _statusController.add(getAllStatuses());
    }
  }

  void dispose() {
    for (final breaker in _breakers.values) {
      breaker.dispose();
    }
    _breakers.clear();
    _statusController.close();
  }
}

/// Health summary for circuit breakers
class CircuitBreakerHealthSummary {
  final int total;
  final int closed;
  final int open;
  final int halfOpen;

  const CircuitBreakerHealthSummary({
    required this.total,
    required this.closed,
    required this.open,
    required this.halfOpen,
  });

  /// Overall health percentage (closed circuits / total)
  double get healthPercentage => total > 0 ? (closed / total) * 100 : 100;

  /// Check if all circuits are healthy
  bool get isHealthy => open == 0 && halfOpen == 0;

  /// Check if there are critical issues
  bool get hasCriticalIssues => open > 0;

  /// Get health status description
  String get statusDescription {
    if (isHealthy) return 'All services operational';
    if (hasCriticalIssues) return '$open service(s) experiencing issues';
    return '$halfOpen service(s) recovering';
  }

  /// Arabic description
  String get statusDescriptionAr {
    if (isHealthy) return 'جميع الخدمات تعمل';
    if (hasCriticalIssues) return '$open خدمة(خدمات) تواجه مشاكل';
    return '$halfOpen خدمة(خدمات) قيد التعافي';
  }

  @override
  String toString() {
    return 'CircuitBreakerHealthSummary(total: $total, '
        'closed: $closed, open: $open, halfOpen: $halfOpen, '
        'health: ${healthPercentage.toStringAsFixed(1)}%)';
  }
}
