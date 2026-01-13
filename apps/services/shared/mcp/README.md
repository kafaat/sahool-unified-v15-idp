# SAHOOL MCP (Model Context Protocol) Module

## Overview

The `shared/mcp` module provides a complete implementation of the Model Context Protocol for SAHOOL, enabling AI assistants to interact with SAHOOL's agricultural intelligence platform.

## Architecture

```
shared/mcp/
├── __init__.py          # Package initialization and exports
├── server.py            # MCP Server implementation
├── client.py            # MCP Client implementation
├── tools.py             # Agricultural tool implementations
├── resources.py         # Resource providers (fields, weather, crops)
├── examples.py          # Usage examples
└── README.md            # This file
```

## Components

### 1. MCP Server (`server.py`)

Production-ready MCP server that handles:

- JSON-RPC 2.0 protocol
- Tool invocation
- Resource management
- Prompt templates
- Multiple transports (stdio, HTTP/SSE)

**Usage:**

```python
from shared.mcp import MCPServer

# Create server
server = MCPServer(name="sahool-mcp-server", version="1.0.0")

# Run with stdio transport
await server.run_stdio()

# Or create FastAPI app for HTTP/SSE
app = server.create_fastapi_app()
```

### 2. MCP Client (`client.py`)

Client for connecting to MCP servers:

```python
from shared.mcp import MCPClient, MCPClientContext

# Using context manager
async with MCPClientContext(server_url="http://localhost:8200") as client:
    # Get weather forecast
    weather = await client.get_weather_forecast(
        latitude=15.5527,
        longitude=48.5164,
        days=7
    )

    # Analyze crop health
    health = await client.analyze_crop_health(
        field_id="field-123",
        analysis_type="ndvi"
    )
```

### 3. Agricultural Tools (`tools.py`)

Five specialized agricultural tools:

1. **get_weather_forecast** - Weather forecasting with agricultural advisories
2. **analyze_crop_health** - Satellite-based crop health analysis (NDVI/NDWI)
3. **get_field_data** - Comprehensive field information
4. **calculate_irrigation** - Irrigation requirements calculation
5. **get_fertilizer_recommendation** - Fertilizer recommendations

**Usage:**

```python
from shared.mcp import SAHOOLTools

tools = SAHOOLTools(base_url="http://localhost:8000")

# Get tool definitions
definitions = tools.get_tool_definitions()

# Invoke a tool
result = await tools.invoke_tool(
    "get_weather_forecast",
    {
        "latitude": 15.5527,
        "longitude": 48.5164,
        "days": 7
    }
)
```

### 4. Resource Providers (`resources.py`)

Three resource providers for agricultural data:

1. **FieldDataResource** - Field boundaries, soil data, activities
2. **WeatherDataResource** - Weather forecasts and historical data
3. **CropCatalogResource** - Crop information and growing guides

**Usage:**

```python
from shared.mcp import ResourceManager

manager = ResourceManager(base_url="http://localhost:8000")

# List all resources
resources = await manager.list_all_resources()

# Get a specific resource
content = await manager.get_resource("field://field-123/info")
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements/mcp.txt
```

### 2. Start MCP Server

#### Option A: Standalone Script

```bash
python -m shared.mcp.server --transport stdio
```

#### Option B: As FastAPI Service

```bash
cd apps/services/mcp-server
python src/main.py
```

#### Option C: Docker

```bash
docker-compose up mcp-server
```

### 3. Use Client

```python
from shared.mcp import MCPClientContext

async with MCPClientContext(server_url="http://localhost:8200") as client:
    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {[t['name'] for t in tools]}")

    # Call a tool
    result = await client.get_weather_forecast(
        latitude=15.5527,
        longitude=48.5164,
        days=7
    )
    print(result)
```

## Available Tools

### get_weather_forecast

Get weather forecast for a location.

**Input:**

```python
{
    "latitude": 15.5527,
    "longitude": 48.5164,
    "days": 7
}
```

**Output:**

```python
{
    "success": True,
    "data": {
        "location": {...},
        "forecast": [...],
        "advisories": [...],
        "summary": "..."
    },
    "metadata": {...}
}
```

### analyze_crop_health

Analyze crop health using satellite imagery.

**Input:**

```python
{
    "field_id": "field-123",
    "analysis_type": "ndvi",
    "date": "2025-12-28"  # optional
}
```

**Output:**

