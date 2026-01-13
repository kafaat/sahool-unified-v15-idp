/**
 * Basic Agent Example
 *
 * This is the simplest example of using the Claude Agent SDK.
 * It demonstrates the basic query() function and message handling.
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

async function main(): Promise<void> {
  console.log("Starting basic agent...\n");

  for await (const message of query({
    prompt: "What files are in this directory?",
    options: {
      model: "opus",
      allowedTools: ["Glob", "Read"],
      maxTurns: 250,
    },
  })) {
    if (message.type === "system" && message.subtype === "init") {
      console.log("Session ID:", message.session_id);
      console.log("Available tools:", message.tools);
      console.log();
    }

    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if ("text" in block) {
          console.log(block.text);
        } else if ("name" in block) {
          console.log(`\nUsing tool: ${block.name}`);
        }
      }
    }

    if (message.type === "result") {
      console.log("\nDone:", message.subtype);
      console.log(`Cost: $${message.total_cost_usd.toFixed(4)}`);
    }
  }
}

main().catch(console.error);
