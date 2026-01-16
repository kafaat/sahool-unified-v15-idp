# AI Architecture (Sprint 9)

## Overview

SAHOOL's AI architecture follows a layered design that separates concerns and prevents conflicts between ML and Backend teams. Each layer is independently testable and replaceable.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAG Pipeline (Entry Point)                  │
│                    advisor/ai/rag_pipeline.py                   │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌────────────────┐
│   Retriever   │    │  Prompt Engine  │    │  LLM Client    │
│  retriever.py │    │ prompt_engine.py│    │ llm_client.py  │
└───────────────┘    └─────────────────┘    └────────────────┘
        │                      │
        ▼                      ▼
┌───────────────┐    ┌─────────────────┐
│    Ranker     │    │ Context Builder │
│   ranker.py   │    │context_builder.py│
└───────────────┘    └─────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Vector Store Adapter                         │
│          advisor/rag/doc_store.py (Protocol)                    │
│          advisor/rag/qdrant_store.py (Qdrant impl)              │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Ingestion                          │
│                   advisor/rag/ingestion.py                      │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Knowledge/Ingestion Layer

**Files:** `advisor/rag/ingestion.py`

Handles document processing and chunking:

- Text chunking with configurable overlap
- Sentence-boundary aware splitting
- Batch ingestion support

```python
from advisor.rag.ingestion import ingest_document

ingest_document(
    store=vector_store,
    collection="agricultural_kb",
    doc_id="irrigation_guide_001",
    text=document_text,
    source="FAO Irrigation Manual",
)
```

### 2. Vector Store Layer

**Files:** `advisor/rag/doc_store.py`, `advisor/rag/qdrant_store.py`

Abstract protocol for vector stores (Qdrant, Pinecone, etc.):

- Pluggable implementations
- Simple interface: `upsert_chunks`, `search`
- In-memory store for testing

```python
from advisor.rag.qdrant_store import QdrantVectorStore

store = QdrantVectorStore(url="http://localhost:6333")
store.upsert_chunks("kb", chunks)
results = store.search("kb", "wheat irrigation", limit=5)
```

### 3. Retrieval Layer

**Files:** `advisor/ai/retriever.py`

Retrieves relevant chunks from vector store:

- Simple retrieval with k limit
- Threshold-based filtering

### 4. Ranking Layer

**Files:** `advisor/ai/ranker.py`

**Key Feature: Deterministic Ranking**

Ranking is deterministic to prevent flaky tests and unpredictable behavior:

- Primary: Score (descending)
- Secondary: doc_id (alphabetical)
- Tertiary: chunk_id (alphabetical)

```python
from advisor.ai.ranker import rank

# Always produces the same order for same input
ranked_chunks = rank(chunks)
```

### 5. Prompt Engine Layer

**Files:** `advisor/ai/prompt_engine.py`

Template-based prompt rendering:

- Templates stored in `shared/contracts/ai/prompt_templates/`
- Consistent formatting across the codebase
- Easy to update without code changes

### 6. Inference Layer

**Files:** `advisor/ai/llm_client.py`

Abstract LLM interface:

- Provider-agnostic (OpenAI, Claude, local LLMs)
- Easy to swap implementations
- Mock client for testing

### 7. RAG Pipeline

**Files:** `advisor/ai/rag_pipeline.py`

Single entry point orchestrating all layers:

```python
from advisor.ai.rag_pipeline import run_rag
from advisor.ai.rag_models import RagRequest

request = RagRequest(
    tenant_id="tenant-123",
    field_id="field-456",
    question="متى أفضل وقت لري القمح؟",
    locale="ar",
)

response = run_rag(
    req=request,
    store=vector_store,
    llm=llm_client,
    field_context=field_context,
    collection="agricultural_kb",
)

print(response.answer)  # Arabic agricultural advice
print(response.sources)  # ["doc1", "doc2"]
print(response.confidence)  # 0.85
```

## Evaluation

**Files:** `advisor/ai/evaluation.py`

Metrics for measuring RAG quality:

- **Pass@K**: Whether any expected document appears in results
- **Recall**: Proportion of expected documents retrieved
- **Precision**: Proportion of retrieved documents that are relevant
- **F1 Score**: Harmonic mean of precision and recall

```python
from advisor.ai.evaluation import pass_at_k, aggregate_results

score = pass_at_k(
    returned_sources=["doc1", "doc3"],
    expected_doc_ids=["doc1", "doc2"],
)  # Returns 1.0 (doc1 found)
```

## Context Building

**Files:** `advisor/ai/context_builder.py`

Aggregates field data from multiple sources:

- NDVI data from ndvi_engine
- Weather data from weather_core
- Soil analysis data
- Field metadata

```python
from advisor.ai.context_builder import build_field_context

context = build_field_context(
    field={"name": "حقل النخيل", "id": "f123", "crop": "dates"},
    ndvi_summary={"ndvi_mean": 0.65, "trend": "rising"},
    weather={"summary": "حار وجاف"},
    soil={"ph": 7.2, "organic_matter": 2.5},
)
```

## Infrastructure

### Qdrant Setup

```bash
# Start Qdrant locally
docker compose -f infra/qdrant/docker-compose.qdrant.yml up -d

# Access dashboard
open http://localhost:6333/dashboard
```

### Dependencies

Required (in `requirements.txt`):

```
qdrant-client>=1.9.0  # Optional, only for Qdrant adapter
```

## Design Goals

1. **Reduce team conflicts**: Each layer can be developed independently
2. **Prevent drift**: Templates are contracts in version control
3. **Deterministic ranking**: Prevents flaky results
4. **Provider independence**: Easy to swap LLM/vector store providers
5. **Testability**: Each layer has focused unit tests

## Future Enhancements (Sprint 10+)

- Embeddings adapter (sentence-transformers, OpenAI, etc.)
- Explainability layer ("why this recommendation?")
- Feedback collection and quality improvement
- AI monitoring and observability
