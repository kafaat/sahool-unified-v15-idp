/**
 * @sahool/shared-db - Shared Database Utilities
 *
 * Comprehensive soft delete pattern implementation for:
 * - Prisma (TypeScript/JavaScript services)
 * - SQLAlchemy (Python services)
 */

// Export types
export type {
  SoftDeletable,
  SoftDeleteOptions,
  RestoreOptions,
  SoftDeleteConfig,
} from './soft-delete';

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
} from './soft-delete';
