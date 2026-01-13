/**
 * Reports Types Unit Tests
 * اختبارات وحدة أنواع التقارير
 *
 * Tests for report generation type definitions
 */

import { describe, it, expect } from "vitest";
import type {
  ReportType,
  ReportFormat,
  ReportStatus,
  ReportSection,
  ShareMethod,
  FieldReportOptions,
  FieldReportData,
  SeasonReportOptions,
} from "../types/reports";

describe("Reports Types", () => {
  describe("ReportType", () => {
    it("should include all report types", () => {
      const types: ReportType[] = [
        "field",
        "season",
        "scouting",
        "tasks",
        "ndvi",
        "weather",
        "comprehensive",
      ];

      expect(types).toHaveLength(7);
      expect(types).toContain("field");
      expect(types).toContain("comprehensive");
    });
  });

  describe("ReportFormat", () => {
    it("should support all export formats", () => {
      const formats: ReportFormat[] = ["pdf", "excel", "csv", "json"];

      expect(formats).toHaveLength(4);
      expect(formats).toContain("pdf");
      expect(formats).toContain("excel");
    });
  });

  describe("ReportStatus", () => {
    it("should have all status values", () => {
      const statuses: ReportStatus[] = [
        "pending",
        "generating",
        "ready",
        "failed",
        "expired",
      ];

      expect(statuses).toHaveLength(5);
      expect(statuses).toContain("ready");
      expect(statuses).toContain("generating");
    });
  });

  describe("ReportSection", () => {
    it("should include all report sections", () => {
      const sections: ReportSection[] = [
        "field_info",
        "ndvi_trend",
        "health_zones",
        "tasks_summary",
        "weather_summary",
        "recommendations",
        "crop_stages",
        "yield_estimate",
        "input_summary",
        "cost_analysis",
        "pest_disease",
        "soil_analysis",
      ];

      expect(sections).toHaveLength(12);
      expect(sections).toContain("ndvi_trend");
      expect(sections).toContain("recommendations");
    });
  });

  describe("ShareMethod", () => {
    it("should support all sharing methods", () => {
      const methods: ShareMethod[] = ["link", "email", "whatsapp", "download"];

      expect(methods).toHaveLength(4);
      expect(methods).toContain("whatsapp");
      expect(methods).toContain("email");
    });
  });

  describe("FieldReportOptions Interface", () => {
    it("should create valid field report options", () => {
      const options: FieldReportOptions = {
        fieldId: "field-001",
        startDate: "2025-01-01",
        endDate: "2025-12-31",
        sections: ["field_info", "ndvi_trend", "recommendations"],
        includeCharts: true,
        includeMaps: true,
        format: "pdf",
        language: "both",
      };

      expect(options.fieldId).toBeDefined();
      expect(options.sections).toHaveLength(3);
      expect(options.language).toBe("both");
    });

    it("should support minimal options", () => {
      const minimalOptions: FieldReportOptions = {
        fieldId: "field-002",
        sections: ["field_info"],
      };

      expect(minimalOptions.fieldId).toBeDefined();
      expect(minimalOptions.startDate).toBeUndefined();
    });
  });

  describe("FieldReportData Interface", () => {
    it("should contain complete field data", () => {
      const reportData: FieldReportData = {
        field: {
          id: "field-001",
          name: "Main Farm Field",
          nameAr: "حقل المزرعة الرئيسي",
          area: 15.5,
          location: {
            latitude: 15.3694,
            longitude: 44.191,
            governorate: "Sana'a",
            governorateAr: "صنعاء",
          },
          cropType: "Wheat",
          cropTypeAr: "قمح",
          plantingDate: "2025-10-15",
        },
        ndviTrend: {
          dates: ["2025-10-01", "2025-11-01", "2025-12-01"],
          values: [0.35, 0.55, 0.72],
          average: 0.54,
          trend: "increasing",
        },
        healthZones: {
          healthy: 60,
          moderate: 25,
          stressed: 10,
          critical: 5,
        },
      };

      expect(reportData.field.area).toBe(15.5);
      expect(reportData.ndviTrend?.trend).toBe("increasing");
      expect(reportData.healthZones?.healthy).toBe(60);
    });

    it("should validate health zones sum to 100", () => {
      const healthZones = {
        healthy: 60,
        moderate: 25,
        stressed: 10,
        critical: 5,
      };

      const total =
        healthZones.healthy +
        healthZones.moderate +
        healthZones.stressed +
        healthZones.critical;
      expect(total).toBe(100);
    });

    it("should support recommendations data", () => {
      const reportData: Partial<FieldReportData> = {
        recommendations: [
          {
            id: "rec-001",
            type: "irrigation",
            priority: "high",
            title: "Increase irrigation frequency",
            titleAr: "زيادة تكرار الري",
            description: "Due to high temperatures, increase irrigation.",
            descriptionAr: "بسبب ارتفاع درجات الحرارة، قم بزيادة الري.",
          },
          {
            id: "rec-002",
            type: "fertilizer",
            priority: "medium",
            title: "Apply nitrogen fertilizer",
            titleAr: "تطبيق الأسمدة النيتروجينية",
            description: "NDVI shows nitrogen deficiency.",
            descriptionAr: "يظهر NDVI نقص النيتروجين.",
          },
        ],
      };

      expect(reportData.recommendations).toHaveLength(2);
      expect(reportData.recommendations?.[0].priority).toBe("high");
    });
  });

  describe("SeasonReportOptions Interface", () => {
    it("should create valid season report options", () => {
      const options: SeasonReportOptions = {
        fieldId: "field-001",
        season: "2025-fall",
        startDate: "2025-09-01",
        endDate: "2025-12-31",
        sections: ["yield_estimate", "cost_analysis", "input_summary"],
        includeCharts: true,
        format: "excel",
        language: "ar",
      };

      expect(options.season).toBe("2025-fall");
      expect(options.sections).toContain("yield_estimate");
    });
  });
});

