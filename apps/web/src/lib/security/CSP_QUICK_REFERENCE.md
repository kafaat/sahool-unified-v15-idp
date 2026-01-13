# CSP Quick Reference Card

## TL;DR

### What Changed?

- ✅ **Strict CSP** with nonce-based scripts/styles
- ✅ **No more `'unsafe-inline'`** in production
- ✅ **CSP violation reporting** at `/api/csp-report`

### For Developers

#### ❌ Don't Do This (CSP violations)

```jsx
// Inline event handlers
<button onclick="handleClick()">Click</button>

// Inline styles
<div style={{ color: 'red' }}>Text</div>

// javascript: URLs
<a href="javascript:void(0)">Link</a>

// eval() or Function()
eval('code');
new Function('code')();
```

#### ✅ Do This Instead

```jsx
// React event handlers
<button onClick={handleClick}>Click</button>

// CSS classes (Tailwind)
<div className="text-red-600">Text</div>

// Buttons instead of links
<button onClick={handleAction}>Link</button>

// Proper functions
const fn = () => code();
```

## Common Scenarios

### 1. Need Inline Script (Server Component)

```tsx
import { getNonce, createInlineScript } from "@/lib/security/nonce";

export default async function Page() {
  const nonce = await getNonce();
  return <script {...createInlineScript(`console.log('hi')`, nonce)} />;
}
```

### 2. Need Dynamic Styles

```tsx
// Use CSS custom properties
<div
  className="dynamic-box"
  style={{ "--bg-color": color } as React.CSSProperties}
>
  Content
</div>

// In CSS: .dynamic-box { background: var(--bg-color); }
```

### 3. Loading External Script

```tsx
import Script from "next/script";

<Script src="https://example.com/script.js" strategy="lazyOnload" />;
```

### 4. Need to Add External Resource

```typescript
// Edit: /apps/web/src/lib/security/csp-config.ts

'script-src': [
  // ...existing
  'https://trusted-domain.com',  // Add here
],
```

## Testing CSP

```bash
# Development
npm run dev

# Report-only mode (reports but doesn't block)
CSP_REPORT_ONLY=true npm run dev

# Production build
npm run build
npm start
```

## Check Violations

1. **Browser Console**: Look for CSP violation messages
2. **Network Tab**: Check for blocked resources
3. **Server Logs**: Check `/api/csp-report` endpoint

## Quick Fixes

### "Refused to execute inline script"

**Solution**: Use `createInlineScript()` with nonce

### "Refused to apply inline style"

**Solution**: Use CSS classes or custom properties

### "Refused to load script from X"

**Solution**: Add domain to CSP config or use `next/script`

### "Refused to connect to X"

**Solution**: Add domain to `connect-src` in CSP config

## File Locations

```
/apps/web/src/lib/security/
├── csp-config.ts        # CSP configuration
├── nonce.ts             # Nonce utilities
├── index.ts             # Main exports
├── csp-example.tsx      # Usage examples
├── CSP_README.md        # Full documentation
├── CSP_MIGRATION.md     # Migration guide
└── CSP_QUICK_REFERENCE.md  # This file

/apps/web/src/app/api/
└── csp-report/
    └── route.ts         # Violation reporting

/apps/web/
├── middleware.ts        # CSP headers applied here
└── next.config.js       # Additional security headers
```

## CSP Header (Production)

```
default-src 'self';
script-src 'self' 'nonce-{random}' 'strict-dynamic';
style-src 'self' 'nonce-{random}' https://fonts.googleapis.com;
img-src 'self' data: https:;
font-src 'self' data: https://fonts.gstatic.com;
connect-src 'self' {API_URLS};
object-src 'none';
frame-ancestors 'none';
form-action 'self';
base-uri 'self';
upgrade-insecure-requests;
block-all-mixed-content;
report-uri /api/csp-report;
```

## Best Practices

1. ✅ Use CSS classes instead of inline styles
2. ✅ Use `next/script` for external scripts
3. ✅ Use React event handlers instead of inline
4. ✅ Test in report-only mode first
5. ✅ Check browser console for violations

## Need Help?

1. Check [CSP_README.md](./CSP_README.md) for detailed docs
2. See [csp-example.tsx](./csp-example.tsx) for code examples
3. Read [CSP_MIGRATION.md](./CSP_MIGRATION.md) for migration help
4. Visit [MDN CSP Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

## Environment Differences

| Feature                  | Development      | Production   |
| ------------------------ | ---------------- | ------------ |
| `'unsafe-eval'`          | ✅ Allowed (HMR) | ❌ Blocked   |
| `'unsafe-inline'` styles | ✅ Allowed       | ❌ Blocked   |
| Localhost                | ✅ Allowed       | ❌ Blocked   |
| HTTPS enforcement        | ❌ Optional      | ✅ Required  |
| Report-only mode         | ⚙️ Configurable  | ❌ Enforcing |

## One-Liners

```bash
# Enable CSP report-only mode
CSP_REPORT_ONLY=true npm run dev

# Check CSP header
curl -I https://sahool.ye | grep -i "content-security"

# Run CSP tests
npm test src/lib/security/csp-config.test.ts

# Validate CSP online
# Visit: https://csp-evaluator.withgoogle.com/
```

---

**Quick Start**: Read [CSP_README.md](./CSP_README.md) for full documentation.
