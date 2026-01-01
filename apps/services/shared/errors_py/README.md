# SAHOOL Python Error Handling Package

## معالجة الأخطاء الموحدة لخدمات Python

Comprehensive error handling package for all SAHOOL FastAPI microservices with bilingual support (English/Arabic).

## Features

- ✅ **Standardized Error Codes**: Consistent error codes across all services
- ✅ **Bilingual Support**: Error messages in both English and Arabic
- ✅ **Custom Exception Classes**: Type-safe exception handling
- ✅ **Request ID Correlation**: Track errors across distributed systems
- ✅ **Security**: Hides sensitive information and stack traces in production
- ✅ **Comprehensive Logging**: Server-side error logging with context
- ✅ **Retry Information**: Indicates if errors are retryable
- ✅ **Validation Support**: Detailed field-level validation errors

## Quick Start

### 1. Setup Exception Handlers

Add to your FastAPI application:

```python
from fastapi import FastAPI
from apps.services.shared.errors_py import setup_exception_handlers, add_request_id_middleware

app = FastAPI()

# Setup exception handlers
setup_exception_handlers(app)

# Add request ID middleware
add_request_id_middleware(app)
```

### 2. Throw Custom Exceptions

```python
from apps.services.shared.errors_py import (
    NotFoundException,
    ValidationException,
    BusinessLogicException,
    ErrorCode,
)

# Simple usage
raise NotFoundException(ErrorCode.FARM_NOT_FOUND)

# With helper methods
raise NotFoundException.farm("farm-123")

# With custom details
raise ValidationException(
    ErrorCode.VALIDATION_ERROR,
    details={"fields": [{"field": "email", "message": "Invalid format"}]}
)

# Business logic errors
raise BusinessLogicException.insufficient_balance(
    available=100.0,
    required=500.0
)
```

### 3. Return Success Responses

```python
from apps.services.shared.errors_py import create_success_response, create_paginated_response

# Simple success response
@app.get("/farms/{farm_id}")
async def get_farm(farm_id: str):
    farm = await get_farm_from_db(farm_id)
    return create_success_response(
        data=farm,
        message="Farm retrieved successfully",
        message_ar="تم استرداد المزرعة بنجاح"
    )

# Paginated response
@app.get("/farms")
async def list_farms(page: int = 1, limit: int = 20):
    farms, total = await get_farms_from_db(page, limit)
    return create_paginated_response(
        data=farms,
        page=page,
        limit=limit,
        total=total,
        message="Farms retrieved successfully",
        message_ar="تم استرداد المزارع بنجاح"
    )
```

## Error Response Format

All errors follow this standardized format:

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

## Success Response Format

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

## Available Exception Classes

### Base Exception
- `AppException`: Base class for all custom exceptions

### Domain-Specific Exceptions
- `ValidationException`: For input validation errors (400)
- `AuthenticationException`: For authentication failures (401)
- `AuthorizationException`: For permission denials (403)
- `NotFoundException`: For resource not found (404)
- `ConflictException`: For conflicts like duplicates (409)
- `BusinessLogicException`: For business rule violations (422)
- `ExternalServiceException`: For external service failures (502/503)
- `DatabaseException`: For database errors (500)
- `InternalServerException`: For internal server errors (500)
- `RateLimitException`: For rate limiting (429)

### Helper Methods

#### NotFoundException
```python
# Specific resource types
NotFoundException.user("user-123")
NotFoundException.farm("farm-123")
NotFoundException.field("field-123")
NotFoundException.crop("crop-123")
NotFoundException.sensor("sensor-123")
NotFoundException.conversation("conv-123")
NotFoundException.message("msg-123")
NotFoundException.wallet("wallet-123")
NotFoundException.order("order-123")
NotFoundException.product("product-123")
```

#### BusinessLogicException
```python
# Predefined business logic errors
BusinessLogicException.insufficient_balance(available=100, required=500)
BusinessLogicException.amount_must_be_positive(amount=-50)
BusinessLogicException.invalid_state_transition("pending", "completed")
BusinessLogicException.operation_not_allowed("delete", "Resource is locked")
```

