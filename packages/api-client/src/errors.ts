// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL API Client - Custom Error Types
// أنواع الأخطاء المخصصة لعميل API
// ═══════════════════════════════════════════════════════════════════════════════

import { AxiosError } from 'axios';

/**
 * Base API Error class
 * All custom API errors extend from this
 */
export class ApiError extends Error {
  public readonly code: string;
  public readonly statusCode?: number;
  public readonly endpoint?: string;
  public readonly method?: string;
  public readonly timestamp: string;
  public readonly originalError?: Error;
  public readonly context?: Record<string, unknown>;

  constructor(
    message: string,
    options: {
      code?: string;
      statusCode?: number;
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    } = {}
  ) {
    super(message);
    this.name = 'ApiError';
    this.code = options.code || 'API_ERROR';
    this.statusCode = options.statusCode;
    this.endpoint = options.endpoint;
    this.method = options.method;
    this.timestamp = new Date().toISOString();
    this.originalError = options.originalError;
    this.context = options.context;

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  /**
   * Convert error to a loggable object
   */
  toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      endpoint: this.endpoint,
      method: this.method,
      timestamp: this.timestamp,
      context: this.context,
      stack: this.stack,
    };
  }
}

/**
 * Network Error - for connection failures, timeouts, etc.
 */
export class NetworkError extends ApiError {
  constructor(
    message: string,
    options: {
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    } = {}
  ) {
    super(message, {
      ...options,
      code: 'NETWORK_ERROR',
    });
    this.name = 'NetworkError';
  }
}

/**
 * Authentication Error - for 401 unauthorized errors
 */
export class AuthError extends ApiError {
  constructor(
    message: string,
    options: {
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    } = {}
  ) {
    super(message, {
      ...options,
      code: 'AUTH_ERROR',
      statusCode: 401,
    });
    this.name = 'AuthError';
  }
}

/**
 * Authorization Error - for 403 forbidden errors
 */
export class AuthorizationError extends ApiError {
  constructor(
    message: string,
    options: {
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    } = {}
  ) {
    super(message, {
      ...options,
      code: 'AUTHORIZATION_ERROR',
      statusCode: 403,
    });
    this.name = 'AuthorizationError';
  }
}

/**
 * Not Found Error - for 404 errors
 */
export class NotFoundError extends ApiError {
  constructor(
    message: string,
    options: {
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    } = {}
  ) {
    super(message, {
      ...options,
      code: 'NOT_FOUND',
      statusCode: 404,
    });
    this.name = 'NotFoundError';
  }
}

/**
 * Validation Error - for 400 bad request errors
 */
export class ValidationError extends ApiError {
  public readonly validationErrors?: Record<string, string[]>;

  constructor(
    message: string,
    options: {
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
      validationErrors?: Record<string, string[]>;
    } = {}
  ) {
    super(message, {
      ...options,
      code: 'VALIDATION_ERROR',
      statusCode: 400,
    });
    this.name = 'ValidationError';
    this.validationErrors = options.validationErrors;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      validationErrors: this.validationErrors,
    };
  }
}

/**
 * Server Error - for 5xx server errors
 */
export class ServerError extends ApiError {
  constructor(
    message: string,
    options: {
      statusCode?: number;
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    } = {}
  ) {
    super(message, {
      ...options,
      code: 'SERVER_ERROR',
      statusCode: options.statusCode || 500,
    });
    this.name = 'ServerError';
  }
}

/**
 * Timeout Error - for request timeout errors
 */
export class TimeoutError extends ApiError {
  public readonly timeout: number;

  constructor(
    message: string,
    options: {
      timeout: number;
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    }
  ) {
    super(message, {
      ...options,
      code: 'TIMEOUT_ERROR',
    });
    this.name = 'TimeoutError';
    this.timeout = options.timeout;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      timeout: this.timeout,
    };
  }
}

/**
 * Rate Limit Error - for 429 too many requests errors
 */
export class RateLimitError extends ApiError {
  public readonly retryAfter?: number;

  constructor(
    message: string,
    options: {
      retryAfter?: number;
      endpoint?: string;
      method?: string;
      originalError?: Error;
      context?: Record<string, unknown>;
    } = {}
  ) {
    super(message, {
      ...options,
      code: 'RATE_LIMIT_ERROR',
      statusCode: 429,
    });
    this.name = 'RateLimitError';
    this.retryAfter = options.retryAfter;
  }

  toJSON(): Record<string, unknown> {
    return {
      ...super.toJSON(),
      retryAfter: this.retryAfter,
    };
  }
}

/**
 * Parse an Axios error into a custom API error
 */
export function parseAxiosError(
  error: AxiosError,
  endpoint?: string,
  method?: string
): ApiError {
  const config = error.config;
  const response = error.response;
  const request = error.request;

  const errorEndpoint = endpoint || config?.url || 'unknown';
  const errorMethod = method || config?.method?.toUpperCase() || 'unknown';

  // Network errors (no response received)
  if (!response) {
    // Timeout errors
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      const timeout = config?.timeout || 0;
      return new TimeoutError(
        `Request timeout after ${timeout}ms: ${errorEndpoint}`,
        {
          timeout,
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
        }
      );
    }

    // Connection errors
    return new NetworkError(
      `Network error: ${error.message}`,
      {
        endpoint: errorEndpoint,
        method: errorMethod,
        originalError: error,
        context: {
          code: error.code,
        },
      }
    );
  }

  // HTTP errors (response received)
  const statusCode = response.status;
  const errorData = response.data as { message?: string; error?: string; errors?: Record<string, string[]> };
  const errorMessage = errorData?.message || errorData?.error || error.message;

  switch (statusCode) {
    case 400:
      return new ValidationError(
        errorMessage || 'Validation error',
        {
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
          validationErrors: errorData?.errors,
          context: { statusCode, data: errorData },
        }
      );

    case 401:
      return new AuthError(
        errorMessage || 'Unauthorized - authentication required',
        {
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
          context: { statusCode },
        }
      );

    case 403:
      return new AuthorizationError(
        errorMessage || 'Forbidden - insufficient permissions',
        {
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
          context: { statusCode },
        }
      );

    case 404:
      return new NotFoundError(
        errorMessage || 'Resource not found',
        {
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
          context: { statusCode },
        }
      );

    case 429:
      const retryAfter = response.headers['retry-after']
        ? parseInt(response.headers['retry-after'], 10)
        : undefined;
      return new RateLimitError(
        errorMessage || 'Rate limit exceeded',
        {
          retryAfter,
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
          context: { statusCode },
        }
      );

    case 500:
    case 502:
    case 503:
    case 504:
      return new ServerError(
        errorMessage || 'Server error',
        {
          statusCode,
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
          context: { statusCode, data: errorData },
        }
      );

    default:
      return new ApiError(
        errorMessage || 'API error',
        {
          code: `HTTP_${statusCode}`,
          statusCode,
          endpoint: errorEndpoint,
          method: errorMethod,
          originalError: error,
          context: { statusCode, data: errorData },
        }
      );
  }
}

/**
 * Check if an error is an API error
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/**
 * Check if an error is a network error
 */
export function isNetworkError(error: unknown): error is NetworkError {
  return error instanceof NetworkError;
}

/**
 * Check if an error is an auth error
 */
export function isAuthError(error: unknown): error is AuthError {
  return error instanceof AuthError;
}
