# Knowledge Graph Service

**خدمة الرسم البياني للمعرفة**

A sophisticated graph database service that manages relationships between agricultural entities: crops, diseases, and treatments. The service provides powerful APIs for querying, navigating, and discovering connections within the knowledge graph.

## Overview

The Knowledge Graph Service stores and queries complex relationships in agricultural domain:

- **Crops**: Agricultural crops with properties (growing season, botanical family, etc.)
- **Diseases**: Plant diseases with symptoms, severity, and pathogen information
- **Treatments**: Pesticides and remedies with dosages, safety levels, and efficacy

### Relationship Types

- **AFFECTS**: Disease affects Crop
- **TREATED_BY**: Disease treated by Treatment
- **USED_FOR**: Treatment used for Disease
- **CAUSES**: Environmental factor causes Disease
- **PREVENTS**: Treatment prevents Disease
- **ALLEVIATES**: Treatment alleviates symptoms
- **REQUIRES**: Crop requires condition
- **COMPATIBLE**: Treatments compatible with Crop
- **FOLLOWS**: One treatment follows another
- **RESISTANT_TO**: Crop resistant to Disease

## Features

### Core Capabilities

1. **Entity Management**
   - Create, read, update crops, diseases, and treatments
   - Store rich entity attributes and metadata
   - Support for bilingual content (English/Arabic)

2. **Relationship Management**
   - Define relationships between entities with confidence scores
   - Track evidence and citations for relationships
   - Validate relationship existence

3. **Graph Queries**
   - Find shortest paths between entities
   - Search across all entity types
   - Get related entities by relationship type
   - Discover connected components

4. **Advanced Queries**
   - Get all crops affected by a disease
   - Get all treatments for a disease
   - Get compatible treatments for a crop
   - Get preventive treatments
   - Get diseases affecting a specific crop

### Architecture

Uses **NetworkX** for in-memory graph operations with extensibility to:
- **PostgreSQL JSONB** for production persistence
- **Neo4j** for advanced graph queries and analysis

```
┌─────────────────────────────────────────────────────────┐
│                  Knowledge Graph Service                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           FastAPI Application                    │  │
│  │  - Health checks (/healthz, /readyz)            │  │
│  │  - API v1 endpoints                             │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Service Layer                          │  │
│  │  - EntityService (CRUD)                         │  │
│  │  - RelationshipService (relationships)          │  │
│  │  - KnowledgeGraphService (graph operations)     │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Data Layer (In-Memory)                 │  │
│  │  - NetworkX DiGraph                             │  │
│  │  - Entity storage (dict-based)                  │  │
│  │  - Relationship tracking                        │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                              │
│  Optional Backend:                                    │
│  - PostgreSQL JSONB (production)                     │
│  - Neo4j (advanced analytics)                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

### Health Checks

```bash
GET /healthz     # Liveness probe
GET /readyz      # Readiness probe
GET /health      # Combined health status
```

### Entities

#### Crops
```bash
GET    /api/v1/entities/crops              # List all crops
GET    /api/v1/entities/crops/{crop_id}    # Get specific crop
POST   /api/v1/entities/crops              # Create crop
```

#### Diseases
```bash
GET    /api/v1/entities/diseases           # List all diseases
GET    /api/v1/entities/diseases/{id}      # Get specific disease
POST   /api/v1/entities/diseases           # Create disease
```

#### Treatments
```bash
GET    /api/v1/entities/treatments         # List all treatments
GET    /api/v1/entities/treatments/{id}    # Get specific treatment
POST   /api/v1/entities/treatments         # Create treatment
```

#### Search
```bash
GET    /api/v1/entities/search             # Search entities
```

### Relationships

```bash
GET    /api/v1/relationships/affected-crops/{disease_id}
       # Get all crops affected by a disease

GET    /api/v1/relationships/disease-treatments/{disease_id}
       # Get all treatments for a disease

GET    /api/v1/relationships/crop-compatible-treatments/{crop_id}
       # Get treatments safe for a crop

GET    /api/v1/relationships/diseases-by-crop/{crop_id}
       # Get diseases affecting a crop

GET    /api/v1/relationships/preventive-treatments/{disease_id}
       # Get preventive treatments for a disease

GET    /api/v1/relationships/path/{source_type}/{source_id}/{target_type}/{target_id}
       # Find path between two entities

POST   /api/v1/relationships/add
       # Create new relationship

POST   /api/v1/relationships/validate
       # Validate relationship existence
```

### Graph Operations

```bash
GET    /api/v1/graphs/stats                # Graph statistics
GET    /api/v1/graphs/search               # Search graph
GET    /api/v1/graphs/path                 # Find shortest path
```

## Configuration

### Environment Variables

```bash
# Service
SERVICE_NAME=knowledge-graph
SERVICE_VERSION=1.0.0
PORT=8140

# Logging
LOG_LEVEL=INFO

# Database (Future: PostgreSQL/Neo4j)
DATABASE_URL=postgresql://user:pass@localhost/sahool
NEO4J_URL=bolt://localhost:7687
```

### Docker

```dockerfile
# Build
docker build -t knowledge-graph:latest .

