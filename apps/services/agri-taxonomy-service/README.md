# agri-taxonomy-service — Agricultural Taxonomy Service (ADR-012)

> **Status:** Phase 3.5 scaffold. The service boots, exposes health/metrics,
> and registers placeholder routes. Domain logic, persistence, and the
> `knowledge-graph` adapter land in Phase 4.

Single source of truth for agricultural taxonomy across the SAHOOL
platform: crops, varieties, diseases, pests, weeds, fertilizers, and the
relations between them.

- **Port:** 8265
- **Kong route:** `/api/v1/taxonomy/*`
- **Layer:** Intelligence
- **ADR:** [docs/adr/ADR-012-agri-taxonomy-service.md](../../../docs/adr/ADR-012-agri-taxonomy-service.md)
- **Client:** [`shared/agri_taxonomy_client/`](../../../shared/agri_taxonomy_client/)

## Responsibilities

| Capability                                | Endpoint (planned)                       |
| ----------------------------------------- | ---------------------------------------- |
| Get one node by stable UUIDv4             | `GET  /api/v1/taxonomy/nodes/{id}`       |
| List nodes by kind / parent               | `GET  /api/v1/taxonomy/nodes?kind=crop`  |
| Search by synonym (Arabic / English / Latin) | `GET  /api/v1/taxonomy/search?q=...`  |
| Forbidden-substance check (used by ADR-013) | `GET  /api/v1/taxonomy/fertilizers/{id}/forbidden` |
| Current released version                  | `GET  /api/v1/taxonomy/version`          |
| Publish a new release (admin)             | `POST /api/v1/taxonomy/releases`         |

## Boundaries

- **Persistence:** delegated to `knowledge-graph` (port 8140). This service
  is *not* a graph DB itself — it owns the **schema** and the **release
  process**, then queries `knowledge-graph` for the data.
- **Hot-reload SLA:** new releases must converge across all consumers
  within 30 s. The service publishes `sahool.taxonomy.released.v{N}` to
  NATS; consumers also poll as a backstop.
- **Identifier policy:** UUIDv4 keys are immutable. Display labels
  (`ar`, `en`, `la`) are mutable and versioned.
- **External vocab cross-refs** (`AGROVOC`, `EPPO`, `Wikidata`) are
  carried as opaque strings in `cross_refs` and are not authoritative.

## Migration plan (Phase 4)

`advisory-service/src/kb/diseases.py` ships an in-memory dict of disease
rules today. Phase 4 migrates that dict into taxonomy releases and
replaces the import in `advisory-service` with a `TaxonomyClient` lookup.
A feature flag (`USE_TAXONOMY_SERVICE=true`) allows side-by-side running
during the cutover.

## Local development

```bash
make dev-infra                # postgres, nats, redis
cd apps/services/agri-taxonomy-service
pip install -r requirements.txt
uvicorn src.main:app --port 8265 --reload
curl http://localhost:8265/healthz
```

## Tests

```bash
pytest apps/services/agri-taxonomy-service/tests/ -v
```
