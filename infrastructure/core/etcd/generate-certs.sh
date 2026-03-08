#!/bin/sh
# ═══════════════════════════════════════════════════════════════════════════════
# Etcd TLS Certificate Generation Script
# Generates self-signed certificates for etcd client/server TLS
#
# Usage: ./generate-certs.sh [output_dir]
# Default output: ./certs/
# ═══════════════════════════════════════════════════════════════════════════════

set -e

OUTPUT_DIR="${1:-./infrastructure/core/etcd/certs}"
DAYS_VALID=365
KEY_SIZE=4096

echo "Generating etcd TLS certificates in ${OUTPUT_DIR}..."
mkdir -p "$OUTPUT_DIR"

# Generate CA key and certificate
openssl genrsa -out "$OUTPUT_DIR/ca-key.pem" "$KEY_SIZE" 2>/dev/null
openssl req -new -x509 -key "$OUTPUT_DIR/ca-key.pem" \
    -out "$OUTPUT_DIR/ca.pem" -days "$DAYS_VALID" \
    -subj "/CN=sahool-etcd-ca/O=SAHOOL/C=SA" 2>/dev/null

# Generate server key and CSR
openssl genrsa -out "$OUTPUT_DIR/server-key.pem" "$KEY_SIZE" 2>/dev/null
openssl req -new -key "$OUTPUT_DIR/server-key.pem" \
    -out "$OUTPUT_DIR/server.csr" \
    -subj "/CN=etcd/O=SAHOOL/C=SA" 2>/dev/null

# Create SAN extension file for server cert
cat > "$OUTPUT_DIR/server-ext.cnf" << EOF
[v3_req]
subjectAltName = @alt_names
[alt_names]
DNS.1 = etcd
DNS.2 = localhost
DNS.3 = sahool-etcd
IP.1 = 127.0.0.1
EOF

# Sign server certificate
openssl x509 -req -in "$OUTPUT_DIR/server.csr" \
    -CA "$OUTPUT_DIR/ca.pem" -CAkey "$OUTPUT_DIR/ca-key.pem" \
    -CAcreateserial -out "$OUTPUT_DIR/server.pem" \
    -days "$DAYS_VALID" -extensions v3_req \
    -extfile "$OUTPUT_DIR/server-ext.cnf" 2>/dev/null

# Cleanup CSR and extension files
rm -f "$OUTPUT_DIR/server.csr" "$OUTPUT_DIR/server-ext.cnf" "$OUTPUT_DIR/ca.srl"

# Set permissions
chmod 600 "$OUTPUT_DIR"/*-key.pem
chmod 644 "$OUTPUT_DIR"/ca.pem "$OUTPUT_DIR"/server.pem

echo "TLS certificates generated successfully:"
echo "  CA:     $OUTPUT_DIR/ca.pem"
echo "  Server: $OUTPUT_DIR/server.pem"
echo "  Key:    $OUTPUT_DIR/server-key.pem"
echo ""
echo "To enable TLS in docker-compose.yml, set:"
echo "  ETCD_ENABLE_TLS=true"
