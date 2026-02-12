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

from .generator import (
    CompositeGenerator,
    Generator,
    GeneratorConfig,
    OllamaGenerator,
    TemplateGenerator,
    create_generator,
)
from .knowledge_base import (
    Chunker,
    ChunkingConfig,
    KnowledgeBase,
)
from .mcp_tools import (
    MCPToolDefinition,
    RAGMCPTools,
    register_rag_tools,
)
from .models import (
    ChunkingStrategy,
    GenerationMode,
    GenerationResult,
    # Data classes
    KnowledgeChunk,
    KnowledgeDocument,
    PipelineStageConfig,
    RAGPipelineConfig,
    RAGRequest,
    RAGResult,
    RerankingMethod,
    RerankResult,
    RetrievalResult,
    # Enums
    RetrievalStrategy,
    WorkflowConfig,
    WorkflowStep,
)
from .pipeline import (
    PipelineContext,
    RAGPipeline,
    RAGPipelineBuilder,
    RAGStage,
    StageResult,
)
from .reranker import (
    CrossEncoderReranker,
    LLMReranker,
    NoReranker,
    ReciprocalRankFusionReranker,
    RerankConfig,
    Reranker,
    get_reranker,
)
from .retriever import (
    AdaptiveRetriever,
    DenseRetriever,
    HybridRetriever,
    RetrievalConfig,
    Retriever,
    SparseRetriever,
)
from .workflow import (
    StepExecutionResult,
    WorkflowEngine,
    WorkflowExecutionContext,
    load_workflow_from_yaml,
    load_workflows_from_directory,
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
