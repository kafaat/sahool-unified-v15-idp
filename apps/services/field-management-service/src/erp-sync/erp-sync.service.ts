/**
 * ERP Sync Service
 * خدمة تكامل ERP
 *
 * Orchestrates posting of field operations and crop seasons to one or
 * more external accounting systems via the registered IErpAdapter
 * implementations. Typical flow:
 *
 *   1. An operator (or automated rule) decides a FieldOperation is
 *      ready to be posted (approval_status = 'approved').
 *   2. `postFieldOperation(id)` is called.
 *   3. This service loads the source row, translates it to an
 *      ErpPostingDocument, and forwards it to every enabled adapter.
 *   4. On success, the source row's `posted_to_erp`, `posted_at`,
 *      `posting_reference`, `external_source` columns are updated.
 *   5. On failure, `posting_attempts` is incremented and
 *      `posting_error` records the last error. If the adapter reports
 *      the error as retryable, the caller (or a scheduled worker) can
 *      re-post later.
 *
 * The service is intentionally un-opinionated about WHICH adapters are
 * active — adapters are registered via constructor injection and the
 * admin can enable/disable them via env vars.
 */

import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { WebhookErpAdapter } from "./webhook-erp.adapter";
import type {
  IErpAdapter,
  ErpPostingDocument,
  ErpPostingResult,
} from "./erp-sync.types";

@Injectable()
export class ErpSyncService {
  private readonly logger = new Logger(ErpSyncService.name);
  private readonly adapters: IErpAdapter[];

  constructor(
    private readonly prisma: PrismaService,
    private readonly webhook: WebhookErpAdapter,
  ) {
    // Register all adapters here. New adapters (QuickBooks, SAP, Odoo,
    // …) should be added to this list once implemented.
    this.adapters = [webhook];
  }

  /**
   * Post a single FieldOperation to every enabled ERP adapter.
   * Returns a map of { sourceName → result } so the caller can see
   * which adapters succeeded.
   */
  async postFieldOperation(
    operationId: string,
    tenantId: string,
  ): Promise<{ [source: string]: ErpPostingResult }> {
    const row = await this.prisma.fieldOperation.findUnique({
      where: { id: operationId },
      include: {
        field: { select: { name: true } },
        cropSeason: { select: { cropType: true, cropTypeAr: true } },
      },
    });
    if (!row || row.tenantId !== tenantId || row.deletedAt) {
      throw new NotFoundException({
        message: "Field operation not found",
        messageAr: "عملية الحقل غير موجودة",
      });
    }
    if (row.approvalStatus !== "approved") {
      throw new BadRequestException({
        message: "Only approved operations can be posted to ERP",
        messageAr: "لا يمكن ترحيل عملية غير معتمدة إلى نظام المحاسبة",
      });
    }

    const doc = this.buildPostingDocument(row);
    const results: Record<string, ErpPostingResult> = {};
    const enabledAdapters = this.adapters.filter((a) => a.isEnabled());
    if (enabledAdapters.length === 0) {
      throw new BadRequestException({
        message: "No ERP adapter is configured",
        messageAr: "لا يوجد موفر ERP مفعّل حالياً",
      });
    }

    for (const adapter of enabledAdapters) {
      try {
        results[adapter.sourceName] = await adapter.postDocument(doc);
      } catch (e) {
        results[adapter.sourceName] = {
          success: false,
          error: e instanceof Error ? e.message : String(e),
          retryable: true,
        };
      }
    }

    // Pick the first successful result to stamp on the source row.
    // If multiple adapters succeeded we keep them all in posting
    // metadata (via posting_reference JSON) but only flip the
    // canonical flag once.
    const firstSuccess = Object.entries(results).find(
      ([, r]) => r.success,
    ) as [string, ErpPostingResult] | undefined;
    const anyError = Object.values(results).find((r) => !r.success);

    await this.prisma.fieldOperation.update({
      where: { id: operationId },
      data: {
        postedToErp: !!firstSuccess,
        postedAt: firstSuccess ? new Date() : undefined,
        postingReference: firstSuccess
          ? JSON.stringify({
              source: firstSuccess[0],
              externalRef: firstSuccess[1].externalRef,
              allResults: results,
            })
          : undefined,
        externalSource: firstSuccess ? firstSuccess[0] : undefined,
        externalId: firstSuccess?.[1].externalRef ?? undefined,
        postingError: anyError?.error ?? null,
        postingAttempts: { increment: 1 },
      },
    });

    return results;
  }

