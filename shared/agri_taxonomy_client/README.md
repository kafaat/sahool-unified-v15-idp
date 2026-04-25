# shared/agri_taxonomy_client — Polling client for `agri-taxonomy-service` (ADR-012)

> **Status:** Phase 4 — implemented. Polling client, optional NATS-style
> notifier-driven wakeups, and atomic snapshot swap are live. See
> [ADR-012](../../docs/adr/ADR-012-agri-taxonomy-service.md).

In-process client used by every consumer of agricultural taxonomy
(crops, varieties, diseases, pests, weeds, fertilizers).

## Modules

| File          | Responsibility                                                |
| ------------- | ------------------------------------------------------------- |
| `models.py`   | `TaxonomyNode`, `TaxonomyVersion`, `TaxonomyEdge`, `Synonym`  |
| `client.py`   | Polling client with configurable refresh + atomic snapshot swap |

## Hot-reload contract

- Service exposes a SemVer `Taxonomy-Version` header on every response.
- Client polls (or subscribes via NATS to `sahool.taxonomy.released.v{N}`)
  and swaps in the new snapshot atomically once download + checksum verify.
- Convergence target: **< 30 s** across all consumers per ADR-012.

## Boundaries

- **No write methods.** Mutations go through the service's REST API.
- **UUIDv4 keys are stable.** Display labels (Arabic / English / Latin)
  are mutable; identifiers are not.
- The service-side scaffold lives at
  [`apps/services/agri-taxonomy-service/`](../../apps/services/agri-taxonomy-service/)
  (Phase 4 — fully implemented).
