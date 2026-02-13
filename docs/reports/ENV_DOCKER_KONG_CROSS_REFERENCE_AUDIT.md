# SAHOOL Platform Cross-Reference Audit Report
# تقرير تدقيق التطابق بين .env و Docker Compose و Kong

**Date**: 2026-02-13
**Scope**: .env.example, docker-compose.yml, Kong configuration, Dockerfiles
**Version**: 16.0.0

---

## Executive Summary

A comprehensive cross-reference audit of configuration files across the SAHOOL platform
revealed **18 issues**: 8 critical (P0), 6 high (P1), and 4 medium (P2).

The most severe issues are **5 wrong port targets in Kong upstreams** that would cause
complete routing failures for those services, and **hardcoded credentials** in 4 v3.0 services.

---

## Files Audited

| File | Lines | Status |
|------|-------|--------|
| `docker-compose.yml` | 4241 (54 services) | Fully read |
| `.env.example` | 1406 | Fully read |
| `apps/admin/.env.example` | 65 | Fully read |
| `apps/web/.env.example` | 57 | Fully read |
| `apps/services/ai-chat-assistant/.env.example` | 46 | Fully read |
| `infrastructure/gateway/kong/kong.yml` | ~3200 | Fully read |
| `infrastructure/gateway/kong/kong-upstreams.yml` | ~1200 | Fully read |
| `infrastructure/gateway/kong/kong-security.yml` | 607 | Fully read |
| `infrastructure/gateway/kong/kong-cors-production.yml` | 85 | Fully read |

---

## P0 - CRITICAL Issues (8)

### 1. Kong Upstreams Wrong Port Targets (5 services)

`kong-upstreams.yml` routes to wrong ports vs `docker-compose.yml`:

| Service | docker-compose | kong-upstreams.yml | Correct Port |
|---------|---------------|-------------------|-------------|
| `chat-service` | 8000 | **8114** | 8000 |
| `copilot-api` | 8088 | **8163** | 8088 |
| `audit-service` | 8114 | **8122** | 8114 |
| `globalgap-compliance` | 8128 | **8168** | 8128 |
| `supply-chain-service` | 8230 | **8166** | 8230 |

**Impact**: Complete routing failure for these 5 services through Kong.

**Fix**: Update `infrastructure/gateway/kong/kong-upstreams.yml` to match docker-compose.yml ports.

### 2. Wrong Service URLs in .env.example (2 services)

| Variable | .env.example Value | Actual Port | Wrong Target |
|----------|-------------------|-------------|-------------|
| `YIELD_PREDICTION_URL` (line 687) | `:8098` | `8152` | Points to yield-engine (legacy) |
| `CODE_REVIEW_SERVICE_URL` (line 1324) | `:8124` | `8102` | Points to soil-analysis-service |

**Impact**: Inter-service calls using these URLs will hit wrong services.

**Fix**: Update .env.example:
- `YIELD_PREDICTION_URL=http://yield-prediction-service:8152`
- `CODE_REVIEW_SERVICE_URL=http://code-review-service:8102`

### 3. Hardcoded Credentials in v3.0 Services

Lines 4037-4158 in docker-compose.yml contain hardcoded default passwords:

```yaml
# 4 services affected:
NATS_PASSWORD:-sahool_nats_2024    # Hardcoded NATS password
REDIS_PASSWORD:-sahool_redis_2024  # Hardcoded Redis password
```

**Affected**: `irrigation-cycle-engine`, `iot-sensor-hub`, `fertigation-engine`, `digital-twin-engine`

**Fix**: Use `${NATS_PASSWORD:?NATS_PASSWORD is required}` pattern like other services.

---

## P1 - HIGH Issues (6)

### 4. JWT Algorithm Conflict (RS256 vs HS256)

`.env.example` defaults to `JWT_ALGORITHM=HS256`, but 5 services default to RS256:

| Service | Default | Line |
|---------|---------|------|
| `ws-gateway` | RS256 | 1525 |
| `agro-advisor` | RS256 | 2170 |
| `iot-gateway` | RS256 | 2219 |
| `ndvi-engine` | RS256 | 2286 |
| `weather-core` | RS256 | 2340 |

**Impact**: If JWT_ALGORITHM not set in .env, token verification fails between HS256 and RS256 services.

### 5. Duplicate CORS_ALLOWED_ORIGINS in .env.example

Defined TWICE with different values:

| Line | Value | Domains |
|------|-------|---------|
| 209 | `https://sahool.app,...` | **.sahool.app** |
| 222 | `https://sahool.com,...` | **.sahool.com** |

