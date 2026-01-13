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

from .client import MCPClient
from .resources import (
    CropCatalogResource,
    FieldDataResource,
    ResourceProvider,
    WeatherDataResource,
)
from .server import MCPServer
from .skills_server import SAHOOLSkillsTools, extend_mcp_server_with_skills
from .tools import SAHOOLTools

__all__ = [
    "MCPServer",
    "MCPClient",
    "SAHOOLTools",
    "SAHOOLSkillsTools",
    "ResourceProvider",
    "FieldDataResource",
    "WeatherDataResource",
    "CropCatalogResource",
    "extend_mcp_server_with_skills",
]

__version__ = "1.0.0"
