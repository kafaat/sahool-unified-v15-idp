#!/usr/bin/env bash
set -euo pipefail

if ! command -v helm >/dev/null 2>&1; then
  echo "helm is required" >&2
  exit 1
fi

helm repo add argo https://argoproj.github.io/argo-helm >/dev/null
helm repo update >/dev/null

kubectl create namespace argo-rollouts --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install argo-rollouts argo/argo-rollouts -n argo-rollouts   --version 2.39.6   --set controller.metrics.enabled=true   --set dashboard.enabled=true

echo "✅ Argo Rollouts installed in namespace argo-rollouts"