Additionally, 5 different CORS configurations across the platform:

| Source | Domains |
|--------|---------|
| `.env.example` line 209 | .sahool.**app** |
| `.env.example` line 222 | .sahool.**com** |
| `kong-security.yml` | .sahool.**io** |
| `kong-cors-production.yml` | .sahool.**com** |
| `kong.yml` global plugin | wildcard `*` |

### 6. Admin Portal Auth URL Points to Kong Admin API

```ini
# apps/admin/.env.example line 15:
NEXT_PUBLIC_AUTH_URL=http://localhost:8001  # Kong Admin API!
```

Should point to `http://localhost:3025` (user-service) or `http://localhost:8000/api/v1/auth` (Kong proxy).

### 7. ai-chat-assistant Missing Authentication

```ini
# apps/services/ai-chat-assistant/.env.example
NATS_URL=nats://nats:4222          # No authentication!
REDIS_PASSWORD=                     # Empty!
```

### 8. Port Conflicts

| Port | Service 1 | Service 2 | Severity |
|------|-----------|-----------|----------|
| 8200 | vault | mcp-server | HIGH - Host port collision |
| 8230 | supply-chain-service | ai-chat-assistant | HIGH - Host port collision |
| 8000 | kong (proxy) | chat-service (internal) | MEDIUM - Resolved via mapping |

### 9. ai-advisor Uses SERVICE_PORT Instead of PORT

```yaml
# docker-compose.yml line 2528:
ai-advisor:
  environment:
    - SERVICE_PORT=8112    # Non-standard! All other services use PORT=
```

---

## P2 - MEDIUM Issues (4)

### 10. Inconsistent DATABASE_URL Formats

| Pattern | Format | Services |
|---------|--------|----------|
| Node.js | `postgresql://...?sslmode=disable&pgbouncer=true` | 10 |
| Python (asyncpg) | `postgresql+asyncpg://...?ssl=disable` | billing-core only |
| Python (standard) | `postgresql://...?sslmode=disable&pgbouncer=true` | ~30 |

### 11. v3.0 Services Missing DATABASE_URL

4 services lack DATABASE_URL entirely: `irrigation-cycle-engine`, `iot-sensor-hub`,
`fertigation-engine`, `digital-twin-engine`.

### 12. Services Without Kong Routes

| Service | Port | Reason |
|---------|------|--------|
| `ussd-gateway` | 8183 | Commented out in kong.yml |
| `iot-sensor-hub` | 8251 | New v3.0 service |
| `fertigation-engine` | 8252 | New v3.0 service |
| `irrigation-cycle-engine` | 8250 | New v3.0 service |
| `digital-twin-engine` | 8253 | New v3.0 service |
| `code-review-agent` | 8145 | In .env only, not in docker-compose |

### 13. Ghost Service Reference in .env.example

```ini
# .env.example line 1323:
CODE_REVIEW_AGENT_URL=http://code-review-agent:8145
```

`code-review-agent` (port 8145) does not exist in docker-compose.yml. Only `code-review-service` (port 8102) exists.

---

## Complete Port Matrix

### Infrastructure Services

| Service | docker-compose Port | .env Port | Kong Port | Status |
|---------|-------------------|-----------|-----------|--------|
| postgres | 5432 | 5432 | N/A | OK |
| pgbouncer | 6432 | 6432 | N/A | OK |
| redis | 6379, 6380 | 6379, 6380 | N/A | OK |
| nats | 4222, 4223, 8222 | 4222, 4223 | N/A | OK |
| vault | 8200 | 8200 | N/A | CONFLICT with mcp-server |
| kong | 8000, 8001 | 8000, 8001 | N/A | OK |
| qdrant | 6333, 6334 | 6333 | N/A | OK |
| milvus | 19530, 9091 | N/A | N/A | OK |
| minio | 9000, 9090 | N/A | N/A | OK |
| mlflow | 5000 | 5000 | N/A | OK |
| mqtt | 1883, 9001 | 1883 | N/A | OK |
| ollama | 11434 | 11434 | N/A | OK |

### Node.js Services

| Service | docker-compose | .env | Kong | Status |
|---------|---------------|------|------|--------|
| field-management-service | 3000 | 3000 | 3000 | OK |
| user-service | 3025 | 3025 | 3025 | OK |
| marketplace-service | 3010 | 3010 | 3010 | OK |
| research-core | 3015 | - | 3015 | OK |
| disaster-assessment | 3020 | - | 3020 | OK |
| chat-service | 8000 (host:8115) | 8000 | **8114** | MISMATCH |
| iot-service | 8117 | - | 8117 | OK |

