"""
UltraRAG Integration for Copilot API
تكامل UltraRAG مع واجهة Copilot

Provides enhanced RAG capabilities using UltraRAG with Tri-RAG
for both agricultural and code agents.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from shared.ai.ultrarag.providers import AgriRAGProvider, CodeRAGProvider
from shared.ai.ultrarag.models import TriRAGConfig, RetrievalStrategy
from shared.ai.ultrarag.mcp_tools import RAGMCPTools

from .service import CopilotRAGService, RAGConfig, SearchResult

logger = structlog.get_logger(__name__)


@dataclass
class UltraRAGConfig:
    """Configuration for UltraRAG integration"""
    # Weights for Tri-RAG
    dense_weight: float = 0.4
    sparse_weight: float = 0.3
    kg_weight: float = 0.3
    kg_max_hops: int = 2

    # Feature flags
    enable_agri_provider: bool = True
    enable_code_provider: bool = True
    enable_mcp_tools: bool = True

    # Fallback
    fallback_to_basic_rag: bool = True

    def __post_init__(self):
        """Load from environment"""
        self.dense_weight = float(os.getenv("ULTRARAG_DENSE_WEIGHT", str(self.dense_weight)))
        self.sparse_weight = float(os.getenv("ULTRARAG_SPARSE_WEIGHT", str(self.sparse_weight)))
        self.kg_weight = float(os.getenv("ULTRARAG_KG_WEIGHT", str(self.kg_weight)))
        self.kg_max_hops = int(os.getenv("ULTRARAG_KG_MAX_HOPS", str(self.kg_max_hops)))
        self.enable_agri_provider = os.getenv("ULTRARAG_ENABLE_AGRI", "true").lower() == "true"
        self.enable_code_provider = os.getenv("ULTRARAG_ENABLE_CODE", "true").lower() == "true"

    def to_trirag_config(self) -> TriRAGConfig:
        """Convert to TriRAGConfig"""
        return TriRAGConfig(
            dense_weight=self.dense_weight,
            sparse_weight=self.sparse_weight,
            kg_weight=self.kg_weight,
            kg_max_hops=self.kg_max_hops,
        )


class UltraRAGCopilotService:
    """
    Enhanced Copilot RAG Service with UltraRAG Integration.
    خدمة Copilot RAG المحسنة مع تكامل UltraRAG

    Provides:
    - Tri-RAG retrieval (Dense + Sparse + Knowledge Graph)
    - Agricultural advisory through AgriRAGProvider
    - Code analysis through CodeRAGProvider
    - MCP tools integration
    - Fallback to basic RAG if needed
    """

    def __init__(
        self,
        config: Optional[UltraRAGConfig] = None,
        basic_rag_service: Optional[CopilotRAGService] = None,
    ):
        """Initialize UltraRAG Copilot service"""
        self.config = config or UltraRAGConfig()
        self.basic_rag = basic_rag_service

        # UltraRAG providers
        self._agri_provider: Optional[AgriRAGProvider] = None
        self._code_provider: Optional[CodeRAGProvider] = None
        self._mcp_tools: Optional[RAGMCPTools] = None

        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize all providers"""
        if self._initialized:
            return True

        trirag_config = self.config.to_trirag_config()

        # Initialize agricultural provider
        if self.config.enable_agri_provider:
            try:
                self._agri_provider = AgriRAGProvider(config=trirag_config)
                await self._agri_provider.initialize()
                logger.info("AgriRAGProvider initialized")
            except Exception as e:
                logger.error("Failed to initialize AgriRAGProvider", error=str(e))

        # Initialize code provider
        if self.config.enable_code_provider:
            try:
                self._code_provider = CodeRAGProvider(config=trirag_config)
                await self._code_provider.initialize()
                logger.info("CodeRAGProvider initialized")
            except Exception as e:
                logger.error("Failed to initialize CodeRAGProvider", error=str(e))

        # Initialize basic RAG if needed
        if self.basic_rag:
            await self.basic_rag.initialize()

        # Initialize MCP tools
        if self.config.enable_mcp_tools:
            self._mcp_tools = RAGMCPTools()

        self._initialized = True
        logger.info(
            "UltraRAG Copilot service initialized",
            agri_enabled=self._agri_provider is not None,
            code_enabled=self._code_provider is not None,
            mcp_enabled=self._mcp_tools is not None,
        )
        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # Agricultural Advisory Methods
    # ═══════════════════════════════════════════════════════════════════════════

    async def diagnose_disease(
        self,
        symptoms: str,
        crop_type: Optional[str] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Diagnose crop disease using Tri-RAG.
        تشخيص مرض المحصول باستخدام Tri-RAG
        """
        await self.initialize()

        if not self._agri_provider:
            return {"error": "Agricultural provider not available"}

        result = await self._agri_provider.diagnose_disease(
            symptoms=symptoms,
            crop_type=crop_type,
        )

        return {
            "query": result.query,
            "advisory": result.advisory,
            "advisory_ar": result.advisory_ar,
            "confidence": result.confidence,
            "diseases": result.related_entities,
            "treatments": result.treatment_options,
            "sources": result.sources[:3],
        }

    async def recommend_irrigation(
        self,
        crop_type: str,
        growth_stage: str,
        soil_moisture: Optional[float] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Get irrigation recommendations using Tri-RAG.
        الحصول على توصيات الري باستخدام Tri-RAG
        """
        await self.initialize()

        if not self._agri_provider:
            return {"error": "Agricultural provider not available"}

        result = await self._agri_provider.recommend_irrigation(
            crop_type=crop_type,
            growth_stage=growth_stage,
            soil_moisture=soil_moisture,
        )

        return {
            "query": result.query,
            "advisory": result.advisory,
            "advisory_ar": result.advisory_ar,
            "confidence": result.confidence,
            "irrigation_methods": result.related_entities,
            "sources": result.sources[:3],
        }

    async def recommend_fertilizer(
        self,
        crop_type: str,
        growth_stage: str,
        soil_analysis: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Get fertilizer recommendations using Tri-RAG.
        الحصول على توصيات الأسمدة باستخدام Tri-RAG
        """
        await self.initialize()

        if not self._agri_provider:
            return {"error": "Agricultural provider not available"}

        result = await self._agri_provider.recommend_fertilizer(
            crop_type=crop_type,
            growth_stage=growth_stage,
            soil_analysis=soil_analysis,
        )

        return {
            "query": result.query,
            "advisory": result.advisory,
            "advisory_ar": result.advisory_ar,
            "confidence": result.confidence,
            "fertilizers": result.treatment_options,
            "sources": result.sources[:3],
        }

    async def predict_yield(
        self,
        crop_type: str,
        area_hectares: float,
        growth_stage: Optional[str] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Predict yield using Tri-RAG knowledge.
        توقع الإنتاج باستخدام معرفة Tri-RAG
        """
        await self.initialize()

        if not self._agri_provider:
            return {"error": "Agricultural provider not available"}

        result = await self._agri_provider.predict_yield(
            crop_type=crop_type,
            area_hectares=area_hectares,
            growth_stage=growth_stage,
        )

        return {
            "query": result.query,
            "advisory": result.advisory,
            "advisory_ar": result.advisory_ar,
            "confidence": result.confidence,
            "sources": result.sources[:3],
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # Code Analysis Methods
    # ═══════════════════════════════════════════════════════════════════════════

    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Analyze code using Tri-RAG.
        تحليل الكود باستخدام Tri-RAG
        """
        await self.initialize()

        if not self._code_provider:
            return {"error": "Code provider not available"}

        result = await self._code_provider.analyze_code(
            code=code,
            language=language,
        )

        return {
            "query": result.query,
            "analysis": result.analysis,
            "suggestions": result.suggestions,
            "patterns": result.related_patterns,
            "confidence": result.confidence,
            "tools": result.metadata.get("tools", []),
        }

    async def find_fix_pattern(
        self,
        error_message: str,
        language: str = "python",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Find fix pattern for an error.
        إيجاد نمط الإصلاح للخطأ
        """
        await self.initialize()

        if not self._code_provider:
            return {"error": "Code provider not available"}

        result = await self._code_provider.find_fix_pattern(
            error_message=error_message,
            language=language,
        )

        return {
            "query": result.query,
            "analysis": result.analysis,
            "suggestions": result.suggestions,
            "confidence": result.confidence,
            "sources": result.sources[:3],
        }

    async def security_scan(
        self,
        code: str,
        language: str = "python",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Scan code for security issues.
        فحص الكود للمشاكل الأمنية
        """
        await self.initialize()

        if not self._code_provider:
            return {"error": "Code provider not available"}

        result = await self._code_provider.security_scan(
            code=code,
            language=language,
        )

        return {
            "query": result.query,
            "analysis": result.analysis,
            "suggestions": result.suggestions,
            "security_issues": result.related_patterns,
            "confidence": result.confidence,
        }

    async def get_best_practices(
        self,
        topic: str,
        language: str = "python",
        framework: Optional[str] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Get best practices for a topic.
        الحصول على أفضل الممارسات لموضوع
        """
        await self.initialize()

        if not self._code_provider:
            return {"error": "Code provider not available"}

        result = await self._code_provider.get_best_practices(
            topic=topic,
            language=language,
            framework=framework,
        )

        return {
            "query": result.query,
            "analysis": result.analysis,
            "suggestions": result.suggestions,
            "confidence": result.confidence,
            "sources": result.sources[:3],
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # General Query Methods
    # ═══════════════════════════════════════════════════════════════════════════

    async def query(
        self,
        query: str,
        domain: str = "auto",  # auto, agricultural, code
        **kwargs,
    ) -> dict[str, Any]:
        """
        General query with automatic domain detection.
        استعلام عام مع كشف تلقائي للمجال
        """
        await self.initialize()

        # Auto-detect domain
        if domain == "auto":
            domain = self._detect_domain(query)

        if domain == "agricultural" and self._agri_provider:
            result = await self._agri_provider.general_query(query)
            return {
                "domain": "agricultural",
                "query": result.query,
                "response": result.advisory,
                "response_ar": result.advisory_ar,
                "confidence": result.confidence,
                "sources": result.sources[:5],
            }

        elif domain == "code" and self._code_provider:
            result = await self._code_provider.general_query(query)
            return {
                "domain": "code",
                "query": result.query,
                "response": result.analysis,
                "confidence": result.confidence,
                "sources": result.sources[:5],
            }

        # Fallback to basic RAG
        if self.basic_rag and self.config.fallback_to_basic_rag:
            results = await self.basic_rag.search(query, top_k=5)
            return {
                "domain": "general",
                "query": query,
                "response": self.basic_rag.format_context_for_prompt(results),
                "confidence": results[0].score if results else 0.0,
                "sources": [r.document.to_dict() for r in results],
            }

        return {"error": "No suitable provider available", "query": query}

    def _detect_domain(self, query: str) -> str:
        """Detect query domain based on keywords"""
        query_lower = query.lower()

        # Agricultural keywords
        agri_keywords = [
            "crop", "wheat", "barley", "irrigation", "fertilizer",
            "disease", "pest", "yield", "harvest", "soil", "farm",
            "محصول", "قمح", "شعير", "ري", "سماد", "مرض", "آفة",
            "إنتاج", "حصاد", "تربة", "مزرعة", "زراعة",
        ]

        # Code keywords
        code_keywords = [
            "code", "error", "bug", "function", "class", "import",
            "python", "typescript", "dart", "fix", "lint", "test",
            "security", "vulnerability", "api", "database",
        ]

        agri_score = sum(1 for kw in agri_keywords if kw in query_lower)
        code_score = sum(1 for kw in code_keywords if kw in query_lower)

        if agri_score > code_score:
            return "agricultural"
        elif code_score > agri_score:
            return "code"
        return "general"

    # ═══════════════════════════════════════════════════════════════════════════
    # MCP Tools
    # ═══════════════════════════════════════════════════════════════════════════

    def get_mcp_tools(self) -> list[dict[str, Any]]:
        """Get available MCP tools"""
        tools = []

        # Agricultural tools
        if self._agri_provider:
            tools.extend([
                {
                    "name": "diagnose_disease",
                    "description": "Diagnose crop disease from symptoms | تشخيص مرض المحصول من الأعراض",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "symptoms": {"type": "string"},
                            "crop_type": {"type": "string"},
                        },
                        "required": ["symptoms"],
                    },
                },
                {
                    "name": "recommend_irrigation",
                    "description": "Get irrigation recommendations | الحصول على توصيات الري",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "crop_type": {"type": "string"},
                            "growth_stage": {"type": "string"},
                            "soil_moisture": {"type": "number"},
                        },
                        "required": ["crop_type", "growth_stage"],
                    },
                },
                {
                    "name": "recommend_fertilizer",
                    "description": "Get fertilizer recommendations | الحصول على توصيات الأسمدة",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "crop_type": {"type": "string"},
                            "growth_stage": {"type": "string"},
                            "soil_analysis": {"type": "object"},
                        },
                        "required": ["crop_type", "growth_stage"],
                    },
                },
            ])

        # Code tools
        if self._code_provider:
            tools.extend([
                {
                    "name": "analyze_code",
                    "description": "Analyze code for issues | تحليل الكود للمشاكل",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "language": {"type": "string", "enum": ["python", "typescript", "dart"]},
                        },
                        "required": ["code"],
                    },
                },
                {
                    "name": "security_scan",
                    "description": "Scan code for security vulnerabilities | فحص الكود للثغرات الأمنية",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "language": {"type": "string"},
                        },
                        "required": ["code"],
                    },
                },
            ])

        return tools

    async def call_mcp_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Call an MCP tool by name"""
        tool_handlers = {
            "diagnose_disease": self.diagnose_disease,
            "recommend_irrigation": self.recommend_irrigation,
            "recommend_fertilizer": self.recommend_fertilizer,
            "predict_yield": self.predict_yield,
            "analyze_code": self.analyze_code,
            "find_fix_pattern": self.find_fix_pattern,
            "security_scan": self.security_scan,
            "get_best_practices": self.get_best_practices,
        }

        handler = tool_handlers.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}

        try:
            return await handler(**arguments)
        except Exception as e:
            logger.error("MCP tool error", tool=name, error=str(e))
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════════════════════
    # Status and Stats
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_stats(self) -> dict[str, Any]:
        """Get service statistics"""
        stats = {
            "initialized": self._initialized,
            "agri_provider": self._agri_provider is not None,
            "code_provider": self._code_provider is not None,
            "mcp_tools_count": len(self.get_mcp_tools()),
            "config": {
                "dense_weight": self.config.dense_weight,
                "sparse_weight": self.config.sparse_weight,
                "kg_weight": self.config.kg_weight,
                "kg_max_hops": self.config.kg_max_hops,
            },
        }

        if self._agri_provider:
            stats["agri_entities"] = len(self._agri_provider.knowledge_graph._entities)
            stats["agri_relations"] = len(self._agri_provider.knowledge_graph._relations)

        if self._code_provider:
            stats["code_entities"] = len(self._code_provider.knowledge_graph._entities)
            stats["code_relations"] = len(self._code_provider.knowledge_graph._relations)

        return stats


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_ultrarag_service: Optional[UltraRAGCopilotService] = None


def get_ultrarag_service() -> UltraRAGCopilotService:
    """Get or create global UltraRAG Copilot service"""
    global _ultrarag_service
    if _ultrarag_service is None:
        from .service import get_rag_service
        _ultrarag_service = UltraRAGCopilotService(
            basic_rag_service=get_rag_service()
        )
    return _ultrarag_service
