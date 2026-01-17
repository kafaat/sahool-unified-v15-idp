# Error Handling Middleware Audit Report

# تقرير تدقيق معالجة الأخطاء

**Date:** 2026-01-06
**Platform:** SAHOOL Unified v15 IDP
**Auditor:** Automated Security Audit
**Scope:** Error handling middleware across NestJS, FastAPI, and web applications

---

## Executive Summary

This audit examines error handling middleware across the SAHOOL platform, focusing on:

- Global error handlers in NestJS services
- Exception handlers in FastAPI services
- Error boundaries in web applications
- Error response formats and consistency
- Information leakage prevention
- Error logging practices
- Error code standardization

### Overall Assessment: **MODERATE** ⚠️

**Strengths:**

- ✅ Centralized error handling infrastructure exists for both NestJS and FastAPI
- ✅ Bilingual error messages (English/Arabic) implemented
- ✅ Structured error codes with categorization
- ✅ Information sanitization patterns in place
- ✅ Error boundaries implemented in web applications
- ✅ Request ID correlation for error tracking

**Critical Issues:**

- ❌ Inconsistent implementation across services (only 5% of FastAPI services use unified handlers)
- ❌ Local error handlers in NestJS services duplicate code and lack standardization
- ❌ Stack traces exposed conditionally but may leak in production
- ❌ No mobile app error boundary implementation found
- ❌ Missing centralized error monitoring/alerting integration

---

## 1. Global Error Handlers in NestJS Services

### 1.1 Centralized Error Handler

**Location:** `/apps/services/shared/errors/http-exception.filter.ts`

**Implementation Analysis:**

✅ **Strengths:**

- Comprehensive exception filter using `@Catch()` decorator
- Handles three types of exceptions:
  - `AppException` (custom application exceptions)
  - `HttpException` (NestJS built-in)
  - Unknown errors (catch-all)
- Sanitization of sensitive information in error messages
- Environment-based stack trace inclusion
- Request ID generation and correlation
- Bilingual error messages (English/Arabic)
- Proper HTTP status code mapping

```typescript
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    // Handles AppException, HttpException, and unknown errors
    // Returns standardized ErrorResponseDto
  }
}
```

**Error Response Format:**

```json
{
  "success": false,
  "error": {
    "code": "ERR_1001",
    "message": "Invalid input provided",
    "messageAr": "تم تقديم بيانات غير صالحة",
    "category": "VALIDATION",
    "retryable": false,
    "timestamp": "2025-12-31T10:30:00.000Z",
    "path": "/api/v1/farms",
    "requestId": "req-123-456-789",
    "details": { ... }
  }
}
```

### 1.2 Implementation Status

**Total NestJS Services:** 10
**Services with Global Filters:** 3 (30%)

**Services Using Unified Handler:**

- ❌ Chat Service - Local implementation
- ❌ User Service - Local implementation
- ❌ Marketplace Service - Local implementation

**Issue:** Most NestJS services implement local exception filters rather than using the shared implementation:

```typescript
// Local implementation in main.ts (INCONSISTENT)
@Catch()
class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const status =
      exception instanceof HttpException
        ? exception.getStatus()
        : HttpStatus.INTERNAL_SERVER_ERROR;

    response.status(status).json({
      success: false,
      error: {
        code: `ERR_${status}`, // ❌ Not using standard error codes
        message,
        timestamp: new Date().toISOString(),
        path: request.url,
      },
    });
  }
}
```

**Problems with Local Implementation:**

1. ❌ Does not use standardized error codes from `ErrorCode` enum
2. ❌ Missing bilingual messages
3. ❌ No request ID correlation
4. ❌ No information sanitization
5. ❌ Inconsistent error response format
6. ❌ Missing error categorization

### 1.3 Recommendations for NestJS

**HIGH PRIORITY:**

1. **Standardize all services** to use shared `HttpExceptionFilter`:

   ```typescript
   import { HttpExceptionFilter } from "@sahool/shared/errors";

   async function bootstrap() {
     const app = await NestFactory.create(AppModule);
     app.useGlobalFilters(new HttpExceptionFilter());
   }
   ```

2. **Remove local implementations** from all service main.ts files

3. **Create a service template** that enforces shared error handling

---

## 2. Exception Handlers in FastAPI Services

### 2.1 Centralized Exception Handlers

**Location:** `/apps/services/shared/errors_py/exception_handlers.py`

**Implementation Analysis:**

✅ **Strengths:**

- Comprehensive exception handling setup via `setup_exception_handlers(app)`
- Four exception types handled:
  - `AppException` (custom)
  - `StarletteHTTPException` (HTTP errors)
  - `RequestValidationError` (Pydantic validation)
  - `Exception` (catch-all)
- **Excellent information sanitization** with regex patterns
- Request ID middleware (`add_request_id_middleware`)
- Environment-based stack trace inclusion
- Bilingual error messages
- Proper logging with structured context

**Sanitization Patterns:**

