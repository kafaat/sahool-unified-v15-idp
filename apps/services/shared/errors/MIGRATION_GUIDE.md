# Migration Guide
# دليل الترحيل

This guide helps you migrate existing SAHOOL backend services to use the new shared error handling module.

يساعدك هذا الدليل في ترحيل خدمات SAHOOL الخلفية الحالية لاستخدام وحدة معالجة الأخطاء المشتركة الجديدة.

---

## 📋 Prerequisites | المتطلبات الأساسية

- NestJS v10.x or higher
- TypeScript 5.x or higher
- Existing service using NestJS exception system

---

## 🔄 Step-by-Step Migration | الترحيل خطوة بخطوة

### Step 1: Add Module Import Path

Update your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@sahool/shared/errors": ["../shared/errors"]
    }
  }
}
```

### Step 2: Install Global Exception Filter

**File:** `src/main.ts`

**Before:**
```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(3000);
}
bootstrap();
```

**After:**
```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from '@sahool/shared/errors';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Add global exception filter
  app.useGlobalFilters(new HttpExceptionFilter());

  await app.listen(3000);
}
bootstrap();
```

### Step 3: Replace Exception Imports

**Before:**
```typescript
import {
  BadRequestException,
  NotFoundException,
  UnauthorizedException,
  InternalServerErrorException,
} from '@nestjs/common';
```

**After:**
```typescript
import {
  ErrorCode,
  ValidationException,
  NotFoundException,
  AuthenticationException,
  InternalServerException,
} from '@sahool/shared/errors';
```

### Step 4: Update Exception Throws

#### Example 1: Not Found Exceptions

**Before:**
```typescript
async getWallet(walletId: string) {
  const wallet = await this.walletRepository.findById(walletId);
  if (!wallet) {
    throw new NotFoundException('المحفظة غير موجودة');
  }
  return wallet;
}
```

**After:**
```typescript
async getWallet(walletId: string) {
  const wallet = await this.walletRepository.findById(walletId);
  if (!wallet) {
    throw NotFoundException.wallet(walletId);
  }
  return wallet;
}
```

#### Example 2: Business Logic Exceptions

**Before:**
```typescript
async withdraw(walletId: string, amount: number) {
  if (amount <= 0) {
    throw new BadRequestException('المبلغ يجب أن يكون أكبر من صفر');
  }

  const wallet = await this.getWallet(walletId);

  if (wallet.balance < amount) {
    throw new BadRequestException('الرصيد غير كافي');
  }

  // Process withdrawal...
}
```

**After:**
```typescript
import { BusinessLogicException } from '@sahool/shared/errors';

async withdraw(walletId: string, amount: number) {
  if (amount <= 0) {
    throw BusinessLogicException.amountMustBePositive(amount);
  }

  const wallet = await this.getWallet(walletId);

  if (wallet.balance < amount) {
    throw BusinessLogicException.insufficientBalance(wallet.balance, amount);
  }

  // Process withdrawal...
}
```

#### Example 3: Authentication Exceptions

**Before:**
```typescript
private extractUserId(headers: any): string {
  const userId = headers['x-user-id'];
  if (!userId) {
    throw new UnauthorizedException('User authentication required');
  }
  return userId;
}
```

**After:**
```typescript
import { AuthenticationException, ErrorCode } from '@sahool/shared/errors';

private extractUserId(headers: any): string {
  const userId = headers['x-user-id'];
  if (!userId) {
    throw new AuthenticationException(ErrorCode.TOKEN_MISSING);
  }
  return userId;
}
```

#### Example 4: Validation Exceptions

**Before:**
```typescript
async createLoan(data: CreateLoanDto) {
  if (data.amount <= 0 || data.amount > 1000000) {
    throw new BadRequestException(
      'المبلغ يجب أن يكون بين 0 و 1,000,000'
    );
  }
  // ...
}
```

**After:**
```typescript
import { ValidationException, ErrorCode } from '@sahool/shared/errors';

async createLoan(data: CreateLoanDto) {
  if (data.amount <= 0 || data.amount > 1000000) {
    throw new ValidationException(
      ErrorCode.INVALID_RANGE,
      {
        en: 'Amount must be between 0 and 1,000,000',
        ar: 'المبلغ يجب أن يكون بين 0 و 1,000,000'
      },
      { min: 0, max: 1000000, provided: data.amount }
    );
  }
  // ...
}
```

### Step 5: Update Response Format

**Before:**
```typescript
@Get(':id')
async getFarm(@Param('id') id: string) {
  const farm = await this.farmService.findById(id);
  return farm;
}
```

**After:**
```typescript
import { createSuccessResponse } from '@sahool/shared/errors';

@Get(':id')
async getFarm(@Param('id') id: string) {
  const farm = await this.farmService.findById(id);
  return createSuccessResponse(
    farm,
    'Farm retrieved successfully',
    'تم استرجاع المزرعة بنجاح'
  );
}
```

### Step 6: Update API Documentation

**Before:**
```typescript
@ApiResponse({
  status: 404,
  description: 'Wallet not found',
})
```

**After:**
```typescript
import { ErrorResponseDto } from '@sahool/shared/errors';

@ApiResponse({
  status: 404,
  description: 'Wallet not found',
  type: ErrorResponseDto,
})
```

---

## 🔍 Common Migration Patterns | أنماط الترحيل الشائعة

### Pattern 1: Replace All BadRequestException

**Find:**
```typescript
throw new BadRequestException('...');
```

**Replace with one of:**
```typescript
// For validation errors
throw new ValidationException(ErrorCode.INVALID_INPUT, {
  en: 'English message',
  ar: 'الرسالة العربية'
});