# Run
docker run -p 8140:8140 \
  -e LOG_LEVEL=INFO \
  knowledge-graph:latest
```

## Usage Examples

### Get Crops Affected by a Disease

```bash
curl -X GET "http://localhost:8140/api/v1/relationships/affected-crops/late-blight"
```

Response:
```json
{
  "status": "success",
  "disease_id": "late-blight",
  "affected_crops_count": 2,
  "data": [
    {
      "id": "potato",
      "name_en": "Potato",
      "name_ar": "البطاطس",
      "relationship": {
        "type": "affects",
        "confidence": 0.99
      }
    }
  ]
}
```

### Find Shortest Path Between Entities

```bash
curl -X GET "http://localhost:8140/api/v1/graphs/path?source_type=crop&source_id=wheat&target_type=treatment&target_id=sulfur-dust"
```

### Search for Entities

```bash
curl -X GET "http://localhost:8140/api/v1/entities/search?q=powdery&limit=10"
```

### Create a New Relationship

```bash
curl -X POST "http://localhost:8140/api/v1/relationships/add" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "disease",
    "source_id": "powdery-mildew",
    "target_type": "crop",
    "target_id": "wheat",
    "relationship_type": "affects",
    "confidence": 0.95
  }'
```

## Data Model

### Crop Entity

```python
{
  "id": "wheat",
  "name_en": "Wheat",
  "name_ar": "القمح",
  "description_en": "Winter cereal grain",
  "description_ar": "حبوب القمح الشتوية",
  "growing_season": "winter",
  "family": "Poaceae",
  "attributes": {}
}
```

### Disease Entity

```python
{
  "id": "powdery-mildew",
  "name_en": "Powdery Mildew",
  "name_ar": "البياض الدقيقي",
  "pathogen_type": "fungal",
  "symptoms_en": ["White powder coating", "Leaf distortion"],
  "symptoms_ar": ["طلاء أبيض ناعم", "تشويه الأوراق"],
  "severity_level": 7,
  "incubation_days": 7
}
```

### Treatment Entity

```python
{
  "id": "sulfur-dust",
  "name_en": "Sulfur Dust",
  "name_ar": "مسحوق الكبريت",
  "treatment_type": "fungicide",
  "active_ingredient": "Sulfur",
  "concentration": "100%",
  "application_method": "dust",
  "safety_level": 1,
  "cost_per_liter": 5.0
}
```

### Relationship

```python
{
  "id": "rel-powdery-mildew-wheat-affects",
  "source_type": "disease",
  "source_id": "powdery-mildew",
  "target_type": "crop",
  "target_id": "wheat",
  "relationship_type": "affects",
  "confidence": 0.95,
  "evidence": ["Research paper XYZ", "Field observation"]
}
```

## Integration with Other Services

### Crop Health AI Service
Queries disease information and treatments:
```
crop-health-ai → knowledge-graph → disease info, treatments
```

### Fertilizer Advisor Service
Gets crop requirements and compatible treatments:
```
fertilizer-advisor → knowledge-graph → crop nutrients, treatment compatibility
```

### Irrigation Smart Service
Discovers crop water requirements:
```
irrigation-smart → knowledge-graph → crop water needs, disease prevention
```

## Performance Characteristics

### In-Memory (Current)
- **Nodes**: ~100-1,000 entities
- **Edges**: ~1,000-10,000 relationships
- **Query Time**: <50ms for path finding
- **Search Time**: <100ms for text search

### Production (PostgreSQL JSONB)
- **Nodes**: Millions of entities
- **Edges**: Tens of millions of relationships
- **Query Time**: <200ms for indexed queries
- **Search Time**: <500ms with full-text search

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Run All Tests
```bash
pytest tests/
```

## File Structure

```
knowledge-graph/
├── Dockerfile              # Production Docker image
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── graphs.py           # Graph query endpoints
│   │       ├── entities.py         # Entity management endpoints
│   │       └── relationships.py    # Relationship endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── graph_models.py        # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── graph_service.py       # Core graph operations
│       ├── entity_service.py      # Entity CRUD
│       └── relationship_service.py # Relationship management
└── tests/
    └── test_graph.py
```

## Future Enhancements

1. **PostgreSQL JSONB Backend**
   - Persistent storage
   - Full-text search
   - JSON operators and indexing

2. **Neo4j Integration**
   - Advanced graph algorithms
   - Community detection
   - Pattern matching

3. **Graph Analytics**
   - Centrality measures
   - Community detection
   - Similarity metrics

4. **Machine Learning**
   - Relationship prediction
   - Anomaly detection
   - Link prediction

5. **Caching Layer**
   - Redis for frequently accessed paths
   - LRU cache for searches

## Support

For issues or questions:
- Check `/docs` endpoint for interactive API documentation
- Review logs with `docker logs knowledge-graph`
- Check health with `curl http://localhost:8140/health`

## License

Proprietary - SAHOOL Platform
