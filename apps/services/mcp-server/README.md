# SAHOOL MCP Server

Model Context Protocol (MCP) server for SAHOOL agricultural platform.

## Overview

The SAHOOL MCP Server exposes all SAHOOL agricultural capabilities through the Model Context Protocol, enabling AI assistants to:

- Access agricultural tools (weather, crop health, irrigation, fertilizer)
- Query agricultural resources (fields, weather data, crop catalog)
- Use agricultural prompt templates

## Features

- **Full MCP Specification Support**: Implements MCP 2024-11-05 specification
- **Multiple Transports**: HTTP/JSON-RPC and Server-Sent Events (SSE)
- **Production Ready**: Health checks, metrics, logging, and error handling
- **Agricultural Tools**: 5 specialized agricultural intelligence tools
- **Resource Providers**: Access to field data, weather, and crop catalogs
- **Prompt Templates**: Pre-built prompts for common agricultural tasks

## Quick Start

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SAHOOL_API_URL=http://localhost:8000
export MCP_SERVER_PORT=8200

# Run server
python src/main.py
```

### Docker

```bash
# Build image
docker build -t sahool-mcp-server .

# Run container
docker run -p 8200:8200 \
  -e SAHOOL_API_URL=http://localhost:8000 \
  sahool-mcp-server
```

### Docker Compose

```yaml
services:
  mcp-server:
    build: ./apps/services/mcp-server
    ports:
      - "8200:8200"
    environment:
      - SAHOOL_API_URL=http://localhost:8000
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8200/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Endpoints

### MCP Endpoints

- **POST /mcp** - JSON-RPC 2.0 endpoint for MCP requests
- **GET /mcp/sse** - Server-Sent Events endpoint for streaming

### Convenience Endpoints

- **GET /** - Server information
- **GET /tools** - List available tools
- **GET /resources** - List available resources
- **GET /prompts** - List available prompts

### Health & Metrics

- **GET /health** - Health check
- **GET /healthz** - Kubernetes health check
- **GET /ready** - Readiness probe
- **GET /metrics** - Prometheus metrics

## Available Tools

### 1. get_weather_forecast

Get weather forecast for a specific location.

```json
{
  "name": "get_weather_forecast",
  "arguments": {
    "latitude": 15.5527,
    "longitude": 48.5164,
    "days": 7
  }
}
```

### 2. analyze_crop_health

Analyze crop health using satellite imagery (NDVI).

```json
{
  "name": "analyze_crop_health",
  "arguments": {
    "field_id": "field-123",
    "analysis_type": "ndvi"
  }
}
```

### 3. get_field_data

Retrieve comprehensive field data.

```json
{
  "name": "get_field_data",
  "arguments": {
    "field_id": "field-123",
    "include_history": true,
    "include_sensors": true
  }
}
```

### 4. calculate_irrigation

Calculate optimal irrigation requirements.

```json
{
  "name": "calculate_irrigation",
  "arguments": {
    "field_id": "field-123",
    "crop_type": "wheat",
    "soil_moisture": 45.5,
    "growth_stage": "flowering"
  }
}
```

### 5. get_fertilizer_recommendation

Get fertilizer recommendations based on soil analysis.

```json
{
  "name": "get_fertilizer_recommendation",
  "arguments": {
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
}
```

## Resource Providers

### Field Data Resources

- `field://{field_id}/info` - Field information
- `field://{field_id}/boundaries` - Geospatial boundaries (GeoJSON)
- `field://{field_id}/soil` - Soil properties
- `field://{field_id}/activities` - Historical activities

### Weather Data Resources

- `weather://current` - Current weather conditions
- `weather://forecast/7day` - 7-day forecast
- `weather://forecast/14day` - 14-day forecast
- `weather://advisories` - Agricultural advisories
- `weather://historical/30day` - Historical weather data

### Crop Catalog Resources

- `crops://catalog` - Complete crop catalog
- `crops://{crop_id}/info` - Crop information
- `crops://{crop_id}/growing-guide` - Growing guide
- `crops://{crop_id}/pests` - Pest management
- `crops://{crop_id}/diseases` - Disease management

## Prompt Templates

### field_analysis

Comprehensive field analysis including health, weather, and recommendations.

### irrigation_plan

Create irrigation plan based on weather forecast and soil conditions.

### crop_recommendation

Recommend crops suitable for field conditions.

## Configuration

### Environment Variables

| Variable          | Description             | Default                 |
| ----------------- | ----------------------- | ----------------------- |
| `SAHOOL_API_URL`  | Base URL for SAHOOL API | `http://localhost:8000` |
| `MCP_SERVER_PORT` | Port to run on          | `8200`                  |
| `MCP_SERVER_HOST` | Host to bind to         | `0.0.0.0`               |
| `LOG_LEVEL`       | Logging level           | `INFO`                  |

## MCP Client Integration

### Using Python Client

```python
from shared.mcp.client import MCPClientContext

async with MCPClientContext(server_url="http://localhost:8200") as client:
    # List tools
    tools = await client.list_tools()

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

### Using Claude Desktop

Add to Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sahool": {
      "url": "http://localhost:8200/mcp"
    }
  }
}
```

### Using stdio Transport

```bash
# Run MCP server with stdio transport
python -m shared.mcp.server --transport stdio
```

## Monitoring

### Prometheus Metrics

- `mcp_requests_total{method, status}` - Total MCP requests
- `mcp_request_duration_seconds{method}` - Request duration histogram
- `mcp_tool_calls_total{tool_name, status}` - Total tool calls
- `mcp_resource_reads_total{resource_type, status}` - Total resource reads

### Health Checks

```bash
# Check health
curl http://localhost:8200/health

# Check readiness
curl http://localhost:8200/ready

# Check metrics
curl http://localhost:8200/metrics
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Production Deployment

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
        - name: mcp-server
          image: sahool-mcp-server:1.0.0
          ports:
            - containerPort: 8200
          env:
            - name: SAHOOL_API_URL
              value: "http://kong:8000"
          livenessProbe:
            httpGet:
              path: /health
              port: 8200
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8200
            initialDelaySeconds: 5
            periodSeconds: 10
```

## License

Proprietary - KAFAAT
