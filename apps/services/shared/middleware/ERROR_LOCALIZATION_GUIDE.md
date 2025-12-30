# API Error Localization - Implementation Guide
# دليل تطبيق توطين أخطاء الواجهة البرمجية

This guide explains how to use the SAHOOL error localization system for both Python (FastAPI) and TypeScript (Express) services.

يشرح هذا الدليل كيفية استخدام نظام توطين الأخطاء في سهول لكل من خدمات Python (FastAPI) و TypeScript (Express).

---

## Features / الميزات

✅ **Bilingual Error Responses** - All errors return both English and Arabic messages
✅ **استجابات أخطاء ثنائية اللغة** - جميع الأخطاء تُرجع رسائل بالإنجليزية والعربية

✅ **Accept-Language Header Support** - Automatically detects preferred language
✅ **دعم رأس Accept-Language** - يكتشف اللغة المفضلة تلقائياً

✅ **Centralized Error Codes** - Consistent error codes across all services
✅ **رموز أخطاء مركزية** - رموز أخطاء متسقة عبر جميع الخدمات

✅ **Secure Error Handling** - Automatically filters sensitive information
✅ **معالجة أخطاء آمنة** - تصفية المعلومات الحساسة تلقائياً

---

## Response Format / تنسيق الاستجابة

All error responses follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found.",
    "message_ar": "المورد غير موجود.",
    "error": "Resource not found.",
    "error_id": "A3F2D891",
    "details": {
      "field": "id",
      "value": "123"
    }
  }
}
```

**Fields:**
- `success`: Always `false` for errors
- `error.code`: Error code (e.g., `NOT_FOUND`, `VALIDATION_ERROR`)
- `error.message`: English error message
- `error.message_ar`: Arabic error message
- `error.error`: Localized message based on `Accept-Language` header (optional)
- `error.error_id`: Unique error ID for tracking/debugging
- `error.details`: Additional error context (optional)

---

## Python (FastAPI) Implementation

### 1. Setup in Your FastAPI Application

```python
from fastapi import FastAPI
from apps.services.shared.middleware.exception_handler import setup_exception_handlers

app = FastAPI()

# Setup exception handlers with localization support
setup_exception_handlers(app)

# Your routes here...
```

### 2. Using Predefined Error Classes

```python
from apps.services.shared.middleware.exception_handler import (
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    RateLimitError,
)

@app.get("/fields/{field_id}")
async def get_field(field_id: str):
    field = await db.get_field(field_id)

    if not field:
        # Raises 404 with bilingual message
        raise NotFoundError("Field", "الحقل")

    return field

@app.post("/fields")
async def create_field(data: dict):
    if await db.field_exists(data["name"]):
        # Raises 409 Conflict
        raise ConflictError(
            "A field with this name already exists",
            "حقل بهذا الاسم موجود بالفعل"
        )

    return await db.create_field(data)
```

### 3. Using Custom AppError

```python
from apps.services.shared.middleware.exception_handler import AppError
from fastapi import status

@app.post("/process")
async def process_data(data: dict):
    if not validate_data(data):
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_DATA",
            message="Data validation failed",
            message_ar="فشل التحقق من البيانات",
            details={"field": "coordinates", "issue": "invalid format"}
        )

    return await process(data)
```

### 4. Adding New Error Translations

Edit `apps/services/shared/middleware/error_translations.py`:

```python
ERROR_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Add your custom error
    "CUSTOM_ERROR_CODE": {
        "en": "Custom error message in English",
        "ar": "رسالة الخطأ المخصصة بالعربية"
    },
    # ... existing errors
}
```

---

## TypeScript (Express) Implementation

### 1. Setup in Your Express Application

```typescript
import express from 'express';
import {
    languageParser,
    errorHandler,
    notFoundHandler,
    asyncHandler,
} from './middleware/errorLocalization';

const app = express();

// Apply language parser middleware early (before routes)
app.use(express.json());
app.use(languageParser());

// Your routes here...
app.get('/api/fields/:id', asyncHandler(async (req, res) => {
    const field = await getField(req.params.id);
    if (!field) {
        throw new NotFoundError('Field', 'الحقل');
    }
    res.json(field);
}));

