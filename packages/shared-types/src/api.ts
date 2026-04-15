/**
 * API Response Types
 * Standard API response structures
 *
 * These types align with the canonical contract definitions in
 * `@sahool/shared-types/contracts`. Prefer importing from the contracts
 * subpath for the most complete type definitions.
 */

/** Standard API success/error response wrapper used by ALL services */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  /** Arabic-localised error message */
  errorAr?: string;
  /** Machine-readable error code (e.g. "UNAUTHORIZED", "E1001") */
  errorCode?: string;
  /** Correlation ID echoed from X-Request-Id header */
  requestId?: string;
  message?: string;
  pagination?: PaginationMeta;
}

/** Pagination metadata returned alongside list endpoints */
export interface PaginationMeta {
  /** Total number of items matching the query */
  total: number;
  /** Current page number (1-based, used with `limit`) */
  page: number;
  /** Maximum number of items per page */
  limit: number;
  totalPages?: number;
  hasMore?: boolean;
  /** Zero-based item offset — may be provided/derived in addition to `page`/`limit` */
  offset?: number;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: PaginationMeta;
}

export interface ErrorResponse {
  success: false;
  error: string;
  /** Arabic-localised error message */
  errorAr?: string;
  message: string;
  statusCode: number;
  timestamp?: string;
  path?: string;
  details?: Record<string, unknown>;
}

export interface SuccessResponse<T = unknown> {
  success: true;
  data: T;
  message?: string;
  statusCode?: number;
}

/**
 * Bilingual API error object (used in typed error payloads)
 */
export interface ApiError {
  /** Machine-readable error code */
  code: string;
  /** English error message */
  message: string;
  /** Arabic error message */
  messageAr?: string;
  details?: Record<string, unknown>;
}

/**
 * Discriminated-union result type for functions that may fail.
 *
 * @example Default error type
 * const result: ApiResult<Field> = await fetchField(id);
 * if (result.success) { ... use result.data ... }
 * else { ... handle result.error ... }
 *
 * @example Custom error type
 * type DomainError = { reason: "quota_exceeded" | "not_found" };
 * const result: ApiResult<Field, DomainError> = await fetchField(id);
 */
export type ApiResult<T, E = ApiError> = { success: true; data: T } | { success: false; error: E };

/**
 * Type guard for successful response
 */
export function isSuccessResponse<T>(response: ApiResponse<T>): response is SuccessResponse<T> {
  return response.success === true && response.data !== undefined;
}

/**
 * Type guard for error response
 */
export function isErrorResponse(response: ApiResponse<unknown>): response is ErrorResponse {
  return response.success === false;
}
