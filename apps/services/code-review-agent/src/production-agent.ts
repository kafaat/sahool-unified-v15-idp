/**
 * Production Code Review Agent
 *
 * A comprehensive, production-ready code review agent that:
 * - Analyzes code for bugs, security issues, and quality problems
 * - Uses specialized subagents for security and test analysis
 * - Provides structured JSON output for integration
 * - Includes audit logging and permission controls
 * - Tracks costs and usage
 */

import {
  query,
  type AgentDefinition,
  type HookCallback,
  type PreToolUseHookInput
} from "@anthropic-ai/claude-agent-sdk";
import {
  reviewSchema,
  type ReviewResult,
  type ContentBlock,
  type ReviewAgentConfig
} from "./types.js";

// ============================================================================
// Hooks
// ============================================================================

/**
 * Audit logging hook - logs all tool usage for compliance
 */
const auditLogger: HookCallback = async (input) => {
  if (input.hook_event_name === "PreToolUse") {
    const preInput = input as PreToolUseHookInput;
    const timestamp = new Date().toISOString();
    console.log(`[AUDIT] ${timestamp} - Tool: ${preInput.tool_name}`);
  }
  return {}; // Allow the operation
};

/**
 * Security hook - blocks dangerous commands
 */
const blockDangerousCommands: HookCallback = async (input) => {
  if (input.hook_event_name === "PreToolUse") {
    const preInput = input as PreToolUseHookInput;
    if (preInput.tool_name === "Bash") {
      const command = String((preInput.tool_input as Record<string, unknown>).command || "");
      const dangerous = ["rm -rf", "sudo", "chmod 777", "curl | sh", "wget | sh"];

      for (const pattern of dangerous) {
        if (command.includes(pattern)) {
          console.log(`[SECURITY] Blocked dangerous command: ${pattern}`);
          return {
            hookSpecificOutput: {
              hookEventName: "PreToolUse",
              permissionDecision: "deny",
              permissionDecisionReason: `Dangerous command blocked: ${pattern}`
            }
          };
        }
      }
    }
  }
  return {};
};

// ============================================================================
// Subagent Definitions
// ============================================================================

/**
 * Security specialist subagent
 */
const securityReviewer: AgentDefinition = {
  description: "Security specialist for vulnerability detection",
  prompt: `You are a security expert specializing in code vulnerability detection.

Focus your analysis on:
- SQL injection, NoSQL injection, and command injection vulnerabilities
- Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF)
- Exposed credentials, API keys, and secrets in code
- Insecure data handling and encryption weaknesses
- Authentication and authorization flaws
- Path traversal and file inclusion vulnerabilities
- Insecure deserialization
- Security misconfigurations

For each vulnerability found, provide:
1. The specific file and line number
2. The vulnerability type (OWASP category if applicable)
3. The potential impact
4. A concrete remediation suggestion

Be thorough but avoid false positives. Focus on actual security risks.`,
  tools: ["Read", "Grep", "Glob"],
  model: "sonnet"
};

/**
 * Test coverage analyzer subagent
 */
const testAnalyzer: AgentDefinition = {
  description: "Test coverage and quality analyzer",
  prompt: `You are a testing expert analyzing code test coverage and quality.

Analyze:
- Test file locations and naming conventions
- Test coverage gaps (functions/classes without tests)
- Missing edge cases and error handling tests
- Test quality and reliability issues
- Suggestions for additional tests

Look for:
- Untested public functions and methods
- Complex logic without corresponding tests
- Error paths that aren't tested
- Integration points lacking tests
- Mock usage patterns and potential issues

Provide actionable recommendations for improving test coverage.`,
  tools: ["Read", "Grep", "Glob"],
  model: "haiku" // Use faster model for test analysis
};

/**
 * Performance analyzer subagent
 */
const performanceAnalyzer: AgentDefinition = {
  description: "Performance and optimization specialist",
  prompt: `You are a performance optimization expert.

Analyze code for:
- N+1 query patterns in database operations
- Unnecessary loops and algorithmic inefficiencies
- Memory leaks and unbounded growth
- Missing caching opportunities
- Blocking operations in async contexts
- Large bundle sizes and lazy loading opportunities
- Inefficient data structures

For each issue, explain:
1. The performance impact
2. Why it's problematic
3. How to fix it with a code example`,
  tools: ["Read", "Grep", "Glob"],
  model: "sonnet"
};

// ============================================================================
// Main Review Function
// ============================================================================

/**
 * Runs a comprehensive code review with subagents
 *
 * @param config - Review configuration options
 * @returns Structured review result or null if failed
 */
