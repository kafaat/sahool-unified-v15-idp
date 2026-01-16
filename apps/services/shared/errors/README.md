# Shared Error Handling Module

# وحدة معالجة الأخطاء المشتركة

## نظرة عامة | Overview

This module provides a comprehensive, standardized error handling system for all SAHOOL backend services. It includes:

توفر هذه الوحدة نظام معالجة أخطاء شامل وموحد لجميع خدمات SAHOOL الخلفية. يتضمن:

- ✅ Centralized error codes with bilingual messages (English & Arabic)
- ✅ Custom exception classes for different error categories
- ✅ HTTP exception filter for consistent error responses
- ✅ Standardized error response format
- ✅ Utility functions for error handling
- ✅ Support for validation errors
- ✅ Retry mechanisms and circuit breaker pattern

---

## 📦 Installation | التثبيت

### Step 1: Import in your service

Add to your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@sahool/shared/errors": ["../shared/errors"]
    }
  }
}
```

### Step 2: Install the exception filter globally

In your `main.ts`:

```typescript
import { HttpExceptionFilter } from "@sahool/shared/errors";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Register global exception filter
  app.useGlobalFilters(new HttpExceptionFilter());

  await app.listen(3000);
}
```

---

## 🚀 Quick Start | البداية السريعة

### Basic Usage

```typescript
import {
  ErrorCode,
  NotFoundException,
  BusinessLogicException
} from '@sahool/shared/errors';

// Example 1: Throw a not found exception
async findFarm(id: string) {
  const farm = await this.farmRepository.findById(id);
  if (!farm) {
    throw NotFoundException.farm(id);
  }
  return farm;
}

// Example 2: Business logic validation
async withdraw(walletId: string, amount: number) {
  const wallet = await this.findWallet(walletId);

  if (amount <= 0) {
    throw BusinessLogicException.amountMustBePositive(amount);
  }

  if (wallet.balance < amount) {
    throw BusinessLogicException.insufficientBalance(wallet.balance, amount);
  }

  // Process withdrawal...
}
```

---

## 📋 Error Codes | أكواد الأخطاء

### Categories | الفئات

Error codes are organized into categories:

| Category         | Range       | Description                                        |
| ---------------- | ----------- | -------------------------------------------------- |
| Validation       | 1000-1999   | Input validation errors - أخطاء التحقق من المدخلات |
| Authentication   | 2000-2999   | Authentication failures - فشل المصادقة             |
| Authorization    | 3000-3999   | Permission/access errors - أخطاء الصلاحيات         |
| Not Found        | 4000-4999   | Resource not found - الموارد غير الموجودة          |
| Conflict         | 5000-5999   | Resource conflicts - تعارض الموارد                 |
| Business Logic   | 6000-6999   | Business rule violations - انتهاك قواعد العمل      |
| External Service | 7000-7999   | External API errors - أخطاء الخدمات الخارجية       |
| Database         | 8000-8999   | Database errors - أخطاء قاعدة البيانات             |
| Internal         | 9000-9999   | Internal server errors - أخطاء الخادم الداخلي      |
| Rate Limit       | 10000-10999 | Rate limiting - تجاوز الحد المسموح                 |

### Common Error Codes

```typescript
// Validation
ErrorCode.VALIDATION_ERROR; // ERR_1000
ErrorCode.INVALID_INPUT; // ERR_1001
ErrorCode.INVALID_EMAIL; // ERR_1004

// Authentication
ErrorCode.AUTHENTICATION_FAILED; // ERR_2000
ErrorCode.TOKEN_EXPIRED; // ERR_2002
ErrorCode.TOKEN_INVALID; // ERR_2003

// Authorization
ErrorCode.FORBIDDEN; // ERR_3000
ErrorCode.INSUFFICIENT_PERMISSIONS; // ERR_3001
ErrorCode.QUOTA_EXCEEDED; // ERR_3006

// Not Found
ErrorCode.RESOURCE_NOT_FOUND; // ERR_4000
ErrorCode.USER_NOT_FOUND; // ERR_4001
ErrorCode.FARM_NOT_FOUND; // ERR_4002
ErrorCode.WALLET_NOT_FOUND; // ERR_4008

