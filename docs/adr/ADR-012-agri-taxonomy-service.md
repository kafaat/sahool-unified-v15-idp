# ADR-012: Agricultural Taxonomy Service (versioned, hot-reloadable)

## Status

Accepted (2026-04-25, Phase 4 complete: TaxonomyClient with atomic snapshot swap + 8 unit tests; service implementation deferred)

## Context

v3.1 mandates a single source of truth for agricultural taxonomy — crops,
varieties, diseases, pests, weeds, fertilizers — with:

- UUIDv4-stable node identifiers (no string keys)
- Latin binomials and a synonyms graph (multi-lingual aliasing)
- Versioned releases with **hot-reload < 30 s** across all consumers
- Cross-references to ontologies (AGROVOC, EPPO codes, ICD-pest)

v16 already has partial assets:

- `apps/services/advisory-service/src/kb/diseases.py` — seed disease list
- `apps/services/knowledge-graph/` (port 8140) — generic graph service
- `shared/ai/knowledge/` — 13 collections, 30+ trusted sources, 6-stage ingestion

These are not unified, not UUID-keyed, and not hot-reloadable across consumers.
Phase 1 (row #10) reclassified this gap from 🔴 (new from scratch) to 🟠
(new service as a **migration + extension** of existing assets).

## Decision

Create a new service `agri-taxonomy-service` (Python FastAPI) that:

- Owns the canonical taxonomy schema (crops, varieties, diseases, pests, weeds,
  fertilizers, agronomic stages) with UUIDv4 primary keys
- Migrates `advisory-service/src/kb/diseases.py` content into versioned releases
- Re-uses `knowledge-graph` (8140) as the backing storage for node/edge graphs
  (synonyms, cross-references) instead of introducing a new graph DB
- Publishes `sahool.taxonomy.released.v{N}` (tenant-scoped where applicable)
  on every release
- Exposes a SemVer-aligned `Taxonomy-Version` HTTP header on every response
- Provides a polling client in `shared/agri_taxonomy_client/` with a
  configurable refresh window and atomic snapshot swap (the snapshot
  itself is the cache — no separate LRU layer)

Existing consumers (advisory-service, agro-rules, crop-intelligence-service,
yolo26-vision-service) will be migrated incrementally behind a feature flag,
with the legacy `kb/diseases.py` kept as a read-only fallback for two minor
versions per the contract deprecation policy.

## Consequences

### Positive

- One source of truth for taxonomy across all services
- Hot-reload removes the need to redeploy services for taxonomy bumps
- UUIDv4 keys decouple display labels from identity (Arabic / English / Latin
  can change without breaking references)
- Existing knowledge-graph (8140) is leveraged, not duplicated

### Negative

- Net-new service to deploy and operate (≈ +1 pod, +Postgres tables, +Kong route)
- Migration of `advisory-service/src/kb/diseases.py` requires a backfill script
  and a verification window
- Hot-reload < 30 s implies a polling or pub/sub fan-out budget on every consumer

### Neutral

- New port allocated from the SERVICE_PORTS contract (TBD in implementation PR)
- New error codes registered in `packages/shared-types/src/contracts/error-codes.ts`

## Alternatives Considered

### Alternative 1: Keep taxonomy embedded per service

Rejected because the v16 codebase already shows divergence between
`advisory-service`, `crop-intelligence-service`, and `yolo26-vision-service`
class lists. Continued embedding guarantees long-term drift.

### Alternative 2: Reuse `knowledge-graph` (8140) directly

Partially adopted — knowledge-graph remains the storage layer. But its API is
generic (nodes/edges) and lacks the agricultural schema, versioning semantics,
and hot-reload contract. Wrapping it in `agri-taxonomy-service` keeps the
domain boundary clean.

### Alternative 3: Build from scratch ignoring existing assets

Rejected. The Phase 1 verification showed that ~60 % of the taxonomy seed
content already exists; a clean-slate rewrite would discard validated data.

## References

- [Phase 1 Gap Analysis row #10](../architecture/GAP_ANALYSIS_v3.1_vs_v16.md)
- `apps/services/advisory-service/src/kb/diseases.py`
- `apps/services/knowledge-graph/`
- `shared/ai/knowledge/`
- Contract deprecation policy in `CLAUDE.md` ("Contract Deprecation Policy")
