/**
 * Structured Code Review Agent
 *
 * Returns structured JSON output for programmatic consumption.
 * Uses JSON Schema to ensure consistent, parseable results.
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import { reviewSchema, type ReviewResult, type ContentBlock } from "./types.js";

/**
 * Reviews code and returns structured results
 *
 * @param directory - Path to the directory to review
 * @returns ReviewResult with structured issue data
 */
async function reviewCodeStructured(
  directory: string,
): Promise<ReviewResult | null> {
  console.log(`\n${"=".repeat(50)}`);
  console.log(`Structured Code Review Agent`);
  console.log(`Directory: ${directory}`);
  console.log(`${"=".repeat(50)}\n`);

  let result: ReviewResult | null = null;

  for await (const message of query({
    prompt: `Review the code in ${directory}. Identify all issues including:
- Bugs and potential crashes
- Security vulnerabilities (SQL injection, XSS, CSRF, etc.)
- Performance issues
- Code quality and maintainability problems

Provide specific file paths and line numbers where possible.`,
    options: {
      model: "opus",
      allowedTools: ["Read", "Glob", "Grep"],
      permissionMode: "bypassPermissions",
      maxTurns: 250,
      outputFormat: {
        type: "json_schema",
        schema: reviewSchema,
      },
    },
  })) {
    // Progress indicator
    if (message.type === "assistant") {
      for (const block of message.message.content as ContentBlock[]) {
        if ("name" in block) {
          process.stdout.write(".");
        }
      }
    }

    // Final result
    if (message.type === "result" && message.subtype === "success") {
      result = message.structured_output as ReviewResult;
      console.log(
        `\n\nReview complete! Cost: $${message.total_cost_usd.toFixed(4)}`,
      );
    }
  }

  return result;
}

/**
 * Prints formatted review results
 */
function printResults(result: ReviewResult): void {
  console.log(`\n${"=".repeat(50)}`);
  console.log(`REVIEW RESULTS`);
  console.log(`${"=".repeat(50)}\n`);

  console.log(`Score: ${result.overallScore}/100`);
  console.log(`Issues Found: ${result.issues.length}\n`);
  console.log(`Summary:\n${result.summary}\n`);

  // Group issues by severity
  const byCategory = {
    critical: result.issues.filter((i) => i.severity === "critical"),
    high: result.issues.filter((i) => i.severity === "high"),
    medium: result.issues.filter((i) => i.severity === "medium"),
    low: result.issues.filter((i) => i.severity === "low"),
  };

  for (const [severity, issues] of Object.entries(byCategory)) {
    if (issues.length === 0) continue;

    const icon =
      severity === "critical"
        ? "[CRITICAL]"
        : severity === "high"
          ? "[HIGH]"
          : severity === "medium"
            ? "[MEDIUM]"
            : "[LOW]";

    console.log(`\n${icon} ${severity.toUpperCase()} (${issues.length})`);
    console.log("-".repeat(40));

    for (const issue of issues) {
      const location = issue.line ? `${issue.file}:${issue.line}` : issue.file;
      console.log(`\n[${issue.category.toUpperCase()}] ${location}`);
      console.log(`  ${issue.description}`);
      if (issue.suggestion) {
        console.log(`  -> ${issue.suggestion}`);
      }
    }
  }

  // Export as JSON for programmatic use
  console.log(`\n${"=".repeat(50)}`);
  console.log("JSON Output:");
  console.log(JSON.stringify(result, null, 2));
}

/**
 * Main entry point
 */
async function main(): Promise<void> {
  const directory = process.argv[2] || ".";
  const result = await reviewCodeStructured(directory);

  if (result) {
    printResults(result);
  } else {
    console.error("Review failed to produce results");
    process.exit(1);
  }
}

main().catch(console.error);