// 404 handler (after all routes)
app.use(notFoundHandler);

// Error handler (must be last)
app.use(errorHandler);

app.listen(3000);
```

### 2. Using Predefined Error Classes

```typescript
import {
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    asyncHandler,
} from './middleware/errorLocalization';

// Example: Field retrieval
app.get('/api/fields/:id', asyncHandler(async (req, res) => {
    const field = await db.getField(req.params.id);

    if (!field) {
        throw new NotFoundError('Field', 'الحقل');
    }

    res.json({ success: true, data: field });
}));

// Example: Field creation with conflict check
app.post('/api/fields', asyncHandler(async (req, res) => {
    const exists = await db.fieldExists(req.body.name);

    if (exists) {
        throw new ConflictError(
            'A field with this name already exists',
            'حقل بهذا الاسم موجود بالفعل'
        );
    }

    const field = await db.createField(req.body);
    res.status(201).json({ success: true, data: field });
}));

// Example: Authentication check
app.get('/api/protected', asyncHandler(async (req, res) => {
    const token = req.headers.authorization;

    if (!token) {
        throw new AuthenticationError(
            'Authentication token is required',
            'رمز المصادقة مطلوب'
        );
    }

    const user = await verifyToken(token);
    res.json({ success: true, user });
}));
```

### 3. Using Custom AppError

```typescript
import { AppError, asyncHandler } from './middleware/errorLocalization';

app.post('/api/process', asyncHandler(async (req, res) => {
    if (!validateData(req.body)) {
        throw new AppError(
            400,
            'INVALID_DATA',
            'Data validation failed',
            'فشل التحقق من البيانات',
            { field: 'coordinates', issue: 'invalid format' }
        );
    }

    const result = await processData(req.body);
    res.json({ success: true, data: result });
}));
```

### 4. Adding New Error Translations

Edit `apps/services/field-core/src/middleware/errorTranslations.ts`:

```typescript
export const ERROR_TRANSLATIONS: Record<string, ErrorTranslation> = {
    // Add your custom error
    CUSTOM_ERROR_CODE: {
        en: "Custom error message in English",
        ar: "رسالة الخطأ المخصصة بالعربية",
    },
    // ... existing errors
};
```

---

## Testing Error Localization

### Test with English (default)

```bash
curl -X GET http://localhost:3000/api/fields/invalid-id
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Field not found.",
    "message_ar": "الحقل غير موجود.",
    "error": "Field not found.",
    "error_id": "A3F2D891"
  }
}
```

### Test with Arabic

```bash
curl -X GET http://localhost:3000/api/fields/invalid-id \
  -H "Accept-Language: ar"
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Field not found.",
    "message_ar": "الحقل غير موجود.",
    "error": "الحقل غير موجود.",
    "error_id": "A3F2D891"
  }
}
```

### Test with Language Priority

```bash
curl -X GET http://localhost:3000/api/fields/invalid-id \
  -H "Accept-Language: ar-SA,ar;q=0.9,en;q=0.8"
