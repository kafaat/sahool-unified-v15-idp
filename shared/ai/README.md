# shared/ai — SAHOOL AI Module | وحدة الذكاء الاصطناعي لمنصة سهول

**Version**: 2.0.0 | **Python**: >=3.11 | **Files**: 82 Python files

Central AI infrastructure for the SAHOOL agricultural platform. Provides everything from
offline-first LLM routing and vector search to automated code fixing, multi-agent
orchestration, computer vision, and full observability — all with bilingual (Arabic/English)
output and offline-first design principles.

---

## Directory Structure

```
shared/ai/
├── __init__.py                  # Unified public API (all exports, availability flags)
│
├── Core LLM & Embeddings
│   ├── llm_provider.py          # Multi-provider LLM manager (failover, cost tracking)
│   ├── code_llm_provider.py     # Code-specialized LLM (completion, review, fix, tests)
│   ├── ollama_client.py         # Local Ollama client (offline-first)
│   ├── embeddings.py            # Unified embedding adapter (4 providers)
│   ├── huggingface_provider.py  # Arabic & multilingual embeddings via HuggingFace
│   ├── ot_embeddings.py         # OpenTelemetry-instrumented embeddings
│   └── vector_store.py          # Persistent vector DB (SQLite/memory backends)
│
├── AI Safety & Reliability
│   ├── validation.py            # Prompt injection & output safety validation
│   ├── circuit_breaker.py       # Circuit breaker for external LLM services
│   ├── audit.py                 # Structured AI audit logging with cost tracking
│   ├── metrics.py               # Prometheus-compatible AI metrics
│   └── observability.py         # Sentry + OpenTelemetry + CI/CD integration
│
├── Agricultural Intelligence
│   ├── crop_vision.py           # Computer vision: disease, pest, growth stage, yield
│   ├── explainability.py        # "Why this recommendation?" explanations (bilingual)
│   ├── feedback.py              # User feedback collection & analysis
│   └── graph_memory.py          # Graph-based knowledge store (Cognee-inspired, ECL)
│
├── Context Engineering
│   └── context_engineering/
│       ├── compression.py       # Token-efficient context compression (3 levels)
│       ├── memory.py            # Persistent farm memory management
│       └── evaluation.py        # LLM-as-Judge advisory quality evaluation
│
├── Auto-Fix Engine
│   └── auto_fix/
│       ├── engine.py            # Main orchestration engine
│       ├── diagnostics.py       # Multi-tool code analysis (Ruff, ESLint, Mypy, Bandit)
│       ├── fixers.py            # Automated fix application with rollback
│       ├── models.py            # Data models (Diagnostic, CodeFix, AuditEntry)
│       ├── auto_audit.py        # Auto-audit integration
│       ├── batch_processor.py   # Async batch diagnostics
│       ├── diagnostic_cli.py    # CLI interface (python -m shared.ai.auto_fix.diagnostic_cli)
│       ├── fix_learning.py      # Learning from fix history
│       ├── frontend_diagnostics.py  # ESLint/TypeScript diagnostics
│       └── health_check.py      # Platform health checks
│
├── Agent Orchestration
│   └── orchestration/
│       ├── router.py            # Q-Learning inspired agent routing
│       ├── swarm.py             # Multi-agent swarm coordination
│       ├── consensus.py         # Distributed consensus (Majority, Raft, Quorum)
│       └── memory.py            # Collective memory with LRU cache
│
├── Agricultural Agents
│   └── agents/
│       ├── base.py              # Base agent class, capabilities, tool use
│       ├── farm_advisor.py      # Main agricultural advisor agent
│       ├── agricultural_research.py  # Multi-source research with citation tracking
│       ├── weather_agent.py     # Weather analysis agent
│       ├── market_agent.py      # Market price agent
│       ├── planner.py           # Seasonal planning agent
│       ├── react_agent.py       # ReAct pattern (Reasoning + Acting)
│       ├── tree_search_agent.py # Tree-of-Thoughts for complex problems
│       ├── memory_system.py     # Multi-level agent memory
│       ├── semantic_memory_enhanced.py  # Enhanced semantic memory
│       ├── feedback_loop.py     # Agent feedback and learning loops
│       └── examples.py          # Usage examples
│
├── UltraRAG
│   └── ultrarag/
│       ├── pipeline.py          # Main RAG orchestration engine
│       ├── retriever.py         # Adaptive/Dense/Hybrid/KG/Sparse/TriRAG retrievers
│       ├── generator.py         # Ollama, template, and composite generators
│       ├── reranker.py          # Result reranking
│       ├── knowledge_base.py    # Chunking and KB management
│       ├── mcp_tools.py         # MCP server tool definitions
│       ├── models.py            # Pipeline data models
│       ├── workflow.py          # Workflow orchestration
│       ├── providers/           # Provider integrations
│       └── workflows/           # Pre-built workflow definitions
│
├── Guardrails
│   └── guardrails/
│       ├── tool_guard.py        # Tool call allowlist enforcement
│       ├── allowlists.py        # Domain, tool, and pattern allowlists
│       └── policy.py            # Configurable guard policy
│
├── Agricultural AI Models Registry
│   └── models_registry/
│       ├── registry.py          # 50+ agricultural AI model catalogue
│       ├── integrator.py        # Model selection and routing
│       ├── connector.py         # API connectors (ShengNong, CropWizard, AgroGPT, etc.)
│       └── models.py            # Registry data models
│
├── Learning & Optimization
│   ├── experience_learning.py   # Experience-based SOP generation (Acontext-inspired)
│   ├── model_training.py        # Fine-tuning via Ollama Modelfiles + LoRA/QLoRA
│   ├── grpo_trainer.py          # GRPO/DAPO/Dr.GRPO reinforcement learning trainer
│   └── hardware_optimizer.py    # Hardware-aware inference optimization
│
├── Quality Orchestration
│   ├── quality_orchestrator.py  # Automated quality management with auto-audit
│   └── tool_registry.py         # Dynamic tool registry for AI agents
│
└── Image Generation
    └── diffusion/
        ├── __init__.py
        └── advisory.py          # Diffusion-based agricultural image generation
```

