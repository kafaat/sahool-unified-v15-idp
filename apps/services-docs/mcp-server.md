# MCP Server - Model Context Protocol Service

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | mcp-server |
| **Type** | Python/FastAPI |
| **Port** | 8200 |
| **Container Name** | sahool-mcp-server |
| **Version** | 1.0.0 (Platform: 16.0.0) |
| **Description** | Model Context Protocol server exposing SAHOOL capabilities to AI assistants (Claude, ChatGPT, etc.) |
| **MCP Protocol Version** | 2024-11-05 |

## Purpose

The MCP Server implements the Model Context Protocol specification, enabling AI assistants to interact with the SAHOOL agricultural intelligence platform. It provides:

- **Tool Invocation**: Agricultural, CRM, and AI agent tools
- **Resource Access**: Read-only access to fields, farmers, weather, crops, and knowledge base
- **Prompt Templates**: Pre-built prompts for common agricultural tasks
- **Multiple Transports**: HTTP/JSON-RPC, SSE (Server-Sent Events), and stdio
- **Bilingual Support**: Full Arabic and English support

---

## API Endpoints

### Health & Monitoring Endpoints

| Endpoint | Method | Description | Response Schema |
|----------|--------|-------------|-----------------|
| `/health` | GET | Health check | `{ status, service, version, timestamp, mcp_server }` |
| `/healthz` | GET | Kubernetes liveness probe (alias of /health) | `{ status, service, version, timestamp, mcp_server }` |
| `/ready` | GET | Readiness probe | `{ status, service, version, checks }` |
| `/readyz` | GET | Kubernetes readiness probe (alias of /ready) | `{ status, service, version, checks }` |
| `/metrics` | GET | Prometheus metrics | Prometheus text format |

#### Health Response Schema

```json
{
  "status": "healthy",
  "service": "mcp-server",
  "version": "1.0.0",
  "timestamp": "2026-01-25T10:30:00.000Z",
  "mcp_server": {
    "name": "sahool-mcp-server",
    "version": "1.0.0"
  }
}
```

#### Readiness Response Schema

```json
{
  "status": "ready",
  "service": "mcp-server",
  "version": "16.0.0",
  "checks": {
    "service": "ready"
  }
}
```

### MCP Protocol Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server information and available endpoints |
| `/mcp` | POST | JSON-RPC 2.0 endpoint for MCP requests |
| `/mcp/sse` | GET | Server-Sent Events for streaming MCP |

### Convenience Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tools` | GET | List all available tools |
| `/resources` | GET | List all available resources |
| `/prompts` | GET | List all available prompts |

---

## MCP JSON-RPC Methods

### Core Protocol Methods

| Method | Description | Request Params | Response |
|--------|-------------|----------------|----------|
| `initialize` | Initialize MCP session | `{ protocolVersion, capabilities, clientInfo }` | Server capabilities and info |
| `tools/list` | List available tools | `{}` | `{ tools: Tool[] }` |
| `tools/call` | Invoke a tool | `{ name, arguments }` | `{ content, isError }` |
| `resources/list` | List available resources | `{}` | `{ resources: Resource[] }` |
| `resources/templates/list` | List resource URI templates | `{}` | `{ resourceTemplates: Template[] }` |
| `resources/read` | Read a resource | `{ uri }` | `{ contents: Content[] }` |
| `prompts/list` | List prompt templates | `{}` | `{ prompts: Prompt[] }` |
| `prompts/get` | Get prompt with arguments | `{ name, arguments }` | `{ description, messages }` |

### JSON-RPC Request Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### JSON-RPC Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [...]
  }
}
```

### JSON-RPC Error Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "message_ar": "خطأ داخلي",
    "data": "Error details"
  }
}
```

---

## Available Tools (14 Total)

### Agricultural Tools (5)

#### 1. `fetch_field_data` / `get_field_data`

