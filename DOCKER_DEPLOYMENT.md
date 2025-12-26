# SAHOOL v16.0.0 Docker Deployment Guide

## Overview

This comprehensive Docker Compose configuration deploys the complete SAHOOL agricultural platform with **44 services** organized into three categories:

- **6 Infrastructure Services**
- **10 Node.js Application Services**
- **28 Python Application Services**

---

## Infrastructure Services (6)

| Service | Image | Ports | Description |
|---------|-------|-------|-------------|
| **postgres** | postgis/postgis:16-3.4 | 5432 | PostGIS spatial database |
| **redis** | redis:7-alpine | 6379 | Cache and session store |
| **nats** | nats:2.10-alpine | 4222, 8222 | Message queue with JetStream |
| **mqtt** | eclipse-mosquitto:2 | 1883, 9001 | IoT device communication |
| **qdrant** | qdrant/qdrant:latest | 6333, 6334 | Vector database for RAG/AI |
| **kong** | kong:3.4 | 8000, 8001 | API Gateway |

---

## Node.js Application Services (10)

| Service | Port | Description |
|---------|------|-------------|
| **field_core** | 3000 | Geospatial field management (PostGIS + Prisma) |
| **marketplace_service** | 3010 | Agricultural marketplace & FinTech |
| **research_core** | 3015 | Scientific research management |
| **disaster_assessment** | 3020 | Agricultural disaster assessment |
| **yield_prediction** | 3021 | ML-based yield prediction |
| **lai_estimation** | 3022 | Leaf Area Index estimation (LAI-TransNet) |
| **crop_growth_model** | 3023 | Crop growth simulation (WOFOST/DSSAT/APSIM) |
| **chat_service** | 8114 | Agricultural chat & messaging |
| **iot_service** | 8117 | IoT device & sensor management |
| **community_chat** | 8097 | Real-time community messaging (Socket.io) |

---

## Python Application Services (28)

### Core Services
| Service | Port | Description |
|---------|------|-------------|
| **field_ops** | 8080 | Field operations management |
| **ws_gateway** | 8081 | WebSocket gateway for real-time updates |
| **billing_core** | 8089 | Subscription & payment management (Stripe, Tharwatt) |

### Satellite & Weather Services
| Service | Port | Description |
|---------|------|-------------|
| **satellite_service** | 8090 | Multi-provider satellite imagery (Sentinel Hub, NASA, Planet) |
| **ndvi_engine** | 8107 | NDVI calculation engine |
| **ndvi_processor** | 8118 | NDVI image processing |
| **weather_core** | 8108 | Multi-provider weather data (OpenWeather, WeatherAPI) |
| **weather_advanced** | 8092 | Advanced weather forecasting |
| **astronomical_calendar** | 8111 | Yemeni agricultural astronomical calendar |

### Analytics & Advisory Services
| Service | Port | Description |
|---------|------|-------------|
| **indicators_service** | 8091 | Agricultural KPIs & analytics |
| **agro_advisor** | 8105 | Agricultural advisory recommendations |
| **ai_advisor** | 8112 | Multi-agent AI system with RAG (Claude, GPT, Gemini) |
| **fertilizer_advisor** | 8093 | Smart fertilization recommendations |
| **irrigation_smart** | 8094 | Smart irrigation management (FAO-56) |
| **virtual_sensors** | 8096 | FAO-56 ET0 calculations |
| **yield_engine** | 8098 | ML crop yield prediction engine |

### AI/ML Services
| Service | Port | Description |
|---------|------|-------------|
| **crop_health_ai** | 8095 | Crop health detection (TensorFlow) |
| **crop_health** | 8100 | Crop health diagnostics |

### Communication Services
| Service | Port | Description |
|---------|------|-------------|
| **field_chat** | 8099 | Field-specific chat service |
| **notification_service** | 8110 | Push notifications & alerts (Email, FCM, SMS) |
| **alert_service** | 8113 | Agricultural alerts and warnings |

