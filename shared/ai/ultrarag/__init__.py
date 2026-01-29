# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Integration Module for SAHOOL Platform
# تكامل UltraRAG مع منصة سهول
# ═══════════════════════════════════════════════════════════════════════════════
#
# This module provides UltraRAG 3.0-inspired RAG capabilities with MCP integration
# Features:
# - YAML-based pipeline configuration (Low-Code)
# - Multiple retrieval strategies (Adaptive, Dense, Hybrid)
# - Query expansion and reranking
# - Arabic/English bilingual support
# - MCP Server integration
# - Offline-first architecture
#
# ═══════════════════════════════════════════════════════════════════════════════

from .models import (
    # Enums
    RetrievalStrategy,
    ChunkingStrategy,
    RerankingMethod,
    GenerationMode,
    # Data classes
    KnowledgeChunk,
    KnowledgeDocument,
    RetrievalResult,
    RerankResult,
    GenerationResult,
    RAGRequest,
    RAGResult,
    RAGPipelineConfig,
    WorkflowConfig,
    WorkflowStep,
    PipelineStageConfig,
)

from .pipeline import (
    RAGPipeline,
    RAGPipelineBuilder,
    RAGStage,
    StageResult,
    PipelineContext,
)

from .retriever import (
    Retriever,
    DenseRetriever,
    SparseRetriever,
    HybridRetriever,
    AdaptiveRetriever,
    RetrievalConfig,
)

from .reranker import (
    Reranker,
    CrossEncoderReranker,
    LLMReranker,
    ReciprocalRankFusionReranker,
    NoReranker,
    RerankConfig,
    get_reranker,
)

from .generator import (
    Generator,
    GeneratorConfig,
    OllamaGenerator,
    TemplateGenerator,
    CompositeGenerator,
    create_generator,
)

from .workflow import (
    WorkflowEngine,
    WorkflowExecutionContext,
    StepExecutionResult,
    load_workflow_from_yaml,
    load_workflows_from_directory,
)

from .knowledge_base import (
    KnowledgeBase,
    Chunker,
    ChunkingConfig,
)

from .mcp_tools import (
    RAGMCPTools,
    MCPToolDefinition,
    register_rag_tools,
)

__version__ = "3.0.0"
__all__ = [
    # Models - Enums
    "RetrievalStrategy",
    "ChunkingStrategy",
    "RerankingMethod",
    "GenerationMode",
    # Models - Data Classes
    "KnowledgeChunk",
    "KnowledgeDocument",
    "RetrievalResult",
    "RerankResult",
    "GenerationResult",
    "RAGRequest",
    "RAGResult",
    "RAGPipelineConfig",
    "WorkflowConfig",
    "WorkflowStep",
    "PipelineStageConfig",
    # Pipeline
    "RAGPipeline",
    "RAGPipelineBuilder",
    "RAGStage",
    "StageResult",
    "PipelineContext",
    # Retriever
    "Retriever",
    "DenseRetriever",
    "SparseRetriever",
    "HybridRetriever",
    "AdaptiveRetriever",
    "RetrievalConfig",
    # Reranker
    "Reranker",
    "CrossEncoderReranker",
    "LLMReranker",
    "ReciprocalRankFusionReranker",
    "NoReranker",
    "RerankConfig",
    "get_reranker",
    # Generator
    "Generator",
    "GeneratorConfig",
    "OllamaGenerator",
    "TemplateGenerator",
    "CompositeGenerator",
    "create_generator",
    # Workflow
    "WorkflowEngine",
    "WorkflowExecutionContext",
    "StepExecutionResult",
    "load_workflow_from_yaml",
    "load_workflows_from_directory",
    # Knowledge Base
    "KnowledgeBase",
    "Chunker",
    "ChunkingConfig",
    # MCP Tools
    "RAGMCPTools",
    "MCPToolDefinition",
    "register_rag_tools",
]
