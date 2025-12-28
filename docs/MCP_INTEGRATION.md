# SAHOOL Model Context Protocol (MCP) Integration

## Overview

SAHOOL now includes full support for the **Model Context Protocol (MCP)**, enabling AI assistants like Claude to directly interact with SAHOOL's agricultural intelligence capabilities.

The MCP integration provides:
- **5 Agricultural Tools** for weather, crop health, irrigation, and fertilizer recommendations
- **3 Resource Providers** for field data, weather data, and crop catalogs
- **3 Prompt Templates** for common agricultural tasks
- **Dual Transport Support** (stdio and HTTP/SSE)
- **Production-Ready** with health checks, metrics, and logging

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Assistant                            │
│                  (Claude, ChatGPT, etc.)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol
                         │ (JSON-RPC 2.0)
┌────────────────────────▼────────────────────────────────────┐
│                   SAHOOL MCP Server                          │
│                   (Port 8200)                                │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Tool Handler │ Resource     │ Prompt Template Engine   │ │
│  │              │ Provider     │                          │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│               SAHOOL Core Services                           │
│  ┌──────────┬──────────┬──────────┬──────────────────────┐  │
│  │ Weather  │ NDVI     │ Field    │ Advisory Services    │  │
│  │ Core     │ Engine   │ Core     │ (Irrigation, Fert.)  │  │
│  └──────────┴──────────┴──────────┴──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start the MCP Server

#### Using Docker Compose

```bash
docker-compose up mcp-server
```

#### Using Python

```bash
cd apps/services/mcp-server
pip install -r requirements.txt
python src/main.py
```

The server will start on `http://localhost:8200`.

### 2. Verify Server is Running

```bash
# Health check
curl http://localhost:8200/health

# List available tools
curl http://localhost:8200/tools

# View API documentation
open http://localhost:8200/docs
```

### 3. Configure AI Assistant

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sahool": {
      "url": "http://localhost:8200/mcp",
      "name": "SAHOOL Agricultural Platform",
      "description": "Agricultural intelligence tools for Yemen and Middle East"
    }
  }
}
```

#### Using stdio Transport

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

## Available Tools

### 1. get_weather_forecast

Get weather forecast with agricultural advisories.

**Parameters:**
- `latitude` (required): Latitude of the location
- `longitude` (required): Longitude of the location
- `days` (optional): Number of days to forecast (1-14, default: 7)

**Example:**
```json
{
  "latitude": 15.5527,
  "longitude": 48.5164,
  "days": 7
}
```

**Returns:**
- Temperature, humidity, precipitation forecasts
- Wind speed and direction
- Agricultural advisories (frost risk, heat stress, etc.)
- Irrigation recommendations based on weather

### 2. analyze_crop_health

Analyze crop health using satellite imagery (NDVI/NDWI).

**Parameters:**
- `field_id` (required): Field identifier
- `analysis_type` (optional): "ndvi", "ndwi", or "full" (default: "ndvi")
- `date` (optional): Analysis date (YYYY-MM-DD)

**Example:**
```json
{
  "field_id": "field-123",
  "analysis_type": "ndvi"
}
```

**Returns:**
- NDVI average and distribution
- Health status (healthy, stressed, diseased)
- Stress area locations
- Disease risk assessment
- Recommendations

### 3. get_field_data

Retrieve comprehensive field data.

**Parameters:**
- `field_id` (required): Field identifier
- `include_history` (optional): Include historical data (default: false)
- `include_sensors` (optional): Include IoT sensor data (default: false)

**Example:**
```json
{
  "field_id": "field-123",
  "include_history": true,
  "include_sensors": true
}
```

**Returns:**
- Field boundaries (GeoJSON)
- Area in hectares
- Soil properties (type, pH, nutrients)
- Current crop information
- Historical activities (optional)
- Sensor readings (optional)

### 4. calculate_irrigation

Calculate optimal irrigation requirements.

**Parameters:**
- `field_id` (required): Field identifier
- `crop_type` (required): Type of crop
- `soil_moisture` (required): Current soil moisture (0-100%)
- `growth_stage` (required): "germination", "vegetative", "flowering", "fruiting", or "maturation"

**Example:**
```json
{
  "field_id": "field-123",
  "crop_type": "wheat",
  "soil_moisture": 45.5,
  "growth_stage": "flowering"
}
```

**Returns:**
- Water amount needed (mm)
- Duration in minutes
- Next irrigation date
- Soil moisture target
- Adjustment factors (weather, growth stage, etc.)

### 5. get_fertilizer_recommendation

Get fertilizer recommendations based on soil analysis.

**Parameters:**
- `field_id` (required): Field identifier
- `crop_type` (required): Type of crop
- `soil_test` (optional): NPK values, pH, organic matter
- `target_yield` (optional): Target yield in tons/ha

**Example:**
```json
{
  "field_id": "field-123",
  "crop_type": "corn",
  "soil_test": {
    "nitrogen_ppm": 20,
    "phosphorus_ppm": 15,
    "potassium_ppm": 150,
    "ph": 6.5,
    "organic_matter_pct": 2.5
  },
  "target_yield": 8.5
}
```

**Returns:**
- NPK recommendation (N-P-K ratios)
- Application schedule
- Total cost estimate
- Organic alternatives
- Warnings and precautions

## Resource Providers

### Field Data Resources

Access field information through URI templates:

- `field://{field_id}/info` - General field information
- `field://{field_id}/boundaries` - GeoJSON boundaries
- `field://{field_id}/soil` - Soil properties
- `field://{field_id}/activities` - Historical activities

