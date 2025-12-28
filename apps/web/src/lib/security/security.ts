/**
 * SAHOOL Security Layer
 * طبقة الأمان
 *
 * Features:
 * - CSRF protection
 * - XSS prevention
 * - Input sanitization
 * - Rate limiting (client-side)
 * - Secure cookie handling
 */

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface SecurityConfig {
  csrfEnabled?: boolean;
  csrfTokenHeader?: string;
  csrfCookieName?: string;
  rateLimitWindow?: number;
  rateLimitMaxRequests?: number;
}

export interface RateLimitEntry {
  count: number;
  resetTime: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const DEFAULT_CONFIG: SecurityConfig = {
  csrfEnabled: true,
  csrfTokenHeader: 'X-CSRF-Token',
  csrfCookieName: 'csrf_token',
  rateLimitWindow: 60000, // 1 minute
  rateLimitMaxRequests: 100,
};

// ═══════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════

let config: SecurityConfig = { ...DEFAULT_CONFIG };
const rateLimitStore = new Map<string, RateLimitEntry>();

// ═══════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Configure security settings
 * تكوين إعدادات الأمان
 */
export function configureSecurity(options: Partial<SecurityConfig>): void {
  config = { ...config, ...options };
}

// ═══════════════════════════════════════════════════════════════════════════
// CSRF Protection
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get CSRF token from cookie
 * الحصول على رمز CSRF من الكوكي
 */
export function getCsrfToken(): string | null {
  if (typeof document === 'undefined') return null;

  const cookieName = config.csrfCookieName || 'csrf_token';
  const match = document.cookie.match(new RegExp(`(^| )${cookieName}=([^;]+)`));
  return match ? (match[2] ?? null) : null;
}

/**
 * Generate CSRF token header for requests
 * إنشاء header CSRF للطلبات
 */
export function getCsrfHeaders(): Record<string, string> {
  if (!config.csrfEnabled) return {};

  const token = getCsrfToken();
  if (!token) return {};

  return {
    [config.csrfTokenHeader || 'X-CSRF-Token']: token,
  };
}

/**
 * Create secure fetch wrapper with CSRF
 * إنشاء wrapper آمن للـ fetch مع CSRF
 */
export function secureFetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  const csrfHeaders = getCsrfHeaders();

  const secureInit: RequestInit = {
    ...init,
    credentials: 'same-origin',
    headers: {
      ...init?.headers,
      ...csrfHeaders,
    },
  };

  return fetch(input, secureInit);
}

// ═══════════════════════════════════════════════════════════════════════════
// XSS Prevention
// ═══════════════════════════════════════════════════════════════════════════

const HTML_ENTITIES: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;',
};

/**
 * Escape HTML entities to prevent XSS
 * تهريب كيانات HTML لمنع XSS
 */
