"""
SAHOOL MCP Server - Model Context Protocol Server Implementation
=================================================================

Implements a production-ready MCP server for SAHOOL agricultural platform.
Supports stdio and SSE transports, tool invocation, resource access, and prompt templates.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .resources import ResourceManager
from .tools import SAHOOLTools

logger = logging.getLogger(__name__)


# ==================== MCP Protocol Models ====================


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request"""

    jsonrpc: str = "2.0"
    id: Optional[str | int] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response"""

    jsonrpc: str = "2.0"
    id: Optional[str | int] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 Error"""

    code: int
    message: str
    data: Optional[Any] = None


# ==================== MCP Server Implementation ====================


class MCPServer:
    """
    Model Context Protocol Server

    Implements the MCP specification for exposing SAHOOL agricultural
    tools and resources to AI assistants.

    Supports:
    - Tool invocation
    - Resource access
    - Prompt templates
    - stdio and SSE transports
    """

    def __init__(self, name: str = "sahool-mcp-server", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools = SAHOOLTools()
        self.resources = ResourceManager()
        self.prompts: List[Dict[str, Any]] = []
        self._initialize_prompts()

    def _initialize_prompts(self):
        """Initialize prompt templates"""
        self.prompts = [
            {
                "name": "field_analysis",
                "description": "Comprehensive field analysis including health, weather, and recommendations",
                "arguments": [
                    {
                        "name": "field_id",
                        "description": "ID of the field to analyze",
                        "required": True,
                    }
                ],
            },
            {
                "name": "irrigation_plan",
                "description": "Create irrigation plan based on weather forecast and soil conditions",
                "arguments": [
                    {
                        "name": "field_id",
                        "description": "ID of the field",
                        "required": True,
                    },
                    {
                        "name": "days",
                        "description": "Number of days to plan for",
                        "required": False,
                    },
                ],
            },
            {
                "name": "crop_recommendation",
                "description": "Recommend crops suitable for field conditions",
                "arguments": [
                    {
                        "name": "field_id",
                        "description": "ID of the field",
                        "required": True,
                    },
                    {
                        "name": "season",
                        "description": "Growing season",
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

    async def handle_initialize(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "prompts": {"listChanged": False},
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version,
            },
        }

    async def handle_tools_list(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {"tools": self.tools.get_tool_definitions()}

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            raise ValueError("Tool name is required")

        result = await self.tools.invoke_tool(tool_name, arguments)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result.dict(), indent=2),
                }
            ],
            "isError": not result.success,
        }

    async def handle_resources_list(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources = await self.resources.list_all_resources()
        return {
            "resources": [
                {
                    "uri": r.uri,
                    "name": r.name,
                    "description": r.description,
                    "mimeType": r.mimeType,
                }
                for r in resources
            ]
        }

    async def handle_resources_templates_list(
        self, params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle resources/templates/list request"""
        return {"resourceTemplates": self.resources.get_resource_templates()}

    async def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        if not uri:
            raise ValueError("Resource URI is required")

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

    async def handle_prompts_list(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        return {"prompts": self.prompts}

    async def handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request"""
        prompt_name = params.get("name")
        prompt_args = params.get("arguments", {})

        # Find the prompt template
        prompt_template = next((p for p in self.prompts if p["name"] == prompt_name), None)

        if not prompt_template:
            raise ValueError(f"Unknown prompt: {prompt_name}")

        # Generate prompt messages based on template
        if prompt_name == "field_analysis":
            field_id = prompt_args.get("field_id")
            messages = [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please provide a comprehensive analysis of field {field_id}, including crop health status, current weather conditions, irrigation needs, and any recommendations for the farmer.",
                    },
                }
            ]

        elif prompt_name == "irrigation_plan":
            field_id = prompt_args.get("field_id")
            days = prompt_args.get("days", 7)
            messages = [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Create an irrigation plan for field {field_id} for the next {days} days. Consider weather forecast, soil moisture levels, crop type, and growth stage.",
                    },
                }
            ]

        elif prompt_name == "crop_recommendation":
            field_id = prompt_args.get("field_id")
            season = prompt_args.get("season", "current")
            messages = [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Recommend suitable crops for field {field_id} for the {season} season. Consider soil properties, climate conditions, and market demand.",
                    },
                }
            ]

        else:
            messages = [
                {
                    "role": "user",
                    "content": {"type": "text", "text": f"Execute prompt: {prompt_name}"},
                }
            ]

        return {"description": prompt_template.get("description"), "messages": messages}

    async def handle_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle a JSON-RPC request"""
        method = request.method
        params = request.params or {}

        try:
            # Route to appropriate handler
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list(params)
            elif method == "resources/templates/list":
                result = await self.handle_resources_templates_list(params)
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            elif method == "prompts/list":
                result = await self.handle_prompts_list(params)
            elif method == "prompts/get":
                result = await self.handle_prompts_get(params)
            else:
                raise ValueError(f"Unknown method: {method}")

            return JSONRPCResponse(jsonrpc="2.0", id=request.id, result=result)

        except Exception as e:
            logger.error(f"Error handling request {method}: {e}", exc_info=True)
            return JSONRPCResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32603,
                    "message": "Internal error",
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
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

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
                    print(response.json(), flush=True)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = JSONRPCResponse(
                        jsonrpc="2.0",
                        error={"code": -32700, "message": "Parse error"},
                    )
                    print(error_response.json(), flush=True)

                except Exception as e:
                    logger.error(f"Error processing request: {e}", exc_info=True)

        except KeyboardInterrupt:
            logger.info("Shutting down...")

        finally:
            await self.close()

    # ==================== Transport: SSE (FastAPI) ====================

    def create_fastapi_app(self) -> FastAPI:
        """
        Create FastAPI application for SSE transport

        Returns FastAPI app that can be run with uvicorn for HTTP/SSE transport.
        """
        app = FastAPI(
            title=self.name,
            version=self.version,
            description="SAHOOL Model Context Protocol Server",
        )

        @app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "server": self.name,
                "version": self.version,
                "timestamp": datetime.utcnow().isoformat(),
            }

        @app.post("/mcp")
        async def handle_mcp_request(request: Request):
            """Handle MCP JSON-RPC request"""
            try:
                data = await request.json()
                rpc_request = JSONRPCRequest(**data)
                response = await self.handle_request(rpc_request)
                return Response(
                    content=response.json(),
                    media_type="application/json",
                )
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}", exc_info=True)
                error_response = JSONRPCResponse(
                    jsonrpc="2.0",
                    error={"code": -32603, "message": "Internal error", "data": str(e)},
                )
                return Response(
                    content=error_response.json(),
                    media_type="application/json",
                    status_code=500,
                )

        @app.get("/mcp/sse")
        async def handle_sse(request: Request):
            """Handle Server-Sent Events for streaming MCP"""

            async def event_generator():
                try:
                    # Send initial connection event
                    yield f"data: {json.dumps({'type': 'connected', 'server': self.name})}\n\n"

                    # Keep connection alive
                    while True:
                        if await request.is_disconnected():
                            break

                        # Send heartbeat
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

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

        @app.on_event("shutdown")
        async def shutdown():
            """Cleanup on shutdown"""
            await self.close()

        return app


# ==================== Standalone Server Runner ====================


async def run_server(transport: str = "stdio", host: str = "0.0.0.0", port: int = 8200):
    """
    Run MCP server with specified transport

    Args:
        transport: Transport type ('stdio' or 'sse')
        host: Host to bind (for SSE transport)
        port: Port to bind (for SSE transport)
    """
    server = MCPServer()

    if transport == "stdio":
        await server.run_stdio()
    elif transport == "sse":
        import uvicorn

        app = server.create_fastapi_app()
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
    else:
        raise ValueError(f"Unknown transport: {transport}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SAHOOL MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE transport (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8200, help="Port for SSE transport (default: 8200)")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(run_server(transport=args.transport, host=args.host, port=args.port))