### Python Services

| Service | docker-compose | .env | Kong | Status |
|---------|---------------|------|------|--------|
| ws-gateway | 8081 | - | 8081 | OK |
| copilot-api | 8088 (host:8163) | - | **8163** | MISMATCH |
| billing-core | 8089 | - | 8089 | OK |
| vegetation-analysis-service | 8090 | 8090 | 8090 | OK |
| indicators-service | 8091 | 8091 | 8091 | OK |
| weather-service | 8092 | 8092 | 8092 | OK |
| advisory-service | 8093 | 8093 | 8093 | OK |
| irrigation-smart | 8094 | 8094 | 8094 | OK |
| crop-intelligence-service | 8095 | 8095 | 8095 | OK |
| field-chat | 8099 | - | 8099 | OK |
| equipment-service | 8101 | - | 8101 | OK |
| code-review-service | 8102 | **8124** | 8102 | .env MISMATCH |
| task-service | 8103 | 8103 | 8103 | OK |
| provider-config | 8104 | - | 8104 | OK |
| iot-gateway | 8106 | 8106 | 8106 | OK |
| notification-service | 8110 | 8110 | 8110 | OK |
| astronomical-calendar | 8111 | 8111 | 8111 | OK |
| ai-advisor | 8112 | 8112 | 8112 | OK |
| alert-service | 8113 | 8113 | 8113 | OK |
| audit-service | 8114 | - | **8122** | MISMATCH |
| inventory-service | 8116 | - | 8116 | OK |
| ndvi-processor | 8118 | - | 8118 | OK |
| virtual-sensors | 8119 | - | 8119 | OK |
| field-intelligence | 8120 | 8120 | 8120 | OK |
| skills-service | 8121 | 8121 | 8121 | OK |
| traceability-service | 8123 | - | 8123 | OK |
| soil-analysis-service | 8124 | - | 8124 | OK |
| pest-detection-service | 8125 | - | 8125 | OK |
| drone-service | 8126 | - | 8126 | OK |
| cooperative-service | 8127 | - | 8127 | OK |
| globalgap-compliance | 8128 | 8128 | **8168** | MISMATCH |
| ai-agents-service | 8130 | 8130 | 8130 | OK |
| crm-service | 8131 | 8131 | 8131 | OK |
| lowcode-engine | 8132 | 8132 | 8132 | OK |
| wechat-service | 8133 | 8133 | 8133 | OK |
| knowledge-graph | 8140 | 8140 | 8140 | OK |
| yolo26-vision-service | 8150 | 8150 | 8150 | OK |
| yield-prediction-service | 8152 | **8098** | 8152 | .env MISMATCH |
| agent-registry | 8160 | 8160 | 8160 | OK |
| ai-agents-core | 8161 | 8161 | 8161 | OK |
| code-fix-agent | 8162 | 8162 | 8162 | OK |
| llm-orchestrator-service | 8164 | - | 8164 | OK |
| hydrology-service | 8165 | 8165 | 8165 | OK |
| logistics-service | 8167 | 8167 | 8167 | OK |
| leveling-optimizer-service | 8170 | 8170 | 8170 | OK |
| edge-orchestrator-service | 8180 | 8180 | 8180 | OK |
| ground-vision-service | 8182 | 8182 | 8182 | OK |
| supply-chain-service | 8230 | - | **8166** | MISMATCH |
| terrain-core-service | 8185 | 8185 | 8185 | OK |
| mcp-server | 8200 | 8200 | 8200 | CONFLICT with vault |
| irrigation-cycle-engine | 8250 | - | - | No Kong route |
| iot-sensor-hub | 8251 | - | - | No Kong route |
| fertigation-engine | 8252 | - | - | No Kong route |
| digital-twin-engine | 8253 | - | - | No Kong route |

---

## Summary

| Priority | Count | Description |
|----------|-------|-------------|
| **P0 - Critical** | **8** | 5 Kong wrong ports + 2 wrong URLs + hardcoded credentials |
| **P1 - High** | **6** | JWT conflict + CORS duplicate + Auth URL + no-auth + port conflicts + SERVICE_PORT |
| **P2 - Medium** | **4** | DATABASE_URL formats + missing DB URLs + no Kong routes + ghost service |
| **Total** | **18** | |

---

_Report generated: 2026-02-13_
_Auditor: Claude Code (Opus 4.6)_