---

## Key Components

### 1. LLM Provider Manager | مدير مزودي اللغة

Multi-provider LLM routing with automatic failover, circuit breaking, and cost tracking.
Ollama (local) has highest priority to support offline-first operation.

```python
from shared.ai import get_llm_manager, LLMProvider, generate_text

# Simple generation (uses priority chain: Ollama → Claude → OpenAI → Gemini → DeepSeek)
response = await generate_text("What causes wheat rust?")
print(response.text)

# Explicit provider selection with fallback to Ollama
response = await generate_with_ollama_fallback(
    prompt="Irrigation schedule for wheat at tillering stage",
    prefer_cloud=True,
)

# Full control
manager = get_llm_manager()
response = await manager.generate(
    prompt="...",
    provider=LLMProvider.ANTHROPIC,  # OLLAMA | ANTHROPIC | OPENAI | GOOGLE | DEEPSEEK
    temperature=0.3,
    max_tokens=2048,
)
print(f"Cost: ${response.cost_usd:.4f} | Tokens: {response.total_tokens}")
```

### 2. Embeddings Adapter | محول التضمينات

Unified interface across four embedding providers with caching and offline-first defaults.

```python
from shared.ai import get_embeddings_adapter, EmbeddingConfig, EmbeddingProvider

# Default: local sentence-transformers (offline-first)
adapter = get_embeddings_adapter()

result = await adapter.embed("wheat irrigation schedule")
print(f"Dimension: {result.dimension}, Latency: {result.latency_ms}ms")

# Batch embedding
results = await adapter.embed_batch([
    "Wheat irrigation schedule",
    "جدول ري القمح",
    "Nitrogen fertilizer application",
])

# Semantic similarity
score = await adapter.similarity("wheat disease", "أمراض القمح")
print(f"Cross-lingual similarity: {score:.2f}")

# Arabic-optimized provider (AraBERT family)
from shared.ai import get_huggingface_provider, get_best_arabic_model
provider = get_huggingface_provider()
model = get_best_arabic_model()  # Returns best available Arabic model
```

### 3. Vector Store | مخزن المتجهات

Persistent vector database for RAG and semantic search, with SQLite and in-memory backends
(offline-first; Qdrant/Pinecone pluggable as future backends).

