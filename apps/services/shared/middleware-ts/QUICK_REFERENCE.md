# Security Middleware - Quick Reference

## Import

```typescript
import {
    securityHeaders,
    removeSensitiveHeaders,
    createSecureCorsOptions,
    secureCors,
    corsWithServerSupport,
    customCSP
} from "../../shared/middleware-ts";
import cors from "cors";
```

## Basic Setup (Most Common)

```typescript
const app = express();

// 1. Remove sensitive headers
app.use(removeSensitiveHeaders);

// 2. Configure CORS
app.use(cors(createSecureCorsOptions()));

// 3. Add security headers
app.use(securityHeaders);

// 4. Standard middleware
app.use(express.json());
```

## CORS Options

### Option 1: Default Secure CORS (Recommended)
```typescript
app.use(cors(createSecureCorsOptions()));
```
- Rejects requests without Origin in production
- Uses environment variable `ALLOWED_ORIGINS`
- Falls back to default allowed origins

### Option 2: Allow Server-to-Server Requests
```typescript
app.use(cors(createSecureCorsOptions({ allowNoOrigin: true })));
```
- Allows requests without Origin header (even in production)
- Use for APIs consumed by other services

### Option 3: Custom Origins
```typescript
app.use(cors(createSecureCorsOptions({
    additionalOrigins: ['https://partner.example.com']
})));
```

### Option 4: Custom Headers/Methods
```typescript
app.use(cors(createSecureCorsOptions({
    methods: ['GET', 'POST', 'PUT'],
    allowedHeaders: ['Content-Type', 'X-Custom-Header']
})));
```

### Option 5: Pre-configured Middleware
```typescript
import { secureCors, corsWithServerSupport } from "../../shared/middleware-ts";

app.use(secureCors);  // Strict CORS
// OR
app.use(corsWithServerSupport);  // Allows no-origin requests
```

## Custom CSP for Specific Routes

```typescript
import { customCSP } from "../../shared/middleware-ts";

// Allow images from CDN for upload endpoint
app.use('/api/upload', customCSP({
    'img-src': "'self' https://cdn.sahool.app data:",
    'connect-src': "'self' https://api.sahool.app"
}));
```

## Environment Variables

```bash
# .env file
NODE_ENV=production
ALLOWED_ORIGINS=https://sahool.app,https://admin.sahool.app,https://custom.domain.com
```

## Security Headers Applied

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevents MIME sniffing |
| X-Frame-Options | DENY | Prevents clickjacking |
| X-XSS-Protection | 1; mode=block | XSS protection (legacy browsers) |
| Strict-Transport-Security | max-age=31536000; includeSubDomains | Forces HTTPS (production only) |
| Content-Security-Policy | (multiple directives) | Prevents XSS and injection attacks |
| Referrer-Policy | strict-origin-when-cross-origin | Controls referrer information |
| Permissions-Policy | (multiple policies) | Disables dangerous browser features |

## Testing

### Test CORS
```bash
# Development - should work
curl -X GET http://localhost:3000/api/v1/fields

# Production - should be rejected (no Origin header)
curl -X GET https://api.sahool.app/api/v1/fields

# Production - should work (with valid Origin)
curl -X GET https://api.sahool.app/api/v1/fields \
  -H "Origin: https://sahool.app"
```

### Check Security Headers
```bash
curl -I http://localhost:3000/api/v1/fields | grep -E "(X-|Content-Security|Strict-Transport)"
```

## Common Issues

### Issue: CORS blocking legitimate requests
**Solution**: Add origin to `ALLOWED_ORIGINS` environment variable
```bash
ALLOWED_ORIGINS=https://sahool.app,https://new-domain.com
```

### Issue: CSP blocking inline scripts
**Solution**: Add route-specific CSP
```typescript
app.use('/specific-route', customCSP({
    'script-src': "'self' 'unsafe-inline'"
}));
```

### Issue: Need to allow server-to-server requests
**Solution**: Use `allowNoOrigin: true`
```typescript
app.use(cors(createSecureCorsOptions({ allowNoOrigin: true })));
```

## Middleware Order Matters!

```typescript
// ✅ CORRECT ORDER
app.use(removeSensitiveHeaders);  // 1. Remove server info
app.use(cors(corsOptions));       // 2. Handle CORS
app.use(securityHeaders);         // 3. Add security headers
app.use(express.json());          // 4. Parse JSON
app.use(otherMiddleware);         // 5. Other middleware

// ❌ WRONG ORDER - Don't do this
app.use(express.json());
app.use(securityHeaders);
app.use(cors(corsOptions));
```

## Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Configure `ALLOWED_ORIGINS` with actual domains
- [ ] Test CORS with actual frontend domains
- [ ] Verify security headers with https://securityheaders.com
- [ ] Test that requests without Origin are rejected
- [ ] Monitor logs for blocked CORS requests
- [ ] Review and adjust CSP if needed

## Support

For questions or issues:
1. Check the detailed [README.md](./README.md)
2. Review [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
3. Consult [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
