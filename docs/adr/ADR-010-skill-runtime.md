# ADR-010: Incremental Skill Runtime (Registry + Router)

| Item | Details |
|------|---------|
| **Status** | Proposed |
| **Date** | 2026-04-14 |
| **Authors** | SAHOOL Platform Team |
| **Reviewers** | Platform Architecture Team, AI/ML Team |
| **Supersedes** | — |
| **Related** | ADR-008 (AI Architecture), ADR-009 (Claude Code Workflow Integration) |

---

## Context

SAHOOL has built three AI layers independently:

1. **LLM layer** — `llm-orchestrator-service` (port 8164), `copilot-api` (8088), multi-provider routing across Claude, OpenAI, Gemini, DeepSeek.
2. **MCP layer** — `mcp-server` (8201), `shared/mcp/tools.py` with 12 agricultural tools (`fetch_field_data`, `spawn_agent`, `query_agent`, etc.).
3. **Skills layer** — `.claude/skills/` with 30 skill files (22 general-purpose + 7 SAHOOL-specific + 1 Anthropic-compliant `sahool-code-audit`).

Following publication of Anthropic's "Complete Guide to Building Skills for Claude" (January 2026) and internal audit:

### Problems identified

1. **No skill runtime binds these layers**. Skill selection today relies on Claude Code's built-in auto-discovery heuristics (prompt-based, probabilistic). No deterministic routing when multiple skills match.
2. **Skill Explosion risk**. 30 skills is within Anthropic's recommended 20–50 range (guide p. 26), but lacks governance to prevent uncontrolled growth.
3. **Overlapping Skills**. Example: `long-form-summary-compressor` (generic) vs. `context-compression` (SAHOOL-specific) — both trigger on "summarize" or "compress". Today the LLM picks randomly.
4. **No tenant scoping on skills**. SAHOOL is multi-tenant (tenant_id in JWT), but skills are global.
5. **No versioning or drift detection**. Skills are plain files; semantic regressions are invisible.

### Architectural reference

The "LLM + MCP + Skills = Production-grade AI System" equation, decomposed into a 5-layer runtime:

1. Interface Layer — user / API / agent entry
2. **Routing Layer** — skill selection, intent detection ← *missing in SAHOOL*
3. **Skill Layer** — workflows, logic, orchestration ← *files exist, no runtime*
4. Tool Layer — MCP-exposed services
5. Execution & Memory — context, state, audit logs

The missing pieces are (2) and the runtime around (3).

### Non-goals (out of scope for this ADR)

- Replacing Claude Code's native auto-discovery (we augment it, not replace it).
- Replacing MCP or LLM orchestrator.
- Building evaluation/testing automation (covered by future ADR).
- Building skill marketplace or distribution pipeline.

---

## Decision

**Adopt an incremental Skill Runtime in three phases.** This ADR commits only to Phase 1. Phases 2 and 3 require a follow-up ADR based on Phase 1 learnings.

### Phase 1 (this ADR) — Skill Registry + Skill Router

#### 1.1 Skill Registry

A single YAML index: `.claude/skills/index.yaml`

Schema:
```yaml
version: "0.1.0"
skills:
  - name: sahool-code-audit
    path: .claude/skills/sahool-code-audit/
    version: "1.0.0"
    description: <from SKILL.md frontmatter>
    triggers:
      keywords: [review, audit, ruff, mypy, bandit, fixops, lint]
      paraphrases:
        - "check this code"
        - "is this up to platform standards"
    tags: [workflow-automation, code-review]
    category: sahool
    tenant_scope: all          # or list of tenant IDs
    mcp_dependencies: [spawn_agent, query_agent]
    deprecated: false
    owner: ai-team
```

The Registry is a read-only artifact generated from skill frontmatter + explicit metadata. A CI job validates:
- Uniqueness of `name`
- Trigger keyword collisions across skills (warn if >2 skills share a keyword)
- Version bump on description/trigger changes

#### 1.2 Skill Router (FastAPI microservice)

New service: `apps/services/skill-router-service/` (suggested port: **8205**, adjacent to `mcp-server` at 8201).

