"""
SAHOOL MCP Module - Model Context Protocol Implementation
=========================================================

Provides MCP (Model Context Protocol) server implementation for SAHOOL
agricultural intelligence platform. Enables AI assistants to access
SAHOOL tools, resources, and prompts.

Components:
- SAHOOLMCPServer: Main MCP server implementation
- SAHOOLTools: Agricultural intelligence tools (field, crop, weather, irrigation, fertilizer)
- ResourceManager: Data resources (fields, farmers, weather, crops, knowledge)
- SAHOOLSkillsTools: Advanced skills (crop advisor, farm documentation, context compression)
- MCPConfig: Configuration management

Usage:
    from shared.mcp import SAHOOLMCPServer, SAHOOLTools, MCPConfig

    # Run with stdio transport
    server = SAHOOLMCPServer()
    await server.run_stdio()

    # Run with HTTP transport
    app = server.create_fastapi_app()

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

# Skills server is always available (only requires httpx, pydantic)
from .skills_server import SAHOOLSkillsTools, extend_mcp_server_with_skills

# Conditional imports for FastAPI-dependent modules
try:
    # Configuration
    # Client
    from .client import MCPClient
    from .config import (
        AgentConfig,
        AgentType,
        APIConfig,
        AuthConfig,
        BilingualConfig,
        Language,
        MCPConfig,
        RateLimitTier,
        ResourceDescriptions,
        ServerConfig,
        ToolDescriptions,
        TransportType,
        get_config,
        reload_config,
    )

    # Resources
    from .resources import (
        CropCatalogResource,
        FarmerDataResource,
        FieldDataResource,
        KnowledgeBaseResource,
        Resource,
        ResourceContent,
        ResourceManager,
        ResourceProvider,
        WeatherDataResource,
    )

    # Server
    from .server import (
        JSONRPCError,
        JSONRPCRequest,
        JSONRPCResponse,
        MCPServer,
        SAHOOLMCPServer,
        run_server,
    )

    # Tools
    from .tools import (
        AgentInstance,
        SAHOOLTools,
        ToolResult,
    )

    __all__ = [
        # Server
        "SAHOOLMCPServer",
        "MCPServer",  # Alias for backward compatibility
        "JSONRPCRequest",
        "JSONRPCResponse",
        "JSONRPCError",
        "run_server",
        # Tools
        "SAHOOLTools",
        "SAHOOLSkillsTools",
        "ToolResult",
        "AgentInstance",
        "extend_mcp_server_with_skills",
        # Resources
        "ResourceManager",
        "ResourceProvider",
        "Resource",
        "ResourceContent",
        "FieldDataResource",
        "FarmerDataResource",
        "WeatherDataResource",
        "CropCatalogResource",
        "KnowledgeBaseResource",
        # Configuration
        "MCPConfig",
        "ServerConfig",
        "APIConfig",
        "AuthConfig",
        "AgentConfig",
        "BilingualConfig",
        "TransportType",
        "Language",
        "AgentType",
        "RateLimitTier",
        "ToolDescriptions",
        "ResourceDescriptions",
        "get_config",
        "reload_config",
        # Client
        "MCPClient",
    ]

except ImportError:
    # FastAPI not available - only skills_server is accessible
    __all__ = [
        "SAHOOLSkillsTools",
        "extend_mcp_server_with_skills",
    ]

__version__ = "1.0.0"
__author__ = "SAHOOL Platform Team"
