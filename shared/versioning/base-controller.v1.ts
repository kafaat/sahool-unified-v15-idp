/**
 * Base Controller for API v1
 * Provides common functionality for v1 controllers
 *
 * @deprecated v1 API is deprecated. Please migrate to v2.
 * Deprecation Date: 2025-06-30
 * Sunset Date: 2026-06-30
 */

import { SetMetadata } from '@nestjs/common';

/**
 * V1 Response format
 * Legacy format maintained for backward compatibility
 */
export interface V1Response<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

/**
 * V1 Error response format
 */
export interface V1ErrorResponse {
  success: false;
  message: string;
  error?: string;
}

/**
 * V1 Pagination metadata
 */
export interface V1PaginationMeta {
  skip: number;
  take: number;
  count: number;
}

/**
 * Base Controller V1
 * Provides utility methods for v1 controllers
 */
export abstract class BaseControllerV1 {
  /**
   * Create a success response in v1 format
   */
  protected success<T>(data: T, message?: string): V1Response<T> {
    return {
      success: true,
      data,
      ...(message && { message }),
    };
  }

  /**
   * Create an error response in v1 format
   */
  protected error(message: string, error?: string): V1ErrorResponse {
    return {
      success: false,
      message,
      ...(error && { error }),
    };
  }

  /**
   * Create a paginated response in v1 format
   */
  protected paginated<T>(
    data: T[],
    meta: V1PaginationMeta,
    message?: string,
  ): V1Response<T[]> & { count: number } {
    return {
      success: true,
      data,
      count: meta.count,
      ...(message && { message }),
    };
  }

  /**
   * Log deprecation warning
   */
  protected logDeprecationWarning(endpoint: string): void {
    console.warn(
      `[DEPRECATION WARNING] v1 endpoint accessed: ${endpoint}. ` +
      `This endpoint will be removed on 2026-06-30. ` +
      `Please migrate to v2: https://docs.sahool.app/api/v2/migration`,
    );
  }
}

/**
 * Decorator to mark v1 endpoints as deprecated
 */
export const ApiV1Deprecated = () => SetMetadata('api-v1-deprecated', true);
