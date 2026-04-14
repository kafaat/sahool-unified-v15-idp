# MCP Integration Reference

How this skill connects to SAHOOL's existing agent and service infrastructure. Corresponds to the "Tool Layer" in the 5-layer architecture.

## Connection topology

```
┌──────────────────────────────────────────────────────┐
│ Claude Code (LLM)                                    │
│  └─ sahool-code-audit skill (this)                   │
└──────┬──────────────────┬──────────────────┬─────────┘
       │                  │                  │
       ▼                  ▼                  ▼
 Local tools       Slash commands      MCP server
 (ruff, mypy,     (/fixops-run,       (port 8201)
  bandit, npm,     /check-contracts,    │
  flutter)         /sync-dart-contracts)│
                                        ▼
                                   spawn_agent, query_agent
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ code-fix-agent     │ port 8162
                              │ code-review-service│ port 8102
                              │ code-review-agent  │ port 8145
                              │ agent-registry     │ port 8160
                              └────────────────────┘
```

## When to use each channel

| Finding scope | Preferred channel | Why |
|---|---|---|
| Single file, auto-fixable lint | Local tool + Edit | Fastest, no network |
| Multi-file same service, auto-fixable | `/fixops-run` slash command | Uses FixOps engine, audit logged |
| Contract drift | `/check-contracts` + `/sync-dart-contracts` | Official contract tooling |
| Complex multi-service refactor | MCP `spawn_agent` → `code-fix-agent` | Full agent execution, isolated workspace |
| Semantic review ("is this idiomatic") | MCP `spawn_agent` → `code-review-agent` | LLM-based review, context-aware |
| Pure automation (CI pipeline) | HTTP direct to service on 8102 / 8162 | No skill overhead |

## Invoking MCP tools from the skill

The skill does not execute MCP calls itself — Claude does. The skill tells Claude *when* to request an MCP call.

### Pattern 1: Spawn code-fix-agent for complex fixes

When Phase 2 audit reveals findings that span multiple files and require semantic reasoning (not just lint):

```
User: "Fix all Pydantic v1 usage across apps/services/ and ensure tests still pass"

Skill directs Claude to:
1. Identify affected files via ruff UP rule
2. Invoke MCP tool via the Agent tool or direct HTTP:
   POST http://sahool-mcp:8201/mcp
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "spawn_agent",
       "arguments": {
         "agent_type": "code-fix-agent",
         "task": "Migrate Pydantic v1 models to v2 in specified files",
         "files": [...],
         "strategy": "COMPREHENSIVE",
         "verify_tests": true
       }
     }
   }
3. Poll query_agent until status=completed
4. Review agent's diff before applying
```

`spawn_agent` and `query_agent` are defined in `shared/mcp/tools.py`.

### Pattern 2: Query code-review-agent for second opinion

When the user asks "is this idiomatic SAHOOL code" or the finding is ambiguous:

```
Invoke code-review-agent via MCP spawn_agent with:
  agent_type: "code-review-agent"
  task: "Review <file> for SAHOOL platform compliance"
  context: <paste of file or diff>

The agent returns structured findings that the skill merges with local Phase 1 output.
```

### Pattern 3: Direct HTTP to code-review-service (no MCP)

For scripted / CI usage, bypass MCP:

```bash
curl -X POST http://code-review-service:8102/api/v1/review \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repo": "...", "pr_number": 123}'
```

Use this when the skill is invoked by a non-interactive agent (GitHub Action, webhook).

## Fallback behavior

If MCP server is unreachable:

1. Check health: `/service-health` slash command
2. If MCP is down but local tools work → continue with Phase 1 & 2 manually
3. For Phase 3:
   - SAFE strategy: fall back to `make fixops-run`
   - COMPREHENSIVE/REFACTOR: abort and request user decision

Never silently skip MCP — always report "MCP unavailable, falling back to local" in the audit report.

## Security notes

- MCP calls inherit the invoking user's `tenant_id` and JWT. Do not bypass auth.
- `code-fix-agent` runs in an isolated workspace per task (see service README). Do not pass secrets in the task description.
- Audit all MCP invocations via `shared/audit_trail/` (automatic for production).
- For `CRITICAL` findings (secrets, auth), NEVER delegate to automated agents — require explicit human fix.

## Related services

| Service | Port | Role |
|---|---|---|
| `mcp-server` | 8201 | JSON-RPC / SSE MCP endpoint |
| `code-fix-agent` | 8162 | Autonomous code fixing with strategies |
| `code-review-service` | 8102 | REST API for review requests |
| `code-review-agent` | 8145 | NestJS LLM-based review agent |
| `agent-registry` | 8160 | Agent discovery and routing |
| `llm-orchestrator-service` | 8164 | Multi-provider LLM routing |

See `apps/services-docs/service-dependencies.md` for the full dependency matrix.
