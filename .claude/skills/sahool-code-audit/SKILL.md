---
name: sahool-code-audit
description: Three-phase code review, audit, and fix workflow for the SAHOOL agricultural platform (Python FastAPI, Node.js NestJS, Flutter, PostGIS, shared contracts). Use when user asks to "review this code", "audit the service", "fix lint errors", "run ruff/mypy/bandit", "check SAHOOL standards", "apply fixops", or pastes a diff/PR for review. Enforces platform-specific rules (health endpoints, NATS subjects, tenant scoping, Pydantic v2, Riverpod, certificate pinning) and routes fixes through code-fix-agent (8162), code-review-service (8102), and /fixops-run.
license: Proprietary
compatibility: Claude Code CLI with repository access. Optional integrations require FixOps CLI, code-fix-agent (port 8162), code-review-service (port 8102), and SAHOOL MCP server (port 8201) for agent delegation.
metadata:
  author: SAHOOL Platform Team
  version: 1.0.0
  mcp-server: sahool-mcp
  category: workflow-automation
  tags:
    - code-review
    - audit
    - fixops
    - sahool-platform
    - multi-language
---

# SAHOOL Code Audit Skill

Three-phase workflow that turns "review this code" into a structured, evidence-based decision with either a concrete fix plan or an applied patch.

## When To Use

Activate this skill when the user:
- Pastes a code snippet, diff, or PR and asks for review
- Says "audit", "fix lint", "run ruff", "check contracts", "apply fixops"
- Requests a pre-merge sanity check on a SAHOOL service
- Asks "is this up to platform standards"

**Do NOT use for**: explaining unfamiliar code, generic programming tutorials, or code review outside the SAHOOL monorepo (use `code-review-generic` skill instead).

---

## The Three Phases

```
Phase 1: REVIEW    → Run tools, collect raw findings
Phase 2: AUDIT     → Classify by SAHOOL severity + domain impact
Phase 3: FIX       → Apply via FixOps, MCP agent, or subagent routing
```

Each phase has a clear gate — do not move forward until the previous phase produces structured output.

---

## Phase 1: Review (Collect Findings)

### 1.1 Detect scope

Identify the affected paths:

| Path pattern | Stack | Tools to run |
|---|---|---|
| `apps/services/*/` (Python) | FastAPI | `ruff`, `mypy`, `bandit` |
| `apps/services/*/` (Node.js) | NestJS | `npm run lint`, `npm run typecheck` |
| `apps/mobile/` | Flutter | `flutter analyze` |
| `shared/` (Python) | Library | `ruff`, `mypy` |
| `packages/shared-types/src/contracts/*` | Contracts | `/check-contracts` slash command |
| `packages/*` (TypeScript) | Workspace | `npm run lint`, `npm run typecheck` |
| `*.sql`, PostGIS migrations | DB | Delegate to `postgis-optimizer` subagent |

### 1.2 Run tools

Prefer the Makefile targets over ad-hoc commands (they match CI):

```bash
# Python
ruff check <path>
ruff format --check <path>
mypy <path>                    # if path has type hints
bandit -r <path>               # security

# Node.js
npm run lint -- <path>
npm run typecheck

# Flutter
flutter analyze <path>

# Platform-specific
/check-contracts               # API contract drift
make fixops                    # FixOps dry-run preview
```

### 1.3 Capture structured output

Collect findings as a list of dicts:

```yaml
- tool: ruff
  code: F401
  file: apps/services/weather-service/src/main.py
  line: 12
  message: "os imported but unused"
  severity_raw: warning
  autofix_available: true
```

If no tools can run (e.g., code pasted without repo context), inspect manually against the checklist in [`references/platform-standards.md`](references/platform-standards.md).

**Gate**: Do not proceed to Phase 2 until you have a finding list (even if empty).

---

## Phase 2: Audit (SAHOOL Severity Classification)

Re-classify tool output using SAHOOL-specific severity, because `ruff W605` and `missing tenant_id` are not the same risk.

### 2.1 Severity matrix (summary — full matrix in [`references/severity-matrix.md`](references/severity-matrix.md))

| SAHOOL Severity | Examples |
|---|---|
| **CRITICAL** | Secrets leaked, auth bypass, SQL injection, missing `tenant_id` in NATS publish, missing RBAC on handler |
| **HIGH** | Contract drift (hardcoded port/error), PHI/dosage handling error, missing cert pinning on mobile Dio client, broken `sahool.{domain}.{action}` subject pattern |
| **MEDIUM** | Pydantic v1 `class Config` in new code, deprecated `@app.on_event`, unstructured logging (f-string instead of `structlog`), missing health endpoints |
| **LOW** | Import order, unused var, docstring absent, line length |

### 2.2 Domain overlays (route to subagent for deep checks)

| Overlay | Subagent | When to invoke |
|---|---|---|
| PostGIS queries, raster ops, PgBouncer constraints | `postgis-optimizer` | Any `*.sql`, GeoAlchemy, or raster handling |
| Arabic strings, RTL, bilingual UI, AraBERT output | `arabic-rtl-tester` | User-facing text, mobile features, advisor content |
| API contracts (ports, error codes, endpoints) | `contract-guard` | Changes under `packages/shared-types/src/contracts/` |

Invoke via the Agent tool with the matching `subagent_type`. See [`references/mcp-integration.md`](references/mcp-integration.md) for MCP-based routing.

### 2.3 Produce audit report

```markdown
## Audit Report — <path>

**Scope**: <files touched>
**Findings**: N total (C critical, H high, M medium, L low)

### Critical
- [CRITICAL] `<file>:<line>` — <description>
  Root cause: <one line>
  Recommended fix: <strategy + target>

### High
...
```

