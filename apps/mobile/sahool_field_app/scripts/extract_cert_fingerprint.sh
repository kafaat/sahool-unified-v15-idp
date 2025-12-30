#!/bin/bash

# SAHOOL Field App - Certificate Fingerprint Extraction Script
# This script helps extract SHA-256 fingerprints for SSL certificate pinning
#
# Usage:
#   ./scripts/extract_cert_fingerprint.sh api.sahool.io
#   ./scripts/extract_cert_fingerprint.sh api.sahool.io 443
#   ./scripts/extract_cert_fingerprint.sh 192.168.1.100 8000

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_PORT=443

# Print usage
usage() {
    echo -e "${BLUE}SAHOOL Certificate Fingerprint Extractor${NC}"
    echo ""
    echo "Usage: $0 <hostname> [port]"
    echo ""
    echo "Examples:"
    echo "  $0 api.sahool.io"
    echo "  $0 api.sahool.io 443"
    echo "  $0 192.168.1.100 8000"
    echo ""
    exit 1
}

# Check if hostname is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Hostname is required${NC}"
    usage
fi

HOSTNAME=$1
PORT=${2:-$DEFAULT_PORT}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SAHOOL Certificate Fingerprint Extraction Tool          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}Error: openssl is not installed${NC}"
    echo "Please install openssl:"
    echo "  - Ubuntu/Debian: sudo apt-get install openssl"
    echo "  - macOS: brew install openssl"
    echo "  - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html"
    exit 1
fi

echo -e "${YELLOW}Connecting to: ${HOSTNAME}:${PORT}${NC}"
echo ""

# Test connection first
echo -e "${BLUE}[1/4] Testing connection...${NC}"
if ! timeout 5 bash -c "echo > /dev/tcp/${HOSTNAME}/${PORT}" 2>/dev/null; then
    echo -e "${RED}Error: Cannot connect to ${HOSTNAME}:${PORT}${NC}"
    echo "Please check:"
    echo "  - Hostname is correct"
    echo "  - Port is correct"
    echo "  - Server is running"
    echo "  - Firewall allows connection"
    exit 1
fi
echo -e "${GREEN}✓ Connection successful${NC}"
echo ""

# Extract certificate
echo -e "${BLUE}[2/4] Extracting certificate...${NC}"
CERT=$(openssl s_client -servername ${HOSTNAME} -connect ${HOSTNAME}:${PORT} </dev/null 2>/dev/null)
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to extract certificate${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Certificate extracted${NC}"
echo ""

# Extract public key and calculate fingerprint
echo -e "${BLUE}[3/4] Calculating SHA-256 fingerprint...${NC}"
FINGERPRINT=$(echo "${CERT}" | \
    openssl x509 -pubkey -noout 2>/dev/null | \
    openssl pkey -pubin -outform der 2>/dev/null | \
    openssl dgst -sha256 -binary | \
    openssl enc -base64)

if [ -z "$FINGERPRINT" ]; then
    echo -e "${RED}Error: Failed to calculate fingerprint${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Fingerprint calculated${NC}"
echo ""

# Extract certificate information
echo -e "${BLUE}[4/4] Extracting certificate details...${NC}"
CERT_INFO=$(echo "${CERT}" | openssl x509 -noout -text 2>/dev/null)
SUBJECT=$(echo "${CERT_INFO}" | grep "Subject:" | sed 's/.*Subject: //')
ISSUER=$(echo "${CERT_INFO}" | grep "Issuer:" | sed 's/.*Issuer: //')
NOT_BEFORE=$(echo "${CERT_INFO}" | grep "Not Before:" | sed 's/.*Not Before: //')
NOT_AFTER=$(echo "${CERT_INFO}" | grep "Not After :" | sed 's/.*Not After : //')

echo -e "${GREEN}✓ Certificate details extracted${NC}"
echo ""

# Display results
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    RESULTS                                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Certificate Information:${NC}"
echo -e "  Subject:    ${SUBJECT}"
echo -e "  Issuer:     ${ISSUER}"
echo -e "  Valid From: ${NOT_BEFORE}"
echo -e "  Valid To:   ${NOT_AFTER}"
echo ""

echo -e "${YELLOW}SHA-256 Public Key Fingerprint:${NC}"
echo -e "${GREEN}sha256/${FINGERPRINT}${NC}"
echo ""

# Generate Dart code snippet
echo -e "${YELLOW}Dart Code Snippet:${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
cat << EOF
static const List<String> _pinnedCertificates = [
  // ${HOSTNAME}:${PORT}
  // Valid until: ${NOT_AFTER}
  'sha256/${FINGERPRINT}',
];
EOF
echo -e "${BLUE}----------------------------------------${NC}"
echo ""

# Copy to clipboard if available
if command -v pbcopy &> /dev/null; then
    echo "sha256/${FINGERPRINT}" | pbcopy
    echo -e "${GREEN}✓ Fingerprint copied to clipboard (macOS)${NC}"
elif command -v xclip &> /dev/null; then
    echo "sha256/${FINGERPRINT}" | xclip -selection clipboard
    echo -e "${GREEN}✓ Fingerprint copied to clipboard (Linux)${NC}"
elif command -v clip.exe &> /dev/null; then
    echo "sha256/${FINGERPRINT}" | clip.exe
    echo -e "${GREEN}✓ Fingerprint copied to clipboard (Windows)${NC}"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Copy the fingerprint above"
echo "  2. Open: lib/core/http/certificate_pinning.dart"
echo "  3. Update the _pinnedCertificates list"
echo "  4. Test with: flutter run --dart-define=ENABLE_CERT_PINNING=true"
echo ""

# Check if certificate expires soon
DAYS_UNTIL_EXPIRY=$(echo "${CERT}" | openssl x509 -noout -checkend 0 2>/dev/null && echo "valid" || echo "expired")
if [ "$DAYS_UNTIL_EXPIRY" = "expired" ]; then
    echo -e "${RED}⚠️  WARNING: Certificate has expired or expires soon!${NC}"
    echo -e "${RED}   Please obtain a new certificate before deployment.${NC}"
    echo ""
fi

# Warning for self-signed certificates
if echo "${ISSUER}" | grep -q "${SUBJECT}"; then
    echo -e "${YELLOW}⚠️  NOTE: This appears to be a self-signed certificate.${NC}"
    echo -e "${YELLOW}   For production, use certificates from a trusted CA.${NC}"
    echo ""
fi

echo -e "${GREEN}Done! ✨${NC}"