Retrieve comprehensive field data including boundaries, soil properties, crop information, sensor data, and historical activities.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "field_id": { "type": "string", "description": "Unique identifier for the field" },
    "include_history": { "type": "boolean", "default": false },
    "include_sensors": { "type": "boolean", "default": false },
    "language": { "type": "string", "enum": ["en", "ar", "both"], "default": "both" }
  },
  "required": ["field_id"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "field_id": "field-123",
    "name": "North Field",
    "name_ar": "الحقل الشمالي",
    "area_hectares": 10.5,
    "boundaries": {},
    "soil_properties": {},
    "current_crop": {},
    "history": [],
    "sensors": [],
    "location": {},
    "irrigation_type": "drip"
  },
  "metadata": {
    "last_updated": "2026-01-25T10:00:00Z",
    "owner": "farmer-001",
    "language": "both"
  }
}
```

#### 2. `analyze_crop_health`

Analyze crop health using satellite imagery and NDVI analysis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "field_id": { "type": "string" },
    "analysis_type": { "type": "string", "enum": ["ndvi", "ndwi", "lai", "full"], "default": "ndvi" },
    "date": { "type": "string", "description": "YYYY-MM-DD format" },
    "include_recommendations": { "type": "boolean", "default": true }
  },
  "required": ["field_id"]
}
```

#### 3. `get_weather_forecast`

Get weather forecast for a specific location.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "latitude": { "type": "number", "minimum": -90, "maximum": 90 },
    "longitude": { "type": "number", "minimum": -180, "maximum": 180 },
    "field_id": { "type": "string", "description": "Alternative to lat/lon" },
    "days": { "type": "integer", "default": 7, "minimum": 1, "maximum": 14 },
    "include_advisories": { "type": "boolean", "default": true }
  },
  "required": []
}
```

#### 4. `irrigation_recommendation` / `calculate_irrigation`

Calculate optimal irrigation requirements.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "field_id": { "type": "string" },
    "crop_type": { "type": "string" },
    "soil_moisture": { "type": "number", "minimum": 0, "maximum": 100 },
    "growth_stage": {
      "type": "string",
      "enum": ["germination", "vegetative", "tillering", "flowering", "fruiting", "maturation"]
    },
    "irrigation_system": {
      "type": "string",
      "enum": ["drip", "sprinkler", "flood", "pivot"],
      "default": "drip"
    }
  },
  "required": ["field_id", "crop_type"]
}
```

#### 5. `fertilizer_recommendation` / `get_fertilizer_recommendation`

Get fertilizer recommendations based on soil analysis and crop requirements.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "field_id": { "type": "string" },
    "crop_type": { "type": "string" },
    "soil_test": {
      "type": "object",
      "properties": {
        "nitrogen_ppm": { "type": "number" },
        "phosphorus_ppm": { "type": "number" },
        "potassium_ppm": { "type": "number" },
        "ph": { "type": "number" },
        "organic_matter_pct": { "type": "number" }
      }
    },
    "target_yield": { "type": "number", "description": "tons/ha" },
    "growth_stage": { "type": "string" }
  },
  "required": ["field_id", "crop_type"]
}
```

### Farmer CRM Tools (3)

#### 6. `get_farmer_info`

Retrieve farmer profile information.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "farmer_id": { "type": "string" },
    "include_farms": { "type": "boolean", "default": true },
    "include_preferences": { "type": "boolean", "default": true },
    "include_interaction_history": { "type": "boolean", "default": false }
  },
  "required": ["farmer_id"]
}
```

#### 7. `log_interaction`

