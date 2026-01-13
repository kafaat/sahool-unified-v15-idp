# Inline Script Security Implementation

## Overview

This document describes the security improvements made to the `createInlineScript` function in `/home/user/sahool-unified-v15-idp/apps/web/src/lib/security/nonce.ts` to mitigate XSS vulnerabilities from `dangerouslySetInnerHTML` usage.

## Security Issue Fixed

### Original Vulnerability

The original `createInlineScript` function accepted any string input without validation:

```typescript
// ❌ VULNERABLE: No validation
export function createInlineScript(code: string, nonce: string | null) {
  return {
    ...getNonceProps(nonce),
    dangerouslySetInnerHTML: { __html: code },
  };
}
```

**Risk**: This could allow injection of malicious scripts if untrusted input was passed.

### New Secure Implementation

The updated function now includes comprehensive validation and sanitization:

```typescript
// ✅ SECURE: With validation and sanitization
export function createInlineScript(
  code: string,
  nonce: string | null,
  options?: {
    skipValidation?: boolean;
    allowSanitization?: boolean;
  },
);
```

## Security Features Implemented

### 1. Dangerous Pattern Detection

The function now checks for and blocks dangerous code patterns:

**Direct Code Execution:**

- `eval()`
- `Function()` constructor
- `new Function()`

**Script Injection:**

- `<script>` tags
- `</script>` closing tags
- `javascript:` protocol

**DOM Manipulation:**

- `.innerHTML =`
- `.outerHTML =`
- `document.write()`
- `document.writeln()`

**XSS Vectors:**

- Inline event handlers (`onclick=`, `onerror=`, etc.)
- `<iframe>` tags
- `<embed>` tags
- `<object>` tags

**Dangerous Imports:**

- `data:text/html` URIs
- Dynamic `import()` statements

### 2. Suspicious Pattern Warnings

The function warns about patterns that might be legitimate but require careful review:

- `localStorage` access
- `sessionStorage` access
- `document.cookie` access
- `window.location` manipulation
- `fetch()` calls
- `XMLHttpRequest` usage
- `postMessage()` calls
- Template literals (potential injection points)

### 3. Code Sanitization (Optional)

When `allowSanitization: true` is enabled, the function removes:

- Script tags
- Iframe tags
- Embed tags
- Object tags
- `javascript:` protocols
- `data:` URIs

### 4. Environment-Aware Error Handling

**Production Mode:**

- Throws an error immediately if dangerous patterns detected
- Fails closed (rejects unsafe scripts)

**Development Mode:**

- Logs errors to console
- Allows execution for debugging purposes
- Displays warnings for suspicious patterns

### 5. Comprehensive JSDoc Documentation

Added extensive documentation including:

- Security warnings
- Safe usage examples
- Unsafe usage examples (what NOT to do)
- Parameter descriptions
- Return type information

## Usage Examples

### ✅ SAFE Usage

```typescript
// Static, trusted code
const nonce = await getNonce();

const configScript = `
  window.__APP_CONFIG__ = {
    apiUrl: '/api',
    version: '16.0.0'
  };
`;

<script {...createInlineScript(configScript, nonce)} />
```

### ❌ UNSAFE Usage (Will be blocked)

```typescript
// User input - NEVER DO THIS
const userCode = req.body.code;
<script {...createInlineScript(userCode, nonce)} /> // ❌ DANGEROUS!

// Dynamic untrusted content
const externalCode = await fetch(untrustedUrl).then(r => r.text());
<script {...createInlineScript(externalCode, nonce)} /> // ❌ DANGEROUS!

// Code with dangerous patterns
const maliciousCode = 'eval(userInput)';
<script {...createInlineScript(maliciousCode, nonce)} /> // ❌ BLOCKED!
```

### Advanced Options

**Skip Validation (Not Recommended):**

```typescript
// Only for extremely trusted, static code
<script {...createInlineScript(trustedCode, nonce, { skipValidation: true })} />
```

**Enable Sanitization:**

```typescript
// Attempt to clean code before validation
<script {...createInlineScript(code, nonce, { allowSanitization: true })} />
```