export async function runCodeReview(
  config: ReviewAgentConfig
): Promise<ReviewResult | null> {
  const {
    directory,
    model = "opus",
    maxTurns = 250,
    useSubagents = true
  } = config;

  console.log(`\n${"=".repeat(60)}`);
  console.log(`  Code Review Agent`);
  console.log(`${"=".repeat(60)}`);
  console.log(`  Directory: ${directory}`);
  console.log(`  Model: ${model}`);
  console.log(`  Subagents: ${useSubagents ? "enabled" : "disabled"}`);
  console.log(`${"=".repeat(60)}\n`);

  let result: ReviewResult | null = null;
  let sessionId: string | undefined;

  // Build tools list
  const tools = ["Read", "Glob", "Grep"];
  if (useSubagents) {
    tools.push("Task");
  }

  // Build agents map
  const agents: Record<string, AgentDefinition> = {};
  if (useSubagents) {
    agents["security-scanner"] = securityReviewer;
    agents["test-analyzer"] = testAnalyzer;
    agents["performance-analyzer"] = performanceAnalyzer;
  }

  for await (const message of query({
    prompt: `Perform a comprehensive code review of ${directory}.

Your review should cover:
1. **Bugs** - Logic errors, potential crashes, off-by-one errors
2. **Security** - Vulnerabilities, exposed secrets, injection risks
3. **Performance** - Inefficient patterns, N+1 queries, memory issues
4. **Code Quality** - Maintainability, readability, best practices

${useSubagents ? `Use the specialized subagents:
- security-scanner: For deep security vulnerability analysis
- test-analyzer: For test coverage evaluation
- performance-analyzer: For performance optimization opportunities` : ""}

Be thorough but focus on actionable issues. Provide specific file paths and line numbers.`,
    options: {
      model,
      allowedTools: tools,
      permissionMode: "bypassPermissions",
      maxTurns,
      outputFormat: {
        type: "json_schema",
        schema: reviewSchema
      },
      agents: useSubagents ? agents : undefined,
      hooks: {
        PreToolUse: [
          { hooks: [auditLogger] },
          { matcher: "Bash", hooks: [blockDangerousCommands] }
        ]
      }
    }
  })) {
    // Capture session ID
    if (message.type === "system" && message.subtype === "init") {
      sessionId = message.session_id;
      console.log(`Session: ${sessionId}\n`);
    }

    // Progress updates
    if (message.type === "assistant") {
      for (const block of message.message.content as ContentBlock[]) {
        if ("name" in block) {
          if (block.name === "Task") {
            const taskInput = block.input as Record<string, unknown>;
            console.log(`  -> Delegating to: ${taskInput.subagent_type}`);
          } else {
            console.log(`  -> ${block.name}: ${getToolSummary(block)}`);
          }
        }
      }
    }

    // Final result
    if (message.type === "result") {
      console.log();
      if (message.subtype === "success" && message.structured_output) {
        result = message.structured_output as ReviewResult;
        console.log(`[SUCCESS] Review complete!`);
        console.log(`  Cost: $${message.total_cost_usd.toFixed(4)}`);

        // Show per-model breakdown if available
        if (message.modelUsage) {
          console.log(`  Model usage:`);
          for (const [modelName, usage] of Object.entries(message.modelUsage)) {
            console.log(`    - ${modelName}: $${usage.costUSD.toFixed(4)}`);
          }
        }
      } else {
        console.log(`[FAILED] Review failed: ${message.subtype}`);
      }
    }
  }

  return result;
}

/**
 * Gets a summary of a tool call for display
 */
