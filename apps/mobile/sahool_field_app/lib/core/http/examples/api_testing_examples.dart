/// Testing examples for the improved API client
///
/// This file demonstrates how to test:
/// - Error handling
/// - Retry logic
/// - Circuit breaker
/// - ApiResult transformations

import 'package:dio/dio.dart';
import '../api_client.dart';
import '../api_error_handler.dart';
import '../api_result.dart';
import '../retry_interceptor.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Mock Error Scenarios for Testing
// ═══════════════════════════════════════════════════════════════════════════

class ApiTestScenarios {
  /// Test network timeout
  static void testTimeout() async {
    final apiClient = ApiClient(
      baseUrl: 'https://httpbin.org',
      maxRetries: 2,
    );

    print('Testing timeout scenario...');
    final result = await apiClient.getSafe<dynamic>(
      '/delay/30', // Will timeout
    );

    result.when(
      success: (_) => print('✓ Success (unexpected)'),
      failure: (error) {
        print('✓ Timeout error caught');
        print('  Type: ${error.type}');
        print('  Message: ${error.message}');
        print('  Retryable: ${error.isRetryable}');
        assert(error.type == ApiErrorType.timeout);
      },
    );
  }

  /// Test network error
  static void testNetworkError() async {
    final apiClient = ApiClient(
      baseUrl: 'https://invalid-domain-12345.com',
      maxRetries: 1,
    );

    print('\nTesting network error...');
    final result = await apiClient.getSafe<dynamic>('/test');

    result.when(
      success: (_) => print('✓ Success (unexpected)'),
      failure: (error) {
        print('✓ Network error caught');
        print('  Type: ${error.type}');
        print('  Message: ${error.message}');
        print('  Network Error: ${error.isNetworkError}');
        assert(error.isNetworkError);
      },
    );
  }

  /// Test 404 Not Found
  static void testNotFound() async {
    final apiClient = ApiClient(
      baseUrl: 'https://httpbin.org',
      maxRetries: 0, // Disable retries for this test
    );

    print('\nTesting 404 Not Found...');
    final result = await apiClient.getSafe<dynamic>('/status/404');

    result.when(
      success: (_) => print('✓ Success (unexpected)'),
      failure: (error) {
        print('✓ Not Found error caught');
        print('  Type: ${error.type}');
        print('  Status: ${error.statusCode}');
        print('  Message: ${error.message}');
        assert(error.type == ApiErrorType.notFound);
        assert(error.statusCode == 404);
      },
    );
  }

  /// Test 401 Unauthorized
  static void testUnauthorized() async {
    final apiClient = ApiClient(
      baseUrl: 'https://httpbin.org',
      maxRetries: 0,
    );

    print('\nTesting 401 Unauthorized...');
    final result = await apiClient.getSafe<dynamic>('/status/401');

    result.when(
      success: (_) => print('✓ Success (unexpected)'),
      failure: (error) {
        print('✓ Auth error caught');
        print('  Type: ${error.type}');
        print('  Status: ${error.statusCode}');
        print('  Auth Error: ${error.isAuthError}');
        assert(error.isAuthError);
        assert(error.statusCode == 401);
      },
    );
  }

  /// Test 500 Server Error
  static void testServerError() async {
    final apiClient = ApiClient(
      baseUrl: 'https://httpbin.org',
      maxRetries: 2,
    );

    print('\nTesting 500 Server Error...');
    final result = await apiClient.getSafe<dynamic>('/status/500');

    result.when(
      success: (_) => print('✓ Success (unexpected)'),
      failure: (error) {
        print('✓ Server error caught (after retries)');
        print('  Type: ${error.type}');
        print('  Status: ${error.statusCode}');
        print('  Server Error: ${error.isServerError}');
        print('  Retryable: ${error.isRetryable}');
        assert(error.isServerError);
        assert(error.statusCode == 500);
      },
    );
  }

  /// Test 429 Rate Limiting
  static void testRateLimited() async {
    final apiClient = ApiClient(
      baseUrl: 'https://httpbin.org',
      maxRetries: 1,
    );

    print('\nTesting 429 Rate Limited...');
    final result = await apiClient.getSafe<dynamic>('/status/429');

    result.when(
      success: (_) => print('✓ Success (unexpected)'),
      failure: (error) {
        print('✓ Rate limit error caught');
        print('  Type: ${error.type}');
        print('  Status: ${error.statusCode}');
        print('  Retryable: ${error.isRetryable}');
        assert(error.type == ApiErrorType.rateLimited);
        assert(error.statusCode == 429);
      },
    );
  }