#### ExternalServiceException
```python
# Service-specific errors
ExternalServiceException.weather_service(error)
ExternalServiceException.satellite_service(error)
ExternalServiceException.payment_gateway(error)
ExternalServiceException.sms_service(error)
ExternalServiceException.email_service(error)
```

#### RateLimitException
```python
# With retry information
RateLimitException.with_retry_after(retry_after_seconds=60)
```

## Error Codes

Error codes are organized by category:

### Validation Errors (1000-1999)
- `ERR_1000`: VALIDATION_ERROR
- `ERR_1001`: INVALID_INPUT
- `ERR_1002`: MISSING_REQUIRED_FIELD
- `ERR_1003`: INVALID_FORMAT
- `ERR_1004`: INVALID_EMAIL
- `ERR_1005`: INVALID_PHONE
- `ERR_1006`: INVALID_DATE
- `ERR_1007`: INVALID_RANGE
- `ERR_1008`: INVALID_ENUM_VALUE

### Authentication Errors (2000-2999)
- `ERR_2000`: AUTHENTICATION_FAILED
- `ERR_2001`: INVALID_CREDENTIALS
- `ERR_2002`: TOKEN_EXPIRED
- `ERR_2003`: TOKEN_INVALID
- `ERR_2004`: TOKEN_MISSING
- `ERR_2005`: SESSION_EXPIRED
- `ERR_2006`: ACCOUNT_LOCKED
- `ERR_2007`: ACCOUNT_DISABLED
- `ERR_2008`: EMAIL_NOT_VERIFIED

### Authorization Errors (3000-3999)
- `ERR_3000`: FORBIDDEN
- `ERR_3001`: INSUFFICIENT_PERMISSIONS
- `ERR_3002`: ACCESS_DENIED
- `ERR_3003`: TENANT_MISMATCH
- `ERR_3004`: ROLE_REQUIRED
- `ERR_3005`: SUBSCRIPTION_REQUIRED
- `ERR_3006`: QUOTA_EXCEEDED

### Not Found Errors (4000-4999)
- `ERR_4000`: RESOURCE_NOT_FOUND
- `ERR_4001`: USER_NOT_FOUND
- `ERR_4002`: FARM_NOT_FOUND
- `ERR_4003`: FIELD_NOT_FOUND
- `ERR_4004`: CROP_NOT_FOUND
- `ERR_4005`: SENSOR_NOT_FOUND
- `ERR_4006`: CONVERSATION_NOT_FOUND
- `ERR_4007`: MESSAGE_NOT_FOUND
- `ERR_4008`: WALLET_NOT_FOUND
- `ERR_4009`: ORDER_NOT_FOUND
- `ERR_4010`: PRODUCT_NOT_FOUND

### Conflict Errors (5000-5999)
- `ERR_5000`: RESOURCE_ALREADY_EXISTS
- `ERR_5001`: DUPLICATE_EMAIL
- `ERR_5002`: DUPLICATE_PHONE
- `ERR_5003`: CONCURRENT_MODIFICATION
- `ERR_5004`: VERSION_MISMATCH

### Business Logic Errors (6000-6999)
- `ERR_6000`: BUSINESS_RULE_VIOLATION
- `ERR_6001`: INSUFFICIENT_BALANCE
- `ERR_6002`: INVALID_STATE_TRANSITION
- `ERR_6003`: OPERATION_NOT_ALLOWED
- `ERR_6004`: AMOUNT_MUST_BE_POSITIVE
- `ERR_6005`: PLANTING_DATE_INVALID
- `ERR_6006`: HARVEST_DATE_BEFORE_PLANTING
- `ERR_6007`: FIELD_ALREADY_HAS_CROP
- `ERR_6008`: ESCROW_ALREADY_EXISTS
- `ERR_6009`: LOAN_NOT_ACTIVE
- `ERR_6010`: PAYMENT_NOT_PENDING

