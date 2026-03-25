/**
 * SAHOOL Unified Error Codes
 * أكواد الأخطاء الموحدة
 *
 * Single source of truth for all API error codes.
 * Used by: Web, Admin, Mobile, api-client, backend services.
 *
 * @module @sahool/shared-types/contracts
 * @version 16.0.0
 */

// ---------------------------------------------------------------------------
// Error Codes - أكواد الأخطاء
// ---------------------------------------------------------------------------

/**
 * Unified error codes used across all SAHOOL clients and services.
 * Each code maps to an HTTP status, English message, and Arabic message.
 */
export const ERROR_CODES = {
  // ── Network & Transport ──────────────────────────────────────────────
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  CIRCUIT_OPEN: 'CIRCUIT_OPEN',
  INVALID_RESPONSE: 'INVALID_RESPONSE',

  // ── Authentication (401) ─────────────────────────────────────────────
  UNAUTHORIZED: 'UNAUTHORIZED',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_INVALID: 'TOKEN_INVALID',
  SESSION_EXPIRED: 'SESSION_EXPIRED',

  // ── Authorization (403) ──────────────────────────────────────────────
  FORBIDDEN: 'FORBIDDEN',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',

  // ── Client Errors (4xx) ──────────────────────────────────────────────
  BAD_REQUEST: 'BAD_REQUEST',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  RATE_LIMITED: 'RATE_LIMITED',

  // ── Server Errors (5xx) ──────────────────────────────────────────────
  SERVER_ERROR: 'SERVER_ERROR',
  BAD_GATEWAY: 'BAD_GATEWAY',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  GATEWAY_TIMEOUT: 'GATEWAY_TIMEOUT',

  // ── Mobile-Specific ──────────────────────────────────────────────────
  OFFLINE: 'OFFLINE',
  SYNC_FAILED: 'SYNC_FAILED',
  SYNC_CONFLICT: 'SYNC_CONFLICT',
  CERTIFICATE_ERROR: 'CERTIFICATE_ERROR',

  // ── Vision Service (E1xxx-E8xxx) ─────────────────────────────────────
  VISION_INVALID_FORMAT: 'E1001',
  VISION_FILE_TOO_LARGE: 'E1002',
  VISION_INVALID_DIMENSIONS: 'E1003',
  VISION_UNSUPPORTED_TYPE: 'E1004',
  VISION_EMPTY_IMAGE: 'E1005',
  VISION_CORRUPT_FILE: 'E1006',
  VISION_MODEL_NOT_FOUND: 'E2001',
  VISION_MODEL_LOAD_FAILED: 'E2002',
  VISION_INFERENCE_FAILED: 'E2003',
  VISION_MODEL_INCOMPATIBLE: 'E2004',
  VISION_WARMUP_FAILED: 'E2005',
  VISION_IMAGE_DECODE: 'E3001',
  VISION_BATCH_FAILED: 'E3003',
  VISION_GPU_OOM: 'E4001',
  VISION_MAX_CONCURRENT: 'E4004',
  VISION_DB_ERROR: 'E5001',
  VISION_CACHE_ERROR: 'E5002',
  VISION_RATE_EXCEEDED: 'E6001',
  VISION_QUOTA_EXCEEDED: 'E6002',
  VISION_INFERENCE_TIMEOUT: 'E7001',
  VISION_REQUEST_TIMEOUT: 'E7002',

  // ── Generic ──────────────────────────────────────────────────────────
  UNKNOWN: 'UNKNOWN',
} as const;

export type ErrorCode = (typeof ERROR_CODES)[keyof typeof ERROR_CODES];

// ---------------------------------------------------------------------------
// Error Messages - رسائل الأخطاء (ثنائية اللغة)
// ---------------------------------------------------------------------------

export interface ErrorMessage {
  /** Error code */
  code: ErrorCode;
  /** Default HTTP status (0 = no HTTP mapping) */
  httpStatus: number;
  /** English message */
  en: string;
  /** Arabic message */
  ar: string;
  /** Whether client should retry */
  retryable: boolean;
}

