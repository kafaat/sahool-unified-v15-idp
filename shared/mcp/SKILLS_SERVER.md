# SAHOOL MCP Skills Server

Advanced skill-based tools for the SAHOOL Model Context Protocol (MCP) server, enabling AI assistants to access sophisticated agricultural intelligence and utility functions.

## Overview

The `skills_server.py` module extends the SAHOOL MCP platform with four powerful skill tools:

1. **crop_advisor** - AI-powered crop health and disease advisory
2. **farm_documentation** - Access agricultural documentation and best practices
3. **compress_context** - Optimize AI context window usage through intelligent compression
4. **query_memory** - Search and retrieve relevant farm memory and historical data

## Architecture

```
┌─────────────────────────────────────────┐
│         MCP Server                      │
├─────────────────────────────────────────┤
│  Base Tools (weather, irrigation, etc)  │
│  ─────────────────────────────────────  │
│  Skill Tools (crop_advisor, etc)        │ ← SAHOOLSkillsTools
└─────────────────────────────────────────┘
         ↓
    AI Assistants
```

## Installation & Setup

### 1. Add to Existing MCP Server

```python
from shared.mcp.server import MCPServer
from shared.mcp.skills_server import extend_mcp_server_with_skills

# Create base server
server = MCPServer()

# Extend with skill tools
server = extend_mcp_server_with_skills(server)

# Run server
await server.run_stdio()
```

### 2. Direct Skills Usage

```python
from shared.mcp.skills_server import SAHOOLSkillsTools

tools = SAHOOLSkillsTools()

# Use any skill tool
result = await tools.crop_advisor(
    field_id="field-123",
    issue_type="disease_detection"
)
```

### 3. Through MCP Client

```python
from shared.mcp.client import MCPClient

async with MCPClient(server_url="http://localhost:8200") as client:
    result = await client.call_tool(
        "crop_advisor",
        {"field_id": "field-123", "issue_type": "pest_management"}
    )
```

## Skill Tools Reference

### 1. crop_advisor

AI-powered crop advisory service providing disease detection, pest management, and optimization recommendations.

**Purpose**: Deliver personalized agricultural guidance based on field analysis, environmental conditions, and historical data.

**Parameters**:
- `field_id` (string, required): Field identifier
- `issue_type` (string, default: "general_advice"): Type of issue
  - `disease_detection`: Detect diseases from symptoms/imagery
  - `pest_management`: Pest identification and control strategies
  - `crop_stress`: Identify stress causes and solutions
  - `yield_optimization`: Maximize expected yield
  - `general_advice`: General agricultural guidance
- `include_weather` (boolean, default: true): Include weather forecast in analysis
- `include_history` (boolean, default: true): Include field history
- `confidence_threshold` (number, default: 0.7): Minimum confidence for recommendations (0-1)

**Returns**:
```json
{
  "success": true,
  "data": {
    "field_id": "field-123",
    "issue_type": "disease_detection",
    "recommendations": [
      {
        "title": "Early Blight Detection",
        "severity": "high",
        "action": "Apply fungicide treatment",
        "timeline": "within 48 hours"
      }
    ],
    "analysis": {
      "disease_risk": "high",
      "affected_area_percent": 15
    },
    "confidence_score": 0.85,
    "action_items": ["Treat affected area", "Monitor progress"],
    "urgency_level": "high"
  },
  "metadata": {
    "advisory_date": "2025-01-13T10:30:00Z",
    "ai_model": "crop-health-v2",
    "analysis_time_ms": 1234
  }
}
```

**Example**:
```python
result = await tools.crop_advisor(
    field_id="field-north-01",
    issue_type="disease_detection",
    include_weather=True,
    include_history=True,
    confidence_threshold=0.7
)
```

### 2. farm_documentation

Access comprehensive agricultural documentation including growing guides, best practices, and disease/pest management.

**Purpose**: Provide farmers and advisors with verified, authoritative information on crop management.