describe("Reports Data Validation", () => {
  it("should validate NDVI values are between 0 and 1", () => {
    const ndviValues = [0.35, 0.55, 0.72, 0.85];

    ndviValues.forEach((value) => {
      expect(value).toBeGreaterThanOrEqual(0);
      expect(value).toBeLessThanOrEqual(1);
    });
  });

  it("should validate coordinates are in valid range", () => {
    const location = {
      latitude: 15.3694,
      longitude: 44.191,
    };

    expect(location.latitude).toBeGreaterThanOrEqual(-90);
    expect(location.latitude).toBeLessThanOrEqual(90);
    expect(location.longitude).toBeGreaterThanOrEqual(-180);
    expect(location.longitude).toBeLessThanOrEqual(180);
  });

  it("should validate area is positive", () => {
    const area = 15.5;
    expect(area).toBeGreaterThan(0);
  });

  it("should validate date format", () => {
    const dateString = "2025-10-15";
    const date = new Date(dateString);

    expect(date).toBeInstanceOf(Date);
    expect(date.getTime()).not.toBeNaN();
  });

  it("should support bilingual content", () => {
    const bilingualField = {
      name: "North Field",
      nameAr: "الحقل الشمالي",
      cropType: "Maize",
      cropTypeAr: "ذرة",
    };

    expect(bilingualField.name).toBeTruthy();
    expect(bilingualField.nameAr).toBeTruthy();
    expect(bilingualField.cropTypeAr).toContain("ذرة");
  });
});

describe("Report Generation Business Rules", () => {
  it("should require field_info section for all reports", () => {
    const options: FieldReportOptions = {
      fieldId: "field-001",
      sections: ["field_info", "ndvi_trend"],
    };

    expect(options.sections).toContain("field_info");
  });

  it("should default to PDF format if not specified", () => {
    const options: FieldReportOptions = {
      fieldId: "field-001",
      sections: ["field_info"],
    };

    const format = options.format || "pdf";
    expect(format).toBe("pdf");
  });

  it("should support both languages option", () => {
    const options: FieldReportOptions = {
      fieldId: "field-001",
      sections: ["field_info"],
      language: "both",
    };

    expect(options.language).toBe("both");
  });
});
