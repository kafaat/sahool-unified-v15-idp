# Unified Error Handling Implementation

## معالجة الأخطاء الموحدة

**Date**: 2026-01-01
**Status**: ✅ Implemented
**Affects**: All microservices (NestJS & FastAPI)

---

## 📋 Overview

Implemented comprehensive unified error handling across the entire SAHOOL platform to ensure consistent, secure, and user-friendly error responses.

### Key Features

- ✅ **Standardized Error Codes**: Consistent error codes (ERR_1000-ERR_10999) across all services
- ✅ **Bilingual Support**: Error messages in both English and Arabic
- ✅ **Security First**: Hides stack traces and sensitive information in production
- ✅ **Request ID Correlation**: Track errors across distributed systems
- ✅ **Comprehensive Logging**: Server-side error logging with full context
- ✅ **Type-Safe Exceptions**: Custom exception classes for both TypeScript and Python
- ✅ **Retry Information**: Indicates if errors are retryable
- ✅ **Validation Support**: Detailed field-level validation errors

---

## 🏗️ Architecture

### Error Response Format

All services now return errors in this standardized format:

```json
{
  "success": false,
  "error": {
    "code": "ERR_4002",
    "message": "Farm not found",
    "messageAr": "المزرعة غير موجودة",
    "category": "NOT_FOUND",
    "retryable": false,
    "timestamp": "2025-12-31T10:30:00.000Z",
    "path": "/api/v1/farms/123",
    "requestId": "req-1234567890-abc123",
    "details": {
      "farmId": "farm-123"
    }
  }
}
```

**Note**: `stack` field is only included in development environments.

### Success Response Format

```json
{
  "success": true,
  "data": {
    "id": "farm-123",
    "name": "My Farm"
  },
  "message": "Farm retrieved successfully",
  "messageAr": "تم استرداد المزرعة بنجاح",
  "timestamp": "2025-12-31T10:30:00.000Z"
}
```

---

## 📦 Components Created

### For NestJS Services (TypeScript)

**Location**: `/apps/services/shared/errors/`

- ✅ `error-codes.ts` - Centralized error code definitions (95+ error codes)
- ✅ `exceptions.ts` - Custom exception classes with helper methods
- ✅ `error-response.dto.ts` - Standardized response DTOs
- ✅ `http-exception.filter.ts` - Global exception filter
- ✅ `error-utils.ts` - Utility functions for error handling
- ✅ `index.ts` - Barrel exports for easy imports

### For FastAPI Services (Python)

**Location**: `/apps/services/shared/errors_py/`

- ✅ `error_codes.py` - Centralized error code definitions (matching TypeScript)
- ✅ `exceptions.py` - Custom exception classes with helper methods
- ✅ `response_models.py` - Pydantic models for responses
- ✅ `exception_handlers.py` - Global exception handlers & middleware
- ✅ `README.md` - Comprehensive documentation
- ✅ `__init__.py` - Package exports

---

## 📝 Error Code Ranges

| Range       | Category         | Description                       |
| ----------- | ---------------- | --------------------------------- |
| 1000-1999   | Validation       | Input validation errors           |
| 2000-2999   | Authentication   | Authentication failures           |
| 3000-3999   | Authorization    | Permission denials                |
| 4000-4999   | Not Found        | Resource not found errors         |
| 5000-5999   | Conflict         | Data conflicts (duplicates, etc.) |
| 6000-6999   | Business Logic   | Business rule violations          |
| 7000-7999   | External Service | External service failures         |
| 8000-8999   | Database         | Database errors                   |
| 9000-9999   | Internal         | Internal server errors            |
| 10000-10999 | Rate Limiting    | Rate limit exceeded               |

---

## 🔧 Implementation Details

### NestJS Services

#### Exception Classes

```typescript
import {
  NotFoundException,
  ValidationException,
  BusinessLogicException,
  ErrorCode,
} from "@sahool/shared/errors";

// Simple usage
throw new NotFoundException(ErrorCode.FARM_NOT_FOUND);

// With helper methods
throw NotFoundException.farm("farm-123");

// Business logic errors
throw BusinessLogicException.insufficientBalance(100.0, 500.0);
```

#### Setup in main.ts

```typescript
import { HttpExceptionFilter } from "@sahool/shared/errors";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  // ... rest of setup
}
```

### FastAPI Services

#### Exception Classes

