#!/usr/bin/env bash
set -euo pipefail

echo "🚀 SAHOOL dev start (docker compose)"
cd "$(dirname "$0")/../.."

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  docker compose up --build
else
  echo "❌ docker compose not found. Install Docker Desktop or Docker Engine + Compose."
  exit 1
fi
