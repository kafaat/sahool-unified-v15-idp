/**
 * CSRF Server-Side Validation
 * التحقق من رمز CSRF من جانب الخادم
 *
 * Server-side CSRF token validation for Next.js middleware
 * Used to protect against Cross-Site Request Forgery attacks
 */

import type { NextRequest } from 'next/server';

/**
 * Timing-safe string comparison for Edge Runtime
 * Compares two strings in constant time to prevent timing attacks
 */
function timingSafeCompare(a: string, b: string): boolean {
  if (a.length !== b.length) {
    return false;
  }

  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

/**
 * State-changing HTTP methods that require CSRF protection
 */
export const CSRF_PROTECTED_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH'] as const;

/**
 * CSRF configuration
 */
export interface CsrfConfig {
  /**
   * Cookie name for CSRF token (default: 'csrf_token')
   */
  cookieName?: string;

  /**
   * Header name for CSRF token (default: 'x-csrf-token')
   */
  headerName?: string;

  /**
   * Paths to exclude from CSRF validation
   */
  excludePaths?: string[];
}

/**
 * Default CSRF configuration
 */
const DEFAULT_CONFIG: Required<CsrfConfig> = {
  cookieName: 'csrf_token',
  headerName: 'x-csrf-token',
  excludePaths: [
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/logout',
    '/api/webhooks',
  ],
};

/**
 * Validate CSRF token using timing-safe comparison
 *
 * @param cookieToken - Token from cookie
 * @param headerToken - Token from request header
 * @returns True if tokens match, false otherwise
 */
export function validateCsrfToken(
  cookieToken: string | undefined,
  headerToken: string | undefined
): boolean {
  // Both tokens must be present
  if (!cookieToken || !headerToken) {
    return false;
  }

  // Tokens must have the same length
  if (cookieToken.length !== headerToken.length) {
    return false;
  }

  try {
    // Use timing-safe comparison to prevent timing attacks
    // This implementation works in Edge Runtime (no Node.js crypto dependency)
    return timingSafeCompare(cookieToken, headerToken);
  } catch (error) {
    // If comparison fails (e.g., encoding issues), reject the request
    return false;
  }
}

/**
 * Check if request requires CSRF validation
 *
 * @param request - Next.js request object
 * @param config - CSRF configuration
 * @returns True if request requires CSRF validation
 */
export function requiresCsrfValidation(
  request: NextRequest,
  config: CsrfConfig = {}
): boolean {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };
  const method = request.method;
  const pathname = request.nextUrl.pathname;

  // Only validate state-changing methods
  if (!CSRF_PROTECTED_METHODS.includes(method as typeof CSRF_PROTECTED_METHODS[number])) {
    return false;
  }

  // Exclude specific paths (e.g., auth endpoints)
  if (mergedConfig.excludePaths.some(path => pathname.startsWith(path))) {
    return false;
  }

  return true;
}

/**
 * Validate CSRF token from request
 *
 * @param request - Next.js request object
 * @param config - CSRF configuration
 * @returns Validation result with error details
 */
export function validateCsrfRequest(
  request: NextRequest,
  config: CsrfConfig = {}
): { valid: boolean; error?: string } {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  // Check if request requires CSRF validation
  if (!requiresCsrfValidation(request, config)) {
    return { valid: true };
  }

  // Get CSRF token from cookie
  const cookieToken = request.cookies.get(mergedConfig.cookieName)?.value;
  if (!cookieToken) {
    return {
      valid: false,
      error: 'CSRF token cookie not found',
    };
  }

  // Get CSRF token from header
  const headerToken = request.headers.get(mergedConfig.headerName);
  if (!headerToken) {
    return {
      valid: false,
      error: 'CSRF token header not found',
    };
  }

  // Validate tokens match
  const tokensMatch = validateCsrfToken(cookieToken, headerToken);
  if (!tokensMatch) {
    return {
      valid: false,
      error: 'CSRF token mismatch',
    };
  }

  return { valid: true };
}

/**
 * Extract CSRF validation error for logging
 *
 * @param request - Next.js request object
 * @param error - Error message
 * @returns Structured error information
 */
export function getCsrfErrorInfo(request: NextRequest, error: string): {
  error: string;
  method: string;
  path: string;
  hasTokenCookie: boolean;
  hasTokenHeader: boolean;
} {
  return {
    error,
    method: request.method,
    path: request.nextUrl.pathname,
    hasTokenCookie: !!request.cookies.get('csrf_token'),
    hasTokenHeader: !!request.headers.get('x-csrf-token'),
  };
}