**Parameters**:
- `document_type` (string, required): Type of documentation
  - `growing_guide`: Complete growing instructions
  - `pest_management`: Pest identification and control
  - `disease_control`: Disease prevention and treatment
  - `best_practices`: Recommended farming practices
  - `soil_management`: Soil health and management
  - `irrigation_guide`: Irrigation scheduling and techniques
  - `fertilizer_guide`: Fertilizer selection and application
  - `harvest_guide`: Harvesting techniques
  - `storage_guide`: Post-harvest storage and handling
- `crop_type` (string, required): Crop type (e.g., "wheat", "tomatoes", "dates")
- `language` (string, default: "en"): Language for documentation
  - `en`: English
  - `ar`: Arabic
- `include_images` (boolean, default: false): Include diagrams/photos
- `search_query` (string, optional): Search within documentation

**Returns**:
```json
{
  "success": true,
  "data": {
    "document_type": "pest_management",
    "crop_type": "tomatoes",
    "title": "Tomato Pest Management Guide",
    "content": "Detailed guide content...",
    "sections": [
      {
        "title": "Common Pests",
        "subsections": [...]
      }
    ],
    "key_points": [
      "Monitor plants regularly",
      "Use integrated pest management"
    ],
    "images": [],
    "references": [
      {"title": "Research paper", "url": "..."}
    ],
    "last_updated": "2024-12-01"
  },
  "metadata": {
    "language": "en",
    "content_type": "text",
    "source": "SAHOOL Documentation"
  }
}
```

**Example**:
```python
result = await tools.farm_documentation(
    document_type="pest_management",
    crop_type="tomatoes",
    language="ar",
    include_images=True
)
```

### 3. compress_context

Optimize AI context window usage through intelligent compression of agricultural data.

**Purpose**: Reduce token consumption for large datasets while preserving critical information, enabling AI assistants to handle more comprehensive analyses.

**Parameters**:
- `data` (object, required): Data to compress (dict or list)
- `data_type` (string, default: "field"): Type of data
  - `field`: Field properties and conditions
  - `weather`: Weather forecasts and historical data
  - `history`: Operational history and activities
  - `text`: Raw text content
- `compression_strategy` (string, default: "hybrid"): Compression approach
  - `selective`: Keep only priority fields
  - `extractive`: Extract key information
  - `abstractive`: Generate summaries
  - `hybrid`: Combine approaches
- `target_ratio` (number, default: 0.3): Target compression ratio (0-1)
- `preserve_critical` (boolean, default: true): Keep critical fields

**Returns**:
```json
{
  "success": true,
  "data": {
    "original_text_preview": "Field: North Field | Area: 50 | Crop: wheat...",
    "compressed_text": "Compressed version...",
    "original_tokens": 150,
    "compressed_tokens": 45,
    "compression_ratio": 0.30,
    "tokens_saved": 105,
    "savings_percentage": 70.0,
    "strategy_used": "hybrid"
  },
  "metadata": {
    "data_type": "field",
    "preserve_critical": true,
    "compression_timestamp": "2025-01-13T10:30:00Z"
  }
}
```

**Example**:
```python
field_data = {
    "field_id": "field-123",
    "name": "North Field",
    "area": 50,
    "crop": "wheat",
    "soil": {...},
    "history": [...]
}

result = await tools.compress_context(
    data=field_data,
    data_type="field",
    compression_strategy="hybrid",
    target_ratio=0.3
)

print(f"Saved {result.data['tokens_saved']} tokens ({result.data['savings_percentage']:.1f}%)")
```

### 4. query_memory

Search and retrieve relevant farm memory entries including conversations, observations, recommendations, and historical events.

**Purpose**: Provide context-aware retrieval of past interactions and observations to support consistent and informed AI decision-making.

**Parameters**:
- `tenant_id` (string, required): Tenant identifier for data isolation
- `query` (string, required): Search query for memory retrieval
- `field_id` (string, optional): Filter by field
- `memory_types` (array of strings, default: ["conversation", "recommendation", "observation"]): Types to search
  - `conversation`: Chat history
  - `field_state`: Field status snapshots
  - `recommendation`: AI recommendations
  - `observation`: Field observations
  - `weather`: Weather events
  - `action`: User actions
  - `system`: System events
