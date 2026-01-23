# @sahool/api-client

Enhanced API client for the SAHOOL Agricultural Platform with advanced error handling, retry logic, caching, and type safety.

## Features

- **Error Handling**: Comprehensive error types with bilingual messages (Arabic/English)
- **Retry Logic**: Exponential backoff with configurable retry strategies
- **Request Caching**: In-memory cache with TTL and stale-while-revalidate support
- **Request Interceptors**: Performance tracking, deduplication, and request transformers
- **Type Safety**: Runtime validation and type guards
- **Circuit Breaker**: Automatic service health management

## Installation

```bash
npm install @sahool/api-client
# or
pnpm add @sahool/api-client
```

## Quick Start

```typescript
import { createApiClient } from "@sahool/api-client";

const client = createApiClient({
  baseUrl: "http://localhost:8000",
  locale: "ar",
  getToken: () => localStorage.getItem("token"),
  onUnauthorized: () => {
    // Handle 401 - redirect to login
    window.location.href = "/login";
  },
});

// Fetch tasks
const tasks = await client.getTasks({ status: "pending" });
```

## Enhanced Configuration

```typescript
import { createApiClient, CacheTTL } from "@sahool/api-client";

const client = createApiClient({
  baseUrl: "http://localhost:8000",
  timeout: 30000,
  locale: "ar",

  // Authentication
  getToken: () => localStorage.getItem("token"),
  setToken: (token) => localStorage.setItem("token", token),
  onUnauthorized: () => window.location.href = "/login",

  // Multi-tenancy
  tenantId: "tenant-123",
  // Or dynamic tenant
  getTenantId: () => getCurrentTenant(),

  // Error handling
  errorHandling: "throw", // "throw" | "silent"
  logLevel: "error", // "none" | "error" | "warn" | "info" | "debug"

  // Retry configuration
  retry: {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 30000,
    backoffMultiplier: 2,
    jitter: true,
    retryableStatusCodes: [408, 429, 500, 502, 503, 504],
    onRetry: (error, attempt, delay) => {
      console.log(`Retry ${attempt} in ${delay}ms`);
    },
  },

  // Cache configuration
  cache: {
    enabled: true,
    defaultTTL: CacheTTL.MEDIUM, // 5 minutes
    maxEntries: 100,
    staleWhileRevalidate: true,
    staleGracePeriod: CacheTTL.SHORT, // 1 minute
  },
  // Or use presets: "aggressive" | "conservative" | "offline"

  // Circuit breaker
  circuitBreaker: {
    failureThreshold: 5,
    resetTimeout: 30000,
    successThreshold: 3,
  },

  // Custom logger
  logger: {
    error: (msg, ctx) => Sentry.captureMessage(msg, ctx),
    warn: console.warn,
    info: console.info,
    debug: () => {}, // Suppress debug in production
  },
});
```

## Convenience Factory Functions

```typescript
import {
  createOfflineFirstClient,
  createRealtimeClient,
  createMinimalClient,
} from "@sahool/api-client";

// For offline-first mobile apps
const offlineClient = createOfflineFirstClient({
  baseUrl: "http://localhost:8000",
});

// For real-time dashboards (minimal caching)
const realtimeClient = createRealtimeClient({
  baseUrl: "http://localhost:8000",
});

// Without advanced features
const minimalClient = createMinimalClient({
  baseUrl: "http://localhost:8000",
});
```

## Error Handling

### Error Types

```typescript
import {
  ApiError,
  NetworkError,
  AuthError,
  AuthorizationError,
  NotFoundError,
  ValidationError,
  ServerError,
  TimeoutError,
  RateLimitError,
  isApiError,
  isNetworkError,
  isAuthError,
} from "@sahool/api-client";

try {
  const task = await client.getTask("invalid-id");
} catch (error) {
  if (error instanceof NotFoundError) {
    console.log("Task not found");
  } else if (error instanceof AuthError) {
    console.log("Please login");
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after ${error.retryAfter}s`);
  } else if (error instanceof NetworkError) {
    console.log("Network error - check your connection");
  } else if (isApiError(error)) {
    console.log(`API Error: ${error.code} - ${error.message}`);
    console.log(`Endpoint: ${error.endpoint}`);
    console.log(`Method: ${error.method}`);
  }
}
```

### Result-Based Error Handling

```typescript
import { success, failure, toResult, Result } from "@sahool/api-client";

// Use requestSafe for Result-based responses
const result = await client.requestSafe<Task[]>(
  `${client.urls.task}/api/v1/tasks`,
  { params: { status: "pending" } }
);

if (result.success) {
  console.log("Tasks:", result.data);
} else {
  console.error("Error:", result.error.message);
}

