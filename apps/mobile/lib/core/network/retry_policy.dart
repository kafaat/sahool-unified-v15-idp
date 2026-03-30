/// SAHOOL Network Retry Policy
/// سياسات إعادة المحاولة للشبكة
///
/// Provides configurable retry policies per endpoint type with:
/// - Exponential backoff (1s, 2s, 4s)
/// - Endpoint-specific configurations
/// - Network quality awareness
/// - Offline request queueing support
library;

import 'dart:math';

/// Network quality levels for adaptive retry behavior
enum NetworkQuality {
  /// Full connectivity, fast responses
  good,

  /// Connectivity present but slow
  slow,

  /// Connectivity present but very slow (>2s latency)
  verySlow,

  /// No network connectivity
  offline,

  /// Unknown network state
  unknown,
}

/// Extension for network quality descriptions
extension NetworkQualityExtension on NetworkQuality {
  /// Arabic description
  String get descriptionAr {
    switch (this) {
      case NetworkQuality.good:
        return 'الاتصال جيد';
      case NetworkQuality.slow:
        return 'الاتصال بطيء';
      case NetworkQuality.verySlow:
        return 'الاتصال بطيء جداً';
      case NetworkQuality.offline:
        return 'لا يوجد اتصال';
      case NetworkQuality.unknown:
        return 'حالة الاتصال غير معروفة';
    }
  }

  /// English description
  String get descriptionEn {
    switch (this) {
      case NetworkQuality.good:
        return 'Good connection';
      case NetworkQuality.slow:
        return 'Slow connection';
      case NetworkQuality.verySlow:
        return 'Very slow connection';
      case NetworkQuality.offline:
        return 'Offline';
      case NetworkQuality.unknown:
        return 'Unknown connection state';
    }
  }

  /// Check if requests should be queued
  bool get shouldQueueRequests => this == NetworkQuality.offline;

  /// Check if retry delays should be extended
  bool get shouldExtendDelays =>
      this == NetworkQuality.slow || this == NetworkQuality.verySlow;
}

/// Endpoint category for retry policy selection
enum EndpointCategory {
  /// Authentication endpoints (login, refresh, etc.)
  authentication,

  /// Critical data operations (field updates, task completion)
  critical,

  /// Standard CRUD operations
  standard,

  /// Analytics and non-essential data
  analytics,

  /// File uploads and downloads
  fileTransfer,

  /// Real-time data (weather, sensors)
  realtime,

  /// Background sync operations
  backgroundSync,
}

/// Retry policy configuration
class RetryPolicy {
  /// Maximum number of retry attempts
  final int maxRetries;

  /// Initial delay before first retry (in milliseconds)
  final int initialDelayMs;

  /// Maximum delay cap (in milliseconds)
  final int maxDelayMs;

  /// Backoff multiplier for exponential growth
  final double backoffMultiplier;

  /// Add random jitter to prevent thundering herd
  final bool enableJitter;

  /// Jitter factor (0.0 to 1.0) - percentage of delay to randomize
  final double jitterFactor;

  /// HTTP status codes that should trigger retry
  final Set<int> retryableStatusCodes;

  /// Whether to retry on connection timeout
  final bool retryOnTimeout;

  /// Whether to retry on connection errors
  final bool retryOnConnectionError;

  /// Whether to queue requests when offline
  final bool queueWhenOffline;

  /// Custom delay calculator (overrides exponential backoff)
  final int Function(int attempt)? customDelayCalculator;

  const RetryPolicy({
    this.maxRetries = 3,
    this.initialDelayMs = 1000,
    this.maxDelayMs = 30000,
    this.backoffMultiplier = 2.0,
    this.enableJitter = true,
    this.jitterFactor = 0.25,
    this.retryableStatusCodes = const {408, 429, 500, 502, 503, 504},
    this.retryOnTimeout = true,
    this.retryOnConnectionError = true,
    this.queueWhenOffline = true,
    this.customDelayCalculator,
  });

  /// Calculate delay for a given retry attempt
  /// Uses exponential backoff: initialDelay * (multiplier ^ attempt)
  int calculateDelay(int attempt, {NetworkQuality? networkQuality}) {
    if (customDelayCalculator != null) {
      return customDelayCalculator!(attempt);
    }

    // Calculate base exponential delay
    final exponentialDelay = initialDelayMs * pow(backoffMultiplier, attempt);

    // Cap at maximum delay
    var cappedDelay = min(exponentialDelay, maxDelayMs.toDouble());

    // Extend delay for slow networks
    if (networkQuality == NetworkQuality.slow) {
      cappedDelay *= 1.5;
    }

    // Add jitter if enabled
    if (enableJitter) {
      final random = Random();
      final jitter = random.nextDouble() * jitterFactor * cappedDelay;
      // Randomly add or subtract jitter
      final jitterSign = random.nextBool() ? 1 : -1;
      cappedDelay += jitter * jitterSign;
    }

    return cappedDelay.toInt().clamp(initialDelayMs, maxDelayMs);
  }

