#!/usr/bin/env bash
# scripts/docker-pull-retry.sh
# Pull all external Docker images used in docker-compose.yml with retry logic.
# Images prefixed with "sahool/" are internal builds and are excluded.
#
# Usage:
#   bash scripts/docker-pull-retry.sh
#   chmod +x scripts/docker-pull-retry.sh && ./scripts/docker-pull-retry.sh

set -euo pipefail

# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------
pull_with_retry() {
  local image="$1"
  local max_attempts=5
  local attempt

  for attempt in $(seq 1 "$max_attempts"); do
    echo "[attempt $attempt/$max_attempts] Pulling $image..."
    if docker pull "$image"; then
      echo "✓ $image pulled successfully"
      return 0
    fi
    if [ "$attempt" -lt "$max_attempts" ]; then
      echo "  Retrying in 10 seconds..."
      sleep 10
    fi
  done

  echo "✗ Failed to pull $image after $max_attempts attempts"
  return 1
}

# ---------------------------------------------------------------------------
# External images extracted from docker-compose.yml
# (sahool/* internal images are excluded — they are built locally)
# ---------------------------------------------------------------------------
IMAGES=(
  # Infrastructure
  "postgis/postgis:16-3.4"
  "redis:7.4-alpine"
  "hashicorp/vault:1.17"
  "nats:2.10.24-alpine"
  "natsio/prometheus-nats-exporter:0.14.0"
  "eclipse-mosquitto:2.0.20"
  "kong:3.9.0"
  "alpine:3.20"

  # Data stores
  "qdrant/qdrant:v1.10.1"
  "mongo:6.0"
  "minio/minio:RELEASE.2025-03-12T18-04-18Z"
  "milvusdb/milvus:v2.5.27"
  "quay.io/coreos/etcd:v3.5.18"  # quay.io registry

  # AI / ML
  "ghcr.io/mlflow/mlflow:v2.15.1"  # GitHub Container Registry
  "ollama/ollama:0.5.4"

  # Communication
  "rocketchat/rocket.chat:7.5.0"

  # Utilities
  "curlimages/curl:8.11.1"
)

# ---------------------------------------------------------------------------
# Pull loop
# ---------------------------------------------------------------------------
FAILED=()

echo "============================================================"
echo "  SAHOOL Docker image pre-pull"
echo "  Images to pull: ${#IMAGES[@]}"
echo "  Max attempts per image: 5  |  Retry wait: 10s"
echo "============================================================"
echo ""

for image in "${IMAGES[@]}"; do
  if pull_with_retry "$image"; then
    : # success already reported inside the function
  else
    FAILED+=("$image")
  fi
  echo ""
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "============================================================"
echo "  SUMMARY"
echo "============================================================"
echo "  Total:     ${#IMAGES[@]}"
echo "  Succeeded: $(( ${#IMAGES[@]} - ${#FAILED[@]} ))"
echo "  Failed:    ${#FAILED[@]}"

if [ "${#FAILED[@]}" -gt 0 ]; then
  echo ""
  echo "FAILED images:"
  for img in "${FAILED[@]}"; do
    echo "  ✗ $img"
  done
  echo ""
  exit 1
fi

echo ""
echo "All images pulled successfully."