Log an interaction with a farmer.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "farmer_id": { "type": "string" },
    "interaction_type": {
      "type": "string",
      "enum": ["advisory", "query", "complaint", "feedback", "follow_up", "training"]
    },
    "channel": {
      "type": "string",
      "enum": ["app", "phone", "sms", "whatsapp", "field_visit", "ai_chat"],
      "default": "ai_chat"
    },
    "summary": { "type": "string" },
    "summary_ar": { "type": "string" },
    "advisory_given": { "type": "string" },
    "farmer_response": { "type": "string" },
    "follow_up_required": { "type": "boolean", "default": false },
    "follow_up_date": { "type": "string" },
    "field_id": { "type": "string" },
    "tags": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["farmer_id", "interaction_type", "summary"]
}
```

#### 8. `get_recommendations_history`

Get history of recommendations given to a farmer.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "farmer_id": { "type": "string" },
    "field_id": { "type": "string" },
    "recommendation_type": {
      "type": "string",
      "enum": ["irrigation", "fertilizer", "pest_control", "disease_treatment", "planting", "harvest", "general"]
    },
    "days": { "type": "integer", "default": 30, "minimum": 1, "maximum": 365 },
    "include_outcomes": { "type": "boolean", "default": true },
    "limit": { "type": "integer", "default": 20, "minimum": 1, "maximum": 100 }
  },
  "required": ["farmer_id"]
}
```

### AI Agent Tools (4)

#### 9. `spawn_agent`

Create a specialized AI agent for agricultural tasks.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "agent_type": {
      "type": "string",
      "enum": [
        "crop_advisor",
        "irrigation_specialist",
        "pest_management",
        "soil_analyst",
        "weather_analyst",
        "farm_planner",
        "general_assistant"
      ]
    },
    "context": {
      "type": "object",
      "properties": {
        "field_id": { "type": "string" },
        "farmer_id": { "type": "string" },
        "crop_type": { "type": "string" },
        "custom_instructions": { "type": "string" },
        "language_preference": { "type": "string", "enum": ["en", "ar", "both"] }
      }
    },
    "model": { "type": "string", "default": "claude-3-sonnet" },
    "timeout_seconds": { "type": "integer", "default": 300, "minimum": 60, "maximum": 3600 }
  },
  "required": ["agent_type"]
}
```

#### 10. `query_agent`

Send a query to a spawned AI agent.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "agent_id": { "type": "string" },
    "query": { "type": "string" },
    "additional_context": { "type": "object" },
    "include_sources": { "type": "boolean", "default": true },
    "response_format": { "type": "string", "enum": ["text", "structured", "actionable"], "default": "text" }
  },
  "required": ["agent_id", "query"]
}
```

#### 11. `get_agent_status`

Check the status of a spawned AI agent.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "agent_id": { "type": "string" },
    "include_metrics": { "type": "boolean", "default": true }
  },
  "required": ["agent_id"]
}
```

#### 12. `terminate_agent` (Internal)

Terminate a spawned AI agent.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "agent_id": { "type": "string" }
  },
  "required": ["agent_id"]
}
```

---

## Resource Providers

### Resource URI Templates

| URI Template | Provider | Description |
|--------------|----------|-------------|
| `field://{field_id}/{resource_type}` | FieldDataResource | Field data, boundaries, soil, sensors, activities, health |
| `farmer://{farmer_id}/{resource_type}` | FarmerDataResource | Profile, farms, preferences, interactions, recommendations |
| `weather://{resource_type}` | WeatherDataResource | Current, forecast, advisories, historical, alerts |
| `crops://{crop_id}/{resource_type}` | CropCatalogResource | Info, growing-guide, pests, diseases, varieties |
| `knowledge://{topic}/{subtopic}` | KnowledgeBaseResource | Documentation, guides, best practices |

### Field Resources

| URI | Description |
|-----|-------------|
| `field://{field_id}/info` | General field information |
| `field://{field_id}/boundaries` | GeoJSON boundaries (MIME: application/geo+json) |
| `field://{field_id}/soil` | Soil properties and tests |
| `field://{field_id}/sensors` | IoT sensor data |
| `field://{field_id}/activities` | Historical activities |
| `field://{field_id}/health` | Crop health metrics and NDVI |

### Farmer Resources