```python
{
    "success": True,
    "data": {
        "ndvi_average": 0.75,
        "health_status": "healthy",
        "stress_areas": [...],
        "disease_risk": {...},
        "recommendations": [...]
    }
}
```

### get_field_data

Get comprehensive field data.

**Input:**

```python
{
    "field_id": "field-123",
    "include_history": True,
    "include_sensors": True
}
```

**Output:**

```python
{
    "success": True,
    "data": {
        "field_id": "field-123",
        "name": "...",
        "area_hectares": 10.5,
        "boundaries": {...},
        "soil_properties": {...},
        "current_crop": {...}
    }
}
```

### calculate_irrigation

Calculate irrigation requirements.

**Input:**

```python
{
    "field_id": "field-123",
    "crop_type": "wheat",
    "soil_moisture": 45.5,
    "growth_stage": "flowering"
}
```

**Output:**

```python
{
    "success": True,
    "data": {
        "recommendation": "...",
        "water_amount_mm": 25.0,
        "duration_minutes": 120,
        "next_irrigation_date": "2025-12-30",
        "soil_moisture_target": 60.0
    }
}
```

### get_fertilizer_recommendation

Get fertilizer recommendations.

**Input:**

```python
{
    "field_id": "field-123",
    "crop_type": "corn",
    "soil_test": {
        "nitrogen_ppm": 20,
        "phosphorus_ppm": 15,
        "potassium_ppm": 150,
        "ph": 6.5
    },
    "target_yield": 8.5
}
```

**Output:**

```python
{
    "success": True,
    "data": {
        "npk_recommendation": {...},
        "application_schedule": [...],
        "total_cost_estimate": 500.0,
        "organic_alternatives": [...],
        "warnings": [...]
    }
}
```

## Resource URIs

### Field Resources

- `field://{field_id}/info` - Field information
- `field://{field_id}/boundaries` - GeoJSON boundaries
- `field://{field_id}/soil` - Soil properties
- `field://{field_id}/activities` - Historical activities

### Weather Resources

- `weather://current` - Current conditions
- `weather://forecast/7day` - 7-day forecast
- `weather://forecast/14day` - 14-day forecast
- `weather://advisories` - Agricultural advisories
- `weather://historical/30day` - Historical data

### Crop Resources

- `crops://catalog` - Complete catalog
- `crops://{crop_id}/info` - Crop information
- `crops://{crop_id}/growing-guide` - Growing guide
- `crops://{crop_id}/pests` - Pest management
- `crops://{crop_id}/diseases` - Disease management

## Examples

See `examples.py` for comprehensive examples:

```bash
# Run all examples
python -m shared.mcp.examples
```

## Testing

```bash
# Run tests
pytest shared/mcp/tests/

# With coverage
pytest --cov=shared.mcp shared/mcp/tests/
```

## Configuration

### Environment Variables

- `SAHOOL_API_URL` - Base URL for SAHOOL API (default: `http://localhost:8000`)
- `MCP_SERVER_PORT` - Server port (default: `8200`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

## Integration with AI Assistants

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sahool": {
      "url": "http://localhost:8200/mcp"
    }
  }
}
```

### Using stdio

```json
{
  "mcpServers": {
    "sahool": {
      "command": "python",
      "args": ["-m", "shared.mcp.server", "--transport", "stdio"],
      "env": {
        "SAHOOL_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## API Reference

### Server Methods

- `handle_initialize()` - Initialize MCP connection
- `handle_tools_list()` - List available tools
- `handle_tools_call()` - Invoke a tool
- `handle_resources_list()` - List resources
- `handle_resources_read()` - Read resource content
- `handle_prompts_list()` - List prompt templates
- `handle_prompts_get()` - Get prompt template

### Client Methods

- `initialize()` - Connect to server
- `list_tools()` - Get tool list
- `call_tool(name, args)` - Call a tool
- `list_resources()` - Get resource list
- `read_resource(uri)` - Read resource
- `list_prompts()` - Get prompt list
- `get_prompt(name, args)` - Get prompt

### Tool Methods

- `get_weather_forecast(latitude, longitude, days)`
- `analyze_crop_health(field_id, analysis_type, date)`
- `get_field_data(field_id, include_history, include_sensors)`
- `calculate_irrigation(field_id, crop_type, soil_moisture, growth_stage)`
- `get_fertilizer_recommendation(field_id, crop_type, soil_test, target_yield)`

## Protocol Specification

Implements MCP specification version: **2024-11-05**

See: https://modelcontextprotocol.io/specification

## License

Proprietary - KAFAAT
