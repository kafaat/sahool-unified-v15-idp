# ═══════════════════════════════════════════════════════════════════════════════
# MCP-RAG Bridge - Bridges MCP Server Tools with UltraRAG Retrieval
# جسر MCP-RAG - يربط أدوات خادم MCP مع استرجاع UltraRAG
# ═══════════════════════════════════════════════════════════════════════════════
#
# Gap G-19: MCP-RAG bridge integration
#
# Provides a bridge layer that exposes UltraRAG retrieval operations as
# JSON-RPC 2.0 compatible MCP tools. Supports the 9 agricultural workflows
# (pest_diagnosis, irrigation_advisory, crop_advisory, fertilizer_advisory,
# soil_analysis, weather_advisory, remote_sensing, comprehensive_field,
# knowledge_search) and returns structured results with citations and
# confidence scores.
#
# يوفر طبقة جسر تعرض عمليات استرجاع UltraRAG كأدوات MCP متوافقة مع
# JSON-RPC 2.0. يدعم 9 سير عمل زراعي ويعيد نتائج منظمة مع اقتباسات
# ودرجات ثقة.
#
# Author: SAHOOL Platform Team
# Updated: March 2026
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Optional imports with graceful fallbacks
# ─────────────────────────────────────────────────────────────────────────────

try:
    from .ultrarag.pipeline import RAGPipeline
except ImportError:
    RAGPipeline = None  # type: ignore[assignment,misc]

try:
    from .ultrarag.conversation_memory import ConversationMemory, RAGConversationManager
except ImportError:
    ConversationMemory = None  # type: ignore[assignment,misc]
    RAGConversationManager = None  # type: ignore[assignment,misc]

try:
    from .knowledge.collections import ALL_COLLECTIONS
except ImportError:
    ALL_COLLECTIONS: list[str] = []  # type: ignore[no-redef]

try:
    from .embeddings import EmbeddingsAdapter
except ImportError:
    EmbeddingsAdapter = None  # type: ignore[assignment,misc]


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class AgriWorkflow(StrEnum):
    """Agricultural workflow identifiers | معرفات سير العمل الزراعي"""

    PEST_DIAGNOSIS = "pest_diagnosis"
    IRRIGATION_ADVISORY = "irrigation_advisory"
    CROP_ADVISORY = "crop_advisory"
    FERTILIZER_ADVISORY = "fertilizer_advisory"
    SOIL_ANALYSIS = "soil_analysis_advisory"
    WEATHER_ADVISORY = "weather_advisory"
    REMOTE_SENSING = "remote_sensing_analysis"
    COMPREHENSIVE_FIELD = "comprehensive_field_advisory"
    KNOWLEDGE_SEARCH = "knowledge_search"


class BridgeToolName(StrEnum):
    """MCP tool names registered by this bridge | أسماء أدوات MCP المسجلة"""

    RAG_SEARCH = "rag_search"
    RAG_RETRIEVE = "rag_retrieve"
    RAG_INGEST = "rag_ingest"
    RAG_WORKFLOW = "rag_workflow"


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Citation:
    """A source citation from RAG retrieval | اقتباس مصدر من استرجاع RAG"""

    document_id: str = ""
    title: str = ""
    collection: str = ""
    chunk_text: str = ""
    relevance_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary | التحويل إلى قاموس"""
        return {
            "document_id": self.document_id,
            "title": self.title,
            "collection": self.collection,
            "chunk_text": self.chunk_text[:300] if self.chunk_text else "",
            "relevance_score": round(self.relevance_score, 4),
            "metadata": self.metadata,
        }


@dataclass
class BridgeResult:
    """Result returned by bridge operations | نتيجة عمليات الجسر"""

    success: bool = True
    data: dict[str, Any] = field(default_factory=dict)
    citations: list[Citation] = field(default_factory=list)
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    workflow_id: str | None = None
    error: str | None = None
    error_ar: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-RPC compatible dictionary | التحويل إلى قاموس متوافق مع JSON-RPC"""
        result: dict[str, Any] = {
            "success": self.success,
            "data": self.data,
            "citations": [c.to_dict() for c in self.citations],
            "confidence": round(self.confidence, 4),
            "processing_time_ms": round(self.processing_time_ms, 2),
        }
        if self.workflow_id:
            result["workflow_id"] = self.workflow_id
        if self.error:
            result["error"] = self.error
        if self.error_ar:
            result["error_ar"] = self.error_ar
        return result


