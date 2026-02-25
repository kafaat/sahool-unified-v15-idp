# SAHOOL Professional Package

Docker Compose deployment for commercial farms requiring satellite imagery, AI crop health diagnostics, smart irrigation, yield prediction, and inventory management. Extends the Starter package with advanced agricultural intelligence services.

## Services Included

### Infrastructure
- PostgreSQL 16 + PostGIS 3.4 (geospatial database)
- Redis 7.x (caching, rate limiting)
- NATS 2.10.x with JetStream (event-driven messaging)

### Core Services (from Starter)
- `field-management-service` (port 3000) - Field and farm management
- `weather-service` (port 8092) - Weather data and forecasts
- `astronomical-calendar` (port 8111) - Islamic/agricultural calendar
- `advisory-service` (port 8093) - Fertilizer and agronomic advisory
- `notification-service` (port 8110) - Push notifications

### Professional-Only Services

| Service | Port | Description |
|---------|------|-------------|
| `vegetation-analysis-service` | 8090 | Sentinel-2 satellite NDVI analysis |
| `ndvi-processor` | 8118 | NDVI processing pipeline |
| `crop-intelligence-service` | 8095 | AI crop disease detection (TFLite) |
| `irrigation-smart` | 8094 | ET0/ETc-based irrigation scheduling |
| `virtual-sensors` | 8119 | Evapotranspiration virtual sensors |
| `yield-prediction-service` | 8152 | ML yield forecasting (NestJS) |
| `advisory-service` | 8093 | Fertilizer recommendations |
| `inventory-service` | 8116 | Input inventory tracking |

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with required values

# 2. Start all services
cd packages/professional
docker-compose up -d --wait

# 3. Verify health
docker-compose ps
curl http://localhost:8090/healthz
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

# Satellite imagery (optional - uses mock data if not set)
SENTINEL_HUB_CLIENT_ID=<id>
SENTINEL_HUB_CLIENT_SECRET=<secret>
NASA_EARTHDATA_USERNAME=<user>
NASA_EARTHDATA_PASSWORD=<password>

# Weather (optional)
OPENWEATHERMAP_API_KEY=<key>
WEATHERAPI_KEY=<key>

# AI model path (required for crop intelligence)
# Models volume mounted at /app/models
```

## Resource Requirements

| Component | CPU | Memory |
|-----------|-----|--------|
| Infrastructure | 2 cores | 2 GB |
| Core services | 3 cores | 3 GB |
| Satellite + Crop AI | 3 cores | 4 GB |
| **Total recommended** | **8+ cores** | **16 GB** |

## Key Differences from Starter

| Feature | Starter | Professional |
|---------|---------|-------------|
| Satellite NDVI | No | Yes (Sentinel-2) |
| Crop disease AI | No | Yes (TFLite) |
| Smart irrigation (ET-based) | No | Yes |
| Yield prediction | No | Yes (ML model) |
| Virtual sensors (ET0/ETc) | No | Yes |
| Inventory management | No | Yes |
| Monitoring (Prometheus/Grafana) | No | No (see Enterprise) |

## Upgrade to Enterprise

To add AI advisory (RAG), IoT gateway, marketplace, billing, and observability, use the Enterprise package:

```bash
cd packages/enterprise
docker-compose up -d
```

## Network and Security

- All services run on isolated `sahool-pro-network` bridge
- Containers run as non-root (`sahool`, UID 1000)
- `no-new-privileges: true` security option on all containers
- AI model files mounted read-only from `../../models`
- Infrastructure ports bound to `127.0.0.1` only
