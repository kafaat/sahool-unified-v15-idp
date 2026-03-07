# AI Data Flow Architecture
# بنية تدفق بيانات الذكاء الاصطناعي

**Version**: 16.0.0
**Last Updated**: 2026-03-06

---

## 1. Overview | نظرة عامة

This document describes how data flows through the 12-layer AI architecture in the SAHOOL platform, from user input to agricultural advisory output.

---

## 2. Primary Data Flows

### 2.1 Agricultural Advisory Flow (Main Path)

```
User Query (Arabic/English)
    │
    ▼
┌─────────────────────────────────┐
│ Layer 2: Safety & Validation     │
│ ┌─────────────┐                  │
│ │ AIValidator  │ ← Input sanitization, domain allowlist check
│ │ ToolGuard    │ ← Tool permission enforcement
│ └──────┬──────┘                  │
│        ▼                         │
│ ┌─────────────┐                  │
│ │ Guardrails   │ ← Blocked patterns, PII detection
│ └──────┬──────┘                  │
└────────┼────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Layer 7: Context Engineering     │
│ ┌──────────────────┐             │
│ │ FarmMemory        │ ← Load entity/event/decision history
│ │ ContextCompressor │ ← Level 1/2/3 compression
│ └──────┬───────────┘             │
│        ▼                         │
│ Optimized context (25-80% size)  │
└────────┼────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Layer 12: Orchestration          │
│ ┌────────────┐                   │
│ │ AgentRouter │ ← Q-learning based agent selection
│ └──────┬─────┘                   │
│        ▼                         │
│ ┌──────────────────┐             │
│ │ SwarmCoordinator  │ ← Multi-agent execution (MESH/STAR/PIPELINE)
│ │  └─ Agent 1       │            │
│ │  └─ Agent 2       │            │
│ │  └─ Agent N       │            │
│ └──────┬───────────┘             │
│        ▼                         │
│ ┌──────────────────┐             │
│ │ ConsensusManager  │ ← Aggregate agent results (Majority/Weighted/Raft)
│ └──────┬───────────┘             │
└────────┼────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Layer 10: UltraRAG 3.0           │
│ ┌──────────────────┐             │
│ │ Tri-RAG Retrieval │             │
│ │  ├─ Dense (0.4)   │ ← Vector similarity search
│ │  ├─ Sparse (0.3)  │ ← BM25 keyword search
│ │  └─ KG (0.3)      │ ← Knowledge graph traversal
│ └──────┬───────────┘             │
│        ▼                         │
│ ┌──────────────────┐             │
│ │ CRAG Correction   │ ← Confidence check, re-query if low
│ └──────┬───────────┘             │
│        ▼                         │
│ ┌──────────────────┐             │
│ │ Reranker          │ ← Cross-encoder or RRF reranking
│ └──────┬───────────┘             │
└────────┼────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Layer 6: LLM Provider            │
│ ┌──────────────────┐             │
│ │ LLMProviderManager│             │
│ │  ├─ Ollama (P0)   │ ← Try local first
│ │  ├─ vLLM (P0)     │ ← Local GPU inference
│ │  ├─ Anthropic (P1) │ ← Cloud fallback
│ │  ├─ OpenAI (P2)   │             │
│ │  ├─ Google (P3)   │             │
│ │  └─ DeepSeek (P4) │             │
│ └──────┬───────────┘             │
│        ▼                         │
│ ┌──────────────────┐             │
│ │ CircuitBreaker    │ ← Per-provider failure tracking
│ │ AuditLogger       │ ← Cost tracking, correlation IDs
│ │ MetricsCollector  │ ← Prometheus metrics
│ └──────┬───────────┘             │
└────────┼────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Layer 5: Explainability          │
│ ┌──────────────────┐             │
│ │ ExplainabilityEng │ ← Factor-based explanations (EN/AR)
│ └──────┬───────────┘             │
└────────┼────────────────────────┘
         │
         ▼
    Advisory Response (Bilingual)
    ├─ Recommendation text (EN + AR)
    ├─ Contributing factors
    ├─ Confidence score
    ├─ Knowledge citations
    ├─ Action plan with steps
    └─ Cost/ROI analysis
```

