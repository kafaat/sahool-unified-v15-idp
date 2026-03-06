# ADR-008: AI Architecture & Model Selection

| Item | Details |
|------|---------|
| **Status** | Accepted |
| **Date** | 2026-03-06 |
| **Authors** | SAHOOL AI Team |
| **Reviewers** | Platform Architecture Team |

## Context

SAHOOL is a national agricultural intelligence platform serving the Middle East. We need a robust AI architecture that:

1. Works **offline-first** in low-connectivity environments
2. Supports **Arabic and English** bilingual interaction
3. Provides **domain-specific** agricultural intelligence across 11 domains
4. Scales from **edge devices** (Jetson Orin) to **cloud GPU** clusters
5. Maintains **auditability** and **cost control** for multi-tenant deployments

## Decision

### 1. 12-Layer Architecture

We adopt a 12-layer AI architecture from foundational services to orchestration:

```
L12: Orchestration    - SwarmCoordinator, ConsensusManager, AgentRouter
L11: Agents           - FarmAdvisorAgent, ReAct, Tree-of-Thoughts
L10: UltraRAG 3.0     - Tri-RAG (Dense + Sparse + Knowledge Graph)
L9:  Knowledge Mgmt   - CRAG, AGROVOC, 13 collections, 6-stage pipeline
L8:  Vector Store      - Qdrant/Milvus with unified embeddings
L7:  Context Eng.      - ContextCompressor (3 levels), FarmMemory
L6:  LLM Providers     - 6 providers with circuit breaker failover
L5:  Specialized AI    - CropVision, GraphMemory, Explainability
L4:  Auto-Fix          - Diagnostics, Fixers, Health Checks
L3:  Feedback          - FeedbackCollector, QualityOrchestrator
L2:  Safety            - AIValidator, Guardrails, ToolGuard
L1:  Foundation        - Models Registry (50+ models), Hardware Optimizer
```

### 2. Offline-First LLM Provider Strategy

**Priority order** (lower = higher priority):
- **Priority 0**: Ollama (local CPU/GPU), vLLM (local GPU)
- **Priority 1**: Anthropic Claude (cloud)
- **Priority 2**: OpenAI GPT (cloud)
- **Priority 3**: Google Gemini (cloud)
- **Priority 4**: DeepSeek (cloud)

**Rationale**: Target users are smallholder farmers in areas with unreliable internet. Local models must work without connectivity. Cloud models enhance quality when available.

### 3. Agricultural Models Registry

50+ domain-specific AI models registered across 8 categories:
- General Agriculture (16 models)
- Breeding & Bioscience (10 models)
- Livestock & Veterinary (8 models)
- Remote Sensing & Geospatial (8 models)
- Specialty (9+ models)

**Model selection** uses task-to-capability mapping with Q-learning based routing.

### 4. Knowledge Base Design

- **13 collections** covering all agricultural domains
- **FRESH metadata** framework (Format, Relevance, Expiration, Sensitivity, Hierarchy)
- **AGROVOC** terminology linking (FAO standard)
- **6-stage ingestion**: Extract → Clean → Chunk → Embed → Validate → Store
- **CRAG** (Corrective RAG) for self-correcting retrieval

### 5. Multi-Agent System

- **A2A Protocol** (Linux Foundation standard) for agent communication
- **11 agent categories**: intelligence, advisory, analysis, monitoring, security, IoT, precision, sustainability, market, social, operations
- **Consensus protocols**: Majority, Weighted, Raft, Unanimous, Quorum

## Consequences

### Positive
- Full functionality without internet connectivity
- Comprehensive agricultural domain coverage
- Resilient multi-provider architecture with automatic failover
- Bilingual (Arabic/English) support throughout
- Audit trail and cost tracking for enterprise compliance

### Negative
- Complexity of maintaining 12 layers
- Local models (7B-13B) have lower quality than cloud models
- 50+ registered models require ongoing connector maintenance
- AGROVOC terminology requires manual curation

### Risks
- Model API changes may break connectors
- Local GPU requirements (CUDA 12.1) may not be available on all edge devices
- Arabic NLP quality depends on AraBERT availability

## References

- AgriRegion (arXiv:2512.10114) - Region-aware RAG pattern
- FAO AGROVOC - Agricultural terminology standard
- FRESH Framework - Knowledge organization
- CRAG (Corrective RAG) - Self-correcting retrieval
- A2A Protocol - Linux Foundation agent communication standard