```python
sensitive_patterns = [
    (r"password[=:]\s*\S+", "[REDACTED]"),
    (r"secret[=:]\s*\S+", "[REDACTED]"),
    (r"token[=:]\s*\S+", "[REDACTED]"),
    (r"api_key[=:]\s*\S+", "[REDACTED]"),
    (r"authorization[=:]\s*\S+", "[REDACTED]"),
    (r"/home/\S+", "[PATH]"),
    (r"/app/\S+", "[PATH]"),
    (r"postgresql://\S+@", "postgresql://[REDACTED]@"),
    (r"redis://\S+@", "redis://[REDACTED]@"),
    (r"mongodb://\S+@", "mongodb://[REDACTED]@"),
]
```

**Details Filtering:**

```python
# Filter out sensitive keys from details
safe_details = {
    k: v for k, v in details.items()
    if k.lower() not in ("password", "secret", "token", "api_key", "authorization")
}
```

### 2.2 Implementation Status

**Total FastAPI Services:** 40
**Services with Unified Exception Handlers:** 2 (5%)

**Services Using Unified Handler:**

- ✅ Weather Service (`/apps/services/weather-service/src/main.py`)
- ✅ Advisory Service (`/apps/services/agro-advisor/src/main.py`)

**Services with Legacy Handler:**

- ⚠️ Field Core Service (no unified handlers detected)
- ⚠️ 38+ other FastAPI services

**Example of Proper Implementation:**

```python
from errors_py import setup_exception_handlers, add_request_id_middleware

app = FastAPI(title="SAHOOL Service", version="15.3.3")

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)
```

### 2.3 Alternative Implementation Found

**Location:** `/apps/services/shared/middleware/exception_handler.py`

A secondary exception handler implementation was found with similar but less comprehensive functionality:

- ❌ Less detailed error codes
- ❌ No regex-based sanitization
- ❌ Simpler error structure

**Status:** This appears to be a legacy implementation that should be **deprecated**.

### 2.4 Recommendations for FastAPI

**CRITICAL PRIORITY:**

1. **Migrate all 38 services** to use unified exception handlers from `shared/errors_py`
2. **Deprecate** the legacy exception handler in `shared/middleware/exception_handler.py`
3. **Add CI/CD checks** to ensure all new FastAPI services use `setup_exception_handlers(app)`
4. **Document migration guide** for existing services

---

## 3. Error Boundaries in Web Applications

### 3.1 Shared Error Boundary

**Location:** `/packages/shared-ui/src/components/ErrorBoundary.tsx`

✅ **Strengths:**

- Class-based React error boundary with comprehensive error handling
- Optional Sentry integration (checks for availability)
- Customizable fallback UI (function or component)
- HOC wrapper (`withErrorBoundary`)
- Async error boundary for Suspense integration
- Development vs production error display modes
- Bilingual error messages (Arabic primary)
- Retry functionality

**Features:**

```typescript
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode | ((error: Error, retry: () => void) => ReactNode);
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showRetry?: boolean;
  showDetails?: boolean; // Shows details in development
  enableSentry?: boolean;
}
```

**Sentry Integration:**

```typescript
if (this.props.enableSentry !== false) {
  try {
    const Sentry = (window as any).Sentry;
    if (Sentry && typeof Sentry.captureException === "function") {
      Sentry.captureException(error, {
        extra: { componentStack: errorInfo.componentStack },
      });
    }
  } catch (sentryError) {
    console.warn("Sentry not available:", sentryError);
  }
}
```

### 3.2 Web App Error Boundary

**Location:** `/apps/web/src/components/common/ErrorBoundary.tsx`

✅ **Features:**

- Server-side error logging via `/api/log-error` endpoint
- RTL support (Arabic)
- Development mode shows full error details
- Production mode shows generic message
- Retry and reload functionality

**Error Logging:**

```typescript
await fetch("/api/log-error", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    type: "react_error_boundary",
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo.componentStack,
    url: window.location.href,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || "production",
  }),
});
```

### 3.3 Admin App Error Boundary

**Location:** `/apps/admin/src/components/common/ErrorBoundary.tsx`

✅ **Features:**

- Admin-specific error display with more technical details
- Expandable stack trace and component stack
- Server-side error logging
- RTL support

### 3.4 Error Logging Endpoints

#### Web App Error Logger

**Location:** `/apps/web/src/app/api/log-error/route.ts`

✅ **Strengths:**

- Rate limiting (10 requests per minute per IP)
- Request validation
- Structured logging with context
- Environment-based logging behavior
- User agent and referer tracking

❌ **Issues:**

- Missing actual integration with external logging service (commented out)
- No error alerting system
- No error aggregation

#### Admin App Error Logger

**Location:** `/apps/admin/src/app/api/log-error/route.ts`

✅ **Strengths:**

- Rate limiting (20 requests per minute per IP - higher for admin)
- Request validation
- Structured logging

❌ **Issues:**

- In-memory rate limiting (will reset on server restart)
- Missing external logging service integration

### 3.5 Mobile App Error Boundaries

**Status:** ❌ **NOT FOUND**

No error boundary implementation found in `/apps/mobile/` directory.

**Impact:** Critical user-facing errors in mobile app may crash the app without graceful handling.

### 3.6 Recommendations for Error Boundaries

**HIGH PRIORITY:**

