# Security Headers and CORS Implementation Summary

## Overview

This document summarizes the security improvements implemented for Express-based services in the Sahool platform. The changes include strict CORS configuration and comprehensive security headers following OWASP best practices.

## Changes Made

### 1. Created Shared Security Middleware (`/apps/services/shared/middleware-ts/`)

A new shared middleware module was created with the following components:

#### A. `securityHeaders.ts`
Implements comprehensive security headers:

- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking attacks
- **X-XSS-Protection**: `1; mode=block` - Enables browser XSS protection
- **Strict-Transport-Security**: `max-age=31536000; includeSubDomains` - Enforces HTTPS (production only)
- **Content-Security-Policy**: Comprehensive CSP with the following directives:
  - `default-src 'self'`
  - `script-src 'self' 'unsafe-inline'`
  - `style-src 'self' 'unsafe-inline'`
  - `img-src 'self' data: https:`
  - `font-src 'self' data:`
  - `connect-src 'self'`
  - `frame-ancestors 'none'`
  - `base-uri 'self'`
  - `form-action 'self'`
  - `object-src 'none'`
  - `upgrade-insecure-requests` (production only)
- **Referrer-Policy**: `strict-origin-when-cross-origin`
- **Permissions-Policy**: Disables dangerous browser features
- **X-Permitted-Cross-Domain-Policies**: `none`

**Additional Features**:
- `customCSP()` - Allows route-specific CSP customization
- `removeSensitiveHeaders()` - Removes X-Powered-By and Server headers

#### B. `corsConfig.ts`
Implements strict CORS configuration:

**Key Features**:
- Rejects requests without Origin header in production
- Supports environment variable `ALLOWED_ORIGINS` for origin configuration
- Default production origins:
  - `https://sahool.app`
  - `https://admin.sahool.app`
  - `https://api.sahool.app`
  - `https://api.sahool.io`
- Development origins (only in non-production):
  - `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`, `http://localhost:4200`
  - `http://127.0.0.1:*` variants
- Credentials support enabled
- Configurable methods and headers
- Exposed headers: ETag, X-Request-ID, X-RateLimit-* headers

**Exported Functions**:
- `createSecureCorsOptions(options?)` - Create custom CORS configuration
- `secureCors` - Default secure CORS middleware
- `corsWithServerSupport` - CORS that allows requests without Origin header
- `corsWithCustomOrigins(origins)` - CORS with additional custom origins

### 2. Updated Services

#### A. Field Core Service (`/apps/services/field-core/src/index.ts`)

**Lines 27-31**: Added imports
```typescript
import {
    securityHeaders,
    removeSensitiveHeaders,
    createSecureCorsOptions
} from "../../shared/middleware-ts";
```

**Lines 36-78**: Replaced old CORS configuration
- Removed hardcoded origin list
- Implemented `createSecureCorsOptions()` with `allowNoOrigin: false`
- Added `removeSensitiveHeaders` middleware
- Added `securityHeaders` middleware

#### B. Field Management Service (`/apps/services/field-management-service/src/index.ts`)

**Lines 22-26**: Added imports
```typescript
import {
    securityHeaders,
    removeSensitiveHeaders,
    createSecureCorsOptions
} from "../../shared/middleware-ts";
```

**Lines 31-73**: Replaced old CORS configuration
- Same changes as field-core service

## Security Improvements

### CORS Security

**Before**:
```typescript
origin: (origin, callback) => {
    // Allow requests with no origin (mobile apps, curl, etc)
    if (!origin) return callback(null, true);  // ⚠️ SECURITY ISSUE
    // ...
}
```

**After**:
```typescript
origin: (origin, callback) => {
    if (!origin) {
        if (isProduction && !options?.allowNoOrigin) {
            console.warn('⚠️ CORS blocked request: No Origin header in production');
            return callback(new Error('Not allowed by CORS - Origin header required'));
        }
        return callback(null, true);
    }
    // ...
}
```

**Benefits**:
- ✅ In production, rejects requests without Origin header (prevents unauthorized server-to-server requests)
- ✅ Supports environment variable configuration (`ALLOWED_ORIGINS`)
- ✅ Strict origin validation
- ✅ Better logging of blocked requests

### Security Headers Benefits

1. **XSS Protection**: CSP prevents injection of malicious scripts
2. **Clickjacking Prevention**: X-Frame-Options prevents embedding in iframes
3. **MIME Sniffing Prevention**: X-Content-Type-Options prevents content type confusion attacks
4. **HTTPS Enforcement**: HSTS ensures all connections use HTTPS in production
5. **Information Disclosure Prevention**: Removed X-Powered-By and Server headers
6. **Feature Policy**: Disables unused browser features to reduce attack surface

