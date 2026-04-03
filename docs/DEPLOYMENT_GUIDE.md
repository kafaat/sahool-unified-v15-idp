# SAHOOL v16 Deployment Guide

## Quick Start (Local)

```bash
# 1. Apply HOTFIX-002
.\scripts\apply-hotfix-002.ps1 -FullReset

# 2. Setup Event Bus
.\scripts\setup-event-bus.ps1

# 3. Start all services
docker compose up -d

# 4. Verify
.\scripts\health-check-all.ps1
```

## Production Deployment (EKS)

```bash
# 1. Deploy to staging
.\scripts\deploy-production.ps1 -Environment "staging" -Version "v16.0.0"

# 2. Deploy to production
.\scripts\deploy-production.ps1 -Environment "production" -Version "v16.0.0"
```

## Monitoring

| Service | URL |
|---------|-----|
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| NATS Monitor | http://localhost:8222 |
| Loki | http://localhost:3100 |
| Tempo | http://localhost:3200 |
