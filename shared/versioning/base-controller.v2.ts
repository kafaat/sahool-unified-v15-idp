/**
 * Base Controller for API v2
 * Provides common functionality for v2 controllers
 *
 * Enhanced response format with metadata and standardization
 */

/**
 * V2 Response format
 * Enhanced format with metadata
 */
export interface V2Response<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  version: string;
  timestamp: string;
  meta: V2ResponseMeta;
}

/**
 * V2 Response metadata
 */
export interface V2ResponseMeta {
  requestId: string;
  pagination?: V2PaginationMeta;
  [key: string]: any;
}

/**
 * V2 Pagination metadata
 */
export interface V2PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/**
 * V2 Error response format
 */
export interface V2ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: string;
    field?: string;
    timestamp: string;
  };
  version: string;
  meta: {
    requestId: string;
    documentation?: string;
  };
}

/**
 * Sort order enum
 */
export enum SortOrder {
  ASC = 'asc',
  DESC = 'desc',
}

/**
 * Base Controller V2
 * Provides utility methods for v2 controllers
 */
export abstract class BaseControllerV2 {
  protected readonly version = '2';

  /**
   * Create a success response in v2 format
   */
  protected success<T>(
    data: T,
    requestId: string,
    message?: string,
    meta?: Partial<V2ResponseMeta>,
  ): V2Response<T> {
    return {
      success: true,
      data,
      ...(message && { message }),
      version: this.version,
      timestamp: new Date().toISOString(),
      meta: {
        requestId,
        ...meta,
      },
    };
  }

  /**
   * Create an error response in v2 format
   */
  protected error(
    code: string,
    message: string,
    requestId: string,
    details?: string,
    field?: string,
  ): V2ErrorResponse {
    return {
      success: false,
      error: {
        code,
        message,
        ...(details && { details }),
        ...(field && { field }),
        timestamp: new Date().toISOString(),
      },
      version: this.version,
      meta: {
        requestId,
        documentation: `https://docs.sahool.app/errors/${code}`,
      },
    };
  }

  /**
   * Create a paginated response in v2 format
   */
  protected paginated<T>(
    data: T[],
    page: number,
    limit: number,
    total: number,
    requestId: string,
    message?: string,
  ): V2Response<T[]> {
    const totalPages = Math.ceil(total / limit);
    const hasNext = page < totalPages;
    const hasPrev = page > 1;

    return {
      success: true,
      data,
      ...(message && { message }),
      version: this.version,
      timestamp: new Date().toISOString(),
      meta: {
        requestId,
        pagination: {
          page,
          limit,
          total,
          totalPages,
          hasNext,
          hasPrev,
        },
      },
    };
  }

  /**
   * Calculate pagination skip value from page and limit
   */
  protected calculateSkip(page: number, limit: number): number {
    return (page - 1) * limit;
  }

  /**
   * Parse and validate pagination parameters
   */
  protected parsePaginationParams(
    page?: string | number,
    limit?: string | number,
  ): { page: number; limit: number; skip: number } {
    const parsedPage = Math.max(1, parseInt(String(page || '1'), 10));
    const parsedLimit = Math.min(
      100,
      Math.max(1, parseInt(String(limit || '20'), 10)),
    );
    const skip = this.calculateSkip(parsedPage, parsedLimit);

    return {
      page: parsedPage,
      limit: parsedLimit,
      skip,
    };
  }

  /**
   * Parse and validate sort parameters
   */
  protected parseSortParams(
    sort?: string,
    order?: string,
  ): { field: string; order: SortOrder } {
    return {
      field: sort || 'createdAt',
      order: (order?.toLowerCase() === 'asc' ? SortOrder.ASC : SortOrder.DESC),
    };
  }
}
