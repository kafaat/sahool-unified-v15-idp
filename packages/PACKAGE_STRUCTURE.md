# SAHOOL Deployment Packages Structure

This document summarizes the deployment package structure created for SAHOOL platform.

## Directory Structure

```
packages/
├── starter/
│   └── docker-compose.yml          # Starter tier (11.7 KB)
├── professional/
│   └── docker-compose.yml          # Professional tier (21.1 KB)
├── enterprise/
│   └── docker-compose.yml          # Enterprise tier (37.2 KB)
├── .env.example                     # Environment variables template (14 KB)
├── DEPLOYMENT.md                    # Deployment documentation (13 KB)
└── README.md                        # TypeScript packages documentation

```

## Package Details

### 🌱 Starter Package
**File:** `/home/user/sahool-unified-v15-idp/packages/starter/docker-compose.yml`

**Services (6):**
- PostgreSQL/PostGIS (512MB RAM)
- Redis (256MB RAM)
- NATS (256MB RAM)
- field_core
- weather_core
- astronomical_calendar
- agro_advisor
- notification_service

**Resource Profile:** Low (suitable for 1-2 CPU cores, 4GB RAM total)

---

### 🚜 Professional Package
**File:** `/home/user/sahool-unified-v15-idp/packages/professional/docker-compose.yml`

**Services (14):**
- All Starter services (with increased resources)
- satellite_service
- ndvi_engine
- crop_health_ai
- irrigation_smart
- virtual_sensors
- yield_engine
- fertilizer_advisor
- inventory_service

**Resource Profile:** Medium (suitable for 4-6 CPU cores, 12GB RAM total)

---

### 🏢 Enterprise Package
**File:** `/home/user/sahool-unified-v15-idp/packages/enterprise/docker-compose.yml`

**Services (25):**
- All Professional services (with increased resources)
- qdrant (vector database)
- mqtt (IoT broker)
- ai_advisor (multi-agent AI)
- iot_gateway
- research_core
- marketplace_service
- billing_core
- disaster_assessment
- crop_growth_model
- lai_estimation
- prometheus (monitoring)
- grafana (dashboards)

**Resource Profile:** High (suitable for 8-16 CPU cores, 32GB RAM total)

---

## Key Features

### All Packages Include:
✅ Proper health checks for all services
✅ Resource limits (CPU & memory)
✅ Docker network isolation
✅ Named volumes for data persistence
✅ Dependency management (depends_on with conditions)
✅ Restart policies (unless-stopped)
✅ Environment variable validation

### Package-Specific Features:

**Starter:**
- Basic agricultural platform
- Essential field and weather services
- Minimal resource footprint

**Professional:**
- Satellite imagery integration
- AI-powered crop health detection
- Smart irrigation & fertilization
- Yield prediction
- Inventory management

**Enterprise:**
- Advanced multi-agent AI advisor
- IoT device support (MQTT)
- Research and simulation tools
- E-commerce marketplace
- Billing and payment processing
- Full observability stack (Prometheus + Grafana)

---

## Files Created

1. **packages/starter/docker-compose.yml** - Starter tier configuration
2. **packages/professional/docker-compose.yml** - Professional tier configuration
3. **packages/enterprise/docker-compose.yml** - Enterprise tier configuration
4. **packages/.env.example** - Environment variables template with detailed comments
5. **packages/DEPLOYMENT.md** - Bilingual (Arabic/English) deployment documentation

---

## Usage

### Quick Start

```bash
# Choose your package tier
cd packages/starter   # or professional, or enterprise

# Copy and configure environment variables
cp ../.env.example .env
nano .env  # Edit with your configuration

# Start the services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Required for all packages:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_PASSWORD`
- `JWT_SECRET_KEY`

Additional for Professional:
- Satellite API keys (optional for enhanced features)

Additional for Enterprise:
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (for AI advisor)
- `MQTT_PASSWORD` (for IoT)
- `GRAFANA_ADMIN_PASSWORD` (for monitoring)

See `.env.example` for complete list with detailed comments.

---

## Validation

All docker-compose files have been created with:
- Valid YAML syntax
- Proper service dependencies
- Health check configurations
- Resource constraints
- Network and volume definitions

---

## Next Steps

1. Review `DEPLOYMENT.md` for detailed package comparison
2. Copy `.env.example` to your chosen package directory
3. Configure environment variables
4. Build service Docker images (or pull from registry)
5. Start services with `docker-compose up -d`
6. Access services via configured ports

---

Created: 2025-12-26
SAHOOL Platform v15.3.2
