# 00-intake.md — SAHOOL Platform Repository Analysis
**Timestamp:** 2026-01-09T00:00:00Z
**Platform:** SAHOOL v16.0.0 - National Agricultural Intelligence Platform

---

## 1. Repository Overview

SAHOOL is an **offline-first agricultural operating system** designed for low-connectivity environments in the Middle East. The platform provides:
- Real-time advisory and irrigation management
- Crop health monitoring (NDVI)
- Field operations management
- AI-driven advisory services
- Event-driven architecture with NATS messaging

**Version:** 16.0.0
**Owner:** KAFAAT
**License:** Proprietary

---

## 2. Detected Stack Components

### 2.1 Infrastructure Services (10)

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| postgres | postgis/postgis:16-3.4 | 5432 | PostGIS spatial database |
| pgbouncer | edoburu/pgbouncer:latest | 6432 | Connection pooler |
| redis | redis:7-alpine | 6379/6380 | Cache & session store |
| nats | nats:2.10-alpine | 4222/4223/8222 | Message queue (JetStream) |
| nats-prometheus-exporter | natsio/prometheus-nats-exporter:0.14.0 | 7777 | NATS metrics |
| mqtt | eclipse-mosquitto:2 | 1883/9001 | IoT communication |
| qdrant | qdrant/qdrant:v1.7.4 | 6333/6334 | Vector database |
| kong | kong (separate compose) | 8000/8443 | API Gateway |
| minio | minio | - | Object storage |
| milvus | milvus | - | Vector search |

### 2.2 Application Services (39+)

**Core Services:**
- field-management-service (Node.js/NestJS)
- marketplace-service
- research-core
- chat-service
- billing-core
- user-service

**Intelligence Services:**
- ai-advisor
- crop-intelligence-service
- disaster-assessment
- yield-prediction
- lai-estimation
- crop-growth-model

**Field Operations:**
- field-ops
- field-service
- field-core
- field-chat
- field-intelligence
- vegetation-analysis-service

**IoT & Weather:**
- iot-service
- iot-gateway
- weather-service
- weather-core
- weather-advanced
- virtual-sensors

**Advisory Services:**
- advisory-service
- agro-advisor
- agro-rules
- irrigation-smart
- fertilizer-advisor

**Supporting Services:**
- notification-service
- alert-service
- equipment-service
- task-service
- inventory-service
- ndvi-engine
- ndvi-processor
- crop-health
- ws-gateway
- provider-config
- community-chat
- astronomical-calendar
- mcp-server
- demo-data

---

## 3. Key Configuration Files

### 3.1 Docker Compose Files

| File | Purpose |
|------|---------|
| docker-compose.yml | Main stack (39 services + infra) |
| docker-compose.prod.yml | Production overrides |
| docker-compose.test.yml | Test environment |
| docker-compose.tls.yml | TLS configuration |
| docker/docker-compose.infra.yml | Infrastructure only |
| infrastructure/gateway/kong/docker-compose.yml | Kong gateway stack |
| infrastructure/monitoring/docker-compose.monitoring.yml | Prometheus/Grafana |

### 3.2 Infrastructure Configs

| Config | Location |
|--------|----------|
| PostgreSQL Init | infrastructure/core/postgres/init/ |
| PgBouncer | infrastructure/core/pgbouncer/pgbouncer.ini |
| Redis | infrastructure/redis/redis-secure.conf |
| NATS | config/nats/nats.conf, config/nats/nats-secure.conf |
| MQTT | infrastructure/core/mqtt/mosquitto.conf |
| Kong | infrastructure/gateway/kong/kong.yml |
| TLS Certs | config/certs/ |

### 3.3 Environment Configuration

| File | Purpose |
|------|---------|
| .env.example | Template with all required variables |
| .env.development.template | Development defaults |

---

## 4. Required Environment Variables

### Critical (REQUIRED)

```bash
# Database
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=sahool

# Redis
REDIS_PASSWORD=<secure_password>

# NATS Authentication
NATS_USER=<user>
NATS_PASSWORD=<password>
NATS_ADMIN_USER=<admin>
NATS_ADMIN_PASSWORD=<admin_password>
NATS_MONITOR_USER=<monitor>
NATS_MONITOR_PASSWORD=<monitor_password>
NATS_CLUSTER_USER=<cluster>
NATS_CLUSTER_PASSWORD=<cluster_password>
NATS_SYSTEM_USER=<system>
NATS_SYSTEM_PASSWORD=<system_password>
NATS_JETSTREAM_KEY=<encryption_key>

# JWT
JWT_SECRET_KEY=<32_char_minimum>
JWT_ALGORITHM=HS256
```

---

## 5. Dependency Chain (Critical Path)

```
1. postgres       <- First (database)
2. pgbouncer      <- depends_on: postgres (healthy)
3. redis          <- Independent
4. nats           <- Independent
5. mqtt           <- Independent
6. kong           <- depends_on: postgres
7. Application services <- depends_on: pgbouncer, redis, nats
```

---

## 6. Known Configuration Issues (Pre-Analysis)

### 6.1 Environment Variables
- All required env vars use `${VAR:?error message}` syntax
- Stack will fail to start without proper `.env` file

### 6.2 TLS Certificates
- TLS is required for production but optional for development
- Certs should be at config/certs/
- Non-TLS configs available for development

### 6.3 PgBouncer Authentication
- Health check uses simple port check (auth issues noted in comments)
- TODO: Fix password authentication

---

## 7. Next Steps

1. **Create .env** from .env.example with proper values
2. **Generate TLS certificates** (optional for dev)
3. **Start infrastructure services** first
4. **Verify health checks** pass
5. **Start application services**

---

*Document generated by Code Engineer Agent*
*SAHOOL v16.0.0 - Unified Platform Analysis*