@dataclass
class MCPToolSchema:
    """Schema definition for an MCP tool | تعريف مخطط أداة MCP"""

    name: str
    description: str
    description_ar: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    category: str = "rag_bridge"

    def to_mcp_format(self) -> dict[str, Any]:
        """Convert to MCP tools/list format | التحويل إلى تنسيق قائمة أدوات MCP"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Tool Schema Definitions
# ─────────────────────────────────────────────────────────────────────────────

RAG_SEARCH_SCHEMA = MCPToolSchema(
    name=BridgeToolName.RAG_SEARCH,
    description="Search the agricultural knowledge base using semantic similarity",
    description_ar="البحث في قاعدة المعرفة الزراعية باستخدام التشابه الدلالي",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query in English or Arabic | استعلام البحث بالإنجليزية أو العربية",
            },
            "collection": {
                "type": "string",
                "description": "Knowledge collection to search | مجموعة المعرفة للبحث",
                "default": "general_agriculture",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return | عدد النتائج",
                "default": 5,
                "minimum": 1,
                "maximum": 20,
            },
            "min_score": {
                "type": "number",
                "description": "Minimum relevance score threshold | الحد الأدنى لدرجة الصلة",
                "default": 0.3,
            },
            "language": {
                "type": "string",
                "enum": ["en", "ar", "both"],
                "description": "Response language | لغة الاستجابة",
                "default": "both",
            },
        },
        "required": ["query"],
    },
)

RAG_RETRIEVE_SCHEMA = MCPToolSchema(
    name=BridgeToolName.RAG_RETRIEVE,
    description="Retrieve a specific document or chunk by ID from the knowledge base",
    description_ar="استرجاع مستند أو قطعة محددة بالمعرف من قاعدة المعرفة",
    input_schema={
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "Document or chunk identifier | معرف المستند أو القطعة",
            },
            "collection": {
                "type": "string",
                "description": "Collection containing the document | المجموعة التي تحتوي على المستند",
                "default": "general_agriculture",
            },
            "include_neighbors": {
                "type": "boolean",
                "description": "Include neighboring chunks for context | تضمين القطع المجاورة للسياق",
                "default": False,
            },
        },
        "required": ["document_id"],
    },
)

RAG_INGEST_SCHEMA = MCPToolSchema(
    name=BridgeToolName.RAG_INGEST,
    description="Ingest a new document into the agricultural knowledge base",
    description_ar="إدخال مستند جديد في قاعدة المعرفة الزراعية",
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
                "default": "general_agriculture",
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata (crop, region, season) | بيانات وصفية إضافية",
            },
        },
        "required": ["text", "title"],
    },
)

RAG_WORKFLOW_SCHEMA = MCPToolSchema(
    name=BridgeToolName.RAG_WORKFLOW,
    description=(
        "Execute a pre-built agricultural RAG workflow "
        "(pest_diagnosis, irrigation_advisory, crop_advisory, fertilizer_advisory, "
        "soil_analysis_advisory, weather_advisory, remote_sensing_analysis, "
        "comprehensive_field_advisory, knowledge_search)"
    ),
    description_ar=(
        "تنفيذ سير عمل RAG زراعي مبني مسبقاً "
        "(تشخيص آفات، استشارة ري، استشارة محاصيل، استشارة أسمدة، "
        "تحليل تربة، استشارة طقس، تحليل استشعار عن بعد، "
        "استشارة حقل شاملة، بحث معرفي)"
    ),
    input_schema={
        "type": "object",
        "properties": {
            "workflow": {
                "type": "string",
                "enum": [w.value for w in AgriWorkflow],
                "description": "Workflow to execute | سير العمل للتنفيذ",
            },
            "query": {
                "type": "string",
                "description": "Query or question for the workflow | الاستعلام أو السؤال لسير العمل",
            },
            "context": {
                "type": "object",
                "description": "Workflow context (crop, field_id, growth_stage, region, etc.) | سياق سير العمل",
            },
            "language": {
                "type": "string",
                "enum": ["en", "ar", "both"],
                "description": "Response language | لغة الاستجابة",
                "default": "both",
            },
        },
        "required": ["workflow", "query"],
    },
)

# All tool schemas for registration
BRIDGE_TOOL_SCHEMAS: list[MCPToolSchema] = [
    RAG_SEARCH_SCHEMA,
    RAG_RETRIEVE_SCHEMA,
    RAG_INGEST_SCHEMA,
    RAG_WORKFLOW_SCHEMA,
]


# ─────────────────────────────────────────────────────────────────────────────
# Workflow-to-collection mapping
# ─────────────────────────────────────────────────────────────────────────────

WORKFLOW_COLLECTION_MAP: dict[str, list[str]] = {
    AgriWorkflow.PEST_DIAGNOSIS: ["pest_knowledge", "crop_knowledge"],
    AgriWorkflow.IRRIGATION_ADVISORY: ["crop_water_requirements", "irrigation_practices"],
    AgriWorkflow.CROP_ADVISORY: ["crop_knowledge", "general_agriculture"],
    AgriWorkflow.FERTILIZER_ADVISORY: ["fertilizer_knowledge", "soil_knowledge"],
    AgriWorkflow.SOIL_ANALYSIS: ["soil_knowledge", "general_agriculture"],
    AgriWorkflow.WEATHER_ADVISORY: ["weather_knowledge", "crop_knowledge"],
    AgriWorkflow.REMOTE_SENSING: ["remote_sensing_knowledge"],
    AgriWorkflow.COMPREHENSIVE_FIELD: [
        "crop_knowledge",
        "soil_knowledge",
        "irrigation_practices",
    ],
    AgriWorkflow.KNOWLEDGE_SEARCH: ["general_agriculture"],
}


# ─────────────────────────────────────────────────────────────────────────────
# MCP-RAG Bridge
# ─────────────────────────────────────────────────────────────────────────────


class MCPRAGBridge:
    """
    Bridge between MCP server tools and UltraRAG retrieval pipeline.
    جسر بين أدوات خادم MCP وخط أنابيب استرجاع UltraRAG.

    Registers RAG tools (rag_search, rag_retrieve, rag_ingest, rag_workflow)
    with an MCP server and routes JSON-RPC 2.0 tool calls to the UltraRAG
    pipeline. Supports the 9 pre-built agricultural workflows and returns
    structured results with citations and confidence scores.

    يسجل أدوات RAG (بحث، استرجاع، إدخال، سير عمل) مع خادم MCP
    ويوجه استدعاءات أدوات JSON-RPC 2.0 إلى خط أنابيب UltraRAG. يدعم
    9 سير عمل زراعي مبني مسبقاً ويعيد نتائج منظمة مع اقتباسات ودرجات ثقة.

    Usage::

        bridge = MCPRAGBridge(
            rag_pipeline=pipeline,
            knowledge_base=kb,
            workflow_engine=engine,
        )
        bridge.register_with_mcp_server(mcp_server)

        # Handle a JSON-RPC 2.0 tools/call request
        response = await bridge.handle_jsonrpc_request(jsonrpc_request)
    """

    def __init__(
        self,
        rag_pipeline: Any | None = None,
        conversation_manager: Any | None = None,
        knowledge_base: Any | None = None,
        workflow_engine: Any | None = None,
    ) -> None:
        self._pipeline = rag_pipeline
        self._conversation_manager = conversation_manager
        self._knowledge_base = knowledge_base
        self._workflow_engine = workflow_engine
        self._tool_handlers: dict[str, Any] = {
            BridgeToolName.RAG_SEARCH: self._handle_search,
            BridgeToolName.RAG_RETRIEVE: self._handle_retrieve,
            BridgeToolName.RAG_INGEST: self._handle_ingest,
            BridgeToolName.RAG_WORKFLOW: self._handle_workflow,
        }

        logger.info(
            "MCPRAGBridge initialized | تم تهيئة جسر MCP-RAG",
            extra={
                "pipeline_available": rag_pipeline is not None,
                "conversation_manager": conversation_manager is not None,
                "knowledge_base": knowledge_base is not None,
                "workflow_engine": workflow_engine is not None,
            },
        )

    # ─────────────────────────────────────────────────────────────────────
    # MCP Registration
    # ─────────────────────────────────────────────────────────────────────

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """
        Return all tool schemas in MCP tools/list format.
        إرجاع جميع مخططات الأدوات بتنسيق قائمة أدوات MCP.
        """
        return [schema.to_mcp_format() for schema in BRIDGE_TOOL_SCHEMAS]

    def register_with_mcp_server(self, mcp_server: Any) -> int:
        """
        Register all RAG bridge tools with an MCP server instance.
        تسجيل جميع أدوات جسر RAG مع مثيل خادم MCP.

        Supports MCP servers that expose either ``register_tool()`` or a
        ``tools`` attribute with ``register_tool()``.

        Args:
            mcp_server: MCP server instance with a register_tool method.

        Returns:
            Number of tools registered | عدد الأدوات المسجلة.
        """
        registered = 0
        for schema in BRIDGE_TOOL_SCHEMAS:
            try:
                if hasattr(mcp_server, "register_tool"):
                    mcp_server.register_tool(
                        name=schema.name,
                        description=schema.description,
                        input_schema=schema.input_schema,
                        handler=lambda args, _name=schema.name: self.handle_tool_call(_name, args),
                    )
                    registered += 1
                elif hasattr(mcp_server, "tools") and hasattr(mcp_server.tools, "register_tool"):
                    mcp_server.tools.register_tool(
                        name=schema.name,
                        description=schema.description,
                        input_schema=schema.input_schema,
                        handler=lambda args, _name=schema.name: self.handle_tool_call(_name, args),
                    )
                    registered += 1
                else:
                    logger.warning(
                        "MCP server missing register_tool method, skipping %s",
                        schema.name,
                    )
            except Exception as exc:
                logger.warning("Failed to register tool %s: %s", schema.name, exc)

        logger.info(
            "Registered %d RAG bridge tools with MCP server | تم تسجيل %d أدوات جسر RAG مع خادم MCP",
            registered,
            registered,
        )
        return registered

    # ─────────────────────────────────────────────────────────────────────
    # JSON-RPC 2.0 Tool Call Router
    # ─────────────────────────────────────────────────────────────────────

    async def handle_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Route a tool call to the appropriate handler and return a result dict.
        توجيه استدعاء أداة إلى المعالج المناسب وإرجاع قاموس النتيجة.

        Args:
            tool_name: Name of the tool to invoke.
            arguments: Tool call arguments from JSON-RPC params.

        Returns:
            JSON-RPC compatible result dictionary with success, data,
            citations, and confidence fields.
        """
        handler = self._tool_handlers.get(tool_name)
        if handler is None:
            return BridgeResult(
                success=False,
                error=f"Unknown tool: {tool_name}",
                error_ar=f"أداة غير معروفة: {tool_name}",
            ).to_dict()

        start = time.monotonic()
        try:
            result: BridgeResult = await handler(arguments)
            result.processing_time_ms = (time.monotonic() - start) * 1000
            return result.to_dict()
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.exception("Tool call failed: %s", tool_name)
            return BridgeResult(
                success=False,
                error=str(exc),
                error_ar="فشل استدعاء الأداة",
                processing_time_ms=elapsed,
            ).to_dict()

    async def handle_jsonrpc_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Handle a full JSON-RPC 2.0 request envelope for tools/call.
        معالجة غلاف طلب JSON-RPC 2.0 كامل لاستدعاء الأدوات.

        Expects ``method`` = ``"tools/call"`` with ``params`` containing
        ``name`` and ``arguments``. Returns a JSON-RPC 2.0 response with
        either ``result`` or ``error``.

        Args:
            request: JSON-RPC 2.0 request dict with jsonrpc, id, method, params.

        Returns:
            JSON-RPC 2.0 response envelope.
        """
        request_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        if method != "tools/call":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not supported: {method}. Use 'tools/call'.",
                },
            }

        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        tool_result = await self.handle_tool_call(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": tool_result}],
                "isError": not tool_result.get("success", False),
            },
        }

    # ─────────────────────────────────────────────────────────────────────
    # Tool Handlers
    # ─────────────────────────────────────────────────────────────────────

    async def _handle_search(self, args: dict[str, Any]) -> BridgeResult:
        """
        Semantic search across knowledge collections.
        بحث دلالي عبر مجموعات المعرفة.
        """
        query = args.get("query", "")
        collection = args.get("collection", "general_agriculture")
        top_k = min(args.get("top_k", 5), 20)
        min_score = args.get("min_score", 0.3)
        language = args.get("language", "both")

        if not query:
            return BridgeResult(
                success=False,
                error="Query is required",
                error_ar="الاستعلام مطلوب",
            )

        # Try pipeline-based search first
        if self._pipeline is not None:
            try:
                from .ultrarag.models import RAGRequest

                request = RAGRequest(
                    query=query,
                    collection=collection,
                    top_k=top_k,
                    language="ar" if language == "ar" else "en",
                )
                rag_result = await self._pipeline.run(request)

                citations = _extract_citations(rag_result.retrieval_results, min_score)
                answer = ""
                answer_ar = None
                confidence = 0.0

                if rag_result.generation_result:
                    answer = rag_result.generation_result.answer or ""
                    answer_ar = getattr(rag_result.generation_result, "answer_ar", None)
                    confidence = rag_result.generation_result.confidence or 0.0

                data: dict[str, Any] = {
                    "answer": answer,
                    "total_results": len(citations),
                    "collection": collection,
                }
                if language in ("ar", "both") and answer_ar:
                    data["answer_ar"] = answer_ar

                return BridgeResult(
                    success=rag_result.success,
                    data=data,
                    citations=citations,
                    confidence=confidence,
                )

            except Exception as exc:
                logger.warning("Pipeline search failed, returning error: %s", exc)

        # Fallback: pipeline not available
        return BridgeResult(
            success=False,
            error="RAG pipeline not available for search",
            error_ar="خط أنابيب RAG غير متوفر للبحث",
            data={"query": query, "collection": collection},
        )

    async def _handle_retrieve(self, args: dict[str, Any]) -> BridgeResult:
        """
        Retrieve a specific document by ID.
        استرجاع مستند محدد بالمعرف.
        """
        document_id = args.get("document_id", "")

        if not document_id:
            return BridgeResult(
                success=False,
                error="document_id is required",
                error_ar="معرف المستند مطلوب",
            )

        if self._knowledge_base is not None:
            try:
                doc = None
                if hasattr(self._knowledge_base, "get_document"):
                    doc = await self._knowledge_base.get_document(document_id)
                elif hasattr(self._knowledge_base, "get_chunk"):
                    doc = await self._knowledge_base.get_chunk(document_id)

                if doc is not None:
                    doc_data = doc.to_dict() if hasattr(doc, "to_dict") else {"id": document_id}
                    return BridgeResult(
                        success=True,
                        data=doc_data,
                        confidence=1.0,
                    )

                return BridgeResult(
                    success=False,
                    error=f"Document not found: {document_id}",
                    error_ar=f"المستند غير موجود: {document_id}",
                )

            except Exception as exc:
                logger.warning("Retrieve failed for %s: %s", document_id, exc)
                return BridgeResult(
                    success=False,
                    error=str(exc),
                    error_ar="فشل الاسترجاع",
                )

        return BridgeResult(
            success=False,
            error="Knowledge base not available",
            error_ar="قاعدة المعرفة غير متوفرة",
        )

    async def _handle_ingest(self, args: dict[str, Any]) -> BridgeResult:
        """
        Ingest a new document into the knowledge base.
        إدخال مستند جديد في قاعدة المعرفة.
        """
        text = args.get("text", "")
        title = args.get("title", "")
        text_ar = args.get("text_ar")
        collection = args.get("collection", "general_agriculture")
        metadata = args.get("metadata", {})

        if not text or not title:
            return BridgeResult(
                success=False,
                error="Both text and title are required",
                error_ar="النص والعنوان مطلوبان",
            )

        if self._knowledge_base is not None:
            try:
                doc = await self._knowledge_base.add_text(
                    text=text,
                    title=title,
                    text_ar=text_ar,
                    collection=collection,
                    metadata=metadata,
                )
                if doc is not None:
                    chunks_count = len(doc.chunks) if hasattr(doc, "chunks") else 0
                    return BridgeResult(
                        success=True,
                        data={
                            "document_id": (doc.id if hasattr(doc, "id") else str(uuid.uuid4())),
                            "title": title,
                            "collection": collection,
                            "chunks_count": chunks_count,
                        },
                        confidence=1.0,
                    )

                return BridgeResult(
                    success=False,
                    error="Failed to ingest document",
                    error_ar="فشل إدخال المستند",
                )

            except Exception as exc:
                logger.warning("Ingest failed: %s", exc)
                return BridgeResult(
                    success=False,
                    error=str(exc),
                    error_ar="فشل إدخال المستند",
                )

        return BridgeResult(
            success=False,
            error="Knowledge base not available for ingestion",
            error_ar="قاعدة المعرفة غير متوفرة للإدخال",
        )

    async def _handle_workflow(self, args: dict[str, Any]) -> BridgeResult:
        """
        Execute a pre-built agricultural RAG workflow.
        تنفيذ سير عمل RAG زراعي مبني مسبقاً.
        """
        workflow_name = args.get("workflow", "")
        query = args.get("query", "")
        context = args.get("context", {})
        language = args.get("language", "both")

        if not workflow_name or not query:
            return BridgeResult(
                success=False,
                error="Both workflow and query are required",
                error_ar="سير العمل والاستعلام مطلوبان",
            )

        # Validate workflow name
        valid_workflows = {w.value for w in AgriWorkflow}
        if workflow_name not in valid_workflows:
            return BridgeResult(
                success=False,
                error=(f"Unknown workflow: {workflow_name}. Valid workflows: {sorted(valid_workflows)}"),
                error_ar=f"سير عمل غير معروف: {workflow_name}",
            )

        # Try the workflow engine first
        if self._workflow_engine is not None:
            try:
                wf_result = await self._workflow_engine.execute(
                    workflow_id=workflow_name,
                    variables={"query": query, "language": language, **context},
                )

                output = wf_result.output if hasattr(wf_result, "output") else {}
                if isinstance(output, dict):
                    data = output
                else:
                    data = {"output": str(output)}

                return BridgeResult(
                    success=True,
                    data=data,
                    workflow_id=workflow_name,
                    confidence=data.get("confidence", 0.7),
                )

            except Exception as exc:
                logger.warning(
                    "Workflow engine execution failed for %s, falling back to pipeline: %s",
                    workflow_name,
                    exc,
                )

        # Fallback: route to pipeline with workflow-appropriate collections
        if self._pipeline is not None:
            return await self._workflow_via_pipeline(workflow_name, query, context, language)

        return BridgeResult(
            success=False,
            error="Neither workflow engine nor RAG pipeline available",
            error_ar="لا محرك سير العمل ولا خط أنابيب RAG متوفر",
            workflow_id=workflow_name,
        )

    async def _workflow_via_pipeline(
        self,
        workflow_name: str,
        query: str,
        context: dict[str, Any],
        language: str,
    ) -> BridgeResult:
        """
        Execute a workflow by routing through the RAG pipeline with
        appropriate collection selection.
        تنفيذ سير العمل عبر خط أنابيب RAG مع اختيار المجموعة المناسبة.
        """
        collections = WORKFLOW_COLLECTION_MAP.get(workflow_name, ["general_agriculture"])
        primary_collection = collections[0] if collections else "general_agriculture"

        # Enrich query with workflow context
        enriched_query = _build_workflow_query(workflow_name, query, context)

        try:
            from .ultrarag.models import RAGRequest

            request = RAGRequest(
                query=enriched_query,
                collection=primary_collection,
                top_k=5,
                language="ar" if language == "ar" else "en",
            )

            rag_result = await self._pipeline.run(request)

            citations = _extract_citations(rag_result.retrieval_results, min_score=0.2)
            answer = ""
            answer_ar = None
            confidence = 0.0

            if rag_result.generation_result:
                answer = rag_result.generation_result.answer or ""
                answer_ar = getattr(rag_result.generation_result, "answer_ar", None)
                confidence = rag_result.generation_result.confidence or 0.0

            data: dict[str, Any] = {
                "answer": answer,
                "workflow": workflow_name,
                "collections_searched": collections,
                "total_sources": len(citations),
            }
            if language in ("ar", "both") and answer_ar:
                data["answer_ar"] = answer_ar

            return BridgeResult(
                success=rag_result.success,
                data=data,
                citations=citations,
                confidence=confidence,
                workflow_id=workflow_name,
            )

        except Exception as exc:
            logger.exception("Pipeline workflow fallback failed for %s", workflow_name)
            return BridgeResult(
                success=False,
                error=str(exc),
                error_ar="فشل تنفيذ سير العمل عبر خط الأنابيب",
                workflow_id=workflow_name,
            )

    # ─────────────────────────────────────────────────────────────────────
    # Introspection
    # ─────────────────────────────────────────────────────────────────────

    def list_workflows(self) -> list[dict[str, Any]]:
        """
        List available agricultural workflows with their collections.
        عرض سير العمل الزراعي المتاح مع مجموعاتهم.
        """
        return [
            {
                "id": w.value,
                "collections": WORKFLOW_COLLECTION_MAP.get(w.value, []),
            }
            for w in AgriWorkflow
        ]

    def list_collections(self) -> list[str]:
        """
        List all available knowledge collections.
        عرض جميع مجموعات المعرفة المتاحة.
        """
        if ALL_COLLECTIONS:
            return list(ALL_COLLECTIONS)
        # Derive from workflow map as a fallback
        seen: set[str] = set()
        result: list[str] = []
        for cols in WORKFLOW_COLLECTION_MAP.values():
            for c in cols:
                if c not in seen:
                    seen.add(c)
                    result.append(c)
        return result

    def get_health(self) -> dict[str, Any]:
        """
        Get bridge health status.
        الحصول على حالة صحة الجسر.
        """
        health: dict[str, Any] = {
            "bridge": "mcp_rag_bridge",
            "pipeline_available": self._pipeline is not None,
            "knowledge_base_available": self._knowledge_base is not None,
            "workflow_engine_available": self._workflow_engine is not None,
            "conversation_manager_available": self._conversation_manager is not None,
            "registered_tools": [s.name for s in BRIDGE_TOOL_SCHEMAS],
            "available_workflows": [w.value for w in AgriWorkflow],
        }
        if self._pipeline and hasattr(self._pipeline, "get_metrics"):
            health["pipeline_metrics"] = self._pipeline.get_metrics()
        return health


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────


def _extract_citations(
    retrieval_results: list[Any],
    min_score: float = 0.0,
) -> list[Citation]:
    """
    Convert UltraRAG retrieval results into Citation objects.
    تحويل نتائج استرجاع UltraRAG إلى كائنات اقتباس.
    """
    citations: list[Citation] = []
    for result in retrieval_results:
        score = getattr(result, "score", 0.0)
        if score < min_score:
            continue

        chunk = getattr(result, "chunk", None)
        if chunk is None:
            continue

        citations.append(
            Citation(
                document_id=getattr(chunk, "document_id", ""),
                title=getattr(chunk, "metadata", {}).get("title", ""),
                collection=getattr(chunk, "collection", ""),
                chunk_text=getattr(chunk, "text", ""),
                relevance_score=score,
                metadata=getattr(chunk, "metadata", {}),
            )
        )
    return citations


def _build_workflow_query(
    workflow_name: str,
    query: str,
    context: dict[str, Any],
) -> str:
    """
    Enrich a user query with workflow-specific context fields.
    إثراء استعلام المستخدم بحقول سياق خاصة بسير العمل.
    """
    parts = [query]

    # Workflow-specific context enrichment
    _context_keys: dict[str, list[str]] = {
        AgriWorkflow.PEST_DIAGNOSIS: ["crop", "symptoms", "region", "growth_stage"],
        AgriWorkflow.IRRIGATION_ADVISORY: [
            "crop",
            "growth_stage",
            "soil_moisture",
            "soil_type",
        ],
        AgriWorkflow.CROP_ADVISORY: ["crop", "growth_stage", "issue", "region"],
        AgriWorkflow.FERTILIZER_ADVISORY: [
            "crop",
            "soil_test",
            "target_yield",
            "growth_stage",
        ],
        AgriWorkflow.SOIL_ANALYSIS: ["soil_type", "ph", "ec", "organic_matter"],
        AgriWorkflow.WEATHER_ADVISORY: ["crop", "region", "forecast", "season"],
        AgriWorkflow.REMOTE_SENSING: ["field_id", "ndvi", "index_type", "date"],
        AgriWorkflow.COMPREHENSIVE_FIELD: ["field_id", "crop", "growth_stage"],
        AgriWorkflow.KNOWLEDGE_SEARCH: ["topic", "category"],
    }

    keys = _context_keys.get(workflow_name, [])
    for key in keys:
        if value := context.get(key):
            parts.append(f"{key}: {value}")

    # Generic context keys not already handled
    for key in ("notes", "additional_info"):
        if key not in keys and (val := context.get(key)):
            parts.append(f"{key}: {val}")

    return ". ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Module exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    "AgriWorkflow",
    "BridgeResult",
    "BridgeToolName",
    "BRIDGE_TOOL_SCHEMAS",
    "Citation",
    "MCPRAGBridge",
    "MCPToolSchema",
    "WORKFLOW_COLLECTION_MAP",
]
