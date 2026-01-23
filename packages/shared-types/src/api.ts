/**
 * SAHOOL API Response Types
 * Standard API response structures and pagination types
 *
 * These types define the contract between frontend and backend services,
 * ensuring consistent response formats across all API endpoints.
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Core API Response Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Standard API response wrapper
 * Used for all API responses to provide consistent structure
 *
 * @typeParam T - The type of the data payload
 *
 * @example
 * // Success response
 * const response: ApiResponse<User> = {
 *   success: true,
 *   data: { id: "1", name: "John", email: "john@example.com", ... },
 *   message: "User retrieved successfully"
 * };
 *
 * // Error response
 * const errorResponse: ApiResponse<User> = {
 *   success: false,
 *   error: "User not found",
 *   statusCode: 404
 * };
 */
export interface ApiResponse<T = unknown> {
  /** Whether the request was successful */
  success: boolean;

  /** The response data (present on success) */
  data?: T;

  /** Error message (present on failure) */
  error?: string;

  /** Error message in Arabic */
  errorAr?: string;

  /** Human-readable message */
  message?: string;

  /** Message in Arabic */
  messageAr?: string;

  /** HTTP status code */
  statusCode?: number;

  /** Request timestamp */
  timestamp?: string;

  /** Request ID for tracing */
  requestId?: string;
}

/**
 * Successful API response with guaranteed data
 *
 * @typeParam T - The type of the data payload
 */
export interface SuccessResponse<T = unknown> {
  readonly success: true;
  data: T;
  message?: string;
  messageAr?: string;
  statusCode?: number;
  timestamp?: string;
  requestId?: string;
}

/**
 * Error API response
 */
export interface ErrorResponse {
  readonly success: false;
  error: string;
  errorAr?: string;
  message: string;
  messageAr?: string;
  statusCode: number;
  timestamp?: string;
  requestId?: string;
  path?: string;
  /** Validation errors or additional context */
  details?: Record<string, unknown>;
  /** Stack trace (development only) */
  stack?: string;
}

/**
 * API error with structured details
 */
export interface ApiError {
  /** Error code (e.g., "FIELD_NOT_FOUND", "VALIDATION_ERROR") */
  code: string;
  /** Error message */
  message: string;
  /** Error message in Arabic */
  messageAr?: string;
  /** Detailed error information */
  details?: Record<string, unknown>;
  /** Field-specific validation errors */
  fieldErrors?: Record<string, string[]>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Pagination Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  /** Current page number (1-indexed) */
  page: number;
  /** Items per page */
  limit: number;
  /** Total number of items */
  total: number;
  /** Total number of pages */
  totalPages: number;
  /** Whether there's a next page */
  hasNextPage: boolean;
  /** Whether there's a previous page */
  hasPreviousPage: boolean;
}

/**
 * Paginated API response
 *
 * @typeParam T - The type of items in the data array
 *
 * @example
 * const response: PaginatedResponse<Field> = {
 *   success: true,
 *   data: [field1, field2, field3],
 *   pagination: {
 *     page: 1,
 *     limit: 10,
 *     total: 100,
 *     totalPages: 10,
 *     hasNextPage: true,
 *     hasPreviousPage: false
 *   }
 * };
 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  /** Pagination information */
  pagination: PaginationMeta;
}

/**
 * Alternative paginated response format (legacy compatibility)
 */
export interface PaginatedData<T> {
  /** Array of items */
  data: T[];
  /** Total count */
  total: number;
  /** Current page */
  page: number;
  /** Page size */
  pageSize: number;
  /** Has more pages */
  hasMore: boolean;
  /** Has next page */
  hasNext?: boolean;
  /** Has previous page */
  hasPrevious?: boolean;
}

/**
 * Pagination request parameters
 */
export interface PaginationParams {
  /** Page number (1-indexed) */
  page?: number;
  /** Items per page (default: 10, max: 100) */
  limit?: number;
  /** Sort field */
  sortBy?: string;
  /** Sort direction */
  sortOrder?: "asc" | "desc";
}

/**
 * Cursor-based pagination for infinite scroll
 */
export interface CursorPaginationParams {
  /** Cursor for the next page */
  cursor?: string;
  /** Items per page */
  limit?: number;
  /** Sort direction */
  direction?: "forward" | "backward";
}

/**
 * Cursor-based pagination response
 */
