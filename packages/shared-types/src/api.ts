/**
 * API Response Types
 * Standard API response structures
 */

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  statusCode?: number;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface ErrorResponse {
  success: false;
  error: string;
  message: string;
  statusCode: number;
  timestamp?: string;
  path?: string;
  details?: Record<string, any>;
}

export interface SuccessResponse<T = any> {
  success: true;
  data: T;
  message?: string;
  statusCode?: number;
}

/**
 * Type guard for successful response
 */
export function isSuccessResponse<T>(
  response: ApiResponse<T>,
): response is SuccessResponse<T> {
  return response.success === true && response.data !== undefined;
}

/**
 * Type guard for error response
 */
export function isErrorResponse(
  response: ApiResponse<any>,
): response is ErrorResponse {
  return response.success === false;
}
