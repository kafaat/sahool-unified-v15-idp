#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Kong Configuration Validation Script
# SAHOOL Platform - v16.1.0
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Get script directory and find kong.yml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check multiple possible locations for Kong config
KONG_CONFIGS=(
    "$PROJECT_ROOT/infrastructure/gateway/kong/kong.yml"
    "$PROJECT_ROOT/infra/kong/kong.yml"
)

KONG_CONFIG=""
for config in "${KONG_CONFIGS[@]}"; do
    if [[ -f "$config" ]]; then
        KONG_CONFIG="$config"
        break
    fi
done

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "Kong Configuration Validation - SAHOOL Platform"
echo "════════════════════════════════════════════════════════════════"

# Check if kong.yml exists
if [[ -z "$KONG_CONFIG" || ! -f "$KONG_CONFIG" ]]; then
    echo -e "${RED}✗ Kong configuration file not found in any expected location${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Kong configuration file found: $KONG_CONFIG${NC}"

# Check for CORS wildcard
if grep -q 'origins:' "$KONG_CONFIG" && grep -A1 'origins:' "$KONG_CONFIG" | grep -q '"\*"'; then
    echo -e "${RED}✗ CORS wildcard detected - security risk!${NC}"
else
    echo -e "${GREEN}✓ CORS properly configured (no wildcard)${NC}"
fi

# Check for upstreams
if grep -q '^upstreams:' "$KONG_CONFIG"; then
    UPSTREAM_COUNT=$(grep -c 'name:.*-upstream' "$KONG_CONFIG" || echo "0")
    echo -e "${GREEN}✓ Upstreams configured: $UPSTREAM_COUNT${NC}"
else
    echo -e "${YELLOW}⚠ No upstreams defined - consider adding health checks${NC}"
fi

# Check for Redis rate limiting
if grep -q 'policy: redis' "$KONG_CONFIG"; then
    REDIS_COUNT=$(grep -c 'policy: redis' "$KONG_CONFIG" || echo "0")
    echo -e "${GREEN}✓ Redis rate-limiting enabled: $REDIS_COUNT plugins${NC}"
else
    echo -e "${YELLOW}⚠ Using local rate-limiting - not distributed${NC}"
fi

# Check for security headers
if grep -q 'X-Content-Type-Options' "$KONG_CONFIG"; then
    echo -e "${GREEN}✓ Security headers configured${NC}"
else
    echo -e "${YELLOW}⚠ Security headers not configured${NC}"
fi

# Check for RS256 JWT support
if grep -q 'algorithm: RS256' "$KONG_CONFIG"; then
    echo -e "${GREEN}✓ RS256 JWT support enabled${NC}"
else
    echo -e "${YELLOW}⚠ Only HS256 JWT configured${NC}"
fi

# Check for IP restrictions on sensitive services
SENSITIVE_SERVICES=("billing-core" "iot-gateway")
for service in "${SENSITIVE_SERVICES[@]}"; do
    if grep -A40 "name: $service" "$KONG_CONFIG" | grep -q 'ip-restriction'; then
        echo -e "${GREEN}✓ IP restriction on $service${NC}"
    else
        echo -e "${YELLOW}⚠ No IP restriction on $service${NC}"
    fi
done

# Check marketplace has rate limiting (no IP restriction needed - public facing)
if grep -A20 "name: marketplace-service" "$KONG_CONFIG" | grep -q 'rate-limiting'; then
    echo -e "${GREEN}✓ Rate limiting on marketplace-service${NC}"
else
    echo -e "${YELLOW}⚠ No rate limiting on marketplace-service${NC}"
fi

# Validate YAML syntax
if command -v python3 &> /dev/null; then
    if python3 -c "import yaml; yaml.safe_load(open('$KONG_CONFIG'))" 2>/dev/null; then
        echo -e "${GREEN}✓ YAML syntax valid${NC}"
    else
        echo -e "${RED}✗ YAML syntax error${NC}"
        exit 1
    fi
fi

echo "════════════════════════════════════════════════════════════════"
echo "Validation complete!"
echo "════════════════════════════════════════════════════════════════"
