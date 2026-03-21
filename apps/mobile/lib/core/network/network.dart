/// SAHOOL Network Module
/// وحدة الشبكة
///
/// Provides robust network handling with:
/// - Exponential backoff retry logic
/// - Circuit breaker pattern
/// - Network quality monitoring
/// - Offline request queueing
/// - Per-endpoint retry policies
///
/// Usage:
/// ```dart
/// import 'package:sahool_field_app/core/network/network.dart';
///
/// // Create interceptor with default settings
/// final interceptor = RobustRetryInterceptor();
///
/// // Add to Dio
/// dio.interceptors.add(interceptor);
///
/// // Use custom policy for specific requests
/// final options = Options();
/// options.extra['retryPolicy'] = RetryPolicies.critical;
///
/// // Monitor network quality
/// interceptor.getNetworkQuality();
///
/// // Check circuit breaker status
/// interceptor.getCircuitBreakerHealth();
/// ```

library;

// API Result types
export 'api_result.dart';

// Error handling
export 'dio_error_handler.dart';

// Retry policies
export 'retry_policy.dart' show
    NetworkQuality,
    NetworkQualityExtension,
    EndpointCategory,
    RetryPolicy,
    RetryPolicies,
    RetryAttemptInfo,
    OnRetryCallback;

// Circuit breaker
export 'circuit_breaker.dart' show
    CircuitBreakerState,
    CircuitBreakerStateExtension,
    CircuitBreakerConfig,
    CircuitBreakerStatus,
    CircuitOpenException,
    CircuitBreaker,
    CircuitBreakerManager,
    CircuitBreakerHealthSummary;

// Retry interceptor
export 'retry_interceptor.dart' show
    NetworkQualityMonitor,
    QueuedNetworkRequest,
    RetryInterceptorStats,
    RobustRetryInterceptor,
    QueuedRequestException,
    RetryPolicyExtension,
    RetryOptionsExtension;
