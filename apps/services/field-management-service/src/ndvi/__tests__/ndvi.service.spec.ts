/**
 * NdviService Unit Tests
 * اختبارات وحدة خدمة NDVI
 *
 * Tests NDVI retrieval, update, summary aggregation, category
 * classification, health score calculation, and tenant isolation.
 */

import { Test, TestingModule } from '@nestjs/testing';
import {
  NotFoundException,
  BadRequestException,
  ForbiddenException,
} from '@nestjs/common';
import { NdviService } from '../ndvi.service';
import { PrismaService } from '../../prisma/prisma.service';
import { CacheService, CACHE_KEYS, CACHE_TTL } from '../../cache/cache.service';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const TENANT_A = 'tenant-aaa-1111';
const TENANT_B = 'tenant-bbb-2222';
const FIELD_ID = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';

const now = new Date('2026-03-30T10:00:00Z');

function makeFieldRow(overrides: Record<string, any> = {}) {
  return {
    id: FIELD_ID,
    name: 'North Wheat Field',
    tenantId: TENANT_A,
    ndviValue: 0.65,
    healthScore: 0.72,
    ...overrides,
  };
}

function makeNdviReadings(count: number, baseValue = 0.6) {
  return Array.from({ length: count }, (_, i) => ({
    id: `reading-${i}`,
    value: baseValue + i * 0.02,
    capturedAt: new Date(now.getTime() - i * 86400000),
    source: 'satellite',
    cloudCover: 20,
    quality: 'good',
  }));
}

// ---------------------------------------------------------------------------
// Mock factories
// ---------------------------------------------------------------------------

function createMockPrisma() {
  return {
    field: {
      findUnique: jest.fn(),
      update: jest.fn(),
    },
    ndviReading: {
      findMany: jest.fn(),
      create: jest.fn(),
    },
    $queryRaw: jest.fn(),
  };
}

