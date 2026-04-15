/**
 * HtmlReportRenderer Unit Tests
 * اختبارات مُولّد تقارير HTML — OS/لغة-محايد، لا I/O
 */

import {
  HtmlReportRenderer,
  type ReportInputSnapshot,
} from "../renderers/html-report.renderer";

function snapshot(): ReportInputSnapshot {
  return {
    field: {
      id: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      name: "Field Alpha",
      nameAr: "الحقل الأول",
      cropType: "wheat",
      areaHectares: 5.5,
      plantingDate: new Date("2026-01-15T00:00:00Z"),
      expectedHarvest: new Date("2026-06-15T00:00:00Z"),
      irrigationType: "drip",
      tenantId: "tenant-aaa",
    },
    currentSeason: {
      id: "22222222-3333-4444-5555-666666666666",
      cropType: "wheat",
      cropTypeAr: "قمح",
      sowingDate: new Date("2026-01-15T00:00:00Z"),
      expectedHarvestDate: new Date("2026-06-15T00:00:00Z"),
      seedVariety: "Sakha 95",
      plantingDensityKgHa: 120,
      totalSeasonCost: 2500,
      totalSeasonHours: 48,
      totalCo2EmissionsKg: 150,
      totalCo2SequestrationKg: 50,
      totalCo2NetKg: 100,
    },
    operations: [
      {
        id: "op-1",
        operationType: "plowing",
        performedAt: new Date("2026-01-10T08:00:00Z"),
        durationHours: 6,
        costAmount: 1200,
        costCurrency: "SAR",
        equipmentName: "John Deere 6120",
        equipmentNameAr: "جون دير 6120",
        co2EmissionsKg: 75,
        co2SequestrationKg: 0,
        notes: null,
      },
      {
        id: "op-2",
        operationType: "sowing",
        performedAt: new Date("2026-01-15T09:00:00Z"),
        durationHours: 4,
        costAmount: 800,
        costCurrency: "SAR",
        equipmentName: null,
        equipmentNameAr: null,
        co2EmissionsKg: 30,
        co2SequestrationKg: 50,
        notes: "Cover crop variant",
      },
    ],
    subZones: [
      {
        id: "zone-1",
        name: "Upper Terrace",
        nameAr: "المدرجة العليا",
        areaHectares: 1.5,
        isTerrace: true,
        terraceLevel: 3,
      },
    ],
    period: {
      from: new Date("2026-01-01T00:00:00Z"),
      to: new Date("2026-04-01T00:00:00Z"),
      generatedAt: new Date("2026-04-01T10:00:00Z"),
    },
  };
}

describe("HtmlReportRenderer", () => {
  const renderer = new HtmlReportRenderer();

  it("renders Arabic field_summary with RTL direction", () => {
    const { html, contentType, sizeBytes } = renderer.render({
      reportType: "field_summary",
      language: "ar",
      snapshot: snapshot(),
    });
    expect(contentType).toContain("text/html");
    expect(sizeBytes).toBeGreaterThan(0);
    expect(html).toContain('dir="rtl"');
    expect(html).toContain('lang="ar"');
    expect(html).toContain("الحقل الأول");
    expect(html).toContain("قمح");
    // Contains the generated-at footer
    expect(html).toContain("سهول");
  });

  it("renders English field_summary with LTR direction", () => {
    const { html } = renderer.render({
      reportType: "field_summary",
      language: "en",
      snapshot: snapshot(),
    });
    expect(html).toContain('dir="ltr"');
    expect(html).toContain('lang="en"');
    expect(html).toContain("Field Alpha");
    expect(html).toContain("Field Summary Report");
  });

  it("escapes HTML entities in field name to prevent XSS", () => {
    const s = snapshot();
    s.field.name = 'Bad <script>alert("x")</script> Name';
    const { html } = renderer.render({
      reportType: "field_summary",
      language: "en",
      snapshot: s,
    });
    expect(html).not.toContain("<script>");
    expect(html).toContain("&lt;script&gt;");
  });

  it("renders operation_log table with all operations", () => {
    const { html } = renderer.render({
      reportType: "operation_log",
      language: "ar",
      snapshot: snapshot(),
    });
    expect(html).toContain("الحراثة");
    expect(html).toContain("البذار");
    expect(html).toContain("جون دير 6120");
  });

  it("renders carbon_footprint report with totals + breakdown", () => {
    const { html } = renderer.render({
      reportType: "carbon_footprint",
      language: "ar",
      snapshot: snapshot(),
    });
    expect(html).toContain("البصمة الكربونية");
    expect(html).toContain("105.0"); // emissions total 75+30
    expect(html).toContain("50.0"); // sequestration total
  });

  it("includes sub-zones section when sub-zones exist", () => {
    const { html } = renderer.render({
      reportType: "field_summary",
      language: "ar",
      snapshot: snapshot(),
    });
    expect(html).toContain("المناطق الفرعية");
    expect(html).toContain("المدرجة العليا");
  });

  it("omits sub-zones section for empty sub-zone list", () => {
    const s = snapshot();
    s.subZones = [];
    const { html } = renderer.render({
      reportType: "field_summary",
      language: "ar",
      snapshot: s,
    });
    expect(html).not.toContain("المناطق الفرعية");
  });

  it("falls back to current season 'ended by' placeholder for unsupported types", () => {
    const { html } = renderer.render({
      reportType: "weather_history",
      language: "ar",
      snapshot: snapshot(),
    });
    // Unsupported types render the note section instead of crashing.
    expect(html).toContain("قيد التطوير");
  });

  it("produces deterministic output for identical input (no Date.now)", () => {
    const a = renderer.render({
      reportType: "field_summary",
      language: "ar",
      snapshot: snapshot(),
    }).html;
    const b = renderer.render({
      reportType: "field_summary",
      language: "ar",
      snapshot: snapshot(),
    }).html;
    expect(a).toBe(b);
  });
});
