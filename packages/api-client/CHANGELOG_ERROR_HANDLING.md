# API Client Error Handling Implementation

## Summary of Changes

This implementation adds comprehensive error handling to the SAHOOL API Client, addressing the issue of silent failures that were masking real problems.

## Files Modified/Created

### New Files

1. **`src/errors.ts`** - Custom error types and utilities
   - `ApiError` - Base error class
   - `NetworkError` - Network/connection errors
   - `AuthError` - 401 authentication errors
   - `AuthorizationError` - 403 permission errors
   - `NotFoundError` - 404 not found errors
   - `ValidationError` - 400 validation errors
   - `ServerError` - 5xx server errors
   - `TimeoutError` - Request timeout errors
   - `RateLimitError` - 429 rate limit errors
   - `parseAxiosError()` - Utility to parse Axios errors into custom types
   - `isApiError()`, `isNetworkError()`, `isAuthError()` - Type guard utilities

2. **`USAGE_EXAMPLES.md`** - Comprehensive usage guide

### Modified Files

1. **`src/index.ts`**
   - Added error handling infrastructure
   - Added logging utilities
   - Updated all methods to use `safeExecute()` wrapper
   - Added support for `errorHandling` and `logLevel` config options

2. **`src/types.ts`**
   - Added `LogLevel` type
   - Extended `ApiClientConfig` with:
     - `errorHandling?: 'throw' | 'silent'`
     - `logLevel?: LogLevel`
     - `logger?: { error, warn, info, debug }`

3. **`src/index.test.ts`**
   - Updated tests for new error handling behavior
   - Added tests for both 'throw' and 'silent' modes
   - Added configuration tests

4. **`package.json`**
   - Added `src/errors.ts` to build
   - Added errors export
   - Added test scripts

## Key Features

### 1. Custom Error Types

All errors extend from `ApiError` base class and include:
- `name` - Error class name
- `message` - Human-readable error message
- `code` - Machine-readable error code
- `statusCode` - HTTP status code (if applicable)
- `endpoint` - API endpoint that failed
- `method` - HTTP method used
- `timestamp` - When the error occurred
- `originalError` - Original error object (if wrapped)
- `context` - Additional contextual information
- `toJSON()` - Serialization method for logging

### 2. Proper Error Logging

- Configurable log levels: `none`, `error`, `warn`, `info`, `debug`
- Custom logger support for integration with existing logging systems
- Console fallback when no custom logger is provided
- Errors are logged even in silent mode
- Rich context included in all log messages

### 3. Backward Compatibility

Two error handling modes:

**Throw Mode (Default - Recommended)**
```typescript
const client = new SahoolApiClient({
  baseUrl: 'http://localhost',
  errorHandling: 'throw', // default
});
```
- Throws custom errors for callers to handle
- More reliable and debuggable
- Type-safe error handling

**Silent Mode (Legacy)**
```typescript
const client = new SahoolApiClient({
  baseUrl: 'http://localhost',
  errorHandling: 'silent',
});
```
- Returns empty arrays/null on errors (old behavior)
- Still logs errors for visibility
- Backward compatible with existing code

### 4. Methods Updated

All methods that previously caught and silently returned empty arrays or null now use the new error handling:

- `getTasks()` - Returns `[]` or throws
- `getFields()` - Returns `[]` or throws
- `getFarms()` - Returns `[]` or throws
- `getFarmById()` - Returns `null` or throws
- `getWeather()` - Returns `null` or throws
- `getWeatherForecast()` - Returns `null` or throws
- `getWeatherAlerts()` - Returns `[]` or throws
- `getDiagnoses()` - Returns `[]` or throws
- `getDiagnosisStats()` - Returns empty stats or throws
- `updateDiagnosisStatus()` - Returns success object or throws
- `getDashboardStats()` - Returns empty stats or throws
- `getDashboard()` - Returns `null` or throws
- `getFieldIndicators()` - Returns `null` or throws
- `getSensorReadings()` - Returns `[]` or throws
- `getEquipment()` - Returns `[]` or throws
- `getNotifications()` - Returns `[]` or throws
- `markNotificationRead()` - Returns `false` or throws
- `getCommunityPosts()` - Returns `[]` or throws
- `updateTaskStatus()` - Returns `false` or throws
- `checkServicesHealth()` - Now logs failures

