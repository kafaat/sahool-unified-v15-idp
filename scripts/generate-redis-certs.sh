#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Redis TLS Certificate Generation Script
# سكريبت إنشاء شهادات TLS لـ Redis
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script generates self-signed TLS certificates for Redis
# For production, use proper CA-signed certificates
#
# Usage:
#   ./scripts/generate-redis-certs.sh
#
# Output:
#   - config/redis/certs/ca.crt (CA certificate)
#   - config/redis/certs/ca.key (CA private key)
#   - config/redis/certs/server.crt (Redis server certificate)
#   - config/redis/certs/server.key (Redis server private key)
#   - config/redis/certs/client.crt (Client certificate - optional)
#   - config/redis/certs/client.key (Client private key - optional)
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CERT_DIR="config/redis/certs"
VALIDITY_DAYS=3650  # 10 years
COUNTRY="SA"
STATE="Riyadh"
CITY="Riyadh"
ORG="SAHOOL Agricultural Platform"
COMMON_NAME="sahool-redis"

# ─────────────────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Script
# ─────────────────────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  Redis TLS Certificate Generation"
echo "  إنشاء شهادات TLS لـ Redis"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    log_error "OpenSSL is not installed. Please install it first."
    echo "  Ubuntu/Debian: sudo apt-get install openssl"
    echo "  CentOS/RHEL: sudo yum install openssl"
    echo "  macOS: brew install openssl"
    exit 1
fi

log_info "OpenSSL version: $(openssl version)"
echo ""

# Create certificate directory
log_info "Creating certificate directory: $CERT_DIR"
mkdir -p "$CERT_DIR"

# Change to cert directory
cd "$CERT_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Generate CA (Certificate Authority)
# ─────────────────────────────────────────────────────────────────────────────

log_info "Step 1: Generating CA certificate..."

# Generate CA private key
openssl genrsa -out ca.key 4096 2>/dev/null

# Generate CA certificate
openssl req -new -x509 -days $VALIDITY_DAYS -key ca.key -out ca.crt \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/CN=SAHOOL Redis CA" \
    2>/dev/null

log_success "CA certificate generated: ca.crt"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Generate Server Certificate
# ─────────────────────────────────────────────────────────────────────────────

log_info "Step 2: Generating Redis server certificate..."

# Generate server private key
openssl genrsa -out server.key 4096 2>/dev/null

# Create server certificate signing request (CSR)
openssl req -new -key server.key -out server.csr \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/CN=$COMMON_NAME" \
    2>/dev/null

# Create extensions file for Subject Alternative Names (SAN)
cat > server_ext.cnf <<EOF
basicConstraints = CA:FALSE
nsCertType = server
nsComment = "SAHOOL Redis Server Certificate"
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer:always
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = redis
DNS.2 = sahool-redis
DNS.3 = redis-master
DNS.4 = localhost
DNS.5 = *.sahool.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Sign server certificate with CA
openssl x509 -req -days $VALIDITY_DAYS -in server.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -extfile server_ext.cnf \
    2>/dev/null

# Clean up CSR and extensions file
rm -f server.csr server_ext.cnf

log_success "Server certificate generated: server.crt"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Generate Client Certificate (Optional)
# ─────────────────────────────────────────────────────────────────────────────

log_info "Step 3: Generating client certificate (optional)..."

# Generate client private key
openssl genrsa -out client.key 4096 2>/dev/null

# Create client certificate signing request (CSR)
openssl req -new -key client.key -out client.csr \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/CN=SAHOOL Redis Client" \
    2>/dev/null

# Create extensions file for client
cat > client_ext.cnf <<EOF
basicConstraints = CA:FALSE
nsCertType = client, email
nsComment = "SAHOOL Redis Client Certificate"
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth, emailProtection
EOF

# Sign client certificate with CA
openssl x509 -req -days $VALIDITY_DAYS -in client.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -extfile client_ext.cnf \
    2>/dev/null