// Wrap any promise in a Result
const wrappedResult = await toResult(fetchData());
```

## Caching

### Cache Policies

```typescript
// Per-request cache configuration
const tasks = await client.request<Task[]>(endpoint, {
  cache: {
    enabled: true,
    ttl: CacheTTL.SHORT, // 1 minute
    policy: "stale-while-revalidate",
    forceRefresh: false,
  },
});

// Disable caching for a request
const freshData = await client.request<Data>(endpoint, {
  cache: false,
});

// Force refresh (bypass cache)
const refreshed = await client.request<Data>(endpoint, {
  cache: { forceRefresh: true },
});
```

### Cache TTL Presets

```typescript
import { CacheTTL } from "@sahool/api-client";

CacheTTL.VERY_SHORT  // 30 seconds - rapidly changing data
CacheTTL.SHORT       // 1 minute
CacheTTL.MEDIUM      // 5 minutes - default
CacheTTL.LONG        // 15 minutes
CacheTTL.VERY_LONG   // 1 hour
CacheTTL.DAY         // 24 hours - static data
CacheTTL.NONE        // No caching
```

### Cache Management

```typescript
// Clear all cache
client.clearCache();

// Invalidate by pattern
client.invalidateCache(/\/api\/v1\/tasks/);

// Get cache statistics
const stats = client.getCacheStats();
console.log(`Hit ratio: ${(stats.hitRatio * 100).toFixed(1)}%`);
console.log(`Entries: ${stats.size}`);
```

## Retry Logic

### Exponential Backoff

```typescript
import { withRetry, calculateDelay } from "@sahool/api-client";

// Wrap any async function with retry
const data = await withRetry(
  () => fetchData(),
  {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 30000,
    backoffMultiplier: 2,
    jitter: true,
    onRetry: (error, attempt, delay) => {
      console.log(`Attempt ${attempt} failed, retrying in ${delay}ms`);
    },
    onExhausted: (error, attempts) => {
      console.log(`All ${attempts} attempts failed`);
    },
  }
);
```

## Circuit Breaker

### Automatic Service Protection

```typescript
// Get circuit breaker status
const status = client.getCircuitBreakerStatus("weather");
if (status?.isOpen) {
  console.log(`Weather service unavailable. Resets in ${status.timeUntilReset}ms`);
}

// Manual reset
client.resetCircuitBreaker("weather");
```

### Standalone Circuit Breaker

```typescript
import { CircuitBreaker, CircuitOpenError } from "@sahool/api-client";

const breaker = new CircuitBreaker({
  failureThreshold: 5,
  resetTimeout: 30000,
  successThreshold: 3,
  onOpen: (failures) => console.log(`Circuit opened after ${failures} failures`),
  onClose: () => console.log("Circuit closed"),
  onHalfOpen: () => console.log("Circuit half-open, testing..."),
});

try {
  const result = await breaker.execute(() => fetchFromService());
} catch (error) {
  if (error instanceof CircuitOpenError) {
    // Service temporarily unavailable
    return cachedFallback();
  }
  throw error;
}
```

## Type Validation

### Runtime Validation

```typescript
import {
  TaskSchema,
  FarmSchema,
  createSchema,
  validateResponse,
  isTask,
  isFarm,
} from "@sahool/api-client";

// Validate response data
const task = TaskSchema.parse(responseData); // Throws if invalid
const result = TaskSchema.safeParse(responseData); // Returns ValidationResult

if (result.success) {
  console.log("Valid task:", result.data);
} else {
  console.log("Validation errors:", result.errors);
}

// Type guards
if (isTask(data)) {
  // data is narrowed to Task type
  console.log(data.title);
}
```

### Custom Schemas

```typescript
import { createSchema } from "@sahool/api-client";

