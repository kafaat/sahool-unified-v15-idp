# SAHOOL MCP Server | خادم بروتوكول سياق النموذج

Model Context Protocol (MCP) server for SAHOOL agricultural platform.

خادم بروتوكول سياق النموذج (MCP) لمنصة سهول الزراعية.

## Overview

The SAHOOL MCP Server exposes all SAHOOL agricultural capabilities through the Model Context Protocol, enabling AI assistants to:

- Access agricultural tools (weather, crop health, irrigation, fertilizer)
- Query agricultural resources (fields, weather data, crop catalog)
- Use agricultural prompt templates

## Features | الميزات

- **Full MCP Specification Support**: Implements MCP 2024-11-05 specification
- **Multiple Transports**: HTTP/JSON-RPC and Server-Sent Events (SSE)
- **Production Ready**: Health checks, metrics, logging, and error handling
- **Agricultural Tools**: 5 specialized agricultural intelligence tools
- **Resource Providers**: Access to field data, weather, and crop catalogs
- **Prompt Templates**: Pre-built prompts for common agricultural tasks

---

- **دعم مواصفات MCP الكاملة**: ينفذ مواصفات MCP 2024-11-05
- **نقل متعدد**: HTTP/JSON-RPC وأحداث مرسلة من الخادم (SSE)
- **جاهز للإنتاج**: فحوصات الصحة والمقاييس وتسجيل الأخطاء والمعالجة
- **أدوات زراعية**: 5 أدوات متخصصة للذكاء الزراعي
- **موفرو الموارد**: الوصول إلى بيانات الحقول والطقس وفهارس المحاصيل
- **قوالب الرسائل**: رسائل مُعدة مسبقًا للمهام الزراعية الشائعة

## Quick Start | البدء السريع

### Development | التطوير

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SAHOOL_API_URL=http://localhost:8000
export MCP_SERVER_PORT=8200

# Run server
python src/main.py
```

### Docker | دوكر

```bash
# Build image
docker build -t sahool-mcp-server .

# Run container
docker run -p 8200:8200 \
  -e SAHOOL_API_URL=http://localhost:8000 \
  sahool-mcp-server
```

### Docker Compose | تكوين دوكر

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

## Endpoints | نقاط النهاية

### MCP Endpoints | نقاط نهاية MCP

- **POST /mcp** - JSON-RPC 2.0 endpoint for MCP requests
- **GET /mcp/sse** - Server-Sent Events endpoint for streaming

### Convenience Endpoints | نقاط النهاية المريحة

- **GET /** - Server information
- **GET /tools** - List available tools
- **GET /resources** - List available resources
- **GET /prompts** - List available prompts

### Health & Metrics | الصحة والمقاييس

- **GET /health** - Health check
- **GET /healthz** - Kubernetes health check
- **GET /ready** - Readiness probe
- **GET /metrics** - Prometheus metrics

## Available Tools | الأدوات المتاحة

### 1. get_weather_forecast | الحصول على توقعات الطقس

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

### 2. analyze_crop_health | تحليل صحة المحصول

Analyze crop health using satellite imagery (NDVI).

تحليل صحة المحصول باستخدام صور الأقمار الصناعية (NDVI).

```json
{
  "name": "analyze_crop_health",
  "arguments": {
    "field_id": "field-123",
    "analysis_type": "ndvi"
  }
}
```

### 3. get_field_data | الحصول على بيانات الحقل

Retrieve comprehensive field data.

استرجاع بيانات الحقل الشاملة.

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

### 4. calculate_irrigation | حساب متطلبات الري

Calculate optimal irrigation requirements.

حساب متطلبات الري المثلى.

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

### 5. get_fertilizer_recommendation | الحصول على توصيات الأسمدة

Get fertilizer recommendations based on soil analysis.

الحصول على توصيات الأسمدة بناءً على تحليل التربة.

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

## Resource Providers | موفرو الموارد

### Field Data Resources | موارد بيانات الحقل

- `field://{field_id}/info` - Field information
- `field://{field_id}/boundaries` - Geospatial boundaries (GeoJSON)
- `field://{field_id}/soil` - Soil properties
- `field://{field_id}/activities` - Historical activities

### Weather Data Resources | موارد بيانات الطقس

- `weather://current` - Current weather conditions
- `weather://forecast/7day` - 7-day forecast
- `weather://forecast/14day` - 14-day forecast
- `weather://advisories` - Agricultural advisories
- `weather://historical/30day` - Historical weather data

### Crop Catalog Resources | موارد فهرس المحاصيل

- `crops://catalog` - Complete crop catalog
- `crops://{crop_id}/info` - Crop information
- `crops://{crop_id}/growing-guide` - Growing guide
- `crops://{crop_id}/pests` - Pest management
- `crops://{crop_id}/diseases` - Disease management

## Prompt Templates | قوالب الرسائل

### field_analysis | تحليل الحقل

Comprehensive field analysis including health, weather, and recommendations.

تحليل شامل للحقل يشمل الصحة والطقس والتوصيات.

### irrigation_plan | خطة الري

Create irrigation plan based on weather forecast and soil conditions.

إنشاء خطة ري بناءً على توقعات الطقس وظروف التربة.

### crop_recommendation | توصية المحصول

Recommend crops suitable for field conditions.

التوصية بالمحاصيل المناسبة لظروف الحقل.

## Configuration | الإعداد

### Environment Variables | متغيرات البيئة

| Variable          | Description             | Default                 |
| ----------------- | ----------------------- | ----------------------- |
| `SAHOOL_API_URL`  | Base URL for SAHOOL API | `http://localhost:8000` |
| `MCP_SERVER_PORT` | Port to run on          | `8200`                  |
| `MCP_SERVER_HOST` | Host to bind to         | `0.0.0.0`               |
| `LOG_LEVEL`       | Logging level           | `INFO`                  |

## MCP Client Integration | تكامل عميل MCP

### Using Python Client | استخدام عميل Python

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

### Using Claude Desktop | استخدام Claude Desktop

Add to Claude Desktop configuration (`claude_desktop_config.json`):

أضفه إلى إعداد Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sahool": {
      "url": "http://localhost:8200/mcp"
    }
  }
}
```

### Using stdio Transport | استخدام نقل stdio

```bash
# Run MCP server with stdio transport
python -m shared.mcp.server --transport stdio
```

## Monitoring | المراقبة

### Prometheus Metrics | مقاييس Prometheus

- `mcp_requests_total{method, status}` - Total MCP requests
- `mcp_request_duration_seconds{method}` - Request duration histogram
- `mcp_tool_calls_total{tool_name, status}` - Total tool calls
- `mcp_resource_reads_total{resource_type, status}` - Total resource reads

### Health Checks | فحوصات الصحة

```bash
# Check health
curl http://localhost:8200/health

# Check readiness
curl http://localhost:8200/ready

# Check metrics
curl http://localhost:8200/metrics
```

## Development | التطوير

### Running Tests | تشغيل الاختبارات

```bash
pytest tests/
```

### Code Quality | جودة الكود

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Production Deployment | نشر الإنتاج

### Kubernetes | كوبرنيتس

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
