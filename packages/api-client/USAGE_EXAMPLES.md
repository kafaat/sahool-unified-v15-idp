# API Client Error Handling - Usage Examples

## Overview

The SAHOOL API Client now includes comprehensive error handling with custom error types, proper logging, and backward compatibility options.

## Key Features

1. **Custom Error Types**: Specific error classes for different scenarios
2. **Proper Error Logging**: Configurable logging levels and custom logger support
3. **Backward Compatibility**: Silent mode for legacy code
4. **Type Safety**: Full TypeScript support for all error types

## Configuration

### Error Handling Modes

```typescript
import { SahoolApiClient } from "@sahool/api-client";

// Throw mode (recommended - default)
const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  errorHandling: "throw", // Throws custom errors
});

// Silent mode (legacy compatibility)
const legacyClient = new SahoolApiClient({
  baseUrl: "http://localhost",
  errorHandling: "silent", // Returns empty arrays/null on errors
});
```

### Log Levels

```typescript
// Set log level
const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  logLevel: "error", // 'none' | 'error' | 'warn' | 'info' | 'debug'
});

// Custom logger
const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  logger: {
    error: (message, context) => myLogger.error(message, context),
    warn: (message, context) => myLogger.warn(message, context),
    info: (message, context) => myLogger.info(message, context),
    debug: (message, context) => myLogger.debug(message, context),
  },
});
```

## Error Types

### Available Error Classes

```typescript
import {
  ApiError, // Base error class
  NetworkError, // Network/connection errors
  AuthError, // 401 authentication errors
  AuthorizationError, // 403 permission errors
  NotFoundError, // 404 not found errors
  ValidationError, // 400 validation errors
  ServerError, // 5xx server errors
  TimeoutError, // Request timeout errors
  RateLimitError, // 429 rate limit errors
} from "@sahool/api-client/errors";
```

### Error Properties

All errors extend `ApiError` and include:

```typescript
{
  name: string;           // Error class name
  message: string;        // Error message
  code: string;           // Error code (e.g., 'AUTH_ERROR')
  statusCode?: number;    // HTTP status code
  endpoint?: string;      // API endpoint
  method?: string;        // HTTP method
  timestamp: string;      // Error timestamp
  originalError?: Error;  // Original error if wrapped
  context?: Record<string, unknown>; // Additional context
}
```

## Usage Examples

### Basic Error Handling (Throw Mode)

```typescript
import {
  SahoolApiClient,
  isAuthError,
  isNetworkError,
} from "@sahool/api-client";

const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  errorHandling: "throw",
});

async function getTasks() {
  try {
    const tasks = await client.getTasks();
    return tasks;
  } catch (error) {
    if (isAuthError(error)) {
      // Handle authentication error
      console.error("Authentication required:", error.message);
      redirectToLogin();
    } else if (isNetworkError(error)) {
      // Handle network error
      console.error("Network error:", error.message);
      showRetryDialog();
    } else {
      // Handle other errors
      console.error("Unexpected error:", error);
    }
    throw error;
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
} from "@sahool/api-client/errors";

async function createTask(taskData) {
  try {
    const task = await client.createTask(taskData);
    return task;
  } catch (error) {
    if (error instanceof AuthError) {
      // Redirect to login
      window.location.href = "/login";
    } else if (error instanceof ValidationError) {
      // Show validation errors to user
      showValidationErrors(error.validationErrors);
    } else if (error instanceof NotFoundError) {
      // Resource not found
      showError("Resource not found");
    } else if (error instanceof ServerError) {
      // Server error
      showError("Server error, please try again later");
    }
  }
}
```

### Legacy Code (Silent Mode)

```typescript
// For backward compatibility with existing code
const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  errorHandling: "silent",
  logLevel: "error", // Still logs errors even in silent mode
});

// Returns empty array on error instead of throwing
const tasks = await client.getTasks();
if (tasks.length === 0) {
  // Could be empty or could be an error
  // Check logs for details
}
```

### With React Query

