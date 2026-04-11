/**
 * FieldReportsService Unit Tests
 * اختبارات وحدة خدمة تقارير الحقل
 *
 * Covers request enqueueing, status-machine transitions, and tenant
 * isolation. The HTML renderer is tested separately.
 */

import { Test, TestingModule } from "@nestjs/testing";
import {
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { FieldReportsService } from "../field-reports.service";
import { PrismaService } from "../../prisma/prisma.service";
import { OutboxService } from "../../outbox/outbox.service";
import { HtmlReportRenderer } from "../renderers/html-report.renderer";
import { InMemoryReportStorage } from "../storage/inmemory-storage.adapter";
import { REPORT_STORAGE_TOKEN } from "../storage/storage.token";

const TENANT = "tenant-aaa-1111";
const OTHER = "tenant-bbb-2222";
const FIELD_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479";
const REPORT_ID = "11111111-2222-3333-4444-555555555555";
const SEASON_ID = "22222222-3333-4444-5555-666666666666";

function mockReport(overrides: Record<string, any> = {}) {
  return {
    id: REPORT_ID,
    tenantId: TENANT,
    fieldId: FIELD_ID,
    cropSeasonId: null,
    reportType: "field_summary",
    language: "ar",
    periodFrom: null,
    periodTo: null,
    status: "pending",
    renderedAt: null,
    errorMessage: null,
    renderAttempts: 0,
    contentHtml: null,
    contentUrl: null,
    contentSizeBytes: null,
    contentType: null,
    expiresAt: null,
    inputSnapshot: null,
    requestedBy: null,
    createdAt: new Date(),
    updatedAt: new Date(),
    ...overrides,
  };
}

function makePrismaMock() {
  return {
    field: { findUnique: jest.fn() },
    cropSeason: { findUnique: jest.fn(), findFirst: jest.fn() },
    fieldReport: {
      create: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
    },
    fieldOperation: { findMany: jest.fn() },
    outboxEvent: { create: jest.fn() },
    $queryRaw: jest.fn(),
  };
}

describe("FieldReportsService", () => {
  let service: FieldReportsService;
  let prisma: ReturnType<typeof makePrismaMock>;

  beforeEach(async () => {
    prisma = makePrismaMock();
    const outbox = {
      writeInTransaction: jest.fn(),
    } as unknown as OutboxService;
    const renderer = new HtmlReportRenderer();
    const storage = new InMemoryReportStorage();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FieldReportsService,
        { provide: PrismaService, useValue: prisma },
        { provide: OutboxService, useValue: outbox },
        { provide: HtmlReportRenderer, useValue: renderer },
        { provide: REPORT_STORAGE_TOKEN, useValue: storage },
      ],
    }).compile();

    service = module.get(FieldReportsService);
  });

  describe("requestReport", () => {
    it("rejects cross-tenant access via parent-field check", async () => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: OTHER,
        isDeleted: false,
      });
      await expect(
        service.requestReport(FIELD_ID, TENANT, {}),
      ).rejects.toThrow(NotFoundException);
    });

    it("rejects a cropSeasonId from a different field", async () => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: TENANT,
        isDeleted: false,
      });
      prisma.cropSeason.findUnique.mockResolvedValue({
        id: SEASON_ID,
        tenantId: TENANT,
        fieldId: "00000000-0000-0000-0000-999999999999",
        deletedAt: null,
      });
      await expect(
        service.requestReport(FIELD_ID, TENANT, {
          cropSeasonId: SEASON_ID,
        }),
      ).rejects.toThrow(NotFoundException);
    });

    it("creates a pending row with default type + language", async () => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: TENANT,
        isDeleted: false,
      });
      prisma.fieldReport.create.mockResolvedValue(mockReport());

      const result = await service.requestReport(
        FIELD_ID,
        TENANT,
        {},
        "user-1",
      );

      expect(prisma.fieldReport.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            tenantId: TENANT,
            fieldId: FIELD_ID,
            status: "pending",
            reportType: "field_summary",
            language: "ar",
            requestedBy: "user-1",
          }),
        }),
      );
      expect(result.status).toBe("pending");
    });

    it("enqueues a report.requested outbox event", async () => {
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        tenantId: TENANT,
        isDeleted: false,
      });
      prisma.fieldReport.create.mockResolvedValue(mockReport());

      await service.requestReport(FIELD_ID, TENANT, {});

      expect(prisma.outboxEvent.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            eventType: "sahool.field.report.requested",
            aggregateType: "FieldReport",
          }),
        }),
      );
    });
  });

  describe("getById", () => {
    it("rejects cross-tenant access", async () => {
      prisma.fieldReport.findUnique.mockResolvedValue(
        mockReport({ tenantId: OTHER }),
      );
      await expect(service.getById(REPORT_ID, TENANT)).rejects.toThrow(
        NotFoundException,
      );
    });

    it("returns the row when tenant matches", async () => {
      prisma.fieldReport.findUnique.mockResolvedValue(mockReport());
      const result = await service.getById(REPORT_ID, TENANT);
      expect(result.id).toBe(REPORT_ID);
    });
  });

  describe("getContent", () => {
    it("throws BadRequestException when report is not ready", async () => {
      prisma.fieldReport.findUnique.mockResolvedValue(
        mockReport({ status: "pending" }),
      );
      await expect(service.getContent(REPORT_ID, TENANT)).rejects.toThrow(
        BadRequestException,
      );
    });

    it("throws NotFoundException when ready but missing html", async () => {
      prisma.fieldReport.findUnique.mockResolvedValue(
        mockReport({ status: "ready", contentHtml: null }),
      );
      await expect(service.getContent(REPORT_ID, TENANT)).rejects.toThrow(
        NotFoundException,
      );
    });

    it("returns HTML when ready", async () => {
      const html = "<!DOCTYPE html><html>...</html>";
      prisma.fieldReport.findUnique.mockResolvedValue(
        mockReport({ status: "ready", contentHtml: html }),
      );
      const result = await service.getContent(REPORT_ID, TENANT);
      expect(result).toBe(html);
    });
  });

  describe("renderReport - state machine", () => {
    it("does nothing when pending→rendering transition fails (race)", async () => {
      prisma.fieldReport.updateMany.mockResolvedValue({ count: 0 });
      await service.renderReport(REPORT_ID);
      expect(prisma.fieldReport.update).not.toHaveBeenCalled();
    });

    it("renders a complete field summary for a tenant", async () => {
      prisma.fieldReport.updateMany.mockResolvedValue({ count: 1 });
      prisma.fieldReport.findUnique.mockResolvedValue(
        mockReport({ status: "rendering" }),
      );
      prisma.field.findUnique.mockResolvedValue({
        id: FIELD_ID,
        name: "Field Alpha",
        cropType: "wheat",
        areaHectares: 5.5,
        plantingDate: new Date("2026-01-15"),
        expectedHarvest: new Date("2026-06-15"),
        irrigationType: "drip",
        tenantId: TENANT,
      });
      prisma.cropSeason.findFirst.mockResolvedValue(null);
      prisma.fieldOperation.findMany.mockResolvedValue([]);
      prisma.$queryRaw.mockResolvedValue([]);
      prisma.fieldReport.update.mockResolvedValue(mockReport());

      await service.renderReport(REPORT_ID);

      // Confirm the row was updated to `ready` with HTML content.
      expect(prisma.fieldReport.update).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "ready",
            contentHtml: expect.stringContaining("<!DOCTYPE html>"),
            contentType: expect.stringContaining("text/html"),
          }),
        }),
      );
    });

    it("transitions to 'failed' when rendering throws", async () => {
      prisma.fieldReport.updateMany.mockResolvedValue({ count: 1 });
      prisma.fieldReport.findUnique.mockResolvedValue(
        mockReport({ status: "rendering" }),
      );
      prisma.field.findUnique.mockResolvedValue(null); // triggers failure path
      prisma.fieldReport.update.mockResolvedValue(mockReport());

      await service.renderReport(REPORT_ID);

      expect(prisma.fieldReport.update).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "failed",
            errorMessage: expect.any(String),
          }),
        }),
      );
    });
  });
});
