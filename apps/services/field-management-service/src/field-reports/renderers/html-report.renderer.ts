/**
 * HTML Report Renderer
 * مُولّد التقارير HTML بالعربية RTL
 *
 * Produces a self-contained, printable HTML document in Arabic RTL or
 * English LTR. No external templating engine — string templates keep
 * the dependency footprint zero and let us inline CSS + fonts for
 * consistent rendering whether the output is served as HTML or later
 * converted to PDF (via headless chromium in a future enhancement).
 *
 * Supported report types (matches DTO):
 *   - field_summary        — snapshot of the field + current season
 *   - crop_season          — per-season history with operations log
 *   - operation_log        — flat list of every operation
 *   - carbon_footprint     — CO2 balance per operation + season total
 *   - ndvi_timeseries      — NDVI chart (placeholder — future enhancement)
 *   - weather_history      — daily weather summary (future enhancement)
 *   - financial_summary    — cost breakdown + ROI (future enhancement)
 *
 * Bilingual: caller picks language='ar' | 'en'. Arabic uses `dir="rtl"`
 * and a Noto Sans Arabic web font fallback so output renders correctly
 * in any modern browser or PDF engine.
 */

import { Injectable } from "@nestjs/common";

export interface ReportInputSnapshot {
  field: {
    id: string;
    name: string;
    nameAr?: string | null;
    cropType: string;
    areaHectares: number | null;
    plantingDate: Date | null;
    expectedHarvest: Date | null;
    irrigationType: string | null;
    tenantId: string;
  };
  currentSeason?: {
    id: string;
    cropType: string;
    cropTypeAr: string | null;
    sowingDate: Date;
    expectedHarvestDate: Date | null;
    seedVariety: string | null;
    plantingDensityKgHa: number | null;
    totalSeasonCost: number | null;
    totalSeasonHours: number | null;
    totalCo2EmissionsKg: number | null;
    totalCo2SequestrationKg: number | null;
    totalCo2NetKg: number | null;
  } | null;
  operations: Array<{
    id: string;
    operationType: string;
    performedAt: Date;
    durationHours: number | null;
    costAmount: number | null;
    costCurrency: string;
    equipmentName: string | null;
    equipmentNameAr: string | null;
    co2EmissionsKg: number | null;
    co2SequestrationKg: number | null;
    notes: string | null;
  }>;
  subZones?: Array<{
    id: string;
    name: string;
    nameAr: string | null;
    areaHectares: number | null;
    isTerrace: boolean;
    terraceLevel: number | null;
  }>;
  period: {
    from: Date | null;
    to: Date | null;
    generatedAt: Date;
  };
}

export type ReportRenderType =
  | "field_summary"
  | "crop_season"
  | "operation_log"
  | "carbon_footprint"
  | "ndvi_timeseries"
  | "weather_history"
  | "financial_summary";

@Injectable()
export class HtmlReportRenderer {
  /**
   * Main entrypoint. Returns { html, contentType, sizeBytes }.
   */
  render(args: {
    reportType: ReportRenderType;
    language: "ar" | "en";
    snapshot: ReportInputSnapshot;
  }): { html: string; contentType: string; sizeBytes: number } {
    const html = this.buildDocument(args);
    return {
      html,
      contentType: "text/html; charset=utf-8",
      sizeBytes: Buffer.byteLength(html, "utf8"),
    };
  }

  // -------------------------------------------------------------------
  // Document assembly
  // -------------------------------------------------------------------

