# ═══════════════════════════════════════════════════════════════════════════════
# MCP-RAG Bridge
# جسر MCP-RAG
# ═══════════════════════════════════════════════════════════════════════════════
#
# Connects the SAHOOL MCP Server with the UltraRAG pipeline, providing:
#   - Automated RAG pipeline initialization with configurable backends
#   - Registration of RAG tools (query, search, knowledge base, advisory)
#     into the MCP server's tool system
#   - Session-based conversation memory for multi-turn interactions
#   - Bilingual support (Arabic/English)
#
# Usage:
#   from shared.ai.mcp_rag_bridge import MCPRAGBridge
#   bridge = MCPRAGBridge()
#   bridge.initialize()
#   bridge.register_with_mcp_server(mcp_server)
#
# يربط خادم MCP الخاص بسهول مع خط أنابيب UltraRAG
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# ─── Imports with graceful fallbacks ──────────────────────────────────────────

try:
    from .ultrarag.models import (
        GenerationMode,
        RAGPipelineConfig,
        RAGRequest,
        RerankingMethod,
        RetrievalStrategy,
    )
    from .ultrarag.pipeline import RAGPipeline, RAGPipelineBuilder
    from .ultrarag.mcp_tools import RAGMCPTools, register_rag_tools
    from .ultrarag.knowledge_base import KnowledgeBase
    from .ultrarag.conversation_memory import (
        ConversationMemory,
        RAGConversationManager,
    )

    _ULTRARAG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"UltraRAG modules not fully available: {e}")
    _ULTRARAG_AVAILABLE = False

try:
    from .embeddings import EmbeddingsAdapter, EmbeddingConfig, EmbeddingProvider
    _EMBEDDINGS_AVAILABLE = True
except ImportError:
    _EMBEDDINGS_AVAILABLE = False

try:
    from .vector_store import VectorStore
    _VECTOR_STORE_AVAILABLE = True
except ImportError:
    _VECTOR_STORE_AVAILABLE = False

try:
    from .knowledge.vector_store_integration import KnowledgeVectorStore
    _KB_VECTOR_STORE_AVAILABLE = True
except ImportError:
    _KB_VECTOR_STORE_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────


