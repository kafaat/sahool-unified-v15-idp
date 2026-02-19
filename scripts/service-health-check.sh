#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Service Health Check Script
# سكربت فحص صحة خدمات سهول
# ═══════════════════════════════════════════════════════════════════════════════
#
# Purpose:
#   Comprehensive health check for all SAHOOL platform services
#   فحص شامل لصحة جميع خدمات منصة سهول
#
# Usage:
#   ./scripts/service-health-check.sh [OPTIONS]
#
# Options:
#   --json       Output in JSON format
#   --quiet      Only show failures
#   --timeout N  HTTP timeout in seconds (default: 5)
#   --help       Show this help message
#
# Exit Codes:
#   0 = All healthy
#   1 = Some warnings
#   2 = Critical failures
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
HTTP_TIMEOUT=5
JSON_OUTPUT=false
QUIET_MODE=false

# Counters
HEALTHY=0
WARNING=0
CRITICAL=0

# Results storage
declare -A SERVICE_STATUS

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

log() {
    local level=$1
    shift
    local message="$*"

    if [[ "$JSON_OUTPUT" == "true" ]]; then
        return
    fi

    if [[ "$QUIET_MODE" == "true" ]] && [[ "$level" == "SUCCESS" || "$level" == "INFO" ]]; then
        return
    fi

    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[OK]${NC} $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[FAIL]${NC} $message"
            ;;
    esac
}

print_header() {
    if [[ "$JSON_OUTPUT" == "false" ]] && [[ "$QUIET_MODE" == "false" ]]; then
        echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
        echo -e "${CYAN}  $1${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}\n"
    fi
}

show_help() {
    grep "^#" "$0" | grep -v "^#!/" | sed 's/^# //' | sed 's/^#//'
    exit 0
}

# ─────────────────────────────────────────────────────────────────────────────
# Parse Arguments
# ─────────────────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --quiet|-q)
            QUIET_MODE=true
            shift
            ;;
        --timeout)
            HTTP_TIMEOUT="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ─────────────────────────────────────────────────────────────────────────────
# Health Check Functions
# ─────────────────────────────────────────────────────────────────────────────

check_http_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}

    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$HTTP_TIMEOUT" "$url" 2>/dev/null || echo "000")

    if [[ "$status_code" == "$expected_status" ]]; then
        SERVICE_STATUS[$name]="healthy"
        log SUCCESS "$name: HTTP $status_code"
        ((HEALTHY++))
        return 0
    elif [[ "$status_code" == "000" ]]; then
        SERVICE_STATUS[$name]="critical"
        log ERROR "$name: Connection failed"
        ((CRITICAL++))
        return 2
    else
        SERVICE_STATUS[$name]="warning"
        log WARNING "$name: HTTP $status_code (expected $expected_status)"
        ((WARNING++))
        return 1
    fi
}

check_tcp_service() {
    local name=$1
    local host=$2
    local port=$3

    if nc -z -w "$HTTP_TIMEOUT" "$host" "$port" 2>/dev/null; then
        SERVICE_STATUS[$name]="healthy"
        log SUCCESS "$name: Port $port open"
        ((HEALTHY++))
        return 0
    else
        SERVICE_STATUS[$name]="critical"
        log ERROR "$name: Port $port closed"
        ((CRITICAL++))
        return 2
    fi
}

check_docker_service() {
    local name=$1
    local container_name=${2:-$name}

    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container_name}$"; then
        local health
        health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "running")

        if [[ "$health" == "healthy" ]] || [[ "$health" == "running" ]]; then
            SERVICE_STATUS[$name]="healthy"
            log SUCCESS "$name: Container running"
            ((HEALTHY++))
            return 0
        else
            SERVICE_STATUS[$name]="warning"
            log WARNING "$name: Container status $health"
            ((WARNING++))
            return 1
        fi
    else
        SERVICE_STATUS[$name]="critical"
        log ERROR "$name: Container not running"
        ((CRITICAL++))
        return 2
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Health Checks
# ─────────────────────────────────────────────────────────────────────────────

