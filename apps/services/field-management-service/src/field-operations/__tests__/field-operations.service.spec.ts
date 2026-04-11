/**
 * FieldOperationsService Unit Tests
 * اختبارات وحدة خدمة عمليات الحقل
 *
 * Covers tenant isolation, cost-breakdown derivation, outbox writes
 * on create/update/delete, approval workflow, posted-to-ERP locking,
 * soft delete, and per-season rollup calculation.
 */

import { Test, TestingModule } from "@nestjs/testing";
import {
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { FieldOperationsService } from "../field-operations.service";
import { PrismaService } from "../../prisma/prisma.service";
import { FieldEventsService } from "../../events/field-events.service";
import { OutboxService } from "../../outbox/outbox.service";

const TENANT = "tenant-aaa-1111";
const OTHER = "tenant-bbb-2222";
const FIELD_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479";
const SEASON_ID = "11111111-2222-3333-4444-555555555555";
const OP_ID = "99999999-8888-7777-6666-555555555555";

function makeField(overrides: Record<string, any> = {}) {
  return {
    id: FIELD_ID,
    tenantId: TENANT,
    isDeleted: false,
    ...overrides,
  };
}

function makeOperation(overrides: Record<string, any> = {}) {
  return {
    id: OP_ID,
    tenantId: TENANT,
    fieldId: FIELD_ID,
    cropSeasonId: SEASON_ID,
    operationType: "plowing",
    performedAt: new Date("2026-01-10"),
    endedAt: null,
    durationHours: 6,
    costAmount: 1200,
    costCurrency: "SAR",
    fuelLiters: null,
    fuelCost: 400,
    laborHours: 6,
    laborCost: 500,
    materialsCost: null,
    overheadCost: 300,
    otherCost: null,
    taxAmount: 60,
    taxRate: 5,
    exchangeRate: null,
    baseCurrency: "SAR",
    invoiceNumber: "INV-001",
    invoiceDate: null,
    vendorId: "vendor-1",
    vendorName: "Al-Falah Equipment",
    receiptUrl: null,
    glAccount: "6100-TILLAGE",
    costCenter: "FARM-01",
    projectCode: "WHEAT-W1",
    externalId: null,
    externalSource: null,
    postedToErp: false,
    postedAt: null,
    postingReference: null,
    postingError: null,
    postingAttempts: 0,
    approvalStatus: "approved",
    approvedBy: "user-1",
    approvedAt: new Date(),
    rejectionReason: null,
    equipmentId: "eq-1",
    equipmentName: "John Deere 6120",
    equipmentNameAr: "جون دير 6120",
    metadata: null,
    notes: null,
    deletedAt: null,
    deletedBy: null,
    deletedReason: null,
    createdBy: "user-1",
    createdAt: new Date(),
    updatedAt: new Date(),
    ...overrides,
  };
}

function makePrismaMock() {
  const txClient = {
    fieldOperation: {
      create: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
    },
    outboxEvent: { create: jest.fn() },
    cropSeason: { updateMany: jest.fn() },
  };
  return {
    tx: txClient,
    client: {
      field: { findUnique: jest.fn() },
      cropSeason: {
        findUnique: jest.fn(),
        updateMany: jest.fn(),
      },
      fieldOperation: {
        findMany: jest.fn(),
        count: jest.fn(),
        findUnique: jest.fn(),
      },
      $transaction: jest.fn(
        async (fn: (tx: typeof txClient) => Promise<unknown>) => fn(txClient),
      ),
    },
  };
}

describe("FieldOperationsService", () => {
  let service: FieldOperationsService;
  let prisma: ReturnType<typeof makePrismaMock>;
  let outbox: OutboxService;

  beforeEach(async () => {
    prisma = makePrismaMock();
    const events = {
      publishFieldOperationRecorded: jest.fn(),
      publishFieldOperationUpdated: jest.fn(),
      publishFieldOperationDeleted: jest.fn(),
    };
    outbox = { writeInTransaction: jest.fn() } as unknown as OutboxService;

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FieldOperationsService,
        { provide: PrismaService, useValue: prisma.client },
        { provide: FieldEventsService, useValue: events },
        { provide: OutboxService, useValue: outbox },
      ],
    }).compile();

    service = module.get(FieldOperationsService);
  });

  describe("create()", () => {
    beforeEach(() => {
      prisma.client.field.findUnique.mockResolvedValue(makeField());
      prisma.tx.fieldOperation.create.mockImplementation(async ({ data }) =>
        makeOperation(data),
      );
    });

    it("rejects invalid performedAt", async () => {
      await expect(
        service.create(FIELD_ID, TENANT, {
          operationType: "plowing",
          performedAt: "not-a-date",
        }),
      ).rejects.toThrow(BadRequestException);
    });

    it("rejects endedAt < performedAt", async () => {
      await expect(
        service.create(FIELD_ID, TENANT, {
          operationType: "plowing",
          performedAt: "2026-01-10",
          endedAt: "2026-01-09T10:00:00Z",
        }),
      ).rejects.toThrow(BadRequestException);
    });

    it("derives total cost from cost breakdown when costAmount omitted", async () => {
      await service.create(FIELD_ID, TENANT, {
        operationType: "plowing",
        performedAt: "2026-01-10",
        fuelCost: 400,
        laborCost: 500,
        overheadCost: 300,
      });

      const created = prisma.tx.fieldOperation.create.mock.calls[0][0].data;
      expect(created.costAmount).toBe(1200);
    });

    it("writes the outbox event with cost breakdown payload", async () => {
      await service.create(FIELD_ID, TENANT, {
        operationType: "plowing",
        performedAt: "2026-01-10",
        fuelCost: 400,
        laborCost: 500,
        overheadCost: 300,
      });

      expect(outbox.writeInTransaction).toHaveBeenCalled();
      const [, envelope] =
        (outbox.writeInTransaction as jest.Mock).mock.calls[0];
      expect(envelope.eventType).toBe("sahool.field.operation.recorded");
      expect(envelope.aggregateType).toBe("FieldOperation");
      expect(envelope.payload.costBreakdown).toEqual(
        expect.objectContaining({ fuel: 400, labor: 500, overhead: 300 }),
      );
    });
  });

  describe("update()", () => {
    it("blocks updates to operations already posted to ERP", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(
        makeOperation({ postedToErp: true }),
      );
      await expect(
        service.update(OP_ID, TENANT, { costAmount: 999 }),
      ).rejects.toThrow(BadRequestException);
    });

    it("rejects cross-tenant access", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(
        makeOperation({ tenantId: OTHER }),
      );
      await expect(
        service.update(OP_ID, TENANT, { costAmount: 999 }),
      ).rejects.toThrow(NotFoundException);
    });

    it("writes an outbox event on successful update", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(makeOperation());
      prisma.tx.fieldOperation.update.mockResolvedValue(makeOperation());
      await service.update(OP_ID, TENANT, { notes: "updated notes" });
      expect(outbox.writeInTransaction).toHaveBeenCalled();
    });
  });

  describe("approval workflow", () => {
    it("approve() flips approvalStatus to approved", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(
        makeOperation({ approvalStatus: "pending" }),
      );
      prisma.tx.fieldOperation.update.mockResolvedValue(
        makeOperation({ approvalStatus: "approved" }),
      );
      const row = await service.approve(OP_ID, TENANT, "reviewer-1");
      expect(row.approvalStatus).toBe("approved");
      expect(outbox.writeInTransaction).toHaveBeenCalled();
    });

    it("approve() rejects already-rejected operations", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(
        makeOperation({ approvalStatus: "rejected" }),
      );
      await expect(service.approve(OP_ID, TENANT, "x")).rejects.toThrow(
        BadRequestException,
      );
    });

    it("reject() requires a reason and writes outbox event", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(
        makeOperation({ approvalStatus: "pending" }),
      );
      prisma.tx.fieldOperation.update.mockResolvedValue(
        makeOperation({ approvalStatus: "rejected" }),
      );
      await service.reject(OP_ID, TENANT, "invalid invoice", "reviewer-1");
      expect(outbox.writeInTransaction).toHaveBeenCalled();
      const [, envelope] = (outbox.writeInTransaction as jest.Mock).mock
        .calls[0];
      expect(envelope.eventType).toBe("sahool.field.operation.rejected");
      expect(envelope.payload.reason).toBe("invalid invoice");
    });
  });

  describe("remove() - soft delete", () => {
    it("blocks delete if already posted to ERP", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(
        makeOperation({ postedToErp: true }),
      );
      await expect(service.remove(OP_ID, TENANT, "user-1")).rejects.toThrow(
        BadRequestException,
      );
    });

    it("soft-deletes and writes an event", async () => {
      prisma.client.fieldOperation.findUnique.mockResolvedValue(makeOperation());
      prisma.tx.fieldOperation.update.mockResolvedValue(
        makeOperation({ deletedAt: new Date() }),
      );
      await service.remove(OP_ID, TENANT, "user-1", "mistake");
      expect(prisma.tx.fieldOperation.update).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            deletedAt: expect.any(Date),
            deletedBy: "user-1",
            deletedReason: "mistake",
          }),
        }),
      );
      expect(outbox.writeInTransaction).toHaveBeenCalled();
    });
  });

  describe("rollupForCropSeason()", () => {
    it("aggregates hours, cost, and breakdown across operations", async () => {
      prisma.client.cropSeason.findUnique.mockResolvedValue({
        id: SEASON_ID,
        tenantId: TENANT,
      });
      prisma.client.fieldOperation.findMany.mockResolvedValue([
        makeOperation({
          durationHours: 6,
          costAmount: 1000,
          fuelCost: 300,
          laborCost: 400,
          materialsCost: 200,
          overheadCost: 100,
          taxAmount: 50,
        }),
        makeOperation({
          durationHours: 4,
          costAmount: 800,
          fuelCost: 200,
          laborCost: 400,
          materialsCost: 100,
          overheadCost: 100,
          taxAmount: 40,
        }),
      ]);
      prisma.client.cropSeason.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.rollupForCropSeason(SEASON_ID, TENANT);

      expect(result.totalOperations).toBe(2);
      expect(result.totalHours).toBe(10);
      expect(result.totalCost).toBe(1800);
      expect(result.costBreakdown.fuel).toBe(500);
      expect(result.costBreakdown.labor).toBe(800);
      expect(result.costBreakdown.materials).toBe(300);
      expect(result.costBreakdown.overhead).toBe(200);
      expect(result.costBreakdown.tax).toBe(90);
    });

    it("rejects cross-tenant access", async () => {
      prisma.client.cropSeason.findUnique.mockResolvedValue({
        id: SEASON_ID,
        tenantId: OTHER,
      });
      await expect(
        service.rollupForCropSeason(SEASON_ID, TENANT),
      ).rejects.toThrow(NotFoundException);
    });
  });
});
