# SAHOOL Platform - Intake Document

**Generated:** 2026-01-08T20:58:00Z
**Engineer:** Code Engineer Agent
**Environment:** Linux 4.4.0 (Docker sandbox - no Docker runtime available)

---

## 1. Repository Overview

**Project:** SAHOOL v16.0.0 Unified Agricultural Platform
**Description:** Complete platform deployment with 39+ microservices + infrastructure
**Primary Language:** Python (FastAPI), Node.js (NestJS)
**Architecture:** Microservices with API Gateway (Kong)

---

## 2. Docker Compose Files Detected

### Primary Compose Files
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Main unified stack (39+ services) |
| `docker-compose.prod.yml` | Production overrides |
| `docker-compose.ha.yml` | High-availability configuration |
| `docker-compose.redis-ha.yml` | Redis HA cluster |
| `docker-compose.test.yml` | Testing environment |
| `docker-compose.telemetry.yml` | Observability stack |
| `docker-compose.tls.yml` | TLS configuration |
| `docker-compose.walg.yml` | WAL-G backup configuration |

### Infrastructure-Specific Compose Files
| File | Purpose |
|------|---------|
| `docker/docker-compose.infra.yml` | Infrastructure services |
| `docker/docker-compose.iot.yml` | IoT services |
| `docker/docker-compose.dlq.yml` | Dead Letter Queue |
| `docker/docker-compose.secrets.yml` | Secrets management |
| `infrastructure/gateway/kong/docker-compose.yml` | Kong standalone |
| `infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml` | PgBouncer |
| `infrastructure/core/qdrant/docker-compose.qdrant.yml` | Qdrant Vector DB |
| `infrastructure/core/vault/docker-compose.vault.yml` | HashiCorp Vault |
| `infrastructure/nats/docker-compose.nats-cluster.yml` | NATS cluster |
| `infrastructure/monitoring/docker-compose.monitoring.yml` | Monitoring |

---

## 3. Infrastructure Services (in docker-compose.yml)

### Core Infrastructure
| Service | Image | Port(s) | Dependencies |
|---------|-------|---------|--------------|
| postgres | postgis/postgis:16-3.4 | 5432 | - |
| pgbouncer | edoburu/pgbouncer:latest | 6432 | postgres |
| redis | redis:7-alpine | 6379, 6380 | - |
| nats | nats:2.10-alpine | 4222, 4223, 6222, 8222 | - |
| mqtt | eclipse-mosquitto:2 | 1883, 9001 | - |
| kong | kong:3.4 | 8000, 8001 | redis |

### Vector Databases & AI
| Service | Image | Port(s) | Dependencies |
|---------|-------|---------|--------------|
| qdrant | qdrant/qdrant:v1.7.4 | 6333, 6334 | - |
| etcd | quay.io/coreos/etcd:v3.5.5 | 2379 | - |
| minio | minio/minio:RELEASE.2024-01-16T16-07-38Z | 9000, 9090 | - |
| milvus | milvusdb/milvus:v2.3.3 | 19530, 9091 | etcd, minio |
| ollama | ollama/ollama:0.5.4 | 11434 | - |

---

## 4. Application Services (Active, Non-Deprecated)

### Node.js Services
| Service | Port | Health Endpoint |
|---------|------|-----------------|
| field-management-service | 3000 | /healthz |
| marketplace-service | 3010 | /api/v1/healthz |
| research-core | 3015 | /api/v1/healthz |
| disaster-assessment | 3020 | /api/v1/disasters/health |
| yield-prediction | 3021 | /api/v1/yield/health |
| lai-estimation | 3022 | /api/v1/lai/health |
| crop-growth-model | 3023 | /api/v1/simulation/health |
| chat-service | 8114 | /api/v1/health |
| iot-service | 8117 | /api/v1/health |
| community-chat | 8097 | /healthz |

### Python Services (FastAPI)
| Service | Port | Health Endpoint |
|---------|------|-----------------|
| ws-gateway | 8081 | /healthz |
| billing-core | 8089 | /healthz |
| vegetation-analysis-service | 8090 | /healthz |
| indicators-service | 8091 | /healthz |
| weather-service | 8092 | /healthz |
| advisory-service | 8093 | /healthz |
| irrigation-smart | 8094 | /healthz |
| crop-intelligence-service | 8095 | /healthz |
| yield-prediction-service | 8098 | /healthz |
| field-chat | 8099 | /healthz |
| equipment-service | 8101 | /health |
| code-review-service | 8102 | /health |
| task-service | 8103 | /healthz |
| provider-config | 8104 | /healthz |
| iot-gateway | 8106 | /health |
| notification-service | 8110 | /healthz |
| astronomical-calendar | 8111 | /healthz |
| ai-advisor | 8112 | /healthz |
| alert-service | 8113 | /healthz |
| field-service | 8115 | /healthz |
| inventory-service | 8116 | /healthz |
| ndvi-processor | 8118 | /healthz |
| virtual-sensors | 8119 | /healthz |
| field-intelligence | 8120 | /healthz |
| mcp-server | 8200 | /health |
| agro-rules | N/A | pgrep-based |

---

## 5. Deprecated Services (under `deprecated` or `legacy` profiles)

| Service | Replacement | Port |
|---------|-------------|------|
| field-ops | field-management-service | 8080 |
| agro-advisor | advisory-service | 8105 |
| ndvi-engine | vegetation-analysis-service | 8107 |
| weather-core | weather-service | 8108 |
| crop-health | crop-intelligence-service | 8100 |