// Business Logic
ErrorCode.INSUFFICIENT_BALANCE; // ERR_6001
ErrorCode.AMOUNT_MUST_BE_POSITIVE; // ERR_6004
ErrorCode.OPERATION_NOT_ALLOWED; // ERR_6003
```

---

## 🎯 Exception Classes | فئات الاستثناءات

### Base Exception

```typescript
import { AppException, ErrorCode } from "@sahool/shared/errors";

throw new AppException(
  ErrorCode.VALIDATION_ERROR,
  { en: "Custom message", ar: "رسالة مخصصة" },
  { customField: "value" },
);
```

### Validation Exception

```typescript
import { ValidationException } from "@sahool/shared/errors";

// Simple validation error
throw new ValidationException(ErrorCode.INVALID_EMAIL);

// With field errors
throw ValidationException.fromFieldErrors([
  {
    field: "email",
    message: "Invalid email format",
    messageAr: "تنسيق البريد الإلكتروني غير صالح",
  },
  {
    field: "phone",
    message: "Invalid phone number",
    messageAr: "رقم هاتف غير صالح",
  },
]);
```

### Not Found Exception

```typescript
import { NotFoundException } from "@sahool/shared/errors";

// Generic
throw new NotFoundException();

// Specific resource types (recommended)
throw NotFoundException.farm("farm-123");
throw NotFoundException.user("user-456");
throw NotFoundException.wallet("wallet-789");
throw NotFoundException.conversation("conv-abc");
```

### Business Logic Exception

```typescript
import { BusinessLogicException } from "@sahool/shared/errors";

// Insufficient balance
throw BusinessLogicException.insufficientBalance(100, 150);
// Returns: "Insufficient balance" (EN) / "الرصيد غير كافي" (AR)
// Details: { available: 100, required: 150 }

// Amount validation
throw BusinessLogicException.amountMustBePositive(-50);

// State transition
throw BusinessLogicException.invalidStateTransition("PENDING", "COMPLETED");

// Operation not allowed
throw BusinessLogicException.operationNotAllowed(
  "delete",
  "Order is already shipped",
);
```

### External Service Exception

```typescript
import { ExternalServiceException } from "@sahool/shared/errors";

try {
  await weatherService.getCurrentWeather(location);
} catch (error) {
  throw ExternalServiceException.weatherService(error);
}

// Other services
throw ExternalServiceException.satelliteService(error);
throw ExternalServiceException.paymentGateway(error);
throw ExternalServiceException.smsService(error);
throw ExternalServiceException.emailService(error);
```

### Database Exception

```typescript
import { DatabaseException } from "@sahool/shared/errors";

try {
  await prisma.user.create({ data });
} catch (error) {
  // Automatically handles Prisma error codes
  throw DatabaseException.fromDatabaseError(error);
}
```

---

## 📤 Error Response Format | تنسيق استجابة الخطأ

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
    "path": "/api/v1/farms/farm-123",
    "requestId": "req-1234567890",
    "details": {
      "farmId": "farm-123"
    }
  }
}
```

### Validation Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERR_1000",
    "message": "Validation error occurred",
    "messageAr": "حدث خطأ في التحقق من صحة البيانات",
    "category": "VALIDATION",
    "retryable": false,
    "timestamp": "2025-12-31T10:30:00.000Z",
    "path": "/api/v1/farms",
    "details": {
      "fields": [
        {
          "field": "name",
          "message": "Name is required",
          "constraint": "isNotEmpty"
        },
        {
          "field": "area",
          "message": "Area must be a positive number",
          "constraint": "isPositive"
        }
      ]
    }
  }
}
```

---

## ✅ Success Response Format | تنسيق استجابة النجاح

For consistency, use the success response DTOs:

```typescript
import { createSuccessResponse, createPaginatedResponse } from '@sahool/shared/errors';

// Simple success response
@Get(':id')
async getFarm(@Param('id') id: string) {
  const farm = await this.farmService.findById(id);
  return createSuccessResponse(
    farm,
    'Farm retrieved successfully',
    'تم استرجاع المزرعة بنجاح'
  );
}

