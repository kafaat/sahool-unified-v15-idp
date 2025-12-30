# Sahool Express Middleware

Shared Express middleware for Sahool services, providing security headers and CORS configuration following OWASP best practices.

## Features

### Security Headers

Implements comprehensive security headers to protect against common web vulnerabilities:

- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables browser XSS protection
- **Strict-Transport-Security**: Enforces HTTPS connections (production only)
- **Content-Security-Policy**: Prevents XSS, data injection, and other attacks
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Disables dangerous browser features

### CORS Configuration

Strict CORS implementation that:

- Rejects requests without Origin header in production
- Only allows specific origins from environment variable
- Supports credentials (cookies, authorization headers)
- Allows specific HTTP methods and headers

## Installation

This is a local package within the monorepo. Services can import it directly:

```typescript
import { securityHeaders, secureCors } from '../shared/middleware-ts';
```

## Usage

### Basic Security Headers

```typescript
import express from 'express';
import { securityHeaders } from '../shared/middleware-ts';

const app = express();

// Apply security headers to all routes
app.use(securityHeaders);
```

### CORS Configuration

#### Option 1: Use default secure CORS

```typescript
import { secureCors } from '../shared/middleware-ts';

app.use(secureCors);
```

#### Option 2: Use environment variable for origins

Set `ALLOWED_ORIGINS` environment variable:

```bash
ALLOWED_ORIGINS=https://sahool.app,https://admin.sahool.app
```

#### Option 3: Custom CORS configuration

```typescript
import { createSecureCorsOptions } from '../shared/middleware-ts';
import cors from 'cors';

app.use(cors(createSecureCorsOptions({
  additionalOrigins: ['https://custom.example.com'],
  allowNoOrigin: false  // Reject requests without Origin in production
})));
```

#### Option 4: Allow server-to-server requests

```typescript
import { corsWithServerSupport } from '../shared/middleware-ts';

// This allows requests without Origin header (for API-to-API calls)
app.use(corsWithServerSupport);
```

### Custom CSP for Specific Routes

```typescript
import { customCSP } from '../shared/middleware-ts';

// Allow images from CDN for upload endpoint
app.use('/api/upload', customCSP({
  'img-src': "'self' https://cdn.sahool.app data:",
  'connect-src': "'self' https://api.sahool.app"
}));
```

### Remove Sensitive Headers

```typescript
import { removeSensitiveHeaders } from '../shared/middleware-ts';

// Remove X-Powered-By and Server headers
app.use(removeSensitiveHeaders);
```

## Complete Example

```typescript
import express from 'express';
import {
  securityHeaders,
  secureCors,
  removeSensitiveHeaders
} from '../shared/middleware-ts';

const app = express();

// Apply middleware in order
app.use(removeSensitiveHeaders);
app.use(secureCors);
app.use(securityHeaders);
app.use(express.json());

// Your routes here
app.get('/api/data', (req, res) => {
  res.json({ message: 'Secure endpoint' });
});

app.listen(3000, () => {
  console.log('Server running with security headers and CORS');
});
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ALLOWED_ORIGINS` | Comma-separated list of allowed origins | `https://sahool.app,https://admin.sahool.app` |
| `NODE_ENV` | Environment (affects HSTS and CSP) | `production` or `development` |

## Security Considerations

### Production vs Development

- In **production**:
  - HSTS is enabled
  - Requests without Origin header are rejected (unless using `corsWithServerSupport`)
  - Only production origins are allowed

- In **development**:
  - HSTS is disabled (to avoid issues with local HTTP)
  - Requests without Origin header are allowed
  - Localhost origins are allowed

### CORS Best Practices

1. **Never use `origin: '*'` in production**
2. **Always specify exact origins** - avoid wildcards
3. **Set credentials: true** only when needed
4. **Validate Origin header** - reject requests without it in production
5. **Use environment variables** for origin configuration

### CSP Best Practices

1. **Avoid 'unsafe-inline'** when possible - use nonces or hashes instead
2. **Start strict** and relax only when necessary
3. **Test thoroughly** - CSP can break functionality if too restrictive
4. **Monitor CSP violations** in production

## References

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Content Security Policy Reference](https://content-security-policy.com/)