  private buildDocument(args: {
    reportType: ReportRenderType;
    language: "ar" | "en";
    snapshot: ReportInputSnapshot;
  }): string {
    const { reportType, language, snapshot } = args;
    const isRtl = language === "ar";
    const dir = isRtl ? "rtl" : "ltr";
    const lang = language;

    const titleByType: Record<ReportRenderType, { ar: string; en: string }> = {
      field_summary: { ar: "تقرير ملخص الحقل", en: "Field Summary Report" },
      crop_season: { ar: "تقرير الموسم المحصولي", en: "Crop Season Report" },
      operation_log: { ar: "سجل عمليات الحقل", en: "Field Operations Log" },
      carbon_footprint: {
        ar: "تقرير البصمة الكربونية",
        en: "Carbon Footprint Report",
      },
      ndvi_timeseries: {
        ar: "تقرير مؤشر NDVI",
        en: "NDVI Time-Series Report",
      },
      weather_history: {
        ar: "تقرير الطقس التاريخي",
        en: "Weather History Report",
      },
      financial_summary: {
        ar: "الملخص المالي",
        en: "Financial Summary Report",
      },
    };

    const title = titleByType[reportType][language];
    const fieldName =
      (isRtl ? snapshot.field.nameAr : undefined) ?? snapshot.field.name;

    const body = this.buildBody(reportType, language, snapshot);
    const generatedAt = this.fmtDateTime(snapshot.period.generatedAt, language);

    // Inline stylesheet — no external deps, prints cleanly.
    return `<!DOCTYPE html>
<html lang="${lang}" dir="${dir}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${this.esc(title)} — ${this.esc(fieldName)}</title>
<style>
  @media print { body { margin: 0; } .no-print { display: none; } }
  body {
    font-family: ${
      isRtl
        ? "'Noto Sans Arabic', 'Tajawal', 'Cairo', sans-serif"
        : "-apple-system, 'Segoe UI', Roboto, Arial, sans-serif"
    };
    color: #1f2937;
    max-width: 900px;
    margin: 24px auto;
    padding: 24px;
    line-height: 1.6;
    direction: ${dir};
  }
  header { border-bottom: 3px solid #16a34a; padding-bottom: 12px; margin-bottom: 24px; }
  header h1 { color: #166534; font-size: 24px; margin: 0 0 4px 0; }
  header .sub { color: #6b7280; font-size: 13px; }
  h2 { color: #166534; font-size: 18px; margin-top: 28px; border-${
    isRtl ? "right" : "left"
  }: 4px solid #22c55e; padding-${isRtl ? "right" : "left"}: 10px; }
  table { width: 100%; border-collapse: collapse; margin: 12px 0; }
  th, td { border: 1px solid #d1d5db; padding: 8px 12px; text-align: ${
    isRtl ? "right" : "left"
  }; font-size: 13px; }
  th { background: #f0fdf4; color: #14532d; font-weight: 600; }
  .metric { display: inline-block; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 16px; margin: 4px; min-width: 140px; }
  .metric .label { color: #6b7280; font-size: 11px; }
  .metric .value { color: #14532d; font-size: 20px; font-weight: 700; }
  .metric .unit  { color: #6b7280; font-size: 11px; margin-${isRtl ? "right" : "left"}: 4px; }
  .badge-positive { background: #dcfce7; color: #14532d; padding: 2px 8px; border-radius: 999px; font-size: 11px; }
  .badge-negative { background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 999px; font-size: 11px; }
  footer { margin-top: 40px; padding-top: 12px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 11px; text-align: center; }
</style>
</head>
<body>
<header>
  <h1>${this.esc(title)}</h1>
  <div class="sub">
    ${this.esc(fieldName)}
    &middot;
    ${isRtl ? "أُنشئ في" : "Generated"} ${this.esc(generatedAt)}
  </div>
</header>
${body}
<footer>
  ${
    isRtl
      ? "تقرير مُولَّد آلياً بواسطة منصة سهول — KAFAAT"
      : "Report automatically generated by SAHOOL Platform — KAFAAT"
  }
</footer>
</body>
</html>`;
  }

  // -------------------------------------------------------------------
  // Section builders
  // -------------------------------------------------------------------

  private buildBody(
    reportType: ReportRenderType,
    language: "ar" | "en",
    snapshot: ReportInputSnapshot,
  ): string {
    switch (reportType) {
      case "field_summary":
        return (
          this.fieldInfoSection(snapshot, language) +
          this.currentSeasonSection(snapshot, language) +
          this.recentOperationsSection(snapshot, language, 10) +
          this.subZonesSection(snapshot, language)
        );
      case "crop_season":
        return (
          this.currentSeasonSection(snapshot, language) +
          this.operationsTable(snapshot, language)
        );
      case "operation_log":
        return this.operationsTable(snapshot, language);
      case "carbon_footprint":
        return (
          this.fieldInfoSection(snapshot, language) +
          this.carbonSection(snapshot, language)
        );
      case "ndvi_timeseries":
      case "weather_history":
      case "financial_summary":
        // Placeholder: fall back to field summary until these have
        // dedicated data fetchers. Caller sees `status=ready` anyway.
        return (
          this.fieldInfoSection(snapshot, language) +
          this.noteSection(language)
        );
    }
  }

  private fieldInfoSection(s: ReportInputSnapshot, lang: "ar" | "en"): string {
    const t = (ar: string, en: string) => (lang === "ar" ? ar : en);
    return `
<h2>${t("معلومات الحقل", "Field Information")}</h2>
<div>
  <span class="metric">
    <div class="label">${t("المساحة", "Area")}</div>
    <div class="value">${this.fmtNumber(s.field.areaHectares)}<span class="unit">${t("هكتار", "ha")}</span></div>
  </span>
  <span class="metric">
    <div class="label">${t("المحصول", "Crop")}</div>
    <div class="value">${this.esc(s.field.cropType)}</div>
  </span>
  <span class="metric">
    <div class="label">${t("نظام الري", "Irrigation")}</div>
    <div class="value">${this.esc(s.field.irrigationType ?? "—")}</div>
  </span>
  <span class="metric">
    <div class="label">${t("تاريخ الزراعة", "Planting")}</div>
    <div class="value">${this.esc(this.fmtDate(s.field.plantingDate, lang))}</div>
  </span>
  <span class="metric">
    <div class="label">${t("الحصاد المتوقع", "Expected Harvest")}</div>
    <div class="value">${this.esc(this.fmtDate(s.field.expectedHarvest, lang))}</div>
  </span>
</div>
`;
  }

