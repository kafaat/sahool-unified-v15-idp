#!/bin/bash

# Certificate Pin Generation Script
# Generates certificate pins for both Android (SHA256) and iOS (SPKI) platforms
#
# Usage:
#   ./generate_cert_pins.sh <domain> [port]
#
# Examples:
#   ./generate_cert_pins.sh api.sahool.app
#   ./generate_cert_pins.sh api.sahool.app 443
#   ./generate_cert_pins.sh api-staging.sahool.app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PORT=443

# Print usage
usage() {
    echo "Usage: $0 <domain> [port]"
    echo ""
    echo "Generates certificate pins for both Android and iOS platforms"
    echo ""
    echo "Arguments:"
    echo "  domain    Domain name (e.g., api.sahool.app)"
    echo "  port      Port number (default: 443)"
    echo ""
    echo "Examples:"
    echo "  $0 api.sahool.app"
    echo "  $0 api.sahool.app 443"
    echo "  $0 api-staging.sahool.app"
    echo ""
    echo "Requirements:"
    echo "  - openssl must be installed"
    echo ""
    exit 1
}

# Check if openssl is installed
check_openssl() {
    if ! command -v openssl &> /dev/null; then
        echo -e "${RED}Error: openssl is not installed${NC}"
        echo "Install with:"
        echo "  Ubuntu/Debian: sudo apt-get install openssl"
        echo "  macOS: brew install openssl"
        exit 1
    fi
}

