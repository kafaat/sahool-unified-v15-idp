/**
 * Safe API Fetch Utilities - أدوات جلب البيانات الآمنة
 *
 * Replaces the anti-pattern of silently returning mock/empty data on API errors.
 * Instead, errors are either:
 * 1. Re-thrown for React Error Boundary / React Query error handling
 * 2. Returned as typed Result<T> for explicit error handling in components
 *
 * Migration guide:
 *   BEFORE: try { return await api.get(url); } catch { return []; }
 *   AFTER:  return await safeFetch(endpoint, () => api.get(url).then(r => r.data));
 */

import axios from 'axios';
import { logger } from '@/lib/logger';

/**
 * API Error class with bilingual messages and structured metadata
 * خطأ API مع رسائل ثنائية اللغة وبيانات وصفية منظمة
 */
export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly messageAr: string;
  public readonly endpoint: string;
  public readonly retryable: boolean;

  constructor(options: {
    message: string;
    messageAr: string;
    statusCode: number;
    endpoint: string;
    retryable?: boolean;
    cause?: unknown;
  }) {
    super(options.message, { cause: options.cause });
    this.name = 'ApiError';
    this.statusCode = options.statusCode;
    this.messageAr = options.messageAr;
    this.endpoint = options.endpoint;
    this.retryable = options.retryable ?? false;
  }
}

/**
 * Convert AxiosError to structured ApiError
 */
function toApiError(error: unknown, endpoint: string): ApiError {
  if (error instanceof ApiError) return error;

  if (axios.isAxiosError(error)) {
    const status = error.response?.status ?? 0;
    const responseData = error.response?.data as Record<string, unknown> | undefined;
    const serverMessage = responseData?.message as string | undefined;
    const serverMessageAr = (responseData?.messageAr ?? responseData?.message_ar) as string | undefined;

    const messages: Record<number, { en: string; ar: string }> = {
      0: { en: 'Network error. Please check your connection.', ar: 'خطأ في الشبكة. يرجى التحقق من الاتصال.' },
      400: { en: 'Invalid request. Please check your input.', ar: 'طلب غير صالح. يرجى التحقق من البيانات المدخلة.' },
      401: { en: 'Session expired. Please log in again.', ar: 'انتهت الجلسة. يرجى تسجيل الدخول مجدداً.' },
      403: { en: 'You do not have permission to access this resource.', ar: 'ليس لديك صلاحية للوصول إلى هذا المورد.' },
      404: { en: 'The requested resource was not found.', ar: 'لم يتم العثور على المورد المطلوب.' },
      409: { en: 'Conflict. The requested operation cannot be completed.', ar: 'تعارض في الطلب. لا يمكن إتمام العملية المطلوبة.' },
      422: { en: 'Validation error. Please review the entered data.', ar: 'خطأ في التحقق من البيانات. يرجى مراجعة البيانات المدخلة.' },
      429: { en: 'Too many requests. Please try again later.', ar: 'طلبات كثيرة جداً. يرجى المحاولة لاحقاً.' },
      500: { en: 'Server error. Please try again later.', ar: 'خطأ في الخادم. يرجى المحاولة لاحقاً.' },
      502: { en: 'Service temporarily unavailable.', ar: 'الخدمة غير متاحة مؤقتاً.' },
      503: { en: 'Service temporarily unavailable.', ar: 'الخدمة غير متاحة مؤقتاً.' },
      504: { en: 'The server is taking too long to respond. Please try again later.', ar: 'الخادم يستغرق وقتاً طويلاً في الاستجابة. يرجى المحاولة لاحقاً.' },
    };

    const fallback = messages[status] ?? messages[500]!;

    return new ApiError({
      message: serverMessage ?? fallback.en,
      messageAr: serverMessageAr ?? fallback.ar,
      statusCode: status,
      endpoint,
      retryable: status === 0 || status === 429 || status >= 500,
      cause: error,
    });
  }

  // Preserve original error message for non-Axios errors (e.g. format validation)
  const originalMessage = error instanceof Error ? error.message : 'An unexpected error occurred.';

  return new ApiError({
    message: originalMessage,
    messageAr: 'حدث خطأ غير متوقع.',
    statusCode: 0,
    endpoint,
    retryable: false,
    cause: error,
  });
}

/**
 * Executes an API call and throws a structured ApiError on failure.
 * Use this when the component has an ErrorBoundary or React Query to handle errors.
 *
 * @example
 * // In a React Query hook:
 * const { data } = useQuery({
 *   queryKey: ['alerts'],
 *   queryFn: () => safeFetch('/api/alerts', () => api.get(ALERT_ENDPOINTS.LIST).then(r => r.data)),
 * });
 */
export async function safeFetch<T>(endpoint: string, fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    const apiError = toApiError(error, endpoint);
    logger.production(`API call failed: ${endpoint}`, {
      statusCode: apiError.statusCode,
      retryable: apiError.retryable,
    });
    throw apiError;
  }
}

/**
 * Result type for explicit error handling without throwing.
 * نوع النتيجة للتعامل الصريح مع الأخطاء بدون رمي استثناء
 */
export type ApiResult<T> =
  | { ok: true; data: T; error?: never }
  | { ok: false; data?: never; error: ApiError };

/**
 * Executes an API call and returns a Result instead of throwing.
 * Use this when you want to handle errors explicitly in the component.
 *
 * @example
 * const result = await safeFetchResult('/api/tasks', () => api.get(url));
 * if (!result.ok) {
 *   showToast(result.error.messageAr);
 *   return;
 * }
 * setTasks(result.data);
 */
export async function safeFetchResult<T>(endpoint: string, fn: () => Promise<T>): Promise<ApiResult<T>> {
  try {
    const data = await fn();
    return { ok: true, data };
  } catch (error) {
    const apiError = toApiError(error, endpoint);
    logger.production(`API call failed (handled): ${endpoint}`, {
      statusCode: apiError.statusCode,
    });
    return { ok: false, error: apiError };
  }
}
