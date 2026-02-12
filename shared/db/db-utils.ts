/**
 * SAHOOL Shared Database Utilities
 * أدوات قاعدة البيانات المشتركة سهول
 *
 * Consolidated database utilities used across all services to ensure
 * consistency, performance, and security.
 *
 * أدوات قاعدة البيانات الموحدة المستخدمة عبر جميع الخدمات لضمان
 * التناسق والأداء والأمان.
 */

import { Logger } from '@nestjs/common';
import { Prisma } from '@prisma/client';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface PaginationParams {
  page?: number;
  limit?: number;
  take?: number;
  skip?: number;
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

export interface CursorPaginationParams {
  cursor?: string;
  limit?: number;
  take?: number;
}

export interface CursorPaginationMeta {
  limit: number;
  hasNext: boolean;
  nextCursor: string | null;
}

export interface CursorPaginatedResponse<T> {
  data: T[];
  meta: CursorPaginationMeta;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

export const MAX_PAGE_SIZE = 100;
export const DEFAULT_PAGE_SIZE = 20;
export const DEFAULT_QUERY_TIMEOUT = 30000; // 30 seconds
export const SLOW_QUERY_THRESHOLD = 1000; // 1 second
export const VERY_SLOW_QUERY_THRESHOLD = 5000; // 5 seconds

/**
 * Transaction configuration for different operation types
 * تكوينات المعاملات لأنواع العمليات المختلفة
 */
export const TRANSACTION_CONFIGS = {
  /**
   * Financial transactions (highest isolation level)
   * المعاملات المالية - مستوى عزل عالي
   */
  FINANCIAL: {
    maxWait: 10000, // 10 seconds max wait for transaction slot
    timeout: 30000, // 30 seconds transaction timeout
    isolationLevel: Prisma.TransactionIsolationLevel.Serializable,
  },

  /**
   * General write operations
   * عمليات الكتابة العامة
   */
  GENERAL: {
    maxWait: 5000, // 5 seconds max wait
    timeout: 15000, // 15 seconds timeout
    isolationLevel: Prisma.TransactionIsolationLevel.ReadCommitted,
  },

  /**
   * Read operations (low isolation level)
   * عمليات القراءة - مستوى عزل منخفض
   */
  READ: {
    maxWait: 2000, // 2 seconds max wait
    timeout: 5000, // 5 seconds timeout
    isolationLevel: Prisma.TransactionIsolationLevel.ReadCommitted,
  },

  /**
   * Batch operations (longer timeout)
   * العمليات الجماعية - مهلة أطول
   */
  BATCH: {
    maxWait: 15000, // 15 seconds max wait
    timeout: 60000, // 60 seconds timeout
    isolationLevel: Prisma.TransactionIsolationLevel.ReadCommitted,
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// Pagination Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate pagination parameters with enforced limits
 * حساب معلمات الترقيم مع فرض الحدود
 *
 * @param params - Pagination parameters
 * @returns Normalized pagination params
 */
export function calculatePagination(params?: PaginationParams): {
  skip: number;
  take: number;
  page: number;
} {
  // Normalize page (minimum 1)
  const page = Math.max(1, params?.page || 1);

  // Get requested limit from multiple possible param names
  const requestedLimit = params?.limit || params?.take || DEFAULT_PAGE_SIZE;

  // Enforce min/max limits
  const take = Math.min(Math.max(1, requestedLimit), MAX_PAGE_SIZE);

  // Calculate skip (0-indexed)
  const skip = params?.skip !== undefined ? params.skip : (page - 1) * take;

  return { skip, take, page };
}

/**
 * Build pagination metadata
 * بناء بيانات الترقيم الوصفية
 *
 * @param total - Total record count
 * @param params - Current pagination params
 * @returns Pagination metadata
 */
export function buildPaginationMeta(
  total: number,
  params: { page: number; take: number }
): PaginationMeta {
  const totalPages = Math.max(1, Math.ceil(total / params.take));

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
 *
 * @param data - Data array
 * @param total - Total record count
 * @param params - Pagination params
 * @returns Paginated response object
 */
export function createPaginatedResponse<T>(
  data: T[],
  total: number,
  params: { page: number; take: number }
): PaginatedResponse<T> {
  return {
    data,
    meta: buildPaginationMeta(total, params),
  };
}

/**
 * Build cursor pagination metadata
 * بناء بيانات ترقيم المؤشر
 *
 * @param data - Data array
 * @param limit - Requested limit
 * @param getCursor - Function to extract cursor from record
 * @returns Cursor pagination metadata
 */
export function buildCursorPaginationMeta<T>(
  data: T[],
  limit: number,
  getCursor: (item: T) => string
): CursorPaginationMeta {
  const hasNext = data.length > limit;
  const trimmedData = hasNext ? data.slice(0, -1) : data;
  const nextCursor = hasNext && trimmedData.length > 0
    ? getCursor(trimmedData[trimmedData.length - 1])
    : null;

  return {
    limit,
    hasNext,
    nextCursor,
  };
}

/**
 * Create cursor-based paginated response
 * إنشاء استجابة مرقمة بالمؤشر
 *
 * @param data - Data array
 * @param limit - Requested limit
 * @param getCursor - Function to extract cursor from record
 * @returns Cursor paginated response
 */
export function createCursorPaginatedResponse<T>(
  data: T[],
  limit: number,
  getCursor: (item: T) => string
): CursorPaginatedResponse<T> {
  const hasNext = data.length > limit;
  const trimmedData = hasNext ? data.slice(0, -1) : data;

  return {
    data: trimmedData,
    meta: buildCursorPaginationMeta(data, limit, getCursor),
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Query Logging & Performance Monitoring
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create query logger for Prisma
 * إنشاء مسجل استعلامات لـ Prisma
 *
 * @param logger - Logger instance
 * @param serviceName - Name of the service (for context)
 * @returns Query event handler
 */
export function createQueryLogger(logger: Logger, serviceName: string) {
  return (event: any) => {
    const duration = event.duration || 0;
    const query = event.query || '';
    const params = event.params || '';

    // Log very slow queries as warnings
    if (duration > VERY_SLOW_QUERY_THRESHOLD) {
      logger.warn(
        `[${serviceName}] VERY SLOW QUERY (${duration}ms): ${query.substring(0, 200)}... | Params: ${params}`,
        'DatabasePerformance'
      );
    }
    // Log slow queries as info
    else if (duration > SLOW_QUERY_THRESHOLD) {
      logger.log(
        `[${serviceName}] Slow query (${duration}ms): ${query.substring(0, 200)}...`,
        'DatabasePerformance'
      );
    }

    // Log all queries in debug mode
    if (process.env.LOG_LEVEL === 'debug') {
      logger.debug(
        `[${serviceName}] Query (${duration}ms): ${query.substring(0, 100)}...`,
        'DatabaseQuery'
      );
    }
  };
}

/**
 * Measure query execution time
 * قياس وقت تنفيذ الاستعلام
 *
 * @param queryFn - Query function to measure
 * @param logger - Logger instance
 * @param queryName - Name of the query (for logging)
 * @returns Query result
 */
export async function measureQueryTime<T>(
  queryFn: () => Promise<T>,
  logger?: Logger,
  queryName?: string
): Promise<T> {
  const start = Date.now();
  try {
    const result = await queryFn();
    const duration = Date.now() - start;

    if (logger) {
      if (duration > VERY_SLOW_QUERY_THRESHOLD) {
        logger.warn(
          `VERY SLOW QUERY [${queryName || 'unknown'}]: ${duration}ms`,
          'DatabasePerformance'
        );
      } else if (duration > SLOW_QUERY_THRESHOLD) {
        logger.log(
          `Slow query [${queryName || 'unknown'}]: ${duration}ms`,
          'DatabasePerformance'
        );
      }
    }

    return result;
  } catch (error) {
    const duration = Date.now() - start;
    if (logger) {
      logger.error(
        `Query [${queryName || 'unknown'}] failed after ${duration}ms: ${error}`,
        'DatabaseError'
      );
    }
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Common Select Fields (Privacy & Security)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Common select patterns to exclude sensitive fields
 * أنماط الاختيار الشائعة لاستبعاد الحقول الحساسة
 */
export const CommonSelects = {
  /**
   * Exclude password fields from User model
   * استبعاد حقول كلمة المرور من نموذج المستخدم
   */
  userPublic: {
    id: true,
    email: true,
    firstName: true,
    lastName: true,
    phone: true,
    status: true,
    role: true,
    createdAt: true,
    updatedAt: true,
    // Explicitly exclude sensitive fields
    passwordHash: false,
    passwordResetToken: false,
    failedLoginAttempts: false,
    lockoutUntil: false,
  },

  /**
   * Timestamps only
   * الطوابع الزمنية فقط
   */
  timestamps: {
    createdAt: true,
    updatedAt: true,
  },

  /**
   * Audit fields
   * حقول التدقيق
   */
  auditFields: {
    createdAt: true,
    updatedAt: true,
    createdBy: true,
    updatedBy: true,
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Soft Delete Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Standard soft delete where clause
 * جملة where القياسية للحذف الناعم
 */
export const NOT_DELETED = {
  deletedAt: null,
};

/**
 * Include soft-deleted records
 * تضمين السجلات المحذوفة ناعماً
 */
export const INCLUDE_DELETED = {};

/**
 * Only soft-deleted records
 * السجلات المحذوفة ناعماً فقط
 */
export const ONLY_DELETED = {
  deletedAt: { not: null },
};

// ═══════════════════════════════════════════════════════════════════════════
// Error Handling
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if error is a unique constraint violation
 * التحقق مما إذا كان الخطأ انتهاكاً لقيد فريد
 *
 * @param error - Error to check
 * @returns True if unique constraint violation
 */
export function isUniqueConstraintError(error: any): boolean {
  return (
    error?.code === 'P2002' || // Prisma unique constraint error
    error?.constraint?.includes('unique') ||
    error?.message?.includes('unique constraint')
  );
}

/**
 * Check if error is a foreign key constraint violation
 * التحقق مما إذا كان الخطأ انتهاكاً لقيد المفتاح الأجنبي
 *
 * @param error - Error to check
 * @returns True if foreign key constraint violation
 */
export function isForeignKeyConstraintError(error: any): boolean {
  return (
    error?.code === 'P2003' || // Prisma foreign key constraint error
    error?.constraint?.includes('foreign') ||
    error?.message?.includes('foreign key constraint')
  );
}

/**
 * Check if error is a record not found error
 * التحقق مما إذا كان الخطأ خطأ عدم العثور على سجل
 *
 * @param error - Error to check
 * @returns True if record not found
 */
export function isRecordNotFoundError(error: any): boolean {
  return (
    error?.code === 'P2025' || // Prisma record not found
    error?.message?.includes('Record to') && error?.message?.includes('not found')
  );
}

/**
 * Extract constraint field from unique constraint error
 * استخراج حقل القيد من خطأ القيد الفريد
 *
 * @param error - Error to parse
 * @returns Field name that caused the constraint violation
 */
export function extractConstraintField(error: any): string | null {
  if (!isUniqueConstraintError(error)) {
    return null;
  }

  // Prisma unique constraint error includes target field
  if (error?.meta?.target && Array.isArray(error.meta.target)) {
    return error.meta.target.join(', ');
  }

  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// Security Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sanitize search input to prevent SQL injection
 * تطهير إدخال البحث لمنع حقن SQL
 *
 * @param input - User input string
 * @returns Sanitized string safe for use in queries
 */
export function sanitizeSearchInput(input: string): string {
  if (!input) return '';

  // Remove potential SQL injection patterns
  return input
    .replace(/['";]/g, '') // Remove quotes and semicolons
    .replace(/--/g, '') // Remove SQL comments
    .replace(/\/\*/g, '') // Remove block comment starts
    .replace(/\*\//g, '') // Remove block comment ends
    .trim()
    .substring(0, 200); // Limit length
}

/**
 * Build safe search filter for text fields
 * بناء مرشح بحث آمن لحقول النص
 *
 * @param field - Field name to search
 * @param search - Search term
 * @param mode - Search mode (default: 'insensitive')
 * @returns Prisma where clause
 */
export function buildSafeSearchFilter(
  field: string,
  search: string,
  mode: 'default' | 'insensitive' = 'insensitive'
): Record<string, any> {
  const sanitized = sanitizeSearchInput(search);
  if (!sanitized) return {};

  return {
    [field]: {
      contains: sanitized,
      mode,
    },
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export all utilities
// ═══════════════════════════════════════════════════════════════════════════

export default {
  // Pagination
  calculatePagination,
  buildPaginationMeta,
  createPaginatedResponse,
  buildCursorPaginationMeta,
  createCursorPaginatedResponse,

  // Query logging
  createQueryLogger,
  measureQueryTime,

  // Common selects
  CommonSelects,

  // Soft delete
  NOT_DELETED,
  INCLUDE_DELETED,
  ONLY_DELETED,

  // Error handling
  isUniqueConstraintError,
  isForeignKeyConstraintError,
  isRecordNotFoundError,
  extractConstraintField,

  // Security
  sanitizeSearchInput,
  buildSafeSearchFilter,

  // Constants
  MAX_PAGE_SIZE,
  DEFAULT_PAGE_SIZE,
  SLOW_QUERY_THRESHOLD,
  VERY_SLOW_QUERY_THRESHOLD,
  TRANSACTION_CONFIGS,
};
