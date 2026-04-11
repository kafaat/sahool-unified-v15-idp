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
import { OutboxService } from "../outbox/outbox.service";
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
    private readonly outbox: OutboxService,
  ) {}

  private uuidOrNull(value: string): string {
    const uuidRe =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRe.test(value)
      ? value
      : "00000000-0000-0000-0000-000000000000";
  }

  /**
   * List operations scoped to the authenticated tenant. Supports filtering
   * by field, crop season, operation type, equipment, and date range.
   * Returns rows ordered newest-first by performedAt.
   */
  async list(tenantId: string, q: QueryFieldOperationsDto) {
    if (q.fieldId) {
      await this.assertFieldOwnership(q.fieldId, tenantId);
    }
    const where: Record<string, unknown> = { tenantId, deletedAt: null };
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
      where: { cropSeasonId, tenantId, deletedAt: null },
      select: {
        operationType: true,
        durationHours: true,
        costAmount: true,
        costCurrency: true,
        fuelCost: true,
        laborCost: true,
        materialsCost: true,
        overheadCost: true,
        otherCost: true,
        taxAmount: true,
      },
    });

    const byType: Record<
      string,
      {
        count: number;
        hours: number;
        cost: number;
        fuelCost: number;
        laborCost: number;
        materialsCost: number;
        overheadCost: number;
      }
    > = {};
    let totalHours = 0;
    let totalCost = 0;
    let totalFuel = 0;
    let totalLabor = 0;
    let totalMaterials = 0;
    let totalOverhead = 0;
    let totalTax = 0;

    for (const r of rows) {
      const hrs = Number(r.durationHours ?? 0);
      const cost = Number(r.costAmount ?? 0);
      const fuel = Number(r.fuelCost ?? 0);
      const labor = Number(r.laborCost ?? 0);
      const materials = Number(r.materialsCost ?? 0);
      const overhead = Number(r.overheadCost ?? 0);
      const tax = Number(r.taxAmount ?? 0);

      totalHours += Number.isFinite(hrs) ? hrs : 0;
      totalCost += Number.isFinite(cost) ? cost : 0;
      totalFuel += Number.isFinite(fuel) ? fuel : 0;
      totalLabor += Number.isFinite(labor) ? labor : 0;
      totalMaterials += Number.isFinite(materials) ? materials : 0;
      totalOverhead += Number.isFinite(overhead) ? overhead : 0;
      totalTax += Number.isFinite(tax) ? tax : 0;

      const bucket = (byType[r.operationType] ||= {
        count: 0,
        hours: 0,
        cost: 0,
        fuelCost: 0,
        laborCost: 0,
        materialsCost: 0,
        overheadCost: 0,
      });
      bucket.count += 1;
      bucket.hours += Number.isFinite(hrs) ? hrs : 0;
      bucket.cost += Number.isFinite(cost) ? cost : 0;
      bucket.fuelCost += Number.isFinite(fuel) ? fuel : 0;
      bucket.laborCost += Number.isFinite(labor) ? labor : 0;
      bucket.materialsCost += Number.isFinite(materials) ? materials : 0;
      bucket.overheadCost += Number.isFinite(overhead) ? overhead : 0;
    }

    // Update the materialised cache on the parent CropSeason row so
    // dashboards can list 100 seasons without re-computing rollups.
    await this.prisma.cropSeason.updateMany({
      where: { id: cropSeasonId, tenantId, deletedAt: null },
      data: {
        totalSeasonCost: totalCost as any,
        totalSeasonHours: totalHours as any,
        totalsUpdatedAt: new Date(),
      },
    });

    return {
      cropSeasonId,
      totalOperations: rows.length,
      totalHours,
      totalCost,
      costBreakdown: {
        fuel: totalFuel,
        labor: totalLabor,
        materials: totalMaterials,
        overhead: totalOverhead,
        tax: totalTax,
      },
      currency: rows[0]?.costCurrency ?? "SAR",
      byType,
    };
  }

  /**
   * Fetch a single operation by id (tenant-scoped).
   */
  async getById(id: string, tenantId: string) {
    const row = await this.prisma.fieldOperation.findUnique({ where: { id } });
    if (!row || row.tenantId !== tenantId || row.deletedAt) {
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

    // Derive total cost from the breakdown if the caller didn't supply
    // an explicit `costAmount`. This guarantees dashboards always have
    // a populated total even when the modal only captures per-component
    // costs (fuel + labor + materials + overhead + other).
    const computedTotal =
      (dto.costAmount ??
        (dto.fuelCost ?? 0) +
          (dto.laborCost ?? 0) +
          (dto.materialsCost ?? 0) +
          (dto.overheadCost ?? 0) +
          (dto.otherCost ?? 0)) || undefined;

    const row = await this.prisma.$transaction(async (tx) => {
      const created = await tx.fieldOperation.create({
        data: {
          tenantId,
          fieldId,
          cropSeasonId: dto.cropSeasonId,
          operationType: dto.operationType,
          performedAt,
          endedAt: endedAt ?? undefined,
          durationHours: dto.durationHours as any,
          costAmount: computedTotal as any,
          costCurrency: dto.costCurrency || "SAR",
          // Cost breakdown
          fuelLiters: dto.fuelLiters as any,
          fuelCost: dto.fuelCost as any,
          laborHours: dto.laborHours as any,
          laborCost: dto.laborCost as any,
          materialsCost: dto.materialsCost as any,
          overheadCost: dto.overheadCost as any,
          otherCost: dto.otherCost as any,
          // Tax + currency
          taxAmount: dto.taxAmount as any,
          taxRate: dto.taxRate as any,
          exchangeRate: dto.exchangeRate as any,
          baseCurrency: dto.baseCurrency,
          // Vendor / invoice
          invoiceNumber: dto.invoiceNumber,
          invoiceDate: dto.invoiceDate ? new Date(dto.invoiceDate) : undefined,
          vendorId: dto.vendorId,
          vendorName: dto.vendorName,
          receiptUrl: dto.receiptUrl,
          // GL / cost-center / project
          glAccount: dto.glAccount,
          costCenter: dto.costCenter,
          projectCode: dto.projectCode,
          // Equipment link
          equipmentId: dto.equipmentId,
          equipmentName: dto.equipmentName,
          equipmentNameAr: dto.equipmentNameAr,
          notes: dto.notes,
          createdBy,
          // Approval: by default `approved` so the existing flow keeps
          // working; admins can configure operation-level approval
          // workflow via env (not in this PR).
          approvalStatus: "approved",
          approvedBy: createdBy,
          approvedAt: new Date(),
        },
      });

      // Outbox write — guaranteed delivery to NDVI pipeline, yield-
      // prediction, advisory-service, ERP webhooks.
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.operation.recorded",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "FieldOperation",
        aggregateId: created.id,
        payload: {
          tenantId,
          fieldId,
          operationId: created.id,
          operationType: created.operationType,
          performedAt: created.performedAt.toISOString(),
          durationHours: created.durationHours
            ? Number(created.durationHours)
            : null,
          costAmount: created.costAmount ? Number(created.costAmount) : null,
          costCurrency: created.costCurrency,
          costBreakdown: {
            fuel: Number(created.fuelCost ?? 0),
            labor: Number(created.laborCost ?? 0),
            materials: Number(created.materialsCost ?? 0),
            overhead: Number(created.overheadCost ?? 0),
            other: Number(created.otherCost ?? 0),
            tax: Number(created.taxAmount ?? 0),
          },
          equipmentId: created.equipmentId ?? null,
          cropSeasonId: created.cropSeasonId ?? null,
          vendorId: created.vendorId ?? null,
          glAccount: created.glAccount ?? null,
        },
      });

      return created;
    });

    return row;
  }

  /**
   * Approve a pending field operation. Only approved operations can be
   * posted to ERP systems (enforced by ErpSyncService).
   */
  async approve(
    id: string,
    tenantId: string,
    approvedBy?: string,
  ) {
    const existing = await this.getById(id, tenantId);
    if (existing.approvalStatus === "approved") return existing;
    if (existing.approvalStatus === "rejected") {
      throw new BadRequestException({
        message: "Operation has been rejected and cannot be approved",
        messageAr: "العملية مرفوضة ولا يمكن اعتمادها",
      });
    }
    return this.prisma.$transaction(async (tx) => {
      const row = await tx.fieldOperation.update({
        where: { id },
        data: {
          approvalStatus: "approved",
          approvedBy: approvedBy ?? "system",
          approvedAt: new Date(),
        },
      });
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.operation.approved",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "FieldOperation",
        aggregateId: id,
        payload: {
          tenantId,
          fieldId: existing.fieldId,
          operationId: id,
          approvedBy: approvedBy ?? "system",
        },
      });
      return row;
    });
  }

  /**
   * Reject a pending field operation. Rejected operations can no longer
   * be approved — they must be deleted and re-recorded.
   */
  async reject(
    id: string,
    tenantId: string,
    reason: string,
    rejectedBy?: string,
  ) {
    const existing = await this.getById(id, tenantId);
    if (existing.approvalStatus === "rejected") return existing;
    return this.prisma.$transaction(async (tx) => {
      const row = await tx.fieldOperation.update({
        where: { id },
        data: {
          approvalStatus: "rejected",
          rejectionReason: reason,
          approvedBy: rejectedBy ?? "system",
          approvedAt: new Date(),
        },
      });
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.operation.rejected",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "FieldOperation",
        aggregateId: id,
        payload: {
          tenantId,
          fieldId: existing.fieldId,
          operationId: id,
          reason,
          rejectedBy: rejectedBy ?? "system",
        },
      });
      return row;
    });
  }

  /**
   * Partial update.
   */
  async update(id: string, tenantId: string, dto: UpdateFieldOperationDto) {
    const existing = await this.getById(id, tenantId);

    // Once an operation has been posted to an ERP system, its
    // accounting fields become immutable — otherwise the posted
    // journal entry wouldn't match the source row anymore. Admins who
    // need to correct a posted row must first reverse the posting.
    if (existing.postedToErp) {
      throw new BadRequestException({
        message:
          "Operation has been posted to ERP and is locked — reverse the posting first",
        messageAr:
          "العملية مرحلة إلى نظام المحاسبة ومقفلة — يجب إلغاء الترحيل أولاً",
      });
    }

    const data: Record<string, unknown> = {};
    const set = <K extends keyof UpdateFieldOperationDto>(
      key: K,
      transform?: (v: NonNullable<UpdateFieldOperationDto[K]>) => unknown,
    ) => {
      const v = dto[key];
      if (v === undefined) return;
      (data as Record<string, unknown>)[key] = transform
        ? transform(v as NonNullable<UpdateFieldOperationDto[K]>)
        : (v as unknown);
    };

    set("operationType");
    set("performedAt", (v) => new Date(v as string));
    set("endedAt", (v) => new Date(v as string));
    set("durationHours");
    set("costAmount");
    set("costCurrency");
    set("equipmentId");
    set("equipmentName");
    set("equipmentNameAr");
    set("notes");
    // Accounting fields
    set("fuelLiters");
    set("fuelCost");
    set("laborHours");
    set("laborCost");
    set("materialsCost");
    set("overheadCost");
    set("otherCost");
    set("taxAmount");
    set("taxRate");
    set("exchangeRate");
    set("baseCurrency");
    set("invoiceNumber");
    set("invoiceDate", (v) => new Date(v as string));
    set("vendorId");
    set("vendorName");
    set("receiptUrl");
    set("glAccount");
    set("costCenter");
    set("projectCode");

    const updated = await this.prisma.$transaction(async (tx) => {
      const row = await tx.fieldOperation.update({
        where: { id },
        data: data as any,
      });
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.operation.updated",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "FieldOperation",
        aggregateId: id,
        payload: {
          tenantId,
          fieldId: existing.fieldId,
          operationId: id,
          changes: Object.keys(data),
        },
      });
      return row;
    });

    return updated;
  }

  /**
   * Soft delete — preserves the row for SOX/IFRS audit compliance.
   * Posted rows cannot be deleted (must reverse posting first).
   */
  async remove(
    id: string,
    tenantId: string,
    deletedBy?: string,
    reason?: string,
  ) {
    const existing = await this.getById(id, tenantId);
    if (existing.postedToErp) {
      throw new BadRequestException({
        message:
          "Operation has been posted to ERP and cannot be deleted — reverse the posting first",
        messageAr:
          "العملية مرحلة إلى نظام المحاسبة ولا يمكن حذفها — يجب إلغاء الترحيل أولاً",
      });
    }
    await this.prisma.$transaction(async (tx) => {
      await tx.fieldOperation.update({
        where: { id },
        data: {
          deletedAt: new Date(),
          deletedBy: deletedBy ?? "system",
          deletedReason: reason ?? null,
        },
      });
      await this.outbox.writeInTransaction(tx, {
        eventType: "sahool.field.operation.deleted",
        tenantId: this.uuidOrNull(tenantId),
        aggregateType: "FieldOperation",
        aggregateId: id,
        payload: {
          tenantId,
          fieldId: existing.fieldId,
          operationId: id,
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