  private currentSeasonSection(
    s: ReportInputSnapshot,
    lang: "ar" | "en",
  ): string {
    if (!s.currentSeason) return "";
    const t = (ar: string, en: string) => (lang === "ar" ? ar : en);
    const cs = s.currentSeason;
    return `
<h2>${t("الموسم الحالي", "Current Season")}</h2>
<table>
  <tr><th>${t("المحصول", "Crop")}</th><td>${this.esc((lang === "ar" ? cs.cropTypeAr : undefined) ?? cs.cropType)}</td></tr>
  <tr><th>${t("تاريخ البذار", "Sowing Date")}</th><td>${this.esc(this.fmtDate(cs.sowingDate, lang))}</td></tr>
  <tr><th>${t("الحصاد المتوقع", "Expected Harvest")}</th><td>${this.esc(this.fmtDate(cs.expectedHarvestDate, lang))}</td></tr>
  <tr><th>${t("الصنف", "Variety")}</th><td>${this.esc(cs.seedVariety ?? "—")}</td></tr>
  <tr><th>${t("كثافة البذر", "Planting Density")}</th><td>${this.fmtNumber(cs.plantingDensityKgHa)} kg/ha</td></tr>
  <tr><th>${t("إجمالي التكلفة", "Total Cost")}</th><td>${this.fmtNumber(cs.totalSeasonCost)} SAR</td></tr>
  <tr><th>${t("إجمالي الساعات", "Total Hours")}</th><td>${this.fmtNumber(cs.totalSeasonHours)} h</td></tr>
  <tr><th>${t("صافي الكربون", "Net CO₂")}</th><td>${this.fmtNumber(cs.totalCo2NetKg)} kg CO₂e</td></tr>
</table>
`;
  }

  private recentOperationsSection(
    s: ReportInputSnapshot,
    lang: "ar" | "en",
    limit: number,
  ): string {
    const subset = s.operations.slice(0, limit);
    if (subset.length === 0) return "";
    return this.operationsTableInternal(subset, lang, true);
  }

  private operationsTable(s: ReportInputSnapshot, lang: "ar" | "en"): string {
    return this.operationsTableInternal(s.operations, lang, false);
  }

  private operationsTableInternal(
    ops: ReportInputSnapshot["operations"],
    lang: "ar" | "en",
    isRecent: boolean,
  ): string {
    const t = (ar: string, en: string) => (lang === "ar" ? ar : en);
    const heading = isRecent
      ? t("العمليات الأخيرة", "Recent Operations")
      : t("سجل العمليات الكامل", "Full Operations Log");
    const rows = ops
      .map((op) => {
        const name =
          (lang === "ar" ? op.equipmentNameAr : undefined) ??
          op.equipmentName ??
          "—";
        const net = this.netCarbon(op);
        return `<tr>
          <td>${this.esc(this.fmtDate(op.performedAt, lang))}</td>
          <td>${this.esc(this.operationLabel(op.operationType, lang))}</td>
          <td>${this.fmtNumber(op.durationHours)}</td>
          <td>${this.fmtNumber(op.costAmount)} ${this.esc(op.costCurrency)}</td>
          <td>${this.esc(name)}</td>
          <td>${net}</td>
        </tr>`;
      })
      .join("\n");
    return `
<h2>${heading}</h2>
<table>
  <thead>
    <tr>
      <th>${t("التاريخ", "Date")}</th>
      <th>${t("النوع", "Type")}</th>
      <th>${t("ساعات", "Hours")}</th>
      <th>${t("التكلفة", "Cost")}</th>
      <th>${t("المعدة", "Equipment")}</th>
      <th>${t("صافي CO₂", "Net CO₂")}</th>
    </tr>
  </thead>
  <tbody>${rows}</tbody>
</table>
`;
  }

