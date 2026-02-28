/**
 * Export Utilities Tests
 * اختبارات أدوات التصدير
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { exportToCSV, exportToExcel, exportData, exportFormatLabels } from "../export";
import type { ExportColumn } from "../export";

const columns: ExportColumn[] = [
  { key: "name", header: "Name", headerAr: "الاسم" },
  { key: "area", header: "Area", headerAr: "المساحة" },
  { key: "status", header: "Status", headerAr: "الحالة" },
];

const data = [
  { name: "حقل 1", area: 10.5, status: "active" },
  { name: "حقل 2", area: 8.3, status: "inactive" },
];

describe("Export Utilities", () => {
  let mockClick: ReturnType<typeof vi.fn>;
  let createElementSpy: ReturnType<typeof vi.spyOn>;
  let appendChildSpy: ReturnType<typeof vi.spyOn>;
  let removeChildSpy: ReturnType<typeof vi.spyOn>;
  let createObjectURLSpy: ReturnType<typeof vi.fn>;
  let revokeObjectURLSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockClick = vi.fn();

    // Mock URL APIs
    createObjectURLSpy = vi.fn(() => "blob:mock-url");
    revokeObjectURLSpy = vi.fn();
    Object.defineProperty(URL, "createObjectURL", {
      value: createObjectURLSpy,
      writable: true,
      configurable: true,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      value: revokeObjectURLSpy,
      writable: true,
      configurable: true,
    });

    // Mock only the 'a' element creation, pass through everything else
    const originalCreateElement = document.createElement.bind(document);
    createElementSpy = vi
      .spyOn(document, "createElement")
      .mockImplementation((tag: string, options?: ElementCreationOptions) => {
        if (tag === "a") {
          return {
            href: "",
            download: "",
            click: mockClick,
            style: {},
          } as unknown as HTMLAnchorElement;
        }
        return originalCreateElement(tag, options);
      });

    appendChildSpy = vi
      .spyOn(document.body, "appendChild")
      .mockImplementation((node) => node);
    removeChildSpy = vi
      .spyOn(document.body, "removeChild")
      .mockImplementation((node) => node);
  });

  afterEach(() => {
    createElementSpy.mockRestore();
    appendChildSpy.mockRestore();
    removeChildSpy.mockRestore();
  });

  describe("exportToCSV", () => {
    it("creates and downloads a CSV file", () => {
      exportToCSV({ filename: "test", columns, data });

      expect(createObjectURLSpy).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
      expect(revokeObjectURLSpy).toHaveBeenCalledWith("blob:mock-url");
    });

    it("uses Arabic headers by default", () => {
      // Capture blob content
      const blobParts: BlobPart[] = [];
      const OriginalBlob = globalThis.Blob;
      const BlobSpy = vi.fn().mockImplementation((parts?: BlobPart[], options?: BlobPropertyBag) => {
        if (parts) blobParts.push(...parts);
        return new OriginalBlob(parts, options);
      });
      vi.stubGlobal("Blob", BlobSpy);

      exportToCSV({ filename: "test", columns, data });

      const content = blobParts.map(String).join("");
      expect(content).toContain("الاسم");
      expect(content).toContain("المساحة");

      vi.unstubAllGlobals();
    });

    it("handles data with commas and quotes", () => {
      const specialData = [
        { name: 'حقل "خاص"', area: "1,234", status: "active" },
      ];

      expect(() =>
        exportToCSV({ filename: "test", columns, data: specialData }),
      ).not.toThrow();
    });

    it("handles null and undefined values", () => {
      const nullData = [{ name: null, area: undefined, status: "active" }];

      expect(() =>
        exportToCSV({
          filename: "test",
          columns,
          data: nullData as unknown as Record<string, unknown>[],
        }),
      ).not.toThrow();
    });

    it("can exclude header row", () => {
      expect(() =>
        exportToCSV({
          filename: "test",
          columns,
          data,
          includeHeader: false,
        }),
      ).not.toThrow();
    });
  });

  describe("exportToExcel", () => {
    it("creates and downloads an Excel file", () => {
      exportToExcel({ filename: "test", columns, data });

      expect(createObjectURLSpy).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
    });

    it("includes title when provided", () => {
      expect(() =>
        exportToExcel({
          filename: "test",
          title: "Test Report",
          titleAr: "تقرير اختبار",
          columns,
          data,
        }),
      ).not.toThrow();
    });

    it("handles empty data", () => {
      expect(() =>
        exportToExcel({ filename: "test", columns, data: [] }),
      ).not.toThrow();
    });
  });

  describe("exportData", () => {
    it("routes to CSV exporter", () => {
      expect(() =>
        exportData({ filename: "test", columns, data, format: "csv" }),
      ).not.toThrow();
    });

    it("routes to Excel exporter", () => {
      expect(() =>
        exportData({ filename: "test", columns, data, format: "excel" }),
      ).not.toThrow();
    });

    it("throws for unsupported format", () => {
      expect(() =>
        exportData({
          filename: "test",
          columns,
          data,
          format: "unknown" as "csv",
        }),
      ).toThrow("Unsupported export format");
    });
  });

  describe("exportFormatLabels", () => {
    it("has labels for all formats", () => {
      expect(exportFormatLabels.csv).toEqual({ en: "CSV", ar: "CSV" });
      expect(exportFormatLabels.excel).toEqual({ en: "Excel", ar: "Excel" });
      expect(exportFormatLabels.pdf).toEqual({ en: "PDF", ar: "PDF" });
    });
  });
});
