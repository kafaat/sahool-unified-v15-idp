# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL MCP RAG Integration - UltraRAG 3.0 Integration
# تكامل RAG مع MCP - دمج UltraRAG 3.0
# ═══════════════════════════════════════════════════════════════════════════════

"""
Integrates UltraRAG 3.0 capabilities with the SAHOOL MCP Server.
Provides RAG tools for knowledge retrieval, document management, and
agricultural advisory generation.

Features:
- Semantic search across agricultural knowledge bases
- Document ingestion and chunking
- RAG-powered advisory generation
- Bilingual Arabic/English support
- YAML workflow execution

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

import json
import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RAGToolResult(BaseModel):
    """Standard result format for RAG tool execution"""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    error_ar: str | None = None
    metadata: dict[str, Any] | None = None


class RAGTools:
    """
    RAG Tools for MCP Integration with UltraRAG 3.0

    Provides agricultural knowledge retrieval and advisory generation
    capabilities through the Model Context Protocol.
    """

    def __init__(
        self,
        rag_pipeline: Any = None,
        knowledge_base: Any = None,
        workflow_engine: Any = None,
    ):
        """
        Initialize RAG Tools

        Args:
            rag_pipeline: UltraRAG pipeline instance
            knowledge_base: Knowledge base instance
            workflow_engine: Workflow engine instance
        """
        self.rag_pipeline = rag_pipeline
        self.knowledge_base = knowledge_base
        self.workflow_engine = workflow_engine

        self._initialized = False

    async def initialize(self):
        """Lazy initialization of RAG components"""
        if self._initialized:
            return

        try:
            # Import UltraRAG components
            from shared.ai.ultrarag import (
                GenerationMode,
                KnowledgeBase,
                RAGPipeline,
                RAGPipelineBuilder,
                RerankingMethod,
                RetrievalStrategy,
                WorkflowEngine,
            )

            # Initialize if not provided
            if self.rag_pipeline is None:
                logger.info("Initializing default RAG pipeline")
                self.rag_pipeline = (
                    RAGPipelineBuilder("sahool-rag")
                    .with_retrieval_strategy(RetrievalStrategy.HYBRID)
                    .with_reranking(RerankingMethod.CROSS_ENCODER)
                    .with_generation_mode(GenerationMode.STANDARD)
                    .with_arabic_support(True)
                    .with_top_k(10, 5)
                    .build()
                )

            if self.knowledge_base is None:
                self.knowledge_base = KnowledgeBase()

            if self.workflow_engine is None:
                self.workflow_engine = WorkflowEngine(self.rag_pipeline)

            self._initialized = True
            logger.info("RAG tools initialized successfully")

        except ImportError as e:
            logger.warning(f"UltraRAG not available: {e}")
            self._initialized = True  # Mark as initialized to prevent retries
        except Exception as e:
            logger.error(f"RAG initialization error: {e}")
            self._initialized = True

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Get MCP tool definitions for RAG tools"""
        return [
            # ═══════════════════════════════════════════════════════════════
            # RAG Query Tools
            # ═══════════════════════════════════════════════════════════════
            {
                "name": "rag_query",
                "description": "Query the RAG system with a question and get an answer with sources. Use for agricultural advisory, pest identification, and general knowledge queries. | استعلام نظام RAG بسؤال والحصول على إجابة مع المصادر. يستخدم للاستشارات الزراعية وتحديد الآفات والاستعلامات المعرفية العامة.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or query to answer | السؤال أو الاستعلام للإجابة عليه",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Knowledge collection to search (default, crop_knowledge, pest_knowledge, irrigation_practices) | مجموعة المعرفة للبحث",
                            "default": "default",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of source documents to retrieve | عدد المستندات المصدر للاسترجاع",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20,
                        },
                        "language": {
                            "type": "string",
                            "description": "Response language | لغة الاستجابة",
                            "enum": ["en", "ar", "both"],
                            "default": "both",
                        },
                        "include_sources": {
                            "type": "boolean",
                            "description": "Include source documents in response | تضمين المستندات المصدر في الاستجابة",
                            "default": True,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "semantic_search",
                "description": "Perform semantic search to find relevant documents without generating an answer. | إجراء بحث دلالي للعثور على المستندات ذات الصلة بدون توليد إجابة.",
                "inputSchema": {
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
                            "minimum": 1,
                            "maximum": 50,
                        },
                        "min_score": {
                            "type": "number",
                            "description": "Minimum similarity score (0-1) | الحد الأدنى لدرجة التشابه",
                            "default": 0.3,
                            "minimum": 0.0,
                            "maximum": 1.0,
                        },
                    },
                    "required": ["query"],
                },
            },
            # ═══════════════════════════════════════════════════════════════
            # Knowledge Base Management Tools
            # ═══════════════════════════════════════════════════════════════
            {
                "name": "add_knowledge",
                "description": "Add a document to the agricultural knowledge base. | إضافة مستند إلى قاعدة المعرفة الزراعية.",
                "inputSchema": {
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
                        "title_ar": {
                            "type": "string",
                            "description": "Arabic title (optional) | العنوان العربي (اختياري)",
                        },
                        "collection": {
                            "type": "string",
                            "description": "Target collection | المجموعة المستهدفة",
                            "default": "default",
                        },
                        "source": {
                            "type": "string",
                            "description": "Source attribution | إسناد المصدر",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata (crop_type, region, etc.) | بيانات وصفية إضافية",
                        },
                    },
                    "required": ["text", "title"],
                },
            },
            {
                "name": "list_knowledge",
                "description": "List documents in the knowledge base. | عرض المستندات في قاعدة المعرفة.",
                "inputSchema": {
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
                            "minimum": 1,
                            "maximum": 200,
                        },
                    },
                },
            },
            {
                "name": "delete_knowledge",
                "description": "Delete a document from the knowledge base. | حذف مستند من قاعدة المعرفة.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "ID of document to delete | معرف المستند للحذف",
                        },
                    },
                    "required": ["document_id"],
                },
            },
            {
                "name": "knowledge_stats",
                "description": "Get knowledge base statistics. | الحصول على إحصائيات قاعدة المعرفة.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            # ═══════════════════════════════════════════════════════════════
            # Agricultural Advisory Tools
            # ═══════════════════════════════════════════════════════════════
            {
                "name": "crop_advisory_rag",
                "description": "Get comprehensive crop advisory using RAG. Combines knowledge base search with AI generation for detailed recommendations. | الحصول على استشارة شاملة للمحاصيل باستخدام RAG. يجمع بين البحث في قاعدة المعرفة والتوليد بالذكاء الاصطناعي للحصول على توصيات مفصلة.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "crop": {
                            "type": "string",
                            "description": "Crop type (wheat, barley, date_palm, tomato, etc.) | نوع المحصول",
                        },
                        "issue": {
                            "type": "string",
                            "description": "Issue or question (yellowing leaves, irrigation schedule, pest control) | المشكلة أو السؤال",
                        },
                        "growth_stage": {
                            "type": "string",
                            "description": "Current growth stage | مرحلة النمو الحالية",
                        },
                        "region": {
                            "type": "string",
                            "description": "Geographic region | المنطقة الجغرافية",
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context (soil_type, weather, etc.) | سياق إضافي",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ar", "both"],
                            "default": "both",
                        },
                    },
                    "required": ["crop", "issue"],
                },
            },
            {
                "name": "irrigation_advisory_rag",
                "description": "Get smart irrigation recommendation using RAG and real-time data. | الحصول على توصية ري ذكية باستخدام RAG والبيانات الآنية.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Field identifier | معرف الحقل",
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Crop type | نوع المحصول",
                        },
                        "soil_moisture": {
                            "type": "number",
                            "description": "Current soil moisture percentage | نسبة رطوبة التربة الحالية",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "growth_stage": {
                            "type": "string",
                            "description": "Crop growth stage | مرحلة نمو المحصول",
                        },
                        "weather_forecast": {
                            "type": "object",
                            "description": "Weather forecast data | بيانات توقعات الطقس",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ar", "both"],
                            "default": "both",
                        },
                    },
                    "required": ["crop_type"],
                },
            },
            {
                "name": "pest_identification_rag",
                "description": "Identify pests and diseases using RAG knowledge base. | تحديد الآفات والأمراض باستخدام قاعدة معرفة RAG.",
                "inputSchema": {
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
                        "affected_parts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Affected plant parts (leaves, stem, root, fruit) | أجزاء النبات المتأثرة",
                        },
                        "region": {
                            "type": "string",
                            "description": "Geographic region | المنطقة الجغرافية",
                        },
                        "season": {
                            "type": "string",
                            "description": "Current season | الموسم الحالي",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ar", "both"],
                            "default": "both",
                        },
                    },
                    "required": ["symptoms"],
                },
            },
            # ═══════════════════════════════════════════════════════════════
            # Workflow Execution Tools
            # ═══════════════════════════════════════════════════════════════
            {
                "name": "execute_rag_workflow",
                "description": "Execute a predefined RAG workflow (crop_advisory, irrigation_advisory, knowledge_search). | تنفيذ سير عمل RAG محدد مسبقاً.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID to execute | معرف سير العمل للتنفيذ",
                            "enum": [
                                "crop_advisory_workflow",
                                "irrigation_advisory_workflow",
                                "knowledge_search_workflow",
                            ],
                        },
                        "variables": {
                            "type": "object",
                            "description": "Variables to pass to the workflow | المتغيرات لتمريرها إلى سير العمل",
                        },
                    },
                    "required": ["workflow_id"],
                },
            },
        ]

    # ═══════════════════════════════════════════════════════════════════════════
    # Tool Implementations
    # ═══════════════════════════════════════════════════════════════════════════

    async def rag_query(
        self,
        query: str,
        collection: str = "default",
        top_k: int = 5,
        language: str = "both",
        include_sources: bool = True,
    ) -> RAGToolResult:
        """Execute RAG query"""
        await self.initialize()

        try:
            if self.rag_pipeline is None:
                return RAGToolResult(
                    success=False,
                    error="RAG pipeline not available",
                    error_ar="خط أنابيب RAG غير متوفر",
                )

            from shared.ai.ultrarag import RAGRequest

            request = RAGRequest(
                query=query,
                collection=collection,
                top_k=top_k,
                language=language[:2] if language != "both" else "en",
                include_sources=include_sources,
            )

            result = await self.rag_pipeline.run(request)

            response_data = {
                "query": query,
                "answer": result.generation_result.answer if result.generation_result else None,
                "confidence": result.generation_result.confidence if result.generation_result else 0.0,
            }

            if language in ["ar", "both"] and result.generation_result:
                response_data["answer_ar"] = result.generation_result.answer_ar

            if include_sources:
                response_data["sources"] = [
                    {
                        "text": r.chunk.text[:300] + "..." if len(r.chunk.text) > 300 else r.chunk.text,
                        "text_ar": r.chunk.text_ar[:300] + "..."
                        if r.chunk.text_ar and len(r.chunk.text_ar) > 300
                        else r.chunk.text_ar,
                        "score": round(r.score, 3),
                        "document_id": r.chunk.document_id,
                    }
                    for r in result.retrieval_results[:top_k]
                ]

            return RAGToolResult(
                success=True,
                data=response_data,
                metadata={
                    "processing_time_ms": result.total_time_ms,
                    "retrieval_count": len(result.retrieval_results),
                },
            )

        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return RAGToolResult(
                success=False,
                error=f"RAG query failed: {str(e)}",
                error_ar=f"فشل استعلام RAG: {str(e)}",
            )

    async def semantic_search(
        self,
        query: str,
        collection: str = "default",
        top_k: int = 10,
        min_score: float = 0.3,
    ) -> RAGToolResult:
        """Perform semantic search"""
        await self.initialize()

        try:
            if self.rag_pipeline is None:
                return RAGToolResult(
                    success=False,
                    error="RAG pipeline not available",
                    error_ar="خط أنابيب RAG غير متوفر",
                )

            from shared.ai.ultrarag import RetrievalConfig

            config = RetrievalConfig(
                top_k=top_k,
                collection=collection,
                min_score_threshold=min_score,
            )

            results = await self.rag_pipeline.retriever.retrieve(query, config)

            return RAGToolResult(
                success=True,
                data={
                    "query": query,
                    "results": [
                        {
                            "text": r.chunk.text,
                            "text_ar": r.chunk.text_ar,
                            "score": round(r.score, 3),
                            "document_id": r.chunk.document_id,
                            "chunk_id": r.chunk.id,
                            "metadata": r.chunk.metadata,
                        }
                        for r in results
                    ],
                    "count": len(results),
                },
                metadata={
                    "collection": collection,
                    "min_score": min_score,
                },
            )

        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Search failed: {str(e)}",
                error_ar=f"فشل البحث: {str(e)}",
            )

    async def add_knowledge(
        self,
        text: str,
        title: str,
        text_ar: str = None,
        title_ar: str = None,
        collection: str = "default",
        source: str = "",
        metadata: dict[str, Any] = None,
    ) -> RAGToolResult:
        """Add document to knowledge base"""
        await self.initialize()

        try:
            if self.knowledge_base is None:
                return RAGToolResult(
                    success=False,
                    error="Knowledge base not available",
                    error_ar="قاعدة المعرفة غير متوفرة",
                )

            doc = await self.knowledge_base.add_text(
                text=text,
                title=title,
                text_ar=text_ar,
                title_ar=title_ar,
                collection=collection,
                source=source,
                metadata=metadata or {},
            )

            if doc:
                return RAGToolResult(
                    success=True,
                    data={
                        "document_id": doc.id,
                        "title": doc.title,
                        "title_ar": doc.title_ar,
                        "chunks_count": len(doc.chunks),
                        "collection": collection,
                        "message": "Document added successfully",
                        "message_ar": "تمت إضافة المستند بنجاح",
                    },
                )
            else:
                return RAGToolResult(
                    success=False,
                    error="Failed to add document",
                    error_ar="فشل في إضافة المستند",
                )

        except Exception as e:
            logger.error(f"Add knowledge error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Failed to add document: {str(e)}",
                error_ar=f"فشل في إضافة المستند: {str(e)}",
            )

    async def list_knowledge(
        self,
        collection: str = None,
        limit: int = 50,
    ) -> RAGToolResult:
        """List documents in knowledge base"""
        await self.initialize()

        try:
            if self.knowledge_base is None:
                return RAGToolResult(
                    success=False,
                    error="Knowledge base not available",
                    error_ar="قاعدة المعرفة غير متوفرة",
                )

            docs = self.knowledge_base.list_documents(
                collection=collection,
                limit=limit,
            )

            return RAGToolResult(
                success=True,
                data={
                    "documents": [
                        {
                            "id": d.id,
                            "title": d.title,
                            "title_ar": d.title_ar,
                            "collection": d.collection,
                            "chunks_count": len(d.chunks),
                            "source": d.source,
                            "created_at": d.created_at.isoformat(),
                        }
                        for d in docs
                    ],
                    "count": len(docs),
                    "collections": self.knowledge_base.list_collections(),
                },
            )

        except Exception as e:
            logger.error(f"List knowledge error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Failed to list documents: {str(e)}",
                error_ar=f"فشل في عرض المستندات: {str(e)}",
            )

    async def delete_knowledge(self, document_id: str) -> RAGToolResult:
        """Delete document from knowledge base"""
        await self.initialize()

        try:
            if self.knowledge_base is None:
                return RAGToolResult(
                    success=False,
                    error="Knowledge base not available",
                    error_ar="قاعدة المعرفة غير متوفرة",
                )

            success = await self.knowledge_base.delete_document(document_id)

            if success:
                return RAGToolResult(
                    success=True,
                    data={
                        "document_id": document_id,
                        "message": "Document deleted successfully",
                        "message_ar": "تم حذف المستند بنجاح",
                    },
                )
            else:
                return RAGToolResult(
                    success=False,
                    error=f"Document not found: {document_id}",
                    error_ar=f"المستند غير موجود: {document_id}",
                )

        except Exception as e:
            logger.error(f"Delete knowledge error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Failed to delete document: {str(e)}",
                error_ar=f"فشل في حذف المستند: {str(e)}",
            )

    async def knowledge_stats(self) -> RAGToolResult:
        """Get knowledge base statistics"""
        await self.initialize()

        try:
            if self.knowledge_base is None:
                return RAGToolResult(
                    success=False,
                    error="Knowledge base not available",
                    error_ar="قاعدة المعرفة غير متوفرة",
                )

            stats = self.knowledge_base.get_stats()

            return RAGToolResult(
                success=True,
                data=stats,
            )

        except Exception as e:
            logger.error(f"Knowledge stats error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Failed to get stats: {str(e)}",
                error_ar=f"فشل في الحصول على الإحصائيات: {str(e)}",
            )

    async def crop_advisory_rag(
        self,
        crop: str,
        issue: str,
        growth_stage: str = None,
        region: str = None,
        context: dict[str, Any] = None,
        language: str = "both",
    ) -> RAGToolResult:
        """Get crop advisory using RAG"""
        await self.initialize()

        try:
            # Build comprehensive query
            query_parts = [f"Agricultural advisory for {crop}"]
            query_parts.append(f"Issue: {issue}")

            if growth_stage:
                query_parts.append(f"Growth stage: {growth_stage}")
            if region:
                query_parts.append(f"Region: {region}")
            if context:
                query_parts.append(f"Context: {json.dumps(context)}")

            query = ". ".join(query_parts)

            # Use RAG query
            result = await self.rag_query(
                query=query,
                collection="crop_knowledge",
                top_k=5,
                language=language,
                include_sources=True,
            )

            if result.success:
                # Enhance response with advisory structure
                result.data["crop"] = crop
                result.data["issue"] = issue
                result.data["advisory_type"] = "crop"

            return result

        except Exception as e:
            logger.error(f"Crop advisory error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Crop advisory failed: {str(e)}",
                error_ar=f"فشلت استشارة المحصول: {str(e)}",
            )

    async def irrigation_advisory_rag(
        self,
        crop_type: str,
        field_id: str = None,
        soil_moisture: float = None,
        growth_stage: str = None,
        weather_forecast: dict[str, Any] = None,
        language: str = "both",
    ) -> RAGToolResult:
        """Get irrigation advisory using RAG"""
        await self.initialize()

        try:
            # Build query
            query_parts = [f"Irrigation recommendation for {crop_type}"]

            if soil_moisture is not None:
                query_parts.append(f"Current soil moisture: {soil_moisture}%")
            if growth_stage:
                query_parts.append(f"Growth stage: {growth_stage}")
            if weather_forecast:
                rain_prob = weather_forecast.get("rain_probability", 0)
                query_parts.append(f"Rain probability: {rain_prob}%")

            query = ". ".join(query_parts)

            # Use RAG query
            result = await self.rag_query(
                query=query,
                collection="irrigation_practices",
                top_k=5,
                language=language,
                include_sources=True,
            )

            if result.success:
                result.data["crop_type"] = crop_type
                result.data["field_id"] = field_id
                result.data["advisory_type"] = "irrigation"

            return result

        except Exception as e:
            logger.error(f"Irrigation advisory error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Irrigation advisory failed: {str(e)}",
                error_ar=f"فشلت استشارة الري: {str(e)}",
            )

    async def pest_identification_rag(
        self,
        symptoms: str,
        crop: str = None,
        affected_parts: list[str] = None,
        region: str = None,
        season: str = None,
        language: str = "both",
    ) -> RAGToolResult:
        """Identify pests using RAG"""
        await self.initialize()

        try:
            # Build query
            query_parts = [f"Identify pest or disease from symptoms: {symptoms}"]

            if crop:
                query_parts.append(f"Crop: {crop}")
            if affected_parts:
                query_parts.append(f"Affected parts: {', '.join(affected_parts)}")
            if region:
                query_parts.append(f"Region: {region}")
            if season:
                query_parts.append(f"Season: {season}")

            query_parts.append("Provide identification and treatment recommendations.")
            query = " ".join(query_parts)

            # Use RAG query
            result = await self.rag_query(
                query=query,
                collection="pest_knowledge",
                top_k=5,
                language=language,
                include_sources=True,
            )

            if result.success:
                result.data["symptoms"] = symptoms
                result.data["crop"] = crop
                result.data["advisory_type"] = "pest_identification"

            return result

        except Exception as e:
            logger.error(f"Pest identification error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Pest identification failed: {str(e)}",
                error_ar=f"فشل تحديد الآفات: {str(e)}",
            )

    async def execute_rag_workflow(
        self,
        workflow_id: str,
        variables: dict[str, Any] = None,
    ) -> RAGToolResult:
        """Execute a RAG workflow"""
        await self.initialize()

        try:
            if self.workflow_engine is None:
                return RAGToolResult(
                    success=False,
                    error="Workflow engine not available",
                    error_ar="محرك سير العمل غير متوفر",
                )

            result = await self.workflow_engine.execute(
                workflow_id=workflow_id,
                initial_variables=variables or {},
            )

            return RAGToolResult(
                success=result.get("success", False),
                data=result,
                metadata={
                    "workflow_id": workflow_id,
                    "execution_path": result.get("execution_path", []),
                },
            )

        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return RAGToolResult(
                success=False,
                error=f"Workflow execution failed: {str(e)}",
                error_ar=f"فشل تنفيذ سير العمل: {str(e)}",
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # Tool Invocation
    # ═══════════════════════════════════════════════════════════════════════════

    async def invoke_tool(self, tool_name: str, arguments: dict[str, Any]) -> RAGToolResult:
        """Invoke a RAG tool by name"""
        tool_map = {
            # Query tools
            "rag_query": self.rag_query,
            "semantic_search": self.semantic_search,
            # Knowledge base tools
            "add_knowledge": self.add_knowledge,
            "list_knowledge": self.list_knowledge,
            "delete_knowledge": self.delete_knowledge,
            "knowledge_stats": self.knowledge_stats,
            # Advisory tools
            "crop_advisory_rag": self.crop_advisory_rag,
            "irrigation_advisory_rag": self.irrigation_advisory_rag,
            "pest_identification_rag": self.pest_identification_rag,
            # Workflow tools
            "execute_rag_workflow": self.execute_rag_workflow,
        }

        if tool_name not in tool_map:
            return RAGToolResult(
                success=False,
                error=f"Unknown RAG tool: {tool_name}",
                error_ar=f"أداة RAG غير معروفة: {tool_name}",
            )

        try:
            return await tool_map[tool_name](**arguments)
        except TypeError as e:
            return RAGToolResult(
                success=False,
                error=f"Invalid arguments for {tool_name}: {str(e)}",
                error_ar=f"معاملات غير صالحة لـ {tool_name}: {str(e)}",
            )
        except Exception as e:
            return RAGToolResult(
                success=False,
                error=f"Tool execution error: {str(e)}",
                error_ar=f"خطأ في تنفيذ الأداة: {str(e)}",
            )
