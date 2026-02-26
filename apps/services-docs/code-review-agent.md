# Code Review Agent Service

**Port**: 8145 | **Type**: Node.js (TypeScript, Claude Agent SDK) | **Version**: 16.0.0

AI-powered code review agent built on the Anthropic Claude Agent SDK. Analyzes codebases for bugs, security vulnerabilities, performance issues, and code-quality problems using specialized subagents.

---

## Overview

`code-review-agent` is a TypeScript library and CLI tool that wraps the Claude Agent SDK to perform multi-dimensional code review. It uses a production agent with three specialized subagents running in parallel, produces structured JSON output validated against a JSON Schema, and exports results in JSON, Markdown, or SARIF (GitHub Code Scanning) format. Dangerous shell commands are blocked by a permission hook, and all tool invocations are audit-logged.

---

## Architecture

```
Production Agent (Claude Opus)
    ├── Security Scanner Subagent  (Claude Sonnet) - deep vulnerability analysis
    ├── Test Analyzer Subagent     (Claude Haiku)  - test coverage evaluation
    └── Performance Analyzer       (Claude Sonnet) - optimization opportunities
```

Each agent uses the `ClaudeAgentSDK` with structured output (JSON Schema) and permission hooks that block `rm -rf`, `sudo`, `chmod 777`, `curl | sh`, and `wget | sh`.

---

## API Endpoints

This service is a CLI / library tool, not a long-running HTTP server. It is invoked programmatically or via CLI during CI pipelines. See the CI workflow `ci-yolo26-vision.yml` and `code-review-agent` GitHub Actions integration for usage.

---

## CLI Usage

```bash
# Review current directory
npx tsx src/review-agent.ts

# Review specific directory
npx tsx src/review-agent.ts ./src

# Production agent with all subagents
npx tsx src/production-agent.ts ./src

# Disable subagents
npx tsx src/production-agent.ts ./src --no-subagents

# Export as Markdown
npx tsx src/production-agent.ts ./src --export --markdown

# Export as SARIF (GitHub Code Scanning)
npx tsx src/production-agent.ts ./src --export --sarif
```

---

## Programmatic API

```typescript
import { runCodeReview, printResults, exportResults } from "@sahool/code-review-agent";

const result = await runCodeReview({
  directory: "./src",
  model: "opus",
  useSubagents: true,
  structuredOutput: true,
  maxTurns: 250,
});

if (result) {
  printResults(result);
  const sarif = exportResults(result, "sarif");
}
```

---

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `directory` | `string` | Required | Directory to review |
| `model` | `'opus' \| 'sonnet' \| 'haiku'` | `'opus'` | Claude model to use |
| `maxTurns` | `number` | `250` | Maximum agent turns |
| `useSubagents` | `boolean` | `true` | Enable specialized subagents |
| `structuredOutput` | `boolean` | `true` | Return validated JSON |

---

## Output Formats

### JSON (default)

```json
{
  "issues": [
    {
      "severity": "high",
      "category": "security",
      "file": "src/auth.ts",
      "line": 42,
      "description": "SQL injection vulnerability",
      "suggestion": "Use parameterized queries"
    }
  ],
  "summary": "Found 3 issues across 2 files",
  "overallScore": 75
}
```

### SARIF

GitHub Code Scanning compatible format for integration with PR checks and security dashboards.

### Markdown

Human-readable structured report suitable for PR comments or documentation.

---

## Subagents

| Subagent | Model | Purpose |
|----------|-------|---------|
| `security-scanner` | Claude Sonnet | Deep security vulnerability analysis |
| `test-analyzer` | Claude Haiku | Test coverage and quality evaluation |
| `performance-analyzer` | Claude Sonnet | Performance optimization opportunities |

---

## Hooks

### Audit Logger

All tool invocations are logged with ISO timestamps:
```
[AUDIT] 2026-01-10T12:00:00.000Z - Tool: Read
[AUDIT] 2026-01-10T12:00:01.000Z - Tool: Grep
```

### Dangerous Command Blocker

Blocks any Bash invocations containing: `rm -rf`, `sudo`, `chmod 777`, `curl | sh`, `wget | sh`.

---

## NATS Events

This service does not connect to NATS. Review results are returned synchronously to the caller (CLI or API consumer).

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Required. API key for Claude models |
| `LOG_LEVEL` | Logging level (default: `info`) |

---

## Source Structure

```
src/
├── index.ts              # Library exports (runCodeReview, printResults, exportResults)
├── types.ts              # ReviewResult, ReviewIssue, reviewSchema (JSON Schema)
├── agent.ts              # Basic agent example
├── review-agent.ts       # Simple review agent
├── review-structured.ts  # Structured output agent
└── production-agent.ts   # Full production agent with subagents
```

---

## Dependencies

- `@anthropic-ai/claude-agent-sdk` - Claude Agent SDK
- `TypeScript` 5.9.x, Node.js >= 20

---

## Health Endpoints

This service has no HTTP health endpoints as it is a CLI/library tool. Health is inferred from process exit code (0 = success, non-zero = failure) for CI integration.

---

## Related Services

- **code-fix-agent** (8162) - Python counterpart for automated fixes
- **code-review-service** (8102) - persistent HTTP code review service
