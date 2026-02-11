/**
 * SAHOOL Shared Database Utilities Tests
 * اختبارات أدوات قاعدة البيانات المشتركة سهول
 *
 * Unit tests for shared database utilities to ensure consistent behavior
 * across all services.
 */

import { describe, it, expect } from 'vitest';
import {
  calculatePagination,
  buildPaginationMeta,
  createPaginatedResponse,
  buildCursorPaginationMeta,
  createCursorPaginatedResponse,
  sanitizeSearchInput,
  buildSafeSearchFilter,
  isUniqueConstraintError,
  isForeignKeyConstraintError,
  isRecordNotFoundError,
  extractConstraintField,
  MAX_PAGE_SIZE,
  DEFAULT_PAGE_SIZE,
  NOT_DELETED,
  INCLUDE_DELETED,
  ONLY_DELETED,
} from '../../../shared/db/db-utils';

describe('Database Utilities - Pagination', () => {
  describe('calculatePagination', () => {
    it('should return default pagination when no params provided', () => {
      const result = calculatePagination();
      expect(result).toEqual({
        skip: 0,
        take: DEFAULT_PAGE_SIZE,
        page: 1,
      });
    });

    it('should calculate correct skip and take for page 2', () => {
      const result = calculatePagination({ page: 2, limit: 10 });
      expect(result).toEqual({
        skip: 10,
        take: 10,
        page: 2,
      });
    });

    it('should enforce max page size limit', () => {
      const result = calculatePagination({ limit: 500 });
      expect(result.take).toBe(MAX_PAGE_SIZE);
    });

    it('should enforce minimum page size of 1', () => {
      const result = calculatePagination({ limit: -5 });
      expect(result.take).toBe(1);
    });

    it('should enforce minimum page number of 1', () => {
      const result = calculatePagination({ page: -1 });
      expect(result.page).toBe(1);
      expect(result.skip).toBe(0);
    });

    it('should accept take parameter as alias for limit', () => {
      const result = calculatePagination({ take: 50 });
      expect(result.take).toBe(50);
    });

    it('should prioritize limit over take when both provided', () => {
      const result = calculatePagination({ limit: 30, take: 50 });
      expect(result.take).toBe(30);
    });

    it('should handle custom skip parameter', () => {
      const result = calculatePagination({ skip: 100, take: 10 });
      expect(result.skip).toBe(100);
      expect(result.page).toBe(1); // Page calculated from skip
    });
  });

  describe('buildPaginationMeta', () => {
    it('should build correct metadata for first page', () => {
      const meta = buildPaginationMeta(100, { page: 1, take: 20 });
      expect(meta).toEqual({
        page: 1,
        limit: 20,
        total: 100,
        totalPages: 5,
        hasNext: true,
        hasPrev: false,
      });
    });

    it('should build correct metadata for middle page', () => {
      const meta = buildPaginationMeta(100, { page: 3, take: 20 });
      expect(meta).toEqual({
        page: 3,
        limit: 20,
        total: 100,
        totalPages: 5,
        hasNext: true,
        hasPrev: true,
      });
    });

    it('should build correct metadata for last page', () => {
      const meta = buildPaginationMeta(100, { page: 5, take: 20 });
      expect(meta).toEqual({
        page: 5,
        limit: 20,
        total: 100,
        totalPages: 5,
        hasNext: false,
        hasPrev: true,
      });
    });

    it('should handle partial last page correctly', () => {
      const meta = buildPaginationMeta(95, { page: 5, take: 20 });
      expect(meta).toEqual({
        page: 5,
        limit: 20,
        total: 95,
        totalPages: 5,
        hasNext: false,
        hasPrev: true,
      });
    });

    it('should handle empty results', () => {
      const meta = buildPaginationMeta(0, { page: 1, take: 20 });
      expect(meta).toEqual({
        page: 1,
        limit: 20,
        total: 0,
        totalPages: 1,
        hasNext: false,
        hasPrev: false,
      });
    });
  });

  describe('createPaginatedResponse', () => {
    it('should create complete paginated response', () => {
      const data = [{ id: 1 }, { id: 2 }, { id: 3 }];
      const response = createPaginatedResponse(data, 50, { page: 2, take: 3 });

      expect(response.data).toBe(data);
      expect(response.meta).toEqual({
        page: 2,
        limit: 3,
        total: 50,
        totalPages: 17,
        hasNext: true,
        hasPrev: true,
      });
    });
  });

  describe('buildCursorPaginationMeta', () => {
    it('should build metadata with next cursor when more results exist', () => {
      const data = [
        { id: '1' },
        { id: '2' },
        { id: '3' },
        { id: '4' }, // Extra item indicates more results
      ];
      const meta = buildCursorPaginationMeta(data, 3, (item) => item.id);

      expect(meta).toEqual({
        limit: 3,
        hasNext: true,
        nextCursor: '3', // Last item of trimmed data
      });
    });

    it('should build metadata without next cursor when no more results', () => {
      const data = [{ id: '1' }, { id: '2' }];
      const meta = buildCursorPaginationMeta(data, 3, (item) => item.id);

      expect(meta).toEqual({
        limit: 3,
        hasNext: false,
        nextCursor: null,
      });
    });
  });

  describe('createCursorPaginatedResponse', () => {
    it('should create cursor paginated response trimming extra item', () => {
      const data = [
        { id: '1' },
        { id: '2' },
        { id: '3' },
        { id: '4' }, // This should be trimmed
      ];
      const response = createCursorPaginatedResponse(data, 3, (item) => item.id);

      expect(response.data).toHaveLength(3);
      expect(response.data).toEqual([{ id: '1' }, { id: '2' }, { id: '3' }]);
      expect(response.meta.hasNext).toBe(true);
      expect(response.meta.nextCursor).toBe('3');
    });

    it('should handle exact limit without trimming', () => {
      const data = [{ id: '1' }, { id: '2' }];
      const response = createCursorPaginatedResponse(data, 3, (item) => item.id);

      expect(response.data).toHaveLength(2);
      expect(response.meta.hasNext).toBe(false);
      expect(response.meta.nextCursor).toBeNull();
    });
  });
});