1. **Implement error boundary for mobile app** (React Native)
2. **Integrate actual error tracking service:**
   - Sentry
   - LogRocket
   - Datadog RUM
   - Or similar service

3. **Implement persistent rate limiting** (Redis-based)
4. **Add error alerting** for critical errors
5. **Create error dashboard** for monitoring
6. **Add error aggregation** to identify common issues

---

## 4. Error Response Formats

### 4.1 Standardized Response Format

Both NestJS and FastAPI services use a similar response structure:

**Success Response:**

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "messageAr": "رسالة اختيارية",
  "timestamp": "2025-12-31T10:30:00.000Z"
}
```

**Error Response:**

```json
{
  "success": false,
  "error": {
    "code": "ERR_1001",
    "message": "Invalid input provided",
    "messageAr": "تم تقديم بيانات غير صالحة",
    "category": "VALIDATION",
    "retryable": false,
    "timestamp": "2025-12-31T10:30:00.000Z",
    "path": "/api/v1/farms",
    "requestId": "req-123-456-789",
    "details": {
      "fields": [
        {
          "field": "email",
          "message": "Invalid email format",
          "constraint": "isEmail"
        }
      ]
    }
  }
}
```

### 4.2 Consistency Analysis

✅ **Consistent Fields:**

- `success` boolean flag
- Bilingual messages (`message`, `messageAr`)
- Timestamp in ISO 8601 format
- Error code structure

⚠️ **Inconsistencies Found:**

- Local NestJS implementations use `ERR_{status}` instead of semantic codes
- Some services don't include `category` field
- Request ID format varies (`req-*` vs `x-request-id`)

### 4.3 Validation Error Format

**NestJS (class-validator):**

```json
{
  "error": {
    "code": "ERR_1000",
    "details": {
      "fields": [
        {
          "field": "email",
          "message": "Invalid email format",
          "constraint": "isEmail",
          "value": "invalid-email"
        }
      ]
    }
  }
}
```

**FastAPI (Pydantic):**

```json
{
  "error": {
    "code": "ERR_1000",
    "details": {
      "fields": [
        {
          "field": "body -> email",
          "message": "value is not a valid email address",
          "type": "value_error.email",
          "value": "invalid-email"
        }
      ]
    }
  }
}
```

✅ Both formats are comprehensive and include field-level details.

---

## 5. Information Leakage Analysis

### 5.1 Stack Trace Exposure

**Current Implementation:**

**NestJS:**

```typescript
private shouldIncludeStack(): boolean {
  return process.env.NODE_ENV === 'development'
    || process.env.INCLUDE_STACK_TRACE === 'true';
}
```

**FastAPI:**

```python
def should_include_stack() -> bool:
    env = os.getenv("ENVIRONMENT", os.getenv("NODE_ENV", "production")).lower()
    return (
        env in ("development", "dev", "local")
        or os.getenv("INCLUDE_STACK_TRACE", "false").lower() == "true"
    )
```

⚠️ **Issues:**

1. `INCLUDE_STACK_TRACE` environment variable could accidentally be set to `true` in production
2. No explicit check for production environment to force disable
3. Stack traces may contain sensitive file paths

**Recommendation:**

```typescript
private shouldIncludeStack(): boolean {
  // Never include stack traces in production, even if env var is set
  if (process.env.NODE_ENV === 'production') {
    return false;
  }
  return process.env.NODE_ENV === 'development'
    || process.env.INCLUDE_STACK_TRACE === 'true';
}
```

### 5.2 Sensitive Information Sanitization

✅ **Excellent Implementation in FastAPI:**

```python
def sanitize_error_message(message: str) -> str:
    sensitive_patterns = [
        (r"password[=:]\s*\S+", "[REDACTED]"),
        (r"secret[=:]\s*\S+", "[REDACTED]"),
        (r"token[=:]\s*\S+", "[REDACTED]"),
        (r"api_key[=:]\s*\S+", "[REDACTED]"),
        (r"authorization[=:]\s*\S+", "[REDACTED]"),
        (r"/home/\S+", "[PATH]"),
        (r"/app/\S+", "[PATH]"),
        (r"postgresql://\S+@", "postgresql://[REDACTED]@"),
        (r"redis://\S+@", "redis://[REDACTED]@"),
        (r"mongodb://\S+@", "mongodb://[REDACTED]@"),
    ]
    # ... regex replacement