```

This will prefer Arabic (`ar`) based on quality values.

---

## Available Error Codes

### Validation Errors
- `VALIDATION_ERROR` - General validation failure
- `REQUIRED_FIELD` - Missing required field
- `INVALID_FORMAT` - Invalid format
- `INVALID_EMAIL` - Invalid email address
- `INVALID_UUID` - Invalid UUID format
- `VALUE_TOO_SMALL` / `VALUE_TOO_LARGE` - Value out of range
- `STRING_TOO_SHORT` / `STRING_TOO_LONG` - String length issues

### Authentication Errors
- `AUTHENTICATION_ERROR` / `UNAUTHORIZED` - Authentication required
- `INVALID_CREDENTIALS` - Wrong username/password
- `TOKEN_EXPIRED` - Session expired
- `TOKEN_INVALID` - Invalid token
- `TOKEN_MISSING` - Token not provided

### Authorization Errors
- `AUTHORIZATION_ERROR` / `FORBIDDEN` - Permission denied
- `INSUFFICIENT_PERMISSIONS` - Not enough permissions
- `TENANT_ACCESS_DENIED` - Organization access denied

### Resource Errors
- `NOT_FOUND` - Resource not found
- `FIELD_NOT_FOUND` - Field not found
- `USER_NOT_FOUND` - User not found
- `TENANT_NOT_FOUND` - Organization not found
- `CROP_NOT_FOUND` - Crop not found
- `DEVICE_NOT_FOUND` - Device not found

### Conflict Errors
- `CONFLICT` - General conflict
- `DUPLICATE_ENTRY` - Entry already exists
- `EMAIL_ALREADY_EXISTS` - Email already registered
- `VERSION_CONFLICT` - Optimistic locking conflict

### Rate Limiting
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `QUOTA_EXCEEDED` - Usage quota exceeded

### Server Errors
- `INTERNAL_ERROR` - Internal server error
- `DATABASE_ERROR` - Database error
- `SERVICE_UNAVAILABLE` - Service unavailable
- `TIMEOUT` - Request timeout

### Geospatial Errors
- `INVALID_COORDINATES` - Invalid coordinates
- `INVALID_POLYGON` - Invalid polygon geometry
- `AREA_TOO_LARGE` / `AREA_TOO_SMALL` - Area size issues
- `BOUNDARY_REQUIRED` - Boundary required

---

## Best Practices / أفضل الممارسات

### 1. Always Use Error Classes
✅ **Good:**
```python
raise NotFoundError("Field", "الحقل")
```

❌ **Bad:**
```python
raise HTTPException(status_code=404, detail="Not found")
```

### 2. Provide Meaningful Error Details
```python
raise ValidationError(
    "Invalid field boundary",
    "حدود الحقل غير صالحة",
    details={
        "field": "boundary",
        "issue": "polygon not closed",
        "coordinates_count": 3
    }
)
```

### 3. Use Async Handlers (TypeScript)
Always wrap async route handlers with `asyncHandler`:
```typescript
app.get('/api/fields', asyncHandler(async (req, res) => {
    // Your async code here
}));
```

### 4. Add Custom Error Codes
When adding domain-specific errors, add translations to both:
- `apps/services/shared/middleware/error_translations.py` (Python)
- `apps/services/field-core/src/middleware/errorTranslations.ts` (TypeScript)

### 5. Never Expose Sensitive Data
The system automatically filters these keys from error details:
- `password`
- `secret`
- `token`
- `api_key`
- `authorization`

---

## Migration Guide

### Migrating Existing Python Code

**Before:**
```python
from fastapi import HTTPException

@app.get("/fields/{id}")
async def get_field(id: str):
    field = await db.get_field(id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
```

**After:**
```python
from apps.services.shared.middleware.exception_handler import NotFoundError

@app.get("/fields/{id}")
async def get_field(id: str):
    field = await db.get_field(id)
    if not field:
        raise NotFoundError("Field", "الحقل")
    return field
```

### Migrating Existing TypeScript Code

**Before:**
```typescript
app.get('/api/fields/:id', async (req, res) => {
    const field = await db.getField(req.params.id);
    if (!field) {
        return res.status(404).json({ error: 'Field not found' });
    }
    res.json(field);
});
```

**After:**
```typescript
import { asyncHandler, NotFoundError } from './middleware/errorLocalization';

app.get('/api/fields/:id', asyncHandler(async (req, res) => {
    const field = await db.getField(req.params.id);
    if (!field) {
        throw new NotFoundError('Field', 'الحقل');
    }
    res.json({ success: true, data: field });
}));
```

---

## Troubleshooting / استكشاف الأخطاء

### Error translations not appearing
1. Verify the error handler is registered:
   - Python: `setup_exception_handlers(app)` called
   - TypeScript: `app.use(errorHandler)` is last middleware

2. Check error code exists in translations mapping

### Accept-Language header not working
1. Verify language parser is registered (TypeScript):
   ```typescript
   app.use(languageParser());
   ```

2. Check header format:
   ```
   Accept-Language: ar
   Accept-Language: en-US,en;q=0.9,ar;q=0.8
   ```

### Error details not showing
Ensure details don't contain sensitive keys that are automatically filtered.

---

## Support / الدعم

For questions or issues:
- Check existing error codes in translation files
- Review this guide for usage examples
- Ensure middleware is properly registered

---

**Created by:** SAHOOL Development Team
**Date:** 2025
**Version:** 1.0
