import { describe, it, expect } from "vitest";
import {
  getHealthScoreColor,
  getSeverityColor,
  getStatusColor,
  getSeverityLabel,
  getStatusLabel,
  formatDate,
  formatNumber,
  formatArea,
} from "../utils";

describe("getHealthScoreColor", () => {
  it("returns dark green for excellent scores (>= 80)", () => {
    expect(getHealthScoreColor(80)).toBe("text-green-700 bg-green-100");
    expect(getHealthScoreColor(95)).toBe("text-green-700 bg-green-100");
    expect(getHealthScoreColor(100)).toBe("text-green-700 bg-green-100");
  });

  it("returns green for good scores (60-79)", () => {
    expect(getHealthScoreColor(60)).toBe("text-green-600 bg-green-50");
    expect(getHealthScoreColor(70)).toBe("text-green-600 bg-green-50");
    expect(getHealthScoreColor(79)).toBe("text-green-600 bg-green-50");
  });

  it("returns yellow for moderate scores (40-59)", () => {
    expect(getHealthScoreColor(40)).toBe("text-yellow-600 bg-yellow-100");
    expect(getHealthScoreColor(50)).toBe("text-yellow-600 bg-yellow-100");
    expect(getHealthScoreColor(59)).toBe("text-yellow-600 bg-yellow-100");
  });

  it("returns orange for poor scores (20-39)", () => {
    expect(getHealthScoreColor(20)).toBe("text-orange-600 bg-orange-100");
    expect(getHealthScoreColor(30)).toBe("text-orange-600 bg-orange-100");
    expect(getHealthScoreColor(39)).toBe("text-orange-600 bg-orange-100");
  });

  it("returns red for critical scores (< 20)", () => {
    expect(getHealthScoreColor(0)).toBe("text-red-600 bg-red-100");
    expect(getHealthScoreColor(10)).toBe("text-red-600 bg-red-100");
    expect(getHealthScoreColor(19)).toBe("text-red-600 bg-red-100");
  });

  it("handles boundary values exactly at thresholds", () => {
    expect(getHealthScoreColor(80)).toBe("text-green-700 bg-green-100");
    expect(getHealthScoreColor(60)).toBe("text-green-600 bg-green-50");
    expect(getHealthScoreColor(40)).toBe("text-yellow-600 bg-yellow-100");
    expect(getHealthScoreColor(20)).toBe("text-orange-600 bg-orange-100");
  });
});

describe("getSeverityColor", () => {
  it("returns correct color for each severity level", () => {
    expect(getSeverityColor("low")).toBe("text-green-600 bg-green-100");
    expect(getSeverityColor("medium")).toBe("text-yellow-600 bg-yellow-100");
    expect(getSeverityColor("high")).toBe("text-orange-600 bg-orange-100");
    expect(getSeverityColor("critical")).toBe("text-red-600 bg-red-100");
  });

  it("returns gray for unknown severity", () => {
    expect(getSeverityColor("unknown")).toBe("text-gray-600 bg-gray-100");
    expect(getSeverityColor("")).toBe("text-gray-600 bg-gray-100");
  });
});

describe("getStatusColor", () => {
  it("returns correct color for each status", () => {
    expect(getStatusColor("pending")).toBe("text-yellow-600 bg-yellow-100");
    expect(getStatusColor("confirmed")).toBe("text-blue-600 bg-blue-100");
    expect(getStatusColor("rejected")).toBe("text-gray-600 bg-gray-100");
    expect(getStatusColor("treated")).toBe("text-green-600 bg-green-100");
    expect(getStatusColor("active")).toBe("text-green-600 bg-green-100");
    expect(getStatusColor("inactive")).toBe("text-red-600 bg-red-100");
  });

  it("returns gray for unknown status", () => {
    expect(getStatusColor("unknown")).toBe("text-gray-600 bg-gray-100");
  });
});

describe("getSeverityLabel", () => {
  it("returns Arabic labels by default", () => {
    expect(getSeverityLabel("low")).toBe("منخفض");
    expect(getSeverityLabel("medium")).toBe("متوسط");
    expect(getSeverityLabel("high")).toBe("مرتفع");
    expect(getSeverityLabel("critical")).toBe("حرج");
  });

  it("returns English labels when locale is en", () => {
    expect(getSeverityLabel("low", "en")).toBe("Low");
    expect(getSeverityLabel("medium", "en")).toBe("Medium");
    expect(getSeverityLabel("high", "en")).toBe("High");
    expect(getSeverityLabel("critical", "en")).toBe("Critical");
  });

  it("returns raw severity for unknown values", () => {
    expect(getSeverityLabel("unknown")).toBe("unknown");
  });
});

describe("getStatusLabel", () => {
  it("returns Arabic labels by default", () => {
    expect(getStatusLabel("pending")).toBe("قيد المراجعة");
    expect(getStatusLabel("confirmed")).toBe("مؤكد");
    expect(getStatusLabel("rejected")).toBe("مرفوض");
    expect(getStatusLabel("treated")).toBe("تم العلاج");
    expect(getStatusLabel("active")).toBe("نشط");
    expect(getStatusLabel("inactive")).toBe("غير نشط");
  });

  it("returns English labels when locale is en", () => {
    expect(getStatusLabel("pending", "en")).toBe("Pending");
    expect(getStatusLabel("confirmed", "en")).toBe("Confirmed");
    expect(getStatusLabel("rejected", "en")).toBe("Rejected");
    expect(getStatusLabel("treated", "en")).toBe("Treated");
    expect(getStatusLabel("active", "en")).toBe("Active");
    expect(getStatusLabel("inactive", "en")).toBe("Inactive");
  });

  it("returns raw status for unknown values", () => {
    expect(getStatusLabel("unknown")).toBe("unknown");
  });
});

describe("formatDate", () => {
  it("formats dates in Arabic locale by default", () => {
    const result = formatDate("2025-06-15");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("formats dates in English locale", () => {
    const result = formatDate("2025-06-15", "en");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("accepts Date objects", () => {
    const result = formatDate(new Date(2025, 5, 15));
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });
});

describe("formatNumber", () => {
  it("formats numbers in Arabic locale by default", () => {
    const result = formatNumber(1234);
    expect(typeof result).toBe("string");
  });

  it("formats numbers in English locale", () => {
    const result = formatNumber(1234, "en");
    expect(result).toBe("1,234");
  });

  it("handles zero", () => {
    expect(typeof formatNumber(0)).toBe("string");
  });
});

describe("formatArea", () => {
  it("formats area with Arabic unit by default", () => {
    const result = formatArea(10.5);
    expect(result).toContain("هكتار");
  });

  it("formats area with English unit", () => {
    const result = formatArea(10.5, "en");
    expect(result).toContain("ha");
    expect(result).toContain("10.5");
  });
});
