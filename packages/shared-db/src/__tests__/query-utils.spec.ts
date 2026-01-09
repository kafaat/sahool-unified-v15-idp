/**
 * اختبارات أدوات الاستعلام والتقسيم
 * Query Utilities Tests
 *
 * Tests for pagination, cursor pagination, query logging, and batch operations.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
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
} from '../query-utils';

// ─────────────────────────────────────────────────────────────────────────────
// Constants Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('Query Utils Constants', () => {
  it('should have correct default values', () => {
    expect(MAX_PAGE_SIZE).toBe(100);
    expect(DEFAULT_PAGE_SIZE).toBe(20);
    expect(DEFAULT_QUERY_TIMEOUT).toBe(5000);
    expect(CRITICAL_WRITE_TIMEOUT).toBe(10000);
    expect(SLOW_QUERY_THRESHOLD).toBe(1000);
  });

  it('should have correct transaction configs', () => {
    expect(FINANCIAL_TRANSACTION_CONFIG.isolationLevel).toBe('Serializable');
    expect(FINANCIAL_TRANSACTION_CONFIG.timeout).toBe(10000);

    expect(GENERAL_TRANSACTION_CONFIG.isolationLevel).toBe('ReadCommitted');
    expect(GENERAL_TRANSACTION_CONFIG.timeout).toBe(5000);

    expect(READ_TRANSACTION_CONFIG.isolationLevel).toBe('ReadCommitted');
    expect(READ_TRANSACTION_CONFIG.timeout).toBe(3000);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Offset Pagination Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('calculatePagination', () => {
  it('should return defaults when no params provided', () => {
    const result = calculatePagination();

    expect(result.skip).toBe(0);
    expect(result.take).toBe(DEFAULT_PAGE_SIZE);
    expect(result.page).toBe(1);
  });

  it('should calculate skip based on page number', () => {
    const result = calculatePagination({ page: 3, limit: 10 });

    expect(result.skip).toBe(20); // (3-1) * 10
    expect(result.take).toBe(10);
    expect(result.page).toBe(3);
  });

  it('should enforce MAX_PAGE_SIZE limit', () => {
    const result = calculatePagination({ limit: 500 });

    expect(result.take).toBe(MAX_PAGE_SIZE);
  });

  it('should handle skip/take pattern', () => {
    const result = calculatePagination({ skip: 50, take: 25 });

    expect(result.skip).toBe(50);
    expect(result.take).toBe(25);
  });

  it('should prioritize skip over page calculation', () => {
    const result = calculatePagination({ page: 2, skip: 100, limit: 10 });

    expect(result.skip).toBe(100);
  });
});

describe('buildPaginationMeta', () => {
  it('should calculate totalPages correctly', () => {
    const meta = buildPaginationMeta(100, 1, 10);

    expect(meta.totalPages).toBe(10);
    expect(meta.total).toBe(100);
    expect(meta.page).toBe(1);
    expect(meta.limit).toBe(10);
  });

  it('should round up totalPages', () => {
    const meta = buildPaginationMeta(25, 1, 10);

    expect(meta.totalPages).toBe(3); // 25/10 = 2.5 → 3
  });

  it('should set hasNext correctly', () => {
    expect(buildPaginationMeta(100, 1, 10).hasNext).toBe(true);
    expect(buildPaginationMeta(100, 10, 10).hasNext).toBe(false);
    expect(buildPaginationMeta(100, 5, 10).hasNext).toBe(true);
  });

  it('should set hasPrev correctly', () => {
    expect(buildPaginationMeta(100, 1, 10).hasPrev).toBe(false);
    expect(buildPaginationMeta(100, 2, 10).hasPrev).toBe(true);
    expect(buildPaginationMeta(100, 10, 10).hasPrev).toBe(true);
  });
});

describe('createPaginatedResponse', () => {
  it('should create response with data and meta', () => {
    const data = [{ id: 1 }, { id: 2 }];
    const response = createPaginatedResponse(data, 50, { page: 1, limit: 10 });

    expect(response.data).toBe(data);
    expect(response.meta.total).toBe(50);
    expect(response.meta.totalPages).toBe(5);
  });

  it('should use defaults when no params provided', () => {
    const data = [{ id: 1 }];
    const response = createPaginatedResponse(data, 100);

    expect(response.meta.limit).toBe(DEFAULT_PAGE_SIZE);
    expect(response.meta.page).toBe(1);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Cursor Pagination Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('buildCursorPagination', () => {
  it('should return take with +1 for hasMore check', () => {
    const options = buildCursorPagination({ limit: 10 });

    expect(options.take).toBe(11); // 10 + 1
  });

  it('should include cursor and skip when cursor provided', () => {
    const options = buildCursorPagination({ cursor: 'abc123', limit: 10 });

    expect(options.cursor).toEqual({ id: 'abc123' });
    expect(options.skip).toBe(1);
  });

  it('should enforce MAX_PAGE_SIZE', () => {
    const options = buildCursorPagination({ limit: 200 });

    expect(options.take).toBe(MAX_PAGE_SIZE + 1);
  });

  it('should use default limit when not provided', () => {
    const options = buildCursorPagination();

    expect(options.take).toBe(DEFAULT_PAGE_SIZE + 1);
  });
});

describe('processCursorResults', () => {
  it('should detect hasMore when extra item present', () => {
    const results = [
      { id: '1' },
      { id: '2' },
      { id: '3' },
    ];

    const response = processCursorResults(results, 2);

    expect(response.hasMore).toBe(true);
    expect(response.data.length).toBe(2);
    expect(response.nextCursor).toBe('2');
  });

  it('should set hasMore false when no extra item', () => {
    const results = [{ id: '1' }, { id: '2' }];

    const response = processCursorResults(results, 5);

    expect(response.hasMore).toBe(false);
    expect(response.data.length).toBe(2);
    expect(response.nextCursor).toBeNull();
  });

  it('should handle empty results', () => {
    const response = processCursorResults([], 10);

    expect(response.hasMore).toBe(false);
    expect(response.data.length).toBe(0);
    expect(response.nextCursor).toBeNull();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Query Logging Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('createQueryLogger', () => {
  it('should call logger.warn for slow queries', () => {
    const mockLogger = { warn: vi.fn(), log: vi.fn() };
    const handler = createQueryLogger(mockLogger, 100);

    handler({
      timestamp: new Date(),
      query: 'SELECT * FROM users',
      params: '[]',
      duration: 200, // Above threshold
      target: 'prisma',
    });

    expect(mockLogger.warn).toHaveBeenCalledWith(
      'Slow query detected',
      expect.objectContaining({ duration: 200 })
    );
  });

  it('should not log queries below threshold', () => {
    const mockLogger = { warn: vi.fn(), log: vi.fn() };
    const handler = createQueryLogger(mockLogger, 100);

    handler({
      timestamp: new Date(),
      query: 'SELECT * FROM users',
      params: '[]',
      duration: 50, // Below threshold
      target: 'prisma',
    });

    expect(mockLogger.warn).not.toHaveBeenCalled();
  });

  it('should use console.warn when no logger provided', () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const handler = createQueryLogger(undefined, 100);

    handler({
      timestamp: new Date(),
      query: 'SELECT * FROM users WHERE long query here',
      params: '[]',
      duration: 200,
      target: 'prisma',
    });

    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });
});

describe('measureQueryTime', () => {
  it('should return query result', async () => {
    const queryFn = vi.fn().mockResolvedValue([{ id: 1 }]);

    const result = await measureQueryTime(queryFn, 'testQuery');

    expect(result).toEqual([{ id: 1 }]);
    expect(queryFn).toHaveBeenCalled();
  });

  it('should log slow queries', async () => {
    const mockLogger = { warn: vi.fn(), log: vi.fn() };
    const queryFn = vi.fn().mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve([]), 1100))
    );

    await measureQueryTime(queryFn, 'slowQuery', mockLogger);

    expect(mockLogger.warn).toHaveBeenCalledWith(
      'Slow query: slowQuery',
      expect.objectContaining({ threshold: expect.any(String) })
    );
  });

  it('should log and rethrow errors', async () => {
    const mockLogger = { warn: vi.fn(), log: vi.fn() };
    const error = new Error('Query failed');
    const queryFn = vi.fn().mockRejectedValue(error);

    await expect(measureQueryTime(queryFn, 'failingQuery', mockLogger)).rejects.toThrow('Query failed');
    expect(mockLogger.warn).toHaveBeenCalledWith(
      'Query failed: failingQuery',
      expect.objectContaining({ error: 'Query failed' })
    );
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Select Helper Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('createSelect', () => {
  it('should create select object from field array', () => {
    const select = createSelect(['id', 'name', 'email']);

    expect(select).toEqual({
      id: true,
      name: true,
      email: true,
    });
  });

  it('should handle empty array', () => {
    const select = createSelect([]);
    expect(select).toEqual({});
  });
});

describe('CommonSelects', () => {
  it('should have userBasic select', () => {
    expect(CommonSelects.userBasic.id).toBe(true);
    expect(CommonSelects.userBasic.email).toBe(true);
    expect(CommonSelects.userBasic.firstName).toBe(true);
    expect(CommonSelects.userBasic.lastName).toBe(true);
  });

  it('should have userMinimal select', () => {
    expect(CommonSelects.userMinimal.id).toBe(true);
    expect(CommonSelects.userMinimal.email).toBe(true);
    expect(Object.keys(CommonSelects.userMinimal).length).toBe(4);
  });

  it('should have productListing select', () => {
    expect(CommonSelects.productListing.id).toBe(true);
    expect(CommonSelects.productListing.name).toBe(true);
    expect(CommonSelects.productListing.price).toBe(true);
  });

  it('should have orderSummary select', () => {
    expect(CommonSelects.orderSummary.id).toBe(true);
    expect(CommonSelects.orderSummary.orderNumber).toBe(true);
    expect(CommonSelects.orderSummary.status).toBe(true);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Batch Operations Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('batchOperation', () => {
  it('should process items in batches', async () => {
    const items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const operation = vi.fn().mockResolvedValue('batch processed');

    const results = await batchOperation(items, 3, operation);

    expect(operation).toHaveBeenCalledTimes(4); // 3+3+3+1
    expect(results.length).toBe(4);
  });

  it('should pass correct batch to operation', async () => {
    const items = ['a', 'b', 'c', 'd', 'e'];
    const operation = vi.fn().mockResolvedValue('done');

    await batchOperation(items, 2, operation);

    expect(operation).toHaveBeenNthCalledWith(1, ['a', 'b']);
    expect(operation).toHaveBeenNthCalledWith(2, ['c', 'd']);
    expect(operation).toHaveBeenNthCalledWith(3, ['e']);
  });

  it('should handle empty array', async () => {
    const operation = vi.fn();

    const results = await batchOperation([], 10, operation);

    expect(operation).not.toHaveBeenCalled();
    expect(results).toEqual([]);
  });
});

describe('parallelLimit', () => {
  it('should process items with concurrency limit', async () => {
    const items = [1, 2, 3, 4, 5];
    let concurrent = 0;
    let maxConcurrent = 0;

    const operation = vi.fn().mockImplementation(async (item) => {
      concurrent++;
      maxConcurrent = Math.max(maxConcurrent, concurrent);
      await new Promise((r) => setTimeout(r, 50));
      concurrent--;
      return item * 2;
    });

    const results = await parallelLimit(items, 2, operation);

    expect(maxConcurrent).toBeLessThanOrEqual(2);
    expect(results.length).toBe(5);
  });

  it('should return results from all operations', async () => {
    const items = [1, 2, 3];
    const operation = vi.fn().mockImplementation(async (item) => item * 2);

    const results = await parallelLimit(items, 5, operation);

    expect(results).toContain(2);
    expect(results).toContain(4);
    expect(results).toContain(6);
  });

  it('should handle empty array', async () => {
    const operation = vi.fn();

    const results = await parallelLimit([], 5, operation);

    expect(operation).not.toHaveBeenCalled();
    expect(results).toEqual([]);
  });
});