**Gate**: Do not proceed to Phase 3 until every CRITICAL finding has a recommended fix.

---

## Phase 3: Fix (Strategy Selection + Application)

### 3.1 Choose fix strategy

From `shared/ai/auto_fix/FixStrategy`:

| Strategy | Use when |
|---|---|
| `MINIMAL` | Only errors blocking CI; no style rewrites |
| `SAFE` | Auto-fixable tool output; no semantic changes — **default** |
| `COMPREHENSIVE` | Dev branch, apply all suggestions |
| `REFACTOR` | Explicit refactor task with tests in place |

Full matrix in [`references/fix-strategies.md`](references/fix-strategies.md).

### 3.2 Apply via the right channel

| Situation | Tool to invoke |
|---|---|
| Ruff/ESLint auto-fixes, formatting | `/fixops-run` slash command (or `make fixops-run`) |
| Mypy / typing gaps | Manual Edit tool, with fix verified via `mypy` re-run |
| Contract drift | `/check-contracts --fix` if available, else hand-edit + bump `CONTRACT_VERSION` |
| Complex multi-file refactor | Delegate to `code-fix-agent` (port 8162) via MCP `spawn_agent` (see references/mcp-integration.md) |
| Domain-specific (PostGIS, RTL, contracts) | Delegate to specialized subagent |

### 3.3 Verify and audit

After applying any fix:

1. Re-run the original Phase 1 tools — confirm findings resolved
2. Run `make test-unit` for the affected service
3. If Critical findings existed, run `make test-integration`
4. Append fix metadata to the audit report (see output format below)

### 3.4 Final output format

```markdown
## Fix Report

**Strategy applied**: SAFE
**Files modified**: N
**Critical resolved**: X/Y
**High resolved**: X/Y
**Tests run**: <commands + result>
**Audit trail**: <path to audit log or commit SHA>

### Remaining items
- <any finding not auto-fixable with explanation>
```

---

## Examples

### Example 1: Quick lint check

```
User: "Run ruff on shared/ai/auto_fix/ and fix what's safe"

Phase 1: ruff check shared/ai/auto_fix/   → 12 findings (all F401, E501)
Phase 2: All LOW severity. No domain overlay triggered.
Phase 3: Strategy=SAFE. Apply via /fixops-run.
Verify: re-run ruff → 0 findings.
```

### Example 2: Pre-merge audit of a new service

```
User: "Audit apps/services/irrigation-smart/ before merge"

Phase 1: ruff (3) + mypy (2) + bandit (1) + /check-contracts (0) = 6 findings
Phase 2:
  - bandit B608 (SQL injection on line 89) → CRITICAL
  - Missing healthz endpoint → HIGH
  - Pydantic v1 Config → MEDIUM (3x)
  - Line length → LOW (2x)
Phase 3:
  - CRITICAL: Manual Edit with parameterized query, verify with re-run
  - HIGH: Add /healthz per shared.errors_py pattern
  - MEDIUM: Run /fixops-run — 3 fixes applied
  - LOW: /fixops-run handles
Verify: make test-unit SERVICE=irrigation-smart → pass
```

### Example 3: Contract drift

```
User: "Why is user-service failing CI?"

Phase 1: /check-contracts → CONTRACT_VERSION bump missing, new error code not in Dart
Phase 2: HIGH (contract-guard overlay triggered)
Phase 3: Delegate to contract-guard subagent for migration plan.
         Run /sync-dart-contracts to regenerate Dart side.
Verify: /check-contracts → pass.
```

---

## Best Practices

- **Never skip Phase 2**. Raw tool output is noisy; SAHOOL severity re-ranking is where the value is.
- **Prefer SAFE strategy**. COMPREHENSIVE and REFACTOR need explicit user approval because they alter semantics.
- **Always verify after fix**. A fix that breaks tests is worse than the original lint warning.
- **Log critical fixes** to the audit trail (`shared/audit_trail/` or commit body).
- **Delegate, don't duplicate**. `postgis-optimizer`, `arabic-rtl-tester`, `contract-guard` subagents already encode platform expertise.

---

## Troubleshooting

### "Tool not found: ruff/mypy/bandit"
Run `pip install -r requirements/dev.txt` or use the Docker target: `make shell SERVICE=<name>` then run tools inside.

### "/fixops-run says no fixes available"
Your finding list is manual-fix only. Use the Edit tool directly with the reasoning from Phase 2.

### "code-fix-agent (8162) unreachable"
Service may be down. Fall back to local FixOps: `make fixops-run`. Check status: `make service-health` or `/service-health`.

### "Contract drift flagged but no visible change"
The `CONTRACT_VERSION` in `packages/shared-types/src/contracts/index.ts` was not bumped. Invoke `contract-guard` subagent.

### Skill doesn't trigger
Rephrase the request using explicit terms: "review", "audit", "fix", "ruff", "lint", or "fixops". Confirm by asking Claude: "When would you use the sahool-code-audit skill?"

---

## References

- [`references/severity-matrix.md`](references/severity-matrix.md) — Full SAHOOL severity classification
- [`references/fix-strategies.md`](references/fix-strategies.md) — FixStrategy decision tree
- [`references/mcp-integration.md`](references/mcp-integration.md) — spawn_agent, code-fix-agent routing

Platform docs:
- `CLAUDE.md` — Platform overview and commands
- `apps/services/code-fix-agent/README.md` — Fix agent API
- `apps/services/code-review-service/README.md` — Review service API
- `shared/ai/auto_fix/` — FixOps engine internals
