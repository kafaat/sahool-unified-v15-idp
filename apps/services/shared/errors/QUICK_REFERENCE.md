# Quick Reference Guide
# دليل المرجع السريع

Quick reference for common error handling scenarios in SAHOOL backend services.

---

## 🚀 Installation

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@sahool/shared/errors": ["../shared/errors"]
    }
  }
}

// main.ts
import { HttpExceptionFilter } from '@sahool/shared/errors';
app.useGlobalFilters(new HttpExceptionFilter());
```

---

## 📋 Common Error Scenarios

### 1. Resource Not Found

```typescript
import { NotFoundException } from '@sahool/shared/errors';

// Specific resources
throw NotFoundException.farm(farmId);
throw NotFoundException.user(userId);
throw NotFoundException.wallet(walletId);
throw NotFoundException.conversation(conversationId);
throw NotFoundException.order(orderId);
```

### 2. Validation Errors

```typescript
import { ValidationException } from '@sahool/shared/errors';

// Simple validation
throw new ValidationException(ErrorCode.INVALID_EMAIL);

// Multiple field errors
throw ValidationException.fromFieldErrors([
  { field: 'email', message: 'Invalid format', messageAr: 'تنسيق غير صالح' },
  { field: 'phone', message: 'Required', messageAr: 'مطلوب' }
]);
```

### 3. Business Logic Errors

```typescript
import { BusinessLogicException } from '@sahool/shared/errors';

// Amount validation
throw BusinessLogicException.amountMustBePositive(amount);

// Insufficient balance
throw BusinessLogicException.insufficientBalance(available, required);

// Invalid state transition
throw BusinessLogicException.invalidStateTransition(currentState, targetState);

// Operation not allowed
throw BusinessLogicException.operationNotAllowed('delete', 'Reason...');
```

### 4. Authentication Errors

```typescript
import { AuthenticationException, ErrorCode } from '@sahool/shared/errors';

throw new AuthenticationException(ErrorCode.TOKEN_EXPIRED);
throw new AuthenticationException(ErrorCode.TOKEN_INVALID);
throw new AuthenticationException(ErrorCode.INVALID_CREDENTIALS);
```

### 5. Authorization Errors

```typescript
import { AuthorizationException, ErrorCode } from '@sahool/shared/errors';

throw new AuthorizationException(ErrorCode.INSUFFICIENT_PERMISSIONS);
throw new AuthorizationException(ErrorCode.QUOTA_EXCEEDED);
throw new AuthorizationException(ErrorCode.SUBSCRIPTION_REQUIRED);
```

### 6. External Service Errors

```typescript
import { ExternalServiceException } from '@sahool/shared/errors';

throw ExternalServiceException.weatherService(error);
throw ExternalServiceException.satelliteService(error);
throw ExternalServiceException.paymentGateway(error);
throw ExternalServiceException.smsService(error);
```

### 7. Database Errors

```typescript
import { DatabaseException } from '@sahool/shared/errors';

try {
  await prisma.user.create({ data });
} catch (error) {
  throw DatabaseException.fromDatabaseError(error);
}
```

---

## ✅ Success Responses

```typescript
import { createSuccessResponse, createPaginatedResponse } from '@sahool/shared/errors';

// Simple success
return createSuccessResponse(
  data,
  'Operation successful',
  'العملية نجحت'
);

// Paginated
return createPaginatedResponse(
  items,
  page,
  limit,
  total,
  'Items retrieved',
  'تم استرجاع العناصر'
);
```

---

## 🛠️ Utilities

### Retry with Backoff

```typescript
import { retryWithBackoff } from '@sahool/shared/errors';

const result = await retryWithBackoff(
  () => externalApi.call(),
  { maxRetries: 3, initialDelay: 1000 }
);
```

### Circuit Breaker

```typescript
import { CircuitBreaker } from '@sahool/shared/errors';

const breaker = new CircuitBreaker();
const result = await breaker.execute(() => service.call());
```

### Error Handler Decorator

```typescript
import { HandleErrors } from '@sahool/shared/errors';

@HandleErrors(ErrorCode.DATABASE_ERROR)
async method() {
  // Auto-wrapped with error handling
}
```

### Timeout

```typescript
import { withTimeout } from '@sahool/shared/errors';

const result = await withTimeout(
  slowOperation(),
  5000,
  'Operation timeout'
);
```

---

## 📊 Error Codes Quick Reference

| Range | Category | Example |
|-------|----------|---------|
| 1000-1999 | Validation | ERR_1000, ERR_1004 |
| 2000-2999 | Authentication | ERR_2000, ERR_2002 |
| 3000-3999 | Authorization | ERR_3000, ERR_3001 |
| 4000-4999 | Not Found | ERR_4000, ERR_4002 |
| 5000-5999 | Conflict | ERR_5000, ERR_5001 |
| 6000-6999 | Business Logic | ERR_6000, ERR_6001 |
| 7000-7999 | External Service | ERR_7000, ERR_7001 |
| 8000-8999 | Database | ERR_8000, ERR_8001 |
| 9000-9999 | Internal | ERR_9000, ERR_9001 |
| 10000-10999 | Rate Limit | ERR_10000 |

---

## 🎯 HTTP Status Mapping

| HTTP Status | Error Code |
|-------------|------------|
| 400 | ERR_1000 (Validation) |
| 401 | ERR_2000 (Authentication) |
| 403 | ERR_3000 (Authorization) |
| 404 | ERR_4000 (Not Found) |
| 409 | ERR_5000 (Conflict) |
| 422 | ERR_6000 (Business Logic) |
| 429 | ERR_10000 (Rate Limit) |
| 500 | ERR_9000 (Internal) |
| 502 | ERR_7000 (External Service) |
| 503 | ERR_9001 (Service Unavailable) |

---

## 📤 Response Format

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERR_4002",
    "message": "Farm not found",
    "messageAr": "المزرعة غير موجودة",
    "retryable": false,
    "timestamp": "2025-12-31T10:30:00.000Z",
    "path": "/api/v1/farms/123"
  }
}
```

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success",
  "messageAr": "نجح",
  "timestamp": "2025-12-31T10:30:00.000Z"
}
```

---

## 🔧 API Documentation

```typescript
import { ErrorResponseDto } from '@sahool/shared/errors';

@ApiResponse({
  status: 404,
  description: 'Not found',
  type: ErrorResponseDto
})
@Get(':id')
async findById(@Param('id') id: string) {
  // ...
}
```

---

## 📝 Testing

```typescript
import { NotFoundException, ErrorCode } from '@sahool/shared/errors';

it('should throw correct error', async () => {
  try {
    await service.findById('invalid');
  } catch (error) {
    expect(error.errorCode).toBe(ErrorCode.FARM_NOT_FOUND);
    expect(error.messageEn).toBe('Farm not found');
    expect(error.messageAr).toBe('المزرعة غير موجودة');
  }
});
```

---

## 💡 Best Practices

✅ **DO:**
- Use specific exception types (e.g., `NotFoundException.farm()`)
- Include context in error details
- Use bilingual messages
- Return standardized responses
- Document errors in Swagger

❌ **DON'T:**
- Throw generic exceptions
- Hardcode error messages in multiple places
- Return inconsistent response formats
- Ignore retryable errors
- Skip error documentation

---

## 🔗 Resources

- [Full Documentation](./README.md)
- [Migration Guide](./MIGRATION_GUIDE.md)
- [Examples](./examples/)
- [Error Codes Reference](./error-codes.ts)