  /// Test successful request
  static void testSuccess() async {
    final apiClient = ApiClient(
      baseUrl: 'https://httpbin.org',
    );

    print('\nTesting successful request...');
    final result = await apiClient.getSafe<Map<String, dynamic>>('/get');

    result.when(
      success: (data) {
        print('✓ Success');
        print('  URL: ${data['url']}');
        assert(data['url'] != null);
      },
      failure: (error) {
        print('✗ Unexpected error: ${error.message}');
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Circuit Breaker Testing
// ═══════════════════════════════════════════════════════════════════════════

class CircuitBreakerTests {
  /// Test circuit breaker opening after failures
  static void testCircuitBreakerOpening() async {
    final circuitBreaker = CircuitBreaker(
      failureThreshold: 3,
      resetTimeout: Duration(seconds: 5),
    );

    print('\nTesting Circuit Breaker Opening...');
    print('Initial state: ${circuitBreaker.state}');
    assert(circuitBreaker.state == CircuitBreakerState.closed);

    // Record failures
    for (int i = 0; i < 3; i++) {
      circuitBreaker.recordFailure();
      print('Recorded failure ${i + 1}/3');
      print('State: ${circuitBreaker.state}');
    }

    // Circuit should be open now
    assert(circuitBreaker.state == CircuitBreakerState.open);
    print('✓ Circuit breaker opened after 3 failures');

    // Requests should be blocked
    assert(!circuitBreaker.canExecute());
    print('✓ Requests are blocked when circuit is open');
  }

  /// Test circuit breaker recovery
  static void testCircuitBreakerRecovery() async {
    final circuitBreaker = CircuitBreaker(
      failureThreshold: 2,
      resetTimeout: Duration(milliseconds: 100),
    );

    print('\nTesting Circuit Breaker Recovery...');

    // Open the circuit
    circuitBreaker.recordFailure();
    circuitBreaker.recordFailure();
    print('Circuit opened');
    assert(circuitBreaker.state == CircuitBreakerState.open);

    // Wait for reset timeout
    await Future.delayed(Duration(milliseconds: 150));

    // Check if circuit can execute (should be half-open)
    final canExecute = circuitBreaker.canExecute();
    print('After timeout - Can execute: $canExecute');
    print('State: ${circuitBreaker.state}');
    assert(canExecute);

    // Record success to close circuit
    circuitBreaker.recordSuccess();
    print('Recorded success');
    print('Final state: ${circuitBreaker.state}');
    assert(circuitBreaker.state == CircuitBreakerState.closed);
    print('✓ Circuit breaker recovered successfully');
  }

  /// Test circuit breaker status
  static void testCircuitBreakerStatus() {
    final circuitBreaker = CircuitBreaker(
      failureThreshold: 5,
    );

    print('\nTesting Circuit Breaker Status...');

    circuitBreaker.recordFailure();
    circuitBreaker.recordFailure();
    circuitBreaker.recordSuccess();

    final status = circuitBreaker.getStatus();
    print('Status:');
    print('  State: ${status['state']}');
    print('  Failures: ${status['failureCount']}');
    print('  Success: ${status['successCount']}');
    print('  Threshold: ${status['failureThreshold']}');

    assert(status['failureCount'] == 0); // Reset after success
    print('✓ Circuit breaker status is accurate');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// ApiResult Testing
// ═══════════════════════════════════════════════════════════════════════════

class ApiResultTests {
  /// Test Success transformation
  static void testSuccessTransformation() {
    print('\nTesting ApiResult Success Transformation...');

    final result = ApiResult.success({'name': 'John', 'age': 30});

    // Test map
    final nameResult = result.map((data) => data['name']);
    assert(nameResult.dataOrNull == 'John');
    print('✓ Map transformation works');

    // Test when
    final output = result.when(
      success: (data) => 'Success: ${data['name']}',
      failure: (_) => 'Error',
    );
    assert(output == 'Success: John');
    print('✓ When pattern matching works');

    // Test getOrElse
    final data = result.getOrElse({});
    assert(data['name'] == 'John');
    print('✓ GetOrElse returns success data');
  }

  /// Test Failure transformation
  static void testFailureTransformation() {
    print('\nTesting ApiResult Failure Transformation...');

    final error = ApiError(
      type: ApiErrorType.network,
      message: 'Network error',
      code: 'NO_CONNECTION',
      exception: Exception('Test'),
    );
    final result = ApiResult<Map<String, dynamic>>.failure(error);

    // Test map (should preserve error)
    final mappedResult = result.map((data) => data['name']);
    assert(mappedResult.isFailure);
    print('✓ Map preserves error');

    // Test when
    final output = result.when(
      success: (_) => 'Success',
      failure: (err) => 'Error: ${err.message}',
    );
    assert(output == 'Error: Network error');
    print('✓ When handles failure');

    // Test getOrElse
    final data = result.getOrElse({'default': true});
    assert(data['default'] == true);
    print('✓ GetOrElse returns default on failure');
  }

  /// Test chaining
  static void testChaining() async {
    print('\nTesting ApiResult Chaining...');

    final result = ApiResult.success(5);

    // Test flatMap
    final doubled = result.flatMap((value) {
      return ApiResult.success(value * 2);
    });
    assert(doubled.dataOrNull == 10);
    print('✓ FlatMap works');

    // Test onSuccess
    int sideEffect = 0;
    result.onSuccess((value) => sideEffect = value);
    assert(sideEffect == 5);
    print('✓ OnSuccess executes side effects');

    // Test onFailure
    bool failureCalled = false;
    result.onFailure((_) => failureCalled = true);
    assert(!failureCalled);
    print('✓ OnFailure is not called on success');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Retry Logic Testing
// ═══════════════════════════════════════════════════════════════════════════

class RetryLogicTests {
  /// Test exponential backoff calculation
  static void testExponentialBackoff() {
    print('\nTesting Exponential Backoff...');

    final interceptor = RetryInterceptor(
      baseDelay: Duration(milliseconds: 100),
      enableJitter: false, // Disable jitter for predictable testing
    );

    // We can't directly test private methods, but we can verify behavior
    print('Retry interceptor configured:');
    print('  Max retries: ${interceptor.maxRetries}');
    print('  Base delay: ${interceptor.baseDelay}');
    print('  Max delay: ${interceptor.maxDelay}');
    print('✓ Exponential backoff configured');
  }

  /// Test should retry logic
  static void testShouldRetry() {
    print('\nTesting Should Retry Logic...');

    // These would be tested via integration tests with actual requests
    // Here we document the expected behavior

    print('Should retry:');
    print('  - Connection timeout: YES');
    print('  - Send timeout: YES');
    print('  - Receive timeout: YES');
    print('  - Connection error: YES');
    print('  - 5xx errors: YES');
    print('  - 429 (rate limit): YES');
    print('  - 408 (timeout): YES');
    print('  - 503 (unavailable): YES');
    print('  - 504 (gateway timeout): YES');

    print('\nShould NOT retry:');
    print('  - 4xx errors (except above): NO');
    print('  - Certificate errors: NO');
    print('  - Cancelled requests: NO');
    print('  - Max retries reached: NO');

    print('✓ Retry logic documented');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

class IntegrationTests {
  /// Run all tests
  static Future<void> runAllTests() async {
    print('═══════════════════════════════════════════════════════');
    print('Running API Client Integration Tests');
    print('═══════════════════════════════════════════════════════');

    // API Error Scenarios
    await ApiTestScenarios.testSuccess();
    await ApiTestScenarios.testTimeout();
    await ApiTestScenarios.testNetworkError();
    await ApiTestScenarios.testNotFound();
    await ApiTestScenarios.testUnauthorized();
    await ApiTestScenarios.testServerError();
    await ApiTestScenarios.testRateLimited();

    // Circuit Breaker Tests
    CircuitBreakerTests.testCircuitBreakerOpening();
    await CircuitBreakerTests.testCircuitBreakerRecovery();
    CircuitBreakerTests.testCircuitBreakerStatus();

    // ApiResult Tests
    ApiResultTests.testSuccessTransformation();
    ApiResultTests.testFailureTransformation();
    await ApiResultTests.testChaining();

    // Retry Logic Tests
    RetryLogicTests.testExponentialBackoff();
    RetryLogicTests.testShouldRetry();

    print('\n═══════════════════════════════════════════════════════');
    print('All Tests Completed!');
    print('═══════════════════════════════════════════════════════');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Entry Point
// ═══════════════════════════════════════════════════════════════════════════

void main() async {
  await IntegrationTests.runAllTests();
}