```python
from shared.ai import get_vector_store, VectorDocument, VectorStoreConfig, VectorStoreBackend

store = get_vector_store(VectorStoreConfig(
    backend=VectorStoreBackend.SQLITE,
    storage_path="/data/vectors/sahool.db",
    dimension=384,  # all-MiniLM-L6-v2
))

# Add documents
await store.add_documents("advisory_kb", [
    VectorDocument(
        id="doc-001",
        content="Wheat requires 25 ppm nitrogen at tillering stage",
        embedding=[...],
        metadata={"crop": "wheat", "stage": "tillering"},
    )
])

# Semantic search
results = await store.search("advisory_kb", query_embedding=[...], top_k=5)
for r in results:
    print(f"[{r.score:.3f}] {r.document.content}")
```

### 4. Crop Vision Analyzer | محلل صور المحاصيل

AI-powered computer vision for agricultural image analysis.

```python
from shared.ai import get_crop_vision_analyzer, CropType, analyze_crop_image

analyzer = get_crop_vision_analyzer()

# Full analysis from image path or base64
result = await analyze_crop_image(
    image_path="/images/field_003.jpg",
    crop_type=CropType.WHEAT,
)

# Disease detection
print(result.disease_detections)
# [DiseaseDetection(disease=WHEAT_RUST, confidence=0.87, severity=HIGH,
#   affected_area_percent=23.5, treatment_recommendation="Apply tebuconazole...")]

# Quick convenience wrappers
disease = await detect_crop_disease(image_path="/images/leaf.jpg", crop_type=CropType.TOMATO)
pests = await detect_crop_pests(image_path="/images/field.jpg", crop_type=CropType.WHEAT)

# Growth stage, yield estimate, NDVI also available in VisionAnalysisResult
print(result.growth_stage_detection)
print(result.yield_estimate)
print(result.ndvi_analysis)
```

### 5. Auto-Fix Engine | محرك الإصلاح التلقائي

Automated multi-tool code diagnostics and fixing with full audit trail.

```python
from shared.ai import AutoFixEngine, FixStrategy, quick_diagnose, quick_fix

# Quick diagnostic
report = await quick_diagnose("apps/services/user-service/src/")
print(f"Issues: {report.total_diagnostics} | Auto-fixable: {report.fixable_count}")

# Quick fix with SAFE strategy
report, results = await quick_fix("shared/", strategy=FixStrategy.SAFE)
fixed = sum(1 for r in results if r.success)
print(f"Fixed {fixed} issues")

# Full control
engine = AutoFixEngine(working_dir="/repo", audit_enabled=True, dry_run=False)
report = await engine.diagnose(
    paths=["apps/", "shared/"],
    tools=["ruff", "mypy", "bandit"],  # Also: "eslint", "dart"
)
plan = await engine.generate_fix_plan(report, strategy=FixStrategy.COMPREHENSIVE)
results = await engine.apply_fix_plan(plan, report)

# CLI usage
# python -m shared.ai.auto_fix.diagnostic_cli --all --fix --strategy safe
```

| Strategy | Description |
|----------|-------------|
| `MINIMAL` | Safest subset only (formatting) |
| `SAFE` | All auto-fixable without logic changes |
| `COMPREHENSIVE` | Apply all suggested fixes |
| `REFACTOR` | Full restructuring allowed |

### 6. Context Engineering | هندسة السياق

Three modules for managing LLM context efficiently in agricultural advisory workflows.

```python
from shared.ai import ContextCompressor, CompressionStrategy, FarmMemory, RecommendationEvaluator

# Compress verbose farm data to fit context windows
compressor = ContextCompressor()
result = compressor.compress(
    text="Field FIELD-003 covers 8.5 hectares of winter wheat...",
    strategy=CompressionStrategy.LEVEL_2,  # LEVEL_1 (80%) | LEVEL_2 (50%) | LEVEL_3 (25%)
)
print(f"Ratio: {result.compression_ratio:.1%} | {result.compressed_text}")

# Persistent farm memory
memory = FarmMemory(farm_id="FARM-001")
await memory.store_event("treatment", {
    "field_id": "FIELD-003", "crop": "wheat",
    "product": "Urea 46%", "rate_kg_ha": 46,
})
history = await memory.query_similar(crop="wheat", issue="nitrogen_deficiency")

# LLM-as-Judge evaluation of AI advisories
evaluator = RecommendationEvaluator()
result = evaluator.evaluate(
    advisory_text="Apply 46 kg/ha Urea at early morning...",
    advisory_type="fertilizer",
    field_context={"crop": "wheat", "stage": "tillering"},
)
print(f"Score: {result.overall_score:.2f}/5.0 | Grade: {result.grade}")
# Dimensions: accuracy (30%), relevance (25%), actionability (20%), timeliness (15%), safety (10%)
```

