/**
 * Centralized Error Handler for Web Application
 * Provides consistent error handling across all API calls
 *
 * معالج أخطاء مركزي لتوحيد معالجة الأخطاء
 */

import { AxiosError } from 'axios';
import { logger } from '@/lib/logger';

interface ApiResponseData {
  message?: string;
  message_ar?: string;
  details?: Record<string, unknown>;
  error?: string | {
    code?: string;
    message?: string;
    message_ar?: string;
    details?: Record<string, unknown>;
  };
  success?: boolean;
  request_id?: string;
}

/**
 * @deprecated Use the ApiError class from safe-fetch instead.
 * Renamed to LegacyApiError to avoid naming conflict with the safe-fetch ApiError class.
 * @internal
 */
export interface LegacyApiError {
  message: string;
  messageAr?: string;
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
  timestamp: string;
  requestId?: string;
}

/**
 * Backend error code to user-friendly message mapping.
 * Mirrors the ErrorCode enum from shared/errors_py.py (E1001-E5003).
 */
const BACKEND_ERROR_MESSAGES: Record<string, { message: string; messageAr: string }> = {
  // General errors (1xxx)
  E1001: {
    message: 'An internal server error occurred. Please try again later.',
    messageAr: 'حدث خطأ داخلي في الخادم. يرجى المحاولة مرة أخرى لاحقاً.',
  },
  E1002: {
    message: 'Validation error. Please check your input and try again.',
    messageAr: 'خطأ في التحقق. يرجى التحقق من المدخلات والمحاولة مرة أخرى.',
  },
  E1003: {
    message: 'The requested resource was not found.',
    messageAr: 'المورد المطلوب غير موجود.',
  },
  E1004: {
    message: 'A conflict occurred. The resource may have been modified by another user.',
    messageAr: 'حدث تعارض. ربما تم تعديل المورد من قبل مستخدم آخر.',
  },
  E1005: {
    message: 'This operation is not supported.',
    messageAr: 'هذه العملية غير مدعومة.',
  },

  // Authentication errors (2xxx)
  E2001: {
    message: 'Authentication required. Please log in to continue.',
    messageAr: 'المصادقة مطلوبة. يرجى تسجيل الدخول للمتابعة.',
  },
  E2002: {
    message: 'Access denied. You do not have permission for this action.',
    messageAr: 'تم رفض الوصول. ليس لديك صلاحية لهذا الإجراء.',
  },
  E2003: {
    message: 'Your session has expired. Please log in again.',
    messageAr: 'انتهت صلاحية جلستك. يرجى تسجيل الدخول مرة أخرى.',
  },
  E2004: {
    message: 'Invalid authentication token. Please log in again.',
    messageAr: 'رمز المصادقة غير صالح. يرجى تسجيل الدخول مرة أخرى.',
  },

  // Business logic errors (3xxx)
  E3001: {
    message: 'This operation violates a business rule. Please review your request.',
    messageAr: 'هذه العملية تخالف قاعدة عمل. يرجى مراجعة طلبك.',
  },
  E3002: {
    message: 'You have exceeded your usage quota. Please upgrade your plan or wait for the quota to reset.',
    messageAr: 'لقد تجاوزت حصة الاستخدام الخاصة بك. يرجى ترقية خطتك أو انتظار إعادة تعيين الحصة.',
  },
  E3003: {
    message: 'The requested resource is exhausted. Please try again later or contact support.',
    messageAr: 'المورد المطلوب مستنفد. يرجى المحاولة لاحقاً أو الاتصال بالدعم.',
  },

  // Infrastructure / external service errors (4xxx)
  E4001: {
    message: 'An external service is temporarily unavailable. Please try again shortly.',
    messageAr: 'خدمة خارجية غير متوفرة مؤقتاً. يرجى المحاولة مرة أخرى بعد قليل.',
  },
  E4002: {
    message: 'A database error occurred. Our team has been notified. Please try again later.',
    messageAr: 'حدث خطأ في قاعدة البيانات. تم إخطار فريقنا. يرجى المحاولة لاحقاً.',
  },
  E4003: {
    message: 'A caching error occurred. Please retry your request.',
    messageAr: 'حدث خطأ في التخزين المؤقت. يرجى إعادة المحاولة.',
  },
  E4004: {
    message: 'A messaging system error occurred. Please try again later.',
    messageAr: 'حدث خطأ في نظام الرسائل. يرجى المحاولة لاحقاً.',
  },

  // AI/ML errors (5xxx)
  E5001: {
    message: 'The AI model encountered an error processing your request. Please try again.',
    messageAr: 'واجه نموذج الذكاء الاصطناعي خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى.',
  },
  E5002: {
    message: 'The AI analysis timed out. Please try with a smaller input or try again later.',
    messageAr: 'انتهت مهلة تحليل الذكاء الاصطناعي. يرجى المحاولة بمدخلات أصغر أو لاحقاً.',
  },
  E5003: {
    message: 'The requested AI model is currently unavailable. Please try again later.',
    messageAr: 'نموذج الذكاء الاصطناعي المطلوب غير متوفر حالياً. يرجى المحاولة لاحقاً.',
  },
};