// Paginated response
@Get()
async getFarms(@Query('page') page: number, @Query('limit') limit: number) {
  const { farms, total } = await this.farmService.findAll(page, limit);
  return createPaginatedResponse(
    farms,
    page,
    limit,
    total,
    'Farms retrieved successfully',
    'تم استرجاع المزارع بنجاح'
  );
}
```

Success response format:

```json
{
  "success": true,
  "data": {
    "id": "farm-123",
    "name": "My Farm"
  },
  "message": "Farm retrieved successfully",
  "messageAr": "تم استرجاع المزرعة بنجاح",
  "timestamp": "2025-12-31T10:30:00.000Z"
}
```

Paginated response format:

```json
{
  "success": true,
  "data": [
    { "id": "farm-1", "name": "Farm 1" },
    { "id": "farm-2", "name": "Farm 2" }
  ],
  "message": "Farms retrieved successfully",
  "messageAr": "تم استرجاع المزارع بنجاح",
  "timestamp": "2025-12-31T10:30:00.000Z",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5,
    "hasNextPage": true,
    "hasPreviousPage": false
  }
}
```

---

## 🛠️ Utility Functions | الدوال المساعدة

### Error Handling Decorator

```typescript
import { HandleErrors } from "@sahool/shared/errors";

export class FarmService {
  @HandleErrors(ErrorCode.DATABASE_ERROR)
  async createFarm(data: CreateFarmDto) {
    // Method implementation
    // Any unhandled errors will be wrapped in DatabaseException
  }
}
```

### Retry with Backoff

```typescript
import { retryWithBackoff } from "@sahool/shared/errors";

const result = await retryWithBackoff(
  async () => {
    return await externalApi.call();
  },
  {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 10000,
    shouldRetry: (error) => error.retryable,
  },
);
```

### Circuit Breaker

```typescript
import { CircuitBreaker } from "@sahool/shared/errors";

const breaker = new CircuitBreaker(5, 60000, 30000);

try {
  const result = await breaker.execute(async () => {
    return await externalService.call();
  });
} catch (error) {
  // Handle error
}

// Check circuit breaker state
const state = breaker.getState();
// { state: 'CLOSED', failureCount: 0, lastFailureTime: null }
```

### Timeout Wrapper

```typescript
import { withTimeout } from "@sahool/shared/errors";

const result = await withTimeout(
  slowOperation(),
  5000, // 5 seconds
  "Operation took too long",
);
```

### Error Aggregation

```typescript
import { ErrorAggregator } from "@sahool/shared/errors";

const aggregator = new ErrorAggregator();

for (let i = 0; i < items.length; i++) {
  try {
    await processItem(items[i]);
  } catch (error) {
    aggregator.add(i, error);
  }
}

// Throw if there are any errors
aggregator.throwIfHasErrors();
```

---

## 🌐 Language Support | دعم اللغات

The module supports bilingual error messages (English and Arabic). The response always includes both languages:

```json
{
  "error": {
    "message": "Farm not found",
    "messageAr": "المزرعة غير موجودة"
  }
}
```

For language-aware filtering based on `Accept-Language` header:

```typescript
import { LanguageAwareExceptionFilter } from "@sahool/shared/errors";

// In main.ts
app.useGlobalFilters(new LanguageAwareExceptionFilter());
```

---

## 🔧 Configuration | التكوين

### Environment Variables

```bash
# Include stack trace in error responses (development only)
INCLUDE_STACK_TRACE=true

# Node environment
NODE_ENV=development
```

### Custom Request ID Header

The filter automatically extracts request IDs from these headers (in order):

- `x-request-id`
- `x-correlation-id`
- Auto-generated if not present

---

## 📚 API Documentation

All error responses are automatically documented in Swagger/OpenAPI when using the DTOs:

```typescript
import { ErrorResponseDto } from '@sahool/shared/errors';

@ApiResponse({
  status: 404,
  description: 'Farm not found',
  type: ErrorResponseDto
})
@Get(':id')
async getFarm(@Param('id') id: string) {
  // ...
}
```

---

## 🧪 Testing | الاختبار

### Unit Testing Exceptions

```typescript
import { NotFoundException, ErrorCode } from "@sahool/shared/errors";

