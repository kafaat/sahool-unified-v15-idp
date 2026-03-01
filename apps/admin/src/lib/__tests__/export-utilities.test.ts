/**
 * Export Utilities Tests
 * اختبارات أدوات التصدير
 *
 * Tests CSV, Excel, and PDF export functionality.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  exportToCSV,
  exportToExcel,
  exportToPDF,
  exportData,
  exportFormatLabels,
  type ExportColumn,
} from "../export";

// Mock DOM APIs
let createdBlobContent: string | undefined;
let createdBlobType: string | undefined;
let downloadedFilename: string | undefined;

beforeEach(() => {
  createdBlobContent = undefined;
  createdBlobType = undefined;
  downloadedFilename = undefined;

  // Mock URL.createObjectURL and revokeObjectURL
  vi.stubGlobal("URL", {
    createObjectURL: vi.fn(() => "blob:test-url"),
    revokeObjectURL: vi.fn(),
  });

  // Mock Blob
  vi.stubGlobal(
    "Blob",
    class MockBlob {
      content: string;
      options: { type: string };
      constructor(parts: string[], options: { type: string }) {
        this.content = parts.join("");
        this.options = options;
        createdBlobContent = this.content;
        createdBlobType = options.type;
      }
    },
  );

  // Mock document methods for download
  const mockLink = {
    href: "",
    download: "",
    click: vi.fn(),
  };
  vi.spyOn(document, "createElement").mockReturnValue(
    mockLink as unknown as HTMLElement,
  );
  vi.spyOn(document.body, "appendChild").mockImplementation((node) => {
    downloadedFilename = (node as unknown as { download: string }).download;
    return node;
  });
  vi.spyOn(document.body, "removeChild").mockImplementation((node) => node);
});

const sampleColumns: ExportColumn[] = [
  { key: "name", header: "Name", headerAr: "الاسم" },
  { key: "area", header: "Area (ha)", headerAr: "المساحة (هكتار)" },
  { key: "health", header: "Health", headerAr: "الصحة" },
];

const sampleData = [
  { name: "مزرعة الشمال", area: 15.5, health: 85 },
  { name: "مزرعة الجنوب", area: 8.2, health: 62 },
  { name: "مزرعة الوسط", area: 22.0, health: 45 },
];

// ═══════════════════════════════════════════════════════════════════════════
// CSV Export Tests | اختبارات تصدير CSV
// ═══════════════════════════════════════════════════════════════════════════

describe("CSV Export", () => {
  it("generates CSV with Arabic headers", () => {
    exportToCSV({
      filename: "test-farms",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toBeDefined();
    expect(createdBlobContent).toContain("الاسم");
    expect(createdBlobContent).toContain("المساحة (هكتار)");
    expect(createdBlobContent).toContain("الصحة");
  });

  it("includes BOM for Arabic character support", () => {
    exportToCSV({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toBeDefined();
    // BOM character
    expect(createdBlobContent!.charCodeAt(0)).toBe(0xfeff);
  });

  it("includes data rows", () => {
    exportToCSV({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toContain("مزرعة الشمال");
    expect(createdBlobContent).toContain("15.5");
    expect(createdBlobContent).toContain("85");
  });

  it("skips header when includeHeader is false", () => {
    exportToCSV({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
      includeHeader: false,
    });

    expect(createdBlobContent).not.toContain("الاسم,المساحة");
  });

  it("escapes commas in values", () => {
    const dataWithComma = [{ name: "مزرعة أ, مزرعة ب", area: 10, health: 70 }];

    exportToCSV({
      filename: "test",
      columns: sampleColumns,
      data: dataWithComma,
    });

    // Value with comma should be quoted
    expect(createdBlobContent).toContain('"مزرعة أ, مزرعة ب"');
  });

  it("handles null/undefined values", () => {
    const dataWithNull = [
      { name: "test", area: null, health: undefined },
    ];

    exportToCSV({
      filename: "test",
      columns: sampleColumns,
      data: dataWithNull as any,
    });

    expect(createdBlobContent).toBeDefined();
  });

  it("applies column format function", () => {
    const columnsWithFormat: ExportColumn[] = [
      {
        key: "health",
        header: "Health",
        headerAr: "الصحة",
        format: (v) => `${v}%`,
      },
    ];

    exportToCSV({
      filename: "test",
      columns: columnsWithFormat,
      data: [{ health: 85 }],
    });

    expect(createdBlobContent).toContain("85%");
  });

  it("sets CSV content type", () => {
    exportToCSV({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobType).toBe("text/csv;charset=utf-8");
  });

  it("downloads with .csv extension", () => {
    exportToCSV({
      filename: "farms-report",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(downloadedFilename).toBe("farms-report.csv");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Excel Export Tests | اختبارات تصدير Excel
// ═══════════════════════════════════════════════════════════════════════════

describe("Excel Export", () => {
  it("generates Excel XML format", () => {
    exportToExcel({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toContain("Workbook");
    expect(createdBlobContent).toContain("Worksheet");
  });

  it("includes Arabic headers in Excel", () => {
    exportToExcel({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toContain("الاسم");
    expect(createdBlobContent).toContain("المساحة (هكتار)");
  });

  it("uses Tajawal font for Arabic support", () => {
    exportToExcel({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toContain("Tajawal");
  });

  it("sets RTL reading order", () => {
    exportToExcel({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toContain("RightToLeft");
  });

  it("includes title row when provided", () => {
    exportToExcel({
      filename: "test",
      title: "Farms Report",
      titleAr: "تقرير المزارع",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toContain("تقرير المزارع");
  });

  it("escapes XML special characters", () => {
    const dataWithSpecial = [
      { name: "Farm <A> & \"B\"", area: 10, health: 70 },
    ];

    exportToExcel({
      filename: "test",
      columns: sampleColumns,
      data: dataWithSpecial,
    });

    expect(createdBlobContent).not.toContain("<A>");
    expect(createdBlobContent).toContain("&lt;A&gt;");
  });

  it("downloads with .xls extension", () => {
    exportToExcel({
      filename: "farms-export",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(downloadedFilename).toBe("farms-export.xls");
  });

  it("uses Number type for numeric data", () => {
    exportToExcel({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobContent).toContain('ss:Type="Number"');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// PDF Export Tests | اختبارات تصدير PDF
// ═══════════════════════════════════════════════════════════════════════════

describe("PDF Export", () => {
  let mockPrintWindow: {
    document: { write: ReturnType<typeof vi.fn>; close: ReturnType<typeof vi.fn> };
    print: ReturnType<typeof vi.fn>;
    onload: (() => void) | null;
  };

  beforeEach(() => {
    mockPrintWindow = {
      document: { write: vi.fn(), close: vi.fn() },
      print: vi.fn(),
      onload: null,
    };
    vi.stubGlobal("open", vi.fn(() => mockPrintWindow));
  });

  it("opens a new window for PDF export", () => {
    exportToPDF({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(window.open).toHaveBeenCalledWith("", "_blank");
  });

  it("generates RTL HTML content", () => {
    exportToPDF({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    const htmlContent = mockPrintWindow.document.write.mock.calls[0][0] as string;
    expect(htmlContent).toContain('dir="rtl"');
    expect(htmlContent).toContain('lang="ar"');
  });

  it("includes Tajawal font for Arabic", () => {
    exportToPDF({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    const htmlContent = mockPrintWindow.document.write.mock.calls[0][0] as string;
    expect(htmlContent).toContain("Tajawal");
  });

  it("includes Arabic title", () => {
    exportToPDF({
      filename: "test",
      titleAr: "تقرير المزارع",
      columns: sampleColumns,
      data: sampleData,
    });

    const htmlContent = mockPrintWindow.document.write.mock.calls[0][0] as string;
    expect(htmlContent).toContain("تقرير المزارع");
  });

  it("includes Sahool branding", () => {
    exportToPDF({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    const htmlContent = mockPrintWindow.document.write.mock.calls[0][0] as string;
    expect(htmlContent).toContain("سهول");
    expect(htmlContent).toContain("SAHOOL");
  });

  it("renders data table with columns", () => {
    exportToPDF({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    const htmlContent = mockPrintWindow.document.write.mock.calls[0][0] as string;
    expect(htmlContent).toContain("<table>");
    expect(htmlContent).toContain("<th>الاسم</th>");
    expect(htmlContent).toContain("مزرعة الشمال");
  });

  it("includes Arabic footer", () => {
    exportToPDF({
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
      footerTextAr: "تقرير رسمي",
    });

    const htmlContent = mockPrintWindow.document.write.mock.calls[0][0] as string;
    expect(htmlContent).toContain("تقرير رسمي");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Main Export Dispatcher | اختبار الموزع الرئيسي للتصدير
// ═══════════════════════════════════════════════════════════════════════════

describe("exportData Dispatcher", () => {
  it("dispatches to CSV handler", () => {
    exportData({
      format: "csv",
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobType).toBe("text/csv;charset=utf-8");
  });

  it("dispatches to Excel handler", () => {
    exportData({
      format: "excel",
      filename: "test",
      columns: sampleColumns,
      data: sampleData,
    });

    expect(createdBlobType).toContain("ms-excel");
  });

  it("throws for unsupported format", () => {
    expect(() => {
      exportData({
        format: "xml" as any,
        filename: "test",
        columns: sampleColumns,
        data: sampleData,
      });
    }).toThrow("Unsupported export format");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Export Format Labels | تسميات صيغ التصدير
// ═══════════════════════════════════════════════════════════════════════════

describe("Export Format Labels", () => {
  it("has labels for all formats", () => {
    expect(exportFormatLabels.csv).toBeDefined();
    expect(exportFormatLabels.excel).toBeDefined();
    expect(exportFormatLabels.pdf).toBeDefined();
  });

  it("has Arabic and English labels", () => {
    expect(exportFormatLabels.csv.ar).toBeDefined();
    expect(exportFormatLabels.csv.en).toBeDefined();
    expect(exportFormatLabels.excel.ar).toBeDefined();
    expect(exportFormatLabels.excel.en).toBeDefined();
    expect(exportFormatLabels.pdf.ar).toBeDefined();
    expect(exportFormatLabels.pdf.en).toBeDefined();
  });
});
