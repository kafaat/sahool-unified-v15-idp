#!/usr/bin/env bash
set -euo pipefail

echo "==> Creating namespaces (monitoring, sahool)..."
kubectl apply -f k8s/addons/00-namespaces.yaml

echo "==> Installing Metrics Server (required for HPA CPU/Memory)..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

echo "==> Adding prometheus-community repo..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "==> Installing kube-prometheus-stack (Prometheus + Grafana + Alertmanager)..."
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --version 80.2.0

echo "==> Installing prometheus-adapter (Custom Metrics API)..."
helm upgrade --install prometheus-adapter prometheus-community/prometheus-adapter \
  --namespace monitoring \
  --version 5.2.0 \
  -f k8s/addons/prometheus-adapter-values.yaml

echo "==> Done."
echo "Tip: verify:"
echo "  kubectl top nodes"
echo "  kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1 | head"
