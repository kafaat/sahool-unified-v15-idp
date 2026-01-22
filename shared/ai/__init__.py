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

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .context_engineering import (
    # Compression
    ContextCompressor,
    CompressionResult,
    CompressionStrategy,
    # Memory
    FarmMemory,
    MemoryEntry,
    MemoryConfig,
    # Evaluation
    RecommendationEvaluator,
    EvaluationResult,
    EvaluationCriteria,
)

from .auto_fix import (
    # Engine
    AutoFixEngine,
    quick_diagnose,
    quick_fix,
    # Diagnostics
    CodeDiagnostics,
    DiagnosticError,
    # Fixers
    CodeFixer,
    FixerError,
    # Models
    Diagnostic,
    DiagnosticReport,
    DiagnosticSeverity,
    DiagnosticCategory,
    CodeFix,
    FixPlan,
    FixResult,
    FixStrategy,
    FixConfidence,
    ToolType,
    AuditEntry,
)

# Audit logging
from .audit import (
    AIAuditLogger,
    AuditEvent,
    AuditEventType,
    SafetyLevel,
    calculate_cost,
    get_audit_logger,
    get_cost_summary,
    log_agent_call,
    LLM_COSTS,
)

# Circuit breaker
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerStats,
    CircuitState,
    get_circuit_breaker,
    get_ollama_circuit_breaker,
    get_anthropic_circuit_breaker,
    get_openai_circuit_breaker,
    get_all_circuit_breakers,
    reset_all_circuit_breakers,
)

# Metrics
from .metrics import (
    AIMetricsCollector,
    MetricType,
    MetricValue,
    get_metrics_collector,
)

# Validation
from .validation import (
    AIValidator,
    ValidationResult,
    ValidationIssue,
    ValidationLevel,
    ThreatCategory,
    Severity,
    get_validator,
    validate_prompt,
    validate_response,
    is_safe_prompt,
    is_safe_response,
)

# LLM Provider Manager (optional - requires httpx)
try:
    from .llm_provider import (
        LLMProviderManager,
        LLMProvider,
        LLMConfig,
        LLMResponse,
        LLMProviderError,
        AllProvidersFailedError,
        get_llm_manager,
        generate_text,
        generate_with_ollama_fallback,
    )
    LLM_MANAGER_AVAILABLE = True
except ImportError:
    LLM_MANAGER_AVAILABLE = False

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
        EvaluationResult as TrainingEvalResult,
        create_code_fix_dataset,
        train_code_fixer,
    )
    TRAINING_AVAILABLE = True
except ImportError:
    TRAINING_AVAILABLE = False

# Embeddings adapter
from .embeddings import (
    EmbeddingsAdapter,
    EmbeddingConfig,
    EmbeddingResult,
    BatchEmbeddingResult,
    EmbeddingProvider,
    EmbeddingProviderError,
    EmbeddingCache,
    get_embeddings_adapter,
    embed_text,
    embed_texts,
    text_similarity,
)

# Explainability layer
from .explainability import (
    ExplainabilityEngine,
    Explanation,
    ContributingFactor,
    AlternativeRecommendation,
    RuleExplanation,
    ExplanationType,
    FactorType,
    ImpactLevel,
    get_explainability_engine,
    explain_recommendation,
)

# Feedback collection
from .feedback import (
    FeedbackCollector,
    FeedbackItem,
    FeedbackSummary,
    FeedbackStorage,
    FeedbackType,
    FeedbackSentiment,
    RecommendationType,
    OutcomeStatus,
    get_feedback_collector,
    collect_rating,
    collect_outcome,
    get_feedback_summary,
)

# Experience-based learning (Acontext-inspired)
from .experience_learning import (
    ExperienceLearner,
    ExperienceStore,
    ExecutionStatus,
    ExecutionStep,
    TaskExecution,
    SOP,
    SOPConfidence,
    get_experience_learner,
    record_task_execution,
    get_task_guidance,
)

# Graph-based memory (Cognee-inspired)
from .graph_memory import (
    GraphMemory,
    GraphStore,
    PersistentGraphStore,
    Entity,
    EntityType,
    Relationship,
    RelationType,
    SearchResult,
    SimpleEmbedder,
    get_graph_memory,
    get_persistent_graph_memory,
    add as graph_add,
    cognify,
    memify,
    search as graph_search,
    cosine_similarity,
)

