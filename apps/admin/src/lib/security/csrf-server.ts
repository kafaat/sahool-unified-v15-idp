/**
 * CSRF Server-Side Validation for Admin
 * التحقق من رمز CSRF من جانب الخادم للوحة الإدارة
 *
 * Server-side CSRF token validation for Next.js middleware
 * Used to protect against Cross-Site Request Forgery attacks
 */

import type { NextRequest } from "next/server";
import { randomBytes } from "crypto";

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
export const CSRF_PROTECTED_METHODS = [
  "POST",
  "PUT",
  "DELETE",
  "PATCH",
] as const;

/**
 * CSRF configuration for admin
 */
export interface CsrfConfig {
  cookieName?: string;
  headerName?: string;
  excludePaths?: string[];
}

/**
 * Default CSRF configuration for admin
 */
const DEFAULT_CONFIG: Required<CsrfConfig> = {
  cookieName: "sahool_admin_csrf",
  headerName: "x-csrf-token",
  excludePaths: [
    "/api/auth/login",
    "/api/auth/logout",
    "/api/health",
    "/login",
  ],
};

/**
 * Generate a secure CSRF token
 */
export function generateCsrfToken(): string {
  // Use Web Crypto API for Edge Runtime compatibility
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, (byte) => byte.toString(16).padStart(2, "0")).join(
    "",
  );
}

/**
 * Validate CSRF token using timing-safe comparison
 */
export function validateCsrfToken(
  cookieToken: string | undefined,
  headerToken: string | undefined,
): boolean {
  if (!cookieToken || !headerToken) {
    return false;
  }

  if (cookieToken.length !== headerToken.length) {
    return false;
  }

  try {
    return timingSafeCompare(cookieToken, headerToken);
  } catch {
    return false;
  }
}

/**
 * Check if request requires CSRF validation
 */
export function requiresCsrfValidation(
  request: NextRequest,
  config: CsrfConfig = {},
): boolean {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };
  const method = request.method;
  const pathname = request.nextUrl.pathname;

  // Only validate state-changing methods
  if (
    !CSRF_PROTECTED_METHODS.includes(
      method as (typeof CSRF_PROTECTED_METHODS)[number],
    )
  ) {
    return false;
  }

  // Exclude specific paths
  if (mergedConfig.excludePaths.some((path) => pathname.startsWith(path))) {
    return false;
  }

  return true;
}

/**
 * Validate CSRF token from request
 */
export function validateCsrfRequest(
  request: NextRequest,
  config: CsrfConfig = {},
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
      error: "CSRF token cookie not found",
    };
  }

  // Get CSRF token from header
  const headerToken = request.headers.get(mergedConfig.headerName);
  if (!headerToken) {
    return {
      valid: false,
      error: "CSRF token header not found",
    };
  }

  // Validate tokens match
  const tokensMatch = validateCsrfToken(cookieToken, headerToken);
  if (!tokensMatch) {
    return {
      valid: false,
      error: "CSRF token mismatch",
    };
  }

  return { valid: true };
}
