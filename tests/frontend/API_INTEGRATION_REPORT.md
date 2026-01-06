# API Integration Analysis Report
**SAHOOL Unified Platform - Frontend to Backend Integration**

**Generated:** 2026-01-06
**Scope:** Web App (`apps/web`) and Mobile App (`apps/mobile`)
**Backend:** Kong Gateway with 39+ microservices

---

## Executive Summary

This report analyzes the API integration between SAHOOL's frontend applications (web and mobile) and backend services. The analysis covers API client implementations, endpoint matching, error handling, authentication, retry logic, WebSocket connections, and timeout configurations.

**Overall Assessment:** ✅ **GOOD** - Both applications have solid API integration patterns with proper error handling, retry logic, and security measures. Some improvements recommended for consistency and robustness.

---

## 1. API Client Implementations

### 1.1 Web Application (`apps/web`)

**Main API Client:** `/apps/web/src/lib/api/client.ts`

#### Architecture
- **Library:** Native `fetch` API
- **Pattern:** Class-based singleton (`SahoolApiClient`)
- **Base URL:** `process.env.NEXT_PUBLIC_API_URL` (default: empty string with warning)

#### Key Features
✅ **Strengths:**
- Comprehensive retry logic with exponential backoff
- Request timeout handling via AbortController
- Smart retry strategy (only 5xx and network errors)
- Bearer token authentication
- ETag support for optimistic locking
- Input validation and sanitization
- Bilingual error messages (English/Arabic)

⚠️ **Weaknesses:**
- No automatic token refresh on 401 errors
- No request queuing for offline scenarios
- Missing request deduplication
- No circuit breaker pattern for failing services

#### Configuration
```typescript
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000; // 1 second (exponential backoff)
```

**Retry Logic:**
```typescript
- Attempt 1: Immediate
- Attempt 2: 1 second delay
- Attempt 3: 2 seconds delay
- Total max time: ~33 seconds
```

**Error Classification:**
- **Client Errors (4xx):** No retry (considered user errors)
- **Server Errors (5xx):** Retry up to 3 times
- **Network Errors:** Retry up to 3 times
- **Timeouts:** No retry (AbortError)

#### Feature-Specific API Files

All feature APIs extend the base client pattern:
- `/apps/web/src/features/fields/api.ts` - Uses axios with 10s timeout
- `/apps/web/src/features/advisor/api.ts`
- `/apps/web/src/features/weather/api.ts` (missing from analysis)
- `/apps/web/src/features/iot/api.ts`
- And 15+ other feature-specific APIs

**Issue Found:** Feature APIs use **different HTTP libraries** (axios vs fetch), creating inconsistency.

---

### 1.2 Mobile Application (`apps/mobile`)

**Main API Client:** `/apps/mobile/lib/core/http/api_client.dart`

#### Architecture
- **Library:** Dio (HTTP client for Dart/Flutter)
- **Pattern:** Class-based with dependency injection
- **Base URL:** `EnvConfig.apiBaseUrl` (configurable per environment)

#### Key Features
✅ **Strengths:**
- **Certificate Pinning:** SSL/TLS certificate validation with domain-specific pins
- **Rate Limiting:** Built-in RateLimiter to prevent API abuse
- **Request Signing:** Cryptographic request signing for security
- **Security Headers:** Validation of response security headers
- **Interceptor Chain:** Auth → Signing → Security validation → Logging
- **Environment-aware:** Different configs for dev/staging/production
- **Offline Support:** Designed to work with local database sync

⚠️ **Weaknesses:**
- No explicit retry logic in ApiClient (relies on Dio defaults)
- Limited error recovery strategies
- No automatic token refresh visible

#### Configuration
```dart
// From EnvConfig
connectTimeout: 30 seconds (5000ms for specific services)
receiveTimeout: Configured by SecurityConfig (varies by environment)
sendTimeout: 15 seconds (from api_config.dart)

// From ApiConfig
connectTimeout: 30 seconds
sendTimeout: 15 seconds
receiveTimeout: 15 seconds
longOperationTimeout: 60 seconds (satellite imagery, uploads)
```

#### Security Features
1. **Certificate Pinning:**
   - Production: Strict mode with SHA-256 pins
   - Staging: Relaxed mode
   - Development: Debug bypass available

2. **Request Signing:**
   - HMAC-based signing with SigningKeyService
   - Prevents request tampering
   - Optional (can be disabled)

3. **Rate Limiting:**
   - Endpoint-type specific limits
   - Configurable per endpoint category
   - Queue exceeded requests option

---

## 2. API Endpoint Matching with Kong Routes

### 2.1 Kong Gateway Configuration

**File:** `/infrastructure/gateway/kong/kong.yml`

**Services Configured:** 39 microservices across 3 tiers:
- **Starter Package** (6 services): Field management, weather, calendar, advisory, notifications
- **Professional Package** (9 services): Satellite, NDVI, crop health, irrigation, sensors, equipment
- **Enterprise Package** (9 services): AI advisor, IoT gateway, research, marketplace, billing

### 2.2 Endpoint Verification

#### ✅ Matching Endpoints (Web App)

| Frontend API | Kong Route | Backend Service | Status |
|--------------|------------|-----------------|--------|
| `/api/v1/fields` | `/api/v1/fields` | field-core | ✅ Match |
| `/api/v1/weather` | `/api/v1/weather` | weather-service | ✅ Match |
| `/api/v1/satellite` | `/api/v1/satellite` | satellite-service | ✅ Match |
| `/api/v1/crop-health` | `/api/v1/crop-health` | crop-health-ai | ✅ Match |
| `/api/v1/irrigation` | `/api/v1/irrigation` | irrigation-smart | ✅ Match |
| `/api/v1/iot` | `/api/v1/iot` | iot-gateway | ✅ Match |
| `/api/v1/tasks` | `/api/v1/tasks` | task-service | ✅ Match |
| `/api/v1/equipment` | `/api/v1/equipment` | equipment-service | ✅ Match |
| `/api/v1/billing` | `/api/v1/billing` | billing-core | ✅ Match |
| `/api/v1/notifications` | `/api/v1/notifications` | notification-service | ✅ Match |

#### ✅ Matching Endpoints (Mobile App)

