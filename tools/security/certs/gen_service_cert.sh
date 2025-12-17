#!/usr/bin/env bash
#
# SAHOOL Service Certificate Generator
# Generates mTLS certificates for services signed by internal CA
#
# Usage:
#   ./gen_service_cert.sh <service_name> [output_dir]
#
# Example:
#   ./gen_service_cert.sh kernel infra/pki
#   ./gen_service_cert.sh field_suite infra/pki
#   ./gen_service_cert.sh advisor infra/pki
#
# Prerequisites:
#   - CA must exist (run gen_ca.sh first)
#

set -euo pipefail

# Configuration
SERVICE="${1:?Usage: $0 <service_name> [output_dir]}"
OUT_DIR="${2:-infra/pki}"
CERT_DAYS="${CERT_DAYS:-825}"  # ~2.25 years (Apple max)
KEY_SIZE="${KEY_SIZE:-2048}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "  SAHOOL Service Certificate Generator"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check CA exists
if [[ ! -f "$OUT_DIR/ca.key" ]] || [[ ! -f "$OUT_DIR/ca.crt" ]]; then
    echo -e "${RED}❌ CA not found at $OUT_DIR${NC}"
    echo "   Run gen_ca.sh first to create the CA."
    exit 1
fi

# Create service directory
SERVICE_DIR="$OUT_DIR/$SERVICE"
mkdir -p "$SERVICE_DIR"

echo "🔧 Service: $SERVICE"
echo "📁 Output: $SERVICE_DIR"
echo "📅 Validity: $CERT_DAYS days"
echo ""

# Generate private key
echo "🔐 Generating private key..."
openssl genrsa -out "$SERVICE_DIR/tls.key" "$KEY_SIZE" 2>/dev/null

# Generate CSR
echo "📝 Generating certificate signing request..."
openssl req -new \
    -key "$SERVICE_DIR/tls.key" \
    -subj "/C=YE/ST=Sana'a/O=SAHOOL/OU=Services/CN=${SERVICE}" \
    -out "$SERVICE_DIR/tls.csr"

# Create SAN config for the service
# Includes common DNS names and localhost for development
echo "📋 Creating SAN configuration..."
cat > "$SERVICE_DIR/san.cnf" <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${SERVICE}
DNS.2 = ${SERVICE}.local
DNS.3 = ${SERVICE}.sahool.local
DNS.4 = ${SERVICE}.default.svc.cluster.local
DNS.5 = localhost
IP.1 = 127.0.0.1
EOF

# Sign certificate with CA
echo "✍️  Signing certificate with CA..."
openssl x509 -req \
    -in "$SERVICE_DIR/tls.csr" \
    -CA "$OUT_DIR/ca.crt" \
    -CAkey "$OUT_DIR/ca.key" \
    -CAcreateserial \
    -out "$SERVICE_DIR/tls.crt" \
    -days "$CERT_DAYS" \
    -sha256 \
    -extfile "$SERVICE_DIR/san.cnf" \
    -extensions v3_req 2>/dev/null

# Set permissions
chmod 600 "$SERVICE_DIR/tls.key"
chmod 644 "$SERVICE_DIR/tls.crt"

# Clean up CSR (not needed after signing)
rm -f "$SERVICE_DIR/tls.csr"

echo ""
echo -e "${GREEN}✅ Certificate created for $SERVICE!${NC}"
echo ""
echo "Files created:"
echo "   - $SERVICE_DIR/tls.key (private key)"
echo "   - $SERVICE_DIR/tls.crt (certificate)"
echo "   - $SERVICE_DIR/san.cnf (SAN config)"
echo ""

# Verify certificate
echo "📋 Certificate Details:"
openssl x509 -in "$SERVICE_DIR/tls.crt" -noout -subject -dates
echo ""
echo "📋 Subject Alternative Names:"
openssl x509 -in "$SERVICE_DIR/tls.crt" -noout -ext subjectAltName 2>/dev/null || echo "   (none)"