**Example:**
```python
resource = await client.read_resource("field://field-123/boundaries")
```

### Weather Data Resources

Access weather data:

- `weather://current` - Current conditions
- `weather://forecast/7day` - 7-day forecast
- `weather://forecast/14day` - 14-day forecast
- `weather://advisories` - Agricultural advisories
- `weather://historical/30day` - 30-day history

### Crop Catalog Resources

Access crop information:

- `crops://catalog` - Complete crop catalog
- `crops://{crop_id}/info` - Crop details
- `crops://{crop_id}/growing-guide` - Growing guide
- `crops://{crop_id}/pests` - Pest management
- `crops://{crop_id}/diseases` - Disease management

## Prompt Templates

### 1. field_analysis

Comprehensive field analysis including health, weather, and recommendations.

**Arguments:**
- `field_id` (required): Field to analyze

**Usage:**
```
Use the field_analysis prompt for field-123
```

### 2. irrigation_plan

Create irrigation plan based on weather forecast and soil conditions.

**Arguments:**
- `field_id` (required): Field identifier
- `days` (optional): Planning horizon (default: 7)

**Usage:**
```
Use the irrigation_plan prompt for field-123 with 14 days
```

### 3. crop_recommendation

Recommend crops suitable for field conditions.

**Arguments:**
- `field_id` (required): Field identifier
- `season` (optional): Growing season

**Usage:**
```
Use the crop_recommendation prompt for field-123 for summer season
```

## Python Client Usage

### Basic Usage

```python
from shared.mcp.client import MCPClientContext

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

    # Calculate irrigation
    irrigation = await client.calculate_irrigation(
        field_id="field-123",
        crop_type="wheat",
        soil_moisture=45.5,
        growth_stage="flowering"
    )
```

### Low-Level API

```python
# Call tool directly
result = await client.call_tool(
    name="get_weather_forecast",
    arguments={
        "latitude": 15.5527,
        "longitude": 48.5164,
        "days": 7
    }
)

# Read resource
resource = await client.read_resource("field://field-123/info")

# Get prompt
prompt = await client.get_prompt(
    name="field_analysis",
    arguments={"field_id": "field-123"}
)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SAHOOL_API_URL` | Base URL for SAHOOL API | `http://localhost:8000` |
| `MCP_SERVER_PORT` | MCP server port | `8200` |
| `MCP_SERVER_HOST` | MCP server host | `0.0.0.0` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Docker Compose Configuration

```yaml
services:
  mcp-server:
    build: ./apps/services/mcp-server
    container_name: sahool-mcp-server
    ports:
      - "8200:8200"
    environment:
      - SAHOOL_API_URL=http://kong:8000
      - LOG_LEVEL=INFO
    depends_on:
      - kong
      - weather-core
      - ndvi-engine
      - field-core
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8200/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sahool-network
```

## Monitoring

### Health Checks

```bash
# Liveness probe
curl http://localhost:8200/health

# Readiness probe
curl http://localhost:8200/ready
```

### Metrics (Prometheus)

```bash
# View metrics
curl http://localhost:8200/metrics
```

**Available Metrics:**
- `mcp_requests_total{method, status}` - Total MCP requests
- `mcp_request_duration_seconds{method}` - Request duration
- `mcp_tool_calls_total{tool_name, status}` - Tool invocations
- `mcp_resource_reads_total{resource_type, status}` - Resource reads

### Logs

Structured JSON logs in production:

```json
{
  "timestamp": "2025-12-28T10:00:00Z",
  "level": "INFO",
  "message": "MCP Request: tools/call (id: 1)",
  "method": "tools/call",
  "tool_name": "get_weather_forecast",
  "duration": 0.234
}
```

## Security

### Authentication

MCP server currently supports:
- No authentication (development)
- API key authentication (coming soon)
- JWT authentication (coming soon)

### Rate Limiting

Configured through Kong API Gateway:
- Free tier: 30 requests/minute
- Standard: 60 requests/minute
- Premium: 120 requests/minute

### CORS

CORS is enabled for all origins in development. Configure for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

## Troubleshooting

### MCP Server Won't Start

1. Check if port 8200 is available:
   ```bash
   lsof -i :8200
   ```

2. Verify SAHOOL API is running:
   ```bash
   curl http://localhost:8000/health
   ```

3. Check logs:
   ```bash
   docker-compose logs mcp-server
   ```

### Tool Calls Failing

1. Verify SAHOOL services are running:
   ```bash
   docker-compose ps
   ```

2. Check service health:
   ```bash
   curl http://localhost:8000/api/weather/health
   curl http://localhost:8000/api/fields/health
   ```

3. Review error messages in MCP server logs

### Resources Not Loading

1. Ensure database is accessible
2. Check PostgreSQL connection
3. Verify field data exists in database

## Examples

See `shared/mcp/examples.py` for comprehensive examples:

```bash
# Run examples
python -m shared.mcp.examples
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8200/docs
- **ReDoc**: http://localhost:8200/redoc

## Support

For issues or questions:
1. Check logs: `docker-compose logs mcp-server`
2. Review documentation: `/docs/MCP_INTEGRATION.md`
3. Contact development team

## License

Proprietary - KAFAAT
