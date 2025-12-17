#!/usr/bin/env bash
#
# SAHOOL Generate All Certificates
# Generates CA and certificates for all services
#
# Usage:
#   ./gen_all_certs.sh [output_dir]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${1:-infra/pki}"

# Services that need certificates
SERVICES=(
    "kernel"
    "field_suite"
    "advisor"
    "api_gateway"
    "field_ops"
    "ndvi_engine"
    "weather_core"
    "iot_gateway"
)

echo "════════════════════════════════════════════════════════════════"
echo "  SAHOOL Full Certificate Generation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Generate CA
echo "📜 Step 1: Generate CA"
echo "────────────────────────────────────────"
bash "$SCRIPT_DIR/gen_ca.sh" "$OUT_DIR" || {
    echo "CA already exists, continuing..."
}
echo ""

# Generate service certificates
echo "🔐 Step 2: Generate Service Certificates"
echo "────────────────────────────────────────"
for service in "${SERVICES[@]}"; do
    echo ""
    echo "→ $service"
    bash "$SCRIPT_DIR/gen_service_cert.sh" "$service" "$OUT_DIR"
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ All certificates generated!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Directory structure:"
find "$OUT_DIR" -type f -name "*.crt" -o -name "*.key" 2>/dev/null | sort
echo ""
echo "⚠️  Remember: Never commit private keys (*.key) to version control!"
