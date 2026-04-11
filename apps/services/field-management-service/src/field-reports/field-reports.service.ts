/**
 * Field Reports Service
 * خدمة تقارير الحقل — توليد HTML/PDF غير متزامن
 *
 * Two-phase flow:
 *
 *   1. Request phase (fast, synchronous): POST /fields/:id/reports
 *      → Insert a row with status='pending'
 *      → Return the new row's id + status
 *      → Client polls GET /field-reports/:id until status='ready'
 *
 *   2. Render phase (slow, background): FieldReportsWorker
 *      → Polls field_reports WHERE status='pending'
 *      → For each row: collect snapshot data, render HTML, upload
 *        via IReportStorageProvider, update row with URL + status.
 *
 * Rationale: reports may take 1-10 seconds to render (DB queries +
 * chart rasterization + upload). Blocking the API request for that
 * long is bad UX and ties up HTTP worker slots. The async pattern
 * matches Farmonaut's `getFieldReport` → static URL workflow and
 * gives us a natural place to add caching/dedup later.
 */

import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { OutboxService } from "../outbox/outbox.service";
import {
  HtmlReportRenderer,
  type ReportInputSnapshot,
  type ReportRenderType,
} from "./renderers/html-report.renderer";
import { InMemoryReportStorage } from "./storage/inmemory-storage.adapter";
import type {
  CreateFieldReportDto,
  QueryFieldReportsDto,
} from "./dto/field-report.dto";

@Injectable()
export class FieldReportsService {
  private readonly logger = new Logger(FieldReportsService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly outbox: OutboxService,
    private readonly renderer: HtmlReportRenderer,
    private readonly storage: InMemoryReportStorage,
  ) {}

  private uuidOrNull(value: string): string {
    const uuidRe =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRe.test(value)
      ? value
      : "00000000-0000-0000-0000-000000000000";
  }

  // ---------------------------------------------------------------------
  // Phase 1: Request (fast path)
  // ---------------------------------------------------------------------

  /**
   * Enqueue a new report generation request. Writes a `status=pending`
   * row and emits a `sahool.field.report.requested` outbox event so the
   * background worker (or any other async renderer) can pick it up.
   */
  async requestReport(
    fieldId: string,
    tenantId: string,
    dto: CreateFieldReportDto,
    requestedBy?: string,
  ) {
    await this.assertFieldOwnership(fieldId, tenantId);

    if (dto.cropSeasonId) {
      await this.assertCropSeasonOwnership(
        dto.cropSeasonId,
        fieldId,
        tenantId,
      );
    }

    const row = await this.prisma.fieldReport.create({
      data: {
        tenantId,
        fieldId,
        cropSeasonId: dto.cropSeasonId,
        reportType: dto.reportType ?? "field_summary",
        language: dto.language ?? "ar",
        periodFrom: dto.periodFrom ? new Date(dto.periodFrom) : null,
        periodTo: dto.periodTo ? new Date(dto.periodTo) : null,
        status: "pending",
        requestedBy,
      },
    });

    try {
      await this.prisma.outboxEvent.create({
        data: {
          eventType: "sahool.field.report.requested",
          eventVersion: 1,
          schemaRef: "sahool.field.report.requested:v1",
          tenantId: this.uuidOrNull(tenantId),
          correlationId: this.uuidOrNull(tenantId),
          aggregateType: "FieldReport",
          aggregateId: row.id,
          payloadJson: JSON.stringify({
            event_type: "sahool.field.report.requested",
            tenant_id: tenantId,
            field_id: fieldId,
            report_id: row.id,
            report_type: row.reportType,
            language: row.language,
            occurred_at: new Date().toISOString(),
          }),
          published: false,
        },
      });
    } catch (e) {
      this.logger.warn(
        `Failed to enqueue report.requested event: ${
          e instanceof Error ? e.message : e
        }`,
      );
    }

    return row;
  }

