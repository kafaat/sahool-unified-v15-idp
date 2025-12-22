# SAHOOL GitOps

## Overview

GitOps deployment configuration using ArgoCD for Kubernetes.

---

## Structure

```
gitops/
├── README_IDP.md                   # IDP integration guide
├── argocd/
│   ├── README_MULTICLUSTER.md      # Multi-cluster setup
│   ├── applications/               # ArgoCD Application manifests
│   │   ├── argo-rollouts-app.yaml
│   │   ├── billing-core-app.yaml
│   │   ├── cert-manager-app.yaml
│   │   ├── external-secrets-app.yaml
│   │   ├── feature-flags-app.yaml
│   │   ├── idp-root-app.yaml
│   │   ├── ingress-nginx-app.yaml
│   │   ├── sahool-governance-policies.yaml
│   │   └── secrets-root-app.yaml
│   ├── applicationsets/            # Dynamic app generation
│   │   ├── sahool-multicluster-appset.yaml
│   │   └── sahool-pr-previews-appset.yaml
│   └── secrets/
│       └── github-pr-generator-secret.yaml
│
├── environments/
│   └── preview/
│       └── values.yaml             # Preview environment config
│
├── feature-flags/
│   └── flagd/                      # OpenFeature flagd setup
│       ├── configmap.yaml
│       ├── deployment.yaml
│       ├── kustomization.yaml
│       ├── namespace.yaml
│       └── service.yaml
│
├── idp/
│   └── applications/               # IDP (Backstage) apps
│       ├── backstage-app.yaml
│       └── kustomization.yaml
│
├── ingress/
│   ├── README.md
│   ├── cert-manager/
│   │   └── cluster-issuer.yaml     # Let's Encrypt issuer
│   └── templates/
│       └── pr-preview-ingress.yaml
│
├── sahool/
│   └── services/
│       └── billing-core/           # Service manifests
│           ├── deployment.yaml
│           ├── kustomization.yaml
│           └── service.yaml
│
├── scripts/
│   └── install-pr-previews.sh      # PR preview automation
│
└── secrets/
    ├── external-secret-example.yaml
    └── secretstore.yaml
```

---

## ArgoCD Applications

### Core Infrastructure

| Application | Description |
|-------------|-------------|
| `cert-manager-app` | TLS certificate management |
| `ingress-nginx-app` | Ingress controller |
| `external-secrets-app` | External secrets operator |
| `argo-rollouts-app` | Progressive delivery |

### SAHOOL Services

| Application | Description |
|-------------|-------------|
| `billing-core-app` | Billing service deployment |
| `feature-flags-app` | Feature flag service |
| `idp-root-app` | Internal Developer Portal |

---

## ApplicationSets

### Multi-cluster Deployment

```yaml
# sahool-multicluster-appset.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: sahool-multicluster
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            env: production
  template:
    spec:
      project: sahool
      source:
        repoURL: https://github.com/kafaat/sahool-unified-v15-idp
        path: helm/sahool
```

### PR Previews

```yaml
# sahool-pr-previews-appset.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: sahool-pr-previews
spec:
  generators:
    - pullRequest:
        github:
          owner: kafaat
          repo: sahool-unified-v15-idp
```

---

## Feature Flags

OpenFeature-compatible feature flags using flagd:

```yaml
# flagd/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: flagd-config
data:
  flags.json: |
    {
      "flags": {
        "offline-mode": {
          "state": "ENABLED",
          "variants": { "on": true, "off": false },
          "defaultVariant": "on"
        }
      }
    }
```

### Deploy flagd

```bash
kubectl apply -k gitops/feature-flags/flagd/
```

---

## Secrets Management

### External Secrets Operator

```yaml
# secretstore.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.sahool.io"
      path: "secret"
      auth:
        kubernetes:
          mountPath: "kubernetes"
```

### Creating External Secret

```yaml
# external-secret-example.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
  target:
    name: db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: database/creds
        property: password
```

---

## PR Preview Environments

Automatic preview environments for pull requests:

### Setup

```bash
# Install PR preview automation
./gitops/scripts/install-pr-previews.sh
```

### How It Works

1. PR opened -> ApplicationSet creates preview
2. Preview URL: `https://pr-{number}.preview.sahool.io`
3. PR closed -> Preview automatically deleted

### Ingress Template

```yaml
# pr-preview-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pr-{{ .pr_number }}-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
    - host: pr-{{ .pr_number }}.preview.sahool.io
```

---

## Deployment Flow

```
┌──────────────┐
│   Git Push   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   ArgoCD     │
│   Sync       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Kubernetes  │
│   Apply      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Rollout     │
│  (Canary)    │
└──────────────┘
```

---

## Commands

```bash
# Sync application
argocd app sync sahool

# Get app status
argocd app get sahool

# Diff changes
argocd app diff sahool

# Rollback
argocd app rollback sahool
```

---

## Related Documentation

- [Helm Charts](../helm/README.md)
- [Infrastructure](../infra/README.md)
- [Architecture](../docs/architecture/PRINCIPLES.md)

---

<p align="center">
  <sub>SAHOOL GitOps v15.5</sub>
  <br>
  <sub>December 2025</sub>
</p>
