# SAHOOL Platform - Observations Document

**Generated:** 2026-01-08T21:05:00Z
**Engineer:** Code Engineer Agent
**Status:** Pre-Run Analysis (Docker not available in sandbox)

---

## Executive Summary

Analysis of the docker-compose.yml and configuration files reveals **12 critical issues** and **8 warnings** that would prevent successful stack deployment. The most significant issues are:

1. Missing `.env` file (required environment variables undefined)
2. PgBouncer hardcoded password in config file
3. Missing TLS certificates directories
4. Kong configuration port mismatches
5. Kong routes to non-existent services

---

## Critical Issues (Stack-Breaking)

### Issue 1: Missing .env File
**Severity:** CRITICAL
**Evidence:**
- Only `.env.example` exists in the repository
- docker-compose.yml uses `${VAR:?error}` syntax requiring these variables
- 25+ required environment variables undefined

**Affected Services:** ALL (39+ services)

**Root Cause:** No `.env` file has been created from `.env.example`

**Impact:**
```
error: POSTGRES_PASSWORD is required
error: REDIS_PASSWORD is required
error: JWT_SECRET_KEY is required
```

---

### Issue 2: PgBouncer Hardcoded Password
**Severity:** CRITICAL
**File:** `infrastructure/core/pgbouncer/pgbouncer.ini:8`

**Evidence:**
```ini
sahool = host=postgres port=5432 dbname=sahool user=sahool password=change_this_secure_password_in_production
```

**Root Cause:** Password is hardcoded instead of using environment variable injection

**Impact:**
- Security vulnerability (password in config file)
- Password mismatch with actual `POSTGRES_PASSWORD` from `.env`
- Authentication failure when connecting to PostgreSQL

---

### Issue 3: Missing MinIO TLS Certificates Directory
**Severity:** HIGH
**File:** `docker-compose.yml` (minio service)

**Evidence:**
```yaml
volumes:
  - ./secrets/minio-certs/production/certs:/root/.minio/certs:ro
```

**Verification:**
```bash
$ ls -la /home/user/sahool-unified-v15-idp/secrets/minio-certs/
Directory not found
```

**Impact:**
- MinIO container will fail to start
- Milvus (depends on MinIO) will fail
- All vector search functionality disabled

---

### Issue 4: Kong Configuration Port Mismatch
**Severity:** HIGH
**Files:**
- `docker-compose.yml:462-469` - code-review-service
- `infrastructure/gateway/kong/kong.yml:458-483`

**Evidence:**

docker-compose.yml:
```yaml
code-review-service:
  ports:
    - "8102:8102"
  environment:
    - API_PORT=8102
```

kong.yml:
```yaml
- name: code-review-upstream
  targets:
    - target: code-review-service:8096  # WRONG PORT!
```

**Impact:**
- Kong health checks fail for code-review-service
- /api/v1/code-review route returns 502 Bad Gateway

---

### Issue 5: Kong Routes to Non-Existent Services
**Severity:** HIGH
**File:** `infrastructure/gateway/kong/kong.yml`

**Missing Services (defined in Kong but not in docker-compose.yml):**

| Service | Port | Kong Route |
|---------|------|------------|
| user-service | 3025 | /api/v1/users, /api/v1/auth |
| agent-registry | 8150 | /api/v1/agents |
| ai-agents-core | 8122 | /api/v1/ai-agents |
| globalgap-compliance | 8153 | /api/v1/compliance |
| analytics-service | 8154 | /api/v1/analytics |
| reporting-service | 8155 | /api/v1/reports |
| integration-service | 8156 | /api/v1/integrations |
| audit-service | 8157 | /api/v1/audit |
| export-service | 8158 | /api/v1/export |
| import-service | 8159 | /api/v1/import |
| admin-dashboard | 3001 | /api/v1/admin |
| monitoring-service | 8160 | /api/v1/monitoring |
| logging-service | 8161 | /api/v1/logs |
| tracing-service | 8162 | /api/v1/tracing |
| cache-service | 8163 | /api/v1/cache |
| search-service | 8164 | /api/v1/search |

**Impact:**
- Kong active healthchecks fail for these upstreams
- Routes return 503 Service Unavailable
- May cause Kong performance degradation due to DNS failures

---

### Issue 6: Missing TLS Certificates Directory
**Severity:** HIGH
**File:** `docker-compose.yml` (multiple services)

**Evidence:**
```yaml
# Multiple services reference:
volumes:
  - ./config/certs:/etc/nats/certs:ro
  - ./config/certs:/etc/redis/certs:ro
  - ./config/certs:/etc/pgbouncer/certs:ro
```

**Verification:**
```bash
$ ls -la /home/user/sahool-unified-v15-idp/config/certs/
# Only contains generate-internal-tls.sh script
# No actual certificate files
```

**Impact:**
- Services expecting TLS will fail if TLS mode is enabled
- Currently mitigated by TLS being disabled in development configs

---

### Issue 7: Ollama GPU Requirement
**Severity:** MEDIUM-HIGH
**File:** `docker-compose.yml:405-417`

