/**
 * Database Utilities for Marketplace Service
 * أدوات قاعدة البيانات لخدمة السوق
 *
 * Local implementation of pagination and query utilities
 * to avoid external package dependencies in Docker builds.
 */

import { Logger } from "@nestjs/common";

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
export const DEFAULT_QUERY_TIMEOUT = 30000; // 30 seconds
export const SLOW_QUERY_THRESHOLD = 1000; // 1 second

/**
 * Transaction configuration for financial operations
 * معاملة مالية - يتطلب مهلة أطول وعزل أعلى
 */
export const FINANCIAL_TRANSACTION_CONFIG = {
  maxWait: 10000, // 10 seconds max wait for transaction slot
  timeout: 30000, // 30 seconds transaction timeout
  isolationLevel: "Serializable" as const,
};

/**
 * Transaction configuration for general operations
 * معاملة عامة - إعدادات افتراضية
 */
export const GENERAL_TRANSACTION_CONFIG = {
  maxWait: 5000, // 5 seconds max wait
  timeout: 15000, // 15 seconds timeout
  isolationLevel: "ReadCommitted" as const,
};

/**
 * Transaction configuration for read operations
 * معاملة قراءة - مهلة قصيرة
 */
export const READ_TRANSACTION_CONFIG = {
  maxWait: 2000, // 2 seconds max wait
  timeout: 5000, // 5 seconds timeout
  isolationLevel: "ReadCommitted" as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Pagination Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate pagination parameters with enforced limits
 * حساب معلمات الترقيم مع فرض الحدود
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
 * بناء بيانات الترقيم الوصفية
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
 * إنشاء استجابة مرقمة
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
 * إنشاء مسجل استعلامات لـ Prisma
 */
export function createQueryLogger(logger: Logger) {
  return (event: any) => {
    const duration = event.duration || 0;

    // Only log slow queries (> 1 second)
    if (duration > SLOW_QUERY_THRESHOLD) {
      logger.warn(
        `Slow query detected (${duration}ms): ${event.query?.substring(0, 200)}...`,
      );
    }
  };
}

/**
 * Measure query execution time
 * قياس وقت تنفيذ الاستعلام
 */
export async function measureQueryTime<T>(
  queryFn: () => Promise<T>,
  logger?: Logger,
  queryName?: string,
): Promise<T> {
  const start = Date.now();
  try {
    const result = await queryFn();
    const duration = Date.now() - start;

    if (logger && duration > SLOW_QUERY_THRESHOLD) {
      logger.warn(`Slow query ${queryName || "unknown"}: ${duration}ms`);
    }

    return result;
  } catch (error) {
    const duration = Date.now() - start;
    if (logger) {
      logger.error(
        `Query ${queryName || "unknown"} failed after ${duration}ms`,
      );
    }
    throw error;
  }
}