## Validation API

### `validateScriptCode(code: string): ValidationResult`

Standalone validation function that can be used independently:

```typescript
import { validateScriptCode } from "@/lib/security/nonce";

const result = validateScriptCode('console.log("test")');

if (!result.isValid) {
  console.error("Validation errors:", result.errors);
}

if (result.warnings.length > 0) {
  console.warn("Validation warnings:", result.warnings);
}
```

**Return Type:**

```typescript
interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}
```

## Best Practices

### DO:

1. ✅ Use only with static, hardcoded scripts
2. ✅ Prefer external script files when possible
3. ✅ Review validation errors and warnings carefully
4. ✅ Use CSP nonces for all inline scripts
5. ✅ Keep inline scripts minimal
6. ✅ Test scripts in development mode first

### DON'T:

1. ❌ Never pass user input directly
2. ❌ Never pass untrusted external content
3. ❌ Never skip validation unless absolutely necessary
4. ❌ Never ignore validation warnings
5. ❌ Never use inline event handlers
6. ❌ Never use `eval()` or `Function()` constructor

## Migration Guide

If you have existing code using the old `createInlineScript`:

### Before (Potentially Unsafe)

```typescript
const script = createInlineScript(someCode, nonce);
```

### After (With Validation)

```typescript
// Option 1: Let it validate (recommended)
const script = createInlineScript(someCode, nonce);

// Option 2: With sanitization
const script = createInlineScript(someCode, nonce, { allowSanitization: true });

// Option 3: Validate separately first
const validation = validateScriptCode(someCode);
if (validation.isValid) {
  const script = createInlineScript(someCode, nonce);
}
```

## Testing

Comprehensive tests are available in:
`/home/user/sahool-unified-v15-idp/apps/web/src/lib/security/__tests__/nonce-validation.test.ts`

Run tests:

```bash
npm test -- nonce-validation.test.ts
```

## Security Considerations

### Defense in Depth

This validation is **one layer** of security. It should be combined with:

1. **Content Security Policy (CSP)** - Already implemented via nonces
2. **Input Sanitization** - At the API/form level
3. **Output Encoding** - Context-appropriate escaping
4. **Regular Security Audits** - Review inline script usage
5. **Principle of Least Privilege** - Minimize inline script usage

### Limitations

⚠️ **Important**: This validation is NOT foolproof!

- Regex-based validation can potentially be bypassed
- New XSS vectors are discovered regularly
- Sanitization is basic and may not catch all patterns
- Always treat inline scripts as high-risk

**The best defense**: Don't use inline scripts at all. Use external files when possible.

## Monitoring and Logging

### Development Mode

- Warnings logged to console: `[Security Warning] Inline script validation warnings`
- Errors logged to console: `[Security Error] Inline script validation failed`

### Production Mode

- Validation errors throw exceptions
- Monitor error tracking for validation failures
- Review logs for security incidents

## Updates and Maintenance

### Adding New Dangerous Patterns

To add new patterns to the blocklist:

1. Update `DANGEROUS_PATTERNS` array in `nonce.ts`
2. Add test cases in `nonce-validation.test.ts`
3. Document the new pattern in this file
4. Update version and changelog

### Adding New Suspicious Patterns

To add new warning patterns:

1. Update `SUSPICIOUS_PATTERNS` array in `nonce.ts`
2. Add test cases for warnings
3. Document why the pattern is suspicious

## References

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Content Security Policy (CSP) Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [React dangerouslySetInnerHTML Documentation](https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html)

## Version History

### v2.0.0 (2026-01-03)

- ✅ Added comprehensive input validation
- ✅ Added dangerous pattern detection
- ✅ Added suspicious pattern warnings
- ✅ Added optional code sanitization
- ✅ Added environment-aware error handling
- ✅ Added extensive JSDoc documentation
- ✅ Added validation API export
- ✅ Added comprehensive test suite
- ✅ Updated security documentation

### v1.0.0 (Previous)

- Basic nonce support
- No validation
