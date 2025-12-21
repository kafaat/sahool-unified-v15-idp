# SAHOOL Development Environment

## Overview

أدوات بيئة التطوير المحلية.

---

## Structure

```
dev/
├── k3d/                    # K3d (lightweight Kubernetes)
│   └── config files        # K3d cluster configuration
└── README.md               # This file
```

---

## K3d (Local Kubernetes)

K3d is a lightweight Kubernetes distribution for local development.

### Prerequisites

```bash
# Install k3d
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# Install kubectl
brew install kubectl  # macOS
# or
apt-get install kubectl  # Ubuntu
```

### Create Cluster

```bash
# Create sahool cluster
k3d cluster create sahool \
  --servers 1 \
  --agents 2 \
  --port 8080:80@loadbalancer \
  --port 8443:443@loadbalancer

# With custom config
k3d cluster create --config dev/k3d/config.yaml
```

### Cluster Management

```bash
# List clusters
k3d cluster list

# Stop cluster
k3d cluster stop sahool

# Start cluster
k3d cluster start sahool

# Delete cluster
k3d cluster delete sahool
```

### Deploy to K3d

```bash
# Build and load images
docker build -t sahool/field-service:dev apps/services/field-service
k3d image import sahool/field-service:dev -c sahool

# Apply manifests
kubectl apply -k gitops/sahool/services/
```

---

## Local Development Flow

### 1. Start Infrastructure

```bash
# Start core services
docker compose up -d postgres redis nats mqtt
```

### 2. Start K3d (Optional)

```bash
# For Kubernetes testing
k3d cluster create sahool --config dev/k3d/config.yaml
```

### 3. Run Services

```bash
# Individual service
cd apps/services/field-service
python -m uvicorn main:app --reload

# Or via Docker Compose
docker compose up field-service satellite-service
```

### 4. Run Frontend

```bash
# Web app
pnpm --filter sahool-web dev

# Admin dashboard
pnpm --filter sahool-admin-dashboard dev
```

---

## Port Mapping

When using K3d, these ports are exposed:

| Port | Service |
|------|---------|
| 8080 | HTTP Ingress |
| 8443 | HTTPS Ingress |
| 6443 | Kubernetes API |

---

## Troubleshooting

### Reset Environment

```bash
# Stop all containers
docker compose down -v

# Delete K3d cluster
k3d cluster delete sahool

# Clean Docker
docker system prune -af
```

### Check Logs

```bash
# K3d logs
k3d cluster list
kubectl logs -f deployment/field-service

# Docker logs
docker compose logs -f field-service
```

---

## Related Documentation

- [Docker Guide](../docs/DOCKER.md)
- [Helm Charts](../helm/README.md)
- [GitOps](../gitops/README.md)

---

<p align="center">
  <sub>SAHOOL Development Environment</sub>
  <br>
  <sub>December 2025</sub>
</p>
