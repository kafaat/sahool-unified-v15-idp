/**
 * Field Operations Service
 * خدمة عمليات الحقل
 *
 * Per-field operation log (plowing, land preparation, fertilization,
 * spraying, irrigation, harvesting, ...). Each row optionally links to:
 *
 *   - CropSeason: so operations roll up into a per-season cost + hours
 *     total, which the yield-prediction and advisory services consume.
 *   - Equipment (from equipment-service): soft cross-service link via UUID.
 *     We cache the display name so the timeline keeps working when
 *     equipment-service is temporarily offline.
 */

import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { FieldEventsService } from "../events/field-events.service";
import type {
  CreateFieldOperationDto,
  UpdateFieldOperationDto,
  QueryFieldOperationsDto,
} from "./dto/field-operation.dto";

@Injectable()
export class FieldOperationsService {
  private readonly logger = new Logger(FieldOperationsService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly events: FieldEventsService,
  ) {}

  /**
   * List operations scoped to the authenticated tenant. Supports filtering
   * by field, crop season, operation type, equipment, and date range.
   * Returns rows ordered newest-first by performedAt.
   */
  async list(tenantId: string, q: QueryFieldOperationsDto) {
    if (q.fieldId) {
      await this.assertFieldOwnership(q.fieldId, tenantId);
    }
    const where: Record<string, unknown> = { tenantId };
    if (q.fieldId) where.fieldId = q.fieldId;
    if (q.cropSeasonId) where.cropSeasonId = q.cropSeasonId;
    if (q.operationType) where.operationType = q.operationType;
    if (q.equipmentId) where.equipmentId = q.equipmentId;
    if (q.fromDate || q.toDate) {
      const range: { gte?: Date; lte?: Date } = {};
      if (q.fromDate) range.gte = new Date(q.fromDate);
      if (q.toDate) range.lte = new Date(q.toDate);
      where.performedAt = range;
    }

    const take = Math.min(q.limit ?? 50, 200);
    const skip = q.offset ?? 0;

    const [items, total] = await Promise.all([
      this.prisma.fieldOperation.findMany({
        where: where as any,
        orderBy: [{ performedAt: "desc" }, { createdAt: "desc" }],
        take,
        skip,
      }),
      this.prisma.fieldOperation.count({ where: where as any }),
    ]);

    return { items, total, limit: take, offset: skip };
  }

  /**
   * Compute per-season rollups (hours + cost) for a given crop season.
   * Feeds the "الإجمالي قبل البذار" / "total season cost" widgets on
   * the web timeline and the yield-prediction service's feature set.
   */
  async rollupForCropSeason(cropSeasonId: string, tenantId: string) {
    const season = await this.prisma.cropSeason.findUnique({
      where: { id: cropSeasonId },
      select: { id: true, tenantId: true },
    });
    if (!season || season.tenantId !== tenantId) {
      throw new NotFoundException({
        message: "Crop season not found",
        messageAr: "الموسم المحصولي غير موجود",
      });
    }

    const rows = await this.prisma.fieldOperation.findMany({
      where: { cropSeasonId, tenantId },
      select: {
        operationType: true,
        durationHours: true,
        costAmount: true,
        costCurrency: true,
      },
    });

    const byType: Record<
      string,
      { count: number; hours: number; cost: number }
    > = {};
    let totalHours = 0;
    let totalCost = 0;
    for (const r of rows) {
      const hrs = Number(r.durationHours ?? 0);
      const cost = Number(r.costAmount ?? 0);
      totalHours += Number.isFinite(hrs) ? hrs : 0;
      totalCost += Number.isFinite(cost) ? cost : 0;
      const bucket = (byType[r.operationType] ||= {
        count: 0,
        hours: 0,
        cost: 0,
      });
      bucket.count += 1;
      bucket.hours += Number.isFinite(hrs) ? hrs : 0;
      bucket.cost += Number.isFinite(cost) ? cost : 0;
    }

    return {
      cropSeasonId,
      totalOperations: rows.length,
      totalHours,
      totalCost,
      currency: rows[0]?.costCurrency ?? "SAR",
      byType,
    };
  }

  /**
   * Fetch a single operation by id (tenant-scoped).
   */
  async getById(id: string, tenantId: string) {
    const row = await this.prisma.fieldOperation.findUnique({ where: { id } });
    if (!row || row.tenantId !== tenantId) {
      throw new NotFoundException({
        message: "Field operation not found",
        messageAr: "عملية الحقل غير موجودة",
      });
    }
    return row;
  }