const CustomSchema = createSchema<MyType>({
  id: { type: "string", required: true },
  name: { type: "string", required: true, minLength: 1, maxLength: 100 },
  email: { type: "string", required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
  age: { type: "number", min: 0, max: 150 },
  status: { type: "enum", enum: ["active", "inactive"] },
  tags: { type: "array", items: { type: "string" }, min: 1, max: 10 },
});

const isValid = CustomSchema.isValid(data);
const validated = CustomSchema.parse(data);
```

## Async State Management

```typescript
import {
  AsyncState,
  idle,
  loading,
  successState,
  errorState,
  isLoading,
  isSuccess,
  isError,
  getDataOrDefault,
} from "@sahool/api-client";

// In React/Vue state
const [state, setState] = useState<AsyncState<Task[]>>(idle());

async function fetchTasks() {
  setState(loading());

  try {
    const tasks = await client.getTasks();
    setState(successState(tasks));
  } catch (error) {
    setState(errorState(error as Error));
  }
}

// Render based on state
if (isLoading(state)) {
  return <Spinner />;
}

if (isError(state)) {
  return <Error message={state.error.message} />;
}

if (isSuccess(state)) {
  return <TaskList tasks={state.data} />;
}

// Get data with fallback
const tasks = getDataOrDefault(state, []);
```

## Performance Monitoring

```typescript
// Get request performance statistics
const stats = client.getPerformanceStats();

console.log(`Total requests: ${stats.totalRequests}`);
console.log(`Success rate: ${(stats.successfulRequests / stats.totalRequests * 100).toFixed(1)}%`);
console.log(`Average duration: ${stats.averageDuration.toFixed(0)}ms`);
console.log(`Slow requests: ${stats.slowRequests}`);

// Get endpoint-specific stats
const endpointStats = stats.requestsByEndpoint.get("/api/v1/tasks");
if (endpointStats) {
  console.log(`Tasks endpoint avg: ${endpointStats.averageDuration}ms`);
}

// Cancel all pending requests
client.cancelAllRequests("User navigated away");
```

## API Methods

### Tasks

```typescript
await client.getTasks(params);          // List tasks
await client.getTask(taskId);           // Get single task
await client.createTask(task);          // Create task
await client.updateTask(taskId, data);  // Update task
await client.updateTaskStatus(id, status);
await client.deleteTask(taskId);
await client.completeTask(taskId, evidence);
```

### Fields & Farms

```typescript
await client.getFields(params);         // List fields
await client.getField(fieldId);         // Get single field
await client.getFarms();                // List farms
await client.getFarmById(farmId);       // Get single farm
```

### Weather

```typescript
await client.getWeather(locationId);
await client.getWeatherForecast(locationId, days);
await client.getWeatherAlerts();
```

### Diagnosis

```typescript
await client.getDiagnoses(params);
await client.getDiagnosisStats();
await client.updateDiagnosisStatus(id, status, notes);
```

### Dashboard & Indicators

```typescript
await client.getDashboardStats();
await client.getDashboard(tenantId);
await client.getFieldIndicators(fieldId);
```

### Other APIs

```typescript
await client.getSensorReadings(farmId);
await client.getEquipment(params);
await client.getNotifications(params);
await client.markNotificationRead(id);
await client.getCommunityPosts(params);
await client.health();
await client.checkServicesHealth();
```

### Paginated Requests

```typescript
// Fetch all pages automatically
const allTasks = await client.fetchAllPages<Task>(
  `${client.urls.task}/api/v1/tasks`,
  { status: "pending" },
  {
    pageSize: 50,
    maxPages: 10,
    onProgress: (loaded, total) => {
      console.log(`Loaded ${loaded} of ${total}`);
    },
  }
);
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Kong Gateway | 8000 | Main API Gateway |
| WebSocket | 8081 | Real-time events |
| satellite-service | 8090 | Satellite analysis |
| indicators-service | 8091 | Agricultural indicators |
| weather-service | 8092 | Weather data |
| fertilizer-advisor | 8093 | Fertilizer recommendations |
| irrigation-smart | 8094 | Smart irrigation |
| crop-health-ai | 8095 | Crop health diagnosis |
| virtual-sensors | 8096 | Virtual sensor data |
| yield-engine | 8098 | Yield predictions |
| equipment-service | 8101 | Equipment management |
| community | 8102 | Community features |
| task-service | 8103 | Task management |
| notification-service | 8110 | Notifications |
| field-management | 3000 | Field management |
| marketplace | 3010 | Agricultural marketplace |

## Types

```typescript
import type {
  // Core types
  Task, CreateTaskRequest, TaskEvidence,
  Field, Farm,
  WeatherData, WeatherForecast, WeatherAlert,
  DiagnosisRecord, DiagnosisStats,
  DashboardStats, DashboardData, FieldIndicators,
  SensorReading, Equipment,
  Notification, CommunityPost,
  Alert, AlertFilters, AlertStats,
  User, AuthState, LoginRequest, LoginResponse,

  // API response types
  ApiResponse, PaginatedResponse,

  // Geometry types (GeoJSON)
  Coordinates, GeoPoint, GeoPolygon, GeoFeature, GeoFeatureCollection,

  // Configuration types
  ApiClientConfig, ServicePorts, LogLevel,

  // Status types
  TaskStatus, DiagnosisStatus, FarmStatus,
  Priority, Severity, AlertSeverity, AlertCategory, AlertStatus,

  // Enhanced types
  RetryConfig, CacheConfig, CircuitBreakerConfig,
  ValidationResult, Result, AsyncState,
} from "@sahool/api-client";
```

## License

MIT