| URI | Description |
|-----|-------------|
| `farmer://{farmer_id}/profile` | Farmer profile information |
| `farmer://{farmer_id}/farms` | List of farms |
| `farmer://{farmer_id}/preferences` | Farmer preferences |
| `farmer://{farmer_id}/interactions` | Interaction history |
| `farmer://{farmer_id}/recommendations` | Recommendation history |

### Weather Resources

| URI | Description |
|-----|-------------|
| `weather://current` | Current weather conditions |
| `weather://forecast/7day` | 7-day weather forecast |
| `weather://forecast/14day` | 14-day weather forecast |
| `weather://advisories` | Agricultural weather advisories |
| `weather://historical/30day` | 30-day historical data |
| `weather://alerts` | Active weather alerts |

### Crop Catalog Resources

| URI | Description |
|-----|-------------|
| `crops://catalog` | Complete crop catalog |
| `crops://{crop_id}/info` | Crop information |
| `crops://{crop_id}/growing-guide` | Growing guide |
| `crops://{crop_id}/pests` | Pest management |
| `crops://{crop_id}/diseases` | Disease management |
| `crops://{crop_id}/varieties` | Crop varieties |

### Knowledge Base Topics

| Topic | Subtopics |
|-------|-----------|
| `irrigation` | guide, drip, sprinkler, scheduling, efficiency |
| `soil` | management, testing, amendments, health |
| `fertilizer` | guide, npk, organic, timing, methods |
| `pest-control` | ipm, biological, chemical, prevention |
| `disease-management` | identification, prevention, treatment, fungal, bacterial, viral |
| `organic` | certification, practices, inputs, marketing |
| `globalgap` | compliance, audit, documentation, traceability |
| `harvest` | timing, techniques, storage, quality |
| `climate` | heat-stress, drought, frost, resilience |

---

## Prompt Templates

| Prompt Name | Description | Required Arguments |
|-------------|-------------|--------------------|
| `field_analysis` | Comprehensive field analysis including health, weather, and recommendations | `field_id` |
| `irrigation_plan` | Create irrigation plan based on weather forecast and soil conditions | `field_id`, optional: `days` |
| `crop_recommendation` | Recommend crops suitable for field conditions | `field_id`, optional: `season` |
| `farmer_advisory` | Generate personalized advisory for a farmer | `farmer_id`, optional: `topic` |
| `pest_diagnosis` | Diagnose pest or disease issues based on symptoms | `field_id`, `symptoms`, optional: `crop_type` |

---

## NATS Events

**Note:** The mcp-server does NOT directly publish or subscribe to NATS events. It communicates with other SAHOOL services via HTTP REST APIs through the Kong gateway.

---

## Prometheus Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `mcp_requests_total` | Counter | method, status | Total number of MCP requests |
| `mcp_request_duration_seconds` | Histogram | method | MCP request duration |
| `mcp_tool_calls_total` | Counter | tool_name, status | Total number of tool calls |
| `mcp_resource_reads_total` | Counter | resource_type, status | Total number of resource reads |

---

## Environment Variables

### Required

| Variable | Description | Default |
|----------|-------------|---------|
| `SAHOOL_API_URL` | Base URL for SAHOOL API (Kong gateway) | `http://localhost:8000` |
| `MCP_SERVER_PORT` | Port to run on | `8200` |
| `MCP_SERVER_HOST` | Host to bind to | `0.0.0.0` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `ENVIRONMENT` | Environment (development, staging, production) | `development` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000,...` |
| `MCP_HOST` | Alternative host binding | `0.0.0.0` |
| `MCP_PORT` | Alternative port | `8200` |
| `MCP_TRANSPORT` | Transport type (stdio, http, sse) | `http` |
| `MCP_DEBUG` | Enable debug mode | `false` |
| `MCP_CORS_ORIGINS` | MCP-specific CORS origins | `*` |
| `MCP_DEFAULT_TIMEOUT` | Default request timeout (seconds) | `30` |
| `MCP_LONG_TIMEOUT` | Long operation timeout (seconds) | `120` |
| `MCP_MAX_AGENTS` | Maximum concurrent agents | `10` |
| `MCP_AGENT_TIMEOUT` | Agent timeout (seconds) | `300` |
| `MCP_AGENT_CLEANUP_INTERVAL` | Agent cleanup interval (seconds) | `60` |
| `MCP_DEFAULT_MODEL` | Default AI model | `claude-3-sonnet` |
| `MCP_DEFAULT_LANGUAGE` | Default response language | `en` |
| `MCP_BILINGUAL` | Enable bilingual output | `true` |
| `MCP_RATE_LIMIT_TIER` | Rate limit tier (free, standard, premium, internal) | `standard` |
| `JWT_SECRET_KEY` | JWT secret for authentication | (empty) |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRY_MINUTES` | JWT token expiry | `60` |
| `OLLAMA_BASE_URL` | Ollama server URL for local LLM | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `codellama:7b` |
| `RELOAD` | Enable uvicorn auto-reload | `false` |