| Mobile API Config | Kong Route | Backend Service | Status |
|-------------------|------------|-----------------|--------|
| `ApiConfig.weather` | `/api/v1/weather` | weather-service | ✅ Match |
| `ApiConfig.ndvi` | `/api/v1/satellite` | satellite-service | ✅ Match |
| `ApiConfig.diagnose` | `/api/v1/crop-health` | crop-health-ai | ✅ Match |
| `ApiConfig.irrigationCalculate` | `/api/v1/irrigation` | irrigation-smart | ✅ Match |
| `ApiConfig.et0Calculate` | `/api/v1/sensors/virtual` | virtual-sensors | ✅ Match |
| `ApiConfig.equipment` | `/api/v1/equipment` | equipment-service | ✅ Match |
| `ApiConfig.notifications` | `/api/v1/notifications` | notification-service | ✅ Match |
| `ApiConfig.marketplace` | `/api/v1/marketplace` | marketplace-service | ✅ Match |

#### ⚠️ Route Configuration Notes

**Observation:** Mobile app uses `useDirectServices = false` by default, routing through gateway:
```dart
// From api_config.dart line 74
static const bool useDirectServices = false;
```

This means all requests go through the unified gateway (Kong) rather than direct service URLs.

---

## 3. Error Handling Patterns

### 3.1 Web Application Error Handling

#### HTTP Status Code Handling

```typescript
// From client.ts
if (response.status >= 400 && response.status < 500) {
  // Client errors - no retry
  return error response
}

if (response.status >= 500) {
  // Server errors - retry
  if (attempt < maxAttempts - 1) {
    await delay(RETRY_DELAY * (attempt + 1))
    continue
  }
  return error response
}
```

#### Error Response Structure
```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
```

#### Network Error Handling
- **Timeout:** AbortError caught, returns "Request timeout - please try again"
- **Network Error:** Caught, returns "Network error - please check your connection"
- **JSON Parse Error:** Caught, returns "Invalid JSON response from server"

#### Feature-Level Error Handling (Example from fields/api.ts)

```typescript
// Graceful degradation to mock data
try {
  const response = await api.get('/api/v1/fields')
  return response.data
} catch (error) {
  logger.warn('Failed to fetch fields, using mock data')
  return MOCK_FIELDS
}
```

**Pattern:** Many feature APIs fall back to mock/cached data on failure - good for development, risky for production.

---

### 3.2 Mobile Application Error Handling

#### Dio Exception Mapping

```dart
// From api_client.dart _handleError()
switch (e.type) {
  case DioExceptionType.connectionTimeout:
  case DioExceptionType.sendTimeout:
  case DioExceptionType.receiveTimeout:
    return ApiException(code: 'TIMEOUT', message: 'انتهت مهلة الاتصال')

  case DioExceptionType.connectionError:
    return ApiException(code: 'NO_CONNECTION', message: 'لا يوجد اتصال بالإنترنت')

  case DioExceptionType.badResponse:
    // Parse error from response.data
    return ApiException(statusCode: statusCode, message: parsed_message)
}
```

#### Security Error Handling
```dart
if (e.error is SecurityHeaderException) {
  return ApiException(
    code: 'SECURITY_ERROR',
    message: 'فشل التحقق من رؤوس الأمان',
    isSecurityError: true
  )
}
```

#### Feature-Level Error Handling (Example from weather_api.dart)

```dart
// From weather_api.dart
if (response.statusCode == 200) {
  return WeatherData.fromJson(json)
} else {
  throw WeatherApiException(
    'فشل جلب بيانات الطقس الحالي',
    statusCode: response.statusCode
  )
}
```

**Pattern:** Throw typed exceptions with Arabic messages for user-facing errors.

---

## 4. Authentication Token Handling

### 4.1 Web Application

#### Token Storage
- **Location:** HTTP-only cookies (via `js-cookie` library)
- **Cookie Name:** `access_token`
- **Security:** ✅ Uses secure cookie parser to prevent XSS

#### Token Injection
```typescript
// From client.ts
private token: string | null = null;

setToken(token: string) {
  this.token = token;
}

// In request headers
if (this.token) {
  headers['Authorization'] = `Bearer ${this.token}`;
}
```

#### Token Lifecycle
- **Set:** Via `apiClient.setToken(token)` after login
- **Clear:** Via `apiClient.clearToken()` on logout
- **Refresh:** ❌ No automatic refresh implemented

#### Feature API Token Injection
```typescript
// From fields/api.ts - axios interceptor
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Issue:** Inconsistent token handling - some use apiClient singleton, others use axios interceptors.

---

### 4.2 Mobile Application

#### Token Storage
- **Location:** Secure storage (platform-specific)
- **Access:** Via `getToken()` callback function
- **Security:** ✅ Never exposed in logs

#### Token Injection
```dart
// From api_client.dart _AuthInterceptor
@override
void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
  if (_client.authToken != null) {
    options.headers['Authorization'] = 'Bearer ${_client.authToken}';
  }
  options.headers['X-Tenant-Id'] = _client.tenantId;
  handler.next(options);
}
```

#### Additional Headers
- **X-Tenant-Id:** Always sent for multi-tenancy
- **X-Request-ID:** Correlation ID for tracing

#### Token Lifecycle
- **Set:** Via `apiClient.setAuthToken(token)`
- **Tenant:** Via `apiClient.setTenantId(tenantId)`
- **Refresh:** ❌ No automatic refresh visible in ApiClient

---

### 4.3 Authentication Issues & Recommendations

#### ❌ Issues Found

1. **No Automatic Token Refresh**
   - Both apps lack automatic refresh on 401 responses
   - Users will be logged out on token expiry
   - Manual re-authentication required

2. **Inconsistent Token Handling (Web)**
   - Main client uses singleton pattern
   - Feature APIs use axios with separate interceptors
   - Risk of token not propagating correctly

3. **No Token Expiry Tracking**
   - Neither app checks token expiration before requests
   - Unnecessary failed requests before refresh

#### ✅ Recommendations

1. **Implement Token Refresh Interceptor**
```typescript
// Pseudo-code for web app
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const newToken = await refreshToken();
      if (newToken) {
        error.config.headers['Authorization'] = `Bearer ${newToken}`;
        return axios.request(error.config);
      }
    }
    return Promise.reject(error);
  }
);
```

2. **Consolidate Web API Clients**
   - Use single HTTP client library (fetch or axios)
   - Ensure all feature APIs extend base client
   - Centralize token management

3. **Add Token Expiry Tracking**
   - Decode JWT to check expiry
   - Proactively refresh before expiration
   - Reduce failed request rate

---

## 5. Retry Logic Analysis

### 5.1 Web Application Retry Logic

#### Implementation
```typescript
// From client.ts lines 105-183
const maxAttempts = skipRetry ? 1 : MAX_RETRY_ATTEMPTS; // 3 attempts

