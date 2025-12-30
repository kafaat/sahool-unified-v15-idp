# SAHOOL HTTP Client - Improved Error Handling & Retry Logic

This directory contains the improved HTTP client implementation with comprehensive error handling, automatic retry logic, and circuit breaker pattern.

## Overview

The HTTP client has been enhanced with:

1. **Type-Safe Error Handling** - `ApiResult<T>` for functional error handling
2. **Standardized Error Types** - Consistent error classification and user-friendly messages
3. **Automatic Retry Logic** - Exponential backoff with jitter for transient failures
4. **Circuit Breaker Pattern** - Prevents cascading failures and reduces server load
5. **Enhanced Logging** - Request timing and detailed error logging

## Files

- **`api_result.dart`** - Type-safe result wrapper for API responses
- **`api_error_handler.dart`** - Standardized error types and error handling
- **`retry_interceptor.dart`** - Retry logic with exponential backoff and circuit breaker
- **`api_client.dart`** - Main HTTP client (updated with new features)
- **`auth_interceptor.dart`** - Authentication and token refresh handling
- **`certificate_pinning.dart`** - SSL certificate pinning for security
- **`examples/api_usage_examples.dart`** - Comprehensive usage examples

## Quick Start

### Basic Usage (Type-Safe)

```dart
// Initialize client
final apiClient = ApiClient(
  maxRetries: 3,
  baseRetryDelay: Duration(milliseconds: 500),
  enableCircuitBreaker: true,
);

// Make a request with type-safe error handling
final result = await apiClient.getSafe<Map<String, dynamic>>('/users/123');

result.when(
  success: (data) => print('Success: $data'),
  failure: (error) => print('Error: ${error.message}'),
);
```

### Legacy Usage (Exception-Based)

```dart
// Backward compatible with existing code
try {
  final data = await apiClient.get('/users/123');
  print('Success: $data');
} on ApiException catch (e) {
  print('Error: ${e.message}');
}
```

## Features

### 1. Type-Safe Error Handling

The `ApiResult<T>` type provides type-safe error handling without exceptions:

```dart
// Fetch data
final result = await apiClient.getSafe<User>('/users/123');

// Handle success/failure
result.when(
  success: (user) => print('User: ${user.name}'),
  failure: (error) => print('Error: ${error.message}'),
);

// Transform data
final emailResult = result.map((user) => user.email);

// Provide defaults
final user = result.getOrElse(defaultUser);

// Chain operations
final friendsResult = result.flatMap((user) async {
  return await apiClient.getSafe<List<User>>('/users/${user.id}/friends');
});
```

### 2. Standardized Error Types

All errors are classified into standard types:

- `network` - Network connectivity issues
- `server` - Server errors (5xx)
- `auth` - Authentication/authorization errors (401, 403)
- `validation` - Validation errors (400, 422)
- `notFound` - Resource not found (404)
- `timeout` - Request timeout
- `rateLimited` - Rate limiting (429)
- `client` - Other client errors (4xx)
- `certificate` - SSL/Certificate errors
- `cancelled` - Request cancelled
- `unknown` - Unknown/unexpected errors

```dart
result.whenOrNull(
  failure: (error) {
    if (error.isNetworkError) {
      // Handle network issues
    } else if (error.isAuthError) {
      // Redirect to login
    } else if (error.isValidationError) {
      // Show validation errors
    }
  },
);
```

### 3. Automatic Retry Logic

Requests are automatically retried on transient failures:

**Retry Conditions:**
- Network errors (connection issues)
- Timeout errors
- Server errors (5xx)
- Rate limiting (429)
- Request timeout (408)
- Service unavailable (503)
- Gateway timeout (504)

**Retry Strategy:**
- Exponential backoff: `baseDelay * 2^attemptCount`
- Random jitter (0-1000ms) to prevent thundering herd
- Configurable max retries (default: 3)
- Maximum delay cap (default: 10 seconds)