# Clean up CSR and extensions file
rm -f client.csr client_ext.cnf ca.srl

log_success "Client certificate generated: client.crt"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Set Permissions
# ─────────────────────────────────────────────────────────────────────────────

log_info "Step 4: Setting file permissions..."

# Set restrictive permissions on private keys
chmod 600 ca.key server.key client.key

# Set readable permissions on certificates
chmod 644 ca.crt server.crt client.crt

log_success "Permissions set successfully"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Verify Certificates
# ─────────────────────────────────────────────────────────────────────────────

log_info "Step 5: Verifying certificates..."

# Verify server certificate
if openssl verify -CAfile ca.crt server.crt 2>/dev/null | grep -q "OK"; then
    log_success "Server certificate verification: OK"
else
    log_error "Server certificate verification failed"
    exit 1
fi

# Verify client certificate
if openssl verify -CAfile ca.crt client.crt 2>/dev/null | grep -q "OK"; then
    log_success "Client certificate verification: OK"
else
    log_error "Client certificate verification failed"
    exit 1
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Display Certificate Information
# ─────────────────────────────────────────────────────────────────────────────

log_info "Certificate Information:"
echo ""
echo "📁 Certificate Directory: $(pwd)"
echo ""
echo "📄 Generated Files:"
echo "   ├── ca.crt          (CA Certificate - 4096 bit RSA)"
echo "   ├── ca.key          (CA Private Key - KEEP SECURE!)"
echo "   ├── server.crt      (Server Certificate - 4096 bit RSA)"
echo "   ├── server.key      (Server Private Key - KEEP SECURE!)"
echo "   ├── client.crt      (Client Certificate - 4096 bit RSA)"
echo "   └── client.key      (Client Private Key - KEEP SECURE!)"
echo ""

# Display CA certificate details
log_info "CA Certificate Details:"
openssl x509 -in ca.crt -noout -subject -issuer -dates | sed 's/^/   /'
echo ""

# Display server certificate details
log_info "Server Certificate Details:"
openssl x509 -in server.crt -noout -subject -issuer -dates | sed 's/^/   /'
echo ""

# Display Subject Alternative Names
log_info "Server Certificate SANs:"
openssl x509 -in server.crt -noout -text | grep -A 10 "Subject Alternative Name" | sed 's/^/   /'
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 7: Generate Docker Compose Volume Mount Instructions
# ─────────────────────────────────────────────────────────────────────────────

cat > ../REDIS_TLS_SETUP.md <<EOF
# Redis TLS Setup Instructions

## Certificate Files Generated