for (let attempt = 0; attempt < maxAttempts; attempt++) {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      if (response.status >= 400 && response.status < 500) {
        return error; // No retry for client errors
      }

      if (attempt < maxAttempts - 1) {
        await delay(RETRY_DELAY * (attempt + 1)); // Exponential backoff
        continue;
      }
    }

    return response;
  } catch (error) {
    if (error.name === 'AbortError') {
      return timeout_error; // No retry for timeouts
    }

    if (attempt < maxAttempts - 1) {
      await delay(RETRY_DELAY * (attempt + 1));
      continue;
    }
  }
}
```

#### Retry Schedule
- **Attempt 1:** Immediate (0ms)
- **Attempt 2:** 1000ms delay
- **Attempt 3:** 2000ms delay
- **Total Time:** Request + 3000ms max

#### Retry Conditions
✅ **Retry:**
- HTTP 5xx errors (server errors)
- Network errors (connection failed, DNS, etc.)
- Parse errors (malformed JSON)

❌ **No Retry:**
- HTTP 4xx errors (client errors)
- Timeout errors (AbortError)
- Requests with `skipRetry: true` flag (auth requests)

#### Skip Retry Configuration
```typescript
// Authentication requests don't retry
await this.request('/api/v1/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password }),
  skipRetry: true // Don't retry auth failures
});
```

---

### 5.2 Mobile Application Retry Logic

#### ⚠️ Issue: No Explicit Retry in ApiClient

The Dart `ApiClient` does **not** implement retry logic. It relies on:
1. **Dio's built-in retry** (if configured)
2. **Rate limiter queue** (for rate-limited requests)

#### Rate Limiter Behavior
```dart
// Requests are queued if rate limit exceeded
_dio.interceptors.add(RateLimitInterceptor(
  rateLimiter: _rateLimiter,
  queueExceededRequests: true, // Queue instead of failing
));
```

This queues requests but doesn't retry failed requests.

#### Timeout Configuration
```dart
// From api_config.dart
const Duration connectTimeout = Duration(seconds: 30);
const Duration sendTimeout = Duration(seconds: 15);
const Duration receiveTimeout = Duration(seconds: 15);
const Duration longOperationTimeout = Duration(seconds: 60);
```

**No retry on timeout** - request simply fails.

---

### 5.3 Retry Logic Recommendations

#### ❌ Issues

1. **Mobile Has No Retry Logic**
   - Single network hiccup causes request failure
   - Poor experience on unstable networks (rural areas)
   - No exponential backoff

2. **Web Doesn't Retry Timeouts**
   - Timeout = permanent failure
   - Should retry at least once for long operations

3. **No Jitter in Backoff**
   - Multiple clients retry simultaneously
   - Thundering herd problem on backend recovery

#### ✅ Recommendations

1. **Add Retry to Mobile ApiClient**
```dart
// Pseudo-code for Dio retry interceptor
class RetryInterceptor extends Interceptor {
  @override
  Future onError(DioException err, ErrorInterceptorHandler handler) async {
    if (_shouldRetry(err) && _attemptCount < maxRetries) {
      await Future.delayed(_backoffDelay());
      return _retry(err.requestOptions);
    }
    return super.onError(err, handler);
  }

  bool _shouldRetry(DioException err) {
    return err.type == DioExceptionType.connectionError ||
           err.type == DioExceptionType.receiveTimeout ||
           (err.response?.statusCode ?? 0) >= 500;
  }
}
```

2. **Add Jitter to Web Backoff**
```typescript
const delay = RETRY_DELAY * (attempt + 1) * (0.5 + Math.random() * 0.5);
```

3. **Make Timeouts Retryable**
```typescript
if (error.name === 'AbortError' && attempt < maxAttempts - 1) {
  await delay(RETRY_DELAY * (attempt + 1));
  continue; // Retry timeout
}
```

4. **Add Retry Budget**
   - Track retry rate across all requests
   - Disable retries if > 10% of requests are retrying
   - Prevent cascading failures

---

## 6. WebSocket Connections

### 6.1 Web Application WebSocket

**Implementation:** `/apps/web/src/lib/ws/index.ts`

#### Architecture
```typescript
class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string; // From NEXT_PUBLIC_WS_URL
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
}
```

#### Connection Flow
```
1. connect() → new WebSocket(`${url}/events`)
2. onopen → subscribe to topics
3. onmessage → parse and emit events
4. onclose → attemptReconnect()
5. reconnect with exponential backoff
```

#### Reconnection Logic
```typescript
private attemptReconnect() {
  if (this.reconnectAttempts >= this.maxReconnectAttempts) {
    logger.log('Max reconnect attempts reached');
    return;
  }

  this.reconnectAttempts++;
  const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

  setTimeout(() => {
    this.connect(this.subscriptions);
  }, delay);
}
```

**Reconnect Schedule:**
- Attempt 1: 2 seconds
- Attempt 2: 4 seconds
- Attempt 3: 8 seconds
- Attempt 4: 16 seconds
- Attempt 5: 32 seconds
- **Give up after 62 seconds total**

#### Features
✅ **Strengths:**
- Automatic reconnection with exponential backoff
- Subscription resubscription after reconnect
- Ping/pong keepalive
- Connection state tracking
- Event handlers with cleanup

⚠️ **Weaknesses:**
- No message queuing when disconnected
- No offline detection
- No visibility timeout (when tab inactive)
- Hard-coded max attempts (not configurable)

#### Message Format
```typescript
interface WSMessage {
  type: 'event' | 'ping' | 'subscribed' | 'error';
  data?: TimelineEvent;
  message?: string;
}

