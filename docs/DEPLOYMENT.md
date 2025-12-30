# SAHOOL v15.3.2 Deployment Guide

## Overview

This guide covers deploying SAHOOL platform using Docker Compose (recommended for development/staging) and Kubernetes/Helm (recommended for production).

## Prerequisites

### Required Software

- Docker 24+ with Compose v2
- OpenSSL (for certificate generation)
- Git
- curl (for health checks)

### For Kubernetes Deployment

- kubectl configured
- Helm 3.x
- Kubernetes cluster 1.25+
- Ingress controller (nginx recommended)

## Quick Start (Docker Compose)

### 1. Clone and Setup

```bash
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp
```

### 2. Generate Environment

```bash
./tools/release/release_v15_3_2.sh --env-only
```

This creates `.env` with:
- Database credentials
- JWT secret keys
- Service configuration

### 3. Start Services

```bash
docker compose up -d
```

### 4. Run Migrations

```bash
./tools/env/migrate.sh
```

### 5. Verify Health

```bash
./tools/release/smoke_test.sh
```

Or manually:

```bash
curl http://localhost:8080/healthz  # FieldOps
curl http://localhost:8097/healthz  # NDVI Engine
curl http://localhost:8098/healthz  # Weather Core
curl http://localhost:8099/healthz  # Field Chat
curl http://localhost:8094/healthz  # IoT Gateway
curl http://localhost:8095/healthz  # Agro Advisor
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway (future)                         │
└─────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  field_ops    │        │  ndvi_engine  │        │ weather_core  │
│    :8080      │        │    :8097      │        │    :8098      │
└───────────────┘        └───────────────┘        └───────────────┘
        │                          │                          │
        │                          │                          │
        ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           NATS JetStream                            │
│                             :4222                                   │
└─────────────────────────────────────────────────────────────────────┘
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  field_chat   │        │  iot_gateway  │        │  agro_advisor │
│    :8099      │        │    :8094      │        │    :8095      │
└───────────────┘        └───────────────┘        └───────────────┘
                                   │
                                   ▼
                         ┌───────────────┐
                         │   ws_gateway  │
                         │    :8090      │
                         └───────────────┘
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| field_ops | 8080 | Task management API |
| ndvi_engine | 8097 | NDVI satellite analysis |
| weather_core | 8098 | Weather forecasting |
| field_chat | 8099 | Real-time chat |
| iot_gateway | 8094 | IoT device management |
| agro_advisor | 8095 | Disease/fertilizer recommendations |
| ws_gateway | 8090 | WebSocket event broadcasting |
| postgres | 5432 | Database |
| nats | 4222 | Message queue |
| redis | 6379 | Cache |
| mqtt | 1883 | IoT broker |

## Kubernetes Deployment (Helm)

### 1. Add Dependencies

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo update
```

### 2. Install Chart

```bash
cd helm/sahool
helm dependency build
helm install sahool . -n sahool --create-namespace
```

### 3. Custom Values

```bash
helm install sahool . -n sahool \
  --set services.fieldOps.replicaCount=3 \
  --set ingress.hosts[0].host=api.sahool.example.com \
  --set security.jwt.secretKey=your-production-secret
```

### 4. Verify Deployment

```bash
kubectl get pods -n sahool
kubectl get services -n sahool
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | **Required** - Set via environment |
| `NATS_URL` | NATS server URL | nats://nats:4222 |
| `REDIS_URL` | Redis connection URL | redis://redis:6379/0 |
| `JWT_SECRET_KEY` | JWT signing key | (generated) |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `LOG_LEVEL` | Logging level | INFO |

### Feature Flags

| Flag | Description | Default |
|------|-------------|---------|
| `ENABLE_SECURITY` | Enable JWT authentication | true |
| `ENABLE_AUDIT_LOGGING` | Enable audit trail | true |
| `ENABLE_MTLS` | Enable mutual TLS | false |
| `ENABLE_RATE_LIMITING` | Enable rate limiting | true |

## Scaling

### Horizontal Scaling

```bash
# Docker Compose
docker compose up -d --scale field_ops=3 --scale field_chat=2

# Kubernetes
kubectl scale deployment sahool-field-ops --replicas=3 -n sahool
```

### Recommended Replicas

| Service | Dev | Staging | Production |
|---------|-----|---------|------------|
| field_ops | 1 | 2 | 3-5 |
| field_chat | 1 | 2 | 3-5 |
| ws_gateway | 1 | 2 | 3-5 |
| Other services | 1 | 1-2 | 2-3 |

## Backup and Restore

### PostgreSQL Backup

```bash
# Backup
docker exec sahool-postgres pg_dump -U sahool sahool > backup.sql

# Restore
docker exec -i sahool-postgres psql -U sahool sahool < backup.sql
```

### NATS JetStream Backup

```bash
# Backup streams
nats stream backup --all /backups/nats/

# Restore
nats stream restore /backups/nats/
```

## Troubleshooting

### Service Won't Start

1. Check logs: `docker compose logs <service>`
2. Verify dependencies are healthy
3. Check environment variables

### Database Connection Issues

```bash
# Test connection
docker exec sahool-postgres pg_isready -U sahool

# Check network
docker network inspect sahool-network
```

### NATS Not Connecting

```bash
# Check NATS status
curl http://localhost:8222/varz

# View streams
nats stream ls
```

## Next Steps

- [Security Configuration](SECURITY.md)
- [Operations Runbook](OPERATIONS.md)
