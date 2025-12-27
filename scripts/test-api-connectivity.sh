#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL API Connectivity Test Script
# اختبار الاتصال بخدمات API الخلفية
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default Kong gateway URL
KONG_URL="${KONG_URL:-http://localhost:8000}"

# Services to test (service_name:port:healthcheck_path)
declare -A SERVICES=(
    ["field-ops"]="8080:/healthz"
    ["ndvi-engine"]="8107:/healthz"
    ["weather-core"]="8108:/healthz"
    ["field-chat"]="8099:/healthz"
    ["iot-gateway"]="8106:/healthz"
    ["agro-advisor"]="8105:/healthz"
    ["ws-gateway"]="8081:/healthz"
    ["crop-health"]="8100:/healthz"
    ["field-core"]="3000:/healthz"
    ["task-service"]="8103:/health"
    ["equipment-service"]="8101:/health"
    ["provider-config"]="8104:/health"
    ["satellite-service"]="8090:/healthz"
    ["indicators-service"]="8091:/healthz"
    ["weather-advanced"]="8092:/healthz"
    ["fertilizer-advisor"]="8093:/healthz"
    ["irrigation-smart"]="8094:/healthz"
    ["crop-health-ai"]="8095:/healthz"
    ["virtual-sensors"]="8096:/healthz"
    ["community-chat"]="8097:/healthz"
    ["yield-engine"]="8098:/healthz"
    ["notification-service"]="8110:/healthz"
    ["research-core"]="3015:/api/v1/healthz"
    ["disaster-assessment"]="3020:/api/v1/disasters/health"
    ["yield-prediction"]="3021:/api/v1/yield/health"
    ["lai-estimation"]="3022:/api/v1/lai/health"
    ["crop-growth-model"]="3023:/api/v1/simulation/health"
    ["marketplace-service"]="3010:/api/v1/healthz"
    ["billing-core"]="8089:/healthz"
    ["ai-advisor"]="8112:/healthz"
    ["astronomical-calendar"]="8111:/healthz"
)

# Kong API routes to test
declare -A API_ROUTES=(
    ["Fields"]="/api/v1/fields"
    ["Tasks"]="/api/v1/tasks"
    ["Weather"]="/api/v1/weather"
    ["IoT Sensors"]="/api/v1/sensors"
    ["Equipment"]="/api/v1/equipment"
    ["NDVI"]="/api/v1/ndvi"
    ["Crop Health"]="/api/v1/crop-health"
    ["Irrigation"]="/api/v1/irrigation"
    ["Fertilizer"]="/api/v1/fertilizer"
    ["Yield"]="/api/v1/yield"
    ["Marketplace"]="/api/v1/marketplace"
    ["Billing"]="/api/v1/billing"
    ["Astronomical"]="/api/v1/astronomical"
)

# Counters
PASSED=0
FAILED=0
SKIPPED=0

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  SAHOOL API Connectivity Test${NC}"
    echo -e "${BLUE}  اختبار الاتصال بخدمات API الخلفية${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

check_docker() {
    echo -e "${YELLOW}Checking Docker status...${NC}"
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed!${NC}"
        return 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}Docker daemon is not running!${NC}"
        return 1
    fi

    echo -e "${GREEN}Docker is running${NC}"
    return 0
}

check_service_direct() {
    local service_name=$1
    local port_path=$2
    local port="${port_path%%:*}"
    local path="${port_path#*:}"

    local url="http://localhost:${port}${path}"

    if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} ${service_name} (port ${port})"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} ${service_name} (port ${port})"
        ((FAILED++))
        return 1
    fi
}

