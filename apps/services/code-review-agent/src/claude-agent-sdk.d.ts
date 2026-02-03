/**
 * Type declarations for @anthropic-ai/claude-agent-sdk
 * This is a placeholder until the official SDK is available
 */

declare module "@anthropic-ai/claude-agent-sdk" {
  export interface OutputFormat {
    type: "json_schema" | "json" | "text";
    schema?: unknown;
  }

  export interface QueryOptions {
    model?: "opus" | "sonnet" | "haiku";
    allowedTools?: string[];
    maxTurns?: number;
    systemPrompt?: string;
    cwd?: string;
    permissionMode?: "auto" | "manual" | "bypassPermissions";
    hooks?: HookConfig;
    subagents?: AgentDefinition[];
    agents?: Record<string, AgentDefinition>;
    outputSchema?: unknown;
    outputFormat?: OutputFormat | "json" | "text";
  }

  export interface HookDefinition {
    hooks?: HookCallback[];
    matcher?: string | ((input: HookInput) => boolean);
  }

  export interface HookConfig {
    PreToolUse?: HookCallback[] | HookDefinition[];
    PostToolUse?: HookCallback[] | HookDefinition[];
  }

  export interface QueryParams {
    prompt: string;
    options?: QueryOptions;
  }

  export interface InitMessage {
    type: "system";
    subtype: "init";
    session_id: string;
    tools: string[];
  }

  export interface ContentBlock {
    text?: string;
    name?: string;
    input?: Record<string, unknown>;
  }

  export interface AssistantMessage {
    type: "assistant";
    message: {
      content: ContentBlock[];
      usage?: {
        input_tokens: number;
        output_tokens: number;
      };
    };
  }

  export interface ModelUsage {
    input_tokens: number;
    output_tokens: number;
    costUSD: number;
  }

  export interface ResultMessage {
    type: "result";
    subtype: "end_turn" | "max_turns" | "error" | "success";
    total_cost_usd: number;
    duration_ms: number;
    output?: unknown;
    structured_output?: unknown;
    modelUsage?: Record<string, ModelUsage>;
  }

  export interface UserMessage {
    type: "user";
    message: {
      content: ContentBlock[];
    };
  }

  export type AgentMessage = InitMessage | AssistantMessage | ResultMessage | UserMessage;

  export function query(params: QueryParams): AsyncIterable<AgentMessage>;

  export interface RunOptions extends QueryOptions {
    onMessage?: (message: AgentMessage) => void;
    onError?: (error: Error) => void;
  }

  export interface RunParams extends QueryParams {
    options?: RunOptions;
  }

  export function run(params: RunParams): Promise<ResultMessage>;

  // Hook types
  export interface HookInput {
    hook_event_name: string;
  }

  export interface PreToolUseHookInput extends HookInput {
    hook_event_name: "PreToolUse";
    tool_name: string;
    tool_input: Record<string, unknown>;
  }

  export interface PostToolUseHookInput extends HookInput {
    hook_event_name: "PostToolUse";
    tool_name: string;
    tool_output: unknown;
  }

  export interface HookOutput {
    hookSpecificOutput?: {
      hookEventName: string;
      permissionDecision?: "allow" | "deny";
      permissionDecisionReason?: string;
    };
  }

  export type HookCallback = (input: HookInput) => Promise<HookOutput>;

  // Subagent types
  export interface AgentDefinition {
    description: string;
    prompt: string;
    allowedTools?: string[];
    tools?: string[];
    model?: "opus" | "sonnet" | "haiku";
  }
}