## Environment Variables

New environment variable support:

```bash
# Comma-separated list of allowed origins
ALLOWED_ORIGINS=https://sahool.app,https://admin.sahool.app,https://custom.domain.com

# Environment (affects HSTS and CSP)
NODE_ENV=production
```

## Usage Examples

### Basic Usage (Already Applied)

```typescript
import { securityHeaders, removeSensitiveHeaders, createSecureCorsOptions } from "../../shared/middleware-ts";
import cors from "cors";

const app = express();

app.use(removeSensitiveHeaders);
app.use(cors(createSecureCorsOptions()));
app.use(securityHeaders);
```

### Custom CORS for Specific Routes

```typescript
import { corsWithCustomOrigins } from "../../shared/middleware-ts";

// Allow additional origin for specific route
app.use('/api/public', corsWithCustomOrigins(['https://partner.example.com']));
```

### Custom CSP for Upload Routes

```typescript
import { customCSP } from "../../shared/middleware-ts";

// Allow images from CDN
app.use('/api/upload', customCSP({
  'img-src': "'self' https://cdn.sahool.app data:",
  'connect-src': "'self' https://api.sahool.app"
}));
```

### Allow Server-to-Server Requests

```typescript
import { corsWithServerSupport } from "../../shared/middleware-ts";

// For APIs that need to accept requests from other services
app.use(corsWithServerSupport);
```

## Testing

### Test CORS Behavior

```bash
# Should be rejected in production without Origin header
curl -X GET http://localhost:3000/api/v1/fields

# Should be accepted with valid Origin
curl -X GET http://localhost:3000/api/v1/fields \
  -H "Origin: https://sahool.app"

# Should be rejected with invalid Origin
curl -X GET http://localhost:3000/api/v1/fields \
  -H "Origin: https://malicious.com"
```

### Verify Security Headers

```bash
# Check response headers
curl -I http://localhost:3000/api/v1/fields

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: ...
# Referrer-Policy: strict-origin-when-cross-origin
# Permissions-Policy: ...
```

## Migration Guide for Other Services

To apply these security improvements to other Express services:

1. **Add the import**:
```typescript
import {
    securityHeaders,
    removeSensitiveHeaders,
    createSecureCorsOptions
} from "../../shared/middleware-ts";
import cors from "cors";
```

2. **Replace CORS configuration**:
```typescript
// Remove old CORS code
// const allowedOrigins = [...];
// const corsOptions = { ... };

// Add new secure CORS
const corsOptions = createSecureCorsOptions({
    allowNoOrigin: false,  // Reject requests without Origin in production
    additionalOrigins: [], // Add any service-specific origins
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: [
        'Content-Type',
        'Authorization',
        // Add service-specific headers
    ]
});
```

3. **Apply middleware in correct order**:
```typescript
app.use(removeSensitiveHeaders);  // First
app.use(cors(corsOptions));       // Second
app.use(securityHeaders);         // Third
app.use(express.json());          // Fourth
```

## Files Created/Modified

### Created
- `/apps/services/shared/middleware-ts/securityHeaders.ts`
- `/apps/services/shared/middleware-ts/corsConfig.ts`
- `/apps/services/shared/middleware-ts/index.ts`
- `/apps/services/shared/middleware-ts/package.json`
- `/apps/services/shared/middleware-ts/tsconfig.json`
- `/apps/services/shared/middleware-ts/README.md`
- `/apps/services/shared/middleware-ts/IMPLEMENTATION_SUMMARY.md`

### Modified
- `/apps/services/field-core/src/index.ts` (lines 27-31, 36-78)
- `/apps/services/field-management-service/src/index.ts` (lines 22-26, 31-73)

## Security Compliance

These implementations follow:
- ✅ [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- ✅ [MDN Web Security Guidelines](https://developer.mozilla.org/en-US/docs/Web/Security)
- ✅ [Content Security Policy Level 3](https://www.w3.org/TR/CSP3/)
- ✅ [CORS Best Practices](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

## Monitoring Recommendations

1. **Monitor CSP Violations**: Consider adding CSP reporting endpoint
2. **Track CORS Rejections**: Monitor logs for blocked CORS requests
3. **Security Headers Validation**: Use tools like [securityheaders.com](https://securityheaders.com/) to validate headers
4. **Regular Updates**: Keep CSP policies updated as application evolves

## Next Steps

1. **Apply to Other Services**: Implement these changes in other Express services
2. **Configure Environment Variables**: Set `ALLOWED_ORIGINS` in production environment
3. **Review CSP**: Adjust CSP directives based on actual application needs
4. **Add CSP Reporting**: Implement CSP violation reporting endpoint
5. **Test Thoroughly**: Test CORS behavior in staging before production deployment