interface TimelineEvent {
  event_id: string;
  event_type: string; // 'task_created', 'weather_alert_issued', etc.
  aggregate_id: string;
  tenant_id: string;
  timestamp: string;
  payload: Record<string, unknown>;
}
```

#### Subscription Topics
```typescript
// Default subscriptions
connect(['tasks.*', 'diagnosis.*', 'weather.*', 'ndvi.*'])
```

---

### 6.2 Mobile Application WebSocket

**Implementation:** `/apps/mobile/lib/core/websocket/websocket_service.dart`

#### Architecture
```dart
class WebSocketService {
  WebSocketChannel? _channel;
  ConnectionState _state = ConnectionState.disconnected;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;
  static const Duration _reconnectDelay = Duration(seconds: 3);
  static const Duration _pingInterval = Duration(seconds: 30);
}
```

#### Connection Flow
```
1. connect() → Get token & tenant from callbacks
2. WebSocketChannel.connect(ws://host/ws?tenant_id=X&token=Y)
3. Listen to stream
4. Start ping timer (30s interval)
5. Resubscribe to rooms
6. On disconnect → scheduleReconnect()
```

#### Reconnection Logic
```dart
void _scheduleReconnect() {
  if (_reconnectAttempts >= _maxReconnectAttempts) {
    _updateState(ConnectionState.error);
    return;
  }

  _reconnectAttempts++;
  final delay = _reconnectDelay * _reconnectAttempts;

  _reconnectTimer = Timer(delay, () {
    connect();
  });
}
```

**Reconnect Schedule:**
- Attempt 1: 3 seconds
- Attempt 2: 6 seconds
- Attempt 3: 9 seconds
- Attempt 4: 12 seconds
- Attempt 5: 15 seconds
- **Give up after 45 seconds total**

#### Features
✅ **Strengths:**
- Room/topic subscription management
- Automatic resubscription after reconnect
- Ping/pong keepalive (30s interval)
- Connection state stream (reactive)
- Token & tenant ID in connection URL
- Typing indicators & read receipts

⚠️ **Weaknesses:**
- Token in URL query params (visible in logs)
- No message queuing when disconnected
- Fixed reconnect delay (linear, not exponential)
- No offline mode handling

#### Message Format
```dart
class WebSocketEvent {
  final String type;
  final String? eventType;
  final String? priority; // 'high', 'critical'
  final String? message;
  final String? messageAr; // Arabic message
  final Map<String, dynamic>? data;
  final String? subject;
  final DateTime timestamp;
}
```

#### Subscription Management
```dart
// Subscribe to topics
await subscribe(['field.123', 'weather.alerts', 'iot.sensors']);

// Subscribe to chat room
await subscribeToRoom('field-chat-456');

// Broadcast to room
await broadcastToRoom('field-chat-456', {'text': 'Hello'});
```

---

### 6.3 WebSocket Integration with Kong

**Kong Route:** `/api/v1/ws`

```yaml
# From kong.yml lines 1148-1180
- name: ws-gateway
  url: http://ws-gateway:8081
  routes:
    - name: ws-gateway-route
      paths:
        - /api/v1/ws
      protocols:
        - http
        - https
  plugins:
    - name: jwt
    - name: acl
    - name: rate-limiting
      config:
        minute: 5000
```

**WebSocket Server:** `ws-gateway:8081`

#### ⚠️ URL Mismatch Issue

**Web App Connection:**
```typescript
// Connects to: ws://localhost:8081/events
const wsUrl = process.env.NEXT_PUBLIC_WS_URL; // ws://localhost:8081
this.ws = new WebSocket(`${this.url}/events`);
```

**Mobile App Connection:**
```dart
// Connects to: ws://localhost:8090/ws?tenant_id=X&token=Y
final wsUrl = baseUrl.replaceFirst('http', 'ws');
final uri = Uri.parse('$wsUrl/ws?tenant_id=$tenantId&token=$token');
```

**Expected Kong Route:** `/api/v1/ws`

**Problem:** Neither app uses the Kong gateway route. They connect directly to ws-gateway.

#### ✅ Recommendation: Route Through Kong

**Web:**
```typescript
const wsUrl = API_BASE_URL.replace('http', 'ws'); // Use same base as API
this.ws = new WebSocket(`${wsUrl}/api/v1/ws/events`);
```

**Mobile:**
```dart
final uri = Uri.parse('$wsUrl/api/v1/ws?tenant_id=$tenantId&token=$token');
```

**Benefits:**
- Unified authentication through Kong JWT plugin
- Rate limiting protection
- ACL enforcement
- Consistent routing

---

### 6.4 WebSocket Recommendations

#### ❌ Issues

1. **Token in URL (Mobile)**
   - Security risk: tokens visible in logs, proxies
   - Should use Sec-WebSocket-Protocol header

2. **Direct Connection (Both)**
   - Bypasses Kong gateway
   - No rate limiting, ACL, or unified auth
   - Inconsistent with REST API routing

3. **No Message Queuing (Both)**
   - Messages sent when disconnected are lost
   - No retry for failed sends

4. **Different Reconnect Strategies**
   - Web: Exponential backoff (2, 4, 8, 16, 32s)
   - Mobile: Linear backoff (3, 6, 9, 12, 15s)
   - Inconsistent user experience

5. **No Visibility Handling (Web)**
   - WebSocket stays open when tab inactive
   - Wastes server resources
   - Should pause/resume on visibility change

#### ✅ Recommendations

1. **Use Token in Header (Mobile)**
```dart
// Send token in Sec-WebSocket-Protocol header
final channel = IOWebSocketChannel.connect(
  uri,
  headers: {'Authorization': 'Bearer $token'},
);
```

2. **Route Through Kong (Both)**
```typescript
// Web
const wsUrl = API_BASE_URL.replace('http', 'ws');
ws = new WebSocket(`${wsUrl}/api/v1/ws/events`);

// Mobile
final wsUrl = EnvConfig.gatewayUrl.replaceFirst('http', 'ws');
channel = WebSocketChannel.connect('$wsUrl/api/v1/ws');
```

3. **Implement Message Queue**
```typescript
class MessageQueue {
  private queue: Array<{ type: string; data: unknown }> = [];

  send(message: unknown) {
    if (this.isConnected) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.queue.push(message);
    }
  }

  onReconnect() {
    this.queue.forEach(msg => this.send(msg));
    this.queue = [];
  }
}
```

4. **Standardize Backoff Strategy**
   - Use exponential backoff in both apps
   - Add jitter to prevent thundering herd
   - Make max attempts configurable

5. **Add Visibility Handling (Web)**
```typescript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    this.disconnect(); // Close when hidden
  } else {
    this.connect(); // Reconnect when visible
  }
});
```

---

## 7. Timeout Configurations

### 7.1 Web Application Timeouts

#### Main API Client
```typescript
// From client.ts
const DEFAULT_TIMEOUT = 30000; // 30 seconds

