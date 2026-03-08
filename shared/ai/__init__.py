"""
SAHOOL AI Module
================
وحدة الذكاء الاصطناعي لمنصة سهول

AI utilities and context engineering for the SAHOOL agricultural platform.
Provides context compression, memory management, recommendation evaluation,
automated code analysis/fixing, model training, audit logging, and circuit breakers.

Modules:
    - context_engineering: Context compression, memory, and evaluation
    - auto_fix: Automated code diagnostics and fixing
    - ollama_client: Local LLM integration via Ollama
    - llm_provider: Multi-provider LLM manager (Ollama, Claude, OpenAI, Gemini, DeepSeek)
    - code_llm_provider: Code-specialized LLM provider (completion, review, fix, tests)
    - model_training: Fine-tuning and training capabilities
    - audit: Unified AI audit logging with cost tracking
    - circuit_breaker: Resilience pattern for external services
    - metrics: Prometheus-compatible observability metrics
    - embeddings: Unified embedding providers (sentence-transformers, OpenAI, Ollama, Huggingface)
    - explainability: Explanation generation for AI recommendations
    - feedback: User feedback collection and analysis
    - experience_learning: Self-learning agents with SOP generation (Acontext-inspired)
    - graph_memory: Graph-based memory with ECL pipeline (Cognee-inspired)
    - crop_vision: Computer vision for crop disease/pest detection (GenAI Roadmap)
    - huggingface_provider: Arabic & multilingual embeddings via Huggingface
    - vector_store: Persistent vector database for RAG and semantic search
    - orchestration: Multi-agent orchestration framework (Claude-Flow inspired)
    - models_registry: Agricultural AI Models Registry (50+ models from global institutions)
    - guardrails: Tool guardrails for safe AI operations

    - feedback_training_pipeline: Unified feedback→training→experience pipeline
    - knowledge_service_bridge: Service-level knowledge base access
    - agent_orchestration_bridge: Reliable agent orchestration with circuit breakers
    - vision_knowledge_bridge: CropVision→Knowledge Base integration
    - mcp_rag_bridge: MCP server→UltraRAG tool integration
    - arabic_models: Arabic-specialized model configurations
    - unified_embeddings: Consistent embeddings across all AI layers
    - training_orchestrator: Model training and GRPO fine-tuning orchestration
    - ab_testing: A/B testing for models and RAG configurations

Author: SAHOOL Platform Team
Updated: March 2026
"""

# Audit logging
from .audit import (
    LLM_COSTS,
    AIAuditLogger,
    AuditEvent,
    AuditEventType,
    SafetyLevel,
    calculate_cost,
    get_audit_logger,
    get_cost_summary,
    log_agent_call,
)
from .auto_fix import (
    AuditEntry,
    # Engine
    AutoFixEngine,
    # Diagnostics
    CodeDiagnostics,
    CodeFix,
    # Fixers
    CodeFixer,
    # Models
    Diagnostic,
    DiagnosticCategory,
    DiagnosticError,
    DiagnosticReport,
    DiagnosticSeverity,
    FixConfidence,
    FixerError,
    FixPlan,
    FixResult,
    FixStrategy,
    ToolType,
    quick_diagnose,
    quick_fix,
)

# Circuit breaker
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerStats,
    CircuitState,
    get_all_circuit_breakers,
    get_anthropic_circuit_breaker,
    get_circuit_breaker,
    get_ollama_circuit_breaker,
    get_openai_circuit_breaker,
    reset_all_circuit_breakers,
)
from .context_engineering import (
    CompressionResult,
    CompressionStrategy,
    # Compression
    ContextCompressor,
    EvaluationCriteria,
    EvaluationResult,
    # Memory
    FarmMemory,
    MemoryConfig,
    MemoryEntry,
    # Evaluation
    RecommendationEvaluator,
)

# Metrics
from .metrics import (
    AIMetricsCollector,
    MetricType,
    MetricValue,
    get_metrics_collector,
)

