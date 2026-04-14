# skill-router-service

Phase 1 implementation of [ADR-010: Incremental Skill Runtime](../../../docs/adr/ADR-010-skill-runtime.md).

Binds the LLM + MCP + Skills layers with deterministic skill routing.

| Item | Value |
|---|---|
| Port | **8205** |
| Version | 16.0.0 |
| Status | Proposed (ADR-010) |
| Owner | ai-team |

## What it does

Accepts a user query, scores it against every registered skill (from `.claude/skills/index.yaml`), and returns the top-K candidates ranked by confidence.

```
User query → Router → [ranked skills] → LLM executes chosen skill
```

## Endpoints

### `POST /api/v1/route`

```json
Request:
{
  "query": "audit this service for vulnerabilities",
  "tenant_id": "default",
  "top_k": 3
}

Response:
{
  "results": [
    { "skill": "sahool-code-audit", "score": 4.4 },
    { "skill": "code-review-generic", "score": 2.2 }
  ]
}
```

### `GET /api/v1/skills`

Debug/observability — lists every registered skill with tenant + deprecation status.

### `GET /healthz`, `GET /readyz`, `GET /metrics`

Standard SAHOOL probes. `/readyz` returns `degraded` if the registry failed to load.

## Scoring (v0 — deliberately simple)

| Signal | Weight |
|---|---|
| Trigger keyword match (substring) | +2.0 per hit |
| Description word match | +0.2 per word |

Skills with score 0 are excluded from the response. No embeddings, no ML, no ranking learned from usage — those belong to Phase 2 (see ADR-010).

## Data source

The service loads `.claude/skills/index.yaml` **once at startup**. To refresh:

1. Regenerate: `python scripts/generate_skill_registry.py`
2. Restart the service (or redeploy)

Hot reload is intentionally out of scope for v0.

## Local run

```bash
# From repo root
pip install -r apps/services/skill-router-service/requirements.txt
SKILLS_INDEX_PATH=.claude/skills/index.yaml \
  uvicorn apps.services.skill-router-service.app.main:app --reload --port 8205
```

## Docker

Build context is the **repo root** (to include `.claude/skills/index.yaml`):

```bash
docker build -t sahool/skill-router-service:latest \
  -f apps/services/skill-router-service/Dockerfile .

docker run -p 8205:8205 sahool/skill-router-service:latest
```

## Manual test

```bash
curl -X POST http://localhost:8205/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"query":"ruff lint failures","tenant_id":"default"}'
```

Expected: `sahool-code-audit` ranks first (description contains `"ruff"` trigger).

## What this service deliberately does NOT do (yet)

- No hot reload of `index.yaml`
- No caching / persistence
- No auth (add via Kong when exposed externally)
- No embeddings or semantic similarity
- No Skill Execution (still done by the LLM)
- No telemetry beyond Prometheus request counter

See ADR-010 for the deferred Phase 2/3 scope and success criteria for promoting this service to Accepted status.

## Iteration feedback loop

This service exists partly to **surface problems** in the registry:

- Skills returning score 0 → trigger keywords are too weak
- Skills never returned → description lacks trigger phrases
- Wrong skill ranked first → keyword collision, needs disambiguation

Monitor `/api/v1/skills` + production routing metrics, then iterate on SKILL.md frontmatter (not the Router).

## Related

- [ADR-010](../../../docs/adr/ADR-010-skill-runtime.md) — Decision record
- [`scripts/generate_skill_registry.py`](../../../scripts/generate_skill_registry.py) — Registry generator
- [`.claude/skills/index.yaml`](../../../.claude/skills/index.yaml) — Registry artifact
- `apps/services/mcp-server/` — MCP layer (port 8201)
- `apps/services/llm-orchestrator-service/` — LLM layer (port 8164)
