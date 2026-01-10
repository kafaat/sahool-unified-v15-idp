/**
 * Type Tests for Code Review Agent
 *
 * Tests type definitions and JSON schema validation.
 */

import { describe, it, expect } from "vitest";
import {
  reviewSchema,
  type ReviewResult,
  type ReviewIssue,
  type IssueSeverity,
  type IssueCategory
} from "../src/types.js";

describe("Types", () => {
  describe("IssueSeverity", () => {
    it("should accept valid severity levels", () => {
      const severities: IssueSeverity[] = ["low", "medium", "high", "critical"];
      expect(severities).toHaveLength(4);
    });
  });

  describe("IssueCategory", () => {
    it("should accept valid categories", () => {
      const categories: IssueCategory[] = ["bug", "security", "performance", "style"];
      expect(categories).toHaveLength(4);
    });
  });

  describe("ReviewIssue", () => {
    it("should create a valid issue with required fields", () => {
      const issue: ReviewIssue = {
        severity: "high",
        category: "security",
        file: "src/auth.ts",
        description: "SQL injection vulnerability"
      };

      expect(issue.severity).toBe("high");
      expect(issue.category).toBe("security");
      expect(issue.file).toBe("src/auth.ts");
      expect(issue.description).toBe("SQL injection vulnerability");
    });

    it("should create a valid issue with optional fields", () => {
      const issue: ReviewIssue = {
        severity: "medium",
        category: "bug",
        file: "src/utils.ts",
        line: 42,
        description: "Off-by-one error in loop",
        suggestion: "Change <= to <"
      };

      expect(issue.line).toBe(42);
      expect(issue.suggestion).toBe("Change <= to <");
    });
  });

  describe("ReviewResult", () => {
    it("should create a valid review result", () => {
      const result: ReviewResult = {
        issues: [
          {
            severity: "critical",
            category: "security",
            file: "src/auth.ts",
            line: 10,
            description: "Hardcoded API key",
            suggestion: "Use environment variables"
          },
          {
            severity: "low",
            category: "style",
            file: "src/utils.ts",
            description: "Unused variable"
          }
        ],
        summary: "Found 2 issues in the codebase",
        overallScore: 75
      };

      expect(result.issues).toHaveLength(2);
      expect(result.summary).toBe("Found 2 issues in the codebase");
      expect(result.overallScore).toBe(75);
    });

    it("should handle empty issues array", () => {
      const result: ReviewResult = {
        issues: [],
        summary: "No issues found",
        overallScore: 100
      };

      expect(result.issues).toHaveLength(0);
      expect(result.overallScore).toBe(100);
    });
  });

  describe("reviewSchema", () => {
    it("should have correct structure", () => {
      expect(reviewSchema.type).toBe("object");
      expect(reviewSchema.properties).toBeDefined();
      expect(reviewSchema.required).toContain("issues");
      expect(reviewSchema.required).toContain("summary");
      expect(reviewSchema.required).toContain("overallScore");
    });

    it("should have issues array schema", () => {
      const issuesSchema = reviewSchema.properties.issues;
      expect(issuesSchema.type).toBe("array");
      expect(issuesSchema.items.type).toBe("object");
    });

    it("should have correct severity enum", () => {
      const severitySchema = reviewSchema.properties.issues.items.properties.severity;
      expect(severitySchema.enum).toContain("low");
      expect(severitySchema.enum).toContain("medium");
      expect(severitySchema.enum).toContain("high");
      expect(severitySchema.enum).toContain("critical");
    });

    it("should have correct category enum", () => {
      const categorySchema = reviewSchema.properties.issues.items.properties.category;
      expect(categorySchema.enum).toContain("bug");
      expect(categorySchema.enum).toContain("security");
      expect(categorySchema.enum).toContain("performance");
      expect(categorySchema.enum).toContain("style");
    });
  });
});
