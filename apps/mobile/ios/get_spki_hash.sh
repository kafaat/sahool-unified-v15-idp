#!/bin/bash

################################################################################
# SPKI Hash Extraction Script for iOS Certificate Pinning
#
# This script extracts the SPKI (Subject Public Key Info) hash from an SSL/TLS
# certificate for use in iOS certificate pinning.
#
# Usage: ./get_spki_hash.sh <domain> [port]
#
# Example:
#   ./get_spki_hash.sh api.sahool.io
#   ./get_spki_hash.sh api-staging.sahool.app 443
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  iOS SPKI Hash Extraction Tool${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Domain name is required${NC}"
    echo ""
    echo "Usage: $0 <domain> [port]"
    echo ""
    echo "Examples:"
    echo "  $0 api.sahool.io"
    echo "  $0 api-staging.sahool.app 443"
    echo ""
    exit 1
fi

DOMAIN=$1
PORT=${2:-443}

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}Error: OpenSSL is not installed${NC}"
    echo "Please install OpenSSL:"
    echo "  macOS: brew install openssl"
    echo "  Ubuntu: sudo apt-get install openssl"
    echo ""
    exit 1
fi

echo -e "${YELLOW}Domain:${NC} $DOMAIN"
echo -e "${YELLOW}Port:${NC} $PORT"
echo ""

# Test connection first
echo -e "${BLUE}Testing connection to $DOMAIN:$PORT...${NC}"
if ! timeout 5 bash -c "echo > /dev/tcp/$DOMAIN/$PORT" 2>/dev/null; then
    echo -e "${RED}Error: Cannot connect to $DOMAIN:$PORT${NC}"
    echo "Please check:"
    echo "  1. Domain name is correct"
    echo "  2. Port is accessible"
    echo "  3. You have internet connection"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ Connection successful${NC}"
echo ""

# Extract SPKI hash
echo -e "${BLUE}Extracting SPKI hash...${NC}"

SPKI_HASH=$(openssl s_client -connect $DOMAIN:$PORT -servername $DOMAIN < /dev/null 2>/dev/null | \
openssl x509 -pubkey -noout | \
openssl pkey -pubin -outform der | \
openssl dgst -sha256 -binary | \
openssl enc -base64)

if [ -z "$SPKI_HASH" ]; then
    echo -e "${RED}Error: Failed to extract SPKI hash${NC}"
    echo "This could be due to:"
    echo "  1. SSL/TLS connection failed"
    echo "  2. Certificate not available"
    echo "  3. OpenSSL version compatibility issue"
    echo ""
    exit 1
fi

# Extract additional certificate information
echo -e "${BLUE}Extracting certificate information...${NC}"
echo ""

CERT_INFO=$(openssl s_client -connect $DOMAIN:$PORT -servername $DOMAIN < /dev/null 2>/dev/null | \
openssl x509 -noout -subject -issuer -dates -fingerprint -sha256)

# Display results
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}  SPKI Hash (for iOS Pinning)${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${YELLOW}SPKI-SHA256-BASE64:${NC}"
echo -e "${GREEN}$SPKI_HASH${NC}"
echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}  Certificate Information${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "$CERT_INFO"
echo ""

# Generate code snippets
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}  Code Snippets${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""

echo -e "${YELLOW}1. For Info.plist:${NC}"
echo ""
cat <<EOF
<dict>
    <key>SPKI-SHA256-BASE64</key>
    <string>$SPKI_HASH</string>
</dict>
EOF

echo ""
echo -e "${YELLOW}2. For CertificatePinning.swift:${NC}"
echo ""
cat <<EOF
certificatePins["$DOMAIN"] = [
    "$SPKI_HASH"
]
EOF

echo ""
echo -e "${YELLOW}3. Current Expiry Date:${NC}"
EXPIRY_DATE=$(echo "$CERT_INFO" | grep "notAfter" | cut -d= -f2-)
echo "$EXPIRY_DATE"
echo ""

# Warning about certificate rotation
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}  Important Notes${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  Certificate Pinning Best Practices:${NC}"
echo ""
echo "1. Always pin at least 2 certificates (current + backup)"
echo "2. Update pins before certificates expire"
echo "3. Test in staging before production"
echo "4. Monitor certificate expiry dates"
echo "5. Keep SPKI hashes secure"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Update ios/Runner/Info.plist with the SPKI hash"
echo "2. Update ios/Runner/CertificatePinning.swift with the SPKI hash"
echo "3. Test the app in both DEBUG and RELEASE modes"
echo "4. Document the certificate expiry date"
echo ""
echo -e "${BLUE}Documentation:${NC} ../CERTIFICATE_ROTATION_IOS.md"
echo ""

# Save to file
OUTPUT_FILE="spki_${DOMAIN}_$(date +%Y%m%d_%H%M%S).txt"
cat > "$OUTPUT_FILE" <<EOF
SPKI Hash Extraction Report
===========================

Domain: $DOMAIN
Port: $PORT
Extraction Date: $(date)

SPKI Hash:
$SPKI_HASH

Certificate Information:
$CERT_INFO

Info.plist snippet:
<dict>
    <key>SPKI-SHA256-BASE64</key>
    <string>$SPKI_HASH</string>
</dict>

CertificatePinning.swift snippet:
certificatePins["$DOMAIN"] = [
    "$SPKI_HASH"
]
EOF

echo -e "${GREEN}✓ Report saved to: $OUTPUT_FILE${NC}"
echo ""