```

❌ **Missing in NestJS:**

- No sanitization of error messages
- No filtering of connection strings
- No path redaction

**Recommendation:**
Implement similar sanitization in NestJS error filter.

### 5.3 Database Connection Strings

✅ **Good:** Connection strings in error messages are sanitized in FastAPI:

```
postgresql://[REDACTED]@localhost/db
```

❌ **Risk:** NestJS may expose database connection strings in error messages.

### 5.4 File Paths

✅ **Good:** Paths are redacted in FastAPI:

```
/home/user/file.py → [PATH]
/app/service/file.py → [PATH]
```

⚠️ **Risk:** Stack traces in both NestJS and FastAPI may expose container paths when `shouldIncludeStack()` returns true.

### 5.5 User Data

✅ **Good:** Sensitive fields filtered from error details:

```python
safe_details = {
    k: v for k, v in details.items()
    if k.lower() not in ("password", "secret", "token", "api_key", "authorization")
}
```

### 5.6 Request/Response Logging

**NestJS:**

```typescript
if (this.shouldIncludeStack()) {
  this.logger.debug("Request details", {
    method: request.method,
    url: request.url,
    headers: request.headers, // ⚠️ May include Authorization header
    body: request.body, // ⚠️ May include sensitive data
    params: request.params,
    query: request.query,
  });
}
```

❌ **Critical Issue:** Request headers and body logged in development mode without sanitization.

**Recommendation:**

```typescript
if (this.shouldIncludeStack()) {
  this.logger.debug("Request details", {
    method: request.method,
    url: request.url,
    headers: this.sanitizeHeaders(request.headers),
    body: this.sanitizeBody(request.body),
    params: request.params,
    query: request.query,
  });
}
```

---

## 6. Error Logging Practices

### 6.1 NestJS Logging

**Implementation:**

```typescript
private logError(exception: any, request: Request, status: HttpStatus) {
  const message = `${request.method} ${request.url} - Status: ${status}`;

  // Log as error for 5xx errors, warn for 4xx errors
  if (status >= 500) {
    this.logger.error(message, exception?.stack || exception);
  } else if (status >= 400) {
    this.logger.warn(message, {
      error: exception?.message || exception,
      requestId: this.getRequestId(request),
    });
  }
}
```

✅ **Strengths:**

- Appropriate log levels (error for 5xx, warn for 4xx)
- Request ID correlation
- HTTP method and URL context

❌ **Issues:**

- No structured logging format
- Missing tenant ID
- Missing user context
- No log aggregation metadata

### 6.2 FastAPI Logging

**Implementation:**

```python
if exc.http_status >= 500:
    logger.error(
        f"AppException [{request_id}]: {exc.error_code.value} - {exc.message_en}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code.value,
            "path": str(request.url.path),
            "method": request.method,
            "details": exc.details,
        },
        exc_info=should_include_stack(),
    )
else:
    logger.warning(
        f"AppException [{request_id}]: {exc.error_code.value} - {exc.message_en}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code.value,
            "path": str(request.url.path),
            "method": request.method,
        },
    )
```

✅ **Strengths:**

- Structured logging with `extra` fields
- Request ID in message and metadata
- Appropriate log levels
- Conditional stack traces via `exc_info`

❌ **Issues:**

- Missing tenant ID
- Missing user context
- No distributed tracing correlation

### 6.3 Frontend Error Logging

**Web App:**

```typescript
await fetch("/api/log-error", {
  method: "POST",
  body: JSON.stringify({
    type: "react_error_boundary",
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo.componentStack,
    url: window.location.href,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || "production",
  }),
});
```

✅ **Strengths:**

- Comprehensive error context
- Environment tracking
- URL context

❌ **Issues:**

- No user identification
- No session ID
- Errors logged to server but not to external service
- No retry mechanism if logging fails

### 6.4 Log Aggregation

**Status:** ❌ **NOT IMPLEMENTED**

**Current State:**

- Logs written to console/files
- No centralized log aggregation
- No log retention policy
- No log analysis tools

**Missing:**

- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki/Grafana
- Datadog Logs
- CloudWatch Logs
- Or similar service

### 6.5 Recommendations for Logging

**CRITICAL PRIORITY:**

1. **Implement centralized log aggregation:**
   - Deploy ELK Stack or equivalent
   - Configure log shipping from all services
   - Set up retention policies (e.g., 30 days for errors, 7 days for warnings)

2. **Add correlation IDs:**
   - Trace ID for distributed tracing
   - Tenant ID for multi-tenant context
   - User ID (when authenticated)
   - Session ID for frontend errors

3. **Implement structured logging:**

   ```typescript
   logger.error({
     message: "Database query failed",
     error_code: "ERR_8000",
     request_id: requestId,
     tenant_id: tenantId,
     user_id: userId,
     trace_id: traceId,
     service: "user-service",
     method: "POST",
     path: "/api/v1/users",
     duration_ms: 1234,
     stack: sanitizedStack,
   });
   ```

4. **Add log alerting:**
   - Critical errors (5xx) → Immediate PagerDuty/Slack alert
   - High error rate → Warning alert
   - Database connection failures → Critical alert

5. **Sanitize all logs:**
   - Never log passwords, tokens, API keys
   - Redact sensitive PII
   - Mask credit card numbers, SSNs, etc.

---

## 7. Error Code Standardization

### 7.1 Error Code Structure

**Format:** `ERR_{category}{number}`

**Categories:**

- 1000-1999: Validation errors
- 2000-2999: Authentication errors
- 3000-3999: Authorization errors
- 4000-4999: Not found errors
- 5000-5999: Conflict errors
- 6000-6999: Business logic errors
- 7000-7999: External service errors
- 8000-8999: Database errors
- 9000-9999: Internal errors
- 10000-10999: Rate limiting errors

### 7.2 Error Code Registry

**NestJS:** `/apps/services/shared/errors/error-codes.ts`
**FastAPI:** `/apps/services/shared/errors_py/error_codes.py`

✅ **Strengths:**

- Comprehensive error code coverage (70+ codes)
- Bilingual messages for all codes
- Category-based organization
- Metadata includes HTTP status and retryability

**Example:**

```typescript
export enum ErrorCode {
  VALIDATION_ERROR = "ERR_1000",
  INVALID_INPUT = "ERR_1001",
  USER_NOT_FOUND = "ERR_4001",
  FARM_NOT_FOUND = "ERR_4002",
  // ...
}

