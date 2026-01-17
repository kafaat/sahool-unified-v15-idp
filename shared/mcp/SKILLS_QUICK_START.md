# SAHOOL Skills Server - Quick Start Guide

## 5-Minute Setup

### 1. Direct Usage

```python
from shared.mcp.skills_server import SAHOOLSkillsTools

async def demo():
    tools = SAHOOLSkillsTools()

    # Get crop advisor
    result = await tools.crop_advisor(
        field_id="field-123",
        issue_type="disease_detection"
    )
    print(result.data["recommendations"])

    await tools.close()
```

### 2. With MCP Server

```python
from shared.mcp.server import MCPServer
from shared.mcp.skills_server import extend_mcp_server_with_skills

async def main():
    server = MCPServer()
    server = extend_mcp_server_with_skills(server)
    await server.run_stdio()
```

### 3. Via MCP Client

```python
from shared.mcp.client import MCPClient

async with MCPClient(server_url="http://localhost:8200") as client:
    result = await client.call_tool(
        "crop_advisor",
        {"field_id": "field-123", "issue_type": "pest_management"}
    )
```

## Available Skills

### crop_advisor
Get AI-powered crop advisory
```python
await tools.crop_advisor(field_id="...", issue_type="disease_detection")
```

### farm_documentation
Access agricultural guides
```python
await tools.farm_documentation(
    document_type="pest_management",
    crop_type="tomatoes"
)
```

### compress_context
Reduce AI context tokens by 60-80%
```python
await tools.compress_context(
    data=field_data,
    data_type="field",
    compression_strategy="hybrid"
)
```

### query_memory
Search farm memory and history
```python
await tools.query_memory(
    tenant_id="tenant-001",
    query="irrigation for wheat",
    field_id="field-123"
)
```

## Configuration

```bash
export SAHOOL_API_URL=http://localhost:8000
```

## Files

- **skills_server.py** (29 KB): Main skills implementation
- **examples_skills.py** (13 KB): Usage examples
- **SKILLS_SERVER.md** (17 KB): Full documentation
- **SKILLS_QUICK_START.md** (this file): Quick reference

## Examples

Run all examples:
```bash
python -m shared.mcp.examples_skills
```

Run specific example:
```python
from shared.mcp.examples_skills import example_direct_skills_usage
await example_direct_skills_usage()
```

## Common Tasks

### Get Disease Recommendations
```python
result = await tools.crop_advisor(
    field_id="field-123",
    issue_type="disease_detection",
    confidence_threshold=0.7
)
# result.data["recommendations"]
```

### Reduce Context Size
```python
result = await tools.compress_context(
    data=large_field_data,
    data_type="field",
    target_ratio=0.3  # 70% reduction
)
print(f"Saved {result.data['tokens_saved']} tokens")
```

### Find Past Recommendations
```python
result = await tools.query_memory(
    tenant_id="tenant-001",
    query="wheat disease treatment",
    memory_types=["recommendation"],
    time_range_days=30,
    limit=5
)
```

### Get Growing Guide (Arabic)
```python
result = await tools.farm_documentation(
    document_type="growing_guide",
    crop_type="wheat",
    language="ar"
)
```

## Error Handling

```python
result = await tools.crop_advisor(field_id="field-123")

if result.success:
    print(result.data)
else:
    print(f"Error: {result.error}")
```

## Integration Checklist

- [ ] Install SAHOOL platform
- [ ] Set `SAHOOL_API_URL` environment variable
- [ ] Import `SAHOOLSkillsTools` or `extend_mcp_server_with_skills`
- [ ] Call skill tools
- [ ] Handle ToolResult responses

## Performance Tips

1. **Compression**: Use `hybrid` strategy for balanced compression
2. **Memory Queries**: Set `time_range_days` to recent data only
3. **API**: Runs on persistent HTTP connections
4. **Timeouts**: Default 30s per request, adjustable

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError` | Ensure shared.ai modules installed |
| `Connection refused` | Check SAHOOL_API_URL |
| `Slow responses` | Reduce `limit` in memory queries |
| `Token limit exceeded` | Use `compress_context` first |

## Next Steps

1. Read **SKILLS_SERVER.md** for full documentation
2. Run **examples_skills.py** to see all features
3. Integrate with your MCP server
4. Customize for your use case

## File Locations

```
sahool-unified-v15-idp/
└── shared/
    └── mcp/
        ├── skills_server.py           ← Main implementation
        ├── examples_skills.py         ← Usage examples
        ├── SKILLS_SERVER.md           ← Full docs
        ├── SKILLS_QUICK_START.md      ← This file
        └── __init__.py                ← Updated exports
```

## API Methods

| Method | Purpose |
|--------|---------|
| `crop_advisor()` | AI crop advisory |
| `farm_documentation()` | Agricultural guides |
| `compress_context()` | Context optimization |
| `query_memory()` | Historical data search |
| `get_tool_definitions()` | List all tools |
| `invoke_tool()` | Generic tool invocation |

## Support

- Full docs: `SKILLS_SERVER.md`
- Examples: `examples_skills.py`
- Issues: See SAHOOL platform docs
- Questions: Check example code patterns

---

**Version**: 1.0.0 | **Updated**: January 2025 | **Status**: Stable