### 7. Agent Orchestration | تنسيق الوكلاء

Multi-agent swarm coordination, Q-Learning routing, and distributed consensus.

```python
from shared.ai import (
    AgentRouter, AgentProfile, AgentCapability,
    SwarmCoordinator, SwarmConfig, SwarmTopology,
    ConsensusManager, MajorityVoting,
    CollectiveMemory,
)

# Register agents with capability profiles
router = AgentRouter()
router.register_agent(AgentProfile(
    agent_id="crop_advisor",
    name="Crop Advisor",
    name_ar="مستشار المحاصيل",
    capabilities=[AgentCapability.CROP_ANALYSIS, AgentCapability.DISEASE_DETECTION],
))

# Route a task to the best agent (Q-Learning adaptive routing)
decision = await router.route(task)

# Swarm execution (parallel multi-agent)
coordinator = get_swarm_coordinator()
config = SwarmConfig(topology=SwarmTopology.MESH, max_agents=5)
result = await coordinator.execute(task, config=config)

# Consensus across agents (Majority / Weighted / Raft / Quorum / Unanimous)
manager = get_consensus_manager()
consensus = await manager.reach_consensus(
    proposals=agent_responses,
    protocol=MajorityVoting(),
)
print(f"Agreed: {consensus.agreed_value} | Confidence: {consensus.confidence:.2%}")
```

### 8. UltraRAG | نظام الاسترداد المتقدم

Production-grade RAG system with multiple retrieval strategies and MCP integration.

```python
from shared.ai.ultrarag import RAGPipeline, RAGRequest, RetrievalStrategy

pipeline = RAGPipeline.from_config("config/rag-pipeline.yaml")

result = await pipeline.run(RAGRequest(
    query="ما هي أعراض صدأ القمح؟",  # Arabic: wheat rust symptoms
    strategy=RetrievalStrategy.ADAPTIVE,   # DENSE | SPARSE | HYBRID | ADAPTIVE | TRI_RAG
    top_k=5,
    rerank=True,
))
print(result.generated_answer)
print(result.retrieved_chunks)  # Source attribution included
```

Available retrievers: `DenseRetriever`, `SparseRetriever`, `HybridRetriever`,
`AdaptiveRetriever`, `TriRAGRetriever`, `KnowledgeGraphRetriever`.

### 9. Agricultural AI Models Registry | سجل نماذج الذكاء الاصطناعي الزراعي

Catalogue and routing layer for 50+ specialized agricultural AI models from global
institutions (China Agricultural University, NCSA/UIUC, MBZUAI, NASA/IBM, etc.).

```python
from shared.ai import get_registry, get_integrator, TaskType, discover_models

registry = get_registry()

# Browse models
models = list_featured_models()         # Flagship models
arabic_models = list_arabic_supported_models()  # Arabic-capable models
oss_models = list_open_source_models()  # Open-source only

# Intelligent model selection for a task
integrator = get_integrator()
selection = await get_best_model(
    task_type=TaskType.DISEASE_DETECTION,
    crop_type="wheat",
    prefer_arabic=True,
    prefer_open_source=True,
)

# Call selected model
result = await call_agri_model(selection.model_id, payload={"image": "..."})

# Compare models head-to-head
comparison = await compare_agri_models(
    model_ids=["shengnong-3.0", "cropwizard", "agrogpt"],
    task_type=TaskType.CROP_ADVISORY,
)
```

### 10. AI Safety | سلامة الذكاء الاصطناعي

Three complementary safety layers.

