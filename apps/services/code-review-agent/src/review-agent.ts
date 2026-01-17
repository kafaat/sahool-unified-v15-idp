/**
 * Code Review Agent
 *
 * Analyzes code for bugs, security issues, performance problems,
 * and code quality improvements using Claude's AI capabilities.
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import type { ContentBlock } from "./types.js";

/**
 * Reviews code in the specified directory
 *
 * @param directory - Path to the directory to review
 */
async function reviewCode(directory: string): Promise<void> {
  console.log(`\n${"=".repeat(50)}`);
  console.log(`Code Review Agent`);
  console.log(`Directory: ${directory}`);
  console.log(`${"=".repeat(50)}\n`);

  for await (const message of query({
    prompt: `Review the code in ${directory} for:
1. Bugs and potential crashes
2. Security vulnerabilities
3. Performance issues
4. Code quality improvements

Be specific about file names and line numbers. Focus on actionable feedback.`,
    options: {
      model: "opus",
      allowedTools: ["Read", "Glob", "Grep"],
      permissionMode: "bypassPermissions", // Auto-approve read operations
      maxTurns: 250,
    },
  })) {
    // Show session initialization
    if (message.type === "system" && message.subtype === "init") {
      console.log(`Session: ${message.session_id}`);
      console.log(`Tools: ${message.tools.join(", ")}\n`);
    }

    // Show Claude's analysis as it happens
    if (message.type === "assistant") {
      for (const block of message.message.content as ContentBlock[]) {
        if ("text" in block) {
          console.log(block.text);
        } else if ("name" in block) {
          console.log(`\n[Tool] ${block.name}: ${getToolSummary(block)}`);
        }
      }
    }

    // Show completion status
    if (message.type === "result") {
      console.log(`\n${"=".repeat(50)}`);
      if (message.subtype === "success") {
        console.log(
          `Review complete! Cost: $${message.total_cost_usd.toFixed(4)}`,
        );
      } else {
        console.log(`Review failed: ${message.subtype}`);
      }
      console.log(`${"=".repeat(50)}\n`);
    }
  }
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

// Get directory from command line or use current directory
const directory = process.argv[2] || ".";
reviewCode(directory).catch(console.error);