### External Service Errors (7000-7999)
- `ERR_7000`: EXTERNAL_SERVICE_ERROR
- `ERR_7001`: WEATHER_SERVICE_UNAVAILABLE
- `ERR_7002`: SATELLITE_SERVICE_UNAVAILABLE
- `ERR_7003`: PAYMENT_GATEWAY_ERROR
- `ERR_7004`: SMS_SERVICE_ERROR
- `ERR_7005`: EMAIL_SERVICE_ERROR
- `ERR_7006`: MAPS_SERVICE_ERROR

### Database Errors (8000-8999)
- `ERR_8000`: DATABASE_ERROR
- `ERR_8001`: DATABASE_CONNECTION_FAILED
- `ERR_8002`: QUERY_TIMEOUT
- `ERR_8003`: TRANSACTION_FAILED
- `ERR_8004`: CONSTRAINT_VIOLATION
- `ERR_8005`: FOREIGN_KEY_VIOLATION
- `ERR_8006`: UNIQUE_CONSTRAINT_VIOLATION

### Internal Errors (9000-9999)
- `ERR_9000`: INTERNAL_SERVER_ERROR
- `ERR_9001`: SERVICE_UNAVAILABLE
- `ERR_9002`: CONFIGURATION_ERROR
- `ERR_9003`: NOT_IMPLEMENTED
- `ERR_9004`: DEPENDENCY_FAILED

### Rate Limiting (10000-10999)
- `ERR_10000`: RATE_LIMIT_EXCEEDED
- `ERR_10001`: TOO_MANY_REQUESTS
- `ERR_10002`: API_QUOTA_EXCEEDED

## Security Features

### Stack Trace Hiding
Stack traces are only included in development environments. Set:
- `ENVIRONMENT=development` or
- `NODE_ENV=development` or
- `INCLUDE_STACK_TRACE=true`

### Sensitive Information Redaction
Automatically sanitizes:
- Passwords
- API keys
- Tokens
- Database connection strings
- File paths

### Request ID Correlation
Every error includes a unique request ID for:
- Tracking errors across services
- Correlating logs
- Customer support

## Best Practices

1. **Use Specific Error Codes**: Use the most specific error code available
2. **Include Context**: Add relevant details to help debugging
3. **Don't Expose Internals**: Never include sensitive data in error responses
4. **Log Server-Side**: Full errors are logged server-side with stack traces
5. **Use Helper Methods**: Leverage convenience methods for common scenarios
6. **Test Error Cases**: Write tests for error scenarios

## Example Integration

```python
from fastapi import FastAPI, Depends
from apps.services.shared.errors_py import (
    setup_exception_handlers,
    add_request_id_middleware,
    NotFoundException,
    ValidationException,
    AuthenticationException,
    ErrorCode,
    create_success_response,
)

app = FastAPI(title="My Service")

# Setup error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

@app.get("/farms/{farm_id}")
async def get_farm(farm_id: str, user=Depends(get_current_user)):
    # Authentication check
    if not user:
        raise AuthenticationException(ErrorCode.TOKEN_MISSING)

    # Validation
    if not farm_id or len(farm_id) < 3:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "farm_id", "message": "Must be at least 3 characters"}
        )

    # Business logic
    farm = await db.get_farm(farm_id)
    if not farm:
        raise NotFoundException.farm(farm_id)

    # Authorization check
    if farm.owner_id != user.id:
        raise AuthorizationException(ErrorCode.ACCESS_DENIED)

    # Success response
    return create_success_response(
        data=farm,
        message="Farm retrieved successfully",
        message_ar="تم استرداد المزرعة بنجاح"
    )
```

## Migration Guide

### From Old Exception Handler

```python
# Old way
from apps.services.shared.middleware.exception_handler import (
    AppError,
    NotFoundError,
    ValidationError,
)

raise NotFoundError("Farm")

# New way
from apps.services.shared.errors_py import (
    NotFoundException,
    ValidationException,
    ErrorCode,
)

raise NotFoundException.farm("farm-123")
```

## Support

For issues or questions:
1. Check the error code in the registry
2. Review the logs with the request ID
3. Contact the platform team

## License

MIT - SAHOOL Agriculture Platform