### Service URLs (for direct service communication)

| Variable | Description | Default |
|----------|-------------|---------|
| `FIELD_SERVICE_URL` | Field Management Service URL | `http://field-management-service:3000` |
| `WEATHER_SERVICE_URL` | Weather Service URL | `http://weather-service:8092` |
| `CROP_INTELLIGENCE_URL` | Crop Intelligence Service URL | `http://crop-intelligence-service:8095` |
| `IRRIGATION_SERVICE_URL` | Irrigation Smart Service URL | `http://irrigation-smart:8094` |
| `ADVISORY_SERVICE_URL` | Advisory Service URL | `http://advisory-service:8093` |
| `USER_SERVICE_URL` | User Service URL | `http://user-service:3025` |
| `NOTIFICATION_SERVICE_URL` | Notification Service URL | `http://notification-service:8110` |

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.126.0 | Web framework |
| `starlette` | >=0.49.1 | ASGI toolkit |
| `uvicorn[standard]` | 0.27.0 | ASGI server |
| `pydantic` | 2.9.2 | Data validation |
| `httpx` | 0.28.1 | Async HTTP client |
| `python-dotenv` | 1.0.1 | Environment management |
| `prometheus-client` | 0.21.1 | Prometheus metrics |
| `structlog` | 24.4.0 | Structured logging |
| `python-jose[cryptography]` | 3.4.0 | JWT authentication |
| `passlib[bcrypt]` | 1.7.4 | Password hashing |

### Shared Module Dependencies

The service relies on these shared modules from `shared/mcp/`:

| Module | Purpose |
|--------|---------|
| `shared.mcp.server` | MCPServer, JSONRPCRequest, JSONRPCResponse |
| `shared.mcp.tools` | SAHOOLTools, ToolResult, AgentInstance |
| `shared.mcp.resources` | ResourceManager, Resource providers |
| `shared.mcp.config` | MCPConfig, environment configuration |
| `shared.mcp.client` | MCPClient for testing |

### Optional Dependencies (imported with fallback)

| Module | Purpose |
|--------|---------|
| `shared.middleware` | RequestLoggingMiddleware, TenantContextMiddleware, setup_cors |
| `shared.observability.middleware` | ObservabilityMiddleware |
| `shared.errors_py` | Unified error handling |

---

## Service Dependencies

| Dependency | Type | Required | Purpose |
|------------|------|----------|---------|
| `kong` | Gateway | Yes | API Gateway for routing |
| `postgres` | Database | Yes (healthcheck) | Database connectivity check |
| `nats` | Messaging | Yes (healthcheck) | NATS connectivity check |

---

## Docker Configuration

### Build Context

```dockerfile
FROM python:3.11-slim-bookworm
WORKDIR /app

# Non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install dependencies
COPY apps/services/mcp-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules and service code
COPY shared/ /app/shared/
COPY apps/services/mcp-server/src/ /app/src/

ENV PYTHONPATH=/app
USER sahool
EXPOSE 8200

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8200"]
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

### Healthcheck

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8200/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 15s
```