```python
# Layer 1: Input/output validation
from shared.ai import validate_prompt, validate_response, is_safe_prompt

if not is_safe_prompt(user_input):
    ...  # Blocked: prompt injection / jailbreak / PII

result = validate_prompt(user_input, level=ValidationLevel.MODERATE)
for issue in result.issues:
    print(f"[{issue.severity}] {issue.category}: {issue.description}")

# Layer 2: Tool call guardrails
from shared.ai.guardrails import guard_tool_call, ToolCallContext

decision = guard_tool_call(ToolCallContext(
    tool_name="execute_sql",
    arguments={"query": "DROP TABLE users"},
    agent_id="farm_advisor",
))
# decision.allowed == False  (DROP is in DANGEROUS_COMMANDS)

# Layer 3: Circuit breaker for external services
from shared.ai import get_anthropic_circuit_breaker

cb = get_anthropic_circuit_breaker()  # Pre-configured for Anthropic
# Also: get_ollama_circuit_breaker(), get_openai_circuit_breaker()
result = await cb.call(lambda: llm_client.generate(prompt))
```

### 11. Graph Memory | الذاكرة التخطيطية

ECL (Extract → Cognify → Load) pipeline for building agricultural knowledge graphs.

```python
from shared.ai import get_graph_memory, cognify, memify, graph_search, EntityType

memory = get_graph_memory()  # In-memory
# or
memory = get_persistent_graph_memory("/data/farm_graph.db")

# Add entities via ECL pipeline
await cognify(memory, [
    {"type": EntityType.FIELD, "id": "FIELD-003", "area_ha": 8.5, "crop": "wheat"},
    {"type": EntityType.TREATMENT, "product": "Urea 46%", "rate": 46, "date": "2026-01-14"},
])

# Semantic + relationship search
results = await graph_search(memory, "nitrogen deficiency treatment wheat")
for r in results:
    print(f"[{r.score:.3f}] {r.entity.type}: {r.entity.id}")
```

### 12. Audit Logging | تسجيل التدقيق

Structured audit trail for all AI operations with cost tracking.

```python
from shared.ai import get_audit_logger, log_agent_call, AuditEventType, LLM_COSTS

logger = get_audit_logger()

# Log agent call with cost
await log_agent_call(
    agent_id="farm_advisor",
    provider="anthropic",
    model="claude-3-haiku-20240307",
    prompt_tokens=512,
    completion_tokens=256,
    success=True,
    metadata={"field_id": "FIELD-003", "tenant_id": "tenant-001"},
)

# Cost reference (USD per 1K tokens)
print(LLM_COSTS["anthropic"]["claude-3-haiku-20240307"])  # {"input": 0.00025, "output": 0.00125}

# Cost summary
summary = await get_cost_summary(tenant_id="tenant-001", days=30)
```

---

## Availability Flags

Some components require optional dependencies. Check flags before use:

```python
from shared.ai import (
    LLM_MANAGER_AVAILABLE,    # requires: httpx
    OLLAMA_AVAILABLE,         # requires: httpx
    TRAINING_AVAILABLE,       # requires: httpx
    CODE_LLM_AVAILABLE,       # requires: httpx + llm_provider
    ORCHESTRATION_AVAILABLE,  # requires: orchestration subpackage
    MODELS_REGISTRY_AVAILABLE,
    TOOL_REGISTRY_AVAILABLE,
    QUALITY_ORCHESTRATOR_AVAILABLE,
    OBSERVABILITY_AVAILABLE,  # requires: sentry-sdk, opentelemetry
)

if OLLAMA_AVAILABLE:
    from shared.ai import OllamaClient, analyze_code_with_ollama
```

---

## Environment Variables

### LLM Providers

```bash
# Ollama (local, offline-first — highest priority)
OLLAMA_BASE_URL=http://localhost:11434      # Default
OLLAMA_MODEL=codellama:13b                 # Default model
OLLAMA_DEFAULT_MODEL=codellama:13b
OLLAMA_TIMEOUT=120

# Cloud providers (fallback when Ollama unavailable)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-haiku-20240307

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash

DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-chat
```

### Embeddings

