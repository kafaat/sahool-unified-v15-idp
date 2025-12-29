/**
 * Content Security Policy Utilities
 * أدوات سياسة أمان المحتوى
 *
 * Utilities for working with CSP nonces in components
 */

import { headers } from 'next/headers';

/**
 * Get the CSP nonce from request headers
 * This nonce should be used for inline scripts and styles to comply with CSP
 *
 * Usage in Server Components:
 * ```tsx
 * import { getCSPNonce } from '@/lib/security/csp';
 *
 * export default async function MyComponent() {
 *   const nonce = await getCSPNonce();
 *
 *   return (
 *     <div>
 *       <script nonce={nonce}>
 *         // Your inline script
 *       </script>
 *       <style nonce={nonce}>
 *         // Your inline styles
 *       </style>
 *     </div>
 *   );
 * }
 * ```
 *
 * @returns The CSP nonce value or undefined if not available
 */
export async function getCSPNonce(): Promise<string | undefined> {
  try {
    const headersList = await headers();
    return headersList.get('X-CSP-Nonce') || undefined;
  } catch (error) {
    // headers() can only be called in Server Components
    console.warn('getCSPNonce: Unable to access headers. This function must be called in a Server Component.');
    return undefined;
  }
}

/**
 * Get nonce attribute for inline scripts/styles
 *
 * Usage:
 * ```tsx
 * <script {...(await getNonceAttribute())}>
 *   // Your code
 * </script>
 * ```
 */
export async function getNonceAttribute(): Promise<{ nonce?: string }> {
  const nonce = await getCSPNonce();
  return nonce ? { nonce } : {};
}

/**
 * Best Practices for CSP Compliance:
 *
 * 1. Use External Files:
 *    - Prefer external .js and .css files over inline scripts/styles
 *    - External files don't require nonces
 *
 * 2. For Inline Scripts:
 *    - Always use the nonce attribute: <script nonce={nonce}>
 *    - Avoid event handlers in HTML: Use addEventListener instead
 *    - Bad:  <button onclick="handleClick()">
 *    - Good: <button id="myButton"> + document.getElementById('myButton').addEventListener('click', handleClick)
 *
 * 3. For Inline Styles:
 *    - Use CSS modules or styled-components when possible
 *    - If inline styles are needed, use nonce: <style nonce={nonce}>
 *    - For inline style attributes, consider using CSS-in-JS libraries
 *
 * 4. For Third-Party Scripts:
 *    - Add trusted domains to CSP configuration in middleware.ts
 *    - Use SRI (Subresource Integrity) for CDN resources
 *
 * 5. Development vs Production:
 *    - Development allows 'unsafe-eval' for Next.js hot reload
 *    - Production uses strict CSP without 'unsafe-eval' or 'unsafe-inline'
 *
 * 6. Testing:
 *    - Check browser console for CSP violations
 *    - Review CSP reports at /api/csp-report
 *    - Test in production mode before deploying
 */
