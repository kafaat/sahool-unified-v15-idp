# SAHOOL Services Helm Charts

This directory contains individual Helm charts for all SAHOOL microservices.

## Available Services

1. **field-ops** - Field Operations Service
2. **weather-core** - Weather Core Service
3. **agro-advisor** - Agro Advisor Service
4. **crop-health** - Crop Health Service
5. **ndvi-engine** - NDVI Engine Service
6. **irrigation-smart** - Irrigation Smart Service
7. **satellite-service** - Satellite Service
8. **weather-advanced** - Weather Advanced Service
9. **crop-health-ai** - Crop Health AI Service
10. **yield-engine** - Yield Engine Service
11. **billing-core** - Billing Core Service
12. **inventory-service** - Inventory Service

## Chart Structure

Each service chart contains:

```
<service-name>/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
└── templates/
    ├── _helpers.tpl        # Template helper functions
    ├── deployment.yaml     # Kubernetes Deployment
    ├── service.yaml        # Kubernetes Service
    └── hpa.yaml           # HorizontalPodAutoscaler (optional)
```

## Installing a Service

```bash
# Install a single service
helm install <release-name> ./services/<service-name>

# Install with custom values
helm install <release-name> ./services/<service-name> \
  --set image.tag=15.3.2 \
  --set environment=production \
  --set deploymentSlot=green

# Install with values file
helm install <release-name> ./services/<service-name> \
  -f custom-values.yaml
```

## Upgrading a Service

```bash
# Upgrade to new version
helm upgrade <release-name> ./services/<service-name>

# Upgrade with new image tag
helm upgrade <release-name> ./services/<service-name> \
  --set image.tag=15.4.0
```

## Common Configuration

All services share common configuration options:

### Image Settings

```yaml
image:
  repository: ghcr.io/kafaat/sahool/<service-name>
  tag: "15.3.2"
  pullPolicy: IfNotPresent
```

### Resource Limits

```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

### Environment & Deployment Slot

```yaml
environment: staging # staging, production
deploymentSlot: blue # blue, green
```

### Autoscaling

```yaml
autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Secrets

```yaml
secrets:
  jwtSecret: ""
database:
  url: ""
```

## Blue-Green Deployment

All services support blue-green deployments via the `deploymentSlot` label:

```bash
# Deploy to blue slot
helm upgrade <release-name>-blue ./services/<service-name> \
  --set deploymentSlot=blue

# Deploy to green slot
helm upgrade <release-name>-green ./services/<service-name> \
  --set deploymentSlot=green
```

## Health Checks

All services include:

- **Liveness Probe**: `/health` endpoint (checks after 30s)
- **Readiness Probe**: `/ready` endpoint (checks after 10s)

## Security Context

All deployments run with:

- Non-root user (UID 1000)
- Read-only root filesystem
- Dropped capabilities
- No privilege escalation

## Service Port

All services expose port 8080 by default via ClusterIP service.

## Examples

### Install field-ops in production

```bash
helm install field-ops-prod ./services/field-ops \
  --set environment=production \
  --set deploymentSlot=blue \
  --set image.tag=15.3.2 \
  --set replicaCount=3
```

### Enable autoscaling for weather-core

```bash
helm install weather-core ./services/weather-core \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=20
```

### Install with custom resources

```bash
helm install crop-health ./services/crop-health \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi \
  --set resources.requests.cpu=200m \
  --set resources.requests.memory=256Mi
```

## Testing Charts

```bash
# Lint a chart
helm lint ./services/<service-name>

# Dry run installation
helm install <release-name> ./services/<service-name> --dry-run --debug

# Template rendering
helm template <release-name> ./services/<service-name>
```

## Notes

- All charts are version 1.0.0 with appVersion 15.3.2
- Charts follow Helm 3 best practices
- All Kubernetes resources include proper labels for monitoring and management
- Secrets are referenced but not created by the charts (must be created separately)
