/**
 * FieldSubZonesService Unit Tests
 * اختبارات وحدة خدمة المناطق الفرعية للحقل
 *
 * Focus: the geometry-independent parts of the service (WKT building,
 * tenant isolation, soft delete, outbox write). The PostGIS-dependent
 * validation path is covered by integration tests since $queryRaw
 * can't be meaningfully unit-tested without a real Postgres.
 */

import { Test, TestingModule } from "@nestjs/testing";
import {
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { FieldSubZonesService } from "../field-sub-zones.service";
import { PrismaService } from "../../prisma/prisma.service";
import { OutboxService } from "../../outbox/outbox.service";

const TENANT = "tenant-aaa-1111";
const OTHER = "tenant-bbb-2222";
const FIELD_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479";
const ZONE_ID = "99999999-8888-7777-6666-555555555555";

function mockRow(overrides: Record<string, any> = {}) {
  return {
    id: ZONE_ID,
    tenant_id: TENANT,
    field_id: FIELD_ID,
    name: "Upper Terrace",
    name_ar: "المدرجة العليا",
    description: null,
    area_hectares: 1.23,
    elevation_m: 2200,
    slope_degrees: 12.5,
    aspect: "S",
    is_terrace: true,
    terrace_level: 3,
    display_order: 0,
    boundary_geojson: JSON.stringify({
      type: "Polygon",
      coordinates: [
        [
          [44.19, 15.36],
          [44.2, 15.36],
          [44.2, 15.37],
          [44.19, 15.37],
          [44.19, 15.36],
        ],
      ],
    }),
    deleted_at: null,
    created_by: "user-1",
    created_at: new Date(),
    updated_at: new Date(),
    ...overrides,
  };
}

function makePrismaMock() {
  return {
    field: { findUnique: jest.fn() },
    outboxEvent: { create: jest.fn() },
    $queryRaw: jest.fn(),
    $queryRawUnsafe: jest.fn(),
    $executeRaw: jest.fn(),
    $transaction: jest.fn(),
  };
}

describe("FieldSubZonesService", () => {
  let service: FieldSubZonesService;
  let prisma: ReturnType<typeof makePrismaMock>;
  let outbox: OutboxService;

  beforeEach(async () => {
    prisma = makePrismaMock();
    outbox = { writeInTransaction: jest.fn() } as unknown as OutboxService;

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FieldSubZonesService,
        { provide: PrismaService, useValue: prisma },
        { provide: OutboxService, useValue: outbox },
      ],
    }).compile();

    service = module.get(FieldSubZonesService);
  });

  describe("listByField", () => {
    it("rejects cross-tenant access via field ownership check", async () => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: OTHER,
        isDeleted: false,
      });
      await expect(
        service.listByField(FIELD_ID, TENANT),
      ).rejects.toThrow(NotFoundException);
    });

    it("returns empty list when no zones exist", async () => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: TENANT,
        isDeleted: false,
      });
      prisma.$queryRaw.mockResolvedValue([]);
      const result = await service.listByField(FIELD_ID, TENANT);
      expect(result).toEqual([]);
    });

    it("maps raw rows into camelCase response shape", async () => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: TENANT,
        isDeleted: false,
      });
      prisma.$queryRaw.mockResolvedValue([mockRow()]);

      const result = await service.listByField(FIELD_ID, TENANT);
      expect(result).toHaveLength(1);
      expect(result[0]).toMatchObject({
        id: ZONE_ID,
        tenantId: TENANT,
        fieldId: FIELD_ID,
        name: "Upper Terrace",
        nameAr: "المدرجة العليا",
        areaHectares: 1.23,
        isTerrace: true,
        terraceLevel: 3,
      });
      expect(result[0].boundary).toEqual(
        expect.objectContaining({ type: "Polygon" }),
      );
    });
  });

  describe("getById", () => {
    it("returns 404 when the row does not belong to the tenant", async () => {
      prisma.$queryRaw.mockResolvedValue([]);
      await expect(service.getById(ZONE_ID, TENANT)).rejects.toThrow(
        NotFoundException,
      );
    });

    it("returns the row when found", async () => {
      prisma.$queryRaw.mockResolvedValue([mockRow()]);
      const result = await service.getById(ZONE_ID, TENANT);
      expect(result.id).toBe(ZONE_ID);
    });
  });

  describe("create - WKT builder + validation shortcuts", () => {
    beforeEach(() => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: TENANT,
        isDeleted: false,
      });
    });

    it("rejects polygons with fewer than 3 vertices", async () => {
      await expect(
        service.create(
          FIELD_ID,
          TENANT,
          {
            name: "Too small",
            boundary: [
              { lat: 15.36, lng: 44.19 },
              { lat: 15.37, lng: 44.2 },
            ],
          },
        ),
      ).rejects.toThrow(BadRequestException);
    });

    it("rejects polygon geometry flagged invalid by PostGIS", async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          is_valid: false,
          is_simple: true,
          area_ha: "1",
          inside_field: true,
        },
      ]);
      await expect(
        service.create(
          FIELD_ID,
          TENANT,
          {
            name: "Invalid",
            boundary: [
              { lat: 15.36, lng: 44.19 },
              { lat: 15.37, lng: 44.2 },
              { lat: 15.365, lng: 44.205 },
            ],
          },
        ),
      ).rejects.toThrow(/invalid/i);
    });

    it("rejects self-intersecting polygons", async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          is_valid: true,
          is_simple: false,
          area_ha: "1",
          inside_field: true,
        },
      ]);
      await expect(
        service.create(
          FIELD_ID,
          TENANT,
          {
            name: "Bowtie",
            boundary: [
              { lat: 15.36, lng: 44.19 },
              { lat: 15.37, lng: 44.2 },
              { lat: 15.365, lng: 44.205 },
            ],
          },
        ),
      ).rejects.toThrow(/self-intersection/i);
    });

    it("rejects sub-zones smaller than 1 m²", async () => {
      prisma.$queryRaw.mockResolvedValue([
        {
          is_valid: true,
          is_simple: true,
          area_ha: "0.00005",
          inside_field: true,
        },
      ]);
      await expect(
        service.create(
          FIELD_ID,
          TENANT,
          {
            name: "Too tiny",
            boundary: [
              { lat: 15.36, lng: 44.19 },
              { lat: 15.37, lng: 44.2 },
              { lat: 15.365, lng: 44.205 },
            ],
          },
        ),
      ).rejects.toThrow(/small/i);
    });
  });

  describe("remove - soft delete", () => {
    it("writes deletedAt + outbox event", async () => {
      prisma.$queryRaw.mockResolvedValue([mockRow()]);
      prisma.$executeRaw.mockResolvedValue(1);

      await service.remove(ZONE_ID, TENANT, "user-1");

      expect(prisma.$executeRaw).toHaveBeenCalled();
      expect(prisma.outboxEvent.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            eventType: "sahool.field.sub_zone.deleted",
            aggregateType: "FieldSubZone",
          }),
        }),
      );
    });
  });
});
