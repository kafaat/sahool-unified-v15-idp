"""
SAHOOL MCP Server - Standalone Service
=======================================

Standalone MCP server that exposes all SAHOOL capabilities via Model Context Protocol.
Supports both stdio and SSE (HTTP) transports.

Port: 8200
Endpoints:
  - POST /mcp - JSON-RPC 2.0 endpoint
  - GET /mcp/sse - Server-Sent Events endpoint
  - GET /health - Health check
  - GET /healthz - Kubernetes health check
  - GET /ready - Readiness probe
  - GET /metrics - Prometheus metrics

Environment Variables:
  - SAHOOL_API_URL: Base URL for SAHOOL API (default: http://localhost:8000)
  - MCP_SERVER_PORT: Port to run on (default: 8200)
  - MCP_SERVER_HOST: Host to bind to (default: 0.0.0.0)
  - LOG_LEVEL: Logging level (default: INFO)
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from shared.mcp.server import MCPServer

# Configuration
PORT = int(os.getenv("MCP_SERVER_PORT", "8200"))
HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SAHOOL_API_URL = os.getenv("SAHOOL_API_URL", "http://localhost:8000")

# CORS Configuration - environment-based allowed origins
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8080,https://sahool.com,https://app.sahool.com"
).split(",")

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Metrics
mcp_requests_total = Counter(
    "mcp_requests_total",
    "Total number of MCP requests",
    ["method", "status"],
)

mcp_request_duration = Histogram(
    "mcp_request_duration_seconds",
    "MCP request duration in seconds",
    ["method"],
)

tool_calls_total = Counter(
    "mcp_tool_calls_total",
    "Total number of tool calls",
    ["tool_name", "status"],
)

resource_reads_total = Counter(
    "mcp_resource_reads_total",
    "Total number of resource reads",
    ["resource_type", "status"],
)


# ==================== Lifespan ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info(f"Starting SAHOOL MCP Server v{app.state.mcp_server.version}")
    logger.info(f"SAHOOL API URL: {SAHOOL_API_URL}")
    logger.info(f"Listening on {HOST}:{PORT}")

    yield

    logger.info("Shutting down SAHOOL MCP Server")
    await app.state.mcp_server.close()


# ==================== FastAPI Application ====================

# Create MCP server instance
mcp_server = MCPServer(name="sahool-mcp-server", version="1.0.0")

# Create FastAPI app
app = FastAPI(
    title="SAHOOL MCP Server",
    version="1.0.0",
    description="Model Context Protocol server for SAHOOL agricultural platform",
    lifespan=lifespan,
)

# Store MCP server in app state
app.state.mcp_server = mcp_server

# CORS middleware - using environment-based allowed origins instead of wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)


# ==================== Health Endpoints ====================


@app.get("/health")
@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mcp-server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_server": {
            "name": mcp_server.name,
            "version": mcp_server.version,
        },
    }


@app.get("/ready")
async def ready():
    """Readiness probe"""
    return {
        "status": "ready",
        "service": "mcp-server",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# ==================== MCP Endpoints ====================


@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": mcp_server.name,
        "version": mcp_server.version,
        "description": "SAHOOL Model Context Protocol Server",
        "endpoints": {
            "mcp": "/mcp",
            "sse": "/mcp/sse",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
        },
        "capabilities": [
            "tools",
            "resources",
            "prompts",
        ],
        "transports": ["http", "sse"],
    }


@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP JSON-RPC request"""
    start_time = asyncio.get_event_loop().time()

    try:
        data = await request.json()
        method = data.get("method", "unknown")

        logger.info(f"MCP Request: {method} (id: {data.get('id')})")

        from shared.mcp.server import JSONRPCRequest

        rpc_request = JSONRPCRequest(**data)
        response = await mcp_server.handle_request(rpc_request)

        # Track metrics
        duration = asyncio.get_event_loop().time() - start_time
        mcp_request_duration.labels(method=method).observe(duration)

        if response.error:
            mcp_requests_total.labels(method=method, status="error").inc()
        else:
            mcp_requests_total.labels(method=method, status="success").inc()

        # Track tool calls
        if method == "tools/call":
            tool_name = data.get("params", {}).get("name", "unknown")
            status = "error" if response.error else "success"
            tool_calls_total.labels(tool_name=tool_name, status=status).inc()

        # Track resource reads
        if method == "resources/read":
            uri = data.get("params", {}).get("uri", "unknown")
            resource_type = uri.split("://")[0] if "://" in uri else "unknown"
            status = "error" if response.error else "success"
            resource_reads_total.labels(resource_type=resource_type, status=status).inc()

        logger.info(
            f"MCP Response: {method} (id: {data.get('id')}) - "
            f"{'ERROR' if response.error else 'SUCCESS'} ({duration:.3f}s)"
        )

        return JSONResponse(
            content=json.loads(response.json()),
            status_code=200 if not response.error else 500,
        )

    except Exception as e:
        duration = asyncio.get_event_loop().time() - start_time
        logger.error(f"Error handling MCP request: {e}", exc_info=True)
        mcp_requests_total.labels(method="unknown", status="error").inc()

        from shared.mcp.server import JSONRPCResponse

        error_response = JSONRPCResponse(
            jsonrpc="2.0",
            error={"code": -32603, "message": "Internal error", "data": str(e)},
        )

        return JSONResponse(
            content=json.loads(error_response.json()),
            status_code=500,
        )


@app.get("/mcp/sse")
async def handle_sse(request: Request):
    """Handle Server-Sent Events for streaming MCP"""
    import json

    async def event_generator():
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'server': mcp_server.name, 'version': mcp_server.version})}\n\n"

            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    logger.info("SSE client disconnected")
                    break

                # Send heartbeat every 30 seconds
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
            "X-Accel-Buffering": "no",
        },
    )


# ==================== Additional Endpoints ====================


@app.get("/tools")
async def list_tools():
    """List available tools (convenience endpoint)"""
    from shared.mcp.server import JSONRPCRequest

    request = JSONRPCRequest(method="tools/list")
    response = await mcp_server.handle_request(request)

    if response.error:
        return JSONResponse(content={"error": response.error}, status_code=500)

    return response.result


@app.get("/resources")
async def list_resources():
    """List available resources (convenience endpoint)"""
    from shared.mcp.server import JSONRPCRequest

    request = JSONRPCRequest(method="resources/list")
    response = await mcp_server.handle_request(request)

    if response.error:
        return JSONResponse(content={"error": response.error}, status_code=500)

    return response.result


@app.get("/prompts")
async def list_prompts():
    """List available prompts (convenience endpoint)"""
    from shared.mcp.server import JSONRPCRequest

    request = JSONRPCRequest(method="prompts/list")
    response = await mcp_server.handle_request(request)

    if response.error:
        return JSONResponse(content={"error": response.error}, status_code=500)

    return response.result


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower(),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
