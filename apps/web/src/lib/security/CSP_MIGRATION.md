# CSP Migration Guide

## Overview

This guide helps you migrate existing code to be compatible with the new strict Content Security Policy (CSP).

## Quick Reference

| Old Pattern (CSP-unsafe) | New Pattern (CSP-safe) |
|--------------------------|------------------------|
| `<div onClick="handler()">` | `<div onClick={handler}>` |
| `<a href="javascript:void(0)">` | `<button onClick={handler}>` |
| `<div style={{ color: 'red' }}>` | `<div className="text-red-600">` |
| `<script>inline code</script>` | `<script {...createInlineScript(code, nonce)} />` |
| `eval('code')` | Use proper function calls |
| `new Function('code')` | Use proper function declarations |

## Common Migration Scenarios

### 1. Inline Event Handlers

#### ❌ Before (Blocked by CSP)
```jsx
<button onclick="handleClick()">Click</button>
<div onmouseover="showTooltip()">Hover</div>
<a href="javascript:deleteItem(123)">Delete</a>
```

#### ✅ After (CSP-compliant)
```jsx
<button onClick={handleClick}>Click</button>
<div onMouseOver={showTooltip}>Hover</div>
<button onClick={() => deleteItem(123)}>Delete</button>
```

### 2. Inline Styles

#### ❌ Before (Blocked by CSP in production)
```jsx
<div style={{ backgroundColor: dynamicColor, padding: '10px' }}>
  Content
</div>
```

#### ✅ After - Option 1: Tailwind Classes
```jsx
<div className={`bg-${colorClass} p-4`}>
  Content
</div>
```

#### ✅ After - Option 2: CSS Custom Properties
```jsx
<div
  className="dynamic-box"
  style={{ '--bg-color': dynamicColor } as React.CSSProperties}
>
  Content
</div>

// In your CSS:
// .dynamic-box {
//   background-color: var(--bg-color);
//   padding: 10px;
// }
```

#### ✅ After - Option 3: CSS Modules
```jsx
import styles from './Component.module.css';

<div className={styles.dynamicBox}>
  Content
</div>
```

### 3. Inline Scripts

#### ❌ Before (Blocked by CSP)
```jsx
export default function Page() {
  return (
    <>
      <div id="map"></div>
      <script>
        initializeMap();
      </script>
    </>
  );
}
```

#### ✅ After - Option 1: External Script File
```jsx
import Script from 'next/script';

export default function Page() {
  return (
    <>
      <div id="map"></div>
      <Script src="/scripts/map-init.js" />
    </>
  );
}
```

#### ✅ After - Option 2: Inline with Nonce (Server Component)
```jsx
import { getNonce, createInlineScript } from '@/lib/security/nonce';

export default async function Page() {
  const nonce = await getNonce();

  const mapScript = `
    initializeMap();
  `;

  return (
    <>
      <div id="map"></div>
      <script {...createInlineScript(mapScript, nonce)} />
    </>
  );
}
```

#### ✅ After - Option 3: Use useEffect (Client Component)
```jsx
'use client';

import { useEffect } from 'react';

export default function Page() {
  useEffect(() => {
    initializeMap();
  }, []);

  return <div id="map"></div>;
}
```

### 4. Dynamic Script Injection

#### ❌ Before (Blocked by CSP)
```javascript
const script = document.createElement('script');
script.src = 'https://example.com/analytics.js';
document.head.appendChild(script);
```

#### ✅ After - Option 1: next/script
```jsx
import Script from 'next/script';

<Script src="https://example.com/analytics.js" strategy="lazyOnload" />
```

#### ✅ After - Option 2: Add to CSP allowed sources
```typescript
// In csp-config.ts
'script-src': [
  "'self'",
  `'nonce-${nonce}'`,
  'https://example.com',  // Add trusted source
],
```

### 5. eval() and new Function()

#### ❌ Before (Blocked by CSP in production)
```javascript
eval('console.log("Hello")');
const fn = new Function('return 1 + 1');
```

#### ✅ After - Refactor to regular code
```javascript
console.log("Hello");
const fn = () => 1 + 1;
```

### 6. javascript: URLs

#### ❌ Before (Blocked by CSP)
```jsx
<a href="javascript:void(0)" onClick={handler}>Link</a>
<a href="javascript:openModal()">Open</a>
```

#### ✅ After
```jsx
<button onClick={handler}>Link</button>
<button onClick={openModal}>Open</button>
```

### 7. Data URIs in Script/Style

#### ❌ Before (May be blocked)
```jsx
<img src="data:image/png;base64,..." />  // OK for images
<script src="data:text/javascript,alert('hi')"></script>  // Blocked
```

#### ✅ After
```jsx
<img src="data:image/png;base64,..." />  // Still OK
<Script src="/scripts/alert.js" />  // Use file
```

### 8. Third-party Libraries

#### ❌ Before - Library with inline scripts
```jsx
import SomeLibrary from 'some-library';

<SomeLibrary
  onInit={() => {
    // This library injects inline scripts
  }}
/>
```

#### ✅ After - Solutions:
1. **Update library** to CSP-compliant version
2. **Add nonce support** if library supports it:
   ```jsx
   import { getNonce } from '@/lib/security/nonce';

   const nonce = await getNonce();
   <SomeLibrary nonce={nonce} />
   ```
3. **Replace library** with CSP-friendly alternative
4. **Load library differently**:
   ```jsx
   import Script from 'next/script';

   <Script src="/libs/some-library.js" />
   ```

### 9. Google Analytics / Tag Manager

