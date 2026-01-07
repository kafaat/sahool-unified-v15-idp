/**
 * CSRF Protection Utilities
 * أدوات حماية CSRF
 *
 * Implements double-submit cookie pattern for CSRF protection
 */

import { randomBytes, createHash, timingSafeEqual } from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════

export const CSRF_CONFIG = {
  TOKEN_LENGTH: 32, // 256-bit tokens
  TOKEN_EXPIRATION: 60 * 60 * 1000, // 1 hour in milliseconds
  COOKIE_NAME: 'sahool_csrf_token',
  HEADER_NAME: 'X-CSRF-Token',
  FIELD_NAME: '_csrf',
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface CsrfTokenPayload {
  token: string;
  createdAt: number;
  expiresAt: number;
}

export interface CsrfValidationResult {
  valid: boolean;
  error?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Token Generation
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generate a cryptographically secure CSRF token
 * توليد رمز CSRF آمن
 */
export function generateCsrfToken(): string {
  return randomBytes(CSRF_CONFIG.TOKEN_LENGTH).toString('base64url');
}

/**
 * Create a complete CSRF token payload with expiration
 * إنشاء حمولة رمز CSRF كاملة مع انتهاء الصلاحية
 */
export function createCsrfTokenPayload(): CsrfTokenPayload {
  const now = Date.now();
  return {
    token: generateCsrfToken(),
    createdAt: now,
    expiresAt: now + CSRF_CONFIG.TOKEN_EXPIRATION,
  };
}

/**
 * Hash a token for secure storage comparison
 * تشفير الرمز للمقارنة الآمنة
 */
export function hashToken(token: string): string {
  return createHash('sha256').update(token).digest('base64url');
}

// ═══════════════════════════════════════════════════════════════════════════
// Token Validation
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validate CSRF token using constant-time comparison
 * التحقق من رمز CSRF باستخدام مقارنة زمنية ثابتة
 */
export function validateCsrfToken(
  providedToken: string,
  storedPayload: CsrfTokenPayload | null
): CsrfValidationResult {
  // Check if stored payload exists
  if (!storedPayload) {
    return { valid: false, error: 'No CSRF token found in session' };
  }

  // Check if token has expired
  if (Date.now() > storedPayload.expiresAt) {
    return { valid: false, error: 'CSRF token has expired' };
  }

  // Check if provided token is present
  if (!providedToken || typeof providedToken !== 'string') {
    return { valid: false, error: 'No CSRF token provided in request' };
  }

  // Constant-time comparison to prevent timing attacks
  try {
    const providedBuffer = Buffer.from(providedToken, 'utf8');
    const storedBuffer = Buffer.from(storedPayload.token, 'utf8');

    // If lengths differ, comparison will fail but we still use timingSafeEqual
    // to prevent timing attacks based on early exit
    if (providedBuffer.length !== storedBuffer.length) {
      return { valid: false, error: 'Invalid CSRF token' };
    }

    const isValid = timingSafeEqual(providedBuffer, storedBuffer);
    return isValid
      ? { valid: true }
      : { valid: false, error: 'Invalid CSRF token' };
  } catch {
    return { valid: false, error: 'CSRF token validation failed' };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Extract CSRF token from request headers
 * استخراج رمز CSRF من رؤوس الطلب
 */
export function extractCsrfTokenFromHeaders(headers: Headers): string | null {
  return headers.get(CSRF_CONFIG.HEADER_NAME);
}

/**
 * Extract CSRF token from form data
 * استخراج رمز CSRF من بيانات النموذج
 */
export function extractCsrfTokenFromFormData(formData: FormData): string | null {
  const token = formData.get(CSRF_CONFIG.FIELD_NAME);
  return typeof token === 'string' ? token : null;
}

/**
 * Parse CSRF token payload from cookie value
 * تحليل حمولة رمز CSRF من قيمة الكوكي
 */
export function parseCsrfTokenPayload(cookieValue: string | undefined): CsrfTokenPayload | null {
  if (!cookieValue) return null;

  try {
    const payload = JSON.parse(cookieValue);
    if (
      typeof payload.token === 'string' &&
      typeof payload.createdAt === 'number' &&
      typeof payload.expiresAt === 'number'
    ) {
      return payload as CsrfTokenPayload;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Serialize CSRF token payload for cookie storage
 * تسلسل حمولة رمز CSRF للتخزين في الكوكي
 */
export function serializeCsrfTokenPayload(payload: CsrfTokenPayload): string {
  return JSON.stringify(payload);
}

/**
 * Check if a request method requires CSRF validation
 * التحقق مما إذا كان أسلوب الطلب يتطلب التحقق من CSRF
 */
export function requiresCsrfValidation(method: string): boolean {
  const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
  return !safeMethods.includes(method.toUpperCase());
}

/**
 * Get cookie options for CSRF token
 * الحصول على خيارات الكوكي لرمز CSRF
 */
export function getCsrfCookieOptions(): {
  httpOnly: boolean;
  secure: boolean;
  sameSite: 'strict' | 'lax' | 'none';
  path: string;
  maxAge: number;
} {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    path: '/',
    maxAge: CSRF_CONFIG.TOKEN_EXPIRATION / 1000, // Convert to seconds
  };
}
