"""
SAHOOL Model Context Protocol (MCP) Integration
================================================

Provides MCP server and client implementations for SAHOOL agricultural platform,
enabling AI assistants to access agricultural tools and resources.

Components:
- tools: Agricultural tool implementations (weather, crop health, irrigation)
- resources: Data resource providers (fields, weather, crops)
- server: MCP server with stdio and SSE transports
- client: MCP client for connecting to MCP servers
- skills_server: Advanced skills tools (crop advisor, farm documentation, context compression, memory query)

Example:
    from shared.mcp import MCPServer, SAHOOLTools, SAHOOLSkillsTools

    server = MCPServer()
    await server.start()
"""

# Skills server is always available (only requires httpx, pydantic)
from .skills_server import SAHOOLSkillsTools, ToolResult, extend_mcp_server_with_skills

# Conditional imports for FastAPI-dependent modules
try:
    from .client import MCPClient
    from .resources import (
        CropCatalogResource,
        FieldDataResource,
        ResourceProvider,
        WeatherDataResource,
    )
    from .server import MCPServer
    from .tools import SAHOOLTools

    __all__ = [
        "MCPServer",
        "MCPClient",
        "SAHOOLTools",
        "SAHOOLSkillsTools",
        "ToolResult",
        "ResourceProvider",
        "FieldDataResource",
        "WeatherDataResource",
        "CropCatalogResource",
        "extend_mcp_server_with_skills",
    ]
except ImportError:
    # FastAPI not available - only skills_server is accessible
    __all__ = [
        "SAHOOLSkillsTools",
        "ToolResult",
        "extend_mcp_server_with_skills",
    ]

__version__ = "1.0.0"
