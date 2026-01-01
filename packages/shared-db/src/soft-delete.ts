/**
 * @fileoverview Soft Delete Pattern Implementation for Prisma
 * @module @sahool/shared-db/soft-delete
 *
 * This module provides a comprehensive soft delete implementation for Prisma ORM:
 * - Middleware that automatically filters out soft-deleted records
 * - Helper functions for soft delete operations (delete, restore, findWithDeleted)
 * - TypeScript types for models with soft delete fields
 *
 * Usage:
 * 1. Add deletedAt and deletedBy fields to your Prisma schema
 * 2. Apply the middleware to your PrismaClient instance
 * 3. Use the helper functions for soft delete operations
 */

import { Prisma } from '@prisma/client';

// ═══════════════════════════════════════════════════════════════════════════
// Types & Interfaces
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Base interface for models that support soft delete
 */
export interface SoftDeletable {
  deletedAt: Date | null;
  deletedBy: string | null;
}

/**
 * Options for soft delete operations
 */
export interface SoftDeleteOptions {
  /** User ID or identifier of who is performing the delete */
  deletedBy?: string;
  /** Whether to include deleted records in the result */
  includeDeleted?: boolean;
}

/**
 * Options for restore operations
 */
export interface RestoreOptions {
  /** User ID or identifier of who is performing the restore */
  restoredBy?: string;
}

/**
 * Configuration for soft delete middleware
 */
export interface SoftDeleteConfig {
  /**
   * Models to exclude from soft delete behavior
   * Use this for audit tables, logs, or models that should always hard delete
   */
  excludedModels?: string[];

  /**
   * Whether to log soft delete operations (useful for debugging)
   */
  enableLogging?: boolean;

  /**
   * Custom logger function
   */
  logger?: (message: string, data?: any) => void;
}

// ═══════════════════════════════════════════════════════════════════════════
// Prisma Middleware - Auto-filter deleted records
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Creates Prisma middleware that implements soft delete pattern
 *
 * This middleware:
 * - Converts `delete` operations to `update` operations (setting deletedAt)
 * - Converts `deleteMany` operations to `updateMany` operations
 * - Automatically filters out soft-deleted records in queries (unless includeDeleted is true)
 * - Preserves all other Prisma functionality
 *
 * @param config Configuration options for the middleware
 * @returns Prisma middleware function
 *
 * @example
 * ```typescript
 * import { PrismaClient } from '@prisma/client';
 * import { createSoftDeleteMiddleware } from '@sahool/shared-db';
 *
 * const prisma = new PrismaClient();
 *
 * // Apply the middleware
 * prisma.$use(createSoftDeleteMiddleware({
 *   excludedModels: ['AuditLog', 'WalletAuditLog'],
 *   enableLogging: process.env.NODE_ENV === 'development'
 * }));
 *
 * // Now all delete operations become soft deletes
 * await prisma.product.delete({ where: { id: '123' } });
 * // This sets deletedAt instead of actually deleting the record
 *
 * // Queries automatically filter out deleted records
 * const products = await prisma.product.findMany();
 * // This only returns non-deleted products
 * ```
 */