The following TLS certificates have been generated in \`config/redis/certs/\`:

- **ca.crt**: CA Certificate (safe to share)
- **ca.key**: CA Private Key (⚠️ KEEP SECURE - DO NOT COMMIT)
- **server.crt**: Redis Server Certificate (safe to share)
- **server.key**: Redis Server Private Key (⚠️ KEEP SECURE - DO NOT COMMIT)
- **client.crt**: Client Certificate (optional, safe to share)
- **client.key**: Client Private Key (optional, ⚠️ KEEP SECURE - DO NOT COMMIT)

## Enabling TLS in Docker Compose

### Option 1: Use redis-secure.conf with TLS enabled

1. Uncomment TLS settings in \`infrastructure/redis/redis-secure.conf\`:

\`\`\`conf
port 0
tls-port 6379
tls-cert-file /etc/redis/certs/server.crt
tls-key-file /etc/redis/certs/server.key
tls-ca-cert-file /etc/redis/certs/ca.crt
tls-auth-clients optional
tls-protocols "TLSv1.2 TLSv1.3"
tls-prefer-server-ciphers yes
tls-ciphers "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4"
tls-session-caching yes
\`\`\`

2. Update \`docker-compose.yml\` to mount certificates:

\`\`\`yaml
redis:
  volumes:
    - redis_data:/data
    - ./infrastructure/redis/redis-secure.conf:/usr/local/etc/redis/redis.conf:ro
    - ./config/redis/certs:/etc/redis/certs:ro  # Add this line
\`\`\`

### Option 2: Use command-line arguments

Update the Redis command in \`docker-compose.yml\`:

\`\`\`yaml
redis:
  command: [
    "redis-server",
    "/usr/local/etc/redis/redis.conf",
    "--requirepass", "\${REDIS_PASSWORD}",
    "--maxmemory", "512mb",
    "--port", "0",
    "--tls-port", "6379",
    "--tls-cert-file", "/etc/redis/certs/server.crt",
    "--tls-key-file", "/etc/redis/certs/server.key",
    "--tls-ca-cert-file", "/etc/redis/certs/ca.crt",
    "--tls-auth-clients", "optional"
  ]
  volumes:
    - ./config/redis/certs:/etc/redis/certs:ro
\`\`\`

## Updating Connection Strings

After enabling TLS, update all Redis connection strings from:

\`\`\`
redis://:password@redis:6379/0
\`\`\`

to:

\`\`\`
rediss://:password@redis:6379/0
\`\`\`

Note the **rediss://** (with double 's') protocol for TLS connections.

## Testing TLS Connection

\`\`\`bash
# Test TLS connection
redis-cli --tls \\
  --cert config/redis/certs/client.crt \\
  --key config/redis/certs/client.key \\
  --cacert config/redis/certs/ca.crt \\
  -h localhost -p 6379 -a \${REDIS_PASSWORD} PING
\`\`\`

## Security Best Practices

1. **NEVER commit private keys (.key files) to version control**
2. Add to .gitignore:
   \`\`\`
   config/redis/certs/*.key
   \`\`\`
3. Store production certificates in secure vault (HashiCorp Vault, AWS Secrets Manager, etc.)
4. Rotate certificates every 90 days in production
5. Use proper CA-signed certificates in production (not self-signed)

## Certificate Validity

- **Generated on**: $(date)
- **Valid for**: $VALIDITY_DAYS days ($((VALIDITY_DAYS / 365)) years)
- **Expires on**: $(date -d "+$VALIDITY_DAYS days" 2>/dev/null || date -v +${VALIDITY_DAYS}d 2>/dev/null || echo "N/A")

## Regenerating Certificates

To regenerate certificates (e.g., before expiration):

\`\`\`bash
./scripts/generate-redis-certs.sh
\`\`\`

EOF

log_success "TLS setup instructions created: config/redis/REDIS_TLS_SETUP.md"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 8: Update .gitignore
# ─────────────────────────────────────────────────────────────────────────────

cd ../../..  # Return to project root

log_info "Step 8: Updating .gitignore to protect private keys..."

GITIGNORE_ENTRY="
# Redis TLS Certificates - Private Keys (DO NOT COMMIT)
config/redis/certs/*.key
"

if ! grep -q "config/redis/certs/\*\.key" .gitignore 2>/dev/null; then
    echo "$GITIGNORE_ENTRY" >> .gitignore
    log_success ".gitignore updated"
else
    log_info ".gitignore already contains Redis certificate exclusions"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════════════════════════"
log_success "Redis TLS certificates generated successfully!"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
log_warning "IMPORTANT SECURITY NOTES:"
echo "  1. Private keys (*.key) have been excluded from git"
echo "  2. DO NOT commit private keys to version control"
echo "  3. Store production keys in a secure vault"
echo "  4. Use proper CA-signed certificates in production"
echo ""
log_info "Next Steps:"
echo "  1. Review: config/redis/REDIS_TLS_SETUP.md"
echo "  2. Enable TLS in redis configuration"
echo "  3. Update docker-compose.yml to mount certificates"
echo "  4. Update connection strings to use rediss://"
echo "  5. Test connectivity with: redis-cli --tls ..."
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