export class ApiErrorHandler {
  /**
   * Extract the backend error code (e.g. "E1001") from the response body.
   * The backend returns errors in the shape:
   *   { success: false, error: { code: "E1001", message: "...", ... }, request_id: "..." }
   */
  /**
   * Extract structured fields from the backend error envelope.
   */
  private static extractBackendError(data: ApiResponseData | undefined): {
    code?: string;
    message?: string;
    messageAr?: string;
    details?: Record<string, unknown>;
    requestId?: string;
  } {
    if (!data) return {};

    const errorObj = typeof data.error === 'object' ? data.error : undefined;

    return {
      code: errorObj?.code,
      message: errorObj?.message ?? data.message,
      messageAr: errorObj?.message_ar ?? data.message_ar,
      details: errorObj?.details ?? data.details,
      requestId: data.request_id,
    };
  }

  /**
   * Handle Axios errors and convert to standardized format.
   *
   * Resolution order:
   * 1. Parse backend error code (E1001-E5003) from response body and map to
   *    a user-friendly message.
   * 2. Fall back to HTTP status code handling when no backend code is present.
   */
  static handleAxiosError(error: AxiosError<ApiResponseData>): LegacyApiError {
    const timestamp = new Date().toISOString();

    // Network error (no response)
    if (!error.response) {
      logger.error('Network error:', error);
      return {
        message: 'Network error. Please check your internet connection.',
        messageAr: 'خطأ في الشبكة. يرجى التحقق من اتصال الإنترنت.',
        code: 'NETWORK_ERROR',
        timestamp,
      };
    }

    // HTTP error with response
    const { status, data } = error.response;
    const backendError = ApiErrorHandler.extractBackendError(data);
    const backendCode = backendError.code;

    // --- Backend error code handling (E1001-E5003) ---
    if (backendCode && backendCode in BACKEND_ERROR_MESSAGES) {
      const mapped = BACKEND_ERROR_MESSAGES[backendCode];

      // Trigger re-authentication for auth-related backend codes
      if (
        (backendCode === 'E2001' || backendCode === 'E2003' || backendCode === 'E2004') &&
        typeof window !== 'undefined'
      ) {
        window.dispatchEvent(new CustomEvent('auth:session-expired'));
      }

      // For AI/ML errors, log additional diagnostics
      if (backendCode >= 'E5001' && backendCode <= 'E5003') {
        logger.error('AI/ML service error:', {
          code: backendCode,
          status,
          details: backendError.details,
          requestId: backendError.requestId,
        });
      }

      // For infrastructure errors, log for operational visibility
      if (backendCode >= 'E4001' && backendCode <= 'E4004') {
        logger.error('Infrastructure error:', {
          code: backendCode,
          status,
          details: backendError.details,
          requestId: backendError.requestId,
        });
      }

      // For business rule violations, include details so the UI can surface specifics
      if (backendCode >= 'E3001' && backendCode <= 'E3003') {
        logger.warn('Business rule violation:', {
          code: backendCode,
          details: backendError.details,
          requestId: backendError.requestId,
        });
      }

      return {
        message: backendError.message || mapped?.message || 'An error occurred',
        messageAr: backendError.messageAr || mapped?.messageAr || 'حدث خطأ',
        code: backendCode,
        status,
        details: backendError.details,
        requestId: backendError.requestId,
        timestamp,
      };
    }

    // --- Fallback: HTTP status code handling ---
    switch (status) {
      case 400:
        return {
          message: backendError.message || 'Invalid request',
          messageAr: backendError.messageAr || 'طلب غير صالح',
          code: 'BAD_REQUEST',
          status,
          details: backendError.details,
          requestId: backendError.requestId,
          timestamp,
        };

      case 401:
        // Session expired - trigger re-authentication
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('auth:session-expired'));
        }
        return {
          message: 'Session expired. Please login again.',
          messageAr: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
          code: 'UNAUTHORIZED',
          status,
          requestId: backendError.requestId,
          timestamp,
        };

      case 403:
        return {
          message: 'Access denied. You do not have permission for this action.',
          messageAr: 'تم رفض الوصول. ليس لديك صلاحية لهذا الإجراء.',
          code: 'FORBIDDEN',
          status,
          requestId: backendError.requestId,
          timestamp,
        };