export interface CursorPaginatedResponse<T> extends ApiResponse<T[]> {
  /** Cursor for the next page */
  nextCursor?: string;
  /** Cursor for the previous page */
  previousCursor?: string;
  /** Whether there are more items */
  hasMore: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Query and Filter Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generic filter operators
 */
export type FilterOperator =
  | "eq"       // Equal
  | "neq"      // Not equal
  | "gt"       // Greater than
  | "gte"      // Greater than or equal
  | "lt"       // Less than
  | "lte"      // Less than or equal
  | "in"       // In array
  | "nin"      // Not in array
  | "contains" // String contains
  | "startsWith"
  | "endsWith"
  | "between"
  | "isNull"
  | "isNotNull";

/**
 * Filter condition
 */
export interface FilterCondition<T = unknown> {
  /** Field to filter */
  field: string;
  /** Filter operator */
  operator: FilterOperator;
  /** Filter value */
  value: T;
}

/**
 * Generic query parameters
 */
export interface QueryParams extends PaginationParams {
  /** Search term */
  search?: string;
  /** Filter conditions */
  filters?: FilterCondition[];
  /** Include related entities */
  include?: string[];
  /** Select specific fields */
  select?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Batch Operation Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Batch operation request
 *
 * @typeParam T - The type of items to process
 */
export interface BatchRequest<T> {
  /** Items to process */
  items: T[];
  /** Operation type */
  operation: "create" | "update" | "delete";
  /** Stop on first error */
  stopOnError?: boolean;
}

/**
 * Batch operation result for a single item
 */
export interface BatchItemResult<T> {
  /** Item index in the batch */
  index: number;
  /** Whether operation succeeded */
  success: boolean;
  /** Result data (on success) */
  data?: T;
  /** Error message (on failure) */
  error?: string;
  /** Original item ID */
  id?: string;
}

/**
 * Batch operation response
 *
 * @typeParam T - The type of processed items
 */
export interface BatchResponse<T> {
  /** Whether all operations succeeded */
  success: boolean;
  /** Total items processed */
  totalProcessed: number;
  /** Successful operations count */
  successCount: number;
  /** Failed operations count */
  failedCount: number;
  /** Individual results */
  results: BatchItemResult<T>[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Health Check Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Service dependency status
 */
export interface DependencyStatus {
  /** Dependency name */
  name: string;
  /** Whether dependency is healthy */
  healthy: boolean;
  /** Response time in milliseconds */
  latencyMs?: number;
  /** Error message if unhealthy */
  error?: string;
  /** Last check timestamp */
  lastChecked?: string;
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  /** Overall status */
  status: "healthy" | "degraded" | "unhealthy";
  /** Service version */
  version: string;
  /** Uptime in seconds */
  uptime?: number;
  /** Dependencies status */
  dependencies?: DependencyStatus[];
  /** Timestamp */
  timestamp: string;
}

/**
 * Readiness check response
 */
export interface ReadinessResponse {
  /** Whether service is ready */
  ready: boolean;
  /** Database connection status */
  database?: boolean;
  /** Message queue connection status */
  messageQueue?: boolean;
  /** Cache connection status */
  cache?: boolean;
  /** Reasons if not ready */
  reasons?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Validation Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Validation error for a single field
 */
export interface ValidationFieldError {
  /** Field name */
  field: string;
  /** Error message */
  message: string;
  /** Message in Arabic */
  messageAr?: string;
  /** Validation rule that failed */
  rule?: string;
  /** Provided value (sanitized) */
  value?: unknown;
}

/**
 * Validation error response
 */
export interface ValidationErrorResponse extends ErrorResponse {
  statusCode: 400;
  code?: "VALIDATION_ERROR";
  /** Field-specific errors */
  fieldErrors: ValidationFieldError[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for successful response
 *
 * @example
 * const response = await api.getField(id);
 * if (isSuccessResponse(response)) {
 *   console.log(response.data.name);
 * } else {
 *   console.error(response.error);
 * }
 */
export function isSuccessResponse<T>(
  response: ApiResponse<T>
): response is SuccessResponse<T> {
  return response.success === true && response.data !== undefined;
}

/**
 * Type guard for error response
 */
export function isErrorResponse(
  response: ApiResponse<unknown>
): response is ErrorResponse {
  return response.success === false;
}

/**
 * Type guard for validation error response
 */
export function isValidationError(
  response: ApiResponse<unknown>
): response is ValidationErrorResponse {
  return (
    isErrorResponse(response) &&
    response.statusCode === 400 &&
    "fieldErrors" in response
  );
}

/**
 * Type guard for paginated response
 */
export function isPaginatedResponse<T>(
  response: ApiResponse<T[]>
): response is PaginatedResponse<T> {
  return (
    response.success === true &&
    Array.isArray(response.data) &&
    "pagination" in response
  );
}

/**
 * Type guard for API error
 */
export function isApiError(obj: unknown): obj is ApiError {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "code" in obj &&
    "message" in obj
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Creates a success response
 */
export function createSuccessResponse<T>(
  data: T,
  message?: string
): SuccessResponse<T> {
  return {
    success: true,
    data,
    message,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Creates an error response
 */
export function createErrorResponse(
  error: string,
  statusCode: number,
  details?: Record<string, unknown>
): ErrorResponse {
  return {
    success: false,
    error,
    message: error,
    statusCode,
    details,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Calculate pagination metadata
 */
export function calculatePagination(
  page: number,
  limit: number,
  total: number
): PaginationMeta {
  const totalPages = Math.ceil(total / limit);
  return {
    page,
    limit,
    total,
    totalPages,
    hasNextPage: page < totalPages,
    hasPreviousPage: page > 1,
  };
}

/**
 * Extracts error message from various error formats
 */
export function extractErrorMessage(error: unknown): string {
  if (typeof error === "string") {
    return error;
  }
  if (error instanceof Error) {
    return error.message;
  }
  if (isApiError(error)) {
    return error.message;
  }
  if (isErrorResponse(error as ApiResponse<unknown>)) {
    return (error as ErrorResponse).error;
  }
  return "An unknown error occurred";
}