# Observability (Sentry, OpenTelemetry, Prometheus, Test Integration, CI/CD)
try:
    from .observability import (
        AgentContext as ObservabilityContext,
    )
    from .observability import (
        AgentErrorType,
        AgentTracer,
        AIAgentObservability,
        CIFeedback,
        GitHubActionsIntegration,
        SentryIntegration,
        TestFrameworkIntegration,
        TestResult,
        create_observability,
        get_agent_tracer,
        get_ci_integration,
        get_sentry_integration,
    )

    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Validation
from .validation import (
    AIValidator,
    Severity,
    ThreatCategory,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    get_validator,
    is_safe_prompt,
    is_safe_response,
    validate_prompt,
    validate_response,
)

# LLM Provider Manager (optional - requires httpx)
try:
    from .llm_provider import (
        AllProvidersFailedError,
        LLMConfig,
        LLMProvider,
        LLMProviderError,
        LLMProviderManager,
        LLMResponse,
        generate_text,
        generate_with_ollama_fallback,
        get_llm_manager,
    )

    LLM_MANAGER_AVAILABLE = True
except ImportError:
    LLM_MANAGER_AVAILABLE = False

# Code-specialized LLM Provider (optional - requires llm_provider)
try:
    from .code_llm_provider import (
        CodeCompletionResult,
        CodeContext,
        CodeFixResult,
        CodeLLMProvider,
        CodeReviewResult,
        CodeTaskType,
        get_code_llm_provider,
    )

    CODE_LLM_AVAILABLE = True
except ImportError:
    CODE_LLM_AVAILABLE = False

# Ollama client (optional - requires httpx)
try:
    from .ollama_client import (
        OllamaClient,
        OllamaConfig,
        OllamaError,
        OllamaModel,
        OllamaResponse,
        analyze_code_with_ollama,
        fix_code_with_ollama,
        generate_tests_with_ollama,
    )

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Model training (optional - requires httpx)
try:
    from .model_training import (
        DatasetBuilder,
        DatasetType,
        ModelTrainer,
        TrainingConfig,
        TrainingDataset,
        TrainingExample,
        TrainingJob,
        TrainingStatus,
        create_code_fix_dataset,
        train_code_fixer,
    )
    from .model_training import (
        EvaluationResult as TrainingEvalResult,
    )

    TRAINING_AVAILABLE = True
except ImportError:
    TRAINING_AVAILABLE = False

# Embeddings adapter
# Crop Vision (Computer Vision for Agriculture)
from .crop_vision import (
    BoundingBox,
    CropType,
    CropVisionAnalyzer,
    DiseaseDetection,
    DiseaseType,
    GrowthStage,
    GrowthStageDetection,
    ImagePreprocessor,
    NDVIAnalysis,
    PestDetection,
    PestType,
    VisionAnalysisResult,
    YieldEstimate,
    analyze_crop_image,
    detect_crop_disease,
    detect_crop_pests,
    get_crop_vision_analyzer,
)
from .crop_vision import (
    Severity as VisionSeverity,
)
from .embeddings import (
    BatchEmbeddingResult,
    EmbeddingCache,
    EmbeddingConfig,
    EmbeddingProvider,
    EmbeddingProviderError,
    EmbeddingResult,
    EmbeddingsAdapter,
    embed_text,
    embed_texts,
    get_embeddings_adapter,
    text_similarity,
)

# Experience-based learning (Acontext-inspired)
from .experience_learning import (
    SOP,
    ExecutionStatus,
    ExecutionStep,
    ExperienceLearner,
    ExperienceStore,
    SOPConfidence,
    TaskExecution,
    get_experience_learner,
    get_task_guidance,
    record_task_execution,
)

# Explainability layer
from .explainability import (
    AlternativeRecommendation,
    ContributingFactor,
    ExplainabilityEngine,
    Explanation,
    ExplanationType,
    FactorType,
    ImpactLevel,
    RuleExplanation,
    explain_recommendation,
    get_explainability_engine,
)