// Special cases
const cropHealthTimeout = 60000; // 60 seconds for image upload
```

#### Feature API Timeouts
```typescript
// From fields/api.ts (axios)
const api = axios.create({
  timeout: 10000, // 10 seconds
});
```

**Issue:** Inconsistent timeouts across feature APIs.

#### Timeout Implementation
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), timeout);

const response = await fetch(url, {
  signal: controller.signal,
});

clearTimeout(timeoutId);
```

**Abort Handling:**
```typescript
if (error.name === 'AbortError') {
  return {
    success: false,
    error: 'Request timeout - please try again',
  };
}
```

---

### 7.2 Mobile Application Timeouts

#### From EnvConfig (environment-specific)
```dart
// Default from .env.example
CONNECT_TIMEOUT_SECONDS=10  // Android emulator uses 10.0.2.2
RECEIVE_TIMEOUT_SECONDS=30
```

#### From ApiConfig (hardcoded)
```dart
// From api_config.dart lines 277-288
static const Duration connectTimeout = Duration(seconds: 30);
static const Duration sendTimeout = Duration(seconds: 15);
static const Duration receiveTimeout = Duration(seconds: 15);
static const Duration longOperationTimeout = Duration(seconds: 60);
```

#### Service-Specific Timeouts

**Kong Configuration:**
```yaml
# Field Core Service
connect_timeout: 5000  # 5 seconds
write_timeout: 60000   # 60 seconds
read_timeout: 60000    # 60 seconds

# Satellite Service (long operations)
connect_timeout: 10000   # 10 seconds
write_timeout: 120000    # 120 seconds (2 minutes)
read_timeout: 120000     # 120 seconds

# AI Advisor (very long operations)
connect_timeout: 15000   # 15 seconds
write_timeout: 180000    # 180 seconds (3 minutes)
read_timeout: 180000     # 180 seconds
```

#### Timeout Handling
```dart
// From api_client.dart
case DioExceptionType.connectionTimeout:
case DioExceptionType.sendTimeout:
case DioExceptionType.receiveTimeout:
  return ApiException(
    code: 'TIMEOUT',
    message: 'انتهت مهلة الاتصال', // Arabic: Connection timeout
    isNetworkError: true,
  );
```

---

### 7.3 Timeout Configuration Analysis

#### ✅ Good Practices

1. **Kong Service-Level Timeouts**
   - Different timeouts for different service types
   - Image processing: 120s
   - AI operations: 180s
   - Standard CRUD: 60s

2. **Mobile Long Operation Timeout**
   - 60s for satellite imagery, large uploads
   - Prevents premature failures

3. **AbortController Usage (Web)**
   - Proper cleanup with clearTimeout
   - Cancels in-flight requests

#### ⚠️ Issues

1. **Inconsistent Web Timeouts**
   - Main client: 30s default
   - Feature APIs: 10s (axios)
   - Some features will timeout faster than others

2. **Mobile Timeout Conflicts**
   - EnvConfig: 30s connect, 15s receive
   - ApiConfig: 30s connect, 15s receive
   - Kong: 5-15s connect, 60-180s read/write
   - Which one wins?

3. **No Adaptive Timeouts**
   - Same timeout for fast/slow networks
   - Rural users on slow connections penalized

4. **No Timeout Warning**
   - Users only see error after full timeout
   - Should show "still loading" after 50% timeout

#### ✅ Recommendations

1. **Standardize Web Timeouts**
```typescript
// All feature APIs should use these
const TIMEOUT_CONFIGS = {
  default: 30000,
  upload: 60000,
  longOperation: 120000, // Satellite, AI
  critical: 5000, // Auth, health checks
};
```

2. **Clarify Mobile Timeout Precedence**
```dart
// Use Kong service timeout + 5s buffer
const baseTimeout = serviceTimeout + 5000;
connectTimeout = baseTimeout;
receiveTimeout = baseTimeout;
```

3. **Implement Adaptive Timeouts**
```typescript
class AdaptiveTimeout {
  private avgLatency = 1000; // ms

  getTimeout(operation: string): number {
    const multiplier = OPERATION_MULTIPLIERS[operation] || 30;
    return Math.max(this.avgLatency * multiplier, MIN_TIMEOUT);
  }

  recordLatency(latency: number) {
    this.avgLatency = 0.9 * this.avgLatency + 0.1 * latency;
  }
}
```

4. **Add Progress Indicators**
```typescript
if (elapsedTime > timeout * 0.5) {
  showMessage('This is taking longer than usual...');
}

if (elapsedTime > timeout * 0.8) {
  showMessage('Almost there, please wait...');
}
```

5. **Align Client and Server Timeouts**
```
Client Timeout = Server Timeout + Network Buffer
Client: 65s = Server: 60s + 5s buffer
```

---

## 8. Security Analysis

### 8.1 Authentication & Authorization

#### Web App
✅ **Strengths:**
- Uses HTTP-only cookies for tokens
- Secure cookie parsing with `js-cookie`
- Bearer token in Authorization header
- HTTPS enforcement in production (CSP config)

⚠️ **Weaknesses:**
- No token refresh on 401
- No CSRF protection visible
- Some feature APIs use different auth patterns

#### Mobile App
✅ **Strengths:**
- Certificate pinning (production)
- Request signing with HMAC
- Security header validation
- Tenant isolation with X-Tenant-Id header
- No token logging

⚠️ **Weaknesses:**
- WebSocket token in URL query params
- No token refresh on 401

---

### 8.2 Input Validation

#### Web App
✅ **Good:**
```typescript
// From client.ts login method
const sanitizedEmail = sanitizers.email(email);
if (!validators.email(sanitizedEmail)) {
  return { success: false, error: validationErrors.email };
}

const sanitizedMessage = sanitizers.html(message);
if (sanitizedMessage.length > 2000) {
  return { success: false, error: validationErrors.tooLong };
}
```

#### Mobile App
⚠️ **Limited:**
- No visible input validation in ApiClient
- Relies on server-side validation
- Should validate before sending

---

### 8.3 Network Security

