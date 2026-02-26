# SAHOOL Starter Package

Minimal Docker Compose deployment for small farms. Provides the essential agricultural services — field management, weather, Islamic agricultural calendar, advisory recommendations, and notifications — with a small resource footprint.

## Services Included

### Infrastructure
- PostgreSQL 16 + PostGIS 3.4 (geospatial field boundaries)
- Redis 7.x (sessions and caching, 256 MB limit)
- NATS 2.10.x with JetStream (event messaging, 256 MB limit)

### Application Services

| Service | Port | Description |
|---------|------|-------------|
| `field-management-service` | 3000 | Field and farm CRUD, geospatial queries |
| `weather-service` | 8092 | Current weather, forecasts, agricultural alerts |
| `astronomical-calendar` | 8111 | Islamic calendar, prayer times, planting timing |
| `advisory-service` | 8093 | Basic fertilizer and agronomic recommendations |
| `notification-service` | 8110 | Email/push notifications via SMTP |

## Quick Start

```bash
# 1. Configure environment
cp ../../.env.example .env
# Edit .env - fill in all required values

# 2. Start services
cd packages/starter
docker-compose up -d

# 3. Wait for all health checks to pass
docker-compose up -d --wait

# 4. Verify
curl http://localhost:3000/healthz    # field-management
curl http://localhost:8092/healthz    # weather
curl http://localhost:8093/healthz    # advisory
```

## Required Environment Variables

```bash
# Database
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=sahool

# Cache
REDIS_PASSWORD=<strong_password>

# Message queue
NATS_USER=sahool
NATS_PASSWORD=<strong_password>

# Authentication
JWT_SECRET_KEY=<minimum_32_char_secret>
JWT_ALGORITHM=HS256

# General
ENVIRONMENT=production
LOG_LEVEL=INFO

# Weather (optional - mock data used if not set)
OPENWEATHERMAP_API_KEY=<key>
WEATHERAPI_KEY=<key>

# Notifications (optional - required for email alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<email>
SMTP_PASSWORD=<password>
SMTP_FROM_EMAIL=noreply@sahool.com
```

## Resource Requirements

Designed to run on small servers or VMs:

| Component | CPU limit | Memory limit |
|-----------|-----------|-------------|
| PostgreSQL | 1 core | 512 MB |
| Redis | 0.5 core | 256 MB |
| NATS | 0.5 core | 256 MB |
| field-management-service | 0.5 core | 512 MB |
| weather-service | 0.5 core | 512 MB |
| astronomical-calendar | 0.25 core | 256 MB |
| advisory-service | 0.5 core | 512 MB |
| notification-service | 0.25 core | 256 MB |
| **Total** | **~4 cores** | **~3 GB** |

Minimum recommended hardware: 4 vCPUs, 4 GB RAM, 20 GB disk.

## Upgrade Paths

| Need | Package |
|------|---------|
| Satellite NDVI, crop AI, smart irrigation | `packages/professional` |
| AI advisory (RAG), IoT, marketplace, monitoring | `packages/enterprise` |

## Security

- Infrastructure ports bound to `127.0.0.1` (not exposed externally)
- Application service ports exposed on all interfaces (firewall externally)
- `no-new-privileges: true` on all containers
- Containers run as non-root user (`sahool`, UID 1000)
- Data persisted to named Docker volumes (`sahool-starter-*`)
- Network isolated to `sahool-starter-network` bridge

## Troubleshooting

```bash
# View logs for a specific service
docker-compose logs -f advisory-service

# Restart a failed service
docker-compose restart weather-service

# Check PostgreSQL connectivity
docker-compose exec postgres pg_isready -U sahool

# Reset everything (WARNING: deletes all data)
docker-compose down -v
```