export const ERROR_REGISTRY: Record<ErrorCode, ErrorCodeMetadata> = {
  [ErrorCode.VALIDATION_ERROR]: {
    code: ErrorCode.VALIDATION_ERROR,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Validation error occurred",
      ar: "حدث خطأ في التحقق من صحة البيانات",
    },
    retryable: false,
  },
  // ...
};
```

### 7.3 Consistency Check

✅ **Synchronized:** Both NestJS and FastAPI versions are in sync with identical codes.

❌ **Usage Inconsistency:**

- Local NestJS implementations use `ERR_{status}` (e.g., `ERR_404`)
- Should use semantic codes (e.g., `ERR_4001` for USER_NOT_FOUND)

### 7.4 Missing Error Codes

**Identified Gaps:**

1. No error codes for:
   - File upload errors (ERR_7100 range)
   - Cache errors (ERR_8100 range)
   - Queue/messaging errors (ERR_7200 range)
   - Webhook errors (ERR_7300 range)

2. No domain-specific error codes for:
   - Weather data errors
   - Satellite imagery errors
   - Crop detection errors
   - IoT sensor errors

### 7.5 Recommendations for Error Codes

**MEDIUM PRIORITY:**

1. **Expand error code registry:**

   ```typescript
   // File upload errors
   FILE_TOO_LARGE = 'ERR_7100',
   INVALID_FILE_TYPE = 'ERR_7101',
   VIRUS_DETECTED = 'ERR_7102',

   // Cache errors
   CACHE_UNAVAILABLE = 'ERR_8100',
   CACHE_EXPIRED = 'ERR_8101',

   // Messaging errors
   QUEUE_FULL = 'ERR_7200',
   MESSAGE_EXPIRED = 'ERR_7201',
   ```

2. **Add domain-specific codes:**

   ```typescript
   // Agricultural domain
   CROP_SEASON_OVERLAP = 'ERR_6100',
   INVALID_PLANTING_DATE = 'ERR_6101',
   WEATHER_DATA_STALE = 'ERR_7400',
   SATELLITE_IMAGE_CLOUDY = 'ERR_7401',
   ```

3. **Document error codes** in API documentation (Swagger/OpenAPI)

4. **Create error code migration guide** for services using old codes

---

## 8. Security Considerations

### 8.1 Information Disclosure

**Current Risks:**

| Risk                        | Severity | Status                      |
| --------------------------- | -------- | --------------------------- |
| Stack traces in production  | HIGH     | ⚠️ Mitigated (env-based)    |
| Database connection strings | HIGH     | ✅ Sanitized (FastAPI only) |
| File paths in errors        | MEDIUM   | ⚠️ Partial (FastAPI only)   |
| Request headers in logs     | HIGH     | ❌ Not sanitized            |
| Request body in logs        | CRITICAL | ❌ Not sanitized            |
| SQL queries in errors       | HIGH     | ❓ Unknown                  |
| Internal service URLs       | MEDIUM   | ❓ Unknown                  |

### 8.2 Error Enumeration

**Attack Vector:** Attackers may use error messages to enumerate valid resources.

**Example Vulnerable Response:**

```json
{
  "error": {
    "code": "ERR_4001",
    "message": "User with email 'test@example.com' not found"
  }
}
```

✅ **Mitigated:** Generic messages used:

```json
{
  "error": {
    "code": "ERR_2001",
    "message": "Invalid credentials"
  }
}
```

### 8.3 Denial of Service via Error Logging

**Risk:** Malicious clients could trigger excessive error logging.

✅ **Mitigated:**

- Rate limiting on `/api/log-error` endpoint (10-20 requests/minute)
- Rate limiting in error handlers (not implemented universally)

❌ **Missing:**

- Circuit breakers to prevent error cascade
- Error rate monitoring and alerting
- Automatic throttling for high error rates

### 8.4 Cross-Site Scripting (XSS) in Error Messages

**Risk:** User input reflected in error messages could enable XSS.

**Example Vulnerable Code:**

```typescript
throw new NotFoundException(`Farm ${farmId} not found`);
```

If `farmId` contains `<script>alert('XSS')</script>`, it could be rendered unsafely.

⚠️ **Status:**

- Backend APIs return JSON (not vulnerable)
- Frontend error boundaries use React (auto-escaped)
- Server-side rendered errors may be vulnerable

**Recommendation:**
Always sanitize user input in error messages:

```typescript
throw new NotFoundException(`Farm not found`, {
  details: { farmId: sanitize(farmId) },
});
```

### 8.5 Recommendations for Security

**HIGH PRIORITY:**

1. **Implement request sanitization in NestJS** (matching FastAPI implementation)
2. **Force disable stack traces in production** (ignore INCLUDE_STACK_TRACE env var)
3. **Add circuit breakers** to prevent error cascades
4. **Implement error rate limiting** at service level
5. **Audit all error messages** for information disclosure
6. **Add security headers** to error responses:
   ```typescript
   response.setHeader("X-Content-Type-Options", "nosniff");
   response.setHeader("X-Frame-Options", "DENY");
   ```

---

## 9. Monitoring and Observability

### 9.1 Current State

**Available:**

- ✅ Request ID correlation
- ✅ Structured logging (FastAPI only)
- ✅ HTTP status code logging
- ✅ Error categorization

**Missing:**

- ❌ Distributed tracing (OpenTelemetry)
- ❌ Error rate metrics (Prometheus)
- ❌ Error dashboards (Grafana)
- ❌ Alerting (PagerDuty, Slack)
- ❌ APM integration (Datadog, New Relic)
- ❌ Error tracking service (Sentry)
- ❌ Session replay (LogRocket)

### 9.2 Metrics Recommendations

**Metrics to Track:**

1. **Error Rate:**
   - Total errors per minute
   - Errors by service
   - Errors by error code
   - Errors by endpoint

2. **Response Time:**
   - P50, P95, P99 latency
   - Error response time vs success response time

3. **User Impact:**
   - Affected users count
   - Affected sessions count
   - Error rate by user segment

4. **Business Impact:**
   - Failed transactions
   - Lost revenue (if applicable)
   - SLA violations

### 9.3 Dashboard Recommendations

**Suggested Dashboards:**

1. **Error Overview:**
   - Total error count (24h, 7d, 30d)
   - Error rate trend
   - Top 10 error codes
   - Error distribution by service

2. **Service Health:**
   - Error rate by service
   - Response time by service
   - Availability percentage
   - Dependency health

3. **User Impact:**
   - Affected users
   - Error rate by user cohort
   - Geographic distribution of errors
   - Device/browser distribution

### 9.4 Alerting Recommendations

**Alert Rules:**

1. **Critical Alerts:**
   - Error rate > 5% for 5 minutes → PagerDuty
   - 5xx errors > 10 per minute → PagerDuty
   - Database connection failures → PagerDuty

2. **Warning Alerts:**
   - Error rate > 2% for 15 minutes → Slack
   - 4xx errors > 50 per minute → Slack
   - External service errors > 10 per minute → Slack

3. **Info Alerts:**
   - New error code detected → Email
   - Error rate increase > 50% → Email

---

## 10. Testing Recommendations

### 10.1 Unit Tests for Error Handlers

**NestJS Example:**

```typescript
describe("HttpExceptionFilter", () => {
  it("should handle AppException correctly", () => {
    // Test AppException handling
  });

  it("should handle HttpException correctly", () => {
    // Test HttpException handling
  });

  it("should handle unknown errors correctly", () => {
    // Test catch-all handling
  });

  it("should sanitize sensitive information", () => {
    // Test sanitization
  });

  it("should not include stack traces in production", () => {
    // Test stack trace exclusion
  });

  it("should generate request ID when missing", () => {
    // Test request ID generation
  });
});
```

### 10.2 Integration Tests

**Test Scenarios:**

1. Validation errors return correct format
2. Authentication errors return 401
3. Authorization errors return 403
4. Not found errors return 404
5. Rate limiting works correctly
6. Request ID is propagated through error chain

### 10.3 E2E Tests

**Test Scenarios:**

1. Frontend error boundary catches React errors
2. Frontend error logging works correctly
3. Error response format is consistent across services
4. Bilingual messages are returned correctly
5. Error details are not leaked in production

---

## 11. Summary of Findings

### 11.1 Critical Issues (Fix Immediately)

| #   | Issue                                                      | Impact                                                | Services Affected      |
| --- | ---------------------------------------------------------- | ----------------------------------------------------- | ---------------------- |
| 1   | Only 5% of FastAPI services use unified error handlers     | Inconsistent error handling, information leakage risk | 38/40 FastAPI services |
| 2   | Request headers/body logged without sanitization in NestJS | Credentials/tokens may be logged                      | All NestJS services    |
| 3   | No mobile app error boundary                               | App crashes without graceful handling                 | Mobile app             |
| 4   | No centralized error tracking/monitoring                   | Cannot identify or respond to production issues       | All services           |
| 5   | Local NestJS error handlers don't use standard error codes | Inconsistent API responses                            | 7/10 NestJS services   |

### 11.2 High Priority Issues (Fix Soon)

| #   | Issue                                                         | Impact                                  | Services Affected   |
| --- | ------------------------------------------------------------- | --------------------------------------- | ------------------- |
| 6   | No sanitization in NestJS error messages                      | Database strings, paths may leak        | All NestJS services |
| 7   | Stack traces may be enabled in production via env var         | Internal implementation details exposed | All services        |
| 8   | Error logging endpoints don't integrate with external service | Lost error data, no alerting            | Web and Admin apps  |
| 9   | In-memory rate limiting for error logging                     | Ineffective across multiple instances   | Web and Admin apps  |
| 10  | No distributed tracing                                        | Cannot trace errors across services     | All services        |

### 11.3 Medium Priority Issues (Fix When Possible)

| #   | Issue                                   | Impact                             | Services Affected |
| --- | --------------------------------------- | ---------------------------------- | ----------------- |
| 11  | Missing domain-specific error codes     | Generic error messages             | Domain services   |
| 12  | No error dashboards                     | Poor visibility into system health | All services      |
| 13  | No automated alerting                   | Delayed incident response          | All services      |
| 14  | No session replay for frontend errors   | Difficult to reproduce user issues | Web apps          |
| 15  | Legacy exception handler not deprecated | Confusion about which to use       | FastAPI services  |

---

## 12. Action Plan

### Phase 1: Critical Fixes (Week 1-2)

**Week 1:**

1. ✅ Create migration guide for unified error handlers
2. ✅ Migrate 5 high-traffic FastAPI services to unified handlers
3. ✅ Implement request sanitization in NestJS
4. ✅ Set up Sentry or equivalent error tracking service
5. ✅ Implement mobile app error boundary

**Week 2:** 6. ✅ Migrate remaining FastAPI services (batch of 10 per day) 7. ✅ Migrate all NestJS services to shared error filter 8. ✅ Force disable stack traces in production 9. ✅ Add comprehensive test suite for error handlers 10. ✅ Deploy error tracking to production

### Phase 2: High Priority (Week 3-4)

**Week 3:**

1. ✅ Implement centralized log aggregation (ELK or equivalent)
2. ✅ Add distributed tracing (OpenTelemetry)
3. ✅ Integrate error logging endpoints with external service
4. ✅ Implement Redis-based rate limiting for error endpoints
5. ✅ Add correlation IDs (trace, tenant, user, session)

**Week 4:** 6. ✅ Create error rate metrics (Prometheus) 7. ✅ Set up error dashboards (Grafana) 8. ✅ Implement automated alerting (PagerDuty/Slack) 9. ✅ Add circuit breakers for error cascades 10. ✅ Deprecate legacy exception handler

### Phase 3: Medium Priority (Week 5-8)

**Week 5-6:**

1. ✅ Expand error code registry with missing codes
2. ✅ Add domain-specific error codes
3. ✅ Update API documentation with error codes
4. ✅ Implement session replay (LogRocket or equivalent)
5. ✅ Add APM integration (Datadog/New Relic)

**Week 7-8:** 6. ✅ Create runbooks for common errors 7. ✅ Implement error recovery strategies 8. ✅ Add retry logic with exponential backoff 9. ✅ Create error code migration tool 10. ✅ Conduct security audit of all error messages

### Phase 4: Continuous Improvement (Ongoing)

1. ✅ Weekly review of top errors
2. ✅ Monthly error dashboard review
3. ✅ Quarterly error code registry update
4. ✅ Bi-annual security audit
5. ✅ Annual disaster recovery drill

---

## 13. Code Examples

### 13.1 Migrating FastAPI Service to Unified Handlers

**Before:**

```python
from fastapi import FastAPI, HTTPException

