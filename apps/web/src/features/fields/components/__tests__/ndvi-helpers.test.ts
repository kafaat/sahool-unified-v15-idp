import { describe, it, expect } from "vitest";
import {
  getNDVIColor,
  getNDVIBorderColor,
  getHealthStatusArabic,
  isValidBoundary,
} from "../HealthZonesLayer";
import {
  getNDVIColor as getFieldNDVIColor,
  getHealthLabel,
} from "../FieldMap";

// ─────────────────────────────────────────────────────────────────────────
// HealthZonesLayer helpers
// ─────────────────────────────────────────────────────────────────────────

describe("HealthZonesLayer getNDVIColor", () => {
  it("returns dark green for excellent NDVI (>= 0.7)", () => {
    expect(getNDVIColor(0.7)).toBe("#1B5E20");
    expect(getNDVIColor(0.85)).toBe("#1B5E20");
    expect(getNDVIColor(1.0)).toBe("#1B5E20");
  });

  it("returns green for good NDVI (0.5 - 0.7)", () => {
    expect(getNDVIColor(0.5)).toBe("#4CAF50");
    expect(getNDVIColor(0.6)).toBe("#4CAF50");
    expect(getNDVIColor(0.69)).toBe("#4CAF50");
  });

  it("returns yellow for moderate NDVI (0.3 - 0.5)", () => {
    expect(getNDVIColor(0.3)).toBe("#FDD835");
    expect(getNDVIColor(0.4)).toBe("#FDD835");
    expect(getNDVIColor(0.49)).toBe("#FDD835");
  });

  it("returns orange for poor NDVI (0.15 - 0.3)", () => {
    expect(getNDVIColor(0.15)).toBe("#FF9800");
    expect(getNDVIColor(0.2)).toBe("#FF9800");
    expect(getNDVIColor(0.29)).toBe("#FF9800");
  });

  it("returns red for critical NDVI (< 0.15)", () => {
    expect(getNDVIColor(0.0)).toBe("#F44336");
    expect(getNDVIColor(0.1)).toBe("#F44336");
    expect(getNDVIColor(0.14)).toBe("#F44336");
  });

  it("handles negative NDVI values", () => {
    expect(getNDVIColor(-1.0)).toBe("#F44336");
  });
});

describe("HealthZonesLayer getNDVIBorderColor", () => {
  it("returns darker green for excellent NDVI (>= 0.7)", () => {
    expect(getNDVIBorderColor(0.7)).toBe("#0D3311");
    expect(getNDVIBorderColor(0.9)).toBe("#0D3311");
  });

  it("returns dark green for good NDVI (0.5 - 0.7)", () => {
    expect(getNDVIBorderColor(0.5)).toBe("#2E7D32");
    expect(getNDVIBorderColor(0.6)).toBe("#2E7D32");
  });

  it("returns dark yellow for moderate NDVI (0.3 - 0.5)", () => {
    expect(getNDVIBorderColor(0.3)).toBe("#F9A825");
    expect(getNDVIBorderColor(0.4)).toBe("#F9A825");
  });

  it("returns dark orange for poor NDVI (0.15 - 0.3)", () => {
    expect(getNDVIBorderColor(0.15)).toBe("#E65100");
    expect(getNDVIBorderColor(0.25)).toBe("#E65100");
  });

  it("returns dark red for critical NDVI (< 0.15)", () => {
    expect(getNDVIBorderColor(0.0)).toBe("#C62828");
    expect(getNDVIBorderColor(0.1)).toBe("#C62828");
  });
});

describe("HealthZonesLayer getHealthStatusArabic", () => {
  it("returns correct Arabic label for each health status", () => {
    expect(getHealthStatusArabic("excellent")).toBe("ممتازة");
    expect(getHealthStatusArabic("good")).toBe("جيدة");
    expect(getHealthStatusArabic("moderate")).toBe("متوسطة");
    expect(getHealthStatusArabic("poor")).toBe("ضعيفة");
    expect(getHealthStatusArabic("critical")).toBe("حرجة");
  });
});