  /**
   * List reports for a field with optional filters. Returns newest first.
   */
  async list(
    fieldId: string,
    tenantId: string,
    filters: QueryFieldReportsDto,
  ) {
    await this.assertFieldOwnership(fieldId, tenantId);
    const where: Record<string, unknown> = { tenantId, fieldId };
    if (filters.reportType) where.reportType = filters.reportType;
    if (filters.status) where.status = filters.status;
    if (filters.cropSeasonId) where.cropSeasonId = filters.cropSeasonId;

    const items = await this.prisma.fieldReport.findMany({
      where: where as any,
      orderBy: { createdAt: "desc" },
      take: 100,
      // Don't return the full HTML in the list view — clients fetch the
      // URL separately to save bandwidth.
      select: {
        id: true,
        tenantId: true,
        fieldId: true,
        cropSeasonId: true,
        reportType: true,
        language: true,
        periodFrom: true,
        periodTo: true,
        status: true,
        renderedAt: true,
        errorMessage: true,
        renderAttempts: true,
        contentUrl: true,
        contentSizeBytes: true,
        contentType: true,
        expiresAt: true,
        requestedBy: true,
        createdAt: true,
        updatedAt: true,
      },
    });
    return items;
  }

  /**
   * Fetch a single report metadata row (tenant-scoped).
   */
  async getById(id: string, tenantId: string) {
    const row = await this.prisma.fieldReport.findUnique({
      where: { id },
    });
    if (!row || row.tenantId !== tenantId) {
      throw new NotFoundException({
        message: "Report not found",
        messageAr: "التقرير غير موجود",
      });
    }
    return row;
  }

  /**
   * Stream the rendered HTML for a report. Used by GET
   * /field-reports/:id/content so the InMemoryReportStorage URL resolves
   * to actual bytes. For the S3 backend this endpoint is never called
   * (client goes directly to the signed URL).
   */
  async getContent(id: string, tenantId: string): Promise<string> {
    const row = await this.getById(id, tenantId);
    if (row.status !== "ready") {
      throw new BadRequestException({
        message: `Report is not ready (status: ${row.status})`,
        messageAr: `التقرير غير جاهز (الحالة: ${row.status})`,
      });
    }
    if (!row.contentHtml) {
      throw new NotFoundException({
        message: "Report content not available",
        messageAr: "محتوى التقرير غير متوفر",
      });
    }
    return row.contentHtml;
  }

  // ---------------------------------------------------------------------
  // Phase 2: Render (background worker entry point)
  // ---------------------------------------------------------------------