describe("FarmService", () => {
  it("should throw NotFoundException when farm not found", async () => {
    await expect(service.findById("invalid-id")).rejects.toThrow(
      NotFoundException,
    );
  });

  it("should include correct error code", async () => {
    try {
      await service.findById("invalid-id");
    } catch (error) {
      expect(error.errorCode).toBe(ErrorCode.FARM_NOT_FOUND);
      expect(error.messageEn).toBe("Farm not found");
      expect(error.messageAr).toBe("المزرعة غير موجودة");
    }
  });
});
```

---

## 📊 Error Code Reference | مرجع أكواد الأخطاء

See the complete list of error codes in [`error-codes.ts`](./error-codes.ts).

### Quick Reference

| Code      | English                 | Arabic                | HTTP Status |
| --------- | ----------------------- | --------------------- | ----------- |
| ERR_1000  | Validation error        | خطأ في التحقق         | 400         |
| ERR_2000  | Authentication failed   | فشل المصادقة          | 401         |
| ERR_3000  | Forbidden               | محظور                 | 403         |
| ERR_4000  | Resource not found      | المورد غير موجود      | 404         |
| ERR_5000  | Resource already exists | المورد موجود بالفعل   | 409         |
| ERR_6000  | Business rule violation | انتهاك قاعدة عمل      | 422         |
| ERR_7000  | External service error  | خطأ في خدمة خارجية    | 502         |
| ERR_8000  | Database error          | خطأ في قاعدة البيانات | 500         |
| ERR_9000  | Internal server error   | خطأ داخلي في الخادم   | 500         |
| ERR_10000 | Rate limit exceeded     | تجاوز الحد المسموح    | 429         |

---

## 🎨 Best Practices | أفضل الممارسات

### 1. Use Specific Exception Types

❌ **Bad:**

```typescript
throw new AppException(ErrorCode.RESOURCE_NOT_FOUND);
```

✅ **Good:**

```typescript
throw NotFoundException.farm(farmId);
```

### 2. Include Context in Error Details

❌ **Bad:**

```typescript
throw BusinessLogicException.insufficientBalance(balance, amount);
```

✅ **Better:**

```typescript
throw new BusinessLogicException(ErrorCode.INSUFFICIENT_BALANCE, undefined, {
  available: balance,
  required: amount,
  currency: "YER",
  walletId: wallet.id,
});
```

### 3. Don't Catch and Rethrow Generic Errors

❌ **Bad:**

```typescript
try {
  await operation();
} catch (error) {
  throw new InternalServerException();
}
```

✅ **Good:**

```typescript
try {
  await operation();
} catch (error) {
  if (error instanceof AppException) {
    throw error; // Preserve original exception
  }
  throw DatabaseException.fromDatabaseError(error);
}
```

### 4. Use Success Response DTOs

❌ **Bad:**

```typescript
return { data: farms };
```

✅ **Good:**

```typescript
return createSuccessResponse(farms, "Success", "نجح");
```

### 5. Validate Business Rules Before Database Operations

✅ **Good:**

```typescript
async createOrder(data: CreateOrderDto) {
  // Validate business rules first
  if (data.amount <= 0) {
    throw BusinessLogicException.amountMustBePositive(data.amount);
  }

  // Then perform database operations
  return await this.orderRepository.create(data);
}
```

---

## 🔍 Troubleshooting | حل المشكلات

### Problem: Stack traces not showing in development

**Solution:** Set environment variable:

```bash
INCLUDE_STACK_TRACE=true
NODE_ENV=development
```

### Problem: Validation errors not formatted correctly

**Solution:** Make sure you're using `class-validator` DTOs and the global ValidationPipe:

```typescript
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }),
);
```

### Problem: Custom error messages not showing

**Solution:** Pass custom messages to the exception constructor:

```typescript
throw new NotFoundException(ErrorCode.FARM_NOT_FOUND, {
  en: `Farm with ID ${farmId} was not found`,
  ar: `المزرعة ذات المعرف ${farmId} غير موجودة`,
});
```

---

## 📞 Support | الدعم

For questions or issues:

- Check the [examples](./examples/) directory
- Review the [error codes reference](./error-codes.ts)
- Contact the SAHOOL development team

---

## 📝 License

MIT License - SAHOOL Platform