```python
from apps.services.shared.errors_py import (
    NotFoundException,
    ValidationException,
    BusinessLogicException,
    ErrorCode,
    setup_exception_handlers,
    add_request_id_middleware,
    create_success_response,
)

# Simple usage
raise NotFoundException(ErrorCode.FARM_NOT_FOUND)

# With helper methods
raise NotFoundException.farm("farm-123")

# Business logic errors
raise BusinessLogicException.insufficient_balance(
    available=100.0,
    required=500.0
)
```

#### Setup in main.py

```python
from apps.services.shared.errors_py import (
    setup_exception_handlers,
    add_request_id_middleware,
)

app = FastAPI(title="My Service")

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)
```

---

## 🔄 Services Updated

### FastAPI Services (Python)

- ✅ **advisory-service** (Port 8095)
  - Updated all HTTPException calls to use custom exceptions
  - Added request ID middleware
  - Using standardized success responses

- ✅ **weather-service** (Port 8108)
  - Updated external service error handling
  - Added request ID middleware
  - Proper error types for weather provider failures

### NestJS Services (TypeScript)

- ✅ **chat-service** (Port 8114)
  - Added global exception filter
  - Using unified error handling

- ✅ **marketplace-service** (Port 3010)
  - Added global exception filter
  - Using unified error handling

**Note**: All other services should follow the same pattern. See migration guide below.

---

## 🔒 Security Features

### 1. Stack Trace Hiding

Stack traces are automatically hidden in production. They are only shown when:

- `ENVIRONMENT=development`
- `NODE_ENV=development`
- `INCLUDE_STACK_TRACE=true`

### 2. Sensitive Information Redaction

The error handlers automatically sanitize:

- Passwords
- API keys
- Tokens
- Database connection strings
- File paths
- Authorization headers

### 3. Request ID Correlation

Every error includes a unique request ID for:

- Tracking errors across microservices
- Correlating logs
- Customer support
- Debugging

The request ID is automatically:

- Generated if not provided
- Added to response headers
- Logged with errors
- Included in error responses

---

## 📚 Available Exception Classes

### NestJS (TypeScript)

- `AppException` - Base class
- `ValidationException` - Input validation (400)
- `AuthenticationException` - Authentication failures (401)
- `AuthorizationException` - Permission denials (403)
- `NotFoundException` - Resources not found (404)
- `ConflictException` - Data conflicts (409)
- `BusinessLogicException` - Business rules (422)
- `ExternalServiceException` - External services (502/503)
- `DatabaseException` - Database errors (500)
- `InternalServerException` - Internal errors (500)
- `RateLimitException` - Rate limiting (429)

### FastAPI (Python)

- `AppException` - Base class
- `ValidationException` - Input validation (400)
- `AuthenticationException` - Authentication failures (401)
- `AuthorizationException` - Permission denials (403)
- `NotFoundException` - Resources not found (404)
- `ConflictException` - Data conflicts (409)
- `BusinessLogicException` - Business rules (422)
- `ExternalServiceException` - External services (502/503)
- `DatabaseException` - Database errors (500)
- `InternalServerException` - Internal errors (500)
- `RateLimitException` - Rate limiting (429)

---

## 🚀 Migration Guide

### For NestJS Services

**Step 1**: Import the global exception filter in `main.ts`:

```typescript
import { HttpExceptionFilter } from "@sahool/shared/errors";

app.useGlobalFilters(new HttpExceptionFilter());
```

**Step 2**: Replace exceptions in your code:

```typescript
// Old way ❌
throw new HttpException("Farm not found", HttpStatus.NOT_FOUND);

// New way ✅
import { NotFoundException, ErrorCode } from "@sahool/shared/errors";
throw NotFoundException.farm("farm-123");
```

### For FastAPI Services

**Step 1**: Setup exception handlers in `main.py`:

```python
from apps.services.shared.errors_py import (
    setup_exception_handlers,
    add_request_id_middleware,
)

app = FastAPI(title="My Service")

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)
```

**Step 2**: Replace exceptions in your code:

```python
# Old way ❌
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Farm not found")

# New way ✅
from apps.services.shared.errors_py import NotFoundException, ErrorCode
raise NotFoundException.farm("farm-123")
```

**Step 3**: Use success response helpers:

