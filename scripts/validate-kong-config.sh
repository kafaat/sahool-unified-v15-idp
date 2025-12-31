#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Kong Configuration Validation Script
# SAHOOL Platform - v16.1.0
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

KONG_CONFIG="/home/user/sahool-unified-v15-idp/infra/kong/kong.yml"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "Kong Configuration Validation - SAHOOL Platform"
echo "════════════════════════════════════════════════════════════════"

# Check if kong.yml exists
if [[ ! -f "$KONG_CONFIG" ]]; then
    echo -e "${RED}✗ Kong configuration file not found: $KONG_CONFIG${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Kong configuration file found${NC}"

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
SENSITIVE_SERVICES=("billing-core" "iot-gateway" "marketplace-service" "admin-dashboard")
for service in "${SENSITIVE_SERVICES[@]}"; do
    if grep -A20 "name: $service" "$KONG_CONFIG" | grep -q 'ip-restriction'; then
        echo -e "${GREEN}✓ IP restriction on $service${NC}"
    else
        echo -e "${YELLOW}⚠ No IP restriction on $service${NC}"
    fi
done

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
