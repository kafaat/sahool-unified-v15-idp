#!/usr/bin/env bash
set -euo pipefail

echo "✅ Installing PR Preview Environments (ApplicationSet)"
echo "1) Apply GitHub token secret template (edit first!)"
echo "   kubectl apply -f gitops/argocd/secrets/github-pr-generator-secret.yaml"
echo "2) Apply the ApplicationSet"
kubectl apply -f gitops/argocd/applicationsets/sahool-pr-previews-appset.yaml

echo ""
echo "Done. Argo CD will create Apps per PR."