      case 404:
        return {
          message: backendError.message || 'Resource not found',
          messageAr: backendError.messageAr || 'المورد غير موجود',
          code: 'NOT_FOUND',
          status,
          requestId: backendError.requestId,
          timestamp,
        };

      case 409:
        return {
          message: backendError.message || 'Conflict. Resource already exists.',
          messageAr: backendError.messageAr || 'تعارض. المورد موجود بالفعل.',
          code: 'CONFLICT',
          status,
          requestId: backendError.requestId,
          timestamp,
        };

      case 422:
        return {
          message: 'Validation error. Please check your input.',
          messageAr: 'خطأ في التحقق. يرجى التحقق من المدخلات.',
          code: 'VALIDATION_ERROR',
          status,
          details: backendError.details,
          requestId: backendError.requestId,
          timestamp,
        };

      case 429:
        return {
          message: 'Too many requests. Please try again later.',
          messageAr: 'طلبات كثيرة جداً. حاول مرة أخرى لاحقاً.',
          code: 'RATE_LIMIT_EXCEEDED',
          status,
          requestId: backendError.requestId,
          timestamp,
        };

      case 500:
      case 502:
      case 503:
      case 504:
        logger.error('Server error:', { status, data });
        return {
          message: 'Server error. Please try again later.',
          messageAr: 'خطأ في الخادم. حاول مرة أخرى لاحقاً.',
          code: 'SERVER_ERROR',
          status,
          requestId: backendError.requestId,
          timestamp,
        };

      default:
        return {
          message: backendError.message || 'An unexpected error occurred',
          messageAr: backendError.messageAr || 'حدث خطأ غير متوقع',
          code: 'UNKNOWN_ERROR',
          status,
          requestId: backendError.requestId,
          timestamp,
        };
    }
  }

  /**
   * Handle generic errors (non-Axios)
   */
  static handleGenericError(error: Error): LegacyApiError {
    logger.error('Generic error:', error);

    return {
      message: error.message || 'An unexpected error occurred',
      messageAr: 'حدث خطأ غير متوقع',
      code: 'GENERIC_ERROR',
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Format error for user display
   */
  static formatErrorMessage(error: LegacyApiError, locale: 'en' | 'ar' = 'en'): string {
    if (locale === 'ar' && error.messageAr) {
      return error.messageAr;
    }
    return error.message;
  }

  /**
   * Check if error is retryable
   */
  static isRetryable(error: LegacyApiError): boolean {
    const retryableCodes = [
      'NETWORK_ERROR',
      'SERVER_ERROR',
      // Infrastructure errors (E4xxx) are transient and retryable
      'E4001', // External service error
      'E4002', // Database error
      'E4003', // Cache error
      'E4004', // Messaging error
      // AI/ML errors that may resolve on retry
      'E5001', // AI model error
      'E5002', // Inference timeout
      'E5003', // Model not available
    ];
    const retryableStatuses = [408, 429, 500, 502, 503, 504];

    return (
      (!!error.code && retryableCodes.includes(error.code)) ||
      (!!error.status && retryableStatuses.includes(error.status))
    );
  }

  /**
   * Get retry delay based on error
   */
  static getRetryDelay(error: LegacyApiError, attempt: number): number {
    // Exponential backoff: 1s, 2s, 4s
    if (error.code === 'NETWORK_ERROR') {
      return Math.min(1000 * Math.pow(2, attempt - 1), 4000);
    }

    // Fixed delay for rate limiting or quota exceeded
    if (error.code === 'RATE_LIMIT_EXCEEDED' || error.code === 'E3002') {
      return 5000; // 5 seconds
    }

    // AI/ML errors: longer backoff since models may need time to recover
    if (error.code === 'E5001' || error.code === 'E5002' || error.code === 'E5003') {
      return Math.min(2000 * Math.pow(2, attempt - 1), 15000);
    }

    // Infrastructure errors: moderate backoff
    if (error.code === 'E4001' || error.code === 'E4002' || error.code === 'E4003' || error.code === 'E4004') {
      return Math.min(1500 * Math.pow(2, attempt - 1), 10000);
    }

    // Default backoff
    return Math.min(1000 * Math.pow(2, attempt - 1), 8000);
  }
}

/**
 * Hook for error handling in components
 */
export function useApiErrorHandler() {
  const handleError = (error: unknown): LegacyApiError => {
    if (error instanceof AxiosError) {
      return ApiErrorHandler.handleAxiosError(error);
    }
    if (error instanceof Error) {
      return ApiErrorHandler.handleGenericError(error);
    }
    return {
      message: 'An unexpected error occurred',
      messageAr: 'حدث خطأ غير متوقع',
      code: 'UNKNOWN_ERROR',
      timestamp: new Date().toISOString(),
    };
  };

  return { handleError };
}