**Evidence:**
```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

**Impact:**
- Fails on systems without NVIDIA GPU
- Fails if nvidia-container-toolkit not installed
- code-review-service depends on ollama (cascade failure)

---

## Warnings (Non-Critical but Should Fix)

### Warning 1: iot-gateway Health Check Path Mismatch
**File:** `docker-compose.yml:1982` vs `kong.yml:197`

**docker-compose.yml:**
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "... 'http://localhost:8106/health' ..."]
```

**kong.yml:**
```yaml
healthchecks:
  active:
    http_path: /healthz  # Different path!
```

---

### Warning 2: marketplace-service Health Check Path
**File:** `docker-compose.yml:864` vs `kong.yml:278`

**docker-compose.yml:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3010/api/v1/healthz"]
```

**kong.yml:**
```yaml
healthchecks:
  active:
    http_path: /healthz  # Missing /api/v1 prefix
```

---

### Warning 3: Etcd Init Script Execution
**File:** `docker-compose.yml:560-566`

**Evidence:**
```yaml
etcd-init:
  command: ["/bin/sh", "/scripts/init-auth.sh"]
  restart: "no"
```

**Concern:** If etcd-init fails, authentication may not be enabled, but Milvus will still try to connect with auth.

---

### Warning 4: Deprecated Services Still Active
**File:** `docker-compose.yml`

Several services are marked deprecated but still run by default:
- yield-prediction (port 3021) - replaced by yield-prediction-service (8098)
- lai-estimation (port 3022) - replaced by vegetation-analysis-service
- crop-growth-model (port 3023) - replaced by crop-intelligence-service
- community-chat (port 8097) - replaced by chat-service
- field-service (port 8115) - replaced by field-management-service
- ndvi-processor (port 8118) - replaced by vegetation-analysis-service

**Impact:** Resource waste, potential confusion, possible port conflicts

---

### Warning 5: Redis TLS Mode Inconsistency
**File:** `.env.example` vs `infrastructure/redis/redis-secure.conf`

**.env.example:**
```
REDIS_URL=rediss://:password@redis:6380/0
```

**redis-secure.conf:**
```
port 6379
# TLS is commented out
```

**Impact:** Connection URL expects TLS on port 6380, but Redis listens on 6379 without TLS

---

### Warning 6: NATS Required Variables
**File:** `docker-compose.yml:201-214`

docker-compose.yml requires 10 NATS environment variables:
```yaml
NATS_USER: ${NATS_USER:?NATS_USER is required}
NATS_PASSWORD: ${NATS_PASSWORD:?NATS_PASSWORD is required}
NATS_ADMIN_USER: ${NATS_ADMIN_USER:?...}
NATS_ADMIN_PASSWORD: ${NATS_ADMIN_PASSWORD:?...}
NATS_MONITOR_USER: ${NATS_MONITOR_USER:?...}
NATS_MONITOR_PASSWORD: ${NATS_MONITOR_PASSWORD:?...}
NATS_CLUSTER_USER: ${NATS_CLUSTER_USER:?...}
NATS_CLUSTER_PASSWORD: ${NATS_CLUSTER_PASSWORD:?...}
NATS_SYSTEM_USER: ${NATS_SYSTEM_USER:?...}
NATS_SYSTEM_PASSWORD: ${NATS_SYSTEM_PASSWORD:?...}
NATS_JETSTREAM_KEY: ${NATS_JETSTREAM_KEY:?...}
```

But only 7 are defined in `.env.example`. Missing:
- NATS_SYSTEM_USER
- NATS_SYSTEM_PASSWORD
- NATS_JETSTREAM_KEY

---

### Warning 7: Milvus Configuration References
**File:** `docker-compose.yml:654-656`

```yaml
ETCD_USERNAME: ${ETCD_ROOT_USERNAME:?...}
ETCD_PASSWORD: ${ETCD_ROOT_PASSWORD:?...}
```

But Milvus may expect different environment variable names for etcd auth.

---

### Warning 8: Kong Redis Authentication
**File:** `infrastructure/gateway/kong/kong.yml`

All rate-limiting plugins use:
```yaml
redis_password: ${REDIS_PASSWORD}
```

But this variable interpolation may not work in Kong declarative config (need to verify).

---

## Summary Table

| Issue | Severity | Impact | Fix Priority |
|-------|----------|--------|--------------|
| Missing .env file | CRITICAL | All services fail | 1 |
| PgBouncer hardcoded password | CRITICAL | DB auth fails | 2 |
| Missing MinIO certs directory | HIGH | Milvus fails | 3 |
| Kong port mismatch | HIGH | Route fails | 4 |
| Non-existent Kong services | HIGH | 16 routes fail | 5 |
| Missing TLS certs directory | HIGH | TLS services fail | 6 |
| Ollama GPU requirement | MEDIUM | AI features fail | 7 |
| Health check path mismatches | LOW | Monitoring gaps | 8 |

---

## Recommended Fix Order

1. **Create .env file** - Unblocks all services
2. **Fix PgBouncer config** - Enables database connectivity
3. **Create certificates directories** - Even if empty, prevents mount failures
4. **Fix Kong port mismatch** - Enables code-review route
5. **Comment out non-existent Kong upstreams** - Prevents healthcheck failures
6. **Add missing .env.example variables** - Prevents future errors
7. **Make Ollama optional** - Allow stack to run without GPU
8. **Fix health check paths** - Align Kong with service endpoints