  /**
   * Record a new field operation. Validates:
   *   - field ownership
   *   - crop-season ownership (if cropSeasonId is set)
   *   - performedAt is a real date
   *   - endedAt (if set) is after performedAt
   */
  async create(
    fieldId: string,
    tenantId: string,
    dto: CreateFieldOperationDto,
    createdBy?: string,
  ) {
    await this.assertFieldOwnership(fieldId, tenantId);

    if (dto.cropSeasonId) {
      const season = await this.prisma.cropSeason.findUnique({
        where: { id: dto.cropSeasonId },
        select: { id: true, tenantId: true, fieldId: true },
      });
      if (
        !season ||
        season.tenantId !== tenantId ||
        season.fieldId !== fieldId
      ) {
        throw new NotFoundException({
          message: "Crop season not found on this field",
          messageAr: "الموسم المحصولي غير موجود لهذا الحقل",
        });
      }
    }

    const performedAt = new Date(dto.performedAt);
    if (Number.isNaN(performedAt.getTime())) {
      throw new BadRequestException({
        message: "Invalid performed-at date",
        messageAr: "تاريخ التنفيذ غير صالح",
      });
    }
    const endedAt = dto.endedAt ? new Date(dto.endedAt) : null;
    if (endedAt && endedAt.getTime() < performedAt.getTime()) {
      throw new BadRequestException({
        message: "End date must be after start date",
        messageAr: "تاريخ الانتهاء يجب أن يكون بعد تاريخ التنفيذ",
      });
    }

    const row = await this.prisma.fieldOperation.create({
      data: {
        tenantId,
        fieldId,
        cropSeasonId: dto.cropSeasonId,
        operationType: dto.operationType,
        performedAt,
        endedAt: endedAt ?? undefined,
        durationHours: dto.durationHours as any,
        costAmount: dto.costAmount as any,
        costCurrency: dto.costCurrency || "SAR",
        equipmentId: dto.equipmentId,
        equipmentName: dto.equipmentName,
        equipmentNameAr: dto.equipmentNameAr,
        notes: dto.notes,
        createdBy,
      },
    });

    await this.events.publishFieldOperationRecorded(tenantId, fieldId, {
      operationId: row.id,
      operationType: row.operationType,
      performedAt: row.performedAt.toISOString(),
      durationHours: row.durationHours ? Number(row.durationHours) : null,
      costAmount: row.costAmount ? Number(row.costAmount) : null,
      costCurrency: row.costCurrency,
      equipmentId: row.equipmentId ?? null,
      cropSeasonId: row.cropSeasonId ?? null,
    });

    return row;
  }

  /**
   * Partial update.
   */
  async update(id: string, tenantId: string, dto: UpdateFieldOperationDto) {
    const existing = await this.getById(id, tenantId);

    const data: Record<string, unknown> = {};
    if (dto.operationType !== undefined) data.operationType = dto.operationType;
    if (dto.performedAt !== undefined)
      data.performedAt = new Date(dto.performedAt);
    if (dto.endedAt !== undefined) data.endedAt = new Date(dto.endedAt);
    if (dto.durationHours !== undefined) data.durationHours = dto.durationHours;
    if (dto.costAmount !== undefined) data.costAmount = dto.costAmount;
    if (dto.costCurrency !== undefined) data.costCurrency = dto.costCurrency;
    if (dto.equipmentId !== undefined) data.equipmentId = dto.equipmentId;
    if (dto.equipmentName !== undefined) data.equipmentName = dto.equipmentName;
    if (dto.equipmentNameAr !== undefined)
      data.equipmentNameAr = dto.equipmentNameAr;
    if (dto.notes !== undefined) data.notes = dto.notes;

    const updated = await this.prisma.fieldOperation.update({
      where: { id },
      data: data as any,
    });

    await this.events.publishFieldOperationUpdated(tenantId, existing.fieldId, {
      operationId: updated.id,
      changes: Object.keys(data),
    });

    return updated;
  }

  /**
   * Hard delete.
   */
  async remove(id: string, tenantId: string) {
    const existing = await this.getById(id, tenantId);
    await this.prisma.fieldOperation.delete({ where: { id } });
    await this.events.publishFieldOperationDeleted(tenantId, existing.fieldId, {
      operationId: existing.id,
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
