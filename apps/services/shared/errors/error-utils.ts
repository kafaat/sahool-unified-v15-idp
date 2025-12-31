/**
 * Error Handling Utilities
 * أدوات معالجة الأخطاء
 *
 * @module shared/errors
 * @description Utility functions for error handling
 */

import { Logger } from '@nestjs/common';
import {
  AppException,
  DatabaseException,
  ExternalServiceException,
  InternalServerException,
} from './exceptions';
import { ErrorCode } from './error-codes';

/**
 * Error Handler Decorator
 * ديكوراتور معالج الأخطاء
 *
 * @description Wraps async methods with error handling
 */
export function HandleErrors(errorCode?: ErrorCode) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
  ) {
    const originalMethod = descriptor.value;
    const logger = new Logger(target.constructor.name);

    descriptor.value = async function (...args: any[]) {
      try {
        return await originalMethod.apply(this, args);
      } catch (error) {
        logger.error(`Error in ${propertyKey}:`, error);

        // If it's already an AppException, rethrow it
        if (error instanceof AppException) {
          throw error;
        }

        // Handle database errors
        if (isDatabaseError(error)) {
          throw DatabaseException.fromDatabaseError(error);
        }

        // If error code is provided, throw with that code
        if (errorCode) {
          throw new AppException(errorCode, undefined, {
            originalError: error.message,
          });
        }

        // Otherwise, throw internal server error
        throw new InternalServerException(ErrorCode.INTERNAL_SERVER_ERROR, undefined, {
          originalError: error.message,
        });
      }
    };

    return descriptor;
  };
}

/**
 * Async Error Handler
 * معالج الأخطاء اللامتزامن
 *
 * @description Wraps async functions with error handling
 */
export async function handleAsync<T>(
  fn: () => Promise<T>,
  fallbackValue?: T,
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (error instanceof AppException) {
      throw error;
    }

    if (fallbackValue !== undefined) {
      return fallbackValue;
    }

    throw new InternalServerException(ErrorCode.INTERNAL_SERVER_ERROR, undefined, {
      originalError: error.message,
    });
  }
}

/**
 * Retry with exponential backoff
 * إعادة المحاولة مع تأخير أسي
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    shouldRetry?: (error: any) => boolean;
  } = {},
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    shouldRetry = (error) =>
      error instanceof AppException ? error.retryable : true,
  } = options;

  let lastError: any;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if we should retry
      if (!shouldRetry(error)) {
        throw error;
      }

      // Check if we have more attempts
      if (attempt < maxRetries - 1) {
        // Calculate delay with exponential backoff
        const delay = Math.min(initialDelay * Math.pow(2, attempt), maxDelay);

        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  // All retries exhausted
  throw lastError;
}

/**
 * Circuit Breaker Pattern
 * نمط قاطع الدائرة
 */
export class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime: number | null = null;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';

  constructor(
    private readonly threshold: number = 5,
    private readonly timeout: number = 60000,
    private readonly resetTimeout: number = 30000,
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime! > this.resetTimeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new ExternalServiceException(
          ErrorCode.EXTERNAL_SERVICE_ERROR,
          {
            en: 'Service circuit breaker is open',
            ar: 'قاطع دائرة الخدمة مفتوح',
          },
          {
            state: this.state,
            failureCount: this.failureCount,
          },
        );
      }
    }

    try {
      const result = await fn();

      // Success - reset circuit breaker
      if (this.state === 'HALF_OPEN') {
        this.state = 'CLOSED';
        this.failureCount = 0;
      }

      return result;
    } catch (error) {
      this.failureCount++;
      this.lastFailureTime = Date.now();

      if (this.failureCount >= this.threshold) {
        this.state = 'OPEN';
      }

      throw error;
    }
  }

  getState() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime,
    };
  }

  reset() {
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.lastFailureTime = null;
  }
}

/**
 * Check if error is a database error
 * التحقق من كون الخطأ خطأ قاعدة بيانات
 */