---

## 6. Key Configuration Files

### Kong Gateway
- **Primary:** `infrastructure/gateway/kong/kong.yml`
- **Mirror:** `infra/kong/kong.yml`
- **Format:** Kong Declarative Config v3.0
- **Features:**
  - 40+ service routes defined
  - Rate limiting via Redis
  - JWT authentication
  - ACL-based authorization
  - CORS configuration
  - Health check endpoints

### NATS Configuration
- **Directory:** `config/nats/`
- **Primary:** `nats.conf` (development)
- **Secure:** `nats-secure.conf` (production with TLS)
- **Cluster:** `nats-cluster-node{1,2,3}.conf`
- **NKey:** `nats-nkey.conf` (NKey-based auth)

### Redis Configuration
- **Directory:** `infrastructure/redis/`
- **Development:** `redis-docker.conf`
- **Production:** `redis-production.conf`
- **Secure:** `redis-secure.conf` (with ACL & TLS)

### Database
- **Init Scripts:** `infrastructure/core/postgres/init/`
- **PgBouncer:** `infrastructure/core/pgbouncer/pgbouncer.ini`

---

## 7. Environment Configuration

### Required Variables (.env.example)

**Database (REQUIRED):**
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password (MUST change)
- `POSTGRES_DB` - Database name

**Redis (REQUIRED):**
- `REDIS_PASSWORD` - Redis password (MUST change)

**NATS (REQUIRED):**
- `NATS_USER` - NATS application user
- `NATS_PASSWORD` - NATS password
- `NATS_ADMIN_USER` - Admin user
- `NATS_ADMIN_PASSWORD` - Admin password
- `NATS_MONITOR_USER` - Monitor user
- `NATS_MONITOR_PASSWORD` - Monitor password
- `NATS_CLUSTER_USER` - Cluster user
- `NATS_CLUSTER_PASSWORD` - Cluster password
- `NATS_SYSTEM_USER` - System user
- `NATS_SYSTEM_PASSWORD` - System password
- `NATS_JETSTREAM_KEY` - JetStream encryption key

**MinIO (REQUIRED):**
- `MINIO_ROOT_USER` - MinIO admin (min 16 chars)
- `MINIO_ROOT_PASSWORD` - MinIO password (min 16 chars)

**Etcd (REQUIRED):**
- `ETCD_ROOT_USERNAME` - Etcd root user
- `ETCD_ROOT_PASSWORD` - Etcd root password

**JWT (REQUIRED):**
- `JWT_SECRET_KEY` - JWT signing key (min 32 chars)

**Kong JWT Secrets:**
- `STARTER_JWT_SECRET`
- `PROFESSIONAL_JWT_SECRET`
- `ENTERPRISE_JWT_SECRET`
- `RESEARCH_JWT_SECRET`
- `ADMIN_JWT_SECRET`

---

## 8. Networks & Volumes

### Networks
| Network | Driver |
|---------|--------|
| sahool-network | bridge |

### Volumes
| Volume | Purpose |
|--------|---------|
| postgres_data | PostgreSQL data |
| redis_data | Redis persistence |
| nats_data | NATS JetStream data |
| qdrant_data | Qdrant vector data |
| mqtt_data | MQTT broker data |
| mqtt_logs | MQTT logs |
| mqtt_passwd | MQTT passwords |
| kong_logs | Kong access logs |
| ollama_data | Ollama models |
| code_review_logs | Code review logs |
| etcd_data | Etcd metadata |
| minio_data | MinIO object storage |
| milvus_data | Milvus vector data |

---

## 9. Commands to Reproduce Stack

```bash
# Standard startup
docker compose up -d --build

# With deprecated services
docker compose --profile deprecated up -d --build

# With demo data
docker compose --profile demo up -d --build

# Production mode
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With HA
docker compose -f docker-compose.yml -f docker-compose.ha.yml up -d
```

---

## 10. Initial Observations (Pre-Run)

### Potential Issues Identified

1. **Missing .env File**
   - Only `.env.example` exists
   - Required variables have `?` constraint (will fail without values)

2. **Volume Mount Path Discrepancy**
   - Redis config: `./infrastructure/redis/redis-secure.conf`
   - Actual path exists at: `./infrastructure/redis/redis-secure.conf` (OK)

3. **Kong Upstream Mismatches**
   - Kong references `code-review-service:8096` but compose uses port `8102`
   - Kong defines upstreams for services not in compose:
     - user-service:3025
     - agent-registry:8150
     - ai-agents-core:8122
     - globalgap-compliance:8153
     - analytics-service:8154
     - reporting-service:8155
     - integration-service:8156
     - audit-service:8157
     - export-service:8158
     - import-service:8159
     - admin-dashboard:3001
     - monitoring-service:8160
     - logging-service:8161
     - tracing-service:8162
     - cache-service:8163
     - search-service:8164

4. **TLS Certificate Dependencies**
   - Many services expect TLS certs at `./config/certs/`
   - Directory may not exist or be empty

5. **Health Check Inconsistencies**
   - equipment-service uses `/health` vs others using `/healthz`
   - iot-gateway uses `/health` with longer timeout (90s start period)

6. **GPU Dependency**
   - Ollama requires NVIDIA GPU
   - Will fail in non-GPU environments

---

## 11. Next Steps

1. Create `.env` file from `.env.example` with secure values
2. Verify/create TLS certificates directory
3. Fix Kong configuration port mismatches
4. Run compose and capture actual failures
5. Prioritize fixes based on dependency order