- `time_range_days` (number, default: 30): Search within last N days
- `limit` (number, default: 10): Maximum results to return
- `min_relevance` (string, default: "medium"): Minimum relevance
  - `critical`: Always include
  - `high`: Include if space
  - `medium`: Include if relevant
  - `low`: Only if requested

**Returns**:
```json
{
  "success": true,
  "data": {
    "query": "irrigation recommendations for wheat",
    "tenant_id": "tenant-001",
    "results_count": 3,
    "entries": [
      {
        "id": "mem-123",
        "timestamp": "2025-01-10T09:00:00Z",
        "memory_type": "recommendation",
        "content": "Apply 25mm irrigation...",
        "relevance": "high"
      }
    ],
    "search_filters": {
      "field_id": "field-123",
      "memory_types": ["recommendation"],
      "time_range_days": 30
    }
  },
  "metadata": {
    "query_timestamp": "2025-01-13T10:30:00Z",
    "memory_backend": "local"
  }
}
```

**Example**:
```python
result = await tools.query_memory(
    tenant_id="tenant-001",
    query="disease prevention for wheat",
    field_id="field-123",
    memory_types=["recommendation", "observation"],
    time_range_days=60,
    limit=5,
    min_relevance="high"
)

for entry in result.data["entries"]:
    print(f"{entry['memory_type']}: {entry['content'][:100]}...")
```

## Integration Examples

### Example 1: Extend Existing MCP Server

```python
from shared.mcp.server import MCPServer
from shared.mcp.skills_server import extend_mcp_server_with_skills

async def main():
    # Create base server
    server = MCPServer(name="sahool-server", version="1.0.0")

    # Add skill tools
    server = extend_mcp_server_with_skills(server)

    # Run with stdio transport
    await server.run_stdio()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Example 2: FastAPI Integration

```python
from fastapi import FastAPI
from shared.mcp.server import MCPServer
from shared.mcp.skills_server import extend_mcp_server_with_skills

async def lifespan(app: FastAPI):
    # Startup
    server = MCPServer()
    server = extend_mcp_server_with_skills(server)
    app.state.mcp_server = server
    yield
    # Shutdown
    await server.close()

app = FastAPI(lifespan=lifespan)

@app.post("/mcp")
async def handle_mcp(request: dict):
    return await app.state.mcp_server.handle_request(request)
```

### Example 3: Client Usage Pattern

```python
from shared.mcp.client import MCPClient

async def analyze_field(field_id: str):
    async with MCPClient(server_url="http://mcp-server:8200") as client:
        # Get crop advisory
        advisory = await client.call_tool(
            "crop_advisor",
            {"field_id": field_id, "issue_type": "disease_detection"}
        )

        # Get documentation
        doc = await client.call_tool(
            "farm_documentation",
            {"document_type": "best_practices", "crop_type": "wheat"}
        )

        # Compress context for analysis
        compressed = await client.call_tool(
            "compress_context",
            {"data": advisory.data, "data_type": "field"}
        )

        # Query memory for history
        history = await client.call_tool(
            "query_memory",
            {
                "tenant_id": "tenant-001",
                "query": "previous issues with this field",
                "field_id": field_id,
                "limit": 10
            }
        )

        return {
            "advisory": advisory,
            "documentation": doc,
            "compressed_size": compressed.data["compression_ratio"],
            "history": history.data["entries"]
        }
```

## Configuration

### Environment Variables

```bash
# SAHOOL API Configuration
SAHOOL_API_URL=http://localhost:8000

# Compression Settings
CONTEXT_MAX_TOKENS=4000
COMPRESSION_STRATEGY=hybrid

# Memory Configuration
MEMORY_WINDOW_SIZE=20
MEMORY_TTL_HOURS=24
MEMORY_MAX_ENTRIES=1000
```

### Programmatic Configuration

```python
from shared.mcp.skills_server import SAHOOLSkillsTools

tools = SAHOOLSkillsTools(base_url="http://api.sahool.local:8000")
```

## Error Handling

All skill tools follow a consistent error handling pattern:

```python
result = await tools.crop_advisor(field_id="field-123")