```typescript
import { useQuery } from '@tanstack/react-query';
import { SahoolApiClient, isAuthError } from '@sahool/api-client';

const client = new SahoolApiClient({
  baseUrl: process.env.REACT_APP_API_URL,
  errorHandling: 'throw',
  onUnauthorized: () => {
    // Redirect to login or refresh token
  },
});

function TasksList() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => client.getTasks(),
    retry: (failureCount, error) => {
      // Don't retry on auth errors
      if (isAuthError(error)) return false;
      return failureCount < 3;
    },
  });

  if (error) {
    if (isAuthError(error)) {
      return <div>Please log in</div>;
    }
    return <div>Error: {error.message}</div>;
  }

  // ...
}
```

### Error Logging with Custom Logger

```typescript
import pino from "pino";

const logger = pino();

const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  logLevel: "debug",
  logger: {
    error: (message, context) => logger.error(context, message),
    warn: (message, context) => logger.warn(context, message),
    info: (message, context) => logger.info(context, message),
    debug: (message, context) => logger.debug(context, message),
  },
});
```

### Rate Limit Handling

```typescript
import { RateLimitError } from "@sahool/api-client/errors";

async function makeRequest() {
  try {
    return await client.getTasks();
  } catch (error) {
    if (error instanceof RateLimitError) {
      // Wait for the retry-after period
      const retryAfter = error.retryAfter || 60;
      console.log(`Rate limited. Retry after ${retryAfter} seconds`);
      await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
      // Retry the request
      return await client.getTasks();
    }
    throw error;
  }
}
```

### Timeout Handling

```typescript
import { TimeoutError } from "@sahool/api-client/errors";

const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  timeout: 5000, // 5 second timeout
});

async function getData() {
  try {
    return await client.getTasks();
  } catch (error) {
    if (error instanceof TimeoutError) {
      console.log(`Request timed out after ${error.timeout}ms`);
      // Show timeout message to user
      showNotification("Request timed out. Please check your connection.");
    }
    throw error;
  }
}
```

## Migration Guide

### From Silent Failures to Proper Error Handling

**Before (Silent Failures):**

```typescript
const tasks = await client.getTasks();
// Empty array could mean no tasks OR an error occurred
if (tasks.length === 0) {
  // Ambiguous - is this an error or just no data?
}
```

**After (Proper Error Handling):**

```typescript
try {
  const tasks = await client.getTasks();
  // Empty array definitely means no tasks
  if (tasks.length === 0) {
    showMessage("No tasks found");
  }
} catch (error) {
  // Definitely an error
  handleError(error);
}
```

### Gradual Migration

1. **Keep existing code working** by using `errorHandling: 'silent'`
2. **Enable logging** with `logLevel: 'error'` to identify issues
3. **Gradually update** code to use try-catch blocks
4. **Switch to throw mode** once all error handling is in place

```typescript
// Step 1: Add silent mode
const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  errorHandling: "silent",
  logLevel: "error", // See errors in console
});

// Step 2: Update one component at a time
// In new/updated components:
async function NewComponent() {
  try {
    const data = await client.getTasks();
    // handle data
  } catch (error) {
    // handle error
  }
}

// Step 3: Once all components are updated, switch to throw mode
const client = new SahoolApiClient({
  baseUrl: "http://localhost",
  errorHandling: "throw", // Now all errors are properly handled
});
```

## Best Practices

1. **Use throw mode for new code** - More reliable and debuggable
2. **Set appropriate log levels** - Use 'error' in production, 'debug' in development
3. **Handle errors specifically** - Check error types and respond appropriately
4. **Log errors with context** - Use custom logger for better observability
5. **Don't catch and ignore** - Always handle or propagate errors
6. **Test error scenarios** - Test how your app handles different error types

## Error Context

All errors include context for debugging:

```typescript
try {
  await client.getTasks();
} catch (error) {
  console.log(error.toJSON());
  // {
  //   name: 'NetworkError',
  //   message: 'Network error: Failed to fetch',
  //   code: 'NETWORK_ERROR',
  //   endpoint: 'http://localhost:8103/api/v1/tasks',
  //   method: 'GET',
  //   timestamp: '2025-01-01T12:00:00.000Z',
  //   stack: '...'
  // }
}
```

This rich error context helps with debugging and monitoring in production environments.
