#!/usr/bin/env bash
set -euo pipefail

NS="${1:-sahool}"

echo "== Rollouts in namespace: $NS =="
kubectl get rollout -n "$NS" || true
echo

echo "== AnalysisTemplates =="
kubectl get analysistemplate -n "$NS" || true
echo

echo "== HPAs =="
kubectl get hpa -n "$NS" || true
echo

echo "Tip: Install kubectl argo rollouts plugin to inspect canary steps:"
echo "  kubectl argo rollouts list rollouts -n $NS"
echo "  kubectl argo rollouts get rollout <name> -n $NS"