---

## Kong Gateway Routes

| Route | Target | Strip Path |
|-------|--------|------------|
| `/api/v1/mcp` | mcp-server:8200 | true |
| `/mcp` | mcp-server:8200 | true |

---

## Bugs, Issues, and Recommendations

### 1. **CRITICAL: Version Mismatch**

**Location:** `src/main.py` lines 169, 185 vs line 132

**Issue:** The `/health` endpoint returns version `"1.0.0"` while `/ready` returns `"16.0.0"`. This inconsistency can cause confusion in monitoring.

**Recommendation:** Standardize version to `"16.0.0"` across all endpoints to match the platform version.

```python
# Current (inconsistent):
@app.get("/health")
async def health():
    return {
        "version": "1.0.0",  # Should be "16.0.0"
        ...
    }

@app.get("/ready")
async def ready():
    return {
        "version": "16.0.0",  # Correct
        ...
    }
```

### 2. **MEDIUM: Missing NATS Integration**

**Location:** `src/main.py`, `shared/mcp/`

**Issue:** The service does not implement NATS event publishing/subscribing, despite NATS being listed as a dependency in docker-compose. The service relies solely on synchronous HTTP calls.

**Recommendation:** Consider implementing NATS event publication for tool invocations and agent activities to improve observability and enable event-driven architecture patterns:
- Publish events on `sahool.mcp.tool.called`
- Publish events on `sahool.mcp.agent.spawned`
- Publish events on `sahool.mcp.resource.read`

### 3. **LOW: Deprecated datetime.utcnow() Usage**

**Location:** `src/main.py` line 170, `shared/mcp/tools.py` multiple lines

**Issue:** `datetime.utcnow()` is deprecated in Python 3.12+. Should use `datetime.now(timezone.utc)` instead.

**Recommendation:**
```python
# Change from:
from datetime import datetime
datetime.utcnow()

# To:
from datetime import datetime, timezone
datetime.now(timezone.utc)
```

### 4. **MEDIUM: Missing Authentication Middleware**

**Location:** `src/main.py`

**Issue:** While JWT configuration is loaded via `MCPConfig`, no authentication middleware is actually applied to the MCP endpoints. The config warns about missing `JWT_SECRET_KEY` but doesn't enforce authentication.

**Recommendation:** Add authentication middleware for production deployment:
```python
# Add auth middleware for protected endpoints
from shared.auth.dependencies import get_current_user

@app.post("/mcp")
async def handle_mcp_request(
    request: Request,
    user: User = Depends(get_current_user)
):
    ...
```

### 5. **LOW: Error Status Code Inconsistency**

**Location:** `src/main.py` lines 270-273, 287-290

**Issue:** The MCP endpoint returns HTTP 500 for JSON-RPC errors. According to JSON-RPC 2.0 spec, HTTP status should be 200 even for JSON-RPC errors (error is in the response body).

**Recommendation:** Always return HTTP 200 for properly formed JSON-RPC requests:
```python
return JSONResponse(
    content=json.loads(response.json()),
    status_code=200,  # Always 200 for JSON-RPC
)
```

### 6. **LOW: Missing Request Validation**

**Location:** `src/main.py` lines 228-241

**Issue:** The JSON-RPC request is not validated for required fields (`jsonrpc`, `method`) before processing.

**Recommendation:** Add validation for JSON-RPC 2.0 compliance:
```python
if data.get("jsonrpc") != "2.0":
    return JSONResponse(
        content={"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}},
        status_code=200
    )
```

### 7. **INFO: Agent Expiration Time Calculation Bug**

**Location:** `shared/mcp/tools.py` lines 1209-1211

**Issue:** The agent expiration time calculation is incorrect:
```python
datetime.utcnow().replace(second=datetime.utcnow().second + timeout_seconds)
```
This will fail if `second + timeout_seconds > 59`.

