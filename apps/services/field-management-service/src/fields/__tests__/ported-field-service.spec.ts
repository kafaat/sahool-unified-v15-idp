/**
 * Regression tests for the 4 endpoints ported from the archived field-service:
 *
 *   GET  /fields/:id/area             — recompute area from PostGIS boundary
 *   POST /fields/check-overlap        — ST_Intersects against tenant fields
 *   GET  /fields/:id/export/kml       — KML document export
 *   GET  /fields/:id/export/geojson   — GeoJSON Feature export
 *
 * These tests cover: tenant isolation, missing-boundary handling, 404 for
 * non-existent fields, XML escaping in KML, polygon closure for overlap.
 */

import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException, BadRequestException, ForbiddenException } from '@nestjs/common';
import { FieldsService } from '../fields.service';
import { PrismaService } from '../../prisma/prisma.service';
import { CacheService } from '../../cache/cache.service';
import { FieldEventsService } from '../../events/field-events.service';

const TENANT_A = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
const TENANT_B = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
const FIELD_ID = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';
const OTHER_FIELD_ID = '11111111-2222-3333-4444-555555555555';

function createMockPrisma() {
  return {
    field: { findUnique: jest.fn() },
    $queryRaw: jest.fn(),
    $queryRawUnsafe: jest.fn(),
    $executeRaw: jest.fn(),
    $transaction: jest.fn(),
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
    publishFieldCreated: jest.fn(),
    publishFieldUpdated: jest.fn(),
    publishFieldDeleted: jest.fn(),
    publishBoundaryChanged: jest.fn(),
  };
}