  /**
   * Build an ErpPostingDocument from a raw FieldOperation row. All the
   * cost breakdown columns become individual line items so the ERP's
   * chart of accounts can slice spend across fuel / labour / materials /
   * overhead / tax.
   */
  private buildPostingDocument(
    row: {
      id: string;
      tenantId: string;
      fieldId: string;
      cropSeasonId: string | null;
      operationType: string;
      performedAt: Date;
      costAmount: unknown;
      costCurrency: string;
      fuelCost: unknown;
      laborCost: unknown;
      materialsCost: unknown;
      overheadCost: unknown;
      otherCost: unknown;
      taxAmount: unknown;
      taxRate: unknown;
      exchangeRate: unknown;
      baseCurrency: string | null;
      invoiceNumber: string | null;
      invoiceDate: Date | null;
      vendorId: string | null;
      vendorName: string | null;
      glAccount: string | null;
      costCenter: string | null;
      projectCode: string | null;
      notes: string | null;
      field: { name: string };
      cropSeason: { cropType: string; cropTypeAr: string | null } | null;
    },
  ): ErpPostingDocument {
    const num = (v: unknown): number | undefined =>
      v === null || v === undefined
        ? undefined
        : Number(v as number | string);

    const total = num(row.costAmount) ?? 0;
    const lines: ErpPostingDocument["lines"] = [];
    const add = (
      description: string,
      descriptionAr: string,
      amount: number | undefined,
    ) => {
      if (!amount || amount <= 0) return;
      lines.push({
        description,
        descriptionAr,
        amount,
        glAccount: row.glAccount ?? undefined,
        costCenter: row.costCenter ?? undefined,
      });
    };

    add("Fuel cost", "تكلفة الوقود", num(row.fuelCost));
    add("Labour cost", "تكلفة العمالة", num(row.laborCost));
    add("Materials cost", "تكلفة المواد", num(row.materialsCost));
    add("Overhead cost", "تكلفة مصاريف عامة", num(row.overheadCost));
    add("Other cost", "تكاليف أخرى", num(row.otherCost));

    // If no breakdown was captured, fall back to a single
    // "Operation cost" line — we still want a valid document.
    if (lines.length === 0 && total > 0) {
      const opLabel = this.operationLabel(row.operationType);
      lines.push({
        description: `${opLabel.en} — ${row.field.name}`,
        descriptionAr: `${opLabel.ar} — ${row.field.name}`,
        amount: total,
        glAccount: row.glAccount ?? undefined,
        costCenter: row.costCenter ?? undefined,
      });
    }

    return {
      documentId: row.id,
      tenantId: row.tenantId,
      vendorId: row.vendorId ?? undefined,
      vendorName: row.vendorName ?? undefined,
      invoiceNumber: row.invoiceNumber ?? undefined,
      invoiceDate: row.invoiceDate?.toISOString() ?? undefined,
      costCenter: row.costCenter ?? undefined,
      projectCode: row.projectCode ?? undefined,
      glAccount: row.glAccount ?? undefined,
      currency: row.costCurrency,
      exchangeRate: num(row.exchangeRate),
      baseCurrency: row.baseCurrency ?? undefined,
      lines,
      taxAmount: num(row.taxAmount),
      taxRate: num(row.taxRate),
      totalAmount: total + (num(row.taxAmount) ?? 0),
      memo: row.notes ?? undefined,
      aggregateType: "FieldOperation",
      aggregateId: row.id,
      occurredAt: row.performedAt.toISOString(),
    };
  }

  private operationLabel(
    slug: string,
  ): { en: string; ar: string } {
    const map: Record<string, { en: string; ar: string }> = {
      plowing: { en: "Plowing", ar: "الحراثة" },
      land_preparation: { en: "Land preparation", ar: "تهيئة الأرض" },
      fertilization: { en: "Fertilization", ar: "التسميد" },
      spraying: { en: "Spraying", ar: "الرش" },
      irrigation: { en: "Irrigation", ar: "الري" },
      harvesting: { en: "Harvesting", ar: "الحصاد" },
      scouting: { en: "Scouting", ar: "الاستكشاف" },
      sowing: { en: "Sowing", ar: "البذار" },
      other: { en: "Other", ar: "أخرى" },
    };
    return map[slug] ?? { en: slug, ar: slug };
  }

  /**
   * Health check — returns the subset of adapters that are currently
   * enabled and reachable. Surfaced at /api/v1/erp-sync/health.
   */
  async health(): Promise<{
    adapters: Array<{ name: string; enabled: boolean; reachable: boolean }>;
  }> {
    const out: Array<{ name: string; enabled: boolean; reachable: boolean }> = [];
    for (const a of this.adapters) {
      const enabled = a.isEnabled();
      let reachable = false;
      if (enabled && a.ping) {
        try {
          reachable = await a.ping();
        } catch {
          reachable = false;
        }
      }
      out.push({ name: a.sourceName, enabled, reachable });
    }
    return { adapters: out };
  }
}
