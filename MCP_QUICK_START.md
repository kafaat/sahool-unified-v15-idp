# SAHOOL MCP Integration - Quick Start Guide

## What is MCP?

The **Model Context Protocol (MCP)** is an open protocol that enables AI assistants (like Claude, ChatGPT) to securely interact with external systems and data sources. SAHOOL's MCP integration exposes agricultural intelligence capabilities to AI assistants.

## 🚀 Quick Start (3 Steps)

### Step 1: Start SAHOOL with MCP

```bash
# Clone repository
git clone https://github.com/kafaat/sahool-unified-v15-idp
cd sahool-unified-v15-idp

# Copy environment file
cp .env.example .env

# Edit .env and set required passwords:
# POSTGRES_PASSWORD=your-secure-password
# REDIS_PASSWORD=your-secure-password

# Start all services including MCP server
docker-compose up -d

# Verify MCP server is running
curl http://localhost:8200/health
```

**Expected Output:**

```json
{
  "status": "healthy",
  "service": "mcp-server",
  "version": "1.0.0",
  "timestamp": "2025-12-28T10:00:00Z"
}
```

### Step 2: Configure Your AI Assistant

#### For Claude Desktop

1. Open Claude Desktop settings
2. Navigate to Developer Settings
3. Add MCP server configuration:

```json
{
  "mcpServers": {
    "sahool": {
      "url": "http://localhost:8200/mcp",
      "name": "SAHOOL Agricultural Platform",
      "description": "Access agricultural data and intelligence"
    }
  }
}
```

4. Restart Claude Desktop

#### For ChatGPT (with MCP plugin)

```json
{
  "servers": {
    "sahool": {
      "endpoint": "http://localhost:8200/mcp",
      "auth": {
        "type": "none"
      }
    }
  }
}
```

### Step 3: Test the Integration

Ask your AI assistant:

```
"Using SAHOOL, get me the weather forecast for Sana'a, Yemen (15.5527, 48.5164) for the next 7 days"
```

Or:

```
"Analyze the crop health for field-123 using NDVI"
```

## 📋 Available Capabilities

### Tools (5)

1. **Weather Forecast** - Get agricultural weather forecasts
2. **Crop Health Analysis** - Analyze crop health using satellite imagery
3. **Field Data** - Access field information and boundaries
4. **Irrigation Calculator** - Calculate irrigation requirements
5. **Fertilizer Recommendations** - Get fertilizer recommendations

### Resources (3 Types)

1. **Field Resources** - Field data, boundaries, soil info
2. **Weather Resources** - Current weather, forecasts, advisories
3. **Crop Resources** - Crop catalog, growing guides, pest/disease info

### Prompts (3)

1. **field_analysis** - Comprehensive field analysis
2. **irrigation_plan** - Create irrigation schedule
3. **crop_recommendation** - Recommend suitable crops

## 🎯 Example Use Cases

### 1. Get Weather Forecast

**Ask:**

```
"What's the weather forecast for my farm at coordinates 15.5527, 48.5164?"
```

**What happens:**

1. AI calls `get_weather_forecast` tool
2. SAHOOL queries weather service
3. Returns 7-day forecast with agricultural advisories

### 2. Analyze Crop Health

**Ask:**

```
"How healthy are my crops in field-123? Use satellite imagery."
```

**What happens:**

1. AI calls `analyze_crop_health` tool
2. SAHOOL analyzes latest satellite data
3. Returns NDVI values, stress areas, and recommendations

### 3. Plan Irrigation

**Ask:**

```
"My wheat field (field-123) has 45% soil moisture and is in flowering stage. When should I irrigate?"
```

**What happens:**

1. AI calls `calculate_irrigation` tool
2. SAHOOL considers weather, crop stage, soil moisture
3. Returns irrigation schedule and water amount

### 4. Get Fertilizer Advice

**Ask:**

```
"What fertilizer do I need for my corn field? My soil test shows nitrogen: 20 ppm, phosphorus: 15 ppm, potassium: 150 ppm, pH: 6.5"
```

**What happens:**