export function escapeHtml(str: string): string {
  return str.replace(/[&<>"'`=/]/g, (char) => HTML_ENTITIES[char] || char);
}

/**
 * Sanitize user input
 * تنظيف مدخلات المستخدم
 */
export function sanitizeInput(input: string): string {
  // Remove null bytes
  let sanitized = input.replace(/\0/g, '');

  // Remove control characters
  sanitized = sanitized.replace(/[\x00-\x1F\x7F]/g, '');

  // Escape HTML
  sanitized = escapeHtml(sanitized);

  return sanitized;
}

/**
 * Validate and sanitize URL
 * التحقق من صحة وتنظيف URL
 */
export function sanitizeUrl(url: string): string | null {
  try {
    const parsed = new URL(url, window.location.origin);

    // Only allow http and https protocols
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return null;
    }

    // Prevent javascript: URLs
    if (url.toLowerCase().startsWith('javascript:')) {
      return null;
    }

    // Prevent data: URLs (except safe types)
    if (parsed.protocol === 'data:') {
      return null;
    }

    return parsed.href;
  } catch {
    return null;
  }
}

/**
 * Strip HTML tags from string
 * إزالة علامات HTML من النص
 */
export function stripHtml(html: string): string {
  const doc = new DOMParser().parseFromString(html, 'text/html');
  return doc.body.textContent || '';
}

// ═══════════════════════════════════════════════════════════════════════════
// Rate Limiting (Client-side)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if request is rate limited
 * التحقق مما إذا كان الطلب محدودًا
 */
export function isRateLimited(key: string): boolean {
  const now = Date.now();
  const entry = rateLimitStore.get(key);

  if (!entry || now > entry.resetTime) {
    rateLimitStore.set(key, {
      count: 1,
      resetTime: now + (config.rateLimitWindow || 60000),
    });
    return false;
  }

  if (entry.count >= (config.rateLimitMaxRequests || 100)) {
    return true;
  }

  entry.count++;
  return false;
}

/**
 * Get remaining rate limit
 * الحصول على الحد المتبقي
 */
export function getRateLimitRemaining(key: string): number {
  const entry = rateLimitStore.get(key);
  if (!entry) return config.rateLimitMaxRequests || 100;

  const max = config.rateLimitMaxRequests || 100;
  return Math.max(0, max - entry.count);
}

/**
 * Reset rate limit for key
 * إعادة تعيين الحد لمفتاح
 */
export function resetRateLimit(key: string): void {
  rateLimitStore.delete(key);
}

// ═══════════════════════════════════════════════════════════════════════════
// Secure Cookie Handling
// ═══════════════════════════════════════════════════════════════════════════

export interface CookieOptions {
  path?: string;
  domain?: string;
  maxAge?: number;
  expires?: Date;
  secure?: boolean;
  sameSite?: 'strict' | 'lax' | 'none';
  httpOnly?: boolean;
}

/**
 * Set secure cookie
 * تعيين كوكي آمن
 */
export function setSecureCookie(
  name: string,
  value: string,
  options: CookieOptions = {}
): void {
  if (typeof document === 'undefined') return;

  const {
    path = '/',
    domain,
    maxAge,
    expires,
    secure = true,
    sameSite = 'strict',
  } = options;

  let cookieString = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;

  if (path) cookieString += `; path=${path}`;
  if (domain) cookieString += `; domain=${domain}`;
  if (maxAge !== undefined) cookieString += `; max-age=${maxAge}`;
  if (expires) cookieString += `; expires=${expires.toUTCString()}`;
  if (secure) cookieString += '; secure';
  if (sameSite) cookieString += `; samesite=${sameSite}`;

  document.cookie = cookieString;
}

/**
 * Get cookie value
 * الحصول على قيمة الكوكي
 */
export function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;

  const match = document.cookie.match(
    new RegExp(`(^| )${encodeURIComponent(name)}=([^;]+)`)
  );
  return match && match[2] ? decodeURIComponent(match[2]) : null;
}

/**
 * Delete cookie
 * حذف الكوكي
 */
export function deleteCookie(name: string, path: string = '/'): void {
  if (typeof document === 'undefined') return;

  document.cookie = `${encodeURIComponent(name)}=; path=${path}; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Content Security
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if content is safe JSON
 * التحقق مما إذا كان المحتوى JSON آمنًا
 */
export function isSafeJson(str: string): boolean {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
}

/**
 * Safe JSON parse with fallback
 * تحليل JSON آمن مع قيمة افتراضية
 */
export function safeJsonParse<T>(str: string, fallback: T): T {
  try {
    return JSON.parse(str) as T;
  } catch {
    return fallback;
  }
}

/**
 * Validate object against schema (simple validation)
 * التحقق من صحة الكائن مقابل المخطط
 */
export function validateSchema<T extends Record<string, unknown>>(
  obj: unknown,
  requiredFields: (keyof T)[]
): obj is T {
  if (typeof obj !== 'object' || obj === null) return false;

  const record = obj as Record<string, unknown>;
  return requiredFields.every((field) => field in record);
}

// ═══════════════════════════════════════════════════════════════════════════
// Password Validation
// ═══════════════════════════════════════════════════════════════════════════

export interface PasswordStrength {
  score: number; // 0-4
  feedback: string[];
  isStrong: boolean;
}

/**
 * Check password strength
 * التحقق من قوة كلمة المرور
 */
export function checkPasswordStrength(password: string): PasswordStrength {
  const feedback: string[] = [];
  let score = 0;

  if (password.length >= 8) {
    score++;
  } else {
    feedback.push('يجب أن تكون كلمة المرور 8 أحرف على الأقل');
  }

  if (/[a-z]/.test(password)) {
    score++;
  } else {
    feedback.push('أضف أحرف صغيرة');
  }

  if (/[A-Z]/.test(password)) {
    score++;
  } else {
    feedback.push('أضف أحرف كبيرة');
  }

  if (/[0-9]/.test(password)) {
    score++;
  } else {
    feedback.push('أضف أرقام');
  }

  if (/[^a-zA-Z0-9]/.test(password)) {
    score++;
  } else {
    feedback.push('أضف رموز خاصة');
  }

  return {
    score: Math.min(score, 4),
    feedback,
    isStrong: score >= 3,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const Security = {
  configure: configureSecurity,
  getCsrfToken,
  getCsrfHeaders,
  secureFetch,
  escapeHtml,
  sanitizeInput,
  sanitizeUrl,
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
};

export default Security;