# Feedback collection
from .feedback import (
    FeedbackCollector,
    FeedbackItem,
    FeedbackSentiment,
    FeedbackStorage,
    FeedbackSummary,
    FeedbackType,
    OutcomeStatus,
    RecommendationType,
    collect_outcome,
    collect_rating,
    get_feedback_collector,
    get_feedback_summary,
)

# Graph-based memory (Cognee-inspired)
from .graph_memory import (
    Entity,
    EntityType,
    GraphMemory,
    GraphStore,
    PersistentGraphStore,
    Relationship,
    RelationType,
    SearchResult,
    SimpleEmbedder,
    cognify,
    cosine_similarity,
    get_graph_memory,
    get_persistent_graph_memory,
    memify,
)
from .graph_memory import (
    add as graph_add,
)
from .graph_memory import (
    search as graph_search,
)

# Huggingface Provider (Arabic & Multilingual Embeddings)
from .huggingface_provider import (
    AGRICULTURAL_MODELS,
    EMBEDDING_MODELS,
    EmbeddingModelFamily,
    HuggingfaceConfig,
    HuggingfaceModelType,
    HuggingfaceProvider,
    ModelInfo,
    get_best_arabic_model,
    get_huggingface_provider,
    list_arabic_models,
)
from .huggingface_provider import (
    BatchEmbeddingResult as HFBatchEmbeddingResult,
)
from .huggingface_provider import (
    EmbeddingCache as HFEmbeddingCache,
)
from .huggingface_provider import (
    EmbeddingResult as HFEmbeddingResult,
)
from .huggingface_provider import (
    embed_text as hf_embed_text,
)
from .huggingface_provider import (
    embed_texts as hf_embed_texts,
)
from .huggingface_provider import (
    text_similarity as hf_text_similarity,
)

# Vector Store (Persistent Vector Database)
from .vector_store import (
    CollectionInfo,
    DistanceMetric,
    IndexType,
    MemoryBackend,
    SQLiteBackend,
    VectorDocument,
    VectorStore,
    VectorStoreBackend,
    VectorStoreBackendBase,
    VectorStoreConfig,
    add_documents,
    get_vector_store,
    search_documents,
)
from .vector_store import (
    SearchResult as VectorSearchResult,
)

__version__ = "3.0.0"

# ─── New Bridge & Integration Modules (Gap Fixes) ───────────────────────────

# Arabic model configurations (G-02)
try:
    from .arabic_models import (
        ARABIC_MODELS,
        ArabicModelConfig,
        ArabicModelTask,
        get_arabic_embedding_model,
        get_arabic_model,
        get_recommended_models_for_agriculture,
    )
    from .arabic_models import (
        list_arabic_models as list_arabic_model_configs,
    )

    ARABIC_MODELS_AVAILABLE = True
except ImportError:
    ARABIC_MODELS_AVAILABLE = False

# Unified embeddings consistency (G-05)
try:
    from .unified_embeddings import (
        EmbeddingConsistencyConfig,
        UnifiedEmbeddingsManager,
        get_unified_embeddings,
    )

    UNIFIED_EMBEDDINGS_AVAILABLE = True
except ImportError:
    UNIFIED_EMBEDDINGS_AVAILABLE = False

# Feedback-training pipeline (G-07, G-12)
try:
    from .feedback_training_pipeline import (
        FeedbackTrainingPipeline,
        get_feedback_training_pipeline,
    )

    FEEDBACK_TRAINING_AVAILABLE = True
except ImportError:
    FEEDBACK_TRAINING_AVAILABLE = False

# Knowledge service bridge (G-04, G-09)
try:
    from .knowledge_service_bridge import (
        KnowledgeServiceBridge,
        get_knowledge_bridge,
    )

    KNOWLEDGE_BRIDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_BRIDGE_AVAILABLE = False

# Agent orchestration bridge (G-10, G-14, G-24)
try:
    from .agent_orchestration_bridge import (
        OrchestrationManager,
        get_orchestration_manager,
    )

    AGENT_ORCHESTRATION_BRIDGE_AVAILABLE = True
except ImportError:
    AGENT_ORCHESTRATION_BRIDGE_AVAILABLE = False

