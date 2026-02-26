# Docker Build System | نظام بناء Docker

Docker configuration for the SAHOOL platform — base images, service Dockerfiles, and compose orchestration.

## Directory Structure

```
docker/
├── Dockerfile.python.base      # Base Python image (python:3.11-slim-bookworm)
├── Dockerfile.ai-base          # AI services base (Aliyun + Tsinghua mirrors)
├── Dockerfile.node.base        # Base Node.js image
├── constraints-ai.txt          # AI service version pins with CVE patches
├── CONSTRAINTS_EXTRAS.md       # Pip constraints vs extras documentation
├── compose/                    # 4-Layer event architecture compose files
│   ├── compose.acquisition.yml # Layer 1: Data ingestion (IoT, weather, satellite)
│   ├── compose.intelligence.yml# Layer 2: Feature extraction & AI
│   ├── compose.decision.yml    # Layer 3: Recommendations & planning
│   ├── compose.business.yml    # Layer 4: User-facing operations
│   └── compose.all.yml         # All layers combined
├── compose.dev.yml             # Development overrides
├── compose.staging.yml         # Staging configuration
├── compose.prod.yml            # Production configuration
├── compose.generated.yml       # Auto-generated compose
├── docker-compose.infra.yml    # Infrastructure-only (postgres, redis, nats, kong)
├── docker-compose.dlq.yml      # Dead Letter Queue services
├── docker-compose.iot.yml      # IoT services (MQTT, sensors)
├── docker-compose.secrets.yml  # Secrets management (Vault)
└── mosquitto/                  # MQTT broker configuration
    └── config/mosquitto.conf
```

## Base Images

| Image | Base | Purpose |
|-------|------|---------|
| `Dockerfile.python.base` | `python:3.11-slim-bookworm` | All Python services |
| `Dockerfile.ai-base` | `python:3.11-slim-bookworm` | AI services (with pip mirror config) |
| `Dockerfile.node.base` | `node:20-slim` | All Node.js/NestJS services |

**Exception**: `yolo26-vision-service` uses `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` for GPU support.

## 4-Layer Compose Architecture

The platform follows a 4-layer event-driven architecture. Each layer can be started independently:

```bash
# Start specific layer
docker compose -f docker/compose/compose.acquisition.yml up
docker compose -f docker/compose/compose.intelligence.yml up
docker compose -f docker/compose/compose.decision.yml up
docker compose -f docker/compose/compose.business.yml up

# Start all layers
docker compose -f docker/compose/compose.all.yml up
```

| Layer | File | Services |
|-------|------|----------|
| **Acquisition** | `compose.acquisition.yml` | IoT, weather, satellite, edge-orchestrator |
| **Intelligence** | `compose.intelligence.yml` | NDVI, crop-intelligence, vision, terrain |
| **Decision** | `compose.decision.yml` | Advisory, irrigation, yield prediction |
| **Business** | `compose.business.yml` | Notification, marketplace, billing, chat |

## Environment-Specific Compose Files

```bash
# Development (with hot-reload, debug tools)
docker compose -f docker/compose.dev.yml up

# Staging
docker compose -f docker/compose.staging.yml up

# Production
docker compose -f docker/compose.prod.yml up

# Infrastructure only (database, cache, queue, gateway)
docker compose -f docker/docker-compose.infra.yml up
```

## Pip Mirror Strategy

Three patterns are used for reliable pip installs (see CLAUDE.md for details):

| Pattern | Services | Strategy |
|---------|----------|----------|
| **A: Multi-Mirror** | 42 services | PyPI → Aliyun → Tencent fallback |
| **B: Aliyun Only** | 20 services | Aliyun mirror direct |
| **C: No Mirror** | 1 service | Direct PyPI only |

## Security

All service Dockerfiles follow:
- Non-root user `sahool` (UID 1000)
- Read-only filesystem where possible
- Multi-stage builds (35+ services)
- HEALTHCHECK directives

## Quick Reference

```bash
make build                 # Build all images (parallel)
make build-python          # Build Python services only
make build-node            # Build Node.js services only
make up                    # Start all services
make down                  # Stop all services
make infra-up              # Infrastructure only
```
