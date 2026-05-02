# بطاقة المرجع السريع - Kong و API Gateway
# Quick Reference Card - Kong & API Gateway

**منصة سهول | SAHOOL Platform v16.0.0**

---

## 🚀 Quick Start

### Kong Admin API
```bash
# Check Kong health
curl http://localhost:8001/status

# List all services
curl http://localhost:8001/services

# List all routes
curl http://localhost:8001/routes

# Validate configuration
docker exec sahool-kong kong config parse /kong/declarative/kong.yml
```

### Service Health Checks
```bash
# Infrastructure
curl http://localhost:5432  # PostgreSQL (port check)
curl http://localhost:6379  # Redis (port check)
curl http://localhost:4222  # NATS (port check)
curl http://localhost:8200  # Vault

# AI Agents
curl http://localhost:8160/healthz  # agent-registry
curl http://localhost:8161/healthz  # ai-agents-core
curl http://localhost:8162/healthz  # code-fix-agent
curl http://localhost:8163/healthz  # copilot-api
curl http://localhost:8164/healthz  # llm-orchestrator
```

---

## 📍 Key Endpoints

### AI Agents
| Service | Port | Kong Route | Health |
|---------|------|-----------|--------|
| agent-registry | 8160 | /api/v1/agents | /healthz |
| ai-agents-core | 8161 | /api/v1/ai-agents | /healthz |
| code-fix-agent | 8162 | /api/v1/code-fix | /healthz |
| copilot-api | 8163 | /api/v1/copilot | /healthz |
| llm-orchestrator | 8164 | /api/v1/llm | /healthz |
| ai-agents-service | 8130 | /api/v1/ai-agents-service | /healthz |

### Infrastructure
| Service | Port | Access | Admin |
|---------|------|--------|-------|
| Kong Gateway | 8000 | Public | 8001 (localhost) |
| PostgreSQL | 5432 | Internal | - |
| PgBouncer | 6432 | Internal | 6432 |
| Redis | 6379 | Internal | - |
| NATS | 4222 | Internal | - |
| Vault | 8200 | Internal | 8200 |

---

## 🔑 Authentication

### JWT Tiers
```yaml
Starter:
  Rate: 100/min, 5000/hour
  Algorithm: HS256
  Key: starter-jwt-key-hs256

Professional:
  Rate: 1000/min, 50000/hour
  Algorithm: HS256
  Key: professional-jwt-key-hs256

Enterprise:
  Rate: 10000/min, 500000/hour
  Algorithm: HS256
  Key: enterprise-jwt-key-hs256

Admin:
  Rate: 10000/min, unlimited/hour
  Algorithm: HS256
  Key: admin-jwt-key-hs256
```

### Example Request
```bash
# Public endpoint (no auth)
curl http://localhost:8000/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Protected endpoint (with JWT)
curl http://localhost:8000/api/v1/fields -X GET \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 🛠️ Common Tasks

### Restart Services
```bash
# Restart Kong
docker restart sahool-kong

# Restart AI agents
docker restart sahool-agent-registry
docker restart sahool-ai-agents-core
docker restart sahool-code-fix-agent
docker restart sahool-copilot-api
docker restart sahool-llm-orchestrator-service

# Restart all
docker-compose restart
```

### View Logs
```bash
# Kong logs
docker logs -f sahool-kong

# AI agent logs
docker logs -f sahool-agent-registry
docker logs -f sahool-copilot-api

# All services
docker-compose logs -f
```

### Database Access
```bash
# Via PgBouncer
docker exec -it sahool-pgbouncer psql \
  -h localhost -p 6432 -U sahool -d sahool

# Direct PostgreSQL
docker exec -it sahool-postgres psql \
  -U sahool -d sahool
```

---

## 📊 Monitoring

### Prometheus Metrics
```bash
# Kong metrics
curl http://localhost:8001/metrics

# NATS metrics
curl http://localhost:7777/metrics
```

### Health Check All Services
```bash
#!/bin/bash
for port in 8160 8161 8162 8163 8164 8130; do
  echo "Checking port $port..."
  curl -s http://localhost:$port/healthz | jq .
done
```

---

## 🐛 Troubleshooting

### Kong Not Starting
```bash
# Check configuration syntax
docker exec sahool-kong kong config parse /kong/declarative/kong.yml

# Check Kong logs
docker logs sahool-kong

# Validate environment variables
docker exec sahool-kong env | grep KONG
```

### Service Not Reachable
```bash
# 1. Check service is running
docker ps | grep <service-name>

# 2. Check service health
docker exec <container> curl localhost:<port>/healthz

# 3. Check Kong route
curl http://localhost:8001/routes | jq '.data[] | select(.name == "<route-name>")'