class MCPRAGConfig:
    """Configuration for the MCP-RAG bridge.
    تكوين جسر MCP-RAG"""

    def __init__(
        self,
        # Pipeline settings
        pipeline_name: str = "sahool-mcp-rag",
        retrieval_strategy: str = "hybrid",
        reranking_method: str = "cross_encoder",
        generation_mode: str = "standard",
        top_k: int = 10,
        rerank_top_k: int = 5,
        # Embedding settings
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        embedding_provider: str = "sentence_transformers",
        # LLM settings
        llm_model: str = "codellama:7b",
        llm_provider: str = "ollama",
        # Conversation memory
        enable_conversation_memory: bool = True,
        session_ttl_seconds: int = 3600,
        max_context_turns: int = 5,
        # Arabic support
        arabic_enabled: bool = True,
        arabic_embedding_model: str = "CAMeL-Lab/bert-base-arabic-camelbert-mix",
        # Offline mode
        offline_first: bool = True,
    ) -> None:
        self.pipeline_name = pipeline_name
        self.retrieval_strategy = retrieval_strategy
        self.reranking_method = reranking_method
        self.generation_mode = generation_mode
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k
        self.embedding_model = embedding_model
        self.embedding_provider = embedding_provider
        self.llm_model = llm_model
        self.llm_provider = llm_provider
        self.enable_conversation_memory = enable_conversation_memory
        self.session_ttl_seconds = session_ttl_seconds
        self.max_context_turns = max_context_turns
        self.arabic_enabled = arabic_enabled
        self.arabic_embedding_model = arabic_embedding_model
        self.offline_first = offline_first

    @classmethod
    def from_env(cls) -> "MCPRAGConfig":
        """Create configuration from environment variables.
        إنشاء التكوين من متغيرات البيئة"""
        return cls(
            pipeline_name=os.getenv("RAG_PIPELINE_NAME", "sahool-mcp-rag"),
            retrieval_strategy=os.getenv("RAG_RETRIEVAL_STRATEGY", "hybrid"),
            reranking_method=os.getenv("RAG_RERANKING_METHOD", "cross_encoder"),
            generation_mode=os.getenv("RAG_GENERATION_MODE", "standard"),
            top_k=int(os.getenv("RAG_TOP_K", "10")),
            rerank_top_k=int(os.getenv("RAG_RERANK_TOP_K", "5")),
            embedding_model=os.getenv(
                "RAG_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
            ),
            embedding_provider=os.getenv("RAG_EMBEDDING_PROVIDER", "sentence_transformers"),
            llm_model=os.getenv("RAG_LLM_MODEL", "codellama:7b"),
            llm_provider=os.getenv("RAG_LLM_PROVIDER", "ollama"),
            enable_conversation_memory=os.getenv(
                "RAG_ENABLE_CONVERSATION_MEMORY", "true"
            ).lower() == "true",
            session_ttl_seconds=int(os.getenv("RAG_SESSION_TTL", "3600")),
            max_context_turns=int(os.getenv("RAG_MAX_CONTEXT_TURNS", "5")),
            arabic_enabled=os.getenv("RAG_ARABIC_ENABLED", "true").lower() == "true",
            offline_first=os.getenv("RAG_OFFLINE_FIRST", "true").lower() == "true",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_name": self.pipeline_name,
            "retrieval_strategy": self.retrieval_strategy,
            "reranking_method": self.reranking_method,
            "top_k": self.top_k,
            "embedding_model": self.embedding_model,
            "llm_model": self.llm_model,
            "conversation_memory": self.enable_conversation_memory,
            "arabic_enabled": self.arabic_enabled,
            "offline_first": self.offline_first,
        }


# ─────────────────────────────────────────────────────────────────────────────
# MCP-RAG Bridge
# ─────────────────────────────────────────────────────────────────────────────


