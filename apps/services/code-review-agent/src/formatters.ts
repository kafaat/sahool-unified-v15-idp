/**
 * Report formatters for code review results.
 *
 * Extracted from production-agent.ts so that each formatter can be
 * unit-tested directly and reused without pulling in the SDK.
 */

import type { ContentBlock, ReviewResult } from "./types.js";

/**
 * Returns a short human-readable summary of a tool-use block, used in
 * progress output while the agent is running.
 */
export function getToolSummary(block: ContentBlock): string {
  if (!("input" in block) || !block.input) return "";

  const input = block.input as Record<string, unknown>;
  switch (block.name) {
    case "Read":
      return String(input.file_path || "file");
    case "Glob":
      return String(input.pattern || "pattern");
    case "Grep":
      return `"${input.pattern}" in ${input.path || "."}`;
    default:
      return "";
  }
}

/**
 * Renders a 10-segment ASCII progress bar for a 0-100 score.
 */
export function getScoreBar(score: number): string {
  const clamped = Math.max(0, Math.min(100, score));
  const filled = Math.round(clamped / 10);
  const empty = 10 - filled;
  return `[${"#".repeat(filled)}${"-".repeat(empty)}]`;
}

/**
 * Maps our severity levels to the SARIF `level` enumeration.
 */
export function mapSeverityToSarif(
  severity: string,
): "error" | "warning" | "note" | "none" {
  switch (severity) {
    case "critical":
    case "high":
      return "error";
    case "medium":
      return "warning";
    case "low":
      return "note";
    default:
      return "none";
  }
}

/**
 * Generates a Markdown report.
 */
export function generateMarkdownReport(result: ReviewResult): string {
  const lines: string[] = [
    "# Code Review Report",
    "",
    `**Score:** ${result.overallScore}/100`,
    `**Issues Found:** ${result.issues.length}`,
    "",
    "## Summary",
    "",
    result.summary,
    "",
    "## Issues",
    "",
  ];

  const groups = {
    critical: result.issues.filter((i) => i.severity === "critical"),
    high: result.issues.filter((i) => i.severity === "high"),
    medium: result.issues.filter((i) => i.severity === "medium"),
    low: result.issues.filter((i) => i.severity === "low"),
  };

  for (const [severity, issues] of Object.entries(groups)) {
    if (issues.length === 0) continue;

    lines.push(
      `### ${severity.charAt(0).toUpperCase() + severity.slice(1)} (${issues.length})`,
    );
    lines.push("");

    for (const issue of issues) {
      const location = issue.line ? `${issue.file}:${issue.line}` : issue.file;
      lines.push(`- **[${issue.category}]** \`${location}\``);
      lines.push(`  - ${issue.description}`);
      if (issue.suggestion) {
        lines.push(`  - *Suggestion:* ${issue.suggestion}`);
      }
      lines.push("");
    }
  }

  return lines.join("\n");
}

/**
 * Generates a SARIF 2.1.0 report suitable for GitHub Code Scanning.
 */
export function generateSarifReport(result: ReviewResult): string {
  const sarif = {
    $schema: "https://json.schemastore.org/sarif-2.1.0.json",
    version: "2.1.0",
    runs: [
      {
        tool: {
          driver: {
            name: "SAHOOL Code Review Agent",
            version: "1.0.0",
            informationUri: "https://sahool.app/code-review",
            rules: [
              {
                id: "bug",
                name: "Bug",
                shortDescription: { text: "Potential bug or logic error" },
              },
              {
                id: "security",
                name: "Security",
                shortDescription: { text: "Security vulnerability" },
              },
              {
                id: "performance",
                name: "Performance",
                shortDescription: { text: "Performance issue" },
              },
              {
                id: "style",
                name: "Style",
                shortDescription: { text: "Code style or quality issue" },
              },
            ],
          },
        },
        results: result.issues.map((issue) => ({
          ruleId: issue.category,
          level: mapSeverityToSarif(issue.severity),
          message: { text: issue.description },
          locations: [
            {
              physicalLocation: {
                artifactLocation: { uri: issue.file },
                region: issue.line ? { startLine: issue.line } : undefined,
              },
            },
          ],
          fixes: issue.suggestion
            ? [
                {
                  description: { text: issue.suggestion },
                },
              ]
            : undefined,
        })),
      },
    ],
  };

  return JSON.stringify(sarif, null, 2);
}
