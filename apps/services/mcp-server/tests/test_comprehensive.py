"""
Comprehensive unit tests for MCP Server Service.
Tests cover: health endpoints, MCP protocol, JSON-RPC validation,
SSE endpoint, convenience endpoints, metrics, error handling.
Target: >60% code coverage.
"""

import json
import os
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add service directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

from src.main import (
    CORS_ALLOWED_ORIGINS,
    HOST,
    LOG_LEVEL,
    PORT,
    SAHOOL_API_URL,
    app,
    mcp_server,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_TENANT_HEADER = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}


class _TenantClient:
    """Wrapper that adds X-Tenant-ID header to all requests."""

    def __init__(self, client):
        self._client = client

    def get(self, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(_TENANT_HEADER)
        return self._client.get(url, headers=headers, **kwargs)

    def post(self, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(_TENANT_HEADER)
        return self._client.post(url, headers=headers, **kwargs)

    def stream(self, method, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(_TENANT_HEADER)
        return self._client.stream(method, url, headers=headers, **kwargs)


@pytest.fixture
def client():
    """Test client fixture with tenant header."""
    return _TenantClient(TestClient(app))


# ---------------------------------------------------------------------------
# Test Configuration
# ---------------------------------------------------------------------------


class TestConfiguration:
    def test_default_port(self):
        assert PORT == 8201

    def test_default_host(self):
        assert HOST == "0.0.0.0"

    def test_default_log_level(self):
        assert LOG_LEVEL == "INFO"

    def test_default_api_url(self):
        assert SAHOOL_API_URL == "http://localhost:8000"

    def test_cors_allowed_origins_parsed(self):
        assert isinstance(CORS_ALLOWED_ORIGINS, list)
        assert len(CORS_ALLOWED_ORIGINS) > 0

    def test_mcp_server_name(self):
        assert mcp_server.name == "sahool-mcp-server"
        assert mcp_server.version == "16.0.0"


# ---------------------------------------------------------------------------
# Test Health Endpoints
# ---------------------------------------------------------------------------


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcp-server"
        assert data["version"] == "16.0.0"
        assert "timestamp" in data
        assert "mcp_server" in data
        assert data["mcp_server"]["name"] == "sahool-mcp-server"

    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ready(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "mcp-server"
        assert "checks" in data

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


# ---------------------------------------------------------------------------
# Test Root Endpoint
# ---------------------------------------------------------------------------


class TestRootEndpoint:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "sahool-mcp-server"
        assert data["version"] == "16.0.0"
        assert "endpoints" in data
        assert "capabilities" in data
        assert "transports" in data

    def test_root_endpoints_structure(self, client):
        data = client.get("/").json()
        endpoints = data["endpoints"]
        assert "mcp" in endpoints
        assert "sse" in endpoints
        assert "health" in endpoints
        assert "metrics" in endpoints

    def test_root_capabilities(self, client):
        data = client.get("/").json()
        caps = data["capabilities"]
        assert "tools" in caps
        assert "resources" in caps
        assert "prompts" in caps

    def test_root_transports(self, client):
        data = client.get("/").json()
        assert "http" in data["transports"]
        assert "sse" in data["transports"]


# ---------------------------------------------------------------------------
# Test MCP JSON-RPC Protocol
# ---------------------------------------------------------------------------


class TestMCPProtocol:
    def test_initialize(self, client):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data

    def test_tools_list(self, client):
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "tools" in data["result"]
        tools = data["result"]["tools"]
        assert len(tools) > 0

    def test_resources_list(self, client):
        request = {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"

    def test_prompts_list(self, client):
        request = {"jsonrpc": "2.0", "id": 5, "method": "prompts/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "prompts" in data["result"]
        assert len(data["result"]["prompts"]) > 0

    def test_prompts_get_field_analysis(self, client):
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "prompts/get",
            "params": {
                "name": "field_analysis",
                "arguments": {"field_id": "field-123"},
            },
        }
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "messages" in data["result"]

    def test_prompts_get_irrigation_plan(self, client):
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "prompts/get",
            "params": {
                "name": "irrigation_plan",
                "arguments": {"field_id": "field-456"},
            },
        }
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

    def test_prompts_get_crop_recommendation(self, client):
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "prompts/get",
            "params": {
                "name": "crop_recommendation",
                "arguments": {"field_id": "field-789"},
            },
        }
        response = client.post("/mcp", json=request)
        assert response.status_code == 200

    def test_resources_templates_list(self, client):
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/templates/list",
            "params": {},
        }
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "resourceTemplates" in data["result"]

    def test_invalid_method(self, client):
        request = {"jsonrpc": "2.0", "id": 10, "method": "nonexistent/method", "params": {}}
        response = client.post("/mcp", json=request)
        # JSON-RPC 2.0 spec: HTTP 200 with error in body
        assert response.status_code == 200
        data = response.json()
        assert "error" in data


# ---------------------------------------------------------------------------
# Test JSON-RPC Validation
# ---------------------------------------------------------------------------


class TestJSONRPCValidation:
    def test_missing_jsonrpc_version(self, client):
        request = {"id": 1, "method": "tools/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600

    def test_wrong_jsonrpc_version(self, client):
        request = {"jsonrpc": "1.0", "id": 1, "method": "tools/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600
        assert "2.0" in data["error"]["message"]

    def test_missing_method(self, client):
        request = {"jsonrpc": "2.0", "id": 1, "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600

    def test_method_not_string(self, client):
        request = {"jsonrpc": "2.0", "id": 1, "method": 123, "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    def test_request_preserves_id(self, client):
        request = {"jsonrpc": "2.0", "id": 42, "method": "tools/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 42

    def test_string_id(self, client):
        request = {"jsonrpc": "2.0", "id": "my-id", "method": "tools/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "my-id"


# ---------------------------------------------------------------------------
# Test Convenience Endpoints
# ---------------------------------------------------------------------------


class TestConvenienceEndpoints:
    def test_list_tools(self, client):
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) > 0

    def test_list_prompts(self, client):
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data
        assert len(data["prompts"]) > 0

    def test_list_resources(self, client):
        response = client.get("/resources")
        assert response.status_code == 200

    def test_tools_match_mcp_protocol(self, client):
        """Convenience endpoint should return same tools as MCP protocol."""
        # Via convenience
        conv_tools = client.get("/tools").json()["tools"]
        # Via MCP protocol
        mcp_resp = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        ).json()
        mcp_tools = mcp_resp["result"]["tools"]
        assert len(conv_tools) == len(mcp_tools)


# ---------------------------------------------------------------------------
# Test Metrics Endpoint
# ---------------------------------------------------------------------------


class TestMetricsEndpoint:
    def test_metrics(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_metrics_contains_counters(self, client):
        # First make a request to populate metrics
        client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        )
        response = client.get("/metrics")
        text = response.text
        assert "mcp_requests_total" in text

    def test_metrics_after_tool_call(self, client):
        """Tool call metrics should be tracked."""
        client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "get_weather_forecast", "arguments": {"location": "Sana'a"}},
            },
        )
        response = client.get("/metrics")
        assert "mcp_tool_calls_total" in response.text

    def test_metrics_after_resource_read(self, client):
        """Resource read metrics should be tracked."""
        client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "resources/read",
                "params": {"uri": "field://test/overview"},
            },
        )
        response = client.get("/metrics")
        assert "mcp_resource_reads_total" in response.text


# ---------------------------------------------------------------------------
# Test SSE Endpoint
# ---------------------------------------------------------------------------


class TestSSEEndpoint:
    def test_sse_endpoint_exists(self, client):
        """Test SSE endpoint is registered on the app."""
        routes = [r.path for r in app.routes if hasattr(r, "path")]
        assert "/mcp/sse" in routes

    def test_sse_handler_is_async(self):
        """Verify the SSE handler function is defined."""
        from src.main import handle_sse
        import asyncio
        assert asyncio.iscoroutinefunction(handle_sse)


# ---------------------------------------------------------------------------
# Test Error Handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_invalid_json_body(self, client):
        """Malformed JSON should return error response."""
        response = client.post(
            "/mcp",
            content=b"not json",
            headers={"content-type": "application/json"},
        )
        # Should still return 200 per JSON-RPC spec with error in body
        assert response.status_code in [200, 422]

    def test_empty_body(self, client):
        response = client.post(
            "/mcp",
            content=b"{}",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    def test_null_id_preserved(self, client):
        request = {"jsonrpc": "2.0", "id": None, "method": "tools/list", "params": {}}
        response = client.post("/mcp", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") is None