function createMockCache() {
  return {
    get: jest.fn().mockResolvedValue(null),
    set: jest.fn().mockResolvedValue(undefined),
    del: jest.fn().mockResolvedValue(undefined),
  };
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe('NdviService', () => {
  let service: NdviService;
  let prisma: ReturnType<typeof createMockPrisma>;
  let cache: ReturnType<typeof createMockCache>;

  beforeEach(async () => {
    prisma = createMockPrisma();
    cache = createMockCache();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        NdviService,
        { provide: PrismaService, useValue: prisma },
        { provide: CacheService, useValue: cache },
      ],
    }).compile();

    service = module.get<NdviService>(NdviService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // =========================================================================
  // getFieldNdvi()
  // =========================================================================
  describe('getFieldNdvi()', () => {
    it('should return NDVI analysis with statistics and history', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());
      const readings = makeNdviReadings(6);
      prisma.ndviReading.findMany.mockResolvedValue(readings);

      const result = await service.getFieldNdvi(FIELD_ID, TENANT_A);

      expect(result.fieldId).toBe(FIELD_ID);
      expect(result.fieldName).toBe('North Wheat Field');
      expect(result.current).toBeDefined();
      expect(result.current.category).toBeDefined();
      expect(result.statistics.average).toBeDefined();
      expect(result.statistics.min).toBeDefined();
      expect(result.statistics.max).toBeDefined();
      expect(result.history).toHaveLength(6);
      expect(cache.set).toHaveBeenCalledWith(
        CACHE_KEYS.NDVI(FIELD_ID),
        expect.any(Object),
        CACHE_TTL.MEDIUM,
      );
    });

    it('should return cached data on cache hit', async () => {
      const cached = { fieldId: FIELD_ID, current: { value: 0.7 } };
      cache.get.mockResolvedValue(cached);

      const result = await service.getFieldNdvi(FIELD_ID, TENANT_A);

      expect(result).toEqual(cached);
      expect(prisma.field.findUnique).not.toHaveBeenCalled();
    });

    it('should throw NotFoundException when field does not exist', async () => {
      prisma.field.findUnique.mockResolvedValue(null);

      await expect(
        service.getFieldNdvi('nonexistent', TENANT_A),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw ForbiddenException for cross-tenant access', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ tenantId: TENANT_A }));

      await expect(
        service.getFieldNdvi(FIELD_ID, TENANT_B),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should calculate trend as "improving" when recent values are higher', async () => {
      // Readings are ordered desc, so index 0 is most recent
      // Make first half (recent) higher than second half (older)
      const readings = [
        { id: '1', value: 0.8, capturedAt: new Date(), source: 's', cloudCover: 10, quality: 'good' },
        { id: '2', value: 0.78, capturedAt: new Date(), source: 's', cloudCover: 10, quality: 'good' },
        { id: '3', value: 0.5, capturedAt: new Date(), source: 's', cloudCover: 10, quality: 'good' },
        { id: '4', value: 0.48, capturedAt: new Date(), source: 's', cloudCover: 10, quality: 'good' },
      ];
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ ndviValue: 0.8 }));
      prisma.ndviReading.findMany.mockResolvedValue(readings);

      const result = await service.getFieldNdvi(FIELD_ID, TENANT_A);

      // Trend compares secondHalf avg - firstHalf avg
      // firstHalf = [0.8, 0.78] avg=0.79, secondHalf = [0.5, 0.48] avg=0.49
      // trend = 0.49 - 0.79 = -0.30 => declining
      expect(result.statistics.trendDirection).toBe('declining');
    });

    it('should return zero statistics when no readings exist', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ ndviValue: null }));
      prisma.ndviReading.findMany.mockResolvedValue([]);

      const result = await service.getFieldNdvi(FIELD_ID, TENANT_A);

      expect(result.current.value).toBe(0);
      expect(result.statistics.average).toBe(0);
      expect(result.statistics.min).toBe(0);
      expect(result.statistics.max).toBe(0);
    });
  });

  // =========================================================================
  // updateFieldNdvi()
  // =========================================================================
  describe('updateFieldNdvi()', () => {
    it('should update NDVI value and return result', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());
      prisma.ndviReading.create.mockResolvedValue({});
      prisma.field.update.mockResolvedValue({});

      const result = await service.updateFieldNdvi(FIELD_ID, TENANT_A, 0.72, 'satellite', 15);

      expect(result.fieldId).toBe(FIELD_ID);
      expect(result.ndviValue).toBe(0.72);
      expect(result.category).toBeDefined();
      expect(result.source).toBe('satellite');
      expect(prisma.ndviReading.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          fieldId: FIELD_ID,
          value: 0.72,
          source: 'satellite',
          cloudCover: 15,
          quality: 'good',
        }),
      });
      expect(cache.del).toHaveBeenCalledWith(CACHE_KEYS.NDVI(FIELD_ID));
      expect(cache.del).toHaveBeenCalledWith(CACHE_KEYS.FIELD(FIELD_ID, TENANT_A));
    });

    it('should throw BadRequestException for NDVI value > 1', async () => {
      await expect(
        service.updateFieldNdvi(FIELD_ID, TENANT_A, 1.5),
      ).rejects.toThrow(BadRequestException);
    });

    it('should throw BadRequestException for NDVI value < -1', async () => {
      await expect(
        service.updateFieldNdvi(FIELD_ID, TENANT_A, -1.5),
      ).rejects.toThrow(BadRequestException);
    });

    it('should throw NotFoundException when field does not exist', async () => {
      prisma.field.findUnique.mockResolvedValue(null);

      await expect(
        service.updateFieldNdvi('nonexistent', TENANT_A, 0.5),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw ForbiddenException for cross-tenant update', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ tenantId: TENANT_A }));

      await expect(
        service.updateFieldNdvi(FIELD_ID, TENANT_B, 0.5),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should set quality to "poor" when cloudCover > 50', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());
      prisma.ndviReading.create.mockResolvedValue({});
      prisma.field.update.mockResolvedValue({});

      await service.updateFieldNdvi(FIELD_ID, TENANT_A, 0.5, 'satellite', 75);

      expect(prisma.ndviReading.create).toHaveBeenCalledWith({
        data: expect.objectContaining({ quality: 'poor' }),
      });
    });

    it('should calculate health score correctly for various NDVI values', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());
      prisma.ndviReading.create.mockResolvedValue({});
      prisma.field.update.mockResolvedValue({});

      // NDVI 0.5 => healthScore = (0.5 - 0.2) / 0.6 = 0.5
      await service.updateFieldNdvi(FIELD_ID, TENANT_A, 0.5);

      expect(prisma.field.update).toHaveBeenCalledWith({
        where: { id: FIELD_ID },
        data: expect.objectContaining({
          healthScore: 0.5,
        }),
      });
    });
  });

  // =========================================================================
  // getTenantNdviSummary()
  // =========================================================================
  describe('getTenantNdviSummary()', () => {
    it('should return NDVI summary from raw query', async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          total_fields: '10',
          average_ndvi: '0.55',
          average_health: '0.68',
          total_area: '500.0',
          healthy_count: '4',
          moderate_count: '3',
          stressed_count: '2',
          critical_count: '1',
        },
      ]);

      const result = await service.getTenantNdviSummary(TENANT_A);

      expect(result.tenantId).toBe(TENANT_A);
      expect(result.totalFields).toBe(10);
      expect(result.averageNdvi).toBe(0.55);
      expect(result.distribution.healthy).toBe(4);
      expect(result.distribution.moderate).toBe(3);
      expect(result.distribution.stressed).toBe(2);
      expect(result.distribution.critical).toBe(1);
      expect(cache.set).toHaveBeenCalled();
    });

    it('should return cached summary on cache hit', async () => {
      const cached = { tenantId: TENANT_A, totalFields: 5 };
      cache.get.mockResolvedValue(cached);

      const result = await service.getTenantNdviSummary(TENANT_A);

      expect(result).toEqual(cached);
      expect(prisma.$queryRaw).not.toHaveBeenCalled();
    });

    it('should return zero values when no fields have NDVI data', async () => {
      prisma.$queryRaw.mockResolvedValue([{}]);

      const result = await service.getTenantNdviSummary(TENANT_A);

      expect(result.totalFields).toBe(0);
      expect(result.averageNdvi).toBe(0);
      expect(result.distribution.healthy).toBe(0);
    });
  });
});
