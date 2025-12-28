"""
SAHOOL MCP Client - Model Context Protocol Client Implementation
=================================================================

Client for connecting to MCP servers and invoking tools/resources.
Supports both stdio and HTTP transports.
"""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """MCP Client error"""

    pass


class ToolCall(BaseModel):
    """Tool call request"""

    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    """Tool call result"""

    content: List[Dict[str, Any]]
    isError: bool = False


class MCPClient:
    """
    Model Context Protocol Client

    Connects to MCP servers and provides methods for invoking tools
    and accessing resources.

    Supports:
    - stdio transport (subprocess)
    - HTTP transport (REST API)
    - SSE transport (Server-Sent Events)
    """

    def __init__(self, server_url: Optional[str] = None, command: Optional[List[str]] = None):
        """
        Initialize MCP Client

        Args:
            server_url: URL for HTTP/SSE transport (e.g., "http://localhost:8200")
            command: Command for stdio transport (e.g., ["python", "server.py"])
        """
        self.server_url = server_url
        self.command = command
        self.client = httpx.AsyncClient(timeout=60.0)
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.capabilities: Optional[Dict[str, Any]] = None
        self.server_info: Optional[Dict[str, Any]] = None

    def _next_request_id(self) -> int:
        """Generate next request ID"""
        self.request_id += 1
        return self.request_id

    async def close(self):
        """Close client and cleanup"""
        await self.client.aclose()
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    # ==================== Connection & Initialization ====================

    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize connection to MCP server

        Returns:
            Server capabilities and info
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "sahool-mcp-client",
                    "version": "1.0.0",
                },
            },
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"Initialize failed: {response['error']}")

        result = response.get("result", {})
        self.capabilities = result.get("capabilities", {})
        self.server_info = result.get("serverInfo", {})

        logger.info(f"Connected to {self.server_info.get('name')} v{self.server_info.get('version')}")

        return result

    # ==================== Tools ====================

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools

        Returns:
            List of tool definitions
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list",
            "params": {},
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"List tools failed: {response['error']}")

        return response.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Call a tool

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"Tool call failed: {response['error']}")

        result = response.get("result", {})
        return ToolResult(**result)

    # ==================== Resources ====================

    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources

        Returns:
            List of resource definitions
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "resources/list",
            "params": {},
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"List resources failed: {response['error']}")

        return response.get("result", {}).get("resources", [])

    async def list_resource_templates(self) -> List[Dict[str, Any]]:
        """
        List resource URI templates

        Returns:
            List of resource templates
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "resources/templates/list",
            "params": {},
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"List resource templates failed: {response['error']}")

        return response.get("result", {}).get("resourceTemplates", [])

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource

        Args:
            uri: Resource URI

        Returns:
            Resource content
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "resources/read",
            "params": {"uri": uri},
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"Read resource failed: {response['error']}")

        contents = response.get("result", {}).get("contents", [])
        return contents[0] if contents else {}

    # ==================== Prompts ====================

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List available prompt templates

        Returns:
            List of prompt definitions
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "prompts/list",
            "params": {},
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"List prompts failed: {response['error']}")

        return response.get("result", {}).get("prompts", [])

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a prompt template

        Args:
            name: Prompt name
            arguments: Prompt arguments

        Returns:
            Prompt with messages
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "prompts/get",
            "params": {
                "name": name,
                "arguments": arguments or {},
            },
        }

        response = await self._send_request(request)

        if "error" in response:
            raise MCPClientError(f"Get prompt failed: {response['error']}")

        return response.get("result", {})

    # ==================== Transport Implementations ====================

    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server"""
        if self.server_url:
            return await self._send_http_request(request)
        elif self.command:
            return await self._send_stdio_request(request)
        else:
            raise MCPClientError("No transport configured (need server_url or command)")

    async def _send_http_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request via HTTP"""
        try:
            response = await self.client.post(
                f"{self.server_url}/mcp",
                json=request,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MCPClientError(f"HTTP request failed: {str(e)}")

    async def _send_stdio_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request via stdio (not implemented in this version)"""
        raise NotImplementedError("stdio transport not implemented in async client")

    # ==================== High-level Helper Methods ====================

    async def get_weather_forecast(
        self, latitude: float, longitude: float, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather forecast (convenience method)

        Args:
            latitude: Latitude
            longitude: Longitude
            days: Number of days

        Returns:
            Weather forecast data
        """
        result = await self.call_tool(
            "get_weather_forecast",
            {
                "latitude": latitude,
                "longitude": longitude,
                "days": days,
            },
        )

        if result.isError:
            raise MCPClientError(f"Weather forecast failed: {result.content}")

        # Parse the text content
        if result.content and result.content[0].get("type") == "text":
            return json.loads(result.content[0]["text"])

        return {}

    async def analyze_crop_health(
        self, field_id: str, analysis_type: str = "ndvi"
    ) -> Dict[str, Any]:
        """
        Analyze crop health (convenience method)

        Args:
            field_id: Field ID
            analysis_type: Type of analysis

        Returns:
            Crop health analysis
        """
        result = await self.call_tool(
            "analyze_crop_health",
            {
                "field_id": field_id,
                "analysis_type": analysis_type,
            },
        )

        if result.isError:
            raise MCPClientError(f"Crop health analysis failed: {result.content}")

        if result.content and result.content[0].get("type") == "text":
            return json.loads(result.content[0]["text"])

        return {}

    async def get_field_data(
        self, field_id: str, include_history: bool = False, include_sensors: bool = False
    ) -> Dict[str, Any]:
        """
        Get field data (convenience method)

        Args:
            field_id: Field ID
            include_history: Include history
            include_sensors: Include sensors

        Returns:
            Field data
        """
        result = await self.call_tool(
            "get_field_data",
            {
                "field_id": field_id,
                "include_history": include_history,
                "include_sensors": include_sensors,
            },
        )

        if result.isError:
            raise MCPClientError(f"Get field data failed: {result.content}")

        if result.content and result.content[0].get("type") == "text":
            return json.loads(result.content[0]["text"])

        return {}

    async def calculate_irrigation(
        self, field_id: str, crop_type: str, soil_moisture: float, growth_stage: str
    ) -> Dict[str, Any]:
        """
        Calculate irrigation (convenience method)

        Args:
            field_id: Field ID
            crop_type: Crop type
            soil_moisture: Soil moisture
            growth_stage: Growth stage

        Returns:
            Irrigation calculation
        """
        result = await self.call_tool(
            "calculate_irrigation",
            {
                "field_id": field_id,
                "crop_type": crop_type,
                "soil_moisture": soil_moisture,
                "growth_stage": growth_stage,
            },
        )

        if result.isError:
            raise MCPClientError(f"Calculate irrigation failed: {result.content}")

        if result.content and result.content[0].get("type") == "text":
            return json.loads(result.content[0]["text"])

        return {}

    async def get_fertilizer_recommendation(
        self,
        field_id: str,
        crop_type: str,
        soil_test: Optional[Dict[str, float]] = None,
        target_yield: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get fertilizer recommendation (convenience method)

        Args:
            field_id: Field ID
            crop_type: Crop type
            soil_test: Soil test results
            target_yield: Target yield

        Returns:
            Fertilizer recommendation
        """
        params = {
            "field_id": field_id,
            "crop_type": crop_type,
        }
        if soil_test:
            params["soil_test"] = soil_test
        if target_yield:
            params["target_yield"] = target_yield

        result = await self.call_tool("get_fertilizer_recommendation", params)

        if result.isError:
            raise MCPClientError(f"Get fertilizer recommendation failed: {result.content}")

        if result.content and result.content[0].get("type") == "text":
            return json.loads(result.content[0]["text"])

        return {}


# ==================== Context Manager Support ====================


class MCPClientContext:
    """Context manager for MCP Client"""

    def __init__(self, *args, **kwargs):
        self.client = MCPClient(*args, **kwargs)

    async def __aenter__(self) -> MCPClient:
        await self.client.initialize()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()


# ==================== Example Usage ====================


async def example_usage():
    """Example of using MCP Client"""
    # Connect to HTTP MCP server
    async with MCPClientContext(server_url="http://localhost:8200") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t['name'] for t in tools]}")

        # Get weather forecast
        weather = await client.get_weather_forecast(latitude=15.5527, longitude=48.5164, days=7)
        print(f"Weather forecast: {weather}")

        # Analyze crop health
        health = await client.analyze_crop_health(field_id="field-123", analysis_type="ndvi")
        print(f"Crop health: {health}")

        # List resources
        resources = await client.list_resources()
        print(f"Available resources: {len(resources)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