#### ❌ Before (Traditional inline script)
```html
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

#### ✅ After - Using next/script with nonce
```jsx
import Script from 'next/script';
import { getNonce } from '@/lib/security/nonce';

export default async function Analytics() {
  const nonce = await getNonce();

  return (
    <>
      <Script
        src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'GA_MEASUREMENT_ID');
        `}
      </Script>
    </>
  );
}
```

And add Google domains to CSP:
```typescript
// In csp-config.ts
'script-src': [
  // ...
  'https://www.googletagmanager.com',
  'https://www.google-analytics.com',
],
'connect-src': [
  // ...
  'https://www.google-analytics.com',
],
```

### 10. Leaflet/OpenStreetMap

#### ❌ Before - May have issues
```jsx
import L from 'leaflet';

useEffect(() => {
  const map = L.map('map').setView([15.5527, 48.5164], 6);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
}, []);
```

#### ✅ After - Already configured in CSP
The CSP configuration already includes OpenStreetMap domains. Just ensure you're loading Leaflet CSS in the head:

```jsx
// In app/layout.tsx
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
  crossOrigin=""
/>
```

### 11. WebSocket Connections

#### ❌ Before - May be blocked
```javascript
const ws = new WebSocket('ws://unknown-domain.com/socket');
```

#### ✅ After - Add to CSP connect-src
```typescript
// In csp-config.ts
'connect-src': [
  "'self'",
  'ws://localhost:*',  // Development
  'wss://your-domain.com',  // Production
],
```

### 12. Form Actions

#### ❌ Before - External form submission
```jsx
<form action="https://external-site.com/submit" method="POST">
  <input type="text" />
  <button type="submit">Submit</button>
</form>
```

#### ✅ After - Option 1: Submit via API
```jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  await fetch('/api/submit', {
    method: 'POST',
    body: formData
  });
};

<form onSubmit={handleSubmit}>
  <input type="text" />
  <button type="submit">Submit</button>
</form>
```

#### ✅ After - Option 2: Add to CSP
```typescript
// In csp-config.ts
'form-action': [
  "'self'",
  'https://trusted-external-site.com',
],
```

## Environment-Specific Considerations

### Development

In development, the CSP is more lenient:
- ✅ `unsafe-eval` is allowed (needed for Next.js HMR)
- ✅ `unsafe-inline` in styles is allowed
- ✅ Localhost connections are allowed

### Production

In production, the CSP is strict:
- ❌ No `unsafe-eval` (except Next.js internals)
- ❌ No `unsafe-inline` without nonce
- ✅ HTTPS enforcement via `upgrade-insecure-requests`
- ✅ Mixed content blocked
- ✅ `strict-dynamic` enabled with nonces

## Testing Your Changes

### 1. Test in Development
```bash
npm run dev
```

Check browser console for CSP violations.

### 2. Test with Report-Only Mode
```bash
CSP_REPORT_ONLY=true npm run dev
```

This reports violations without blocking them.

### 3. Check CSP Reports
```bash
# Monitor the CSP report endpoint
tail -f logs/csp-violations.log

# Or check browser Network tab for POST to /api/csp-report
```

### 4. Test in Production Mode
```bash
npm run build
npm start
```

Test all features to ensure nothing is broken.

## Tools and Resources

### Browser DevTools

1. **Console** - Shows CSP violation messages
2. **Network** - Shows blocked resources
3. **Application > Storage** - Check cookies and localStorage

### CSP Validators

- [CSP Evaluator](https://csp-evaluator.withgoogle.com/) - Validate your CSP
- [Report URI CSP Builder](https://report-uri.com/home/generate) - Build CSP policies

### Browser Extensions

- **CSP Mitigator** - Test CSP policies
- **Security Headers** - Check security headers

## Common Errors and Solutions

### Error: "Refused to execute inline script"

**Cause**: Inline script without nonce

**Solution**:
```jsx
import { getNonce, createInlineScript } from '@/lib/security/nonce';

const nonce = await getNonce();
<script {...createInlineScript(code, nonce)} />
```

### Error: "Refused to apply inline style"

**Cause**: Inline style attribute without nonce

**Solution**: Use CSS classes or CSS custom properties instead

### Error: "Refused to load script from..."

**Cause**: External script not in CSP allowlist

**Solution**: Add domain to CSP config:
```typescript
'script-src': ['...', 'https://trusted-domain.com'],
```

### Error: "Refused to connect to..."

**Cause**: API/WebSocket not in connect-src

**Solution**: Add to CSP config:
```typescript
'connect-src': ['...', 'https://api.example.com'],
```

## Rollback Plan

If CSP causes issues in production:

### 1. Temporary - Use Report-Only Mode
```typescript
// In csp-config.ts
reportOnly: true  // Reports violations but doesn't block
```

### 2. Relax Specific Directive
```typescript
// Temporarily add back unsafe-inline for debugging
'script-src': ['...', "'unsafe-inline'"],  // NOT recommended for production
```

### 3. Complete Rollback
```bash
git revert <csp-commit-hash>
```

## Gradual Migration Strategy

1. **Week 1**: Enable CSP in report-only mode
   - Monitor violations
   - Identify problematic code

2. **Week 2**: Fix high-priority violations
   - Inline event handlers
   - Critical scripts

3. **Week 3**: Fix remaining violations
   - Styles
   - Third-party integrations

4. **Week 4**: Enable enforcing mode
   - Deploy to production
   - Monitor closely

## Questions?

- Check the [CSP_README.md](./CSP_README.md) for usage examples
- Review [csp-example.tsx](./csp-example.tsx) for code samples
- Consult [MDN CSP Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
