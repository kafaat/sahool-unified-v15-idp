# Content Security Policy (CSP) Implementation

## Overview

This implementation provides a robust Content Security Policy for the SAHOOL web dashboard with the following features:

- **Nonce-based script and style directives** - Eliminates need for `unsafe-inline` in production
- **Environment-aware configuration** - Different policies for development and production
- **CSP violation reporting** - Monitors and logs policy violations
- **Easy integration** - Simple utilities for React components

## Security Improvements

### Before

```
script-src 'self' 'unsafe-inline' 'unsafe-eval'
style-src 'self' 'unsafe-inline'
```

### After (Production)

```
script-src 'self' 'nonce-{random}' 'strict-dynamic'
style-src 'self' 'nonce-{random}' https://fonts.googleapis.com
```

### After (Development)

```
script-src 'self' 'nonce-{random}' 'unsafe-eval'  # Only for HMR
style-src 'self' 'nonce-{random}' https://fonts.googleapis.com
```

## Files Created/Modified

### New Files

1. `/src/lib/security/csp-config.ts` - CSP configuration and nonce generation
2. `/src/lib/security/nonce.ts` - Nonce utilities for React components
3. `/src/app/api/csp-report/route.ts` - CSP violation reporting endpoint

### Modified Files

1. `/src/middleware.ts` - Updated to use new CSP with nonce support
2. `/next.config.js` - Enhanced security headers

## Usage Guide

### 1. Server Components with Inline Scripts

```tsx
import { getNonce, createInlineScript } from "@/lib/security/nonce";

export default async function MyComponent() {
  const nonce = await getNonce();

  return (
    <>
      <div id="map"></div>
      <script
        {...createInlineScript(`console.log('Initializing map...');`, nonce)}
      />
    </>
  );
}
```

### 2. Server Components with Inline Styles

```tsx
import { getNonce, createInlineStyle } from "@/lib/security/nonce";

export default async function MyComponent() {
  const nonce = await getNonce();

  return (
    <>
      <div className="custom-styled">Content</div>
      <style {...createInlineStyle(`.custom-styled { color: red; }`, nonce)} />
    </>
  );
}
```

### 3. Using CSS Variables (Recommended)

Instead of inline styles, use CSS custom properties:

```tsx
// ❌ Bad (blocked by CSP)
<div style={{ color: 'red', fontSize: '16px' }}>Text</div>

// ✅ Good (CSP-safe)
<div
  className="dynamic-style"
  style={{ '--color': 'red', '--size': '16px' } as React.CSSProperties}
>
  Text
</div>

// Add to your CSS
.dynamic-style {
  color: var(--color);
  font-size: var(--size);
}
```

### 4. External Scripts

For third-party scripts, add them to the CSP configuration:

```typescript
// In /src/lib/security/csp-config.ts
'script-src': [
  "'self'",
  `'nonce-${nonce}'`,
  'https://trusted-cdn.com',  // Add trusted sources
],
```

### 5. Loading External Resources

Images, fonts, and other resources are already configured. To add new sources:

```typescript
// In /src/lib/security/csp-config.ts
'img-src': [
  "'self'",
  'data:',
  'https://your-cdn.com',  // Add your CDN
],
```

## CSP Violation Reporting

### Monitoring Violations

CSP violations are automatically reported to `/api/csp-report` and logged:

```json
{
  "timestamp": "2025-12-30T...",
  "documentUri": "https://sahool.ye/dashboard",
  "violatedDirective": "script-src",
  "blockedUri": "https://malicious-script.com/evil.js",
  "sourceFile": "https://sahool.ye/page.html",
  "lineNumber": 42
}
```

### Viewing Violations

In development:

```bash
# Check console output
npm run dev
```

In production:

```bash
# Check container logs
docker logs sahool-web

# Or check your logging service (Sentry, LogRocket, etc.)
```

## Environment Configuration

### Development Mode

- Allows `unsafe-eval` for Next.js Hot Module Replacement (HMR)
- Allows `unsafe-inline` for faster iteration
- Allows localhost connections for API and WebSocket
- Can use report-only mode by setting `CSP_REPORT_ONLY=true`

### Production Mode

- Strict nonce-based policy
- No `unsafe-inline` or `unsafe-eval` (except Next.js internals)
- Enforces HTTPS with `upgrade-insecure-requests`
- Blocks mixed content
- Uses `strict-dynamic` for better security

## Testing CSP

### 1. Test in Report-Only Mode

```bash
# In development
CSP_REPORT_ONLY=true npm run dev
```

This will report violations without blocking resources.

### 2. Check Browser Console

Open DevTools Console to see CSP violations:

```
Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self' 'nonce-...'".
```

### 3. Verify Headers

```bash
# Check CSP headers
curl -I https://sahool.ye/dashboard
```

## Common Issues and Solutions

### Issue: Next.js Scripts Blocked

**Solution**: This is handled automatically. Next.js internal scripts use the nonce.

### Issue: Third-party Library Uses Inline Styles

**Solution 1**: Move styles to external CSS file
**Solution 2**: Use CSS custom properties
**Solution 3**: Add the library's domain to `style-src` (less secure)

### Issue: Google Maps/Leaflet Not Working

**Solution**: Ensure map provider domains are in CSP config:

```typescript
'img-src': [
  'https://tile.openstreetmap.org',
  'https://*.tile.openstreetmap.org',
],
'connect-src': [
  'https://tile.openstreetmap.org',
],
```

### Issue: WebSocket Connection Blocked

**Solution**: Add WebSocket URLs to `connect-src`:

```typescript
'connect-src': [
  "'self'",
  'ws://localhost:*',  // Development
  'wss://api.sahool.ye',  // Production
],
```

## Best Practices

1. **Avoid Inline Scripts**: Use external files or nonce-based inline scripts
2. **Avoid Inline Styles**: Use CSS files or CSS custom properties
3. **Use Strict CSP**: Don't add `unsafe-inline` or `unsafe-eval` to production
4. **Monitor Violations**: Regularly check CSP reports
5. **Test Thoroughly**: Test all features after CSP changes
6. **Whitelist Carefully**: Only add trusted sources to CSP

## Next.js Specific Considerations

### Server Components (Recommended)

Server Components can use the nonce utilities directly:

```tsx
import { getNonce } from "@/lib/security/nonce";

export default async function Page() {
  const nonce = await getNonce();
  // Use nonce...
}
```

### Client Components

Client components should avoid inline scripts. Use:

- External script files
- `next/script` component
- CSS modules for styles

### Dynamic Routes

CSP nonce is generated per request, so it works automatically with dynamic routes.

## Security Checklist

- [x] Remove `unsafe-inline` from production CSP
- [x] Remove `unsafe-eval` from production CSP (except Next.js dev)
- [x] Implement nonce-based script/style loading
- [x] Add CSP violation reporting
- [x] Set `frame-ancestors 'none'` to prevent clickjacking
- [x] Set `upgrade-insecure-requests` in production
- [x] Set `block-all-mixed-content` in production
- [x] Use `strict-dynamic` with nonces
- [x] Whitelist only necessary external sources
- [x] Configure CORS headers properly
- [x] Add Cross-Origin-\* headers

## Resources

- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Evaluator](https://csp-evaluator.withgoogle.com/)
- [Next.js Security Headers](https://nextjs.org/docs/advanced-features/security-headers)
- [OWASP CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

## Support

For issues or questions about CSP implementation:

1. Check browser console for CSP violations
2. Review `/api/csp-report` logs
3. Test with `CSP_REPORT_ONLY=true` first
4. Consult the resources above