export function isDatabaseError(error: any): boolean {
  // Prisma errors
  if (error.code && typeof error.code === 'string' && error.code.startsWith('P')) {
    return true;
  }

  // TypeORM errors
  if (error.name && error.name.includes('QueryFailed')) {
    return true;
  }

  // MongoDB errors
  if (error.name && error.name === 'MongoError') {
    return true;
  }

  return false;
}

/**
 * Check if error is a network error
 * التحقق من كون الخطأ خطأ شبكة
 */
export function isNetworkError(error: any): boolean {
  return (
    error.code === 'ECONNREFUSED' ||
    error.code === 'ENOTFOUND' ||
    error.code === 'ETIMEDOUT' ||
    error.code === 'ECONNRESET'
  );
}

/**
 * Check if error is retryable
 * التحقق من إمكانية إعادة محاولة الخطأ
 */
export function isRetryable(error: any): boolean {
  if (error instanceof AppException) {
    return error.retryable;
  }

  // Network errors are retryable
  if (isNetworkError(error)) {
    return true;
  }

  // Some database errors are retryable
  if (isDatabaseError(error)) {
    const retryablePrismaCodes = ['P1001', 'P1002', 'P1008', 'P1017'];
    if (retryablePrismaCodes.includes(error.code)) {
      return true;
    }
  }

  return false;
}

/**
 * Safe error message extraction
 * استخراج رسالة الخطأ بشكل آمن
 */
export function getErrorMessage(error: any): string {
  if (error instanceof AppException) {
    return error.messageEn;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'Unknown error occurred';
}

/**
 * Log error with context
 * تسجيل الخطأ مع السياق
 */
export function logError(
  logger: Logger,
  error: any,
  context?: Record<string, any>,
) {
  const errorMessage = getErrorMessage(error);
  const errorCode = error instanceof AppException ? error.errorCode : 'UNKNOWN';

  logger.error(`[${errorCode}] ${errorMessage}`, {
    error: error instanceof Error ? error.stack : error,
    ...context,
  });
}

/**
 * Sanitize error for client
 * تنظيف الخطأ للعميل
 *
 * @description Removes sensitive information from error details
 */
export function sanitizeError(error: any): any {
  if (error instanceof AppException) {
    return {
      code: error.errorCode,
      message: error.messageEn,
      messageAr: error.messageAr,
    };
  }

  return {
    code: ErrorCode.INTERNAL_SERVER_ERROR,
    message: 'An error occurred',
    messageAr: 'حدث خطأ',
  };
}

/**
 * Error aggregation for batch operations
 * تجميع الأخطاء لعمليات الدُفعات
 */
export class ErrorAggregator {
  private errors: Array<{ index: number; error: any }> = [];

  add(index: number, error: any) {
    this.errors.push({ index, error });
  }

  hasErrors(): boolean {
    return this.errors.length > 0;
  }

  getErrors() {
    return this.errors;
  }

  throwIfHasErrors() {
    if (this.hasErrors()) {
      throw new AppException(
        ErrorCode.BUSINESS_RULE_VIOLATION,
        {
          en: `Batch operation failed with ${this.errors.length} errors`,
          ar: `فشلت عملية الدُفعة مع ${this.errors.length} أخطاء`,
        },
        {
          errors: this.errors.map((e) => ({
            index: e.index,
            message: getErrorMessage(e.error),
          })),
        },
      );
    }
  }
}

/**
 * Timeout wrapper
 * غلاف المهلة
 */
export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  errorMessage?: string,
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => {
      reject(
        new InternalServerException(
          ErrorCode.INTERNAL_SERVER_ERROR,
          {
            en: errorMessage || `Operation timed out after ${timeoutMs}ms`,
            ar: errorMessage || `انتهت مهلة العملية بعد ${timeoutMs} ملي ثانية`,
          },
          { timeoutMs },
        ),
      );
    }, timeoutMs);
  });

  return Promise.race([promise, timeout]);
}
