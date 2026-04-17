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

import { writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import {
  query,
  type AgentDefinition,
  type HookCallback,
  type PreToolUseHookInput,
} from "@anthropic-ai/claude-agent-sdk";

import {
  generateMarkdownReport,
  generateSarifReport,
  getScoreBar,
  getToolSummary,
} from "./formatters.js";
import { logger } from "./logger.js";
import {
  CLI_USAGE,
  parseArgs,
  type OutputFormat,
  type ParsedCli,
} from "./cli.js";
import {
  reviewSchema,
  type ContentBlock,
  type ReviewAgentConfig,
  type ReviewResult,
} from "./types.js";

// ============================================================================
// Hooks
// ============================================================================

/**
 * Audit logging hook - logs all tool usage for compliance.
 *
 * Note: A previous `blockDangerousCommands` hook was removed because it only
 * matched `tool_name === "Bash"`, which is never in `allowedTools`. The hook
 * could never fire and gave a false sense of security. The allowlist itself
 * (Read/Glob/Grep/Task) is the real control.
 */
const auditLogger: HookCallback = async (input) => {
  if (input.hook_event_name === "PreToolUse") {
    const preInput = input as PreToolUseHookInput;
    logger.info("tool_use", { tool: preInput.tool_name });
  }
  return {}; // Allow the operation
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
  model: "sonnet",
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
  model: "haiku", // Use faster model for test analysis
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
  model: "sonnet",
};

// ============================================================================
// Main Review Function
// ============================================================================

const DEFAULT_TIMEOUT_MS = 600_000; // 10 minutes

function resolveTimeoutMs(): number {
  const raw = process.env.AUDIT_REVIEW_TIMEOUT_MS;
  if (!raw) return DEFAULT_TIMEOUT_MS;
  const parsed = Number.parseInt(raw, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    logger.warn("invalid_timeout_env_ignored", {
      AUDIT_REVIEW_TIMEOUT_MS: raw,
      fallbackMs: DEFAULT_TIMEOUT_MS,
    });
    return DEFAULT_TIMEOUT_MS;
  }
  return parsed;
}

/**
 * Runs a comprehensive code review with subagents
 *
 * @param config - Review configuration options
 * @returns Structured review result or null if failed / timed out
 */
export async function runCodeReview(
  config: ReviewAgentConfig,
): Promise<ReviewResult | null> {
  const {
    directory,
    model = "opus",
    maxTurns = 250,
    useSubagents = true,
  } = config;

  logger.info("review_started", {
    directory,
    model,
    subagents: useSubagents,
    maxTurns,
  });

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

  const timeoutMs = resolveTimeoutMs();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  // Abort sentinel so Promise.race resolves (rather than throwing) when the
  // timeout fires — lets us log a clear message and exit cleanly.
  const TIMEOUT_SENTINEL: unique symbol = Symbol("timeout");
  const timeoutPromise = new Promise<typeof TIMEOUT_SENTINEL>((resolve) => {
    controller.signal.addEventListener(
      "abort",
      () => resolve(TIMEOUT_SENTINEL),
      { once: true },
    );
  });

  try {
    const iterator = query({
      prompt: `Perform a comprehensive code review of ${directory}.

Your review should cover:
1. **Bugs** - Logic errors, potential crashes, off-by-one errors
2. **Security** - Vulnerabilities, exposed secrets, injection risks
3. **Performance** - Inefficient patterns, N+1 queries, memory issues
4. **Code Quality** - Maintainability, readability, best practices

${
  useSubagents
    ? `Use the specialized subagents:
- security-scanner: For deep security vulnerability analysis
- test-analyzer: For test coverage evaluation
- performance-analyzer: For performance optimization opportunities`
    : ""
}

Be thorough but focus on actionable issues. Provide specific file paths and line numbers.`,
      options: {
        model,
        allowedTools: tools,
        // "auto" is the SDK default; subagents inherit `allowedTools` instead
        // of silently bypassing permissions as "bypassPermissions" used to.
        permissionMode: "auto",
        maxTurns,
        outputFormat: {
          type: "json_schema",
          schema: reviewSchema,
        },
        agents: useSubagents ? agents : undefined,
        hooks: {
          PreToolUse: [{ hooks: [auditLogger] }],
        },
      },
    })[Symbol.asyncIterator]();

    while (true) {
      const nextPromise = iterator.next();
      const settled = await Promise.race([nextPromise, timeoutPromise]);

      if (settled === TIMEOUT_SENTINEL) {
        logger.error("review_timeout", { timeoutMs, directory });
        // Try to release the underlying iterator if it supports `return`.
        if (typeof iterator.return === "function") {
          try {
            await iterator.return();
          } catch {
            // Ignore cleanup errors
          }
        }
        return null;
      }

      const { value: message, done } = settled;
      if (done) break;

      // Capture session ID
      if (message.type === "system" && message.subtype === "init") {
        sessionId = message.session_id;
        logger.info("session_started", { sessionId });
      }

      // Progress updates
      if (message.type === "assistant") {
        for (const block of message.message.content as ContentBlock[]) {
          if ("name" in block) {
            if (block.name === "Task") {
              const taskInput = block.input as Record<string, unknown>;
              logger.info("delegating", {
                subagent: String(taskInput.subagent_type ?? "unknown"),
              });
            } else {
              const summary = getToolSummary(block);
              logger.info("tool_call", {
                tool: block.name,
                ...(summary ? { summary } : {}),
              });
            }
          }
        }
      }

      // Final result
      if (message.type === "result") {
        if (message.subtype === "success" && message.structured_output) {
          result = message.structured_output as ReviewResult;
          logger.info("review_complete", {
            costUsd: Number(message.total_cost_usd.toFixed(4)),
          });

          if (message.modelUsage) {
            for (const [modelName, usage] of Object.entries(
              message.modelUsage,
            )) {
              logger.info("model_usage", {
                model: modelName,
                costUsd: Number(usage.costUSD.toFixed(4)),
              });
            }
          }
        } else {
          logger.error("review_failed", { subtype: message.subtype });
        }
      }
    }
  } finally {
    clearTimeout(timer);
  }

  return result;
}

/**
 * Prints formatted review results
 */
export function printResults(result: ReviewResult): void {
  // Human-readable report — stays on console.log intentionally (not logs).
  // eslint-disable-next-line no-console
  console.log(`\n${"=".repeat(60)}`);
  // eslint-disable-next-line no-console
  console.log(`  REVIEW RESULTS`);
  // eslint-disable-next-line no-console
  console.log(`${"=".repeat(60)}\n`);

  // Score with visual indicator
  const scoreBar = getScoreBar(result.overallScore);
  // eslint-disable-next-line no-console
  console.log(`Score: ${result.overallScore}/100 ${scoreBar}`);
  // eslint-disable-next-line no-console
  console.log(`Issues Found: ${result.issues.length}\n`);

  // Summary
  // eslint-disable-next-line no-console
  console.log("Summary:");
  // eslint-disable-next-line no-console
  console.log("-".repeat(40));
  // eslint-disable-next-line no-console
  console.log(result.summary);
  // eslint-disable-next-line no-console
  console.log();

  // Group issues by severity
  const groups = {
    critical: result.issues.filter((i) => i.severity === "critical"),
    high: result.issues.filter((i) => i.severity === "high"),
    medium: result.issues.filter((i) => i.severity === "medium"),
    low: result.issues.filter((i) => i.severity === "low"),
  };

  for (const [severity, issues] of Object.entries(groups)) {
    if (issues.length === 0) continue;

    const header = `${severity.toUpperCase()} SEVERITY (${issues.length})`;
    // eslint-disable-next-line no-console
    console.log(`\n${header}`);
    // eslint-disable-next-line no-console
    console.log("=".repeat(header.length));

    for (const issue of issues) {
      const location = issue.line ? `${issue.file}:${issue.line}` : issue.file;
      // eslint-disable-next-line no-console
      console.log(`\n[${issue.category.toUpperCase()}] ${location}`);
      // eslint-disable-next-line no-console
      console.log(`  ${issue.description}`);
      if (issue.suggestion) {
        // eslint-disable-next-line no-console
        console.log(`  Suggestion: ${issue.suggestion}`);
      }
    }
  }

  // Statistics
  // eslint-disable-next-line no-console
  console.log(`\n${"=".repeat(60)}`);
  // eslint-disable-next-line no-console
  console.log("Statistics:");
  // eslint-disable-next-line no-console
  console.log("-".repeat(40));
  // eslint-disable-next-line no-console
  console.log(`  Critical: ${groups.critical.length}`);
  // eslint-disable-next-line no-console
  console.log(`  High: ${groups.high.length}`);
  // eslint-disable-next-line no-console
  console.log(`  Medium: ${groups.medium.length}`);
  // eslint-disable-next-line no-console
  console.log(`  Low: ${groups.low.length}`);

  const byCategory = result.issues.reduce(
    (acc, issue) => {
      acc[issue.category] = (acc[issue.category] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>,
  );

  // eslint-disable-next-line no-console
  console.log();
  for (const [category, count] of Object.entries(byCategory)) {
    // eslint-disable-next-line no-console
    console.log(`  ${category}: ${count}`);
  }
}

/**
 * Exports results in various formats
 */
export function exportResults(
  result: ReviewResult,
  format: "json" | "markdown" | "sarif",
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

// ============================================================================
// CLI Entry Point
// ============================================================================

async function writeOrPrint(
  payload: string,
  outputPath: string | undefined,
): Promise<void> {
  if (outputPath) {
    await writeFile(outputPath, payload, "utf8");
    logger.info("report_written", { path: outputPath });
    return;
  }
  // eslint-disable-next-line no-console
  console.log(payload);
}

async function main(): Promise<void> {
  let parsed: ParsedCli;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (err) {
    logger.error("cli_parse_error", {
      message: err instanceof Error ? err.message : String(err),
    });
    // eslint-disable-next-line no-console
    console.error(CLI_USAGE);
    process.exit(2);
  }

  if (parsed.help) {
    // eslint-disable-next-line no-console
    console.log(CLI_USAGE);
    return;
  }

  for (const msg of parsed.deprecations) {
    logger.warn("deprecated_flag", { message: msg });
  }

  const result = await runCodeReview({
    directory: parsed.repo,
    model: parsed.model,
    maxTurns: parsed.maxTurns,
    useSubagents: parsed.useSubagents,
  });

  if (!result) {
    logger.error("review_no_result");
    process.exit(1);
  }

  // Only print the human summary when not writing to a file (otherwise the
  // human summary would clobber stdout that the caller wants clean).
  if (!parsed.output) {
    printResults(result);
  }

  const payload = exportResults(result, parsed.format as OutputFormat);
  await writeOrPrint(payload, parsed.output);
}

/**
 * Detect whether this module was invoked directly (vs imported as a library).
 * ESM-safe equivalent of `require.main === module`.
 */
function isMainEntry(): boolean {
  const argvEntry = process.argv[1];
  if (!argvEntry) return false;
  try {
    return import.meta.url === new URL(`file://${argvEntry}`).href;
  } catch {
    try {
      return fileURLToPath(import.meta.url) === argvEntry;
    } catch {
      return false;
    }
  }
}

if (isMainEntry()) {
  main().catch((err) => {
    logger.error("fatal", {
      message: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
    });
    process.exit(1);
  });
}
