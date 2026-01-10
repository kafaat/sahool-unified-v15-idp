/**
 * Code Review Agent
 *
 * AI-powered code review agent using the Claude Agent SDK.
 *
 * Features:
 * - Analyzes code for bugs, security issues, and quality problems
 * - Uses specialized subagents for security and test analysis
 * - Provides structured JSON output for integration
 * - Supports multiple output formats (JSON, Markdown, SARIF)
 * - Includes audit logging and permission controls
 *
 * @example
 * ```typescript
 * import { runCodeReview, printResults } from '@sahool/code-review-agent';
 *
 * const result = await runCodeReview({
 *   directory: './src',
 *   model: 'opus',
 *   useSubagents: true
 * });
 *
 * if (result) {
 *   printResults(result);
 * }
 * ```
 *
 * @packageDocumentation
 */

// Re-export types
export {
  type ReviewResult,
  type ReviewIssue,
  type IssueSeverity,
  type IssueCategory,
  type ReviewAgentConfig,
  reviewSchema
} from "./types.js";

// Re-export functions
export {
  runCodeReview,
  printResults,
  exportResults
} from "./production-agent.js";