describe('FieldsService - Ported field-service endpoints', () => {
  let service: FieldsService;
  let prisma: ReturnType<typeof createMockPrisma>;

  beforeEach(async () => {
    prisma = createMockPrisma();
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FieldsService,
        { provide: PrismaService, useValue: prisma },
        { provide: CacheService, useValue: createMockCache() },
        { provide: FieldEventsService, useValue: createMockEvents() },
      ],
    }).compile();
    service = module.get(FieldsService);
  });

  afterEach(() => jest.clearAllMocks());

  // =========================================================================
  // getFieldArea()
  // =========================================================================

  describe('getFieldArea()', () => {
    it('returns PostGIS-computed area with diff vs stored column', async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          id: FIELD_ID,
          tenant_id: TENANT_A,
          stored_area: 12.5,
          calculated_area: 12.8,
          centroid_lat: 24.75,
          centroid_lng: 46.75,
          has_boundary: true,
        },
      ]);

      const result = await service.getFieldArea(FIELD_ID, TENANT_A);

      expect(result.field_id).toBe(FIELD_ID);
      expect(result.calculated_area_hectares).toBe(12.8);
      expect(result.stored_area_hectares).toBe(12.5);
      // ((12.8 - 12.5) / 12.5) * 100 = 2.4%
      expect(result.difference_percent).toBeCloseTo(2.4, 1);
      expect(result.centroid).toEqual({ lat: 24.75, lng: 46.75 });
    });

    it('throws 404 when field does not exist', async () => {
      prisma.$queryRaw.mockResolvedValue([]);
      await expect(service.getFieldArea(FIELD_ID, TENANT_A)).rejects.toThrow(
        NotFoundException,
      );
    });

    it('throws 403 on cross-tenant access', async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          id: FIELD_ID,
          tenant_id: TENANT_B, // belongs to B, caller is A
          stored_area: 10,
          calculated_area: 10,
          centroid_lat: 0,
          centroid_lng: 0,
          has_boundary: true,
        },
      ]);
      await expect(service.getFieldArea(FIELD_ID, TENANT_A)).rejects.toThrow(
        ForbiddenException,
      );
    });

    it('throws 400 when field has no boundary', async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          id: FIELD_ID,
          tenant_id: TENANT_A,
          stored_area: 0,
          calculated_area: null,
          centroid_lat: null,
          centroid_lng: null,
          has_boundary: false,
        },
      ]);
      await expect(service.getFieldArea(FIELD_ID, TENANT_A)).rejects.toThrow(
        BadRequestException,
      );
    });

    it('reports 0% difference when stored area is 0 (avoids divide-by-zero)', async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          id: FIELD_ID,
          tenant_id: TENANT_A,
          stored_area: 0,
          calculated_area: 5,
          centroid_lat: 0,
          centroid_lng: 0,
          has_boundary: true,
        },
      ]);
      const result = await service.getFieldArea(FIELD_ID, TENANT_A);
      expect(result.difference_percent).toBe(0);
    });
  });

  // =========================================================================
  // checkOverlap()
  // =========================================================================

  describe('checkOverlap()', () => {
    const candidate = {
      coordinates: [
        [46.7, 24.7],
        [46.8, 24.7],
        [46.8, 24.8],
        [46.7, 24.8],
      ],
    };

    it('closes the candidate polygon before querying PostGIS', async () => {
      prisma.$queryRaw.mockResolvedValue([]);
      await service.checkOverlap(candidate as any, TENANT_A);
      // The candidate ring was open (first ≠ last); the service should
      // auto-close it so PostGIS gets a valid polygon.
      const call = prisma.$queryRaw.mock.calls[0];
      const values = call.slice(1); // first arg is TemplateStringsArray
      const candidateJson = values.find(
        (v: any) => typeof v === 'string' && v.includes('Polygon'),
      );
      expect(candidateJson).toBeDefined();
      const parsed = JSON.parse(candidateJson as string);
      const ring = parsed.coordinates[0];
      expect(ring[0]).toEqual(ring[ring.length - 1]);
    });

    it('reports has_overlap=false when no rows intersect', async () => {
      prisma.$queryRaw.mockResolvedValue([]);
      const result = await service.checkOverlap(candidate as any, TENANT_A);
      expect(result.has_overlap).toBe(false);
      expect(result.overlapping_fields).toEqual([]);
      expect(result.overlap_area_hectares).toBe(0);
    });

    it('returns overlapping fields with individual and total areas', async () => {
      prisma.$queryRaw.mockResolvedValue([
        { id: OTHER_FIELD_ID, name: 'North Plot', overlap_area: 1.2345 },
        { id: FIELD_ID, name: 'South Plot', overlap_area: 0.5 },
      ]);
      const result = await service.checkOverlap(candidate as any, TENANT_A);
      expect(result.has_overlap).toBe(true);
      expect(result.overlapping_fields).toHaveLength(2);
      expect(result.overlapping_fields[0]).toEqual({
        field_id: OTHER_FIELD_ID,
        field_name: 'North Plot',
        overlap_area_hectares: 1.2345,
      });
      expect(result.overlap_area_hectares).toBeCloseTo(1.7345, 4);
    });

    it('filters out zero-area intersections (touching boundaries)', async () => {
      // ST_Intersects can return "true" for shared edges; the resulting
      // ST_Intersection has zero area. We must not report those.
      prisma.$queryRaw.mockResolvedValue([
        { id: OTHER_FIELD_ID, name: 'Edge Neighbor', overlap_area: 0 },
      ]);
      const result = await service.checkOverlap(candidate as any, TENANT_A);
      expect(result.has_overlap).toBe(false);
      expect(result.overlapping_fields).toHaveLength(0);
    });

    it('respects excludeFieldId when checking against existing fields', async () => {
      prisma.$queryRaw.mockResolvedValue([]);
      await service.checkOverlap(
        { ...candidate, excludeFieldId: FIELD_ID } as any,
        TENANT_A,
      );
      // Just verify the call completed — the SQL template contains the
      // exclude-UUID bind and the mock fulfils it. The important contract
      // is that PostgreSQL receives the excludeFieldId value.
      const call = prisma.$queryRaw.mock.calls[0];
      const values = call.slice(1);
      expect(values).toContain(FIELD_ID);
    });
  });

  // =========================================================================
  // exportFieldKml()
  // =========================================================================

  describe('exportFieldKml()', () => {
    function mockField(overrides: Record<string, any> = {}) {
      prisma.$queryRaw.mockResolvedValue([
        {
          id: FIELD_ID,
          name: 'North Wheat Field',
          tenant_id: TENANT_A,
          area_hectares: 12.5,
          crop_type: 'wheat',
          soil_type: 'loamy',
          boundary_geojson: JSON.stringify({
            type: 'Polygon',
            coordinates: [
              [
                [46.7, 24.7],
                [46.8, 24.7],
                [46.8, 24.8],
                [46.7, 24.8],
                [46.7, 24.7],
              ],
            ],
          }),
          ...overrides,
        },
      ]);
    }

    it('returns a valid KML document with polygon coordinates', async () => {
      mockField();
      const kml = await service.exportFieldKml(FIELD_ID, TENANT_A);
      expect(kml).toContain('<?xml version="1.0" encoding="UTF-8"?>');
      expect(kml).toContain('<kml xmlns="http://www.opengis.net/kml/2.2">');
      expect(kml).toContain('<name>North Wheat Field</name>');
      // Coordinates in KML are `lng,lat,alt` space-separated
      expect(kml).toMatch(/46\.7,24\.7,0/);
      expect(kml).toMatch(/46\.8,24\.8,0/);
    });

    it('XML-escapes the field name (prevents injection via user-controlled string)', async () => {
      mockField({ name: '<script>alert("x")</script> & Co' });
      const kml = await service.exportFieldKml(FIELD_ID, TENANT_A);
      expect(kml).toContain('&lt;script&gt;');
      expect(kml).toContain('&amp; Co');
      expect(kml).not.toContain('<script>');
    });

    it('throws 404 when field does not exist', async () => {
      prisma.$queryRaw.mockResolvedValue([]);
      await expect(service.exportFieldKml(FIELD_ID, TENANT_A)).rejects.toThrow(
        NotFoundException,
      );
    });

    it('throws 403 on cross-tenant access', async () => {
      mockField({ tenant_id: TENANT_B });
      await expect(service.exportFieldKml(FIELD_ID, TENANT_A)).rejects.toThrow(
        ForbiddenException,
      );
    });

    it('throws 400 when the field has no boundary', async () => {
      mockField({ boundary_geojson: null });
      await expect(service.exportFieldKml(FIELD_ID, TENANT_A)).rejects.toThrow(
        BadRequestException,
      );
    });
  });

  // =========================================================================
  // exportFieldGeoJson()
  // =========================================================================

  describe('exportFieldGeoJson()', () => {
    it('returns a GeoJSON Feature with agronomic properties', async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          id: FIELD_ID,
          name: 'North Wheat Field',
          tenant_id: TENANT_A,
          area_hectares: 12.5,
          crop_type: 'wheat',
          soil_type: 'loamy',
          boundary_geojson: JSON.stringify({
            type: 'Polygon',
            coordinates: [
              [
                [46.7, 24.7],
                [46.8, 24.7],
                [46.8, 24.8],
                [46.7, 24.7],
              ],
            ],
          }),
        },
      ]);

      const feature = await service.exportFieldGeoJson(FIELD_ID, TENANT_A);
      expect(feature.type).toBe('Feature');
      expect(feature.geometry.type).toBe('Polygon');
      expect(feature.properties).toEqual({
        field_id: FIELD_ID,
        name: 'North Wheat Field',
        area_hectares: 12.5,
        crop_type: 'wheat',
        soil_type: 'loamy',
      });
    });

    it('throws 404 when field does not exist', async () => {
      prisma.$queryRaw.mockResolvedValue([]);
      await expect(
        service.exportFieldGeoJson(FIELD_ID, TENANT_A),
      ).rejects.toThrow(NotFoundException);
    });
  });
});
