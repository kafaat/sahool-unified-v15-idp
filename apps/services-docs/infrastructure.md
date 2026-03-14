# SAHOOL Platform - Infrastructure Services Documentation

## Overview

This document provides comprehensive documentation for the core infrastructure services that power the SAHOOL Agricultural Intelligence Platform. These services provide the foundational data persistence, messaging, connection pooling, and API routing capabilities required by the 57+ microservices in the platform.

**Version**: 16.0.0
**Last Updated**: 2026-01-25

---

## Table of Contents

1. [PostgreSQL + PostGIS](#1-postgresql--postgis)
2. [PgBouncer (Connection Pooler)](#2-pgbouncer-connection-pooler)
3. [NATS (Message Queue)](#3-nats-message-queue)
4. [Kong (API Gateway)](#4-kong-api-gateway)
5. [Service Dependencies](#5-service-dependencies)
6. [Health Check Endpoints](#6-health-check-endpoints)
7. [Recommended Optimizations](#7-recommended-optimizations)
8. [Security Considerations](#8-security-considerations)
9. [Configuration Files Reference](#9-configuration-files-reference)

---

## 1. PostgreSQL + PostGIS

### Description

PostgreSQL 16 with PostGIS 3.4 extension serves as the primary relational database for the SAHOOL platform. PostGIS enables spatial/geospatial operations essential for field boundary management, mapping, and location-based features.

### Docker Image

```
postgis/postgis:16-3.4
```

### Container Name

```
sahool-postgres
```

### Ports

| Port | Binding | Description |
|------|---------|-------------|
| 5432 | 127.0.0.1:5432 | PostgreSQL client connections (localhost only) |

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | Yes | `sahool` | Database superuser name |
| `POSTGRES_PASSWORD` | **Required** | - | Database password (must be set) |
| `POSTGRES_DB` | Yes | `sahool` | Default database name |
| `PGDATA` | No | `/var/lib/postgresql/data/pgdata` | Data directory path |
| `POSTGRES_PORT` | No | `5432` | Host port binding |
| `POSTGRES_SSL_MODE` | Yes (prod) | `require` | SSL mode (require/verify-full) |

### Volumes

| Volume | Path | Description |
|--------|------|-------------|
| `postgres_data` | `/var/lib/postgresql/data` | Persistent database storage |
| Init Scripts | `/docker-entrypoint-initdb.d` | Initialization SQL scripts |
| Migrations | `/migrations` | Database migration scripts |

### Initialization Scripts

Located at `/home/user/sahool-unified-v15-idp/infrastructure/core/postgres/init/`:

1. **00-init-sahool.sql** - Complete database initialization including:
   - Extensions: `uuid-ossp`, `postgis`, `postgis_topology`, `pg_trgm`, `pgcrypto`
   - Custom ENUM types for user roles, field status, crop status, etc.
   - Core tables: tenants, users, fields, crops, tasks, alerts, IoT devices
   - NDVI/Satellite tables for vegetation analysis
   - Weather tables for forecasts and records
   - Marketplace tables for products, orders, wallets
   - Research tables for experiments and trials
   - Chat tables for field-level communication
   - Demo data for development/testing

2. **01-research-expansion.sql** - Research module schema expansion

3. **02-pgbouncer-user.sql** - PgBouncer authentication setup:
   - Creates `pgbouncer` schema
   - Creates `pgbouncer.get_auth()` function for SCRAM-SHA-256 authentication
   - Grants `pg_monitor` role for auth_query access

### Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-sahool} -d ${POSTGRES_DB:-sahool}"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

### Connection URLs

```bash
# Standard connection via PgBouncer (recommended for services)
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool?sslmode=require&pgbouncer=true&connection_limit=8

# Direct connection (for migrations only)
DATABASE_URL_DIRECT=postgresql://sahool:password@postgres:5432/sahool?sslmode=require
```

### Key Features

- **PostGIS 3.4**: Full geospatial support for field boundaries (POLYGON), center points (POINT)
- **UUID Support**: All primary keys use UUID (`uuid_generate_v4()`)
- **SCRAM-SHA-256**: Modern password authentication (PostgreSQL 16 default)
- **Row-Level Security**: Tenant isolation support via RLS policies
- **Automatic Triggers**: `updated_at` timestamp management, field area calculation

---

## 2. PgBouncer (Connection Pooler)

### Description

PgBouncer provides connection pooling for PostgreSQL, preventing connection exhaustion under high load from 39+ microservices. Optimized for transaction pooling mode with SCRAM-SHA-256 authentication.

### Docker Image

```
edoburu/pgbouncer:latest
```

### Container Name

```
sahool-pgbouncer
```

### Ports

| Port | Binding | Description |
|------|---------|-------------|
| 6432 | 127.0.0.1:6432 | PgBouncer client connections (localhost only) |

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | Yes | `postgres` | PostgreSQL hostname |
| `DB_PORT` | Yes | `5432` | PostgreSQL port |
| `DB_USER` | Yes | `sahool` | Database username (auth_user) |
| `DB_PASSWORD` | **Required** | - | Database password |
| `DB_NAME` | Yes | `sahool` | Database name |
| `POOL_MODE` | No | `transaction` | Pool mode (transaction/session/statement) |
| `MAX_DB_CONNECTIONS` | No | `250` | Max connections to PostgreSQL |
| `DEFAULT_POOL_SIZE` | No | `30` | Default pool size per user/db pair |
| `MIN_POOL_SIZE` | No | `10` | Minimum pool size (warm connections) |
| `RESERVE_POOL_SIZE` | No | `10` | Reserve pool for maintenance |
| `MAX_CLIENT_CONN` | No | `800` | Max client connections to PgBouncer |
| `CLIENT_IDLE_TIMEOUT` | No | `900` | Client idle timeout (seconds) |
| `SERVER_IDLE_TIMEOUT` | No | `600` | Server idle timeout (seconds) |
| `QUERY_TIMEOUT` | No | `120` | Query timeout (seconds) |
| `QUERY_WAIT_TIMEOUT` | No | `30` | Query wait timeout (seconds) |
| `ADMIN_USERS` | No | `pgbouncer_admin` | Admin console users |
| `STATS_USERS` | No | `pgbouncer_stats` | Stats viewing users |

### Configuration File

Located at `/home/user/sahool-unified-v15-idp/infrastructure/core/pgbouncer/pgbouncer.ini`

#### Key Settings

```ini
[databases]
sahool = host=postgres port=5432 dbname=sahool
* = host=postgres port=5432

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_query = SELECT usename, passwd FROM pgbouncer.get_auth($1)
auth_user = sahool
auth_file = /etc/pgbouncer/runtime/userlist.txt

; Pool Configuration (Optimized for 39+ services)
pool_mode = transaction
max_db_connections = 250
default_pool_size = 30
min_pool_size = 10
reserve_pool_size = 10
max_client_conn = 800

; Timeouts
server_idle_timeout = 600
client_idle_timeout = 900
query_timeout = 120
query_wait_timeout = 30
server_lifetime = 3600

; Health Check
server_check_delay = 30
server_check_query = SELECT 1

; Admin Console
admin_users = pgbouncer_admin
stats_users = pgbouncer_stats
ignore_startup_parameters = extra_float_digits,jit,statement_timeout

; Security (TLS disabled for dev, enable for prod)
server_tls_sslmode = disable
client_tls_sslmode = disable
```

### Volumes

| Volume | Path | Description |
|--------|------|-------------|
| `pgbouncer.ini` | `/etc/pgbouncer/pgbouncer.ini:ro` | Configuration file |
| `entrypoint.sh` | `/entrypoint-custom.sh:ro` | Custom startup script |
| `pgbouncer-userlist` | `/etc/pgbouncer/runtime` | Generated userlist.txt |

### Entrypoint Script

The custom entrypoint (`entrypoint.sh`) performs:
1. Waits for PostgreSQL to be ready (using netcat)
2. Generates `userlist.txt` with plaintext passwords from environment
3. Verifies configuration files
4. Starts PgBouncer with the configuration

### Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "nc -z localhost 6432 || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 256M
    reservations:
      cpus: '0.1'
      memory: 64M
```

### Pool Mode Selection

| Mode | Use Case | Limitations |
|------|----------|-------------|
| `transaction` | Web applications (recommended) | No prepared statements, temp tables |
| `session` | Long-running sessions | Higher connection usage |
| `statement` | Simple queries only | No transactions |

### Admin Console Commands

Connect to admin console:
```bash
psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer
```

Useful commands:
```sql
SHOW POOLS;
SHOW STATS;
SHOW CLIENTS;
SHOW SERVERS;
SHOW CONFIG;
RELOAD;
```

---

## 3. NATS (Message Queue)

### Description

NATS 2.10.24 with JetStream provides high-performance messaging for the SAHOOL platform's 4-layer event architecture. Supports pub/sub, request-reply, and persistent streams for reliable message delivery.

### Docker Image

```
nats:2.10.24-alpine
```

### Container Name

```
sahool-nats
```

### Ports

| Port | Binding | Description |
|------|---------|-------------|
| 4222 | 0.0.0.0:4222 | Client connections |
| 8222 | 127.0.0.1:8222 | HTTP monitoring |
| 6222 | Internal | Cluster routing (HA mode) |
| 7222 | Internal | Gateway connections (multi-region) |

### Environment Variables

#### Basic Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NATS_USER` | Yes | `sahool_app` | Application service username |
| `NATS_PASSWORD` | **Required** | - | Application service password (32+ chars) |
| `NATS_ADMIN_USER` | Yes | `nats_admin` | Administrator username |
| `NATS_ADMIN_PASSWORD` | **Required** | - | Administrator password |
| `NATS_MONITOR_USER` | Yes | `nats_monitor` | Monitoring username (read-only) |
| `NATS_MONITOR_PASSWORD` | **Required** | - | Monitoring password |
| `NATS_SYSTEM_USER` | Yes | `nats_system` | System account username |
| `NATS_SYSTEM_PASSWORD` | **Required** | - | System account password |

#### Cluster Configuration (HA Mode)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NATS_CLUSTER_USER` | Yes (HA) | `nats_cluster` | Cluster authentication user |
| `NATS_CLUSTER_PASSWORD` | Yes (HA) | - | Cluster authentication password |
| `NATS_GATEWAY_USER` | No | `gateway_user` | Gateway (multi-region) user |
| `NATS_GATEWAY_PASSWORD` | No | - | Gateway password |
| `NATS_JETSTREAM_KEY` | Yes (secure) | - | 32-byte base64 encryption key |

#### TLS Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NATS_TLS_ENABLED` | Yes (prod) | `false` | Enable TLS encryption |
| `NATS_TLS_PORT` | No | `4223` | TLS client port |
| `NATS_TLS_CERT` | Yes (TLS) | - | Path to TLS certificate |
| `NATS_TLS_KEY` | Yes (TLS) | - | Path to TLS private key |
| `NATS_TLS_CA` | Yes (TLS) | - | Path to CA certificate |

### Configuration Files

#### Development Configuration

Located at `/home/user/sahool-unified-v15-idp/config/nats/nats.conf`

```conf
server_name: sahool-nats
listen: 0.0.0.0:4222
http_port: 8222

jetstream {
    store_dir: /data
    max_memory_store: 1GB
    max_file_store: 10GB
}

authorization {
    users = [
        {
            user: $NATS_ADMIN_USER
            password: $NATS_ADMIN_PASSWORD
            permissions = { publish = { allow = [">"] }, subscribe = { allow = [">"] } }
        },
        {
            user: $NATS_USER
            password: $NATS_PASSWORD
            permissions = {
                publish = { allow = ["sahool.>", "field.>", "weather.>", "iot.>", "notification.>", "marketplace.>", "billing.>", "chat.>", "alert.>", "_INBOX.>", "$JS.API.>"] }
                subscribe = { allow = ["sahool.>", "field.>", "weather.>", "iot.>", "notification.>", "marketplace.>", "billing.>", "chat.>", "alert.>", "_INBOX.>", "$JS.API.>"] }
            }
        },
        {
            user: $NATS_MONITOR_USER
            password: $NATS_MONITOR_PASSWORD
            permissions = { publish = { deny = [">"] }, subscribe = { allow = [">"] } }
        }
    ]
}

max_connections: 1000
max_payload: 8MB
max_pending: 64MB
ping_interval: 120s
```

#### Secure/Production Configuration

Located at `/home/user/sahool-unified-v15-idp/config/nats/nats-secure.conf`

Additional security features:
- TLS enforcement with certificate verification
- JetStream encryption at rest (AES-256)
- Per-user connection limits
- System account for monitoring
- Cluster TLS configuration
- Modern cipher suites (TLS 1.2+)

### Volumes

| Volume | Path | Description |
|--------|------|-------------|
| `nats_data` | `/data` | JetStream persistent storage |
| Config | `/etc/nats/nats.conf:ro` | Configuration file |
| Certs | `/etc/nats/certs:ro` | TLS certificates (production) |

### Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -q -O /dev/null http://localhost:8222/healthz || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

### Event Architecture (4-Layer)

| Layer | Services | Subjects |
|-------|----------|----------|
| **Acquisition** | satellite-service, iot-service, weather-service | `iot.>`, `weather.>` |
| **Intelligence** | indicators-service, ndvi-processor, crop-intelligence | `sahool.>` |
| **Decision** | advisory-service, irrigation-smart, yield-engine | `alert.>`, `notification.>` |
| **Business** | notification-service, billing-core, marketplace | `marketplace.>`, `billing.>`, `chat.>` |

### Subject Pattern

```
sahool.{tenant_id}.{event_type}
```

Example subjects:
- `sahool.tenant123.field.created`
- `iot.sensor.reading`
- `alert.weather.frost`

### High Availability (3-Node Cluster)

Docker Compose for HA: `/home/user/sahool-unified-v15-idp/infrastructure/nats/docker-compose.nats-cluster.yml`

| Node | Client Port | Monitor Port | Cluster Port | Gateway Port |
|------|-------------|--------------|--------------|--------------|
| Node 1 | 4222 | 8222 | 6222 | 7222 |
| Node 2 | 4223 | 8223 | 6223 | 7223 |
| Node 3 | 4224 | 8224 | 6224 | 7224 |

Client connection string for HA:
```
nats://nats-node1:4222,nats://nats-node2:4222,nats://nats-node3:4222
```

### Monitoring Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8222/healthz` | Health check |
| `http://localhost:8222/varz` | Server variables/stats |
| `http://localhost:8222/connz` | Active connections |
| `http://localhost:8222/routez` | Cluster routes |
| `http://localhost:8222/subsz` | Subscriptions |
| `http://localhost:8222/jsz` | JetStream info |

---

## 4. Kong (API Gateway)

### Description

Kong 3.9 serves as the API gateway for the SAHOOL platform, providing routing, authentication, rate limiting, CORS handling, and observability for all microservices. Runs in DB-less (declarative) mode for simplified deployment.

### Docker Image

```
kong:3.9
```

### Container Name

```
sahool-kong
```

### Ports

| Port | Binding | Description |
|------|---------|-------------|
| 8000 | 0.0.0.0:8000 | HTTP Proxy |
| 8443 | 0.0.0.0:8443 | HTTPS Proxy |
| 8001 | 127.0.0.1:8001 | Admin API HTTP (localhost only) |
| 8444 | 127.0.0.1:8444 | Admin API HTTPS (localhost only) |

### Environment Variables

#### Core Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KONG_DATABASE` | No | `off` | Database mode (off = DB-less) |
| `KONG_DECLARATIVE_CONFIG` | Yes | `/kong/declarative/kong.yml` | Declarative config path |
| `KONG_PROXY_ACCESS_LOG` | No | `/dev/stdout` | Proxy access log output |
| `KONG_ADMIN_ACCESS_LOG` | No | `/dev/stdout` | Admin access log output |
| `KONG_PROXY_ERROR_LOG` | No | `/dev/stderr` | Proxy error log output |
| `KONG_ADMIN_ERROR_LOG` | No | `/dev/stderr` | Admin error log output |
| `KONG_ADMIN_LISTEN` | No | `127.0.0.1:8001` | Admin API listen address |
| `KONG_LOG_LEVEL` | No | `notice` | Log level (debug/info/notice/warn/error) |

#### PostgreSQL Mode (Alternative)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KONG_DATABASE` | Yes | `postgres` | Enable PostgreSQL mode |
| `KONG_PG_HOST` | Yes | `kong-database` | PostgreSQL hostname |
| `KONG_PG_PORT` | No | `5432` | PostgreSQL port |
| `KONG_PG_DATABASE` | Yes | `kong` | Kong database name |
| `KONG_PG_USER` | Yes | `kong` | Kong database user |
| `KONG_PG_PASSWORD` | **Required** | - | Kong database password |

#### DNS & Service Discovery

| Variable | Default | Description |
|----------|---------|-------------|
| `KONG_DNS_RESOLVER` | `127.0.0.11:53` | Docker DNS resolver |
| `KONG_DNS_ORDER` | `LAST,SRV,A,CNAME` | DNS resolution order |
| `KONG_DNS_STALE_TTL` | `4` | Stale DNS cache time (seconds) |
| `KONG_DNS_NOT_FOUND_TTL` | `1` | Negative cache time |
| `KONG_DNS_ERROR_TTL` | `1` | Error cache time |

#### Performance Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `KONG_NGINX_WORKER_PROCESSES` | `4` | Worker processes count (fixed from 'auto') |
| `KONG_NGINX_WORKER_CONNECTIONS` | `4096` | Connections per worker |
| `KONG_UPSTREAM_KEEPALIVE_POOL_SIZE` | `60` | Upstream connection pool |
| `KONG_UPSTREAM_KEEPALIVE_MAX_REQUESTS` | `100` | Max requests per connection |
| `KONG_MEM_CACHE_SIZE` | `128m` | In-memory cache size |
| `KONG_DB_UPDATE_FREQUENCY` | `5` | Config refresh interval |

#### Security Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `KONG_HEADERS` | `server_tokens=off` | Hide server version |
| `KONG_TRUSTED_IPS` | `0.0.0.0/0,::/0` | Trusted IP ranges |
| `KONG_ENFORCE_RBAC` | `on` | Enable RBAC |

### Declarative Configuration

Located at `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong/kong.yml`

#### Global Plugins

```yaml
plugins:
  # CORS - Cross-Origin Resource Sharing
  - name: cors
    config:
      origins: ["*"]  # Restrict in production
      methods: [GET, POST, PUT, PATCH, DELETE, OPTIONS]
      headers: [Accept, Authorization, Content-Type, X-Request-Id, X-Correlation-Id]
      credentials: false
      max_age: 3600

  # Prometheus Metrics
  - name: prometheus
    config: {}

  # Request Correlation ID
  - name: correlation-id
    config:
      header_name: X-Correlation-Id
      generator: uuid#counter
      echo_downstream: true

  # Request Size Limiting
  - name: request-size-limiting
    config:
      allowed_payload_size: 10  # MB
      size_unit: megabytes
```

#### Service Routing Examples

```yaml
services:
  # Field Management Service (Node.js)
  - name: field-management-service
    host: field-management-service
    port: 3000
    protocol: http
    routes:
      - name: field-management-service-route
        paths: ["/api/v1/fields", "/api/v1/field", "/field"]
        strip_path: true
        protocols: ["http", "https"]

  # User Service - Public Auth Routes (no JWT required)
  - name: user-service-public
    host: user-service
    port: 3025
    protocol: http
    routes:
      - name: user-service-auth-public
        paths:
          - /api/v1/auth/login
          - /api/v1/auth/register
          - /api/v1/auth/forgot-password
        strip_path: false
    plugins:
      - name: rate-limiting
        config:
          minute: 30
          hour: 500
          policy: local

  # Weather Service (Python/FastAPI)
  - name: weather-service
    host: weather-service
    port: 8092
    protocol: http
    routes:
      - name: weather-service-route
        paths: ["/api/v1/weather", "/weather"]
        strip_path: true
```

### Volumes

| Volume | Path | Description |
|--------|------|-------------|
| Config | `/kong/declarative/kong.yml:ro` | Declarative configuration |
| Packages | `/etc/kong/kong-packages.yml:ro` | Package-specific routes |

### Health Check

```yaml
healthcheck:
  test: ["CMD", "kong", "health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

### Rate Limiting Tiers

| Tier | Requests/min | Requests/hour | Burst |
|------|-------------|---------------|-------|
| Free | 30 | 500 | 5 |
| Standard | 60 | 2,000 | 10 |
| Premium | 120 | 5,000 | 20 |
| Internal | 1,000 | 50,000 | 100 |

### Configured Services (62 Total)

#### Node.js Services

| Service | Host | Port | Routes |
|---------|------|------|--------|
| field-management-service | field-management-service | 3000 | `/api/v1/fields`, `/field` |
| user-service | user-service | 3025 | `/api/v1/auth/*`, `/api/v1/users` |
| marketplace-service | marketplace-service | 3010 | `/api/v1/marketplace` |
| research-core | research-core | 3015 | `/api/v1/research` |
| disaster-assessment | disaster-assessment | 3020 | `/api/v1/disaster` |
| iot-service | iot-service | 8117 | `/api/v1/iot` |
| community-chat | community-chat | 8097 | `/api/v1/community` |

#### Python Services (FastAPI)

| Service | Host | Port | Routes |
|---------|------|------|--------|
| weather-service | weather-service | 8092 | `/api/v1/weather` |
| advisory-service | advisory-service | 8093 | `/api/v1/advisory`, `/api/v1/fertilizer` |
| irrigation-smart | irrigation-smart | 8094 | `/api/v1/irrigation` |
| crop-intelligence-service | crop-intelligence-service | 8095 | `/api/v1/crop-health` |
| vegetation-analysis-service | vegetation-analysis-service | 8090 | `/api/v1/vegetation`, `/api/v1/ndvi` |
| notification-service | notification-service | 8110 | `/api/v1/notifications` |
| task-service | task-service | 8103 | `/api/v1/tasks` |
| billing-core | billing-core | 8089 | `/api/v1/billing` |

### Admin API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | List all endpoints |
| `GET /services` | List all services |
| `GET /routes` | List all routes |
| `GET /plugins` | List all plugins |
| `GET /status` | Kong status |
| `GET /config` | Current configuration |

---

## 5. Service Dependencies

### Dependency Graph

```
                    ┌─────────────┐
                    │   Kong      │
                    │ (Gateway)   │
                    └─────┬───────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
┌─────────────────┐ ┌──────────┐ ┌─────────────────┐
│ Node.js Services│ │  Python  │ │   WebSocket     │
│ (NestJS/Prisma) │ │ Services │ │   Gateway       │
└────────┬────────┘ └────┬─────┘ └────────┬────────┘
         │               │                │
         └───────────────┼────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       ┌──────────────┐      ┌────────────┐
       │  PgBouncer   │      │    NATS    │
       │ (Pooling)    │      │ (Messaging)│
       └──────┬───────┘      └────────────┘
              │
              ▼
       ┌──────────────┐
       │  PostgreSQL  │
       │  (PostGIS)   │
       └──────────────┘
```

### Startup Order

1. **PostgreSQL** - Database must be healthy first
2. **PgBouncer** - Depends on PostgreSQL being healthy
3. **NATS** - Independent, can start in parallel with PostgreSQL
4. **Kong** - Depends on PostgreSQL being healthy (for config only)
5. **Microservices** - Depend on PgBouncer and NATS

### Docker Compose Dependencies

```yaml
services:
  postgres:
    # No dependencies - starts first

  pgbouncer:
    depends_on:
      postgres:
        condition: service_healthy

  nats:
    # No dependencies - can start in parallel

  kong:
    depends_on:
      postgres:
        condition: service_healthy

  # Example microservice
  field-management-service:
    depends_on:
      pgbouncer:
        condition: service_healthy
      nats:
        condition: service_healthy
```

---

## 6. Health Check Endpoints

### Infrastructure Health Endpoints

| Service | Endpoint | Method | Expected Response |
|---------|----------|--------|-------------------|
| PostgreSQL | `pg_isready -U sahool -d sahool` | Shell | Exit code 0 |
| PgBouncer | `nc -z localhost 6432` | Shell | Connection success |
| NATS | `http://localhost:8222/healthz` | GET | HTTP 200 |
| Kong | `kong health` | Shell | Exit code 0 |

### Infrastructure Monitoring Endpoints

| Service | Endpoint | Description |
|---------|----------|-------------|
| NATS | `http://localhost:8222/varz` | Server variables |
| NATS | `http://localhost:8222/jsz` | JetStream status |
| NATS | `http://localhost:8222/connz` | Active connections |
| Kong | `http://localhost:8001/status` | Gateway status |
| Kong | `http://localhost:8000/health` | Proxy health |

### Health Check Script

```bash
#!/bin/bash
# Infrastructure health check

echo "Checking PostgreSQL..."
docker exec sahool-postgres pg_isready -U sahool -d sahool

echo "Checking PgBouncer..."
nc -z localhost 6432 && echo "PgBouncer: OK" || echo "PgBouncer: FAILED"

echo "Checking NATS..."
curl -s http://localhost:8222/healthz && echo "NATS: OK" || echo "NATS: FAILED"

echo "Checking Kong..."
curl -s http://localhost:8000/health && echo "Kong: OK" || echo "Kong: FAILED"
```

---

## 7. Recommended Optimizations

### PostgreSQL Optimizations

```sql
-- Recommended postgresql.conf settings for SAHOOL workload

# Memory Configuration
shared_buffers = 4GB                  # 25% of available RAM
effective_cache_size = 12GB           # 75% of available RAM
maintenance_work_mem = 1GB
work_mem = 64MB

# Connection Settings (PgBouncer handles pooling)
max_connections = 300                 # Above PgBouncer max_db_connections
superuser_reserved_connections = 5

# WAL Configuration
wal_buffers = 64MB
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 1GB

# Query Planning
random_page_cost = 1.1                # SSD storage
effective_io_concurrency = 200        # SSD storage
default_statistics_target = 200

# Parallelism
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

# Logging
log_min_duration_statement = 1000     # Log slow queries (1s+)
log_checkpoints = on
log_connections = off                 # PgBouncer logs these
log_disconnections = off

# PostGIS Specific
geqo_threshold = 14                   # Better spatial query planning
```

### PgBouncer Optimizations

```ini
; Production optimizations for pgbouncer.ini

[pgbouncer]
; Increase pool sizes for high-traffic services
default_pool_size = 50
min_pool_size = 20
reserve_pool_size = 15
max_client_conn = 1500
max_db_connections = 400

; Faster query timeouts for real-time services
query_timeout = 60
query_wait_timeout = 15

; Enable statistics logging
log_stats = 1
stats_period = 30

; Connection health
server_check_delay = 15
server_fast_close = 1
```

### NATS Optimizations

```conf
# Production NATS optimizations

# Increase connection limits
max_connections: 5000
max_pending: 128MB
max_payload: 16MB

# JetStream tuning for high throughput
jetstream {
    max_memory_store: 4GB
    max_file_store: 100GB
    sync_interval: "1m"
}

# Rate limiting per user
connection_limits = {
    max_connections: 200
    max_subscriptions: 1000
}

# Write deadline optimization
write_deadline: 5s
```

### Kong Optimizations

```yaml
# Production Kong environment variables

KONG_NGINX_WORKER_PROCESSES: 8
KONG_NGINX_WORKER_CONNECTIONS: 16384
KONG_UPSTREAM_KEEPALIVE_POOL_SIZE: 200
KONG_UPSTREAM_KEEPALIVE_MAX_REQUESTS: 1000
KONG_UPSTREAM_KEEPALIVE_IDLE_TIMEOUT: 120
KONG_MEM_CACHE_SIZE: 512m
KONG_DB_UPDATE_FREQUENCY: 1

# Enable gzip compression
KONG_NGINX_PROXY_GZIP: "on"
KONG_NGINX_PROXY_GZIP_TYPES: "application/json application/xml text/plain"
```

---

## 8. Security Considerations

### PostgreSQL Security

- **TLS Encryption**: Enforce `sslmode=require` or `sslmode=verify-full` for all connections
- **Password Authentication**: Use SCRAM-SHA-256 (PostgreSQL 16 default)
- **Network Isolation**: Bind to localhost only (`127.0.0.1:5432`)
- **Row-Level Security**: Enable RLS policies for tenant isolation
- **Audit Logging**: Enable `pgaudit` extension for compliance
- **Backup Encryption**: Encrypt all database backups at rest

### PgBouncer Security

- **TLS Encryption**: Enable `server_tls_sslmode = require` and `client_tls_sslmode = require` in production
- **Authentication**: Use SCRAM-SHA-256 with `auth_query` function
- **Network Isolation**: Bind to localhost only (`127.0.0.1:6432`)
- **Admin Access**: Restrict admin console to specific users
- **Userlist Protection**: Generate userlist.txt dynamically (not hardcoded)

```ini
; Production security settings
server_tls_sslmode = require
server_tls_ca_file = /etc/pgbouncer/certs/ca.crt
client_tls_sslmode = require
client_tls_cert_file = /etc/pgbouncer/certs/server.crt
client_tls_key_file = /etc/pgbouncer/certs/server.key
```

### NATS Security

- **TLS Encryption**: Enforce TLS for all connections (client, cluster, gateway)
- **Authentication**: Use username/password or NKeys for enhanced security
- **Authorization**: Implement granular subject-level permissions
- **JetStream Encryption**: Enable AES encryption for data at rest
- **Rate Limiting**: Set per-user connection and message limits
- **System Account**: Use dedicated system account for monitoring

```conf
; Production TLS settings
tls {
    cert_file: "/etc/nats/certs/server.crt"
    key_file: "/etc/nats/certs/server.key"
    ca_file: "/etc/nats/certs/ca.crt"
    verify: true
    verify_and_map: true
    min_version: "1.2"
    cipher_suites: [
        "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
        "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    ]
}
```

### Kong Security

- **Admin API Isolation**: Bind admin API to localhost only
- **HTTPS Enforcement**: Redirect HTTP to HTTPS in production
- **Rate Limiting**: Apply rate limits per consumer/route
- **CORS Configuration**: Specify exact origins (no wildcards) in production
- **Request Size Limits**: Enforce payload size limits
- **JWT Validation**: Enable JWT plugin for protected routes
- **IP Restriction**: Whitelist known IP ranges for sensitive endpoints

```yaml
# Production CORS configuration
plugins:
  - name: cors
    config:
      origins:
        - "https://app.sahool.com"
        - "https://admin.sahool.com"
      credentials: true
      max_age: 3600
```

### Environment Variable Security

- **Never hardcode secrets**: Use environment variables or secrets management
- **Strong passwords**: Minimum 32 characters, randomly generated
- **Rotation policy**: Rotate credentials regularly
- **Secrets management**: Use HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault in production

```bash
# Generate strong passwords
openssl rand -base64 32

# Generate JetStream encryption key
openssl rand -base64 32
```

---

## 9. Configuration Files Reference

### File Locations

| Component | Configuration File | Description |
|-----------|-------------------|-------------|
| PostgreSQL | `infrastructure/core/postgres/init/*.sql` | Init scripts |
| PostgreSQL | `infrastructure/core/postgres/migrations/*.sql` | Migration scripts |
| PgBouncer | `infrastructure/core/pgbouncer/pgbouncer.ini` | Pool configuration |
| PgBouncer | `infrastructure/core/pgbouncer/entrypoint.sh` | Startup script |
| NATS | `config/nats/nats.conf` | Development config |
| NATS | `config/nats/nats-secure.conf` | Production config (TLS) |
| NATS | `config/nats/nats-cluster-node*.conf` | Cluster node configs |
| Kong | `infrastructure/gateway/kong/kong.yml` | Declarative config |
| Kong | `infrastructure/gateway/kong/kong-packages.yml` | Package-specific routes |
| Kong | `infrastructure/gateway/kong/kong-v2-routes.yml` | v2 API routes |
| Docker | `docker/docker-compose.infra.yml` | Infrastructure compose |
| Docker | `infrastructure/nats/docker-compose.nats-cluster.yml` | NATS HA cluster |
| Docker | `infrastructure/gateway/kong/docker-compose.yml` | Kong with PostgreSQL |
| Environment | `.env.example` | Environment template |

### Makefile Commands

```bash
# Start infrastructure only
make infra-up

# Start full development stack
make dev

# View infrastructure logs
make logs-infra

# Check service status
make status

# Database operations
make db-shell        # PostgreSQL shell
make db-migrate      # Run migrations
make db-seed         # Seed demo data
make db-backup       # Create backup
make db-reset        # Reset database (WARNING!)

# Health checks
make health          # Check all services
```

---

## Appendix A: Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep sahool-postgres

# Check PostgreSQL logs
docker logs sahool-postgres

# Test direct connection
psql -h localhost -p 5432 -U sahool -d sahool

# Check PostGIS extension
docker exec sahool-postgres psql -U sahool -c "SELECT PostGIS_Version();"
```

### PgBouncer Connection Issues

```bash
# Check PgBouncer status
docker logs sahool-pgbouncer

# Test PgBouncer connection
psql -h localhost -p 6432 -U sahool -d sahool

# Access admin console
psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer -c "SHOW POOLS;"

# Check pool statistics
psql -h localhost -p 6432 -U pgbouncer_admin pgbouncer -c "SHOW STATS;"
```

### NATS Connection Issues

```bash
# Check NATS health
curl http://localhost:8222/healthz

# Check server info
curl http://localhost:8222/varz | jq .

# Check JetStream status
curl http://localhost:8222/jsz | jq .

# Test NATS connection
nats pub test "hello" -s nats://sahool_app:password@localhost:4222
```

### Kong Routing Issues

```bash
# Check Kong health
curl http://localhost:8001/status

# List all routes
curl http://localhost:8001/routes | jq .

# Test specific route
curl http://localhost:8000/api/v1/health

# Reload configuration
curl -X POST http://localhost:8001/config -F config=@kong.yml
```

---

## Appendix B: Quick Reference

### Connection Strings

```bash
# PostgreSQL via PgBouncer (recommended)
postgresql://sahool:password@pgbouncer:6432/sahool?sslmode=require

# PostgreSQL direct (migrations only)
postgresql://sahool:password@postgres:5432/sahool?sslmode=require

# Redis
redis://:password@redis:6379/0

# NATS
nats://sahool_app:password@nats:4222

# Kong API Gateway
http://kong:8000
```

### Port Summary

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| PostgreSQL | 5432 | 127.0.0.1:5432 | Database |
| PgBouncer | 6432 | 127.0.0.1:6432 | Connection pooling |
| NATS | 4222 | 0.0.0.0:4222 | Messaging |
| NATS Monitor | 8222 | 127.0.0.1:8222 | Monitoring |
| Kong Proxy | 8000 | 0.0.0.0:8000 | API Gateway |
| Kong Admin | 8001 | 127.0.0.1:8001 | Admin API |

### Required Environment Variables

```bash
# Database (REQUIRED)
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=sahool

# Redis (REQUIRED)
REDIS_PASSWORD=<strong_password>

# NATS (REQUIRED)
NATS_USER=sahool_app
NATS_PASSWORD=<strong_password>
NATS_ADMIN_USER=nats_admin
NATS_ADMIN_PASSWORD=<strong_password>

# JWT (REQUIRED)
JWT_SECRET_KEY=<32+_char_secret>
```

---

*Last Updated: 2026-01-25*
*Platform Version: 16.0.0*
*Documentation maintained by SAHOOL Platform Team*