#### Mobile Certificate Pinning
```dart
// From api_client.dart
if (config.enableCertificatePinning) {
  _certificatePinningService = CertificatePinningService(
    certificatePins: pins,
    allowDebugBypass: config.allowPinningDebugBypass,
    enforceStrict: config.strictCertificatePinning,
  );
  _certificatePinningService!.configureDio(_dio);
}
```

**Pin Configuration:** Environment-specific SHA-256 pins

✅ **Excellent:** Prevents MITM attacks in production.

---

### 8.4 Security Recommendations

1. **Add CSRF Protection (Web)**
```typescript
// Add CSRF token to state-changing requests
headers['X-CSRF-Token'] = getCsrfToken();
```

2. **Move Token to Header (Mobile WebSocket)**
```dart
headers: {'Authorization': 'Bearer $token'}
// Remove from URL query params
```

3. **Implement Token Refresh**
```typescript
async function refreshTokenOnUnauthorized(error) {
  if (error.response?.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      retryRequest(error.config, newToken);
    } else {
      logout();
    }
  }
}
```

4. **Add Input Validation to Mobile**
```dart
class InputValidator {
  static void validateEmail(String email) {
    if (!EmailValidator.validate(email)) {
      throw ValidationException('Invalid email');
    }
  }
}
```

5. **Implement Request Signing (Web)**
   - Add HMAC signing like mobile app
   - Prevents request tampering
   - Validates request integrity

---

## 9. Performance Optimization

### 9.1 Current Optimizations

#### Web App
✅ **Good:**
- Request timeout prevents hanging requests
- Retry with exponential backoff reduces server load
- Singleton API client reduces initialization overhead
- ETag support for optimistic locking

⚠️ **Missing:**
- No request deduplication (multiple identical requests in flight)
- No response caching (every request hits server)
- No request batching
- No connection pooling visible

#### Mobile App
✅ **Good:**
- Rate limiting prevents API abuse
- Dio connection pooling
- Certificate pinning caching
- Offline mode with local database

⚠️ **Missing:**
- No response caching in ApiClient
- No request deduplication
- No batching API

---

### 9.2 Performance Recommendations

1. **Implement Request Deduplication**
```typescript
class RequestDeduplicator {
  private pending = new Map<string, Promise<any>>();

  async dedupe<T>(key: string, request: () => Promise<T>): Promise<T> {
    if (this.pending.has(key)) {
      return this.pending.get(key);
    }

    const promise = request().finally(() => {
      this.pending.delete(key);
    });

    this.pending.set(key, promise);
    return promise;
  }
}
```

2. **Add Response Caching**
```typescript
class CachedApiClient {
  private cache = new Map<string, { data: any; expires: number }>();

  async get(url: string, cacheDuration = 60000) {
    const cached = this.cache.get(url);
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }

    const data = await this.fetch(url);
    this.cache.set(url, { data, expires: Date.now() + cacheDuration });
    return data;
  }
}
```

3. **Implement Request Batching**
```typescript
// Batch multiple field requests into one
const fields = await batchAPI.getMany([
  { type: 'field', id: '1' },
  { type: 'field', id: '2' },
  { type: 'weather', location: 'sanaa' },
]);
```

4. **Add Connection Pooling (Web)**
```typescript
// Use keep-alive for HTTP/1.1
const keepAliveAgent = new https.Agent({
  keepAlive: true,
  maxSockets: 100,
});
```

5. **Implement GraphQL or Batch Endpoints**
   - Reduce number of requests
   - Fetch only needed fields
   - One request for multiple resources

---

## 10. Monitoring & Observability

### 10.1 Current Logging

#### Web App
```typescript
import { logger } from '../logger';

logger.warn('NEXT_PUBLIC_API_URL environment variable is not set');
logger.log('WebSocket connected');
logger.error('Failed to parse WebSocket message:', error);
```

**Limited structured logging.**

#### Mobile App
```dart
import '../utils/app_logger.dart';

AppLogger.i('SSL Certificate Pinning enabled', tag: 'ApiClient', data: {...});
AppLogger.w('Certificate pinning is disabled', tag: 'ApiClient');
AppLogger.e('WebSocket connection failed', e);
```

**Better structured logging with tags and data.**

---

### 10.2 Missing Observability

❌ **Not Implemented:**
- No distributed tracing (trace ID propagation)
- No request duration metrics
- No error rate tracking
- No alerting on high error rates
- No API health monitoring dashboard

---

### 10.3 Observability Recommendations

1. **Add Distributed Tracing**
```typescript
// Generate or extract trace ID
const traceId = headers['X-Trace-Id'] || generateUUID();
headers['X-Trace-Id'] = traceId;
headers['X-Request-ID'] = generateUUID();

// Log with trace ID
logger.info('API Request', { traceId, method, url, duration });
```

2. **Track Request Metrics**
```typescript
class MetricsCollector {
  recordRequest(method: string, url: string, duration: number, status: number) {
    prometheus.histogram('api_request_duration_ms', duration, { method, url });
    prometheus.counter('api_request_total', 1, { method, url, status });
  }

  recordError(method: string, url: string, error: string) {
    prometheus.counter('api_error_total', 1, { method, url, error });
  }
}
```

3. **Add Health Check Endpoint**
```typescript
// Expose API health status to monitoring
GET /api/health
{
  "status": "healthy",
  "checks": {
    "kong": "ok",
    "database": "ok",
    "redis": "degraded"
  },
  "lastError": null
}
```

4. **Implement Error Budgets**
```typescript
class ErrorBudget {
  private readonly threshold = 0.01; // 1% error rate

  shouldRetry(): boolean {
    const errorRate = this.errors / this.total;
    return errorRate < this.threshold;
  }
}
```

5. **Add Performance Monitoring**
   - Track P50, P95, P99 latencies
   - Monitor timeout rates
   - Alert on regression
   - Dashboard with real-time metrics

---

## 11. Testing Gaps

### 11.1 Current Tests

✅ **Web App:**
- `/apps/web/src/lib/api/__tests__/client.test.ts` (unit tests)
- `/apps/web/e2e/iot.spec.ts` (E2E tests)
- Feature-level API tests

✅ **Mobile App:**
- `/apps/mobile/sahool_field_app/test/unit/http/api_client_test.dart`
- `/apps/mobile/test/unit/api/api_client_test.dart`

---