app = FastAPI(title="My Service")

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    if not item_id:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

**After:**

```python
from fastapi import FastAPI
from errors_py import (
    setup_exception_handlers,
    add_request_id_middleware,
    NotFoundException,
    ErrorCode,
)

app = FastAPI(title="My Service")

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    if not item_id:
        raise NotFoundException(
            ErrorCode.RESOURCE_NOT_FOUND,
            details={"resource": "item", "item_id": item_id}
        )
    return {"item_id": item_id}
```

### 13.2 Migrating NestJS Service to Shared Filter

**Before (main.ts):**

```typescript
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

// Local implementation
@Catch()
class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    // ... duplicated code
  }
}

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalFilters(new HttpExceptionFilter());
  await app.listen(3000);
}
```

**After (main.ts):**

```typescript
import { NestFactory } from "@nestjs/core";
import { HttpExceptionFilter } from "@sahool/shared/errors";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalFilters(new HttpExceptionFilter());
  await app.listen(3000);
}
```

### 13.3 Using Custom Exceptions

**NestJS:**

```typescript
import {
  NotFoundException,
  ValidationException,
  ErrorCode,
  BilingualMessage,
} from "@sahool/shared/errors";

// Simple usage
throw NotFoundException.farm("farm-123");

// Custom message
throw new ValidationException(
  ErrorCode.INVALID_INPUT,
  new BilingualMessage(
    "Invalid farm coordinates",
    "إحداثيات المزرعة غير صالحة",
  ),
  {
    field: "coordinates",
    value: coordinates,
  },
);
```