### 2.2 Vision Detection Flow

```
Camera Image (field/drone)
    │
    ▼
┌──────────────────────────────────┐
│ yolo26-vision-service (Port 8150) │
│ POST /api/v1/detect/pest          │
│ POST /api/v1/detect/disease       │
│ POST /api/v1/detect/weed          │
│    ▼                              │
│ YOLO26 Inference (GPU)            │
│    ▼                              │
│ Detection Results                 │
│ {class, confidence, bbox, severity}│
└──────────┬───────────────────────┘
           │
     ┌─────┴─────────────────┐
     │ NATS Event             │
     │ "sahool.vision.*"      │
     ▼                        ▼
┌──────────────┐    ┌──────────────────┐
│ Knowledge    │    │ advisory-service │
│ Base Lookup  │    │ (Port 8093)      │
│ PEST_KNOWLEDGE│    │ IPM Plan         │
│ CROP_KNOWLEDGE│    │ Treatment Rec.   │
└──────┬───────┘    └──────┬───────────┘
       │                    │
       └────────┬───────────┘
                ▼
        ┌──────────────────┐
        │ notification-    │
        │ service (8110)   │
        │ Push to mobile   │
        └──────────────────┘
```

### 2.3 Knowledge Ingestion Flow

```
Source Documents
├─ docs/knowledge-base/crops/ (19 files)
├─ docs/knowledge-base/soils/ (6 files)
├─ docs/knowledge-base/irrigation/ (8 files)
├─ docs/knowledge-base/fertilization/ (8 files)
├─ docs/knowledge-base/diseases/ (4 files)
├─ docs/knowledge-base/weather/ (5 files)
├─ docs/knowledge-base/remote-sensing/ (4 files)
├─ docs/knowledge-base/ai-smart-agriculture/ (3 files)
├─ docs/knowledge-base/precision-farming/ (3 files)
├─ docs/knowledge-base/digital-twin/ (3 files)
└─ docs/knowledge-base/best-practices/ (2 files)
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Stage 1: Extract                                 │
│ MarkdownExtractor / PDFExtractor / HTMLExtractor  │
│ → Raw text + metadata                            │
├─────────────────────────────────────────────────┤
│ Stage 2: Preprocess                              │
│ ArabicTextPreprocessor → Normalize Arabic text   │
│ AgriculturalTermNormalizer → Unify terminology   │
│ MetadataEnricher → Add FRESH/Geospatial metadata │
├─────────────────────────────────────────────────┤
│ Stage 3: Source Validation                       │
│ SourceCredibilityRegistry → Check credibility    │
│ (FAO=5, ICARDA=5, MEWA=4, University=4, Blog=1) │
├─────────────────────────────────────────────────┤
│ Stage 4: Content Validation                      │
│ KnowledgeValidator → Scientific range checks     │
│ (pH 0-14, Kc 0-2, Temp -50~60C, NDVI -1~1)     │
├─────────────────────────────────────────────────┤
│ Stage 5: Region Filtering                        │
│ AgriRegion Filter → Climate/crop/soil compat.    │
│ GeospatialMetadata → Applicable regions          │
├─────────────────────────────────────────────────┤
│ Stage 6: Store (Vector DB)                       │
│ TextChunker → Split into chunks                  │
│ EmbeddingsAdapter → Generate embeddings          │
│ KnowledgeVectorStore → Store in Qdrant/Milvus    │
│ → Return vector IDs for retrieval                │
└─────────────────────────────────────────────────┘
```

### 2.4 Feedback → Training Loop

