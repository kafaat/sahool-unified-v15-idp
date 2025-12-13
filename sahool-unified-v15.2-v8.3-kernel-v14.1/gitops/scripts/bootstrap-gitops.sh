#!/usr/bin/env bash
set -euo pipefail

echo "==> Bootstrapping Argo CD + SAHOOL GitOps"

# 1) Install Argo CD (if not installed)
kubectl create namespace argocd >/dev/null 2>&1 || true
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "==> Apply SAHOOL namespaces + project + root app"
kubectl apply -f gitops/argocd/namespace.yaml
kubectl apply -f gitops/argocd/project-sahool.yaml
kubectl apply -f gitops/argocd/applications/root-app.yaml

echo
echo "IMPORTANT:"
echo "- Edit gitops/argocd/applications/*.yaml and replace REPLACE_WITH_YOUR_REPO_URL"
echo "- Then Argo CD will sync automatically."