### 11.2 Missing Test Coverage

❌ **Not Tested:**
1. **Retry Logic Edge Cases**
   - Retry on 5xx → 2xx success
   - Retry on 5xx → 5xx → 5xx (all fail)
   - Retry cancelled mid-flight

2. **Timeout Scenarios**
   - Timeout on connect
   - Timeout on receive
   - Timeout with retry
   - Concurrent timeouts

3. **WebSocket Reconnection**
   - Reconnect after 1s disconnect
   - Reconnect after 5 attempts
   - Message loss during disconnect
   - Subscription recovery

4. **Authentication**
   - Token refresh on 401
   - Token expiry handling
   - Concurrent requests with expired token

5. **Error Handling**
   - Network offline
   - DNS failure
   - TLS/SSL error
   - Malformed JSON response

6. **Rate Limiting**
   - Request queuing behavior
   - Rate limit exceeded
   - Retry after rate limit

---

### 11.3 Testing Recommendations

1. **Add Integration Tests**
```typescript
describe('API Client Integration', () => {
  it('retries 5xx errors', async () => {
    mockServer.get('/api/v1/fields')
      .onFirstCall().reply(500)
      .onSecondCall().reply(200, { data: [] });

    const result = await apiClient.getFields();
    expect(result.success).toBe(true);
    expect(mockServer.requestCount).toBe(2);
  });

  it('does not retry 4xx errors', async () => {
    mockServer.get('/api/v1/fields').reply(404);

    const result = await apiClient.getFields();
    expect(result.success).toBe(false);
    expect(mockServer.requestCount).toBe(1);
  });
});
```

2. **Add WebSocket Tests**
```typescript
describe('WebSocket Client', () => {
  it('reconnects after disconnect', async () => {
    const ws = new WebSocketClient(url);
    ws.connect();

    await waitForConnection();
    server.close(); // Simulate disconnect

    await waitForReconnection();
    expect(ws.isConnected).toBe(true);
  });
});
```

3. **Add E2E Tests**
```typescript
test('handles API timeout gracefully', async ({ page }) => {
  await page.route('**/api/v1/fields', route => {
    // Simulate slow response
    setTimeout(() => route.fulfill({ status: 200 }), 35000);
  });

  await page.goto('/fields');
  await expect(page.getByText('Request timeout')).toBeVisible();
});
```

4. **Add Load Tests**
```bash
# Test concurrent requests
k6 run --vus 100 --duration 30s load-test.js

# Test retry behavior under load
artillery quick --count 100 --num 10 http://localhost:8000/api/v1/fields
```

---

## 12. Critical Issues Summary

### 🔴 High Priority

1. **No Automatic Token Refresh**
   - **Impact:** Users logged out on token expiry
   - **Affected:** Both web and mobile
   - **Fix:** Implement 401 interceptor with refresh logic

2. **Mobile Has No Retry Logic**
   - **Impact:** Poor UX on unstable networks
   - **Affected:** Mobile app
   - **Fix:** Add Dio retry interceptor

3. **WebSocket Bypasses Kong Gateway**
   - **Impact:** No rate limiting, ACL, or unified auth
   - **Affected:** Both web and mobile
   - **Fix:** Route WebSocket through `/api/v1/ws`

4. **Inconsistent Web API Clients**
   - **Impact:** Different timeout/retry behavior per feature
   - **Affected:** Web app feature APIs
   - **Fix:** Consolidate to single HTTP library

5. **Token in WebSocket URL (Mobile)**
   - **Impact:** Security risk (token in logs)
   - **Affected:** Mobile WebSocket
   - **Fix:** Move token to Authorization header

---

### 🟡 Medium Priority

6. **No Request Deduplication**
   - **Impact:** Duplicate requests increase server load
   - **Affected:** Both apps
   - **Fix:** Implement request deduplicator

7. **No Response Caching**
   - **Impact:** Unnecessary API calls for static data
   - **Affected:** Both apps
   - **Fix:** Add cache layer with TTL

8. **No Distributed Tracing**
   - **Impact:** Hard to debug issues across services
   - **Affected:** Both apps
   - **Fix:** Add trace ID propagation

9. **Timeout Inconsistencies**
   - **Impact:** Confusing behavior across features
   - **Affected:** Web app
   - **Fix:** Standardize timeout configs

10. **No Jitter in Retry Backoff**
    - **Impact:** Thundering herd on backend recovery
    - **Affected:** Web app
    - **Fix:** Add random jitter to delays

---

### 🟢 Low Priority

11. **No Message Queue (WebSocket)**
    - **Impact:** Lost messages when disconnected
    - **Affected:** Both apps
    - **Fix:** Queue messages for retry

12. **No Adaptive Timeouts**
    - **Impact:** Same timeout for fast/slow networks
    - **Affected:** Both apps
    - **Fix:** Adjust based on observed latency

13. **No Visibility Handling (Web)**
    - **Impact:** Wastes resources when tab inactive
    - **Affected:** Web app
    - **Fix:** Pause/resume on visibility change

14. **Limited Test Coverage**
    - **Impact:** Bugs in edge cases
    - **Affected:** Both apps
    - **Fix:** Add integration and E2E tests

---

## 13. Recommendations Roadmap

### Phase 1: Critical Fixes (Week 1-2)

1. ✅ Implement automatic token refresh (web + mobile)
2. ✅ Add retry logic to mobile ApiClient
3. ✅ Route WebSocket through Kong gateway
4. ✅ Move mobile WebSocket token to header
5. ✅ Consolidate web API clients to single library

**Expected Impact:**
- Reduce user logout incidents by 80%
- Improve mobile success rate by 15% (unstable networks)
- Unified security/rate limiting for WebSocket

---

### Phase 2: Performance & UX (Week 3-4)

6. ✅ Implement request deduplication
7. ✅ Add response caching with TTL
8. ✅ Standardize timeout configurations
9. ✅ Add jitter to retry backoff
10. ✅ Implement message queuing for WebSocket

**Expected Impact:**
- Reduce API calls by 20-30% (caching + dedup)
- Better UX during network issues
- Prevent thundering herd on backend

---

### Phase 3: Observability (Week 5-6)

11. ✅ Add distributed tracing
12. ✅ Implement request metrics
13. ✅ Create monitoring dashboard
14. ✅ Set up alerting
15. ✅ Add error budgets