## Usage Examples

### Basic Usage (Throw Mode)

```typescript
import { SahoolApiClient, isAuthError, isNetworkError } from '@sahool/api-client';

const client = new SahoolApiClient({
  baseUrl: process.env.API_URL,
  errorHandling: 'throw',
  logLevel: 'error',
});

try {
  const tasks = await client.getTasks();
  console.log('Tasks:', tasks);
} catch (error) {
  if (isAuthError(error)) {
    redirectToLogin();
  } else if (isNetworkError(error)) {
    showRetryDialog();
  } else {
    showError(error.message);
  }
}
```

### Type-Specific Error Handling

```typescript
import {
  AuthError,
  ValidationError,
  NotFoundError,
  ServerError,
  TimeoutError,
} from '@sahool/api-client/errors';

try {
  const task = await client.createTask(taskData);
} catch (error) {
  if (error instanceof AuthError) {
    window.location.href = '/login';
  } else if (error instanceof ValidationError) {
    showValidationErrors(error.validationErrors);
  } else if (error instanceof NotFoundError) {
    showError('Resource not found');
  } else if (error instanceof TimeoutError) {
    showError(`Request timed out after ${error.timeout}ms`);
  } else if (error instanceof ServerError) {
    showError('Server error');
  }
}
```

### Custom Logger

```typescript
import winston from 'winston';

const logger = winston.createLogger({...});

const client = new SahoolApiClient({
  baseUrl: process.env.API_URL,
  logLevel: 'debug',
  logger: {
    error: (msg, ctx) => logger.error(msg, ctx),
    warn: (msg, ctx) => logger.warn(msg, ctx),
    info: (msg, ctx) => logger.info(msg, ctx),
    debug: (msg, ctx) => logger.debug(msg, ctx),
  },
});
```

### Legacy Code (Silent Mode)

```typescript
const client = new SahoolApiClient({
  baseUrl: process.env.API_URL,
  errorHandling: 'silent',
  logLevel: 'error', // Still logs errors
});

// Returns empty array on error
const tasks = await client.getTasks();
```

## Migration Guide

### For Existing Code

1. **No immediate changes required** - Default is 'throw' mode, but you can set to 'silent' for backward compatibility
2. **Enable logging** - Set `logLevel: 'error'` to see errors in console
3. **Gradually add error handling** - Update components one at a time to use try-catch
4. **Switch to throw mode** - Once all error handling is in place

### Recommended Approach

```typescript
// Phase 1: Keep existing behavior
const client = new SahoolApiClient({
  baseUrl: 'http://localhost',
  errorHandling: 'silent', // Maintain old behavior
  logLevel: 'error',       // But see what's failing
});

// Phase 2: Update components gradually
// In new/updated components, add try-catch

// Phase 3: Switch to throw mode
const client = new SahoolApiClient({
  baseUrl: 'http://localhost',
  errorHandling: 'throw',  // Now all errors are properly handled
  logLevel: 'error',
});
```

## Benefits

1. **Better Error Visibility** - Errors are no longer silently masked
2. **Easier Debugging** - Rich error context helps identify issues quickly
3. **Type Safety** - TypeScript support for error types
4. **Production Ready** - Custom logger support for error tracking services
5. **Backward Compatible** - Existing code can continue to work
6. **Flexible** - Choose between throwing or silent mode based on needs

## Testing

All existing tests have been updated to work with the new error handling:
- Tests for 'throw' mode
- Tests for 'silent' mode
- Tests for custom logger
- Tests for log levels

Run tests with:
```bash
npm run test
```

## Build

The package exports are updated to include errors:
```typescript
import { SahoolApiClient } from '@sahool/api-client';
import { ApiError, NetworkError } from '@sahool/api-client/errors';
import type { LogLevel } from '@sahool/api-client/types';
```

Build the package:
```bash
npm run build
```

## Performance Impact

Minimal performance impact:
- Logging only occurs when errors happen or log level permits
- Error object creation is lightweight
- No impact on successful requests

## Breaking Changes

**None** - The default behavior is designed to be backward compatible:
- Silent mode maintains old behavior
- Throw mode is opt-in via configuration
- All existing APIs remain unchanged
