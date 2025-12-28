# SAHOOL Agent Registry Service

## نظام سجل الوكلاء - Agent Registry System

A production-ready Agent Registry Service following the A2A (Agent-to-Agent) protocol specification.

خدمة سجل الوكلاء جاهزة للإنتاج تتبع مواصفات بروتوكول A2A (الوكيل-إلى-وكيل).

## Features | الميزات

### Core Capabilities | القدرات الأساسية

- **Agent Registration** - تسجيل الوكلاء
  - Register AI agents with complete metadata
  - Version management
  - Capability and skill indexing
  - Automatic TTL management

- **Agent Discovery** - اكتشاف الوكلاء
  - Discover by capability
  - Discover by skill/expertise
  - Discover by tags/keywords
  - Filter by status and category

- **Health Monitoring** - مراقبة الصحة
  - Automatic health checks
  - Real-time status tracking
  - Degraded state detection
  - Response time monitoring

- **Storage Options** - خيارات التخزين
  - In-memory storage (development)
  - Redis-backed storage (production)
  - Configurable TTL
  - Distributed and persistent

## A2A Protocol Compliance

This service implements the A2A protocol specification for agent cards:

- **Agent Identity**: Unique ID, name, version (semver)
- **Capabilities**: Structured capability definitions with I/O schemas
- **Skills**: Expertise areas with proficiency levels
- **Security**: Multiple auth schemes (Bearer, API Key, OAuth2, mTLS)
- **Communication**: Input/output modes (text, structured, multimodal, stream)
- **Endpoints**: Primary and health check endpoints
- **Metadata**: Tags, categories, documentation, licensing

## Quick Start | البدء السريع

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit configuration
nano .env
```

### Running Locally

```bash
# Development mode (in-memory storage)
ENVIRONMENT=development python -m uvicorn src.main:app --reload --port 8080

# Production mode (Redis storage)
ENVIRONMENT=production python -m uvicorn src.main:app --host 0.0.0.0 --port 8080
```

### Running with Docker

```bash
# Build image
docker build -t sahool/agent-registry:latest .

# Run container
docker run -d \
  --name agent-registry \
  -p 8080:8080 \
  -e REDIS_HOST=redis \
  -e API_KEY=your-secret-key \
  sahool/agent-registry:latest
```

## API Documentation

### Base URL
```
http://localhost:8080
```

### Authentication
Most endpoints require an API key:
```
X-API-Key: your-secret-api-key
```

### Endpoints

#### Health & Status

- `GET /healthz` - Health check
- `GET /v1/registry/stats` - Registry statistics

#### Agent Management

- `POST /v1/registry/agents` - Register agent (requires API key)
- `GET /v1/registry/agents` - List all agents
- `GET /v1/registry/agents/{agent_id}` - Get agent card
- `DELETE /v1/registry/agents/{agent_id}` - Deregister agent (requires API key)

#### Discovery

- `GET /v1/registry/discover/capability?capability={name}` - Discover by capability
- `GET /v1/registry/discover/skill?skill={id}` - Discover by skill
- `POST /v1/registry/discover/tags` - Discover by tags

#### Health Monitoring

- `GET /v1/registry/agents/{agent_id}/health` - Check agent health
- `GET /v1/registry/health/all` - Get all health statuses

### Example: Register an Agent

```bash
curl -X POST http://localhost:8080/v1/registry/agents \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "agent_card": {
      "agent_id": "disease-expert-agent",
      "name": "Disease Expert Agent",
      "version": "1.0.0",
      "description": "AI agent specialized in diagnosing crop diseases",
      "capabilities": [
        {
          "name": "diagnose_disease",
          "description": "Diagnose crop diseases from symptoms"
        }
      ],
      "skills": [
        {
          "skill_id": "crop_pathology",
          "name": "Crop Pathology",
          "level": "expert",
          "keywords": ["disease", "diagnosis"]
        }
      ],
      "endpoint": {
        "url": "https://api.sahool.app/agents/disease-expert/invoke",
        "method": "POST"
      },
      "health_endpoint": "https://api.sahool.app/agents/disease-expert/health",
      "security_scheme": "bearer",
      "status": "active"
    }
  }'
```

### Example: Discover Agents

```bash
# Discover by capability
curl http://localhost:8080/v1/registry/discover/capability?capability=diagnose_disease

# Discover by skill
curl http://localhost:8080/v1/registry/discover/skill?skill=crop_pathology

# Discover by tags
curl -X POST http://localhost:8080/v1/registry/discover/tags \
  -H "Content-Type: application/json" \
  -d '{"tags": ["agriculture", "ai", "disease"]}'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_NAME` | Service name | `agent-registry` |
| `SERVICE_PORT` | HTTP port | `8080` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment (development/production) | `production` |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database | `0` |
| `REDIS_PASSWORD` | Redis password | - |
| `REDIS_PREFIX` | Key prefix | `sahool:registry:` |
| `HEALTH_CHECK_INTERVAL_SECONDS` | Health check interval | `60` |
| `HEALTH_CHECK_TIMEOUT_SECONDS` | Health check timeout | `5` |
| `AGENT_TTL_SECONDS` | Agent registration TTL | `3600` |
| `REQUIRE_API_KEY` | Require API key auth | `true` |
| `API_KEY` | API key for auth | - |
| `CORS_ORIGINS` | Allowed CORS origins | - |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Agent Registry Service                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   FastAPI    │────────▶│   Registry   │             │
│  │  REST API    │         │   Service    │             │
│  └──────────────┘         └──────────────┘             │
│         │                         │                      │
│         │                         │                      │
│         ▼                         ▼                      │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Storage    │◀────────│   Indexing   │             │
│  │   Layer      │         │   Engine     │             │
│  └──────────────┘         └──────────────┘             │
│    │         │                                           │
│    │         │                                           │
│    ▼         ▼                                           │
│  ┌────┐   ┌──────┐                                      │
│  │Mem │   │Redis │                                      │
│  └────┘   └──────┘                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_registry.py::test_register_agent
```

## Production Deployment

### Prerequisites

- Python 3.11+
- Redis 6.0+
- 512MB RAM minimum
- HTTPS/TLS certificate

### Deployment Checklist

- [ ] Set strong `API_KEY`
- [ ] Configure Redis with password
- [ ] Enable TLS/HTTPS
- [ ] Set appropriate `CORS_ORIGINS`
- [ ] Configure health check monitoring
- [ ] Set up log aggregation
- [ ] Enable metrics collection
- [ ] Configure backup for Redis
- [ ] Set up auto-scaling (if needed)

## Integration with SAHOOL

The Agent Registry integrates with the SAHOOL platform as follows:

1. **AI Advisor Service** registers its agents on startup
2. **Other services** query the registry to discover available agents
3. **Orchestration layer** uses registry for routing decisions
4. **Monitoring** tracks agent health and availability

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub: https://github.com/sahool/sahool-unified-v15-idp
- Documentation: https://docs.sahool.app/agent-registry
- Email: support@sahool.app
