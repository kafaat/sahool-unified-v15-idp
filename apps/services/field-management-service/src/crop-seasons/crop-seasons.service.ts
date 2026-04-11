/**
 * Crop Seasons Service
 * خدمة مواسم المحاصيل
 *
 * First-class archive of per-field crop rotations. Replaces the earlier
 * `field.metadata.cropHistory[]` JSON shim. Enforces:
 *
 *   - Exactly one isCurrent=true season per field (DB-level partial
 *     unique index + application-level transaction wrap).
 *   - Tenant isolation on every query (the controller passes tenantId
 *     from the JWT; service layer never trusts a body-supplied tenantId).
 *   - Soft end-of-season: closing a season sets endedAt + isCurrent=false
 *     but keeps the row for historical queries / yield back-testing.
 */

import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { FieldEventsService } from "../events/field-events.service";
import { OutboxService } from "../outbox/outbox.service";
import type {
  CreateCropSeasonDto,
  UpdateCropSeasonDto,
  EndCropSeasonDto,
  QueryCropSeasonsDto,
} from "./dto/crop-season.dto";

@Injectable()
export class CropSeasonsService {
  private readonly logger = new Logger(CropSeasonsService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly events: FieldEventsService,
    private readonly outbox: OutboxService,
  ) {}

  /**
   * List crop seasons scoped to the authenticated tenant. If fieldId is
   * provided, also verifies that field exists and belongs to the tenant.
   */
  async list(tenantId: string, q: QueryCropSeasonsDto) {
    if (q.fieldId) {
      await this.assertFieldOwnership(q.fieldId, tenantId);
    }
    // Always filter out soft-deleted rows unless the caller explicitly
    // asks via metadata — audit queries can use the raw table.
    const where: Record<string, unknown> = {
      tenantId,
      deletedAt: null,
    };
    if (q.fieldId) where.fieldId = q.fieldId;
    if (q.cropType) where.cropType = q.cropType;
    if (typeof q.isCurrent === "boolean") where.isCurrent = q.isCurrent;
    if (q.sowingAfter || q.sowingBefore) {
      const range: { gte?: Date; lte?: Date } = {};
      if (q.sowingAfter) range.gte = new Date(q.sowingAfter);
      if (q.sowingBefore) range.lte = new Date(q.sowingBefore);
      where.sowingDate = range;
    }

    const take = Math.min(q.limit ?? 50, 100);
    const skip = q.offset ?? 0;

    const [items, total] = await Promise.all([
      this.prisma.cropSeason.findMany({
        where: where as any,
        orderBy: [{ sowingDate: "desc" }, { createdAt: "desc" }],
        take,
        skip,
      }),
      this.prisma.cropSeason.count({ where: where as any }),
    ]);

    return { items, total, limit: take, offset: skip };
  }

  /**
   * Fetch a single crop season by id, enforcing tenant ownership.
   */
  async getById(id: string, tenantId: string) {
    const row = await this.prisma.cropSeason.findUnique({ where: { id } });
    if (!row || row.tenantId !== tenantId || row.deletedAt) {
      throw new NotFoundException({
        message: "Crop season not found",
        messageAr: "الموسم المحصولي غير موجود",
      });
    }
    return row;
  }

