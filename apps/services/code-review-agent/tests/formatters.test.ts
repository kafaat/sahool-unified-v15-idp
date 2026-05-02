import { describe, expect, it } from "vitest";
import {
  generateMarkdownReport,
  generateSarifReport,
  getScoreBar,
  getToolSummary,
  mapSeverityToSarif,
} from "../src/formatters.js";
import type { ContentBlock, ReviewResult } from "../src/types.js";

describe("formatters", () => {
  it("summarizes common tool-use blocks", () => {
    const readBlock: ContentBlock = {
      type: "tool_use",
      id: "tool-1",
      name: "Read",
      input: { file_path: "src/main.ts" },
    };
    const grepBlock: ContentBlock = {
      type: "tool_use",
      id: "tool-2",
      name: "Grep",
      input: { pattern: "tenantId", path: "apps/services" },
    };

    expect(getToolSummary(readBlock)).toBe("src/main.ts");
    expect(getToolSummary(grepBlock)).toBe("\"tenantId\" in apps/services");
  });

  it("clamps score bars to the supported 0-100 range", () => {
    expect(getScoreBar(-5)).toBe("[----------]");
    expect(getScoreBar(46)).toBe("[#####-----]");
    expect(getScoreBar(150)).toBe("[##########]");
  });

  it("maps internal severities to SARIF levels", () => {
    expect(mapSeverityToSarif("critical")).toBe("error");
    expect(mapSeverityToSarif("high")).toBe("error");
    expect(mapSeverityToSarif("medium")).toBe("warning");
    expect(mapSeverityToSarif("low")).toBe("note");
    expect(mapSeverityToSarif("unknown")).toBe("none");
  });

  it("renders Markdown and SARIF reports", () => {
    const result: ReviewResult = {
      overallScore: 82,
      summary: "No critical findings.",
      issues: [
        {
          severity: "high",
          category: "security",
          file: "src/auth.ts",
          line: 42,
          description: "Missing tenant scope.",
          suggestion: "Filter by tenantId.",
        },
      ],
    };

    const markdown = generateMarkdownReport(result);
    expect(markdown).toContain("# Code Review Report");
    expect(markdown).toContain("### High (1)");
    expect(markdown).toContain("src/auth.ts:42");

    const sarif = JSON.parse(generateSarifReport(result));
    expect(sarif.version).toBe("2.1.0");
    expect(sarif.runs[0].results[0]).toMatchObject({
      ruleId: "security",
      level: "error",
      message: { text: "Missing tenant scope." },
    });
  });
});