if not result.success:
    # Handle error
    error_message = result.error
    print(f"Error: {error_message}")
else:
    # Use data
    recommendations = result.data["recommendations"]
```

## Performance Considerations

### Context Compression

- **Target Ratio**: Set based on AI model context window
- **Strategy**: `hybrid` for balanced compression; `selective` for fastest
- **Token Savings**: Typically 60-80% for agricultural data

### Memory Queries

- **Batch Queries**: Combine multiple memory searches into single requests
- **Time Windows**: Use smaller `time_range_days` for faster retrieval
- **Relevance Filtering**: Set `min_relevance` higher to reduce results

### API Calls

- **Timeouts**: Default 30 seconds per request
- **Connection Pooling**: HTTP client maintains persistent connections
- **Error Retry**: Implement exponential backoff for transient failures

## Testing

Run the examples:

```bash
python -m shared.mcp.examples_skills
```

Run unit tests:

```bash
pytest tests/unit/mcp/test_skills_server.py -v
```

## Troubleshooting

### Import Errors

```python
# If context compression module not available:
# Install: pip install shared-ai-context-engineering

# Tool will gracefully degrade if optional modules unavailable
tools = SAHOOLSkillsTools()  # Still works, with reduced features
```

### API Connection Issues

```python
# Verify SAHOOL_API_URL is configured
import os
print(os.getenv("SAHOOL_API_URL", "http://localhost:8000"))

# Test connectivity
async with SAHOOLSkillsTools() as tools:
    # Client initialization handles connection pooling
    pass
```

### Memory Module Not Found

```python
# If shared.ai.context_engineering not available
result = await tools.query_memory(...)  # Falls back to API
result = await tools.compress_context(...)  # Falls back to API
```

## API Contracts

### Crop Advisor API Endpoint

```
POST /api/skills/crop-advisor
Content-Type: application/json

Request:
{
  "field_id": "string",
  "issue_type": "disease_detection|pest_management|crop_stress|yield_optimization|general_advice",
  "include_weather": boolean,
  "include_history": boolean,
  "confidence_threshold": number
}

Response:
{
  "recommendations": [...],
  "analysis": {...},
  "confidence_score": number,
  "action_items": [...],
  "urgency_level": "critical|high|normal|low"
}
```

### Documentation API Endpoint

```
GET /api/skills/documentation
Query Parameters:
  - document_type (required)
  - crop_type (required)
  - language (default: en)
  - include_images (default: false)
  - search_query (optional)

Response:
{
  "title": "string",
  "content": "string",
  "sections": [...],
  "key_points": [...],
  "references": [...]
}
```

### Memory Query API Endpoint

```
POST /api/skills/memory/query
Content-Type: application/json

Request:
{
  "tenant_id": "string",
  "query": "string",
  "field_id": "string (optional)",
  "memory_types": [...],
  "time_range": "ISO8601 duration",
  "limit": number,
  "min_relevance": "critical|high|medium|low"
}

Response:
{
  "results": [
    {
      "id": "string",
      "timestamp": "ISO8601",
      "memory_type": "string",
      "content": "string|object",
      "relevance": "string"
    }
  ]
}
```

## Related Documentation

- [MCP Server Documentation](/docs/mcp-server.md)
- [MCP Client Reference](/docs/mcp-client.md)
- [Context Engineering Guide](/docs/context-engineering.md)
- [AI Advisory Services](/docs/ai-advisory.md)

## Support & Contributing

For issues, feature requests, or contributions:

1. Check existing issues on GitHub
2. Create detailed bug reports with reproduction steps
3. Submit feature requests with use cases
4. Follow code style guidelines for contributions

## Version History

### v1.0.0 (January 2025)

- Initial release
- crop_advisor skill
- farm_documentation skill
- compress_context tool
- query_memory tool
- Full MCP integration support

## License

Proprietary - SAHOOL Platform. All rights reserved.

---

**Author**: SAHOOL Platform Team
**Updated**: January 2025
**Stability**: Stable
