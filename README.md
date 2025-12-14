# SAHOOL Platform v15.3.2

> **منصة إدارة العمليات الزراعية الذكية | Smart Agricultural Operations Management Platform**

## Overview

SAHOOL is a comprehensive agricultural platform combining field operations management, satellite imagery analysis (NDVI), weather forecasting, IoT integration, and intelligent advisory services.

### Key Features

- **Field Operations** - Task management, assignments, and tracking
- **NDVI Analysis** - Satellite-based vegetation index monitoring
- **Weather Intelligence** - Forecasting and agricultural alerts
- **IoT Integration** - Sensor data collection and device management
- **Agro Advisory** - Disease detection and fertilizer recommendations
- **Real-time Chat** - Team collaboration on fields and tasks
- **Security** - JWT authentication, RBAC, audit logging

## Quick Start

```bash
# Generate environment
./tools/release/release_v15_3_2.sh --env-only

# Start services
docker compose up -d

# Run migrations
./tools/env/migrate.sh

# Verify health
./tools/release/smoke_test.sh
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| field_ops | 8080 | Task management |
| ndvi_engine | 8097 | Satellite analysis |
| weather_core | 8098 | Weather services |
| field_chat | 8099 | Collaboration |
| iot_gateway | 8094 | Device management |
| agro_advisor | 8095 | Recommendations |
| ws_gateway | 8090 | Real-time events |

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Guide](docs/SECURITY.md)
- [Operations Runbook](docs/OPERATIONS.md)

## Project Structure

```
kernel/services/     # Microservices
shared/security/     # Auth, RBAC, audit
tools/release/       # Build and release
helm/                # Kubernetes charts
docs/                # Documentation
```

---

# Internal Developer Platform (IDP) Add-on

This repository also includes an **Internal Developer Platform** add-on:

- `idp/backstage/` - Backstage app + deployment manifests
- `idp/templates/` - Service scaffolder templates
- `idp/sahoolctl/` - CLI for scaffolding services
- `dev/` - k3d-based internal dev environment
- `gitops/` - Argo CD applications

### IDP Quick Start

```bash
# Create local cluster
./dev/k3d/create-cluster.sh

# Install IDP apps
kubectl apply -f gitops/argocd/applications/idp-root-app.yaml

# Open Backstage
kubectl -n backstage port-forward svc/backstage 7007:7007
```

---

Version: 15.3.2 | Updated: 2025-12-14
