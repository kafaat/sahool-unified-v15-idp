"""
SAHOOL Vector Service - MCP Server
خادم MCP لخدمة المتجهات

Model Context Protocol (MCP) server exposing vector operations as tools.
This enables any MCP-compatible agent (Claude, etc.) to use SAHOOL's RAG capabilities.

Standards: https://modelcontextprotocol.io
"""
import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)

from .settings import settings
from .embedder import create_embedder
from .milvus_client import connect, ensure_collection, get_collection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP Server
server = Server("sahool-vector")

# Global embedder
embedder = None


def init_services():
    """Initialize Milvus connection and embedder"""
    global embedder
    try:
        connect()
        ensure_collection()
        embedder = create_embedder()
        logger.info("MCP Server: Services initialized successfully")
    except Exception as e:
        logger.error(f"MCP Server: Failed to initialize services: {e}")
        raise


# ============================================================================
# Tool Definitions
# ============================================================================

TOOLS = [
    Tool(
        name="search_knowledge",
        description="""Search SAHOOL's agricultural knowledge base for relevant information.
        Use this to find context about crops, diseases, irrigation, weather impacts, etc.
        Returns relevant text chunks with similarity scores.""",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query in Arabic or English"
                },
                "tenant_id": {
                    "type": "string",
                    "description": "Tenant identifier for multi-tenant isolation"
                },
                "namespace": {
                    "type": "string",
                    "description": "Knowledge namespace (e.g., 'advisor', 'docs', 'cases')",
                    "default": "advisor"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters: crop, region, season, source",
                    "properties": {
                        "crop": {"type": "string"},
                        "region": {"type": "string"},
                        "season": {"type": "string"},
                        "source": {"type": "string"}
                    }
                }
            },
            "required": ["query", "tenant_id"]
        }
    ),
    Tool(
        name="get_rag_context",
        description="""Get formatted RAG context for answering agricultural questions.
        Returns a pre-formatted context string with source citations.
        Use this when building prompts for agricultural advice.""",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The question to find context for"
                },
                "tenant_id": {
                    "type": "string",
                    "description": "Tenant identifier"
                },
                "namespace": {
                    "type": "string",
                    "description": "Knowledge namespace",
                    "default": "advisor"
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum context length in characters",
                    "default": 4000
                },
                "format": {
                    "type": "string",
                    "enum": ["plain", "arabic"],
                    "description": "Context format",
                    "default": "arabic"
                }
            },
            "required": ["query", "tenant_id"]
        }
    ),
    Tool(
        name="add_knowledge",
        description="""Add new knowledge to SAHOOL's vector database.
        Use this to ingest agricultural documents, case studies, or expert knowledge.""",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text content to add"
                },
                "doc_id": {
                    "type": "string",
                    "description": "Unique document identifier"
                },
                "tenant_id": {
                    "type": "string",
                    "description": "Tenant identifier"
                },
                "namespace": {
                    "type": "string",
                    "description": "Knowledge namespace",
                    "default": "advisor"
                },
                "metadata": {
                    "type": "object",
                    "description": "Metadata: crop, region, season, source",
                    "properties": {
                        "crop": {"type": "string"},
                        "region": {"type": "string"},
                        "season": {"type": "string"},
                        "source": {"type": "string"}
                    }
                }
            },
            "required": ["text", "doc_id", "tenant_id"]
        }
    ),
]


