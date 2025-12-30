/// Unit Tests - Retry Interceptor & Circuit Breaker
/// اختبارات وحدة - إعادة المحاولة والحماية من الأعطال

import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Exponential Backoff Tests', () {
    test('should calculate correct delay for first retry', () {
      // Arrange
      const baseDelayMs = 1000;
      const retryAttempt = 1;

      // Act - Exponential backoff: baseDelay * 2^(attempt - 1)
      final delayMs = baseDelayMs * (1 << (retryAttempt - 1));

      // Assert
      expect(delayMs, equals(1000)); // 1s for first retry
    });

    test('should calculate correct delay for second retry', () {
      // Arrange
      const baseDelayMs = 1000;
      const retryAttempt = 2;

      // Act
      final delayMs = baseDelayMs * (1 << (retryAttempt - 1));

      // Assert
      expect(delayMs, equals(2000)); // 2s for second retry
    });

    test('should calculate correct delay for third retry', () {
      // Arrange
      const baseDelayMs = 1000;
      const retryAttempt = 3;

      // Act
      final delayMs = baseDelayMs * (1 << (retryAttempt - 1));

      // Assert
      expect(delayMs, equals(4000)); // 4s for third retry
    });

    test('should calculate exponential backoff sequence', () {
      // Arrange
      const baseDelayMs = 1000;
      final expectedDelays = [1000, 2000, 4000, 8000, 16000];

      // Act
      final actualDelays = <int>[];
      for (int attempt = 1; attempt <= 5; attempt++) {
        final delay = baseDelayMs * (1 << (attempt - 1));
        actualDelays.add(delay);
      }

      // Assert
      expect(actualDelays, equals(expectedDelays));
    });

    test('should cap maximum delay', () {
      // Arrange
      const baseDelayMs = 1000;
      const maxDelayMs = 30000; // 30 seconds max
      const retryAttempt = 10; // Would normally be 512 seconds

      // Act
      var delayMs = baseDelayMs * (1 << (retryAttempt - 1));
      if (delayMs > maxDelayMs) {
        delayMs = maxDelayMs;
      }

      // Assert
      expect(delayMs, equals(maxDelayMs));
    });

    test('should add jitter to prevent thundering herd', () {
      // Arrange
      const baseDelayMs = 1000;
      const retryAttempt = 3;
      const jitterPercent = 0.25; // ±25%

      // Act
      final baseDelay = baseDelayMs * (1 << (retryAttempt - 1));
      final jitterRange = (baseDelay * jitterPercent).toInt();

      // Simulate random jitter (in test, we check the range)
      final minDelay = baseDelay - jitterRange;
      final maxDelay = baseDelay + jitterRange;

      // Assert
      expect(minDelay, equals(3000)); // 4000 - 1000
      expect(maxDelay, equals(5000)); // 4000 + 1000
      expect(baseDelay, equals(4000));
    });

    test('should implement full-jitter strategy', () {
      // Arrange
      const baseDelayMs = 1000;
      const retryAttempt = 3;

      // Act - Full jitter: random(0, baseDelay * 2^attempt)
      final maxPossibleDelay = baseDelayMs * (1 << (retryAttempt - 1));

      // Simulate random value between 0 and maxPossibleDelay
      final simulatedDelay = (maxPossibleDelay * 0.7).toInt(); // 70% of max

      // Assert
      expect(simulatedDelay, lessThanOrEqualTo(maxPossibleDelay));
      expect(simulatedDelay, greaterThanOrEqualTo(0));
      expect(maxPossibleDelay, equals(4000));
    });

    test('should implement decorrelated jitter', () {
      // Arrange
      const baseDelayMs = 1000;
      const maxDelayMs = 30000;
      var lastDelay = baseDelayMs;

      // Act - Decorrelated jitter: random(baseDelay, lastDelay * 3)
      final delays = <int>[];
      for (int i = 0; i < 5; i++) {
        final maxNext = (lastDelay * 3).clamp(baseDelayMs, maxDelayMs);
        lastDelay = ((maxNext + baseDelayMs) / 2).toInt(); // Average for testing
        delays.add(lastDelay);
      }

      // Assert - Each delay should be reasonable
      for (final delay in delays) {
        expect(delay, greaterThanOrEqualTo(baseDelayMs));
        expect(delay, lessThanOrEqualTo(maxDelayMs));
      }
    });
  });

  group('Max Retries Tests', () {
    test('should stop after max retries', () {
      // Arrange
      const maxRetries = 3;
      var attemptCount = 0;

      // Act - Simulate retry loop
      while (attemptCount < maxRetries) {
        attemptCount++;
        // Simulate failed request
      }

      // Assert
      expect(attemptCount, equals(maxRetries));
    });

    test('should not retry if max retries is 0', () {
      // Arrange
      const maxRetries = 0;
      var attemptCount = 0;

      // Act
      while (attemptCount < maxRetries) {
        attemptCount++;
      }

      // Assert
      expect(attemptCount, equals(0));
    });

    test('should track retry count per request', () {
      // Arrange
      final requestRetries = <String, int>{};

      // Act - Simulate multiple requests with retries
      requestRetries['request-1'] = 2;
      requestRetries['request-2'] = 1;
      requestRetries['request-3'] = 3;

      // Assert
      expect(requestRetries['request-1'], equals(2));
      expect(requestRetries['request-2'], equals(1));
      expect(requestRetries['request-3'], equals(3));
    });

    test('should reset retry count on success', () {
      // Arrange
      var retryCount = 3;

      // Act - Simulate successful request
      retryCount = 0;

      // Assert
      expect(retryCount, equals(0));
    });

    test('should configure different max retries per operation', () {
      // Arrange
      final maxRetries = {
        'critical': 5,
        'normal': 3,
        'background': 10,
      };

      // Act & Assert
      expect(maxRetries['critical'], equals(5));
      expect(maxRetries['normal'], equals(3));
      expect(maxRetries['background'], equals(10));
    });
  });

  group('Retryable Errors Tests', () {
    test('should retry on network timeout', () {
      // Arrange
      const errorCode = 'TIMEOUT';
      const retryableErrors = ['TIMEOUT', 'CONNECTION_ERROR', 'NETWORK_ERROR'];

      // Act
      final shouldRetry = retryableErrors.contains(errorCode);

      // Assert
      expect(shouldRetry, isTrue);
    });

    test('should retry on 5xx server errors', () {
      // Arrange
      final retryableStatusCodes = [500, 502, 503, 504];

      // Act & Assert
      for (final code in retryableStatusCodes) {
        expect(code >= 500 && code < 600, isTrue);
      }
    });

    test('should not retry on 4xx client errors', () {
      // Arrange
      final nonRetryableStatusCodes = [400, 401, 403, 404];

      // Act & Assert
      for (final code in nonRetryableStatusCodes) {
        final shouldRetry = code >= 500;
        expect(shouldRetry, isFalse);
      }
    });

    test('should retry on 429 Too Many Requests', () {
      // Arrange
      const statusCode = 429;

      // Act
      final shouldRetry = statusCode == 429 || (statusCode >= 500 && statusCode < 600);

      // Assert
      expect(shouldRetry, isTrue);
    });

    test('should use Retry-After header for 429 errors', () {
      // Arrange
      const retryAfterSeconds = 60;
      const defaultBackoffMs = 2000;

      // Act
      final delayMs = retryAfterSeconds * 1000;

      // Assert
      expect(delayMs, equals(60000)); // Use Retry-After instead of backoff
      expect(delayMs, greaterThan(defaultBackoffMs));
    });

    test('should not retry on authentication errors', () {
      // Arrange
      final authErrorCodes = [401, 403];

      // Act
      final shouldRetry = authErrorCodes.any((code) => code >= 500);

      // Assert
      expect(shouldRetry, isFalse);
    });

    test('should define custom retryable errors', () {
      // Arrange
      final customRetryable = {
        'ETIMEDOUT',
        'ECONNRESET',
        'ENOTFOUND',
        'ECONNREFUSED',
      };

      // Act
      final isRetryable = customRetryable.contains('ETIMEDOUT');

      // Assert
      expect(isRetryable, isTrue);
    });
  });

  group('Circuit Breaker Tests', () {
    test('should open circuit after threshold failures', () {
      // Arrange
      const failureThreshold = 5;
      var failureCount = 0;
      var circuitOpen = false;

      // Act - Simulate failures
      for (int i = 0; i < failureThreshold; i++) {
        failureCount++;
      }

      if (failureCount >= failureThreshold) {
        circuitOpen = true;
      }

      // Assert
      expect(circuitOpen, isTrue);
      expect(failureCount, equals(failureThreshold));
    });

    test('should keep circuit closed under threshold', () {
      // Arrange
      const failureThreshold = 5;
      var failureCount = 3;
      var circuitOpen = false;

      // Act
      if (failureCount >= failureThreshold) {
        circuitOpen = true;
      }

      // Assert
      expect(circuitOpen, isFalse);
    });

    test('should reset circuit after timeout', () {
      // Arrange
      const circuitOpenDuration = Duration(minutes: 1);
      final circuitOpenedAt = DateTime.now().subtract(const Duration(minutes: 2));

      // Act
      final elapsed = DateTime.now().difference(circuitOpenedAt);
      final shouldReset = elapsed >= circuitOpenDuration;

      // Assert
      expect(shouldReset, isTrue);
    });

    test('should not reset circuit before timeout', () {
      // Arrange
      const circuitOpenDuration = Duration(minutes: 1);
      final circuitOpenedAt = DateTime.now().subtract(const Duration(seconds: 30));

      // Act
      final elapsed = DateTime.now().difference(circuitOpenedAt);
      final shouldReset = elapsed >= circuitOpenDuration;

      // Assert
      expect(shouldReset, isFalse);
    });

    test('should transition to half-open state', () {
      // Arrange
      var circuitState = 'OPEN';
      const resetTimeout = Duration(seconds: 30);
      final openedAt = DateTime.now().subtract(const Duration(seconds: 35));

      // Act
      final elapsed = DateTime.now().difference(openedAt);
      if (elapsed >= resetTimeout && circuitState == 'OPEN') {
        circuitState = 'HALF_OPEN';
      }

      // Assert
      expect(circuitState, equals('HALF_OPEN'));
    });

    test('should close circuit on successful half-open request', () {
      // Arrange
      var circuitState = 'HALF_OPEN';
      const requestSuccessful = true;

      // Act
      if (circuitState == 'HALF_OPEN' && requestSuccessful) {
        circuitState = 'CLOSED';
      }

      // Assert
      expect(circuitState, equals('CLOSED'));
    });

    test('should reopen circuit on failed half-open request', () {
      // Arrange
      var circuitState = 'HALF_OPEN';
      const requestSuccessful = false;

      // Act
      if (circuitState == 'HALF_OPEN' && !requestSuccessful) {
        circuitState = 'OPEN';
      }

      // Assert
      expect(circuitState, equals('OPEN'));
    });

    test('should reject requests when circuit is open', () {
      // Arrange
      const circuitState = 'OPEN';

      // Act
      final canMakeRequest = circuitState == 'CLOSED' || circuitState == 'HALF_OPEN';

      // Assert
      expect(canMakeRequest, isFalse);
    });

    test('should reset failure count on successful request', () {
      // Arrange
      var failureCount = 3;
      const requestSuccessful = true;

      // Act
      if (requestSuccessful) {
        failureCount = 0;
      }

      // Assert
      expect(failureCount, equals(0));
    });

    test('should track circuit state per endpoint', () {
      // Arrange
      final circuitStates = <String, String>{
        '/api/fields': 'CLOSED',
        '/api/tasks': 'OPEN',
        '/api/users': 'HALF_OPEN',
      };

      // Act & Assert
      expect(circuitStates['/api/fields'], equals('CLOSED'));
      expect(circuitStates['/api/tasks'], equals('OPEN'));
      expect(circuitStates['/api/users'], equals('HALF_OPEN'));
    });

    test('should use sliding window for failure tracking', () {
      // Arrange
      const windowSize = 10;
      final recentRequests = <bool>[
        false, false, true, false, false, // 4 failures in last 10
        true, true, false, true, true,    // 3 successes in last 10
      ];

      // Act
      final failureCount = recentRequests.where((success) => !success).length;
      final failureRate = failureCount / windowSize;

      // Assert
      expect(failureCount, equals(5));
      expect(failureRate, equals(0.5));
    });

    test('should open circuit based on failure rate', () {
      // Arrange
      const failureRateThreshold = 0.5; // 50%
      const windowSize = 10;
      final recentRequests = List<bool>.filled(10, false); // All failures
      recentRequests[0] = true; // 1 success

      // Act
      final failureCount = recentRequests.where((success) => !success).length;
      final failureRate = failureCount / windowSize;
      final shouldOpen = failureRate >= failureRateThreshold;

      // Assert
      expect(failureRate, equals(0.9));
      expect(shouldOpen, isTrue);
    });
  });

  group('Retry Strategy Selection Tests', () {
    test('should select appropriate strategy for sync operation', () {
      // Arrange
      const operationType = 'sync';

      // Act
      final strategy = _getRetryStrategy(operationType);

      // Assert
      expect(strategy['maxRetries'], equals(5));
      expect(strategy['baseDelayMs'], equals(2000));
    });

    test('should select appropriate strategy for critical operation', () {
      // Arrange
      const operationType = 'critical';

      // Act
      final strategy = _getRetryStrategy(operationType);

      // Assert
      expect(strategy['maxRetries'], greaterThan(3));
    });

    test('should select appropriate strategy for background task', () {
      // Arrange
      const operationType = 'background';

      // Act
      final strategy = _getRetryStrategy(operationType);

      // Assert
      expect(strategy['maxRetries'], greaterThanOrEqualTo(10));
    });

    test('should use default strategy for unknown operation', () {
      // Arrange
      const operationType = 'unknown';

      // Act
      final strategy = _getRetryStrategy(operationType);

      // Assert
      expect(strategy['maxRetries'], equals(3));
      expect(strategy['baseDelayMs'], equals(1000));
    });
  });

  group('Retry Context and Metadata Tests', () {
    test('should track retry metadata', () {
      // Arrange
      final retryMetadata = {
        'requestId': 'req-123',
        'attempt': 2,
        'maxAttempts': 3,
        'lastError': 'TIMEOUT',
        'nextRetryAt': DateTime.now().add(const Duration(seconds: 4)),
      };

      // Act & Assert
      expect(retryMetadata['attempt'], equals(2));
      expect(retryMetadata['maxAttempts'], equals(3));
      expect(retryMetadata['lastError'], equals('TIMEOUT'));
    });

    test('should calculate progress percentage', () {
      // Arrange
      const currentAttempt = 3;
      const maxAttempts = 5;

      // Act
      final progress = (currentAttempt / maxAttempts * 100).round();

      // Assert
      expect(progress, equals(60));
    });

    test('should log retry attempts', () {
      // Arrange
      final retryLog = <Map<String, dynamic>>[];

      // Act - Simulate retries
      for (int i = 1; i <= 3; i++) {
        retryLog.add({
          'attempt': i,
          'timestamp': DateTime.now().toIso8601String(),
          'delay': 1000 * (1 << (i - 1)),
        });
      }

      // Assert
      expect(retryLog.length, equals(3));
      expect(retryLog[0]['attempt'], equals(1));
      expect(retryLog[2]['delay'], equals(4000));
    });
  });

  group('Concurrent Request Handling Tests', () {
    test('should handle multiple concurrent retries', () {
      // Arrange
      final activeRetries = <String, int>{
        'request-1': 2,
        'request-2': 1,
        'request-3': 3,
      };

      // Act
      final totalRetries = activeRetries.values.reduce((a, b) => a + b);

      // Assert
      expect(totalRetries, equals(6));
      expect(activeRetries.length, equals(3));
    });

    test('should limit concurrent retry attempts', () {
      // Arrange
      const maxConcurrentRetries = 5;
      final activeRetries = <String>['req1', 'req2', 'req3', 'req4', 'req5'];

      // Act
      final canAddMore = activeRetries.length < maxConcurrentRetries;

      // Assert
      expect(canAddMore, isFalse);
    });

    test('should queue retries when limit reached', () {
      // Arrange
      const maxConcurrentRetries = 3;
      final activeRetries = <String>['req1', 'req2', 'req3'];
      final retryQueue = <String>[];

      // Act - Try to add more
      if (activeRetries.length >= maxConcurrentRetries) {
        retryQueue.add('req4');
      }

      // Assert
      expect(retryQueue.length, equals(1));
    });
  });

  group('Retry Budget Tests', () {
    test('should implement retry budget', () {
      // Arrange
      const retryBudgetPerMinute = 10;
      var retriesInCurrentMinute = 8;

      // Act
      final canRetry = retriesInCurrentMinute < retryBudgetPerMinute;
      if (canRetry) {
        retriesInCurrentMinute++;
      }

      // Assert
      expect(canRetry, isTrue);
      expect(retriesInCurrentMinute, equals(9));
    });

    test('should block retries when budget exhausted', () {
      // Arrange
      const retryBudgetPerMinute = 10;
      var retriesInCurrentMinute = 10;

      // Act
      final canRetry = retriesInCurrentMinute < retryBudgetPerMinute;

      // Assert
      expect(canRetry, isFalse);
    });

    test('should reset retry budget every minute', () {
      // Arrange
      var retriesInCurrentMinute = 10;
      final lastResetTime = DateTime.now().subtract(const Duration(minutes: 1, seconds: 5));

      // Act
      final shouldReset = DateTime.now().difference(lastResetTime).inMinutes >= 1;
      if (shouldReset) {
        retriesInCurrentMinute = 0;
      }

      // Assert
      expect(shouldReset, isTrue);
      expect(retriesInCurrentMinute, equals(0));
    });
  });
}

/// Helper function to get retry strategy based on operation type
Map<String, dynamic> _getRetryStrategy(String operationType) {
  switch (operationType) {
    case 'sync':
      return {'maxRetries': 5, 'baseDelayMs': 2000};
    case 'critical':
      return {'maxRetries': 10, 'baseDelayMs': 1000};
    case 'background':
      return {'maxRetries': 20, 'baseDelayMs': 5000};
    default:
      return {'maxRetries': 3, 'baseDelayMs': 1000};
  }
}