describe('Database Utilities - Security', () => {
  describe('sanitizeSearchInput', () => {
    it('should remove SQL injection patterns', () => {
      const malicious = "'; DROP TABLE users; --";
      const sanitized = sanitizeSearchInput(malicious);
      expect(sanitized).not.toContain("'");
      expect(sanitized).not.toContain(';');
      expect(sanitized).not.toContain('--');
    });

    it('should remove block comment patterns', () => {
      const malicious = '/* comment */ SELECT';
      const sanitized = sanitizeSearchInput(malicious);
      expect(sanitized).not.toContain('/*');
      expect(sanitized).not.toContain('*/');
    });

    it('should limit length to 200 characters', () => {
      const longInput = 'a'.repeat(500);
      const sanitized = sanitizeSearchInput(longInput);
      expect(sanitized.length).toBe(200);
    });

    it('should trim whitespace', () => {
      const input = '  search term  ';
      const sanitized = sanitizeSearchInput(input);
      expect(sanitized).toBe('search term');
    });

    it('should handle empty input', () => {
      expect(sanitizeSearchInput('')).toBe('');
      expect(sanitizeSearchInput(null as any)).toBe('');
      expect(sanitizeSearchInput(undefined as any)).toBe('');
    });

    it('should preserve safe search terms', () => {
      const safe = 'wheat seeds 2026';
      const sanitized = sanitizeSearchInput(safe);
      expect(sanitized).toBe(safe);
    });
  });

  describe('buildSafeSearchFilter', () => {
    it('should build safe filter for valid input', () => {
      const filter = buildSafeSearchFilter('name', 'wheat');
      expect(filter).toEqual({
        name: {
          contains: 'wheat',
          mode: 'insensitive',
        },
      });
    });

    it('should sanitize malicious input', () => {
      const filter = buildSafeSearchFilter('name', "'; DROP TABLE; --");
      expect(filter.name.contains).not.toContain("'");
      expect(filter.name.contains).not.toContain(';');
    });

    it('should return empty object for empty input', () => {
      const filter = buildSafeSearchFilter('name', '');
      expect(filter).toEqual({});
    });

    it('should support case-sensitive mode', () => {
      const filter = buildSafeSearchFilter('name', 'Wheat', 'default');
      expect(filter.name.mode).toBe('default');
    });
  });
});