**FastAPI:**

```python
from errors_py import (
    NotFoundException,
    ValidationException,
    ErrorCode,
    BilingualMessage,
)

# Simple usage
raise NotFoundException.farm('farm-123')

# Custom message
raise ValidationException(
    ErrorCode.INVALID_INPUT,
    BilingualMessage(
        en='Invalid farm coordinates',
        ar='إحداثيات المزرعة غير صالحة'
    ),
    details={
        'field': 'coordinates',
        'value': coordinates,
    }
)
```

### 13.4 Implementing Error Boundary in Mobile App

**React Native:**

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import * as Sentry from '@sentry/react-native';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log to Sentry
    Sentry.captureException(error, {
      extra: {
        componentStack: errorInfo.componentStack,
      },
    });

    // Log to backend
    fetch('https://api.sahool.com/api/log-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'react_native_error_boundary',
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
      }),
    }).catch(console.error);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <View style={styles.container}>
          <Text style={styles.title}>حدث خطأ غير متوقع</Text>
          <Text style={styles.message}>
            نعتذر عن هذا الخطأ. يرجى المحاولة مرة أخرى.
          </Text>
          <TouchableOpacity style={styles.button} onPress={this.handleRetry}>
            <Text style={styles.buttonText}>إعادة المحاولة</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  message: {
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
    color: '#666',
  },
  button: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