# Vision-knowledge bridge (G-11)
try:
    from .vision_knowledge_bridge import (
        VisionKnowledgeBridge,
        VisionKnowledgeResult,
    )

    VISION_KNOWLEDGE_BRIDGE_AVAILABLE = True
except ImportError:
    VISION_KNOWLEDGE_BRIDGE_AVAILABLE = False

# MCP-RAG bridge (G-19)
try:
    from .mcp_rag_bridge import (
        MCPRAGBridge,
        create_mcp_rag_bridge,
    )

    MCP_RAG_BRIDGE_AVAILABLE = True
except ImportError:
    MCP_RAG_BRIDGE_AVAILABLE = False

# Training orchestrator (G-13, G-18)
try:
    from .training_orchestrator import (
        TrainingOrchestrator,
        TrainingOrchestratorJob,
        get_training_orchestrator,
    )

    TRAINING_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    TRAINING_ORCHESTRATOR_AVAILABLE = False

# A/B testing (G-16, G-17)
try:
    from .ab_testing import (
        ABTest,
        ABTestManager,
        ABTestResult,
        ABTestStatus,
    )

    AB_TESTING_AVAILABLE = True
except ImportError:
    AB_TESTING_AVAILABLE = False

__all__ = [
    # Context Engineering - Compression
    "ContextCompressor",
    "CompressionResult",
    "CompressionStrategy",
    # Context Engineering - Memory
    "FarmMemory",
    "MemoryEntry",
    "MemoryConfig",
    # Context Engineering - Evaluation
    "RecommendationEvaluator",
    "EvaluationResult",
    "EvaluationCriteria",
    # Auto-Fix - Engine
    "AutoFixEngine",
    "quick_diagnose",
    "quick_fix",
    # Auto-Fix - Diagnostics
    "CodeDiagnostics",
    "DiagnosticError",
    # Auto-Fix - Fixers
    "CodeFixer",
    "FixerError",
    # Auto-Fix - Models
    "Diagnostic",
    "DiagnosticReport",
    "DiagnosticSeverity",
    "DiagnosticCategory",
    "CodeFix",
    "FixPlan",
    "FixResult",
    "FixStrategy",
    "FixConfidence",
    "ToolType",
    "AuditEntry",
    # Audit logging
    "AIAuditLogger",
    "AuditEvent",
    "AuditEventType",
    "SafetyLevel",
    "calculate_cost",
    "get_audit_logger",
    "get_cost_summary",
    "log_agent_call",
    "LLM_COSTS",
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerError",
    "CircuitBreakerStats",
    "CircuitState",
    "get_circuit_breaker",
    "get_ollama_circuit_breaker",
    "get_anthropic_circuit_breaker",
    "get_openai_circuit_breaker",
    "get_all_circuit_breakers",
    "reset_all_circuit_breakers",
    # Metrics
    "AIMetricsCollector",
    "MetricType",
    "MetricValue",
    "get_metrics_collector",
    # Observability
    "OBSERVABILITY_AVAILABLE",
    # Validation
    "AIValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationLevel",
    "ThreatCategory",
    "Severity",
    "get_validator",
    "validate_prompt",
    "validate_response",
    "is_safe_prompt",
    "is_safe_response",
    # Availability flags
    "OLLAMA_AVAILABLE",
    "TRAINING_AVAILABLE",
    "LLM_MANAGER_AVAILABLE",
    # Embeddings
    "EmbeddingsAdapter",
    "EmbeddingConfig",
    "EmbeddingResult",
    "BatchEmbeddingResult",
    "EmbeddingProvider",
    "EmbeddingProviderError",
    "EmbeddingCache",
    "get_embeddings_adapter",
    "embed_text",
    "embed_texts",
    "text_similarity",
    # Explainability
    "ExplainabilityEngine",
    "Explanation",
    "ContributingFactor",
    "AlternativeRecommendation",
    "RuleExplanation",
    "ExplanationType",
    "FactorType",
    "ImpactLevel",
    "get_explainability_engine",
    "explain_recommendation",
    # Feedback
    "FeedbackCollector",
    "FeedbackItem",
    "FeedbackSummary",
    "FeedbackStorage",
    "FeedbackType",
    "FeedbackSentiment",
    "RecommendationType",
    "OutcomeStatus",
    "get_feedback_collector",
    "collect_rating",
    "collect_outcome",
    "get_feedback_summary",
    # Experience Learning (Acontext-inspired)
    "ExperienceLearner",
    "ExperienceStore",
    "ExecutionStatus",
    "ExecutionStep",
    "TaskExecution",
    "SOP",
    "SOPConfidence",
    "get_experience_learner",
    "record_task_execution",
    "get_task_guidance",
    # Graph Memory (Cognee-inspired)
    "GraphMemory",
    "GraphStore",
    "PersistentGraphStore",
    "Entity",
    "EntityType",
    "Relationship",
    "RelationType",
    "SearchResult",
    "SimpleEmbedder",
    "get_graph_memory",
    "get_persistent_graph_memory",
    "graph_add",
    "cognify",
    "memify",
    "graph_search",
    "cosine_similarity",
    # Crop Vision (Computer Vision for Agriculture)
    "CropVisionAnalyzer",
    "CropType",
    "DiseaseType",
    "GrowthStage",
    "PestType",
    "VisionSeverity",
    "BoundingBox",
    "VisionAnalysisResult",
    "DiseaseDetection",
    "GrowthStageDetection",
    "PestDetection",
    "YieldEstimate",
    "NDVIAnalysis",
    "ImagePreprocessor",
    "get_crop_vision_analyzer",
    "analyze_crop_image",
    "detect_crop_disease",
    "detect_crop_pests",
    # Huggingface Provider (Arabic & Multilingual Embeddings)
    "HuggingfaceProvider",
    "HuggingfaceConfig",
    "HuggingfaceModelType",
    "EmbeddingModelFamily",
    "HFEmbeddingResult",
    "HFBatchEmbeddingResult",
    "ModelInfo",
    "HFEmbeddingCache",
    "EMBEDDING_MODELS",
    "AGRICULTURAL_MODELS",
    "get_huggingface_provider",
    "hf_embed_text",
    "hf_embed_texts",
    "hf_text_similarity",
    "list_arabic_models",
    "get_best_arabic_model",
    # Vector Store (Persistent Vector Database)
    "VectorStore",
    "VectorStoreConfig",
    "VectorStoreBackend",
    "DistanceMetric",
    "IndexType",
    "VectorDocument",
    "VectorSearchResult",
    "CollectionInfo",
    "VectorStoreBackendBase",
    "SQLiteBackend",
    "MemoryBackend",
    "get_vector_store",
    "add_documents",
    "search_documents",
]

