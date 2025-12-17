#!/usr/bin/env bash
#
# SAHOOL Internal CA Generator
# Generates a root CA for internal mTLS communication
#
# Usage:
#   ./gen_ca.sh [output_dir]
#
# Example:
#   ./gen_ca.sh infra/pki
#
# IMPORTANT:
#   - Never commit ca.key to version control
#   - Store ca.key securely (Vault, HSM, etc.)
#   - Rotate CA before expiration (10 years default)
#

set -euo pipefail

# Configuration
OUT_DIR="${1:-infra/pki}"
CA_DAYS="${CA_DAYS:-3650}"  # 10 years
CA_KEY_SIZE="${CA_KEY_SIZE:-4096}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "  SAHOOL Internal CA Generator"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Create output directory
mkdir -p "$OUT_DIR"

# Check if CA already exists
if [[ -f "$OUT_DIR/ca.key" ]]; then
    echo -e "${YELLOW}⚠️  CA already exists at $OUT_DIR/ca.key${NC}"
    echo "   Delete existing CA files to regenerate."
    exit 1
fi

echo "📁 Output directory: $OUT_DIR"
echo "🔑 Key size: $CA_KEY_SIZE bits"
echo "📅 Validity: $CA_DAYS days"
echo ""

# Generate CA private key
echo "🔐 Generating CA private key..."
openssl genrsa -out "$OUT_DIR/ca.key" "$CA_KEY_SIZE" 2>/dev/null

# Generate CA certificate
echo "📜 Generating CA certificate..."
openssl req -x509 -new -nodes \
    -key "$OUT_DIR/ca.key" \
    -sha256 \
    -days "$CA_DAYS" \
    -subj "/C=YE/ST=Sana'a/O=SAHOOL/OU=Platform Security/CN=SAHOOL Internal CA" \
    -out "$OUT_DIR/ca.crt"

# Set permissions
chmod 600 "$OUT_DIR/ca.key"
chmod 644 "$OUT_DIR/ca.crt"

echo ""
echo -e "${GREEN}✅ CA created successfully!${NC}"
echo ""
echo "Files created:"
echo "   - $OUT_DIR/ca.key (private key - KEEP SECRET)"
echo "   - $OUT_DIR/ca.crt (certificate - distribute to services)"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Never commit ca.key to version control!${NC}"
echo ""

# Verify certificate
echo "📋 CA Certificate Details:"
openssl x509 -in "$OUT_DIR/ca.crt" -noout -subject -dates