Endpoints:
```
POST /api/v1/route
  body: { "query": str, "tenant_id": str, "context_hint": str? }
  returns: [
    { "skill": str, "path": str, "confidence": float, "reason": str },
    ...  # top 3
  ]

GET  /api/v1/skills                    # list registered skills
GET  /api/v1/skills/{name}             # skill detail + latest version
GET  /healthz, /readyz, /metrics       # SAHOOL standard probes
```

Matching algorithm (Phase 1 — deliberately simple):
1. Keyword match with weighted scoring
2. Tenant-scope filter
3. Deprecation filter
4. Tie-breaker: most-recently-updated

Embeddings-based semantic match is deferred to Phase 2.

#### 1.3 Integration surface

- **Claude Code**: continues using native auto-discovery. Router is an **optional advisory** callable via MCP tool `route_skill` added to `shared/mcp/tools.py`.
- **LLM Orchestrator** (8164): adds a pre-inference hook that queries `/api/v1/route` when skill hint is missing from the request.
- **CI / Governance**: `governance-ci.yml` workflow runs Registry validation on every PR touching `.claude/skills/`.

### Phase 2 (deferred) — Skill Executor

Triggered by: Phase 1 metrics showing >70% of LLM calls benefit from skill routing, OR production incidents caused by missing skill orchestration.

Scope (for future ADR): step engine, validation gates between steps, MCP call chaining, rollback semantics.

### Phase 3 (deferred) — Full Runtime

Triggered by: Phase 2 validated, multi-tenant skill libraries emerge, skill marketplace requirement.

Scope: Context Manager (progressive disclosure runtime), Evaluation Engine (continuous validation), Cost Manager.

---

## Consequences

### Positive

- **Deterministic skill selection** for the subset of queries that hit the Router. Reduces prompt-based randomness.
- **Governance hook** prevents uncontrolled skill growth (duplicate keywords caught in CI).
- **Tenant scoping** becomes possible — critical for B2B SaaS tier.
- **Migration path** — Phases 2–3 slot in without rework.
- **Low risk** — Router is additive; Claude Code's native auto-discovery keeps working if Router is down.
- **Measurable** — confidence scores and routing decisions logged to Prometheus. Enables evidence-based Phase 2 decision.

### Negative

- **New service to operate** (skill-router-service on 8205). Adds one microservice, one Helm chart, one health check to the 72-service platform.
- **Duplication risk with Claude Code's internals**. We cannot see how Claude Code's native matcher ranks skills, so Router's decisions may occasionally conflict. Mitigated by treating Router as advisory.
- **Registry maintenance burden**. Every new skill needs a registry entry. Mitigated by CI autogen from SKILL.md frontmatter.
- **Does not fix Claude.ai web uploads**. Registry + Router live server-side; they don't help users who upload skills manually to Claude.ai.

### Neutral

- Phase 1 does not add an Executor — so skills are still **executed** by the LLM, not the Router. This is intentional: we validate routing first before committing to execution control.

---

## Alternatives Considered

### Alternative 1: Skill Registry only (no Router)

**Rejected**. Solves Skill Explosion and Overlap problems at governance level only. Does not add any runtime capability. The system remains LLM-driven with no deterministic orchestration. Described as "تحسين إداري، وليس معماري" — administrative improvement, not architectural — in internal review.

### Alternative 2: Full Skill Engine (5 components: Registry, Router, Executor, Context Manager, Evaluation)

**Rejected for now**. Estimated 4–6 weeks of work without production feedback. Violates Goal-Driven Execution principle from `CLAUDE.md`:
> "Strong success criteria let you loop independently. Weak criteria ('make it work') require constant clarification."

Building Executor + Context Manager + Evaluation before observing Phase 1 metrics risks over-engineering components that may not match real usage patterns.

### Alternative 3: Rely solely on Claude Code's native auto-discovery

**Rejected**. Works for individual developer use, but does not provide:
- Tenant scoping (critical for SAHOOL B2B tier)
- CI-level governance
- Server-side integration with `llm-orchestrator-service` (8164) for non-interactive agents
- Observability into skill selection decisions

