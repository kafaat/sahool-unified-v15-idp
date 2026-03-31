/**
 * FieldsService Unit Tests
 * اختبارات وحدة خدمة الحقول
 *
 * Tests CRUD operations, tenant isolation, caching, ETag-based
 * optimistic locking, PostGIS queries, and boundary history.
 */

import { Test, TestingModule } from '@nestjs/testing';
import {
  NotFoundException,
  ConflictException,
  BadRequestException,
  ForbiddenException,
} from '@nestjs/common';
import { FieldsService } from '../fields.service';
import { PrismaService } from '../../prisma/prisma.service';
import { CacheService, CACHE_KEYS, CACHE_TTL } from '../../cache/cache.service';
import { FieldEventsService } from '../../events/field-events.service';

// ---------------------------------------------------------------------------
// Helpers & fixtures
// ---------------------------------------------------------------------------

const TENANT_A = 'tenant-aaa-1111';
const TENANT_B = 'tenant-bbb-2222';
const FIELD_ID = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';
const FARM_ID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
const OWNER_ID = 'b2c3d4e5-f6a7-8901-bcde-f12345678901';
const HISTORY_ID = 'c3d4e5f6-a7b8-9012-cdef-123456789012';

const now = new Date('2026-03-30T10:00:00Z');

function makeFieldRow(overrides: Record<string, any> = {}) {
  return {
    id: FIELD_ID,
    name: 'North Wheat Field',
    tenantId: TENANT_A,
    cropType: 'wheat',
    status: 'active',
    areaHectares: 12.5,
    healthScore: 0.72,
    ndviValue: 0.65,
    irrigationType: 'drip',
    soilType: 'loamy',
    plantingDate: now,
    expectedHarvest: new Date('2026-07-15T00:00:00Z'),
    metadata: null,
    version: 1,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Mock factories
// ---------------------------------------------------------------------------

function createMockPrisma() {
  return {
    field: {
      create: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
      count: jest.fn(),
      update: jest.fn(),
    },
    farm: {
      findUnique: jest.fn(),
    },
    fieldBoundaryHistory: {
      create: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
    },
    $transaction: jest.fn((cb: any) => cb({
      field: {
        create: jest.fn().mockResolvedValue(makeFieldRow()),
        update: jest.fn().mockResolvedValue(makeFieldRow({ version: 2 })),
      },
      fieldBoundaryHistory: {
        create: jest.fn().mockResolvedValue({}),
      },
      $executeRaw: jest.fn().mockResolvedValue(1),
      $queryRaw: jest.fn().mockResolvedValue([{ boundary: null }]),
    })),
    $queryRaw: jest.fn(),
    $executeRaw: jest.fn(),
  };
}

function createMockCache() {
  return {
    get: jest.fn().mockResolvedValue(null),
    set: jest.fn().mockResolvedValue(undefined),
    del: jest.fn().mockResolvedValue(undefined),
    invalidateField: jest.fn().mockResolvedValue(undefined),
    invalidateTenant: jest.fn().mockResolvedValue(undefined),
  };
}

function createMockEvents() {
  return {
    publishFieldCreated: jest.fn().mockResolvedValue(undefined),
    publishFieldUpdated: jest.fn().mockResolvedValue(undefined),
    publishFieldDeleted: jest.fn().mockResolvedValue(undefined),
    publishBoundaryChanged: jest.fn().mockResolvedValue(undefined),
  };
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe('FieldsService', () => {
  let service: FieldsService;
  let prisma: ReturnType<typeof createMockPrisma>;
  let cache: ReturnType<typeof createMockCache>;
  let events: ReturnType<typeof createMockEvents>;

  beforeEach(async () => {
    prisma = createMockPrisma();
    cache = createMockCache();
    events = createMockEvents();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FieldsService,
        { provide: PrismaService, useValue: prisma },
        { provide: CacheService, useValue: cache },
        { provide: FieldEventsService, useValue: events },
      ],
    }).compile();

    service = module.get<FieldsService>(FieldsService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // =========================================================================
  // create()
  // =========================================================================
  describe('create()', () => {
    const baseDto = {
      name: 'North Wheat Field',
      tenantId: TENANT_A,
      cropType: 'wheat',
      ownerId: OWNER_ID,
    };

    it('should create a field without coordinates', async () => {
      const row = makeFieldRow();
      // The service calls findById after creating, so mock that path
      prisma.field.findUnique.mockResolvedValue(row);

      const result = await service.create(baseDto as any);

      expect(result).toBeDefined();
      expect(result.id).toBe(FIELD_ID);
      expect(result.etag).toContain(FIELD_ID);
      expect(cache.invalidateTenant).toHaveBeenCalledWith(TENANT_A);
      expect(events.publishFieldCreated).toHaveBeenCalled();
    });

    it('should create a field with coordinates and calculate boundary', async () => {
      const dto = {
        ...baseDto,
        coordinates: [
          [46.7, 24.7],
          [46.8, 24.7],
          [46.8, 24.8],
          [46.7, 24.8],
        ],
      };
      const row = makeFieldRow();
      prisma.field.findUnique.mockResolvedValue(row);

      const result = await service.create(dto as any);

      expect(result).toBeDefined();
      // The $transaction should have been called (PostGIS update inside)
      expect(prisma.$transaction).toHaveBeenCalled();
    });

    it('should throw BadRequestException when farmId references a non-existent farm', async () => {
      prisma.farm.findUnique.mockResolvedValue(null);

      await expect(
        service.create({ ...baseDto, farmId: FARM_ID } as any),
      ).rejects.toThrow(BadRequestException);
    });

    it('should throw ForbiddenException for cross-tenant farm reference', async () => {
      prisma.farm.findUnique.mockResolvedValue({ tenantId: TENANT_B });

      await expect(
        service.create({ ...baseDto, farmId: FARM_ID } as any),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should close polygon when last coordinate differs from first', async () => {
      const dto = {
        ...baseDto,
        coordinates: [
          [46.7, 24.7],
          [46.8, 24.7],
          [46.8, 24.8],
        ],
      };
      const row = makeFieldRow();
      prisma.field.findUnique.mockResolvedValue(row);

      await service.create(dto as any);

      // Verify transaction was called (boundary path)
      expect(prisma.$transaction).toHaveBeenCalled();
    });
  });

  // =========================================================================
  // findById()
  // =========================================================================
  describe('findById()', () => {
    it('should return a field from the database when cache misses', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());

      const result = await service.findById(FIELD_ID);

      expect(result.id).toBe(FIELD_ID);
      expect(result.name).toBe('North Wheat Field');
      expect(result.etag).toBeDefined();
      expect(cache.set).toHaveBeenCalledWith(
        CACHE_KEYS.FIELD(FIELD_ID),
        expect.any(Object),
        CACHE_TTL.MEDIUM,
      );
    });

    it('should return cached field on cache hit', async () => {
      const cachedField = {
        id: FIELD_ID,
        name: 'Cached Field',
        tenantId: TENANT_A,
        version: 1,
        etag: `"${FIELD_ID}-v1"`,
      };
      cache.get.mockResolvedValue(cachedField);

      const result = await service.findById(FIELD_ID);

      expect(result.name).toBe('Cached Field');
      expect(prisma.field.findUnique).not.toHaveBeenCalled();
    });

    it('should throw NotFoundException when field does not exist', async () => {
      prisma.field.findUnique.mockResolvedValue(null);

      await expect(service.findById('nonexistent-id')).rejects.toThrow(
        NotFoundException,
      );
    });

    it('should enforce tenant isolation when tenantId is provided', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ tenantId: TENANT_A }));

      await expect(
        service.findById(FIELD_ID, TENANT_B),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should enforce tenant isolation on cached results', async () => {
      cache.get.mockResolvedValue({
        id: FIELD_ID,
        tenantId: TENANT_A,
        version: 1,
        etag: `"${FIELD_ID}-v1"`,
      });

      await expect(
        service.findById(FIELD_ID, TENANT_B),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should pass tenant check when tenantIds match', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());

      const result = await service.findById(FIELD_ID, TENANT_A);

      expect(result.id).toBe(FIELD_ID);
    });

    it('should convert Decimal fields to numbers in the response', async () => {
      const row = makeFieldRow({
        areaHectares: { toNumber: () => 12.5 },
        healthScore: { toNumber: () => 0.72 },
        ndviValue: { toNumber: () => 0.65 },
      });
      prisma.field.findUnique.mockResolvedValue(row);

      const result = await service.findById(FIELD_ID);

      expect(typeof result.areaHectares).toBe('number');
    });
  });

  // =========================================================================
  // findAll()
  // =========================================================================
  describe('findAll()', () => {
    it('should return paginated fields for a tenant', async () => {
      const fields = [makeFieldRow(), makeFieldRow({ id: 'field-2', name: 'South Field' })];
      prisma.field.findMany.mockResolvedValue(fields);
      prisma.field.count.mockResolvedValue(2);

      const result = await service.findAll({ tenantId: TENANT_A, page: 1, limit: 20 });

      expect(result.data).toHaveLength(2);
      expect(result.meta.total).toBe(2);
      expect(result.meta.page).toBe(1);
      expect(result.meta.hasNext).toBe(false);
      expect(result.meta.hasPrev).toBe(false);
    });

    it('should filter by status', async () => {
      prisma.field.findMany.mockResolvedValue([]);
      prisma.field.count.mockResolvedValue(0);

      await service.findAll({ tenantId: TENANT_A, status: 'active' as any });

      const whereArg = prisma.field.findMany.mock.calls[0][0].where;
      expect(whereArg.status).toBe('active');
    });

    it('should filter by cropType', async () => {
      prisma.field.findMany.mockResolvedValue([]);
      prisma.field.count.mockResolvedValue(0);

      await service.findAll({ tenantId: TENANT_A, cropType: 'wheat' });

      const whereArg = prisma.field.findMany.mock.calls[0][0].where;
      expect(whereArg.cropType).toBe('wheat');
    });

    it('should cap the limit at 100', async () => {
      prisma.field.findMany.mockResolvedValue([]);
      prisma.field.count.mockResolvedValue(0);

      await service.findAll({ tenantId: TENANT_A, limit: 500 });

      const takeArg = prisma.field.findMany.mock.calls[0][0].take;
      expect(takeArg).toBe(100);
    });

    it('should default page to 1 and limit to 20', async () => {
      prisma.field.findMany.mockResolvedValue([]);
      prisma.field.count.mockResolvedValue(0);

      await service.findAll({ tenantId: TENANT_A });

      const callArgs = prisma.field.findMany.mock.calls[0][0];
      expect(callArgs.skip).toBe(0);
      expect(callArgs.take).toBe(20);
    });

    it('should calculate pagination metadata correctly', async () => {
      prisma.field.findMany.mockResolvedValue([makeFieldRow()]);
      prisma.field.count.mockResolvedValue(50);

      const result = await service.findAll({ tenantId: TENANT_A, page: 2, limit: 10 });

      expect(result.meta.totalPages).toBe(5);
      expect(result.meta.hasNext).toBe(true);
      expect(result.meta.hasPrev).toBe(true);
    });

    it('should always scope queries to tenantId', async () => {
      prisma.field.findMany.mockResolvedValue([]);
      prisma.field.count.mockResolvedValue(0);

      await service.findAll({ tenantId: TENANT_A });

      const whereArg = prisma.field.findMany.mock.calls[0][0].where;
      expect(whereArg.tenantId).toBe(TENANT_A);
    });

    it('should include etag on each response item', async () => {
      prisma.field.findMany.mockResolvedValue([makeFieldRow()]);
      prisma.field.count.mockResolvedValue(1);

      const result = await service.findAll({ tenantId: TENANT_A });

      expect(result.data[0].etag).toBe(`"${FIELD_ID}-v1"`);
    });
  });

  // =========================================================================
  // update()
  // =========================================================================
  describe('update()', () => {
    it('should update a field and return the new etag', async () => {
      prisma.field.findUnique
        .mockResolvedValueOnce(makeFieldRow()) // current lookup
        .mockResolvedValueOnce(makeFieldRow({ version: 2 })); // findById after update
      prisma.$transaction.mockImplementation(async (cb: any) => {
        await cb({
          field: { update: jest.fn().mockResolvedValue(makeFieldRow({ version: 2 })) },
          $executeRaw: jest.fn(),
        });
      });

      const result = await service.update(
        FIELD_ID,
        { name: 'Updated Field' },
        TENANT_A,
      );

      expect(result).toBeDefined();
      expect(cache.invalidateField).toHaveBeenCalledWith(FIELD_ID, TENANT_A);
      expect(events.publishFieldUpdated).toHaveBeenCalled();
    });

    it('should throw NotFoundException when field does not exist', async () => {
      prisma.field.findUnique.mockResolvedValue(null);

      await expect(
        service.update('nonexistent', { name: 'Test' }, TENANT_A),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw ForbiddenException for cross-tenant update', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ tenantId: TENANT_A }));

      await expect(
        service.update(FIELD_ID, { name: 'Test' }, TENANT_B),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should throw ConflictException on ETag mismatch', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ version: 1 }));

      await expect(
        service.update(
          FIELD_ID,
          { name: 'Test' },
          TENANT_A,
          '"wrong-etag"',
        ),
      ).rejects.toThrow(ConflictException);
    });

    it('should accept matching ETag and proceed', async () => {
      prisma.field.findUnique
        .mockResolvedValueOnce(makeFieldRow({ version: 1 }))
        .mockResolvedValueOnce(makeFieldRow({ version: 2 }));
      prisma.$transaction.mockImplementation(async (cb: any) => {
        await cb({
          field: { update: jest.fn() },
          $executeRaw: jest.fn(),
        });
      });

      const etag = `"${FIELD_ID}-v1"`;
      const result = await service.update(FIELD_ID, { name: 'Test' }, TENANT_A, etag);

      expect(result).toBeDefined();
    });
  });

  // =========================================================================
  // delete()
  // =========================================================================
  describe('delete()', () => {
    it('should soft-delete a field', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());

      await service.delete(FIELD_ID, TENANT_A);

      expect(prisma.field.update).toHaveBeenCalledWith({
        where: { id: FIELD_ID },
        data: { isDeleted: true, status: 'inactive' },
      });
      expect(cache.invalidateField).toHaveBeenCalledWith(FIELD_ID, TENANT_A);
      expect(events.publishFieldDeleted).toHaveBeenCalledWith(TENANT_A, FIELD_ID);
    });

    it('should throw NotFoundException when field does not exist', async () => {
      prisma.field.findUnique.mockResolvedValue(null);

      await expect(service.delete('nonexistent', TENANT_A)).rejects.toThrow(
        NotFoundException,
      );
    });

    it('should throw ForbiddenException for cross-tenant delete', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ tenantId: TENANT_A }));

      await expect(service.delete(FIELD_ID, TENANT_B)).rejects.toThrow(
        ForbiddenException,
      );
    });
  });

  // =========================================================================
  // updateBoundary()
  // =========================================================================
  describe('updateBoundary()', () => {
    const boundaryDto = {
      coordinates: [
        [46.7, 24.7],
        [46.8, 24.7],
        [46.8, 24.8],
        [46.7, 24.8],
      ],
      userId: 'user-001',
      reason: 'Survey correction',
    };

    it('should update boundary and track history', async () => {
      prisma.field.findUnique
        .mockResolvedValueOnce(makeFieldRow()) // initial lookup
        .mockResolvedValueOnce(makeFieldRow({ version: 2 })); // findById after update

      const result = await service.updateBoundary(FIELD_ID, boundaryDto as any, TENANT_A);

      expect(result).toBeDefined();
      expect(prisma.$transaction).toHaveBeenCalled();
      expect(cache.invalidateField).toHaveBeenCalledWith(FIELD_ID, TENANT_A);
      expect(events.publishBoundaryChanged).toHaveBeenCalled();
    });

    it('should throw NotFoundException when field does not exist', async () => {
      prisma.field.findUnique.mockResolvedValue(null);

      await expect(
        service.updateBoundary('nonexistent', boundaryDto as any, TENANT_A),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw ForbiddenException for cross-tenant boundary update', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow({ tenantId: TENANT_A }));

      await expect(
        service.updateBoundary(FIELD_ID, boundaryDto as any, TENANT_B),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should report changeSource as "mobile" when deviceId is present', async () => {
      prisma.field.findUnique
        .mockResolvedValueOnce(makeFieldRow())
        .mockResolvedValueOnce(makeFieldRow({ version: 2 }));

      const dtoWithDevice = { ...boundaryDto, deviceId: 'dev-001' };
      await service.updateBoundary(FIELD_ID, dtoWithDevice as any, TENANT_A);

      expect(events.publishBoundaryChanged).toHaveBeenCalledWith(
        TENANT_A,
        FIELD_ID,
        expect.objectContaining({ changeSource: 'mobile' }),
      );
    });

    it('should report changeSource as "api" when no deviceId', async () => {
      prisma.field.findUnique
        .mockResolvedValueOnce(makeFieldRow())
        .mockResolvedValueOnce(makeFieldRow({ version: 2 }));

      await service.updateBoundary(FIELD_ID, boundaryDto as any, TENANT_A);

      expect(events.publishBoundaryChanged).toHaveBeenCalledWith(
        TENANT_A,
        FIELD_ID,
        expect.objectContaining({ changeSource: 'api' }),
      );
    });
  });

  // =========================================================================
  // rollbackBoundary()
  // =========================================================================
  describe('rollbackBoundary()', () => {
    it('should throw NotFoundException when field does not exist', async () => {
      prisma.field.findUnique.mockResolvedValue(null);
      prisma.fieldBoundaryHistory.findUnique.mockResolvedValue({ id: HISTORY_ID, fieldId: FIELD_ID });

      await expect(
        service.rollbackBoundary('nonexistent', { historyId: HISTORY_ID } as any, TENANT_A),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw NotFoundException when history entry not found', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());
      prisma.fieldBoundaryHistory.findUnique.mockResolvedValue(null);

      await expect(
        service.rollbackBoundary(FIELD_ID, { historyId: 'bad-id' } as any, TENANT_A),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw NotFoundException when history entry belongs to different field', async () => {
      prisma.field.findUnique.mockResolvedValue(makeFieldRow());
      prisma.fieldBoundaryHistory.findUnique.mockResolvedValue({
        id: HISTORY_ID,
        fieldId: 'some-other-field',
        versionAtChange: 1,
      });

      await expect(
        service.rollbackBoundary(FIELD_ID, { historyId: HISTORY_ID } as any, TENANT_A),
      ).rejects.toThrow(NotFoundException);
    });
  });

  // =========================================================================
  // findNearby()
  // =========================================================================
  describe('findNearby()', () => {
    it('should execute a PostGIS proximity query and return parsed results', async () => {
      const rawResult = [
        {
          id: FIELD_ID,
          name: 'North Field',
          crop_type: 'wheat',
          status: 'active',
          area_hectares: 12.5,
          health_score: 0.72,
          boundary: '{"type":"Polygon","coordinates":[[[46.7,24.7]]]}',
          centroid: '{"type":"Point","coordinates":[46.75,24.75]}',
          distance_meters: 1500,
        },
      ];
      prisma.$queryRaw.mockResolvedValue(rawResult);

      const result = await service.findNearby({
        tenantId: TENANT_A,
        lat: 24.7,
        lng: 46.7,
        radius: 5000,
      });

      expect(result).toHaveLength(1);
      expect(result[0].boundary).toEqual({ type: 'Polygon', coordinates: [[[46.7, 24.7]]] });
      expect(result[0].centroid).toEqual({ type: 'Point', coordinates: [46.75, 24.75] });
      expect(result[0].distance_meters).toBe(1500);
    });

    it('should handle fields with null boundary', async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          id: FIELD_ID,
          name: 'No Boundary',
          boundary: null,
          centroid: null,
          distance_meters: 2000,
        },
      ]);

      const result = await service.findNearby({
        tenantId: TENANT_A,
        lat: 24.7,
        lng: 46.7,
        radius: 5000,
      });

      expect(result[0].boundary).toBeNull();
      expect(result[0].centroid).toBeNull();
    });
  });

  // =========================================================================
  // getStats()
  // =========================================================================
  describe('getStats()', () => {
    it('should return stats from the database on cache miss', async () => {
      const statsRow = {
        total_fields: 10,
        active_fields: 8,
        fallow_fields: 1,
        harvested_fields: 1,
        total_area: 500.5,
        average_health: 0.72,
        average_ndvi: 0.6,
        crop_types: 3,
      };
      prisma.$queryRaw.mockResolvedValue([statsRow]);

      const result = await service.getStats(TENANT_A);

      expect(result).toEqual(statsRow);
      expect(cache.set).toHaveBeenCalledWith(
        CACHE_KEYS.FIELD_STATS(TENANT_A),
        statsRow,
        CACHE_TTL.MEDIUM,
      );
    });

    it('should return cached stats on cache hit', async () => {
      const cachedStats = { total_fields: 5 };
      cache.get.mockResolvedValue(cachedStats);

      const result = await service.getStats(TENANT_A);

      expect(result).toEqual(cachedStats);
      expect(prisma.$queryRaw).not.toHaveBeenCalled();
    });

    it('should return empty object when raw query returns empty array', async () => {
      prisma.$queryRaw.mockResolvedValue([]);

      const result = await service.getStats(TENANT_A);

      expect(result).toEqual({});
    });
  });

  // =========================================================================
  // getBoundaryHistory()
  // =========================================================================
  describe('getBoundaryHistory()', () => {
    it('should return boundary history with GeoJSON parsed', async () => {
      const historyRows = [
        {
          id: HISTORY_ID,
          fieldId: FIELD_ID,
          versionAtChange: 1,
          areaChangeHectares: 0.5,
          changedBy: 'user-001',
          changeReason: 'Survey',
          changeSource: 'mobile',
          deviceId: 'dev-001',
          createdAt: now,
        },
      ];
      prisma.fieldBoundaryHistory.findMany.mockResolvedValue(historyRows);
      prisma.$queryRaw.mockResolvedValue([
        {
          id: HISTORY_ID,
          previous_boundary_geojson: '{"type":"Polygon","coordinates":[[[46.7,24.7]]]}',
          new_boundary_geojson: '{"type":"Polygon","coordinates":[[[46.8,24.8]]]}',
        },
      ]);

      const result = await service.getBoundaryHistory(FIELD_ID, TENANT_A);

      expect(result).toHaveLength(1);
      expect(result[0].previousBoundary).toEqual({
        type: 'Polygon',
        coordinates: [[[46.7, 24.7]]],
      });
      expect(result[0].newBoundary).toEqual({
        type: 'Polygon',
        coordinates: [[[46.8, 24.8]]],
      });
    });

    it('should return empty array when no history exists', async () => {
      prisma.fieldBoundaryHistory.findMany.mockResolvedValue([]);

      const result = await service.getBoundaryHistory(FIELD_ID, TENANT_A);

      expect(result).toEqual([]);
    });
  });
});