# Parse arguments
if [ $# -lt 1 ]; then
    usage
fi

DOMAIN=$1
if [ $# -ge 2 ]; then
    PORT=$2
fi

# Validate domain
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Error: Domain cannot be empty${NC}"
    usage
fi

# Check dependencies
check_openssl

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Certificate Pin Generator${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Domain: ${GREEN}$DOMAIN${NC}"
echo -e "Port:   ${GREEN}$PORT${NC}"
echo ""

# Create temporary files
TMP_CERT=$(mktemp)
TMP_PUBKEY=$(mktemp)

# Cleanup on exit
cleanup() {
    rm -f "$TMP_CERT" "$TMP_PUBKEY"
}
trap cleanup EXIT

# Fetch certificate
echo -e "${YELLOW}Fetching certificate from $DOMAIN:$PORT...${NC}"
if ! echo | openssl s_client -connect "$DOMAIN:$PORT" -servername "$DOMAIN" 2>/dev/null | \
    openssl x509 -outform PEM > "$TMP_CERT" 2>/dev/null; then
    echo -e "${RED}Error: Failed to fetch certificate from $DOMAIN:$PORT${NC}"
    echo "Please check:"
    echo "  1. Domain name is correct"
    echo "  2. Port is accessible"
    echo "  3. Server is running and has a valid certificate"
    exit 1
fi

echo -e "${GREEN}✓ Certificate fetched successfully${NC}"
echo ""

# Extract certificate information
echo -e "${BLUE}Certificate Information:${NC}"
echo "----------------------------------------"

# Subject
SUBJECT=$(openssl x509 -in "$TMP_CERT" -noout -subject 2>/dev/null | sed 's/subject=//')
echo -e "Subject:     ${GREEN}$SUBJECT${NC}"

# Issuer
ISSUER=$(openssl x509 -in "$TMP_CERT" -noout -issuer 2>/dev/null | sed 's/issuer=//')
echo -e "Issuer:      ${GREEN}$ISSUER${NC}"

# Valid from
VALID_FROM=$(openssl x509 -in "$TMP_CERT" -noout -startdate 2>/dev/null | sed 's/notBefore=//')
echo -e "Valid From:  ${GREEN}$VALID_FROM${NC}"

# Valid until
VALID_UNTIL=$(openssl x509 -in "$TMP_CERT" -noout -enddate 2>/dev/null | sed 's/notAfter=//')
echo -e "Valid Until: ${GREEN}$VALID_UNTIL${NC}"

echo ""

# Generate Android SHA256 fingerprint (full certificate hash)
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ANDROID - SHA256 Certificate Fingerprint${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

SHA256_FINGERPRINT=$(openssl x509 -in "$TMP_CERT" -noout -fingerprint -sha256 2>/dev/null | \
    sed 's/SHA256 Fingerprint=//' | tr -d ':')

# Also get lowercase version without colons for Dart
SHA256_LOWERCASE=$(echo "$SHA256_FINGERPRINT" | tr '[:upper:]' '[:lower:]')

echo -e "${YELLOW}For Android network_security_config.xml:${NC}"
echo ""
echo "    <pin-set>"
echo "        <pin digest=\"sha256\">$SHA256_FINGERPRINT</pin>"
echo "    </pin-set>"
echo ""

echo -e "${YELLOW}For Dart (certificate_pinning_service.dart):${NC}"
echo ""
echo "    CertificatePin("
echo "      type: PinType.sha256,"
echo "      value: '$SHA256_LOWERCASE',"
echo "      expiryDate: DateTime(YYYY, MM, DD),"
echo "      description: 'Production certificate for $DOMAIN',"
echo "    ),"
echo ""

# Generate iOS SPKI hash (Subject Public Key Info)
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}iOS - SPKI Public Key Hash (Base64)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Extract public key
openssl x509 -in "$TMP_CERT" -pubkey -noout > "$TMP_PUBKEY" 2>/dev/null

# Calculate SPKI hash
SPKI_HASH=$(openssl pkey -pubin -in "$TMP_PUBKEY" -outform DER 2>/dev/null | \
    openssl dgst -sha256 -binary | \
    openssl enc -base64)

echo -e "${YELLOW}For iOS Info.plist:${NC}"
echo ""
echo "    <dict>"
echo "        <key>SPKI-SHA256-BASE64</key>"
echo "        <string>$SPKI_HASH</string>"
echo "    </dict>"
echo ""

# Generate backup pin recommendation
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Important Notes${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Certificate Pinning Best Practices:${NC}"
echo ""
echo "1. ${GREEN}Always pin at least 2 certificates${NC} (current + backup)"
echo "   - Primary: Current production certificate"
echo "   - Backup: Next certificate for rotation"
echo ""
echo "2. ${GREEN}Generate backup pins BEFORE current expires${NC}"
echo "   - Get backup certificate from your certificate provider"
echo "   - Add backup pin alongside current pin"
echo "   - Remove old pin only after certificate rotation"
echo ""
echo "3. ${GREEN}Different formats for different platforms:${NC}"
echo "   - Android: Uses SHA256 of full certificate"
echo "   - iOS: Uses SHA256 of SPKI (public key only)"
echo "   - Dart: Uses SHA256 of full certificate"
echo ""
echo "4. ${GREEN}Test before deploying:${NC}"
echo "   - Test in staging environment first"
echo "   - Verify connectivity with new pins"
echo "   - Monitor logs for certificate validation"
echo ""
echo "5. ${GREEN}Set expiry dates:${NC}"
echo "   - Add expiryDate to all pins"
echo "   - Monitor for expiring certificates"
echo "   - Plan rotation before expiry"
echo ""

# Generate summary file
SUMMARY_FILE="cert_pins_${DOMAIN}_$(date +%Y%m%d_%H%M%S).txt"

cat > "$SUMMARY_FILE" <<EOF
Certificate Pins Generated for $DOMAIN
Generated: $(date)
========================================

DOMAIN: $DOMAIN
PORT: $PORT

CERTIFICATE INFORMATION:
----------------------------------------
Subject:     $SUBJECT
Issuer:      $ISSUER
Valid From:  $VALID_FROM
Valid Until: $VALID_UNTIL

ANDROID - SHA256 FINGERPRINT:
----------------------------------------
Fingerprint (with colons): $SHA256_FINGERPRINT
Fingerprint (lowercase):   $SHA256_LOWERCASE

network_security_config.xml:
    <domain-config>
        <domain includeSubdomains="true">$DOMAIN</domain>
        <pin-set>
            <pin digest="sha256">$SHA256_FINGERPRINT</pin>
        </pin-set>
    </domain-config>

Dart (certificate_pinning_service.dart):
    '$DOMAIN': [
        CertificatePin(
            type: PinType.sha256,
            value: '$SHA256_LOWERCASE',
            expiryDate: DateTime(YYYY, MM, DD),
            description: 'Production certificate for $DOMAIN',
        ),
    ],

iOS - SPKI HASH (BASE64):
----------------------------------------
SPKI Hash: $SPKI_HASH

Info.plist:
    <key>$DOMAIN</key>
    <dict>
        <key>NSIncludesSubdomains</key>
        <true/>
        <key>NSPinnedLeafIdentities</key>
        <array>
            <dict>
                <key>SPKI-SHA256-BASE64</key>
                <string>$SPKI_HASH</string>
            </dict>
        </array>
    </dict>

NEXT STEPS:
----------------------------------------
1. Update certificate_pinning_service.dart with the Dart pin
2. Update android/app/src/main/res/xml/network_security_config.xml
3. Update ios/Runner/Info.plist with the iOS pin
4. Add backup pins (get from your certificate provider)
5. Test in staging environment
6. Deploy to production
7. Monitor logs for certificate validation

IMPORTANT:
----------------------------------------
- Always have at least 2 pins (primary + backup)
- Test thoroughly before production deployment
- Set expiry dates and monitor for expiring certificates
- Plan certificate rotation before expiry
EOF

echo -e "${GREEN}✓ Summary saved to: $SUMMARY_FILE${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Certificate pins generated successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