# Add LLM Manager exports if available
if LLM_MANAGER_AVAILABLE:
    __all__.extend(
        [
            "LLMProviderManager",
            "LLMProvider",
            "LLMConfig",
            "LLMResponse",
            "LLMProviderError",
            "AllProvidersFailedError",
            "get_llm_manager",
            "generate_text",
            "generate_with_ollama_fallback",
        ]
    )

# Add Code LLM Provider exports if available
if CODE_LLM_AVAILABLE:
    __all__.extend(
        [
            "CodeLLMProvider",
            "CodeTaskType",
            "CodeContext",
            "CodeCompletionResult",
            "CodeReviewResult",
            "CodeFixResult",
            "get_code_llm_provider",
            "CODE_LLM_AVAILABLE",
        ]
    )

# Add Ollama exports if available
if OLLAMA_AVAILABLE:
    __all__.extend(
        [
            "OllamaClient",
            "OllamaConfig",
            "OllamaError",
            "OllamaModel",
            "OllamaResponse",
            "analyze_code_with_ollama",
            "fix_code_with_ollama",
            "generate_tests_with_ollama",
        ]
    )

# Add training exports if available
if TRAINING_AVAILABLE:
    __all__.extend(
        [
            "DatasetBuilder",
            "DatasetType",
            "ModelTrainer",
            "TrainingConfig",
            "TrainingDataset",
            "TrainingExample",
            "TrainingJob",
            "TrainingStatus",
            "TrainingEvalResult",
            "create_code_fix_dataset",
            "train_code_fixer",
        ]
    )

