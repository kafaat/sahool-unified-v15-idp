/**
 * Export Tests for Code Review Agent
 *
 * Tests that all exports are properly defined and accessible.
 */

import { describe, it, expect } from "vitest";
import {
  runCodeReview,
  printResults,
  exportResults,
  reviewSchema,
  type ReviewResult,
  type ReviewIssue,
  type ReviewAgentConfig
} from "../src/index.js";

describe("Exports", () => {
  describe("Functions", () => {
    it("should export runCodeReview function", () => {
      expect(runCodeReview).toBeDefined();
      expect(typeof runCodeReview).toBe("function");
    });

    it("should export printResults function", () => {
      expect(printResults).toBeDefined();
      expect(typeof printResults).toBe("function");
    });

    it("should export exportResults function", () => {
      expect(exportResults).toBeDefined();
      expect(typeof exportResults).toBe("function");
    });
  });

  describe("Schema", () => {
    it("should export reviewSchema", () => {
      expect(reviewSchema).toBeDefined();
      expect(reviewSchema.type).toBe("object");
    });
  });

  describe("exportResults", () => {
    const mockResult: ReviewResult = {
      issues: [
        {
          severity: "high",
          category: "security",
          file: "test.ts",
          line: 10,
          description: "Test issue",
          suggestion: "Fix it"
        }
      ],
      summary: "Test summary",
      overallScore: 80
    };

    it("should export as JSON", () => {
      const json = exportResults(mockResult, "json");
      const parsed = JSON.parse(json);
      expect(parsed.issues).toHaveLength(1);
      expect(parsed.overallScore).toBe(80);
    });

    it("should export as Markdown", () => {
      const markdown = exportResults(mockResult, "markdown");
      expect(markdown).toContain("# Code Review Report");
      expect(markdown).toContain("**Score:** 80/100");
      expect(markdown).toContain("Test issue");
    });

    it("should export as SARIF", () => {
      const sarif = exportResults(mockResult, "sarif");
      const parsed = JSON.parse(sarif);
      expect(parsed.$schema).toContain("sarif");
      expect(parsed.version).toBe("2.1.0");
      expect(parsed.runs).toHaveLength(1);
      expect(parsed.runs[0].results).toHaveLength(1);
    });
  });

  describe("printResults", () => {
    it("should not throw for valid result", () => {
      const result: ReviewResult = {
        issues: [],
        summary: "No issues",
        overallScore: 100
      };

      expect(() => printResults(result)).not.toThrow();
    });

    it("should handle results with all severity levels", () => {
      const result: ReviewResult = {
        issues: [
          { severity: "critical", category: "security", file: "a.ts", description: "Critical" },
          { severity: "high", category: "bug", file: "b.ts", description: "High" },
          { severity: "medium", category: "performance", file: "c.ts", description: "Medium" },
          { severity: "low", category: "style", file: "d.ts", description: "Low" }
        ],
        summary: "Mixed issues",
        overallScore: 50
      };

      expect(() => printResults(result)).not.toThrow();
    });
  });
});