run_health_checks() {
    print_header "SAHOOL Service Health Check"

    log INFO "Checking infrastructure services..."
    echo ""

    # Infrastructure Services
    check_tcp_service "PostgreSQL" "localhost" 5432 || true
    check_tcp_service "Redis" "localhost" 6379 || true
    check_tcp_service "NATS" "localhost" 4222 || true
    check_tcp_service "PgBouncer" "localhost" 6432 || true

    echo ""
    log INFO "Checking API services..."
    echo ""

    # API Gateway
    check_http_service "Kong Gateway" "http://localhost:8000" 404 || true

    # Core Services - check /health or /healthz endpoints
    check_http_service "Field Ops" "http://localhost:8080/healthz" 200 || true
    check_http_service "Weather Service" "http://localhost:8092/healthz" 200 || true
    check_http_service "Advisory Service" "http://localhost:8093/healthz" 200 || true
    check_http_service "Irrigation Smart" "http://localhost:8094/healthz" 200 || true

    # Node.js Services
    check_http_service "Field Core" "http://localhost:3000/health" 200 || true
    check_http_service "Crop Growth Model" "http://localhost:3023/health" 200 || true
    check_http_service "User Service" "http://localhost:3025/health" 200 || true

    # Web Applications
    check_http_service "Web App" "http://localhost:3000" 200 || true
    check_http_service "Admin Dashboard" "http://localhost:3001" 200 || true

    # New Services
    check_http_service "MCP Server" "http://localhost:8201/healthz" 200 || true
    check_http_service "Vision Service" "http://localhost:8150/healthz" 200 || true
    check_http_service "Terrain Service" "http://localhost:8185/healthz" 200 || true

    echo ""
    log INFO "Checking monitoring services..."
    echo ""

    # Monitoring
    check_http_service "Prometheus" "http://localhost:9090/-/healthy" 200 || true
    check_http_service "Grafana" "http://localhost:3002/api/health" 200 || true
}

# ─────────────────────────────────────────────────────────────────────────────
# Output Functions
# ─────────────────────────────────────────────────────────────────────────────

generate_json_output() {
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local status="healthy"
    local exit_code=0

    if [[ $CRITICAL -gt 0 ]]; then
        status="critical"
        exit_code=2
    elif [[ $WARNING -gt 0 ]]; then
        status="warning"
        exit_code=1
    fi

    local json='{'
    json+='"timestamp":"'"$timestamp"'",'
    json+='"status":"'"$status"'",'
    json+='"summary":{"healthy":'"$HEALTHY"',"warning":'"$WARNING"',"critical":'"$CRITICAL"'},'
    json+='"services":{'

    local first=true
    for service in "${!SERVICE_STATUS[@]}"; do
        if [[ "$first" == "false" ]]; then
            json+=','
        fi
        json+='"'"$service"'":"'"${SERVICE_STATUS[$service]}"'"'
        first=false
    done

    json+='}}'

    echo "$json"
}

generate_summary() {
    echo ""
    print_header "Health Check Summary"

    local total=$((HEALTHY + WARNING + CRITICAL))

    log INFO "Total Services Checked: $total"
    echo ""

    if [[ $HEALTHY -gt 0 ]]; then
        echo -e "  ${GREEN}Healthy:${NC}  $HEALTHY"
    fi
    if [[ $WARNING -gt 0 ]]; then
        echo -e "  ${YELLOW}Warnings:${NC} $WARNING"
    fi
    if [[ $CRITICAL -gt 0 ]]; then
        echo -e "  ${RED}Critical:${NC} $CRITICAL"
    fi

    echo ""

    if [[ $CRITICAL -gt 0 ]]; then
        echo -e "${RED}Status: CRITICAL - Some services are down${NC}"
        echo ""
        echo "Run 'make dev' or 'make infra-up' to start services"
        return 2
    elif [[ $WARNING -gt 0 ]]; then
        echo -e "${YELLOW}Status: WARNING - Some services have issues${NC}"
        return 1
    else
        echo -e "${GREEN}Status: HEALTHY - All services operational${NC}"
        return 0
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    run_health_checks

    if [[ "$JSON_OUTPUT" == "true" ]]; then
        generate_json_output
        if [[ $CRITICAL -gt 0 ]]; then
            exit 2
        elif [[ $WARNING -gt 0 ]]; then
            exit 1
        else
            exit 0
        fi
    else
        generate_summary
        exit $?
    fi
}

main