```dart
// Configure retry behavior
final apiClient = ApiClient(
  maxRetries: 5,
  baseRetryDelay: Duration(milliseconds: 1000),
);
```

**Example Retry Timeline:**
- Attempt 1: Immediate
- Attempt 2: After 500ms + jitter
- Attempt 3: After 1000ms + jitter
- Attempt 4: After 2000ms + jitter

### 4. Circuit Breaker Pattern

Prevents cascading failures and reduces load on failing servers:

**States:**
- **Closed** - Normal operation, requests flow through
- **Open** - Circuit is broken, requests are blocked
- **Half-Open** - Testing if service has recovered

**Configuration:**
- Failure threshold: 5 failures
- Reset timeout: 60 seconds
- Half-open timeout: 30 seconds

```dart
// Check circuit breaker status
final status = apiClient.getCircuitBreakerStatus();
print('State: ${status['state']}');
print('Failures: ${status['failureCount']}/${status['failureThreshold']}');

// Manually reset circuit breaker
apiClient.resetCircuitBreaker();
```

**Flow:**
1. Circuit starts in **Closed** state
2. After 5 consecutive failures, circuit opens
3. Requests are blocked for 60 seconds
4. After timeout, circuit enters **Half-Open** state
5. If next request succeeds, circuit closes
6. If next request fails, circuit opens again

### 5. Enhanced Logging

All requests are logged with timing and error details:

```dart
// Request log
ℹ️ [NETWORK] 📤 GET /users/123

// Success log
ℹ️ [NETWORK] 📥 GET /users/123 200 (245ms)

// Error log
❌ [NETWORK] 📥 GET /users/123 500 (1023ms)

// Retry log
ℹ️ [RETRY] Retrying request (2/3) after 1500ms
```

## Error Messages

All error messages are user-friendly and localized (Arabic):

| Error Type | Arabic Message | English Equivalent |
|------------|---------------|-------------------|
| `TIMEOUT` | انتهت مهلة الاتصال | Connection timeout |
| `NO_CONNECTION` | لا يوجد اتصال بالإنترنت | No internet connection |
| `UNAUTHORIZED` | انتهت صلاحية الجلسة | Session expired |
| `FORBIDDEN` | ليس لديك صلاحية للوصول | Access forbidden |
| `NOT_FOUND` | المورد المطلوب غير موجود | Resource not found |
| `VALIDATION_ERROR` | البيانات المدخلة غير صحيحة | Invalid input |
| `RATE_LIMITED` | تم تجاوز عدد الطلبات المسموح به | Too many requests |
| `SERVER_ERROR` | حدث خطأ في الخادم | Server error |

## API Methods

### Type-Safe Methods (Recommended)

- `getSafe<T>(path, {queryParameters})` - GET request
- `postSafe<T>(path, data, {queryParameters, headers})` - POST request
- `putSafe<T>(path, data, {queryParameters, headers})` - PUT request
- `deleteSafe<T>(path, {queryParameters, headers})` - DELETE request
- `uploadFileSafe<T>(path, filePath, {fieldName, extraData})` - File upload

### Legacy Methods (Backward Compatible)

- `get(path, {queryParameters})` - GET request
- `post(path, data, {queryParameters, headers})` - POST request
- `put(path, data, {queryParameters, headers})` - PUT request
- `delete(path, {queryParameters, headers})` - DELETE request
- `uploadFile(path, filePath, {fieldName, extraData})` - File upload

## Advanced Usage

### Handling Validation Errors

```dart
final result = await apiClient.postSafe<Map<String, dynamic>>(
  '/users',
  {'name': '', 'email': 'invalid'},
);

result.whenOrNull(
  failure: (error) {
    if (error.isValidationError && error.data is Map) {
      final errors = error.data['errors'] as Map<String, dynamic>;
      errors.forEach((field, message) {
        print('$field: $message');
      });
    }
  },
);
```

### Chaining API Calls