### Alternative 4: Adopt a third-party skill runtime (e.g., Multica, LangChain, semantic-kernel)

**Rejected**. SAHOOL already has substantial orchestration: `agent-registry` (8160), `ai-agents-core` (8161), `llm-orchestrator-service` (8164), `mcp-server` (8201). Adding a seventh orchestration layer violates Simplicity First. None of the third-party runtimes currently support Anthropic's Skills spec natively as of April 2026.

---

## Mitigations for Known Risks

Per user architectural analysis — four production risks were flagged:

| Risk | Mitigation in Phase 1 |
|---|---|
| **Skill Explosion** | CI validation on PRs; Registry enforces uniqueness; soft-cap of 50 skills with warning |
| **Overlapping Skills** | Router confidence scores expose ambiguity; `tags` and `category` resolve ties; CI warns on keyword collisions |
| **Skill Drift** | `version` field in Registry + CI diff detection; semantic regression requires version bump |
| **LLM Non-Compliance** | Skills validated against `description` spec (Anthropic guide p. 10); future Executor (Phase 2) will enforce step-level validation |

---

## Success Criteria for Phase 1

Measured after 30 days of production use:

1. **Router triggered on ≥30% of LLM orchestrator calls** (Prometheus metric: `skill_router_queries_total`)
2. **Top-1 confidence ≥0.7 on ≥80% of routed queries** (`skill_router_confidence_bucket`)
3. **Zero production incidents** attributable to Router misrouting
4. **Registry validation blocks ≥1 duplicate-keyword PR** in the period (proves governance works)
5. **Tenant-scoped skills** used by ≥2 tenants (proves multi-tenancy value)

If <3 of these 5 criteria are met, Phase 2 is paused and ADR is revisited.

---

## Implementation Plan

**Week 1** — Registry + basic Router
- Day 1–2: `index.yaml` schema, autogen script from SKILL.md frontmatter
- Day 3–4: `skill-router-service` skeleton (FastAPI, per SAHOOL conventions)
- Day 5: CI validation workflow, Backstage catalog entry
- Day 5: Integration test with `llm-orchestrator-service`

**Week 2** — Observability and governance
- Day 6–7: Prometheus metrics, Grafana dashboard
- Day 8: Tenant scoping logic + tests
- Day 9: Documentation, runbook, alerts
- Day 10: Production deployment behind feature flag

**Not in Week 1 or 2**:
- ❌ Executor
- ❌ Context Manager
- ❌ Evaluation Engine
- ❌ Semantic/embedding match

Hooks for these exist in the Router's code (interfaces defined, implementations stubbed).

---

## References

### External
- [Anthropic: The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) (32-page PDF, Jan 2026)
- [Anthropic: Agent Skills documentation](https://docs.anthropic.com/)
- [MCP: Model Context Protocol specification](https://modelcontextprotocol.io/)

### Internal
- `CLAUDE.md` — platform guidelines
- `docs/adr/ADR-008-ai-architecture.md` — existing AI layer decisions
- `docs/adr/ADR-009-claude-code-workflow-integration.md` — Claude Code adoption
- `apps/services/mcp-server/` — MCP server implementation (port 8201)
- `apps/services/llm-orchestrator-service/` — LLM routing (port 8164)
- `shared/mcp/tools.py` — MCP tool catalog
- `.claude/skills/sahool-code-audit/` — first Anthropic-compliant skill

### Prior art
- LangChain `Runnable` abstraction (different scope: per-call, not per-skill)
- semantic-kernel `Planner` (closer but .NET/Python split, doesn't align with Anthropic Skills spec)
- Internal user architectural analysis (Apr 2026 review, "LLM + MCP + Skills Operating Model")

---

## Sign-off Checklist

- [ ] Reviewed by AI/ML team lead
- [ ] Reviewed by Platform Architecture team
- [ ] Security review (tenant scoping, audit trail)
- [ ] Observability review (Prometheus metrics, SLO definition)
- [ ] Cost estimate reviewed (incremental service cost)
- [ ] Success criteria metrics instrumented before deployment

**Promote from Proposed → Accepted only after sign-off checklist is complete.**