function getToolSummary(block: ContentBlock): string {
  if (!("input" in block)) return "";

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
 * Prints formatted review results
 */
export function printResults(result: ReviewResult): void {
  console.log(`\n${"=".repeat(60)}`);
  console.log(`  REVIEW RESULTS`);
  console.log(`${"=".repeat(60)}\n`);

  // Score with visual indicator
  const scoreBar = getScoreBar(result.overallScore);
  console.log(`Score: ${result.overallScore}/100 ${scoreBar}`);
  console.log(`Issues Found: ${result.issues.length}\n`);

  // Summary
  console.log("Summary:");
  console.log("-".repeat(40));
  console.log(result.summary);
  console.log();

  // Group issues by severity
  const groups = {
    critical: result.issues.filter((i) => i.severity === "critical"),
    high: result.issues.filter((i) => i.severity === "high"),
    medium: result.issues.filter((i) => i.severity === "medium"),
    low: result.issues.filter((i) => i.severity === "low")
  };

  for (const [severity, issues] of Object.entries(groups)) {
    if (issues.length === 0) continue;

    const header = `${severity.toUpperCase()} SEVERITY (${issues.length})`;
    console.log(`\n${header}`);
    console.log("=".repeat(header.length));

    for (const issue of issues) {
      const location = issue.line ? `${issue.file}:${issue.line}` : issue.file;
      console.log(`\n[${issue.category.toUpperCase()}] ${location}`);
      console.log(`  ${issue.description}`);
      if (issue.suggestion) {
        console.log(`  Suggestion: ${issue.suggestion}`);
      }
    }
  }

  // Statistics
  console.log(`\n${"=".repeat(60)}`);
  console.log("Statistics:");
  console.log("-".repeat(40));
  console.log(`  Critical: ${groups.critical.length}`);
  console.log(`  High: ${groups.high.length}`);
  console.log(`  Medium: ${groups.medium.length}`);
  console.log(`  Low: ${groups.low.length}`);

  const byCategory = result.issues.reduce(
    (acc, issue) => {
      acc[issue.category] = (acc[issue.category] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  console.log();
  for (const [category, count] of Object.entries(byCategory)) {
    console.log(`  ${category}: ${count}`);
  }
}

/**
 * Creates a visual score bar
 */
function getScoreBar(score: number): string {
  const filled = Math.round(score / 10);
  const empty = 10 - filled;
  return `[${"#".repeat(filled)}${"-".repeat(empty)}]`;
}

/**
 * Exports results in various formats
 */
export function exportResults(
  result: ReviewResult,
  format: "json" | "markdown" | "sarif"
): string {
  switch (format) {
    case "json":
      return JSON.stringify(result, null, 2);

    case "markdown":
      return generateMarkdownReport(result);

    case "sarif":
      return generateSarifReport(result);

    default:
      return JSON.stringify(result, null, 2);
  }
}

/**
 * Generates a Markdown report
 */
function generateMarkdownReport(result: ReviewResult): string {
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
    ""
  ];

  const groups = {
    critical: result.issues.filter((i) => i.severity === "critical"),
    high: result.issues.filter((i) => i.severity === "high"),
    medium: result.issues.filter((i) => i.severity === "medium"),
    low: result.issues.filter((i) => i.severity === "low")
  };

  for (const [severity, issues] of Object.entries(groups)) {
    if (issues.length === 0) continue;

    lines.push(`### ${severity.charAt(0).toUpperCase() + severity.slice(1)} (${issues.length})`);
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
 * Generates a SARIF report for integration with GitHub Code Scanning
 */
function generateSarifReport(result: ReviewResult): string {
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
                shortDescription: { text: "Potential bug or logic error" }
              },
              {
                id: "security",
                name: "Security",
                shortDescription: { text: "Security vulnerability" }
              },
              {
                id: "performance",
                name: "Performance",
                shortDescription: { text: "Performance issue" }
              },
              {
                id: "style",
                name: "Style",
                shortDescription: { text: "Code style or quality issue" }
              }
            ]
          }
        },
        results: result.issues.map((issue) => ({
          ruleId: issue.category,
          level: mapSeverityToSarif(issue.severity),
          message: { text: issue.description },
          locations: [
            {
              physicalLocation: {
                artifactLocation: { uri: issue.file },
                region: issue.line ? { startLine: issue.line } : undefined
              }
            }
          ],
          fixes: issue.suggestion
            ? [
                {
                  description: { text: issue.suggestion }
                }
              ]
            : undefined
        }))
      }
    ]
  };

  return JSON.stringify(sarif, null, 2);
}

/**
 * Maps severity to SARIF level
 */
function mapSeverityToSarif(
  severity: string
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

// ============================================================================
// CLI Entry Point
// ============================================================================

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const directory = args[0] || ".";
  const useSubagents = !args.includes("--no-subagents");
  const outputFormat = args.includes("--sarif")
    ? "sarif"
    : args.includes("--markdown")
      ? "markdown"
      : "json";

  const result = await runCodeReview({
    directory,
    model: "opus",
    useSubagents
  });

  if (result) {
    printResults(result);

    // Export if requested
    if (args.includes("--export")) {
      console.log(`\n${"=".repeat(60)}`);
      console.log(`Exported (${outputFormat.toUpperCase()}):`);
      console.log("=".repeat(60));
      console.log(exportResults(result, outputFormat));
    }
  } else {
    console.error("\nReview failed to produce results");
    process.exit(1);
  }
}

main().catch(console.error);
