/**
 * Page Smoke Tests - File Existence & Structure Verification
 * اختبارات التدخين - التحقق من وجود وبنية صفحات التطبيق
 *
 * Verifies all page modules exist as valid files and export default components.
 * Uses filesystem checks for fast, reliable smoke testing.
 */

import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

const APP_DIR = path.resolve(__dirname, "..");

/**
 * Validate that a resolved path stays within the base directory.
 * Prevents path traversal (e.g., via "../" segments).
 */
function safePath(base: string, relative: string): string {
  const resolved = path.resolve(base, relative);
  if (!resolved.startsWith(base + path.sep) && resolved !== base) {
    throw new Error(`Path traversal detected: ${relative}`);
  }
  return resolved;
}

/**
 * Helper: check that a page file exists and contains a default export
 */
function verifyPageFile(relativePath: string) {
  // Try .tsx then .ts extensions
  const tsxPath = safePath(APP_DIR, relativePath + ".tsx");
  const tsPath = safePath(APP_DIR, relativePath + ".ts");

  const filePath = fs.existsSync(tsxPath)
    ? tsxPath
    : fs.existsSync(tsPath)
      ? tsPath
      : null;

  expect(filePath, `Page file not found: ${relativePath}`).not.toBeNull();

  const content = fs.readFileSync(filePath!, "utf-8");
  // Check for default export (function, const, or export default)
  const hasDefaultExport =
    /export\s+default\s+/.test(content) ||
    /export\s*\{\s*default\s*\}/.test(content);

  expect(
    hasDefaultExport,
    `No default export found in ${relativePath}`,
  ).toBe(true);

  return content;
}

describe("Page Module Existence - Smoke Tests", () => {
  // Auth pages
  it("has login page", () => {
    verifyPageFile("(auth)/login/page");
  });

  it("has register page", () => {
    verifyPageFile("(auth)/register/page");
  });

  it("has forgot-password page", () => {
    verifyPageFile("(auth)/forgot-password/page");
  });

  it("has verify-otp page", () => {
    verifyPageFile("(auth)/verify-otp/page");
  });

  it("has reset-password page", () => {
    verifyPageFile("(auth)/reset-password/page");
  });

  // Dashboard
  it("has dashboard page", () => {
    verifyPageFile("dashboard/page");
  });

  // Operations
  it("has farms page", () => {
    verifyPageFile("farms/page");
  });

  it("has diseases page", () => {
    verifyPageFile("diseases/page");
  });

  it("has irrigation page", () => {
    verifyPageFile("irrigation/page");
  });

  it("has tasks page", () => {
    verifyPageFile("tasks/page");
  });

  // Monitoring
  it("has sensors page", () => {
    verifyPageFile("sensors/page");
  });

  it("has alerts page", () => {
    verifyPageFile("alerts/page");
  });

  it("has epidemic page", () => {
    verifyPageFile("epidemic/page");
  });

  it("has yield page", () => {
    verifyPageFile("yield/page");
  });

  // Management
  it("has users page", () => {
    verifyPageFile("users/page");
  });

  it("has equipment page", () => {
    verifyPageFile("equipment/page");
  });

  it("has inventory page", () => {
    verifyPageFile("inventory/page");
  });

  it("has marketplace page", () => {
    verifyPageFile("marketplace/page");
  });

  it("has research page", () => {
    verifyPageFile("research/page");
  });

  // System
  it("has settings page", () => {
    verifyPageFile("settings/page");
  });

  it("has support page", () => {
    verifyPageFile("support/page");
  });

  // Additional features
  it("has community page", () => {
    verifyPageFile("community/page");
  });

  it("has compliance page", () => {
    verifyPageFile("compliance/page");
  });

  it("has copilot page", () => {
    verifyPageFile("copilot/page");
  });

  it("has crop-health page", () => {
    verifyPageFile("crop-health/page");
  });

  it("has disasters page", () => {
    verifyPageFile("disasters/page");
  });

  it("has lab page", () => {
    verifyPageFile("lab/page");
  });

  it("has logistics page", () => {
    verifyPageFile("logistics/page");
  });

  // Error/Not found pages
  it("has error page", () => {
    verifyPageFile("error");
  });

  it("has not-found page", () => {
    verifyPageFile("not-found");
  });

  it("has global-error page", () => {
    verifyPageFile("global-error");
  });

  // Precision agriculture
  it("has VRA page", () => {
    verifyPageFile("precision-agriculture/vra/page");
  });

  it("has GDD page", () => {
    verifyPageFile("precision-agriculture/gdd/page");
  });

  it("has spray page", () => {
    verifyPageFile("precision-agriculture/spray/page");
  });

  it("has pivot page", () => {
    verifyPageFile("precision-agriculture/pivot/page");
  });

  // Analytics
  it("has profitability page", () => {
    verifyPageFile("analytics/profitability/page");
  });

  it("has satellite analytics page", () => {
    verifyPageFile("analytics/satellite/page");
  });
});

describe("Loading Page Existence", () => {
  it("has root loading module", () => {
    verifyPageFile("loading");
  });

  it("has dashboard loading module", () => {
    verifyPageFile("dashboard/loading");
  });

  it("has alerts loading module", () => {
    verifyPageFile("alerts/loading");
  });
});

describe("Layout File Existence", () => {
  it("has root layout", () => {
    verifyPageFile("layout");
  });

  it("has auth layout", () => {
    verifyPageFile("(auth)/layout");
  });
});

describe("Page Structure Validation", () => {
  /**
   * Recursively find page files within APP_DIR.
   * Validates each resolved path stays within APP_DIR to prevent traversal.
   */
  function findPages(dir: string): string[] {
    const results: string[] = [];
    const resolvedDir = path.resolve(dir);
    if (!resolvedDir.startsWith(APP_DIR)) return results;

    const entries = fs.readdirSync(resolvedDir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.resolve(resolvedDir, entry.name);
      if (!fullPath.startsWith(APP_DIR)) continue;

      if (entry.isDirectory() && entry.name !== "__tests__" && entry.name !== "node_modules") {
        results.push(...findPages(fullPath));
      } else if (entry.name === "page.tsx" || entry.name === "page.ts") {
        results.push(fullPath);
      }
    }
    return results;
  }

  it("all pages use React component pattern", () => {
    const pageFiles = findPages(APP_DIR);

    expect(pageFiles.length).toBeGreaterThanOrEqual(30);

    for (const file of pageFiles) {
      const content = fs.readFileSync(file, "utf-8");
      const hasDefaultExport =
        /export\s+default\s+/.test(content) ||
        /export\s*\{\s*default\s*\}/.test(content);
      const relativePath = path.relative(APP_DIR, file);
      expect(
        hasDefaultExport,
        `Missing default export in ${relativePath}`,
      ).toBe(true);
    }
  });

  it("no page file exceeds 2000 lines", () => {
    const pageFiles = findPages(APP_DIR);

    for (const file of pageFiles) {
      const content = fs.readFileSync(file, "utf-8");
      const lineCount = content.split("\n").length;
      const relativePath = path.relative(APP_DIR, file);
      expect(
        lineCount,
        `${relativePath} has ${lineCount} lines (max 2000)`,
      ).toBeLessThanOrEqual(2000);
    }
  });
});