1. AI calls `get_fertilizer_recommendation` tool
2. SAHOOL analyzes soil test and crop requirements
3. Returns NPK recommendation and application schedule

## 🔧 Troubleshooting

### MCP Server Not Starting

```bash
# Check if port 8200 is available
lsof -i :8200

# Check logs
docker-compose logs mcp-server

# Restart service
docker-compose restart mcp-server
```

### AI Assistant Can't Connect

1. Verify MCP server is running:

   ```bash
   curl http://localhost:8200/health
   ```

2. Check firewall settings (port 8200 must be accessible)

3. Verify URL in AI assistant configuration matches server address

4. Check logs for connection errors:
   ```bash
   docker-compose logs -f mcp-server
   ```

### Tools Not Working

1. Verify SAHOOL core services are running:

   ```bash
   docker-compose ps
   ```

2. Check service health:

   ```bash
   curl http://localhost:8000/health  # Kong gateway
   ```

3. Review MCP server logs:
   ```bash
   docker-compose logs mcp-server | grep ERROR
   ```

## 📊 Monitoring

### Health Checks

```bash
# Server health
curl http://localhost:8200/health

# List available tools
curl http://localhost:8200/tools

# List resources
curl http://localhost:8200/resources

# Prometheus metrics
curl http://localhost:8200/metrics
```

### View Logs

```bash
# Follow MCP server logs
docker-compose logs -f mcp-server

# View last 100 lines
docker-compose logs --tail=100 mcp-server

# Search for errors
docker-compose logs mcp-server | grep -i error
```

## 🔐 Security

### Development (Default)

- No authentication required
- CORS enabled for all origins
- Suitable for local development only

### Production

1. Enable API key authentication:

   ```bash
   export MCP_API_KEY=your-secure-api-key
   ```

2. Configure CORS:

   ```python
   # Edit apps/services/mcp-server/src/main.py
   allow_origins=["https://your-domain.com"]
   ```

3. Use HTTPS:

   ```bash
   export SAHOOL_API_URL=https://api.sahool.io
   ```

4. Enable rate limiting (via Kong)

## 📚 Additional Resources

- **Full Documentation**: `/docs/MCP_INTEGRATION.md`
- **MCP Module README**: `/shared/mcp/README.md`
- **Service README**: `/apps/services/mcp-server/README.md`
- **API Documentation**: `http://localhost:8200/docs`
- **MCP Specification**: https://modelcontextprotocol.io

## 🆘 Getting Help

1. Check documentation in `/docs/`
2. Review logs: `docker-compose logs mcp-server`
3. Check GitHub issues
4. Contact development team

## 🎓 Advanced Usage

### Using Python Client

```python
from shared.mcp import MCPClientContext

async with MCPClientContext(server_url="http://localhost:8200") as client:
    # Get weather
    weather = await client.get_weather_forecast(
        latitude=15.5527,
        longitude=48.5164,
        days=7
    )
    print(weather)

    # Analyze crop health
    health = await client.analyze_crop_health(
        field_id="field-123",
        analysis_type="ndvi"
    )
    print(health)
```

### Custom Integrations

See `/shared/mcp/examples.py` for:

- Low-level MCP client usage
- Batch operations
- Resource access
- Prompt template usage

### Running Examples

```bash
# Run all examples
python -m shared.mcp.examples

# Or run specific examples
cd shared/mcp
python examples.py
```

## ✅ Verification Checklist

- [ ] MCP server is running (port 8200)
- [ ] Health check responds: `curl http://localhost:8200/health`
- [ ] AI assistant is configured with correct URL
- [ ] AI assistant can see SAHOOL tools
- [ ] Test tool call works (e.g., weather forecast)
- [ ] Logs show successful requests

## 🎉 Success!

You now have SAHOOL's agricultural intelligence accessible to AI assistants!

Try asking questions like:

- "What's the weather forecast for my farm?"
- "How healthy are my crops?"
- "When should I irrigate my wheat field?"
- "What fertilizer do I need for corn?"

---

**SAHOOL v16.0.0** | Built with ❤️ for Saudi Agriculture