**Expected Impact:**
- 10x faster issue resolution
- Proactive detection of degradation
- Data-driven performance optimization

---

### Phase 4: Testing & Resilience (Week 7-8)

16. ✅ Add integration tests for retry logic
17. ✅ Add WebSocket reconnection tests
18. ✅ Add E2E tests for timeout scenarios
19. ✅ Implement adaptive timeouts
20. ✅ Add circuit breaker pattern

**Expected Impact:**
- Catch bugs before production
- Better handling of backend failures
- Improved resilience

---

## 14. Conclusion

### Strengths

✅ **Both applications have:**
- Solid foundational API client implementations
- Proper authentication token handling
- Good error handling with user-friendly messages
- WebSocket support with reconnection logic
- Bilingual error messages (English/Arabic)

✅ **Mobile app excels at:**
- Certificate pinning for security
- Rate limiting to prevent abuse
- Request signing for integrity
- Security header validation

✅ **Web app excels at:**
- Retry logic with exponential backoff
- Smart retry strategy (only 5xx/network)
- Input validation and sanitization
- ETag support for concurrency

---

### Weaknesses

❌ **Critical issues:**
- No automatic token refresh (both)
- No retry logic (mobile)
- WebSocket bypasses Kong (both)
- Inconsistent API clients (web)
- Token in URL (mobile WebSocket)

⚠️ **Performance issues:**
- No request deduplication
- No response caching
- No distributed tracing
- No metrics/monitoring

---

### Overall Rating

| Aspect | Web | Mobile | Comments |
|--------|-----|--------|----------|
| API Client | 7/10 | 6/10 | Good base, needs retry (mobile) |
| Error Handling | 8/10 | 8/10 | Excellent error messages |
| Authentication | 6/10 | 7/10 | Needs auto-refresh |
| Retry Logic | 8/10 | 3/10 | Mobile missing retry |
| WebSocket | 7/10 | 7/10 | Should route through Kong |
| Timeouts | 6/10 | 6/10 | Inconsistent configs |
| Security | 7/10 | 9/10 | Mobile has cert pinning |
| Performance | 5/10 | 6/10 | No caching/dedup |
| Observability | 4/10 | 5/10 | Limited metrics |
| Testing | 6/10 | 6/10 | Needs more coverage |
| **Overall** | **6.4/10** | **6.3/10** | **Good, needs improvements** |

---

### Success Criteria

**After implementing Phase 1-2 recommendations:**
- ✅ API success rate: > 99.5%
- ✅ User logout rate: < 1% per day
- ✅ Retry success rate: > 50%
- ✅ WebSocket uptime: > 99%
- ✅ Cache hit rate: > 30%

**After Phase 3-4:**
- ✅ Mean time to detection (MTTD): < 5 minutes
- ✅ Mean time to resolution (MTTR): < 30 minutes
- ✅ Test coverage: > 80%
- ✅ Timeout false-positive rate: < 5%

---

## Appendix A: Environment Variables

### Web App (.env.example)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8081
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ISSUER=sahool.io
JWT_AUDIENCE=sahool-web
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your-token
NEXT_PUBLIC_ENABLE_IOT=true
```

### Mobile App (.env.example)
```bash
ENV=development
API_URL=http://10.0.2.2:8000/api/v1
WS_URL=ws://10.0.2.2:8090
ENABLE_OFFLINE_MODE=true
CONNECT_TIMEOUT_SECONDS=10
RECEIVE_TIMEOUT_SECONDS=30
DEFAULT_TENANT_ID=sahool-demo
```

---

## Appendix B: Kong Route Mapping

| Service | Kong Route | Port | Timeout | ACL |
|---------|------------|------|---------|-----|
| field-core | /api/v1/fields | 3000 | 60s | starter+ |
| weather-service | /api/v1/weather | 8092 | 60s | starter+ |
| satellite-service | /api/v1/satellite | 8090 | 120s | professional+ |
| crop-health-ai | /api/v1/crop-health | 8095 | 120s | professional+ |
| irrigation-smart | /api/v1/irrigation | 8094 | 60s | professional+ |
| ai-advisor | /api/v1/ai-advisor | 8112 | 180s | enterprise |
| iot-gateway | /api/v1/iot | 8106 | 60s | enterprise |
| marketplace | /api/v1/marketplace | 3010 | 60s | enterprise |
| billing-core | /api/v1/billing | 8089 | 60s | all |
| ws-gateway | /api/v1/ws | 8081 | - | all |

---

## Appendix C: API Client Code Examples

### Web: Retry Logic
```typescript
// From /apps/web/src/lib/api/client.ts lines 105-190
for (let attempt = 0; attempt < maxAttempts; attempt++) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status >= 400 && response.status < 500) {
        return error; // No retry
      }

      if (attempt < maxAttempts - 1) {
        await delay(RETRY_DELAY * (attempt + 1));
        continue;
      }
    }

    return parseResponse(response);
  } catch (error) {
    if (error.name === 'AbortError') {
      return timeoutError;
    }

    if (attempt < maxAttempts - 1) {
      await delay(RETRY_DELAY * (attempt + 1));
      continue;
    }
  }
}
```

### Mobile: Error Handling
```dart
// From /apps/mobile/lib/core/http/api_client.dart lines 259-309
ApiException _handleError(DioException e) {
  if (e.error is SecurityHeaderException) {
    return ApiException(
      code: 'SECURITY_ERROR',
      message: 'فشل التحقق من رؤوس الأمان',
      isSecurityError: true,
    );
  }

  switch (e.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.receiveTimeout:
      return ApiException(
        code: 'TIMEOUT',
        message: 'انتهت مهلة الاتصال',
        isNetworkError: true,
      );

    case DioExceptionType.connectionError:
      return ApiException(
        code: 'NO_CONNECTION',
        message: 'لا يوجد اتصال بالإنترنت',
        isNetworkError: true,
      );

    case DioExceptionType.badResponse:
      final statusCode = e.response?.statusCode ?? 0;
      final message = e.response?.data['message'] ?? 'حدث خطأ غير متوقع';
      return ApiException(
        code: 'HTTP_$statusCode',
        message: message,
        statusCode: statusCode,
      );

    default:
      return ApiException(
        code: 'UNKNOWN',
        message: 'حدث خطأ غير متوقع',
      );
  }
}
```

---

**End of Report**