export const ERROR_MESSAGES: Record<string, ErrorMessage> = {
  // ── Network & Transport ──────────────────────────────────────────────
  [ERROR_CODES.NETWORK_ERROR]: {
    code: ERROR_CODES.NETWORK_ERROR,
    httpStatus: 0,
    en: 'Network error - please check your connection',
    ar: 'خطأ في الشبكة - يرجى التحقق من اتصالك',
    retryable: true,
  },
  [ERROR_CODES.TIMEOUT]: {
    code: ERROR_CODES.TIMEOUT,
    httpStatus: 504,
    en: 'Request timed out - please try again',
    ar: 'انتهت مهلة الطلب - يرجى المحاولة مرة أخرى',
    retryable: true,
  },
  [ERROR_CODES.CIRCUIT_OPEN]: {
    code: ERROR_CODES.CIRCUIT_OPEN,
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  },
  [ERROR_CODES.INVALID_RESPONSE]: {
    code: ERROR_CODES.INVALID_RESPONSE,
    httpStatus: 502,
    en: 'Invalid response from server',
    ar: 'استجابة غير صالحة من الخادم',
    retryable: false,
  },

  // ── Authentication (401) ─────────────────────────────────────────────
  [ERROR_CODES.UNAUTHORIZED]: {
    code: ERROR_CODES.UNAUTHORIZED,
    httpStatus: 401,
    en: 'Authentication required',
    ar: 'المصادقة مطلوبة',
    retryable: false,
  },
  [ERROR_CODES.TOKEN_EXPIRED]: {
    code: ERROR_CODES.TOKEN_EXPIRED,
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  },
  [ERROR_CODES.TOKEN_INVALID]: {
    code: ERROR_CODES.TOKEN_INVALID,
    httpStatus: 401,
    en: 'Invalid authentication token',
    ar: 'رمز مصادقة غير صالح',
    retryable: false,
  },
  [ERROR_CODES.SESSION_EXPIRED]: {
    code: ERROR_CODES.SESSION_EXPIRED,
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  },

  // ── Authorization (403) ──────────────────────────────────────────────
  [ERROR_CODES.FORBIDDEN]: {
    code: ERROR_CODES.FORBIDDEN,
    httpStatus: 403,
    en: 'Access denied - insufficient permissions',
    ar: 'الوصول مرفوض - صلاحيات غير كافية',
    retryable: false,
  },
  [ERROR_CODES.INSUFFICIENT_PERMISSIONS]: {
    code: ERROR_CODES.INSUFFICIENT_PERMISSIONS,
    httpStatus: 403,
    en: 'You do not have permission to perform this action',
    ar: 'ليس لديك صلاحية لتنفيذ هذا الإجراء',
    retryable: false,
  },

  // ── Client Errors (4xx) ──────────────────────────────────────────────
  [ERROR_CODES.BAD_REQUEST]: {
    code: ERROR_CODES.BAD_REQUEST,
    httpStatus: 400,
    en: 'Invalid request',
    ar: 'طلب غير صالح',
    retryable: false,
  },
  [ERROR_CODES.VALIDATION_ERROR]: {
    code: ERROR_CODES.VALIDATION_ERROR,
    httpStatus: 400,
    en: 'Validation error - please check your input',
    ar: 'خطأ في التحقق - يرجى مراجعة المدخلات',
    retryable: false,
  },
  [ERROR_CODES.NOT_FOUND]: {
    code: ERROR_CODES.NOT_FOUND,
    httpStatus: 404,
    en: 'Resource not found',
    ar: 'المورد غير موجود',
    retryable: false,
  },
  [ERROR_CODES.CONFLICT]: {
    code: ERROR_CODES.CONFLICT,
    httpStatus: 409,
    en: 'Conflict - resource was modified by another request',
    ar: 'تعارض - تم تعديل المورد بواسطة طلب آخر',
    retryable: false,
  },
  [ERROR_CODES.RATE_LIMITED]: {
    code: ERROR_CODES.RATE_LIMITED,
    httpStatus: 429,
    en: 'Too many requests. Please wait.',
    ar: 'طلبات كثيرة جداً. يرجى الانتظار.',
    retryable: true,
  },

  // ── Server Errors (5xx) ──────────────────────────────────────────────
  [ERROR_CODES.SERVER_ERROR]: {
    code: ERROR_CODES.SERVER_ERROR,
    httpStatus: 500,
    en: 'Server error - please try again later',
    ar: 'خطأ في الخادم - يرجى المحاولة لاحقاً',
    retryable: true,
  },
  [ERROR_CODES.BAD_GATEWAY]: {
    code: ERROR_CODES.BAD_GATEWAY,
    httpStatus: 502,
    en: 'Bad gateway - upstream service error',
    ar: 'خطأ في البوابة - خطأ في الخدمة الأصلية',
    retryable: true,
  },
  [ERROR_CODES.SERVICE_UNAVAILABLE]: {
    code: ERROR_CODES.SERVICE_UNAVAILABLE,
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  },
  [ERROR_CODES.GATEWAY_TIMEOUT]: {
    code: ERROR_CODES.GATEWAY_TIMEOUT,
    httpStatus: 504,
    en: 'Gateway timeout - please try again',
    ar: 'انتهت مهلة البوابة - يرجى المحاولة مرة أخرى',
    retryable: true,
  },

  // ── Mobile-Specific ──────────────────────────────────────────────────
  [ERROR_CODES.OFFLINE]: {
    code: ERROR_CODES.OFFLINE,
    httpStatus: 0,
    en: 'You are offline. Changes will sync when connected.',
    ar: 'أنت غير متصل. سيتم مزامنة التغييرات عند الاتصال.',
    retryable: true,
  },
  [ERROR_CODES.SYNC_FAILED]: {
    code: ERROR_CODES.SYNC_FAILED,
    httpStatus: 0,
    en: 'Sync failed. Please try again.',
    ar: 'فشلت المزامنة. يرجى المحاولة مرة أخرى.',
    retryable: true,
  },
  [ERROR_CODES.SYNC_CONFLICT]: {
    code: ERROR_CODES.SYNC_CONFLICT,
    httpStatus: 409,
    en: 'Sync conflict detected. Please resolve manually.',
    ar: 'تم اكتشاف تعارض في المزامنة. يرجى الحل يدوياً.',
    retryable: false,
  },
  [ERROR_CODES.CERTIFICATE_ERROR]: {
    code: ERROR_CODES.CERTIFICATE_ERROR,
    httpStatus: 0,
    en: 'Security certificate error',
    ar: 'خطأ في شهادة الأمان',
    retryable: false,
  },

  // ── Generic ──────────────────────────────────────────────────────────
  [ERROR_CODES.UNKNOWN]: {
    code: ERROR_CODES.UNKNOWN,
    httpStatus: 0,
    en: 'An unexpected error occurred',
    ar: 'حدث خطأ غير متوقع',
    retryable: false,
  },
};

