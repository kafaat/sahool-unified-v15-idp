# SAHOOL v16.0.0 SRE Analysis Report
# تقرير تحليل SRE لمنصة سهول

**Generated:** 2026-02-02
**Analyst:** Senior SRE Agent
**Status:** CRITICAL ISSUES IDENTIFIED

---

## Executive Summary | ملخص تنفيذي

The analysis identified **23 critical issues** across infrastructure, services, and gateway configuration that require immediate attention before production deployment.

| Category | Issues Found | Severity |
|----------|-------------|----------|
| Database Connectivity | 12 services | CRITICAL |
| NATS Messaging | 5 services | HIGH |
| Kong Gateway | 14 orphaned routes | HIGH |
| SSL/TLS Configuration | 6 services | HIGH |
| Missing Dependencies | 3 services | MEDIUM |

---

## 1. Infrastructure Topology Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SAHOOL v16.0.0 Infrastructure                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │  PostgreSQL │◄───│  PgBouncer  │◄───│  39+ Svcs   │                  │
│  │  (PostGIS)  │    │  (Pool 250) │    │             │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│        ▲                                      │                          │
│        │                                      ▼                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │    Vault    │    │    NATS     │◄───│  Event Bus  │                  │
│  │  (Secrets)  │    │ (JetStream) │    │             │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│                           ▲                                              │
│                           │                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │    Redis    │    │    MQTT     │    │   Qdrant    │                  │
│  │  (Cache)    │    │   (IoT)     │    │  (Vector)   │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                         Kong API Gateway :8000                       ││
│  │  Routes: 68 services | Plugins: CORS, Prometheus, Rate-Limit, JWT   ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Critical Database Issues | مشاكل قاعدة البيانات الحرجة

### 2.1 SSL Upgrade Rejection (3 services)

**Root Cause:** PgBouncer rejects SSL upgrade attempts. Services using asyncpg without `sslmode=disable` fail.

| Service | Error | Fix Required |
|---------|-------|--------------|
| sahool-ai-agents-service | SSL upgrade rejected | Add `?sslmode=disable` |
| sahool-crm-service | SSL upgrade rejected | Add `?sslmode=disable` |
| sahool-lowcode-engine | SSL upgrade rejected | Add `?sslmode=disable` |

### 2.2 Connection Refused (7 services)

**Root Cause:** Services starting before PgBouncer is healthy OR missing depends_on condition.

| Service | Error | Fix Required |
|---------|-------|--------------|
| sahool-crop-intelligence-service | [Errno 111] Connection refused | Verify depends_on |
| sahool-indicators-service | [Errno 111] Connection refused | Verify depends_on |
| sahool-edge-orchestrator-service | [Errno 111] Connection refused | Add pgbouncer dependency |
| sahool-ground-vision-service | Connect call failed | Add pgbouncer dependency |
| sahool-marketplace | Can't reach database | Verify pgbouncer health |
| sahool-research-core | Can't reach database | Verify pgbouncer health |
| sahool-field-management-service | Connection failed | Verify pgbouncer health |

### 2.3 Wrong Database Scheme (1 service)

| Service | Error | Fix Required |
|---------|-------|--------------|
| sahool-field-chat | Unknown DB scheme: postgresql | Change to `postgresql+asyncpg://` |

### 2.4 Missing SSL Mode Parameter (3 services)

| Service | Port | Current DATABASE_URL | Fix |
|---------|------|---------------------|-----|
| provider-config | 8104 | No sslmode | Add `?sslmode=disable` |
| ndvi-engine | 8107 | No sslmode | Add `?sslmode=disable` |
| weather-core | 8108 | No sslmode | Add `?sslmode=disable` |

---

## 3. NATS Messaging Issues | مشاكل الرسائل NATS

### 3.1 Invalid URL Format (1 service)

**Root Cause:** Node.js nats library doesn't support credentials in URL format.

| Service | Error | Current Config | Fix |
|---------|-------|---------------|-----|
| marketplace-service | Invalid URL | `nats://user:pass@host:4222` | Parse separately |

**Code Fix Required:**
```typescript
// BEFORE (broken)
const nc = await connect({
  servers: process.env.NATS_URL  // nats://user:pass@nats:4222 - INVALID
});

// AFTER (fixed)
const nc = await connect({
  servers: "nats://nats:4222",
  user: process.env.NATS_USER,
  pass: process.env.NATS_PASSWORD
});
```

### 3.2 Connection Refused (4 services)

**Root Cause:** NATS service not running or services starting before NATS is healthy.