describe('Database Utilities - Error Handling', () => {
  describe('isUniqueConstraintError', () => {
    it('should detect Prisma unique constraint error', () => {
      const error = { code: 'P2002', meta: { target: ['email'] } };
      expect(isUniqueConstraintError(error)).toBe(true);
    });

    it('should detect constraint error by message', () => {
      const error = { message: 'unique constraint violation on email' };
      expect(isUniqueConstraintError(error)).toBe(true);
    });

    it('should return false for non-unique errors', () => {
      const error = { code: 'P2003' };
      expect(isUniqueConstraintError(error)).toBe(false);
    });
  });

  describe('isForeignKeyConstraintError', () => {
    it('should detect Prisma foreign key error', () => {
      const error = { code: 'P2003' };
      expect(isForeignKeyConstraintError(error)).toBe(true);
    });

    it('should detect constraint error by message', () => {
      const error = { message: 'foreign key constraint failed' };
      expect(isForeignKeyConstraintError(error)).toBe(true);
    });

    it('should return false for non-FK errors', () => {
      const error = { code: 'P2002' };
      expect(isForeignKeyConstraintError(error)).toBe(false);
    });
  });

  describe('isRecordNotFoundError', () => {
    it('should detect Prisma record not found error', () => {
      const error = { code: 'P2025' };
      expect(isRecordNotFoundError(error)).toBe(true);
    });

    it('should detect error by message', () => {
      const error = { message: 'Record to update not found' };
      expect(isRecordNotFoundError(error)).toBe(true);
    });

    it('should return false for other errors', () => {
      const error = { code: 'P2002' };
      expect(isRecordNotFoundError(error)).toBe(false);
    });
  });

  describe('extractConstraintField', () => {
    it('should extract field from Prisma unique error', () => {
      const error = {
        code: 'P2002',
        meta: { target: ['email'] },
      };
      const field = extractConstraintField(error);
      expect(field).toBe('email');
    });

    it('should extract composite field names', () => {
      const error = {
        code: 'P2002',
        meta: { target: ['tenantId', 'email'] },
      };
      const field = extractConstraintField(error);
      expect(field).toBe('tenantId, email');
    });

    it('should return null for non-unique errors', () => {
      const error = { code: 'P2003' };
      const field = extractConstraintField(error);
      expect(field).toBeNull();
    });

    it('should return null when target is missing', () => {
      const error = { code: 'P2002', meta: {} };
      const field = extractConstraintField(error);
      expect(field).toBeNull();
    });
  });
});

describe('Database Utilities - Soft Delete', () => {
  it('should provide NOT_DELETED filter', () => {
    expect(NOT_DELETED).toEqual({ deletedAt: null });
  });

  it('should provide INCLUDE_DELETED filter', () => {
    expect(INCLUDE_DELETED).toEqual({});
  });

  it('should provide ONLY_DELETED filter', () => {
    expect(ONLY_DELETED).toEqual({
      deletedAt: { not: null },
    });
  });
});

describe('Database Utilities - Constants', () => {
  it('should export consistent pagination constants', () => {
    expect(MAX_PAGE_SIZE).toBe(100);
    expect(DEFAULT_PAGE_SIZE).toBe(20);
  });

  it('should export query threshold constants', () => {
    expect(typeof import('../../../shared/db/db-utils').SLOW_QUERY_THRESHOLD).toBe('number');
    expect(typeof import('../../../shared/db/db-utils').VERY_SLOW_QUERY_THRESHOLD).toBe('number');
  });
});