### Management Services
| Service | Port | Description |
|---------|------|-------------|
| **equipment_service** | 8101 | Equipment management |
| **task_service** | 8103 | Agricultural task management |
| **inventory_service** | 8116 | Inventory tracking & analytics |
| **field_service** | 8115 | Field management service |

### IoT & Integration Services
| Service | Port | Description |
|---------|------|-------------|
| **iot_gateway** | 8106 | IoT gateway (MQTT bridge to NATS) |
| **provider_config** | 8104 | Multi-provider configuration management |

### Worker Services
| Service | Port | Description |
|---------|------|-------------|
| **agro_rules** | - | NATS event-driven worker (no HTTP port) |

---

## Quick Start

### 1. Prerequisites

- Docker 20.10+
- Docker Compose v2.0+
- At least 16GB RAM
- 50GB free disk space

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set required variables (minimum):
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD
# - JWT_SECRET_KEY
# - MQTT_PASSWORD
```

### 3. Deploy Services

```bash
# Start all services
docker compose up -d

# Start specific services
docker compose up -d postgres redis nats

# Start infrastructure only
docker compose up -d postgres redis nats mqtt qdrant kong

# View logs
docker compose logs -f [service_name]

# Check status
docker compose ps
```

### 4. Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (CAUTION: deletes all data)
docker compose down -v
```

---

## Required Environment Variables

### Critical (Must be set)
```env
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=sahool
REDIS_PASSWORD=<secure_redis_password>
JWT_SECRET_KEY=<secure_jwt_secret_at_least_32_chars>
MQTT_PASSWORD=<secure_mqtt_password>
```

### Optional API Keys
```env
# Weather Providers
OPENWEATHERMAP_API_KEY=
WEATHERAPI_KEY=

# Satellite Providers
SENTINEL_HUB_CLIENT_ID=
SENTINEL_HUB_CLIENT_SECRET=
NASA_EARTHDATA_USERNAME=
NASA_EARTHDATA_PASSWORD=

# AI/LLM Providers
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=

# Payment Gateways
STRIPE_API_KEY=
THARWATT_API_KEY=

# Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FCM_SERVER_KEY=
```

---

## Service Dependencies

### Dependency Graph

```
Infrastructure Layer:
  ├── postgres (required by most services)
  ├── redis (required by caching services)
  ├── nats (required by event-driven services)
  ├── mqtt (required by IoT services)
  ├── qdrant (required by ai_advisor)
  └── kong (API gateway)

Application Layer:
  ├── Core Services
  │   ├── field_ops (depends on: postgres, nats, redis)
  │   ├── field_core (depends on: postgres, redis, nats)
  │   └── ws_gateway (depends on: nats, redis)
  │
  ├── IoT Services
  │   ├── iot_gateway (depends on: postgres, nats, mqtt)
  │   └── iot_service (depends on: postgres, redis, nats, mqtt)
  │
  ├── AI Services
  │   ├── ai_advisor (depends on: qdrant, nats, crop_health_ai, weather_core, agro_advisor)
  │   ├── crop_health_ai (depends on: postgres, nats)
  │   └── crop_health (standalone)
  │
  └── Worker Services
      └── agro_rules (depends on: nats, field_ops)
```

---

## Resource Allocation

### Total Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 8 cores | 16 cores |
| **RAM** | 16GB | 32GB |
| **Disk** | 50GB | 100GB SSD |
| **Network** | 100Mbps | 1Gbps |

### Per-Service Limits

**Infrastructure Services:**
- postgres: 0.5-2 CPUs, 512MB-2GB RAM
- redis: 0.25-1 CPUs, 256MB-768MB RAM
- nats: 0.25-1 CPUs, 128MB-512MB RAM
- mqtt: 0.1-0.5 CPUs, 64MB-256MB RAM
- qdrant: 0.25-1 CPUs, 256MB-1GB RAM
- kong: 0.25-1 CPUs, 128MB-512MB RAM

**Application Services:**
- Node.js services: 0.25-1 CPUs, 128MB-512MB RAM
- Python services: 0.1-1 CPUs, 64MB-512MB RAM
- AI/ML services: 0.5-2 CPUs, 512MB-2GB RAM