```bash
# HuggingFace (Arabic NLP)
HUGGINGFACE_API_TOKEN=hf_...
# Embeddings default: sentence-transformers/all-MiniLM-L6-v2 (local, no key needed)
```

### Auto-Fix Engine

```bash
AUTO_FIX_ENABLED=true
AUTO_FIX_DRY_RUN=false          # Set true to preview without applying
AUTO_FIX_AUDIT_ENABLED=true
AUTO_FIX_MAX_FILES=100
```

### Observability

```bash
SENTRY_DSN=https://...@sentry.io/...
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=sahool-ai
```

### Vector Store

```bash
VECTOR_STORE_PATH=/data/vectors/sahool.db   # SQLite backend path
VECTOR_STORE_BACKEND=sqlite                 # sqlite | memory
```

---

## Dependencies

### Always Required (no extras)

These are available with a standard Python 3.11 install and platform dependencies:

| Package | Purpose |
|---------|---------|
| `pydantic` | Data validation |
| `structlog` | Structured logging |

### Optional — install as needed

| Extra | Packages | Enables |
|-------|----------|---------|
| LLM | `httpx>=0.27` | `llm_provider`, `ollama_client`, `model_training`, `code_llm_provider` |
| Embeddings | `sentence-transformers>=3.0` | Local sentence embedding (offline-first) |
| Embeddings (Arabic) | `transformers>=4.40`, `torch>=2.0` | HuggingFace Arabic models |
| Vision | `Pillow>=10.0` | `crop_vision` image preprocessing |
| Observability | `sentry-sdk>=2.0`, `opentelemetry-api>=1.20` | `observability` module |
| RAG | `structlog>=24.0` | `ultrarag` pipeline |
| Training (RL) | `torch>=2.0` | `grpo_trainer` |

Install all optional dependencies for full functionality:

```bash
pip install httpx sentence-transformers Pillow structlog sentry-sdk opentelemetry-api
```

---

## Integration Points

### Services that consume `shared/ai`

| Service | Components Used |
|---------|----------------|
| `copilot-api` (port 8088) | `llm_provider`, `ultrarag`, `embeddings`, `vector_store` |
| `advisory-service` (port 8093) | `explainability`, `feedback`, `crop_vision` |
| `code-fix-agent` (port 8162) | `auto_fix`, `code_llm_provider`, `quality_orchestrator` |
| `ai-agents-core` (port 8161) | `agents`, `orchestration`, `graph_memory` |
| `llm-orchestrator-service` (port 8164) | `llm_provider`, `models_registry`, `embeddings` |
| `crop-intelligence-service` (port 8095) | `crop_vision`, `context_engineering` |
| `knowledge-graph` (port 8140) | `graph_memory`, `vector_store`, `ultrarag` |

### FixOps CLI integration

```bash
# Preview issues across the platform
make fixops              # Dry-run using auto_fix engine

# Apply safe fixes
make fixops-run          # FixStrategy.SAFE

# Comprehensive fix pass
make fixops-comprehensive
```

### MCP Server

The `ultrarag/mcp_tools.py` module exposes RAG capabilities as MCP tools, consumable
by the `mcp-server` service (port 8201) and any A2A-compatible agent.

---

## Testing

```bash
# Run all AI module tests
pytest tests/unit/ -k "ai" -v

# Run with coverage
pytest tests/unit/ -k "ai" --cov=shared/ai --cov-report=term-missing

# Smoke test (import verification — no I/O required)
pytest tests/smoke/ -k "ai" -v

# Auto-fix engine integration tests
pytest tests/integration/ -k "auto_fix" -v
```

Test markers: `@pytest.mark.unit`, `@pytest.mark.smoke`, `@pytest.mark.integration`

---

## See Also

- `CLAUDE.md` — Platform-wide conventions and AI module overview (AI Auto-Fix Engine section)
- `shared/ai/context_engineering/METRICS_INTEGRATION.md` — Context engineering metrics guide
- `apps/services-docs/advisory-service.md` — Advisory service consuming this module
- `tools/` — FixOps CLI built on `auto_fix`
- `.claude/skills/context-engineering/` — AI skills for context compression and evaluation

---

_Module version 2.0.0. Last updated: February 2026. Owner: SAHOOL Platform Team._