  /**
   * Render a single pending report. Called by FieldReportsWorker.tick()
   * for each row with status='pending'.
   */
  async renderReport(reportId: string): Promise<void> {
    // Atomically transition pending → rendering to prevent two workers
    // from racing on the same row.
    const locked = await this.prisma.fieldReport.updateMany({
      where: { id: reportId, status: "pending" },
      data: {
        status: "rendering",
        renderAttempts: { increment: 1 },
      },
    });
    if (locked.count === 0) {
      // Another worker already picked it up (or the row was deleted).
      return;
    }

    const row = await this.prisma.fieldReport.findUnique({
      where: { id: reportId },
    });
    if (!row) return;

    try {
      const snapshot = await this.buildSnapshot(row);

      const rendered = this.renderer.render({
        reportType: row.reportType as ReportRenderType,
        language: (row.language as "ar" | "en") ?? "ar",
        snapshot,
      });

      const uploaded = await this.storage.store({
        tenantId: row.tenantId,
        fieldId: row.fieldId,
        reportId: row.id,
        contentType: rendered.contentType,
        body: rendered.html,
      });

      await this.prisma.fieldReport.update({
        where: { id: reportId },
        data: {
          status: "ready",
          renderedAt: new Date(),
          contentHtml: rendered.html,
          contentUrl: uploaded.url,
          contentSizeBytes: BigInt(uploaded.sizeBytes),
          contentType: uploaded.contentType,
          expiresAt: uploaded.expiresAt,
          inputSnapshot: this.snapshotForAudit(snapshot) as any,
          errorMessage: null,
        },
      });

      try {
        await this.prisma.outboxEvent.create({
          data: {
            eventType: "sahool.field.report.ready",
            eventVersion: 1,
            schemaRef: "sahool.field.report.ready:v1",
            tenantId: this.uuidOrNull(row.tenantId),
            correlationId: this.uuidOrNull(row.tenantId),
            aggregateType: "FieldReport",
            aggregateId: row.id,
            payloadJson: JSON.stringify({
              event_type: "sahool.field.report.ready",
              tenant_id: row.tenantId,
              field_id: row.fieldId,
              report_id: row.id,
              report_type: row.reportType,
              url: uploaded.url,
              size_bytes: uploaded.sizeBytes,
              occurred_at: new Date().toISOString(),
            }),
            published: false,
          },
        });
      } catch {
        // best-effort
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      this.logger.error(`Render failed for ${reportId}: ${msg}`);
      await this.prisma.fieldReport.update({
        where: { id: reportId },
        data: {
          status: "failed",
          errorMessage: msg.slice(0, 2000),
        },
      });
      try {
        await this.prisma.outboxEvent.create({
          data: {
            eventType: "sahool.field.report.failed",
            eventVersion: 1,
            schemaRef: "sahool.field.report.failed:v1",
            tenantId: this.uuidOrNull(row.tenantId),
            correlationId: this.uuidOrNull(row.tenantId),
            aggregateType: "FieldReport",
            aggregateId: row.id,
            payloadJson: JSON.stringify({
              event_type: "sahool.field.report.failed",
              tenant_id: row.tenantId,
              field_id: row.fieldId,
              report_id: row.id,
              error: msg.slice(0, 500),
              occurred_at: new Date().toISOString(),
            }),
            published: false,
          },
        });
      } catch {
        // best-effort
      }
    }
  }

  // ---------------------------------------------------------------------
  // Data collection for the renderer
  // ---------------------------------------------------------------------

  /**
   * Build a ReportInputSnapshot by querying all the data the renderer
   * needs. This is deliberately centralised so new report types can
   * extend it without touching the renderer.
   */
  private async buildSnapshot(row: {
    fieldId: string;
    tenantId: string;
    cropSeasonId: string | null;
    periodFrom: Date | null;
    periodTo: Date | null;
  }): Promise<ReportInputSnapshot> {
    const field = await this.prisma.field.findUnique({
      where: { id: row.fieldId },
      select: {
        id: true,
        name: true,
        cropType: true,
        areaHectares: true,
        plantingDate: true,
        expectedHarvest: true,
        irrigationType: true,
        tenantId: true,
      },
    });
    if (!field) {
      throw new Error("Field not found during snapshot build");
    }

    // Get the current (or explicit) crop season.
    const currentSeason = await this.prisma.cropSeason.findFirst({
      where: row.cropSeasonId
        ? { id: row.cropSeasonId, tenantId: row.tenantId }
        : {
            fieldId: row.fieldId,
            tenantId: row.tenantId,
            isCurrent: true,
            deletedAt: null,
          },
      orderBy: { sowingDate: "desc" },
    });

    const opWhere: Record<string, unknown> = {
      tenantId: row.tenantId,
      fieldId: row.fieldId,
      deletedAt: null,
    };
    if (currentSeason) opWhere.cropSeasonId = currentSeason.id;
    if (row.periodFrom || row.periodTo) {
      const range: { gte?: Date; lte?: Date } = {};
      if (row.periodFrom) range.gte = row.periodFrom;
      if (row.periodTo) range.lte = row.periodTo;
      opWhere.performedAt = range;
    }

    const operations = await this.prisma.fieldOperation.findMany({
      where: opWhere as any,
      orderBy: { performedAt: "desc" },
      take: 500,
    });

    // Sub-zones via raw SQL (PostGIS geometries not round-trip-safe
    // through Prisma's typed API).
    const subZones = await this.prisma.$queryRaw<
      Array<{
        id: string;
        name: string;
        name_ar: string | null;
        area_hectares: string | number | null;
        is_terrace: boolean;
        terrace_level: number | null;
      }>
    >`
      SELECT id, name, name_ar, area_hectares, is_terrace, terrace_level
      FROM field_sub_zones
      WHERE tenant_id = ${row.tenantId}
        AND field_id = ${row.fieldId}::uuid
        AND deleted_at IS NULL
      ORDER BY display_order ASC, created_at ASC
    `;

    return {
      field: {
        id: field.id,
        name: field.name,
        nameAr: null,
        cropType: field.cropType,
        areaHectares: field.areaHectares ? Number(field.areaHectares) : null,
        plantingDate: field.plantingDate,
        expectedHarvest: field.expectedHarvest,
        irrigationType: field.irrigationType,
        tenantId: field.tenantId,
      },
      currentSeason: currentSeason
        ? {
            id: currentSeason.id,
            cropType: currentSeason.cropType,
            cropTypeAr: currentSeason.cropTypeAr,
            sowingDate: currentSeason.sowingDate,
            expectedHarvestDate: currentSeason.expectedHarvestDate,
            seedVariety: currentSeason.seedVariety,
            plantingDensityKgHa: currentSeason.plantingDensityKgHa
              ? Number(currentSeason.plantingDensityKgHa)
              : null,
            totalSeasonCost: currentSeason.totalSeasonCost
              ? Number(currentSeason.totalSeasonCost)
              : null,
            totalSeasonHours: currentSeason.totalSeasonHours
              ? Number(currentSeason.totalSeasonHours)
              : null,
            totalCo2EmissionsKg: currentSeason.totalCo2EmissionsKg
              ? Number(currentSeason.totalCo2EmissionsKg)
              : null,
            totalCo2SequestrationKg: currentSeason.totalCo2SequestrationKg
              ? Number(currentSeason.totalCo2SequestrationKg)
              : null,
            totalCo2NetKg: currentSeason.totalCo2NetKg
              ? Number(currentSeason.totalCo2NetKg)
              : null,
          }
        : null,
      operations: operations.map((op) => ({
        id: op.id,
        operationType: op.operationType,
        performedAt: op.performedAt,
        durationHours: op.durationHours ? Number(op.durationHours) : null,
        costAmount: op.costAmount ? Number(op.costAmount) : null,
        costCurrency: op.costCurrency,
        equipmentName: op.equipmentName,
        equipmentNameAr: op.equipmentNameAr,
        co2EmissionsKg: op.co2EmissionsKg ? Number(op.co2EmissionsKg) : null,
        co2SequestrationKg: op.co2SequestrationKg
          ? Number(op.co2SequestrationKg)
          : null,
        notes: op.notes,
      })),
      subZones: subZones.map((z) => ({
        id: z.id,
        name: z.name,
        nameAr: z.name_ar,
        areaHectares: z.area_hectares ? Number(z.area_hectares) : null,
        isTerrace: z.is_terrace,
        terraceLevel: z.terrace_level,
      })),
      period: {
        from: row.periodFrom,
        to: row.periodTo,
        generatedAt: new Date(),
      },
    };
  }

  /**
   * Strip sensitive data before persisting to input_snapshot for audit.
   * Currently we retain IDs + counts + totals but not full rows.
   */
  private snapshotForAudit(s: ReportInputSnapshot): Record<string, unknown> {
    return {
      field_id: s.field.id,
      operations_count: s.operations.length,
      sub_zones_count: s.subZones?.length ?? 0,
      has_current_season: !!s.currentSeason,
      generated_at: s.period.generatedAt.toISOString(),
    };
  }

  // ---------------------------------------------------------------------
  // Tenant guards
  // ---------------------------------------------------------------------

  private async assertFieldOwnership(fieldId: string, tenantId: string) {
    const field = await this.prisma.field.findUnique({
      where: { id: fieldId },
      select: { id: true, tenantId: true, isDeleted: true },
    });
    if (!field || field.isDeleted || field.tenantId !== tenantId) {
      throw new NotFoundException({
        message: "Field not found",
        messageAr: "الحقل غير موجود",
      });
    }
  }

  private async assertCropSeasonOwnership(
    cropSeasonId: string,
    fieldId: string,
    tenantId: string,
  ) {
    const season = await this.prisma.cropSeason.findUnique({
      where: { id: cropSeasonId },
      select: { id: true, tenantId: true, fieldId: true, deletedAt: true },
    });
    if (
      !season ||
      season.deletedAt ||
      season.tenantId !== tenantId ||
      season.fieldId !== fieldId
    ) {
      throw new NotFoundException({
        message: "Crop season not found on this field",
        messageAr: "الموسم المحصولي غير موجود لهذا الحقل",
      });
    }
  }
}
