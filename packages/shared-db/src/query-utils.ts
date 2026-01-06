/**
 * Query Utilities for SAHOOL Platform
 * Shared database query optimization patterns
 *
 * Features:
 * - Pagination with configurable limits
 * - Query timeout configurations
 * - Cursor-based pagination helpers
 * - Query performance logging
 */

// ═══════════════════════════════════════════════════════════════════════════
// Configuration Constants
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Maximum allowed page size to prevent memory exhaustion
 */
export const MAX_PAGE_SIZE = 100;

/**
 * Default page size when not specified
 */
export const DEFAULT_PAGE_SIZE = 20;

/**
 * Default query timeout for non-critical read operations (5 seconds)
 */
export const DEFAULT_QUERY_TIMEOUT = 5000;

/**
 * Timeout for critical write operations (10 seconds)
 */
export const CRITICAL_WRITE_TIMEOUT = 10000;

/**
 * Slow query threshold for logging (1 second)
 */
export const SLOW_QUERY_THRESHOLD = 1000;

// ═══════════════════════════════════════════════════════════════════════════
// Transaction Configuration Presets
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Transaction isolation levels
 */
export type TransactionIsolationLevel =
  | 'ReadUncommitted'
  | 'ReadCommitted'
  | 'RepeatableRead'
  | 'Serializable';

/**
 * Configuration for financial transactions requiring SERIALIZABLE isolation
 */
export const FINANCIAL_TRANSACTION_CONFIG: {
  isolationLevel: TransactionIsolationLevel;
  maxWait: number;
  timeout: number;
} = {
  isolationLevel: 'Serializable',
  maxWait: 5000,
  timeout: 10000,
};

/**
 * Configuration for general business transactions
 */
export const GENERAL_TRANSACTION_CONFIG: {
  isolationLevel: TransactionIsolationLevel;
  maxWait: number;
  timeout: number;
} = {
  isolationLevel: 'ReadCommitted',
  maxWait: 3000,
  timeout: 5000,
};

/**
 * Configuration for read-only transactions
 */
export const READ_TRANSACTION_CONFIG: {
  isolationLevel: TransactionIsolationLevel;
  maxWait: number;
  timeout: number;
} = {
  isolationLevel: 'ReadCommitted',
  maxWait: 2000,
  timeout: 3000,
};

// ═══════════════════════════════════════════════════════════════════════════
// Pagination Utilities
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Parameters for offset-based pagination
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  skip?: number;
  take?: number;
}

/**
 * Metadata returned with paginated results
 */
export interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

/**
 * Calculate pagination parameters with enforced limits
 *
 * @param params - Pagination parameters
 * @returns Validated skip and take values
 *
 * @example
 * ```typescript
 * const { skip, take } = calculatePagination({ page: 2, limit: 50 });
 * const users = await prisma.user.findMany({ skip, take });
 * ```
 */
export function calculatePagination(params?: PaginationParams): {
  skip: number;
  take: number;
  page: number;
} {
  // Support both page/limit and skip/take patterns
  const page = params?.page || 1;
  const limit = Math.min(
    params?.limit || params?.take || DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE
  );
  const skip = params?.skip !== undefined ? params.skip : (page - 1) * limit;

  return {
    skip,
    take: limit,
    page,
  };
}

/**
 * Build pagination metadata
 *
 * @param total - Total count of items
 * @param page - Current page number
 * @param limit - Items per page
 * @returns Pagination metadata
 *
 * @example
 * ```typescript
 * const [data, total] = await Promise.all([
 *   prisma.user.findMany({ skip, take }),
 *   prisma.user.count({ where })
 * ]);
 * return { data, meta: buildPaginationMeta(total, page, limit) };
 * ```
 */
export function buildPaginationMeta(
  total: number,
  page: number,
  limit: number
): PaginationMeta {
  const totalPages = Math.ceil(total / limit);
  return {
    total,
    page,
    limit,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
  };
}

/**
 * Create a paginated response with data and metadata
 *
 * @param data - Array of items
 * @param total - Total count
 * @param params - Pagination parameters
 * @returns Paginated response
 */
