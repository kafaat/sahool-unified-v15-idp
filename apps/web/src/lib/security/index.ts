/**
 * SAHOOL Security Module
 * وحدة الأمان
 *
 * Central export for all security-related utilities
 * تصدير مركزي لجميع أدوات الأمان
 */

// Core security utilities (excluding sanitizeUrl to avoid conflict with url-sanitizer)
export {
  configureSecurity,
  getCsrfToken,
  getCsrfHeaders,
  secureFetch,
  escapeHtml,
  sanitizeInput,
  stripHtml,
  isRateLimited,
  getRateLimitRemaining,
  resetRateLimit,
  setSecureCookie,
  getCookie,
  deleteCookie,
  isSafeJson,
  safeJsonParse,
  validateSchema,
  checkPasswordStrength,
  type SecurityConfig,
  type RateLimitEntry,
  type CookieOptions,
  type PasswordStrength,
} from "./security";
export { default as Security } from "./security";

// CSP utilities
export * from "./csp-config";
export { default as CSP } from "./csp-config";

// Nonce utilities
export * from "./nonce";
export { default as Nonce } from "./nonce";

// URL sanitization utilities (preferred over security.ts sanitizeUrl)
export { sanitizeUrl, isUrlSafe, sanitizeUrlForNavigation } from "./url-sanitizer";
export { default as UrlSanitizer } from "./url-sanitizer";
