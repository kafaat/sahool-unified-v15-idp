/**
 * Shared Error Handling Module
 * وحدة معالجة الأخطاء المشتركة
 *
 * @module shared/errors
 * @description Centralized error handling for all SAHOOL backend services
 *
 * @example
 * ```typescript
 * import {
 *   ErrorCode,
 *   AppException,
 *   NotFoundException,
 *   HttpExceptionFilter,
 * } from '@sahool/shared/errors';
 *
 * // Throw a custom exception
 * throw new NotFoundException(ErrorCode.FARM_NOT_FOUND);
 *
 * // Or use the helper methods
 * throw NotFoundException.farm('farm-123');
 * ```
 */

// Export error codes and types
export {
  ErrorCode,
  ErrorCategory,
  BilingualMessage,
  ErrorCodeMetadata,
  ERROR_REGISTRY,
  getErrorMetadata,
  getErrorCodesByCategory,
} from "./error-codes";

// Export custom exceptions
export {
  AppException,
  ValidationException,
  AuthenticationException,
  AuthorizationException,
  NotFoundException,
  ConflictException,
  BusinessLogicException,
  ExternalServiceException,
  DatabaseException,
  InternalServerException,
  RateLimitException,
} from "./exceptions";

// Export DTOs
export {
  FieldErrorDto,
  ErrorDetailsDto,
  ErrorResponseDto,
  ValidationErrorResponseDto,
  SuccessResponseDto,
  PaginatedResponseDto,
  PaginationMetaDto,
  createSuccessResponse,
  createPaginatedResponse,
} from "./error-response.dto";

// Export filters
export {
  HttpExceptionFilter,
  LanguageAwareExceptionFilter,
} from "./http-exception.filter";

// Export utilities
export {
  HandleErrors,
  handleAsync,
  retryWithBackoff,
  CircuitBreaker,
  isDatabaseError,
  isNetworkError,
  isRetryable,
  getErrorMessage,
  logError,
  sanitizeError,
  ErrorAggregator,
  withTimeout,
} from "./error-utils";
