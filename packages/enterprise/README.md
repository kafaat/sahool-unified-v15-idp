# SAHOOL Enterprise Package

Full-stack Docker Compose deployment for large-scale agricultural enterprises. Includes all Professional tier services plus AI/RAG capabilities, IoT gateway, research tools, marketplace, billing, and integrated observability with Prometheus and Grafana.

## Services Included

### Infrastructure
- PostgreSQL 16 + PostGIS 3.4 (geospatial database)
- Redis 7.x (caching and sessions)
- NATS 2.10.x with JetStream (event messaging)
- Qdrant (vector database for RAG)

### Core (from Starter)
- `field-management-service` (port 3000) - Field and farm management
- `weather-service` (port 8092) - Weather data and forecasts
- `astronomical-calendar` (port 8111) - Islamic/agricultural calendar
- `advisory-service` (port 8093) - Agronomic advisory
- `notification-service` (port 8110) - Push notifications

### Professional Tier (from Professional)
- `vegetation-analysis-service` (port 8090) - Satellite NDVI analysis
- `crop-intelligence-service` (port 8095) - Crop health AI
- `irrigation-smart` (port 8094) - Smart irrigation scheduling
- `virtual-sensors` (port 8119) - ET0/ETc virtual sensors
- `yield-prediction-service` (port 8152) - ML yield prediction
- `inventory-service` (port 8116) - Input inventory management

### Enterprise-Only Services
- `ai_advisor` (port 8112) - Multi-LLM AI advisory with RAG
- `copilot_api` (port 8088) - Agricultural copilot (Claude, OpenAI, Gemini)
- `code_fix_agent` (port 8162) - Auto-fix code agent
- `iot_gateway` (port 8106) - MQTT/IoT protocol gateway
- `research_core` (port 3015) - Research trial management
- `crop_growth_model` (port 3023) - Crop growth simulation
- `lai_estimation` (port 3022) - Leaf Area Index estimation
- `disaster_assessment` (port 3020) - Disaster risk assessment
- `marketplace_service` (port 3010) - Agricultural marketplace
- `billing_core` (port 8089) - Subscription and invoicing
- Prometheus + Grafana - Observability stack

### Optional: Local LLM
```bash
docker-compose --profile with-ollama up -d
```
Starts Ollama (port 11434) with `codellama:7b` for offline AI inference.

## Quick Start

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env with required secrets (see below)

# 2. Start all services
cd packages/enterprise
docker-compose up -d

# 3. Wait for health checks
docker-compose up -d --wait

# 4. Check status
docker-compose ps
```

## Required Environment Variables

```bash
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=sahool
REDIS_PASSWORD=<strong_password>
NATS_USER=sahool
NATS_PASSWORD=<strong_password>
JWT_SECRET_KEY=<minimum_32_char_secret>
JWT_ALGORITHM=HS256
ENVIRONMENT=production

# AI providers (at least one required for ai_advisor)
ANTHROPIC_API_KEY=<key>
OPENAI_API_KEY=<key>

# Satellite imagery (optional - enables NDVI from real satellite data)
SENTINEL_HUB_CLIENT_ID=<id>
SENTINEL_HUB_CLIENT_SECRET=<secret>

# Weather (optional - enables live weather data)
OPENWEATHERMAP_API_KEY=<key>

# Notifications (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USER=<email>
SMTP_PASSWORD=<password>
```

## Resource Requirements

| Component | CPU (min) | Memory (min) |
|-----------|-----------|-------------|
| Infrastructure (PG + Redis + NATS) | 4 cores | 4 GB |
| Core services | 4 cores | 4 GB |
| AI services (without GPU) | 4 cores | 8 GB |
| AI services (with GPU) | 4 cores + GPU | 8 GB + VRAM |
| **Total recommended** | **16 cores** | **32 GB** |

All containers run as non-root user (`sahool`, UID 1000) with resource limits enforced via Docker deploy constraints.

## Monitoring

```bash
# Grafana dashboards
open http://localhost:3001

# Prometheus metrics
open http://localhost:9090

# NATS monitoring
open http://localhost:8222
```

## Network

All services communicate on the isolated `sahool-enterprise-network` bridge network. Only necessary ports are bound to `localhost` (infrastructure) or all interfaces (application services).
