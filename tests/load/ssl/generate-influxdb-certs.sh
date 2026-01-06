#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - InfluxDB TLS Certificate Generation Script
# توليد شهادات TLS لقاعدة بيانات InfluxDB
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script generates self-signed TLS certificates for InfluxDB instances
# For production, replace with CA-signed certificates
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_DIR="${SCRIPT_DIR}"

# Certificate validity (days)
VALIDITY_DAYS=365

# Certificate details
COUNTRY="SA"
STATE="Riyadh"
LOCALITY="Riyadh"
ORGANIZATION="SAHOOL Agricultural Platform"
OU="Infrastructure Security"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}SAHOOL InfluxDB TLS Certificate Generator${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to generate certificates for a specific environment
generate_cert() {
    local ENV_NAME=$1
    local COMMON_NAME=$2
    local KEY_FILE="${CERT_DIR}/influxdb-${ENV_NAME}-key.pem"
    local CERT_FILE="${CERT_DIR}/influxdb-${ENV_NAME}-cert.pem"
    local CSR_FILE="${CERT_DIR}/influxdb-${ENV_NAME}.csr"

    echo -e "${YELLOW}Generating certificates for ${ENV_NAME} environment...${NC}"

    # Generate private key
    openssl genrsa -out "${KEY_FILE}" 4096 2>/dev/null
    echo -e "${GREEN}✓ Private key generated: ${KEY_FILE}${NC}"

    # Generate certificate signing request
    openssl req -new \
        -key "${KEY_FILE}" \
        -out "${CSR_FILE}" \
        -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/OU=${OU}/CN=${COMMON_NAME}" \
        2>/dev/null
    echo -e "${GREEN}✓ CSR generated: ${CSR_FILE}${NC}"

    # Generate self-signed certificate
    openssl x509 -req \
        -days ${VALIDITY_DAYS} \
        -in "${CSR_FILE}" \
        -signkey "${KEY_FILE}" \
        -out "${CERT_FILE}" \
        -extfile <(printf "subjectAltName=DNS:${COMMON_NAME},DNS:localhost,IP:127.0.0.1") \
        2>/dev/null
    echo -e "${GREEN}✓ Certificate generated: ${CERT_FILE}${NC}"

    # Set proper permissions
    chmod 600 "${KEY_FILE}"
    chmod 644 "${CERT_FILE}"

    # Clean up CSR
    rm -f "${CSR_FILE}"

    # Display certificate info
    echo -e "${YELLOW}Certificate Information:${NC}"
    openssl x509 -in "${CERT_FILE}" -noout -subject -dates -fingerprint -sha256
    echo ""
}

# Generate certificates for each environment
echo "Generating certificates for all InfluxDB environments..."
echo ""

# Load Testing Environment
generate_cert "load" "influxdb"

# Simulation Environment
generate_cert "sim" "sahool-influxdb"

# Advanced Environment
generate_cert "advanced" "sahool-influxdb"

# Create combined certificate bundle for easier management
echo -e "${YELLOW}Creating certificate bundle...${NC}"
cat "${CERT_DIR}/influxdb-load-cert.pem" > "${CERT_DIR}/bundle.crt"
cat "${CERT_DIR}/influxdb-sim-cert.pem" >> "${CERT_DIR}/bundle.crt"
cat "${CERT_DIR}/influxdb-advanced-cert.pem" >> "${CERT_DIR}/bundle.crt"
echo -e "${GREEN}✓ Certificate bundle created: ${CERT_DIR}/bundle.crt${NC}"
echo ""

# Create a README for certificate management
cat > "${CERT_DIR}/README.md" << 'EOF'
# InfluxDB TLS Certificates

## Generated Certificates

This directory contains TLS certificates for InfluxDB instances across different environments:

### Files Generated

- `influxdb-load-key.pem` / `influxdb-load-cert.pem` - Load Testing Environment
- `influxdb-sim-key.pem` / `influxdb-sim-cert.pem` - Simulation Environment
- `influxdb-advanced-key.pem` / `influxdb-advanced-cert.pem` - Advanced Environment
- `bundle.crt` - Combined certificate bundle

### Security Notes

⚠️ **IMPORTANT**: These are self-signed certificates for development/testing only.

For production environments:
1. Use CA-signed certificates
2. Store private keys in secure key management systems (HashiCorp Vault, AWS KMS, etc.)
3. Implement certificate rotation policies
4. Monitor certificate expiration dates

### Certificate Validity

- Validity: 365 days from generation
- Renewal: Re-run `generate-influxdb-certs.sh` before expiration

### Usage in Docker Compose

```yaml
volumes:
  - ./ssl/influxdb-load-cert.pem:/etc/ssl/influxdb-cert.pem:ro
  - ./ssl/influxdb-load-key.pem:/etc/ssl/influxdb-key.pem:ro
```

### Verification

Test certificate:
```bash
openssl x509 -in influxdb-load-cert.pem -noout -text
openssl verify -CAfile influxdb-load-cert.pem influxdb-load-cert.pem
```

Test InfluxDB TLS connection:
```bash
curl --cacert influxdb-load-cert.pem https://localhost:8086/ping
```

### Regeneration

To regenerate all certificates:
```bash
./generate-influxdb-certs.sh
```

## File Permissions

- Private keys: 600 (read/write for owner only)
- Certificates: 644 (readable by all, writable by owner)

Do not commit private keys to version control!
EOF

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Certificate generation complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the generated certificates in: ${CERT_DIR}"
echo "2. Update docker-compose files to mount certificates"
echo "3. Configure InfluxDB to use TLS"
echo "4. Update client configurations (k6, Grafana) to use HTTPS"
echo ""
echo -e "${RED}⚠️  SECURITY WARNING:${NC}"
echo -e "${RED}   These are self-signed certificates for testing only.${NC}"
echo -e "${RED}   Use CA-signed certificates for production environments.${NC}"
echo -e "${RED}   Never commit private keys to version control!${NC}"
echo ""
