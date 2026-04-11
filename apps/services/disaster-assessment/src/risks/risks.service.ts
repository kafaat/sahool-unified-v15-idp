// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Risks Service - خدمة مخاطر الكوارث
// ═══════════════════════════════════════════════════════════════════════════════
//
// Aggregates risk information from multiple sources into a unified "risk record"
// view expected by the frontend. Records are derived from:
//
//   1. Active disaster reports (treated as current high-probability risks)
//   2. Field damage assessments (per-field historical risk with scores)
//
// This avoids duplicating storage - the underlying risks live in the same
// `disaster_reports` and `field_assessments` tables used by the existing
// `/disasters/risk/flood` and `/disasters/risk/drought` endpoints.
// ═══════════════════════════════════════════════════════════════════════════════

import { Injectable, Logger, NotFoundException } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { ListRisksQueryDto } from "./risks.dto";

type RiskRecord = {
  id: string;
  source: "disaster_report" | "field_assessment";
  riskType: string;
  governorate: string | null;
  fieldId: string | null;
  riskScore: number;
  probability: number;
  severity: string;
  status: string;
  mitigationPlan: string[];
  mitigationPlanAr: string[];
  computedAt: string;
};

const SEVERITY_SCORES: Record<string, number> = {
  low: 2.5,
  medium: 5.0,
  high: 7.5,
  critical: 10.0,
};

const SEVERITY_PROBABILITIES: Record<string, number> = {
  low: 0.2,
  medium: 0.45,
  high: 0.7,
  critical: 0.9,
};

@Injectable()
export class RisksService {
  private readonly logger = new Logger(RisksService.name);

  constructor(private readonly prisma: PrismaService) {}

  // ─────────────────────────────────────────────────────────────────────────
  // Scoring helpers
  // ─────────────────────────────────────────────────────────────────────────

  private scoreFromSeverity(severity: string): number {
    return SEVERITY_SCORES[severity] ?? 5.0;
  }

  private probabilityFromSeverity(severity: string): number {
    return SEVERITY_PROBABILITIES[severity] ?? 0.5;
  }

  private scoreFromDamage(damagePct: number): number {
    // 0..100% → 0..10
    return Math.round((damagePct / 10) * 100) / 100;
  }

