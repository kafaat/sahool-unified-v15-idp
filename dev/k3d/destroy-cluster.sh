#!/usr/bin/env bash
set -euo pipefail
k3d cluster delete "${CLUSTER_NAME:-sahool-dev}"
