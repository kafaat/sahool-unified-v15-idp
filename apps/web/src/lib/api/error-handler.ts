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
  error?: string;
}

export interface ApiError {
  message: string;
  messageAr?: string;
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
  timestamp: string;
}

export class ApiErrorHandler {
  /**
   * Handle Axios errors and convert to standardized format
   */
  static handleAxiosError(error: AxiosError<ApiResponseData>): ApiError {
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

    // Handle specific status codes
    switch (status) {
      case 400:
        return {
          message: data?.message || 'Invalid request',
          messageAr: data?.message_ar || 'طلب غير صالح',
          code: 'BAD_REQUEST',
          status,
          details: data?.details,
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
          timestamp,
        };

      case 403:
        return {
          message: 'Access denied. You do not have permission for this action.',
          messageAr: 'تم رفض الوصول. ليس لديك صلاحية لهذا الإجراء.',
          code: 'FORBIDDEN',
          status,
          timestamp,
        };

      case 404:
        return {
          message: data?.message || 'Resource not found',
          messageAr: data?.message_ar || 'المورد غير موجود',
          code: 'NOT_FOUND',
          status,
          timestamp,
        };

      case 409:
        return {
          message: data?.message || 'Conflict. Resource already exists.',
          messageAr: data?.message_ar || 'تعارض. المورد موجود بالفعل.',
          code: 'CONFLICT',
          status,
          timestamp,
        };

      case 422:
        return {
          message: 'Validation error. Please check your input.',
          messageAr: 'خطأ في التحقق. يرجى التحقق من المدخلات.',
          code: 'VALIDATION_ERROR',
          status,
          details: data?.details,
          timestamp,
        };

      case 429:
        return {
          message: 'Too many requests. Please try again later.',
          messageAr: 'طلبات كثيرة جداً. حاول مرة أخرى لاحقاً.',
          code: 'RATE_LIMIT_EXCEEDED',
          status,
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
          timestamp,
        };

      default:
        return {
          message: data?.message || 'An unexpected error occurred',
          messageAr: data?.message_ar || 'حدث خطأ غير متوقع',
          code: 'UNKNOWN_ERROR',
          status,
          timestamp,
        };
    }
  }

  /**
   * Handle generic errors (non-Axios)
   */
  static handleGenericError(error: Error): ApiError {
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
  static formatErrorMessage(error: ApiError, locale: 'en' | 'ar' = 'en'): string {
    if (locale === 'ar' && error.messageAr) {
      return error.messageAr;
    }
    return error.message;
  }

  /**
   * Check if error is retryable
   */
  static isRetryable(error: ApiError): boolean {
    const retryableCodes = ['NETWORK_ERROR', 'SERVER_ERROR'];
    const retryableStatuses = [408, 429, 500, 502, 503, 504];

    return (
      (!!error.code && retryableCodes.includes(error.code)) ||
      (!!error.status && retryableStatuses.includes(error.status))
    );
  }

  /**
   * Get retry delay based on error
   */
  static getRetryDelay(error: ApiError, attempt: number): number {
    // Exponential backoff: 1s, 2s, 4s
    if (error.code === 'NETWORK_ERROR') {
      return Math.min(1000 * Math.pow(2, attempt - 1), 4000);
    }

    // Fixed delay for rate limiting
    if (error.code === 'RATE_LIMIT_EXCEEDED') {
      return 5000; // 5 seconds
    }

    // Default backoff
    return Math.min(1000 * Math.pow(2, attempt - 1), 8000);
  }
}

/**
 * Hook for error handling in components
 */
export function useApiErrorHandler() {
  const handleError = (error: unknown): ApiError => {
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