# Agent Orchestration Framework (Claude-Flow inspired) - optional
try:
    from .orchestration import (
        # Enums
        AgentCapability,
        # Agent Models
        AgentProfile,
        # Router
        AgentRouter,
        AgentScore,
        AggregationStrategy,
        BestResultAggregation,
        # Collective Memory
        CollectiveMemory,
        ConcatenateAggregation,
        ConsensusManager,
        # Consensus Protocols
        ConsensusProtocol,
        # Consensus Models
        ConsensusResult,
        ConsensusType,
        LRUCache,
        MajorityVoteAggregation,
        MajorityVoting,
        MemoryNamespace,
        MemoryStats,
        PatternMatch,
        QuorumConsensus,
        RaftConsensus,
        RouterStats,
        # Routing Models
        RoutingDecision,
        # Swarm Models
        SwarmConfig,
        # Swarm Coordination
        SwarmCoordinator,
        SwarmResult,
        SwarmState,
        SwarmTopology,
        # Task Models
        Task,
        TaskPriority,
        TaskResult,
        TaskStatus,
        UnanimousConsensus,
        Vote,
        WeightedAverageAggregation,
        WeightedVoting,
        cosine_similarity,
        get_collective_memory,
        get_consensus_manager,
        get_router,
        get_swarm_coordinator,
        jaccard_similarity,
        reach_consensus,
        reset_collective_memory,
        reset_router,
        reset_swarm_coordinator,
        text_similarity,
    )
    from .orchestration import (
        AgentState as OrchestrationAgentState,
    )
    from .orchestration import (
        # Memory Models
        MemoryEntry as OrchestrationMemoryEntry,
    )

    ORCHESTRATION_AVAILABLE = True

    __all__.extend(
        [
            # === Orchestration Enums ===
            "AgentCapability",
            "ConsensusType",
            "MemoryNamespace",
            "SwarmTopology",
            "TaskPriority",
            "TaskStatus",
            # === Orchestration Agent Models ===
            "AgentProfile",
            "AgentScore",
            "OrchestrationAgentState",
            # === Orchestration Task Models ===
            "Task",
            "TaskResult",
            # === Orchestration Swarm Models ===
            "SwarmConfig",
            "SwarmResult",
            "SwarmState",
            # === Orchestration Consensus Models ===
            "ConsensusResult",
            "Vote",
            # === Orchestration Memory Models ===
            "OrchestrationMemoryEntry",
            "MemoryStats",
            "PatternMatch",
            # === Orchestration Routing Models ===
            "RoutingDecision",
            "RouterStats",
            # === Router ===
            "AgentRouter",
            "get_router",
            "reset_router",
            # === Swarm Coordination ===
            "SwarmCoordinator",
            "AggregationStrategy",
            "MajorityVoteAggregation",
            "WeightedAverageAggregation",
            "ConcatenateAggregation",
            "BestResultAggregation",
            "get_swarm_coordinator",
            "reset_swarm_coordinator",
            # === Consensus Protocols ===
            "ConsensusProtocol",
            "MajorityVoting",
            "WeightedVoting",
            "RaftConsensus",
            "UnanimousConsensus",
            "QuorumConsensus",
            "ConsensusManager",
            "get_consensus_manager",
            "reach_consensus",
            # === Collective Memory ===
            "CollectiveMemory",
            "LRUCache",
            "cosine_similarity",
            "jaccard_similarity",
            "text_similarity",
            "get_collective_memory",
            "reset_collective_memory",
            "ORCHESTRATION_AVAILABLE",
        ]
    )
except ImportError:
    ORCHESTRATION_AVAILABLE = False