  /// Check if a status code is retryable
  bool isStatusCodeRetryable(int statusCode) {
    // Never retry client errors (4xx) except specific ones
    if (statusCode >= 400 && statusCode < 500) {
      return retryableStatusCodes.contains(statusCode);
    }

    // Server errors (5xx) are retryable if in the set
    if (statusCode >= 500) {
      return retryableStatusCodes.contains(statusCode);
    }

    return false;
  }

  /// Check if should retry based on attempt count
  bool shouldRetry(int currentAttempt) {
    return currentAttempt < maxRetries;
  }

  /// Get delay as Duration
  Duration getDelayDuration(int attempt, {NetworkQuality? networkQuality}) {
    return Duration(
        milliseconds: calculateDelay(attempt, networkQuality: networkQuality));
  }

  /// Copy with modifications
  RetryPolicy copyWith({
    int? maxRetries,
    int? initialDelayMs,
    int? maxDelayMs,
    double? backoffMultiplier,
    bool? enableJitter,
    double? jitterFactor,
    Set<int>? retryableStatusCodes,
    bool? retryOnTimeout,
    bool? retryOnConnectionError,
    bool? queueWhenOffline,
    int Function(int attempt)? customDelayCalculator,
  }) {
    return RetryPolicy(
      maxRetries: maxRetries ?? this.maxRetries,
      initialDelayMs: initialDelayMs ?? this.initialDelayMs,
      maxDelayMs: maxDelayMs ?? this.maxDelayMs,
      backoffMultiplier: backoffMultiplier ?? this.backoffMultiplier,
      enableJitter: enableJitter ?? this.enableJitter,
      jitterFactor: jitterFactor ?? this.jitterFactor,
      retryableStatusCodes: retryableStatusCodes ?? this.retryableStatusCodes,
      retryOnTimeout: retryOnTimeout ?? this.retryOnTimeout,
      retryOnConnectionError:
          retryOnConnectionError ?? this.retryOnConnectionError,
      queueWhenOffline: queueWhenOffline ?? this.queueWhenOffline,
      customDelayCalculator:
          customDelayCalculator ?? this.customDelayCalculator,
    );
  }

  @override
  String toString() {
    return 'RetryPolicy(maxRetries: $maxRetries, initialDelayMs: $initialDelayMs, '
        'backoffMultiplier: $backoffMultiplier, enableJitter: $enableJitter)';
  }
}

/// Pre-defined retry policies for different endpoint types
class RetryPolicies {
  RetryPolicies._();

  /// Default policy for most endpoints
  /// - 3 retries with exponential backoff (1s, 2s, 4s)
  /// - Retries on 5xx and specific 4xx codes
  static const RetryPolicy standard = RetryPolicy(
    maxRetries: 3,
    initialDelayMs: 1000,
    maxDelayMs: 30000,
    backoffMultiplier: 2.0,
    enableJitter: true,
    jitterFactor: 0.25,
    retryableStatusCodes: {408, 429, 500, 502, 503, 504},
    retryOnTimeout: true,
    retryOnConnectionError: true,
    queueWhenOffline: true,
  );

  /// Authentication endpoints - quick failure, minimal retries
  static const RetryPolicy authentication = RetryPolicy(
    maxRetries: 2,
    initialDelayMs: 500,
    maxDelayMs: 5000,
    backoffMultiplier: 2.0,
    enableJitter: false,
    retryableStatusCodes: {408, 429, 502, 503, 504},
    retryOnTimeout: true,
    retryOnConnectionError: true,
    queueWhenOffline: false, // Don't queue auth requests
  );

  /// Critical operations - more retries, longer delays
  static const RetryPolicy critical = RetryPolicy(
    maxRetries: 5,
    initialDelayMs: 1000,
    maxDelayMs: 60000,
    backoffMultiplier: 2.0,
    enableJitter: true,
    jitterFactor: 0.2,
    retryableStatusCodes: {408, 429, 500, 502, 503, 504},
    retryOnTimeout: true,
    retryOnConnectionError: true,
    queueWhenOffline: true,
  );

  /// Analytics - minimal retries, fail fast
  static const RetryPolicy analytics = RetryPolicy(
    maxRetries: 1,
    initialDelayMs: 500,
    maxDelayMs: 2000,
    backoffMultiplier: 1.5,
    enableJitter: false,
    retryableStatusCodes: {503, 504},
    retryOnTimeout: true,
    retryOnConnectionError: false,
    queueWhenOffline: false,
  );

  /// File transfers - longer delays, more patient
  static const RetryPolicy fileTransfer = RetryPolicy(
    maxRetries: 3,
    initialDelayMs: 2000,
    maxDelayMs: 120000,
    backoffMultiplier: 3.0,
    enableJitter: true,
    jitterFactor: 0.3,
    retryableStatusCodes: {408, 429, 500, 502, 503, 504},
    retryOnTimeout: true,
    retryOnConnectionError: true,
    queueWhenOffline: true,
  );

