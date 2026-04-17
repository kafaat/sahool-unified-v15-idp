/**
 * Unit tests for src/formatters.ts.
 */

import { describe, expect, it } from "vitest";
import {
  generateMarkdownReport,
  generateSarifReport,
  getScoreBar,
  getToolSummary,
  mapSeverityToSarif,
} from "../src/formatters.js";
import type { ReviewResult } from "../src/types.js";

describe("getToolSummary", () => {
  it("returns the file_path for Read", () => {
    const block = {
      type: "tool_use" as const,
      id: "1",
      name: "Read",
      input: { file_path: "src/index.ts" },
    };
    expect(getToolSummary(block)).toBe("src/index.ts");
  });

  it("falls back to 'file' when Read has no file_path", () => {
    const block = {
      type: "tool_use" as const,
      id: "1",
      name: "Read",
      input: {},
    };
    expect(getToolSummary(block)).toBe("file");
  });

  it("returns the pattern for Glob", () => {
    const block = {
      type: "tool_use" as const,
      id: "2",
      name: "Glob",
      input: { pattern: "**/*.ts" },
    };
    expect(getToolSummary(block)).toBe("**/*.ts");
  });

  it("falls back to 'pattern' when Glob has no pattern", () => {
    const block = {
      type: "tool_use" as const,
      id: "2",
      name: "Glob",
      input: {},
    };
    expect(getToolSummary(block)).toBe("pattern");
  });

  it("formats Grep as \"pattern\" in path", () => {
    const block = {
      type: "tool_use" as const,
      id: "3",
      name: "Grep",
      input: { pattern: "TODO", path: "src" },
    };
    expect(getToolSummary(block)).toBe('"TODO" in src');
  });

  it("defaults Grep path to '.'", () => {
    const block = {
      type: "tool_use" as const,
      id: "3",
      name: "Grep",
      input: { pattern: "TODO" },
    };
    expect(getToolSummary(block)).toBe('"TODO" in .');
  });

  it("returns empty string for unknown tools", () => {
    const block = {
      type: "tool_use" as const,
      id: "4",
      name: "Unknown",
      input: { foo: "bar" },
    };
    expect(getToolSummary(block)).toBe("");
  });

  it("returns empty string for text blocks (no input)", () => {
    const block = { type: "text" as const, text: "hello" };
    expect(getToolSummary(block)).toBe("");
  });
});

describe("getScoreBar", () => {
  it("renders a full bar for score 100", () => {
    expect(getScoreBar(100)).toBe("[##########]");
  });

  it("renders an empty bar for score 0", () => {
    expect(getScoreBar(0)).toBe("[----------]");
  });

  it("renders a half bar for score 50", () => {
    expect(getScoreBar(50)).toBe("[#####-----]");
  });

  it("clamps scores above 100", () => {
    expect(getScoreBar(150)).toBe("[##########]");
  });

  it("clamps negative scores to 0", () => {
    expect(getScoreBar(-10)).toBe("[----------]");
  });

  it("produces a 12-character string (incl. brackets)", () => {
    expect(getScoreBar(42)).toHaveLength(12);
  });
});

describe("mapSeverityToSarif", () => {
  it("maps critical to error", () => {
    expect(mapSeverityToSarif("critical")).toBe("error");
  });

  it("maps high to error", () => {
    expect(mapSeverityToSarif("high")).toBe("error");
  });

  it("maps medium to warning", () => {
    expect(mapSeverityToSarif("medium")).toBe("warning");
  });

  it("maps low to note", () => {
    expect(mapSeverityToSarif("low")).toBe("note");
  });

  it("maps unknown severities to none", () => {
    expect(mapSeverityToSarif("totally-unknown")).toBe("none");
  });
});

describe("generateMarkdownReport", () => {
  const sample: ReviewResult = {
    issues: [
      {
        severity: "high",
        category: "security",
        file: "src/auth.ts",
        line: 42,
        description: "Hardcoded API key",
        suggestion: "Use env vars",
      },
      {
        severity: "low",
        category: "style",
        file: "src/util.ts",
        description: "Unused variable",
      },
    ],
    summary: "Two issues total",
    overallScore: 72,
  };

  it("includes the score and issue count", () => {
    const md = generateMarkdownReport(sample);
    expect(md).toContain("**Score:** 72/100");
    expect(md).toContain("**Issues Found:** 2");
  });

  it("includes a summary section", () => {
    expect(generateMarkdownReport(sample)).toContain("Two issues total");
  });

  it("includes severity headings with counts", () => {
    const md = generateMarkdownReport(sample);
    expect(md).toContain("### High (1)");
    expect(md).toContain("### Low (1)");
  });

  it("omits empty severity groups", () => {
    const md = generateMarkdownReport(sample);
    expect(md).not.toContain("### Critical");
    expect(md).not.toContain("### Medium");
  });

  it("renders file:line locations when line is present", () => {
    expect(generateMarkdownReport(sample)).toContain("`src/auth.ts:42`");
  });
});

describe("generateSarifReport", () => {
  const sample: ReviewResult = {
    issues: [
      {
        severity: "critical",
        category: "security",
        file: "src/auth.ts",
        line: 10,
        description: "SQL injection",
        suggestion: "Parameterize query",
      },
    ],
    summary: "One critical issue",
    overallScore: 40,
  };

  it("emits a SARIF 2.1.0 envelope", () => {
    const parsed = JSON.parse(generateSarifReport(sample));
    expect(parsed.version).toBe("2.1.0");
    expect(parsed.$schema).toContain("sarif-2.1.0");
    expect(parsed.runs).toHaveLength(1);
  });

  it("declares the 4 rule categories in tool.driver.rules", () => {
    const parsed = JSON.parse(generateSarifReport(sample));
    const ruleIds = parsed.runs[0].tool.driver.rules.map(
      (r: { id: string }) => r.id,
    );
    expect(ruleIds).toEqual(
      expect.arrayContaining(["bug", "security", "performance", "style"]),
    );
  });

  it("maps each issue to a result with physicalLocation", () => {
    const parsed = JSON.parse(generateSarifReport(sample));
    expect(parsed.runs[0].results).toHaveLength(1);
    const r = parsed.runs[0].results[0];
    expect(r.ruleId).toBe("security");
    expect(r.level).toBe("error"); // critical -> error
    expect(r.locations[0].physicalLocation.artifactLocation.uri).toBe(
      "src/auth.ts",
    );
    expect(r.locations[0].physicalLocation.region.startLine).toBe(10);
  });

  it("includes fix descriptions when suggestion is present", () => {
    const parsed = JSON.parse(generateSarifReport(sample));
    expect(parsed.runs[0].results[0].fixes[0].description.text).toBe(
      "Parameterize query",
    );
  });

  it("omits the region when line is absent", () => {
    const noLine: ReviewResult = {
      issues: [
        {
          severity: "low",
          category: "style",
          file: "src/x.ts",
          description: "meh",
        },
      ],
      summary: "s",
      overallScore: 99,
    };
    const parsed = JSON.parse(generateSarifReport(noLine));
    expect(
      parsed.runs[0].results[0].locations[0].physicalLocation.region,
    ).toBeUndefined();
  });
});
