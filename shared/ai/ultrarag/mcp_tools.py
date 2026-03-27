# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG MCP Tools - Model Context Protocol Integration
# أدوات MCP لـ UltraRAG - تكامل بروتوكول سياق النموذج
# ═══════════════════════════════════════════════════════════════════════════════

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import structlog

from .knowledge_base import KnowledgeBase
from .models import (
    GenerationMode,
    RAGRequest,
    RerankingMethod,
    RetrievalStrategy,
)
from .pipeline import RAGPipeline

logger = structlog.get_logger(__name__)


@dataclass
class MCPToolDefinition:
    """MCP Tool definition | تعريف أداة MCP"""

    name: str
    description: str
    description_ar: str
    input_schema: dict[str, Any]
    handler: Callable
    category: str = "rag"


class RAGMCPTools:
    """
    MCP Tools for RAG Operations
    أدوات MCP لعمليات RAG
    """

    def __init__(
        self,
        rag_pipeline: RAGPipeline | None = None,
        knowledge_base: KnowledgeBase | None = None,
    ):
        self.rag_pipeline = rag_pipeline
        self.knowledge_base = knowledge_base
        self._tools: dict[str, MCPToolDefinition] = {}

        # Register built-in tools
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in RAG tools"""

        # ═══════════════════════════════════════════════════════════════════════
        # Query Tools
        # ═══════════════════════════════════════════════════════════════════════

        self._register_tool(
            MCPToolDefinition(
                name="rag_query",
                description="Query the RAG system with a question and get an answer with sources",
                description_ar="استعلام نظام RAG بسؤال والحصول على إجابة مع المصادر",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or query to answer | السؤال أو الاستعلام للإجابة عليه",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Collection to search in | المجموعة للبحث فيها",
                            "default": "default",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to retrieve | عدد النتائج للاسترجاع",
                            "default": 5,
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ar"],
                            "description": "Response language | لغة الاستجابة",
                            "default": "en",
                        },
                    },
                    "required": ["query"],
                },
                handler=self._handle_rag_query,
                category="query",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="semantic_search",
                description="Perform semantic search to find relevant documents",
                description_ar="إجراء بحث دلالي للعثور على المستندات ذات الصلة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query | استعلام البحث",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Collection to search | المجموعة للبحث",
                            "default": "default",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results | عدد النتائج",
                            "default": 10,
                        },
                        "min_score": {
                            "type": "number",
                            "description": "Minimum similarity score | الحد الأدنى لدرجة التشابه",
                            "default": 0.0,
                        },
                    },
                    "required": ["query"],
                },
                handler=self._handle_semantic_search,
                category="query",
            )
        )

        # ═══════════════════════════════════════════════════════════════════════
        # Knowledge Base Tools
        # ═══════════════════════════════════════════════════════════════════════

        self._register_tool(
            MCPToolDefinition(
                name="add_document",
                description="Add a document to the knowledge base",
                description_ar="إضافة مستند إلى قاعدة المعرفة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Document text content | محتوى المستند النصي",
                        },
                        "title": {
                            "type": "string",
                            "description": "Document title | عنوان المستند",
                        },
                        "text_ar": {
                            "type": "string",
                            "description": "Arabic text content (optional) | المحتوى العربي (اختياري)",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Target collection | المجموعة المستهدفة",
                            "default": "default",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata | بيانات وصفية إضافية",
                        },
                    },
                    "required": ["text", "title"],
                },
                handler=self._handle_add_document,
                category="knowledge_base",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="add_file",
                description="Add a file to the knowledge base",
                description_ar="إضافة ملف إلى قاعدة المعرفة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file | مسار الملف",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Target collection | المجموعة المستهدفة",
                            "default": "default",
                        },
                    },
                    "required": ["file_path"],
                },
                handler=self._handle_add_file,
                category="knowledge_base",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="list_documents",
                description="List documents in the knowledge base",
                description_ar="عرض المستندات في قاعدة المعرفة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Filter by collection | تصفية حسب المجموعة",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results | الحد الأقصى لعدد النتائج",
                            "default": 50,
                        },
                    },
                },
                handler=self._handle_list_documents,
                category="knowledge_base",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="delete_document",
                description="Delete a document from the knowledge base",
                description_ar="حذف مستند من قاعدة المعرفة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "ID of document to delete | معرف المستند للحذف",
                        },
                    },
                    "required": ["document_id"],
                },
                handler=self._handle_delete_document,
                category="knowledge_base",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="kb_stats",
                description="Get knowledge base statistics",
                description_ar="الحصول على إحصائيات قاعدة المعرفة",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
                handler=self._handle_kb_stats,
                category="knowledge_base",
            )
        )

        # ═══════════════════════════════════════════════════════════════════════
        # Pipeline Configuration Tools
        # ═══════════════════════════════════════════════════════════════════════

        self._register_tool(
            MCPToolDefinition(
                name="configure_pipeline",
                description="Configure RAG pipeline settings",
                description_ar="تكوين إعدادات خط أنابيب RAG",
                input_schema={
                    "type": "object",
                    "properties": {
                        "retrieval_strategy": {
                            "type": "string",
                            "enum": ["dense", "sparse", "hybrid", "adaptive"],
                            "description": "Retrieval strategy | استراتيجية الاسترجاع",
                        },
                        "reranking_method": {
                            "type": "string",
                            "enum": ["none", "cross_encoder", "llm", "reciprocal_rank"],
                            "description": "Reranking method | طريقة إعادة الترتيب",
                        },
                        "generation_mode": {
                            "type": "string",
                            "enum": ["standard", "cot", "self_reflective", "iterative"],
                            "description": "Generation mode | وضع التوليد",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of documents to retrieve | عدد المستندات للاسترجاع",
                        },
                        "chunk_size": {
                            "type": "integer",
                            "description": "Chunk size for documents | حجم القطعة للمستندات",
                        },
                    },
                },
                handler=self._handle_configure_pipeline,
                category="configuration",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="get_pipeline_config",
                description="Get current RAG pipeline configuration",
                description_ar="الحصول على تكوين خط أنابيب RAG الحالي",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
                handler=self._handle_get_pipeline_config,
                category="configuration",
            )
        )

        # ═══════════════════════════════════════════════════════════════════════
        # Agricultural Advisory Tools
        # ═══════════════════════════════════════════════════════════════════════

        self._register_tool(
            MCPToolDefinition(
                name="crop_advisory",
                description="Get agricultural advisory for a specific crop and situation",
                description_ar="الحصول على استشارة زراعية لمحصول وحالة معينة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "crop": {
                            "type": "string",
                            "description": "Crop type (e.g., wheat, barley, date_palm) | نوع المحصول",
                        },
                        "issue": {
                            "type": "string",
                            "description": "Issue or question (e.g., 'yellowing leaves', 'irrigation schedule') | المشكلة أو السؤال",
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context (soil_type, growth_stage, etc.) | سياق إضافي",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ar", "both"],
                            "description": "Response language | لغة الاستجابة",
                            "default": "both",
                        },
                    },
                    "required": ["crop", "issue"],
                },
                handler=self._handle_crop_advisory,
                category="agricultural",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="pest_identification",
                description="Identify pests and get treatment recommendations",
                description_ar="تحديد الآفات والحصول على توصيات العلاج",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symptoms": {
                            "type": "string",
                            "description": "Observed symptoms | الأعراض الملاحظة",
                        },
                        "crop": {
                            "type": "string",
                            "description": "Affected crop | المحصول المتأثر",
                        },
                        "region": {
                            "type": "string",
                            "description": "Geographic region | المنطقة الجغرافية",
                        },
                    },
                    "required": ["symptoms"],
                },
                handler=self._handle_pest_identification,
                category="agricultural",
            )
        )

        # ═══════════════════════════════════════════════════════════════════════
        # Satellite & GEE Analysis Tools
        # أدوات تحليل صور الأقمار الصناعية
        # ═══════════════════════════════════════════════════════════════════════

        self._register_tool(
            MCPToolDefinition(
                name="ndvi_time_series",
                description="Analyze NDVI time series for a field to detect trends, anomalies, and phenology",
                description_ar="تحليل السلسلة الزمنية لـ NDVI للحقل لاكتشاف الاتجاهات والشذوذ ومراحل النمو",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Field identifier | معرف الحقل",
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Start date (YYYY-MM-DD) | تاريخ البداية",
                        },
                        "end_date": {
                            "type": "string",
                            "format": "date",
                            "description": "End date (YYYY-MM-DD) | تاريخ النهاية",
                        },
                        "index_type": {
                            "type": "string",
                            "enum": ["ndvi", "evi", "savi", "ndwi", "ndmi", "lai"],
                            "description": "Vegetation index type | نوع مؤشر الغطاء النباتي",
                            "default": "ndvi",
                        },
                        "satellite": {
                            "type": "string",
                            "enum": ["sentinel_2", "landsat_8", "landsat_9", "modis"],
                            "description": "Satellite source | مصدر القمر الصناعي",
                            "default": "sentinel_2",
                        },
                    },
                    "required": ["field_id", "start_date", "end_date"],
                },
                handler=self._handle_ndvi_time_series,
                category="satellite",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="change_detection",
                description="Detect vegetation changes between two dates (harvest, planting, stress, drought)",
                description_ar="كشف تغيرات الغطاء النباتي بين تاريخين (حصاد، زراعة، إجهاد، جفاف)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Field identifier | معرف الحقل",
                        },
                        "date1": {
                            "type": "string",
                            "format": "date",
                            "description": "First date (YYYY-MM-DD) | التاريخ الأول",
                        },
                        "date2": {
                            "type": "string",
                            "format": "date",
                            "description": "Second date (YYYY-MM-DD) | التاريخ الثاني",
                        },
                        "ndvi1": {
                            "type": "number",
                            "description": "NDVI value at date1 (optional) | قيمة NDVI في التاريخ الأول",
                        },
                        "ndvi2": {
                            "type": "number",
                            "description": "NDVI value at date2 (optional) | قيمة NDVI في التاريخ الثاني",
                        },
                    },
                    "required": ["field_id", "date1", "date2"],
                },
                handler=self._handle_change_detection,
                category="satellite",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="land_cover_classification",
                description="Classify land cover type (cropland, forest, bare soil, water) from satellite imagery",
                description_ar="تصنيف نوع الغطاء الأرضي (زراعي، غابة، تربة عارية، ماء) من صور الأقمار الصناعية",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Field identifier | معرف الحقل",
                        },
                        "analysis_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Date for analysis (YYYY-MM-DD) | تاريخ التحليل",
                        },
                        "ndvi": {
                            "type": "number",
                            "description": "NDVI value (optional) | قيمة NDVI",
                        },
                        "ndwi": {
                            "type": "number",
                            "description": "NDWI value (optional) | قيمة NDWI",
                        },
                    },
                    "required": ["field_id"],
                },
                handler=self._handle_land_cover,
                category="satellite",
            )
        )

        self._register_tool(
            MCPToolDefinition(
                name="satellite_query",
                description="General query about satellite imagery, vegetation indices, or remote sensing",
                description_ar="استعلام عام عن صور الأقمار الصناعية أو مؤشرات الغطاء النباتي أو الاستشعار عن بعد",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query about satellite imagery | استعلام عن صور الأقمار الصناعية",
                        },
                        "field_id": {
                            "type": "string",
                            "description": "Optional field context | سياق الحقل (اختياري)",
                        },
                    },
                    "required": ["query"],
                },
                handler=self._handle_satellite_query,
                category="satellite",
            )
        )

    def _register_tool(self, tool: MCPToolDefinition):
        """Register a tool"""
        self._tools[tool.name] = tool

    def get_tools(self) -> list[dict[str, Any]]:
        """Get all tools in MCP format"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    def get_tools_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get tools filtered by category"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in self._tools.values()
            if tool.category == category
        ]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Call a tool by name"""
        if name not in self._tools:
            return {
                "success": False,
                "error": f"Tool not found: {name}",
            }

        tool = self._tools[name]

        try:
            result = await tool.handler(arguments)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            logger.error("mcp_tool_error", tool=name, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }

    # ═══════════════════════════════════════════════════════════════════════════
    # Tool Handlers
    # ═══════════════════════════════════════════════════════════════════════════

    async def _handle_rag_query(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle RAG query"""
        if self.rag_pipeline is None:
            return {"error": "RAG pipeline not configured"}

        request = RAGRequest(
            query=args["query"],
            collection=args.get("collection", "default"),
            top_k=args.get("top_k", 5),
            language=args.get("language", "en"),
        )

        result = await self.rag_pipeline.run(request)

        return {
            "answer": result.generation_result.answer if result.generation_result else None,
            "answer_ar": result.generation_result.answer_ar if result.generation_result else None,
            "confidence": result.generation_result.confidence if result.generation_result else 0.0,
            "sources": [r.to_dict() for r in result.retrieval_results[:5]],
            "success": result.success,
            "processing_time_ms": result.total_time_ms,
        }

    async def _handle_semantic_search(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle semantic search"""
        if self.rag_pipeline is None:
            return {"error": "RAG pipeline not configured"}

        from .retriever import RetrievalConfig

        config = RetrievalConfig(
            top_k=args.get("top_k", 10),
            collection=args.get("collection", "default"),
            min_score_threshold=args.get("min_score", 0.0),
        )

        results = await self.rag_pipeline.retriever.retrieve(args["query"], config)

        return {
            "results": [r.to_dict() for r in results],
            "count": len(results),
        }

    async def _handle_add_document(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle add document"""
        if self.knowledge_base is None:
            return {"error": "Knowledge base not configured"}

        doc = await self.knowledge_base.add_text(
            text=args["text"],
            title=args["title"],
            text_ar=args.get("text_ar"),
            collection=args.get("collection", "default"),
            metadata=args.get("metadata", {}),
        )

        if doc:
            return {
                "document_id": doc.id,
                "title": doc.title,
                "chunks_count": len(doc.chunks),
            }
        return {"error": "Failed to add document"}

    async def _handle_add_file(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle add file"""
        if self.knowledge_base is None:
            return {"error": "Knowledge base not configured"}

        doc = await self.knowledge_base.add_file(
            file_path=args["file_path"],
            collection=args.get("collection", "default"),
        )

        if doc:
            return {
                "document_id": doc.id,
                "title": doc.title,
                "chunks_count": len(doc.chunks),
            }
        return {"error": "Failed to add file"}

    async def _handle_list_documents(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle list documents"""
        if self.knowledge_base is None:
            return {"error": "Knowledge base not configured"}

        docs = self.knowledge_base.list_documents(
            collection=args.get("collection"),
            limit=args.get("limit", 50),
        )

        return {
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "collection": d.collection,
                    "chunks_count": len(d.chunks),
                    "created_at": d.created_at.isoformat(),
                }
                for d in docs
            ],
            "count": len(docs),
        }

    async def _handle_delete_document(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle delete document"""
        if self.knowledge_base is None:
            return {"error": "Knowledge base not configured"}

        success = await self.knowledge_base.delete_document(args["document_id"])
        return {"success": success}

    async def _handle_kb_stats(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle KB stats"""
        if self.knowledge_base is None:
            return {"error": "Knowledge base not configured"}

        return self.knowledge_base.get_stats()

    async def _handle_configure_pipeline(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle pipeline configuration"""
        if self.rag_pipeline is None:
            return {"error": "RAG pipeline not configured"}

        config = self.rag_pipeline.config

        if "retrieval_strategy" in args:
            config.retrieval_strategy = RetrievalStrategy(args["retrieval_strategy"])
        if "reranking_method" in args:
            config.reranking_method = RerankingMethod(args["reranking_method"])
        if "generation_mode" in args:
            config.generation_mode = GenerationMode(args["generation_mode"])
        if "top_k" in args:
            config.top_k = args["top_k"]
        if "chunk_size" in args:
            config.chunk_size = args["chunk_size"]

        return {"message": "Pipeline configured", "config": config.to_dict()}

    async def _handle_get_pipeline_config(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle get pipeline config"""
        if self.rag_pipeline is None:
            return {"error": "RAG pipeline not configured"}

        return self.rag_pipeline.config.to_dict()

    async def _handle_crop_advisory(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle crop advisory query"""
        if self.rag_pipeline is None:
            return {"error": "RAG pipeline not configured"}

        # Build agricultural query
        crop = args["crop"]
        issue = args["issue"]
        context = args.get("context", {})
        language = args.get("language", "both")

        query = f"Agricultural advisory for {crop}: {issue}"
        if context:
            query += f". Context: {json.dumps(context)}"

        request = RAGRequest(
            query=query,
            collection="agricultural_knowledge",
            top_k=5,
            language="en" if language == "en" else "ar",
        )

        result = await self.rag_pipeline.run(request)

        response = {
            "crop": crop,
            "issue": issue,
            "advisory": result.generation_result.answer if result.generation_result else None,
            "confidence": result.generation_result.confidence if result.generation_result else 0.0,
            "sources": [r.to_dict() for r in result.retrieval_results[:3]],
        }

        if language in ["ar", "both"] and result.generation_result:
            response["advisory_ar"] = result.generation_result.answer_ar

        return response

    async def _handle_pest_identification(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle pest identification"""
        if self.rag_pipeline is None:
            return {"error": "RAG pipeline not configured"}

        symptoms = args["symptoms"]
        crop = args.get("crop", "")
        region = args.get("region", "")

        query = f"Identify pest from symptoms: {symptoms}"
        if crop:
            query += f" on {crop}"
        if region:
            query += f" in {region}"
        query += ". Provide treatment recommendations."

        request = RAGRequest(
            query=query,
            collection="pest_knowledge",
            top_k=5,
        )

        result = await self.rag_pipeline.run(request)

        return {
            "symptoms": symptoms,
            "identification": result.generation_result.answer if result.generation_result else None,
            "confidence": result.generation_result.confidence if result.generation_result else 0.0,
            "sources": [r.to_dict() for r in result.retrieval_results[:3]],
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # Satellite & GEE Tool Handlers
    # معالجات أدوات صور الأقمار الصناعية
    # ═══════════════════════════════════════════════════════════════════════════

    async def _handle_ndvi_time_series(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle NDVI time series analysis"""
        from datetime import date

        try:
            from .providers.gee_provider import GEERAGProvider, VegetationIndex

            provider = GEERAGProvider()

            # Parse dates
            start_date = date.fromisoformat(args["start_date"])
            end_date = date.fromisoformat(args["end_date"])

            # Map index type
            index_str = args.get("index_type", "ndvi").upper()
            index_type = (
                VegetationIndex[index_str] if index_str in VegetationIndex.__members__ else VegetationIndex.NDVI
            )

            result = await provider.analyze_time_series(
                field_id=args["field_id"],
                start_date=start_date,
                end_date=end_date,
                index_type=index_type,
            )

            if result.time_series:
                return {
                    "field_id": args["field_id"],
                    "analysis": result.time_series.to_dict(),
                    "confidence": result.confidence,
                    "sources": result.sources[:3],
                }

            return {"error": "No time series data available"}

        except ImportError:
            return {"error": "GEE provider not available"}
        except Exception as e:
            logger.error("ndvi_time_series_error", error=str(e))
            return {"error": str(e)}

    async def _handle_change_detection(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle change detection between dates"""
        from datetime import date

        try:
            from .providers.gee_provider import GEERAGProvider

            provider = GEERAGProvider()

            # Parse dates
            date1 = date.fromisoformat(args["date1"])
            date2 = date.fromisoformat(args["date2"])

            result = await provider.detect_changes(
                field_id=args["field_id"],
                date1=date1,
                date2=date2,
                ndvi1=args.get("ndvi1"),
                ndvi2=args.get("ndvi2"),
            )

            if result.change_detection:
                return {
                    "field_id": args["field_id"],
                    "change": result.change_detection.to_dict(),
                    "confidence": result.confidence,
                    "sources": result.sources[:3],
                }

            return {"error": "No change detection result"}

        except ImportError:
            return {"error": "GEE provider not available"}
        except Exception as e:
            logger.error("change_detection_error", error=str(e))
            return {"error": str(e)}

    async def _handle_land_cover(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle land cover classification"""
        from datetime import date

        try:
            from .providers.gee_provider import GEERAGProvider

            provider = GEERAGProvider()

            # Parse date or use today
            analysis_date = date.today()
            if "analysis_date" in args and args["analysis_date"]:
                analysis_date = date.fromisoformat(args["analysis_date"])

            result = await provider.classify_land_cover(
                field_id=args["field_id"],
                analysis_date=analysis_date,
                ndvi=args.get("ndvi"),
                ndwi=args.get("ndwi"),
            )

            if result.land_cover:
                return {
                    "field_id": args["field_id"],
                    "classification": result.land_cover.to_dict(),
                    "confidence": result.confidence,
                    "sources": result.sources[:3],
                }

            return {"error": "No land cover classification result"}

        except ImportError:
            return {"error": "GEE provider not available"}
        except Exception as e:
            logger.error("land_cover_error", error=str(e))
            return {"error": str(e)}

    async def _handle_satellite_query(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle general satellite query"""
        try:
            from .providers.gee_provider import GEERAGProvider

            provider = GEERAGProvider()

            result = await provider.general_query(
                query=args["query"],
            )

            return {
                "query": args["query"],
                "related_entities": result.related_entities,
                "sources": result.sources[:5],
                "confidence": result.confidence,
            }

        except ImportError:
            return {"error": "GEE provider not available"}
        except Exception as e:
            logger.error("satellite_query_error", error=str(e))
            return {"error": str(e)}


def register_rag_tools(mcp_server: Any, rag_tools: RAGMCPTools):
    """
    Register RAG tools with MCP server
    تسجيل أدوات RAG مع خادم MCP
    """
    tools = rag_tools.get_tools()

    for tool in tools:
        logger.info("registering_mcp_tool", tool_name=tool["name"])

        # Register with MCP server (implementation depends on MCP server API)
        if hasattr(mcp_server, "register_tool"):
            mcp_server.register_tool(
                name=tool["name"],
                description=tool["description"],
                input_schema=tool["inputSchema"],
                handler=lambda args, t=tool["name"]: rag_tools.call_tool(t, args),
            )

    logger.info("rag_tools_registered", count=len(tools))


# Export classes
__all__ = [
    "RAGMCPTools",
    "MCPToolDefinition",
    "register_rag_tools",
]