```python
from apps.services.shared.errors_py import create_success_response

@app.get("/farms/{farm_id}")
async def get_farm(farm_id: str):
    farm = await get_farm_from_db(farm_id)
    return create_success_response(
        data=farm,
        message="Farm retrieved successfully",
        message_ar="تم استرداد المزرعة بنجاح"
    )
```

---

## 📊 Error Code Examples

### Common Use Cases

```typescript
// NestJS
throw NotFoundException.user("user-123");
throw NotFoundException.farm("farm-123");
throw NotFoundException.field("field-123");
throw NotFoundException.crop("crop-123");

throw ValidationException.fromFieldErrors([
  { field: "email", message: "Invalid format" },
]);

throw BusinessLogicException.insufficientBalance(100, 500);
throw BusinessLogicException.invalidStateTransition("pending", "completed");

throw ExternalServiceException.weatherService(error);
throw ExternalServiceException.paymentGateway(error);

throw RateLimitException.withRetryAfter(60);
```

```python
# FastAPI
raise NotFoundException.user("user-123")
raise NotFoundException.farm("farm-123")
raise NotFoundException.field("field-123")
raise NotFoundException.crop("crop-123")

raise ValidationException.from_field_errors([
    {"field": "email", "message": "Invalid format"}
])

raise BusinessLogicException.insufficient_balance(100, 500)
raise BusinessLogicException.invalid_state_transition("pending", "completed")

raise ExternalServiceException.weather_service(error)
raise ExternalServiceException.payment_gateway(error)

raise RateLimitException.with_retry_after(60)
```

---

## 🔍 Monitoring & Logging

### Server-Side Logging

All errors are logged with full context:

```
[ERROR] UnhandledException [req-123-abc]: DatabaseError
  - Request ID: req-123-abc
  - Path: /api/v1/farms/123
  - Method: GET
  - User: user-456
  - Stack trace: [full stack trace]
```

### Client-Side Response

Client receives sanitized error:

```json
{
  "success": false,
  "error": {
    "code": "ERR_8000",
    "message": "Database error occurred",
    "messageAr": "حدث خطأ في قاعدة البيانات",
    "requestId": "req-123-abc",
    "retryable": true
  }
}
```

---

## ✅ Verification

### Stack Trace Hiding

**Development**:

```bash
ENVIRONMENT=development
# Stack traces are included in responses
```

**Production**:

```bash
ENVIRONMENT=production
# Stack traces are hidden from responses but logged server-side
```

### Request ID Correlation

1. Client sends request with optional `X-Request-ID` header
2. Server generates one if not provided
3. All logs include the request ID
4. Error responses include the request ID
5. Response headers include `X-Request-ID`

---

## 📖 Documentation

### NestJS Error Handling

- Location: `/apps/services/shared/errors/`
- README: `/apps/services/shared/errors/README.md`
- Migration Guide: `/apps/services/shared/errors/MIGRATION_GUIDE.md`
- Quick Reference: `/apps/services/shared/errors/QUICK_REFERENCE.md`

### FastAPI Error Handling

- Location: `/apps/services/shared/errors_py/`
- README: `/apps/services/shared/errors_py/README.md`

---

## 🎯 Benefits

1. **Consistency**: All services return errors in the same format
2. **Security**: Sensitive information never exposed to clients
3. **Debugging**: Request IDs enable easy tracking across services
4. **User Experience**: Bilingual error messages (English/Arabic)
5. **Developer Experience**: Type-safe exception classes with helpers
6. **Monitoring**: Comprehensive server-side logging
7. **Maintainability**: Centralized error code definitions

---

## 🔄 Next Steps

### Recommended Actions

1. **Update All Services**: Follow migration guide to update remaining services
2. **Add Monitoring**: Set up alerts for error rate spikes
3. **Document Error Codes**: Create user-facing error code documentation
4. **Error Analytics**: Track most common errors for improvements
5. **Client SDK**: Create client SDKs with typed error handling

### Future Enhancements

- [ ] Error code translation service for more languages
- [ ] Error recovery suggestions in responses
- [ ] Automated error documentation generation
- [ ] Error rate limiting per client
- [ ] Machine learning for error pattern detection

---

## 📞 Support

For questions or issues:

1. Check the error code in the registry
2. Review the logs with the request ID
3. Contact the platform team
4. See documentation in `/apps/services/shared/errors/`

---

## 📄 License

MIT - SAHOOL Agriculture Platform

---

**Implementation Date**: 2026-01-01
**Last Updated**: 2026-01-01
**Version**: 1.0.0
