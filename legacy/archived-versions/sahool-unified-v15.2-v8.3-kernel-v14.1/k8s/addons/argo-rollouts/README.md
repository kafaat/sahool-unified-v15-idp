# Argo Rollouts Addon

This folder contains helpers to install and verify Argo Rollouts (controller + dashboard) and to test SAHOOL canary rollouts.

## Install (Helm)
Recommended via GitOps (Argo CD) using `gitops/argocd/applications/argo-rollouts-app.yaml`.

Manual install:
```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
kubectl create namespace argo-rollouts --dry-run=client -o yaml | kubectl apply -f -
helm upgrade --install argo-rollouts argo/argo-rollouts -n argo-rollouts   --version 2.39.6   --set controller.metrics.enabled=true   --set dashboard.enabled=true
```

## Verify
```bash
kubectl get pods -n argo-rollouts
kubectl argo rollouts version || true
```

## SAHOOL Rollouts
The SAHOOL Helm chart will create `Rollout` objects (instead of `Deployment`) when:
- `.Values.rollouts.enabled=true`
- and `services.<svc>.rollout.enabled=true` (default: false)

Adjust canary steps in `k8s/helm/sahool-kernel/values.yaml` under `rollouts.canary.steps`.
