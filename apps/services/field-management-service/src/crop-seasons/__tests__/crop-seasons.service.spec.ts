/**
 * CropSeasonsService Unit Tests
 * اختبارات وحدة خدمة مواسم المحاصيل
 *
 * Covers tenant isolation, transactional close-old-insert-new logic,
 * partial unique index guard (one current season per field), outbox
 * writes, and soft delete.
 */

import { Test, TestingModule } from "@nestjs/testing";
import {
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { CropSeasonsService } from "../crop-seasons.service";
import { PrismaService } from "../../prisma/prisma.service";
import { FieldEventsService } from "../../events/field-events.service";
import { OutboxService } from "../../outbox/outbox.service";

const TENANT = "tenant-aaa-1111";
const OTHER = "tenant-bbb-2222";
const FIELD_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479";
const SEASON_ID = "11111111-2222-3333-4444-555555555555";

function makeField(overrides: Record<string, any> = {}) {
  return {
    id: FIELD_ID,
    tenantId: TENANT,
    isDeleted: false,
    ...overrides,
  };
}

function makeSeason(overrides: Record<string, any> = {}) {
  return {
    id: SEASON_ID,
    fieldId: FIELD_ID,
    tenantId: TENANT,
    cropType: "wheat",
    cropTypeAr: null,
    season: "winter",
    sowingDate: new Date("2026-01-01"),
    expectedHarvestDate: new Date("2026-06-01"),
    actualHarvestDate: null,
    endedAt: null,
    endReason: null,
    isCurrent: true,
    seedVariety: null,
    seedVarietyAr: null,
    plantingDensityKgHa: null,
    irrigationType: null,
    yieldKgHa: null,
    notes: null,
    metadata: null,
    externalId: null,
    externalSource: null,
    costCenter: null,
    projectCode: null,
    baseCurrency: null,
    totalSeasonCost: null,
    totalSeasonRevenue: null,
    totalSeasonHours: null,
    totalsUpdatedAt: null,
    deletedAt: null,
    deletedBy: null,
    deletedReason: null,
    createdAt: new Date(),
    updatedAt: new Date(),
    ...overrides,
  };
}

// Build a minimal mock Prisma that transparently forwards between the
// root client and the transaction client. Tests replace specific model
// methods with jest.fn() before calling the service.
function makePrismaMock() {
  const txClient = {
    cropSeason: {
      findFirst: jest.fn(),
      update: jest.fn(),
      create: jest.fn(),
      updateMany: jest.fn(),
    },
    field: {
      update: jest.fn(),
    },
    outboxEvent: {
      create: jest.fn(),
    },
  };
  return {
    tx: txClient,
    client: {
      field: { findUnique: jest.fn() },
      cropSeason: {
        findMany: jest.fn(),
        count: jest.fn(),
        findUnique: jest.fn(),
        findFirst: jest.fn(),
        update: jest.fn(),
      },
      $transaction: jest.fn(
        async (fn: (tx: typeof txClient) => Promise<unknown>) => fn(txClient),
      ),
    },
  };
}

describe("CropSeasonsService", () => {
  let service: CropSeasonsService;
  let prisma: ReturnType<typeof makePrismaMock>;
  let outbox: OutboxService;

  beforeEach(async () => {
    prisma = makePrismaMock();
    const events = {
      publishCropSeasonStarted: jest.fn(),
      publishCropSeasonUpdated: jest.fn(),
      publishCropSeasonEnded: jest.fn(),
      publishCropSeasonDeleted: jest.fn(),
    };
    outbox = { writeInTransaction: jest.fn() } as unknown as OutboxService;

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        CropSeasonsService,
        { provide: PrismaService, useValue: prisma.client },
        { provide: FieldEventsService, useValue: events },
        { provide: OutboxService, useValue: outbox },
      ],
    }).compile();

    service = module.get(CropSeasonsService);
  });

  describe("list()", () => {
    it("filters by tenant and excludes soft-deleted rows", async () => {
      prisma.client.cropSeason.findMany.mockResolvedValue([]);
      prisma.client.cropSeason.count.mockResolvedValue(0);

      await service.list(TENANT, {});

      const where = prisma.client.cropSeason.findMany.mock.calls[0][0].where;
      expect(where.tenantId).toBe(TENANT);
      expect(where.deletedAt).toBeNull();
    });

    it("verifies field ownership before returning", async () => {
      prisma.client.field.findUnique.mockResolvedValue(
        makeField({ tenantId: OTHER }),
      );
      await expect(
        service.list(TENANT, { fieldId: FIELD_ID }),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("getById()", () => {
    it("rejects cross-tenant access", async () => {
      prisma.client.cropSeason.findUnique.mockResolvedValue(
        makeSeason({ tenantId: OTHER }),
      );
      await expect(service.getById(SEASON_ID, TENANT)).rejects.toThrow(
        NotFoundException,
      );
    });

    it("rejects soft-deleted rows", async () => {
      prisma.client.cropSeason.findUnique.mockResolvedValue(
        makeSeason({ deletedAt: new Date() }),
      );
      await expect(service.getById(SEASON_ID, TENANT)).rejects.toThrow(
        NotFoundException,
      );
    });

    it("returns the row on tenant match", async () => {
      const row = makeSeason();
      prisma.client.cropSeason.findUnique.mockResolvedValue(row);
      await expect(service.getById(SEASON_ID, TENANT)).resolves.toBe(row);
    });
  });

  describe("create()", () => {
    beforeEach(() => {
      prisma.client.field.findUnique.mockResolvedValue(makeField());
      prisma.tx.cropSeason.findFirst.mockResolvedValue(null);
      prisma.tx.cropSeason.create.mockResolvedValue(makeSeason());
      prisma.tx.cropSeason.update.mockResolvedValue(makeSeason());
      prisma.tx.cropSeason.updateMany.mockResolvedValue({ count: 0 });
      prisma.tx.field.update.mockResolvedValue({});
    });

    it("rejects when sowing date is invalid", async () => {
      await expect(
        service.create(FIELD_ID, TENANT, {
          cropType: "wheat",
          sowingDate: "not-a-date",
        }),
      ).rejects.toThrow(BadRequestException);
    });

    it("rejects when expected harvest is before sowing", async () => {
      await expect(
        service.create(FIELD_ID, TENANT, {
          cropType: "wheat",
          sowingDate: "2026-06-01",
          expectedHarvestDate: "2026-03-01",
        }),
      ).rejects.toThrow(BadRequestException);
    });

    it("closes the previous active season and writes outbox events", async () => {
      const previous = makeSeason({
        id: "00000000-1111-2222-3333-444444444444",
      });
      prisma.tx.cropSeason.findFirst.mockResolvedValue(previous);

      await service.create(FIELD_ID, TENANT, {
        cropType: "wheat",
        sowingDate: "2026-01-01",
      });

      // Previous row should be closed
      expect(prisma.tx.cropSeason.update).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { id: previous.id },
          data: expect.objectContaining({
            isCurrent: false,
            endedAt: expect.any(Date),
          }),
        }),
      );
      // Two outbox writes: ended + started
      expect(
        (outbox.writeInTransaction as jest.Mock).mock.calls.length,
      ).toBeGreaterThanOrEqual(2);
      const eventTypes = (outbox.writeInTransaction as jest.Mock).mock.calls.map(
        (c: any[]) => c[1].eventType,
      );
      expect(eventTypes).toEqual(
        expect.arrayContaining([
          "sahool.field.crop_season.ended",
          "sahool.field.crop_season.started",
        ]),
      );
    });

    it("mirrors the crop type onto the parent Field row", async () => {
      await service.create(FIELD_ID, TENANT, {
        cropType: "barley",
        sowingDate: "2026-01-01",
      });
      expect(prisma.tx.field.update).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { id: FIELD_ID },
          data: expect.objectContaining({ cropType: "barley" }),
        }),
      );
    });
  });

  describe("remove() - soft delete", () => {
    it("sets deletedAt and writes the outbox event", async () => {
      prisma.client.cropSeason.findUnique.mockResolvedValue(makeSeason());
      prisma.tx.cropSeason.update.mockResolvedValue(
        makeSeason({ deletedAt: new Date() }),
      );

      await service.remove(SEASON_ID, TENANT, "user-1", "manual correction");

      expect(prisma.tx.cropSeason.update).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            deletedAt: expect.any(Date),
            deletedBy: "user-1",
            deletedReason: "manual correction",
            isCurrent: false,
          }),
        }),
      );
      expect(outbox.writeInTransaction).toHaveBeenCalled();
    });
  });
});
