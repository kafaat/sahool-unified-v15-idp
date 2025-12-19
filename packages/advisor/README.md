# SAHOOL Advisor Package

> AI-powered agricultural advisory system with RAG capabilities

## Modules

| Module | Description |
|--------|-------------|
| `ai/` | LLM client, ranker, prompt engine, RAG pipeline |
| `rag/` | Document store, Qdrant adapter, ingestion |
| `context/` | Context aggregation and service |
| `feedback/` | User feedback collection and analysis |
| `explainability/` | AI decision explainability |
| `monitoring/` | Metrics and monitoring |

## Usage

```python
from packages.advisor.ai import LLMClient
from packages.advisor.rag import QdrantStore
```

## Dependencies

- `qdrant-client` for vector storage
- `openai` or `anthropic` for LLM
- See `requirements.txt` in root

## Consumers

- `kernel-services-v15.3/crop-growth-model/` (multi-agent advisor)
- `kernel-services-v15.3/fertilizer-advisor/`