---

## Health Checks

All services include health checks with:
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3-5
- **Start period**: 10-40s (depending on service complexity)

Check service health:
```bash
docker compose ps
docker inspect <container_name> | jq '.[0].State.Health'
```

---

## Networking

- **Network**: `sahool-network` (bridge driver)
- **Internal communication**: Services communicate using service names
- **External access**: Only Kong (8000), selected services exposed on 127.0.0.1

### Port Mapping Strategy

- **Infrastructure**: 5432, 6379, 4222, 8222, 1883, 9001, 6333, 6334, 8000, 8001
- **Node.js services**: 3000-3099, 8097, 8114, 8117
- **Python services**: 8080-8118

---

## Data Persistence

Named volumes for persistent data:
- `sahool-postgres-data`: PostgreSQL database
- `sahool-redis-data`: Redis cache
- `sahool-nats-data`: NATS JetStream
- `sahool-qdrant-data`: Qdrant vector database
- `sahool-mqtt-data`: MQTT broker data
- `sahool-mqtt-logs`: MQTT logs

### Backup Commands

```bash
# Backup PostgreSQL
docker compose exec postgres pg_dump -U sahool sahool > backup.sql

# Backup volumes
docker run --rm -v sahool-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore PostgreSQL
docker compose exec -T postgres psql -U sahool sahool < backup.sql
```

---

## Monitoring & Observability

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f field_core

# Last 100 lines
docker compose logs --tail=100 field_core
```

### Metrics
- Prometheus integration available (configure separately)
- All services expose `/healthz` endpoints
- Resource usage: `docker stats`

---

## Security Considerations

1. **Environment Variables**: Never commit `.env` file
2. **Secrets**: Use strong passwords (32+ characters)
3. **Network**: All infrastructure ports bound to `127.0.0.1` only
4. **TLS**: Configure Kong for HTTPS in production
5. **Authentication**: JWT-based authentication enabled by default
6. **Rate Limiting**: Configured per service tier

---

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker compose logs <service_name>

# Check if required env vars are set
docker compose config

# Restart specific service
docker compose restart <service_name>
```

**Database connection issues:**
```bash
# Verify PostgreSQL is healthy
docker compose ps postgres

# Check PostgreSQL logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U sahool -d sahool -c "SELECT 1"
```

**Memory issues:**
```bash
# Check resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or adjust service resource limits in docker-compose.yml
```

**Port conflicts:**
```bash
# Check which ports are in use
netstat -tuln | grep -E "5432|6379|4222|1883|8000"

# Modify port mappings in docker-compose.yml
```

---

## Scaling Services

Scale horizontally:
```bash
# Scale specific service
docker compose up -d --scale field_ops=3

# Note: Services with fixed ports cannot be scaled without load balancer
```

---

## Development vs Production

**Development:**
- Use `.env` with development settings
- Mount source code as volumes for hot reload
- Enable debug logging: `LOG_LEVEL=DEBUG`

**Production:**
- Use secrets management (Vault, AWS Secrets Manager)
- Enable TLS/HTTPS
- Configure backups
- Set up monitoring (Prometheus, Grafana)
- Use orchestration (Kubernetes, Docker Swarm)
- Implement CI/CD pipeline

---

## Support

For issues or questions:
- Check service logs: `docker compose logs -f <service>`
- Review health status: `docker compose ps`
- Verify environment variables: `docker compose config`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kong API Gateway (8000)                  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Node.js   │  │   Python    │  │   Python    │
│  Services   │  │ Core Svcs   │  │  AI/ML Svcs │
│   (10)      │  │   (15)      │  │    (13)     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  PostgreSQL │  │  NATS/MQTT  │  │Redis/Qdrant │
│   PostGIS   │  │  Messaging  │  │  Cache/RAG  │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

**Version**: 16.0.0
**Last Updated**: December 2025
**Platform**: SAHOOL Agricultural Technology Platform