export function createPaginatedResponse<T>(
  data: T[],
  total: number,
  params?: PaginationParams
): PaginatedResponse<T> {
  const { page, take } = calculatePagination(params);
  return {
    data,
    meta: buildPaginationMeta(total, page, take),
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Cursor-Based Pagination
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Parameters for cursor-based pagination
 */
export interface CursorPaginationParams {
  cursor?: string;
  limit?: number;
}

/**
 * Response for cursor-based pagination
 */
export interface CursorPaginatedResponse<T> {
  data: T[];
  nextCursor: string | null;
  hasMore: boolean;
}

/**
 * Build cursor pagination options for Prisma queries
 *
 * @param params - Cursor pagination parameters
 * @returns Prisma query options
 *
 * @example
 * ```typescript
 * const options = buildCursorPagination({ cursor: 'abc123', limit: 50 });
 * const messages = await prisma.message.findMany({
 *   where: { conversationId },
 *   orderBy: { createdAt: 'desc' },
 *   ...options
 * });
 * ```
 */
export function buildCursorPagination(params?: CursorPaginationParams): {
  take: number;
  cursor?: { id: string };
  skip?: number;
} {
  const limit = Math.min(
    params?.limit || DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE
  );

  const options: any = {
    take: limit + 1, // Fetch one extra to determine hasMore
  };

  if (params?.cursor) {
    options.cursor = { id: params.cursor };
    options.skip = 1; // Skip the cursor itself
  }

  return options;
}

/**
 * Process cursor pagination results
 *
 * @param results - Query results (should include one extra item)
 * @param limit - Requested limit
 * @returns Cursor paginated response
 *
 * @example
 * ```typescript
 * const results = await prisma.message.findMany({ ...options });
 * return processCursorResults(results, limit);
 * ```
 */
export function processCursorResults<T extends { id: string }>(
  results: T[],
  limit?: number
): CursorPaginatedResponse<T> {
  const effectiveLimit = Math.min(limit || DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE);
  const hasMore = results.length > effectiveLimit;
  const data = hasMore ? results.slice(0, effectiveLimit) : results;
  const nextCursor = hasMore && data.length > 0 ? data[data.length - 1].id : null;

  return {
    data,
    nextCursor,
    hasMore,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Query Performance Logging
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Query log entry
 */
export interface QueryLog {
  query: string;
  duration: number;
  params?: any;
  timestamp: Date;
}

/**
 * Logger interface for query logging
 */
export interface QueryLogger {
  warn(message: string, context?: any): void;
  log(message: string, context?: any): void;
}

/**
 * Query event from Prisma
 */
export interface PrismaQueryEvent {
  timestamp: Date;
  query: string;
  params: string;
  duration: number;
  target: string;
}

/**
 * Create a query logging function for Prisma client
 *
 * @param logger - Logger instance (e.g., NestJS Logger)
 * @param threshold - Slow query threshold in ms (default: 1000ms)
 * @returns Query event handler
 *
 * @example
 * ```typescript
 * const prisma = new PrismaClient({
 *   log: [
 *     { level: 'query', emit: 'event' },
 *     { level: 'error', emit: 'stdout' },
 *     { level: 'warn', emit: 'stdout' }
 *   ]
 * });
 *
 * const logger = new Logger('PrismaService');
 * prisma.$on('query', createQueryLogger(logger));
 * ```
 */
export function createQueryLogger(
  logger?: QueryLogger,
  threshold: number = SLOW_QUERY_THRESHOLD
) {
  return (e: PrismaQueryEvent) => {
    if (e.duration >= threshold) {
      const logEntry: QueryLog = {
        query: e.query,
        duration: e.duration,
        params: e.params,
        timestamp: new Date(),
      };

      if (logger?.warn) {
        logger.warn('Slow query detected', logEntry);
      } else {
        console.warn('⚠️  Slow query detected:', {
          duration: `${e.duration}ms`,
          query: e.query.substring(0, 100) + '...',
          params: e.params,
        });
      }
    }
  };
}

/**
 * Measure query execution time
 *
 * @param queryFn - Async function to measure
 * @param queryName - Name for logging
 * @param logger - Optional logger
 * @returns Query result
 *
 * @example
 * ```typescript
 * const users = await measureQueryTime(
 *   () => prisma.user.findMany({ where: { status: 'ACTIVE' } }),
 *   'findActiveUsers',
 *   logger
 * );
 * ```
 */
export async function measureQueryTime<T>(
  queryFn: () => Promise<T>,
  queryName: string,
  logger?: QueryLogger
): Promise<T> {
  const startTime = Date.now();
  try {
    const result = await queryFn();
    const duration = Date.now() - startTime;

    if (duration >= SLOW_QUERY_THRESHOLD && logger?.warn) {
      logger.warn(`Slow query: ${queryName}`, {
        duration: `${duration}ms`,
        threshold: `${SLOW_QUERY_THRESHOLD}ms`,
      });
    }

    return result;
  } catch (error) {
    const duration = Date.now() - startTime;
    if (logger?.warn) {
      logger.warn(`Query failed: ${queryName}`, {
        duration: `${duration}ms`,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Select Field Helpers
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create a select object from an array of field names
 * Useful for reducing over-fetching
 *
 * @param fields - Array of field names
 * @returns Prisma select object
 *
 * @example
 * ```typescript
 * const userFields = createSelect(['id', 'email', 'firstName', 'lastName']);
 * const user = await prisma.user.findUnique({
 *   where: { id },
 *   select: userFields
 * });
 * ```
 */
export function createSelect<T extends string>(
  fields: T[]
): Record<T, true> {
  return fields.reduce((acc, field) => {
    acc[field] = true;
    return acc;
  }, {} as Record<T, true>);
}

/**
 * Common select patterns for frequently used entities
 */
export const CommonSelects = {
  /**
   * Basic user fields (excluding sensitive data)
   */
  userBasic: createSelect([
    'id',
    'email',
    'firstName',
    'lastName',
    'role',
    'status',
    'createdAt',
    'updatedAt',
  ]),

  /**
   * User fields for listing (minimal)
   */
  userMinimal: createSelect([
    'id',
    'email',
    'firstName',
    'lastName',
  ]),

  /**
   * Product fields for listing
   */
  productListing: createSelect([
    'id',
    'name',
    'nameAr',
    'category',
    'price',
    'stock',
    'unit',
    'imageUrl',
    'featured',
    'createdAt',
  ]),

  /**
   * Order summary fields
   */
  orderSummary: createSelect([
    'id',
    'orderNumber',
    'status',
    'totalAmount',
    'createdAt',
    'updatedAt',
  ]),
};

// ═══════════════════════════════════════════════════════════════════════════
// Batch Operations
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Execute operations in batches to prevent overwhelming the database
 *
 * @param items - Array of items to process
 * @param batchSize - Number of items per batch
 * @param operation - Async operation to perform on each batch
 * @returns Array of results
 *
 * @example
 * ```typescript
 * const userIds = ['id1', 'id2', 'id3', ...]; // 1000 IDs
 * const results = await batchOperation(
 *   userIds,
 *   50,
 *   async (batch) => prisma.user.findMany({ where: { id: { in: batch } } })
 * );
 * ```
 */
export async function batchOperation<T, R>(
  items: T[],
  batchSize: number,
  operation: (batch: T[]) => Promise<R>
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const result = await operation(batch);
    results.push(result);
  }

  return results;
}

/**
 * Execute promises in parallel with concurrency limit
 *
 * @param items - Array of items
 * @param concurrency - Maximum concurrent operations
 * @param operation - Async operation for each item
 * @returns Array of results
 *
 * @example
 * ```typescript
 * const productIds = ['id1', 'id2', ...];
 * const products = await parallelLimit(
 *   productIds,
 *   5,
 *   async (id) => prisma.product.findUnique({ where: { id } })
 * );
 * ```
 */
export async function parallelLimit<T, R>(
  items: T[],
  concurrency: number,
  operation: (item: T) => Promise<R>
): Promise<R[]> {
  const results: R[] = [];
  const executing: Promise<void>[] = [];

  for (const item of items) {
    const promise = operation(item).then((result) => {
      results.push(result);
      executing.splice(executing.indexOf(promise), 1);
    });

    executing.push(promise);

    if (executing.length >= concurrency) {
      await Promise.race(executing);
    }
  }

  await Promise.all(executing);
  return results;
}

// ═══════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════

export default {
  // Constants
  MAX_PAGE_SIZE,
  DEFAULT_PAGE_SIZE,
  DEFAULT_QUERY_TIMEOUT,
  CRITICAL_WRITE_TIMEOUT,
  SLOW_QUERY_THRESHOLD,

  // Transaction configs
  FINANCIAL_TRANSACTION_CONFIG,
  GENERAL_TRANSACTION_CONFIG,
  READ_TRANSACTION_CONFIG,

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
};