# ============================================================================
# Tool Handlers
# ============================================================================

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available MCP tools"""
    return ListToolsResult(tools=TOOLS)


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "search_knowledge":
            result = await search_knowledge(**arguments)
        elif name == "get_rag_context":
            result = await get_rag_context(**arguments)
        elif name == "add_knowledge":
            result = await add_knowledge(**arguments)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        )
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def search_knowledge(
    query: str,
    tenant_id: str,
    namespace: str = "advisor",
    top_k: int = 5,
    filters: dict = None
) -> dict:
    """Search the knowledge base"""
    global embedder

    # Generate query embedding
    qvec = embedder.embed(query)

    # Build filter expression
    expr = f'tenant_id == "{tenant_id}" and namespace == "{namespace}"'

    if filters:
        if filters.get("crop"):
            expr += f' and crop == "{filters["crop"]}"'
        if filters.get("region"):
            expr += f' and region == "{filters["region"]}"'
        if filters.get("season"):
            expr += f' and season == "{filters["season"]}"'
        if filters.get("source"):
            expr += f' and source == "{filters["source"]}"'

    search_params = {"metric_type": "IP", "params": {"ef": 128}}

    collection = get_collection()
    results = collection.search(
        data=[qvec],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        expr=expr,
        output_fields=["doc_id", "text", "metadata_json", "crop", "region", "season", "source"],
    )

    hits = []
    for hit in results[0]:
        metadata = {}
        try:
            metadata = json.loads(hit.entity.get("metadata_json") or "{}")
        except:
            pass

        hits.append({
            "doc_id": hit.entity.get("doc_id", ""),
            "score": float(hit.distance),
            "text": hit.entity.get("text", ""),
            "crop": hit.entity.get("crop", ""),
            "region": hit.entity.get("region", ""),
            "season": hit.entity.get("season", ""),
            "source": hit.entity.get("source", ""),
        })

    return {
        "query": query,
        "hits": hits,
        "total_found": len(hits)
    }


async def get_rag_context(
    query: str,
    tenant_id: str,
    namespace: str = "advisor",
    max_chars: int = 4000,
    format: str = "arabic"
) -> dict:
    """Get formatted RAG context with sources"""
    # First search for relevant content
    search_result = await search_knowledge(
        query=query,
        tenant_id=tenant_id,
        namespace=namespace,
        top_k=5
    )

    hits = search_result["hits"]

    # Build context string
    if format == "arabic":
        context_parts = ["المعلومات المتاحة:"]
        for i, hit in enumerate(hits, 1):
            context_parts.append(f"\n[{i}] {hit['text']}")
            if hit.get("source"):
                context_parts.append(f"   (المصدر: {hit['source']})")
    else:
        context_parts = ["Available information:"]
        for i, hit in enumerate(hits, 1):
            context_parts.append(f"\n[{i}] {hit['text']}")
            if hit.get("source"):
                context_parts.append(f"   (Source: {hit['source']})")

    context = "\n".join(context_parts)

    # Truncate if needed
    if len(context) > max_chars:
        context = context[:max_chars] + "..."

    # Extract sources
    sources = [{"doc_id": h["doc_id"], "score": h["score"]} for h in hits]

    return {
        "context": context,
        "sources": sources,
        "query": query,
        "hits_count": len(hits),
        "no_relevant_context": len(hits) == 0,
        "guardrail_note": "أجب فقط من السياق المتاح. إن لم يكفِ قل: لا أملك معلومات كافية." if len(hits) == 0 else None
    }


async def add_knowledge(
    text: str,
    doc_id: str,
    tenant_id: str,
    namespace: str = "advisor",
    metadata: dict = None
) -> dict:
    """Add new knowledge to the vector database"""
    global embedder

    metadata = metadata or {}

    # Generate embedding
    vec = embedder.embed(text)

    # Compute unique ID
    _id = f"{tenant_id}:{namespace}:{doc_id}"
    metadata_json = json.dumps(metadata, ensure_ascii=False)

    # Extract scalar fields
    crop = str(metadata.get("crop", ""))
    region = str(metadata.get("region", ""))
    season = str(metadata.get("season", ""))
    source = str(metadata.get("source", namespace))

    # Prepare entities
    entities = [
        [_id],
        [tenant_id],
        [namespace],
        [doc_id],
        [crop],
        [region],
        [season],
        [source],
        [text],
        [metadata_json],
        [vec],
    ]

    collection = get_collection()
    collection.insert(entities)
    collection.flush()

    return {
        "inserted": 1,
        "id": _id,
        "doc_id": doc_id
    }


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run the MCP server"""
    logger.info("Starting SAHOOL Vector MCP Server...")
    init_services()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
