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

Example:
    from shared.mcp import MCPServer, SAHOOLTools

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
from .tools import SAHOOLTools

__all__ = [
    "MCPServer",
    "MCPClient",
    "SAHOOLTools",
    "ResourceProvider",
    "FieldDataResource",
    "WeatherDataResource",
    "CropCatalogResource",
]

__version__ = "1.0.0"