**Recommendation:**
```python
from datetime import timedelta
expires_at = (datetime.utcnow() + timedelta(seconds=timeout_seconds)).isoformat()
```

### 8. **MEDIUM: Missing Agent Cleanup Background Task**

**Location:** `shared/mcp/tools.py`

**Issue:** While `MCP_AGENT_CLEANUP_INTERVAL` is configurable, no background task is implemented to clean up expired agents. Agents accumulate until the pool limit is reached.

**Recommendation:** Add a background task to periodically clean up expired agents:
```python
async def cleanup_expired_agents():
    async with self._agent_lock:
        now = datetime.utcnow()
        expired = [
            aid for aid, agent in self._agents.items()
            if (now - agent.last_active).total_seconds() > self.config.agent.agent_timeout_seconds
        ]
        for aid in expired:
            del self._agents[aid]
```

### 9. **INFO: Missing OpenAPI/Swagger Documentation**

**Location:** `src/main.py`

**Issue:** The FastAPI app is created but no detailed OpenAPI schema descriptions are provided for the endpoints.

**Recommendation:** Add response_model and description parameters to endpoints for better auto-generated documentation.

### 10. **LOW: HTTP Client Not Closed on Startup Failure**

**Location:** `shared/mcp/tools.py`, `shared/mcp/resources.py`

**Issue:** If an exception occurs during initialization, the httpx client may not be properly closed.

**Recommendation:** Ensure proper cleanup in all resource providers' `__init__` methods.

---

## Testing

### Running Tests

```bash
cd apps/services/mcp-server
pytest tests/ -v
```

### Test Coverage

The test suite covers:
- Health endpoint responses
- MCP protocol initialization
- Tools listing and verification (5 agricultural tools expected)
- Resources templates listing (3 templates expected)
- Prompts listing and retrieval (3 prompts expected)
- Invalid method handling
- Metrics endpoint

### Test Import Path Issue

**Location:** `tests/test_mcp_server.py` line 15

**Issue:** Test imports use underscore notation `mcp_server` but directory uses dash `mcp-server`:
```python
from apps.services.mcp_server.src.main import app  # Incorrect path
```

**Recommendation:** Ensure proper Python package naming or update import paths.

---

## Usage Examples

### Initialize MCP Session

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8200/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "my-client", "version": "1.0.0"}
            }
        }
    )
```

### Get Weather Forecast

```python
response = await client.post(
    "http://localhost:8200/mcp",
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_weather_forecast",
            "arguments": {
                "latitude": 15.5527,
                "longitude": 48.5164,
                "days": 7
            }
        }
    }
)
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "sahool": {
      "url": "http://localhost:8200/mcp"
    }
  }
}
```

### Python Client Usage

```python
from shared.mcp.client import MCPClientContext

async with MCPClientContext(server_url="http://localhost:8200") as client:
    tools = await client.list_tools()
    weather = await client.get_weather_forecast(latitude=15.5527, longitude=48.5164, days=7)
    health = await client.analyze_crop_health(field_id="field-123", analysis_type="ndvi")
```

---

## Security Considerations

1. **Non-Root User**: Container runs as non-privileged `sahool` user (UID 1000)
2. **Security Options**: `no-new-privileges:true` prevents privilege escalation
3. **CORS Configuration**: Environment-based allowed origins (not wildcard in production)
4. **JWT Support**: Configuration ready for JWT authentication (currently not enforced)
5. **CVE Fixes**: `python-jose` updated to 3.4.0 to address CVE-2024-33663 and CVE-2024-33664

---

## Related Services

| Service | Relationship |
|---------|--------------|
| `field-management-service` | Field data source |
| `weather-service` | Weather data source |
| `crop-intelligence-service` | Crop health analysis |
| `irrigation-smart` | Irrigation calculations |
| `advisory-service` | Agricultural recommendations |
| `user-service` | Farmer/user data |
| `notification-service` | Notification delivery |

---

*Last Updated: 2026-01-25*
