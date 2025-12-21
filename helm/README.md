# SAHOOL Helm Charts

## Overview

Kubernetes deployment charts for SAHOOL platform.

---

## Chart Structure

```
helm/
└── sahool/
    ├── Chart.yaml                  # Chart metadata
    ├── values.yaml                 # Default values
    ├── values.generated.yaml       # Generated values
    └── templates/
        ├── _helpers.tpl            # Template helpers
        ├── configmap.yaml          # ConfigMaps
        ├── deployment-field-ops.yaml  # Field ops deployment
        ├── hpa.yaml                # Horizontal Pod Autoscaler
        ├── pdb.yaml                # Pod Disruption Budget
        ├── rollout.yaml            # Argo Rollouts
        └── secrets.yaml            # Secrets
```

---

## Chart Info

```yaml
# Chart.yaml
name: sahool
version: 15.3.2
appVersion: "15.3.2"
description: SAHOOL Agricultural Platform - Complete Field Operations Management
```

### Dependencies

| Chart | Version | Repository |
|-------|---------|------------|
| postgresql | 13.x.x | bitnami |
| nats | 1.x.x | nats-io |
| redis | 18.x.x | bitnami |

---

## Installation

### Add Repositories

```bash
# Bitnami
helm repo add bitnami https://charts.bitnami.com/bitnami

# NATS
helm repo add nats https://nats-io.github.io/k8s/helm/charts/

# Update
helm repo update
```

### Install

```bash
# Install with default values
helm install sahool ./helm/sahool

# Install with custom values
helm install sahool ./helm/sahool -f custom-values.yaml

# Install to specific namespace
helm install sahool ./helm/sahool -n sahool --create-namespace
```

### Upgrade

```bash
helm upgrade sahool ./helm/sahool

# With values
helm upgrade sahool ./helm/sahool -f values.yaml
```

### Uninstall

```bash
helm uninstall sahool
```

---

## Values

### Main Configuration

```yaml
# values.yaml
replicaCount: 2

image:
  repository: ghcr.io/kafaat/sahool
  tag: "latest"
  pullPolicy: IfNotPresent

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

### Environment-specific

```yaml
# Production
production:
  replicaCount: 3
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi

# Staging
staging:
  replicaCount: 2
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
```

---

## Templates

### Deployment

```yaml
# deployment-field-ops.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "sahool.fullname" . }}-field-ops
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: field-ops
  template:
    spec:
      containers:
        - name: field-ops
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

### HPA (Auto-scaling)

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
```

### PDB (High Availability)

```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: sahool
```

### Argo Rollouts

```yaml
# rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: {duration: 30s}
        - setWeight: 50
        - pause: {duration: 30s}
```

---

## Configuration

### Database

```yaml
postgresql:
  enabled: true
  auth:
    postgresPassword: changeme
    database: sahool
  primary:
    persistence:
      size: 10Gi
```

### Message Queue

```yaml
nats:
  enabled: true
  cluster:
    enabled: true
    replicas: 3
```

### Cache

```yaml
redis:
  enabled: true
  auth:
    password: changeme
  master:
    persistence:
      size: 1Gi
```

---

## Secrets Management

### Using External Secrets

```yaml
externalSecrets:
  enabled: true
  secretStore: vault
  refreshInterval: 1h
```

### Sealed Secrets

```bash
# Encrypt secret
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml

# Apply
kubectl apply -f sealed-secret.yaml
```

---

## Commands

```bash
# Template (dry-run)
helm template sahool ./helm/sahool

# Lint
helm lint ./helm/sahool

# Package
helm package ./helm/sahool

# Debug install
helm install sahool ./helm/sahool --dry-run --debug
```

---

## Related Documentation

- [GitOps Setup](../gitops/README_IDP.md)
- [Infrastructure](../infra/README.md)
- [Docker Guide](../docs/DOCKER.md)

---

<p align="center">
  <sub>SAHOOL Helm Charts v15.3.2</sub>
  <br>
  <sub>December 2025</sub>
</p>
