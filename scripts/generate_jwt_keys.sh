#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - JWT RSA Key Generation Script
# سكريبت توليد مفاتيح JWT RSA لمنصة سهول
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        SAHOOL Platform - JWT RSA Key Generator                  ║"
echo "║        توليد مفاتيح JWT RSA لمنصة سهول                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Create keys directory
KEYS_DIR="./config/keys"
mkdir -p "$KEYS_DIR"

echo ""
echo -e "${YELLOW}🔐 Generating RSA 4096-bit key pair...${NC}"

# Generate private key
openssl genrsa -out "$KEYS_DIR/jwt_private.pem" 4096

# Generate public key from private key
openssl rsa -in "$KEYS_DIR/jwt_private.pem" -pubout -out "$KEYS_DIR/jwt_public.pem"

# Set secure permissions
chmod 600 "$KEYS_DIR/jwt_private.pem"
chmod 644 "$KEYS_DIR/jwt_public.pem"

echo ""
echo -e "${GREEN}✅ JWT RSA keys generated successfully!${NC}"
echo ""
echo "Files created:"
echo "  - $KEYS_DIR/jwt_private.pem (Private Key - KEEP SECRET!)"
echo "  - $KEYS_DIR/jwt_public.pem (Public Key)"
echo ""

# Generate base64 encoded versions for .env
echo -e "${YELLOW}📋 Generating base64 encoded keys for .env file...${NC}"
echo ""

PRIVATE_KEY_B64=$(cat "$KEYS_DIR/jwt_private.pem" | base64 -w 0)
PUBLIC_KEY_B64=$(cat "$KEYS_DIR/jwt_public.pem" | base64 -w 0)

echo "Add these to your .env file:"
echo ""
echo "# JWT RSA Keys (RS256)"
echo "JWT_ALGORITHM=RS256"
echo "JWT_PRIVATE_KEY_PATH=$KEYS_DIR/jwt_private.pem"
echo "JWT_PUBLIC_KEY_PATH=$KEYS_DIR/jwt_public.pem"
echo ""
echo "# Or use base64 encoded keys directly:"
echo "# JWT_PRIVATE_KEY=$PRIVATE_KEY_B64"
echo "# JWT_PUBLIC_KEY=$PUBLIC_KEY_B64"
echo ""

# Save to file for reference
cat > "$KEYS_DIR/README.md" << 'EOF'
# JWT RSA Keys

These keys are used for JWT authentication with RS256 algorithm.

## Files

- `jwt_private.pem` - Private key (KEEP SECRET!)
- `jwt_public.pem` - Public key (can be shared)

## Security

- NEVER commit private keys to git
- Keep private key permissions at 600
- Rotate keys periodically

## Usage

Add to `.env`:

```env
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=./config/keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./config/keys/jwt_public.pem
```

Or in Kong configuration, use the public key content.

## Regenerating Keys

```bash
./scripts/generate_jwt_keys.sh
```

EOF

echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  - Add 'config/keys/*.pem' to .gitignore"
echo "  - Never commit private keys to version control"
echo "  - Update Kong configuration to use RS256 after adding keys"
echo ""
echo -e "${GREEN}Done!${NC}"