```dart
final result = await apiClient
    .getSafe<User>('/users/123')
    .flatMapAsync((user) async {
      return await apiClient.getSafe<List<Post>>(
        '/users/${user.id}/posts',
      );
    });
```

### Side Effects

```dart
final result = await apiClient
    .postSafe<User>('/users', userData)
    .onSuccessAsync((user) async {
      // Log analytics
      await analytics.logEvent('user_created', {'id': user.id});
    })
    .onFailureAsync((error) async {
      // Report error to crash reporting service
      await crashlytics.recordError(error, error.stackTrace);
    });
```

### UI State Management

```dart
class UserState {
  final User? user;
  final bool isLoading;
  final ApiError? error;

  // ... constructor and copyWith
}

Future<void> loadUser(String userId) async {
  state = state.copyWith(isLoading: true, error: null);

  final result = await apiClient.getSafe<User>('/users/$userId');

  state = result.when(
    success: (user) => state.copyWith(user: user, isLoading: false),
    failure: (error) => state.copyWith(error: error, isLoading: false),
  );
}
```

## Best Practices

1. **Use Type-Safe Methods** - Prefer `getSafe()`, `postSafe()`, etc. over legacy methods
2. **Handle All Error Types** - Check for network, auth, validation, and server errors
3. **Provide User Feedback** - Use the user-friendly error messages
4. **Log Technical Details** - Use `error.technicalMessage` for debugging
5. **Monitor Circuit Breaker** - Check status during critical operations
6. **Graceful Degradation** - Provide defaults or cached data on errors
7. **Retry Logic** - Trust the automatic retry for transient failures
8. **Error Recovery** - Guide users on how to recover from errors

## Migration Guide

### From Legacy to Type-Safe

**Before:**
```dart
try {
  final data = await apiClient.get('/users/123');
  final user = User.fromJson(data);
  print('User: ${user.name}');
} on ApiException catch (e) {
  print('Error: ${e.message}');
}
```

**After:**
```dart
final result = await apiClient.getSafe<Map<String, dynamic>>('/users/123');

result
    .map((data) => User.fromJson(data))
    .when(
      success: (user) => print('User: ${user.name}'),
      failure: (error) => print('Error: ${error.message}'),
    );
```

## Performance Considerations

- **Request Timing** - All requests are timed automatically
- **Circuit Breaker** - Prevents wasted requests to failing services
- **Exponential Backoff** - Reduces server load during issues
- **Jitter** - Prevents thundering herd problem
- **Memory** - Circuit breaker and retry state use minimal memory

## Security Features

- **SSL Certificate Pinning** - Prevents man-in-the-middle attacks
- **Sensitive Data Protection** - Request/response bodies not logged in production
- **Token Refresh** - Automatic token refresh on 401 (via `auth_interceptor.dart`)
- **Secure Storage** - Tokens stored in secure storage

## Testing

See `examples/api_usage_examples.dart` for comprehensive examples of:
- Basic usage patterns
- Error handling strategies
- Transformations and chaining
- UI integration patterns
- Legacy compatibility

## Troubleshooting

### Circuit Breaker is Open

```dart
// Check status
final status = apiClient.getCircuitBreakerStatus();
print('State: ${status['state']}'); // 'open'

// Wait for automatic reset or manually reset
apiClient.resetCircuitBreaker();
```

### Retries Not Working

- Check if error type is retryable (see retry conditions)
- Verify max retries configuration
- Check circuit breaker state

### High Latency

- Review retry delays configuration
- Check network conditions
- Monitor server response times

## Configuration

```dart
final apiClient = ApiClient(
  baseUrl: 'https://api.sahool.app/v1',
  maxRetries: 3,                                    // Max retry attempts
  baseRetryDelay: Duration(milliseconds: 500),     // Base delay for retries
  enableCircuitBreaker: true,                       // Enable circuit breaker
);
```

## Dependencies

- `dio: ^5.x.x` - HTTP client
- `flutter_riverpod: ^2.x.x` - State management (for auth interceptor)

## License

Part of SAHOOL Field App - Internal use only