class MCPRAGBridge:
    """Bridge connecting the SAHOOL MCP Server with UltraRAG pipeline.
    جسر يربط خادم MCP الخاص بسهول مع خط أنابيب UltraRAG

    Handles:
    - Initializing the RAG pipeline with embedding/vector store/LLM backends
    - Creating RAGMCPTools and registering them with the MCP server
    - Managing conversation memory for multi-turn interactions
    - Providing health status and metrics

    Usage:
        # In MCP server lifespan or startup:
        bridge = MCPRAGBridge(config=MCPRAGConfig.from_env())
        bridge.initialize()
        bridge.register_with_mcp_server(mcp_server)

        # In MCP server shutdown:
        bridge.shutdown()
    """

    def __init__(
        self,
        config: MCPRAGConfig | None = None,
        vector_store: Any | None = None,
        embedding_service: Any | None = None,
        llm_client: Any | None = None,
    ) -> None:
        self._config = config or MCPRAGConfig.from_env()
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._llm_client = llm_client

        self._pipeline: RAGPipeline | None = None
        self._knowledge_base: KnowledgeBase | None = None
        self._rag_tools: RAGMCPTools | None = None
        self._conversation_manager: RAGConversationManager | None = None
        self._conversation_memory: ConversationMemory | None = None
        self._initialized = False

        logger.info(
            "MCP-RAG bridge created | تم إنشاء جسر MCP-RAG",
            extra={"config": self._config.to_dict()},
        )

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def pipeline(self) -> RAGPipeline | None:
        return self._pipeline

    @property
    def rag_tools(self) -> RAGMCPTools | None:
        return self._rag_tools

    @property
    def conversation_manager(self) -> RAGConversationManager | None:
        return self._conversation_manager

    def initialize(self) -> bool:
        """Initialize the RAG pipeline and all supporting components.
        تهيئة خط أنابيب RAG وجميع المكونات الداعمة

        Returns:
            True if initialization succeeded, False otherwise.
        """
        if not _ULTRARAG_AVAILABLE:
            logger.error(
                "Cannot initialize MCP-RAG bridge: UltraRAG modules not available. "
                "لا يمكن تهيئة جسر MCP-RAG: وحدات UltraRAG غير متاحة"
            )
            return False

        try:
            # Step 1: Initialize embedding service if not provided
            if self._embedding_service is None:
                self._embedding_service = self._create_embedding_service()

            # Step 2: Initialize vector store if not provided
            if self._vector_store is None:
                self._vector_store = self._create_vector_store()

            # Step 3: Build the RAG pipeline
            self._pipeline = self._build_pipeline()

            # Step 4: Initialize knowledge base
            self._knowledge_base = self._create_knowledge_base()

            # Step 5: Create RAG MCP tools
            self._rag_tools = RAGMCPTools(
                rag_pipeline=self._pipeline,
                knowledge_base=self._knowledge_base,
            )

            # Step 6: Initialize conversation memory if enabled
            if self._config.enable_conversation_memory:
                self._conversation_memory = ConversationMemory(
                    session_ttl_seconds=self._config.session_ttl_seconds,
                    max_context_turns=self._config.max_context_turns,
                )
                self._conversation_manager = RAGConversationManager(
                    pipeline=self._pipeline,
                    memory=self._conversation_memory,
                    inject_context=True,
                    context_turns=self._config.max_context_turns,
                )

            self._initialized = True
            logger.info(
                "MCP-RAG bridge initialized successfully | تم تهيئة جسر MCP-RAG بنجاح",
                extra={
                    "pipeline": self._config.pipeline_name,
                    "strategy": self._config.retrieval_strategy,
                    "conversation_memory": self._config.enable_conversation_memory,
                },
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to initialize MCP-RAG bridge: {e} | فشل في تهيئة جسر MCP-RAG: {e}",
                exc_info=True,
            )
            return False

    def register_with_mcp_server(self, mcp_server: Any) -> int:
        """Register RAG tools with an MCP server instance.
        تسجيل أدوات RAG مع مثيل خادم MCP

        Supports two MCP server types:
        1. SAHOOLMCPServer (shared.mcp.server.MCPServer) - registers via tools/call routing
        2. FastAPI app (apps/services/mcp-server) - registers tool handlers

        Args:
            mcp_server: MCP server instance to register tools with

        Returns:
            Number of tools registered
        """
        if not self._initialized or self._rag_tools is None:
            logger.warning(
                "Cannot register tools: bridge not initialized. "
                "لا يمكن تسجيل الأدوات: الجسر غير مهيأ"
            )
            return 0

        tools = self._rag_tools.get_tools()
        registered_count = 0

        # Try to use the register_rag_tools helper
        try:
            register_rag_tools(mcp_server, self._rag_tools)
            registered_count = len(tools)
            logger.info(
                f"Registered {registered_count} RAG tools with MCP server via register_rag_tools"
            )
            return registered_count
        except Exception:
            pass

        # Fallback: try direct tool registration methods
        for tool in tools:
            tool_name = tool["name"]
            try:
                if hasattr(mcp_server, "register_tool"):
                    mcp_server.register_tool(
                        name=tool_name,
                        description=tool["description"],
                        input_schema=tool["inputSchema"],
                        handler=lambda args, t=tool_name: self._rag_tools.call_tool(t, args),
                    )
                    registered_count += 1
                elif hasattr(mcp_server, "tools") and hasattr(mcp_server.tools, "register_tool"):
                    mcp_server.tools.register_tool(
                        name=tool_name,
                        description=tool["description"],
                        input_schema=tool["inputSchema"],
                        handler=lambda args, t=tool_name: self._rag_tools.call_tool(t, args),
                    )
                    registered_count += 1
                else:
                    logger.debug(
                        f"No registration method found for tool {tool_name}"
                    )
            except Exception as e:
                logger.warning(f"Failed to register tool {tool_name}: {e}")

        # Register conversation tools if memory is enabled
        if self._conversation_manager:
            conv_tools = self._get_conversation_tools()
            for tool in conv_tools:
                tool_name = tool["name"]
                try:
                    if hasattr(mcp_server, "register_tool"):
                        mcp_server.register_tool(
                            name=tool_name,
                            description=tool["description"],
                            input_schema=tool["inputSchema"],
                            handler=tool["handler"],
                        )
                        registered_count += 1
                except Exception as e:
                    logger.warning(f"Failed to register conversation tool {tool_name}: {e}")

        logger.info(
            f"Registered {registered_count} tools with MCP server | "
            f"تم تسجيل {registered_count} أدوات مع خادم MCP"
        )
        return registered_count

    def _build_pipeline(self) -> RAGPipeline:
        """Build the RAG pipeline from configuration.
        بناء خط أنابيب RAG من التكوين"""
        cfg = self._config

        builder = RAGPipelineBuilder(name=cfg.pipeline_name)

        # Set retrieval strategy
        strategy_map = {
            "dense": RetrievalStrategy.DENSE,
            "sparse": RetrievalStrategy.SPARSE,
            "hybrid": RetrievalStrategy.HYBRID,
            "adaptive": RetrievalStrategy.ADAPTIVE,
            "tri_rag": RetrievalStrategy.TRI_RAG,
        }
        strategy = strategy_map.get(cfg.retrieval_strategy, RetrievalStrategy.HYBRID)
        builder = builder.with_retrieval_strategy(strategy)

        # Set reranking
        rerank_map = {
            "none": RerankingMethod.NONE,
            "cross_encoder": RerankingMethod.CROSS_ENCODER,
            "llm": RerankingMethod.LLM,
            "reciprocal_rank": RerankingMethod.RECIPROCAL_RANK,
        }
        rerank = rerank_map.get(cfg.reranking_method, RerankingMethod.CROSS_ENCODER)
        builder = builder.with_reranking(rerank)

        # Set generation mode
        gen_map = {
            "standard": GenerationMode.STANDARD,
            "cot": GenerationMode.CHAIN_OF_THOUGHT,
            "self_reflective": GenerationMode.SELF_REFLECTIVE,
            "iterative": GenerationMode.ITERATIVE,
        }
        gen_mode = gen_map.get(cfg.generation_mode, GenerationMode.STANDARD)
        builder = builder.with_generation_mode(gen_mode)

        # Set top_k
        builder = builder.with_top_k(cfg.top_k, cfg.rerank_top_k)

        # Set embedding
        builder = builder.with_embedding(cfg.embedding_model, cfg.embedding_provider)

        # Set LLM
        builder = builder.with_llm(cfg.llm_model, cfg.llm_provider)

        # Set Arabic support
        builder = builder.with_arabic_support(cfg.arabic_enabled, cfg.arabic_embedding_model)

        # Inject services
        if self._vector_store:
            builder = builder.with_vector_store(self._vector_store)
        if self._embedding_service:
            builder = builder.with_embedding_service(self._embedding_service)
        if self._llm_client:
            builder = builder.with_llm_client(self._llm_client)

        pipeline = builder.build()

        logger.info(
            f"RAG pipeline built: {cfg.pipeline_name} | "
            f"تم بناء خط أنابيب RAG: {cfg.pipeline_name}",
            extra={
                "strategy": strategy.value,
                "reranking": rerank.value,
                "generation": gen_mode.value,
            },
        )
        return pipeline

    def _create_embedding_service(self) -> Any:
        """Create embedding service from config.
        إنشاء خدمة التضمين من التكوين"""
        if not _EMBEDDINGS_AVAILABLE:
            logger.warning(
                "Embeddings module not available, using None. "
                "وحدة التضمينات غير متاحة"
            )
            return None

        try:
            provider_map = {
                "sentence_transformers": EmbeddingProvider.SENTENCE_TRANSFORMERS,
                "ollama": EmbeddingProvider.OLLAMA,
                "openai": EmbeddingProvider.OPENAI,
            }
            provider = provider_map.get(
                self._config.embedding_provider,
                EmbeddingProvider.SENTENCE_TRANSFORMERS,
            )

            config = EmbeddingConfig(
                provider=provider,
                model=self._config.embedding_model,
                cache_enabled=True,
            )
            adapter = EmbeddingsAdapter(config)
            logger.info(
                f"Embedding service created: {self._config.embedding_model} | "
                f"تم إنشاء خدمة التضمين: {self._config.embedding_model}"
            )
            return adapter

        except Exception as e:
            logger.warning(f"Failed to create embedding service: {e}")
            return None

    def _create_vector_store(self) -> Any:
        """Create vector store from config.
        إنشاء مخزن المتجهات من التكوين"""
        if not _VECTOR_STORE_AVAILABLE:
            logger.warning(
                "VectorStore module not available, using None. "
                "وحدة مخزن المتجهات غير متاحة"
            )
            return None

        try:
            store = VectorStore()
            logger.info("Vector store created | تم إنشاء مخزن المتجهات")
            return store
        except Exception as e:
            logger.warning(f"Failed to create vector store: {e}")
            return None

    def _create_knowledge_base(self) -> KnowledgeBase | None:
        """Create knowledge base instance.
        إنشاء مثيل قاعدة المعرفة"""
        try:
            kb = KnowledgeBase()
            logger.info("Knowledge base created | تم إنشاء قاعدة المعرفة")
            return kb
        except Exception as e:
            logger.warning(f"Failed to create knowledge base: {e}")
            return None

    def _get_conversation_tools(self) -> list[dict[str, Any]]:
        """Build MCP tool definitions for conversation management.
        بناء تعريفات أدوات MCP لإدارة المحادثات"""
        if not self._conversation_manager:
            return []

        return [
            {
                "name": "conversation_start",
                "description": "Start a new conversation session for multi-turn RAG queries",
                "description_ar": "بدء جلسة محادثة جديدة لاستعلامات RAG متعددة الجولات",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID | معرف المستأجر",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ar", "both"],
                            "description": "Session language | لغة الجلسة",
                            "default": "en",
                        },
                    },
                },
                "handler": self._handle_conversation_start,
            },
            {
                "name": "conversation_query",
                "description": "Send a query within an existing conversation session",
                "description_ar": "إرسال استعلام ضمن جلسة محادثة قائمة",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID | معرف الجلسة",
                        },
                        "query": {
                            "type": "string",
                            "description": "Query text | نص الاستعلام",
                        },
                        "query_ar": {
                            "type": "string",
                            "description": "Arabic query (optional) | الاستعلام بالعربية (اختياري)",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Collection to search | المجموعة للبحث",
                            "default": "default",
                        },
                    },
                    "required": ["session_id", "query"],
                },
                "handler": self._handle_conversation_query,
            },
            {
                "name": "conversation_end",
                "description": "End a conversation session",
                "description_ar": "إنهاء جلسة محادثة",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to end | معرف الجلسة للإنهاء",
                        },
                    },
                    "required": ["session_id"],
                },
                "handler": self._handle_conversation_end,
            },
        ]

    async def _handle_conversation_start(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle conversation start tool call"""
        if not self._conversation_manager:
            return {"error": "Conversation memory not enabled"}

        session_id = self._conversation_manager.start_session(
            tenant_id=args.get("tenant_id"),
            language=args.get("language", "en"),
        )

        return {
            "session_id": session_id,
            "message": "Conversation session started",
            "message_ar": "تم بدء جلسة المحادثة",
        }

    async def _handle_conversation_query(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle conversation query tool call"""
        if not self._conversation_manager:
            return {"error": "Conversation memory not enabled"}

        session_id = args["session_id"]
        query = args["query"]

        result = await self._conversation_manager.query(
            session_id=session_id,
            query=query,
            query_ar=args.get("query_ar"),
            collection=args.get("collection", "default"),
        )

        return {
            "session_id": session_id,
            "answer": result.generation_result.answer if result.generation_result else None,
            "answer_ar": result.generation_result.answer_ar if result.generation_result else None,
            "confidence": result.generation_result.confidence if result.generation_result else 0.0,
            "sources": [r.to_dict() for r in result.retrieval_results[:5]],
            "success": result.success,
            "processing_time_ms": result.total_time_ms,
        }

    async def _handle_conversation_end(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle conversation end tool call"""
        if not self._conversation_manager:
            return {"error": "Conversation memory not enabled"}

        success = self._conversation_manager.end_session(args["session_id"])
        return {
            "success": success,
            "message": "Session ended" if success else "Session not found",
            "message_ar": "تم إنهاء الجلسة" if success else "الجلسة غير موجودة",
        }

    def get_health(self) -> dict[str, Any]:
        """Get bridge health status.
        الحصول على حالة صحة الجسر"""
        health: dict[str, Any] = {
            "initialized": self._initialized,
            "pipeline": self._pipeline is not None,
            "knowledge_base": self._knowledge_base is not None,
            "rag_tools": self._rag_tools is not None,
            "conversation_memory": self._conversation_memory is not None,
            "embedding_service": self._embedding_service is not None,
            "vector_store": self._vector_store is not None,
        }

        if self._pipeline:
            health["pipeline_metrics"] = self._pipeline.get_metrics()

        if self._conversation_memory:
            health["conversation_stats"] = self._conversation_memory.get_stats()

        if self._rag_tools:
            health["tools_count"] = len(self._rag_tools.get_tools())

        return health

    def shutdown(self) -> None:
        """Shutdown the bridge and cleanup resources.
        إيقاف الجسر وتنظيف الموارد"""
        if self._conversation_memory:
            self._conversation_memory.cleanup_expired()

        self._initialized = False
        logger.info("MCP-RAG bridge shut down | تم إيقاف جسر MCP-RAG")


# ─────────────────────────────────────────────────────────────────────────────
# Convenience functions
# ─────────────────────────────────────────────────────────────────────────────


def create_mcp_rag_bridge(
    config: MCPRAGConfig | None = None,
    auto_initialize: bool = True,
) -> MCPRAGBridge:
    """Create and optionally initialize an MCP-RAG bridge.
    إنشاء واختيارياً تهيئة جسر MCP-RAG

    Args:
        config: Bridge configuration (default: from environment)
        auto_initialize: Whether to initialize immediately

    Returns:
        Configured MCPRAGBridge instance
    """
    bridge = MCPRAGBridge(config=config)
    if auto_initialize:
        bridge.initialize()
    return bridge


def setup_rag_for_mcp_server(
    mcp_server: Any,
    config: MCPRAGConfig | None = None,
) -> MCPRAGBridge:
    """One-line setup: create bridge, initialize, and register with MCP server.
    إعداد من سطر واحد: إنشاء الجسر وتهيئته وتسجيله مع خادم MCP

    Args:
        mcp_server: MCP server instance to register tools with
        config: Bridge configuration (default: from environment)

    Returns:
        Initialized and registered MCPRAGBridge
    """
    bridge = MCPRAGBridge(config=config)
    if bridge.initialize():
        bridge.register_with_mcp_server(mcp_server)
    else:
        logger.error(
            "Failed to set up RAG for MCP server | فشل في إعداد RAG لخادم MCP"
        )
    return bridge


# Export classes
__all__ = [
    "MCPRAGBridge",
    "MCPRAGConfig",
    "create_mcp_rag_bridge",
    "setup_rag_for_mcp_server",
]
