/**
 * Code Review Agent Types
 *
 * Type definitions for the Claude Agent SDK-based code review agent.
 */

/**
 * Severity levels for code review issues
 */
export type IssueSeverity = "low" | "medium" | "high" | "critical";

/**
 * Categories of code review issues
 */
export type IssueCategory = "bug" | "security" | "performance" | "style";

/**
 * Represents a single issue found during code review
 */
export interface ReviewIssue {
  /** Severity level of the issue */
  severity: IssueSeverity;
  /** Category of the issue */
  category: IssueCategory;
  /** File path where the issue was found */
  file: string;
  /** Line number where the issue occurs (optional) */
  line?: number;
  /** Description of the issue */
  description: string;
  /** Suggested fix for the issue (optional) */
  suggestion?: string;
}

/**
 * Complete code review result
 */
export interface ReviewResult {
  /** List of issues found during review */
  issues: ReviewIssue[];
  /** Summary of the review findings */
  summary: string;
  /** Overall code quality score (0-100) */
  overallScore: number;
}

/**
 * JSON Schema for structured review output
 */
export const reviewSchema = {
  type: "object",
  properties: {
    issues: {
      type: "array",
      items: {
        type: "object",
        properties: {
          severity: {
            type: "string",
            enum: ["low", "medium", "high", "critical"]
          },
          category: {
            type: "string",
            enum: ["bug", "security", "performance", "style"]
          },
          file: { type: "string" },
          line: { type: "number" },
          description: { type: "string" },
          suggestion: { type: "string" }
        },
        required: ["severity", "category", "file", "description"]
      }
    },
    summary: { type: "string" },
    overallScore: { type: "number" }
  },
  required: ["issues", "summary", "overallScore"]
} as const;

/**
 * Configuration options for the code review agent
 */
export interface ReviewAgentConfig {
  /** Directory to review */
  directory: string;
  /** Model to use (opus, sonnet, haiku) */
  model?: "opus" | "sonnet" | "haiku";
  /** Maximum number of turns for the agent */
  maxTurns?: number;
  /** Whether to use structured output */
  structuredOutput?: boolean;
  /** Whether to use subagents for specialized analysis */
  useSubagents?: boolean;
  /** File patterns to include */
  includePatterns?: string[];
  /** File patterns to exclude */
  excludePatterns?: string[];
}

/**
 * Tool input types for logging
 */
export interface ToolInput {
  file_path?: string;
  pattern?: string;
  path?: string;
  command?: string;
  [key: string]: unknown;
}

/**
 * Content block types from Claude responses
 */
export interface TextBlock {
  type: "text";
  text: string;
}

export interface ToolUseBlock {
  type: "tool_use";
  id: string;
  name: string;
  input: ToolInput;
}

export type ContentBlock = TextBlock | ToolUseBlock;

/**
 * Agent message types
 */
export interface SystemMessage {
  type: "system";
  subtype: "init";
  session_id: string;
  tools: string[];
}

export interface AssistantMessage {
  type: "assistant";
  message: {
    role: "assistant";
    content: ContentBlock[];
  };
}

export interface ResultMessage {
  type: "result";
  subtype: "success" | "error" | "max_turns_reached";
  total_cost_usd: number;
  structured_output?: ReviewResult;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
  modelUsage?: Record<string, {
    costUSD: number;
    inputTokens: number;
    outputTokens: number;
  }>;
}

export type AgentMessage = SystemMessage | AssistantMessage | ResultMessage;
