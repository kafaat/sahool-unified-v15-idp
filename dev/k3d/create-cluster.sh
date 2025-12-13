#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-sahool-dev}"
K8S_VERSION="${K8S_VERSION:-v1.30.4-k3s1}"

if ! command -v k3d >/dev/null 2>&1; then
  echo "❌ k3d not found. Install k3d first."
  exit 1
fi

echo "🚀 Creating k3d cluster: ${CLUSTER_NAME}"
k3d cluster create "${CLUSTER_NAME}" \
  --image "rancher/k3s:${K8S_VERSION}" \
  --agents 2 \
  --servers 1 \
  --k3s-arg "--disable=traefik@server:0" \
  --port "8080:80@loadbalancer" \
  --port "8443:443@loadbalancer"

echo "✅ Cluster ready"
kubectl cluster-info
