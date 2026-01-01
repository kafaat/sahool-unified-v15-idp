"""
Tests for SAHOOL MCP Server
"""

import json

import pytest
from fastapi.testclient import TestClient

# Import after adding to path
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)

from apps.services.mcp_server.src.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_health(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcp-server"

    def test_healthz(self, client):
        """Test healthz endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ready(self, client):
        """Test ready endpoint"""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "sahool-mcp-server"
        assert "endpoints" in data
        assert "capabilities" in data


class TestMCPProtocol:
    """Test MCP protocol endpoints"""

    def test_initialize(self, client):
        """Test MCP initialize request"""
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
        assert data["result"]["protocolVersion"] == "2024-11-05"
        assert "capabilities" in data["result"]
        assert "serverInfo" in data["result"]

    def test_tools_list(self, client):
        """Test tools/list request"""
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        response = client.post("/mcp", json=request)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "tools" in data["result"]

        tools = data["result"]["tools"]
        assert len(tools) == 5

        tool_names = [t["name"] for t in tools]
        assert "get_weather_forecast" in tool_names
        assert "analyze_crop_health" in tool_names
        assert "get_field_data" in tool_names
        assert "calculate_irrigation" in tool_names
        assert "get_fertilizer_recommendation" in tool_names

    def test_resources_list(self, client):
        """Test resources/list request"""
        request = {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}

        response = client.post("/mcp", json=request)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        # Note: This may fail if SAHOOL API is not available
        # assert "resources" in data["result"]

    def test_resources_templates_list(self, client):
        """Test resources/templates/list request"""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/templates/list",
            "params": {},
        }

        response = client.post("/mcp", json=request)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "resourceTemplates" in data["result"]

        templates = data["result"]["resourceTemplates"]
        assert len(templates) == 3

        uri_templates = [t["uriTemplate"] for t in templates]
        assert "field://{field_id}/{resource_type}" in uri_templates
        assert "weather://{resource_type}" in uri_templates
        assert "crops://{crop_id}/{resource_type}" in uri_templates

    def test_prompts_list(self, client):
        """Test prompts/list request"""
        request = {"jsonrpc": "2.0", "id": 5, "method": "prompts/list", "params": {}}

        response = client.post("/mcp", json=request)
        assert response.status_code == 200

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "prompts" in data["result"]

        prompts = data["result"]["prompts"]
        assert len(prompts) == 3

        prompt_names = [p["name"] for p in prompts]
        assert "field_analysis" in prompt_names
        assert "irrigation_plan" in prompt_names
        assert "crop_recommendation" in prompt_names

    def test_prompts_get(self, client):
        """Test prompts/get request"""
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
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "messages" in data["result"]
        assert len(data["result"]["messages"]) > 0

    def test_invalid_method(self, client):
        """Test invalid method"""
        request = {"jsonrpc": "2.0", "id": 7, "method": "invalid/method", "params": {}}

        response = client.post("/mcp", json=request)
        assert response.status_code == 500

        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "error" in data


class TestConvenienceEndpoints:
    """Test convenience endpoints"""

    def test_list_tools_endpoint(self, client):
        """Test GET /tools endpoint"""
        response = client.get("/tools")
        assert response.status_code == 200

        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 5

    def test_list_prompts_endpoint(self, client):
        """Test GET /prompts endpoint"""
        response = client.get("/prompts")
        assert response.status_code == 200

        data = response.json()
        assert "prompts" in data
        assert len(data["prompts"]) == 3


class TestMetrics:
    """Test metrics endpoint"""

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "mcp_requests_total" in response.text