// For business logic errors
throw new BusinessLogicException(ErrorCode.BUSINESS_RULE_VIOLATION, {
  en: 'English message',
  ar: 'الرسالة العربية'
});
```

### Pattern 2: Replace All NotFoundException

**Find:**
```typescript
throw new NotFoundException('المحفظة غير موجودة');
```

**Replace with:**
```typescript
throw NotFoundException.wallet(walletId);
// or
throw new NotFoundException(ErrorCode.WALLET_NOT_FOUND);
```

### Pattern 3: Replace All UnauthorizedException

**Find:**
```typescript
throw new UnauthorizedException('...');
```

**Replace with:**
```typescript
throw new AuthenticationException(ErrorCode.AUTHENTICATION_FAILED);
// or for specific cases
throw new AuthenticationException(ErrorCode.TOKEN_EXPIRED);
```

### Pattern 4: Replace All ForbiddenException

**Find:**
```typescript
throw new ForbiddenException('...');
```

**Replace with:**
```typescript
throw new AuthorizationException(ErrorCode.FORBIDDEN);
// or for specific cases
throw new AuthorizationException(ErrorCode.INSUFFICIENT_PERMISSIONS);
```

---

## 📝 Service-Specific Examples | أمثلة خاصة بالخدمات

### Marketplace Service (Fintech)

**File:** `apps/services/marketplace-service/src/fintech/fintech.service.ts`

**Before:**
```typescript
async deposit(walletId: string, amount: number) {
  if (amount <= 0) {
    throw new BadRequestException('المبلغ يجب أن يكون أكبر من صفر');
  }

  const wallet = await this.walletRepository.findById(walletId);
  if (!wallet) {
    throw new NotFoundException('المحفظة غير موجودة');
  }

  // Process deposit...
}
```

**After:**
```typescript
import {
  BusinessLogicException,
  NotFoundException,
} from '@sahool/shared/errors';

async deposit(walletId: string, amount: number) {
  if (amount <= 0) {
    throw BusinessLogicException.amountMustBePositive(amount);
  }

  const wallet = await this.walletRepository.findById(walletId);
  if (!wallet) {
    throw NotFoundException.wallet(walletId);
  }

  // Process deposit...
}
```

### Chat Service

**File:** `apps/services/chat-service/src/chat/chat.controller.ts`

**Before:**
```typescript
private extractUserId(headers: any): string {
  const userId = headers['x-user-id'];
  if (!userId) {
    throw new UnauthorizedException('User authentication required');
  }
  return userId;
}
```

**After:**
```typescript
import { AuthenticationException, ErrorCode } from '@sahool/shared/errors';

private extractUserId(headers: any): string {
  const userId = headers['x-user-id'];
  if (!userId) {
    throw new AuthenticationException(
      ErrorCode.TOKEN_MISSING,
      {
        en: 'User authentication required',
        ar: 'مطلوب مصادقة المستخدم'
      }
    );
  }
  return userId;
}
```

---

## ✅ Verification Checklist | قائمة التحقق

After migration, verify:

- [ ] All endpoints return standardized error responses
- [ ] Error messages include both English and Arabic
- [ ] HTTP status codes are correct
- [ ] Error codes are assigned to all errors
- [ ] Swagger documentation shows correct error response types
- [ ] Tests are updated to use new exception types
- [ ] Logging includes error codes
- [ ] Retryable errors are marked correctly

---

## 🧪 Testing Migration | اختبار الترحيل

Update your tests:

**Before:**
```typescript
it('should throw NotFoundException', async () => {
  await expect(service.findById('invalid')).rejects.toThrow(NotFoundException);
});
```

**After:**
```typescript
import { NotFoundException, ErrorCode } from '@sahool/shared/errors';

it('should throw NotFoundException with correct error code', async () => {
  try {
    await service.findById('invalid');
    fail('Should have thrown NotFoundException');
  } catch (error) {
    expect(error).toBeInstanceOf(NotFoundException);
    expect(error.errorCode).toBe(ErrorCode.FARM_NOT_FOUND);
    expect(error.messageEn).toBe('Farm not found');
    expect(error.messageAr).toBe('المزرعة غير موجودة');
  }
});
```

---

## 🚨 Breaking Changes | التغييرات الكبيرة

### Response Format

**Old:**
```json
{
  "statusCode": 404,
  "message": "Resource not found"
}
```

**New:**
```json
{
  "success": false,
  "error": {
    "code": "ERR_4000",
    "message": "Resource not found",
    "messageAr": "المورد غير موجود",
    "retryable": false,
    "timestamp": "2025-12-31T10:30:00.000Z",
    "path": "/api/v1/resource/123"
  }
}
```

### Exception Constructors

Some NestJS exceptions take a single string parameter, while our new exceptions require structured parameters. Make sure to update all exception throws accordingly.

---

## 📞 Support | الدعم

If you encounter issues during migration:

1. Check the [README.md](./README.md) for detailed documentation
2. Review the [examples](./examples/) directory
3. Contact the SAHOOL development team

---

## 📅 Migration Timeline | الجدول الزمني للترحيل

Recommended migration approach:

1. **Week 1:** Migrate core services (auth, billing)
2. **Week 2:** Migrate high-traffic services (marketplace, chat)
3. **Week 3:** Migrate remaining services
4. **Week 4:** Testing and validation

---

## 🎯 Benefits After Migration | الفوائد بعد الترحيل

- ✅ Consistent error handling across all services
- ✅ Bilingual error messages (English & Arabic)
- ✅ Better error tracking with error codes
- ✅ Improved API documentation
- ✅ Easier debugging and monitoring
- ✅ Retryable error identification
- ✅ Better client error handling