# Crop Vision (Computer Vision for Agriculture)
from .crop_vision import (
    CropVisionAnalyzer,
    CropType,
    DiseaseType,
    GrowthStage,
    PestType,
    Severity as VisionSeverity,
    BoundingBox,
    VisionAnalysisResult,
    DiseaseDetection,
    GrowthStageDetection,
    PestDetection,
    YieldEstimate,
    NDVIAnalysis,
    ImagePreprocessor,
    get_crop_vision_analyzer,
    analyze_crop_image,
    detect_crop_disease,
    detect_crop_pests,
)

# Huggingface Provider (Arabic & Multilingual Embeddings)
from .huggingface_provider import (
    HuggingfaceProvider,
    HuggingfaceConfig,
    HuggingfaceModelType,
    EmbeddingModelFamily,
    EmbeddingResult as HFEmbeddingResult,
    BatchEmbeddingResult as HFBatchEmbeddingResult,
    ModelInfo,
    EmbeddingCache as HFEmbeddingCache,
    EMBEDDING_MODELS,
    AGRICULTURAL_MODELS,
    get_huggingface_provider,
    embed_text as hf_embed_text,
    embed_texts as hf_embed_texts,
    text_similarity as hf_text_similarity,
    list_arabic_models,
    get_best_arabic_model,
)

# Vector Store (Persistent Vector Database)
from .vector_store import (
    VectorStore,
    VectorStoreConfig,
    VectorStoreBackend,
    DistanceMetric,
    IndexType,
    VectorDocument,
    SearchResult as VectorSearchResult,
    CollectionInfo,
    VectorStoreBackendBase,
    SQLiteBackend,
    MemoryBackend,
    get_vector_store,
    add_documents,
    search_documents,
)

__version__ = "1.9.0"

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
    __all__.extend([
        "LLMProviderManager",
        "LLMProvider",
        "LLMConfig",
        "LLMResponse",
        "LLMProviderError",
        "AllProvidersFailedError",
        "get_llm_manager",
        "generate_text",
        "generate_with_ollama_fallback",
    ])

# Add Ollama exports if available
if OLLAMA_AVAILABLE:
    __all__.extend([
        "OllamaClient",
        "OllamaConfig",
        "OllamaError",
        "OllamaModel",
        "OllamaResponse",
        "analyze_code_with_ollama",
        "fix_code_with_ollama",
        "generate_tests_with_ollama",
    ])

# Add training exports if available
if TRAINING_AVAILABLE:
    __all__.extend([
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
    ])

# Agent Orchestration Framework (Claude-Flow inspired)
from .orchestration import (
    # Enums
    AgentCapability,
    ConsensusType,
    MemoryNamespace,
    SwarmTopology,
    TaskPriority,
    TaskStatus,
    # Agent Models
    AgentProfile,
    AgentScore,
    AgentState as OrchestrationAgentState,
    # Task Models
    Task,
    TaskResult,
    # Swarm Models
    SwarmConfig,
    SwarmResult,
    SwarmState,
    # Consensus Models
    ConsensusResult,
    Vote,
    # Memory Models
    MemoryEntry as OrchestrationMemoryEntry,
    MemoryStats,
    PatternMatch,
    # Routing Models
    RoutingDecision,
    RouterStats,
    # Router
    AgentRouter,
    get_router,
    reset_router,
    # Swarm Coordination
    SwarmCoordinator,
    AggregationStrategy,
    MajorityVoteAggregation,
    WeightedAverageAggregation,
    ConcatenateAggregation,
    BestResultAggregation,
    get_swarm_coordinator,
    reset_swarm_coordinator,
    # Consensus Protocols
    ConsensusProtocol,
    MajorityVoting,
    WeightedVoting,
    RaftConsensus,
    UnanimousConsensus,
    QuorumConsensus,
    ConsensusManager,
    get_consensus_manager,
    reach_consensus,
    # Collective Memory
    CollectiveMemory,
    LRUCache,
    cosine_similarity,
    jaccard_similarity,
    text_similarity,
    get_collective_memory,
    reset_collective_memory,
)

__all__.extend([
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
])