# Agricultural AI Models Registry - optional
try:
    from .models_registry import (
        TASK_CAPABILITY_MAP,
        # Registry
        AgriculturalAIRegistry,
        AgroGPTConnector,
        # Models & Enums
        AIModelCategory,
        AIModelInfo,
        # Connectors
        BaseConnector,
        ConnectorResponse,
        CropWizardConnector,
        DeveloperInfo,
        GenericRESTConnector,
        LanguageSupport,
        ModelArchitecture,
        ModelCallResult,
        ModelCapability,
        ModelComparison,
        ModelDiscoveryResult,
        ModelEndpoint,
        ModelIntegrator,
        ModelLicense,
        ModelPerformance,
        ModelSelection,
        ModelStatus,
        PlantGPTConnector,
        ShengNongConnector,
        # Integrator
        TaskType,
        create_connector,
        discover_models,
        get_available_connectors,
        get_best_model,
        get_category_info,
        get_integrator,
        # Utilities
        get_philosophy,
        get_registry,
        list_arabic_supported_models,
        list_featured_models,
        list_open_source_models,
        reset_integrator,
        reset_registry,
    )
    from .models_registry import (
        call_model as call_agri_model,
    )
    from .models_registry import (
        compare_models as compare_agri_models,
    )

    MODELS_REGISTRY_AVAILABLE = True

    __all__.extend(
        [
            # === Agricultural AI Models Registry ===
            # Models & Enums
            "AIModelCategory",
            "ModelCapability",
            "ModelLicense",
            "ModelStatus",
            "ModelArchitecture",
            "LanguageSupport",
            "ModelEndpoint",
            "DeveloperInfo",
            "ModelPerformance",
            "AIModelInfo",
            "ModelComparison",
            "ModelDiscoveryResult",
            # Registry
            "AgriculturalAIRegistry",
            "get_registry",
            "reset_registry",
            # Integrator
            "TaskType",
            "ModelIntegrator",
            "ModelCallResult",
            "ModelSelection",
            "get_integrator",
            "reset_integrator",
            "discover_models",
            "get_best_model",
            "call_agri_model",
            "compare_agri_models",
            "TASK_CAPABILITY_MAP",
            # Connectors
            "BaseConnector",
            "ConnectorResponse",
            "ShengNongConnector",
            "CropWizardConnector",
            "PlantGPTConnector",
            "AgroGPTConnector",
            "GenericRESTConnector",
            "create_connector",
            "get_available_connectors",
            # Utilities
            "get_philosophy",
            "get_category_info",
            "list_featured_models",
            "list_arabic_supported_models",
            "list_open_source_models",
            "MODELS_REGISTRY_AVAILABLE",
        ]
    )
except ImportError:
    MODELS_REGISTRY_AVAILABLE = False

# Tool Registry (Dynamic tool management for AI agents)
try:
    from .tool_registry import (
        Language,
        QualityConfig,
        ToolCapability,
        ToolCategory,
        ToolInfo,
        ToolMetrics,
        ToolRegistry,
        ToolResult,
        ToolStatus,
        generate_default_config,
        get_tool_registry,
        reset_tool_registry,
    )

    TOOL_REGISTRY_AVAILABLE = True
except ImportError:
    TOOL_REGISTRY_AVAILABLE = False

# Quality Orchestrator (Automated quality management with auto-audit)
try:
    from .quality_orchestrator import (
        AuditAction,
        AutoAudit,
        IssueSeverity,
        QualityGateResult,
        QualityIssue,
        QualityLevel,
        QualityOrchestrator,
        QualityReport,
        generate_quality_report_markdown,
        run_quality_check,
    )
    from .quality_orchestrator import (
        AuditEntry as QualityAuditEntry,
    )

    QUALITY_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    QUALITY_ORCHESTRATOR_AVAILABLE = False

