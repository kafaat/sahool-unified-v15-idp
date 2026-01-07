/**
 * Database Utilities for User Service
 * أدوات قاعدة البيانات لخدمة المستخدمين
 */

import { Logger } from '@nestjs/common';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface PaginationParams {
  page?: number;
  limit?: number;
  take?: number;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

export const MAX_PAGE_SIZE = 100;
export const DEFAULT_PAGE_SIZE = 20;
export const SLOW_QUERY_THRESHOLD = 1000;

/**
 * Transaction configuration for general operations
 */
export const GENERAL_TRANSACTION_CONFIG = {
  maxWait: 5000,
  timeout: 15000,
  isolationLevel: 'ReadCommitted' as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Common Select Fields
// ═══════════════════════════════════════════════════════════════════════════

export const CommonSelects = {
  /** User basic info (exclude password) */
  userBasic: {
    id: true,
    email: true,
    name: true,
    phone: true,
    status: true,
    roles: true,
    createdAt: true,
    updatedAt: true,
  },

  /** User with profile */
  userWithProfile: {
    id: true,
    email: true,
    name: true,
    phone: true,
    status: true,
    roles: true,
    createdAt: true,
    updatedAt: true,
    profile: true,
  },

  /** Timestamps only */
  timestamps: {
    createdAt: true,
    updatedAt: true,
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Pagination Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate pagination parameters with enforced limits
 */
export function calculatePagination(params?: PaginationParams): {
  skip: number;
  take: number;
  page: number;
} {
  const page = Math.max(1, params?.page || 1);
  const requestedLimit = params?.limit || params?.take || DEFAULT_PAGE_SIZE;
  const take = Math.min(Math.max(1, requestedLimit), MAX_PAGE_SIZE);
  const skip = (page - 1) * take;

  return { skip, take, page };
}

/**
 * Build pagination metadata
 */
export function buildPaginationMeta(
  total: number,
  params: { page: number; take: number },
): PaginationMeta {
  const totalPages = Math.ceil(total / params.take);

  return {
    page: params.page,
    limit: params.take,
    total,
    totalPages,
    hasNext: params.page < totalPages,
    hasPrev: params.page > 1,
  };
}

/**
 * Create paginated response
 */
export function createPaginatedResponse<T>(
  data: T[],
  total: number,
  params: { page: number; take: number },
): PaginatedResponse<T> {
  return {
    data,
    meta: buildPaginationMeta(total, params),
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Query Logging
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create query logger for Prisma
 */
export function createQueryLogger(logger: Logger) {
  return (event: any) => {
    const duration = event.duration || 0;
    if (duration > SLOW_QUERY_THRESHOLD) {
      logger.warn(
        `Slow query detected (${duration}ms): ${event.query?.substring(0, 200)}...`,
      );
    }
  };
}