  private mitigationFor(type: string): { en: string[]; ar: string[] } {
    const plans: Record<string, { en: string[]; ar: string[] }> = {
      flood: {
        en: [
          "Improve drainage infrastructure",
          "Install early warning systems",
          "Use flood-resistant varieties",
        ],
        ar: [
          "تحسين البنية التحتية للصرف",
          "تركيب أنظمة إنذار مبكر",
          "استخدام أصناف مقاومة للفيضانات",
        ],
      },
      drought: {
        en: [
          "Install drip irrigation",
          "Apply mulching",
          "Use drought-resistant varieties",
        ],
        ar: [
          "تركيب الري بالتنقيط",
          "تطبيق التغطية",
          "استخدام أصناف مقاومة للجفاف",
        ],
      },
      locust: {
        en: [
          "Monitor swarms via satellite",
          "Maintain approved insecticide stock",
          "Coordinate area-wide treatment",
        ],
        ar: [
          "مراقبة الأسراب عبر الأقمار الصناعية",
          "الاحتفاظ بمخزون مبيدات معتمدة",
          "تنسيق المعالجة الشاملة",
        ],
      },
    };
    return (
      plans[type] || {
        en: [
          "Document risk factors",
          "Contact agricultural extension services",
        ],
        ar: [
          "توثيق عوامل الخطر",
          "التواصل مع خدمات الإرشاد الزراعي",
        ],
      }
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // List risk records (aggregated)
  // ─────────────────────────────────────────────────────────────────────────

  async listRisks(tenantId: string, query: ListRisksQueryDto) {
    const limit = query.limit ?? 50;
    const offset = query.offset ?? 0;

    // 1) Active disaster reports → one risk record per report
    const reportWhere: Record<string, unknown> = {
      tenantId,
      status: { in: ["active", "monitoring", "verified", "reported"] },
    };
    if (query.type) reportWhere.type = query.type;
    if (query.governorate) reportWhere.governorate = query.governorate;

    const reports = await this.prisma.disasterReport.findMany({
      where: reportWhere,
      orderBy: { updatedAt: "desc" },
      take: 1000,
    });

    const reportRecords: RiskRecord[] = (reports as unknown as Array<{
      id: string;
      type: string;
      severity: string;
      status: string;
      governorate: string;
      updatedAt: Date;
    }>).map((r) => {
      const plan = this.mitigationFor(r.type);
      return {
        id: `dr-${r.id}`,
        source: "disaster_report",
        riskType: r.type,
        governorate: r.governorate,
        fieldId: null,
        riskScore: this.scoreFromSeverity(r.severity),
        probability: this.probabilityFromSeverity(r.severity),
        severity: r.severity,
        status: r.status,
        mitigationPlan: plan.en,
        mitigationPlanAr: plan.ar,
        computedAt: r.updatedAt.toISOString(),
      };
    });

    // 2) Field assessments → per-field historical risk
    const fieldWhere: Record<string, unknown> = { tenantId };
    if (query.fieldId) fieldWhere.fieldId = query.fieldId;

    const assessments = await this.prisma.fieldAssessment.findMany({
      where: fieldWhere,
      include: { disaster: true },
      orderBy: { assessedAt: "desc" },
      take: 1000,
    });

    const assessmentRecords: RiskRecord[] = (assessments as unknown as Array<{
      id: string;
      fieldId: string;
      damagePercentage: number;
      assessedAt: Date;
      disaster: { type: string; severity: string; governorate: string } | null;
    }>)
      .filter((a) => !query.type || a.disaster?.type === query.type)
      .filter(
        (a) =>
          !query.governorate || a.disaster?.governorate === query.governorate,
      )
      .map((a) => {
        const type = a.disaster?.type ?? "unknown";
        const plan = this.mitigationFor(type);
        return {
          id: `fa-${a.id}`,
          source: "field_assessment",
          riskType: type,
          governorate: a.disaster?.governorate ?? null,
          fieldId: a.fieldId,
          riskScore: this.scoreFromDamage(a.damagePercentage),
          probability: a.disaster
            ? this.probabilityFromSeverity(a.disaster.severity)
            : 0.5,
          severity: a.disaster?.severity ?? "medium",
          status: "historical",
          mitigationPlan: plan.en,
          mitigationPlanAr: plan.ar,
          computedAt: a.assessedAt.toISOString(),
        };
      });

    const all = [...reportRecords, ...assessmentRecords].sort(
      (a, b) => b.riskScore - a.riskScore,
    );
    const paginated = all.slice(offset, offset + limit);

    return {
      total: all.length,
      limit,
      offset,
      risks: paginated,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Get single risk record by ID
  // ─────────────────────────────────────────────────────────────────────────

  async getRisk(id: string, tenantId: string) {
    // IDs are prefixed: dr-<uuid> or fa-<uuid>
    const [prefix, rawId] = id.split("-", 2);
    const remainder = id.slice(prefix.length + 1);

    if (prefix === "dr") {
      const row = await this.prisma.disasterReport.findFirst({
        where: { id: remainder, tenantId },
      });
      if (!row) {
        throw new NotFoundException({
          error: "Risk not found",
          errorAr: "المخاطرة غير موجودة",
        });
      }
      const r = row as unknown as {
        id: string;
        type: string;
        severity: string;
        status: string;
        governorate: string;
        updatedAt: Date;
      };
      const plan = this.mitigationFor(r.type);
      return {
        id: `dr-${r.id}`,
        source: "disaster_report",
        riskType: r.type,
        governorate: r.governorate,
        fieldId: null,
        riskScore: this.scoreFromSeverity(r.severity),
        probability: this.probabilityFromSeverity(r.severity),
        severity: r.severity,
        status: r.status,
        mitigationPlan: plan.en,
        mitigationPlanAr: plan.ar,
        computedAt: r.updatedAt.toISOString(),
      };
    }

    if (prefix === "fa") {
      const row = await this.prisma.fieldAssessment.findFirst({
        where: { id: remainder, tenantId },
        include: { disaster: true },
      });
      if (!row) {
        throw new NotFoundException({
          error: "Risk not found",
          errorAr: "المخاطرة غير موجودة",
        });
      }
      const a = row as unknown as {
        id: string;
        fieldId: string;
        damagePercentage: number;
        assessedAt: Date;
        disaster: {
          type: string;
          severity: string;
          governorate: string;
        } | null;
      };
      const type = a.disaster?.type ?? "unknown";
      const plan = this.mitigationFor(type);
      return {
        id: `fa-${a.id}`,
        source: "field_assessment",
        riskType: type,
        governorate: a.disaster?.governorate ?? null,
        fieldId: a.fieldId,
        riskScore: this.scoreFromDamage(a.damagePercentage),
        probability: a.disaster
          ? this.probabilityFromSeverity(a.disaster.severity)
          : 0.5,
        severity: a.disaster?.severity ?? "medium",
        status: "historical",
        mitigationPlan: plan.en,
        mitigationPlanAr: plan.ar,
        computedAt: a.assessedAt.toISOString(),
      };
    }

    throw new NotFoundException({
      error: "Risk not found",
      errorAr: "المخاطرة غير موجودة",
    });
  }
}