  /// Real-time data - fast retries for time-sensitive data
  static const RetryPolicy realtime = RetryPolicy(
    maxRetries: 2,
    initialDelayMs: 300,
    maxDelayMs: 3000,
    backoffMultiplier: 2.0,
    enableJitter: true,
    jitterFactor: 0.15,
    retryableStatusCodes: {502, 503, 504},
    retryOnTimeout: true,
    retryOnConnectionError: true,
    queueWhenOffline: false, // Real-time data should not be queued
  );

  /// Background sync - aggressive retries, patient delays
  static const RetryPolicy backgroundSync = RetryPolicy(
    maxRetries: 5,
    initialDelayMs: 2000,
    maxDelayMs: 300000, // 5 minutes max
    backoffMultiplier: 2.5,
    enableJitter: true,
    jitterFactor: 0.4,
    retryableStatusCodes: {408, 429, 500, 502, 503, 504},
    retryOnTimeout: true,
    retryOnConnectionError: true,
    queueWhenOffline: true,
  );

  /// No retry - for endpoints that should not retry
  static const RetryPolicy none = RetryPolicy(
    maxRetries: 0,
    initialDelayMs: 0,
    retryOnTimeout: false,
    retryOnConnectionError: false,
    queueWhenOffline: false,
  );

  /// Get policy for endpoint category
  static RetryPolicy forCategory(EndpointCategory category) {
    switch (category) {
      case EndpointCategory.authentication:
        return authentication;
      case EndpointCategory.critical:
        return critical;
      case EndpointCategory.standard:
        return standard;
      case EndpointCategory.analytics:
        return analytics;
      case EndpointCategory.fileTransfer:
        return fileTransfer;
      case EndpointCategory.realtime:
        return realtime;
      case EndpointCategory.backgroundSync:
        return backgroundSync;
    }
  }

  /// Get policy based on endpoint path
  static RetryPolicy forPath(String path) {
    // Authentication endpoints
    if (path.contains('/auth/') || path.contains('/login') || path.contains('/token')) {
      return authentication;
    }

    // Critical endpoints (field operations, tasks)
    if (path.contains('/fields') && !path.contains('/sync')) {
      return critical;
    }
    if (path.contains('/tasks')) {
      return critical;
    }

    // Analytics endpoints
    if (path.contains('/analytics') || path.contains('/metrics') || path.contains('/stats')) {
      return analytics;
    }

    // File transfer endpoints
    if (path.contains('/upload') || path.contains('/download') || path.contains('/files')) {
      return fileTransfer;
    }

    // Real-time data endpoints
    if (path.contains('/weather/current') || path.contains('/sensors/') || path.contains('/alerts')) {
      return realtime;
    }

    // Sync endpoints
    if (path.contains('/sync')) {
      return backgroundSync;
    }

    // Default to standard policy
    return standard;
  }
}

/// Retry attempt information
class RetryAttemptInfo {
  /// Current attempt number (0-indexed)
  final int attempt;

  /// Maximum attempts allowed
  final int maxAttempts;

  /// Delay before next retry
  final Duration delay;

  /// HTTP status code that triggered retry (if applicable)
  final int? statusCode;

  /// Error message
  final String? errorMessage;

  /// Timestamp of this attempt
  final DateTime timestamp;

  /// Network quality at time of attempt
  final NetworkQuality networkQuality;

  const RetryAttemptInfo({
    required this.attempt,
    required this.maxAttempts,
    required this.delay,
    this.statusCode,
    this.errorMessage,
    required this.timestamp,
    this.networkQuality = NetworkQuality.unknown,
  });

  /// Check if this is the final attempt
  bool get isFinalAttempt => attempt >= maxAttempts - 1;

  /// Get remaining attempts
  int get remainingAttempts => maxAttempts - attempt - 1;

  /// Human-readable status
  String get statusDescription {
    if (isFinalAttempt) {
      return 'Final attempt';
    }
    return 'Attempt ${attempt + 1}/$maxAttempts, retrying in ${delay.inSeconds}s';
  }

  /// Arabic status description
  String get statusDescriptionAr {
    if (isFinalAttempt) {
      return 'المحاولة الأخيرة';
    }
    return 'المحاولة ${attempt + 1}/$maxAttempts، إعادة المحاولة خلال ${delay.inSeconds} ثانية';
  }

  @override
  String toString() {
    return 'RetryAttemptInfo(attempt: ${attempt + 1}/$maxAttempts, '
        'delay: ${delay.inMilliseconds}ms, statusCode: $statusCode)';
  }
}

/// Callback type for retry events
typedef OnRetryCallback = void Function(RetryAttemptInfo info);
