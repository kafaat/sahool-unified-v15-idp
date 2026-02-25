# Knowledge Graph Service

**Type:** Python / FastAPI
**Port:** 8140
**Version:** 16.0.0
**Layer:** Intelligence (Event Architecture)

## Overview

The Knowledge Graph Service manages relationships between agricultural entities — crops, diseases, and treatments — using an in-memory directed graph built on NetworkX. It provides APIs for entity CRUD, relationship management, shortest-path queries, semantic search, and advanced relationship traversals such as "get all diseases affecting wheat" or "find treatments compatible with date palm." The service is designed for extensibility to PostgreSQL JSONB for production persistence and Neo4j for advanced graph analytics.

## Architecture

```
FastAPI Application (port 8140)
├── Entity Service (CRUD for crops, diseases, treatments)
├── Relationship Service (add, validate, traverse relationships)
└── Graph Query Service (path finding, connected components, search)
    ↓
Data Layer: NetworkX DiGraph (in-memory)
├── Entity storage: dict-based with rich attributes
└── Relationship tracking with confidence scores and evidence

Optional Production Backends:
├── PostgreSQL JSONB (persistent storage, full-text search)
└── Neo4j (advanced graph algorithms, community detection)
```

Current implementation uses in-memory storage suitable for ~1 000 entities and ~10 000 relationships with sub-50 ms query times. Migration to PostgreSQL JSONB or Neo4j is planned for production scale.

## Entity Types

### Crop Entity
```json
{
  "id": "wheat",
  "name_en": "Wheat",
  "name_ar": "القمح",
  "description_en": "Winter cereal grain",
  "growing_season": "winter",
  "family": "Poaceae",
  "attributes": {}
}
```

### Disease Entity
```json
{
  "id": "powdery-mildew",
  "name_en": "Powdery Mildew",
  "name_ar": "البياض الدقيقي",
  "pathogen_type": "fungal",
  "symptoms_en": ["White powder coating", "Leaf distortion"],
  "severity_level": 7,
  "incubation_days": 7
}
```

### Treatment Entity
```json
{
  "id": "sulfur-dust",
  "name_en": "Sulfur Dust",
  "name_ar": "مسحوق الكبريت",
  "treatment_type": "fungicide",
  "active_ingredient": "Sulfur",
  "application_method": "dust",
  "safety_level": 1,
  "cost_per_liter": 5.0
}
```

## Relationship Types

| Type | Direction | Description |
|------|-----------|-------------|
| AFFECTS | Disease → Crop | Disease affects a crop |
| TREATED_BY | Disease → Treatment | Disease treated by a treatment |
| USED_FOR | Treatment → Disease | Treatment used for a disease |
| CAUSES | Factor → Disease | Environmental factor causes disease |
| PREVENTS | Treatment → Disease | Treatment prevents disease |
| ALLEVIATES | Treatment → Disease | Treatment alleviates symptoms |
| REQUIRES | Crop → Condition | Crop requires a growing condition |
| COMPATIBLE | Treatment → Crop | Treatment safe for crop |
| FOLLOWS | Treatment → Treatment | Application sequence |
| RESISTANT_TO | Crop → Disease | Crop has natural resistance |

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Combined health status |

### Crop Entities
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/entities/crops` | GET | List all crops |
| `/api/v1/entities/crops/{crop_id}` | GET | Get crop by ID |
| `/api/v1/entities/crops` | POST | Create crop entity |

### Disease Entities
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/entities/diseases` | GET | List all diseases |
| `/api/v1/entities/diseases/{id}` | GET | Get disease by ID |
| `/api/v1/entities/diseases` | POST | Create disease entity |

### Treatment Entities
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/entities/treatments` | GET | List all treatments |
| `/api/v1/entities/treatments/{id}` | GET | Get treatment by ID |
| `/api/v1/entities/treatments` | POST | Create treatment entity |

### Search
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/entities/search` | GET | Full-text search across all entity types |

### Relationships
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/relationships/affected-crops/{disease_id}` | GET | All crops affected by a disease |
| `/api/v1/relationships/disease-treatments/{disease_id}` | GET | All treatments for a disease |
| `/api/v1/relationships/crop-compatible-treatments/{crop_id}` | GET | Treatments safe for a crop |
| `/api/v1/relationships/diseases-by-crop/{crop_id}` | GET | Diseases affecting a crop |
| `/api/v1/relationships/preventive-treatments/{disease_id}` | GET | Preventive treatments |
| `/api/v1/relationships/path/{source_type}/{source_id}/{target_type}/{target_id}` | GET | Shortest path between entities |
| `/api/v1/relationships/add` | POST | Create a new relationship |
| `/api/v1/relationships/validate` | POST | Validate relationship existence |

### Graph Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/graphs/stats` | GET | Graph statistics (node count, edge count, density) |
| `/api/v1/graphs/search` | GET | Semantic graph search |
| `/api/v1/graphs/path` | GET | Find shortest path with query parameters |

## NATS Events

The Knowledge Graph Service does not currently publish or consume NATS events. It is called synchronously by other services (crop-intelligence-service, advisory-service, copilot-api) via HTTP.

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8140` | No | Service port |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |
| `DATABASE_URL` | — | No | PostgreSQL JSONB (future persistence) |
| `NEO4J_URL` | — | No | Neo4j bolt URL (future analytics) |

No database is required for current in-memory operation.

## Performance Characteristics

| Metric | In-Memory (Current) | PostgreSQL JSONB (Future) |
|--------|---------------------|--------------------------|
| Max nodes | ~1 000 | Millions |
| Max edges | ~10 000 | Tens of millions |
| Path query | < 50 ms | < 200 ms |
| Text search | < 100 ms | < 500 ms |

## Service Integration

| Consumer | Usage |
|----------|-------|
| crop-intelligence-service | Queries disease information and treatment options |
| advisory-service | Gets crop requirements and compatible treatments |
| irrigation-smart | Discovers crop water requirements and disease prevention |
| copilot-api | RAG enrichment with crop-disease-treatment relationships |
| pest-detection-service | Looks up pest-to-crop and pest-to-treatment relationships |

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "knowledge-graph"}
GET /readyz   → {"status": "ok", "graph_nodes": 450, "graph_edges": 1200}
GET /health   → Combined status with graph statistics
```

## Admin Integration Notes

- The admin portal's knowledge management section can use entity endpoints to browse and add crops, diseases, and treatments to the graph.
- `GET /api/v1/relationships/disease-treatments/{disease_id}` powers the "recommended treatments" panel in the field advisory module.
- `GET /api/v1/entities/search?q=rust` enables free-text search across all entity types for the admin knowledge base search bar.
- The graph stats endpoint (`GET /api/v1/graphs/stats`) provides a quick integrity check for the knowledge base — display node/edge counts in the admin system health panel.
- Future migration to Neo4j will enable community detection and similarity-based recommendations; no API changes are planned.