```
User Interaction
    │
    ▼
┌──────────────────────┐
│ FeedbackCollector     │
│ - Rating (1-5)        │
│ - Thumbs up/down      │
│ - Outcome tracking    │
│ - Corrections         │
└──────────┬───────────┘
           │
     ┌─────┴──────────────────────┐
     ▼                            ▼
┌──────────────────┐    ┌──────────────────┐
│ ExperienceLearner │    │ FeedbackTraining │
│ - Record execution│    │   Pipeline       │
│ - Generate SOPs   │    │ - Export training │
│ - Update confidence│   │   examples       │
│ - Pattern matching │   │ - Trigger retrain│
└──────────────────┘    └──────────┬───────┘
                                   │
                                   ▼
                        ┌──────────────────┐
                        │ ModelTrainer /    │
                        │ GRPO Trainer     │
                        │ - Fine-tune model│
                        │ - Evaluate       │
                        │ - Deploy         │
                        └──────────────────┘
```

### 2.5 Event-Driven Integration (NATS)

```
┌─────────────────────────────────────────────────────────────┐
│                    NATS JetStream                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  sahool.vision.pest_detected      ──→ advisory-service      │
│  sahool.vision.disease_detected   ──→ crop-intelligence     │
│  sahool.vision.critical_alert     ──→ notification-service  │
│  sahool.vision.plant_count_done   ──→ field-intelligence    │
│  sahool.field.created             ──→ vegetation-analysis   │
│  sahool.weather.alert             ──→ advisory, irrigation  │
│  sahool.decision.ipm_plan         ──→ notification-service  │
│  sahool.sensor.image.captured     ──→ pest-detection        │
│                                                              │
│  Tenant-scoped: sahool.tenant.{tid}.{domain}.{action}       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Service Integration Matrix

### 3.1 AI Service Ports

| Service | Port | Layer | Dependencies |
|---------|------|-------|-------------|
| copilot-api | 8088 | L7 App | LLM, RAG, Guardrails |
| ai-advisor | 8112 | L7 App | LLM, Agents, Knowledge |
| ai-chat-assistant | 8260 | L7 App | LLM, Memory |
| advisory-service | 8093 | L7 App | Knowledge, RAG |
| llm-orchestrator | 8220 | L6 Orch | NLP, Satellite, ML, CrewAI |
| agent-registry | 8160 | L12 | Orchestration |
| ai-agents-core | 8161 | L11 | Agents, LLM |
| ai-agents-service | 8130 | L11 | Agents, LLM |
| knowledge-graph | 8140 | L9 | GraphMemory |
| yolo26-vision | 8150 | L4 | GPU, NATS |
| pest-detection | 8125 | L4 | Vision, Knowledge |
| crop-intelligence | 8095 | L4 | Vision, Knowledge |
| mcp-server | 8201 | L10 | UltraRAG, MCP |

### 3.2 Shared Module Dependencies

```
shared/ai/
├── llm_provider.py          ← Used by: copilot-api, ai-advisor, llm-orchestrator
├── embeddings.py            ← Used by: copilot-api, ai-advisor, knowledge
├── knowledge/               ← Used by: advisory-service, copilot-api, ai-advisor
├── ultrarag/                ← Used by: copilot-api, advisory-service, mcp-server
├── models_registry/         ← Used by: llm-orchestrator, agent-registry
├── guardrails/              ← Used by: copilot-api, ai-advisor
├── orchestration/           ← Used by: llm-orchestrator, ai-agents-core
├── context_engineering/     ← Used by: copilot-api, ai-advisor
├── feedback.py              ← Used by: llm-orchestrator, copilot-api
├── crop_vision.py           ← Used by: yolo26-vision, pest-detection
├── explainability.py        ← Used by: advisory-service, copilot-api
└── graph_memory.py          ← Used by: knowledge-graph
```

---

## 4. Offline-First Data Flow

When no internet connectivity is available:

```
User Query
    │
    ▼
[L2: Validation] → Local rules, no cloud API calls
    │
    ▼
[L7: Context] → FarmMemory (local SQLite/file)
    │
    ▼
[L10: RAG] → Local vector store (SQLite-backed)
    │         Local knowledge base (13 collections)
    ▼
[L6: LLM] → Ollama (local, codellama:13b)
    │         vLLM (local GPU, if available)
    │         ✗ No cloud providers
    ▼
[L5: Explain] → Local factor-based explanations
    │
    ▼
Advisory Response (reduced quality, full functionality)
```

---

*Last Updated: 2026-03-06*