check_kong_route() {
    local route_name=$1
    local route_path=$2

    local url="${KONG_URL}${route_path}"

    local response=$(curl -sf --max-time 10 -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")

    if [ "$response" == "200" ] || [ "$response" == "401" ] || [ "$response" == "403" ]; then
        # 401/403 means the route exists but requires auth
        echo -e "${GREEN}✓${NC} ${route_name} (${route_path}) - HTTP ${response}"
        ((PASSED++))
        return 0
    elif [ "$response" == "000" ]; then
        echo -e "${YELLOW}○${NC} ${route_name} (${route_path}) - Connection failed"
        ((SKIPPED++))
        return 1
    else
        echo -e "${RED}✗${NC} ${route_name} (${route_path}) - HTTP ${response}"
        ((FAILED++))
        return 1
    fi
}

check_kong_status() {
    echo -e "${YELLOW}Checking Kong API Gateway...${NC}"

    local kong_admin="http://localhost:8001/status"

    if curl -sf --max-time 5 "$kong_admin" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Kong Admin API is accessible${NC}"

        # Get Kong status
        local status=$(curl -sf "$kong_admin" 2>/dev/null)
        if [ ! -z "$status" ]; then
            echo -e "  Kong Status: $(echo "$status" | jq -r '.server.connections_active // "N/A"') active connections"
        fi
        return 0
    else
        echo -e "${YELLOW}○ Kong Admin API not accessible (localhost only)${NC}"
        return 1
    fi
}

check_infrastructure() {
    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}  Infrastructure Services${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────────────────${NC}"

    # PostgreSQL
    if docker exec sahool-postgres pg_isready -U sahool > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL (PostGIS)"
        ((PASSED++))
    else
        echo -e "${YELLOW}○${NC} PostgreSQL - not running or not accessible"
        ((SKIPPED++))
    fi

    # Redis
    if docker exec sahool-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis"
        ((PASSED++))
    else
        echo -e "${YELLOW}○${NC} Redis - not running or not accessible"
        ((SKIPPED++))
    fi

    # NATS
    if curl -sf --max-time 3 "http://localhost:8222/healthz" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} NATS JetStream"
        ((PASSED++))
    else
        echo -e "${YELLOW}○${NC} NATS - not running or not accessible"
        ((SKIPPED++))
    fi

    # Qdrant
    if curl -sf --max-time 3 "http://localhost:6333/readyz" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Qdrant Vector DB"
        ((PASSED++))
    else
        echo -e "${YELLOW}○${NC} Qdrant - not running or not accessible"
        ((SKIPPED++))
    fi

    # MQTT
    if docker exec sahool-mqtt pidof mosquitto > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} MQTT (Mosquitto)"
        ((PASSED++))
    else
        echo -e "${YELLOW}○${NC} MQTT - not running or not accessible"
        ((SKIPPED++))
    fi
}

check_services_direct() {
    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}  Direct Service Health Checks${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────────────────${NC}"

    for service in "${!SERVICES[@]}"; do
        check_service_direct "$service" "${SERVICES[$service]}"
    done
}

check_kong_routes() {
    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}  Kong API Gateway Routes${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────────────────${NC}"

    check_kong_status
    echo ""

    for route in "${!API_ROUTES[@]}"; do
        check_kong_route "$route" "${API_ROUTES[$route]}"
    done
}

print_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Test Summary${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}Passed:${NC}  $PASSED"
    echo -e "  ${RED}Failed:${NC}  $FAILED"
    echo -e "  ${YELLOW}Skipped:${NC} $SKIPPED"
    echo ""

    local total=$((PASSED + FAILED + SKIPPED))
    if [ $total -gt 0 ]; then
        local success_rate=$((PASSED * 100 / total))
        echo -e "  Success Rate: ${success_rate}%"
    fi
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All connectivity tests passed!${NC}"
        return 0
    else
        echo -e "${YELLOW}Some services are not available. Please check Docker containers.${NC}"
        return 1
    fi
}

# Main execution
main() {
    print_header

    # Check mode
    MODE="${1:-full}"

    case $MODE in
        "docker")
            check_docker
            ;;
        "infra")
            check_docker && check_infrastructure
            ;;
        "services")
            check_docker && check_services_direct
            ;;
        "kong")
            check_kong_routes
            ;;
        "full")
            check_docker
            check_infrastructure
            check_services_direct
            check_kong_routes
            ;;
        *)
            echo "Usage: $0 [docker|infra|services|kong|full]"
            exit 1
            ;;
    esac

    print_summary
}

main "$@"