# 4. Check DNS resolution
docker exec sahool-kong nslookup <service-name>
```

### Database Connection Issues
```bash
# Check PgBouncer status
docker exec sahool-pgbouncer psql \
  -h localhost -p 6432 -U pgbouncer -d pgbouncer \
  -c "SHOW POOLS;"

# Check PostgreSQL connections
docker exec sahool-postgres psql -U sahool -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

---

## 📝 Configuration Files

### Main Files
```
infrastructure/gateway/kong/kong.yml    # Kong declarative config (1,407 lines)
docker-compose.yml                      # Service orchestration (4,200+ lines)
governance/agents.yaml                  # AI agents definitions (1,200+ lines)
mcp.json                                # MCP configuration
.env.example                            # Environment variables template
```

### Kong Configuration Structure
```yaml
_format_version: "3.0"
_transform: true

plugins:                 # Global plugins
  - cors
  - prometheus
  - correlation-id
  - request-size-limiting

services:               # 77 services
  - name: <service>
    host: <service>
    port: <port>
    routes:
      - paths: [...]

upstreams:              # Load balancing (optional)
  - name: <upstream>
    targets:
      - target: <host>:<port>

consumers:              # JWT consumers (5 tiers)
  - username: <tier>-consumer

acls:                   # Access control groups
  - consumer: <consumer>
    group: <group>
```

---

## 🔧 Environment Variables

### Required Variables
```bash
# Database
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=sahool

# Redis
REDIS_PASSWORD=<secure_password>

# NATS
NATS_USER=sahool
NATS_PASSWORD=<secure_password>

# JWT
JWT_SECRET_KEY=<32_char_minimum_secret_key>
JWT_ALGORITHM=HS256

# General
ENVIRONMENT=development|staging|production
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
```

### Optional Variables
```bash
# LLM Providers
ANTHROPIC_API_KEY=<api_key>
OPENAI_API_KEY=<api_key>

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=codellama:7b

# MCP
SAHOOL_API_URL=http://localhost:8000
```

---

## 📊 Current Status

### ✅ What's Working
- ✅ 80 active services registered
- ✅ All ports matching between Kong & Docker
- ✅ AI agents (6) fully operational
- ✅ Copilot & LLM Orchestrator integrated
- ✅ JWT authentication (5 tiers)
- ✅ Rate limiting (Redis-based)
- ✅ Connection pooling (PgBouncer)

### ⚠️ Minor Issues
- 🟡 7 deprecated services in Kong (need removal)
- 🟡 CORS open to all (dev only, fix for production)
- 🟡 TLS/SSL disabled (dev only, required for production)
- 🟡 3 services under development (mcp-server, code-review, ai-advisor)

### 📈 Overall Rating
```
Configuration:    9.0/10 ✅
Performance:      9.0/10 ✅
Integration:      8.5/10 ✅
Documentation:    8.0/10 ✅
Security:         7.5/10 🟡

TOTAL:           8.4/10 🟢
```

---

## 🚨 Production Checklist

Before deploying to production:

- [ ] Enable TLS/SSL on Kong
  ```yaml
  KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl"
  KONG_SSL_CERT: /etc/kong/ssl/server.crt
  KONG_SSL_CERT_KEY: /etc/kong/ssl/server.key
  ```

- [ ] Update CORS origins
  ```yaml
  origins:
    - "https://app.sahool.com"
    - "https://admin.sahool.com"
  credentials: true
  ```

- [ ] Add security headers
  ```yaml
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  ```

- [ ] Enable PostgreSQL SSL
  ```bash
  sslmode=require  # in DATABASE_URL
  ```

- [ ] Configure IP restrictions for sensitive services
- [ ] Setup monitoring & alerting
- [ ] Review and update rate limits
- [ ] Backup configuration files
- [ ] Document disaster recovery procedures

---

## 📞 Support

### Documentation
- Full Report: `KONG_API_COMPREHENSIVE_REVIEW_AR_EN.md`
- Executive Summary: `KONG_REVIEW_EXECUTIVE_SUMMARY.md`
- Architecture: `KONG_ARCHITECTURE_DIAGRAM.md`

### Contact
- Infrastructure: infra@sahool.io
- Security: security@sahool.io
- AI Team: ai@sahool.io
- Support: support@sahool.io

---

## 🔗 Useful Links

```bash
# Kong Documentation
https://docs.konghq.com/gateway/3.4.x/

# Docker Compose
https://docs.docker.com/compose/

# FastAPI (Python services)
https://fastapi.tiangolo.com/

# NestJS (Node.js services)
https://nestjs.com/

# PostgreSQL + PostGIS
https://postgis.net/
```

---

**Quick Reference v1.0**
**Created: 2026-02-04**
**© KAFAAT - SAHOOL Platform**