  private carbonSection(s: ReportInputSnapshot, lang: "ar" | "en"): string {
    const t = (ar: string, en: string) => (lang === "ar" ? ar : en);
    const totalEmit = s.operations.reduce(
      (sum, op) => sum + (op.co2EmissionsKg ?? 0),
      0,
    );
    const totalSeq = s.operations.reduce(
      (sum, op) => sum + (op.co2SequestrationKg ?? 0),
      0,
    );
    const net = totalEmit - totalSeq;
    const badge =
      net > 0
        ? `<span class="badge-negative">+${net.toFixed(1)} kg</span>`
        : `<span class="badge-positive">${net.toFixed(1)} kg</span>`;
    return `
<h2>${t("البصمة الكربونية", "Carbon Footprint")}</h2>
<div>
  <span class="metric">
    <div class="label">${t("إجمالي الانبعاثات", "Total Emissions")}</div>
    <div class="value">${totalEmit.toFixed(1)}<span class="unit">kg CO₂e</span></div>
  </span>
  <span class="metric">
    <div class="label">${t("إجمالي الاحتجاز", "Total Sequestration")}</div>
    <div class="value">${totalSeq.toFixed(1)}<span class="unit">kg CO₂e</span></div>
  </span>
  <span class="metric">
    <div class="label">${t("الصافي", "Net")}</div>
    <div class="value">${badge}</div>
  </span>
</div>
${this.operationsTableInternal(
  s.operations.filter((op) => op.co2EmissionsKg || op.co2SequestrationKg),
  lang,
  false,
)}
`;
  }

  private subZonesSection(s: ReportInputSnapshot, lang: "ar" | "en"): string {
    if (!s.subZones || s.subZones.length === 0) return "";
    const t = (ar: string, en: string) => (lang === "ar" ? ar : en);
    const rows = s.subZones
      .map(
        (z) => `<tr>
          <td>${this.esc((lang === "ar" ? z.nameAr : undefined) ?? z.name)}</td>
          <td>${this.fmtNumber(z.areaHectares)} ha</td>
          <td>${z.isTerrace ? t("مدرّجة", "Terrace") : "—"}</td>
          <td>${z.terraceLevel ?? "—"}</td>
        </tr>`,
      )
      .join("\n");
    return `
<h2>${t("المناطق الفرعية", "Sub-Zones")}</h2>
<table>
  <thead>
    <tr>
      <th>${t("الاسم", "Name")}</th>
      <th>${t("المساحة", "Area")}</th>
      <th>${t("نوع", "Type")}</th>
      <th>${t("المستوى", "Level")}</th>
    </tr>
  </thead>
  <tbody>${rows}</tbody>
</table>
`;
  }

  private noteSection(lang: "ar" | "en"): string {
    const t = (ar: string, en: string) => (lang === "ar" ? ar : en);
    return `
<p style="color:#6b7280; font-style: italic;">
  ${t(
    "هذا النوع من التقارير قيد التطوير وسيُدعم قريباً.",
    "This report type is under development and will be supported soon.",
  )}
</p>`;
  }

  // -------------------------------------------------------------------
  // Formatting helpers
  // -------------------------------------------------------------------

  private operationLabel(slug: string, lang: "ar" | "en"): string {
    const map: Record<string, { ar: string; en: string }> = {
      plowing: { ar: "الحراثة", en: "Plowing" },
      land_preparation: { ar: "تهيئة الأرض", en: "Land Preparation" },
      fertilization: { ar: "التسميد", en: "Fertilization" },
      spraying: { ar: "الرش", en: "Spraying" },
      irrigation: { ar: "الري", en: "Irrigation" },
      harvesting: { ar: "الحصاد", en: "Harvesting" },
      scouting: { ar: "الاستكشاف", en: "Scouting" },
      sowing: { ar: "البذار", en: "Sowing" },
      other: { ar: "أخرى", en: "Other" },
    };
    return map[slug]?.[lang] ?? slug;
  }

  private netCarbon(op: ReportInputSnapshot["operations"][number]): string {
    const emit = Number(op.co2EmissionsKg ?? 0);
    const seq = Number(op.co2SequestrationKg ?? 0);
    if (emit === 0 && seq === 0) return "—";
    const net = emit - seq;
    return net >= 0 ? `+${net.toFixed(1)}` : net.toFixed(1);
  }

  private fmtNumber(v: number | string | null | undefined): string {
    if (v === null || v === undefined) return "—";
    const n = typeof v === "number" ? v : Number(v);
    if (!Number.isFinite(n)) return "—";
    return n.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  private fmtDate(d: Date | null | undefined, lang: "ar" | "en"): string {
    if (!d) return "—";
    const dd = d instanceof Date ? d : new Date(d);
    if (Number.isNaN(dd.getTime())) return "—";
    return dd.toLocaleDateString(lang === "ar" ? "ar-SA" : "en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  }

  private fmtDateTime(d: Date, lang: "ar" | "en"): string {
    const dd = d instanceof Date ? d : new Date(d);
    return dd.toLocaleString(lang === "ar" ? "ar-SA" : "en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  /** Minimal HTML escaping — no external dep needed. */
  private esc(v: string | null | undefined): string {
    if (v === null || v === undefined) return "";
    return String(v)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
}
