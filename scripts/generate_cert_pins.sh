#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# SAHOOL Certificate Pin Generator
# Generates SHA-256 fingerprints for certificate pinning in mobile apps
#
# Usage:
#   ./scripts/generate_cert_pins.sh <domain>
#   ./scripts/generate_cert_pins.sh api.sahool.app
#   ./scripts/generate_cert_pins.sh ws.sahool.app
#
# Output: SHA-256 fingerprints for use in:
#   - apps/mobile/lib/core/security/certificate_config.dart
#   - apps/mobile/sahool_field_app/lib/core/security/certificate_config.dart
#   - Flutter build: --dart-define=CERT_PIN_API_PRIMARY=<hash>
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <domain> [port]${NC}"
    echo "Example: $0 api.sahool.app"
    echo "Example: $0 api.sahool.app 8443"
    exit 1
fi

DOMAIN=$1
PORT=${2:-443}

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} SAHOOL Certificate Pin Generator${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Domain: ${YELLOW}${DOMAIN}:${PORT}${NC}"
echo ""

# Check openssl availability
if ! command -v openssl &>/dev/null; then
    echo -e "${RED}Error: openssl is required but not installed${NC}"
    exit 1
fi

# Get the certificate chain
echo -e "${YELLOW}Fetching certificate chain...${NC}"
CERT_CHAIN=$(echo | openssl s_client -connect "${DOMAIN}:${PORT}" -servername "${DOMAIN}" 2>/dev/null)

if [ -z "$CERT_CHAIN" ]; then
    echo -e "${RED}Error: Could not connect to ${DOMAIN}:${PORT}${NC}"
    exit 1
fi

# Extract leaf certificate SHA-256 fingerprint
echo -e "${GREEN}Leaf Certificate:${NC}"
LEAF_SHA256=$(echo "$CERT_CHAIN" | openssl x509 -fingerprint -sha256 -noout 2>/dev/null | sed 's/sha256 Fingerprint=//i' | tr -d ':' | tr '[:upper:]' '[:lower:]')
echo -e "  SHA-256: ${YELLOW}${LEAF_SHA256}${NC}"

# Get certificate details
SUBJECT=$(echo "$CERT_CHAIN" | openssl x509 -subject -noout 2>/dev/null | sed 's/subject=//')
ISSUER=$(echo "$CERT_CHAIN" | openssl x509 -issuer -noout 2>/dev/null | sed 's/issuer=//')
NOT_AFTER=$(echo "$CERT_CHAIN" | openssl x509 -enddate -noout 2>/dev/null | sed 's/notAfter=//')
echo -e "  Subject: ${SUBJECT}"
echo -e "  Issuer:  ${ISSUER}"
echo -e "  Expires: ${NOT_AFTER}"

# Extract SPKI hash (for iOS NSPinnedDomains)
echo ""
echo -e "${GREEN}SPKI Hash (for iOS Info.plist):${NC}"
SPKI_HASH=$(echo "$CERT_CHAIN" | openssl x509 -pubkey -noout 2>/dev/null | openssl pkey -pubin -outform der 2>/dev/null | openssl dgst -sha256 -binary | openssl enc -base64)
echo -e "  SPKI-SHA256-BASE64: ${YELLOW}${SPKI_HASH}${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} Usage in SAHOOL:${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}1. Dart certificate_config.dart:${NC}"
echo "   value: '${LEAF_SHA256}',"
echo ""
echo -e "${YELLOW}2. Flutter build command:${NC}"
echo "   flutter build apk --dart-define=CERT_PIN_API_PRIMARY=${LEAF_SHA256}"
echo ""
echo -e "${YELLOW}3. iOS Info.plist NSPinnedDomains:${NC}"
echo "   <key>${DOMAIN}</key>"
echo "   <dict>"
echo "     <key>NSIncludesSubdomains</key><true/>"
echo "     <key>NSPinnedCAIdentities</key>"
echo "     <array><dict>"
echo "       <key>SPKI-SHA256-BASE64</key>"
echo "       <string>${SPKI_HASH}</string>"
echo "     </dict></array>"
echo "   </dict>"
echo ""
