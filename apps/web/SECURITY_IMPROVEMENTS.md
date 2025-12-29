# Frontend Security Improvements

This document describes the XSS vulnerability fixes and security enhancements implemented in the frontend application.

## Overview

Multiple XSS (Cross-Site Scripting) vulnerabilities and insecure data handling issues have been addressed across the frontend codebase. These improvements enhance the application's security posture and protect against malicious attacks.

## Changes Implemented

### 1. XSS Prevention with DOMPurify

**Files Modified:**
- `/apps/web/src/components/dashboard/MapView.tsx`
- `/apps/web/src/features/equipment/components/EquipmentMap.tsx`
- `/apps/web/src/features/iot/components/SensorMap.tsx`

**Changes:**
- Replaced manual HTML escaping with DOMPurify library for robust sanitization
- All user-generated content in map popups is now sanitized before rendering
- Implemented allowlist-based sanitization (only allowing specific HTML tags and attributes)

**Before:**
```typescript
const escapeHtml = (text: string | number | undefined): string => {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML; // Inefficient and potentially unsafe
};
```

**After:**
```typescript
const safeName = DOMPurify.sanitize(String(props?.name || 'حقل'), { ALLOWED_TAGS: [] });
const popupContent = DOMPurify.sanitize(`...`, {
  ALLOWED_TAGS: ['div', 'h4', 'p', 'span'],
  ALLOWED_ATTR: ['class', 'dir'],
});
```

### 2. Proper TypeScript Typing for External Libraries

**Files Modified:**
- `/apps/web/src/features/equipment/components/EquipmentMap.tsx`
- `/apps/web/src/features/iot/components/SensorMap.tsx`

**Changes:**
- Removed `@ts-ignore` comments
- Added proper global type declarations for Leaflet library
- Implemented null checks before accessing `window.L`

**Before:**
```typescript
// @ts-ignore - Leaflet is loaded via CDN
const L = window.L;
if (!L) return;
```

**After:**
```typescript
// Proper global type declaration
declare global {
  interface Window {
    L?: typeof import('leaflet');
  }
}

// Proper null check
if (typeof window === 'undefined' || !window.L) {
  console.warn('Leaflet library not loaded');
  return;
}
const L = window.L;
```

### 3. Encrypted LocalStorage with Zod Validation

**Files Modified:**
- `/apps/web/src/features/marketplace/hooks/useCart.tsx`

**Changes:**
- Implemented AES encryption for cart data in localStorage
- Added Zod schema validation for all cart data
- Automatic migration from old unencrypted cart data
- Comprehensive type safety for cart operations

**Key Features:**
- AES-256 encryption using crypto-js
- Schema validation prevents malformed data
- Environment variable support for encryption key
- Backward compatibility with migration path

**Implementation:**
```typescript
// Encryption
const encrypted = CryptoJS.AES.encrypt(jsonString, CART_ENCRYPTION_KEY).toString();
localStorage.setItem(CART_STORAGE_KEY, encrypted);

// Decryption with validation
const bytes = CryptoJS.AES.decrypt(encryptedData, CART_ENCRYPTION_KEY);
const decryptedString = bytes.toString(CryptoJS.enc.Utf8);
const parsed = JSON.parse(decryptedString);
const validated = CartItemsSchema.parse(parsed); // Zod validation
```

### 4. Safe JSON Parsing Utility

**New File:**
- `/apps/web/src/lib/utils/safeJson.ts`

**Features:**
- Safe JSON parsing with optional Zod schema validation
- Default value fallback support
- Comprehensive error handling
- Type-safe operations

**Usage:**
```typescript
import { safeJsonParse } from '@/lib/utils/safeJson';

// With validation
const data = safeJsonParse<MyType>(jsonString, MySchema);

// With default fallback
const data = safeJsonParseWithDefault(jsonString, defaultValue, MySchema);
```

### 5. Validated JSON Parsing in WebSocket Handlers

**Files Modified:**
- `/apps/web/src/hooks/useWebSocket.ts`
- `/apps/web/src/lib/ws/index.ts`

**Changes:**
- All WebSocket message parsing now uses Zod validation
- Invalid messages are rejected before processing
- Prevents injection attacks through WebSocket messages

**Implementation:**
```typescript
const WSMessageSchema = z.object({
  type: z.enum(['kpi_update', 'alert_new', ...]),
  payload: z.unknown(),
  timestamp: z.string(),
});

const message = safeJsonParse<WSMessage>(event.data, WSMessageSchema);
if (message) {
  onMessageRef.current?.(message);
}
```

### 6. Validated LocalStorage Operations

**Files Modified:**
- `/apps/web/src/lib/services/service-switcher.ts`

**Changes:**
- All localStorage read/write operations now use safe JSON utilities
- Zod schema validation for service version data
- Type-safe storage operations

## Dependencies Added

```json
{
  "dependencies": {
    "dompurify": "^3.2.3",
    "zod": "^4.2.1",
    "crypto-js": "^4.2.0"
  },
  "devDependencies": {
    "@types/dompurify": "^3.2.0",
    "@types/crypto-js": "^4.2.2"
  }
}
```

## Security Best Practices

### 1. Content Sanitization
- Always use DOMPurify for any user-generated HTML content
- Use allowlist-based sanitization (ALLOWED_TAGS, ALLOWED_ATTR)
- Never trust user input

### 2. Data Validation
- Validate all external data with Zod schemas
- Use type-safe parsing utilities
- Handle validation errors gracefully

### 3. Storage Security
- Encrypt sensitive data in localStorage
- Use environment variables for encryption keys
- Implement data migration for breaking changes

### 4. Type Safety
- Remove all `@ts-ignore` comments
- Use proper type declarations for external libraries
- Implement null checks before accessing global objects

## Environment Variables

For production deployment, set the following environment variable:

```bash
NEXT_PUBLIC_CART_ENCRYPTION_KEY=your-secure-random-key-here
```

**Important:** Generate a strong, random key for production use. The default key is only for development.

## Testing

All changes have been verified with:
- TypeScript type checking: `npm run type-check`
- Build verification: `npm run build`
- Runtime testing of affected components

## Migration Guide

### For Existing Users

Cart data will be automatically migrated from the old unencrypted format to the new encrypted format on first load. No user action is required.

### For Developers

When working with JSON data:
1. Use `safeJsonParse()` instead of `JSON.parse()`
2. Define Zod schemas for all data structures
3. Use DOMPurify for all HTML content
4. Never use `@ts-ignore` - add proper type declarations

## Future Recommendations

1. **Content Security Policy (CSP)**: Implement strict CSP headers
2. **Input Validation**: Add server-side validation for all API endpoints
3. **Rate Limiting**: Implement rate limiting on sensitive operations
4. **Security Audits**: Regular security audits and penetration testing
5. **Dependency Updates**: Keep security-related dependencies up to date

## References

- [DOMPurify Documentation](https://github.com/cure53/DOMPurify)
- [Zod Documentation](https://zod.dev/)
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Web Crypto Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
