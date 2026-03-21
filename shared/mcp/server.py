"""
SAHOOL MCP Server - Model Context Protocol Server Implementation
=================================================================

Implements a production-ready MCP server for SAHOOL agricultural platform.
Supports stdio and HTTP/SSE transports, tool invocation, resource access, and prompt templates.

Features:
- Full MCP protocol compliance (version 2024-11-05)
- Bilingual support (English/Arabic)
- Multiple transport options (stdio, HTTP, SSE, WebSocket)
- Tool registration and invocation
- Resource management
- Prompt templates
- Health monitoring

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import MCPConfig, get_config
from .resources import ResourceManager
from .tools import SAHOOLTools

logger = logging.getLogger(__name__)


# ==================== MCP Protocol Models ====================


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request"""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    method: str
    params: dict[str, Any] | None = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response"""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    result: Any | None = None
    error: dict[str, Any] | None = None


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 Error"""

    code: int
    message: str
    data: Any | None = None


# ==================== MCP Server Implementation ====================


class SAHOOLMCPServer:
    """
    SAHOOL Model Context Protocol Server

    Implements the MCP specification for exposing SAHOOL agricultural
    tools and resources to AI assistants.

    Features:
    - Tool invocation (agricultural, CRM, AI agents)
    - Resource access (fields, farmers, weather, crops, knowledge)
    - Prompt templates
    - Multiple transports (stdio, HTTP, SSE)
    - Bilingual support (English/Arabic)

    Usage:
        server = SAHOOLMCPServer()
        await server.run_stdio()  # For stdio transport
        # OR
        app = server.create_fastapi_app()  # For HTTP transport
    """

    def __init__(
        self,
        name: str | None = None,
        version: str = "1.0.0",
        config: MCPConfig | None = None,
    ):
        """
        Initialize SAHOOL MCP Server

        Args:
            name: Server name (default: from config)
            version: Server version
            config: MCP configuration (default: from environment)
        """
        self.config = config or get_config()
        self.name = name or self.config.server.name
        self.name_ar = self.config.server.name_ar
        self.version = version
        self.tools = SAHOOLTools(config=self.config)
        self.resources = ResourceManager(config=self.config)
        self.prompts: list[dict[str, Any]] = []
        self._initialize_prompts()

    def _initialize_prompts(self):
        """Initialize prompt templates with bilingual support"""
        self.prompts = [
            {
                "name": "field_analysis",
                "description": "Comprehensive field analysis including health, weather, and recommendations",
                "description_ar": "تحليل شامل للحقل يشمل الصحة والطقس والتوصيات",
                "arguments": [
                    {
                        "name": "field_id",
                        "description": "ID of the field to analyze | معرف الحقل للتحليل",
                        "required": True,
                    },
                    {
                        "name": "language",
                        "description": "Response language (en, ar, both) | لغة الرد",
                        "required": False,
                    },
                ],
            },
            {
                "name": "irrigation_plan",
                "description": "Create irrigation plan based on weather forecast and soil conditions",
                "description_ar": "إنشاء خطة ري بناءً على توقعات الطقس وظروف التربة",
                "arguments": [
                    {
                        "name": "field_id",
                        "description": "ID of the field | معرف الحقل",
                        "required": True,
                    },
                    {
                        "name": "days",
                        "description": "Number of days to plan for | عدد أيام الخطة",
                        "required": False,
                    },
                ],
            },
            {
                "name": "crop_recommendation",
                "description": "Recommend crops suitable for field conditions",
                "description_ar": "توصية بالمحاصيل المناسبة لظروف الحقل",
                "arguments": [
                    {
                        "name": "field_id",
                        "description": "ID of the field | معرف الحقل",
                        "required": True,
                    },
                    {
                        "name": "season",
                        "description": "Growing season | موسم الزراعة",
                        "required": False,
                    },
                ],
            },
            {
                "name": "farmer_advisory",
                "description": "Generate personalized advisory for a farmer",
                "description_ar": "إنشاء استشارة مخصصة للمزارع",
                "arguments": [
                    {
                        "name": "farmer_id",
                        "description": "ID of the farmer | معرف المزارع",
                        "required": True,
                    },
                    {
                        "name": "topic",
                        "description": "Advisory topic (irrigation, fertilizer, pest, general) | موضوع الاستشارة",
                        "required": False,
                    },
                ],
            },
            {
                "name": "pest_diagnosis",
                "description": "Diagnose pest or disease issues based on symptoms",
                "description_ar": "تشخيص مشاكل الآفات أو الأمراض بناءً على الأعراض",
                "arguments": [
                    {
                        "name": "field_id",
                        "description": "ID of the field | معرف الحقل",
                        "required": True,
                    },
                    {
                        "name": "symptoms",
                        "description": "Observed symptoms | الأعراض الملاحظة",
                        "required": True,
                    },
                    {
                        "name": "crop_type",
                        "description": "Type of crop | نوع المحصول",
                        "required": False,
                    },
                ],
            },
        ]

    async def close(self):
        """Close server and cleanup resources"""
        await self.tools.close()
        await self.resources.close()

    # ==================== MCP Protocol Handlers ====================

    async def handle_initialize(self, params: dict[str, Any] | None) -> dict[str, Any]:
        """Handle initialize request"""
        return {
            "protocolVersion": self.config.server.protocol_version,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "prompts": {"listChanged": False},
            },
            "serverInfo": {
                "name": self.name,
                "name_ar": self.name_ar,
                "version": self.version,
                "description": "SAHOOL Agricultural Intelligence Platform MCP Server",
                "description_ar": "خادم MCP لمنصة سهول للذكاء الزراعي",
            },
        }

    async def handle_tools_list(self, params: dict[str, Any] | None) -> dict[str, Any]:
        """Handle tools/list request"""
        return {"tools": self.tools.get_tool_definitions()}

    async def handle_tools_call(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name", "").strip()
        arguments = params.get("arguments", {})

        if not tool_name:
            raise ValueError("Tool name is required | اسم الأداة مطلوب")

        # Validate tool_name against registered tools to prevent injection
        registered_tools = {t["name"] for t in self.tools.get_tool_definitions()}
        if tool_name not in registered_tools:
            raise ValueError(f"Unknown tool: {tool_name} | أداة غير معروفة: {tool_name}")

        result = await self.tools.invoke_tool(tool_name, arguments)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result.model_dump(), indent=2, ensure_ascii=False),
                }
            ],
            "isError": not result.success,
        }

    async def handle_resources_list(self, params: dict[str, Any] | None) -> dict[str, Any]:
        """Handle resources/list request"""
        resources = await self.resources.list_all_resources()
        return {
            "resources": [
                {
                    "uri": r.uri,
                    "name": r.name,
                    "name_ar": r.name_ar,
                    "description": r.description,
                    "description_ar": r.description_ar,
                    "mimeType": r.mimeType,
                }
                for r in resources
            ]
        }

    async def handle_resources_templates_list(self, params: dict[str, Any] | None) -> dict[str, Any]:
        """Handle resources/templates/list request"""
        return {"resourceTemplates": self.resources.get_resource_templates()}

    async def handle_resources_read(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        if not uri:
            raise ValueError("Resource URI is required | معرف URI للمورد مطلوب")

        content = await self.resources.get_resource(uri)

        return {
            "contents": [
                {
                    "uri": content.uri,
                    "mimeType": content.mimeType,
                    "text": content.text,
                    "blob": content.blob,
                }
            ]
        }

    async def handle_prompts_list(self, params: dict[str, Any] | None) -> dict[str, Any]:
        """Handle prompts/list request"""
        return {"prompts": self.prompts}

    async def handle_prompts_get(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle prompts/get request"""
        prompt_name = params.get("name")
        prompt_args = params.get("arguments", {})

        # Find the prompt template
        prompt_template = next((p for p in self.prompts if p["name"] == prompt_name), None)

        if not prompt_template:
            raise ValueError(f"Unknown prompt: {prompt_name} | قالب غير معروف: {prompt_name}")

        # Generate prompt messages based on template
        language = prompt_args.get("language", "both")

        if prompt_name == "field_analysis":
            field_id = prompt_args.get("field_id")
            if language == "ar":
                text = f"يرجى تقديم تحليل شامل للحقل {field_id}، بما في ذلك حالة صحة المحصول وظروف الطقس الحالية واحتياجات الري وأي توصيات للمزارع."
            elif language == "en":
                text = f"Please provide a comprehensive analysis of field {field_id}, including crop health status, current weather conditions, irrigation needs, and any recommendations for the farmer."
            else:
                text = f"Please provide a comprehensive analysis of field {field_id}, including crop health status, current weather conditions, irrigation needs, and any recommendations for the farmer.\n\nيرجى تقديم تحليل شامل للحقل {field_id}، بما في ذلك حالة صحة المحصول وظروف الطقس الحالية واحتياجات الري وأي توصيات للمزارع."
            messages = [{"role": "user", "content": {"type": "text", "text": text}}]

        elif prompt_name == "irrigation_plan":
            field_id = prompt_args.get("field_id")
            days = prompt_args.get("days", 7)
            if language == "ar":
                text = f"أنشئ خطة ري للحقل {field_id} للأيام الـ {days} القادمة. خذ بعين الاعتبار توقعات الطقس ومستويات رطوبة التربة ونوع المحصول ومرحلة النمو."
            elif language == "en":
                text = f"Create an irrigation plan for field {field_id} for the next {days} days. Consider weather forecast, soil moisture levels, crop type, and growth stage."
            else:
                text = f"Create an irrigation plan for field {field_id} for the next {days} days. Consider weather forecast, soil moisture levels, crop type, and growth stage.\n\nأنشئ خطة ري للحقل {field_id} للأيام الـ {days} القادمة. خذ بعين الاعتبار توقعات الطقس ومستويات رطوبة التربة ونوع المحصول ومرحلة النمو."
            messages = [{"role": "user", "content": {"type": "text", "text": text}}]

        elif prompt_name == "crop_recommendation":
            field_id = prompt_args.get("field_id")
            season = prompt_args.get("season", "current")
            if language == "ar":
                text = f"أوصِ بالمحاصيل المناسبة للحقل {field_id} لموسم {season}. خذ بعين الاعتبار خصائص التربة والظروف المناخية والطلب في السوق."
            elif language == "en":
                text = f"Recommend suitable crops for field {field_id} for the {season} season. Consider soil properties, climate conditions, and market demand."
            else:
                text = f"Recommend suitable crops for field {field_id} for the {season} season. Consider soil properties, climate conditions, and market demand.\n\nأوصِ بالمحاصيل المناسبة للحقل {field_id} لموسم {season}. خذ بعين الاعتبار خصائص التربة والظروف المناخية والطلب في السوق."
            messages = [{"role": "user", "content": {"type": "text", "text": text}}]

        elif prompt_name == "farmer_advisory":
            farmer_id = prompt_args.get("farmer_id")
            topic = prompt_args.get("topic", "general")
            if language == "ar":
                text = f"أنشئ استشارة مخصصة للمزارع {farmer_id} حول موضوع {topic}. خذ بعين الاعتبار تاريخ المزارع وتفضيلاته والظروف الحالية للمزرعة."
            elif language == "en":
                text = f"Generate personalized advisory for farmer {farmer_id} about {topic}. Consider the farmer's history, preferences, and current farm conditions."
            else:
                text = f"Generate personalized advisory for farmer {farmer_id} about {topic}. Consider the farmer's history, preferences, and current farm conditions.\n\nأنشئ استشارة مخصصة للمزارع {farmer_id} حول موضوع {topic}. خذ بعين الاعتبار تاريخ المزارع وتفضيلاته والظروف الحالية للمزرعة."
            messages = [{"role": "user", "content": {"type": "text", "text": text}}]

        elif prompt_name == "pest_diagnosis":
            field_id = prompt_args.get("field_id")
            symptoms = prompt_args.get("symptoms", "")
            crop_type = prompt_args.get("crop_type", "")
            if language == "ar":
                text = f"شخّص مشكلة الآفات أو المرض في الحقل {field_id}. الأعراض الملاحظة: {symptoms}. نوع المحصول: {crop_type}. قدم التشخيص وخيارات العلاج."
            elif language == "en":
                text = f"Diagnose pest or disease issue in field {field_id}. Observed symptoms: {symptoms}. Crop type: {crop_type}. Provide diagnosis and treatment options."
            else:
                text = f"Diagnose pest or disease issue in field {field_id}. Observed symptoms: {symptoms}. Crop type: {crop_type}. Provide diagnosis and treatment options.\n\nشخّص مشكلة الآفات أو المرض في الحقل {field_id}. الأعراض الملاحظة: {symptoms}. نوع المحصول: {crop_type}. قدم التشخيص وخيارات العلاج."
            messages = [{"role": "user", "content": {"type": "text", "text": text}}]

        else:
            messages = [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Execute prompt: {prompt_name}",
                    },
                }
            ]

        return {
            "description": prompt_template.get("description"),
            "description_ar": prompt_template.get("description_ar"),
            "messages": messages,
        }

    async def handle_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle a JSON-RPC request"""
        method = request.method
        params = request.params or {}

        try:
            # Route to appropriate handler
            handlers = {
                "initialize": self.handle_initialize,
                "tools/list": self.handle_tools_list,
                "tools/call": self.handle_tools_call,
                "resources/list": self.handle_resources_list,
                "resources/templates/list": self.handle_resources_templates_list,
                "resources/read": self.handle_resources_read,
                "prompts/list": self.handle_prompts_list,
                "prompts/get": self.handle_prompts_get,
            }

            if method not in handlers:
                raise ValueError(f"Unknown method: {method}")

            result = await handlers[method](params)
            return JSONRPCResponse(jsonrpc="2.0", id=request.id, result=result)

        except Exception as e:
            logger.error(f"Error handling request {method}: {e}", exc_info=True)
            return JSONRPCResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32603,
                    "message": "Internal error",
                    "message_ar": "خطأ داخلي",
                    "data": str(e),
                },
            )

    # ==================== Transport: stdio ====================

    async def run_stdio(self):
        """
        Run MCP server with stdio transport

        Reads JSON-RPC requests from stdin and writes responses to stdout.
        Used for direct integration with AI assistants.
        """
        logger.info(f"Starting {self.name} v{self.version} (stdio transport)")

        try:
            while True:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse JSON-RPC request
                    request_data = json.loads(line)
                    request = JSONRPCRequest(**request_data)

                    # Handle request
                    response = await self.handle_request(request)

                    # Write response to stdout
                    print(response.model_dump_json(), flush=True)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = JSONRPCResponse(
                        jsonrpc="2.0",
                        error={"code": -32700, "message": "Parse error"},
                    )
                    print(error_response.model_dump_json(), flush=True)

                except Exception as e:
                    logger.error(f"Error processing request: {e}", exc_info=True)

        except KeyboardInterrupt:
            logger.info("Shutting down...")

        finally:
            await self.close()

    # ==================== Transport: HTTP/SSE (FastAPI) ====================

    def create_fastapi_app(self) -> FastAPI:
        """
        Create FastAPI application for HTTP/SSE transport

        Returns FastAPI app that can be run with uvicorn for HTTP/SSE transport.
        """
        app = FastAPI(
            title=self.name,
            version=self.version,
            description="SAHOOL Model Context Protocol Server - خادم MCP لمنصة سهول",
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.server.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/health")
        @app.get("/healthz")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "status_ar": "صحي",
                "server": self.name,
                "server_ar": self.name_ar,
                "version": self.version,
                "timestamp": datetime.now(UTC).isoformat(),
                "active_agents": len(self.tools.list_active_agents()),
            }

        @app.get("/readyz")
        async def readiness():
            """Readiness check endpoint"""
            return {
                "status": "ready",
                "status_ar": "جاهز",
                "tools_loaded": len(self.tools.get_tool_definitions()),
                "providers": self.resources.list_providers(),
            }

        @app.get("/info")
        async def server_info():
            """Get server information"""
            return {
                "name": self.name,
                "name_ar": self.name_ar,
                "version": self.version,
                "protocol_version": self.config.server.protocol_version,
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True,
                },
                "tool_count": len(self.tools.get_tool_definitions()),
                "prompt_count": len(self.prompts),
                "transports": ["stdio", "http", "sse"],
            }

        @app.post("/mcp")
        async def handle_mcp_request(request: Request):
            """Handle MCP JSON-RPC request"""
            try:
                data = await request.json()
                rpc_request = JSONRPCRequest(**data)
                response = await self.handle_request(rpc_request)
                return Response(
                    content=response.model_dump_json(),
                    media_type="application/json",
                )
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}", exc_info=True)
                error_response = JSONRPCResponse(
                    jsonrpc="2.0",
                    error={
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e),
                    },
                )
                return Response(
                    content=error_response.model_dump_json(),
                    media_type="application/json",
                    status_code=500,
                )

        @app.get("/mcp/sse")
        async def handle_sse(request: Request):
            """Handle Server-Sent Events for streaming MCP"""

            async def event_generator():
                try:
                    # Send initial connection event
                    yield f"data: {json.dumps({'type': 'connected', 'server': self.name, 'server_ar': self.name_ar})}\n\n"

                    # Keep connection alive
                    while True:
                        if await request.is_disconnected():
                            break

                        # Send heartbeat
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

                        await asyncio.sleep(30)

                except Exception as e:
                    logger.error(f"SSE error: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        @app.get("/tools")
        async def list_tools():
            """List all available tools"""
            return {"tools": self.tools.get_tool_definitions()}

        @app.get("/resources")
        async def list_resources():
            """List all available resources"""
            resources = await self.resources.list_all_resources()
            return {
                "resources": [
                    {
                        "uri": r.uri,
                        "name": r.name,
                        "name_ar": r.name_ar,
                        "description": r.description,
                    }
                    for r in resources
                ]
            }

        @app.get("/prompts")
        async def list_prompts():
            """List all available prompts"""
            return {"prompts": self.prompts}

        @app.get("/agents")
        async def list_agents():
            """List active AI agents"""
            return {"agents": self.tools.list_active_agents()}

        @app.on_event("shutdown")
        async def shutdown():
            """Cleanup on shutdown"""
            await self.close()

        return app


# Alias for backward compatibility
MCPServer = SAHOOLMCPServer


# ==================== Standalone Server Runner ====================


async def run_server(
    transport: str = "stdio",
    host: str | None = None,
    port: int = 8200,
    config: MCPConfig | None = None,
):
    # Default to localhost for security; use MCP_HOST env var or explicit param for containers
    if host is None:
        host = os.getenv("MCP_HOST", "127.0.0.1")
    """
    Run MCP server with specified transport

    Args:
        transport: Transport type ('stdio', 'http', or 'sse')
        host: Host to bind (for HTTP/SSE transport)
        port: Port to bind (for HTTP/SSE transport)
        config: MCP configuration
    """
    config = config or get_config()
    server = SAHOOLMCPServer(config=config)

    if transport == "stdio":
        await server.run_stdio()
    elif transport in ("http", "sse"):
        import uvicorn

        app = server.create_fastapi_app()
        uv_config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info" if config.server.debug else "warning",
        )
        server_instance = uvicorn.Server(uv_config)
        await server_instance.serve()
    else:
        raise ValueError(f"Unknown transport: {transport}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SAHOOL MCP Server | خادم MCP لسهول")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport type (default: stdio) | نوع النقل",
    )
    parser.add_argument(
        "--host",
        default=None,  # Will use MCP_HOST env var or 127.0.0.1; use --host 0.0.0.0 for containers
        help="Host for HTTP/SSE transport (default: 127.0.0.1, use 0.0.0.0 for containers)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8200,
        help="Port for HTTP/SSE transport (default: 8200)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(run_server(transport=args.transport, host=args.host, port=args.port))
