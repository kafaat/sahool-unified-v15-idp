# Code Review Agent

AI-powered code review agent using the Claude Agent SDK. Analyzes codebases for bugs, security vulnerabilities, performance issues, and code quality problems.

## Features

- **Comprehensive Analysis**: Bugs, security, performance, and code quality
- **Specialized Subagents**: Security scanner, test analyzer, performance analyzer
- **Structured Output**: JSON Schema-validated results
- **Multiple Formats**: JSON, Markdown, SARIF (GitHub Code Scanning)
- **Audit Logging**: Track all tool usage for compliance
- **Permission Controls**: Block dangerous commands

## Quick Start

```bash
# Install dependencies
npm install

# Run basic review on current directory
npm run review

# Run with structured output
npm run review:structured

# Run production agent
npm run review:production ./src
```

## Usage

### CLI

```bash
# Review current directory
npx tsx src/review-agent.ts

# Review specific directory
npx tsx src/review-agent.ts ./src

# Production agent with all features
npx tsx src/production-agent.ts ./src

# Disable subagents
npx tsx src/production-agent.ts ./src --no-subagents

# Export as Markdown
npx tsx src/production-agent.ts ./src --export --markdown

# Export as SARIF
npx tsx src/production-agent.ts ./src --export --sarif
```

### Programmatic

```typescript
import { runCodeReview, printResults, exportResults } from '@sahool/code-review-agent';

// Run review
const result = await runCodeReview({
  directory: './src',
  model: 'opus',
  useSubagents: true
});

if (result) {
  // Print formatted results
  printResults(result);

  // Export as SARIF for GitHub
  const sarif = exportResults(result, 'sarif');
  fs.writeFileSync('results.sarif', sarif);
}
```

## Configuration

### ReviewAgentConfig

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `directory` | `string` | Required | Directory to review |
| `model` | `'opus' \| 'sonnet' \| 'haiku'` | `'opus'` | Claude model to use |
| `maxTurns` | `number` | `250` | Maximum agent turns |
| `useSubagents` | `boolean` | `true` | Use specialized subagents |
| `structuredOutput` | `boolean` | `true` | Return structured JSON |

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
  "summary": "Found 3 issues...",
  "overallScore": 75
}
```

### SARIF

GitHub Code Scanning compatible format for CI/CD integration.

### Markdown

Human-readable report format.

## Subagents

The production agent uses specialized subagents:

| Subagent | Model | Purpose |
|----------|-------|---------|
| `security-scanner` | Sonnet | Deep security vulnerability analysis |
| `test-analyzer` | Haiku | Test coverage evaluation |
| `performance-analyzer` | Sonnet | Performance optimization opportunities |

## Hooks

### Audit Logger

Logs all tool usage with timestamps:

```
[AUDIT] 2025-01-10T12:00:00.000Z - Tool: Read
[AUDIT] 2025-01-10T12:00:01.000Z - Tool: Grep
```

### Dangerous Command Blocker

Blocks commands containing:
- `rm -rf`
- `sudo`
- `chmod 777`
- `curl | sh`
- `wget | sh`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for Claude |
| `LOG_LEVEL` | Logging level (default: `info`) |

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run tests
npm test

# Type check
npm run typecheck

# Lint
npm run lint
```

## Docker

```bash
# Build image
docker build -t code-review-agent .

# Run container
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd):/code:ro \
  code-review-agent /code
```

## Architecture

```
src/
├── index.ts              # Main exports
├── types.ts              # TypeScript types and JSON Schema
├── agent.ts              # Basic agent example
├── review-agent.ts       # Simple review agent
├── review-structured.ts  # Structured output agent
└── production-agent.ts   # Full production agent
```

## License

Proprietary - KAFAAT
