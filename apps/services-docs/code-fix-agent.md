# Code Fix Agent Service

**Port**: 8162 | **Type**: Python (FastAPI) | **Version**: 16.0.0

AI-powered code analysis, automated bug fixing, pull-request review, test generation, and feature implementation agent for the SAHOOL platform.

---

## Overview

`code-fix-agent` exposes a `CodeFixAgent` instance (LEARNING type, SPECIALIST layer, A2A-compliant) via a REST API. The agent perceives code snippets or error logs, selects fix strategies using utility-based decision making, and returns structured bilingual (Arabic/English) reasoning with confidence scores. It learns from submitted feedback to improve fix accuracy over time, accumulating success patterns in memory.

---

## Architecture

```
FastAPI API
    └── CodeFixAgent (singleton, initialized at startup)
        ├── Analyzers   (Python, TypeScript, Dart)
        ├── Fixers      (syntax, security, performance, style)
        ├── Generators  (test suites, feature stubs)
        └── Knowledge   (SAHOOL-specific patterns)
```

NATS connection is optional: if `NATS_URL` is set, the agent connects on startup to publish fix events; the service operates fully without NATS.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe (includes agent status) |
| GET | `/health` | Combined health with agent metrics |
| GET | `/metrics` | Prometheus metrics (plaintext) |

### Agent Operations

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/analyze` | Analyze code for bugs, security issues, performance, style |
| POST | `/api/v1/fix` | Auto-fix errors in a code snippet |
| POST | `/api/v1/review` | Review a PR diff and generate comments |
| POST | `/api/v1/generate-tests` | Generate unit tests with configurable coverage target |
| POST | `/api/v1/implement` | Implement a feature from a specification object |
| POST | `/api/v1/feedback` | Submit fix outcome for reinforcement learning |
| GET | `/api/v1/agent/info` | Agent metadata and current status |

---

## Request/Response Examples

### Analyze Code

```json
POST /api/v1/analyze
{
  "code": "def foo():\n    eval(input())",
  "language": "python",
  "file_path": "src/utils.py"
}
```

### Fix Code

```json
POST /api/v1/fix
{
  "code": "def add(a, b)\n    return a + b",
  "errors": [{"type": "SyntaxError", "line": 1, "message": "expected :"}],
  "language": "python",
  "strategy": "minimal"
}
```

### Agent Response Schema

```json
{
  "success": true,
  "action_type": "fix_code",
  "data": {"fixed_code": "...", "changes": [...]},
  "confidence": 0.92,
  "reasoning": "Applied syntax fix for missing colon",
  "reasoning_ar": "تم تطبيق إصلاح النحو للنقطتين المفقودة",
  "response_time_ms": 145.3,
  "agent_id": "code-fix-agent_001"
}
```

---

## Fix Strategies

| Strategy | Description |
|----------|-------------|
| `minimal` | Smallest safe change; default for `/api/v1/fix` |
| `comprehensive` | Apply all suggested fixes |
| `refactor` | Full restructuring allowed |

---

## Supported Languages

- Python (3.10+)
- TypeScript
- Dart (Flutter)

---

## Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `code_fix_agent_requests_total` | counter | Total requests processed |
| `code_fix_agent_success_rate` | gauge | Success rate percentage |
| `code_fix_agent_response_time_ms` | gauge | Average response time |
| `code_fix_agent_patterns_learned` | gauge | Number of learned fix patterns |

---

## NATS Events

This service optionally connects to NATS. When connected, it may publish fix-result events for CI/CD pipeline integration. No NATS events are consumed.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8162` | HTTP listen port |
| `HOST` | `0.0.0.0` | Bind address |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `ENVIRONMENT` | `production` | `development` enables hot-reload |
| `NATS_URL` | - | Optional NATS server URL |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Comma-separated allowed origins |

---

## Dependencies

- `structlog` for structured JSON logging
- `shared.errors_py` for unified HTTP exception handling (request-ID middleware)
- `nats-py` for optional event publishing
- Local `agent` package: `CodeFixAgent`, `AgentPercept`

---

## Health Endpoints

```
GET /healthz → {"status": "ok", "service": "code-fix-agent", "version": "16.0.0"}
GET /readyz  → {"status": "ok", "agent": "active|idle", "version": "16.0.0"}
```

---

## Related Services

- **code-review-agent** (8145) - Claude SDK-based review agent (Node.js)
- **code-review-service** (8102) - code review service
- **agent-registry** (8160) - registers this agent via A2A protocol