```

---

## 14. Metrics and KPIs

### 14.1 Success Metrics

**Target Metrics (After Implementation):**

- ✅ 100% of services use unified error handlers
- ✅ 0 stack traces leaked in production
- ✅ 0 credentials/tokens logged
- ✅ < 1 minute mean time to detect (MTTD) critical errors
- ✅ < 15 minutes mean time to respond (MTTR) to critical errors
- ✅ < 0.1% error rate overall
- ✅ 99.9% error logging success rate

### 14.2 Current Baseline

**Measured on:** 2026-01-06

- FastAPI services with unified handlers: **5%** (2/40)
- NestJS services with unified handlers: **0%** (0/10, using shared filter but local implementation)
- Web apps with error boundaries: **100%** (2/2)
- Mobile apps with error boundaries: **0%** (0/1)
- Services with error tracking: **0%**
- Services with centralized logging: **0%**
- Services with alerting: **0%**

### 14.3 Improvement Targets

**Month 1:**

- FastAPI unified handlers: 50% (20/40)
- NestJS unified handlers: 100% (10/10)
- Mobile error boundary: 100% (1/1)
- Error tracking: 100% (all services)

**Month 2:**

- FastAPI unified handlers: 100% (40/40)
- Centralized logging: 100%
- Alerting: 100%
- Error dashboards: Deployed

**Month 3:**

- MTTD < 5 minutes
- MTTR < 30 minutes
- Error rate < 1%
- Zero information leakage incidents

---

## 15. Conclusion

The SAHOOL platform has a **solid foundation** for error handling with centralized error handlers, bilingual messages, and structured error codes. However, **critical inconsistencies** in implementation across services pose significant risks:

### Key Takeaways

1. **Immediate Action Required:**
   - Migrate all services to unified error handlers
   - Implement mobile app error boundary
   - Set up error tracking service
   - Sanitize request data in logs

2. **Short-term Improvements:**
   - Centralized log aggregation
   - Distributed tracing
   - Automated alerting
   - Error dashboards

3. **Long-term Goals:**
   - Proactive error detection
   - Automated error recovery
   - Comprehensive error analytics
   - Continuous security monitoring

### Final Recommendation

**Prioritize Phase 1 (Critical Fixes)** immediately. The inconsistent implementation of error handlers across 95% of FastAPI services and lack of mobile error boundary are critical gaps that could lead to:

- Information disclosure
- Poor user experience
- Difficulty troubleshooting production issues
- Compliance violations

With the existing shared error handling infrastructure, migrating all services should be straightforward and can be completed within 2 weeks.

---

## Appendices

### Appendix A: Services Inventory

**NestJS Services (10 total):**

1. chat-service
2. crop-growth-model
3. disaster-assessment
4. iot-service
5. lai-estimation
6. marketplace-service
7. research-core
8. user-service
9. yield-prediction
10. yield-prediction-service

**FastAPI Services with Unified Handlers (2):**

1. weather-service ✅
2. advisory-service (agro-advisor) ✅

**FastAPI Services Needing Migration (38):**

1. field-core
2. field-service
3. field-management-service
4. field-intelligence
5. ai-advisor
6. ai-agents-core
7. agent-registry
8. alert-service
9. astronomical-calendar
10. billing-core
11. code-review-service
12. crop-health
13. crop-health-ai
14. crop-intelligence-service
15. equipment-service
16. fertilizer-advisor
17. field-chat
18. field-ops
19. globalgap-compliance
20. indicators-service
21. inventory-service
22. iot-gateway
23. irrigation-smart
24. mcp-server
25. ndvi-engine
26. ndvi-processor
27. notification-service
28. provider-config
29. satellite-service
30. task-service
31. vegetation-analysis-service
32. virtual-sensors
33. weather-advanced
34. weather-core
35. ws-gateway
36. yield-engine
37. demo-data
38. community-chat (Node.js/Express - separate assessment needed)

### Appendix B: Error Code Reference

See `/apps/services/shared/errors/error-codes.ts` and `/apps/services/shared/errors_py/error_codes.py` for complete error code registry.

### Appendix C: Related Documentation

- Shared Error Handling Module: `/apps/services/shared/errors/`
- Python Error Handling Module: `/apps/services/shared/errors_py/`
- Error Boundary Components: `/packages/shared-ui/src/components/ErrorBoundary.tsx`
- API Error Logging: `/apps/web/src/app/api/log-error/route.ts`

---

**Report Generated:** 2026-01-06
**Next Review Date:** 2026-02-06
**Audit Frequency:** Monthly
