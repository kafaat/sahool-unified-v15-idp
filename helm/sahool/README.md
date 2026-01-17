# SAHOOL Kubernetes Helm Chart

# E.77 Helm DEF5) 3GHD 'D21'9J)

Version: 15.3.2

## Overview | F81) 9'E)

This Helm chart deploys the SAHOOL Agricultural Platform on Kubernetes with support for three deployment tiers:

- **Starter**: Basic agricultural services
- **Professional**: Advanced monitoring and AI features
- **Enterprise**: Full platform with marketplace, billing, and research tools

G0' 'DE.77 JF41 EF5) 3GHD 'D21'9J) 9DI Kubernetes E9 /9E D+D'+ -2E:

- **'D#3'3J)**: 'D./E'\* 'D21'9J) 'D#3'3J)
- **'DE-\*1A)**: EJ2'* 'DE1'B() H'D0C'! 'D'57F'9J 'DE*B/E)
- **'DE$33J)**: 'DEF5) 'DC'ED) E9 'D3HB H'DAH*1) H#/H'* 'D(-+

## Prerequisites | 'DE*7D('* 'D#3'3J)

- Kubernetes 1.24+
- Helm 3.8+
- PV provisioner support in the underlying infrastructure
- cert-manager (for TLS certificates)
- Nginx Ingress Controller

## Quick Start | 'D(/! 'D31J9

### 1. Install Dependencies

```bash
# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo update

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Install nginx-ingress
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### 2. Create Secrets

```bash
# PostgreSQL password
kubectl create secret generic sahool-postgresql-secret \
  --from-literal=password='your-postgres-password'

# Redis password
kubectl create secret generic sahool-redis-secret \
  --from-literal=redis-password='your-redis-password'

# JWT secret
kubectl create secret generic sahool-jwt-secret \
  --from-literal=secret-key='your-jwt-secret-key-min-32-chars'

# Database URL secret
kubectl create secret generic sahool-database-secret \
  --from-literal=url='postgresql://username:password@host:5432/database'
```

### 3. Install SAHOOL

#### Starter Package | 'D-2E) 'D#3'3J)

```bash
helm install sahool ./helm/sahool \
  --values helm/sahool/values.yaml \
  --set packageTier=starter \
  --namespace sahool \
  --create-namespace
```

#### Professional Package | 'D-2E) 'DE-\*1A)

```bash
helm install sahool ./helm/sahool \
  --values helm/sahool/values.yaml \
  --values helm/sahool/values-staging.yaml \
  --set packageTier=professional \
  --namespace sahool \
  --create-namespace
```

#### Enterprise Package | 'D-2E) 'DE$33J)

```bash
helm install sahool ./helm/sahool \
  --values helm/sahool/values-production.yaml \
  --set packageTier=enterprise \
  --namespace sahool-prod \
  --create-namespace
```

## Configuration | 'D%9/'/'\*

### Package Tiers | E3*HJ'* 'D-2E

| Tier         | Services        | Replicas | Resource Profile  |
| ------------ | --------------- | -------- | ----------------- |
| Starter      | 5 core services | 1-2      | Low (4GB RAM)     |
| Professional | 13 services     | 1-3      | Medium (12GB RAM) |
| Enterprise   | 21 services     | 2-3+     | High (32GB+ RAM)  |

### Starter Package Services

- field-core (3000)
- weather-core (8108)
- astronomical-calendar (8111)
- agro-advisor (8105)
- notification-service (8110)

### Professional Package (includes Starter +)

- satellite-service (8090)
- ndvi-engine (8107)
- crop-health-ai (8095)
- irrigation-smart (8094)
- virtual-sensors (8096)
- yield-engine (8098)
- fertilizer-advisor (8093)
- inventory-service (8116)

### Enterprise Package (includes Professional +)

- ai-advisor (8112)
- iot-gateway (8106)
- research-core (3015)
- marketplace-service (3010)
- billing-core (8089)
- disaster-assessment (3020)
- crop-growth-model (3023)
- lai-estimation (3022)

## Values Configuration | \*CHJF 'DBJE

### Global Settings

```yaml
global:
  imageRegistry: "ghcr.io/sahool"
  environment: "production"
  storageClass: "standard"

packageTier: "starter" # starter, professional, enterprise
```

### Infrastructure

```yaml
infrastructure:
  postgresql:
    enabled: true
    primary:
      persistence:
        size: 20Gi
      resources:
        limits:
          cpu: 2000m
          memory: 4Gi

  redis:
    enabled: true
    master:
      persistence:
        size: 5Gi

  nats:
    enabled: true
    jetstream:
      enabled: true
      fileStorage:
        size: 10Gi

  kong:
    enabled: true
    replicaCount: 2
```

### Service Customization

Each service can be customized:

```yaml
services:
  fieldCore:
    enabled: true
    replicaCount: 2
    resources:
      limits:
        cpu: 1000m
        memory: 1Gi
    autoscaling:
      enabled: true
      minReplicas: 2
      maxReplicas: 5
```

### Ingress Configuration

```yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: api.sahool.ag
      paths:
        - path: /api/v1/fields
          service: field-core
          port: 3000
  tls:
    - secretName: sahool-tls-prod
      hosts:
        - api.sahool.ag
```

## Upgrading | 'D\*1BJ)

```bash
# Upgrade to Professional tier
helm upgrade sahool ./helm/sahool \
  --values helm/sahool/values-staging.yaml \
  --set packageTier=professional \
  --namespace sahool

# Upgrade to Enterprise tier
helm upgrade sahool ./helm/sahool \
  --values helm/sahool/values-production.yaml \
  --set packageTier=enterprise \
  --namespace sahool-prod
```

## Monitoring | 'DE1'B()

Enable monitoring (Enterprise only):

```yaml
monitoring:
  enabled: true
  prometheus:
    enabled: true
    retention: 30d
  grafana:
    enabled: true
```

Access Grafana:

```bash
kubectl port-forward svc/sahool-grafana 3000:80 -n sahool-prod
```

## Troubleshooting | '3\*C4'A 'D#.7'!

### Check Pod Status

```bash
kubectl get pods -n sahool
kubectl logs -f <pod-name> -n sahool
```

### Check Service Endpoints

```bash
kubectl get svc -n sahool
kubectl get ingress -n sahool
```

### Database Connection

```bash
kubectl exec -it <field-core-pod> -n sahool -- sh
psql $DATABASE_URL
```

### NATS Status

```bash
kubectl port-forward svc/sahool-nats 8222:8222 -n sahool
curl http://localhost:8222/healthz
```

## Backup & Recovery | 'DF3. 'D'-*J'7J H'D'3*9'/)

Enable automated backups (Production):

```yaml
backup:
  enabled: true
  schedule: "0 2 * * *" # Daily at 2 AM
  retention: 90 # days
  size: 200Gi
```

## Uninstalling | %D:'! 'D*+(J*

```bash
helm uninstall sahool -n sahool

# Clean up PVCs
kubectl delete pvc -l app.kubernetes.io/instance=sahool -n sahool
```

## Security | 'D#E'F

### Network Policies

Network policies are enabled by default to restrict traffic between pods.

### Pod Security

All pods run with:

- Non-root user (UID 1000)
- Read-only root filesystem
- Dropped capabilities
- Seccomp profile

### Secrets Management

Use external secret management solutions:

- Sealed Secrets
- External Secrets Operator
- Vault

## Support | 'D/9E

For issues and questions:

- Email: support@sahool.ag
- GitHub: https://github.com/sahool/platform/issues

## License

Apache 2.0

---

Made with d by the SAHOOL Team
5OF9 (CD d EF A1JB 3GHD
