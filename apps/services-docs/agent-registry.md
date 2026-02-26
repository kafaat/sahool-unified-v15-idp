# Agent Registry Service

**Port**: 8160 | **Type**: Python (FastAPI) | **Version**: 16.0.0

A production-ready A2A (Agent-to-Agent) protocol-compliant registry service for discovering, registering, and monitoring AI agents across the SAHOOL platform.

---

## Overview

The Agent Registry Service provides a centralized directory for all AI agents in the SAHOOL ecosystem. It follows the Linux Foundation A2A protocol specification, enabling agents to advertise their capabilities and skills, and allowing other services to discover agents at runtime. Storage is dual-mode: in-memory for development and Redis-backed for production with configurable TTL.

---

## Architecture

```
FastAPI REST API
      |
  Registry Service (indexing, health monitoring, TTL management)
      |
  Storage Layer
  ├── InMemoryStorage   (development)
  └── RedisStorage      (production, configurable TTL)
```

On startup the service initializes the appropriate storage backend based on `ENVIRONMENT` and `REDIS_HOST`, then starts background health-check polling at `HEALTH_CHECK_INTERVAL_SECONDS` (default 60 s).

---

## API Endpoints

### Health & Status

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe (checks Redis ping if applicable) |
| GET | `/readyz` | Kubernetes readiness probe |
| GET | `/v1/registry/stats` | Registry statistics (total agents, active, degraded) |

### Agent Management (authentication required for write operations)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/v1/registry/agents` | API Key | Register a new agent |
| GET | `/v1/registry/agents` | - | List agents (filter: `status`, `category`) |
| GET | `/v1/registry/agents/{agent_id}` | - | Get agent card by ID |
| DELETE | `/v1/registry/agents/{agent_id}` | API Key | Deregister agent |

### Discovery

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/registry/discover/capability?capability={name}` | Find agents by capability name |
| GET | `/v1/registry/discover/skill?skill={id}` | Find agents by skill ID |
| POST | `/v1/registry/discover/tags` | Find agents matching a list of tags |

### Health Monitoring

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/registry/agents/{agent_id}/health` | Check liveness of a specific agent |
| GET | `/v1/registry/health/all` | Aggregate health status of all registered agents |

---

## A2A Agent Card Schema

Each registered agent submits an `AgentCard` containing:
- **Identity**: `agent_id`, `name`, `version` (semver)
- **Capabilities**: structured list with I/O schema definitions
- **Skills**: expertise areas with proficiency levels and keywords
- **Security**: auth scheme (`bearer`, `api_key`, `oauth2`, `mtls`)
- **Communication**: input/output modes (`text`, `structured`, `multimodal`, `stream`)
- **Endpoints**: `endpoint.url`, `health_endpoint`
- **Metadata**: `tags`, `category`, documentation links

---

## NATS Events

This service does not publish NATS events. Agent lifecycle events are emitted by consumer services that query the registry.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | `agent-registry` | Service identifier |
| `SERVICE_PORT` | `8080` | HTTP listen port |
| `ENVIRONMENT` | `production` | `development` uses in-memory storage |
| `REDIS_HOST` | `localhost` | Redis hostname (production) |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database index |
| `REDIS_PASSWORD` | - | Redis auth password |
| `REDIS_PREFIX` | `sahool:registry:` | Key namespace prefix |
| `HEALTH_CHECK_INTERVAL_SECONDS` | `60` | Agent health poll interval |
| `HEALTH_CHECK_TIMEOUT_SECONDS` | `5` | Per-agent health check timeout |
| `AGENT_TTL_SECONDS` | `3600` | Redis TTL for agent registrations |
| `REQUIRE_API_KEY` | `true` | Enforce `X-API-Key` on write endpoints |
| `API_KEY` | - | Secret key for write authentication |
| `CORS_ORIGINS` | - | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Dependencies

- **FastAPI** + **structlog** for structured JSON logging
- **Redis** (`redis.asyncio`) for production storage
- `shared.errors_py` for unified error handling and request-ID middleware
- `shared/registry/` (`AgentCard`, `AgentRegistry`, `RegistryConfig`) for A2A protocol logic

---

## Health Endpoints

```
GET /healthz   → {"status": "healthy|degraded", "service": "agent-registry", "version": "16.0.0", "storage": "healthy|unhealthy"}
GET /readyz    → {"status": "ready", "service": "agent-registry", "version": "16.0.0", "checks": {"service": "ready"}}
```

---

## Related Services

- **ai-agents-core** (8161) - registers specialist agents on startup
- **llm-orchestrator-service** (8164) - queries registry for agent routing
- **advisory-service** (8093) - registers advisory agents
