"""
SAHOOL MCP Skills Server - Agricultural Intelligence Skills
===========================================================

Implements MCP tool specifications for SAHOOL skill-based tools.
Exposes agricultural skills (crop advisor, farm documentation) and
utility tools (context compression, memory query) for AI assistants.

Skills available:
- crop_advisor: AI-powered crop advisory for disease detection and recommendations
- farm_documentation: Access farm documentation, guides, and best practices
- compress_context: Optimize AI context windows through intelligent compression
- query_memory: Search and retrieve relevant farm memory and historical data

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2025
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ==================== Tool Result Models ====================


class ToolResult(BaseModel):
    """Standard result format for tool execution"""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


# ==================== Skills Tools Implementation ====================


class SAHOOLSkillsTools:
    """
    SAHOOL Agricultural Skills Tools for MCP Integration

    Provides advanced agricultural skills and utility tools that can be
    invoked by AI assistants through the Model Context Protocol.

    Skills:
    - crop_advisor: AI-driven crop health and disease advisory
    - farm_documentation: Access agricultural documentation and guides
    - compress_context: Optimize AI context through compression algorithms
    - query_memory: Search farm memory and historical data
    """

    def __init__(self, base_url: str | None = None):
        """
        Initialize SAHOOL Skills Tools

        Args:
            base_url: Base URL for SAHOOL API (default: from env or localhost)
        """
        self.base_url = base_url or os.getenv("SAHOOL_API_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(timeout=30.0)
        self._init_compression_engine()

    async def close(self):
        """Close HTTP client and cleanup resources"""
        await self.client.aclose()

    def _init_compression_engine(self):
        """Initialize context compression engine"""
        try:
            from shared.ai.context_engineering.compression import (
                ContextCompressor,
                CompressionStrategy,
            )

            self.compressor = ContextCompressor(
                default_strategy=CompressionStrategy.HYBRID, max_tokens=4000
            )
            self.compression_available = True
        except ImportError:
            logger.warning("Context compression module not available")
            self.compressor = None
            self.compression_available = False

    def _init_memory_engine(self):
        """Initialize memory query engine"""
        try:
            from shared.ai.context_engineering.memory import (
                FarmMemory,
                MemoryType,
                RelevanceScore,
            )

            self.memory = FarmMemory()
            self.memory_available = True
        except ImportError:
            logger.warning("Farm memory module not available")
            self.memory = None
            self.memory_available = False

    # ==================== Tool Definitions ====================

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        Get MCP tool definitions for all SAHOOL skills

        Returns:
            List of tool definitions following MCP specification
        """
        return [
            {
                "name": "crop_advisor",
                "description": "AI-powered crop advisory service for disease detection, pest management, and crop health recommendations. Analyzes field conditions, historical data, and environmental factors to provide personalized advice.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the agricultural field",
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Type of agricultural issue to address",
                            "enum": [
                                "disease_detection",
                                "pest_management",
                                "crop_stress",
                                "yield_optimization",
                                "general_advice",
                            ],
                            "default": "general_advice",
                        },
                        "include_weather": {
                            "type": "boolean",
                            "description": "Include weather forecast in advisory",
                            "default": True,
                        },
                        "include_history": {
                            "type": "boolean",
                            "description": "Include historical field data in analysis",
                            "default": True,
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "description": "Minimum confidence score for recommendations (0-1)",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.7,
                        },
                    },
                    "required": ["field_id"],
                },
            },
            {
                "name": "farm_documentation",
                "description": "Access comprehensive farm documentation including growing guides, best practices, pest/disease databases, and agricultural techniques. Available in both Arabic and English.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "description": "Type of documentation to retrieve",
                            "enum": [
                                "growing_guide",
                                "pest_management",
                                "disease_control",
                                "best_practices",
                                "soil_management",
                                "irrigation_guide",
                                "fertilizer_guide",
                                "harvest_guide",
                                "storage_guide",
                            ],
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop (e.g., wheat, tomatoes, dates)",
                        },
                        "language": {
                            "type": "string",
                            "description": "Preferred language for documentation",
                            "enum": ["en", "ar"],
                            "default": "en",
                        },
                        "include_images": {
                            "type": "boolean",
                            "description": "Include images and diagrams if available",
                            "default": False,
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Optional search query within documentation",
                        },
                    },
                    "required": ["document_type", "crop_type"],
                },
            },
            {
                "name": "compress_context",
                "description": "Optimize AI context window usage through intelligent compression of field data, weather information, and historical records. Reduces token consumption while preserving critical information.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "Data object to compress (field data, weather, or history)",
                        },
                        "data_type": {
                            "type": "string",
                            "description": "Type of data being compressed",
                            "enum": ["field", "weather", "history", "text"],
                            "default": "field",
                        },
                        "compression_strategy": {
                            "type": "string",
                            "description": "Compression strategy to use",
                            "enum": ["selective", "extractive", "abstractive", "hybrid"],
                            "default": "hybrid",
                        },
                        "target_ratio": {
                            "type": "number",
                            "description": "Target compression ratio (0-1, lower = more compression)",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.3,
                        },
                        "preserve_critical": {
                            "type": "boolean",
                            "description": "Preserve critical/priority fields",
                            "default": True,
                        },
                    },
                    "required": ["data", "data_type"],
                },
            },
            {
                "name": "query_memory",
                "description": "Search and retrieve relevant farm memory entries including past conversations, field observations, recommendations, weather events, and actions. Supports semantic search and filtering.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant identifier for memory isolation",
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query for memory retrieval",
                        },
                        "field_id": {
                            "type": "string",
                            "description": "Optional field ID to filter memory entries",
                        },
                        "memory_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "conversation",
                                    "field_state",
                                    "recommendation",
                                    "observation",
                                    "weather",
                                    "action",
                                    "system",
                                ],
                            },
                            "description": "Types of memory entries to search",
                            "default": ["conversation", "recommendation", "observation"],
                        },
                        "time_range_days": {
                            "type": "integer",
                            "description": "Search within last N days (default: 30)",
                            "minimum": 1,
                            "maximum": 365,
                            "default": 30,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 10,
                        },
                        "min_relevance": {
                            "type": "string",
                            "description": "Minimum relevance score for results",
                            "enum": ["critical", "high", "medium", "low"],
                            "default": "medium",
                        },
                    },
                    "required": ["tenant_id", "query"],
                },
            },
        ]

    # ==================== Tool Implementations ====================

    async def crop_advisor(
        self,
        field_id: str,
        issue_type: str = "general_advice",
        include_weather: bool = True,
        include_history: bool = True,
        confidence_threshold: float = 0.7,
    ) -> ToolResult:
        """
        AI-powered crop advisory service

        Args:
            field_id: Field identifier
            issue_type: Type of issue to address
            include_weather: Include weather data in analysis
            include_history: Include historical data
            confidence_threshold: Minimum confidence for recommendations

        Returns:
            ToolResult with crop advisory recommendations
        """
        try:
            payload = {
                "field_id": field_id,
                "issue_type": issue_type,
                "include_weather": include_weather,
                "include_history": include_history,
                "confidence_threshold": confidence_threshold,
            }

            response = await self.client.post(
                f"{self.base_url}/api/skills/crop-advisor", json=payload
            )
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "issue_type": issue_type,
                    "recommendations": data.get("recommendations", []),
                    "analysis": data.get("analysis", {}),
                    "confidence_score": data.get("confidence_score"),
                    "action_items": data.get("action_items", []),
                    "urgency_level": data.get("urgency_level", "normal"),
                    "supporting_data": data.get("supporting_data", {}),
                },
                metadata={
                    "advisory_date": datetime.utcnow().isoformat(),
                    "ai_model": data.get("model_used", "unknown"),
                    "analysis_time_ms": data.get("processing_time_ms", 0),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"Crop advisor API error: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"Unexpected error: {str(e)}")

    async def farm_documentation(
        self,
        document_type: str,
        crop_type: str,
        language: str = "en",
        include_images: bool = False,
        search_query: str | None = None,
    ) -> ToolResult:
        """
        Access farm documentation and guides

        Args:
            document_type: Type of documentation
            crop_type: Type of crop
            language: Preferred language (en or ar)
            include_images: Include images/diagrams
            search_query: Optional search within documentation

        Returns:
            ToolResult with documentation content
        """
        try:
            params = {
                "document_type": document_type,
                "crop_type": crop_type,
                "language": language,
                "include_images": include_images,
            }
            if search_query:
                params["search_query"] = search_query

            response = await self.client.get(
                f"{self.base_url}/api/skills/documentation",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "document_type": document_type,
                    "crop_type": crop_type,
                    "title": data.get("title", ""),
                    "content": data.get("content", ""),
                    "sections": data.get("sections", []),
                    "key_points": data.get("key_points", []),
                    "images": data.get("images", []) if include_images else [],
                    "references": data.get("references", []),
                    "last_updated": data.get("last_updated"),
                },
                metadata={
                    "language": language,
                    "content_type": data.get("content_type", "text"),
                    "source": data.get("source", "SAHOOL Documentation"),
                    "search_query": search_query,
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"Documentation API error: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"Unexpected error: {str(e)}")

    async def compress_context(
        self,
        data: dict[str, Any],
        data_type: str = "field",
        compression_strategy: str = "hybrid",
        target_ratio: float = 0.3,
        preserve_critical: bool = True,
    ) -> ToolResult:
        """
        Compress context for AI optimization

        Args:
            data: Data to compress
            data_type: Type of data (field, weather, history, text)
            compression_strategy: Compression strategy
            target_ratio: Target compression ratio
            preserve_critical: Preserve critical fields

        Returns:
            ToolResult with compressed context
        """
        if not self.compression_available:
            return ToolResult(
                success=False,
                error="Context compression module not available",
            )

        try:
            from shared.ai.context_engineering.compression import CompressionStrategy

            strategy = CompressionStrategy(compression_strategy)

            if data_type == "field":
                result = self.compressor.compress_field_data(
                    data, strategy=strategy, target_ratio=target_ratio
                )
            elif data_type == "weather":
                result = self.compressor.compress_weather_data(
                    data, strategy=strategy
                )
            elif data_type == "history":
                result = self.compressor.compress_history(
                    data if isinstance(data, list) else [data],
                    max_entries=int(20 * target_ratio),
                    strategy=strategy,
                )
            elif data_type == "text":
                if isinstance(data, dict):
                    text = data.get("text", json.dumps(data))
                else:
                    text = str(data)
                result = self.compressor.compress_arabic_text(
                    text,
                    target_tokens=int(4000 * target_ratio),
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown data type: {data_type}",
                )

            return ToolResult(
                success=True,
                data={
                    "original_text_preview": result.original_text[:200]
                    if result.original_text
                    else "",
                    "compressed_text": result.compressed_text,
                    "original_tokens": result.original_tokens,
                    "compressed_tokens": result.compressed_tokens,
                    "compression_ratio": result.compression_ratio,
                    "tokens_saved": result.tokens_saved,
                    "savings_percentage": result.savings_percentage,
                    "strategy_used": result.strategy.value,
                },
                metadata={
                    "data_type": data_type,
                    "preserve_critical": preserve_critical,
                    "compression_timestamp": datetime.utcnow().isoformat(),
                },
            )
        except Exception as e:
            logger.error(f"Context compression error: {str(e)}", exc_info=True)
            return ToolResult(success=False, error=f"Compression error: {str(e)}")

    async def query_memory(
        self,
        tenant_id: str,
        query: str,
        field_id: str | None = None,
        memory_types: list[str] | None = None,
        time_range_days: int = 30,
        limit: int = 10,
        min_relevance: str = "medium",
    ) -> ToolResult:
        """
        Query farm memory for relevant entries

        Args:
            tenant_id: Tenant identifier
            query: Search query
            field_id: Optional field filter
            memory_types: Types of memory to search
            time_range_days: Search range in days
            limit: Maximum results
            min_relevance: Minimum relevance score

        Returns:
            ToolResult with memory entries
        """
        try:
            from datetime import timedelta

            from shared.ai.context_engineering.memory import (
                MemoryType,
                RelevanceScore,
            )

            if not memory_types:
                memory_types = ["conversation", "recommendation", "observation"]

            # Build the query payload
            payload = {
                "tenant_id": tenant_id,
                "query": query,
                "memory_types": [MemoryType(mt) for mt in memory_types],
                "time_range": timedelta(days=time_range_days),
                "limit": limit,
                "min_relevance": RelevanceScore(min_relevance),
            }

            if field_id:
                payload["field_id"] = field_id

            # Try to use local memory engine if available
            if self.memory_available and hasattr(self, "memory"):
                results = await self.memory.query(
                    tenant_id=tenant_id,
                    query=query,
                    field_id=field_id,
                    memory_types=[MemoryType(mt) for mt in memory_types],
                    limit=limit,
                    days=time_range_days,
                )

                return ToolResult(
                    success=True,
                    data={
                        "query": query,
                        "tenant_id": tenant_id,
                        "results_count": len(results),
                        "entries": [entry.to_dict() for entry in results],
                        "search_filters": {
                            "field_id": field_id,
                            "memory_types": memory_types,
                            "time_range_days": time_range_days,
                            "min_relevance": min_relevance,
                        },
                    },
                    metadata={
                        "query_timestamp": datetime.utcnow().isoformat(),
                        "memory_backend": "local",
                    },
                )
            else:
                # Fall back to API
                response = await self.client.post(
                    f"{self.base_url}/api/skills/memory/query",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                return ToolResult(
                    success=True,
                    data={
                        "query": query,
                        "tenant_id": tenant_id,
                        "results_count": len(data.get("results", [])),
                        "entries": data.get("results", []),
                        "search_filters": {
                            "field_id": field_id,
                            "memory_types": memory_types,
                            "time_range_days": time_range_days,
                            "min_relevance": min_relevance,
                        },
                    },
                    metadata={
                        "query_timestamp": datetime.utcnow().isoformat(),
                        "memory_backend": "api",
                    },
                )

        except Exception as e:
            logger.error(f"Memory query error: {str(e)}", exc_info=True)
            return ToolResult(success=False, error=f"Memory query error: {str(e)}")

    async def invoke_tool(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """
        Invoke a skill tool by name with arguments

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments

        Returns:
            ToolResult from tool execution
        """
        tool_map = {
            "crop_advisor": self.crop_advisor,
            "farm_documentation": self.farm_documentation,
            "compress_context": self.compress_context,
            "query_memory": self.query_memory,
        }

        if tool_name not in tool_map:
            return ToolResult(success=False, error=f"Unknown skill tool: {tool_name}")

        try:
            logger.info(f"Invoking skill tool: {tool_name} with args: {arguments}")
            return await tool_map[tool_name](**arguments)
        except TypeError as e:
            return ToolResult(
                success=False, error=f"Invalid arguments for {tool_name}: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}", exc_info=True)
            return ToolResult(success=False, error=f"Tool execution error: {str(e)}")


# ==================== Skills Server Integration ====================


def extend_mcp_server_with_skills(mcp_server: Any) -> Any:
    """
    Extend an existing MCP server with skill tools

    Args:
        mcp_server: MCPServer instance to extend

    Returns:
        Extended MCPServer instance

    Example:
        >>> from shared.mcp.server import MCPServer
        >>> from shared.mcp.skills_server import extend_mcp_server_with_skills
        >>> server = MCPServer()
        >>> server = extend_mcp_server_with_skills(server)
    """
    skills_tools = SAHOOLSkillsTools()

    # Add skill tool definitions to server
    original_get_tools = mcp_server.tools.get_tool_definitions

    def get_combined_tools():
        base_tools = original_get_tools()
        skill_tools = skills_tools.get_tool_definitions()
        return base_tools + skill_tools

    mcp_server.tools.get_tool_definitions = get_combined_tools

    # Add skill tool invocation
    original_invoke = mcp_server.tools.invoke_tool

    async def invoke_combined(tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        # Try skill tools first
        if tool_name in [
            "crop_advisor",
            "farm_documentation",
            "compress_context",
            "query_memory",
        ]:
            return await skills_tools.invoke_tool(tool_name, arguments)
        # Fall back to base tools
        return await original_invoke(tool_name, arguments)

    mcp_server.tools.invoke_tool = invoke_combined

    # Store skills tools reference for cleanup
    mcp_server.skills_tools = skills_tools

    # Update close method to cleanup skills tools
    original_close = mcp_server.close

    async def close_with_skills():
        await original_close()
        await skills_tools.close()

    mcp_server.close = close_with_skills

    logger.info("MCP server extended with SAHOOL skills")
    return mcp_server


if __name__ == "__main__":
    import asyncio

    async def test_skills():
        """Test skills tools initialization"""
        tools = SAHOOLSkillsTools()
        defs = tools.get_tool_definitions()
        print(f"Loaded {len(defs)} skill tools:")
        for tool in defs:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
        await tools.close()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(test_skills())