# Add Observability exports if available
if OBSERVABILITY_AVAILABLE:
    __all__.extend(
        [
            # Observability (Sentry, OpenTelemetry, Prometheus, Test Integration, CI/CD)
            "AIAgentObservability",
            "ObservabilityContext",
            "AgentErrorType",
            "AgentTracer",
            "CIFeedback",
            "GitHubActionsIntegration",
            "SentryIntegration",
            "TestFrameworkIntegration",
            "TestResult",
            "create_observability",
            "get_agent_tracer",
            "get_ci_integration",
            "get_sentry_integration",
        ]
    )

# Add Tool Registry exports if available
if TOOL_REGISTRY_AVAILABLE:
    __all__.extend(
        [
            # Tool Registry
            "ToolRegistry",
            "ToolInfo",
            "ToolResult",
            "QualityConfig",
            "ToolMetrics",
            "ToolCategory",
            "ToolCapability",
            "ToolStatus",
            "Language",
            "get_tool_registry",
            "reset_tool_registry",
            "generate_default_config",
            "TOOL_REGISTRY_AVAILABLE",
        ]
    )

# Add Quality Orchestrator exports if available
if QUALITY_ORCHESTRATOR_AVAILABLE:
    __all__.extend(
        [
            # Quality Orchestrator
            "QualityOrchestrator",
            "QualityReport",
            "QualityIssue",
            "QualityGateResult",
            "AutoAudit",
            "QualityAuditEntry",
            "QualityLevel",
            "IssueSeverity",
            "AuditAction",
            "run_quality_check",
            "generate_quality_report_markdown",
            "QUALITY_ORCHESTRATOR_AVAILABLE",
        ]
    )

# ─── New Bridge & Integration Module Exports ────────────────────────────────

if ARABIC_MODELS_AVAILABLE:
    __all__.extend(
        [
            "ArabicModelConfig",
            "ArabicModelTask",
            "ARABIC_MODELS",
            "get_arabic_model",
            "get_arabic_embedding_model",
            "list_arabic_model_configs",
            "get_recommended_models_for_agriculture",
            "ARABIC_MODELS_AVAILABLE",
        ]
    )

if UNIFIED_EMBEDDINGS_AVAILABLE:
    __all__.extend(
        [
            "UnifiedEmbeddingsManager",
            "EmbeddingConsistencyConfig",
            "get_unified_embeddings",
            "UNIFIED_EMBEDDINGS_AVAILABLE",
        ]
    )

if FEEDBACK_TRAINING_AVAILABLE:
    __all__.extend(
        [
            "FeedbackTrainingPipeline",
            "get_feedback_training_pipeline",
            "FEEDBACK_TRAINING_AVAILABLE",
        ]
    )

if KNOWLEDGE_BRIDGE_AVAILABLE:
    __all__.extend(
        [
            "KnowledgeServiceBridge",
            "get_knowledge_bridge",
            "KNOWLEDGE_BRIDGE_AVAILABLE",
        ]
    )

if AGENT_ORCHESTRATION_BRIDGE_AVAILABLE:
    __all__.extend(
        [
            "OrchestrationManager",
            "get_orchestration_manager",
            "AGENT_ORCHESTRATION_BRIDGE_AVAILABLE",
        ]
    )

if VISION_KNOWLEDGE_BRIDGE_AVAILABLE:
    __all__.extend(
        [
            "VisionKnowledgeBridge",
            "VisionKnowledgeResult",
            "VISION_KNOWLEDGE_BRIDGE_AVAILABLE",
        ]
    )

if MCP_RAG_BRIDGE_AVAILABLE:
    __all__.extend(
        [
            "MCPRAGBridge",
            "create_mcp_rag_bridge",
            "MCP_RAG_BRIDGE_AVAILABLE",
        ]
    )

if TRAINING_ORCHESTRATOR_AVAILABLE:
    __all__.extend(
        [
            "TrainingOrchestrator",
            "TrainingOrchestratorJob",
            "get_training_orchestrator",
            "TRAINING_ORCHESTRATOR_AVAILABLE",
        ]
    )

if AB_TESTING_AVAILABLE:
    __all__.extend(
        [
            "ABTestManager",
            "ABTest",
            "ABTestResult",
            "ABTestStatus",
            "AB_TESTING_AVAILABLE",
        ]
    )