// ---------------------------------------------------------------------------
// Helper Functions - دوال مساعدة
// ---------------------------------------------------------------------------

/**
 * Get the ErrorMessage for a given code.
 */
export function getErrorMessage(code: string): ErrorMessage {
  return ERROR_MESSAGES[code] ?? ERROR_MESSAGES[ERROR_CODES.UNKNOWN]!;
}

/**
 * Get localized error text.
 */
export function getLocalizedError(code: string, locale: 'ar' | 'en' = 'ar'): string {
  const msg = getErrorMessage(code);
  return locale === 'ar' ? msg.ar : msg.en;
}

/**
 * Map an HTTP status code to the best matching error code.
 */
export function httpStatusToErrorCode(status: number): ErrorCode {
  if (status === 401) return ERROR_CODES.UNAUTHORIZED;
  if (status === 403) return ERROR_CODES.FORBIDDEN;
  if (status === 404) return ERROR_CODES.NOT_FOUND;
  if (status === 409) return ERROR_CODES.CONFLICT;
  if (status === 429) return ERROR_CODES.RATE_LIMITED;
  if (status === 400) return ERROR_CODES.BAD_REQUEST;
  if (status === 502) return ERROR_CODES.INVALID_RESPONSE;
  if (status === 503) return ERROR_CODES.SERVICE_UNAVAILABLE;
  if (status === 504) return ERROR_CODES.GATEWAY_TIMEOUT;
  if (status >= 500) return ERROR_CODES.SERVER_ERROR;
  return ERROR_CODES.UNKNOWN;
}

/**
 * Check if an error code is retryable.
 */
export function isRetryable(code: string): boolean {
  return getErrorMessage(code).retryable;
}