describe("HealthZonesLayer isValidBoundary", () => {
  it("returns true for valid polygon boundaries (>= 3 points)", () => {
    const validBoundary: [number, number][] = [
      [15.0, 48.0],
      [15.1, 48.1],
      [15.0, 48.1],
    ];
    expect(isValidBoundary(validBoundary)).toBe(true);
  });

  it("returns false for empty or too few coordinates", () => {
    expect(isValidBoundary([])).toBe(false);
    expect(isValidBoundary([[15.0, 48.0]])).toBe(false);
    expect(
      isValidBoundary([
        [15.0, 48.0],
        [15.1, 48.1],
      ]),
    ).toBe(false);
  });

  it("returns false for null/undefined", () => {
    expect(isValidBoundary(null as any)).toBe(false);
    expect(isValidBoundary(undefined as any)).toBe(false);
  });

  it("returns false for coordinates out of valid range", () => {
    const outOfRange: [number, number][] = [
      [91, 48.0], // lat > 90
      [15.0, 48.0],
      [15.1, 48.1],
    ];
    expect(isValidBoundary(outOfRange)).toBe(false);
  });

  it("returns false for coordinates with NaN", () => {
    const withNaN: [number, number][] = [
      [NaN, 48.0],
      [15.0, 48.0],
      [15.1, 48.1],
    ];
    expect(isValidBoundary(withNaN)).toBe(false);
  });

  it("returns false for longitude out of range", () => {
    const invalidLng: [number, number][] = [
      [15.0, 181], // lng > 180
      [15.0, 48.0],
      [15.1, 48.1],
    ];
    expect(isValidBoundary(invalidLng)).toBe(false);
  });
});

// ─────────────────────────────────────────────────────────────────────────
// FieldMap helpers
// ─────────────────────────────────────────────────────────────────────────

describe("FieldMap getNDVIColor", () => {
  it("returns gray for undefined/null NDVI", () => {
    expect(getFieldNDVIColor(undefined)).toBe("#9ca3af");
    expect(getFieldNDVIColor(null as any)).toBe("#9ca3af");
  });

  it("returns dark green for excellent NDVI (>= 0.7)", () => {
    expect(getFieldNDVIColor(0.7)).toBe("#1B5E20");
    expect(getFieldNDVIColor(0.85)).toBe("#1B5E20");
  });

  it("returns green for good NDVI (0.5 - 0.7)", () => {
    expect(getFieldNDVIColor(0.5)).toBe("#4CAF50");
    expect(getFieldNDVIColor(0.6)).toBe("#4CAF50");
  });

  it("returns yellow for moderate NDVI (0.3 - 0.5)", () => {
    expect(getFieldNDVIColor(0.3)).toBe("#FDD835");
    expect(getFieldNDVIColor(0.4)).toBe("#FDD835");
  });

  it("returns orange for poor NDVI (0.15 - 0.3)", () => {
    expect(getFieldNDVIColor(0.15)).toBe("#FF9800");
    expect(getFieldNDVIColor(0.2)).toBe("#FF9800");
  });

  it("returns red for critical NDVI (< 0.15)", () => {
    expect(getFieldNDVIColor(0.0)).toBe("#F44336");
    expect(getFieldNDVIColor(0.1)).toBe("#F44336");
  });
});

describe("FieldMap getHealthLabel", () => {
  it("returns غير معروف for undefined/null NDVI", () => {
    expect(getHealthLabel(undefined)).toBe("غير معروف");
    expect(getHealthLabel(null as any)).toBe("غير معروف");
  });

  it("returns ممتاز for excellent NDVI (>= 0.7)", () => {
    expect(getHealthLabel(0.7)).toBe("ممتاز");
    expect(getHealthLabel(0.9)).toBe("ممتاز");
  });

  it("returns جيد for good NDVI (0.5 - 0.7)", () => {
    expect(getHealthLabel(0.5)).toBe("جيد");
    expect(getHealthLabel(0.65)).toBe("جيد");
  });

  it("returns متوسط for moderate NDVI (0.3 - 0.5)", () => {
    expect(getHealthLabel(0.3)).toBe("متوسط");
    expect(getHealthLabel(0.45)).toBe("متوسط");
  });

  it("returns ضعيف for poor NDVI (0.15 - 0.3)", () => {
    expect(getHealthLabel(0.15)).toBe("ضعيف");
    expect(getHealthLabel(0.25)).toBe("ضعيف");
  });

  it("returns حرج for critical NDVI (< 0.15)", () => {
    expect(getHealthLabel(0.0)).toBe("حرج");
    expect(getHealthLabel(0.1)).toBe("حرج");
  });
});

// ─────────────────────────────────────────────────────────────────────────
// Cross-component consistency checks
// ─────────────────────────────────────────────────────────────────────────

describe("Cross-component NDVI color consistency", () => {
  const testValues = [0.0, 0.1, 0.15, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0];

  it("HealthZonesLayer and FieldMap return the same colors for the same NDVI values", () => {
    for (const value of testValues) {
      expect(getNDVIColor(value)).toBe(
        getFieldNDVIColor(value),
      );
    }
  });
});
