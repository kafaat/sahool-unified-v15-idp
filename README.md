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
# 1. Set up JWT keys (REQUIRED)
# See docs/SECURITY.md for detailed instructions
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
export JWT_PRIVATE_KEY=$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_private.pem)
export JWT_PUBLIC_KEY=$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_public.pem)

# 2. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 3. Start services
docker compose up -d

# 4. Verify health
./tools/release/smoke_test.sh
```

**Note:** Never commit `.pem` or `.key` files. They are excluded by `.gitignore`.

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