  /**
   * Create a new crop season. If the field already has an `isCurrent` row,
   * that row is automatically closed (endedAt = now, isCurrent = false)
   * inside the same transaction so the partial unique index holds.
   */
  async create(
    fieldId: string,
    tenantId: string,
    dto: CreateCropSeasonDto,
    createdBy?: string,
  ) {
    await this.assertFieldOwnership(fieldId, tenantId);

    // Validate sowing date is a real date
    const sowingDate = new Date(dto.sowingDate);
    if (Number.isNaN(sowingDate.getTime())) {
      throw new BadRequestException({
        message: "Invalid sowing date",
        messageAr: "تاريخ البذار غير صالح",
      });
    }
    const expectedHarvestDate = dto.expectedHarvestDate
      ? new Date(dto.expectedHarvestDate)
      : null;
    if (
      expectedHarvestDate &&
      expectedHarvestDate.getTime() < sowingDate.getTime()
    ) {
      throw new BadRequestException({
        message: "Expected harvest date must be after sowing date",
        messageAr: "تاريخ الحصاد المتوقع يجب أن يكون بعد تاريخ البذار",
      });
    }

    // Single-transaction close-old + insert-new + outbox-write so the
    // partial unique index never observes two "current" rows AND the
    // downstream NATS event is guaranteed to be published at-least-once
    // via the outbox publisher (reliable delivery to NDVI pipeline,
    // yield-prediction, advisory-service, ERP webhooks).
    const result = await this.prisma.$transaction(async (tx) => {
      // Close any previously-active season.
      const previous = await tx.cropSeason.findFirst({
        where: { fieldId, isCurrent: true, deletedAt: null },
      });
      if (previous) {
        await tx.cropSeason.update({
          where: { id: previous.id },
          data: { isCurrent: false, endedAt: new Date() },
        });
        await this.outbox.writeInTransaction(tx, {
          eventType: "sahool.field.crop_season.ended",
          tenantId: this.uuidOrNull(tenantId),
          aggregateType: "CropSeason",
          aggregateId: previous.id,
          payload: {
            tenantId,
            fieldId,
            cropSeasonId: previous.id,
            endedAt: new Date().toISOString(),
            endReason: "superseded_by_new_season",
          },
        });
      }

      const row = await tx.cropSeason.create({
        data: {
          tenantId,
          fieldId,
          cropType: dto.cropType,
          cropTypeAr: dto.cropTypeAr,
          season: dto.season,
          sowingDate,
          expectedHarvestDate,
          isCurrent: true,
          seedVariety: dto.seedVariety,
          seedVarietyAr: dto.seedVarietyAr,
          plantingDensityKgHa: dto.plantingDensityKgHa as any,
          irrigationType: dto.irrigationType,
          notes: dto.notes,
          metadata: (createdBy ? { createdBy } : undefined) as any,
        },
      });

      // Mirror the current crop type on the parent Field row so
      // existing consumers of `field.cropType` (legacy code, NDVI
      // pipeline baseline, advisory cache) keep working unchanged.
      await tx.field.update({
        where: { id: fieldId },
        data: {
          cropType: dto.cropType,
          plantingDate: sowingDate,
          expectedHarvest: expectedHarvestDate,
          irrigationType: dto.irrigationType ?? undefined,
        },
      });

      // Outbox: crop_season.started (guaranteed delivery to all
      // downstream services via the outbox publisher worker).
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.crop_season.started",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "CropSeason",
        aggregateId: row.id,
        payload: {
          tenantId,
          fieldId,
          cropSeasonId: row.id,
          cropType: row.cropType,
          cropTypeAr: row.cropTypeAr,
          sowingDate: row.sowingDate.toISOString(),
          expectedHarvestDate: row.expectedHarvestDate?.toISOString() ?? null,
          seedVariety: row.seedVariety,
          irrigationType: row.irrigationType,
        },
      });

      return row;
    });

    return result;
  }

  /**
   * Tenant IDs in this service are VARCHAR(100) (free-form strings),
   * but the outbox table stores them as UUIDs to match the platform-
   * wide shared outbox schema. For non-UUID tenants we fall back to
   * the nil UUID — the downstream consumer still has the full string
   * inside `payload.tenantId`, so no information is lost.
   */
  private uuidOrNull(value: string): string {
    const uuidRe =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRe.test(value)
      ? value
      : "00000000-0000-0000-0000-000000000000";
  }

  /**
   * Patch an existing crop season (partial update).
   */
  async update(id: string, tenantId: string, dto: UpdateCropSeasonDto) {
    const existing = await this.getById(id, tenantId);

    // Guard against flipping isCurrent=true on a season that has already
    // been superseded. The DB partial-unique index would already reject
    // this, but we want a friendly Arabic error message first.
    if (dto.isCurrent === true) {
      const alreadyCurrent = await this.prisma.cropSeason.findFirst({
        where: {
          fieldId: existing.fieldId,
          isCurrent: true,
          NOT: { id: existing.id },
        },
      });
      if (alreadyCurrent) {
        throw new BadRequestException({
          message: "Another current season exists for this field",
          messageAr: "يوجد موسم حالي آخر لهذا الحقل — يجب إنهاؤه أولاً",
        });
      }
    }

    const data: Record<string, unknown> = {};
    if (dto.cropType !== undefined) data.cropType = dto.cropType;
    if (dto.cropTypeAr !== undefined) data.cropTypeAr = dto.cropTypeAr;
    if (dto.season !== undefined) data.season = dto.season;
    if (dto.sowingDate !== undefined)
      data.sowingDate = new Date(dto.sowingDate);
    if (dto.expectedHarvestDate !== undefined)
      data.expectedHarvestDate = new Date(dto.expectedHarvestDate);
    if (dto.actualHarvestDate !== undefined)
      data.actualHarvestDate = new Date(dto.actualHarvestDate);
    if (dto.seedVariety !== undefined) data.seedVariety = dto.seedVariety;
    if (dto.seedVarietyAr !== undefined) data.seedVarietyAr = dto.seedVarietyAr;
    if (dto.plantingDensityKgHa !== undefined)
      data.plantingDensityKgHa = dto.plantingDensityKgHa;
    if (dto.irrigationType !== undefined)
      data.irrigationType = dto.irrigationType;
    if (dto.yieldKgHa !== undefined) data.yieldKgHa = dto.yieldKgHa;
    if (dto.notes !== undefined) data.notes = dto.notes;
    if (dto.isCurrent !== undefined) data.isCurrent = dto.isCurrent;

    const updated = await this.prisma.$transaction(async (tx) => {
      const row = await tx.cropSeason.update({
        where: { id },
        data: data as any,
      });
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.crop_season.updated",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "CropSeason",
        aggregateId: id,
        payload: {
          tenantId,
          fieldId: existing.fieldId,
          cropSeasonId: id,
          changes: Object.keys(data),
        },
      });
      return row;
    });

    return updated;
  }

  /**
   * End an active crop season (isCurrent=false + endedAt stamp).
   */
  async end(id: string, tenantId: string, dto: EndCropSeasonDto) {
    const existing = await this.getById(id, tenantId);
    if (!existing.isCurrent) {
      throw new BadRequestException({
        message: "Season is already ended",
        messageAr: "الموسم منتهٍ بالفعل",
      });
    }

    const endedAt = dto.endedAt ? new Date(dto.endedAt) : new Date();
    const actualHarvestDate = dto.actualHarvestDate
      ? new Date(dto.actualHarvestDate)
      : null;

    const updated = await this.prisma.$transaction(async (tx) => {
      const row = await tx.cropSeason.update({
        where: { id },
        data: {
          isCurrent: false,
          endedAt,
          endReason: dto.endReason,
          actualHarvestDate: actualHarvestDate ?? undefined,
          yieldKgHa: dto.yieldKgHa as any,
        },
      });
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.crop_season.ended",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "CropSeason",
        aggregateId: id,
        payload: {
          tenantId,
          fieldId: existing.fieldId,
          cropSeasonId: id,
          endedAt: endedAt.toISOString(),
          endReason: dto.endReason ?? null,
          yieldKgHa: dto.yieldKgHa ?? null,
          actualHarvestDate: actualHarvestDate?.toISOString() ?? null,
        },
      });
      return row;
    });

    return updated;
  }

  /**
   * Soft-delete — sets deleted_at + deleted_by but keeps the row for
   * audit / SOX / IFRS compliance. Hard-delete is intentionally not
   * exposed; operators who need to scrub rows must do so via direct SQL
   * with a documented incident response procedure.
   */
  async remove(
    id: string,
    tenantId: string,
    deletedBy?: string,
    reason?: string,
  ) {
    const existing = await this.getById(id, tenantId);
    await this.prisma.$transaction(async (tx) => {
      await tx.cropSeason.update({
        where: { id },
        data: {
          deletedAt: new Date(),
          deletedBy: deletedBy ?? "system",
          deletedReason: reason ?? null,
          isCurrent: false,
        },
      });
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.crop_season.deleted",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "CropSeason",
        aggregateId: id,
        payload: {
          tenantId,
          fieldId: existing.fieldId,
          cropSeasonId: id,
          deletedBy: deletedBy ?? "system",
          reason: reason ?? null,
        },
      });
    });
    return { id };
  }

  /**
   * Tenant-guard helper: ensures the field exists and belongs to the tenant.
   */
  private async assertFieldOwnership(fieldId: string, tenantId: string) {
    const field = await this.prisma.field.findUnique({
      where: { id: fieldId },
      select: { id: true, tenantId: true, isDeleted: true },
    });
    if (!field || field.isDeleted) {
      throw new NotFoundException({
        message: "Field not found",
        messageAr: "الحقل غير موجود",
      });
    }
    if (field.tenantId !== tenantId) {
      throw new NotFoundException({
        message: "Field not found",
        messageAr: "الحقل غير موجود",
      });
    }
  }
}