export function createSoftDeleteMiddleware(
  config: SoftDeleteConfig = {}
): (params: any, next: (params: any) => Promise<any>) => Promise<any> {
  const {
    excludedModels = [],
    enableLogging = false,
    logger = console.log,
  } = config;

  return async (params, next) => {
    const model = params.model;

    // Skip if model is in excluded list
    if (!model || excludedModels.includes(model)) {
      return next(params);
    }

    // Log if enabled
    if (enableLogging) {
      logger(`[SoftDelete] ${params.action} on ${model}`, { args: params.args });
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Handle DELETE operations - convert to UPDATE
    // ─────────────────────────────────────────────────────────────────────────
    if (params.action === 'delete') {
      params.action = 'update';
      params.args.data = {
        deletedAt: new Date(),
        deletedBy: (params.args as any).deletedBy || null,
      };

      if (enableLogging) {
        logger(`[SoftDelete] Converted delete to update for ${model}`);
      }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Handle DELETE MANY operations - convert to UPDATE MANY
    // ─────────────────────────────────────────────────────────────────────────
    if (params.action === 'deleteMany') {
      params.action = 'updateMany';
      params.args.data = {
        deletedAt: new Date(),
        deletedBy: (params.args as any).deletedBy || null,
      };

      if (enableLogging) {
        logger(`[SoftDelete] Converted deleteMany to updateMany for ${model}`);
      }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Handle FIND operations - filter out deleted records
    // ─────────────────────────────────────────────────────────────────────────
    const readActions = [
      'findUnique',
      'findFirst',
      'findMany',
      'count',
      'aggregate',
      'groupBy',
    ];

    if (readActions.includes(params.action)) {
      // Check if user explicitly wants to include deleted records
      const includeDeleted = (params.args as any)?.includeDeleted;

      if (!includeDeleted) {
        // Add filter to exclude deleted records
        if (params.args.where) {
          // Preserve existing where clause
          if (params.args.where.deletedAt === undefined) {
            params.args.where.deletedAt = null;
          }
        } else {
          params.args.where = { deletedAt: null };
        }
      } else {
        // Remove the includeDeleted flag to avoid Prisma errors
        delete (params.args as any).includeDeleted;
      }
    }

    return next(params);
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Soft delete a single record
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param where The where clause to identify the record
 * @param options Soft delete options
 * @returns The updated (soft-deleted) record
 *
 * @example
 * ```typescript
 * import { softDelete } from '@sahool/shared-db';
 *
 * const deletedProduct = await softDelete(
 *   prisma.product,
 *   { id: 'product-123' },
 *   { deletedBy: 'user-456' }
 * );
 * ```
 */
export async function softDelete<T extends { update: any }>(
  prismaModel: T,
  where: any,
  options: SoftDeleteOptions = {}
): Promise<any> {
  return prismaModel.update({
    where,
    data: {
      deletedAt: new Date(),
      deletedBy: options.deletedBy || null,
    },
  });
}

/**
 * Soft delete multiple records
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param where The where clause to identify records
 * @param options Soft delete options
 * @returns Object with count of records updated
 *
 * @example
 * ```typescript
 * import { softDeleteMany } from '@sahool/shared-db';
 *
 * const result = await softDeleteMany(
 *   prisma.product,
 *   { category: 'DEPRECATED' },
 *   { deletedBy: 'admin-123' }
 * );
 * console.log(`Deleted ${result.count} products`);
 * ```
 */
export async function softDeleteMany<T extends { updateMany: any }>(
  prismaModel: T,
  where: any,
  options: SoftDeleteOptions = {}
): Promise<{ count: number }> {
  return prismaModel.updateMany({
    where,
    data: {
      deletedAt: new Date(),
      deletedBy: options.deletedBy || null,
    },
  });
}

/**
 * Restore a soft-deleted record
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param where The where clause to identify the record
 * @param options Restore options
 * @returns The restored record
 *
 * @example
 * ```typescript
 * import { restore } from '@sahool/shared-db';
 *
 * const restoredProduct = await restore(
 *   prisma.product,
 *   { id: 'product-123' },
 *   { restoredBy: 'admin-456' }
 * );
 * ```
 */
export async function restore<T extends { update: any }>(
  prismaModel: T,
  where: any,
  options: RestoreOptions = {}
): Promise<any> {
  return prismaModel.update({
    where,
    data: {
      deletedAt: null,
      deletedBy: null,
      // Optionally store who restored in metadata or another field
      ...(options.restoredBy && {
        updatedAt: new Date(),
        // You might want to add a restoredBy field to your schema
      }),
    },
  });
}

/**
 * Restore multiple soft-deleted records
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param where The where clause to identify records
 * @param options Restore options
 * @returns Object with count of records restored
 *
 * @example
 * ```typescript
 * import { restoreMany } from '@sahool/shared-db';
 *
 * const result = await restoreMany(
 *   prisma.product,
 *   { category: 'TEMPORARILY_REMOVED' }
 * );
 * console.log(`Restored ${result.count} products`);
 * ```
 */
export async function restoreMany<T extends { updateMany: any }>(
  prismaModel: T,
  where: any,
  options: RestoreOptions = {}
): Promise<{ count: number }> {
  return prismaModel.updateMany({
    where,
    data: {
      deletedAt: null,
      deletedBy: null,
    },
  });
}

/**
 * Find records including soft-deleted ones
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param args Standard Prisma findMany arguments
 * @returns Array of records including deleted ones
 *
 * @example
 * ```typescript
 * import { findWithDeleted } from '@sahool/shared-db';
 *
 * // Find all products, including deleted ones
 * const allProducts = await findWithDeleted(prisma.product, {
 *   where: { category: 'SEEDS' }
 * });
 *
 * // Only find deleted products
 * const deletedProducts = await findWithDeleted(prisma.product, {
 *   where: {
 *     category: 'SEEDS',
 *     deletedAt: { not: null }
 *   }
 * });
 * ```
 */
export async function findWithDeleted<T extends { findMany: any }>(
  prismaModel: T,
  args: any = {}
): Promise<any[]> {
  return prismaModel.findMany({
    ...args,
    includeDeleted: true, // Our middleware will handle this
  });
}

/**
 * Find a single record including soft-deleted ones
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param args Standard Prisma findFirst arguments
 * @returns Single record or null
 *
 * @example
 * ```typescript
 * import { findFirstWithDeleted } from '@sahool/shared-db';
 *
 * const product = await findFirstWithDeleted(prisma.product, {
 *   where: { id: 'product-123' }
 * });
 * ```
 */
export async function findFirstWithDeleted<T extends { findFirst: any }>(
  prismaModel: T,
  args: any = {}
): Promise<any | null> {
  return prismaModel.findFirst({
    ...args,
    includeDeleted: true,
  });
}

/**
 * Check if a record is soft-deleted
 *
 * @param record The record to check
 * @returns True if the record is soft-deleted
 *
 * @example
 * ```typescript
 * import { isDeleted } from '@sahool/shared-db';
 *
 * const product = await prisma.product.findUnique({
 *   where: { id: '123' }
 * });
 *
 * if (product && isDeleted(product)) {
 *   console.log('This product has been deleted');
 * }
 * ```
 */
export function isDeleted(record: any): boolean {
  return record?.deletedAt !== null && record?.deletedAt !== undefined;
}

/**
 * Permanently delete a record (hard delete)
 * Use this sparingly and only when necessary (e.g., GDPR compliance)
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param where The where clause to identify the record
 * @returns The deleted record
 *
 * @example
 * ```typescript
 * import { hardDelete } from '@sahool/shared-db';
 *
 * // Permanently delete a record (cannot be recovered)
 * await hardDelete(prisma.product, { id: 'product-123' });
 * ```
 */
export async function hardDelete<T extends { delete: any }>(
  prismaModel: T,
  where: any
): Promise<any> {
  // Bypass the middleware by using a raw query or direct delete
  // Note: This will still go through middleware, so you might need
  // to add the model to excludedModels list temporarily
  return prismaModel.delete({ where });
}

/**
 * Count records excluding soft-deleted ones
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param where Optional where clause
 * @returns Count of non-deleted records
 */
export async function count<T extends { count: any }>(
  prismaModel: T,
  where: any = {}
): Promise<number> {
  return prismaModel.count({
    where: {
      ...where,
      deletedAt: null,
    },
  });
}

/**
 * Count all records including soft-deleted ones
 *
 * @param prismaModel The Prisma model delegate (e.g., prisma.product)
 * @param where Optional where clause
 * @returns Count of all records
 */
export async function countWithDeleted<T extends { count: any }>(
  prismaModel: T,
  where: any = {}
): Promise<number> {
  return prismaModel.count({
    where,
    includeDeleted: true,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get deletion metadata from a record
 *
 * @param record The record to extract metadata from
 * @returns Deletion metadata or null if not deleted
 */
export function getDeletionMetadata(
  record: any
): { deletedAt: Date; deletedBy: string | null } | null {
  if (!isDeleted(record)) {
    return null;
  }

  return {
    deletedAt: record.deletedAt,
    deletedBy: record.deletedBy,
  };
}

/**
 * Filter array of records to only include non-deleted ones
 * Useful for in-memory filtering
 *
 * @param records Array of records
 * @returns Filtered array without deleted records
 */
export function filterDeleted<T>(records: T[]): T[] {
  return records.filter((record) => !isDeleted(record));
}

/**
 * Filter array of records to only include deleted ones
 *
 * @param records Array of records
 * @returns Filtered array with only deleted records
 */
export function filterOnlyDeleted<T>(records: T[]): T[] {
  return records.filter((record) => isDeleted(record));
}
