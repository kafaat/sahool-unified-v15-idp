/**
 * @sahool/shared-db - Shared Database Utilities
 *
 * Comprehensive database utilities including:
 * - Soft delete pattern implementation for Prisma and SQLAlchemy
 * - Query optimization utilities (pagination, timeouts, logging)
 * - Performance monitoring and helpers
 */

// ═══════════════════════════════════════════════════════════════════════════
// Soft Delete Pattern
// ═══════════════════════════════════════════════════════════════════════════

// Export types
export type {
  SoftDeletable,
  SoftDeleteOptions,
  RestoreOptions,
  SoftDeleteConfig,
} from "./soft-delete";

// Export functions
export {
  // Middleware
  createSoftDeleteMiddleware,

  // Core CRUD operations
  softDelete,
  softDeleteMany,
  restore,
  restoreMany,
  hardDelete,

  // Query helpers
  findWithDeleted,
  findFirstWithDeleted,
  count,
  countWithDeleted,

  // Utility functions
  isDeleted,
  getDeletionMetadata,
  filterDeleted,
  filterOnlyDeleted,
} from "./soft-delete";

// ═══════════════════════════════════════════════════════════════════════════
// Query Optimization Utilities
// ═══════════════════════════════════════════════════════════════════════════

// Export types
export type {
  PaginationParams,
  PaginationMeta,
  PaginatedResponse,
  CursorPaginationParams,
  CursorPaginatedResponse,
  QueryLog,
  QueryLogger,
} from "./query-utils";

// Export constants
export {
  MAX_PAGE_SIZE,
  DEFAULT_PAGE_SIZE,
  DEFAULT_QUERY_TIMEOUT,
  CRITICAL_WRITE_TIMEOUT,
  SLOW_QUERY_THRESHOLD,
  FINANCIAL_TRANSACTION_CONFIG,
  GENERAL_TRANSACTION_CONFIG,
  READ_TRANSACTION_CONFIG,
} from "./query-utils";

// Export functions
export {
  // Pagination
  calculatePagination,
  buildPaginationMeta,
  createPaginatedResponse,
  buildCursorPagination,
  processCursorResults,

  // Logging
  createQueryLogger,
  measureQueryTime,

  // Select helpers
  createSelect,
  CommonSelects,

  // Batch operations
  batchOperation,
  parallelLimit,
} from "./query-utils";