| Service | Status | Fix |
|---------|--------|-----|
| sahool-ai-agents-service | 51+ retry attempts | Verify depends_on: nats: condition: service_healthy |
| sahool-crm-service | 12+ retry attempts | Add NATS dependency |
| sahool-lowcode-engine | 2+ retry attempts | Add NATS dependency |

### 3.3 Missing NATS Dependency (1 service)

| Service | Error | Fix |
|---------|-------|-----|
| sahool-virtual-sensors | NATS package not installed | Add `nats-py` to requirements.txt |

---

## 4. Kong Gateway Issues | مشاكل بوابة Kong

### 4.1 Orphaned Services (Remove from kong.yml)

These services are configured in Kong but don't exist in docker-compose:

```yaml
# REMOVE THESE FROM kong.yml:
- agent-registry
- ai-agents-core
- audit-service
- field-core
- field-service
- globalgap-compliance
- knowledge-graph
- logistics-service
- ussd-gateway
- yield-engine
```

### 4.2 Route Conflicts

| Conflicting Path | Services | Resolution |
|------------------|----------|------------|
| `/api/v1/alerts` | notification-service, alert-service | Assign to notification-service only |
| `/api/v1/field-core` | field-intelligence, field-core | Remove field-core (deprecated) |

### 4.3 Missing Routes

| Service | Port | Missing Route |
|---------|------|---------------|
| ground-vision-service | 8182 | Add `/api/v1/ground-vision` |

### 4.4 Security Gaps

- **JWT Coverage:** Only 5/64 services (8%) protected
- **Rate Limiting:** Only 7/64 services (11%) have limits
- **CORS:** Wildcard origin (development mode)

---

## 5. Deprecated Services | الخدمات المهملة

| Deprecated Service | Profile | Replacement | Port |
|--------------------|---------|-------------|------|
| field-ops | deprecated | field-management-service | 3000 |
| agro-advisor | deprecated, legacy | advisory-service | 8093 |
| ndvi-engine | deprecated, legacy | vegetation-analysis-service | 8090 |
| weather-core | deprecated, legacy | weather-service | 8092 |
| satellite-service | (active but deprecated) | vegetation-analysis-service | 8090 |
| fertilizer-advisor | (active but deprecated) | advisory-service | 8093 |
| crop-health-ai | (active but deprecated) | crop-intelligence-service | 8095 |

**Action:** Ensure deprecated services are not in default profile and Kong routes point to replacements.

---

## 6. GPU Services | خدمات GPU

| Service | Profile | GPU Requirement | Fallback |
|---------|---------|-----------------|----------|
| ollama | gpu | NVIDIA (required) | Service won't start |
| yolo26-vision-service | - | NVIDIA (optional) | CPU fallback available |
| ground-vision-service | - | NVIDIA (required) | No fallback |

**Recommendation:** Add health checks that verify GPU availability before marking service healthy.

---

## 7. Port Allocation | تخصيص المنافذ

### Verified Port Map (No Conflicts Found)

| Port Range | Services |
|------------|----------|
| 3000-3025 | Node.js services |
| 8080-8199 | Python services |
| 8200 | Vault |
| 4222, 6222, 8222 | NATS |
| 5432, 6432 | PostgreSQL, PgBouncer |
| 6379-6380 | Redis |
| 6333-6334 | Qdrant |
| 8000-8001 | Kong |

---

## 8. Configuration Patches | تصحيحات التكوين

### 8.1 docker-compose.yml Patches

See separate file: `docker-compose.patches.yml`

### 8.2 kong.yml Patches

See separate file: `infrastructure/gateway/kong/kong.yml.patched`

### 8.3 Service Code Fixes

See separate file: `SERVICE_CODE_FIXES.md`

---

## 9. Recommended Startup Order

```bash
# Phase 1: Infrastructure
docker compose up -d postgres
sleep 10
docker compose up -d pgbouncer redis nats vault

# Phase 2: Wait for health
docker compose exec postgres pg_isready
docker compose exec redis redis-cli ping
docker compose exec nats wget -q --spider http://localhost:8222/healthz

# Phase 3: Core Services
docker compose up -d kong user-service notification-service

# Phase 4: Application Services
docker compose up -d field-management-service advisory-service weather-service

# Phase 5: Intelligence Services
docker compose up -d vegetation-analysis-service crop-intelligence-service

# Phase 6: Optional (GPU)
docker compose --profile gpu up -d ollama yolo26-vision-service
```

---

## 10. Monitoring Checklist

- [ ] PgBouncer pool utilization < 80%
- [ ] NATS message backlog < 10000
- [ ] Redis memory usage < 400MB
- [ ] Kong request latency p99 < 500ms
- [ ] All healthchecks passing

---

**Report End**
